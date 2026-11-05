#!/usr/bin/env python3
"""Render original Outspoken carousel drafts from structured copy and licensed brand assets."""
import json,hashlib,math,textwrap,zipfile
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont

HERE=Path(__file__).resolve().parent
if (HERE/'content.json').is_file() and (HERE/'../repository').resolve().is_dir():
 RUN=HERE.parent; REPO=RUN/'repository'; CONTENT=HERE/'content.json'; OUT=HERE/'output'; REVIEW=RUN/'verification'; ZIP=HERE/'outspoken-10-carousels.zip'
else:
 REPO=HERE.parents[1]; CONTENT=HERE/'content.json'; OUT=HERE/'generated'; REVIEW=HERE/'generated-review'; ZIP=HERE/'generated-carousels.zip'
ID=REPO/'design and website/assets/public/assets/identity/v13/lockup-os-3x.png'
FONTS=REPO/'design and website/assets/offer-deck-r15/fonts'
FONT={'display':FONTS/'fraunces-latin-full-normal.woff2','body':FONTS/'mona-sans-latin-wght-normal.woff2','mono':FONTS/'geist-mono-latin-wght-normal.woff2'}
W,H=1080,1350
NAVY='#162760'; DEEP='#0D1A3B'; PAPER='#F6F7F9'; WHITE='#FFFFFF'; INK='#202F58'; NICKEL='#666F7F'; ORANGE='#EAA93C'; PALE='#F6D591'; COBALT='#3157D5'

def f(role,size):
 font=ImageFont.truetype(str(FONT[role]),size)
 # Pillow otherwise chooses the fonts' unusual variation defaults (900/200).
 # Use the project's actual 400 display/body and 500 label weights.
 font.set_variation_by_axes({'display':[min(144,max(9,size)),400,0,1],
                             'body':[400],'mono':[500]}[role])
 return font
def width(draw,txt,font):return draw.textbbox((0,0),txt,font=font)[2]
def lines(draw,txt,font,maxwidth):
 out=[];current=''
 for word in txt.split():
  trial=(current+' '+word).strip()
  if width(draw,trial,font)>maxwidth and current:out.append(current);current=word
  else:current=trial
 if current:out.append(current)
 return out

def block(draw,txt,x,y,maxwidth,role,size,color,maxlines,leading=1.12):
 while size>=28:
  font=f(role,size);ls=lines(draw,txt,font,maxwidth)
  if len(ls)<=maxlines and all(width(draw,line,font)<=maxwidth for line in ls):break
  size-=2
 else:raise ValueError('Cannot fit: '+txt)
 step=round(size*leading)
 for i,line in enumerate(ls):draw.text((x,y+i*step),line,font=font,fill=color,stroke_width=0)
 bbox=(x,y,x+max(width(draw,line,font) for line in ls),y+step*len(ls))
 assert bbox[2]<=W-65 and bbox[3]<H-95,(txt,bbox)
 return bbox

def rounded(draw,box,r,fill,outline=None,w=2):draw.rounded_rectangle(box,radius=r,fill=fill,outline=outline,width=w)
def base(dark,number):
 im=Image.new('RGB',(W,H),DEEP if dark else PAPER);d=ImageDraw.Draw(im)
 # restrained tonal planes, plus the dotted texture from the existing system
 for y in range(0,H,48):
  for x in range(0,W,48):d.ellipse((x+22,y+22,x+25,y+25),fill=('#22345E' if dark else '#D8DDE5'))
 if dark:
  d.polygon([(775,0),(1080,0),(1080,360)],fill='#142759')
  rounded(d,(62,55,450,131),20,WHITE)
 logo=Image.open(ID).convert('RGBA');logo.thumbnail((348,58),Image.Resampling.LANCZOS)
 im.paste(logo,(80,67),logo)
 d=ImageDraw.Draw(im)
 rounded(d,(877,64,1005,118),27,'#243660' if dark else WHITE, '#4A5B7C' if dark else '#CFD6E0')
 d.text((900,73),f'{number:02d} / 05',font=f('mono',22),fill=WHITE if dark else NAVY)
 return im,d

def draw_slide(deck,i):
 dark=i in (0,4);im,d=base(dark,i+1);fg=WHITE if dark else NAVY;secondary='#D8DFEA' if dark else INK
 if i==0:
  d.text((72,220),deck['series'],font=f('mono',24),fill=PALE)
  titlebox=block(d,deck['title'],72,300,912,'display',94,fg,4,1.08)
  # A distinct motif for each cover, designed from primitive geometry.
  y=max(760,titlebox[3]+75); offset=int(deck['id'][:2]);
  rounded(d,(72,y,1008,y+205),30,'#1C315C','#45577C')
  labels=['QUESTION','DECISION','EVIDENCE'] if offset%3==1 else (['CONTEXT','THINKING','LESSON'] if offset%3==2 else ['SIGNAL','CLARITY','ACTION'])
  for n,label in enumerate(labels):
   x=103+n*295
   d.ellipse((x,y+38,x+55,y+93),fill=ORANGE if n==offset%3 else '#D8DFEA')
   d.text((x,y+120),label,font=f('mono',20),fill=WHITE)
   if n<2:d.line((x+70,y+65,x+270,y+65),fill='#61708F',width=3)
  d.text((72,1240),'A PRACTICAL OUTSPOKEN CAROUSEL',font=f('mono',20),fill='#B7C2D5')
 else:
  k,title,body=deck['slides'][i-1]
  d.text((72,195),k,font=f('mono',25),fill=PALE if dark else '#824F19')
  titlebox=block(d,title,72,255,910,'display',80,fg,4,1.08)
  body_y=max(625,titlebox[3]+58)
  bodybox=block(d,body,72,body_y,905,'body',42,secondary,5,1.30)
  panel_y=max(945,bodybox[3]+40)
  if panel_y>1085:raise ValueError('Text extends into footer: '+deck['id'])
  rounded(d,(72,panel_y,1008,panel_y+120),24,'#253A63' if dark else WHITE,'#4E5F7C' if dark else '#D5DBE4')
  # Content-first graphic: index and a proportional decision pathway.
  rounded(d,(96,panel_y+25,166,panel_y+95),17,ORANGE)
  d.text((115,panel_y+37),f'{i:02d}',font=f('mono',25),fill=NAVY)
  themes=[('BUYER','CHOICE','LESSON'),('CUSTOMER','OPTION','PROOF'),('TASK','REVIEW','LIMIT'),('INPUT','CHECK','ACTION'),('ASK','LISTEN','EDIT'),('JOB','COMPARE','DECIDE'),('FOUNDER','COMPANY','BUYER'),('QUESTION','PROOF','REVIEW'),('REACTION','COMMENT','MISSING'),('OBSERVE','LEARN','IMPROVE')]
  labels=themes[int(deck['id'][:2])-1]
  for n,label in enumerate(labels):
   x=205+n*245; active=n==(i-1)%3
   rounded(d,(x,panel_y+31,x+215,panel_y+88),15,('#F6D591' if active else ('#3A4F77' if dark else '#E9EDF3')))
   label_font=f('mono',17);label_width=width(d,label,label_font)
   d.text((x+(215-label_width)//2,panel_y+47),label,font=label_font,fill=NAVY if active or not dark else WHITE)
  footer='Book an intro call' if i==4 else 'OUTSPOKEN  /  FOUNDER-LED CONTENT'
  d.text((72,1240),footer,font=f('mono',20),fill='#C9D2E2' if dark else NICKEL)
 return im

def main():
 decks=json.loads(CONTENT.read_text());assert len(decks)==10 and len({d['id'] for d in decks})==10
 OUT.mkdir(parents=True,exist_ok=True);REVIEW.mkdir(parents=True,exist_ok=True);manifest=[];covers=[];sheets=[]
 for deck in decks:
  assert len(deck['slides'])==4
  dest=OUT/deck['id'];dest.mkdir(parents=True,exist_ok=True);pages=[];imgs=[]
  for i in range(5):
   im=draw_slide(deck,i);path=dest/f'slide-{i+1:02d}.png';im.save(path,optimize=True)
   imgs.append(im);pages.append({'path':str(path.relative_to(OUT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'alt':('Cover: '+deck['title']) if i==0 else (deck['slides'][i-1][1]+' '+deck['slides'][i-1][2])})
  # PDF pages are built from the exact reviewed PNG pixels, in order.
  pdf=dest/'carousel.pdf';imgs[0].save(pdf,save_all=True,append_images=imgs[1:],resolution=96,quality=90)
  (dest/'caption.txt').write_text(deck['caption']+'\n',encoding='utf8')
  covers.append(imgs[0].copy());sheet=Image.new('RGB',(1080,1350),'white')
  for i,im in enumerate(imgs):
   thumbnail=im.copy();thumbnail.thumbnail((205,256));sheet.paste(thumbnail,(i*215,350))
  sheets.append(sheet)
  manifest.append({'id':deck['id'],'title':deck['title'],'series':deck['series'],'slide_count':5,'slides':pages,'caption':str((dest/'caption.txt').relative_to(OUT)),'pdf':str(pdf.relative_to(OUT)),'pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),'status':'proposed; founder review required','rights':'Original graphic layouts with owner-selected Outspoken lockup and project-licensed fonts.'})
  print(deck['id'],'5 slides + PDF',flush=True)
 sheet=Image.new('RGB',(1080,620),'#E8EBF1')
 for i,im in enumerate(covers):
  im.thumbnail((195,245));sheet.paste(im,(45+(i%5)*205,45+(i//5)*280))
 sheet.save(REVIEW/'contact-sheet.png',optimize=True)
 for deck in manifest:
  row=Image.new('RGB',(1080,270),'#E8EBF1')
  for i,entry in enumerate(deck['slides']):
   im=Image.open(OUT/entry['path']);im.thumbnail((200,250));row.paste(im,(10+i*214,10))
  row.save(REVIEW/(deck['id']+'-contact.png'),optimize=True)
 (OUT/'manifest.json').write_text(json.dumps({'schema':'outspoken-carousels/1','status':'draft_for_owner_review','post_count':10,'slide_count':50,'decks':manifest},ensure_ascii=False,indent=2)+'\n')
 from html import escape
 cards=''.join(f'<article><a href="{m["slides"][0]["path"]}"><img src="{m["slides"][0]["path"]}" alt="{escape(m["title"])}"></a><h2>{escape(m["title"])}</h2><p><a href="{m["pdf"]}">Carousel PDF</a> · <a href="{m["caption"]}">Caption</a> · '+ ' '.join(f'<a href="{v["path"]}">{i+1:02d}</a>' for i,v in enumerate(m['slides']))+'</p></article>' for m in manifest)
 (OUT/'index.html').write_text('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Outspoken — 10 carousel drafts</title><style>body{font:16px/1.55 system-ui;color:#162760;background:#f1f3f6;margin:0;padding:32px}main{max-width:1240px;margin:auto}h1{font-size:clamp(32px,5vw,56px)}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(235px,1fr));gap:22px}article{background:white;border-radius:18px;padding:14px}img{width:100%;border-radius:10px}a{color:#284ca8}h2{font-size:20px}</style><main><h1>Ten founder-led carousels</h1><p>Drafts for owner review. Each includes five images, a document PDF and a caption.</p><div class="grid">'+cards+'</div></main>')
 z=ZIP
 with zipfile.ZipFile(z,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
  for p in sorted(OUT.rglob('*')):
   if p.is_file():archive.write(p,p.relative_to(OUT))
 print('DONE',len(decks),'posts',sum(x['slide_count'] for x in manifest),'slides')
if __name__=='__main__':main()
