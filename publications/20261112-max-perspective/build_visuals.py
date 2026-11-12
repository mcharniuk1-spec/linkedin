import base64, html, json, textwrap, shutil
from pathlib import Path
R=Path(__file__).resolve().parent
P=R
W,H=1080,1350
BG,INK,MUTED,LINE,ACC='#FCFFFC','#162760','#676D7A','#E5E8ED','#FBD387'
def t(s,x,y,size=40,serif=False,weight=400):
    return f'<text x="{x}" y="{y}" font-size="{size}" font-family="{("Young Serif" if serif else "Mona Sans")}" font-weight="{weight}" fill="{INK}">{html.escape(s)}</text>'
def para(s,x,y,size=36,cols=43,leading=48):
    lines=textwrap.wrap(s,width=cols,break_long_words=False)
    return ''.join(t(s,x,y+i*leading,size) for i,s in enumerate(lines)),y+len(lines)*leading
def rule(y):return f'<path d="M72 {y}H1008" stroke="{LINE}" stroke-width="2"/>'
def marker(x,y,w):return f'<rect x="{x}" y="{y+44}" width="{w}" height="8" fill="{ACC}"/>'
def row(title,detail,y):
    out=t(title,72,y,43,True); q,yy=para(detail,72,y+59,39,41,49);return out+q+rule(yy+24)
def art(n,p):
    v=p['visual'];o='';end=1180
    if n==0:
        o+=t('Before I edit the wording,',72,620,43,True)
        o+=t('I want the reader’s question.',72,679,43,True)
        for i,s in enumerate(['What will they understand?','Which decision can they inspect?','What can they use afterward?']):
            o+=rule(768+i*112)+t(s,72,829+i*112,38)
    elif n==1:
        for k,(label,value) in enumerate([('Reaction counts',276),('Comment counts',256)]):
            y=555+k*260;o+=t(label,72,y,36,False,600)+t(f'{value} / 279',72,y+76,66,True)+t('Median '+('107.5' if k==0 else '36.5'),640,y+76,36)
            for i in range(279):
                x=72+(i%31)*29;yy=y+103+(i//31)*10
                o+=f'<rect x="{x}" y="{yy}" width="21" height="6" fill="{INK if i<value else ACC}"/>'
        o+=t('Navy: observed · amber: missing',72,1080,29)
        o+=t('Reach, impressions and sales were unobserved.',72,1130,29)
    elif n==2:
        q,y=para('Goal. Constraint. Real alternative.',72,500,38,42);o+=q
        q,y=para('Then ask what actually happened.',72,y+12,38,42);o+=q
        raw=base64.b64encode((P/'assets/interview-context.png').read_bytes()).decode()
        o+=f'<defs><clipPath id="scene"><rect x="72" y="690" width="936" height="470" rx="8"/></clipPath></defs><image x="72" y="690" width="936" height="624" preserveAspectRatio="xMidYMid slice" href="data:image/png;base64,{raw}" clip-path="url(#scene)"/>'
        o+=t('AI-generated context illustration; no real meeting depicted.',72,1202,25)
    elif n==3:
        o+=t('An illustrative sentence',72,540,31)
        for i,s in enumerate(['A support lead','reviews unclear requests','before a reply goes out.']):
            o+=marker(72,594+i*75,min(870,len(s)*19))+t(s,72,624+i*75,44,True)
        for i,s in enumerate(['Person: who owns the work?','Task: what do they actually do?','Check: does the product work this way?']):o+=t(s,72,935+i*73,34)
    elif n==4:
        o+=row('What you can inspect','One input, the result, the review step.',570)
        o+=row('What to ask next','Unclear cases, failures and the conditions.',803)
        o+=row('What needs broader evidence','Reliability, effort and repeatability.',1036)
    elif n==5:
        o+=t('The sentence has to name the handoff.',72,550,36)
        for i,(s,d) in enumerate([('The founder','Flags an inaccurate product detail.'),('Writer and designer','Update the caption and visual.'),('The final reviewer','Checks that both versions agree.')]):
            y=665+i*166;o+=marker(72,y-15,44)+t(s,145,y,46,True)+t(d,145,y+65,34)
        o+=t('Use actual product details. This is a writing check.',72,1190,28)
    elif n==6:
        o+=t('I can ask for a complete rewrite.',72,570,43,True)
        o+=t('The position still has to be mine.',72,633,43,True)
        for i,s in enumerate(v['labels']):o+=rule(748+i*135)+t(s,72,818+i*135,39)
    elif n==7:
        o+=t('A vague visual label',72,535,30)
        o+=t('Observation limit',72,610,46,True)
        o+=t('What could the reader ask instead?',72,726,38)
        for i,s in enumerate(['What did this example show?', 'Which case did we inspect?', 'What still needs testing?']):
            o+=marker(72,795+i*85,min(900,len(s)*19))+t(s,72,825+i*85,43,True)
        o+=t('Turn the label into a useful question.',72,1150,35)
    elif n==8:
        for i,(a,b) in enumerate([('Did they understand?','Ask a reader to explain the point back.'),('Who saw it?','Use available native analytics.'),('Was there interest?','Read the actual conversation in context.')]):o+=row(a,b,550+i*220)
        o+=t('Each measure has limits. No sales result is assumed.',72,1240,27)
    else:
        q,y=para('I want a founder to read the final post and recognise their own thinking in it.',72,560,46,35,64);o+=q
        o+=marker(72,899,610)
        for i,s in enumerate(['Product truth.','A useful buyer question.','A draft the author can stand behind.']):o+=t(s,72,928+i*75,39)
        o+=t('Max Charniuk',72,1207,37,True)
    return o
posts=json.loads((P/'content.json').read_text());jobs=[]
for n,p in enumerate(posts):
    v=p['visual'];head=textwrap.wrap(v['headline'],width=27,break_long_words=False)
    o=f'<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1350" viewBox="0 0 1080 1350"><title>{html.escape(v["headline"])}</title><desc>{html.escape(v["detail"]+" "+"; ".join(v["labels"]))}</desc><rect width="1080" height="1350" fill="{BG}"/>'
    o+=t('OutSpoken',72,90,32,True)
    for i,s in enumerate(head):o+=t(s,72,220+i*82,68,True)
    o+=art(n,p)
    o+='</svg>'
    (P/'assets'/f'{p["id"]}.svg').write_text(o)
    jobs.append({'id':p['id'],'svg':f'assets/{p["id"]}.svg','png':f'assets/{p["id"]}.png'})
    (P/'assets'/f'{p["id"]}-alt.txt').write_text(v['headline']+'. '+v['detail']+' '+ '; '.join(v['labels'])+('. Generated interview-context image shows anonymous hands, a notebook and paper slips; it is an illustration, not documentary evidence.' if n==2 else '')+'\n')
(R/'render-jobs.json').write_text(json.dumps(jobs,indent=2))
gallery='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Max’s OutSpoken publications — review edition</title><style>@font-face{font-family:Young;src:url(assets/fonts/YoungSerif-Regular.ttf)}@font-face{font-family:Mona;src:url(assets/fonts/mona-sans-latin-wght-normal.woff2)}*{box-sizing:border-box}body{margin:0;background:#FCFFFC;color:#162760;font:18px/1.6 Mona,Arial,sans-serif}main{max-width:1120px;margin:auto;padding:48px 24px}h1,h2{font-family:Young,Georgia,serif;font-weight:400}h1{font-size:42px;line-height:1.2}header{max-width:760px}article{display:grid;grid-template-columns:1fr 1fr;gap:40px;padding:56px 0;border-top:1px solid #e5e8ed}img{width:100%;height:auto;display:block}pre{white-space:pre-wrap;font:inherit}aside{padding:20px;background:#f3f4f8}a{color:inherit}a:focus-visible{outline:3px solid #547CD6;outline-offset:4px}@media(max-width:720px){article{grid-template-columns:1fr}h1{font-size:34px}main{padding:28px 20px}}</style><main><header><p>Review edition · 12 November 2026</p><h1>My perspective, made useful to the reader.</h1><p>Ten personal drafts for Max, with distinct OutSpoken repost introductions. Facts, stance, voice and final visual approval remain for author review. No posts have been published.</p><p><a href="../../reports/20261112-sequential-execution/README.md">Execution report and questions</a> · <a href="CAPTIONS.md">All captions</a></p></header>'''
for p in posts:
    alt=(P/'assets'/f'{p["id"]}-alt.txt').read_text().strip()
    gallery+=f'<article id="{p["id"]}"><div><a href="assets/{p["id"]}.png"><img src="assets/{p["id"]}.png" width="1080" height="1350" alt="{html.escape(alt,quote=True)}"></a></div><div><h2>{html.escape(p["title"])}</h2><pre>{html.escape(p["caption"])}</pre><aside><b>Company repost introduction</b><p>{html.escape(p["outspoken_repost"])}</p><b>Your input</b><p>{html.escape(p["author_question"])}</p></aside></div></article>'
(P/'index.html').write_text(gallery+'</main></html>')
print('Built',len(jobs),'editable SVGs and gallery')
