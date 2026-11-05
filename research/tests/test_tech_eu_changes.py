import asyncio
from datetime import datetime,timezone
import json
import tempfile
import unittest
from urllib.parse import parse_qs,urlsplit
from research.collector.contracts import FetchResult
from research.collector.store import Store
from research.collector.tech_eu import _seed,_put
from research.collector.tech_eu_changes import collect_changes

NOW=datetime(2026,11,5,12,tzinfo=timezone.utc)
SINCE='2026-11-04T00:00:00+00:00'
CID='00000000-0000-4000-8000-000000000001'
R1='00000000-0000-4000-8000-000000000002'
R2='00000000-0000-4000-8000-000000000003'
STAMP='2026-11-04T06:42:33.139640Z'

def make_row(rid=R1):
    return {'id':rid,'createdAt':STAMP,'date':'2026-11-03','stage':'Seed','confidence':'high',
            'pageUrl':'https://funding.tech.eu/deals/'+rid,'company':{'id':CID,'name':'Example',
            'country':'Belgium','sectors':['AI'],'pageUrl':'https://funding.tech.eu/companies/example-00000000'}}

class Fake:
    def __init__(self,responses):self.responses=responses;self.calls=[]
    async def fetch(self,url,**_):
        self.calls.append(url);status,body=self.responses[len(self.calls)-1]
        return FetchResult(url=url,status_code=status,body=json.dumps(body).encode(),collected_at=NOW.isoformat())
    async def aclose(self):pass

def page(rows,after=None,removed=None,complete=True):
    return {'type':'rounds','since':SINCE,'data':rows,'removed':removed or [],
            'removedComplete':complete,'nextCursor':after}

class ChangesTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.s=Store(self.tmp.name)
        self.s.db.execute('CREATE TABLE candidate_queue (category TEXT,identity TEXT,payload TEXT,PRIMARY KEY(category,identity))')
        with self.s.db:
            self.s.db.execute('INSERT INTO metadata VALUES (?,?)',('tech_eu_bootstrap_started_at',SINCE))
            self.s.db.execute('INSERT INTO metadata VALUES (?,?)',('tech_eu_seed_done','yes'))
    def tearDown(self):self.s.close();self.tmp.cleanup()
    def run_it(self,fake,**kw):return asyncio.run(collect_changes(self.s,now=NOW,transport_factory=lambda *_:fake,**kw))
    def meta(self,key):
        row=self.s.db.execute('SELECT value FROM metadata WHERE key=?',(key,)).fetchone()
        return row[0] if row else None
    def test_pages_commit_atomically_and_resume(self):
        first=STAMP+'__'+R1
        fake=Fake([(200,page([make_row()],first)),(200,page([make_row(R2)]))])
        result=self.run_it(fake)
        self.assertEqual(result['status'],'ok');self.assertEqual(result['requests'],2)
        self.assertEqual(result['new_items'],1);self.assertEqual(result['duplicates'],1)
        self.assertEqual(self.meta('tech_eu_changes_after'),STAMP+'__'+R2)
        self.assertEqual(self.meta('tech_eu_changes_since'),SINCE)
        self.assertEqual(self.meta('tech_eu_changes_complete_utc_day'),'2026-11-05')
        self.assertEqual(parse_qs(urlsplit(fake.calls[1]).query)['after'],[first])
        self.assertTrue(all(urlsplit(x).hostname=='funding.tech.eu' for x in fake.calls))
    def test_partial_page_is_resumable_without_daily_complete(self):
        cursor=STAMP+'__'+R1; fake=Fake([(200,page([make_row()],cursor))])
        result=self.run_it(fake,max_pages=1)
        self.assertEqual(result['status'],'partial');self.assertEqual(self.meta('tech_eu_changes_after'),cursor)
        self.assertIsNone(self.meta('tech_eu_changes_complete_utc_day'))
        fake=Fake([(200,page([make_row(R2)]))]);result=self.run_it(fake)
        self.assertEqual(result['status'],'ok');self.assertEqual(parse_qs(urlsplit(fake.calls[0]).query)['after'],[cursor])
    def test_later_error_never_advances_or_saves_prior_page(self):
        fake=Fake([(200,page([make_row()],STAMP+'__'+R1)),(500,{})]);result=self.run_it(fake)
        self.assertEqual(result['status'],'error');self.assertIsNone(self.meta('tech_eu_changes_after'))
        self.assertEqual(self.s.db.execute('select count(*) from candidate_queue').fetchone()[0],0)
    def test_tombstone_marks_source_without_deleting_review(self):
        seed=_seed(make_row(),NOW.isoformat(),datetime(2026,1,1,tzinfo=timezone.utc).date())
        seed['review_status']='reviewed';seed['buying_interest']='owner_reviewed';
        with self.s.db:_put(self.s,seed)
        fake=Fake([(200,page([],removed=[{'id':R1,'removedAt':STAMP}]))]);result=self.run_it(fake)
        payload=json.loads(self.s.db.execute('select payload from candidate_queue').fetchone()[0])
        self.assertEqual(result['status'],'ok');self.assertEqual(payload['review_status'],'reviewed')
        self.assertEqual(payload['buying_interest'],'owner_reviewed')
        self.assertEqual(payload['funding']['source_status'],'withdrawn_by_source')
    def test_incomplete_tombstones_hold_without_advancing(self):
        result=self.run_it(Fake([(200,page([make_row()],complete=False))]))
        self.assertEqual(result['status'],'error');self.assertIsNone(self.meta('tech_eu_changes_after'))
        self.assertEqual(self.meta('tech_eu_changes_hold'),'tombstone_list_incomplete')
    def test_missing_bootstrap_and_denied_access_hold(self):
        with self.s.db:self.s.db.execute("delete from metadata where key='tech_eu_seed_done'")
        fake=Fake([]);self.assertEqual(self.run_it(fake)['status'],'held');self.assertEqual(fake.calls,[])
        with self.s.db:self.s.db.execute('INSERT INTO metadata VALUES (?,?)',('tech_eu_seed_done','yes'))
        self.assertEqual(self.run_it(Fake([(429,{})]))['status'],'held')
        self.assertIsNone(self.meta('tech_eu_changes_after'))
    def test_millisecond_normalization_rounds_anchor_down_without_a_gap(self):
        with self.s.db:
            self.s.db.execute("update metadata set value=? where key='tech_eu_bootstrap_started_at'",('2026-11-04T00:00:00.123456+00:00',))
        response=page([]);response['since']='2026-11-04T00:00:00.123Z'
        fake=Fake([(200,response)]);result=self.run_it(fake)
        self.assertEqual(result['status'],'ok')
        self.assertEqual(self.meta('tech_eu_changes_since'),'2026-11-04T00:00:00.123+00:00')

if __name__=='__main__':unittest.main()
