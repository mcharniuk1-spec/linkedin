"""Bounded public-source LinkedIn research cycle, v5. No account, cookies, paid API or scheduler.

Each command finishes without a conversational agent. Semantic analysis remains a
separate supervisor step. v4 adds corpus-wide identity, immutable reobservation
snapshots, due-only refresh, a persistent access stop, a run lock, exposed-link and
rotating approved-author discovery, explicit date holds and observed-velocity export.
Prior runs are read as corpus inputs only; their files are never written.
"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo
from statistics import median
from bs4 import BeautifulSoup
import argparse, fcntl, hashlib, json, re, sqlite3, subprocess, sys, time, urllib.request, urllib.error
import normalizer
from runtime_config import load_config, tool_command

VERSION='0.5.0'
HERE=Path(__file__).resolve().parent
STOP_CODES=[401,403,429,999]
AUTH_PATHS=('/authwall','/login','/checkpoint','/uas/login','/signup')
def now(): return datetime.now(timezone.utc).isoformat()
def sha(b): return hashlib.sha256(b).hexdigest()
def dump(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.tmp');tmp.write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n');tmp.replace(p)
def read(p): return json.loads(Path(p).read_text(),object_pairs_hook=normalizer.unique)
def rows(p): return [json.loads(l,object_pairs_hook=normalizer.unique) for l in Path(p).read_text().splitlines() if l.strip()] if Path(p).exists() else []
def qa_record_sha256(record):
    # Exclude only the digest itself and the legacy untrusted bypass boolean.
    stable={k:v for k,v in record.items() if k not in ('qa_record_sha256','supervisor_reviewed')}
    return sha(json.dumps(stable,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())
def norm(t): return re.sub(r'\s+',' ',t).strip().lower()
def parse_date(d):
    try:
        v=datetime.fromisoformat(d.replace('Z','+00:00'));return v if v.tzinfo else v.replace(tzinfo=timezone.utc)
    except (ValueError,AttributeError,TypeError): return None
class SameHostRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        old,new=urlsplit(req.full_url),urlsplit(newurl)
        if new.scheme!='https' or new.hostname!=old.hostname or new.port not in [None,443] or new.username or new.password:raise ValueError('Redirect blocked before cross-host/port request')
        return super().redirect_request(req,fp,code,msg,headers,newurl)
def keys(p):
    """Corpus identity: activity, underlying share, canonical URL, normalized text."""
    return (p['id'],p.get('attributed_urn') or p['id'],normalizer.canonical(p['url']),sha(norm(p['text']).encode()))
def slug(url):
    parts=[x for x in urlsplit(url or '').path.split('/') if x];return parts[1].lower() if len(parts)>1 and parts[0] in ('in','company') else None
def post_slug(url):
    m=re.search(r'/posts/([^_/]+)_',url or '');return m.group(1).lower() if m else None
def activity(url):
    m=re.search(r'activity-(\d{19})',url or '');return m.group(1) if m else None
def date_status(published,captured,skew_hours=1):
    """Source publication date only; comments, search freshness and IDs are never substituted."""
    if published in (None,''):return 'date_missing'
    d=parse_date(published)
    if d is None:return 'date_malformed'
    c=parse_date(captured)
    if c and d>c+timedelta(hours=skew_hours):return 'future_date_hold'
    return 'verified_source_date'
def media_kind(p):
    t={m['type'] for m in p.get('media',[])}
    return 'video' if 'video' in t else 'image' if 'image' in t else 'document' if p.get('_documents') else 'text_or_other'
def age_bin(days):
    if days is None:return 'age_unknown'
    for limit,label in [(7,'age_0_7d'),(30,'age_8_30d'),(90,'age_31_90d'),(180,'age_91_180d')]:
        if days<=limit:return label
    return 'age_over_180d'

class Locked(RuntimeError):pass

class Cycle:
    def __init__(self,config,lock=True):
        self.cfg=load_config(config, object_pairs_hook=normalizer.unique);self.root=Path(self.cfg['run_root']).resolve()
        if self.cfg['qualification'].get('as_of_mode')=='runtime':self.cfg['qualification']['as_of']=datetime.now(ZoneInfo('Europe/Sofia')).date().isoformat()
        protected=[Path(p).resolve().parent.parent for p in self.corpus_paths()]
        if self.root in protected:raise ValueError('Corpus runs are immutable; choose a new run root')
        for d in ['raw/objects','data','media/objects','operations','transcripts','analysis']:(self.root/d).mkdir(parents=True,exist_ok=True)
        self.lockfile=None
        if lock:
            self.lockfile=(self.root/'operations/cycle.lock').open('a+')
            try:fcntl.flock(self.lockfile,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:raise Locked('Another cycle process holds operations/cycle.lock; no overlap allowed')
        self.db=sqlite3.connect(self.root/'operations/cycle.sqlite');self.db.execute('pragma foreign_keys=on')
        self.db.executescript('''CREATE TABLE IF NOT EXISTS posts(id TEXT PRIMARY KEY,payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS captures(id TEXT PRIMARY KEY,post_id TEXT NOT NULL,captured_at TEXT NOT NULL,raw_sha256 TEXT NOT NULL,raw_path TEXT NOT NULL,capture_kind TEXT NOT NULL,source_run TEXT NOT NULL,payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS assets(id TEXT PRIMARY KEY,post_id TEXT NOT NULL,payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS events(id TEXT PRIMARY KEY,kind TEXT NOT NULL,created_at TEXT NOT NULL,payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS requests(id TEXT PRIMARY KEY,url TEXT NOT NULL,created_at TEXT NOT NULL,payload TEXT NOT NULL);''')
        self.requests_made=0
    # ---------- corpus and store ----------
    def corpus_paths(self):
        c=list(self.cfg.get('corpus_posts',[]))
        if self.cfg.get('baseline_posts') and self.cfg['baseline_posts'] not in c:c.append(self.cfg['baseline_posts'])
        return c
    def corpus(self):
        if not hasattr(self,'_corpus'):
            self._corpus=[]
            for p in self.corpus_paths():
                run=Path(p).resolve().parent.parent.name
                for r in rows(p):
                    raw=Path(r['source']['raw_path'])
                    if not raw.is_absolute():r={**r,'source':{**r['source'],'raw_path':str((Path(p).resolve().parent.parent/raw).resolve())}}
                    self._corpus.append({**r,'_source_run':run})
        return self._corpus
    def event(self,kind,payload):
        x={'kind':kind,'created_at':now(),**payload};eid=sha(json.dumps(x,sort_keys=True).encode());x['event_id']=eid
        with self.db:self.db.execute('INSERT OR IGNORE INTO events VALUES(?,?,?,?)',(eid,kind,x['created_at'],json.dumps(x)))
        dump(self.root/'operations/events'/f'{eid}.json',x);return x
    def posts(self):return [json.loads(x[0]) for x in self.db.execute('SELECT payload FROM posts ORDER BY id')]
    def known(self):
        """All known publications: prior corpus plus posts first discovered in this store."""
        k={p['id']:p for p in self.corpus()}
        for p in self.posts():k.setdefault(p['id'],p)
        return k
    def approved(self,p):
        policy=self.cfg.get('collection_approval',{})
        if not policy.get('require_watchlist',False):return True
        return urlsplit(p['author'].get('url') or '').path.rstrip('/').lower() in policy.get('approved_author_paths',[])
    def export_posts(self):
        ps=self.posts();p=self.root/'data/new-posts.ndjson';p.write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in ps));return ps
    # ---------- access control ----------
    def access_stop(self):
        f=self.root/'operations/access-stop.json'
        if not f.exists():return None
        s=read(f);until=parse_date(s.get('stopped_at'))+timedelta(hours=self.cfg['capture'].get('stop_cooldown_hours',24))
        return s if datetime.now(timezone.utc)<until else None
    def stop(self,reason,receipt):
        s={'stopped_at':now(),'reason':reason,'url':receipt.get('url'),'http_status':receipt.get('http_status'),'final_url':receipt.get('final_url'),'policy':'No further LinkedIn/media requests until cooldown passes or a supervisor clears this file; no cookies, proxies or paid fallback.'}
        dump(self.root/'operations/access-stop.json',s);self.event('access_stopped',s);return s
    def get(self,url,kind='page',probe=False):
        p=urlsplit(url);host=p.hostname or '';allowed=(host=='linkedin.com' or host.endswith('.linkedin.com')) if kind=='page' else (host=='licdn.com' or host.endswith('.licdn.com'))
        if p.scheme!='https' or not allowed or p.username or p.password or p.port not in [None,443]:raise ValueError('Unexpected public source URL')
        cfg=self.cfg['capture' if kind=='page' else 'media'];cap=cfg.get('max_html_bytes',cfg.get('max_video_bytes') if kind=='video' else cfg.get('max_other_bytes'))
        stamp=now();receipt={'url':url,'captured_at':stamp,'kind':kind,'method':'anonymous_public_GET','cookies':False,'rights':'Internal reference analysis; reuse not cleared'}
        if not probe and self.access_stop():receipt.update(status='refused_access_stop');return receipt,None
        self.requests_made+=1
        try:
            req=urllib.request.Request(url,headers={'User-Agent':'OutspokenPublicResearch/0.5'})
            with urllib.request.build_opener(SameHostRedirect()).open(req,timeout=cfg['timeout_seconds']) as f:
                if urlsplit(f.url).hostname!=host:raise ValueError('Cross-host redirect; no automatic continuation')
                b=f.read(cap+1);receipt.update(http_status=f.status,final_url=f.url,content_type=f.headers.get('Content-Type'))
            if urlsplit(receipt['final_url']).path.rstrip('/').startswith(AUTH_PATHS):receipt.update(status='stopped',error='auth_or_challenge_page');return receipt,None
            if len(b)>cap:raise ValueError('Source exceeds size cap')
            receipt.update(status='acquired',sha256=sha(b),bytes=len(b));return receipt,b
        except urllib.error.HTTPError as e:receipt.update(status='stopped' if e.code in self.cfg['capture'].get('error_stop_codes',STOP_CODES) else 'failed',http_status=e.code,error=type(e).__name__);return receipt,None
        except Exception as e:receipt.update(status='failed',error=type(e).__name__+': '+str(e));return receipt,None
    def record_request(self,r):
        rid=sha(json.dumps(r,sort_keys=True).encode())
        with self.db:self.db.execute('INSERT OR IGNORE INTO requests VALUES(?,?,?,?)',(rid,r['url'],r['captured_at'],json.dumps(r)))
    def waves(self,urls,kind='page'):
        """Two-request waves with a delay; any stop code or auth/challenge page persists a stop and defers the rest."""
        results=[];workers=self.cfg['capture']['workers'];delay=self.cfg['capture'].get('wave_delay_seconds',0)
        if self.access_stop():return results,list(urls),'ACCESS_STOPPED'
        for offset in range(0,len(urls),workers):
            with ThreadPoolExecutor(max_workers=workers) as ex:batch=list(ex.map(lambda u:self.get(u,kind),urls[offset:offset+workers]))
            results.extend(batch)
            for r,_ in batch:self.record_request(r)
            health_path=self.root/'operations/layout-health.json';health=read(health_path) if health_path.exists() else {'consecutive_unparseable_200':0}
            soft_hit=None
            for r,body in batch:
                if kind=='page' and r.get('http_status')==200 and body is not None:
                    try:normalizer.post_context(BeautifulSoup(body,'html.parser'),r['url']);health['consecutive_unparseable_200']=0
                    except ValueError:health['consecutive_unparseable_200']+=1
                    if health['consecutive_unparseable_200']>=self.cfg['capture'].get('soft_wall_consecutive_limit',3):soft_hit={**r,'error':'consecutive_200_without_supported_post'}
                else:health['consecutive_unparseable_200']=0
            dump(health_path,health)
            hit=next((r for r,_ in batch if r.get('status')=='stopped'),None) or soft_hit
            if hit:
                self.stop(hit.get('error') or f"http_{hit.get('http_status')}",hit);walls=[r for r,_ in batch if r.get('error')=='auth_or_challenge_page']
                if walls:self.block(walls)
                redo=[r['url'] for r,_ in batch if r.get('status')=='stopped' and r.get('error')!='auth_or_challenge_page']
                return results,redo+urls[offset+workers:],'ACCESS_STOPPED'
            if delay and offset+workers<len(urls):time.sleep(delay)
        return results,[],'OK'
    # ---------- identity and capture ----------
    def store_capture(self,p,raw,kind,run):
        rawp=self.root/'raw/objects'/(sha(raw)+'.html')
        if rawp.exists():assert rawp.read_bytes()==raw
        else:rawp.write_bytes(raw)
        sid=sha((p['id']+'|'+p['captured_at']+'|'+sha(raw)).encode());payload=json.dumps(p,ensure_ascii=False,sort_keys=True)
        with self.db:
            existing=self.db.execute('SELECT payload FROM captures WHERE id=?',(sid,)).fetchone()
            if existing and existing[0]!=payload:raise ValueError('Immutable capture conflict')
            self.db.execute('INSERT OR IGNORE INTO captures VALUES(?,?,?,?,?,?,?,?)',(sid,p['id'],p['captured_at'],sha(raw),str(rawp),kind,run,payload))
        return sid
    def accept(self,p,raw):
        """New publication or reobservation of a known one. Never both; never a second publication record."""
        normalizer.validate_record(p);assert sha(raw)==p['source']['sha256']
        soup=BeautifulSoup(raw,'html.parser');a,layout,ld=normalizer.post_context(soup,p['url']);actor=normalizer.main_actor(a,ld.get('creator') or ld.get('author') or {})
        if not actor:raise ValueError('Main actor unavailable')
        p['author']['name']=actor.get_text(' ',strip=True);p['author']['url']=actor['href'].split('?')[0]
        known=self.known();k=keys(p)
        if p['id'] in known:
            prior=known[p['id']]
            if normalizer.canonical(prior['url'])!=p['url'] or urlsplit(prior['author'].get('url') or '').path.rstrip('/').lower()!=urlsplit(p['author']['url']).path.rstrip('/').lower():raise ValueError('Reobservation identity conflict; held for supervisor')
            p['source']['reobservation_flags']=[f for f,c in [('text_changed',sha(norm(prior['text']).encode())!=k[3]),('attributed_urn_changed',(prior.get('attributed_urn') or None)!=(p.get('attributed_urn') or None)),('published_at_conflict',(prior.get('published_at') or None)!=(p.get('published_at') or None))] if c]
            self.store_capture(p,raw,'reobservation',self.root.name);return p,'reobservation'
        if len(norm(p['text']))<60:raise ValueError('Insufficient original commentary')
        if re.search(r'#(?:ad\b|sponsored\b|\w*partner\b)',p['text'],re.I):raise ValueError('Explicit paid tag; separate cohort')
        header=soup.select_one('.base-main-card__context')
        if header and re.search(r'\brepost(?:ed)?\b',header.get_text(' ',strip=True),re.I):raise ValueError('Visible reshare header')
        conflict=next((q for q in known.values() if q['id']!=p['id'] and any(x==y for x,y in zip(k,keys(q)))),None)
        if conflict:raise ValueError('Duplicate share/URL/text of known post '+conflict['id'])
        sid=self.store_capture(p,raw,'new_discovery',self.root.name);p['source']['raw_path']=str((self.root/'raw/objects'/(sha(raw)+'.html')).resolve())
        with self.db:self.db.execute('INSERT INTO posts VALUES(?,?) ON CONFLICT(id) DO NOTHING',(p['id'],json.dumps(p,ensure_ascii=False,sort_keys=True)))
        return p,'new_discovery'
    def import_baseline(self):
        """Re-parse every prior raw capture with the current parser so snapshots compare like with like."""
        imported=0;errors=[]
        for r in self.corpus():
            try:
                raw=Path(r['source']['raw_path']).read_bytes()
                if sha(raw)!=r['source']['sha256']:raise ValueError('Prior raw object hash mismatch')
                p=normalizer.parse_post(r['source']['raw_path'],r['url'],r['captured_at'])
                if p['id']!=r['id']:raise ValueError('Prior identity mismatch on reparse')
                p['author']={**p['author'],'name':r['author'].get('name'),'url':r['author'].get('url')}
                p['source']['normalization_provenance']={'kind':'derived_reparse_not_new_observation','source_run':r['_source_run'],'source_parser_version':r.get('parser_version'),'original_observed_at':r['captured_at'],'raw_sha256':r['source']['sha256']}
                self.store_capture(p,raw,'baseline_import',r['_source_run']);imported+=1
            except Exception as e:errors.append({'post_id':r.get('id'),'error':str(e)})
        # Prior runs' reobservations keep velocity history across stores; their first captures arrive via corpus_posts.
        known={r['id']:r for r in self.corpus()};reobs=0
        for path in self.cfg.get('corpus_snapshots',[]):
            try:prior=read(path)
            except (OSError,ValueError) as e:errors.append({'snapshot_file':str(path),'error':type(e).__name__+': '+str(e)});continue
            for s in prior:
                if s.get('capture_kind')!='reobservation':continue
                try:
                    snapshot_path=Path(s['raw_path']);snapshot_path=snapshot_path if snapshot_path.is_absolute() else Path(path).resolve().parent.parent/snapshot_path
                    raw=snapshot_path.read_bytes()
                    if sha(raw)!=s['raw_sha256']:raise ValueError('Prior snapshot raw hash mismatch')
                    if s['post_id'] not in known:raise ValueError('Snapshot post absent from corpus_posts')
                    p=normalizer.parse_post(snapshot_path,s['url'],s['captured_at']);k=known[s['post_id']]
                    if p['id']!=s['post_id']:raise ValueError('Snapshot identity mismatch on reparse')
                    p['author']={**p['author'],'name':k['author'].get('name'),'url':k['author'].get('url')};p['source']['reobservation_flags']=s.get('reobservation_flags',[])
                    p['source']['normalization_provenance']={'kind':'derived_reparse_not_new_observation','source_run':s['source_run'],'source_parser_version':s.get('parser_version'),'original_observed_at':s['captured_at'],'raw_sha256':s['raw_sha256']}
                    self.store_capture(p,raw,'reobservation',s['source_run']);reobs+=1
                except Exception as e:errors.append({'post_id':s.get('post_id'),'snapshot':s.get('snapshot_id'),'error':str(e)})
        dump(self.root/'operations/baseline-import.json',{'corpus_posts':len(self.corpus()),'imported_or_verified':imported,'prior_reobservations_imported':reobs,'errors':errors,'parser_version':normalizer.VERSION});return {'imported_or_verified':imported,'prior_reobservations':reobs,'errors':len(errors)}
    def block(self,receipts):
        """Auth/challenge redirects for one post are kept, not auto-retried; a supervisor may re-queue them."""
        f=self.root/'operations/blocked-urls.json';b=read(f) if f.exists() else {}
        for r in receipts:b[r['url']]={'reason':r.get('error'),'final_url':r.get('final_url'),'at':r.get('captured_at'),'auto_retry':False}
        dump(f,b)
    def note_failures(self,errors,successes):
        f=self.root/'operations/capture-failures.json';x=read(f) if f.exists() else {}
        for u in successes:x.pop(u,None)
        for e in errors:
            if e.get('url') and e.get('error') and e.get('status')!='stopped':
                v=x.get(e['url'],{'count':0});x[e['url']]={'count':v['count']+1,'last_error':e['error'][:160],'last_at':now()}
        dump(f,x);return x
    def capture(self,urls):
        bf=self.root/'operations/blocked-urls.json';blocked=read(bf) if bf.exists() else {};ff=self.root/'operations/capture-failures.json';fails=read(ff) if ff.exists() else {};maxf=self.cfg.get('refresh',{}).get('max_failures',2)
        known=set(self.known());urls=[u for u in dict.fromkeys(normalizer.canonical(u) for u in urls) if u not in blocked and fails.get(u,{}).get('count',0)<maxf][:self.cfg['capture']['max_urls']]
        results,deferred,state=self.waves(urls,'page');df=self.root/'operations/deferred-capture-queue.json';done={r['url'] for r,_ in results}
        # Merge, never overwrite: a later refresh must not erase URLs deferred by an earlier stop.
        dump(df,list(dict.fromkeys([u for u in (read(df) if df.exists() else []) if u not in done]+deferred)))
        out={'new_discovery':[],'reobservation':[],'errors':[]}
        for receipt,b in results:
            if b is None:out['errors'].append(receipt);continue
            fp=self.root/'raw/objects'/(sha(b)+'.html')
            if not fp.exists():fp.write_bytes(b)
            try:p,kind=self.accept(normalizer.parse_post(fp,receipt['url'],receipt['captured_at']),b);out[kind].append(p['id']);out.setdefault('_ok',[]).append(receipt['url'])
            except Exception as e:out['errors'].append({'url':receipt['url'],'error':str(e)})
        self.note_failures(out['errors'],out.pop('_ok',[]));self.export_posts();out.update(state=state,deferred=len(deferred),requested=len(results),known_before=len(known))
        dump(self.root/'operations/capture-result.json',out);return {k:(len(v) if isinstance(v,list) else v) for k,v in out.items()}
    def refresh(self):
        """Reobserve known posts only when their latest capture is at least the policy interval old."""
        cfg=self.cfg.get('refresh',{});minh=cfg.get('min_interval_hours',self.cfg['qualification']['velocity_min_observation_span_hours']);t=datetime.now(timezone.utc)
        last={pid:parse_date(ts) for pid,ts in self.db.execute('SELECT post_id,max(captured_at) FROM captures GROUP BY post_id')}
        due=[];notdue=[];ff=self.root/'operations/capture-failures.json';fails=read(ff) if ff.exists() else {};skipped=[];bf=self.root/'operations/blocked-urls.json';blocked=read(bf) if bf.exists() else {}
        for pid,p in self.known().items():
            if fails.get(p['url'],{}).get('count',0)>=cfg.get('max_failures',2) or p['url'] in blocked:skipped.append(p['url']);continue
            l=last.get(pid) or parse_date(p['captured_at'])
            if (t-l).total_seconds()/3600>=minh:due.append((l,p['url'],pid))
            else:notdue.append((l,p['url'],pid))
        due.sort();urls=[u for _,u,_ in due][:cfg.get('max_urls',0)]
        res=self.capture(urls) if urls else {'state':'NOTHING_DUE'}
        out={'due':len(due),'requested_urls':len(urls),'not_due':len(notdue),'skipped_failures_or_blocked':len(skipped),'min_interval_hours':minh,'next_due_at':min((l+timedelta(hours=minh) for l,_,_ in notdue),default=None),'result':res}
        out['next_due_at']=out['next_due_at'].isoformat() if out['next_due_at'] else None
        dump(self.root/'operations/refresh-result.json',out);return out
    # ---------- discovery ----------
    def exposed_links(self):
        """Same-author and related-post links exposed on already captured public pages (no new requests)."""
        known=self.known();seen={};pages=self.db.execute('SELECT post_id,raw_path,raw_sha256 FROM captures').fetchall()
        for pid,path,h in pages:
            page=known.get(pid);au=slug((page or {}).get('author',{}).get('url'))
            try:soup=BeautifulSoup(Path(path).read_bytes(),'html.parser')
            except OSError:continue
            for a in soup.select('a[data-tracking-control-name="link-overlay-public_post"][href]'):
                try:u=normalizer.canonical(a['href'])
                except ValueError:continue
                aid=activity(u)
                if not aid or 'urn:li:activity:'+aid in known or u in seen:continue
                s=post_slug(u);rel='exposed_same_author' if au and s==au else 'exposed_related_other_author'
                seen[u]={'url':u,'source':rel,'source_page_post_id':pid,'source_page_raw_sha256':h,'author_slug_from_url':s,'approved_author':('/in/'+s) in self.cfg['collection_approval']['approved_author_paths'] if s else False,'activity_id_order_hint':int(aid),'order_hint_is_not_date_evidence':True}
        cands=sorted(seen.values(),key=lambda c:(c['source']!='exposed_same_author',not c['approved_author'],-c['activity_id_order_hint']))
        return cands
    def exa(self,q,n):
        arg='exa-public.web_search_exa(query: '+json.dumps(q)+', numResults: '+str(n)+')'
        try:p=subprocess.run(['mcporter','--config',str(HERE/'mcporter.json'),'call',arg],capture_output=True,text=True,timeout=80);out,code=p.stdout,p.returncode
        except subprocess.TimeoutExpired:out,code='',124
        raw=out.encode();fp=self.root/'raw'/('search-'+sha(q.encode())[:16]+'-'+sha(raw)[:8]+'.txt');fp.write_bytes(raw)
        urls=[]
        for u in re.findall(r'^URL:\s*(https://[^\s<>]+)',out,re.M):
            try:
                u=normalizer.canonical(u)
                if '/posts/' in u and activity(u):urls.append(u)
            except ValueError:pass
        limited=code!=0 or bool(re.search(r'rate limit|quota|unauthori[sz]ed|too many requests',out,re.I))
        return {'query':q,'backend':'installed_mcporter_exa_keyless','runtime_utc':now(),'exit_code':code,'raw_path':str(fp.relative_to(self.root)),'raw_sha256':sha(raw),'matching_post_urls':urls,'limited_or_failed':limited,'result_order_is_not_reach':True,'date_operator_is_not_publication_proof':True}
    def discover(self):
        cfg=self.cfg['discovery'];anchor=parse_date(self.cfg['qualification']['as_of']+'T00:00:00+00:00')
        fill=lambda q:q.replace('{since90}',(anchor-timedelta(days=90)).date().isoformat()).replace('{tomorrow}',(anchor+timedelta(days=1)).date().isoformat())
        state_f=self.root/'operations/discovery-state.json';st=read(state_f) if state_f.exists() else {'author_rotation_index':0}
        authors=[p.split('/')[-1] for p in self.cfg['collection_approval']['approved_author_paths']];k=cfg.get('author_queries_per_cycle',0);i=st['author_rotation_index']%max(1,len(authors))
        rotation=[(authors+authors)[i+j] for j in range(min(k,len(authors)))]
        plan=[('exa_topic',fill(q)) for q in cfg['queries'][:cfg['max_queries']]]+[('exa_author',fill(cfg['author_query_template'].replace('{slug}',a))) for a in rotation]
        results=[];cands={};known=set(self.known())
        for src,q in plan:
            r=self.exa(q,cfg['max_results_per_query']);r['source']=src;results.append(r)
            if r['limited_or_failed']:break
            for u in r['matching_post_urls']:
                if 'urn:li:activity:'+activity(u) not in known:cands.setdefault(u,{'url':u,'source':src,'query':q,'raw_sha256':r['raw_sha256'],'approved_author':('/in/'+(post_slug(u) or '')) in self.cfg['collection_approval']['approved_author_paths']})
        exposed=self.exposed_links() if cfg.get('exposed_links',True) else []
        for c in exposed[:cfg.get('max_exposed_urls',0)]:cands.setdefault(c['url'],c)
        ran=[r for r in results if r['source']=='exa_author' and not r['limited_or_failed']];st={'author_rotation_index':(i+len(ran))%max(1,len(authors)),'last_rotation':rotation[:len(ran)],'updated_at':now()};dump(state_f,st)
        queue=self.prioritize(list(cands),cands);dump(self.root/'operations/discovery.json',results);dump(self.root/'operations/discovery-candidates.json',list(cands.values()));dump(self.root/'operations/url-queue.json',queue)
        return {'queries':len(results),'exposed_available':len(exposed),'unique_new_candidate_urls':len(queue),'by_source':{s:sum(c['source']==s for c in cands.values()) for s in {c['source'] for c in cands.values()}},'urls':queue}
    def prioritize(self,urls,cands):
        """Approved-watchlist candidates first, then round-robin across discovery sources, so an access stop costs the least valuable requests."""
        groups={}
        for u in urls:c=cands.get(u,{});groups.setdefault((not c.get('approved_author'),c.get('source','unknown')),[]).append(u)
        out=[]
        for approved in (False,True):
            lanes=[v for k,v in sorted(groups.items()) if k[0]==approved]
            while any(lanes):
                for lane in lanes:
                    if lane:out.append(lane.pop(0))
        return out
    def resume(self):
        """Capture the deferred queue left by an access stop, prioritized; refuses while the stop is active."""
        f=self.root/'operations/deferred-capture-queue.json';urls=read(f) if f.exists() else []
        cf=self.root/'operations/discovery-candidates.json';cands={c['url']:c for c in read(cf)} if cf.exists() else {}
        return self.capture(self.prioritize(urls,cands)) if urls else {'state':'NOTHING_DEFERRED'}
    # ---------- downstream stages ----------
    def media_posts(self):
        targets={p['id']:p for p in self.posts()};known=self.known()
        for pid in self.cfg.get('media',{}).get('prior_post_ids',[]):
            if pid not in known:raise ValueError('Selected prior media post absent from explicit corpus: '+pid)
            targets.setdefault(pid,known[pid])
        return list(targets.values())
    def media(self):
        selected=self.media_posts();postmap={p['id']:p for p in selected}
        (self.root/'data/media-source-posts.ndjson').write_text(''.join(json.dumps(p,ensure_ascii=False)+'\n' for p in selected))
        tasks=[];docs=[];held=[];old={x['asset_id']:x for x in read(self.root/'data/media-manifest.json')} if (self.root/'data/media-manifest.json').exists() else {}
        for p in selected:
            if not self.approved(p):held.append({'post_id':p['id'],'url':p['url'],'author':p['author'],'published_at':p.get('published_at'),'status':'awaiting_reference_account_qualification','media_downloaded':False,'required':'supervisor confirms public B2B role/topic relevance before watchlist and media collection'});continue
            for m in p['media']:
                if m['type']=='image':tasks.append({'post_id':p['id'],'asset_id':m['id'],'kind':'image','url':m['url']})
                if m['type']=='video':
                    vs=[v for v in m.get('renditions',[]) if isinstance(v,dict) and v.get('src')]
                    if vs:tasks.append({'post_id':p['id'],'asset_id':m['id'],'kind':'video','url':min(vs,key=lambda v:v.get('data-bitrate',10**15))['src'],'available_renditions':vs})
                    for key,kind in [('caption_url','captions'),('poster_url','poster')]:
                        if m.get(key):tasks.append({'post_id':p['id'],'asset_id':m['id']+':'+kind,'kind':kind,'url':m[key]})
            a,_,_=normalizer.post_context(BeautifulSoup(Path(p['source']['raw_path']).read_bytes(),'html.parser'),p['url'])
            for i,node in enumerate(a.select(':scope > iframe[data-native-document-config]')):
                d=json.loads(node['data-native-document-config'])['doc'];previews=d.get('coverPages',[]);docs.append({'post_id':p['id'],'title':d.get('title'),'total_pages':d.get('totalPageCount'),'exposed_preview_pages':len(previews),'complete_document':False})
                for j,page in enumerate(previews):
                    u=page.get('config',{}).get('src')
                    if u:tasks.append({'post_id':p['id'],'asset_id':f'{p["id"]}:document:{i}:page:{j}','kind':'document_preview','url':u})
        for t in tasks:t['source_capture_sha256']=postmap[t['post_id']]['source']['sha256']
        dump(self.root/'operations/account-qualification-queue.json',held)
        def cached(t):
            # Signed CDN URLs change; the cache binds to the source capture hash and the file hash instead.
            previous=old.get(t['asset_id'])
            if previous and previous.get('source_capture_sha256')==t['source_capture_sha256'] and previous.get('status')=='acquired' and (self.root/previous['path']).exists() and sha((self.root/previous['path']).read_bytes())==previous['sha256']:return {**previous,'cache_verified':True}
        def fetch(t):
            c=cached(t)
            if c:return c
            try:receipt,b=self.get(t['url'],'video' if t['kind']=='video' else 'media')
            except ValueError as e:return {**t,'status':'failed','error':'ValueError: '+str(e)}
            if b is None:return {**t,**receipt}
            ext='.mp4' if t['kind']=='video' else '.srt' if t['kind']=='captions' else '.gif' if b.startswith(b'GIF8') else '.png' if b.startswith(b'\x89PNG') else '.jpg'
            dest=self.root/'media/objects'/(sha(b)+ext)
            if not dest.exists():dest.write_bytes(b)
            a={**t,'status':'acquired','path':str(dest.relative_to(self.root)),'sha256':sha(b),'bytes':len(b),'captured_at':receipt['captured_at'],'rights':receipt['rights'],'analysis_status':'pending','http_status':receipt['http_status']}
            if t['kind']=='video':
                pp=subprocess.run([tool_command(self.cfg,'ffprobe'),'-v','quiet','-show_format','-show_streams','-of','json',str(dest)],capture_output=True,text=True,timeout=20);a['ffprobe']=json.loads(pp.stdout) if pp.returncode==0 else {'error':'ffprobe_failed'}
            return a
        assets=[];workers=self.cfg['media']['workers'];stopped=self.access_stop()
        for offset in range(0,len(tasks),workers):
            if stopped:assets.extend(cached(t) or {**t,'status':'deferred_after_access_stop'} for t in tasks[offset:]);break
            with ThreadPoolExecutor(max_workers=workers) as ex:batch=list(ex.map(fetch,tasks[offset:offset+workers]))
            assets.extend(batch)
            hit=next((x for x in batch if x.get('status')=='stopped'),None)
            if hit:stopped=self.stop('media_'+str(hit.get('http_status') or hit.get('error')),hit)
        for a in assets:
            with self.db:self.db.execute('INSERT INTO assets VALUES(?,?,?) ON CONFLICT(id) DO UPDATE SET payload=excluded.payload',(a['asset_id'],a['post_id'],json.dumps(a)))
        dump(self.root/'data/media-manifest.json',assets);dump(self.root/'data/documents.json',docs)
        return {'asset_tasks':len(assets),'acquired':sum(a['status']=='acquired' for a in assets),'unavailable':sum(a['status']!='acquired' for a in assets),'held_new_author_posts':len(held)}
    def transcribe(self):
        c=self.cfg['whisper']
        with (self.root/'operations/transcribe-stdout.txt').open('w') as out,(self.root/'operations/transcribe-stderr.txt').open('w') as err:p=subprocess.run([c['python'],str(HERE/'asr_worker.py'),'--config',str(self.config_path)],stdout=out,stderr=err,timeout=5400)
        if p.returncode:raise RuntimeError('Transcription worker failed; inspect saved stderr and partial index')
        return {'exit_code':p.returncode,'transcripts_index':str(self.root/'transcripts/index.json')}
    def transcript_qa(self):
        import transcript_qa
        assets={};transcripts={};prior_alternatives={}
        for source in self.cfg.get('transcript_qa',{}).get('corpus_datasets',[]):
            source=Path(source).resolve();base=source.parent.parent;d=read(source)
            for a in d.get('assets',[]):
                a=dict(a)
                if a.get('path'):a['path']=str((base/a['path']).resolve())
                assets[a['asset_id']]=a
            for q in d.get('transcript_qa',[]):
                alt=q.get('alternative')
                if isinstance(alt,dict) and alt.get('path'):prior_alternatives[q['asset_id']]=(base,q)
            for t in d.get('transcripts',[]):
                t=dict(t);rel=t.get('source_path') or t.get('path')
                if rel:
                    actual=(base/rel).resolve();t['source_path']=str(actual);t['transcript_source_root']=str(actual.parent.parent)
                transcripts[t['asset_id']]=t
        manifest=read(self.root/'data/media-manifest.json') if (self.root/'data/media-manifest.json').exists() else []
        for a in manifest:assets[a['asset_id']]=a
        for t in read(self.root/'transcripts/index.json') if (self.root/'transcripts/index.json').exists() else []:
            transcripts[t['asset_id']]={**t,'source_path':t['path']}
        src=self.root/'operations/transcript-qa-input.json';dump(src,{'assets':list(assets.values()),'transcripts':list(transcripts.values())})
        out,_=transcript_qa.run(src,self.root,self.root/'data/transcript-qa.json',decode=False)
        if not out['reconciliation']['ok']:raise RuntimeError('Transcript QA input/output reconciliation failed')
        carried=[]
        for rec in out['records']:
            if rec.get('alternative') or rec['asset_id'] not in prior_alternatives:continue
            base,prior=prior_alternatives[rec['asset_id']];alt=prior['alternative'];ap=(base/alt['path']).resolve()
            if prior.get('transcript_sha256')!=rec['transcript_sha256'] or prior.get('source_video_sha256')!=rec['source_video_sha256']:continue
            if not ap.is_file() or sha(ap.read_bytes())!=alt.get('sha256'):raise ValueError('Prior alternative decode source hash differs')
            data=read(ap)
            if data.get('asset_id')!=rec['asset_id'] or data.get('source_video_sha256')!=rec['source_video_sha256'] or data.get('original',{}).get('sha256')!=rec['transcript_sha256'] or data.get('supersedes_original'):raise ValueError('Prior alternative decode identity mismatch')
            rec['alternative']={**alt,'path':str(ap),'carried_from_prior_source_unchanged':True};carried.append(rec['asset_id'])
        out['alternative_summary']['prior_alternatives_carried']=carried
        out['alternative_summary']['alternatives_attached']=sorted(set(out['alternative_summary']['alternatives_attached']+carried))
        out['alternative_summary']['candidates_without_alternative']=[aid for aid in out['alternative_summary']['candidates_without_alternative'] if aid not in carried]
        for rec in out['records']+out['gap_records']:rec['qa_record_sha256']=qa_record_sha256(rec)
        dump(self.root/'data/transcript-qa.json',out)
        return {'records':len(out['records']),'gaps':len(out['gap_records']),'status_counts':out['reconciliation']['status_counts'],'prior_alternatives_carried':len(carried),'decode':False}
    def prepare(self):
        with (self.root/'operations/prepare-stdout.txt').open('w') as out,(self.root/'operations/prepare-stderr.txt').open('w') as err:p=subprocess.run([sys.executable,str(HERE/'prepare_evidence.py'),'--config',str(self.config_path)],stdout=out,stderr=err,timeout=3600)
        if p.returncode:raise RuntimeError('Evidence preparation failed; review queue not released')
        return {'exit_code':p.returncode,'evidence_index':'analysis/evidence-index.json'}
    def snapshots(self):
        out=[]
        for sid,pid,ts,h,path,kind,run,payload in self.db.execute('SELECT id,post_id,captured_at,raw_sha256,raw_path,capture_kind,source_run,payload FROM captures ORDER BY post_id,captured_at'):
            p=json.loads(payload);out.append({'snapshot_id':sid,'post_id':pid,'url':p['url'],'captured_at':ts,'capture_kind':kind,'source_run':run,'raw_sha256':h,'raw_path':path,'parser_version':p['parser_version'],'parser_sha256':p['source'].get('normalizer_sha256'),'normalization_provenance':p['source'].get('normalization_provenance'),'published_at':p.get('published_at'),'date_status':date_status(p.get('published_at'),ts),'text_sha256':sha(norm(p['text']).encode()),'reobservation_flags':p['source'].get('reobservation_flags',[]),'metrics':{k:{'value':p['metrics'][k]['value'],'status':p['metrics'][k]['status']} for k in ('reactions','comments','reposts')}})
        return out
    def qualify(self):
        cfg=self.cfg['qualification'];asof=datetime.fromisoformat(cfg['as_of']+'T23:59:59').replace(tzinfo=ZoneInfo('Europe/Sofia'));snaps=self.snapshots();known=self.known();by={}
        for s in snaps:by.setdefault(s['post_id'],[]).append(s)
        docfiles=[self.root/'data/documents.json']+[Path(c).resolve().parent/'documents.json' for c in self.corpus_paths()]
        docs={d['post_id'] for f in docfiles if f.exists() for d in read(f)};new_ids={x['id'] for x in self.posts()}
        velocity=[];qual=[]
        for pid,ss in sorted(by.items()):
            p=known.get(pid);first,last=ss[0],ss[-1];span=(parse_date(last['captured_at'])-parse_date(first['captured_at'])).total_seconds()/3600
            dates={s['published_at'] for s in ss};ds='date_conflict_hold' if len(dates)>1 else date_status(first['published_at'],first['captured_at'])
            pub=parse_date(first['published_at']) if ds=='verified_source_date' else None;age_first=round((parse_date(first['captured_at'])-pub).total_seconds()/86400,2) if pub else None
            mk=media_kind({**(p or {}),'_documents':pid in docs});ra,rb=first['metrics']['reactions']['value'],last['metrics']['reactions']['value']
            reason='eligible' if len(ss)>1 and span>=cfg['velocity_min_observation_span_hours'] and ra is not None and rb is not None and first['parser_version']==last['parser_version'] and first.get('parser_sha256')==last.get('parser_sha256') else 'single_capture' if len(ss)==1 else 'span_below_min' if span<cfg['velocity_min_observation_span_hours'] else 'parser_version_mismatch' if first['parser_version']!=last['parser_version'] or first.get('parser_sha256')!=last.get('parser_sha256') else 'metric_not_observed'
            ok=reason=='eligible';ca,cb=first['metrics']['comments']['value'],last['metrics']['comments']['value']
            velocity.append({'post_id':pid,'snapshots':len(ss),'first_captured_at':first['captured_at'],'last_captured_at':last['captured_at'],'span_hours':round(span,2),'eligible':ok,'reason':reason,'reactions_first':ra,'reactions_last':rb,'reaction_delta':rb-ra if ok else None,'reactions_per_hour':round((rb-ra)/span,4) if ok else None,'comments_delta':cb-ca if ok and ca is not None and cb is not None else None,'counter_decreased':bool(ok and rb<ra),'age_days_at_first_capture':age_first,'media_kind':mk,'cohort':age_bin(age_first)+'|'+mk,'publication_date_status':ds,'measure':'public reaction counter change; not reach, impressions, engagement rate or trend rank'})
            if p and pid in new_ids:
                age=(asof-pub).total_seconds()/86400 if pub else None
                topics=[k for k,terms in cfg['topics'].items() if any(re.search(r'(?<!\w)'+re.escape(t)+r'(?!\w)',p['text'],re.I) for t in terms)]
                qual.append({'post_id':pid,'publication_date_status':ds,'publication_date_verified':ds=='verified_source_date','age_days':round(age,2) if age is not None else None,'topic_candidates':topics,'topic_labels_are_lexical_not_semantic_validation':True,'reference_class':'fresh_candidate' if age is not None and 0<=age<=cfg['fresh_candidate_max_days'] and topics else 'recent_reference' if age is not None and 0<=age<=cfg['recent_reference_max_days'] and topics else 'historical_reference' if pub else 'date_hold','account_watchlist_approved':self.approved(p),'trending_status':'velocity_observed_not_ranked' if ok else 'not_established','sales_effectiveness':'unknown','paid_exposure':'unknown_except_explicit_tag_filter'})
        cohorts={}
        for v in velocity:
            if v['eligible']:cohorts.setdefault(v['cohort'],[]).append(v)
        cohort_rows=[]
        for c,vs in sorted(cohorts.items()):
            comparable=[v for v in vs if not v['counter_decreased']]
            rates=[v['reaction_delta']/((parse_date(v['last_captured_at'])-parse_date(v['first_captured_at'])).total_seconds()/3600) for v in comparable]
            reason='publication_age_unknown' if c.startswith('age_unknown') else 'n_below_min' if len(comparable)<cfg['same_cohort_min_posts'] else 'all_tied_or_no_positive_growth' if len(set(rates))<2 or not any(x>0 for x in rates) else None
            ranked=reason is None
            order=sorted(comparable,key=lambda v:(-(v['reaction_delta']/((parse_date(v['last_captured_at'])-parse_date(v['first_captured_at'])).total_seconds()/3600)),v['post_id'])) if ranked else sorted(comparable,key=lambda v:v['post_id'])
            cohort_rows.append({'cohort':c,'n':len(comparable),'eligible_measurement_n':len(vs),'min_n':cfg['same_cohort_min_posts'],'ranked':ranked,'not_ranked_reason':reason,'median_reactions_per_hour':round(median(rates),4) if ranked else None,'counter_decreases':sum(v['counter_decreased'] for v in vs),'distinct_unrounded_velocity_values':len(set(rates)),'members':[v['post_id'] for v in order],'excluded_counter_decrease_members':[v['post_id'] for v in vs if v['counter_decreased']],'ranking_basis':'observed unrounded reaction counter change per hour within the same age-at-first-capture and media cohort; ties are not distinct ranks; not a LinkedIn-wide trend rank'})
        dump(self.root/'data/snapshots.json',snaps);dump(self.root/'data/velocity.json',velocity);dump(self.root/'data/cohorts.json',cohort_rows);dump(self.root/'data/qualification.json',qual)
        return {'snapshots':len(snaps),'posts_with_snapshots':len(by),'velocity_eligible':sum(v['eligible'] for v in velocity),'cohorts':len(cohort_rows),'ranked_cohorts':sum(c['ranked'] for c in cohort_rows),'new_post_qualifications':len(qual)}
    def queue(self):
        assets=read(self.root/'data/media-manifest.json') if (self.root/'data/media-manifest.json').exists() else []
        tx=read(self.root/'transcripts/index.json') if (self.root/'transcripts/index.json').exists() else []
        reviews=read(self.root/'analysis/media-reviews.json') if (self.root/'analysis/media-reviews.json').exists() else []
        tqa=read(self.root/'data/transcript-qa.json') if (self.root/'data/transcript-qa.json').exists() else []
        if isinstance(tqa,dict):tqa=tqa.get('records',[])+tqa.get('gap_records',[])
        hashes={a['asset_id']:a.get('sha256') for a in assets}
        done={v['asset_id'] for v in reviews if v.get('source_sha256')==hashes.get(v['asset_id']) and v.get('review_status')=='reviewed'}
        pending=[{'asset_id':a['asset_id'],'post_id':a['post_id'],'kind':a['kind'],'path':a['path'],'source_sha256':a['sha256'],'required':'visual description; video story/framing/sequence + transcript alignment; record sampled scope truthfully','status':'awaiting_supervisor_review'} for a in assets if a['status']=='acquired' and a['kind'] in ['image','video','document_preview'] and a['asset_id'] not in done]
        ledger_path=self.root/'analysis/transcript-reviews.json';audio_reviews=read(ledger_path) if ledger_path.exists() else []
        def qa_hash_valid(t):return t.get('qa_record_sha256')==qa_record_sha256(t)
        def adjudicated(t):
            if not qa_hash_valid(t):return False
            for review in audio_reviews:
                if not isinstance(review,dict):continue
                if any(review.get(k)!=t.get(k) or not t.get(k) for k in ('asset_id','source_video_sha256','transcript_sha256','qa_record_sha256')):continue
                stamp=parse_date(review.get('reviewed_at'));reviewer=review.get('reviewer')
                if stamp is None or stamp>datetime.now(timezone.utc)+timedelta(minutes=1):continue
                if not isinstance(reviewer,str) or reviewer.strip().lower() in ('','unknown','unknown_reviewer','unverified','none','n/a','pending'):continue
                if review.get('reviewer_type') not in ('human','agent') or review.get('review_status')!='reviewed':continue
                if review.get('audio_review') is not True or not isinstance(review.get('audio_review_scope'),str) or not review['audio_review_scope'].strip():continue
                if review.get('outcome') not in ('original_confirmed','accepted_with_limitations'):continue
                return True
            return False
        pending+=[{'asset_id':t['asset_id'],'post_id':t['post_id'],'kind':'transcript_qa','flags':t.get('flags',[]),'source_video_sha256':t.get('source_video_sha256'),'transcript_sha256':t.get('transcript_sha256'),'qa_record_sha256':t.get('qa_record_sha256'),'required':'source-bound audio adjudication in analysis/transcript-reviews.json; compare original/alternative, keep both; boolean supervisor_reviewed is insufficient','status':'awaiting_supervisor_review'} for t in tqa if (t.get('status') not in ['pass','not_applicable_no_audio'] or not qa_hash_valid(t)) and not adjudicated(t)]
        def valid_transcript(v,t):
            if t.get('asset_id')!=v['asset_id'] or t.get('source_video_sha256')!=v['sha256']:return False
            try:
                path=(self.root/t['path']).resolve()
                if not path.is_relative_to(self.root) or not path.is_file():return False
                d=read(path)
                if d.get('asset_id')!=v['asset_id'] or d.get('source_video_sha256')!=v['sha256']:return False
                if d.get('review_status') not in ['transcript_available_not_audio_verified','not_applicable_no_audio']:return False
                if d.get('text','').strip():return True
                streams=v.get('ffprobe',{}).get('streams',[])
                return d.get('origin')=='no_audio_stream_in_acquired_file' and any(s.get('codec_type')=='video' for s in streams) and not any(s.get('codec_type')=='audio' for s in streams)
            except (ValueError,KeyError,OSError,TypeError):return False
        unresolved=[a for a in assets if a['status']!='acquired'];videos=[a for a in assets if a['kind']=='video' and a['status']=='acquired'];missing_tx=[v['asset_id'] for v in videos if not any(valid_transcript(v,t) for t in tx)];held=[p for p in self.media_posts() if not self.approved(p)]
        for v in videos:
            current=next((t for t in tx if valid_transcript(v,t)),None)
            if not current:continue
            file_hash=sha((self.root/current['path']).read_bytes())
            matching=[q for q in tqa if q.get('asset_id')==v['asset_id'] and q.get('source_video_sha256')==v['sha256'] and q.get('transcript_sha256')==file_hash and qa_hash_valid(q)]
            if not matching:pending.append({'asset_id':v['asset_id'],'post_id':v['post_id'],'kind':'transcript_qa','status':'awaiting_transcript_quality_check','required':'run transcript-qa on current video/transcript hashes'})
        deferred=read(self.root/'operations/deferred-capture-queue.json') if (self.root/'operations/deferred-capture-queue.json').exists() else []
        captures=self.db.execute('select count(*) from captures').fetchone()[0]
        bf=self.root/'operations/blocked-urls.json';blocked=read(bf) if bf.exists() else {};open_blocked=[u for u,b in blocked.items() if not b.get('resolution')]
        state='ACCESS_STOPPED' if self.access_stop() else 'NO_SOURCES' if not captures else 'COLLECTION_PARTIAL' if unresolved or deferred or open_blocked else 'TRANSCRIPTION_PENDING' if missing_tx else 'AWAITING_ACCOUNT_QUALIFICATION' if held else 'AWAITING_SUPERVISOR_REVIEW' if pending else 'READY_FOR_VERIFICATION'
        dump(self.root/'operations/review-queue.json',pending);event=self.event('collection_and_transcription_checkpoint',{'pipeline_version':VERSION,'new_posts':len(self.posts()),'captures':captures,'assets':len(assets),'transcripts':len(tx),'pending_reviews':len(pending),'unavailable_assets':len(unresolved),'deferred_urls':len(deferred),'blocked_urls':len(blocked),'blocked_unresolved':len(open_blocked),'missing_transcript_asset_ids':missing_tx,'unqualified_accounts_posts':len(held),'state':state,'delivery':'durable local event only; not an agent wakeup','schedule_active':False})
        dump(self.root/'operations/supervisor-event.json',event);return event

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',type=Path,default=HERE/'config.json')
    p.add_argument('command',choices=['import-baseline','refresh','discover','capture','resume','ingest','media','transcribe','transcript-qa','prepare','qualify','queue','cycle','status']);p.add_argument('--input',type=Path)
    p.add_argument('--no-discover',action='store_true');p.add_argument('--no-refresh',action='store_true');a=p.parse_args()
    try:c=Cycle(a.config)
    except Locked as e:print(json.dumps({'state':'LOCKED_ANOTHER_RUN_ACTIVE','error':str(e)}));sys.exit(3)
    c.config_path=a.config.resolve()
    if a.command=='import-baseline':out=c.import_baseline()
    elif a.command=='refresh':out=c.refresh()
    elif a.command=='discover':out=c.discover()
    elif a.command=='capture':out=c.capture(read(a.input or c.root/'operations/url-queue.json'))
    elif a.command=='resume':out=c.resume()
    elif a.command=='media':out=c.media()
    elif a.command=='transcribe':out=c.transcribe()
    elif a.command=='transcript-qa':out=c.transcript_qa()
    elif a.command=='prepare':out=c.prepare()
    elif a.command=='qualify':out=c.qualify()
    elif a.command=='queue':out=c.queue()
    elif a.command=='status':out={'pipeline_version':VERSION,'new_posts':len(c.posts()),'captures':c.db.execute('select count(*) from captures').fetchone()[0],'events':c.db.execute('select count(*) from events').fetchone()[0],'access_stop':c.access_stop(),'schedule_active':False}
    elif a.command=='ingest':raise SystemExit('ingest replay is v3-only; v4 records reobservations through capture/refresh')
    else:
        out={'import_baseline':c.import_baseline()}
        if not a.no_refresh:out['refresh']=c.refresh()
        if not a.no_discover:out['discover']=c.discover();out['capture']=c.capture(out['discover']['urls'])
        out['media']=c.media();out['transcribe']=c.transcribe();out['transcript_qa']=c.transcript_qa();out['prepare']=c.prepare();out['qualify']=c.qualify();out['checkpoint']=c.queue()
    out['requests_made']=c.requests_made;print(json.dumps(out,indent=2,ensure_ascii=False,default=str))
if __name__=='__main__':
    try:main()
    except SystemExit:raise
    except Exception as e:
        try:
            config=Path(sys.argv[sys.argv.index('--config')+1]) if '--config' in sys.argv else HERE/'config.json';Cycle(config,lock=False).event('cycle_failed',{'error_type':type(e).__name__,'error':str(e),'state':'FAILED_REQUIRES_REVIEW','schedule_active':False})
        except Exception:pass
        raise
