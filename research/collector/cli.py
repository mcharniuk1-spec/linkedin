"""Collection-only jobs and explicit manual review preparation. No social writes."""
from __future__ import annotations
from datetime import datetime,timezone
from pathlib import Path
import argparse,asyncio,csv,hashlib,json,os,shutil,time,uuid
from .contracts import CollectionError,ConfigurationError,AccessSuspended,utcnow
from .store import Store


def unique(items):
    out={}
    for k,v in items:
        if k in out:raise ConfigurationError('duplicate_configuration_key')
        out[k]=v
    return out


def load_config(path):
    path=Path(path).resolve();cfg=json.loads(path.read_text(),object_pairs_hook=unique)
    if cfg.get('schema')!='linkedin-hybrid-config/1':raise ConfigurationError('unknown_config_schema')
    cfg['_path']=str(path)
    for name in ('state_dir','baseline_seed'):
        cfg[name]=str((path.parent/cfg[name]).resolve())
    if not 1<=int(cfg.get('max_new_records',20))<=100:raise ConfigurationError('record_limit_out_of_range')
    if not 1<=int(cfg.get('max_candidates',40))<=160:raise ConfigurationError('candidate_limit_out_of_range')
    return cfg


def _repo():
    return Path(__file__).resolve().parents[2]


def credential_settings(cfg):
    from .oauth import Credentials
    cid=os.environ.get('LINKEDIN_CLIENT_ID');secret=os.environ.get('LINKEDIN_CLIENT_SECRET')
    if cid and secret:return Credentials(cid,secret)
    path=os.environ.get(cfg.get('oauth',{}).get('client_credentials_file_env','LINKEDIN_CREDENTIALS_FILE'))
    if not path:raise ConfigurationError('linkedin_credentials_unavailable')
    return Credentials.from_yaml(path)


def preflight(cfg):
    oauth=cfg.get('oauth',{});redirect=os.environ.get(oauth.get('redirect_uri_env','LINKEDIN_REDIRECT_URI'))
    try:
        credential_settings(cfg);credentials=True
    except ConfigurationError:
        credentials=False
    vault=Path(cfg['state_dir'])/oauth.get('token_vault','tokens.enc')
    return {'credential_configuration_present':credentials,'registered_redirect_configured':bool(redirect),
        'requested_scopes_configured':bool(oauth.get('scopes')),'encrypted_token_present':vault.is_file(),
        'api_access_proven':False,'global_profile_or_trending_search_available':False,
        'secret_values_printed':False,'next_step':'Configure the exact registered redirect and approved read scopes, then complete member consent. Server responses must prove resource access.'}


class TimedTransport:
    def __init__(self,base,store,source_id):self.base=base;self.state=store;self.source_id=source_id
    async def fetch(self,url,*,headers=None):
        start=time.perf_counter();status=None
        try:
            result=await self.base.fetch(url,headers=headers);status=result.status_code;return result
        finally:
            self.state.log_request(self.source_id,{'kind':'fetch_call','status_code':status,
                'latency_ms':(time.perf_counter()-start)*1000,'collected_at':utcnow()})
    async def aclose(self):await self.base.aclose()


def _capacity(store,cfg):
    pages=store.db.execute('PRAGMA page_count').fetchone()[0];size=store.db.execute('PRAGMA page_size').fetchone()[0]
    return pages*size+4_000_000<int(cfg.get('max_database_bytes',24*1024*1024))


async def collect(config_path, *, discover_fn=None, transport_factory=None):
    cfg=load_config(config_path);store=Store(cfg['state_dir']);report={'run_id':uuid.uuid4().hex,'started_at':utcnow(),
        'mode':'collection_only_new_records','inserted':0,'duplicates':0,'new_profiles':0,'errors':[],
        'analysis_executed':False,'refresh_executed':False,'automatic_media_bytes':False}
    start=time.perf_counter()
    try:
        with store.lock():
            seed=json.loads(Path(cfg['baseline_seed']).read_text(),object_pairs_hook=unique);store.seed(seed)
            before=store.counts();initial_requests={x[0] for x in store.db.execute('SELECT id FROM requests')}
            candidates=[]
            if cfg.get('discovery',{}).get('enabled') and _capacity(store,cfg):
                from .discovery import discover
                try:
                    candidates=(discover_fn or discover)(cfg['discovery'],store,cfg.get('approved_author_paths',[]))
                except (CollectionError,ValueError,KeyError):
                    report['errors'].append({'source_id':'exa-search','error_code':'discovery_unavailable'})
            from .transport import HttpxTransport,UrllibTransport
            from .adapters import StaticHTTPAdapter,FeedAdapter,GenericAPIAdapter,PlaywrightAdapter,ScrapyAdapter
            adapters={'http':StaticHTTPAdapter,'rss':FeedAdapter,'api':GenericAPIAdapter,
                      'playwright':PlaywrightAdapter,'scrapy':ScrapyAdapter}
            class LimitReached(CollectionError):pass
            def accept(value):
                if report['inserted']>=cfg['max_new_records'] or not _capacity(store,cfg):raise LimitReached('capacity_or_record_cap')
                result=store.ingest(value)
                report['inserted' if result['inserted'] else 'duplicates']+=1
            for raw in cfg.get('sources',[]):
                spec=dict(raw)
                if not spec.get('enabled'):
                    if spec.get('access_hold'):report['errors'].append({'source_id':spec['source_id'],'error_code':'configured_access_hold'})
                    continue
                if report['inserted']>=cfg['max_new_records'] or not _capacity(store,cfg):
                    report['capacity_hold']=True;break
                kind=spec.get('adapter');source_id=spec['source_id']
                if kind=='http' and 'www.linkedin.com' in spec.get('allowed_hosts',[]):
                    spec['urls']=list(dict.fromkeys(spec.get('urls',[])+candidates))[:cfg['max_candidates']]
                cls=HttpxTransport if kind=='linkedin_api' or cfg.get('default_transport')=='httpx' else UrllibTransport
                base=transport_factory(spec,store) if transport_factory else cls(spec,store)
                transport=TimedTransport(base,store,source_id)
                try:
                    if kind=='linkedin_api':
                        from .linkedin_api import ReadonlyLinkedInAPIAdapter
                        from .oauth import EncryptedTokenVault,OAuthClient
                        from .ci_state import key
                        vault=EncryptedTokenVault(Path(cfg['state_dir'])/'tokens.enc',key()[0])
                        token=vault.load(allow_expired=bool(cfg.get('oauth',{}).get('refresh_entitled')))
                        if token['expires_at']<time.time()+3600 and cfg.get('oauth',{}).get('refresh_entitled'):
                            auth=OAuthClient(credential_settings(cfg),os.environ['LINKEDIN_REDIRECT_URI'],refresh_entitled=True)
                            token=auth.refresh(token);vault.save(token)
                        await ReadonlyLinkedInAPIAdapter().collect(spec,transport,Path(cfg['state_dir']),store.known_url,token,on_record=accept)
                    elif kind in adapters:
                        # Per-page commits prevent a later denial losing earlier successful records.
                        if kind=='http':
                            unsupported=0
                            for url in spec.get('urls',[]):
                                if report['inserted']>=cfg['max_new_records'] or not _capacity(store,cfg):
                                    report['capacity_hold']=True;break
                                try:
                                    await adapters[kind]().collect({**spec,'urls':[url]},transport,Path(cfg['state_dir']),store.known_url,on_record=accept)
                                    unsupported=0
                                except ValueError:
                                    unsupported+=1;report['errors'].append({'source_id':source_id,'error_code':'unsupported_source_or_identity_hold'})
                                    if unsupported>=3:
                                        store.suspend(spec.get('access_group',source_id),'repeated_unsupported_layout');raise AccessSuspended('unsupported_layout_stop')
                        else:
                            await adapters[kind]().collect(spec,transport,Path(cfg['state_dir']),store.known_url,on_record=accept)
                    else:raise ConfigurationError('unknown_adapter')
                except LimitReached:
                    report['capacity_hold']=True;break
                except (CollectionError,ValueError,OSError,KeyError) as exc:
                    report['errors'].append({'source_id':source_id,'error_code':type(exc).__name__})
                finally:
                    await transport.aclose()
            after=store.counts();report['new_profiles']=after['profiles']-before['profiles'];report['state_counts']=after
            events=[(sid,json.loads(payload)) for k,sid,payload in store.db.execute('SELECT id,source_id,payload FROM requests') if k not in initial_requests]
            metrics={}
            for sid,e in events:
                m=metrics.setdefault(sid,{'request_events':0,'fetch_latency_ms':[],'access_or_rate_responses':0,'error_events':0})
                m['request_events']+=1
                if e.get('kind')=='fetch_call':m['fetch_latency_ms'].append(e['latency_ms'])
                if e.get('status_code') in (401,403,429,999):m['access_or_rate_responses']+=1
                if e.get('error_code'):m['error_events']+=1
            for m in metrics.values():
                lat=m.pop('fetch_latency_ms');m['mean_fetch_latency_ms']=sum(lat)/len(lat) if lat else None
                m['latency_definition']='End-to-end fetch call including configured pacing/retry delay.'
            report.update(metrics=metrics,elapsed_seconds=time.perf_counter()-start,
                status='COMPLETE' if not report['errors'] and not after['suspensions'] else 'COMPLETE_WITH_SOURCE_HOLDS',finished_at=utcnow())
            with store.db:store.db.execute('INSERT INTO runs VALUES (?,?)',(report['run_id'],json.dumps(report,sort_keys=True)))
            (Path(cfg['state_dir'])/'last-run.json').write_text(json.dumps(report,indent=2)+'\n')
            return report
    finally:store.close()


def update_run(config_path, output=None):
    """Prepare a private source-bound handoff; never run an LLM or claim media review."""
    cfg=load_config(config_path);store=Store(cfg['state_dir'])
    try:
        with store.lock():
            store.seed(json.loads(Path(cfg['baseline_seed']).read_text()))
            output=Path(output) if output else Path(cfg['state_dir'])/'manual'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
            result=store.export_pending(output)
            discoveries=[]
            if store.db.execute("SELECT 1 FROM sqlite_master WHERE name='discoveries'").fetchone():
                discoveries=[json.loads(x[0]) for x in store.db.execute('SELECT payload FROM discoveries')]
            for d in discoveries:
                h=d.get('raw_sha256')
                if h:
                    raw=output/'raw'/f'{h}.bin';raw.parent.mkdir(exist_ok=True,mode=0o700);raw.write_bytes(store.raw_bytes(h));os.chmod(raw,0o600);d['raw_path']=str(raw.relative_to(output))
            discovery_path=output/'discovery-observations.ndjson';discovery_path.write_text(''.join(json.dumps(d)+'\n' for d in discoveries));os.chmod(discovery_path,0o600)
            result['discovery_observations']=len(discoveries)
            fields=['record_id','source_id','external_id','source_url','content_hash','raw_sha256','topic','reader','editorial_job','hook','claim','image_structure_style','video_story_timestamps','transcript_path','reference_value','performance_evidence','practical_adaptation','limitations','review_status']
            with (output/'insights.csv').open('w',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
                for row in store.pending():writer.writerow({**{k:row.get(k,'') for k in fields},'review_status':'pending_actual_source_review'})
            from .writing_graph import build_writing_graph
            graph=build_writing_graph(_repo())
            packet={'schema':'linkedin-manual-update/1','created_at':utcnow(),**result,'insights_table':'insights.csv',
                'graph':graph,'tool_readiness':{'ffmpeg':bool(shutil.which('ffmpeg')),'ffprobe':bool(shutil.which('ffprobe')),
                'cached_whisper_model':(Path.home()/'.cache/whisper/large-v3-turbo.pt').is_file()},
                'automatic_stages_executed':[],
                'next_steps':['Read original source facts and exact hashes; qualify author/business fit before media.',
                    'Use existing permitted media/cached Whisper/frame preparation only for explicitly requested stages.',
                    'Actually inspect each image and source-bound video evidence; distinguish frame sampling, continuous watching and listening.',
                    'Preserve original transcripts; append QA alternatives and exact-source review; do not clear audio flags mechanically.',
                    'Fill practical insights with sources and limitations, then pass existing release/export/public-boundary checks.']}
            (output/'analysis-packet.json').write_text(json.dumps(packet,indent=2)+'\n');os.chmod(output/'analysis-packet.json',0o600);os.chmod(output/'insights.csv',0o600);return packet
    finally:store.close()


def oauth_start(cfg,allow_loopback=False):
    from .oauth import OAuthClient
    from .ci_state import key
    oauth=cfg.get('oauth',{});redirect=os.environ.get(oauth.get('redirect_uri_env','LINKEDIN_REDIRECT_URI'),'')
    auth=OAuthClient(credential_settings(cfg),redirect,allow_loopback_http=allow_loopback)
    begun=auth.begin(oauth.get('scopes',[]));state_dir=Path(cfg['state_dir']);state_dir.mkdir(parents=True,exist_ok=True,mode=0o700)
    state=key()[1].encrypt(json.dumps({'pending':auth._pending,'redirect_uri':redirect,'allow_loopback_http':allow_loopback}).encode())
    p=state_dir/'oauth-state.enc';p.write_bytes(state);os.chmod(p,0o600)
    import html
    page=state_dir/'authorize.html';page.write_text('<!doctype html><meta charset="utf-8"><title>LinkedIn read authorization</title><h1>Authorize approved LinkedIn read scopes</h1><p>Continue only if the app and scopes match your intention.</p><a href="'+html.escape(begun['authorization_url'],quote=True)+'">Continue to LinkedIn</a>');os.chmod(page,0o600)
    return {'status':'AWAITING_MEMBER_CONSENT','local_authorization_page':str(page),'credential_values_printed':False}


def oauth_finish(cfg):
    from .oauth import OAuthClient,EncryptedTokenVault
    from .ci_state import key
    import getpass
    state_dir=Path(cfg['state_dir']);saved=json.loads(key()[1].decrypt((state_dir/'oauth-state.enc').read_bytes()))
    auth=OAuthClient(credential_settings(cfg),saved['redirect_uri'],allow_loopback_http=saved['allow_loopback_http']);auth._pending=saved['pending']
    # Never put codes/tokens in argv, reports, chat or shell history.
    returned=getpass.getpass('Paste the exact returned callback URL (hidden): ')
    from urllib.parse import urlsplit,parse_qs
    actual=urlsplit(returned);expected=urlsplit(saved['redirect_uri'])
    if (actual.scheme,actual.netloc,actual.path)!=(expected.scheme,expected.netloc,expected.path):raise ConfigurationError('callback_redirect_mismatch')
    query=parse_qs(actual.query,strict_parsing=True)
    if {k:v for k,v in query.items() if k not in {'code','state'}} != parse_qs(expected.query):raise ConfigurationError('callback_static_query_mismatch')
    if any(len(query.get(k,[]))!=1 for k in ('code','state')):raise ConfigurationError('callback_code_or_state_invalid')
    token=auth.exchange(query['code'][0],query['state'][0])
    token['authorized_actors']=[a for s in cfg['sources'] if s['adapter']=='linkedin_api' for a in s.get('authorized_actors',[])]
    EncryptedTokenVault(state_dir/'tokens.enc',key()[0]).save(token);(state_dir/'oauth-state.enc').unlink()
    return {'status':'TOKEN_STORED_ENCRYPTED','resource_access_proven':False,'granted_read_scopes':token['scope'].split(),'next_step':'Run authorized resource preflight; a successful token exchange does not prove data access.'}


def main(argv=None):
    ap=argparse.ArgumentParser();ap.add_argument('command',choices=['collect','status','update-run','oauth-preflight','oauth-start','oauth-finish','resume-source'])
    ap.add_argument('--config',default=str(Path(__file__).with_name('config.json')));ap.add_argument('--output');ap.add_argument('--access-group');ap.add_argument('--reason');ap.add_argument('--allow-loopback-http',action='store_true');args=ap.parse_args(argv)
    try:
        cfg=load_config(args.config)
        if args.command=='collect':result=asyncio.run(asyncio.wait_for(collect(args.config),timeout=min(1200,int(cfg.get('max_run_seconds',600)))))
        elif args.command=='update-run':result=update_run(args.config,args.output)
        elif args.command=='oauth-preflight':result=preflight(cfg)
        elif args.command=='oauth-start':result=oauth_start(cfg,args.allow_loopback_http)
        elif args.command=='oauth-finish':result=oauth_finish(cfg)
        else:
            store=Store(cfg['state_dir'])
            try:
                if args.command=='resume-source':store.resume(args.access_group or '',args.reason or '')
                result={'counts':store.counts(),'outbound_requests':0}
            finally:store.close()
        print(json.dumps(result,indent=2));return 2 if args.command=='collect' and result.get('status')!='COMPLETE' else 0
    except (CollectionError,ValueError,OSError,KeyError) as exc:
        print(json.dumps({'status':'FAILED_CLOSED','error_code':type(exc).__name__,'details':'Inspect the local configuration and operational record; secrets and raw errors are intentionally omitted.'}));return 2

if __name__=='__main__':raise SystemExit(main())
