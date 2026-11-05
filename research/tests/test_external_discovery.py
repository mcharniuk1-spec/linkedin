import asyncio
import json
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
import unittest

from research.collector.contracts import FetchResult
from research.collector.external_discovery import collect_external, load_sources
from research.collector.store import Store


class FakeTransport:
    def __init__(self, spec, store, responses, calls):
        self.responses, self.calls = responses, calls

    async def fetch(self, url, *, headers=None):
        self.calls.append(url)
        status, body = self.responses[url]
        return FetchResult(url=url, body=body, status_code=status,
                           collected_at='2026-11-05T12:00:00+00:00')

    async def aclose(self):
        pass


class ExternalDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = Store(Path(self.tmp.name) / 'state')
        self.config = load_sources()
        self.urls = {s['source_id']: s['url'] for s in self.config['sources']}
        self.responses = {
            self.urls['hacker-news-top']: (200, b'[123, 456]'),
            self.urls['huggingface-blog-rss']: (200, b'''<rss><channel>
                <item><title>AI systems</title><link>https://example.org/one</link>
                <pubDate>Thu, 05 Nov 2026 11:00:00 +0000</pubDate></item>
                <item><title>duplicate</title><link>https://example.org/one</link></item>
                <item><title>bad</title><link>javascript:alert(1)</link></item>
                <item><title>LinkedIn candidate</title><link>https://linkedin.com/posts/example</link></item>
                </channel></rss>'''),
        }
        for identifier in (123, 456):
            self.responses[f'https://hacker-news.firebaseio.com/v0/item/{identifier}.json'] = (
                200, json.dumps({'id': identifier, 'type': 'story', 'title': 'Founder story',
                                 'time': 1793876400, 'score': 77, 'descendants': 14}).encode())
        self.calls = []

    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def run_collection(self, config=None):
        return asyncio.run(collect_external(self.store, config or self.config,
            transport_factory=lambda spec, store: FakeTransport(spec, store, self.responses, self.calls)))

    def test_source_provenance_dedup_and_snapshots_are_separate(self):
        first = self.run_collection()
        second = self.run_collection()
        self.assertEqual(sum(x['new_items'] for x in first['source_results']), 4)
        self.assertEqual(sum(x['new_items'] for x in second['source_results']), 0)
        self.assertEqual(sum(x['duplicates'] for x in second['source_results']), 4)
        self.assertEqual(self.store.db.execute('select count(*) from records').fetchone()[0], 0)
        self.assertEqual(self.store.db.execute('select count(*) from external_discovery_items').fetchone()[0], 4)
        self.assertEqual(self.store.db.execute('select count(*) from external_discovery_observations').fetchone()[0], 8)
        self.assertNotIn('AI systems', str(first))
        self.assertNotIn('linkedin.com', str(first))
        self.assertFalse(any('linkedin.com' in url for url in self.calls))
        self.assertEqual(first['linkedin_posts_collected'], 0)

    def test_denied_source_is_suspended_and_independent_sources_continue(self):
        self.responses[self.urls['hacker-news-top']] = (403, b'')
        first = self.run_collection()
        self.assertEqual(first['source_results'][0]['status'], 'held')
        self.assertEqual(first['source_results'][1]['status'], 'ok')
        self.assertIsNotNone(self.store.get_suspension('hacker-news-top'))
        self.calls.clear()
        second = self.run_collection()
        self.assertEqual(second['source_results'][0]['requests'], 0)
        self.assertNotIn(self.urls['hacker-news-top'], self.calls)

    def test_linkedin_hold_does_not_affect_independent_sources(self):
        self.store.suspend('linkedin-public', 'challenge_page')
        result = self.run_collection()
        self.assertEqual(result['status'], 'ok')
        self.assertIsNotNone(self.store.get_suspension('linkedin-public'))
        self.assertEqual(len(self.calls), 4)

    def test_hn_details_are_bounded_rotated_and_marked_as_hn(self):
        ids = list(range(100, 107))
        self.responses[self.urls['hacker-news-top']] = (200, json.dumps(ids).encode())
        for identifier in ids:
            self.responses[f'https://hacker-news.firebaseio.com/v0/item/{identifier}.json'] = (
                200, json.dumps({'id': identifier, 'type': 'story', 'title': 'AI founders',
                                 'time': 1793876400, 'score': 77, 'descendants': 14}).encode())
        first = self.run_collection()
        self.assertEqual(first['source_results'][0]['detail_requests'], 5)
        self.calls.clear()
        second = self.run_collection()
        self.assertEqual(second['source_results'][0]['detail_requests'], 5)
        self.assertIn('https://hacker-news.firebaseio.com/v0/item/105.json', self.calls)
        self.assertIn('https://hacker-news.firebaseio.com/v0/item/106.json', self.calls)
        raw = self.store.db.execute("select metadata from external_discovery_items where source_id='hacker-news-top' and external_id='105'").fetchone()[0]
        self.assertEqual(json.loads(raw)['engagement']['hn_score'], 77)
        self.assertEqual(json.loads(raw)['source_platform'], 'hacker_news')

    def test_duplicate_hn_ids_never_repeat_detail_fetch(self):
        self.responses[self.urls['hacker-news-top']] = (200, b'[123, 123, 456]')
        result = self.run_collection()
        self.assertEqual(result['source_results'][0]['detail_requests'], 2)
        self.assertEqual(self.calls.count('https://hacker-news.firebaseio.com/v0/item/123.json'), 1)

    def test_detail_denial_stops_hn_and_preserves_other_sources(self):
        url = 'https://hacker-news.firebaseio.com/v0/item/123.json'
        self.responses[url] = (429, b'')
        result = self.run_collection()
        self.assertEqual(result['source_results'][0]['status'], 'held')
        self.assertEqual(result['source_results'][0]['items_observed'], 2)
        self.assertNotIn('https://hacker-news.firebaseio.com/v0/item/456.json', self.calls)
        self.assertEqual(result['source_results'][1]['status'], 'ok')

    def test_retention_prunes_old_observations_and_unseen_items(self):
        self.run_collection()
        cutoff = (datetime.now(timezone.utc) - timedelta(days=91)).isoformat()
        with self.store.db:
            self.store.db.execute('UPDATE external_discovery_items SET last_seen=?', (cutoff,))
            self.store.db.execute('UPDATE external_discovery_observations SET observed_at=?', (cutoff,))
        self.responses[self.urls['hacker-news-top']] = (200, b'[]')
        self.responses[self.urls['huggingface-blog-rss']] = (200, b'<rss><channel/></rss>')
        self.run_collection()
        self.assertEqual(self.store.db.execute('select count(*) from external_discovery_items').fetchone()[0], 0)
        self.assertEqual(self.store.db.execute('select count(*) from external_discovery_observations').fetchone()[0], 0)

    def test_all_access_stop_codes_hold_without_retry(self):
        for status in (401, 403, 429, 999):
            with self.subTest(status=status), tempfile.TemporaryDirectory() as directory:
                state = Store(directory)
                responses = dict(self.responses)
                responses[self.urls['hacker-news-top']] = (status, b'')
                calls = []
                result = asyncio.run(collect_external(state, self.config,
                    transport_factory=lambda spec, store: FakeTransport(spec, store, responses, calls)))
                self.assertEqual(result['source_results'][0]['status'], 'held')
                self.assertEqual(calls.count(self.urls['hacker-news-top']), 1)
                self.assertFalse(any('/item/' in url for url in calls))
                state.close()

    def test_rejects_new_source_url_even_if_host_claimed_permitted(self):
        cfg = deepcopy(self.config)
        cfg['sources'][0]['url'] = 'https://www.linkedin.com/search/results/content/'
        cfg['sources'][0]['allowed_hosts'] = ['www.linkedin.com']
        result = self.run_collection(cfg)
        self.assertEqual(result['source_results'][0]['status'], 'error')
        self.assertFalse(any('linkedin.com' in url for url in self.calls))

    def test_rejects_xml_entities_and_continues(self):
        self.responses[self.urls['huggingface-blog-rss']] = (200, b'<!DOCTYPE rss [<!ENTITY x "a">]><rss/>')
        result = self.run_collection()
        self.assertEqual(result['source_results'][1]['status'], 'error')
        self.assertEqual(result['source_results'][0]['status'], 'ok')


if __name__ == '__main__':
    unittest.main()
