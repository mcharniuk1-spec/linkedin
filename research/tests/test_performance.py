import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from performance import assess, post_format


def fixture(counts):
    ps = [{'id': str(i), 'author': {'url': 'https://www.linkedin.com/in/example'},
           'published_at': '2026-10-01T00:00:00Z', 'captured_at': '2026-10-22T00:00:00Z',
           'metrics': {'reactions': {'value': c, 'status': 'observed'}, 'comments': {'value': None, 'status': 'not_exposed'}},
           'source': {'sha256': 'raw'}, 'media': []} for i, c in enumerate(counts)]
    sem = [{'post_id': p['id'], 'content_language': 'English'} for p in ps]
    return ps, sem


class PerformanceTests(unittest.TestCase):
    def test_ties_are_not_strong(self):
        p, s = fixture([100] * 8)
        rows = assess(p, [], [], s)
        self.assertTrue(all(r['reaction_midrank_percentile'] == .5 for r in rows))
        self.assertTrue(all(r['performance_status'] != 'strong_sample_reference' for r in rows))

    def test_small_sample_no_percentile(self):
        p, s = fixture([1, 2, 100000])
        self.assertTrue(all(r['reaction_midrank_percentile'] is None for r in assess(p, [], [], s)))

    def test_upper_sample_is_descriptive(self):
        p, s = fixture([1, 2, 3, 4, 5, 6, 7, 100])
        r = assess(p, [], [], s)[-1]
        self.assertEqual(r['performance_status'], 'strong_sample_reference')
        self.assertEqual(r['trend_status'], 'not_established')
        self.assertEqual(r['sales_effectiveness'], 'unknown')

    def test_missing_and_conflict_not_zero(self):
        p, s = fixture([1] * 8)
        p[0]['metrics']['reactions']['status'] = 'conflict'
        r = assess(p, [], [], s)[0]
        self.assertIsNone(r['reactions'])
        self.assertEqual(r['comparison_n'], 7)

    def test_latest_snapshot_is_explicit(self):
        p, s = fixture([1])
        snaps = [{'post_id': '0', 'snapshot_id': 'second', 'captured_at': '2026-10-22T10:00:00Z', 'metrics': {'reactions': {'value': 9, 'status': 'observed'}}, 'raw_sha256': 'secondraw'}]
        r = assess(p, snaps, [], s)[0]
        self.assertEqual((r['reactions'], r['metric_snapshot_id'], r['metric_source_sha256']), (9, 'second', 'secondraw'))

    def test_negative_and_flat_counter_not_trend(self):
        p, s = fixture([1, 2])
        vv = [{'post_id': '0', 'eligible': True, 'counter_decreased': True}, {'post_id': '1', 'eligible': True, 'reaction_delta': 0, 'span_hours': 8}]
        rr = assess(p, [], vv, s)
        self.assertEqual([r['trend_status'] for r in rr], ['counter_decrease_review', 'flat_observed_window'])

    def test_growth_does_not_prove_trend(self):
        p, s = fixture([1])
        v = [{'post_id': '0', 'eligible': True, 'reaction_delta': 2, 'span_hours': 8, 'reactions_per_hour': .25}]
        self.assertEqual(assess(p, [], v, s)[0]['trend_status'], 'growth_observed_not_trend')

    def test_unknown_future_and_conflicting_dates_held(self):
        p, s = fixture([1] * 8)
        p[0]['published_at'] = None
        p[1]['published_at'] = '2027-01-01T00:00:00Z'
        snaps = [{'post_id': '2', 'captured_at': '2026-10-22T10:00:00Z', 'published_at': '2026-10-01T00:00:00Z', 'metrics': {}}, {'post_id': '2', 'captured_at': '2026-10-22T11:00:00Z', 'published_at': '2026-10-02T00:00:00Z', 'metrics': {}}]
        rr = assess(p, snaps, [], s)
        self.assertTrue(all(rr[i]['reaction_midrank_percentile'] is None for i in [0, 1, 2]))

    def test_format_and_language_separate_cohorts(self):
        p, s = fixture([1] * 8)
        p[0]['media'] = [{'type': 'video'}]
        s[1]['content_language'] = 'German'
        rr = assess(p, [], [], s)
        self.assertEqual([rr[i]['comparison_n'] for i in [0, 1, 2]], [1, 1, 6])
        self.assertEqual(post_format(p[2], ['document_preview']), 'document')


if __name__ == '__main__':
    unittest.main()
