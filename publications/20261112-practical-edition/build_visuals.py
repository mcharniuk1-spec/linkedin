import html,json,textwrap,re
from pathlib import Path
R=Path(__file__).resolve().parent;P=R
BG,INK,MUTED,LINE,ACC,WHITE='#FCFFFC','#162760','#676D7A','#E5E8ED','#FBD387','#FFFFFF'
def e(s):return html.escape(str(s),quote=True)
def t(s,x,y,z=40,bold=False,serif=False,color=INK):return f'<text x="{x}" y="{y}" font-family="{("Young Serif" if serif else "Mona Sans")}" font-size="{z}" font-weight="{600 if bold else 400}" fill="{color}">{e(s)}</text>'
def para(s,x,y,z=39,w=43,lead=None,serif=False,bold=False):
 a=textwrap.wrap(s,w,break_long_words=False);lead=lead or z*1.3
 return ''.join(t(v,x,y+i*lead,z,bold,serif) for i,v in enumerate(a)),y+len(a)*lead
def ln(y,x=72,w=936):return f'<path d="M{x} {y}h{w}" stroke="{LINE}" stroke-width="2"/>'
def note(x,y,w,h):return f'<rect x="{x+7}" y="{y+9}" width="{w}" height="{h}" rx="10" fill="{LINE}"/><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{WHITE}" stroke="{LINE}" stroke-width="2"/>'
def underline(x,y,w):return f'<path d="M{x} {y}h{w}" stroke="{ACC}" stroke-width="10" stroke-linecap="round"/>'
def row(title,body,y):
 s=t(title,72,y,45,True);p,yy=para(body,72,y+61,38,44);return s+p+ln(yy+24)
def blank(title):
 s=f'<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1350" viewBox="0 0 1080 1350"><title>{e(title)}</title><rect width="1080" height="1350" fill="{BG}"/>'
 s+=t('OutSpoken',72,86,31,serif=True)
 p,yy=para(title,72,206,67,24,79,True);s+=p
 return s
def footer(s):return t(s,72,1268,27,color=MUTED)
def emit(id,title,body,foot='',page=1):
 svg=blank(title)+body+(footer(foot) if foot else '')+'</svg>';name=f'{id}-{page:02d}'
 (P/'assets'/f'{name}.svg').write_text(svg)
 texts=re.findall(r'<text[^>]*>(.*?)</text>',svg)
 transcript='\n'.join(html.unescape(x) for x in texts)
 (P/'assets'/f'{name}-transcript.txt').write_text(transcript+'\n')
 (P/'assets'/f'{name}-alt.txt').write_text(title+'. '+transcript.replace('\n',' ')+'\n')
 jobs.append({'id':id,'page':page,'svg':f'assets/{name}.svg','png':f'assets/{name}.png'})
 return name
posts=json.loads((P/'content.json').read_text());jobs=[]
for n,p in enumerate(posts):
 id=p['id'];title=p['visual']['headline'];s=''
 if n==0:
  title='Someone read your post. What happens next?'
  stages=[('Your knowledge','Interview, product material and buyer questions.'),('A useful explanation','A clear profile, posts and visual examples.'),('A relevant conversation','One question, useful material and actual replies.'),('An agreed next step','Qualification and a meeting brief when there is fit.')]
  for j,(a,b) in enumerate(stages):
   y=493+j*158;s+=f'<circle cx="100" cy="{y-14}" r="27" fill="{INK}"/>'+t(str(j+1),91,y,31,bold=True,color=WHITE)
   if j<3:s+=f'<path d="M100 {y+15}V{y+108}" stroke="{LINE}" stroke-width="3"/>'
   s+=t(a,151,y,43,True);q,yy=para(b,151,y+52,33,42,43);s+=q
  emit(id,title,s,'Voice builds the content. Pipeline adds researched conversations.',1)
  s='';s+=note(72,449,936,640)
  for j,(a,b) in enumerate([('Bring','Product deck, existing posts and buyer questions.'),('Discuss','Who is it for? What problem? What makes it different?'),('Leave with','A buyer brief, voice guide and profile direction.')]):
   y=535+j*189;s+=t(a,108,y,43,True);q,yy=para(b,108,y+60,39,40);s+=q
  emit(id,'Start with what you already know',s,'The founder supplies product truth and approves the point of view.',2)
  s=''
  for j,(a,b) in enumerate([('Explain the decision','Why does this approach matter to the buyer?'),('Show the work','A worked example, walkthrough or comparison.'),('Help someone choose','A checklist they can use in their own situation.')]):s+=row(a,b,500+j*225)
  emit(id,'Give one buyer question three useful angles',s,'Original writing and meaningful visuals; facts reviewed by the founder.',3)
  s+= ''
  s=note(72,470,936,210)+t('Example buyer reply',110,528,30,color=MUTED)
  q,yy=para('How would this work for our team?',110,587,44,34,55,True);s+=q
  s+=note(72,724,936,268)+t('A useful next question',110,780,30,color=MUTED)
  q,yy=para('Which reporting task would you want to improve first?',110,840,44,34,55,True);s+=q
  s+=t('Clarify the problem. Share the right example.',72,1108,38)
  s+=t('Agree whether a meeting is useful.',72,1163,38)
  emit(id,'Keep the conversation moving',s,'Voice + Pipeline includes research, reply qualification and a sales brief.',4)
 elif n==1:
  for j,(a,b) in enumerate([('Is the problem worth solving?','Post: find where invoice approvals get delayed.'),('Is this approach right for us?','Post: compare manual and rule-based routing.'),('Can we put it to work?','Post: walk through one invoice to approval.')]):s+=row(a,b,500+j*226)
  emit(id,title,s,'Illustrative invoice-approval product. Each post answers a different question.')
 elif n==2:
  s+=note(72,460,936,668)
  for j,(a,b) in enumerate([('The decision','Why did you choose this route?'),('The buyer question','What must they understand?'),('The usable example','What can we show or explain?'),('Your position','What would you recommend or challenge?')]):
   y=530+j*148;s+=t(a,108,y,40,True);q,yy=para(b,108,y+54,36,43);s+=q
  emit(id,title,s,'Use this as the interview sheet, then review the factual details.')
 elif n==3:
  s+=t('A proposed headline',72,483,31,color=MUTED)+note(72,518,936,222)
  q,yy=para('Building OutSpoken | LinkedIn content and buyer conversations for Europe-based B2B AI SaaS founders.',110,586,40,39,53);s+=q
  for j,(a,b) in enumerate([('About','The problem, approach and work involved.'),('Featured','One useful example or next step.'),('Recent posts','A point of view the buyer can assess.')]):
   y=843+j*124;s+=t(a,72,y,41,True)+t(b,72,y+51,34)
  emit(id,title,s,'Headline, profile and posts should tell the same buyer story.')
 elif n==4:
  s+=t('Job',72,486,33,True)+t('Starter option',421,486,33,True)+ln(510)
  for j,(a,b) in enumerate([('Capture','Shared document'),('Plan','Simple content board'),('Review','Google Docs suggestions'),('Preview','Native / AuthoredUp'),('Research','Native / Sales Navigator'),('Follow through','Spreadsheet / HubSpot')]):
   y=577+j*96;s+=t(a,72,y,39,True)+t(b,421,y,36)+ln(y+32)
  emit(id,title,s,'Tool examples; choose by need, access, client effort and cost.')
 elif n==5:
  s+=note(72,450,936,389)+t('Illustrative message',108,513,30,color=MUTED)
  q,yy=para('Hi Maya — I saw you’re hiring your first customer-success lead. Would a checklist for turning onboarding questions into founder posts be useful?',108,575,39,39,52);s+=q
  for j,a in enumerate(['Checked context','Relevant problem','One useful next step']):s+=t(a,72,944+j*79,43,True)+underline(72,964+j*79,min(850,len(a)*19))
  emit(id,title,s,'Use the hiring detail only when it is real and relevant.')
 elif n==6:
  s+=t('Example incoming reply',72,479,30,color=MUTED)+t('“Send me details.”',72,542,48,True,True)
  s+=note(72,599,936,277)
  q,yy=para('Is the bigger problem finding ideas, or turning your knowledge into posts that sound like you?',108,669,42,36,56);s+=q
  for j,a in enumerate(['Answer the request','Ask what changes the recommendation','Share the relevant example','Agree the next step']):s+=t(f'{j+1}. {a}',72,957+j*66,35,True)
  emit(id,title,s,'Record the actual reply and next action in the contact record.')
 elif n==7:
  s+=note(72,466,936,160)+t('One substantial source',108,526,36,True)+t('Product decision, newsletter or useful research',108,581,33)
  for j,(a,b) in enumerate([('Explain','Why this decision?'),('Show','How does the workflow work?'),('Help choose','What should a buyer check?')]):s+=row(a,b,736+j*151)
  emit(id,title,s,'Inspired by Buffer’s Kevin Indig case, September 2026; not our result.')
 elif n==8:
  s+=t('55%',72,626,158,serif=True)
  q,yy=para('of US hidden decision-makers said thought leadership is one way they vet vendors.',438,503,38,25,51);s+=q
  for j,(a,b) in enumerate([('User','How does the task change?'),('Manager','What must the team adopt?'),('Finance / risk','What cost, evidence and responsibility?')]):s+=t(a,72,880+j*104,39,True)+t(b,390,880+j*104,34)
  emit(id,title,s,'2025 Edelman–LinkedIn survey, p.8. Self-reported US responses.')
 elif n==9:
  for j,(a,b) in enumerate([('Publish','Did the planned material go out?'),('Understand','What did relevant people ask?'),('Progress','What next step did they agree?'),('Change','What should we do differently?')]):s+=row(a,b,487+j*165)
  emit(id,title,s,'Native analytics for distribution; actual replies and CRM notes for conversations.')
 elif n==10:
  s+=t('Illustrative AI reporting trial',72,482,32,color=MUTED)
  s+=note(72,530,936,197)+t('A broad promise',110,585,31,color=MUTED)
  q,yy=para('Start your AI journey',110,653,49,31,60,True);s+=q
  s+=note(72,772,936,255)+t('A clear first action',110,827,31,color=MUTED)
  s+=f'<rect x="110" y="862" width="824" height="94" rx="9" fill="{INK}"/>'+t('Try a report with sample data',143,924,42,True,color=WHITE)
  q,yy=para('Next: show the answer and where its evidence comes from.',72,1124,39,41);s+=q
  emit(id,title,s,'A static example of a design choice, not a live product or conversion test.')
 elif n==11:
  for j,(label,value) in enumerate([('Distrust AI-tool accuracy',46),('Trust AI-tool accuracy',33)]):
   y=488+j*185;s+=t(label,72,y,36,True)+t(str(value)+'%',844,y,48,serif=True)
   s+=f'<rect x="72" y="{y+31}" width="936" height="32" fill="{LINE}"/><rect x="72" y="{y+31}" width="{936*value/100}" height="32" fill="{INK if j==0 else ACC}"/>'
  for j,a in enumerate(['Show the question and answer','Link the evidence','Name when a person must check']):s+=t(a,72,982+j*76,39,True)
  emit(id,title,s,'Stack Overflow 2025 · accuracy question · 33,244 responses · not buyer data.')
 elif n==12:
  for j,(a,b) in enumerate([('Product truth','Does this match what we deliver?'),('Founder voice','Is this the position and phrasing?'),('Reader action','Is this a useful, agreed next step?')]):s+=row(a,b,492+j*194)
  s+=t('Example edit:',72,1117,31,color=MUTED)
  q,yy=para('“Confirm the promised response time or remove it.”',72,1174,36,47);s+=q
  emit(id,title,s,'Name the reviewer and the decision needed to finish the post.')
 else:
  s+=note(72,462,936,278)+t('Voice',108,528,50,serif=True)
  q,yy=para('Strategy, voice guide, profile, posts, visuals, publishing and engagement.',108,591,40,39,53);s+=q
  s+=note(72,785,936,278)+t('Voice + Pipeline',108,851,50,serif=True)
  q,yy=para('Everything in Voice, plus researched outreach, qualification and meeting context.',108,914,40,39,53);s+=q
  s+=t('Book an intro call',72,1187,42,True)+underline(72,1208,344)
  emit(id,title,s,'For founders of Europe-based B2B AI SaaS companies.')

(R/'render-jobs.json').write_text(json.dumps(jobs,indent=2)+'\n')
assert len(jobs)==17 and sum(x['id']=='01-the-flow' for x in jobs)==4
print('Built17nativeeditablegraphics for14publications')
