#!/usr/bin/env python3
"""Verify the entire two-package public source snapshot. No network or writes."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
EXCLUDED={'node_modules','dist','storybook-static','__pycache__','.cache','.vite'}
def pairs(items):
 out={}
 for k,v in items:
  if k in out:raise ValueError('Duplicate JSON key '+k)
  out[k]=v
 return out
def read(p):return json.loads(p.read_text(),object_pairs_hook=pairs)
def check(folder):
 root=ROOT/folder;m=read(root/'release-manifest.json')
 assert m['status']=='source_snapshot_verified' and m['publication_authority']=='owner_requested_current_source_git_sync'
 assert m['owner_accepted'] is False
 actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and not any(x in EXCLUDED for x in p.relative_to(root).parts) and p.name!='release-manifest.json'}
 expected=[x['path']for x in m['files']]
 assert len(expected)==len(set(expected)),folder+' duplicate manifest paths'
 assert set(expected)==actual,(folder,'missing',sorted(set(expected)-actual),'extra',sorted(actual-set(expected)))
 for x in m['files']:
  assert not Path(x['path']).is_absolute() and '..' not in Path(x['path']).parts
  p=root/x['path'];assert not p.is_symlink();b=p.read_bytes()
  assert len(b)==x['bytes'] and hashlib.sha256(b).hexdigest()==x['sha256'],str(p)
  if p.suffix=='.json':read(p)
 rights=m['rights_ledger'];by={x['path']:x for x in rights};assert len(by)==len(rights),'duplicate rights'
 for x in rights:
  assert x['rights_state'] in {'owned','licensed','permission_verified'},x
  f=next((f for f in m['files']if f['path']==x['path']),None);assert f and f['sha256']==x['sha256'],x
 assets={p for p in actual if p.startswith('assets/')and p!='assets/README.md'}
 assert assets<=set(by),('unregistered assets',assets-set(by))
 blocked={digest for x in m.get('exclusions',[])if isinstance(x,dict)for digest in x.get('recorded_hashes',{}).values()}
 assert not any(x['sha256']in blocked for x in m['files']), 'Excluded source bytes reappear under an alias'
 return {'files':len(expected),'registered_rights':len(rights),'assets':len(assets),'owner_accepted':False}
def main():
 results={folder:check(folder)for folder in ['design and website','editorial']}
 blocked={h for folder in ['design and website','editorial']for x in read(ROOT/folder/'release-manifest.json').get('exclusions',[])if isinstance(x,dict)for h in x.get('recorded_hashes',{}).values()}
 for p in ROOT.rglob('*'):
  if not p.is_file()or any(x in EXCLUDED|{'.git'}for x in p.relative_to(ROOT).parts):continue
  assert hashlib.sha256(p.read_bytes()).hexdigest()not in blocked,('Excluded bytes anywhere in public tree',p.relative_to(ROOT))
 app=ROOT/'design and website/website';package=read(app/'package.json');lock=read(app/'package-lock.json');assert package['name']==lock['name']==lock['packages']['']['name']
 for key in ['dependencies','devDependencies','engines']:assert package[key]==lock['packages'][''][key],key
 print(json.dumps({'status':'PASS','packages':results,'lockfile_root_matches':True},indent=2))
if __name__=='__main__':main()
