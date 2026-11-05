"""Bounded, metadata-only topic discovery independent of LinkedIn access.

Results belong to their original sources, not to LinkedIn. This module never
fetches discovered links. Rights to use source material remain unverified.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
from uuid import uuid4
import xml.etree.ElementTree as ET

from .contracts import AccessSuspended, CollectionError, ConfigurationError
from .transport import UrllibTransport

# Exact reviewed endpoints. New endpoints require a source and rights review.
_ENDPOINTS = {
    "hacker-news-top": ("hn_top", "https://hacker-news.firebaseio.com/v0/topstories.json"),
    "huggingface-blog-rss": ("rss", "https://huggingface.co/blog/feed.xml"),
}


def load_sources(path=None):
    path = Path(path) if path else Path(__file__).with_name("external-sources.json")
    return json.loads(path.read_text(encoding="utf-8"))


def _schema(store):
    store.db.executescript('''
      CREATE TABLE IF NOT EXISTS external_discovery_items (
        source_id TEXT NOT NULL, external_id TEXT NOT NULL, source_url TEXT NOT NULL,
        first_seen TEXT NOT NULL, last_seen TEXT NOT NULL, metadata TEXT NOT NULL,
        PRIMARY KEY (source_id, external_id));
      CREATE TABLE IF NOT EXISTS external_discovery_observations (
        observation_id TEXT PRIMARY KEY, source_id TEXT NOT NULL, external_id TEXT NOT NULL,
        observed_at TEXT NOT NULL, metadata TEXT NOT NULL,
        FOREIGN KEY (source_id, external_id) REFERENCES external_discovery_items(source_id, external_id));
    ''')
    # Permit in-place use of databases initialized by the initial module revision.
    columns = {row[1] for row in store.db.execute('PRAGMA table_info(external_discovery_items)')}
    if 'last_seen' not in columns:
        with store.db:
            store.db.execute('ALTER TABLE external_discovery_items ADD COLUMN last_seen TEXT')
            store.db.execute('UPDATE external_discovery_items SET last_seen=first_seen WHERE last_seen IS NULL')


class _ExternalState:
    # Do not copy denied response bodies into raw_objects. Persist the hold only.
    def __init__(self, store):
        self.store = store

    def get_suspension(self, key):
        return self.store.get_suspension(key)

    def suspend(self, key, reason, retry_after_seconds=None):
        return self.store.suspend(key, reason, retry_after_seconds=retry_after_seconds)

    def log_request(self, source_id, event):
        return self.store.log_request(source_id, event)


def _url(value):
    try:
        parts = urlsplit(value or "")
        if parts.scheme not in ("https", "http") or not parts.hostname or parts.username or parts.password:
            return None
        return urlunsplit((parts.scheme, parts.netloc, parts.path, parts.query, ""))
    except ValueError:
        return None


def _date(value):
    if not value:
        return None
    try:
        parsed = parsedate_to_datetime(value)
        return parsed.astimezone(timezone.utc).isoformat() if parsed.tzinfo else None
    except (ValueError, TypeError, OverflowError):
        return None


def _text(node, name):
    for child in node:
        if child.tag.rsplit('}', 1)[-1].lower() == name.lower():
            return ''.join(child.itertext()).strip()
    return ''


def _parse_feed(body, source, timestamp):
    # Reject declarations, including custom entities, before parsing untrusted XML.
    if b'<!DOCTYPE' in body.upper() or b'<!ENTITY' in body.upper():
        raise ValueError('xml_declaration_forbidden')
    root = ET.fromstring(body)
    records = []
    for node in root.iter():
        if node.tag.rsplit('}', 1)[-1].lower() not in ('item', 'entry'):
            continue
        link = _text(node, 'link')
        if not link:
            for child in node:
                if child.tag.rsplit('}', 1)[-1].lower() == 'link' and child.get('href'):
                    link = child.get('href')
                    break
        link = _url(link)
        title = _text(node, 'title')[:500]
        if not link or not title:
            continue
        identifier = hashlib.sha256(link.encode()).hexdigest()
        records.append({"source_id": source["source_id"], "external_id": identifier,
                        "source_url": link, "title": title,
                        "published_at": _date(_text(node, 'pubDate') or _text(node, 'published')),
                        "observed_at": timestamp, "signal_type": "external_topic_signal",
                        "source_platform": "publisher_feed", "review_status": "unverified_candidate",
                        "permission_state": source['rights'], "engagement": None})
        if len(records) >= min(int(source.get('max_items', 20)), 20):
            break
    return records


def _parse_hn(body, source, timestamp):
    ids = json.loads(body)
    if not isinstance(ids, list):
        raise ValueError('invalid_hn_index')
    records = []
    for rank, number in enumerate(ids[:min(int(source.get('max_items', 20)), 20)], 1):
        if type(number) is not int or number <= 0:
            continue
        records.append({"source_id": source['source_id'], "external_id": str(number),
                        "source_url": f'https://news.ycombinator.com/item?id={number}',
                        "title": None, "published_at": None, "observed_at": timestamp,
                        "signal_type": "external_topic_signal", "source_platform": "hacker_news",
                        "hn_index_rank": rank, "engagement": None,
                        "missing_fields": ['title', 'topic', 'hn_score', 'published_at'],
                        "review_status": "unverified_candidate", "permission_state": source['rights']})
    return records


def _validate(source):
    expected = _ENDPOINTS.get(source.get('source_id'))
    if not expected or (source.get('kind'), source.get('url')) != expected:
        raise ConfigurationError('external_endpoint_not_approved')
    host = urlsplit(source['url']).hostname
    if source.get('allowed_hosts') != [host] or source.get('rights') != 'metadata_for_internal_review_reuse_unverified':
        raise ConfigurationError('external_source_policy_invalid')
    if type(source.get('max_items')) is not int or not 1 <= source['max_items'] <= 20:
        raise ConfigurationError('external_item_limit_invalid')


def _store(store, row):
    payload = json.dumps(row, sort_keys=True, ensure_ascii=False)
    with store.db:
        cursor = store.db.execute('INSERT OR IGNORE INTO external_discovery_items (source_id, external_id, source_url, first_seen, last_seen, metadata) VALUES (?,?,?,?,?,?)',
            (row['source_id'], row['external_id'], row['source_url'], row['observed_at'], row['observed_at'], payload))
        inserted = cursor.rowcount == 1
        if not inserted:
            store.db.execute('UPDATE external_discovery_items SET last_seen=?, metadata=? WHERE source_id=? AND external_id=?',
                (row['observed_at'], payload, row['source_id'], row['external_id']))
        store.db.execute('INSERT INTO external_discovery_observations VALUES (?,?,?,?,?)',
            (uuid4().hex, row['source_id'], row['external_id'], row['observed_at'], payload))
    return inserted


def _enrich_hn(row, body, observed_at):
    item = json.loads(body)
    if not isinstance(item, dict) or item.get('id') != int(row['external_id']):
        raise ValueError('invalid_hn_item')
    if item.get('deleted') or item.get('dead') or item.get('type') != 'story':
        row['detail_status'] = 'unavailable_or_non_story'
    else:
        row['title'] = str(item.get('title') or '')[:500] or None
        timestamp = item.get('time')
        if type(timestamp) is int:
            try:
                row['published_at'] = datetime.fromtimestamp(timestamp, timezone.utc).isoformat()
            except (ValueError, OSError, OverflowError):
                pass
        # HN scores and discussion counts are HN metrics, never LinkedIn metrics.
        row['engagement'] = {'hn_score': item.get('score') if type(item.get('score')) is int else None,
                             'hn_descendant_count': item.get('descendants') if type(item.get('descendants')) is int else None}
        row['detail_status'] = 'observed'
    row['detail_collected_at'] = observed_at
    row['missing_fields'] = [field for field, value in (
        ('title', row['title']), ('topic', None), ('hn_score', (row.get('engagement') or {}).get('hn_score')),
        ('published_at', row['published_at'])) if value is None]


def _priority_hn(store, rows):
    previous = {}
    for external_id, payload in store.db.execute(
            "SELECT external_id, metadata FROM external_discovery_items WHERE source_id='hacker-news-top'"):
        try:
            previous[external_id] = json.loads(payload)
        except (ValueError, TypeError):
            continue
    for row in rows:
        old = previous.get(row['external_id'], {})
        for field in ('title', 'published_at', 'engagement', 'detail_status', 'detail_collected_at', 'missing_fields'):
            if field in old:
                row[field] = old[field]
    # Previously unobserved details first; oldest observed details next.
    return sorted(rows, key=lambda row: row.get('detail_collected_at') or '')[:5]


def _prune(store):
    now = datetime.now(timezone.utc)
    with store.db:
        store.db.execute('DELETE FROM external_discovery_observations WHERE observed_at < ?',
                         ((now - timedelta(days=30)).isoformat(),))
        store.db.execute('DELETE FROM external_discovery_items WHERE last_seen < ? AND NOT EXISTS '
                         '(SELECT 1 FROM external_discovery_observations o WHERE o.source_id=external_discovery_items.source_id '
                         'AND o.external_id=external_discovery_items.external_id)', ((now - timedelta(days=90)).isoformat(),))


async def collect_external(store, config=None, *, transport_factory=None):
    """Collect one request per feed, and up to six HN requests; return safe counts.

    The store must be locked by the caller. Titles/URLs and source observations
    stay in the encrypted checkpoint; return values contain no titles or snippets.
    Factories receive (transport_spec, store) and expose async fetch/aclose.
    """
    config = load_sources() if config is None else config
    _schema(store)
    _prune(store)
    results, observations = [], []
    seen_sources = set()
    for source in config.get('sources', []):
        sid = source.get('source_id', 'unknown')
        result = {"source_id": sid, "status": "error", "requests": 0, "successful_requests": 0,
                  "items_observed": 0, "new_items": 0, "duplicates": 0, "detail_requests": 0, "details_observed": 0, "error": None}
        results.append(result)
        transport = None
        try:
            _validate(source)
            if sid in seen_sources:
                raise ConfigurationError('duplicate_external_source')
            seen_sources.add(sid)
            if store.get_suspension(sid):
                result.update(status='held', error='source_access_suspended')
                continue
            spec = {"source_id": sid, "access_group": sid, "allowed_hosts": source['allowed_hosts'],
                    "permitted_methods": ['GET'], "permissions": {"public_read": True},
                    "max_attempts": 1, "concurrency": 1, "rate_per_second": 0.5,
                    "timeout_seconds": 15, "max_bytes": 1_000_000}
            transport = (transport_factory or UrllibTransport)(spec, _ExternalState(store))
            result['requests'] = 1
            response = await transport.fetch(source['url'])
            if response.status_code in (401, 403, 429, 999):
                # Also fail closed when an injected transport returns rather than raising.
                store.suspend(sid, f'http_{response.status_code}')
                raise AccessSuspended('source_access_suspended')
            if response.status_code != 200:
                raise CollectionError('external_http_error')
            result['successful_requests'] += 1
            rows = (_parse_hn(response.body, source, response.collected_at) if source['kind'] == 'hn_top'
                    else _parse_feed(response.body, source, response.collected_at))
            # Deduplicate before detail fetch as well as before storage.
            rows = list({row['external_id']: row for row in rows}.values())
            if source['kind'] == 'hn_top':
                # On any deny or transport failure, save index and already completed
                # detail observations, stop this source, then continue other sources.
                try:
                    for row in _priority_hn(store, rows):
                        detail_url = 'https://hacker-news.firebaseio.com/v0/item/' + row['external_id'] + '.json'
                        result['requests'] += 1
                        result['detail_requests'] += 1
                        detail = await transport.fetch(detail_url)
                        if detail.status_code in (401, 403, 429, 999):
                            store.suspend(sid, f'http_{detail.status_code}')
                            raise AccessSuspended('source_access_suspended')
                        if detail.status_code != 200:
                            raise CollectionError('external_http_error')
                        result['successful_requests'] += 1
                        _enrich_hn(row, detail.body, detail.collected_at)
                        result['details_observed'] += 1
                except (AccessSuspended, CollectionError, ValueError, TypeError, KeyError) as exc:
                    result['status'] = 'held' if isinstance(exc, AccessSuspended) else 'error'
                    result['error'] = 'source_access_suspended' if isinstance(exc, AccessSuspended) else type(exc).__name__
            seen = set()
            for row in rows:
                if row['external_id'] in seen:
                    continue
                seen.add(row['external_id'])
                new = _store(store, row)
                result['items_observed'] += 1
                result['new_items' if new else 'duplicates'] += 1
                observations.append({"source_id": sid, "external_id": row['external_id'],
                                     "observation_type": row['signal_type'], "new": new})
            if result['error'] is None:
                result['status'] = 'ok'
        except AccessSuspended:
            result.update(status='held', error='source_access_suspended')
        except (ConfigurationError, CollectionError, ValueError, TypeError, ET.ParseError, KeyError) as exc:
            result.update(status='error', error=type(exc).__name__)
        finally:
            if transport is not None:
                await transport.aclose()
    return {"source_results": results, "observations": observations,
            "status": 'ok' if results and all(x['status'] == 'ok' for x in results) else 'partial',
            "linkedin_posts_collected": 0,
            "data_classification": 'external signals; not LinkedIn engagement'}
