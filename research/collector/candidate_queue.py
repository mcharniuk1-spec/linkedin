"""Metadata-only queues; discovery is not collection or engagement evidence."""
import json
import re
from urllib.parse import urlsplit
from .contracts import utcnow
from .store import canonical_url


def enqueue(store, category, url, source_id, *, topic=None, description=None):
    if category not in {'publication', 'reference_account', 'target_company'}:
        raise ValueError('invalid_candidate_category')
    if not isinstance(url,str):
        raise ValueError('candidate_url_required')
    p = urlsplit(url)
    if p.hostname not in {'linkedin.com', 'www.linkedin.com'} or p.username or p.password or p.scheme != 'https':
        raise ValueError('invalid_candidate_url')
    path = p.path.rstrip('/')
    if category == 'publication':
        match = re.search(r'activity-(\d{19})', path)
        if not path.startswith('/posts/') or not match:
            raise ValueError('invalid_publication_identity')
        identity = 'activity:' + match.group(1)
        if store.known_url(url):
            return 0
    else:
        allowed = r'/company/[^/]+' if category == 'target_company' else r'/(?:company|in)/[^/]+'
        if not re.fullmatch(allowed, path, re.I):
            raise ValueError('invalid_account_identity')
        identity = path.lower()
    if not isinstance(source_id,str) or not source_id or len(source_id)>120:
        raise ValueError('invalid_candidate_source')
    payload = {'source_id': source_id, 'source_url': canonical_url(url), 'topic': topic,
               'description': description, 'discovered_at': utcnow(), 'permission_state': 'unverified',
               'review_status': 'pending', 'performance_evidence': None,
               'content_opportunity': None, 'expressed_need': None, 'buying_interest': None}
    store.db.execute('CREATE TABLE IF NOT EXISTS candidate_queue (category TEXT NOT NULL, identity TEXT NOT NULL, payload TEXT NOT NULL, PRIMARY KEY(category,identity))')
    with store.db:
        result = store.db.execute('INSERT OR IGNORE INTO candidate_queue VALUES (?,?,?)',
                                  (category, identity, json.dumps(payload, ensure_ascii=False)))
    return result.rowcount
