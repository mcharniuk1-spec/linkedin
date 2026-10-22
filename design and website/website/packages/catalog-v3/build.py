from pathlib import Path
import json,html,textwrap,hashlib,shutil
D=Path(__file__).parent;N='#162760';C='#D4DD67';S='#A9AFBA';P='#FBFBF7';B='#3157C8';INK='#101218'
contexts=[('buyer-question','Make the buyer’s question visible.','Start with the task. Name the decision.','Buyer context'),('experience','Your experience has a point.','Find the useful lesson behind the work.','Founder story'),('position','Give the product a clear position.','Say who it helps and what changes.','Positioning'),('sequence','One idea. A useful sequence.','Give each part a reason to exist.','Editorial sequence'),('decision','The decision deserves context.','Explain the options and the consequence.','Product judgment'),('voice','Write in the founder’s voice.','Keep the meaning. Make it easier to read.','Professional writing'),('change','Explain what changed.','Connect the announcement to a buyer task.','Company story'),('evidence','Let the evidence set the limit.','Separate what was observed from what it means.','Evidence note'),('next-step','Keep the next step clear.','Make the invitation relevant and considered.','Conversation'),('questions','Make room for real questions.','Use the next interview to find the substance.','Regular interviews'),('approval','Review before you publish.','Check the meaning,voice and factual detail.','Approval workflow')]
layoutnames=['split-field','center-sign','margin-rail','numbered-editorial','horizon-band','photo-column','ribbon-sign','quote-field','open-ledger','stepped-argument','diagonal-marker']
config={'banner':(1584,396),'poster':(1080,1350),'block':(1200,660),'heading':(1200,360),'video-frame':(1600,900),'caption-emphasis':(1200,360),'schema':(1200,900)}
photos=['01-tidal-signal','03-still-to-signal','02-resonance-field']
def e(s):return html.escape(str(s),quote=True)
def rect(x,y,w,h,f=P,rx=0,stroke=None):return f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{rx:g}" fill="{f}"'+(f' stroke="{stroke}" stroke-width="2"' if stroke else '')+'/>'
def txt(x,y,s,size=34,weight=400,fill=N,slot=None,anchor=None):return f'<text x="{x:g}" y="{y:g}" font-family="'+('Archivo' if weight>=600 else 'Inter')+f'" font-size="{size:g}" font-weight="{weight}" fill="{fill}"'+(f' data-slot="{slot}"' if slot else '')+(f' text-anchor="{anchor}"' if anchor else '')+f'>{e(s)}</text>'
def path(d,stroke=B,width=3,extra=''):return f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{width}" {extra}/>'
def image(x,y,w,h,i=0):return f'<image data-slot="media" href="../../../assets/revisions/v3/nature/{photos[i%3]}.webp" x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" preserveAspectRatio="xMidYMid slice"/>'
def wrap(s,width,size):return textwrap.wrap(s,width=max(9,int(width/(size*.57))),break_long_words=False,break_on_hyphens=False)
def textblock(x,y,width,title,body,size,bodySize,colour=N,maxlines=4,emph=False):
 out='';ls=wrap(title,width,size)
 for i,t in enumerate(ls):
  if emph and i==len(ls)-1:out+=rect(x-3,y+i*size*1.1-size*.83,min(width,len(t)*size*.56+18),size*.97,C)
  out+=txt(x,y+i*size*1.1,t,size,700,colour,'title-'+str(i))
 yy=y+len(ls)*size*1.1+bodySize*.6
 for i,t in enumerate(wrap(body,width,bodySize)):out+=txt(x,yy+i*bodySize*1.45,t,bodySize,400,colour,'body-'+str(i))
 return out,yy

def footer(w,h,mini=False):
 fs=17 if h<=400 else 23;m=38 if h<=400 else 54;y=h-27
 return path(f'M{m} {h-62}H{w-m}',S,1)+txt(m,y,'Out',fs+6,700,N)+txt(m+(fs+6)*1.78,y,'spoken',fs+6,700,S)+txt(w-m,y,'Illustrative design specimen',fs,400,N,anchor='end')
def defs():return '''<defs><linearGradient id="shade" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#0B1830" stop-opacity=".72"/><stop offset="1" stop-color="#162760" stop-opacity=".12"/></linearGradient><marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M0 0L10 5L0 10" fill="none" stroke="#3157C8" stroke-width="1.5"/></marker></defs><style>@font-face{font-family:Archivo;src:url('../../../assets/identity/font-source/archivo/Archivo[wdth,wght].ttf')}@font-face{font-family:Inter;src:url('../../../assets/identity/font-source/inter/Inter[opsz,wght].ttf')}</style>'''

def editorial(cat,i,w,h,title,body,tag):
 m=42 if h<500 else 64;safeH=h-90;compact=h<=400;fs=(43 if cat=='heading' else 51) if compact else (70 if cat=='poster' else 62);bs=(21 if cat=='heading' else 23) if compact else 31;out='';kind=i%11
 # Eleven visibly different systems,including image,sign,type,rail,step and openledger arrangements.
 if kind==0:
  out+=image(w*.67,0,w*.33,safeH,i)+txt(m,m+14,tag.upper(),bs*.8,600,slot='eyebrow');b,_=textblock(m,m+fs+35,w*.55,title,body,fs,bs,emph=True);out+=b
 elif kind==1:
  out+=rect(w*.43,20,w*.14,10,C)+txt(w/2,62,tag.upper(),bs*.8,600,slot='eyebrow',anchor='middle');ls=wrap(title,w*.78,fs)
  for j,t in enumerate(ls):out+=txt(w/2,(80+fs*1.1)+j*fs*1.1,t,fs,700,N,'title-'+str(j),'middle')
  yy=(80+fs*1.1)+len(ls)*fs*1.1+bs
  for j,t in enumerate(wrap(body,w*.78,bs)):out+=txt(w/2,yy+j*bs*1.4,t,bs,400,N,'body-'+str(j),'middle')
 elif kind==2:
  out+=rect(0,0,w*.21,safeH,N)+txt(24,94,'03',52 if compact else 82,700,'#FFFFFF')+path(f'M{w*.21+28} 30V{safeH-15}',S,2)+txt(w*.25,61,tag.upper(),bs*.8,600,slot='eyebrow');b,_=textblock(w*.25,126,w*.66,title,body,fs,bs);out+=b
 elif kind==3:
  out+=txt(m,158,'04',84 if compact else 146,700,S)+txt(w*.26,58,tag.upper(),bs*.8,600,slot='eyebrow');b,_=textblock(w*.26,125,w*.67,title,body,fs,bs,emph=True);out+=b
 elif kind==4:
  ph=90 if compact else safeH*.31;out+=image(0,0,w,ph,i)+rect(0,0,w,ph,'url(#shade)')+txt(m,ph*.64,tag.upper(),bs*.85,600,'#FFFFFF',slot='eyebrow');b,_=textblock(m,ph+fs+18,w-2*m,title,body,fs*.9,bs);out+=b
 elif kind==5:
  out+=image(0,0,w*.31,safeH,i)+txt(w*.36,59,tag.upper(),bs*.8,600,slot='eyebrow');b,_=textblock(w*.36,126,w*.58,title,body,fs*.94,bs);out+=b
 elif kind==6:
  out+=rect(0,0,w,45,N)+txt(m,32,tag.upper(),23,600,'#FFFFFF',slot='eyebrow')+path(f'M{m} 78H{w-m-26}L{w-m-44} 61M{w-m-26} 78L{w-m-44} 95',B,3);b,_=textblock(m,150,w-2*m,title,body,fs*.95,bs,emph=True);out+=b
 elif kind==7:
  out+=txt(m,112,'“',112,700,S)+txt(m+85,55,tag.upper(),bs*.8,600,slot='eyebrow');b,_=textblock(m+85,128,w-m*2-85,title,body,fs*.95,bs);out+=b
 elif kind==8:
  out+=txt(m,58,tag.upper(),bs*.8,600,slot='eyebrow')+path(f'M{m} 78H{w-m}',S,2);b,_=textblock(m,145,w*.55,title,body,fs*.95,bs);out+=b+path(f'M{w*.66} 103V{safeH-15}',S,2)+txt(w*.70,145,'ASK',bs,600)+txt(w*.70,195,'EXPLAIN',bs,600)+txt(w*.70,245,'REVIEW',bs,600)
 elif kind==9:
  out+=txt(m,56,tag.upper(),bs*.8,600,slot='eyebrow');ls=wrap(title,w*.72,fs*.9)
  for j,t in enumerate(ls):out+=rect(m+j*18,95+j*fs*.97,min(w-m*2,len(t)*fs*.51+32),fs*.99,C if j==len(ls)-1 else '#EEF0E8')+txt(m+12+j*18,95+j*fs*.97+fs*.77,t,fs*.9,700,N,'title-'+str(j))
  yy=95+len(ls)*fs*.97+bs
  for j,t in enumerate(wrap(body,w*.8,bs)):out+=txt(m,yy+j*bs*1.35,t,bs,400,N,'body-'+str(j))
 else:
  out+=path(f'M{w*.79} 20L{w-20} {safeH*.55}M{w*.84} 20L{w-20} {safeH*.39}',B,4)+rect(m,30,220,38,C)+txt(m+12,58,tag.upper(),21,600,slot='eyebrow');b,_=textblock(m,142,w*.73,title,body,fs*.96,bs);out+=b
 return out

def namedimage(x,y,w,h,source,opacity=1):return f'<image data-slot="media" href="../../../assets/{source}" x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" preserveAspectRatio="xMidYMid slice" opacity="{opacity}"/>'
def wave(y,w=1080,colour=B):return path(f'M-90 {y}C160 {y-190} 430 {y+190} {w+90} {y-70}',colour,5)+path(f'M-90 {y+44}C160 {y-146} 430 {y+234} {w+90} {y-26}',S,2)
def poster(i,w,h,title,body,tag):
 m=64;out='';fs=108;bs=38
 if i==0:
  out+=namedimage(555,300,525,928,'revisions/v3/nature/05-real-human-shadow.webp')+txt(m,105,tag.upper(),28,600,slot='eyebrow');out+=textblock(m,290,480,title,body,106,36,emph=True)[0]+wave(1080,560)
 elif i==1:
  out+=txt(w/2,110,tag.upper(),28,600,slot='eyebrow',anchor='middle')+rect(410,150,260,16,C)
  ls=wrap(title,920,110)
  for j,t in enumerate(ls):out+=txt(w/2,350+j*121,t,110,700,N,'title-'+str(j),'middle')
  out+=txt(w/2,750,body,34,400,N,'body-0','middle')+image(0,850,w,378,0)
 elif i==2:
  out+=rect(0,0,1080,1228,N)+image(845,0,235,1228,2)+txt(m,105,tag.upper(),28,600,'#FFFFFF',slot='eyebrow')+textblock(m,320,740,title,body,110,38,'#FFFFFF')[0]+wave(1030,845,C)
 elif i==3:
  out+=txt(m,105,tag.upper(),28,600,slot='eyebrow')+txt(568,1110,'04',342,700,'#E1E5E7')+textblock(m,310,900,title,body,110,38,emph=True)[0]+image(m,865,435,300,1)
 elif i==4:
  out+=image(0,0,w,716,2)+rect(0,0,w,716,'url(#shade)')+txt(m,105,tag.upper(),28,600,'#FFFFFF',slot='eyebrow')+textblock(m,842,940,title,body,94,34)[0]
 elif i==5:
  out+=namedimage(0,250,470,978,'revisions/v2/photos/OS-PH205.png')+txt(m,110,tag.upper(),28,600,slot='eyebrow')+textblock(535,340,480,title,body,101,34,emph=True)[0]
 elif i==6:
  out+=rect(0,0,w,72,N)+txt(m,48,tag.upper(),27,600,'#FFFFFF',slot='eyebrow')+textblock(m,310,930,title,body,112,38,emph=True)[0]
  for j in range(3):out+=image(64+j*320,865,296,300,j)
  out+=path('M64 817H1016L986 788M1016 817L986 846',B,4)
 elif i==7:
  out+=image(0,0,w,1228,2)+rect(0,0,w,1228,'url(#shade)')+txt(m,105,tag.upper(),28,600,'#FFFFFF',slot='eyebrow')+textblock(m,330,936,title,body,108,38,'#FFFFFF')[0]+rect(m,1028,792,90,C)+txt(m+22,1088,'Evidence before bigger promises.',42,600,N,'caption')
 elif i==8:
  out+=txt(m,105,tag.upper(),28,600,slot='eyebrow')+textblock(m,300,575,title,body,102,35)[0]+path('M730 250V1110',S,2)
  for y,label in [(370,'ASK'),(665,'EXPLAIN'),(960,'REVIEW')]:out+=txt(780,y,label,45,700,N)
  out+=image(m,830,575,340,0)
 elif i==9:
  out+=txt(m,105,tag.upper(),28,600,slot='eyebrow');ls=wrap(title,940,108)
  for j,t in enumerate(ls):out+=rect(m-4,245+j*124-88,min(936,len(t)*108*.55+20),110,C if j==len(ls)-1 else '#E9ECE4')+txt(m+8,245+j*124,t,108,700,N,'title-'+str(j))
  for j,t in enumerate(wrap(body,930,38)):out+=txt(m,710+j*55,t,38,400,N,'body-'+str(j))
  out+=image(0,876,w,352,1)+wave(1080,w,C)
 else:
  out+=txt(m,105,tag.upper(),28,600,slot='eyebrow')+textblock(m,300,936,title,body,110,38,emph=True)[0]
  for j,t in enumerate(['Meaning','Voice','Factual detail']):y=815+j*130;out+=rect(m,y-51,52,52,C)+path(f'M{m+10} {y-23}l12 12l24-31',N,4)+txt(156,y,t,58,600,N,'check-'+str(j))
 return out

def video(i,w,h,title,body,tag):
 m=64;out=txt(m,62,tag.upper(),27,600,slot='eyebrow');x,y,mw,mh=64,110,w-128,h-280
 if i==0:x,y,mw,mh=64,110,1080,600
 if i==1:x,y,mw,mh=380,110,840,600
 if i==2:x,y,mw,mh=64,110,1472,480
 if i==3:x,y,mw,mh=64,110,950,600
 if i==4:x,y,mw,mh=64,165,1472,480
 if i==5:x,y,mw,mh=64,110,650,600
 if i==6:x,y,mw,mh=64,110,1472,600
 if i==7:x,y,mw,mh=500,110,640,600
 if i==8:x,y,mw,mh=64,110,1120,600
 if i==9:x,y,mw,mh=270,110,1050,590
 if i==10:x,y,mw,mh=64,110,1472,570
 bg=namedimage(x,y,mw,mh,'revisions/v2/photos/OS-PH205.png') if i==1 else namedimage(x,y,mw,mh,'revisions/v3/nature/05-real-human-shadow.webp') if i==3 else namedimage(x,y,mw,mh,'revisions/v2/paper/OS-TX201.png') if i in [5,8,10] else image(x,y,mw,mh,i)
 out+=bg+(rect(x,y,mw,mh,'url(#shade)') if i not in [5,8,10] else '<defs><clipPath id="mediaClip">'+rect(x,y,mw,mh)+'</clipPath></defs><g clip-path="url(#mediaClip)"><g transform="translate('+str(x)+' 0)">'+wave(y+mh*.62,mw)+'</g></g>')+path(f'M{x} {y+mh}H{x+mw}',S,3)
 # Format-specific signs occupy actual media safe zones; no extra decorative nested containers.
 if i%3==0:out+=rect(x,y+mh-90,mw,90,N)+txt(x+28,y+mh-36,'Explain one consequential product choice.',34,500,'#FFFFFF','caption')
 elif i%3==1:out+=rect(x+30,y+30,190,48,C)+txt(x+45,y+64,'CHAPTER '+str(i+1).zfill(2),26,600,slot='caption')
 else:out+=path(f'M{x+30} {y+30}h70M{x+30} {y+30}v55M{x+mw-30} {y+mh-30}h-70M{x+mw-30} {y+mh-30}v-55',N if i in [5,8,10] else '#FFFFFF',3)+txt(x+35,y+mh-40,'Sound optional. Meaning essential.',31,500,N if i in [5,8,10] else '#FFFFFF','caption')
 out+=textblock(m,h-117,w-128,title,'',33,20)[0]
 if i in [0,3,5,8]:
  side=x+mw+40;out+=txt(side,170,'STORY',26,600)+txt(side,218,'DECISION',26,600)+txt(side,266,'CONSEQUENCE',26,600)
 return out

def captions(i,w,h,title,body,tag):
 out='';m=42;fs=42
 if i==0:out+=rect(0,80,w,145,N);col='#FFFFFF';x=42;y=142
 elif i==1:out+=path('M42 80V246',B,7);col=N;x=78;y=137
 elif i==2:out+=rect(42,40,200,42,C)+txt(54,70,'SOURCE NOTE',23,600);col=N;x=42;y=150
 elif i==3:out+=txt(42,145,'“',100,700,S);col=N;x=118;y=135
 elif i==4:out+=txt(42,150,'05',96,700,S);col=N;x=230;y=130
 elif i==5:out+=rect(42,45,215,44,N)+txt(56,76,'KEY QUESTION',22,600,'#FFFFFF');col=N;x=42;y=153
 elif i==6:out+=rect(0,50,w,195,C);col=N;x=42;y=123
 elif i==7:out+=path('M42 68H1158M42 256H1158',S,2);col=N;x=42;y=135
 elif i==8:out+=rect(42,126,720,22,C);col=N;x=42;y=133
 elif i==9:out+=path('M42 68H1050L1028 47M1050 68L1028 89',B,3);col=N;x=42;y=150
 else:out+=rect(42,65,105,145,N)+txt(66,155,'Q',56,700,'#FFFFFF');col=N;x=185;y=130
 for j,t in enumerate(wrap(title,w-x-65,fs)):out+=txt(x,y+j*fs*1.08,t,fs,700,col,'title-'+str(j))
 out+=txt(x,min(264,y+len(wrap(title,w-x-65,fs))*fs*1.08+28),body,24,400,col,'body-0')
 return out

def schema(i,w,h,title,body,tag):
 out=txt(54,57,tag.upper(),25,600,slot='eyebrow')+txt(54,129,title,49,700,N,'title-0')+txt(54,185,'Illustrative workflow · not a client implementation',27,400,N,'body-0')
 layouts=[[(65,370),(450,370),(835,370)],[(480,260),(480,460),(480,660)],[(65,330),(450,330),(835,330),(450,610)],[(65,330),(450,330),(835,330),(65,610),(835,610)],[(65,280),(65,520),(450,400),(835,400)],[(65,400),(450,280),(450,530),(835,400)],[(65,300),(450,300),(835,300),(450,600)],[(65,300),(450,450),(835,600)],[(65,520),(450,300),(835,520)],[(65,300),(65,600),(450,450),(835,450)],[(65,300),(450,300),(835,300),(450,600)]]
 labels=[['Source','Human review','Approved output'],['Buyer context','Clear position','Content direction'],['Interview','Draft','Review','Source check'],['Question','Options','Decision','Evidence','Buyer consequence'],['Notes','Product context','Writer','Founder review'],['Experience','Technical detail','Voice feedback','Clear draft'],['Company story','Founder view','Campaign','Approval'],['Observe','Interpret','Test next'],['Invitation','Relevant reason','Human conversation'],['Founder','Expert','Interview','Editorial material'],['Draft','Claims check','Approval','Revision']][i]
 pts=layouts[i];nw,nh=295,118
 edges=[(j,j+1) for j in range(len(pts)-1)]
 if i in [2,6,10]:edges=[(0,1),(1,2),(1,3)]
 if i==3:edges=[(0,1),(1,2),(3,1),(2,4)]
 if i in [4,9]:edges=[(0,2),(1,2),(2,3)]
 if i==5:edges=[(0,1),(0,2),(1,3),(2,3)]
 for a,b in edges:
  ax,ay=pts[a];bx,by=pts[b]
  if abs(bx-ax)>80:
   x1,y1=ax+nw,ay+nh/2;x2,y2=bx-12,by+nh/2;mid=(x1+x2)/2;out+=path(f'M{x1} {y1}H{mid}V{y2}H{x2}',B,3,'marker-end="url(#arrow)"')
  else:out+=path(f'M{ax+nw/2} {ay+nh}V{by-12}',B,3,'marker-end="url(#arrow)"')
 for j,((x,y),label) in enumerate(zip(pts,labels)):
  out+=rect(x,y,nw,nh,'#FFFFFF',0,N)+rect(x,y,6,nh,C if j==len(pts)-1 else N)
  for q,t in enumerate(wrap(label,nw-34,31)):out+=txt(x+18,y+49+q*36,t,31,600,N,'node-'+str(j)+'-'+str(q))
 return out

items=[]
for cat,(w,h) in config.items():
 folder=D/'masters'/cat;folder.mkdir(parents=True,exist_ok=True)
 for i,(key,title,body,tag) in enumerate(contexts):
  body=body.replace(',',', ')
  id='OS-'+{'banner':'BA','poster':'PO','block':'BL','heading':'HE','video-frame':'VF','caption-emphasis':'CE','schema':'SC'}[cat]+'3-'+str(i+1).zfill(2)
  content=poster(i,w,h,title,body,tag) if cat=='poster' else video(i,w,h,title,body,tag) if cat=='video-frame' else captions(i,w,h,title,body,tag) if cat=='caption-emphasis' else schema(i,w,h,title,body,tag) if cat=='schema' else editorial(cat,i,w,h,title,body,tag)
  svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img"><title>{e(id+" "+cat+" "+layoutnames[i])}</title><desc>Original editable Outspoken design specimen. No customer result or implementation is claimed.</desc>{defs()}{rect(0,0,w,h)}{content}{footer(w,h)}</svg>'
  p=folder/(id+'.svg');p.write_text(svg)
  import re
  slots=re.findall(r'data-slot="([^"]+)"',svg)
  items.append({'id':id,'category':cat,'variant':key,'layout':layoutnames[i] if cat not in ['video-frame','caption-emphasis','schema'] else cat+'-'+key,'use_when':tag+': '+body,'size':{'width':w,'height':h},'source':'masters/'+cat+'/'+id+'.svg','editable_props':slots,'defaults':{'title':title,'body':body,'eyebrow':tag},'spacing':{'outer':42 if h<=400 else 54,'minimum_text_line_gap':12,'media_safe_zone':30},'angle':{'rest':0,'website_perspective_optional':{'yaw_degrees':12 if cat=='video-frame' else 0,'focus_yaw_degrees':0}},'type':{'headline':'Archivo700','body':'Inter400','caption':'Inter500'},'colours':{'navy':N,'silver':S,'citron':C,'paper':P},'meaningful_variation':layoutnames[i]+': '+tag,'label':'Illustrative design specimen','sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'render_state':'pending'})
# 11 publication variants use10 master families + a new compact editorial checklist.
pub=D/'masters/publication';pub.mkdir(exist_ok=True)
base=Path('brand-library/packages/content/revisions/v3');ids=['OS-T301','OS-T302','OS-T303','OS-T304-01','OS-T305','OS-T306','OS-T307','OS-T308','OS-T309','OS-T310']
for i,id in enumerate(ids,1):
 s=(base/(id+'.svg')).read_text().replace('../../../assets/','../../../assets/');dest=pub/('OS-PUB3-'+str(i).zfill(2)+'.svg');s=s.replace('#9FA9B8','#A9AFBA');counter=[0]
 def mark(m):
  n=counter[0];counter[0]+=1;return '<text data-slot="text-'+str(n)+'" '+m.group(1)
 s=__import__('re').sub(r'<text (?![^>]*data-slot=)([^>]*>)',mark,s);dest.write_text(s);items.append({'id':dest.stem,'category':'publication','variant':id,'layout':'existing-native-master-'+id,'use_when':'Use original '+id+' publication master;LinkedIn UI chrome remains separate.','size':{'width':1080,'height':1350},'source':'masters/publication/'+dest.name,'editable_props':['text-'+str(n) for n in range(counter[0])],'spacing':{'outer':72},'angle':{'rest':0},'type':{'headline':'Archivo700','body':'Inter400'},'colours':{'navy':N,'silver':S,'citron':C,'paper':P},'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'render_state':'pending'})
id='OS-PUB3-11';s=f'<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1350" viewBox="0 0 1080 1350">{defs()}{rect(0,0,1080,1350)}{txt(72,100,"BEFORE THE POST",29,600,slot="eyebrow")}{textblock(72,260,936,"Is it ready to leave the draft?","A practical review checklist.",74,38,emph=True)[0]}'
for i,t in enumerate(['One clear buyer question','A point worth explaining','A source behind the claim','The founder’s factual review','An appropriate next step']):y=590+i*112;s+=rect(72,y-38,36,36,'#FFFFFF',0,N)+path(f'M80 {y-20}l8 8l15-20',B,3)+txt(142,y,t,35,500,N,'check-'+str(i))
s+=footer(1080,1350)+'</svg>';p=pub/(id+'.svg');p.write_text(s);items.append({'id':id,'category':'publication','variant':'approval-checklist','layout':'open-review-checklist','use_when':'Show how professional source/review discipline supports a useful publication.','size':{'width':1080,'height':1350},'source':'masters/publication/'+p.name,'editable_props':['eyebrow','title-0','title-1','body-0','check-0','check-1','check-2','check-3','check-4'],'spacing':{'outer':72,'row_gap':112},'angle':{'rest':0},'type':{'headline':'Archivo700','body':'Inter400'},'colours':{'navy':N,'silver':S,'citron':C,'paper':P},'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'render_state':'pending'})
m={'version':'3.0.0','expected_categories':list(config)+['publication'],'expected_per_category':11,'expected_total':88,'count_rule':'77 newly generated families across7 requested categories plus11 publication variants. The first10 publications reuse current native masters;the11th is new.','entries':items,'source_rights':'Original authoredSVG/copy plus existing original generated nature images and licensed Archivo/Inter fonts. No competitor media,customer proof or copied M2Lab layout.','platform_boundary':'Website interaction/perspective is a presentation layer,not a native LinkedIn feature.','react_component':'CatalogSurface.tsx','storybook':'Catalog.stories.tsx','render_state':'pending'}
(D/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
(D/'render.html').write_text('''<!doctype html><html><meta charset="utf-8"><style>html,body{margin:0;overflow:hidden}svg{display:block}</style><main></main><script>let p=new URLSearchParams(location.search).get('src');let base=document.createElement('base');base.href=new URL(p,location.href).href;document.head.append(base);fetch(base.href).then(r=>r.text()).then(s=>{document.querySelector('main').innerHTML=s;document.fonts.ready.then(()=>window.catalogReady=true)})</script></html>''')
(D/'index.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Outspoken V3 component atlas</title><style>body{font:16px Inter,Arial;color:#162760;background:#f6f6f1;margin:36px}h1{font-size:36px}nav{display:flex;gap:12px;flex-wrap:wrap}a{color:inherit}section{margin:64px 0}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:24px}object{width:100%;height:360px;background:white;object-fit:contain}.meta{font-size:13px;line-height:1.5}h3{margin-bottom:6px}</style><h1>Outspoken · editable component atlas</h1><p>11 layouts in each of8 categories.88 nativeSVG surfaces. Design specimens,not customer evidence. M2Lab informed practical breadth and signage only.</p><nav></nav><main></main><script>fetch('manifest.json').then(r=>r.json()).then(m=>{for(let c of m.expected_categories){let a=document.createElement('a');a.href='#'+c;a.textContent=c;document.querySelector('nav').append(a);let s=document.createElement('section');s.id=c;s.innerHTML='<h2>'+c+'</h2><div class="grid"></div>';for(let e of m.entries.filter(e=>e.category===c)){let art=document.createElement('article');art.innerHTML='<object type="image/svg+xml" data="'+e.source+'"></object><h3>'+e.id+' · '+e.layout+'</h3><p class="meta">'+e.use_when+'</p><a href="'+e.source+'">Open nativeSVG master</a>';s.querySelector('.grid').append(art)}document.querySelector('main').append(s)}})</script></html>''')
print({'entries':len(items),'per_category':{c:sum(x['category']==c for x in items) for c in m['expected_categories']}})
