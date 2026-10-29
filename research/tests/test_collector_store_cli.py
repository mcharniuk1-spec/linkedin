import asyncio,hashlib,json,os,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from research.collector.contracts import record,FetchResult,AccessSuspended,ConfigurationError
from research.collector.store import Store,canonical_url
from research.collector.cli import collect,update_run,load_config


def item(i='1',text=None,**kw):
    return record(source_id='fixture',external_id=i,source_url='https://example.test/'+i,text=text or ('Observed exact source facts for this public fixture. '+i)*2,content_type='static_page',permissions={'collection':True,'license':'test fixture'},raw=b'<main>source</main>',**kw)

class StoreTests(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.store=Store(self.tmp.name)
    def tearDown(self):self.store.close();self.tmp.cleanup()
    def test_full_required_set_and_invalid_hash(self):
        row=item()
        for field in ('source_id','external_id','source_url','author','published_at','collected_at','content_type','text','extracted_fields','content_hash','permissions','processing_status'):
            broken=dict(row);broken.pop(field)
            with self.subTest(field=field),self.assertRaises(ConfigurationError):self.store.ingest(broken)
        broken=dict(row);broken['content_hash']='bad'
        with self.assertRaises(ConfigurationError):self.store.ingest(broken)
        self.assertEqual(self.store.counts()['records'],0)
    def test_all_alias_modes_cross_source_and_immutable_raw(self):
        first=item(identity_aliases=['id:urn:li:share:11']);out=self.store.ingest(first)
        self.assertTrue(out['inserted']);self.assertEqual(self.store.raw_bytes(hashlib.sha256(first['_raw']).hexdigest()),first['_raw'])
        duplicates=[item('2',text='different text',identity_aliases=['id:urn:li:share:11']),item('3',text=first['text'].upper()),item()]
        for row in duplicates:
            row['source_id']='another'
            self.assertFalse(self.store.ingest(row)['inserted'])
        self.assertEqual(self.store.counts()['records'],1)
        self.assertEqual(self.store.pending()[0]['text'],first['text'])
    def test_identity_seed_only_and_skip_before_fetch(self):
        seed={'publications':[{'external_id':'urn:li:activity:123','aliases':['id:urn:li:activity:123','url:https://www.linkedin.com/posts/known_activity-123']}],'profiles':[{'url':'https://www.linkedin.com/company/fixture','name':'Fixture'}]}
        self.assertEqual(self.store.seed(seed),1);self.assertEqual(self.store.seed(seed),0)
        self.assertTrue(self.store.known_url('https://www.linkedin.com/posts/changed_activity-123?tracking=yes'))
        self.assertEqual(self.store.counts()['records'],0);self.assertEqual(self.store.counts()['profiles'],1)
    def test_source_dates_stay_holds_and_no_date_invention(self):
        for i,pub in enumerate((None,'bad','2099-01-01T00:00:00Z','2026-01-01T00:00:00Z')):
            self.store.ingest(item(str(i),published_at=pub))
        rows={x['external_id']:x for x in self.store.pending()}
        self.assertEqual(rows['0']['published_at'],None);self.assertEqual(rows['0']['publication_date_status'],'missing')
        self.assertEqual(rows['1']['publication_date_status'],'malformed_hold');self.assertEqual(rows['2']['publication_date_status'],'future_or_timezone_hold');self.assertEqual(rows['3']['publication_date_status'],'verified_source_date')
    def test_persistent_stop_requires_explicit_reason_and_logging_has_no_secrets(self):
        self.store.suspend('g','rate',99);self.store.close();self.store=Store(self.tmp.name)
        self.assertFalse(self.store.get_suspension('g')['automatic_resume'])
        with self.assertRaises(ConfigurationError):self.store.resume('g','')
        self.store.log_request('g',{'token':'SECRET','url':'https://secret','status_code':429,'event':'response'})
        payload=self.store.db.execute('select payload from requests').fetchone()[0]
        self.assertNotIn('SECRET',payload);self.assertNotIn('https://secret',payload)
        self.store.resume('g','Manual source access verified');self.assertIsNone(self.store.get_suspension('g'))
    def test_profile_is_metadata_only_and_export_has_original(self):
        row=item(author={'url':'https://example.test/author','name':'Fixture'})
        self.store.ingest(row)
        profile=json.loads(self.store.db.execute('select payload from profiles').fetchone()[0])
        self.assertFalse(profile['full_profile_retrieved']);self.assertEqual(profile['observation_scope'],'public_post_actor_only')
        out=Path(self.tmp.name)/'manual';receipt=self.store.export_pending(out)
        self.assertEqual(receipt['pending_records'],1)
        exported=json.loads((out/'records.ndjson').read_text());self.assertEqual((out/exported['raw_path']).read_bytes(),row['_raw'])
    def test_urls_do_not_trust_similar_domain_or_secret_query(self):
        self.assertEqual(canonical_url('https://notlinkedin.com/x?q=1'),'https://notlinkedin.com/x?q=1')
        self.assertEqual(canonical_url('https://uk.linkedin.com/posts/x/?tracking=1'),'https://www.linkedin.com/posts/x')
        with self.assertRaises(ConfigurationError):canonical_url('https://example.test/x?access_token=secret')

class CycleTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();root=Path(self.tmp.name);(root/'seed.json').write_text(json.dumps({'publications':[],'profiles':[]}))
        self.path=root/'config.json';self.cfg={'schema':'linkedin-hybrid-config/1','state_dir':'state','baseline_seed':'seed.json','max_new_records':2,'max_candidates':10,'max_database_bytes':24000000,'discovery':{'enabled':False},'sources':[{'source_id':'fixture','adapter':'http','enabled':True,'urls':['https://example.test/one','https://example.test/two'],'allowed_hosts':['example.test'],'permitted_methods':['GET'],'permissions':{'collection':True},'text_selector':'main'}]}
        self.path.write_text(json.dumps(self.cfg));self.calls=[]
    def tearDown(self):self.tmp.cleanup()
    def factory(self,spec,store):
        outer=self
        class Fake:
            async def fetch(self,url,*,headers=None):
                outer.calls.append(url)
                return FetchResult(url=url,body=('<main>'+url+' observed public fixture content</main>').encode(),status_code=200)
            async def aclose(self):pass
        return Fake()
    async def test_two_runs_do_not_refetch_and_manual_packet_no_analysis(self):
        first=await collect(self.path,transport_factory=self.factory)
        self.assertEqual(first['inserted'],2);self.assertFalse(first['analysis_executed']);self.assertFalse(first['refresh_executed'])
        second=await collect(self.path,transport_factory=self.factory)
        self.assertEqual(second['inserted'],0);self.assertEqual(len(self.calls),2)
        with patch('research.collector.writing_graph.build_writing_graph',return_value={'status':'fixture'}):
            packet=update_run(self.path)
        self.assertEqual(packet['pending_records'],2);self.assertEqual(packet['automatic_stages_executed'],[])
        self.assertTrue((Path(packet['output'])/'insights.csv').is_file())
    async def test_partial_success_saved_before_access_stop(self):
        base=self.factory
        def factory(spec,store):
            f=base(spec,store);original=f.fetch
            async def fetch(url,**kw):
                if url.endswith('two'):store.suspend('fixture','access');raise AccessSuspended('stopped')
                return await original(url,**kw)
            f.fetch=fetch;return f
        result=await collect(self.path,transport_factory=factory)
        self.assertEqual(result['inserted'],1);self.assertEqual(result['status'],'COMPLETE_WITH_SOURCE_HOLDS')
        s=Store(Path(self.tmp.name)/'state');self.assertEqual(s.counts()['records'],1);s.close()
    async def test_cap_and_discovery_failure_keep_explicit_status(self):
        self.cfg['max_new_records']=1;self.cfg['discovery']={'enabled':True};self.path.write_text(json.dumps(self.cfg))
        def bad(*args):raise AccessSuspended('quota')
        result=await collect(self.path,discover_fn=bad,transport_factory=self.factory)
        self.assertEqual(result['inserted'],1);self.assertTrue(result['errors']);self.assertEqual(len(self.calls),1)
    def test_duplicate_config_keys_rejected(self):
        self.path.write_text('{"schema":"linkedin-hybrid-config/1","schema":"bad"}')
        with self.assertRaises(ConfigurationError):load_config(self.path)

if __name__=='__main__':unittest.main()

class ResourceBoundaryTests(unittest.TestCase):
 def test_two_comments_and_parent_post_are_three_resources(self):
  with tempfile.TemporaryDirectory() as td:
   s=Store(td)
   try:
    for ext,typ,url in [('p','linkedin_post','https://www.linkedin.com/feed/update/urn:li:share:1'),('urn:li:comment:(urn:li:share:1,1)','linkedin_comment','https://www.linkedin.com/feed/update/urn:li:share:1#comment-urn:li:comment:(urn:li:share:1,1)'),('urn:li:comment:(urn:li:share:1,2)','linkedin_comment','https://www.linkedin.com/feed/update/urn:li:share:1#comment-urn:li:comment:(urn:li:share:1,2)')]:
     row=item(ext,text='Repeated long comment words that two different people can legitimately write.');row['source_url']=url;row['content_type']=typ
     self.assertTrue(s.ingest(row)['inserted'])
    self.assertEqual(s.counts()['records'],3)
   finally:s.close()
 def test_manual_output_private_only_and_restricts_existing_modes(self):
  with tempfile.TemporaryDirectory() as td:
   s=Store(Path(td)/'state');s.ingest(item())
   try:
    with self.assertRaises(ConfigurationError):s.export_pending(Path(td)/'shared')
    out=s.root/'manual';out.mkdir(mode=0o755);os.chmod(out,0o755);s.export_pending(out)
    self.assertEqual(out.stat().st_mode&0o777,0o700);self.assertEqual((out/'records.ndjson').stat().st_mode&0o777,0o600)
   finally:s.close()
