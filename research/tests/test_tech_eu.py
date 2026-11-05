import asyncio
from datetime import datetime, timedelta, timezone
import json
import tempfile
import unittest
from urllib.parse import parse_qs, urlsplit

from research.collector.contracts import FetchResult
from research.collector.store import Store
from research.collector.tech_eu import collect_tech_eu, prune_unreviewed_seeds

NOW=datetime(2026,11,5,12,tzinfo=timezone.utc)
CID='00000000-0000-4000-8000-000000000001'
RID='00000000-0000-4000-8000-000000000002'


def row(stage='Seed',country='Belgium'):
    return {'id':RID,'date':'2026-11-04','stage':stage,'confidence':'high',
            'pageUrl':'https://funding.tech.eu/deals/'+RID,
            'company':{'id':CID,'name':'Example','country':country,'sectors':['AI'],
                       'pageUrl':'https://funding.tech.eu/companies/example-00000000'}}


class Fake:
    def __init__(self, status=200, bad_filters=False, countries=None, more=False):
        self.status=status; self.calls=[]; self.bad_filters=bad_filters;self.countries=countries;self.more=more
    async def fetch(self,url,**kwargs):
        self.calls.append(url);params=parse_qs(urlsplit(url).query);stage=params['stage'][0]
        filters={'stage':stage,'sector':'AI','from':params['from'][0]}
        if self.bad_filters:filters.pop('from')
        countries=self.countries or ['Belgium']
        rows=[row(stage,c) for c in countries]
        body=json.dumps({'data':rows,'appliedFilters':filters,'nextCursor':'next' if self.more else None}).encode()
        return FetchResult(url=url,body=body,status_code=self.status,collected_at=NOW.isoformat())
    async def aclose(self):pass


class TechEuTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.store=Store(self.tmp.name)
    def tearDown(self):
        self.store.close();self.tmp.cleanup()
    def run_source(self,fake,**kw):
        return asyncio.run(collect_tech_eu(self.store,now=NOW,transport_factory=lambda *_:fake,**kw))
    def test_dedupe_source_facts_and_unknowns(self):
        f=Fake();result=self.run_source(f)
        self.assertEqual(result['status'],'ok');self.assertEqual(result['requests'],3)
        self.assertEqual(result['new_items'],1);self.assertEqual(result['duplicates'],2)
        payload=json.loads(self.store.db.execute('select payload from candidate_queue').fetchone()[0])
        self.assertEqual(payload['funding']['stage'],'Seed')
        for key in ('employee_count','business_model','linkedin_url','expressed_need','buying_interest'):
            self.assertIsNone(payload[key])
        self.assertEqual(payload['attribution'],'Tech.eu Funding Explorer')
        self.assertEqual(payload['licence_url'],'https://creativecommons.org/licenses/by/4.0/')
        self.assertTrue(payload['source_changes'])
        self.assertEqual(payload['review_status'],'pending')
        self.assertEqual(self.store.db.execute('select count(*) from records').fetchone()[0],0)
        self.assertTrue(all(url.startswith('https://funding.tech.eu/api/v1/rounds?') for url in f.calls))
        second=self.run_source(f);self.assertEqual(second['status'],'already_completed_today')
        self.assertEqual(len(f.calls),3)
    def test_denial_durably_holds_source_without_further_requests(self):
        for code in (401,403,429,999):
            with self.subTest(code=code),tempfile.TemporaryDirectory() as td:
                store=Store(td);fake=Fake(status=code)
                try:
                    result=asyncio.run(collect_tech_eu(store,now=NOW,transport_factory=lambda *_:fake))
                    self.assertEqual(result['status'],'held');self.assertEqual(len(fake.calls),1)
                    self.assertIsNotNone(store.get_suspension('tech-eu-funding-explorer'))
                    again=asyncio.run(collect_tech_eu(store,now=NOW,transport_factory=lambda *_:fake))
                    self.assertEqual(again['requests'],0);self.assertEqual(len(fake.calls),1)
                finally:store.close()
    def test_country_scope_filters_outside_europe(self):
        result=self.run_source(Fake(countries=['Türkiye','Israel','Russia','Belgium']))
        self.assertEqual(result['new_items'],1);self.assertEqual(result['excluded'],9)
    def test_filter_confirmation_and_page_limit(self):
        bad=Fake(bad_filters=True);result=self.run_source(bad)
        self.assertEqual(result['status'],'error');self.assertEqual(len(bad.calls),1)
        good=Fake(more=True);result=self.run_source(good,max_pages_per_stage=2)
        self.assertEqual(result['requests'],6);self.assertEqual(result['status'],'ok')
        self.assertTrue(any('after=next' in x for x in good.calls))
        self.assertEqual(result['truncated_stages'],['Seed','Series A','Series B'])
    def test_retention_expires_only_untouched_managed_pending_seeds(self):
        self.run_source(Fake())
        original=self.store.db.execute('select identity,payload from candidate_queue').fetchone()
        self.store.db.execute('insert into candidate_queue values (?,?,?)',('target_company','edited',original[1]))
        edited=json.loads(original[1]);edited['description']='Reviewed by a person'
        self.store.db.execute('update candidate_queue set payload=? where identity=?',(json.dumps(edited),'edited'))
        self.assertEqual(prune_unreviewed_seeds(self.store,NOW+timedelta(days=179)),0)
        self.assertEqual(prune_unreviewed_seeds(self.store,NOW+timedelta(days=180)),1)
        self.assertEqual(self.store.db.execute('select identity from candidate_queue').fetchall(),[('edited',)])
    def test_source_cannot_clear_linkedin_hold(self):
        self.store.suspend('linkedin-public','challenge_page')
        result=self.run_source(Fake())
        self.assertEqual(result['status'],'ok')
        self.assertEqual(self.store.get_suspension('linkedin-public')['reason'],'challenge_page')


if __name__=='__main__':unittest.main()
