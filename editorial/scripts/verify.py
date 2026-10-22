#!/usr/bin/env python3
"""Verify this portable review export without accounts, network or dependencies."""
from pathlib import Path
from collections import Counter
import hashlib,html,json,re,sys
ROOT=Path(__file__).resolve().parents[1]
def pairs(xs):
 d={}
 for k,v in xs:
  if k in d:raise ValueError('duplicate JSON key: '+k)
  d[k]=v
 return d
def readj(p):return json.loads(p.read_text(),object_pairs_hook=pairs)
def digest(b):return hashlib.sha256(b).hexdigest()
def main():
 m=readj(ROOT/'release-manifest.json');actual={p.relative_to(ROOT).as_posix()for p in ROOT.rglob('*')if p.is_file()and p.name!='release-manifest.json'and'__pycache__'not in p.parts};expected=[x['path']for x in m['files']]
 assert len(expected)==len(set(expected))and actual==set(expected),'file coverage mismatch'
 checks=1
 for x in m['files']:
  b=(ROOT/x['path']).read_bytes();assert len(b)==x['bytes']and digest(b)==x['sha256'],x['path'];checks+=1
 for p in ROOT.rglob('*.json'):readj(p);checks+=1
 posts=readj(ROOT/'copy/publications.json')['publications'];assert[p['id']for p in posts]==[f'P{i:02}'for i in range(1,21)];assert Counter(p['format']for p in posts)==Counter({'image':13,'video':2,'text-only':5});checks+=2
 fmap={p['id']:p for p in readj(ROOT/'figma/FRAME-MAP.json')['posts']};assert set(fmap)=={p['id']for p in posts};checks+=1
 for p in posts:
  h=digest(p['body'].encode());assert h==m['body_hashes'][p['id']]==fmap[p['id']]['bodySha256'];checks+=1
 page=(ROOT/'index.html').read_text()
 for link in re.findall(r'(?:src|href)=["\']([^"\']+)',page):
  if link.startswith(('http:','https:','#','mailto:','data:')):continue
  assert(ROOT/link).is_file(),link;checks+=1
  # A link points only within this package.
  assert(ROOT/link).resolve().is_relative_to(ROOT.resolve()),link
 for pid in['P14','P15']:
  script=readj(ROOT/f'videos/scripts/{pid}.json');assert len(script['shots'])==5;checks+=1
  for ext in['srt','vtt']:
   s=(ROOT/f'videos/scripts/{pid}.{ext}').read_text();assert s.count(' --> ')==5
   words=' '.join(x for x in s.splitlines()if x and not x.isdigit()and' --> 'not in x and x!='WEBVTT');tokens=lambda x:re.findall(r'\w+',x.casefold());assert tokens(words)==tokens(script['spoken_script']);checks+=1
 for x in m['rights_ledger']:
  assert x['path']in actual and digest((ROOT/x['path']).read_bytes())==x['sha256'];assert x['rights_state']in['owned','licensed','permission_verified'];checks+=1
  if 'license_path'in x:assert(ROOT/x['license_path']).is_file()
 print(json.dumps({'status':'PASS','checks':checks,'files':len(expected),'publications':20,'owner_accepted':False,'limits':'Structural/checksum verification. Artistic/author acceptance and social publication remain separate.'},indent=2))
if __name__=='__main__':
 try:main()
 except Exception as e:print(json.dumps({'status':'FAIL','error':str(e)}));sys.exit(1)
