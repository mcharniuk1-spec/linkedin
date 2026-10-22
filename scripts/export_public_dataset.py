#!/usr/bin/env python3
"""Build a field-allowlisted public derived dataset. No network or source-media copy."""
import argparse,csv,hashlib,json,math,os,re,sqlite3,tempfile
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import urlsplit,urlunsplit

SCHEMA='linkedin-public-derived/1'
SEM_FIELDS=('text_sha256','content_language','primary_topic','secondary_topics','editorial_job','intended_reader','content_summary','hook_pattern','central_claim','reference_value','qualification_reason','media_role','media_evidence_basis','claim_caveat','adaptation_pattern','variant_group_id','pattern_representative')
PERF_FIELDS=('metric_snapshot_id','metric_source_sha256','metric_captured_at','reactions','comments','reposts','metric_statuses','publication_date_conflict','format','content_language','age_days_at_metric_capture','comparison_cohort','comparison_n','comparison_median_reactions','pattern_representative','reaction_midrank_percentile','performance_status','performance_reason','trend_status','trend_reason','causal_status','sales_effectiveness','scope')
SNAP_FIELDS=('snapshot_id','post_id','captured_at','capture_kind','source_run','raw_sha256','parser_version','parser_sha256','published_at','date_status','text_sha256','reobservation_flags')
NORM_FIELDS=('kind','source_run','source_parser_version','original_observed_at','raw_sha256')
DESC_KEYS=set(('literal','style','structure','role','conflicts','transfer','format','setting','composition','hierarchy','typography','palette','framing','camera_and_editing','story','hook','cta','CTA','practical_category','relation_to_post_text','interpretation','legibility_limits','literal_visible','form','colors','subject','CTA_and_structure','visual_hook','structure_style','legibility','cuts','transfer_hypothesis','narrative_sequence','visual_timeline','subtitles','edit_boundaries','speaker_or_graphics','evidence_vs_interpretation','visible_actors','colors_and_graphics','typography_and_legibility','visual_verbal_relationship','presenter_and_styling','diagram','argument','key_emphasis','framing_and_editing','timecode','fact','evidence','seconds','start','end','timestamp','scene','visual','meaning','caveat','confidence','stage','description','caption_style'))
FORBIDDEN_KEYS={'text','post_text','raw_path','source_path','transcript_path','original_path','filename','on_image_text','onscreen_text_observed','reviewer','reviewer_identity','reviewer_task','supervisor_review','employee_list','employees','contacts','email','phone'}
PRIVATE_PREFIXES=['/'+'Users/','/'+'private/var/','/'+'private/tmp/','/'+'var/folders/','/'+'home/','/'+'opt/homebrew/','/'+'root/']
PRIVATE_RE=re.compile('|'.join(re.escape(x) for x in PRIVATE_PREFIXES)+r'|[A-Za-z]:\\'+r'Users\\|(?:ghp_|github_pat_|sk-proj-)[A-Za-z0-9_-]{10,}',re.I)
METRICS=('reactions','comments','reposts')


def unique_pairs(items):
    d={}
    for k,v in items:
        if k in d:raise ValueError('Duplicate JSON key: '+k)
        d[k]=v
    return d


def pick(source,fields):
    return {k:source[k] for k in fields if k in source}


def source_url(value):
    if value in (None,''):return None
    p=urlsplit(str(value))
    if p.scheme not in ('https','http') or not p.hostname or p.username or p.password:raise ValueError('Invalid public source URL')
    if p.hostname=='licdn.com' or p.hostname.endswith('.licdn.com'):raise ValueError('CDN media URL is not a public projection source locator')
    return urlunsplit((p.scheme,p.netloc,p.path,'',''))


def metric(source):
    value=source.get('value');status=source.get('status','unknown')
    if not isinstance(status,str):raise ValueError('Metric status must be a scalar label')
    if value is not None and (type(value) not in (int,float) or not math.isfinite(value)):raise ValueError('Invalid numeric metric')
    return {'value':value,'status':status}


def describe(value):
    """Keep only owned descriptive fields; never copy observed text or source paths."""
    if isinstance(value,str):return value[:6000]
    if isinstance(value,list):return [describe(x) for x in value[:60] if isinstance(x,(str,dict,int,float))]
    if isinstance(value,dict):return {k:describe(v) for k,v in value.items() if k in DESC_KEYS}
    if value is None or type(value) in (int,float,bool):return value
    return None


def public_review(raw):
    if not raw:return None
    review=pick(raw,('review_status','review_mode','source_sha256','source_video_sha256','duration_seconds','story_summary','visual_description','story_or_message','layout_and_composition','typography','palette','format_type','relation_to_post_text','contradictions','uncertainty','inference_limits','interpretation_limit','legibility_limits','limitations','caveats','full_watch','audio_review','sampled_frames_reviewed','sample_interval_seconds','sampled_frame_count','frame_interval_seconds','decoded_sample_count','claims_and_limits','adaptation_for_founders'))
    review['description']=describe(raw.get('description') or raw.get('literal_and_structure') or raw.get('literal_visible') or {})
    # Fields such as on_image_text, transcript_evidence, sheets, reviewer and paths are excluded.
    review['scope']='Owned descriptive analysis only. Source media and full transcripts remain local; sampled frames do not establish continuous watching or audio accuracy.'
    return review


def public_transcript(transcript,qa):
    if not transcript and not qa:return None
    out=pick(transcript or {},('asset_id','post_id','origin','source_video_sha256','source_sha256','audio_verified','full_watch','timing_status','timing_overrun_seconds','caption_end_overrun_seconds'))
    out.update(available=bool(transcript),full_text_distribution='retained_locally_not_published')
    if qa:
        out['qa']=pick(qa,('status','flags','origin_family','transcript_kind','duration_seconds','text_chars','timed_units','last_timed_end','audio_verified','accuracy_verified','qa_record_sha256','transcript_sha256','source_video_sha256'))
        alt=qa.get('alternative');out['alternative_available']=isinstance(alt,dict)
        if isinstance(alt,dict):
            out['alternative']=pick(alt,('sha256','review_status','supersedes_original','adjudication'))
            out['alternative']['qa']=pick(alt.get('qa',{}) or {},('status','flags','duration_seconds','text_chars','timed_units','last_timed_end','audio_verified','accuracy_verified'))
            sides={}
            for name in ('original','alternative'):
                side=(alt.get('side_by_side') or {}).get(name,{})
                sides[name]=pick(side,('status','flags','text_chars','timed_units','last_timed_end'))
                if type(side.get('segments')) is int:sides[name]['segment_count']=side['segments']
            out['alternative']['comparison']=sides
    return out


def public_author(raw):
    out=pick(raw,('author_key','author_name','decision','role_or_company_evidence','source_evidence_summary','reason','reference_transfer','caveat','professional_role_status','media_collection_decision','decision_scope','observed_role','company','reviewed_at','checked_at','uncertainty'))
    out['author_url']=source_url(raw.get('author_url'))
    out['source_posts']=[{**pick(x,('post_id','raw_sha256','text_sha256')),'url':source_url(x.get('url'))} for x in raw.get('source_posts',[])]
    out['role_sources']=[]
    for field in ('sources','role_sources','evidence_sources','professional_sources','role_resolution_evidence'):
        for x in raw.get(field,[]) if isinstance(raw.get(field),list) else []:
            if not isinstance(x,dict):continue
            out['role_sources'].append({**pick(x,('title','observed_at','published_at','accessed_at','status','source_id','fact','evidence_summary','evidence_id','observed_at_utc','retrieval_mode','source_published_at','fact_paraphrase','limitation','receipt_sha256')),'url':source_url(x.get('url') or x.get('source_url'))})
    return out


def public_prospect(raw):
    out=pick(raw,('id','stable_key','name','description','reviewed_at','fit_status','fit_is_not_sales_qualification','gaps','next_step'))
    out['website']=source_url(raw.get('website'));out['linkedin_url']=source_url(raw.get('linkedin_url'))
    nested={
      'country_and_base':('value','source_ids','observed_at','status','caveat'),
      'headcount':('value','source_ids','observed_at','status','lower_bound','upper_bound','caveat'),
      'business':('value','source_ids','observed_at','status','saas_contract_model','caveat'),
      'funding':('value','source_ids','observed_at','status','amount','announcement_date','latest_round_exhaustively_verified','caveat'),
      'linkedin_presence':('status','source_ids','visible_activity_card_count','scope'),
      'content_opportunity':('status','angle','basis_source_ids','unmet_need_verified'),
      'expressed_need':('status','inference_allowed'),
      'buying_interest':('status','inference_allowed')}
    for key,fields in nested.items():out[key]=pick(raw.get(key,{}) or {},fields)
    return out


def index(rows,key,label):
    result={}
    for row in rows:
        ident=row.get(key)
        if not ident or ident in result:raise ValueError('Missing or duplicate '+label+' identity')
        result[ident]=row
    return result


def assert_public(value):
    if isinstance(value,dict):
        for key,item in value.items():
            if key in FORBIDDEN_KEYS or key.startswith('reviewer'):raise ValueError('Forbidden public field: '+key)
            assert_public(item)
    elif isinstance(value,list):
        for item in value:assert_public(item)
    elif isinstance(value,str):
        if PRIVATE_RE.search(value):raise ValueError('Private path or credential-like value in public projection')
        if re.search(r'https?://[^\s"<>]*licdn\.com',value,re.I):raise ValueError('CDN media URL leaked into public projection')
    elif isinstance(value,float) and not math.isfinite(value):raise ValueError('Non-finite public number')


def project(source,source_sha):
    posts=index(source.get('posts',[]),'id','post')
    interpretations=index(source.get('interpretations',[]),'post_id','interpretation')
    performance=index(source.get('performance',[]),'post_id','performance')
    if set(posts)!=set(interpretations) or set(posts)!=set(performance):raise ValueError('Every publication requires exactly one interpretation and performance record')
    snapshots=[]
    for raw in source.get('snapshots',[]):
        if raw.get('post_id') not in posts:raise ValueError('Snapshot references unknown post')
        row=pick(raw,SNAP_FIELDS);row['url']=source_url(raw.get('url'));row['metrics']={k:metric(raw.get('metrics',{}).get(k,{}) or {}) for k in METRICS}
        row['normalization_provenance']=pick(raw.get('normalization_provenance',{}) or {},NORM_FIELDS);snapshots.append(row)
    index(snapshots,'snapshot_id','snapshot')
    reviews={x['asset_id']:x for k in ('visual_reviews','video_reviews') for x in source.get(k,[])}
    transcripts={x['asset_id']:x for x in source.get('transcripts',[])}
    qa={x['asset_id']:x for x in source.get('transcript_qa',[])}
    media=[]
    for raw in source.get('assets',[]):
        if raw.get('post_id') not in posts:raise ValueError('Media references unknown post')
        row=pick(raw,('asset_id','post_id','kind','sha256','bytes','status','cycle'));duration=(raw.get('ffprobe') or {}).get('format',{}).get('duration')
        try:duration=float(duration) if duration is not None else None
        except (ValueError,TypeError):duration=None
        row['duration_seconds']=duration;row['distribution']='original_bytes_retained_locally';row['reuse_rights']='not_established'
        row['analysis']=public_review(reviews.get(raw['asset_id']));row['transcript']=public_transcript(transcripts.get(raw['asset_id']),qa.get(raw['asset_id']));media.append(row)
    index(media,'asset_id','asset')
    rows=[]
    for pid,raw in posts.items():
        row=pick(raw,('id','published_at','captured_at','cycle','attributed_urn'));row['url']=source_url(raw.get('url'));row['source_sha256']=(raw.get('source') or {}).get('sha256');row['author']=pick(raw.get('author',{}),('name','type','followers'));row['author']['url']=source_url(raw.get('author',{}).get('url'))
        row['interpretation']=pick(interpretations[pid],SEM_FIELDS);row['performance']=pick(performance[pid],PERF_FIELDS)
        if 'metric_statuses' in row['performance']:
            statuses=row['performance']['metric_statuses'];row['performance']['metric_statuses']={k:statuses[k] for k in METRICS if k in statuses}
            if any(not isinstance(v,str) for v in row['performance']['metric_statuses'].values()):raise ValueError('Performance metric statuses must be scalar labels')
        row['original_post_distribution']='full_text_retained_locally';rows.append(row)
    authors=[public_author(x) for x in source.get('author_decisions',[])]
    if authors:index(authors,'author_key','author decision')
    prospects=[public_prospect(x) for x in source.get('prospects',[])];index(prospects,'id','prospect')
    summary=source.get('summary',{});counts={'posts':len(rows),'accounts':len({p['author'].get('url') or p['author'].get('name') for p in rows}),'snapshots':len(snapshots),'media':len(media),'author_decisions':len(authors),'prospects':len(prospects),'transcripts':len(transcripts),'flagged_transcripts':sum(x.get('status')=='flagged' for x in qa.values()),'reference_values':dict(Counter(x['interpretation'].get('reference_value') for x in rows)),'performance':dict(Counter(x['performance'].get('performance_status') for x in rows))}
    out={'schema':SCHEMA,'provenance':{'source_dataset_sha256':source_sha,'source_run_id':summary.get('run_id'),'as_of':summary.get('as_of'),'scope':'Field-allowlisted derived research. Original posts, raw captures, media bytes, full transcripts, device paths and private contacts are excluded. Hashes are source identities, not redistributed source bytes.','schedule_active':False,'external_wake_active':False},'counts':counts,'posts':rows,'snapshots':snapshots,'media':media,'author_decisions':authors,'prospects':prospects}
    assert_public(out);return out


def canon(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False)


def csv_cell(value):
    if value is None:return ''
    if isinstance(value,(dict,list)):value=canon(value)
    if isinstance(value,str) and value[:1] in ('=','+','-','@'):return "'"+value
    return str(value)


def csv_write(path,fields,rows):
    with path.open('w',encoding='utf-8',newline='') as f:
        writer=csv.writer(f,lineterminator='\n');writer.writerow(fields)
        writer.writerows([[csv_cell(row.get(k)) for k in fields] for row in rows])


def export(dataset_path,out,template=None):
    source_bytes=Path(dataset_path).read_bytes();source=json.loads(source_bytes,object_pairs_hook=unique_pairs);public=project(source,hashlib.sha256(source_bytes).hexdigest());out=Path(out);out.mkdir(parents=True,exist_ok=True)
    template=Path(template) if template else Path(__file__).resolve().parents[1]/'datasets/current/viewer-template.html'
    content=template.read_text();assert content.count('__PUBLIC_DATASET__')==1,'Viewer template must have exactly one data placeholder'
    with tempfile.TemporaryDirectory(prefix='.public-export-',dir=str(out.parent)) as temp:
        temp=Path(temp);(temp/'dataset.json').write_text(json.dumps(public,indent=2,ensure_ascii=False)+'\n')
        flat=[{'post_id':p['id'],'author':p['author'].get('name'),'url':p['url'],**p['interpretation'],**p['performance']} for p in public['posts']]
        post_fields=('post_id','author','url','primary_topic','editorial_job','intended_reader','reference_value','content_summary','qualification_reason','hook_pattern','claim_caveat','adaptation_pattern','reactions','comments','reposts','metric_captured_at','comparison_n','performance_status','performance_reason','trend_status','trend_reason')
        csv_write(temp/'qualification-table.csv',post_fields,flat)
        snap_rows=[{**s,**{k:s['metrics'][k]['value'] for k in METRICS},**{k+'_status':s['metrics'][k]['status'] for k in METRICS}} for s in public['snapshots']]
        snap_fields=('snapshot_id','post_id','captured_at','capture_kind','source_run','raw_sha256','parser_version','parser_sha256','published_at','date_status','reactions','reactions_status','comments','comments_status','reposts','reposts_status')
        csv_write(temp/'snapshots.csv',snap_fields,snap_rows)
        csv_write(temp/'media.csv',('asset_id','post_id','kind','sha256','bytes','status','duration_seconds','distribution','reuse_rights'),public['media'])
        csv_write(temp/'prospects.csv',('id','name','website','linkedin_url','description','fit_status','gaps'),public['prospects'])
        db=sqlite3.connect(temp/'derived.sqlite');entity_keys={'posts':'id','snapshots':'snapshot_id','media':'asset_id','author_decisions':'author_key','prospects':'id'}
        for entity,key in entity_keys.items():
            db.execute('create table '+entity+' (id text primary key, payload text not null)');db.executemany('insert into '+entity+' values (?,?)',[(x[key],canon(x)) for x in public[entity]])
        db.execute('create table metadata (id text primary key,payload text not null)');db.executemany('insert into metadata values (?,?)',[(k,canon(public[k])) for k in ('schema','provenance','counts')]);db.commit();assert db.execute('pragma integrity_check').fetchone()[0]=='ok'
        for entity,key in entity_keys.items():assert {k:json.loads(v) for k,v in db.execute('select id,payload from '+entity)}=={x[key]:x for x in public[entity]}
        db.close();embedded=json.dumps(public,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026');(temp/'index.html').write_text(content.replace('__PUBLIC_DATASET__',embedded))
        for name,fields,rows in [('qualification-table.csv',post_fields,flat),('snapshots.csv',snap_fields,snap_rows),('media.csv',('asset_id','post_id','kind','sha256','bytes','status','duration_seconds','distribution','reuse_rights'),public['media']),('prospects.csv',('id','name','website','linkedin_url','description','fit_status','gaps'),public['prospects'])]:
            with (temp/name).open(newline='') as f:reader=csv.DictReader(f);assert reader.fieldnames==list(fields);actual=list(reader)
            assert actual==[{k:csv_cell(row.get(k)) for k in fields} for row in rows]
        disk=json.loads((temp/'dataset.json').read_text(),object_pairs_hook=unique_pairs);assert disk==public
        match=re.search(r'<script id="public-dataset" type="application/json">(.*?)</script>',(temp/'index.html').read_text(),re.S);assert match and json.loads(match.group(1),object_pairs_hook=unique_pairs)==public
        generated=sorted(x.name for x in temp.iterdir());report={'status':'PASS','schema':SCHEMA,'source_dataset_sha256':public['provenance']['source_dataset_sha256'],'source_run_id':public['provenance']['source_run_id'],'counts':public['counts'],'checked':['explicit field projection','private-path/credential/CDN exclusion','unique identities and exact semantic/performance coverage','all immutable snapshot IDs','all CSV rows/columns/formula escaping','every SQLite entity ID/full payload','JSON readback','safe embedded JSON payload equality'],'files':{name:hashlib.sha256((temp/name).read_bytes()).hexdigest() for name in generated},'limits':'Derived data only. No original source/media/full transcript redistribution, no actual listening/continuous watching or global ranking claim.'};(temp/'export-verification.json').write_text(json.dumps(report,indent=2)+'\n')
        for path in temp.iterdir():os.replace(path,out/path.name)
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--dataset',required=True,type=Path);parser.add_argument('--out',required=True,type=Path);parser.add_argument('--template',type=Path);a=parser.parse_args();report=export(a.dataset,a.out,a.template);print(json.dumps({'status':report['status'],'counts':report['counts']}))

if __name__=='__main__':main()
