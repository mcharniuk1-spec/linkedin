"""Write a local, explicit, source-separated dashboard snapshot."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from .cli import load_config
from .coverage import daily_progress
from .store import Store
from .consented_exports import ConsentedStore


def build(store, *, authorized=None):
    progress = daily_progress(store)
    tables = {r[0] for r in store.db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    queues = {'publication': [], 'reference_account': [], 'target_company': []}
    if 'candidate_queue' in tables:
        for category, payload in store.db.execute('SELECT category,payload FROM candidate_queue ORDER BY rowid DESC LIMIT 10000'):
            if category in queues: queues[category].append(json.loads(payload))
    external = []
    if 'external_discovery_items' in tables:
        for (metadata,) in store.db.execute('SELECT metadata FROM external_discovery_items ORDER BY last_seen DESC LIMIT 10000'):
            item=json.loads(metadata)
            engagement=item.get('engagement') or {}
            external.append({'title':item.get('title'), 'source_id':item.get('source_id'),
                'source_url':item.get('source_url'), 'source_type':item.get('source_platform'),
                'discovered_at':item.get('observed_at'), 'permission_state':item.get('permission_state'),
                'review_status':item.get('review_status'),
                'description': ('Hacker News discussion descendants: '+str(engagement.get('hn_descendant_count'))
                                if engagement.get('hn_descendant_count') is not None else None),
                'metrics':{'score':engagement.get('hn_score'), 'comments':None}})
    start=datetime.fromisoformat(progress['window_start_utc']); end=datetime.fromisoformat(progress['window_end_utc'])
    now=datetime.now(timezone.utc); daily_runs=[]
    for (payload,) in store.db.execute('SELECT payload FROM runs ORDER BY rowid'):
        try:
            run=json.loads(payload); stamp=datetime.fromisoformat(run['started_at'].replace('Z','+00:00'))
            if stamp.tzinfo is not None and start<=stamp<end and stamp<=now:daily_runs.append(run)
        except (ValueError,TypeError,KeyError):continue
    last=daily_runs[-1] if daily_runs else {}; sources_by_id={}
    for run in daily_runs:
        for result in run.get('external_discovery',{}).get('source_results',[]):
            sid=result['source_id']; entry=sources_by_id.setdefault(sid,{'source_id':sid,
                'attempted_requests':0,'successful_requests':0,'quota_used':None,'quota_limit':None})
            entry.update(status=result['status'],hold=result['status']=='held',observed_at=run.get('finished_at'))
            entry['attempted_requests']+=result['requests']
            entry['successful_requests']+=result.get('successful_requests',0)
        prospect=run.get('prospect_discovery')
        if isinstance(prospect,dict):
            sid=prospect['source_id'];entry=sources_by_id.setdefault(sid,{'source_id':sid,
                'attempted_requests':0,'successful_requests':0,'quota_used':None,'quota_limit':None})
            entry.update(status=prospect['status'],hold=prospect['status']=='held',observed_at=run.get('finished_at'))
            entry['attempted_requests']+=prospect['requests'];entry['successful_requests']+=prospect['successful_requests']
        metrics=run.get('metrics',{}).get('exa-search')
        if metrics:
            entry=sources_by_id.setdefault('exa-search',{'source_id':'exa-search','attempted_requests':0,
                'successful_requests':0,'quota_used':None,'quota_limit':None})
            entry.update(status='completed_or_see_errors',hold=bool(store.get_suspension('exa-search')))
            entry['attempted_requests']+=metrics['request_events']
            entry['successful_requests']+=metrics.get('successful_http_responses',0)
    for error in last.get('errors',[]):
        sid=error.get('source_id');entry=sources_by_id.setdefault(sid,{'source_id':sid})
        entry.update(status=error.get('error_code'),hold=error.get('error_code')=='source_access_hold')
    sources=list(sources_by_id.values())
    posts_by_id={}
    for row in authorized or []:
        if row.get('granularity')!='post': continue
        key=row['subject_id']
        post=posts_by_id.setdefault(key,{'title':'Owner-provided analytics export', 'source_id':'owner-export',
            'source_url':row.get('post_url'), 'permission_state':'owner_attested',
            'review_status':'pending', 'published_at':row.get('date'),
            'publication_date_status':'day_only_unverified', 'observed_at':row['observed_at'],
            'metrics':row['metrics'], 'snapshots':[]})
        post['snapshots'].append({'source_id':'owner-export','parser_version':'owner-export-v1',
                                  'observed_at':row['observed_at'],'metrics':row['metrics']})
        post['metrics']=row['metrics'];post['observed_at']=row['observed_at']
        if not post['source_url']:post['source_url']=row.get('post_url')
    hold=store.get_suspension('linkedin-public')
    return {'schema':'outspoken-research-viewer/1','generated_at':datetime.now(timezone.utc).isoformat(),
        'operations':{'linkedin_status':'blocked' if hold else 'not verified',
          'status_notes':'Independent discovery is not LinkedIn collection. Owner consent is attested.',
          'duplicates':sum(r.get('duplicates',0) for r in daily_runs) if daily_runs else None, 'missed_or_delayed_runs':None,
          'daily_progress':progress, 'sources':sources},
        'authorized_posts':list(posts_by_id.values()),'reference_candidates':queues['publication']+queues['reference_account'],
        'external_signals':external,'target_companies':queues['target_company']}


def main():
    ap=argparse.ArgumentParser(description='Write a private local viewer snapshot')
    ap.add_argument('--config',required=True);ap.add_argument('--output',required=True)
    ap.add_argument('--owner-store');ap.add_argument('--account-id')
    args=ap.parse_args(); output=Path(args.output).expanduser().absolute()
    if output.parent.resolve()!=output.parent:
        raise ValueError('symlinked_output_parent_forbidden')
    if any((p/'.git').exists() for p in (output.parent,*output.parents)):
        raise ValueError('output_must_be_outside_git')
    if bool(args.owner_store)!=bool(args.account_id):raise ValueError('owner_store_and_account_required')
    cfg=load_config(args.config); store=Store(cfg['state_dir']); owner=None
    try:
        if args.owner_store:
            owner=ConsentedStore(args.owner_store); authorized=owner.get_snapshots(args.account_id)
        else: authorized=[]
        with store.lock(): data=build(store,authorized=authorized)
        output.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
        fd=os.open(output,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
        with os.fdopen(fd,'w',encoding='utf-8') as f: json.dump(data,f,ensure_ascii=False,indent=2)
        print('Private snapshot written; select it in the local viewer.')
    finally:
        if owner: owner.close()
        store.close()


if __name__=='__main__':main()
