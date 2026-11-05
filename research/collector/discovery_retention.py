"""Bounded retention of newly-created Exa raw objects only.

The caller must hold the collector lock. Call ``register`` in the same SQLite
transaction as inserting the raw object and discovery row, passing the actual
``INSERT OR IGNORE`` rowcount as ``created_new_raw``. Old/unregistered objects
are never adopted. No VACUUM or network operations are performed here.
"""
from datetime import datetime, timedelta, timezone
import json
import re
import sqlite3


class RetentionError(ValueError):
    pass


def _stamp(value):
    if not isinstance(value,str): raise RetentionError('invalid_timestamp')
    try: stamp=datetime.fromisoformat(value.replace('Z','+00:00'))
    except ValueError: raise RetentionError('invalid_timestamp') from None
    if stamp.tzinfo is None: raise RetentionError('timezone_required')
    return stamp.astimezone(timezone.utc)


def _digest(value):
    if not isinstance(value,str) or not re.fullmatch(r'[0-9a-f]{64}',value):
        raise RetentionError('invalid_digest')
    return value


def _schema(db):
    expected={'discoveries':['id','payload'], 'raw_objects':['sha256','compressed']}
    for table,columns in expected.items():
        actual=[r[1] for r in db.execute('PRAGMA table_info("'+table+'")')]
        if actual!=columns:raise RetentionError('unexpected_source_schema')
    # These statements participate in the caller's transaction; executescript
    # would commit it and could split insertion from registration.
    db.execute('CREATE TABLE IF NOT EXISTS exa_retention_objects (sha256 TEXT PRIMARY KEY, created_at TEXT NOT NULL)')
    db.execute('CREATE TABLE IF NOT EXISTS exa_retention_refs (discovery_id TEXT PRIMARY KEY, sha256 TEXT NOT NULL, observed_at TEXT NOT NULL, expires_at TEXT NOT NULL)')
    for table,columns in {'exa_retention_objects':['sha256','created_at'],
                          'exa_retention_refs':['discovery_id','sha256','observed_at','expires_at']}.items():
        if [r[1] for r in db.execute('PRAGMA table_info("'+table+'")')]!=columns:
            raise RetentionError('unexpected_retention_schema')
    if db.execute("SELECT 1 FROM sqlite_master WHERE type='trigger' AND tbl_name IN ('raw_objects','discoveries','exa_retention_objects','exa_retention_refs') LIMIT 1").fetchone():
        raise RetentionError('unexpected_mutation_trigger')


def register(store, discovery_id, digest, *, observed_at, created_new_raw, retention_days=30, registered_at=None):
    """Register a newly captured observation, or leave an old shared hash alone.

    ``created_new_raw`` must be exactly the insertion rowcount (0 or 1), not a
    caller guess. Returns ``managed`` or ``unmanaged_existing``. Captures must
    use a minimum 30-day window. The caller owns commit/rollback.
    """
    db=store.db; _schema(db); digest=_digest(digest)
    if not isinstance(discovery_id,str) or not discovery_id:raise RetentionError('invalid_discovery_id')
    if type(created_new_raw) is not int or created_new_raw not in (0,1):raise RetentionError('raw_insert_rowcount_required')
    if type(retention_days) is not int or retention_days<30:raise RetentionError('retention_below_minimum')
    observed=_stamp(observed_at)
    registration=_stamp(registered_at) if registered_at is not None else datetime.now(timezone.utc)
    # A late import cannot make a newly managed object expire immediately.
    expiry=max(observed,registration)+timedelta(days=retention_days)
    row=db.execute('SELECT payload FROM discoveries WHERE id=?',(discovery_id,)).fetchone()
    if row is None or not db.execute('SELECT 1 FROM raw_objects WHERE sha256=?',(digest,)).fetchone():
        raise RetentionError('raw_or_observation_missing')
    try: payload=json.loads(row[0])
    except (TypeError,ValueError):raise RetentionError('malformed_discovery') from None
    if not isinstance(payload,dict) or payload.get('source_id')!='exa-search' or payload.get('raw_sha256')!=digest or _stamp(payload.get('collected_at'))!=observed:
        raise RetentionError('observation_identity_mismatch')
    if 'raw_retention' in payload:raise RetentionError('existing_retention_metadata')
    managed=db.execute('SELECT created_at FROM exa_retention_objects WHERE sha256=?',(digest,)).fetchone()
    if managed and created_new_raw:raise RetentionError('inconsistent_raw_insert')
    if not managed and not created_new_raw:return 'unmanaged_existing'
    if not managed:
        db.execute('INSERT INTO exa_retention_objects VALUES (?,?)',(digest,observed.isoformat()))
    else:
        _stamp(managed[0])
    payload['raw_retention']={'status':'managed','retain_until':expiry.isoformat(),'version':1}
    db.execute('INSERT INTO exa_retention_refs VALUES (?,?,?,?)',(discovery_id,digest,observed.isoformat(),expiry.isoformat()))
    db.execute('UPDATE discoveries SET payload=? WHERE id=?',(json.dumps(payload,sort_keys=True),discovery_id))
    return 'managed'


def _external_reference(db,digest,eligible_ids):
    # Scan all actual SQLite text values, including columns with no declared
    # type. Ignore only our own ledger and the raw object's own identity.
    excluded={'raw_objects','exa_retention_objects','exa_retention_refs'}
    tables=[r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
    for table in tables:
        if table in excluded:continue
        name='"'+table.replace('"','""')+'"'
        cols=[r[1] for r in db.execute('PRAGMA table_info('+name+')')]
        for col in cols:
            field='"'+col.replace('"','""')+'"'
            if table=='discoveries':
                for ident,value in db.execute('SELECT id,'+field+' FROM '+name+' WHERE typeof('+field+")='text' AND instr("+field+',?)>0',(digest,)):
                    if ident in eligible_ids:continue
                    if col=='payload':
                        try:
                            row=json.loads(value);meta=row['raw_retention']
                            if (row['source_id']=='exa-search' and row['raw_sha256']==digest and
                                meta['version']==1 and meta['status']=='expired' and
                                _stamp(meta['expired_at'])>=_stamp(meta['retain_until']) and
                                _stamp(row['collected_at'])<=_stamp(meta['retain_until'])):
                                continue
                        except (ValueError,TypeError,KeyError,RetentionError):pass
                    return True
            elif db.execute('SELECT 1 FROM '+name+' WHERE typeof('+field+")='text' AND instr("+field+',?)>0 LIMIT 1',(digest,)).fetchone():
                return True
    return False


def expire(store, *, now):
    """Delete eligible managed raw only and preserve discovery provenance.

    Validate every ledger date and reference before mutations. On any mismatch,
    raise RetentionError without deleting anything; an enclosing transaction
    must roll back. Any untracked or external text reference blocks deletion.
    """
    db=store.db; _schema(db); current=_stamp(now)
    objects=dict(db.execute('SELECT sha256,created_at FROM exa_retention_objects'))
    refs={digest:[] for digest in objects}
    for digest,created in objects.items():_digest(digest);_stamp(created)
    for ident,digest,observed,expiry in db.execute('SELECT discovery_id,sha256,observed_at,expires_at FROM exa_retention_refs'):
        if digest not in objects:raise RetentionError('orphaned_reference')
        o,e=_stamp(observed),_stamp(expiry)
        if e-o<timedelta(days=30):raise RetentionError('retention_below_minimum')
        row=db.execute('SELECT payload FROM discoveries WHERE id=?',(ident,)).fetchone()
        if row is None:raise RetentionError('observation_missing')
        try:payload=json.loads(row[0])
        except (TypeError,ValueError):raise RetentionError('malformed_discovery') from None
        if not isinstance(payload,dict):raise RetentionError('malformed_discovery')
        meta=payload.get('raw_retention')
        if (o<_stamp(objects[digest]) or payload.get('raw_sha256')!=digest or payload.get('source_id')!='exa-search' or
            _stamp(payload.get('collected_at'))!=o or not isinstance(meta,dict) or
            meta.get('version')!=1 or meta.get('status')!='managed' or _stamp(meta.get('retain_until'))!=e):
            raise RetentionError('retention_identity_mismatch')
        refs[digest].append((ident,e,payload))
    for digest,observations in refs.items():
        if not observations:raise RetentionError('managed_object_without_reference')
        if not db.execute('SELECT 1 FROM raw_objects WHERE sha256=?',(digest,)).fetchone():
            raise RetentionError('managed_raw_missing')
    eligible=[]; blocked=0
    for digest,observations in refs.items():
        if any(expiry>current for _,expiry,_ in observations):continue
        ids={ident for ident,_,_ in observations}
        if _external_reference(db,digest,ids):blocked+=1;continue
        eligible.append((digest,observations))
    db.execute('SAVEPOINT exa_retention_expiry')
    try:
        for digest,observations in eligible:
            for ident,_,payload in observations:
                payload['raw_retention']['status']='expired'
                payload['raw_retention']['expired_at']=current.isoformat()
                db.execute('UPDATE discoveries SET payload=? WHERE id=?',(json.dumps(payload,sort_keys=True),ident))
            db.execute('DELETE FROM raw_objects WHERE sha256=?',(digest,))
            db.execute('DELETE FROM exa_retention_refs WHERE sha256=?',(digest,))
            db.execute('DELETE FROM exa_retention_objects WHERE sha256=?',(digest,))
        db.execute('RELEASE exa_retention_expiry')
    except (sqlite3.Error,ValueError):
        db.execute('ROLLBACK TO exa_retention_expiry');db.execute('RELEASE exa_retention_expiry');raise
    return {'expired_raw_objects':len(eligible),'blocked_shared_objects':blocked}
