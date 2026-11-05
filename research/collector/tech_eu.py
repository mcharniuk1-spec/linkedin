"""Bounded, attribution-preserving European funding prospect seeds.

The caller holds the collector lock. Results are not qualified clients, LinkedIn
profiles, buying intent, posts, or performance evidence.
"""
from datetime import datetime, timedelta, timezone
import hashlib
import json
import re
from urllib.parse import urlencode, urlsplit
from .contracts import AccessSuspended, CollectionError, ConfigurationError
from .transport import UrllibTransport
from .external_discovery import _ExternalState

SOURCE='tech-eu-funding-explorer'
ENDPOINT='https://funding.tech.eu/api/v1/rounds'
STAGES=('Seed','Series A','Series B')
# Europe-based scope: EU plus UK, EEA, Switzerland, and European microstates.
# Transcontinental and disputed jurisdictions require explicit future review.
COUNTRIES=frozenset({'Austria','Belgium','Bulgaria','Croatia','Cyprus','Czech Republic',
    'Czechia','Denmark','Estonia','Finland','France','Germany','Greece','Hungary','Ireland',
    'Italy','Latvia','Lithuania','Luxembourg','Malta','Netherlands','Poland','Portugal',
    'Romania','Slovakia','Slovenia','Spain','Sweden','UK','United Kingdom','Iceland',
    'Liechtenstein','Norway','Switzerland','Andorra','Monaco','San Marino','Vatican City'})
UUID=re.compile(r'^[0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}$')


def _url(value):
    if not isinstance(value,str):return None
    p=urlsplit(value)
    if p.scheme!='https' or p.hostname!='funding.tech.eu' or p.username or p.password or p.query or p.fragment:
        return None
    return value


def _seed(row, observed_at, since):
    if not isinstance(row,dict) or not isinstance(row.get('company'),dict):return None
    c=row['company']; cid=c.get('id'); rid=row.get('id'); stage=row.get('stage')
    name=c.get('name'); country=c.get('country'); sectors=c.get('sectors'); stamp=row.get('date')
    try:
        day=datetime.fromisoformat(stamp).date()
    except (ValueError,TypeError):return None
    if not isinstance(cid,str) or not UUID.fullmatch(cid) or not isinstance(rid,str) or not UUID.fullmatch(rid):return None
    if country not in COUNTRIES or stage not in STAGES or day<since or day>datetime.fromisoformat(observed_at.replace('Z','+00:00')).date():return None
    if not isinstance(name,str) or not name.strip() or len(name)>300 or not isinstance(sectors,list) or 'AI' not in sectors:return None
    company_url=_url(c.get('pageUrl')); round_url=_url(row.get('pageUrl'))
    if not company_url or not round_url:return None
    return {'name':name.strip(),'source_id':SOURCE,'source_url':company_url,
        'discovered_at':observed_at,'permission_state':'CC BY 4.0; attribution required',
        'review_status':'pending', 'fit_status':'unverified', 'country':country,
        'employee_count':None,'business_model':None,'linkedin_url':None,
        'content_opportunity':None,'expressed_need':None,'buying_interest':None,
        'funding':{'stage':stage,'date':stamp,'sector':'AI','source_url':round_url,
                   'confidence':row.get('confidence') if row.get('confidence') in ('high','medium','low') else None},
        'description':'Funding and sector seed. B2B SaaS fit, employee count and LinkedIn activity require independent review.',
        'attribution':'Tech.eu Funding Explorer', 'licence':'CC BY 4.0',
        'licence_url':'https://creativecommons.org/licenses/by/4.0/',
        'source_changes':'Filtered by stage, date, sector and geography; fields normalized.',
        'source_company_id':cid.lower(),
        'retention':{'policy':'unreviewed-funding-seed-180d-v1',
                     'last_seen_at':observed_at}}


def _put(store, value):
    identity='tech-eu:'+value['source_company_id']
    prior=store.db.execute('SELECT payload FROM candidate_queue WHERE category=? AND identity=?',('target_company',identity)).fetchone()
    if prior:
        existing=json.loads(prior[0]); old=existing.get('funding') or {}
        if (existing.get('retention') or {}).get('source_digest')!=_source_digest(existing):
            return False  # Never overwrite a human-edited or legacy candidate.
        changed=False
        if (value.get('funding') or {}).get('date','') > old.get('date',''):
            # Refresh source fact only. Never overwrite human review or hypotheses.
            existing['funding']=value['funding'];changed=True
        if (existing.get('retention') or {}).get('policy')=='unreviewed-funding-seed-180d-v1':
            existing['retention']['last_seen_at']=value['discovered_at'];changed=True
        if changed:
            existing['retention']['source_digest']=_source_digest(existing)
            store.db.execute('UPDATE candidate_queue SET payload=? WHERE category=? AND identity=?',
                             (json.dumps(existing,ensure_ascii=False), 'target_company',identity))
        return False
    value['retention']['source_digest']=_source_digest(value)
    store.db.execute('INSERT INTO candidate_queue VALUES (?,?,?)',('target_company',identity,json.dumps(value,ensure_ascii=False)))
    return True


def _source_digest(row):
    payload={k:v for k,v in row.items() if k!='retention'}
    return hashlib.sha256(json.dumps(payload,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()


def prune_unreviewed_seeds(store, now):
    """Expire only source-created, untouched pending seeds; preserve reviews."""
    removed=0
    allowed={'name','source_id','source_url','discovered_at','permission_state','review_status',
             'fit_status','country','employee_count','business_model','linkedin_url',
             'content_opportunity','expressed_need','buying_interest','funding','description',
             'attribution','licence','licence_url','source_changes','source_company_id','retention'}
    with store.db:
        for identity,payload in list(store.db.execute("SELECT identity,payload FROM candidate_queue WHERE category='target_company'")):
            try:
                row=json.loads(payload);ret=row.get('retention') or {}
                stamp=datetime.fromisoformat(ret.get('last_seen_at','').replace('Z','+00:00'))
                if (not isinstance(row,dict) or set(row)-allowed or stamp.tzinfo is None or
                    row.get('source_id')!=SOURCE or row.get('review_status')!='pending' or
                    row.get('fit_status')!='unverified' or ret.get('policy')!='unreviewed-funding-seed-180d-v1' or
                    ret.get('source_digest')!=_source_digest(row) or
                    any(row.get(k) is not None for k in ('employee_count','business_model','linkedin_url','content_opportunity','expressed_need','buying_interest'))):continue
                if now.astimezone(timezone.utc)-stamp.astimezone(timezone.utc)>=timedelta(days=180):
                    removed+=store.db.execute("DELETE FROM candidate_queue WHERE category='target_company' AND identity=?",(identity,)).rowcount
            except (ValueError,TypeError,AttributeError):continue
    return removed


async def collect_tech_eu(store, *, now=None, transport_factory=None, lookback_days=90, max_pages_per_stage=1):
    """Collect <=3 * max_pages_per_stage pages; skip after one complete UTC-day cycle.

    max_pages_per_stage is 1..2 and page size 50. Returns aggregate data only.
    Does not read or fetch LinkedIn. Never converts these seeds to observed posts.
    """
    now=now or datetime.now(timezone.utc)
    if now.tzinfo is None or type(lookback_days) is not int or not 1<=lookback_days<=365 or type(max_pages_per_stage) is not int or not 1<=max_pages_per_stage<=2:
        raise ValueError('invalid_tech_eu_bounds')
    now=now.astimezone(timezone.utc); since=now.date()-timedelta(days=lookback_days)
    store.db.execute('CREATE TABLE IF NOT EXISTS candidate_queue (category TEXT NOT NULL, identity TEXT NOT NULL, payload TEXT NOT NULL, PRIMARY KEY(category,identity))')
    result={'source_id':SOURCE,'status':'error','requests':0,'successful_requests':0,'new_items':0,
            'duplicates':0,'excluded':0,'linkedin_posts_collected':0,'error':None,
            'attribution':'Tech.eu Funding Explorer','licence':'CC BY 4.0',
            'truncated_stages':[]}
    result['expired_unreviewed_seeds']=prune_unreviewed_seeds(store,now)
    if store.get_suspension(SOURCE):
        result.update(status='held',error='source_access_suspended');return result
    last=store.db.execute('SELECT value FROM metadata WHERE key=?',('tech_eu_seed_done',)).fetchone()
    if last:
        result['status']='already_completed_today';return result
    with store.db:
        store.db.execute('INSERT OR IGNORE INTO metadata VALUES (?,?)',('tech_eu_bootstrap_started_at',now.isoformat()))
    spec={'source_id':SOURCE,'access_group':SOURCE,'allowed_hosts':['funding.tech.eu'],
          'permitted_methods':['GET'],'permissions':{'public_read':True},'max_attempts':1,
          'concurrency':1,'rate_per_second':0.5,'timeout_seconds':15,'max_bytes':1_000_000}
    transport=(transport_factory or UrllibTransport)(spec,_ExternalState(store))
    try:
        for stage in STAGES:
            after=None
            for _ in range(max_pages_per_stage):
                args={'stage':stage,'sector':'AI','from':since.isoformat(),'limit':50}
                if after:args['after']=after
                result['requests']+=1
                response=await transport.fetch(ENDPOINT+'?'+urlencode(args))
                if response.status_code in (401,403,429,999):
                    store.suspend(SOURCE,'http_'+str(response.status_code))
                    raise AccessSuspended('source_access_suspended')
                if response.status_code!=200:raise CollectionError('tech_eu_http_error')
                result['successful_requests']+=1
                data=json.loads(response.body)
                if not isinstance(data,dict) or not isinstance(data.get('data'),list) or len(data['data'])>50:
                    raise CollectionError('invalid_tech_eu_response')
                filters=data.get('appliedFilters') or {}
                if not isinstance(filters,dict) or filters.get('stage')!=stage or filters.get('sector')!='AI' or filters.get('from')!=since.isoformat():
                    raise CollectionError('tech_eu_filters_not_confirmed')
                for row in data['data']:
                    seed=_seed(row,response.collected_at,since)
                    if not seed:result['excluded']+=1;continue
                    with store.db:
                        added=_put(store,seed)
                    result['new_items' if added else 'duplicates']+=1
                after=data.get('nextCursor')
                if not after:break
                if not isinstance(after,str) or len(after)>200:raise CollectionError('invalid_tech_eu_cursor')
            if after:result['truncated_stages'].append(stage)
        with store.db:
            store.db.execute('INSERT OR REPLACE INTO metadata VALUES (?,?)',('tech_eu_seed_done','true'))
        result['status']='ok'
    except AccessSuspended:
        result.update(status='held',error='source_access_suspended')
    except (CollectionError,ConfigurationError,ValueError,TypeError,KeyError,json.JSONDecodeError) as exc:
        result.update(status='error',error=type(exc).__name__)
    finally:
        await transport.aclose()
    return result
