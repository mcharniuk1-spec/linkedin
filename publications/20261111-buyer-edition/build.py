#!/usr/bin/env python3
"""Build editable, typography-led Outspoken buyer publication SVGs."""
import argparse, html, json, math, re, os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
W, H, M = 1080, 1350, 72
PAPER, INK, SECONDARY, WHITE, DIVIDER, MARKER = '#FCFFFC', '#162760', '#676D7A', '#FFFFFF', '#E5E8ED', '#FBD387'
FONTS = [ROOT/'fonts/YoungSerif-Regular.ttf', ROOT/'fonts/mona-sans-latin-wght-normal.woff2']

def esc(x): return html.escape(str(x), quote=True)
def width(s, size):
    return sum(size*(.28 if c in "ilI.,'’ :;!" else .88 if c in 'MW@%' else .58) for c in s)
def wrap(s, size, maxw, limit, label):
    s=str(s).strip()
    if not s: raise ValueError('Missing '+label)
    lines=[]; line=''
    for word in s.split():
        if width(word,size)>maxw: raise ValueError(f'Unbreakable {label}: {word}')
        nxt=(line+' '+word).strip()
        if line and width(nxt,size)>maxw: lines.append(line); line=word
        else: line=nxt
    if line: lines.append(line)
    if len(lines)>limit: raise ValueError(f'{label} needs {len(lines)} lines (max {limit}): {s}')
    return lines
def txt(lines,x,y,size,fill=INK,family='Mona Sans',weight=400,leading=None,anchor='start'):
    lead=leading or size*1.22
    return ''.join(f'<text x="{x}" y="{y+i*lead:.1f}" font-family="{family}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{esc(s)}</text>' for i,s in enumerate(lines))
def line(x1,y1,x2,y2,color=DIVIDER,sw=2): return f'<path d="M{x1} {y1} L{x2} {y2}" fill="none" stroke="{color}" stroke-width="{sw}"/>'
def visual(kind,items,y,idx):
    items=list(map(str,items or [])); n=len(items); out=[]; end=y
    # Each composition uses the copy's objects, with layout chosen by the requested visual type.
    if kind in ('contrast','annotated','two-column') and n>=2:
        gap=44; cw=(W-2*M-gap)/2
        for j,item in enumerate(items[:2]):
            x=M+j*(cw+gap); out.append(txt(wrap(item,34,cw-10,3,'comparison text'),x,y+38,34,INK,'Mona Sans',600,42))
            out.append(line(x,y+178,x+min(cw,width(item,34)),y+178,DIVIDER,5))
            # Meaning comes from the exact example, not a repeated explanatory filler.
        out.append(line(M+cw+gap/2,y+4,M+cw+gap/2,y+154)); end=y+190
    elif kind=='metric' and n>=2:
        cw=(W-2*M)/n
        for j,it in enumerate(items):
            x=M+j*cw; mt=re.match(r'\s*([\d.,]+)\s*(.*)',it)
            number,unit=(mt.group(1),mt.group(2)) if mt else (it,'')
            out.append(txt([number],x,y+82,84,INK,'Young Serif',400,94))
            if unit: out.append(txt(wrap(unit,28,cw-8,2,'metric label'),x,y+120,28,SECONDARY,'Mona Sans',600,34))
            if j: out.append(line(x,y,x,y+140))
        end=y+155
    elif kind=='checklist':
        for j,it in enumerate(items):
            yy=y+j*58; out.append(f'<circle cx="{M+13}" cy="{yy-9}" r="9" fill="none" stroke="{INK}" stroke-width="2"/><path d="M{M+8} {yy-9} l4 4 7-9" fill="none" stroke="{INK}" stroke-width="2"/>')
            out.append(txt(wrap(it,32,W-2*M-44,2,'checklist item'),M+40,yy,32,INK,'Mona Sans',400,39))
        end=y+n*58
    elif kind in ('story','editorial'):
        # Margin rationale beside a clear document-like excerpt.
        out.append(line(M,y,M,y+max(150,n*54),DIVIDER,6))
        for j,it in enumerate(items): out.append(txt(wrap(it,36,W-2*M-38,2,'story item'),M+28,y+34+j*57,36,INK,'Mona Sans',400,44))
        end=y+max(150,n*57)
    elif kind in ('decision','recipe','sequence'):
        for j,it in enumerate(items):
            yy=y+j*66; out.append(txt([f'{j+1:02d}'],M,yy,25,SECONDARY,'Mona Sans',600,30))
            out.append(txt(wrap(it,34,W-2*M-68,2,'decision item'),M+58,yy,34,INK,'Mona Sans',400,42))
            if j<n-1: out.append(line(M+58,yy+18,M+58,yy+50))
        end=y+n*66
    else:
        # Document excerpt / typographic pull quote for other copy types.
        out.append(line(M,y,M,y+145,DIVIDER,6))
        for j,it in enumerate(items[:3]): out.append(txt(wrap(it,39,W-2*M-44,2,'visual item'),M+32,y+43+j*54,39,INK,'Young Serif' if j==0 else 'Mona Sans',400,48))
        end=y+max(145,min(3,n)*54)
    return ''.join(out), end

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--content',type=Path,default=ROOT/'content.json'); ap.add_argument('--review',type=Path,required=True); a=ap.parse_args()
    content=json.loads(a.content.read_text()); assert len(content)==10, 'Expected 10 publications'
    assert all(p.exists() for p in FONTS), 'Required local fonts missing'
    svgdir=ROOT/'assets/source-svg'; svgdir.mkdir(parents=True,exist_ok=True)
    layout=[]; jobs=[]; pdfjobs=[]; gallery=[]
    for pi,post in enumerate(content):
        pages=post['pages']; expected=4 if pi<5 else 1
        if len(pages)!=expected: raise ValueError(f"{post['id']}: expected {expected} pages")
        folder=ROOT/'assets'/post['id']; folder.mkdir(parents=True,exist_ok=True)
        (folder/'caption.txt').write_text(post['caption'].strip()+'\n')
        thumbs=[]
        for qi,p in enumerate(pages):
            num=f'{pi+1:02d}'; page=f'{qi+1:02d}'; title=post['title']
            head=wrap(p['headline'],74,W-2*M,3,'headline'); body=wrap(p['body'],42,W-2*M,4,'body'); emph=wrap(p.get('emphasis',''),30,W-2*M,2,'emphasis')
            hy=190; he=hy+(len(head)-1)*84+58; by=he+76; be=by+(len(body)-1)*54
            ey=be+54; ee=ey+(len(emph)-1)*40+12
            vy=max(ee+72,760)
            art,ve=visual(p.get('visual_type',''),p.get('visual_items',[]),vy,qi)
            end=max(ve,ee)
            if end>1198: raise ValueError(f"{post['id']} page {qi+1}: content ends at {end}, footer begins 1250")
            # One short hypothetical sentence is retained as reader-facing copy where needed.
            label='OutSpoken'
            svg=(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><title>{esc(title)} — page {qi+1}</title><desc>{esc(p["headline"]+". "+p["body"]+". "+"; ".join(p.get("visual_items",[])))}</desc>'
                 f'<style>@font-face{{font-family:Young Serif;src:url(../../fonts/YoungSerif-Regular.ttf)}}@font-face{{font-family:"Mona Sans";src:url({esc(os.path.relpath(FONTS[1],svgdir))});font-weight:100 900}}*{{shape-rendering:geometricPrecision}}</style><rect width="1080" height="1350" fill="{PAPER}"/>')
            svg+=txt(head,M,hy,74,INK,'Young Serif',400,84)+txt(body,M,by,42,INK,'Mona Sans',400,54)
            svg+=txt(emph,M,ey,30,INK,'Mona Sans',600,40)+line(M,ey+13,M+min(W-2*M,width(emph[0],30)),ey+13,MARKER,5)
            svg+=art+(txt(['Book an intro call'],M,1150,42,INK,'Mona Sans',600,52) if pi==9 else '')+line(M,1250,W-M,1250)+txt([label],M,1300,26,INK,'Young Serif',400,32)
            svg+='</svg>'
            svgname=f'{num}-page-{page}.svg'; (svgdir/svgname).write_text(svg)
            png=f'assets/{post["id"]}/editorial-{page}.png'
            jobs.append({'id':post['id'],'variant':'editorial','page':qi+1,'svg':f'assets/source-svg/{svgname}','png':png})
            layout.append({'id':post['id'],'page':qi+1,'headline_lines':len(head),'body_lines':len(body),'emphasis_lines':len(emph),'visual_type':p.get('visual_type'),'content_top':hy,'content_end':end,'footer_y':1250,'overflow':False})
            thumbs.append(f'<figure><a href="{post["id"]}/editorial-{page}.png"><img src="{post["id"]}/editorial-{page}.png" alt="{esc(p["headline"]+". "+p["body"])}" loading="lazy"></a><figcaption>{qi+1}. {esc(p["headline"])}<br>{esc(p["body"])}</figcaption><a href="{post["id"]}/editorial-{page}.png">PNG</a> · <a href="source-svg/{svgname}">Editable SVG</a></figure>')
        if expected==4: pdfjobs.append({'id':post['id'],'variant':'editorial','images':[j['png'] for j in jobs[-4:]],'pdf':f'assets/{post["id"]}/carousel.pdf'})
        gallery.append(f'<article><h2>{esc(post["title"])}</h2><div class="slides">{"".join(thumbs)}</div><details><summary>Full caption / transcript</summary><div class="caption">{esc(post["caption"].strip())}</div></details></article>')
    if len(jobs)!=25 or len(pdfjobs)!=5: raise ValueError('Incorrect export job count')
    a.review.mkdir(parents=True,exist_ok=True)
    (a.review/'renderjobs.json').write_text(json.dumps(jobs,indent=2)+'\n')
    (a.review/'pdfjobs.json').write_text(json.dumps(pdfjobs,indent=2)+'\n')
    (a.review/'layout.json').write_text(json.dumps({'status':'PASS','basis':'Conservative text-width estimate; render inspection still required','canvas':[W,H],'panels':layout},indent=2)+'\n')
    (ROOT/'assets/index.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Outspoken buyer publications</title><style>@font-face{font-family:"Mona Sans";src:url('+esc(os.path.relpath(FONTS[1],ROOT/'assets'))+')}body{margin:0;background:#FCFFFC;color:#162760;font:18px/1.5 "Mona Sans",Arial,sans-serif}main{max-width:1200px;margin:auto;padding:28px}h1,h2{font-family:Georgia,serif}article{border-top:1px solid #E5E8ED;padding:24px 0}figure{margin:0;flex:0 0 min(360px,85vw)}img{width:100%;height:auto;border:1px solid #E5E8ED}.slides{display:flex;gap:18px;overflow:auto}.caption{white-space:pre-wrap;max-width:850px}a{color:#162760}</style><main><h1>Outspoken · Buyer publications</h1>'+''.join(gallery)+'</main></html>')
    print(json.dumps({'publications':len(content),'panels':len(jobs),'pdfs':len(pdfjobs),'review':str(a.review)}))
if __name__=='__main__': main()
