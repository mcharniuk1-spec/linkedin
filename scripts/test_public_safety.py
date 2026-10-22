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
if __name__=='__main__':unittest.main()
