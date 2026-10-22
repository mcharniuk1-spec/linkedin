from pathlib import Path
import json,tempfile,unittest,sys,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parent));import public_safety_scan as safety
class PublicBoundary(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.r=Path(self.tmp.name)
 def tearDown(self):self.tmp.cleanup()
 def write(self,p,b):
  f=self.r/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(b if isinstance(b,bytes) else b.encode());return f
 def reasons(self):return {p['problem'] for p in safety.scan(self.r)['problems']}
 def test_public_method_passes(self):self.write('README.md','Source public counters remain observations. No schedule.');self.assertEqual(safety.scan(self.r)['status'],'PASS')
 def test_rejects_private_machine_reference(self):self.write('data.json',json.dumps({'source':'/'+'Users/'+'example-owner/private-corpus'}));self.assertIn('private_machine_path',self.reasons())
 def test_rejects_token_like_secret(self):self.write('settings.py','token = '+repr('ghp_'+'X'*36));self.assertIn('credential_or_private_key_pattern',self.reasons())
 def test_rejects_private_workbook(self):self.write('enquiries.xlsx',b'privatefixture');self.assertIn('forbidden_private_file_type',self.reasons())
 def test_checks_duplicate_json_keys(self):self.write('facts.json','{"x":1,"x":2}');self.assertIn('invalid_json_or_duplicate_key',self.reasons())
 def test_rejects_unreviewed_binary(self):self.write('design and website/assets/scene.png',b'\x89PNG\x00\xff');self.assertIn('unreviewed_binary',self.reasons())
 def test_accepts_only_exact_final_asset_rights_hash(self):
  f=self.write('design and website/assets/scene.png',b'\x89PNG\x00\xff');h=hashlib.sha256(f.read_bytes()).hexdigest();rel=f.relative_to(self.r).as_posix();m={'status':'finalized','files':[{'path':rel,'sha256':h}],'rights_ledger':[{'path':rel,'sha256':h,'rights_state':'owned'}]};self.write('design and website/release-manifest.json',json.dumps(m));self.assertEqual(safety.scan(self.r)['status'],'PASS');m['rights_ledger'][0]['sha256']='0'*64;self.write('design and website/release-manifest.json',json.dumps(m));self.assertIn('unreviewed_binary',self.reasons())
 def test_current_snapshot_requires_authority_and_exact_rights(self):
  for folder in ['design and website','editorial']:
   with self.subTest(folder=folder):
    f=self.write(folder+'/assets/scene.png',b'\x89PNG\x00\xff');h=hashlib.sha256(f.read_bytes()).hexdigest()
    m={'status':'source_snapshot_verified','files':[{'path':'assets/scene.png','sha256':h}],'rights_ledger':[{'path':'assets/scene.png','sha256':h,'rights_state':'owned'}]}
    self.write(folder+'/release-manifest.json',json.dumps(m));self.assertIn('unreviewed_binary',self.reasons())
    m['publication_authority']='owner_requested_current_source_git_sync';self.write(folder+'/release-manifest.json',json.dumps(m));self.assertEqual(safety.scan(self.r)['status'],'PASS')
    m['rights_ledger'][0]['rights_state']='unresolved';self.write(folder+'/release-manifest.json',json.dumps(m));self.assertIn('unreviewed_binary',self.reasons())
    m['rights_ledger'][0]['rights_state']='owned';m['files'].append(m['files'][0]);self.write(folder+'/release-manifest.json',json.dumps(m));self.assertIn('unreviewed_binary',self.reasons())
    f.unlink();(self.r/folder/'release-manifest.json').unlink()
 def test_snapshot_rejects_incomplete_or_conflicting_ledgers(self):
  f=self.write('editorial/assets/scene.png',b'\x89PNG\x00\xff');h=hashlib.sha256(f.read_bytes()).hexdigest()
  valid={'status':'source_snapshot_verified','publication_authority':'owner_requested_current_source_git_sync','files':[{'path':'assets/scene.png','sha256':h}],'rights_ledger':[{'path':'assets/scene.png','sha256':h,'rights_state':'licensed'}]}
  for change in ['duplicate_rights','wrong_file_hash','no_rights','wrong_status','wrong_authority']:
   with self.subTest(change=change):
    m=json.loads(json.dumps(valid))
    if change=='duplicate_rights':m['rights_ledger'].append(m['rights_ledger'][0])
    elif change=='wrong_file_hash':m['files'][0]['sha256']='0'*64
    elif change=='no_rights':m['rights_ledger']=[]
    elif change=='wrong_status':m['status']='draft'
    else:m['publication_authority']='unverified'
    self.write('editorial/release-manifest.json',json.dumps(m));self.assertIn('unreviewed_binary',self.reasons())
 def test_rejects_directory_and_broken_symlinks(self):
  (self.r/'directory').mkdir();(self.r/'directory-link').symlink_to(self.r/'directory',target_is_directory=True);(self.r/'broken-link').symlink_to(self.r/'missing')
  problems=safety.scan(self.r)['problems'];self.assertEqual({x['file'] for x in problems if x['problem']=='symlink_not_allowed'},{'directory-link','broken-link'})
if __name__=='__main__':unittest.main()
