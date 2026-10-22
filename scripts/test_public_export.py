"""Self-contained public-projection tests. Invented records only; no network/model calls."""
from pathlib import Path
from unittest import mock
import csv,hashlib,json,re,shutil,sqlite3,subprocess,sys,tempfile,unittest
sys.path.insert(0,str(Path(__file__).resolve().parent))
import export_public_dataset as exp


def fixture():
    posts=[];sem=[];perf=[];snap=[]
    for i in (1,2):
        pid='urn:li:activity:'+str(7000000000000000000+i)
        posts.append({'id':pid,'url':'https://www.linkedin.com/posts/synthetic_'+str(i)+'-activity-'+str(7000000000000000000+i)+'-AbCd','published_at':'2026-10-20T08:00:00Z','captured_at':'2026-10-22T08:00:00Z','cycle':'fixture','text':'DO_NOT_EXPORT_ORIGINAL_POST_TEXT','source':{'raw_path':'/'+'Users/fixture/private/source.html','sha256':'a'*64},'author':{'name':'Synthetic Author '+str(i),'url':'https://www.linkedin.com/in/synthetic-'+str(i),'type':'Person','followers':100}})
        sem.append({'post_id':pid,'primary_topic':'positioning_messaging' if i==1 else 'sales_outbound','editorial_job':'teach_method','reference_value':'core','content_summary':'Original synthetic derived assessment '+str(i),'qualification_reason':'An invented buyer problem and method.','intended_reader':'B2B founders','hook_pattern':'Specific problem','central_claim':'A fictional method helps explain a decision.','claim_caveat':'No conversion proof.','adaptation_pattern':'Use original customer evidence.','media_role':'Invented explanatory graphic.','media_evidence_basis':'synthetic','reviewer_task':'DO_NOT_EXPORT_REVIEWER'})
        perf.append({'post_id':pid,'reactions':i*10,'comments':None,'reposts':0,'metric_captured_at':'2026-10-22T08:00:00Z','metric_snapshot_id':'snapshot-'+str(i),'metric_source_sha256':'b'*64,'metric_statuses':{'reactions':'observed','comments':'not_exposed','reposts':'observed'},'comparison_n':1,'performance_status':'insufficient_comparable_sample','performance_reason':'One invented example is not a comparison.','trend_status':'not_established','trend_reason':'No second capture.','scope':'Synthetic fixture.'})
        snap.append({'snapshot_id':'snapshot-'+str(i),'post_id':pid,'captured_at':'2026-10-22T08:00:00Z','capture_kind':'new_discovery','raw_path':'/'+'Users/fixture/source.html','raw_sha256':'b'*64,'parser_version':'fixture1','parser_sha256':'c'*64,'metrics':{'reactions':{'value':i*10,'status':'observed','source_path':'private_selector'},'comments':{'value':None,'status':'not_exposed'},'reposts':{'value':0,'status':'observed'}}})
    asset={'asset_id':'video:1','post_id':posts[0]['id'],'kind':'video','sha256':'d'*64,'bytes':10,'status':'acquired','path':'/'+'Users/fixture/video.mp4','url':'https://media.licdn.com/secret.mp4?token=DO_NOT_EXPORT','ffprobe':{'format':{'duration':'2.5','filename':'private-video.mp4'}}}
    return {'summary':{'run_id':'synthetic-test','as_of':'2026-10-22'},'posts':posts,'interpretations':sem,'performance':perf,'snapshots':snap,'assets':[asset],'visual_reviews':[],'video_reviews':[{'asset_id':'video:1','source_sha256':'d'*64,'description':{'format':'Invented screen demonstration','on_image_text':'DO_NOT_EXPORT_ON_IMAGE_TEXT','framing':'Wide synthetic layout'},'story_summary':'An invented example introduces and demonstrates a method.','post_text':'DO_NOT_EXPORT_VIDEO_POST_TEXT','reviewer_identity':'DO_NOT_EXPORT_REVIEWER','full_watch':False,'audio_review':False}],'transcripts':[{'asset_id':'video:1','post_id':posts[0]['id'],'origin':'synthetic_ASR','text':'DO_NOT_EXPORT_FULL_TRANSCRIPT','source_path':'private/transcript.json','source_video_sha256':'d'*64,'audio_verified':False}],'transcript_qa':[{'asset_id':'video:1','status':'flagged','flags':['timing_overrun'],'text_chars':100,'alternative':{'path':'private/alternative.json','sha256':'e'*64,'review_status':'alternative_decode_unreviewed','side_by_side':{'original':{'status':'flagged','text':'DO_NOT_EXPORT_SIDE_TEXT','segments':4},'alternative':{'status':'pass','segments':3}}}}],'author_decisions':[{'author_key':'/in/synthetic-1','author_name':'Synthetic Author 1','author_url':'https://www.linkedin.com/in/synthetic-1','decision':'approve_reference','role_or_company_evidence':'Invented B2B product role','source_posts':[{'post_id':posts[0]['id'],'url':posts[0]['url'],'raw_path':'private/raw.html'}],'role_resolution_evidence':[{'evidence_id':'role1','url':'https://company.example/about?utm_source=fixture','fact_paraphrase':'Invented professional role','saved_local_path':'/'+'Users/fixture/role.json','receipt_sha256':'f'*64}]}],'prospects':[{'id':'P1','name':'Synthetic Company','website':'https://company.example','linkedin_url':'https://www.linkedin.com/company/synthetic-company','description':'Invented B2B software company','fit_status':'plausible_pending_evidence','gaps':['Funding unknown'],'employees':['DO_NOT_EXPORT_EMPLOYEE'],'headcount':{'value':'11–50','status':'self_reported'},'funding':{'value':None},'expressed_need':{'status':'unknown'},'buying_interest':{'status':'unknown'}}]}

class PublicExport(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='public-export-test-');self.root=Path(self.temp.name);self.input=self.root/'input.json';self.out=self.root/'out';self.data=fixture();self.input.write_text(json.dumps(self.data))
    def tearDown(self):self.temp.cleanup()
    def run_export(self):self.input.write_text(json.dumps(self.data));return exp.export(self.input,self.out)
    def test_every_projection_output_preserves_source_identities(self):
        report=self.run_export();d=json.loads((self.out/'dataset.json').read_text());self.assertEqual(report['status'],'PASS');self.assertEqual(d['provenance']['source_dataset_sha256'],hashlib.sha256(self.input.read_bytes()).hexdigest());self.assertEqual({p['id'] for p in d['posts']},{p['id'] for p in self.data['posts']});self.assertEqual({s['snapshot_id'] for s in d['snapshots']},{s['snapshot_id'] for s in self.data['snapshots']});self.assertEqual(d['counts']['posts'],2)
        db=sqlite3.connect(self.out/'derived.sqlite')
        try:
            for table,key in [('posts','id'),('snapshots','snapshot_id'),('media','asset_id'),('author_decisions','author_key'),('prospects','id')]:self.assertEqual({k:json.loads(v) for k,v in db.execute('select id,payload from '+table)},{x[key]:x for x in d[table]})
        finally:db.close()
    def test_original_content_private_paths_and_unknown_fields_never_pass_through(self):
        self.run_export()
        for p in self.out.iterdir():
            b=p.read_bytes()
            for sentinel in [b'DO_NOT_EXPORT',b'private/source.html',b'private-video.mp4',b'media.licdn.com',('/'+'Users/').encode()]:self.assertNotIn(sentinel,b,p.name)
        d=json.loads((self.out/'dataset.json').read_text());self.assertEqual(d['media'][0]['transcript']['alternative']['comparison']['original']['segment_count'],4);self.assertNotIn('employees',d['prospects'][0]);self.assertEqual(d['author_decisions'][0]['role_sources'][0]['url'],'https://company.example/about')
    def test_owned_description_private_path_causes_hard_failure(self):
        self.data['interpretations'][0]['content_summary']='/'+'Users/fixture/private-copy'
        with self.assertRaisesRegex(ValueError,'Private path'):self.run_export()
        self.assertFalse((self.out/'dataset.json').exists())
    def test_missing_or_duplicate_semantic_identity_blocks_export(self):
        self.data['interpretations'].pop()
        with self.assertRaisesRegex(ValueError,'exactly one'):self.run_export()
        self.data=fixture();self.data['performance'].append(dict(self.data['performance'][0]))
        with self.assertRaisesRegex(ValueError,'duplicate'):self.run_export()
    def test_nested_metric_schema_drops_unknown_fields_and_rejects_objects(self):
        self.data['performance'][0]['metric_statuses']['unknown_nested_field']={'private_note':'not eligible'};self.run_export();d=json.loads((self.out/'dataset.json').read_text());self.assertNotIn('unknown_nested_field',d['posts'][0]['performance']['metric_statuses'])
        self.data['snapshots'][0]['metrics']['comments']['status']={'private_note':'not a status'}
        with self.assertRaisesRegex(ValueError,'scalar label'):self.run_export()
    def test_duplicate_input_json_keys_are_rejected(self):
        self.input.write_text('{"posts":[],"posts":[]}')
        with self.assertRaisesRegex(ValueError,'Duplicate JSON key'):exp.export(self.input,self.out)
    def test_unknown_stats_and_formula_escaping_are_retained(self):
        self.data['posts'][0]['author']['name']='=SUM(A1:A2)';self.run_export();d=json.loads((self.out/'dataset.json').read_text());self.assertIsNone(d['posts'][0]['performance']['comments']);self.assertEqual(d['posts'][0]['performance']['reposts'],0)
        with (self.out/'qualification-table.csv').open(newline='') as f:rows=list(csv.DictReader(f))
        self.assertEqual(rows[0]['author'],"'=SUM(A1:A2)");self.assertEqual(rows[0]['comments'],'');self.assertEqual(rows[0]['reposts'],'0')
        with (self.out/'snapshots.csv').open(newline='') as f:rows=list(csv.DictReader(f))
        self.assertEqual(rows[0]['comments_status'],'not_exposed');self.assertEqual(rows[0]['comments'],'')
    def test_script_closing_text_is_safely_embedded_and_roundtrips(self):
        payload='</script><script>window.injected=true</script>&';self.data['interpretations'][0]['content_summary']=payload;self.run_export();html=(self.out/'index.html').read_text();self.assertNotIn(payload,html);m=re.search(r'<script id="public-dataset" type="application/json">(.*?)</script>',html,re.S);self.assertEqual(json.loads(m.group(1))['posts'][0]['interpretation']['content_summary'],payload)
    @unittest.skipUnless(shutil.which('node'),'Existing Node required for viewer execution test')
    def test_viewer_filtering_tabs_and_media_boundary_execute(self):
        self.run_export();html=(self.out/'index.html').read_text();js=re.search(r'<script>\n(.*?)</script>',html,re.S).group(1);data=json.loads((self.out/'dataset.json').read_text())
        harness="""const fs=require('fs'),vm=require('vm'),input=JSON.parse(fs.readFileSync(0,'utf8')),elements={};function element(id){return elements[id]||(elements[id]={value:'',innerHTML:'',textContent:'',hidden:false,events:{},addEventListener(n,f){this.events[n]=f},setAttribute(k,v){this[k]=v}})}const context=vm.createContext({document:{querySelector:s=>element(s.slice(1)),getElementById:id=>id==='public-dataset'?{textContent:JSON.stringify(input.data)}:element(id)},Map,Set,JSON,console});vm.runInContext(input.js,context);const initial=element('post-count').textContent;element('topic').value='positioning_messaging';element('topic').events.change();const filtered=element('post-count').textContent;element('prospects-tab').events.click();process.stdout.write(JSON.stringify({initial,filtered,prospectVisible:!element('prospects').hidden,referenceHidden:element('references').hidden,companies:element('prospect-count').textContent,media:element('posts').innerHTML.includes('Original media retained locally.'),transcript:element('posts').innerHTML.includes('full text retained locally')}));"""
        run=subprocess.run(['node','-e',harness],input=json.dumps({'js':js,'data':data}),capture_output=True,text=True);self.assertEqual(run.returncode,0,run.stderr);result=json.loads(run.stdout);self.assertEqual(result['initial'],'2 matching publications');self.assertEqual(result['filtered'],'1 matching publications');self.assertTrue(result['prospectVisible']);self.assertTrue(result['referenceHidden']);self.assertEqual(result['companies'],'1 company summaries');self.assertTrue(result['media']);self.assertTrue(result['transcript'])

if __name__=='__main__':unittest.main()
