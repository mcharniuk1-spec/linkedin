#!/usr/bin/env python3
"""Verify the finite writing-skill/publication export contract. No collection."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import struct
import xml.etree.ElementTree as ET

IDS=['01-the-reason','02-what-we-actually-saw','03-the-interview','04-positioning','05-proof','06-product-to-buyer','07-two-voices','08-visuals','09-measure','10-the-delivery']
SKILLS={'linkedin-publication-architecture':['SKILL.md','references/composition-contract.md','references/interest-and-format.md'],'linkedin-reference-pattern-review':['SKILL.md','references/evidence-contract.md']}
PKG='publications/20261110-skills-v2'
REPORT='reports/20261110-skills-publications'

def pairs(items):
    out={}
    for k,v in items:
        if k in out:raise ValueError('Duplicate JSON key: '+k)
        out[k]=v
    return out

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]);a=ap.parse_args();root=a.root.resolve();p=root/PKG;report=root/REPORT;checks=[]
    def check(name,ok,detail=None):checks.append({'check':name,'status':'PASS' if ok else 'FAIL','detail':detail})
    def read(path):return json.loads(path.read_text(),object_pairs_hook=pairs)
    content=read(p/'content.json');apps=read(p/'skill-applications.json')['posts'];manifest=read(p/'release-manifest.json');layout=read(p/'assets/manifest.json')
    check('Exact ten concept identities',[x['id'] for x in content]==[x['id'] for x in apps]==IDS)
    check('First five carousels and five singles',[x['format'] for x in content]==['carousel']*5+['single']*5)
    check('All ten complete skill application records',all(x['skills_applied']==list(SKILLS) and x['remaining_holds'] and x['status']=='draft_ready_for_author_review' for x in apps))
    check('All ten caption hashes match applied revision',all(hashlib.sha256(x['caption'].encode()).hexdigest()==y['caption_sha256'] for x,y in zip(content,apps)))
    check('Required exact CTA in both offer directions',all(x.get('cta')=='Book an intro call' for v in content[-1]['variants'].values() for x in v) and content[-1]['caption'].endswith('Book an intro call'))
    check('No first-person client or benchmark invented in proof caption','hypothetical' in content[4]['caption'].lower() and 'No product execution, benchmark or customer result' in content[4]['caption'])
    check('All ten proof panels preserve hypothetical no-test context',all('Hypothetical' in x['context'] and 'no product test reported' in x['context'] for v in content[4]['variants'].values() for x in v))
    check('Unsupported old survey figure absent from caption/panels','73%' not in content[4]['caption'] and all('73%' not in x['headline']+x['body']+x['context'] for v in content[4]['variants'].values() for x in v))
    check('Research sample and current metric date literal','279' in content[1]['caption'] and '61' in content[1]['caption'] and '276' in content[1]['caption'] and '107.5' in content[1]['caption'] and '256' in content[1]['caption'] and '36.5' in content[1]['caption'] and all('22 Oct 2026' in x['context'] for v in content[1]['variants'].values() for x in v))
    check('Positioning four-check promise paid off',all(x['variants'][v][0]['diagram']==['BUYER','TASK','ALTERNATIVE','EVIDENCE'] and 'alternative' in x['variants'][v][3]['headline'].lower() for x in [content[3]] for v in ['graphic','people']))
    check('Two visual directions have identical claim text',all(x['variants']['graphic']==x['variants']['people'] for x in content))
    check('Caption lengths remain below documented post maximum',all(0<len(x['caption'])<=3000 for x in content))
    paths=[];source_svg=[];pdfs=[];captions=[]
    for i,x in enumerate(content):
        n=5 if i<5 else 1
        for v in ['graphic','people']:
            check('Complete panel copy: '+x['id']+':'+v,len(x['variants'][v])==n and all(all(z.get(k) for k in ['headline','body','diagram','diagram_type','context']) for z in x['variants'][v]))
            paths += [p/'assets'/x['id']/(v+'-'+str(k).zfill(2)+'.png') for k in range(1,n+1)]
            source_svg += [p/'assets/source-svg'/(str(i+1).zfill(2)+'-'+v+'-'+str(k).zfill(2)+'.svg') for k in range(1,n+1)]
            if n==5:pdfs.append(p/'assets'/x['id']/(v+'-carousel.pdf'))
        captions.append(p/'assets'/x['id']/'caption.txt')
    actual_png=set((p/'assets').rglob('*.png'));actual_svg=set((p/'assets').rglob('*.svg'));actual_pdf=set((p/'assets').rglob('*.pdf'))
    check('Exact sixty PNG export set',len(paths)==len(set(paths))==60 and set(paths)==actual_png)
    check('Exact sixty native SVG source set',len(source_svg)==len(set(source_svg))==60 and set(source_svg)==actual_svg)
    check('Exact ten PDF set',len(pdfs)==10 and set(pdfs)==actual_pdf)
    check('Every PNG is native 1080x1350',all(q.read_bytes()[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',q.read_bytes()[16:24])==(1080,1350) for q in paths))
    check('Sixty distinct rendered PNGs',len({digest(q) for q in paths})==60)
    check('Every PDF has expected binary header',all(q.read_bytes().startswith(b'%PDF-') for q in pdfs))
    check('Exact ten caption text copies',all(q.read_text()==x['caption']+'\n' for q,x in zip(captions,content)))
    ns={'s':'http://www.w3.org/2000/svg'};bad=[];people_labels=0;external=[]
    asset_root=(root/'publications/20261105-evidence-v1/assets').resolve()
    for q in source_svg:
        text=q.read_text();doc=ET.fromstring(text)
        if doc.attrib.get('viewBox')!='0 0 1080 1350':bad.append(q.name)
        if '-people-' in q.name:people_labels+=('ILLUSTRATIVE SCENE' in text)
        for im in doc.findall('.//s:image',ns):
            href=im.attrib.get('href') or im.attrib.get('{http://www.w3.org/1999/xlink}href','');target=(q.parent/href).resolve()
            if '://' in href or href.startswith('data:') or not target.is_relative_to(asset_root) or not target.is_file():external.append(q.name+':'+href)
        if q.name.startswith(('08-','09-')):
            check('Stacked mapping rows: '+q.name,'INTERACTIONS' in text and 'BUYING INTENT' in text if q.name.startswith('09-') else 'COMPARISON' in text and 'ORDER' in text)
    check('Every SVG parses with exact canvas',not bad,bad)
    check('All thirty people SVGs disclose illustration',people_labels==30)
    check('Shared image references stay portable and confined',not external,external)
    html=(p/'assets/index.html').read_text();check('Gallery avoids object serialization artifacts','[object Object]' not in html and all(x['id'] in html for x in content))
    check('Layout content identity matches canonical copy',layout['source_content_sha256']==digest(p/'content.json')==manifest['content_sha256'])
    actual={q.relative_to(p).as_posix():q for q in (p/'assets').rglob('*') if q.is_file()};listed={x['path']:x for x in manifest['files']};rights={x['path']:x for x in manifest['rights_ledger']}
    check('Release file and rights ledgers cover every exact asset',len(listed)==len(manifest['files'])==len(rights)==len(manifest['rights_ledger'])==len(actual) and set(actual)==set(listed)==set(rights))
    check('Every asset hash and rights assertion reconciles',all(digest(q)==listed[k]['sha256']==rights[k]['sha256'] and q.stat().st_size==listed[k]['bytes'] and rights[k]['rights_state'] in ['owned','licensed'] for k,q in actual.items()))
    check('Source Git authority is distinct from author/social approval',manifest['publication_authority']=='owner_requested_current_source_git_sync' and manifest['status']=='source_snapshot_verified' and manifest['owner_accepted'] is False and manifest['social_published'] is False)
    for name,expected in SKILLS.items():
        folder=root/'skills'/name;actual={q.relative_to(folder).as_posix() for q in folder.rglob('*') if q.is_file()}
        check('Exact owned skill file set: '+name,actual==set(expected))
        text=(folder/'SKILL.md').read_text();check('Skill frontmatter and internal references: '+name,('name: '+name) in text and 'version: 1.0.0' in text and all((folder/z).exists() for z in re.findall(r'\]\((references/[^)]+)\)',text)))
    installed=read(report/'skill-installation.json');check('Both project roots have exact static scan readback receipts',len(installed['receipts'])==4 and all(x['recommendation']=='SAFE' and x['coverage_percent']==100 and x['scanner_version']=='2.9.6' and x['llm_scan'] is False and x['semantic_limitations'] for x in installed['receipts']))
    order=read(report/'pdf-order-verification.json');check('All fifty actual PDF page identities/order passed',order['status']=='PASS' and order['pages']==50 and order['pdfs']==10 and len(order['results'])==50 and all(x['pass'] and x['nearest']==x['expected'] and x['mean_absolute_error']<1.5 for x in order['results']))
    source=read(report/'evidence-checks.json');check('Saved-evidence deterministic checks passed',source.get('status')=='PASS')
    result={'schema':'outspoken-skills-publications-verification/1','status':'PASS' if all(x['status']=='PASS' for x in checks) else 'FAIL','check_count':len(checks),'checks':checks,'counts':{'posts':10,'directions':20,'pngs':60,'svgs':60,'pdfs':10,'pdf_pages':50,'captions':10,'skills':2,'skill_source_files':5},'limits':['Finite structural/provenance/export checks do not establish founder approval, writing quality or audience outcomes.','Behavioral test accounting and independent source/visual review are separate records.','Platform maximum is not an optimal caption length.']}
    report.mkdir(parents=True,exist_ok=True);(report/'verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':result['status'],'checks':len(checks),'failures':[x for x in checks if x['status']=='FAIL']},indent=2));return 0 if result['status']=='PASS' else 1

if __name__=='__main__':raise SystemExit(main())
