import tempfile
import unittest
from datetime import datetime, timezone
from research.collector.coverage import daily_progress
from research.collector.contracts import record
from research.collector.store import Store


class DailyCoverageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = Store(self.temp.name)

    def tearDown(self):
        self.store.close()
        self.temp.cleanup()

    def add(self, ident, timestamp, author=None, typ='linkedin_post'):
        return self.store.ingest(record(source_id='fixture', external_id=ident,
            source_url='https://www.linkedin.com/posts/example_activity-'+ident,
            content_type=typ, text='small '+ident, author=author, collected_at=timestamp,
            permissions={'collection':True, 'license':'test'}))

    def test_sofia_dst_window_unique_actors_and_unknown(self):
        # The fall-back day has 25 hours. Midnight is 21:00 UTC on the preceding day.
        self.add('1','2026-10-24T21:00:00Z',{'url':'https://www.linkedin.com/in/Person'})
        self.add('2','2026-10-25T15:00:00Z',{'url':'https://linkedin.com/in/person?tracking=1'})
        self.add('3','2026-10-25T16:00:00Z',{'url':'https://www.linkedin.com/company/example'})
        self.add('4','2026-10-25T17:00:00Z',None)
        self.add('5','2026-10-24T20:59:59Z',{'url':'https://www.linkedin.com/in/outside'})
        self.add('6','2026-10-25T18:30:00Z',None,'linkedin_comment')
        result=daily_progress(self.store,now=datetime(2026,10,25,21,59,tzinfo=timezone.utc),posts_goal=4,accounts_goal=2)
        self.assertEqual(result['window_start_utc'],'2026-10-24T21:00:00+00:00')
        self.assertEqual(result['window_end_utc'],'2026-10-25T22:00:00+00:00')
        self.assertEqual(result['new_unique_posts'],4)
        self.assertEqual(result['distinct_observed_accounts'],2)
        self.assertEqual(result['posts_without_usable_actor'],1)
        self.assertTrue(result['posts_goal_met']); self.assertTrue(result['accounts_goal_met'])

    def test_future_and_unverified_actor_are_not_counted_as_current_actors(self):
        self.add('1','2026-11-05T08:00:00Z',{'url':'https://notlinkedin.com/in/person'})
        self.add('2','2026-11-05T10:00:00Z',{'url':'https://www.linkedin.com/in/person'})
        result=daily_progress(self.store,now=datetime(2026,11,5,9,tzinfo=timezone.utc))
        self.assertEqual(result['new_unique_posts'],1)
        self.assertEqual(result['distinct_observed_accounts'],0)
        self.assertEqual(result['posts_without_usable_actor'],1)
        self.assertEqual(result['future_records_excluded'],1)
        self.assertFalse(result['posts_goal_met'])
        with self.assertRaises(ValueError):daily_progress(self.store,now=datetime(2026,11,5))


if __name__ == '__main__':
    unittest.main()
