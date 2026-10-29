import json,tempfile,unittest
from datetime import datetime
from zoneinfo import ZoneInfo
import httpx
from research.collector.store import Store
from research.collector.discovery import discover,ENDPOINT
from research.collector.contracts import AccessSuspended,CollectionError

URL='https://www.linkedin.com/posts/fixture_business-activity-7518006369120055296-abcd'
class DiscoveryTests(unittest.TestCase):
 def setUp(self):self.t=tempfile.TemporaryDirectory();self.s=Store(self.t.name);self.calls=[]
 def tearDown(self):self.s.close();self.t.cleanup()
 def client(self,deny=False):
  def handle(request):
   body=json.loads(request.content);self.calls.append(body)
   if body['method']=='notifications/initialized':return httpx.Response(202)
   if deny and body['method']=='tools/call':return httpx.Response(429)
   result={'protocolVersion':'2025-03-26'}
   if body['method']=='tools/list':result={'tools':[{'name':'web_search_exa','inputSchema':{'properties':{'query':{},'objective':{}}}}]}
   if body['method']=='tools/call':result={'content':[{'type':'text','text':URL+'\nhttps://evil-linkedin.com/posts/no-activity-7518006369120055296-x'}]}
   return httpx.Response(200,headers={'content-type':'text/event-stream','mcp-session-id':'test-session-only'},text='data: '+json.dumps({'jsonrpc':'2.0','id':body['id'],'result':result})+'\n\n')
  return httpx.Client(transport=httpx.MockTransport(handle))
 def config(self):return {'enabled':True,'endpoint':ENDPOINT,'queries':['site:linkedin.com/posts/ B2B after:{since14} before:{tomorrow}'],'max_queries':2,'author_queries_per_run':1,'max_results_per_query':2}
 def test_schema_objective_raw_lineage_cursor_and_domain(self):
  with self.client() as c:urls=discover(self.config(),self.s,['/in/fixture'],client=c,now=datetime(2026,10,29,tzinfo=ZoneInfo('Europe/Sofia')))
  self.assertEqual(urls,[URL]);queries=[c for c in self.calls if c['method']=='tools/call'];self.assertEqual(len(queries),2)
  for q in queries:self.assertTrue(q['params']['arguments']['objective'])
  self.assertIn('after:2026-10-15',queries[0]['params']['arguments']['query'])
  self.assertEqual(self.s.db.execute('select count(*) from discoveries').fetchone()[0],2)
  self.assertEqual(self.s.db.execute("select value from metadata where key='author_cursor'").fetchone()[0],'1')
 def test_429_is_durable_stop_without_backend_switch(self):
  with self.client(True) as c:
   with self.assertRaises(AccessSuspended):discover(self.config(),self.s,client=c)
  count=len(self.calls)
  with self.client() as c:
   with self.assertRaises(AccessSuspended):discover(self.config(),self.s,client=c)
  self.assertEqual(len(self.calls),count);self.assertFalse(self.s.get_suspension('exa-search')['automatic_resume'])
 def test_known_post_excluded_and_other_backend_refused(self):
  self.s.seed({'publications':[{'external_id':'urn:li:activity:7518006369120055296','aliases':['id:urn:li:activity:7518006369120055296']} ]})
  with self.client() as c:self.assertEqual(discover(self.config(),self.s,client=c),[])
  with self.assertRaises(CollectionError):discover({**self.config(),'endpoint':'https://unapproved.test'},self.s)
if __name__=='__main__':unittest.main()
