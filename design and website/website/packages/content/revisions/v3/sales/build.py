from pathlib import Path
import hashlib,json,re
A=Path('brand-library/packages/content');O=A/'revisions/v3/sales';entries=[]
for n in range(1,5):
 name=f'OS-S{n:03d}';src=A/'sales'/f'{name}.html';s=src.read_text();original=s
 s=s.replace('<meta charset="utf-8">','<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">')
 s=s.replace('/packages/assets/identity/concepts/02-folded-voice/lockup-primary.svg','../../../../assets/revisions/v4/identity/OS-LV4-004/lockup-gradient.svg').replace('/packages/assets/','../../../../assets/')
 s=s.replace('alt="Outspoken"','alt="OUTSPOKEN"')
 s=s.replace('OUTSPOKEN / STAGE 1 /','OUTSPOKEN / V3 /').replace('Candidate v1 · 19 October 2026 · Owner review pending · Full website work is Stage 2','V3 sales materials · 20 October 2026 · Candidate · Owner review pending')
 if n==4:s=s.replace('</section>','<footer>V3 sales materials · 20 October 2026 · Candidate · Owner review pending</footer></section>')
 s=s.replace('</style>','body{background:#F5F6F3}.page{background-color:#FCFCFA}.logo{height:auto;display:block;margin-block:20px 28px}h1,h2,h3,p,td{overflow-wrap:break-word}table{table-layout:fixed}td:first-child{width:56%}footer{color:#66738C}section>img{height:auto}@media(max-width:700px){.page{padding:24px;margin:12px}h1[style]{font-size:clamp(32px,9vw,46px)!important}.page p[style]{font-size:21px!important}td,th{overflow-wrap:anywhere}.page h3{font-size:23px}}@media print{footer{font-size:9pt}.page:last-child{break-after:auto}h1[style]{font-size:34pt!important}.page{break-inside:auto}.page p[style]{font-size:19pt!important}tr{break-inside:avoid}}'+'</style>')
 (O/f'{name}.html').write_text(s)
 refs=re.findall(r'(?:src|href)=["\']([^"\']+)',s)+re.findall(r"url\('([^']+)'\)",s)
 for ref in refs:assert(O/ref).exists(),ref
 # Exact approved copy preserved: only dated label/footer and image URL/formatting changes allowed.
 def bodytext(text):
  text=re.sub(r'<style>.*?</style>','',text,flags=re.S);text=re.sub(r'<footer>.*?</footer>','',text,flags=re.S);text=text.replace('OUTSPOKEN / STAGE 1 /','OUTSPOKEN / V3 /');return re.sub(r'<[^>]+>','',text)
 assert bodytext(original)==bodytext(s),(name,'copy changed')
 assert 'Full website work is Stage 2'not in s and 'lockup-primary.svg'not in s
 entries.append({'id':name,'source':str(src),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'html':str(O/f'{name}.html'),'html_sha256':hashlib.sha256(s.encode()).hexdigest(),'copy_invariant_pass':True,'relative_references':refs,'fictional_disclosure_preserved':'Illustrative example — not a customer testimonial'in s if n==4 else None})
(O/'manifest.json').write_text(json.dumps({'revision':'v3','date':'2026-10-20','identity_revision':'v4','lead_identity':'OS-LV4-004 Say It; uppercase OUTSPOKEN gradient primary','state':'candidate_owner_review_pending','entries':entries},indent=2))
print('4 HTML copies created; body-copy invariants and all relative references pass')
