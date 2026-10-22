"""Local cached-model ASR worker; no model downloads or external provider calls."""
from pathlib import Path
from runtime_config import load_config, tool_command
import argparse,json,hashlib,time
def read(p):return json.loads(Path(p).read_text())
def sha_file(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--config',type=Path,required=True);a=ap.parse_args();cfg=load_config(a.config);r=Path(cfg['run_root']);m=read(r/'data/media-manifest.json');posts={x['id']:x for f in [r/'data/new-posts.ndjson',r/'data/media-source-posts.ndjson'] if f.exists() for x in map(json.loads,(line for line in f.read_text().splitlines() if line.strip()))};out=r/'transcripts';out.mkdir(exist_ok=True)
    caps={x['asset_id'].removesuffix(':captions'):x for x in m if x['kind']=='captions' and x['status']=='acquired'};videos=[x for x in m if x['kind']=='video' and x['status']=='acquired'];records=[];model=None;modelsha=None
    (out/'index.json').write_text('[]\n')
    for v in videos:
        dest=out/(v['post_id'].split(':')[-1]+'-'+hashlib.sha256(v['asset_id'].encode()).hexdigest()[:8]+'.json');legacy=out/(v['post_id'].split(':')[-1]+'.json');old=read(dest) if dest.exists() else read(legacy) if legacy.exists() else None
        streams=v.get('ffprobe',{}).get('streams',[]);probe_ok=isinstance(streams,list) and any(s.get('codec_type')=='video' for s in streams);has_audio=probe_ok and any(s.get('codec_type')=='audio' for s in streams)
        origin='platform_captions' if v['asset_id'] in caps else 'public_page_transcript' if posts[v['post_id']]['transcript']['text'] and sum(x['post_id']==v['post_id'] for x in videos)==1 else 'local_whisper_ASR' if has_audio else 'no_audio_stream_in_acquired_file' if probe_ok else 'audio_probe_unavailable'
        if origin=='local_whisper_ASR' and modelsha is None:
            mp=Path(cfg['whisper']['model']);assert mp.is_file(),'Cached Whisper model missing; no download permitted';modelsha=sha_file(mp)
        signature={'origin':origin,'language':cfg['whisper']['language'] if origin=='local_whisper_ASR' else None,'model_sha256':modelsha if origin=='local_whisper_ASR' else None,'caption_sha256':caps[v['asset_id']]['sha256'] if origin=='platform_captions' else None,'page_transcript_sha256':hashlib.sha256(posts[v['post_id']]['transcript']['text'].encode()).hexdigest() if origin=='public_page_transcript' else None}
        if old and old.get('asset_id')==v['asset_id'] and old.get('source_video_sha256')==v['sha256'] and old.get('transcription_signature')==signature:d=old
        elif origin=='platform_captions':
            c=caps[v['asset_id']];raw=(r/c['path']).read_text(errors='replace');text='\n'.join(l for l in raw.splitlines() if l.strip() and not l.strip().isdigit() and '-->' not in l and l.strip()!='WEBVTT');d={'post_id':v['post_id'],'asset_id':v['asset_id'],'origin':'platform_captions','text':text,'original_path':c['path'],'timing_verified':False,'source_video_sha256':v['sha256'],'audio_verified':False}
        elif origin=='public_page_transcript':
            d={'post_id':v['post_id'],'asset_id':v['asset_id'],'origin':'public_page_transcript','text':posts[v['post_id']]['transcript']['text'],'source_video_sha256':v['sha256'],'audio_verified':False,'timing_verified':False}
        elif origin=='local_whisper_ASR':
            mp=Path(cfg['whisper']['model']);assert mp.is_file(),'Cached Whisper model missing; no download permitted'
            if model is None:
                import torch,whisper
                torch.set_num_threads(cfg['whisper']['threads']);model=whisper.load_model(str(mp),device='cpu')
            start=time.time();x=model.transcribe(str(r/v['path']),language=cfg['whisper']['language'],fp16=False,verbose=False)
            d={'post_id':v['post_id'],'asset_id':v['asset_id'],'origin':'local_whisper_ASR','text':x['text'],'segments':x['segments'],'language':x['language'],'model':mp.name,'model_sha256':modelsha,'elapsed_seconds':round(time.time()-start,2),'source_video_sha256':v['sha256'],'audio_verified':False,'timing_verified':False,'external_provider':False}
        else:d={'post_id':v['post_id'],'asset_id':v['asset_id'],'origin':origin,'text':'','source_video_sha256':v['sha256'],'audio_verified':False,'timing_verified':False,'gap':'Acquired video has no audio stream; speech transcription not applicable to this file. On-screen text belongs in visual review.' if origin=='no_audio_stream_in_acquired_file' else 'Audio/video probe unavailable; do not infer silence. Repair ffprobe before completing this item.'}
        d['transcription_signature']=signature;d['full_watch']=False;d['review_status']='not_applicable_no_audio' if origin=='no_audio_stream_in_acquired_file' else 'blocked_audio_probe' if origin=='audio_probe_unavailable' else 'transcript_available_not_audio_verified';dest.write_text(json.dumps(d,indent=2)+'\n');records.append({'post_id':d['post_id'],'asset_id':d['asset_id'],'path':str(dest.relative_to(r)),'origin':d['origin'],'chars':len(d['text']),'source_video_sha256':v['sha256']});(out/'index.json').write_text(json.dumps(records,indent=2)+'\n');print(json.dumps(records[-1]),flush=True)
    complete=len(records)==len(videos) and all(x['origin']!='audio_probe_unavailable' for x in records);print(json.dumps({'transcript_records':len(records),'videos':len(videos),'complete':complete}),flush=True)
    if not complete:raise SystemExit(2)
if __name__=='__main__':main()
