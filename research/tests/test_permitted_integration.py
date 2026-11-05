import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from research.collector.candidate_queue import enqueue
from research.collector.store import Store
from research.collector.viewer_projection import build
from research.collector.job_summary import summary


class QueueAndViewerTests(unittest.TestCase):
    def test_viewer_preserves_exa_hold_when_prior_run_error_was_generic(self):
        from datetime import datetime,timezone
        with tempfile.TemporaryDirectory() as directory:
            store=Store(directory)
            try:
                store.suspend('exa-search','discovery_tool_quota_or_error')
                run={'started_at':datetime.now(timezone.utc).isoformat(),'duplicates':0,
                     'errors':[{'source_id':'exa-search','error_code':'discovery_unavailable'}]}
                with store.db:store.db.execute('INSERT INTO runs VALUES (?,?)',('run',json.dumps(run)))
                sources=build(store)['operations']['sources']
                self.assertTrue(next(s for s in sources if s['source_id']=='exa-search')['hold'])
            finally:store.close()
    def test_actions_summary_is_honest_about_holds_and_missing_counts(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'run.json'
            path.write_text(json.dumps({'linkedin_status':'blocked_by_persistent_access_hold',
                'daily_progress':{'new_unique_posts':0,'distinct_observed_accounts':0},
                'external_discovery':{'source_results':[{'source_id':'hacker-news-top','status':'ok',
                    'successful_requests':6,'requests':6,'new_items':20}]}}))
            result=summary(path)
            self.assertIn('blocked by persistent access hold',result)
            self.assertIn('0 / 100 target',result)
            self.assertIn('6/6 requests succeeded',result)
            self.assertIn('unknown',result)

    def test_categories_are_distinct_deduplicated_and_not_post_records(self):
        with tempfile.TemporaryDirectory() as directory:
            store=Store(directory)
            try:
                post='https://www.linkedin.com/posts/abc_activity-1234567890123456789?tracking=x'
                self.assertEqual(enqueue(store,'publication',post,'exa-search'),1)
                self.assertEqual(enqueue(store,'publication',post,'exa-search'),0)
                self.assertEqual(enqueue(store,'target_company','https://www.linkedin.com/company/example/','manual'),1)
                self.assertEqual(enqueue(store,'reference_account','https://www.linkedin.com/company/example/','manual'),1)
                with self.assertRaises(ValueError):enqueue(store,'target_company','https://evil.example/company/example','manual')
                data=build(store)
                self.assertEqual(len(data['reference_candidates']),2)
                self.assertEqual(len(data['target_companies']),1)
                self.assertEqual(data['operations']['daily_progress']['new_unique_posts'],0)
                self.assertEqual(data['authorized_posts'],[])
                self.assertIsNone(data['reference_candidates'][0]['performance_evidence'])
            finally:store.close()

    def test_owner_export_and_source_signals_remain_in_separate_views(self):
        with tempfile.TemporaryDirectory() as directory:
            store=Store(directory)
            try:
                store.suspend('linkedin-public','challenge_page')
                post={'granularity':'post','subject_id':'id:example','observed_at':'2026-11-05T12:00:00+00:00',
                      'post_url':'https://www.linkedin.com/posts/example', 'date':'2026-11-04',
                      'metrics':{'reactions':3,'comments':None,'impressions':10}}
                data=build(store,authorized=[post])
                self.assertEqual(data['operations']['linkedin_status'],'blocked')
                self.assertEqual(data['authorized_posts'][0]['metrics']['reactions'],3)
                self.assertIsNone(data['authorized_posts'][0]['metrics']['comments'])
                self.assertEqual(data['external_signals'],[])
                self.assertEqual(data['reference_candidates'],[])
            finally:store.close()


if __name__=='__main__':unittest.main()
