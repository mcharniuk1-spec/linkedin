from pathlib import Path
import hashlib,json,tempfile,unittest
import verify_release as release

class ReleaseExclusions(unittest.TestCase):
 def test_excluded_bytes_are_rejected_under_a_new_filename(self):
  with tempfile.TemporaryDirectory()as tmp:
   previous=release.ROOT;release.ROOT=Path(tmp)
   try:
    root=release.ROOT/'design and website';p=root/'assets/renamed-scene.bin';p.parent.mkdir(parents=True);data=b'owned-looking-alias';p.write_bytes(data);h=hashlib.sha256(data).hexdigest()
    m={'status':'source_snapshot_verified','publication_authority':'owner_requested_current_source_git_sync','owner_accepted':False,'files':[{'path':'assets/renamed-scene.bin','bytes':len(data),'sha256':h}],'rights_ledger':[{'path':'assets/renamed-scene.bin','sha256':h,'rights_state':'owned'}]}
    manifest=root/'release-manifest.json';manifest.write_text(json.dumps(m));self.assertEqual(release.check('design and website')['files'],1)
    m['exclusions']=[{'source':'unrelated-original-name.png','recorded_hashes':{'source':h}}];manifest.write_text(json.dumps(m))
    with self.assertRaisesRegex(AssertionError,'Excluded source bytes'):release.check('design and website')
   finally:release.ROOT=previous

if __name__=='__main__':unittest.main()
