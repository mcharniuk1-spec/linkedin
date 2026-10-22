"""Portable runtime checks use temporary synthetic sources; no network or models."""
from pathlib import Path
from datetime import datetime,timezone
from unittest.mock import patch
import json,os,sys,tempfile,unittest
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'pipeline'))
from runtime_config import load_config,tool_command
import cycle,normalizer

class PortableConfig(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='portable-config-');self.root=Path(self.tmp.name).resolve()
        self.config=self.root/'settings/config.json';self.config.parent.mkdir()
        self.value=json.loads((HERE.parent/'pipeline/config.json').read_text())
        self.value.update(run_root='../output',corpus_posts=['../corpus/data/posts.ndjson'],corpus_snapshots=['../previous/data/snapshots.json'])
        self.value['transcript_qa']['corpus_datasets']=['../previous/data/dataset.json']
        self.config.write_text(json.dumps(self.value))
    def tearDown(self):self.tmp.cleanup()
    def test_paths_resolve_from_config_directory_not_calling_cwd(self):
        old=Path.cwd()
        try:
            os.chdir(self.root)
            c=load_config(self.config)
        finally:os.chdir(old)
        self.assertEqual(c['run_root'],str(self.root/'output'))
        self.assertEqual(c['corpus_posts'],[str(self.root/'corpus/data/posts.ndjson')])
        self.assertEqual(c['corpus_snapshots'],[str(self.root/'previous/data/snapshots.json')])
        self.assertEqual(c['transcript_qa']['corpus_datasets'],[str(self.root/'previous/data/dataset.json')])
    def test_local_environment_model_and_python_overrides(self):
        with patch.dict(os.environ,{'LINKEDIN_WHISPER_MODEL':'../models/cached.pt','LINKEDIN_WHISPER_PYTHON':'python3'}):
            c=load_config(self.config)
        self.assertEqual(c['whisper']['model'],str(self.root/'models/cached.pt'))
        self.assertEqual(c['whisper']['python'],'python3')
        self.assertFalse(c['whisper']['allow_download'])
    def test_duplicate_config_keys_rejected_by_cycle_loader(self):
        self.config.write_text('{"run_root":"a","run_root":"b"}')
        with self.assertRaisesRegex(ValueError,'duplicate JSON key'):
            cycle.Cycle(self.config)
    def test_tool_uses_existing_path_binary(self):
        tools=self.root/'tools';tools.mkdir();f=tools/'fixture-tool';f.write_text('#!/bin/sh\nexit 0\n');f.chmod(0o700)
        c=load_config(self.config);c['tools']={'ffprobe':'../tools/fixture-tool'}
        self.assertEqual(tool_command(c,'ffprobe'),str(f))
    def test_missing_tool_fails_without_installing(self):
        c=load_config(self.config);c['tools']={'ffprobe':'unavailable-synthetic-binary-001'}
        with self.assertRaisesRegex(RuntimeError,'No installation attempted'):
            tool_command(c,'ffprobe')
    def test_relative_corpus_raw_source_is_run_relative(self):
        corpus=self.root/'corpus';(corpus/'data').mkdir(parents=True)
        (corpus/'raw').mkdir();raw=corpus/'raw/source.html'
        raw.write_bytes((HERE/'fixtures/cycle/legacy-1.html').read_bytes())
        u='https://www.linkedin.com/posts/synthetic-author-1_synthetic-activity-7000000000000000001-AbCd'
        p=normalizer.parse_post(raw,u,datetime.now(timezone.utc).isoformat());p['source']['raw_path']='raw/source.html'
        (corpus/'data/posts.ndjson').write_text(json.dumps(p)+'\n')
        self.value['corpus_snapshots']=[];self.config.write_text(json.dumps(self.value))
        c=cycle.Cycle(self.config)
        try:
            self.assertEqual(c.import_baseline(),{'imported_or_verified':1,'prior_reobservations':0,'errors':0})
            self.assertEqual(c.requests_made,0)
        finally:c.db.close();c.lockfile.close()
    def test_relative_reobservation_source_resolves_from_prior_run(self):
        corpus=self.root/'corpus';(corpus/'data').mkdir(parents=True);(corpus/'raw').mkdir()
        raw=corpus/'raw/source.html';raw.write_bytes((HERE/'fixtures/cycle/legacy-1.html').read_bytes())
        u='https://www.linkedin.com/posts/synthetic-author-1_synthetic-activity-7000000000000000001-AbCd'
        p=normalizer.parse_post(raw,u,'2026-10-20T08:00:00+00:00');p['source']['raw_path']='raw/source.html'
        (corpus/'data/posts.ndjson').write_text(json.dumps(p)+'\n')
        previous=self.root/'previous';(previous/'data').mkdir(parents=True);(previous/'raw').mkdir()
        (previous/'raw/later.html').write_bytes(raw.read_bytes())
        snap={'capture_kind':'reobservation','post_id':p['id'],'url':u,'captured_at':'2026-10-20T16:00:00+00:00','raw_path':'raw/later.html','raw_sha256':p['source']['sha256'],'source_run':'synthetic-prior','parser_version':normalizer.VERSION}
        (previous/'data/snapshots.json').write_text(json.dumps([snap]))
        c=cycle.Cycle(self.config)
        try:
            self.assertEqual(c.import_baseline(),{'imported_or_verified':1,'prior_reobservations':1,'errors':0})
            self.assertEqual(c.requests_made,0)
            self.assertEqual(c.db.execute('select count(*) from captures').fetchone()[0],2)
        finally:c.db.close();c.lockfile.close()
    def test_public_sample_has_no_collection_or_schedule_enabled(self):
        c=json.loads((HERE.parent/'pipeline/config.json').read_text())
        self.assertEqual(c['discovery']['queries'],[])
        self.assertEqual(c['collection_approval']['approved_author_paths'],[])
        self.assertFalse(c['supervisor']['schedule_active'])
        self.assertIsNone(c['supervisor']['external_wake_adapter'])
        self.assertFalse(c['whisper']['allow_download'])

if __name__=='__main__':unittest.main()
