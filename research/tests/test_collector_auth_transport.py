import unittest,tempfile
import httpx
from research.collector.transport import HttpxTransport
from research.collector.store import Store
from research.collector.contracts import AccessSuspended,CollectionError

class AuthTransportTests(unittest.IsolatedAsyncioTestCase):
 async def test_only_official_adapter_forwards_bearer_and_no_redirect(self):
  with tempfile.TemporaryDirectory() as td:
   store=Store(td);seen=[]
   def handler(request):seen.append(request);return httpx.Response(200,content=b'{}')
   def factory(**kw):return httpx.AsyncClient(transport=httpx.MockTransport(handler),**kw)
   spec={'source_id':'li','adapter':'linkedin_api','allowed_hosts':['api.linkedin.com'],'permitted_methods':['GET'],'permissions':{'collection':True},'rate_per_second':10000}
   tr=HttpxTransport(spec,store,client_factory=factory)
   await tr.fetch('https://api.linkedin.com/rest/posts',headers={'Authorization':'Bearer synthetic-fixture','Cookie':'discard'})
   self.assertEqual(seen[0].headers['Authorization'],'Bearer synthetic-fixture');self.assertNotIn('cookie',seen[0].headers)
   await tr.aclose();tr=HttpxTransport({**spec,'adapter':'http'},store,client_factory=factory)
   await tr.fetch('https://api.linkedin.com/rest/posts',headers={'Authorization':'Bearer synthetic-fixture'})
   self.assertNotIn('authorization',seen[1].headers);await tr.aclose()
   def redirect(request):return httpx.Response(302,headers={'location':'/next'})
   tr=HttpxTransport(spec,store,client_factory=lambda **kw:httpx.AsyncClient(transport=httpx.MockTransport(redirect),**kw))
   with self.assertRaises(CollectionError):await tr.fetch('https://api.linkedin.com/rest/posts',headers={'Authorization':'Bearer synthetic-fixture'})
   await tr.aclose();store.close()
 async def test_long_retry_after_suspends_without_early_retry(self):
  with tempfile.TemporaryDirectory() as td:
   store=Store(td);hits=[]
   def handler(request):hits.append(request);return httpx.Response(503,headers={'retry-after':'120'})
   spec={'source_id':'fixture','allowed_hosts':['example.test'],'permitted_methods':['GET'],'permissions':{'collection':True},'rate_per_second':10000}
   tr=HttpxTransport(spec,store,client_factory=lambda **kw:httpx.AsyncClient(transport=httpx.MockTransport(handler),**kw))
   with self.assertRaises(AccessSuspended):await tr.fetch('https://example.test/source')
   self.assertEqual(len(hits),1);self.assertEqual(store.get_suspension('fixture')['retry_after_seconds'],120)
   await tr.aclose();store.close()
if __name__=='__main__':unittest.main()
