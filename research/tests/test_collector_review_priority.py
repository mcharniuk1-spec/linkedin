import unittest
from datetime import datetime,timezone,timedelta
from research.collector.review_priority import prioritize

NOW=datetime(2026,11,5,12,tzinfo=timezone.utc)
def row(name,age,rx=10,comments=1,observed_age=1,status='verified_source_date'):
    return {'record_id':name,'external_id':name,'source_id':'fixture','source_url':'https://example.test/'+name,
        'content_type':'linkedin_post','published_at':(NOW-timedelta(hours=age)).isoformat(),
        'collected_at':(NOW-timedelta(hours=observed_age)).isoformat(),'publication_date_status':status,
        'legacy_record':{'metrics':{'reactions':{'status':'observed','value':rx},
                                    'comments':{'status':'observed','value':comments}}}}

class ReviewPriorityTests(unittest.TestCase):
    def test_fresh_age_bands_then_separate_observed_counts(self):
        rows=[row('older',50,10000,1),row('lower',5,12,8),row('higher',8,15,0),row('tie',3,15,4)]
        result=prioritize(rows,now=NOW)
        self.assertEqual([x['external_id'] for x in result],['tie','higher','lower','older'])
        self.assertEqual([x['priority'] for x in result],[1,2,3,4])
        self.assertTrue(all(x['trend_status']=='not_measured_single_snapshot' for x in result))
    def test_missing_invalid_and_stale_counters_are_holds_not_zero(self):
        missing=row('missing',3);missing['legacy_record']['metrics']['comments']={'status':'not_exposed','value':None}
        invalid=row('invalid',3,rx=True)
        undated=row('undated',3,status='missing')
        stale=row('stale',40,observed_age=25)
        future=row('future',-1,observed_age=0)
        result=prioritize([missing,invalid,undated,stale,future],now=NOW)
        self.assertTrue(all(x['priority'] is None for x in result))
        self.assertEqual([x['qualification'] for x in result],['reaction_or_comment_count_unavailable',
            'reaction_or_comment_count_unavailable','source_date_unverified','observation_older_than_24h',
            'invalid_or_future_observation'])
        self.assertIsNone(result[0]['comments'])

if __name__=='__main__':unittest.main()
