"""Prepare timestamped video frames for a supervisor. This does not review video."""
from pathlib import Path
from runtime_config import load_config, tool_command
from PIL import Image,ImageDraw
import argparse,json,hashlib,subprocess,math,re
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--config',type=Path,required=True);a=ap.parse_args();c=load_config(a.config);r=Path(c['run_root']);m=json.loads((r/'data/media-manifest.json').read_text());out=[]
    for v in m:
        if v['kind']!='video' or v['status']!='acquired':continue
        pid=v['post_id'].split(':')[-1];signature=hashlib.sha256(json.dumps({'asset_id':v['asset_id'],'source':v['sha256'],'max_frames':c['analysis']['max_video_frames'],'width':c['analysis']['frame_width'],'per_sheet':c['analysis']['max_frames_per_sheet'],'version':2},sort_keys=True).encode()).hexdigest()[:16];d=r/'analysis/evidence'/(pid+'-'+signature);d.mkdir(parents=True,exist_ok=True);src=r/v['path'];assert sha(src)==v['sha256'];receipt=d/'evidence.json'
        if receipt.exists():
            old=json.loads(receipt.read_text())
            if old['source_sha256']==v['sha256'] and all(sha(r/s['path'])==s['sha256'] for s in old['sheets']):out.append(old);continue
        duration=float(v['ffprobe']['format']['duration']);step=max(2,duration/max(1,c['analysis']['max_video_frames']-1));width=c['analysis']['frame_width']
        filt=f"select='isnan(prev_selected_t)+gte(t-prev_selected_t,{step})',scale={width}:-2,showinfo"
        p=subprocess.run([tool_command(c,'ffmpeg'),'-hide_banner','-loglevel','info','-threads','2','-i',str(src),'-an','-vf',filt,'-fps_mode','vfr','-q:v','3','-y',str(d/'frame-%03d.jpg')],capture_output=True,text=True,timeout=240);(d/'ffmpeg.log').write_text(p.stderr);assert p.returncode==0
        times=[float(x) for x in re.findall(r'Parsed_showinfo[^\n]*pts_time:([0-9.]+)',p.stderr)];frames=sorted(d.glob('frame-*.jpg'));assert len(times)==len(frames)
        end=max(0,duration-.15);p=subprocess.run([tool_command(c,'ffmpeg'),'-v','error','-ss',str(end),'-i',str(src),'-frames:v','1','-vf',f'scale={width}:-2','-y',str(d/'end.jpg')],capture_output=True,timeout=60)
        if (d/'end.jpg').exists():frames.append(d/'end.jpg');times.append(end)
        sheets=[];per=c['analysis']['max_frames_per_sheet'];cols=3
        for offset in range(0,len(frames),per):
            fs=frames[offset:offset+per];ts=times[offset:offset+per];imgs=[Image.open(f).convert('RGB') for f in fs];height=max(x.height for x in imgs)+28;sheet=Image.new('RGB',(cols*width,math.ceil(len(imgs)/cols)*height+35),'#eee');draw=ImageDraw.Draw(sheet);draw.text((8,8),f'{pid} | duration {duration:.2f}s | sampled step {step:.2f}s | NOT continuous watch',fill='black')
            for i,(im,t) in enumerate(zip(imgs,ts)):
                x=i%cols*width;y=35+i//cols*height;sheet.paste(im,(x,y));draw.text((x+4,y+im.height+3),f'{t:.3f}s'+(' requested endpoint' if fs[i].name=='end.jpg' else ' decoded PTS'),fill='black')
            dest=d/f'sheet-{offset//per+1}.jpg';sheet.save(dest,quality=90);sheets.append({'path':str(dest.relative_to(r)),'sha256':sha(dest),'timestamps':ts,'reviewed':False})
        x={'post_id':v['post_id'],'asset_id':v['asset_id'],'source_path':v['path'],'source_sha256':v['sha256'],'duration_seconds':duration,'sample_interval_seconds':step,'sampled_frames':len(frames),'timestamps':times,'sheets':sheets,'visual_review_status':'pending','full_watch':False,'audio_review':False,'between_frame_events':'not_verified'};receipt.write_text(json.dumps(x,indent=2)+'\n');out.append(x)
    (r/'analysis/evidence-index.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'videos':len(out),'frames':sum(v['sampled_frames'] for v in out),'sheets':sum(len(v['sheets']) for v in out)}))
if __name__=='__main__':main()
