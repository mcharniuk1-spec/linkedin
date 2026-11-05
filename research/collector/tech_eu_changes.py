"""Incremental source additions/removals; no LinkedIn collection.

The source does not expose in-place edits. Persistent anchor and cursors do not
prove complete market coverage, nor an uninterrupted upstream change history.
The caller holds the collector lock.
"""
from datetime import datetime, timedelta, timezone
import json
from urllib.parse import urlencode
from .contracts import AccessSuspended, CollectionError, ConfigurationError
from .external_discovery import _ExternalState
from .tech_eu import SOURCE, UUID, _seed, _put, prune_unreviewed_seeds
from .transport import UrllibTransport

ENDPOINT='https://funding.tech.eu/api/v1/changes'


def _time(value):
    if not isinstance(value,str):raise ValueError('timestamp_required')
    t=datetime.fromisoformat(value.replace('Z','+00:00'))
    if t.tzinfo is None:raise ValueError('timezone_required')
    return t.astimezone(timezone.utc)


def _value(db,key):
    r=db.execute('SELECT value FROM metadata WHERE key=?',(key,)).fetchone()
    return r[0] if r else None


def _set(db,key,value):
    db.execute('INSERT OR REPLACE INTO metadata VALUES (?,?)',(key,value))


def _cursor(created,identifier):
    _time(created)
    if not isinstance(identifier,str) or not UUID.fullmatch(identifier):raise ValueError('invalid_change_identity')
    return created+'__'+identifier


def _mark_removed(db,removed,seen_at):
    """Preserve review and history; flag any candidate citing this source round."""
    rid=removed['id'].lower()
    db.execute('INSERT OR IGNORE INTO tech_eu_tombstones VALUES (?,?,?)',
               (rid,removed.get('removedAt'),seen_at))
    for category,identity,payload in db.execute("SELECT category,identity,payload FROM candidate_queue WHERE category='target_company' AND identity LIKE 'tech-eu:%'").fetchall():
        candidate=json.loads(payload); funding=candidate.get('funding') or {}
        url=funding.get('source_url') or ''
        if url.rstrip('/').rsplit('/',1)[-1].lower()==rid:
            funding['source_status']='withdrawn_by_source'; candidate['funding']=funding
            db.execute('UPDATE candidate_queue SET payload=? WHERE category=? AND identity=?',
                       (json.dumps(candidate,ensure_ascii=False),category,identity))


async def collect_changes(store, *, now=None, transport_factory=None, max_pages=3, lookback_days=90):
    now=now or datetime.now(timezone.utc)
    if now.tzinfo is None or type(max_pages) is not int or not 1<=max_pages<=5 or type(lookback_days) is not int or not 1<=lookback_days<=365:
        raise ValueError('invalid_change_bounds')
    now=now.astimezone(timezone.utc)
    result={'source_id':SOURCE+'-changes','status':'error','requests':0,'successful_requests':0,
            'new_items':0,'duplicates':0,'excluded':0,'tombstones_seen':0,
            'linkedin_posts_collected':0,'error':None,'coverage':'additions and removals only; upstream in-place edits not observed'}
    anchor=_value(store.db,'tech_eu_bootstrap_started_at'); done=_value(store.db,'tech_eu_seed_done')
    if not anchor or not done:
        result.update(status='held',error='bootstrap_start_and_completion_required');return result
    result['expired_unreviewed_seeds']=prune_unreviewed_seeds(store,now)
    try:
        # This API normalizes `since` to milliseconds. Round down, so its
        # normalization cannot drop changes during the bootstrap microseconds.
        anchor_time=_time(anchor)
        floor=anchor_time.replace(microsecond=(anchor_time.microsecond//1000)*1000)
        since=_value(store.db,'tech_eu_changes_since') or (anchor if floor==anchor_time else floor.isoformat(timespec='milliseconds'))
        if _time(since)!=floor or _time(since)>now:raise ValueError('invalid_bootstrap_anchor')
    except ValueError:
        result.update(status='held',error='invalid_bootstrap_anchor');return result
    hold=_value(store.db,'tech_eu_changes_hold')
    if hold:result.update(status='held',error=hold);return result
    if store.get_suspension(SOURCE):result.update(status='held',error='source_access_suspended');return result
    if _value(store.db,'tech_eu_changes_complete_utc_day')==now.date().isoformat():
        result['status']='already_completed_today';return result
    cursor=_value(store.db,'tech_eu_changes_after'); after=cursor
    if after:
        try:
            a,b=after.rsplit('__',1);_cursor(a,b)
        except ValueError:
            result.update(status='held',error='invalid_saved_cursor');return result
    spec={'source_id':SOURCE,'access_group':SOURCE,'allowed_hosts':['funding.tech.eu'],
          'permitted_methods':['GET'],'permissions':{'public_read':True},'max_attempts':1,
          'concurrency':1,'rate_per_second':0.5,'timeout_seconds':15,'max_bytes':1_000_000}
    transport=(transport_factory or UrllibTransport)(spec,_ExternalState(store))
    staged=[]; tombstones={}; caught_up=False
    try:
        previous=None
        if after:
            stamp,identifier=after.rsplit('__',1);previous=(_time(stamp),identifier.lower())
        for _ in range(max_pages):
            params={'type':'rounds','since':since,'limit':50}
            if after:params['after']=after
            result['requests']+=1
            response=await transport.fetch(ENDPOINT+'?'+urlencode(params))
            if response.status_code in (401,403,429,999):
                store.suspend(SOURCE,'http_'+str(response.status_code));raise AccessSuspended('source_access_suspended')
            if response.status_code!=200:raise CollectionError('changes_http_error')
            result['successful_requests']+=1
            data=json.loads(response.body)
            if not isinstance(data,dict) or data.get('type')!='rounds' or _time(data.get('since'))!=_time(since):
                raise CollectionError('changes_anchor_mismatch')
            if data.get('removedComplete') is not True:
                # A truncated tombstone list is a material gap; do not advance.
                with store.db:_set(store.db,'tech_eu_changes_hold','tombstone_list_incomplete')
                raise CollectionError('tombstone_list_incomplete')
            rows=data.get('data'); removed=data.get('removed'); next_cursor=data.get('nextCursor')
            if not isinstance(rows,list) or len(rows)>50 or not isinstance(removed,list) or len(removed)>10000:
                raise CollectionError('changes_invalid_shape')
            for item in removed:
                if not isinstance(item,dict) or not isinstance(item.get('id'),str) or not UUID.fullmatch(item['id']):
                    raise CollectionError('invalid_tombstone')
                if item.get('removedAt') is not None:_time(item['removedAt'])
                tombstones[item['id'].lower()]=item
            for row in rows:
                if not isinstance(row,dict):raise CollectionError('invalid_change')
                new_cursor=_cursor(row.get('createdAt'),row.get('id'))
                if _time(row['createdAt'])<_time(since):raise CollectionError('change_before_anchor')
                position=(_time(row['createdAt']),row['id'].lower())
                if previous is not None and position<=previous:raise CollectionError('changes_not_strictly_ordered')
                previous=position
                staged.append((row,response.collected_at)); after=new_cursor
            if next_cursor is not None:
                if not rows or next_cursor!=after:raise CollectionError('changes_cursor_mismatch')
                if next_cursor==cursor:raise CollectionError('changes_cursor_not_progressing')
                cursor=next_cursor
            else:
                caught_up=True;break
        # Apply all pages together: a later page error never advances the cursor.
        with store.db:
            store.db.execute('CREATE TABLE IF NOT EXISTS tech_eu_tombstones (round_id TEXT PRIMARY KEY,removed_at TEXT,observed_at TEXT NOT NULL)')
            for item in tombstones.values():_mark_removed(store.db,item,now.isoformat())
            for row,observed_at in staged:
                # A removed record must not be reinserted via an older addition.
                if row['id'].lower() in tombstones:
                    result['excluded']+=1;continue
                seed=_seed(row,observed_at,now.date()-timedelta(days=lookback_days))
                if not seed:result['excluded']+=1;continue
                added=_put(store,seed);result['new_items' if added else 'duplicates']+=1
            _set(store.db,'tech_eu_changes_since',since)
            if after:_set(store.db,'tech_eu_changes_after',after)
            if caught_up:_set(store.db,'tech_eu_changes_complete_utc_day',now.date().isoformat())
        result['tombstones_seen']=len(tombstones)
        result['status']='ok' if caught_up else 'partial'
    except AccessSuspended:
        result.update(status='held',error='source_access_suspended')
    except (CollectionError,ConfigurationError,ValueError,TypeError,KeyError) as exc:
        result.update(status='error',error='tombstone_list_incomplete' if str(exc)=='tombstone_list_incomplete' else type(exc).__name__)
    finally:
        await transport.aclose()
    return result
