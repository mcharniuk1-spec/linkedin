from pathlib import Path
import json,html,textwrap,re,xml.etree.ElementTree as ET,shutil,base64
P=Path(__file__).resolve().parent;A=P/'assets'
N='#162760';B='#3157D5';M='#EAA93C';MARK='#F6D591';W='#FFFFFF';PAPER='#F7F8FA';SILVER='#A9AFBA';GREY='#5D6679';LINE='#DDE2EB'
BROWSER_FAMILY={'body':'Mona Sans','bold':'Mona Sans','display':'Fraunces','mono':'Geist Mono'}
FONT_CSS=''.join('@font-face{font-family:'+repr(family)+';src:url(data:font/woff2;base64,'+base64.b64encode((A/'fonts'/file).read_bytes()).decode()+') format(\"woff2\");font-weight:100 900;}' for family,file in [('Fraunces','fraunces-latin-full-normal.woff2'),('Mona Sans','mona-sans-latin-wght-normal.woff2'),('Geist Mono','geist-mono-latin-wght-normal.woff2')])
F={'body':'MonaSansExtraLight-Regular_Regular','bold':'MonaSansExtraLight-Regular_SemiBold','display':'Fraunces-Regular','mono':'GeistMono-Medium'}
def esc(x):return html.escape(str(x),quote=True)
def tx(s,x,y,size=38,role='body',color=N):
 return f'<text x="{x}" y="{y}" font-family="{BROWSER_FAMILY[role]}" data-postscript="{F[role]}" font-weight="{600 if role=='bold' else 500 if role=='mono' else 400}" font-size="{size}" letter-spacing="{(-size*.02 if role=='display' else size*.09 if role=='mono' else 0)}" fill="{color}">{esc(s)}</text>'
def wrap(s,x,y,size=38,width=42,lead=None,role='body',color=N):
 lines=textwrap.wrap(s,width,break_long_words=False);lead=lead or size*1.3
 return ''.join(tx(t,x,y+i*lead,size,role,color) for i,t in enumerate(lines)),y+len(lines)*lead
def rect(x,y,w,h,fill=W,r=0,stroke=None):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}"'+(f' stroke="{stroke}" stroke-width="2"' if stroke else '')+'/>'
def rule(x,y,w,color=LINE):return f'<path d="M{x} {y}h{w}" stroke="{color}" stroke-width="2"/>'
def badge(s,x,y,w=None,dark=False):
 w=w or len(s)*18+34
 return rect(x,y-30,w,44,MARK,5)+tx(s,x+16,y,25,'bold',N)
def label(s,x,y,dark=False):return tx(s.upper(),x,y,23,'mono',MARK if dark else GREY)
def logo(dark=False):
 src=(A/('wordmark-inverse.svg' if dark else 'wordmark.svg')).read_text();root=ET.fromstring(src);v=root.get('viewBox').split();width=float(v[2]);body=src[src.index('>')+1:src.rindex('</svg>')];return f'<g transform="translate(64,48) scale({218/width})">{body}</g>'
def start(title,dark=False):
 s=f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1080" height="1350" viewBox="0 0 1080 1350"><title>{esc(title)}</title><defs><style>{FONT_CSS}</style></defs>'+rect(0,0,1080,1350,N if dark else W)+logo(dark)
 q,y=wrap(title,64,205,72,25,83,'display',W if dark else N);return s+q
jobs=[]
def save(pid,title,body,page=1,dark=False):
 name=f'{pid}-{page:02d}';svg=start(title,dark)+body+'</svg>'
 (A/(name+'.svg')).write_text(svg)
 texts=re.findall(r'<text[^>]*>(.*?)</text>',svg);trans='\n'.join(html.unescape(x) for x in texts)
 (A/(name+'-transcript.txt')).write_text(trans+'\n');(A/(name+'-alt.txt')).write_text(title+'. '+trans.replace('\n',' ')+(' The company-selection scene is AI-generated illustration.' if pid=='06-the-first-message' else '')+'\n')
 jobs.append({'id':pid,'page':page,'svg':'assets/'+name+'.svg','png':'assets/'+name+'.png'})
def paragraph(s,x,y,w=40,size=36,color=N,role='body'):
 return wrap(s,x,y,size,w,size*1.33,role,color)[0]
def number(s,x,y,color=M,size=68):return tx(s,x,y,size,'display',color)
def icon(kind,x,y):
 if kind=='source':return rect(x,y,94,112,PAPER,8,N)+rule(x+18,y+27,58,N)+rule(x+18,y+48,58,N)+rule(x+18,y+69,43,M)
 if kind=='talk':return rect(x,y,112,70,N,20)+f'<path d="M{x+24} {y+70}l-3 20 28-20" fill="{N}"/>'+rect(x+20,y+28,112,70,MARK,20)
 return rect(x,y,94,112,PAPER,8,N)+f'<path d="M{x+18} {y+37}l14 13 29-29" fill="none" stroke="{N}" stroke-width="7"/>'+rule(x+18,y+76,58,M)
# First carousel. Its chapters remain meaningful as separate slides.
id='01-the-flow';s=''
for i,(a,b) in enumerate([('Understand the business','Real knowledge, buyers and a useful point of view.'),('Make the profile clear','Who you help and what someone can inspect.'),('Build useful content','One buyer question, a clear example and a takeaway.'),('Continue the conversation','Relevant replies, checked context and an agreed next step.')]):
 y=445+i*202;s+=number(str(i+1),64,y, B,76)+tx(a,154,y-4,41,'bold')+paragraph(b,154,y+51,40,35)+rule(154,y+111,850)
s+=badge('VOICE + PIPELINE BUILDS ON THE CONTENT FOUNDATION',64,1270,940)
save(id,'A post starts a useful path.',s,1)
s=''
for j,(a,b,k) in enumerate([('Bring','Your product or service page, existing material and buyer questions.','source'),('Discuss','Who is it for, what needs to be clearer and what can we show?','talk'),('Leave with','A short summary, priorities and a useful next decision.','report')]):
 y=430+j*262;s+=icon(k,70,y-37)+rect(216,y-51,400 if j==2 else 330,78,MARK,7)+tx(a,230,y+5,56,'bold')+paragraph(b,230,y+90,35,38)
save(id,'Start with useful material.',s,2)
s=''
for j,(a,b,c) in enumerate([('Explain','The decision','Why did the team choose this approach?'),('Show','A worked example','How does one task work, including an exception?'),('Help choose','A practical checklist','What should the buyer check before deciding?')]):
 y=430+j*256;s+=number('0'+str(j+1),64,y+6,MARK,90)+label(a,240,y,True)+tx(b,240,y+65,47,'display',W)+paragraph(c,240,y+126,34,36,W)
save(id,'One example. Three useful posts.',s,3,True)
s=label('A RELEVANT EXAMPLE',64,426)+rect(64,460,952,145,PAPER,18)+tx('Can you send me details?',98,550,49,'display')
s+=label('A REPLY COULD BE',64,687)+rect(64,720,952,340,N,18)+paragraph('Of course. Here is a short example of our interview-to-post process. Which part would help you most: ideas, writing or review?',99,790,38,39,W)
s+=badge('ANSWER',64,1173,176)+badge('CLARIFY',263,1173,186)+badge('SHOW',473,1173,146)+badge('AGREE',643,1173,166)
save(id,'Give the reply a useful next step.',s,4)
# 02 buyer decision worksheet
s=''
for j,(a,b) in enumerate([('Is it worth solving?','Show where invoice approvals get delayed.'),('Is this approach suitable?','Compare manual and rule-based routing.'),('Can our team use it?','Walk through one invoice and one exception.')]):
 y=445+j*235;s+=rect(64,y-49,15,172,M)+tx(a,110,y,46,'display')+paragraph(b,110,y+72,40,37)
s+=label('ILLUSTRATIVE INVOICE-APPROVAL PRODUCT',64,1274)
save('02-the-strategy','Give the topic a buyer decision.',s)
# 03 annotated interview prompts
s=label('A BROAD PROMPT',64,421)+tx('Tell me about your journey.',64,491,43,'display',GREY)+f'<path d="M64 536h660" stroke="{SILVER}" stroke-width="3"/>'
s+=badge('ASK FOR THE DECISION',64,620,430)
for j,(a,b) in enumerate([('The choice','What did you choose and why?'),('The alternative','What made another route less suitable?'),('The example','What can a buyer inspect?'),('The position','What would you recommend or challenge?')]):
 y=730+j*132;s+=tx(a,64,y,34,'bold')+paragraph(b,386,y,28,33)+rule(64,y+54,952)
save('03-the-interview','Find the detail worth explaining.',s)
# 04 profile before and after
s=label('A VAGUE HEADLINE',64,411)+paragraph('Founder | AI | Innovation',64,471,33,42,GREY)
s+=badge('A DIRECTION TO TEST',64,600,384)+rect(64,639,952,205,PAPER,12)+paragraph('Building OutSpoken | LinkedIn content and buyer conversations for B2B teams.',98,702,39,40)
for j,(a,b) in enumerate([('ABOUT','Explain the problem and approach.'),('FEATURED','Give the visitor one useful example.'),('RECENT POSTS','Let the buyer hear your judgment.')]):
 y=935+j*116;s+=label(a,64,y)+paragraph(b,365,y,31,33)
save('04-the-profile','Make the profile the next useful step.',s)
# 05 tool-job matching, contrasting jobs and outputs
s=label('JOB',64,420)+label('STARTER TOOL',382,420)+label('USEFUL OUTPUT',728,420)+rule(64,451,952)
rows=[('Capture','Shared document','Source material'),('Plan','Content board','Buyer questions'),('Review','Visible edits','Approved claims'),('Publish','Native LinkedIn','Agreed revision'),('Research','Native search','Checked candidates'),('Follow through','CRM or Sheet','Actual next step')]
for j,(a,b,c) in enumerate(rows):
 y=525+j*111;s+=tx(a,64,y,34,'bold')+tx(b,382,y,31)+tx(c,728,y,29)+rule(64,y+40,952)
s+=badge('START WITH THE HANDOFF THAT NEEDS HELP',64,1269,838)
save('05-the-tools','Give every tool a clear job.',s)
# 06 meaningful photo context plus native editable annotations
s=paragraph('One checked observation. One useful next step.',64,414,43,38)
s+='<image x="64" y="510" width="952" height="635" preserveAspectRatio="xMidYMid slice" href="selection-context.png"/>'
s+=rect(88,790,485,234,N,12)+label('WHY THIS COMPANY?',118,843,True)+tx('Checked context',118,903,34,'bold',W)+tx('Relevant problem',118,948,34,'bold',W)+tx('Useful resource',118,993,34,'bold',W)
s+=''.join(rect(103,y,6,6,M,3) for y in [890,935,980])
s+=paragraph('Verify the reason before writing the message.',64,1241,45,34)
save('06-the-first-message','Give the message a reason to exist.',s)
# 07 resource + reply
s=label('EXAMPLE REPLY',64,410)+rect(64,451,952,338,PAPER,18)
s+=paragraph('Of course. Here is a short example of how we turn founder material into a post. Which part takes the most time: ideas, writing or review?',100,520,40,38)
for j,(a,b) in enumerate([('Answer','Send the relevant detail.'),('Clarify','Ask what changes the recommendation.'),('Continue','Record the actual answer and next step.')]):
 y=916+j*126;s+=badge(a,64,y,210)+paragraph(b,314,y,35,34)
save('07-the-reply','Send the useful detail first.',s)
# 08 source and three editorial angles
s=label('ONE REVIEWED SOURCE',64,408)+rect(64,444,952,128,N,12)+tx('A product or service workflow',100,523,45,'display',W)
for j,(a,b,c) in enumerate([('EXPLAIN','The choice','Why this approach?'),('SHOW','The work','How does one task work?'),('HELP CHOOSE','The test','What should a buyer check?')]):
 x=64+j*326;s+=rect(x,665,300,440,PAPER if j!=1 else MARK,12)+label(a,x+24,720)+paragraph(b,x+24,817,13,43,role='display')+paragraph(c,x+24,960,17,32)
s+=paragraph('Keep the facts. Change the buyer question.',64,1234,43,34)
save('08-the-case','One source. Three different uses.',s)
# 09 buying-group four-way questions
for j,(a,b) in enumerate([('User','What changes in my task?'),('Manager','What must the team adopt?'),('Finance','What cost and value can we assess?'),('Risk','Who checks data and responsibility?')]):
 x=64+(j%2)*490;y=435+(j//2)*390;dark=j==0;s=locals().get('s09','') if False else ''
s=''
for j,(a,b) in enumerate([('User','What changes in my task?'),('Manager','What must the team adopt?'),('Finance','What cost and value can we assess?'),('Risk','Who checks data and responsibility?')]):
 x=64+(j%2)*490;y=435+(j//2)*385;dark=j==0;s+=rect(x,y,462,350,N if dark else (MARK if j==3 else PAPER),14)+tx(a,x+30,y+74,48,'display',W if dark else N)+paragraph(b,x+30,y+155,20,36,W if dark else N)
save('09-the-buying-group','Your champion has a buying group.',s)
# 10 a worked review decision
s=label('ILLUSTRATIVE REVIEW NOTE',64,421)
for j,(a,b) in enumerate([('Observed','A relevant buyer asks how setup works.'),('Useful next post','Show a sample-data walkthrough.'),('Evidence to use','Actual reply, product steps and a clear example.'),('Action owner','Name the reviewer and set a review date.')]):
 y=499+j*182;s+=label(a,64,y)+paragraph(b,64,y+66,43,40)+rule(64,y+144,952)
s+=badge('ANALYTICS FOR DISTRIBUTION. CRM FOR CONVERSATIONS.',64,1272,944)
save('10-the-review','Turn the review into a decision.',s)
# 11 native interface comparison
s=label('ILLUSTRATIVE FIRST SCREEN',64,422)
for j,(tag,button,detail) in enumerate([('BROAD','Start your AI journey','The visitor still has to guess the task.'),('CONCRETE','Try a report with sample data','The action and expected result are clearer.')]):
 y=475+j*360;s+=rect(64,y,952,305,PAPER,18)+label(tag,97,y+54)+rect(98,y+100,884,91,N if j else SILVER,10)+tx(button,122,y+158,36,'bold',W if j else N)+paragraph(detail,98,y+249,44,31)
save('11-the-designer','Make the first action clear.',s)
# 12 answer checking path, no borrowed generic stats
s=rect(64,428,952,214,N,12)+label('ONE FEATURE',96,486,True)+paragraph('Show how a person can check the answer.',96,554,34,43,W,'display')
for j,(a,b) in enumerate([('Input','What question or material did the tool use?'),('Output','What exactly did it return?'),('Evidence','Which source can the user inspect?'),('Review','When should a person check or stop?')]):
 y=737+j*130;s+=number(str(j+1),64,y,M,55)+tx(a,142,y,36,'bold')+paragraph(b,386,y,31,32)
save('12-the-developer','Give the buyer a way to check.',s)
# 13 review decisions
s=''
for j,(a,b) in enumerate([('Product truth','Does this match what we deliver?'),('Founder position','Can the author stand behind it?'),('Reader action','Is the next step useful and agreed?')]):
 y=450+j*218;s+=number('0'+str(j+1),64,y,M,77)+tx(a,222,y,43,'display')+paragraph(b,222,y+71,35,36)+rule(222,y+125,794)
s+=rect(64,1130,952,146,MARK,10)+paragraph('Confirm the promised timing or remove the time claim.',96,1187,43,32)
save('13-the-manager','Give the reviewer a decision.',s)
# 14 offer, foundation and extension
s=rect(64,428,952,327,N,16)+tx('Voice',98,505,58,'display',W)+paragraph('Make your expertise understandable.',98,578,36,40,W)+paragraph('Strategy · Profile · Posts · Visuals · Review',98,689,48,30,W)
s+=rect(64,800,952,315,MARK,16)+tx('Voice + Pipeline',98,877,58,'display')+paragraph('Build relevant buyer conversations.',98,948,36,40)+paragraph('Research · Outreach · Qualification · Meeting context',98,1057,48,29)
s+=badge('Book an intro call',64,1259,383)
save('14-the-offer','Choose the work your business needs.',s)
# 15 proportional planning agenda
s=number('45',64,522,N,176)+tx('MINUTES',73,577,26,'mono',GREY)+paragraph('A clearer brief and a useful next decision.',371,427,24,42,role='display')
agenda=[('0–12','Business and buyer',12),('12–22','Current process',10),('22–31','The main constraint',9),('31–38','The relevant branch',7),('38–45','Fit and next action',7)]
y=715
for j,(when,what,mins) in enumerate(agenda):
 s+=rect(64,y-34,max(18,mins*5),56,[N,B,M,SILVER,MARK][j],4)+tx(when,159,y+6,29,'mono')+tx(what,375,y+6,36,'bold');y+=102
s+=label('DRAFT AGENDA. FOLLOW THE CLIENT’S PRIORITY.',64,1282)
save('15-the-call','Use the call to find the useful work.',s)
# 16 purposeful cadence worksheet
s=''
for j,(a,b) in enumerate([('Reader purpose','What should someone understand or do?'),('Source material','Which distinct examples can we support?'),('Review time','Who can check facts and voice?'),('Useful format','Show, explain, compare or demonstrate.'),('Review point','When will we decide whether to adjust?')]):
 y=425+j*155;s+=rect(64,y-30,13,91,M)+tx(a,108,y,36,'bold')+paragraph(b,108,y+55,43,33)
s+=badge('AGREE THE STARTING CADENCE ON THE CALL',64,1280,850)
save('16-the-cadence','Choose a rhythm you can support.',s)
(P/'render-jobs.json').write_text(json.dumps(jobs,indent=2)+'\n');assert len(jobs)==19
print('Built19 varied nativeSVGs with exact branded type, chapter emphasis, meaningful examples and one contextual photo.')
