#!/usr/bin/env python3
"""Scan the complete eligible public tree, including SQLite payloads. No network."""
from pathlib import Path
import argparse,hashlib,json,re,sqlite3,sys
ROOT=Path(__file__).resolve().parents[1]
EXCLUDE_PARTS={'.git','__pycache__','node_modules','.venv','work','.pytest_cache'}
PRIVATE_PATHS=[re.compile('/'+'Users/'),re.compile('/'+'private/(?:tmp|var)/'),re.compile('/'+'opt/homebrew/'),re.compile(r'[A-Za-z]:\\Users\\'),re.compile('/'+'home/(?!runner(?:/|$)|example(?:/|$))')]
SECRETS=[re.compile(r'gh[pousr]_[A-Za-z0-9]{30,}'),re.compile(r'github_pat_[A-Za-z0-9_]{30,}'),re.compile(r'(?<![A-Za-z0-9_-])sk-[A-Za-z0-9_-]{24,}'),re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),re.compile(r'exaApiKey=(?!YOUR_|example|placeholder)[A-Za-z0-9]{16,}')]
FORBIDDEN_NAMES={'.env','.env.local','cookies.json','cookies.txt','credentials.json','id_rsa','id_ed25519','ld.yaml','ld.yml','tokens.enc','oauth-state.enc','collector-state.key','authorize.html'}
FORBIDDEN_SUFFIXES={'.xlsx','.xlsm','.xls','.p12','.pem','.key','.enc'}

def pairs(xs):
 d={}
 for k,v in xs:
  if k in d:raise ValueError('duplicate JSON key '+k)
  d[k]=v
 return d

def text_problems(text):
 out=[]
 if any(p.search(text) for p in PRIVATE_PATHS):out.append('private_machine_path')
 if any(p.search(text) for p in SECRETS):out.append('credential_or_private_key_pattern')
 return out

def approved_asset(root,rel,digest):
 # A Git source snapshot has its own publication authority. It does not imply
 # artistic acceptance. Both states still require exact per-file rights/hash.
 if not rel.parts or rel.parts[0] not in {'design and website','editorial'}:return False
 package=root/rel.parts[0]
 if len(rel.parts)<3 or rel.parts[1]!='assets':return False
 manifest=package/'release-manifest.json'
 if not manifest.is_file():return False
 try:m=json.loads(manifest.read_text(),object_pairs_hook=pairs)
 except (ValueError,OSError):return False
 if m.get('status') not in {'finalized','source_snapshot_verified'}:return False
 if m.get('status')=='source_snapshot_verified' and m.get('publication_authority')!='owner_requested_current_source_git_sync':return False
 candidates={rel.as_posix(),Path(*rel.parts[1:]).as_posix()}
 files=[x for x in m.get('files',[]) if x.get('path') in candidates]
 rights=[x for x in m.get('rights_ledger',[]) if x.get('path') in candidates]
 return len(files)==len(rights)==1 and files[0].get('sha256')==digest and rights[0].get('sha256')==digest and rights[0].get('rights_state') in {'owned','licensed','permission_verified'}

def scan(root=ROOT):
 problems=[];seen=[];jsons=0;dbs=0
 for p in sorted(root.rglob('*')):
  rel=p.relative_to(root)
  if any(x in EXCLUDE_PARTS for x in rel.parts):continue
  if p.is_symlink():problems.append({'file':rel.as_posix(),'problem':'symlink_not_allowed'});continue
  if not p.is_file():continue
  if p.name in FORBIDDEN_NAMES or p.suffix.lower() in FORBIDDEN_SUFFIXES:problems.append({'file':rel.as_posix(),'problem':'forbidden_private_file_type'})
  b=p.read_bytes();seen.append({'file':rel.as_posix(),'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)})
  if p.suffix=='.sqlite':
   if rel.as_posix()!='datasets/current/derived.sqlite':problems.append({'file':rel.as_posix(),'problem':'unexpected_database'});continue
   c=sqlite3.connect('file:'+str(p)+'?mode=ro',uri=True)
   try:
    assert c.execute('pragma integrity_check').fetchone()[0]=='ok'
    for (name,) in c.execute("select name from sqlite_master where type='table'"):
     assert re.fullmatch('[A-Za-z_]+',name)
     for row in c.execute('select * from '+name):
      for v in row:
       if isinstance(v,str):
        for issue in text_problems(v):problems.append({'file':rel.as_posix(),'problem':issue,'table':name})
    dbs+=1
   finally:c.close()
   continue
  try:text=b.decode('utf-8')
  except UnicodeDecodeError:
   approved=approved_asset(root,rel,seen[-1]['sha256'])
   if not approved:problems.append({'file':rel.as_posix(),'problem':'unreviewed_binary'})
   continue
  for issue in text_problems(text):problems.append({'file':rel.as_posix(),'problem':issue})
  if p.suffix=='.json':
   try:json.loads(text,object_pairs_hook=pairs);jsons+=1
   except Exception as e:problems.append({'file':rel.as_posix(),'problem':'invalid_json_or_duplicate_key','detail':str(e)})
  if rel.parts[:2]==('datasets','current') and p.suffix not in {'.md','.html','.json','.csv'}:problems.append({'file':rel.as_posix(),'problem':'unexpected_public_dataset_file'})
 return {'status':'PASS' if not problems else 'FAIL','files_checked':len(seen),'json_files_checked':jsons,'sqlite_files_checked':dbs,'problems':problems,'tree_sha256':hashlib.sha256(json.dumps(seen,sort_keys=True).encode()).hexdigest(),'limits':'Static boundary checks; source rights, factual accuracy, owner acceptance and actual runtime integrations require their separate evidence.'}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=ROOT);a=ap.parse_args();r=scan(a.root);print(json.dumps(r,indent=2));return 0 if r['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
