#!/usr/bin/env python3
"""Cycle-size-agnostic release builder for the LinkedIn research pipeline.

Joins the immutable base dataset (previous cycle's data/dataset.json) with this
run's new posts, media, transcripts, per-post metric snapshots, observed-velocity
rows, cohorts, transcript QA and held-author queue. No counts are hard-coded: every
count is derived from the inputs and written to verification/release-checks.json.

    python3 release.py                       # build + verify in this run folder
    python3 release.py --dry-run             # run every data check, write nothing
    python3 release.py --root R --base B     # explicit run / base folders
    python3 release.py --hash-dataless       # also read iCloud-evicted files to hash them

Absent analytical replacement files inherit dated base evidence with a warning;
an explicit current file, including an empty list, is authoritative. Other absent
new inputs are reported as empty. A failed check blocks promotion: existing
outputs stay untouched and the exit code is 1.
Standard library only. Semantics: a snapshot "velocity" is the observed change of a
public reaction counter between two captures; it is not reach, impressions or trend rank.
"""
import argparse
import csv
import hashlib
import json
import os
import re
import sqlite3
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
import performance

HERE = Path(__file__).resolve().parent
DEFAULT_BASE = HERE / 'tests/fixtures/release/v3'
SCHEMA_VERSION = 1
BASE_REQUIRED = ['summary', 'posts', 'assets', 'visual_reviews', 'video_reviews', 'transcripts',
                 'qualification', 'accounts', 'prospects']
MEDIA_KINDS = ('image', 'document_preview', 'video')
SNAPSHOT_KINDS = ('baseline_import', 'reobservation', 'new_discovery')
METRIC_STATUS = ('observed', 'not_exposed', 'unavailable', 'conflict')
METRIC_NAMES = ('reactions', 'comments', 'reposts')
# Single source of truth for local links the viewer may render (also injected into the page).
SAFE_PATH_PATTERN = r'^(?:\.\./[A-Za-z0-9._-]+/)?(?:media|transcripts|analysis|visual-root|visual-a|video-review)/[A-Za-z0-9_.\-/]+$'
SF_DATALESS = 0x40000000  # macOS: file content evicted to iCloud; reading it blocks on a download
LINK_CANDIDATES = [('README.md', 'Method and report'), ('data/new-posts.csv', 'New posts CSV'),
                   ('data/posts.csv', 'All posts CSV'), ('data/snapshots.csv', 'Snapshot history CSV'),
                   ('data/velocity.csv', 'Observed velocity CSV'), ('data/linkedin.sqlite', 'Joined SQLite'),
                   ('data/qualification-table.csv', 'Qualification CSV'),
                   ('handoff/NEXT-RUN-PROMPT.md', 'Next-run prompt'), ('gaps.json', 'Gaps')]
PRODUCED = {'data/new-posts.csv', 'data/posts.csv', 'data/snapshots.csv', 'data/velocity.csv',
            'data/linkedin.sqlite', 'data/qualification-table.csv'}
# dataset key, sqlite table, row key, post id of row (None when the entity is not post-scoped)
ENTITIES = [
    ('posts', 'posts', lambda r: r['id'], lambda r: r['id']),
    ('snapshots', 'snapshots', lambda r: r['snapshot_id'], lambda r: r['post_id']),
    ('velocity', 'velocity', lambda r: r['post_id'], lambda r: r['post_id']),
    ('cohorts', 'cohorts', lambda r: r['cohort'], None),
    ('accounts', 'accounts', lambda r: r['id'], None),
    ('assets', 'media_assets', lambda r: r['asset_id'], lambda r: r['post_id']),
    ('visual_reviews', 'visual_reviews', lambda r: r['asset_id'], lambda r: r.get('post_id')),
    ('video_reviews', 'video_reviews', lambda r: r['asset_id'], lambda r: r.get('post_id')),
    ('media_gaps', 'media_gaps', lambda r: r['asset_id'], lambda r: r['post_id']),
    ('transcripts', 'transcripts', lambda r: r['asset_id'], lambda r: r.get('post_id')),
    ('transcript_gaps', 'transcript_gaps', lambda r: r['asset_id'], lambda r: r['post_id']),
    ('transcript_qa', 'transcript_qa', lambda r: r['asset_id'], lambda r: r.get('post_id')),
    ('qualification', 'qualification', lambda r: r['post_id'], lambda r: r['post_id']),
    ('prospects', 'prospects', lambda r: r['id'], None),
    ('held_authors', 'held_authors', lambda r: r['author_key'], None),
    ('interpretations', 'interpretations', lambda r: r['post_id'], lambda r: r['post_id']),
    ('performance', 'performance_assessments', lambda r: r['post_id'], lambda r: r['post_id']),
    ('author_decisions', 'author_decisions', lambda r: r['author_key'], None),
]


class ReleaseAbort(Exception):
    """An input cannot be read at all; later checks would be meaningless."""


# --------------------------------------------------------------------------- helpers
def unique_pairs(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise ValueError('duplicate JSON key: ' + k)
        out[k] = v
    return out


def jloads(text):
    return json.loads(text, object_pairs_hook=unique_pairs)


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def canon(x):
    return json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def norm_text(t):
    return re.sub(r'\s+', ' ', t or '').strip().lower()


def parse_ts(s):
    if not isinstance(s, str):
        return None
    try:
        d = datetime.fromisoformat(s.replace('Z', '+00:00'))
    except ValueError:
        return None
    return d if d.tzinfo else None


def canonical_url(u):
    p = urlsplit(u)
    host = p.hostname or ''
    if p.scheme != 'https' or not (host == 'linkedin.com' or host.endswith('.linkedin.com')):
        raise ValueError('expected a public HTTPS LinkedIn URL')
    if p.username or p.password or p.port not in (None, 443):
        raise ValueError('unexpected authority')
    return urlunsplit(('https', 'www.linkedin.com', p.path.rstrip('/'), '', ''))


def cycle_label(path):
    m = re.search(r'(?:^|-)(v\d+)$', Path(path).name)
    return m.group(1) if m else Path(path).name


def is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and v == v


def brief(x, limit=25):
    """Keep expected/observed fields readable: long collections become a total plus a sample."""
    if isinstance(x, (set, frozenset)):
        x = sorted(x, key=str)
    if isinstance(x, (list, tuple)) and len(x) > limit:
        return {'total': len(x), 'first': list(x[:limit])}
    return x


def metric_errors(name, m):
    if not isinstance(m, dict) or 'value' not in m or 'status' not in m:
        return [name + ': metric must be an object with value and status']
    errs = []
    if m['status'] not in METRIC_STATUS:
        errs.append(name + ': unknown status ' + repr(m['status']))
    v = m['value']
    if v is not None and (not is_int(v) or v < 0):
        errs.append(name + ': value must be null or a non-negative integer')
    if (m['status'] == 'observed') != (v is not None):
        errs.append(name + ': observed status and value disagree (missing must stay null, never 0)')
    return errs


def post_errors(r):
    if not isinstance(r, dict):
        return ['record is not an object']
    errs = ['missing field ' + k for k in ('id', 'url', 'captured_at', 'source', 'author', 'published_at', 'text', 'metrics', 'media') if k not in r]
    if errs:
        return errs
    if not re.fullmatch(r'urn:li:activity:\d+', str(r['id'])):
        errs.append('invalid post id')
    try:
        if canonical_url(r['url']) != r['url']:
            errs.append('non-canonical url')
    except (ValueError, TypeError, AttributeError) as e:
        errs.append('url: ' + str(e))
    m = re.search(r'activity-(\d+)', str(r['url']))
    if not m or r['id'] != 'urn:li:activity:' + m.group(1):
        errs.append('URL and post id disagree')
    if parse_ts(r['captured_at']) is None:
        errs.append('captured_at must be an ISO time with a timezone')
    if r['published_at'] is not None and parse_ts(r['published_at']) is None:
        errs.append('published_at must be null or an ISO time with a timezone')
    if not isinstance(r['source'], dict) or not re.fullmatch(r'[0-9a-f]{64}', str(r['source'].get('sha256', ''))):
        errs.append('source.sha256 missing or malformed')
    if not isinstance(r['author'], dict):
        errs.append('author must be an object')
    if not isinstance(r['text'], str):
        errs.append('text must be a string')
    if not isinstance(r['media'], list):
        errs.append('media must be a list')
    if not isinstance(r['metrics'], dict):
        errs.append('metrics must be an object')
    else:
        for k, m in r['metrics'].items():
            errs += metric_errors(k, m)
    return errs


# --------------------------------------------------------------------------- release
class Release:
    def __init__(self, root=HERE, base=DEFAULT_BASE, template=None, as_of=None, hash_dataless=False,
                 dry_run=False, baseline_cycle='v2'):
        self.root = Path(root).resolve()
        self.base = Path(base).resolve()
        self.template = Path(template).resolve() if template else HERE / 'viewer-template.html'
        self.as_of_arg = as_of
        self.hash_dataless = hash_dataless
        self.dry_run = dry_run
        self.cycle = cycle_label(self.root)
        self.base_cycle = cycle_label(self.base)
        self.baseline_cycle = baseline_cycle
        self.cycle_order = [c for c in dict.fromkeys([baseline_cycle, self.base_cycle, self.cycle])]
        self.checks, self.warnings, self.gaps, self.inputs, self.outputs = [], [], [], [], []
        self.staged = {}
        self.counts = {}

    # ---- reporting
    def add(self, name, ok, expected=None, observed=None, detail=None, status=None):
        self.checks.append({'name': name, 'status': status or ('pass' if ok else 'fail'), 'expected': brief(expected),
                            'observed': brief(observed), **({'detail': detail} if detail else {})})
        return ok

    def warn(self, kind, ref, msg):
        self.warnings.append({'kind': kind, 'ref': ref, 'message': msg})

    def gap(self, kind, ref, reason):
        self.gaps.append({'kind': kind, 'ref': ref, 'reason': reason})

    def failed(self):
        return any(c['status'] == 'fail' for c in self.checks)

    def rel(self, p):
        return os.path.relpath(str(p), str(self.root))

    def rebase(self, owner, p):
        """Path written relative to `owner` -> path relative to this run (where index.html lives)."""
        return os.path.relpath(str((owner / p).resolve()), str(self.root))

    def resolve_in(self, owner, p):
        pp = Path(p)
        return pp if pp.is_absolute() else owner / pp

    def resolve_any(self, p, owners):
        """Records written by another lane may be relative to this run or to the base run; take the first that exists."""
        cands = [self.resolve_in(o, p) for o in owners]
        return next((c for c in cands if c.exists()), cands[0])

    # ---- input loading
    def read_input(self, path, role, kind='json', required=False):
        path = Path(path)
        rec = {'role': role, 'path': self.rel(path), 'status': 'missing', 'sha256': None, 'count': 0}
        self.inputs.append(rec)
        if not path.exists():
            if required:
                self.add('input_present:' + role, False, 'file present', 'missing', rec['path'])
                raise ReleaseAbort(role + ' is required')
            print('release: input missing, treated as empty: ' + rec['path'], flush=True)
            return []
        raw = path.read_bytes()
        rec['sha256'] = sha_bytes(raw)
        try:
            text = raw.decode('utf-8')
            data = [jloads(l) for l in text.splitlines() if l.strip()] if kind == 'ndjson' else jloads(text) if text.strip() else []
        except (ValueError, UnicodeDecodeError) as e:
            self.add('input_parses:' + role, False, 'valid JSON without duplicate keys', 'parse error', str(e))
            raise ReleaseAbort(role + ' unreadable')
        rec['count'] = len(data['records']) if isinstance(data, dict) and isinstance(data.get('records'), list) else len(data) if isinstance(data, list) else None
        rec['status'] = 'present' if data else 'empty'
        return data

    def read_list(self, path, role, keys=(), kind='json'):
        data = self.read_input(path, role, kind=kind)
        if isinstance(data, dict):
            data = next((data[k] for k in keys if isinstance(data.get(k), list)), data if data else [])
        if not isinstance(data, list):
            self.add('input_shape:' + role, False, 'a list of records', type(data).__name__, self.rel(path))
            raise ReleaseAbort(role + ' has the wrong shape')
        if any(not isinstance(x, dict) for x in data):
            self.add('input_shape:' + role, False, 'a list of objects', 'non-object element', self.rel(path))
            raise ReleaseAbort(role + ' has non-object elements')
        return data

    def load(self):
        r = self.root
        base = self.read_input(self.base / 'data/dataset.json', 'base_dataset', required=True)
        miss = [k for k in BASE_REQUIRED if k not in base]
        self.add('base_dataset_shape', not miss, BASE_REQUIRED, sorted(base), 'missing: ' + ', '.join(miss) if miss else None)
        if miss:
            raise ReleaseAbort('base dataset incomplete')
        self.b = base
        self.new_posts = self.read_list(r / 'data/new-posts.ndjson', 'new_posts', kind='ndjson')
        self.manifest = self.read_list(r / 'data/media-manifest.json', 'media_manifest', ('assets',))
        self.qual_in = self.read_list(r / 'data/qualification.json', 'qualification', ('records',))
        self.tx_index = self.read_list(r / 'transcripts/index.json', 'transcript_index', ('items',))
        self.snaps_in = self.read_list(r / 'data/snapshots.json', 'snapshots', ('snapshots',))
        self.vel_in = self.read_list(r / 'data/velocity.json', 'velocity', ('rows',))
        self.coh_in = self.read_list(r / 'data/cohorts.json', 'cohorts', ('cohorts',))
        self.qa_raw = self.read_input(r / 'data/transcript-qa.json', 'transcript_qa')  # list, or {records, gap_records, ...}
        self.queue_in = self.read_input(r / 'operations/account-qualification-queue.json', 'account_qualification_queue')
        # A report-only successor retains dated analytical evidence when no replacement
        # file exists. An explicit current file is authoritative, including empty input.
        for attr, key, path in [('snaps_in', 'snapshots', r/'data/snapshots.json'),
                                ('vel_in', 'velocity', r/'data/velocity.json'),
                                ('coh_in', 'cohorts', r/'data/cohorts.json'),
                                ('qa_raw', 'transcript_qa', r/'data/transcript-qa.json'),
                                ('queue_in', 'held_authors', r/'operations/account-qualification-queue.json')]:
            if not path.exists() and self.b.get(key):
                value = self.b[key]
                if key == 'snapshots':
                    value = [dict(x, raw_path=str(self.resolve_in(self.base, x['raw_path']))) if x.get('raw_path') else dict(x) for x in value]
                setattr(self, attr, value)
                self.warn('dated_analytical_input_inherited', key, 'No current replacement file; preserving dated base evidence, not claiming recomputation.')
        files = [r / 'analysis/media-reviews.json', r / 'data/media-reviews.json'] + [f for f in sorted(r.glob('analysis/*/reviews.json')) if not f.parent.name.startswith('semantic-')]
        self.review_in = []
        for f in files:
            if f.exists():
                self.review_in += [dict(x, _from=self.rel(f)) for x in self.read_list(f, 'media_reviews:' + self.rel(f), ('reviews',))]
        if not self.review_in:
            self.inputs.append({'role': 'media_reviews', 'path': 'analysis/media-reviews.json | analysis/*/reviews.json',
                                'status': 'missing', 'sha256': None, 'count': 0})
        cfg = r / 'pipeline/config.json'
        self.config = self.read_input(cfg, 'pipeline_config') if cfg.exists() else {}
        qcfg = self.config.get('qualification', {}) if isinstance(self.config, dict) else {}
        self.min_span = qcfg.get('velocity_min_observation_span_hours', 6)
        self.watch_allowed = bool((self.config.get('analysis', {}) if isinstance(self.config, dict) else {}).get('continuous_watch_claim_allowed', False))
        self.reg_posts = qcfg.get('account_regular_min_posts90', 8)
        self.reg_weeks = qcfg.get('account_regular_min_distinct_weeks90', 6)
        date_rx = r'\d{4}-\d{2}-\d{2}'
        if self.as_of_arg is not None and not re.fullmatch(date_rx, str(self.as_of_arg)):
            self.add('as_of_valid', False, 'YYYY-MM-DD', self.as_of_arg)
            raise ReleaseAbort('bad as_of')
        cfg_as_of = qcfg.get('as_of') if re.fullmatch(date_rx, str(qcfg.get('as_of'))) else None  # 'runtime-resolved-...' is not a date
        self.as_of = self.as_of_arg or cfg_as_of
        self.as_of_source = 'argument' if self.as_of_arg else 'pipeline_config' if cfg_as_of else 'latest_capture_date_europe_sofia'

    # ---- file verification (never hydrates iCloud-evicted files unless asked)
    def verify_files(self, items):
        """items: (label, path, expected_sha, expected_bytes). Returns counts and problem lists."""
        out = {'checked': 0, 'hash_verified': 0, 'skipped_dataless': 0, 'missing': [], 'hash_mismatch': [], 'size_mismatch': []}
        for label, path, sha, size in items:
            try:
                st = os.stat(path)
            except OSError:
                out['missing'].append(label)
                continue
            if not os.path.isfile(path):
                out['missing'].append(label)
                continue
            out['checked'] += 1
            if size is not None and st.st_size != size:
                out['size_mismatch'].append(label)
            if sha is None:
                continue
            if getattr(st, 'st_flags', 0) & SF_DATALESS and not self.hash_dataless:
                out['skipped_dataless'] += 1
                continue
            if sha_file(path) != sha:
                out['hash_mismatch'].append(label)
            else:
                out['hash_verified'] += 1
        return out

    def file_check(self, name, items, what):
        v = self.verify_files(items)
        bad = v['missing'] + v['hash_mismatch'] + v['size_mismatch']
        status = None
        if not bad and v['checked'] and v['hash_verified'] == 0 and v['skipped_dataless']:
            status = 'skipped'
        detail = None
        if v['skipped_dataless']:
            detail = '%d %s are evicted to iCloud (dataless): existence and size checked, bytes not re-read; use --hash-dataless to hydrate and hash' % (v['skipped_dataless'], what)
        self.add(name, not bad, 'every %s exists with matching size and sha256' % what, v, detail, status=status)
        return v

    # ---- build the corpus
    def build(self):
        b = self.b
        cmap = {'baseline': self.baseline_cycle, 'new': self.base_cycle}
        self.base_posts = []
        for p in b['posts']:
            q = dict(p)
            if isinstance(p.get('source'), dict) and p['source'].get('raw_path'):
                q['source'] = dict(p['source'], raw_path=str(self.resolve_in(self.base, p['source']['raw_path'])))
            q['cycle'] = p.get('cycle') or cmap.get(p.get('collection'), self.base_cycle)
            q['collection'] = 'baseline'
            self.base_posts.append(q)
        errs = {}
        self.v4_posts = []
        for p in self.new_posts:
            e = post_errors(p)
            if e:
                errs[p.get('id', '?')] = e
            self.v4_posts.append({**p, 'cycle': self.cycle, 'collection': 'new'})
        self.add('new_posts_schema_valid', not errs, 'every new post passes the post schema', errs or {'valid': len(self.v4_posts)})
        berrs = {p.get('id', '?'): post_errors(p) for p in self.base_posts if post_errors(p)}
        self.add('base_posts_schema_valid', not berrs, 'every base post passes the post schema', berrs or {'valid': len(self.base_posts)})
        self.posts = self.base_posts + self.v4_posts
        self.cycle_order = list(dict.fromkeys([p['cycle'] for p in self.posts] + [self.cycle]))
        self.pmap = {p['id']: p for p in self.posts if isinstance(p, dict) and 'id' in p}
        self.new_ids = {p['id'] for p in self.v4_posts if 'id' in p}
        # corpus-wide duplicate detection on four independent keys
        def dupes(fn, skip_empty=False):
            seen = defaultdict(list)
            for p in self.posts:
                try:
                    k = fn(p)
                except (KeyError, TypeError, ValueError):
                    k = None
                if k is None or (skip_empty and not k):
                    continue
                seen[k].append(p.get('id'))
            return {str(k)[:90]: v for k, v in seen.items() if len(v) > 1}, sum(len(v) for v in seen.values())
        specs = [('dedupe_activity_id', lambda p: p['id'], 'activity id'),
                 ('dedupe_attributed_share_urn', lambda p: p.get('attributed_urn') or None, 'attributed share URN'),
                 ('dedupe_canonical_url', lambda p: canonical_url(p['url']), 'canonical URL'),
                 ('dedupe_normalized_text_sha256', lambda p: sha_bytes(norm_text(p['text']).encode()) if norm_text(p['text']) else None, 'normalized text sha256')]
        for name, fn, label in specs:
            d, n = dupes(fn)
            self.add(name, not d, {'records': len(self.posts), 'duplicate_groups': 0}, {'keyed_records': n, 'duplicate_groups': len(d), 'groups': d},
                     'every post must be unique by ' + label)
        empty_text = [p['id'] for p in self.posts if not norm_text(p.get('text'))]
        if empty_text:
            self.warn('empty_text', empty_text[:10], '%d posts have no text; they are excluded from the text-hash duplicate check' % len(empty_text))
        if errs or berrs:  # duplicates are reported above first; joins below need well-formed records
            raise ReleaseAbort('post records are malformed; joins would be meaningless')
        # raw capture bytes of this run's posts (+ base posts when materialized locally)
        items = [(p['id'], self.resolve_in(self.root, p['source'].get('raw_path', '')), p['source'].get('sha256'), None) for p in self.v4_posts if isinstance(p.get('source'), dict)]
        self.file_check('new_posts_raw_capture_bytes', items, 'new-post raw capture')
        items = [(p['id'], self.resolve_in(self.base, p['source'].get('raw_path', '')), p['source'].get('sha256'), None) for p in self.base_posts if isinstance(p.get('source'), dict)]
        self.file_check('base_posts_raw_capture_bytes', items, 'base-post raw capture')
        self.build_media()
        self.build_transcripts()
        self.build_snapshots()
        self.build_velocity()
        self.build_held()
        self.build_qualification()
        self.build_accounts()
        self.build_prospects()

    # ---- media assets and per-asset analysis
    def build_media(self):
        base_assets = []
        for a in self.b['assets']:
            q = dict(a)
            q['path'] = self.rebase(self.base, a['path']) if a.get('path') else a.get('path')
            q['cycle'] = a.get('cycle') or {'baseline': self.baseline_cycle, 'new': self.base_cycle}.get(a.get('collection'), self.base_cycle)
            q['collection'] = 'baseline'
            base_assets.append(q)
        v4_assets = [dict(a, path=self.rebase(self.root, a['path']) if a.get('path') else a.get('path'), cycle=self.cycle, collection='new') for a in self.manifest]
        assets = base_assets + v4_assets
        ids = Counter(a.get('asset_id') for a in assets)
        dup = sorted(k for k, n in ids.items() if n > 1 or k is None)
        self.add('assets_unique_ids', not dup, 'unique asset_id across base and new manifests', dup or {'assets': len(assets)})
        orphans = sorted(a.get('asset_id') for a in assets if a.get('post_id') not in self.pmap)
        self.add('assets_reference_known_posts', not orphans, 'every asset belongs to a post in the corpus', orphans or {'assets': len(assets)})
        if dup or orphans:
            raise ReleaseAbort('asset identity is broken; media joins would be meaningless')
        self.amap = {a['asset_id']: a for a in assets if a.get('asset_id')}
        held_posts = set()
        items = [(a['asset_id'], self.root / a['path'], a.get('sha256'), a.get('bytes')) for a in v4_assets if a.get('status') == 'acquired']
        self.file_check('new_asset_files_exist_size_hash', items, 'new asset file')
        items = [(a['asset_id'], self.root / a['path'], a.get('sha256'), a.get('bytes')) for a in base_assets if a.get('status') == 'acquired']
        self.file_check('base_asset_files_exist_size_hash', items, 'base asset file')
        # reviews: base entries untouched, new entries joined by asset_id and bound to the asset bytes
        base_ids = {a['asset_id'] for a in base_assets}
        vis, vid = [], []
        for v in self.b['visual_reviews']:
            vis.append({**v, 'cycle': v.get('cycle') or self.cycle_of(v.get('collection')), 'collection': 'baseline'})
        for v in self.b['video_reviews']:
            vid.append({**v, 'cycle': v.get('cycle') or self.cycle_of(v.get('collection')), 'collection': 'baseline'})
        new_reviews, conflicts, ignored = {}, [], []
        for rv in self.review_in:
            aid = rv.get('asset_id')
            src = rv.pop('_from')
            if aid in base_ids:
                ignored.append(aid)
                continue
            if aid in new_reviews and canon(new_reviews[aid]) != canon(rv):
                conflicts.append(aid)
            new_reviews[aid] = rv
        if ignored:
            self.warn('review_for_base_asset_ignored', sorted(set(ignored))[:10], 'base assets keep their dated reviews; new review records for them are ignored')
        unknown = sorted(a for a in new_reviews if a not in self.amap)
        self.add('reviews_reference_known_assets', not unknown and not conflicts, 'every new review names a manifest asset, once',
                 {'unknown_assets': unknown, 'conflicting_duplicates': conflicts})
        self.media_gaps = [dict(g) for g in self.b.get('media_gaps', [])]
        bad_sha, watch = [], []
        for a in v4_assets:
            if a.get('kind') not in MEDIA_KINDS:
                continue
            aid, rv = a['asset_id'], new_reviews.get(a['asset_id'])
            if a.get('status') != 'acquired':
                self.media_gaps.append(self.media_gap(a, 'asset not acquired (status %s); nothing to analyse' % a.get('status')))
            elif rv is None:
                self.media_gaps.append(self.media_gap(a, 'no analysis record found in analysis inputs at release time (awaiting review)'))
            elif rv.get('review_status') != 'reviewed':
                self.media_gaps.append(self.media_gap(a, str(rv.get('reason') or rv.get('gap') or 'review status %s' % rv.get('review_status'))))
            else:
                h = rv.get('source_sha256') or rv.get('source_video_sha256') or (rv.get('source') or {}).get('sha256')
                if h != a.get('sha256'):
                    bad_sha.append(aid)
                if a['kind'] == 'video':
                    if (rv.get('full_watch') or rv.get('audio_review')) and not self.watch_allowed:
                        watch.append(aid)
                    vid.append({**self.norm_video(rv), 'asset_id': aid, 'post_id': rv.get('post_id') or a['post_id'], 'cycle': self.cycle, 'collection': 'new'})
                else:
                    vis.append({**self.norm_visual(rv), 'asset_id': aid, 'post_id': rv.get('post_id') or a['post_id'], 'cycle': self.cycle, 'collection': 'new'})
        self.add('reviews_bound_to_asset_bytes', not bad_sha, 'review source_sha256 equals the manifest sha256', bad_sha or {'reviews': len(new_reviews)})
        self.add('no_unsupported_watch_or_audio_claims', not watch, 'no new review claims continuous watching or listening unless the config allows it', watch or 'none')
        self.visual_reviews, self.video_reviews = vis, vid
        for a in assets:  # a manifest review_status can be stale (base assets say not_reviewed); derive it from the joined reviews
            a['manifest_review_status'] = a.get('review_status')
        reviewed = {v['asset_id'] for v in vis + vid}
        gap_ids = {g['asset_id'] for g in self.media_gaps}
        expected = {a['asset_id'] for a in assets if a.get('kind') in MEDIA_KINDS}
        self.add('every_media_asset_has_analysis_or_gap', expected == (reviewed | gap_ids) and not (reviewed & gap_ids) and len(vis + vid) == len(reviewed),
                 {'image_document_video_assets': len(expected)}, {'reviewed': len(reviewed), 'explicit_gaps': len(gap_ids),
                  'overlap': sorted(reviewed & gap_ids), 'unaccounted': sorted(expected - reviewed - gap_ids), 'extra': sorted((reviewed | gap_ids) - expected)})
        for a in assets:
            a['review_status'] = 'reviewed' if a['asset_id'] in reviewed else 'not_reviewed' if a.get('kind') in MEDIA_KINDS else 'not_applicable'
        for g in self.media_gaps:
            self.gap('media_not_reviewed', g['asset_id'], g['reason'])
        self.assets = assets

    def cycle_of(self, collection):
        return {'baseline': self.baseline_cycle, 'new': self.base_cycle}.get(collection, self.base_cycle)

    def media_gap(self, a, reason):
        return {'asset_id': a['asset_id'], 'post_id': a['post_id'], 'kind': a.get('kind'), 'review_status': 'not_reviewed', 'reason': reason, 'cycle': a.get('cycle')}

    @staticmethod
    def norm_visual(v):
        h = v.get('source_sha256') or (v.get('source') or {}).get('sha256')
        desc = v.get('description') or v.get('literal_and_structure') or {k: v[k] for k in ['literal_visible', 'interpretation', 'transfer_hypothesis', 'legibility_limits'] if k in v}
        return {**v, 'source_sha256': h, 'review_status': 'reviewed', 'description': desc}

    @staticmethod
    def norm_video(v):
        desc = v.get('description') or v.get('analysis')
        return {**v, 'source_sha256': v.get('source_sha256') or v.get('source_video_sha256'), 'review_status': 'reviewed', 'description': desc,
                'story_summary': v.get('story_summary') or (desc.get('format') if isinstance(desc, dict) else None)}

    # ---- transcripts, visible text, QA
    def build_transcripts(self):
        trans = []
        for t in self.b['transcripts']:
            q = dict(t)
            if t.get('source_path'):
                q['source_path'] = self.rebase(self.base, t['source_path'])
            q['cycle'] = t.get('cycle') or self.cycle_of(t.get('collection'))
            q['collection'] = 'baseline'
            trans.append(q)
        vreview = {v['asset_id']: v for v in self.video_reviews}
        problems = []
        for it in self.tx_index:
            aid = it.get('asset_id')
            a = self.amap.get(aid)
            if a is None or a.get('kind') != 'video':
                problems.append({'asset_id': aid, 'problem': 'not a video asset in the manifest'})
                continue
            path = self.root / it.get('path', '')
            if not path.is_file():
                problems.append({'asset_id': aid, 'problem': 'transcript file missing: ' + str(it.get('path'))})
                continue
            try:
                d = jloads(path.read_text(encoding='utf-8'))
            except ValueError as e:
                problems.append({'asset_id': aid, 'problem': str(e)})
                continue
            if d.get('source_video_sha256') != a.get('sha256') or (it.get('source_video_sha256') or a.get('sha256')) != a.get('sha256'):
                problems.append({'asset_id': aid, 'problem': 'transcript is bound to different video bytes'})
                continue
            duration = ((a.get('ffprobe') or {}).get('format') or {}).get('duration')
            try:
                ends = [s.get('end', 0) for s in d.get('segments') or []]
                over = round(max(max(ends, default=0) - float(duration), 0), 3) if duration is not None else None
            except (TypeError, ValueError):
                over = None
            text = d.get('text') or ''
            vr = vreview.get(aid, {})
            trans.append({**d, 'asset_id': aid, 'post_id': d.get('post_id') or a['post_id'], 'text': text, 'source_path': it['path'],
                          'cycle': self.cycle, 'collection': 'new', 'timing_overrun_seconds': over,
                          'timing_warning': 'ASR segments exceed source duration; repeated tail may be hallucinated. Original output preserved; audio verification required.' if over and over > .5 else None,
                          'onscreen_text_observed': vr.get('onscreen_text_observed') if not text.strip() else None})
        self.add('transcript_records_valid', not problems, 'every transcript index item binds to a manifest video and its bytes', problems or {'new_transcripts': len(self.tx_index)})
        ids = Counter(t.get('asset_id') for t in trans)
        dup = sorted(k for k, n in ids.items() if n > 1)
        self.add('transcripts_unique_per_asset', not dup, 'at most one transcript record per video', dup or {'transcripts': len(trans)})
        missing = [t['asset_id'] for t in trans if not t.get('source_path') or not (self.root / t['source_path']).exists()]
        self.add('transcript_source_files_exist', not missing, 'every transcript source file exists', missing or {'transcripts': len(trans)})
        # every video: transcript text, visible text, or an explicit gap record
        self.transcripts = trans
        tmap = {t['asset_id']: t for t in trans}
        vtext = {v['asset_id']: v.get('onscreen_text_observed') for v in self.video_reviews}
        self.transcript_gaps = []
        videos = [a for a in self.assets if a.get('kind') == 'video']
        for a in videos:
            t, aid = tmap.get(a['asset_id']), a['asset_id']
            has_text = bool(t and str(t.get('text') or '').strip())
            has_visible = bool(vtext.get(aid)) or bool(t and t.get('onscreen_text_observed'))
            if has_text or has_visible:
                continue
            if a.get('status') != 'acquired':
                reason = 'video not acquired (status %s)' % a.get('status')
            elif t is None:
                reason = 'no transcript record and no visible-text record for this video at release time'
            else:
                reason = str(t.get('gap') or 'transcript text empty and no visible text recorded')
            self.transcript_gaps.append({'asset_id': aid, 'post_id': a['post_id'], 'reason': reason, 'transcript_record_present': t is not None, 'cycle': a.get('cycle')})
            self.gap('transcript_missing', aid, reason)
        gap_ids = {g['asset_id'] for g in self.transcript_gaps}
        covered = {a['asset_id'] for a in videos} - gap_ids
        self.add('every_video_has_transcript_or_visible_text_or_gap', {a['asset_id'] for a in videos} == (covered | gap_ids) and not (covered & gap_ids) and all(g['reason'] for g in self.transcript_gaps),
                 {'videos': len(videos)}, {'with_transcript_or_visible_text': len(covered), 'explicit_gaps': len(gap_ids)})
        self.build_transcript_qa(tmap)

    def build_transcript_qa(self, tmap):
        """QA records attach by asset_id. Original transcript text is never modified; an alternative decode is
        carried beside it (loaded from its file, hash-bound) and never supersedes the original."""
        raw = self.qa_raw
        if isinstance(raw, dict):
            recs, gaprecs = raw.get('records', raw.get('items', [])), raw.get('gap_records') or []
            if not isinstance(recs, list) or not isinstance(gaprecs, list):
                self.add('transcript_qa_valid', False, 'records and gap_records are lists', {k: type(v).__name__ for k, v in raw.items()})
                raise ReleaseAbort('qa shape')
        else:
            recs, gaprecs = raw, []
        if any(not isinstance(x, dict) for x in recs + gaprecs):
            self.add('transcript_qa_valid', False, 'QA entries are objects', 'non-object entry')
            raise ReleaseAbort('qa shape')
        qa, bad, files = [], [], []
        for x in recs:
            aid = x.get('asset_id')
            a = self.amap.get(aid)
            if a is None or a.get('kind') != 'video':
                bad.append({'asset_id': aid, 'problem': 'unknown video asset'})
                continue
            if x.get('post_id') not in (None, a['post_id']):
                bad.append({'asset_id': aid, 'problem': 'post_id differs from the asset post'})
                continue
            if not isinstance(x.get('flags', []), list) or not isinstance(x.get('status'), str):
                bad.append({'asset_id': aid, 'problem': 'status must be a string and flags a list'})
                continue
            if x.get('source_video_sha256') not in (None, a.get('sha256')):
                bad.append({'asset_id': aid, 'problem': 'QA is bound to different video bytes'})
                continue
            rec = {**x, 'post_id': a['post_id'], 'flags': x.get('flags', [])}
            if x.get('transcript_path'):
                tp = self.resolve_any(x['transcript_path'], [self.root, self.base])
                files.append((aid + ' transcript', tp, x.get('transcript_sha256'), None))
                rec['transcript_path'] = self.rel(tp.resolve())  # relative to index.html like every other path
            alt = x.get('alternative')
            if isinstance(alt, str):
                alt = {'text': alt}
            if isinstance(alt, dict):
                alt = dict(alt)
                if alt.get('supersedes_original'):
                    bad.append({'asset_id': aid, 'problem': 'an alternative decode must not supersede the original'})
                    continue
                if alt.get('path'):
                    ap = self.resolve_any(alt['path'], [self.root, self.base])
                    files.append((aid + ' alternative', ap, alt.get('sha256'), None))
                    alt['path'] = self.rel(ap.resolve())
                    try:
                        d = jloads(ap.read_text(encoding='utf-8'))
                    except (OSError, ValueError) as e:
                        bad.append({'asset_id': aid, 'problem': 'alternative file unreadable: %s' % e})
                        continue
                    if d.get('asset_id') not in (None, aid):
                        bad.append({'asset_id': aid, 'problem': 'alternative file belongs to another asset'})
                        continue
                    alt.update({'text': d.get('text'), 'origin': d.get('origin'), 'language': d.get('language'),
                                'segment_count': len(d.get('segments') or []),
                                'last_segment_end': max([s.get('end', 0) for s in d.get('segments') or []], default=None)})
                alt.setdefault('review_status', 'alternative_decode_unreviewed')
                alt['supersedes_original'] = False
                rec['alternative'] = alt
            qa.append(rec)
        for g in gaprecs:  # QA that could not be computed stays visible as its own row
            a = self.amap.get(g.get('asset_id'))
            if a is None:
                bad.append({'asset_id': g.get('asset_id'), 'problem': 'QA gap record names an unknown asset'})
                continue
            qa.append({'post_id': a['post_id'], 'asset_id': g['asset_id'], 'status': 'qa_gap', 'flags': [], 'details': g})
            self.gap('transcript_qa_gap', g['asset_id'], str(g.get('reason') or 'QA gap record'))
        ids = Counter(x['asset_id'] for x in qa)
        dup = sorted(k for k, n in ids.items() if n > 1)
        self.add('transcript_qa_valid', not bad and not dup, 'every QA record names one known video once, bound to its bytes; alternatives never supersede originals',
                 {'invalid': bad, 'duplicates': dup} if (bad or dup) else {'qa_records': len(qa), 'with_alternative': sum(bool(x.get('alternative')) for x in qa)})
        if files:
            self.file_check('transcript_qa_files_exist_hash', files, 'QA-referenced transcript/alternative file')
        self.transcript_qa = sorted(qa, key=lambda x: (x['post_id'], x['asset_id']))
        no_t = [x['asset_id'] for x in self.transcript_qa if x['asset_id'] not in tmap]
        if no_t:
            self.warn('qa_without_transcript', no_t, 'QA records exist for videos with no transcript record')

    # ---- snapshots and observed velocity
    def build_snapshots(self):
        snaps, errs = [], {}
        for s in self.snaps_in:
            e = []
            for k in ('snapshot_id', 'post_id', 'captured_at', 'capture_kind', 'raw_sha256'):
                if not s.get(k):
                    e.append('missing ' + k)
            if s.get('post_id') not in self.pmap:
                e.append('unknown post')
            if s.get('capture_kind') not in SNAPSHOT_KINDS:
                e.append('capture_kind must be one of ' + '|'.join(SNAPSHOT_KINDS))
            if parse_ts(s.get('captured_at')) is None:
                e.append('captured_at must include a timezone')
            if not isinstance(s.get('metrics', {}), dict):
                e.append('metrics must be an object')
            else:
                for k, m in s.get('metrics', {}).items():
                    e += metric_errors(k, m)
            if e:
                errs[s.get('snapshot_id') or '?'] = e
            snaps.append(s)
        self.add('snapshots_valid', not errs, 'every snapshot has identity, kind, UTC-aware time, a known post and consistent metrics', errs or {'snapshots': len(snaps)})
        if errs:
            raise ReleaseAbort('snapshots are malformed; velocity cannot be checked against them')
        ids = Counter(s.get('snapshot_id') for s in snaps)
        dup = sorted(k for k, n in ids.items() if n > 1)
        self.add('snapshots_unique_ids', not dup, 'unique snapshot_id', dup or {'snapshots': len(snaps)})
        self.snapshots = sorted(snaps, key=lambda s: (str(s.get('post_id')), parse_ts(s.get('captured_at')) or datetime.min.replace(tzinfo=timezone.utc), str(s.get('snapshot_id'))))
        raw = []
        for s in self.snapshots:
            rp = s.get('raw_path')
            if rp:
                raw.append((s['snapshot_id'], self.resolve_in(self.root, rp), s['raw_sha256'], None))
        if raw:
            self.file_check('snapshot_raw_capture_bytes', raw, 'snapshot raw capture')
        else:
            self.add('snapshot_raw_capture_bytes', True, 'raw_path present on snapshots', 'no snapshot carries a raw_path', status='skipped')
        mism = [s['snapshot_id'] for s in self.snapshots if s['capture_kind'] == 'baseline_import' and s.get('post_id') in self.pmap
                and self.pmap[s['post_id']].get('source', {}).get('sha256') != s['raw_sha256']]
        if mism:
            self.warn('baseline_import_differs_from_post_record', mism[:10], 'baseline_import snapshot raw hash differs from the post record capture')
        by_post = defaultdict(list)
        for s in self.snapshots:
            by_post[s['post_id']].append(s)
        self.snap_by_post = by_post
        for pid in sorted(set(self.pmap) - set(by_post)):
            self.gap('snapshot_missing', pid, 'post has no snapshot record; the card shows its capture as a single implicit row')

    def build_velocity(self):
        rows, errs = [], {}
        for v in self.vel_in:
            e, pid = [], v.get('post_id')
            if pid not in self.pmap:
                e.append('unknown post')
            if not isinstance(v.get('eligible'), bool):
                e.append('eligible must be true or false')
            elif v['eligible']:
                need = ['reactions_first', 'reactions_last', 'reaction_delta', 'reactions_per_hour', 'span_hours', 'first_captured_at', 'last_captured_at']
                e += ['eligible row lacks ' + k for k in need if v.get(k) is None]
                if not e:
                    d = v['reactions_last'] - v['reactions_first']
                    if not (is_int(v['reactions_first']) and is_int(v['reactions_last']) and v['reaction_delta'] == d):
                        e.append('reaction_delta is not reactions_last - reactions_first')
                    if not is_num(v['span_hours']) or v['span_hours'] <= 0:
                        e.append('span_hours must be positive')
                    else:
                        want = d / v['span_hours']
                        if not is_num(v['reactions_per_hour']) or abs(v['reactions_per_hour'] - want) > 0.01 + 0.01 * abs(want):
                            e.append('reactions_per_hour %r disagrees with delta/span %.4f' % (v['reactions_per_hour'], want))
                        if v['span_hours'] < self.min_span:
                            e.append('eligible span %.2f h is below the configured minimum %s h' % (v['span_hours'], self.min_span))
                    t0, t1 = parse_ts(v['first_captured_at']), parse_ts(v['last_captured_at'])
                    ss = self.snap_by_post.get(pid, [])
                    f = [s for s in ss if parse_ts(s['captured_at']) == t0]
                    l = [s for s in ss if parse_ts(s['captured_at']) == t1]
                    if t0 is None or t1 is None or not t1 > t0:
                        e.append('first/last captured_at must be ordered UTC-aware times')
                    elif not any((s.get('metrics', {}).get('reactions') or {}).get('value') == v['reactions_first'] for s in f) or \
                            not any((s.get('metrics', {}).get('reactions') or {}).get('value') == v['reactions_last'] for s in l):
                        e.append('velocity endpoints are not backed by snapshots of this post with the same reaction counts')
                    elif abs((t1 - t0).total_seconds() / 3600 - v['span_hours']) > 0.05 + 0.01 * v['span_hours']:
                        e.append('span_hours disagrees with the snapshot times')
            else:
                if not v.get('reason'):
                    self.warn('velocity_reason_missing', pid, 'ineligible velocity row has no reason; the card shows "reason not recorded"')
            if is_int(v.get('snapshots')) and v['snapshots'] != len(self.snap_by_post.get(pid, [])):
                e.append('row counts %d snapshots but %d are attached' % (v['snapshots'], len(self.snap_by_post.get(pid, []))))
            if e:
                errs[pid or '?'] = e
            rows.append(v)
        self.add('velocity_rows_valid', not errs, 'rows reference known posts; eligible rows are arithmetic- and snapshot-consistent', errs or {'rows': len(rows)})
        ids = Counter(v.get('post_id') for v in rows)
        dup = sorted(k for k, n in ids.items() if n > 1)
        self.add('velocity_unique_per_post', not dup, 'one velocity row per post', dup or {'rows': len(rows)})
        self.velocity = sorted(rows, key=lambda v: str(v.get('post_id')))
        vmap = {v.get('post_id'): v for v in self.velocity}
        coh, cerr = [], {}
        for c in self.coh_in:
            e = []
            mem = c.get('members')
            if not isinstance(mem, list):
                e.append('members must be a list')
                mem = []
            if c.get('n') != len(mem):
                e.append('n %r != members %d' % (c.get('n'), len(mem)))
            if not is_int(c.get('min_n')) or not isinstance(c.get('ranked'), bool) or not c.get('cohort'):
                e.append('cohort, ranked (bool) and min_n (int) are required')
            elif c['ranked'] and c.get('n', 0) < c['min_n']:
                e.append('ranked cohort has n < min_n')
            unknown = [m for m in mem if m not in self.pmap]
            if unknown:
                e.append('unknown members: %s' % unknown[:5])
            wrong = [m for m in mem if m in vmap and vmap[m].get('cohort') not in (None, c.get('cohort'))]
            if wrong:
                e.append('members whose velocity row names another cohort: %s' % wrong[:5])
            if e:
                cerr[c.get('cohort') or '?'] = e
            coh.append(c)
        self.add('cohorts_valid', not cerr, 'members known; n equals members; ranked implies n >= min_n', cerr or {'cohorts': len(coh)})
        ids = Counter(c.get('cohort') for c in coh)
        dup = sorted(k for k, n in ids.items() if n > 1)
        self.add('cohorts_unique_names', not dup, 'one record per cohort', dup or {'cohorts': len(coh)})
        self.cohorts = sorted(coh, key=lambda c: str(c.get('cohort')))
        cnames = {c.get('cohort') for c in self.cohorts}
        stray = sorted({v['cohort'] for v in self.velocity if v.get('cohort') and v['cohort'] not in cnames})
        if stray:
            self.warn('velocity_cohort_not_listed', stray[:10], 'velocity rows name cohorts that have no cohorts.json record')

    # ---- held authors
    def build_held(self):
        raw = self.queue_in
        if isinstance(raw, dict):
            items = next((raw[k] for k in ('held', 'queue', 'items', 'records', 'authors', 'posts') if isinstance(raw.get(k), list)), None)
            if items is None and raw:
                self.add('held_queue_shape', False, 'a list, or an object holding a list', sorted(raw))
                raise ReleaseAbort('queue shape')
            items = items or []
        else:
            items = raw
        groups = {}
        for i, it in enumerate(items):
            if not isinstance(it, dict):
                continue
            pids = list(it.get('post_ids') or [])
            pid = it.get('post_id') or (it.get('id') if str(it.get('id', '')).startswith('urn:li:activity:') else None)
            if pid:
                pids.append(pid)
            post = self.pmap.get(pids[0]) if pids else None
            author = it.get('author') if isinstance(it.get('author'), dict) else {}
            url = it.get('author_url') or author.get('url') or (post or {}).get('author', {}).get('url')
            name = it.get('author_name') or author.get('name') or (it.get('author') if isinstance(it.get('author'), str) else None) or (post or {}).get('author', {}).get('name')
            key = (urlsplit(url).path.rstrip('/') if url else None) or 'unknown:%s' % (pids[0] if pids else i)
            g = groups.setdefault(key, {'author_key': key, 'author_name': name, 'author_url': url, 'status': it.get('status') or 'held_before_media',
                                        'reason': it.get('reason') or it.get('hold_reason') or it.get('required') or 'new author awaiting account qualification; media not collected',
                                        'queued_at': it.get('queued_at') or it.get('held_at'), 'posts': []})
            for p in pids:
                if p not in [x['post_id'] for x in g['posts']]:
                    g['posts'].append({'post_id': p, 'url': it.get('url') or (self.pmap.get(p) or {}).get('url'), 'in_corpus': p in self.pmap,
                                       'published_at': it.get('published_at') or (self.pmap.get(p) or {}).get('published_at'),
                                       'media_downloaded': it.get('media_downloaded')})
        for g in groups.values():
            g['post_ids'] = [x['post_id'] for x in g['posts']]
            g['posts_missing_from_corpus'] = [x['post_id'] for x in g['posts'] if not x['in_corpus']]
        self.held_authors = sorted(groups.values(), key=lambda g: g['author_key'])
        held = {p for g in self.held_authors for p in g['post_ids']}
        with_media = sorted(a['asset_id'] for a in self.assets if a.get('post_id') in held)
        claimed = sorted(x['post_id'] for g in self.held_authors for x in g['posts'] if x.get('media_downloaded') is True)
        self.add('held_posts_have_no_media', not with_media and not claimed, 'media is held until account qualification: no asset belongs to a held post',
                 {'assets_of_held_posts': with_media, 'queue_says_media_downloaded': claimed} if (with_media or claimed) else {'held_posts': len(held)})
        for g in self.held_authors:
            if g['posts_missing_from_corpus']:
                self.warn('held_post_not_in_corpus', g['author_key'], 'queue lists posts that are not in new-posts.ndjson: %s' % g['posts_missing_from_corpus'][:5])
        self.held_ids = held

    # ---- qualification, accounts, prospects
    def build_qualification(self):
        qmap = {q['post_id']: dict(q) for q in self.b['qualification'] if isinstance(q, dict) and 'post_id' in q}
        unknown = sorted(q.get('post_id') for q in self.qual_in if q.get('post_id') not in self.pmap)
        self.add('qualification_references_known_posts', not unknown, 'every qualification record names a corpus post', unknown or {'records': len(self.qual_in)})
        for q in self.qual_in:
            if q.get('post_id') in self.pmap:
                qmap[q['post_id']] = dict(q)
        for p in self.posts:
            if p['id'] not in qmap:
                qmap[p['id']] = {'post_id': p['id'], 'reference_class': 'unqualified_no_record', 'age_days': None, 'publication_date_verified': None,
                                 'trending_status': 'not_established', 'sales_effectiveness': 'unknown', 'topic_candidates': [],
                                 'qualification_gap': 'no qualification record at release time'}
                self.gap('qualification_missing', p['id'], 'no qualification record at release time')
        extra = sorted(set(qmap) - set(self.pmap))
        self.add('qualification_covers_every_post', not extra and set(qmap) == set(self.pmap), {'posts': len(self.pmap)}, {'records': len(qmap), 'extra': extra})
        self.qualification = [qmap[p['id']] for p in self.posts]

    def build_accounts(self):
        if self.as_of:
            asof = self.as_of
        else:  # deterministic from inputs: newest capture, as a Europe/Sofia calendar date (the pipeline's runtime zone)
            from zoneinfo import ZoneInfo
            stamps = [parse_ts(x.get('captured_at')) for x in self.posts + self.snapshots]
            asof = max([t for t in stamps if t] + [datetime(1970, 1, 1, tzinfo=timezone.utc)]).astimezone(ZoneInfo('Europe/Sofia')).date().isoformat()
        self.as_of = asof
        end = parse_ts(asof + 'T23:59:59+00:00')

        def age(p):
            d = parse_ts(p.get('published_at'))
            return (end - d).total_seconds() / 86400 if d else None
        groups = defaultdict(list)
        for p in self.posts:
            groups[urlsplit(p['author'].get('url') or '').path.rstrip('/') or '(unknown author)'].append(p)
        accounts = []
        for key in sorted(groups):
            ps = groups[key]
            fresh = [p for p in ps if age(p) is not None and 0 <= age(p) <= 90]
            weeks = {parse_ts(p['published_at']).strftime('%G-%V') for p in fresh}
            reactions = [p['metrics'].get('reactions', {}).get('value') for p in ps if p['metrics'].get('reactions', {}).get('value') is not None]
            cycles = sorted({p['cycle'] for p in ps}, key=self.cycle_order.index)
            accounts.append({'id': sha_bytes(key.encode())[:16], 'name': ps[0]['author'].get('name'), 'url': ps[0]['author'].get('url'),
                             'first_cycle': cycles[0], 'cycles': cycles, 'collection': 'new' if cycles[0] == self.cycle else 'baseline', 'posts': len(ps),
                             'within90': len(fresh), 'distinct_weeks90': len(weeks),
                             'observed_regular_sample_threshold_met': len(fresh) >= self.reg_posts and len(weeks) >= self.reg_weeks,
                             'regularity_limit': 'A sample can show repeated posting; insufficient samples do not prove inactivity or complete cadence. Threshold is a proposed operating rule.',
                             'sample_median_reactions': statistics.median(reactions) if reactions else None, 'trending_status': 'not_established'})
        self.accounts = accounts
        old = {a['id']: a for a in self.b['accounts']}
        drift = sorted(i for i, a in old.items() if i in {x['id'] for x in accounts} and
                       {k: a.get(k) for k in ('posts', 'within90', 'distinct_weeks90')} != {k: next(x for x in accounts if x['id'] == i)[k] for k in ('posts', 'within90', 'distinct_weeks90')})
        self.add('accounts_cover_every_post_author', sum(a['posts'] for a in accounts) == len(self.posts), {'posts': len(self.posts)}, {'accounts': len(accounts), 'posts_assigned': sum(a['posts'] for a in accounts)})
        if drift:
            self.warn('account_statistics_changed', drift, 'base account counts differ now (new posts for the account, or a later as_of); recomputed values are used')

    def build_prospects(self):
        pros = [dict(p) for p in self.b['prospects']]
        ids = Counter(p.get('id') for p in pros)
        dup = sorted(k for k, n in ids.items() if n > 1)
        self.add('prospects_unique_ids', not dup, 'unique prospect id', dup or {'prospects': len(pros)})

        def keys(x, acc):
            if isinstance(x, dict):
                for k, v in x.items():
                    acc.add(k.lower())
                    keys(v, acc)
            elif isinstance(x, list):
                for v in x:
                    keys(v, acc)
            return acc
        forbidden = {'media', 'posts', 'post_text', 'post_history', 'employees', 'employee_list', 'images', 'videos', 'assets'}
        bad = sorted({p.get('id') for p in pros if keys(p, set()) & forbidden})
        self.add('prospects_hold_no_posts_or_media', not bad, 'target-audience records carry description, links and qualification evidence only', bad or {'prospects': len(pros)})
        self.prospects = pros

    # ---- path checks that apply to what the page links
    def check_paths(self):
        used = [a['path'] for a in self.assets if a.get('kind') in MEDIA_KINDS and a.get('path')] + [t['source_path'] for t in self.transcripts if t.get('source_path')]
        rx = re.compile(SAFE_PATH_PATTERN)
        unsafe = sorted(p for p in used if not rx.match(p))
        self.add('viewer_paths_match_safe_pattern', not unsafe, 'every linked media/transcript path matches the viewer pattern', unsafe or {'paths': len(used)})
        missing = sorted(p for p in used if not (self.root / p).exists())
        self.add('media_paths_resolve_from_index_html', not missing, 'every path referenced by index.html exists relative to the run folder', missing or {'paths': len(used)})

    # ---- summary, dataset
    def make_summary(self):
        b = self.b['summary']
        kinds = Counter(a.get('kind') for a in self.assets)
        new_assets = Counter(a.get('kind') for a in self.assets if a['cycle'] == self.cycle)
        by_cycle = Counter(p['cycle'] for p in self.posts)
        sn = Counter(s['capture_kind'] for s in self.snapshots)
        multi = sum(1 for v in self.snap_by_post.values() if len(v) > 1)
        elig = [v for v in self.velocity if v.get('eligible') is True]
        fit = sum(p.get('fit_status') == 'observed_icp_fit' for p in self.prospects)
        no_audio = sum(t.get('origin') == 'no_audio_stream_in_acquired_file' for t in self.transcripts)
        return {
            'run_id': self.root.name, 'base_run_id': self.base.name, 'as_of': self.as_of, 'cycle': self.cycle,
            'posts_by_cycle': dict(by_cycle), 'total_posts': len(self.posts), 'new_posts': len(self.v4_posts), 'baseline_posts': len(self.base_posts),
            'total_accounts': len(self.accounts), 'new_accounts': sum(a['collection'] == 'new' for a in self.accounts),
            'new_undated': sum(parse_ts(p.get('published_at')) is None for p in self.v4_posts),
            'assets': dict(kinds), 'new_assets': dict(new_assets), 'unique_payload_hashes': len({a.get('sha256') for a in self.assets if a.get('sha256')}),
            'visual_reviews': len(self.visual_reviews), 'video_reviews': len(self.video_reviews), 'media_gaps': len(self.media_gaps),
            'transcripts': len(self.transcripts), 'transcript_texts': sum(bool(str(t.get('text') or '').strip()) for t in self.transcripts),
            'no_audio_records': no_audio, 'transcript_gaps': len(self.transcript_gaps),
            'transcript_timing_flags': sum(bool(t.get('timing_warning')) for t in self.transcripts),
            'transcript_qa_records': len(self.transcript_qa), 'transcript_qa_flagged': sum(bool(x.get('flags')) for x in self.transcript_qa),
            'transcripts_with_alternative': sum(x.get('alternative') not in (None, '', {}) for x in self.transcript_qa),
            'snapshots': len(self.snapshots), 'snapshots_by_kind': dict(sn), 'posts_with_snapshots': len(self.snap_by_post), 'posts_reobserved': multi,
            'velocity_rows': len(self.velocity), 'velocity_eligible': len(elig), 'velocity_ineligible': len(self.velocity) - len(elig),
            'velocity_ineligible_reasons': dict(Counter(str(v.get('reason') or 'reason not recorded') for v in self.velocity if v.get('eligible') is not True)),
            'cohorts': len(self.cohorts), 'cohorts_ranked': sum(bool(c.get('ranked')) for c in self.cohorts), 'cohorts_not_ranked': sum(not c.get('ranked') for c in self.cohorts),
            'held_authors': len(self.held_authors), 'held_posts': len(self.held_ids),
            'prospects': len(self.prospects), 'prospect_observed_fit': fit, 'prospect_holds': len(self.prospects) - fit,
            'full_continuous_watch': sum(bool(v.get('full_watch')) for v in self.video_reviews), 'audio_listened': sum(bool(v.get('audio_review')) for v in self.video_reviews),
            'trend_velocity_rank_verified': False, 'schedule_active': bool(b.get('schedule_active', False)),
            'external_supervisor_wakeup': bool(b.get('external_supervisor_wakeup', False)), 'paid_provider_spend': b.get('paid_provider_spend', 0),
        }

    def make_dataset(self):
        cyc = [{'id': c, 'posts': sum(p['cycle'] == c for p in self.posts), 'is_current': c == self.cycle} for c in self.cycle_order]
        links = [{'href': h, 'label': l} for h, l in LINK_CANDIDATES if h in PRODUCED or (self.root / h).exists()]
        ds = {'summary': self.make_summary(),
                'meta': {'schema_version': SCHEMA_VERSION, 'run_id': self.root.name, 'cycle': self.cycle, 'cycles': cyc, 'as_of': self.as_of, 'as_of_source': self.as_of_source,
                         'safe_path_pattern': SAFE_PATH_PATTERN, 'links': links, 'min_velocity_span_hours': self.min_span,
                         'velocity_wording': 'observed reaction change {delta} over {span} h ({rate}/h); public counter, not reach/impressions/trend rank'},
                'posts': self.posts, 'snapshots': self.snapshots, 'velocity': self.velocity, 'cohorts': self.cohorts, 'accounts': self.accounts,
                'assets': self.assets, 'visual_reviews': self.visual_reviews, 'video_reviews': self.video_reviews, 'media_gaps': self.media_gaps,
                'transcripts': self.transcripts, 'transcript_gaps': self.transcript_gaps, 'transcript_qa': self.transcript_qa,
                'qualification': self.qualification, 'prospects': self.prospects, 'held_authors': self.held_authors}
        src = self.root / 'analysis/post-interpretations.json'
        interpretations = self.read_list(src, 'semantic_interpretations') if src.exists() else []
        required = self.config.get('analysis', {}).get('require_semantic_coverage', False)
        contract = self.root / 'analysis/taxonomy-contract.json'
        issues = performance.validate_interpretations(self.posts, interpretations, jloads(contract.read_text())) if interpretations and contract.exists() else ([] if not required else ['Required semantic rows or contract are absent.'])
        self.add('semantic_source_coverage', not issues, 'exact post/text-hash coverage and controlled categories', issues or {'posts': len(interpretations)})
        ds['interpretations'] = interpretations
        ds['performance'] = performance.assess(self.posts, self.snapshots, self.velocity, interpretations, assets=self.assets)
        decisions = self.root / 'analysis/author-decisions.json'
        ds['author_decisions'] = self.read_list(decisions, 'author_decisions') if decisions.exists() else []
        ds['summary']['semantic_interpretations'] = len(interpretations)
        ds['summary']['performance_assessments'] = len(ds['performance'])
        ds['summary']['strong_sample_references'] = sum(x['performance_status'] == 'strong_sample_reference' for x in ds['performance'])
        ds['summary']['independent_pattern_representatives'] = sum(x.get('pattern_representative', True) for x in interpretations)
        return ds

    def check_entity_keys(self, ds):
        bad = {}
        for key, _t, kfn, _p in ENTITIES:
            try:
                ks = [kfn(r) for r in ds[key]]
            except (KeyError, TypeError) as e:
                bad[key] = 'missing key field: %s' % e
                continue
            d = sorted(k for k, n in Counter(ks).items() if n > 1 or k is None)
            if d:
                bad[key] = d[:10]
        self.add('entity_keys_unique_and_present', not bad, 'every dataset entity has a unique non-null key', bad or {e[0]: len(ds[e[0]]) for e in ENTITIES})
        return not bad

    # ---- exports (staged as *.tmp; promoted only when every check passed)
    def stage(self, rel, data, mode='w'):
        path = self.root / rel
        tmp = path.with_name(path.name + '.tmp')
        path.parent.mkdir(parents=True, exist_ok=True)
        if mode == 'wb':
            tmp.write_bytes(data)
        else:
            with tmp.open('w', encoding='utf-8', newline='') as f:
                f.write(data)
        self.staged[rel] = tmp
        return tmp

    def write_csv(self, rel, fields, rows):
        import io
        buf = io.StringIO()
        w = csv.writer(buf, lineterminator='\n')
        w.writerow(fields)
        for r in rows:
            w.writerow(["'" + v if isinstance(v, str) and v[:1] in ('=', '+', '-', '@') else ('' if v is None else v) for v in (r.get(f) for f in fields)])
        self.stage(rel, buf.getvalue())

    def export(self, ds):
        self.stage('data/dataset.json', json.dumps(ds, indent=2, ensure_ascii=False) + '\n')
        pr = lambda p: {'id': p['id'], 'cycle': p['cycle'], 'collection': p['collection'], 'author': p['author'].get('name'), 'url': p['url'], 'published_at': p['published_at'],
                        'captured_at': p['captured_at'], 'reactions': p['metrics'].get('reactions', {}).get('value'), 'comments': p['metrics'].get('comments', {}).get('value'),
                        'reposts': p['metrics'].get('reposts', {}).get('value'), 'text': p['text'], 'raw_sha256': p['source']['sha256']}
        pf = ['id', 'cycle', 'collection', 'author', 'url', 'published_at', 'captured_at', 'reactions', 'comments', 'reposts', 'text', 'raw_sha256']
        self.write_csv('data/posts.csv', pf, [pr(p) for p in self.posts])
        self.write_csv('data/new-posts.csv', pf, [pr(p) for p in self.v4_posts])
        sf = ['snapshot_id', 'post_id', 'captured_at', 'capture_kind', 'reactions', 'comments', 'reposts', 'source_run', 'raw_sha256', 'parser_version', 'published_at', 'text_sha256']
        self.write_csv('data/snapshots.csv', sf, [{**s, **{m: (s.get('metrics', {}).get(m) or {}).get('value') for m in METRIC_NAMES}} for s in self.snapshots])
        vf = ['post_id', 'eligible', 'reason', 'first_captured_at', 'last_captured_at', 'span_hours', 'reactions_first', 'reactions_last', 'reaction_delta', 'reactions_per_hour',
              'comments_delta', 'age_days_at_first_capture', 'media_kind', 'cohort', 'publication_date_status']
        self.write_csv('data/velocity.csv', vf, self.velocity)
        self.stage('data/performance.json', json.dumps(ds['performance'], ensure_ascii=False, indent=2) + '\n')
        self.stage('data/interpretations.json', json.dumps(ds['interpretations'], ensure_ascii=False, indent=2) + '\n')
        im = {x['post_id']: x for x in ds['interpretations']}
        pm = {x['post_id']: x for x in ds['performance']}
        fields = ['post_id', 'author', 'url', 'primary_topic', 'editorial_job', 'intended_reader', 'reference_value', 'content_summary', 'qualification_reason', 'media_role', 'media_evidence_basis', 'hook_pattern', 'claim_caveat', 'adaptation_pattern', 'reactions', 'comments', 'metric_captured_at', 'comparison_n', 'reaction_midrank_percentile', 'performance_status', 'performance_reason', 'trend_status', 'trend_reason']
        self.write_csv('data/qualification-table.csv', fields, [{**{'post_id': p['id'], 'author': p['author']['name'], 'url': p['url']}, **{k: im.get(p['id'], {}).get(k) for k in fields if k in im.get(p['id'], {})}, **{k: pm[p['id']].get(k) for k in fields if k in pm[p['id']]}} for p in self.posts])
        self.stage_sqlite(ds)
        tpl = self.template.read_text(encoding='utf-8')
        ok = tpl.count('__DATASET__') == 1
        self.add('template_has_single_dataset_placeholder', ok, 1, tpl.count('__DATASET__'), self.rel(self.template))
        if not ok:
            return
        embedded = json.dumps(ds, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
        self.stage('index.html', tpl.replace('__DATASET__', embedded))

    def stage_sqlite(self, ds):
        rel = 'data/linkedin.sqlite'
        path = self.root / rel
        tmp = path.with_name(path.name + '.tmp')
        path.parent.mkdir(parents=True, exist_ok=True)
        if tmp.exists():
            tmp.unlink()
        con = sqlite3.connect(tmp)
        try:
            for key, table, kfn, pfn in ENTITIES:
                extra = ', url TEXT NOT NULL UNIQUE, author_name TEXT, cycle TEXT, published_at TEXT, captured_at TEXT' if table == 'posts' else ''
                con.execute('CREATE TABLE %s(id TEXT PRIMARY KEY, post_id TEXT, payload TEXT NOT NULL%s)' % (table, extra))
                if table == 'posts':
                    con.executemany('INSERT INTO posts VALUES(?,?,?,?,?,?,?,?)', [(r['id'], r['id'], json.dumps(r, ensure_ascii=False), r['url'], r['author'].get('name'), r['cycle'], r['published_at'], r['captured_at']) for r in ds[key]])
                else:
                    con.executemany('INSERT INTO %s VALUES(?,?,?)' % table, [(kfn(r), pfn(r) if pfn else None, json.dumps(r, ensure_ascii=False)) for r in ds[key]])
            con.execute('CREATE INDEX snapshots_post ON snapshots(post_id)')
            con.commit()
        finally:
            con.close()
        self.staged[rel] = tmp

    def verify_staged(self, ds):
        # SQLite: integrity and one table per entity with counts equal to the dataset.json read back from disk
        disk = jloads(self.staged['data/dataset.json'].read_text(encoding='utf-8'))
        self.add('dataset_json_equals_in_memory', canon(disk) == canon(ds), 'dataset.json round-trips exactly', sha_bytes(canon(disk).encode()) == sha_bytes(canon(ds).encode()))
        con = sqlite3.connect('file:%s?mode=ro' % self.staged['data/linkedin.sqlite'], uri=True)
        try:
            integrity = con.execute('PRAGMA integrity_check').fetchone()[0]
            self.add('sqlite_integrity_check', integrity == 'ok', 'ok', integrity)
            tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            exp = {t: len(disk[k]) for k, t, _f, _p in ENTITIES}
            obs = {t: con.execute('SELECT count(*) FROM %s' % t).fetchone()[0] for t in exp if t in tables}
            self.add('sqlite_table_per_entity_counts_equal_json', obs == exp and tables == set(exp), exp, obs, 'tables present: %s' % sorted(tables))
            sample_bad = [t for t, k, kf in [(e[1], e[0], e[2]) for e in ENTITIES]
                          if {r[0] for r in con.execute('SELECT id FROM %s' % t)} != {str(kf(r)) for r in disk[k]}]
            self.add('sqlite_row_keys_equal_json', not sample_bad, 'row keys equal dataset keys', sample_bad or 'all tables')
        finally:
            con.close()
        html = self.staged['index.html'].read_text(encoding='utf-8')
        m = re.search(r'<script id="dataset" type="application/json">(.*?)</script>', html, re.S)
        emb = jloads(m.group(1)) if m else None
        h_emb = sha_bytes(canon(emb).encode()) if emb is not None else None
        h_disk = sha_bytes(canon(disk).encode())
        self.html_hashes = {'embedded_canonical_sha256': h_emb, 'dataset_json_canonical_sha256': h_disk}
        self.add('html_embeds_dataset_exactly', h_emb is not None and h_emb == h_disk, h_disk, h_emb, 'hash of the canonical (sorted-key, compact) JSON of the parsed dataset')
        self.add('html_has_no_unreplaced_placeholder', '__DATASET__' not in html, 'no __DATASET__ left', '__DATASET__' in html)
        links = [l['href'] for l in ds['meta']['links']]
        gone = [h for h in links if not ((self.root / h).exists() or (h in PRODUCED and (self.root / h).with_name(Path(h).name + '.tmp').exists()))]
        self.add('index_html_links_resolve', not gone, 'every header link exists', gone or {'links': len(links)})

    def promote(self):
        for rel, tmp in self.staged.items():
            os.replace(tmp, self.root / rel)
        for rel in self.staged:
            p = self.root / rel
            self.outputs.append({'path': rel, 'sha256': sha_file(p), 'bytes': p.stat().st_size})
        self.staged = {}

    def discard(self):
        for tmp in self.staged.values():
            if tmp.exists():
                tmp.unlink()
        for rel in ['data/dataset.json', 'data/posts.csv', 'data/new-posts.csv', 'data/snapshots.csv', 'data/velocity.csv', 'data/linkedin.sqlite', 'index.html']:
            leftover = (self.root / rel).with_name(Path(rel).name + '.tmp')  # a stage that raised midway
            if leftover.exists():
                leftover.unlink()
        self.staged = {}

    # ---- driver
    def run(self):
        ds = None
        try:
            print('release: root=%s base=%s cycle=%s' % (self.root.name, self.base.name, self.cycle), flush=True)
            self.load()
            self.build()
            self.check_paths()
            ds = self.make_dataset()
            self.counts = {k: len(ds[k]) for k, *_ in ENTITIES}
            self.counts_summary = ds['summary']
            if self.check_entity_keys(ds) and not self.failed() and not self.dry_run:
                print('release: staging exports', flush=True)
                self.export(ds)
                if not self.failed():
                    self.verify_staged(ds)
            if self.failed() or self.dry_run:
                self.discard()
            else:
                self.promote()
        except ReleaseAbort as e:
            print('release: aborted: %s' % e, flush=True)
            self.discard()
        except Exception as e:  # a bug or an input shape nobody planned for: report it as a failed release, keep old outputs
            import traceback
            traceback.print_exc()
            self.add('release_internal_error', False, 'no unexpected exception', '%s: %s' % (type(e).__name__, e))
            self.discard()
        return self.finish()

    def finish(self):
        fails = [c['name'] for c in self.checks if c['status'] == 'fail']
        report = {
            'schema_version': SCHEMA_VERSION, 'run_id': self.root.name, 'base_run_id': self.base.name,
            'status': 'fail' if fails or not self.counts else 'pass', 'dry_run': self.dry_run,
            'generated_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
            'code': {'release_py_sha256': sha_file(HERE / 'release.py'), 'viewer_template_sha256': sha_file(self.template) if self.template.exists() else None,
                     'python': sys.version.split()[0]},
            'counts': {'entities': self.counts, 'summary': getattr(self, 'counts_summary', None)},
            'check_totals': dict(Counter(c['status'] for c in self.checks)), 'failed_checks': fails,
            'inputs': self.inputs, 'outputs': self.outputs, 'html_hashes': getattr(self, 'html_hashes', None),
            'checks': self.checks, 'gaps': self.gaps, 'warnings': self.warnings,
            'scope_limits': [
                'Velocity is the observed change of a public reaction counter between captured snapshots; it is not reach, impressions or a trend rank.',
                'Cohort ranking is shown only where the pipeline marks a cohort as ranked; cohorts with n below min_n stay unranked.',
                'Visual and video reviews are sampled agent inspections; continuous watching and audio listening are not claimed.',
                'Files evicted to iCloud (dataless) are checked for existence and size; their bytes are re-hashed only with --hash-dataless.',
                'Absent analytical replacement files inherit dated base evidence with a warning; explicit current files, including empty lists, remain authoritative. Other absent new inputs are reported as empty.'],
        }
        if not self.dry_run:
            out = self.root / 'verification/release-checks.json'
            out.parent.mkdir(parents=True, exist_ok=True)
            tmp = out.with_name(out.name + '.tmp')
            tmp.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
            os.replace(tmp, out)
        self.report = report
        return 0 if report['status'] == 'pass' else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', type=Path, default=HERE, help='run folder to release (default: this script folder)')
    ap.add_argument('--base', type=Path, default=DEFAULT_BASE, help='previous cycle folder holding data/dataset.json')
    ap.add_argument('--template', type=Path, help='viewer template (default: viewer-template.html next to this script)')
    ap.add_argument('--as-of', help='YYYY-MM-DD for account activity windows (default: pipeline/config.json qualification.as_of, else latest capture date)')
    ap.add_argument('--baseline-cycle', default='v2', help="cycle label of the base dataset's 'baseline' collection")
    ap.add_argument('--hash-dataless', action='store_true', help='read and hash iCloud-evicted files (may block on downloads)')
    ap.add_argument('--dry-run', action='store_true', help='run all data checks; write nothing')
    a = ap.parse_args(argv)
    rel = Release(a.root, a.base, a.template, a.as_of, a.hash_dataless, a.dry_run, a.baseline_cycle)
    code = rel.run()
    r = rel.report
    print(json.dumps({'status': r['status'], 'check_totals': r['check_totals'], 'failed_checks': r['failed_checks'], 'entities': r['counts']['entities'],
                      'gaps': dict(Counter(g['kind'] for g in r['gaps'])), 'warnings': len(r['warnings']), 'outputs': [o['path'] for o in r['outputs']]}, indent=2))
    return code


if __name__ == '__main__':
    sys.exit(main())
