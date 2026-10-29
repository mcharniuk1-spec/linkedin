"""Durable deduplication and immutable extracted records for one writer."""
from __future__ import annotations
from contextlib import contextmanager
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
import fcntl
import gzip
import hashlib
import json
import os
import sqlite3
import uuid
from .contracts import ConfigurationError, utcnow

REQUIRED = {'source_id','external_id','source_url','author','published_at','collected_at',
            'content_type','text','extracted_fields','content_hash','permissions','processing_status'}


def canonical_url(url):
    p = urlsplit(url)
    if p.username or p.password or not p.hostname or p.scheme not in ('http','https'):
        raise ConfigurationError('invalid_record_url')
    if any(k.lower() in {'access_token','client_secret','refresh_token','code','password'} for k in parse_qs(p.query)):
        raise ConfigurationError('secret_parameter_in_record_url')
    if p.hostname != 'api.linkedin.com' and (p.hostname == 'linkedin.com' or p.hostname.endswith('.linkedin.com')):
        # Comment fragments identify distinct resources; other fragments are tracking only.
        import re
        fragment = '#'+p.fragment if re.fullmatch(r'comment-[A-Za-z0-9_()\-:,]+',p.fragment) else ''
        return 'https://www.linkedin.com' + p.path.rstrip('/') + fragment
    return p._replace(fragment='').geturl()


class Store:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        os.chmod(self.root, 0o700)
        self.path = self.root / 'collector.sqlite'
        self.db = sqlite3.connect(self.path, timeout=15)
        os.chmod(self.path, 0o600)
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS records (
          record_id TEXT PRIMARY KEY, source_id TEXT NOT NULL, external_id TEXT NOT NULL,
          source_url TEXT NOT NULL, collected_at TEXT NOT NULL, content_hash TEXT NOT NULL,
          payload TEXT NOT NULL, UNIQUE(source_id,external_id));
        CREATE TABLE IF NOT EXISTS aliases (alias TEXT PRIMARY KEY, record_id TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS raw_objects (sha256 TEXT PRIMARY KEY, compressed BLOB NOT NULL);
        CREATE TABLE IF NOT EXISTS profiles (identity TEXT PRIMARY KEY, payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS suspensions (access_group TEXT PRIMARY KEY, payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS requests (id TEXT PRIMARY KEY, source_id TEXT NOT NULL, payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS runs (id TEXT PRIMARY KEY, payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS processing_events (id TEXT PRIMARY KEY, record_id TEXT NOT NULL,
          created_at TEXT NOT NULL, status TEXT NOT NULL, evidence TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        ''')

    def close(self):
        self.db.close()

    @contextmanager
    def lock(self):
        with (self.root/'collector.lock').open('a+') as f:
            try:
                fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                raise ConfigurationError('collector_already_running') from None
            try:
                yield self
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)

    def seed(self, seed):
        """Identity-only bootstrap; never manufacture source observations or text."""
        if self.db.execute("SELECT 1 FROM metadata WHERE key='bootstrap_sha256'").fetchone():
            return 0
        payload = json.dumps(seed,sort_keys=True,separators=(',',':'))
        count = 0
        with self.db:
            for item in seed['publications']:
                owner = 'baseline:' + item['external_id']
                for alias in item['aliases']:
                    self.db.execute('INSERT OR IGNORE INTO aliases VALUES (?,?)',(alias,owner))
                count += 1
            for item in seed.get('profiles',[]):
                self.db.execute('INSERT OR IGNORE INTO profiles VALUES (?,?)',
                    (canonical_url(item['url']),json.dumps(item,sort_keys=True)))
            self.db.execute('INSERT INTO metadata VALUES (?,?)',
                ('bootstrap_sha256',hashlib.sha256(payload.encode()).hexdigest()))
        return count

    def known_url(self, url):
        try:
            u = canonical_url(url)
        except (ValueError,ConfigurationError):
            return False
        if self.db.execute('SELECT 1 FROM aliases WHERE alias=?',('url:'+u,)).fetchone():
            return True
        import re
        m = re.search(r'activity-(\d+)',u)
        return bool(m and self.db.execute('SELECT 1 FROM aliases WHERE alias=?',
            ('id:urn:li:activity:'+m.group(1),)).fetchone())

    def ingest(self, value):
        if not REQUIRED <= value.keys():
            raise ConfigurationError('missing_record_fields')
        if not all(isinstance(value[k],str) and value[k] for k in ('source_id','external_id','source_url','collected_at','content_type')):
            raise ConfigurationError('invalid_record_identity')
        if not isinstance(value['text'],str) or not isinstance(value['permissions'],dict) or not value['permissions']:
            raise ConfigurationError('missing_permission_or_text_contract')
        expected = hashlib.sha256(value['text'].encode()).hexdigest()
        if value['content_hash'] != expected:
            raise ConfigurationError('content_hash_mismatch')
        stamp = datetime.fromisoformat(value['collected_at'].replace('Z','+00:00'))
        if stamp.tzinfo is None:
            raise ConfigurationError('collection_timezone_required')
        url = canonical_url(value['source_url'])
        aliases = set(value.get('identity_aliases',[])) | {'url:'+url,'id:'+value['external_id']}
        # Both prefixed legacy variants are accepted at the boundary, not confused with IDs.
        if value['content_type'] in {'linkedin_post','static_page','feed_item','api_item'} and len(value['text'].strip()) >= 60:
            import re
            aliases.add('text:'+hashlib.sha256(re.sub(r'\s+',' ',value['text']).strip().lower().encode()).hexdigest())
        normalized = {k:v for k,v in value.items() if not k.startswith('_')}
        normalized['source_url'] = url
        normalized['processing_status'] = 'pending_review'
        normalized['publication_date_status'] = 'missing'
        if value['published_at']:
            try:
                pub = datetime.fromisoformat(value['published_at'].replace('Z','+00:00'))
                normalized['publication_date_status'] = ('verified_source_date' if pub.tzinfo and pub <= stamp+timedelta(hours=1) else 'future_or_timezone_hold')
            except (ValueError,TypeError,AttributeError):
                normalized['publication_date_status'] = 'malformed_hold'
        raw = value.get('_raw')
        if raw is not None and not isinstance(raw,bytes):
            raise ConfigurationError('raw_source_must_be_bytes')
        normalized['raw_sha256'] = hashlib.sha256(raw).hexdigest() if raw is not None else value.get('raw_sha256')
        owner = hashlib.sha256((value['source_id']+'|'+value['external_id']).encode()).hexdigest()
        with self.db:
            existing = next((row for a in aliases if (row:=self.db.execute('SELECT record_id FROM aliases WHERE alias=?',(a,)).fetchone())),None)
            if existing:
                return {'inserted':False,'duplicate_of':existing[0]}
            self.db.execute('INSERT INTO records VALUES (?,?,?,?,?,?,?)',
                (owner,value['source_id'],value['external_id'],url,value['collected_at'],expected,json.dumps(normalized,sort_keys=True,ensure_ascii=False)))
            for alias in aliases:
                self.db.execute('INSERT INTO aliases VALUES (?,?)',(alias,owner))
            if raw is not None:
                self.db.execute('INSERT OR IGNORE INTO raw_objects VALUES (?,?)',
                    (normalized['raw_sha256'],gzip.compress(raw,mtime=0)))
            author = value.get('author')
            if isinstance(author,dict) and author.get('url'):
                identity = canonical_url(author['url'])
                self.db.execute('INSERT OR IGNORE INTO profiles VALUES (?,?)',
                    (identity,json.dumps({**author,'observation_scope':'public_post_actor_only',
                     'collected_at':value['collected_at'],'full_profile_retrieved':False},sort_keys=True)))
        return {'inserted':True,'record_id':owner}

    def get_suspension(self, key):
        row = self.db.execute('SELECT payload FROM suspensions WHERE access_group=?',(key,)).fetchone()
        return json.loads(row[0]) if row else None

    def suspend(self, key, reason, retry_after_seconds=None):
        value = {'reason':str(reason)[:120],'suspended_at':utcnow(),
                 'retry_after_seconds':retry_after_seconds,'automatic_resume':False}
        with self.db:
            self.db.execute('INSERT OR REPLACE INTO suspensions VALUES (?,?)',(key,json.dumps(value)))

    def resume(self, key, reason):
        if not reason.strip():
            raise ConfigurationError('resume_requires_source_backed_reason')
        with self.db:
            self.db.execute('DELETE FROM suspensions WHERE access_group=?',(key,))
            self.db.execute('INSERT INTO metadata VALUES (?,?)',('resume:'+uuid.uuid4().hex,json.dumps({'key':key,'reason':reason,'at':utcnow()})))

    def log_request(self, source_id, event):
        # Strict allowlist: no URL, query, body, token, authorization or arbitrary exceptions.
        safe = {k:v for k,v in event.items() if k in {'status','status_code','http_status','latency_ms','bytes','attempt','error_code','event','kind','collected_at'}}
        with self.db:
            self.db.execute('INSERT INTO requests VALUES (?,?,?)',(uuid.uuid4().hex,source_id,json.dumps(safe)))

    def counts(self):
        return {t:self.db.execute('SELECT count(*) FROM '+t).fetchone()[0]
                for t in ('records','aliases','profiles','raw_objects','suspensions','requests')}

    def pending(self):
        return [{'record_id':k,**json.loads(v)} for k,v in self.db.execute('SELECT record_id,payload FROM records ORDER BY collected_at')
                if not self.db.execute('SELECT 1 FROM processing_events WHERE record_id=? AND status=?',(k,'reviewed')).fetchone()]

    def raw_bytes(self, digest):
        row = self.db.execute('SELECT compressed FROM raw_objects WHERE sha256=?',(digest,)).fetchone()
        if not row:
            raise ConfigurationError('raw_source_not_available')
        body = gzip.decompress(row[0])
        if hashlib.sha256(body).hexdigest() != digest:
            raise ConfigurationError('raw_source_hash_mismatch')
        return body

    def export_pending(self, output):
        requested = Path(output).absolute()
        if requested.is_symlink():raise ConfigurationError('manual_export_symlink_refused')
        output = requested.resolve()
        if not output.is_relative_to(self.root):raise ConfigurationError('manual_export_requires_private_state_subdirectory')
        output.mkdir(parents=True,exist_ok=True,mode=0o700);os.chmod(output,0o700)
        rows = self.pending()
        for row in rows:
            h=row.get('raw_sha256')
            if h:
                raw=self.db.execute('SELECT compressed FROM raw_objects WHERE sha256=?',(h,)).fetchone()
                if raw:
                    body=gzip.decompress(raw[0]);assert hashlib.sha256(body).hexdigest()==h
                    p=output/'raw'/f'{h}.bin';p.parent.mkdir(exist_ok=True,mode=0o700);p.write_bytes(body);os.chmod(p,0o600)
                    row['raw_path']=str(p.relative_to(output))
        (output/'records.ndjson').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in rows));os.chmod(output/'records.ndjson',0o600)
        return {'pending_records':len(rows),'output':str(output),'automatic_analysis':False}

    def snapshot(self, destination):
        target=sqlite3.connect(destination)
        try:
            self.db.backup(target)
        finally:
            target.close()
        os.chmod(destination,0o600)
