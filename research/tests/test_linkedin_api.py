import json
import tempfile
import unittest
from pathlib import Path

from research.collector.contracts import AccessSuspended, CollectionError, ConfigurationError, FetchResult
from research.collector.linkedin_api import ReadonlyLinkedInAPIAdapter
from research.collector.store import Store


ORG = "urn:li:organization:12345"
TOKEN = {"access_token": "fake-token", "expires_at": 4102444800,
         "scope": "r_organization_social, r_organization_social_feed, r_member_social", "authorized_actors": [{"urn": ORG, "type": "organization"}]}


class FakeState:
    def __init__(self): self.stops = []
    def suspend(self, *args): self.stops.append(args)


class FakeTransport:
    def __init__(self, pages):
        self.pages = list(pages); self.calls = []; self.state = FakeState()
    async def fetch(self, url, headers=None):
        self.calls.append((url, dict(headers or {})))
        status, body, response_headers = self.pages.pop(0)
        return FetchResult(url=url, body=json.dumps(body).encode(), status_code=status, headers=response_headers)


class LinkedInAPITests(unittest.IsolatedAsyncioTestCase):
    async def test_posts_are_paginated_with_version_and_normalized_without_invented_dates(self):
        first = {"elements": [{"id": "urn:li:share:111", "commentary": {"text": "Owned source copy"},
                               "createdAt": None, "lifecycleState": "PUBLISHED",
                               "socialDetail": {"numLikes": 5}}],
                 "paging": {"start": 0, "count": 1, "total": 2}}
        second = {"elements": [{"id": "urn:li:share:222", "commentary": "Second post",
                                "createdAt": {"time": 1700000000000}}],
                  "paging": {"start": 1, "count": 1, "total": 2}}
        transport = FakeTransport([(200, first, {}), (200, second, {})])
        spec = {"source_id": "li-api-test", "api_version": "202610", "operations": ["posts"],
                "actors": [{"urn": ORG, "type": "organization"}], "allowed_resources": [ORG],
                "permitted_methods": ["GET"], "licensing": "owner-approved-internal",
                "auth_basis": "explicit-owner-consent"}
        records = await ReadonlyLinkedInAPIAdapter().collect(spec, transport, Path("."), lambda _: False, TOKEN)
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0]["text"], "Owned source copy")
        self.assertIsNone(records[0]["published_at"])
        self.assertEqual(records[0]["extracted_fields"]["counters"]["numLikes"], 5)
        self.assertEqual(records[0]["_raw"], json.dumps(first).encode())
        self.assertEqual(records[0]["processing_status"], "pending_review")
        self.assertEqual(records[0]["permissions"]["licensing"], "owner-approved-internal")
        self.assertEqual(records[0]["permissions"]["authorization_basis"], "explicit-owner-consent")
        self.assertEqual(records[0]["permissions"]["source_endpoint"], "/rest/posts?q=author")
        self.assertIn("start=1", transport.calls[1][0])
        self.assertEqual(transport.calls[0][1]["LinkedIn-Version"], "202610")
        self.assertEqual(transport.calls[0][1]["X-Restli-Protocol-Version"], "2.0.0")

    async def test_missing_scope_or_actor_is_rejected_before_network(self):
        transport = FakeTransport([])
        spec = {"operations": ["posts"], "authorized_actors": [{"urn": ORG, "type": "organization"}],
                "allowed_resources": [ORG]}
        with self.assertRaises(ConfigurationError):
            await ReadonlyLinkedInAPIAdapter().collect(spec, transport, Path("."), lambda _: False,
                {**TOKEN, "scope": "r_member_social"})
        with self.assertRaises(ConfigurationError):
            await ReadonlyLinkedInAPIAdapter().collect({**spec, "authorized_actors": [
                {"urn": "urn:li:organization:999", "type": "organization"}]}, transport,
                Path("."), lambda _: False, TOKEN)
        self.assertEqual(transport.calls, [])

    async def test_api_version_and_global_search_are_not_accepted(self):
        transport = FakeTransport([])
        spec = {"api_version": "202613", "operations": ["posts"],
                "authorized_actors": [{"urn": ORG, "type": "organization"}], "allowed_resources": [ORG]}
        with self.assertRaises(ConfigurationError):
            await ReadonlyLinkedInAPIAdapter().collect(spec, transport, Path("."), lambda _: False, TOKEN)
        with self.assertRaises(ConfigurationError):
            await ReadonlyLinkedInAPIAdapter().collect({**spec, "api_version": "202610",
                "operations": ["keyword_search"]}, transport, Path("."), lambda _: False, TOKEN)
        self.assertEqual(transport.calls, [])

    async def test_access_denials_suspend_without_fallback(self):
        transport = FakeTransport([(429, {"message": "do not expose"}, {"Retry-After": "60"})])
        spec = {"operations": ["posts"], "authorized_actors": [{"urn": ORG, "type": "organization"}],
                "allowed_resources": [ORG]}
        with self.assertRaises(AccessSuspended):
            await ReadonlyLinkedInAPIAdapter().collect(spec, transport, Path("."), lambda _: False, TOKEN)
        self.assertEqual(len(transport.calls), 1)
        self.assertEqual(transport.state.stops[0][1:], ("http_429", 60))

    async def test_out_of_allowlist_pagination_link_is_rejected(self):
        body = {"elements": [], "paging": {"links": [{"rel": "next", "href": "https://evil.example/rest/posts?start=1"}]}}
        transport = FakeTransport([(200, body, {})])
        spec = {"operations": ["posts"], "authorized_actors": [{"urn": ORG, "type": "organization"}],
                "allowed_resources": [ORG]}
        with self.assertRaises(ConfigurationError):
            await ReadonlyLinkedInAPIAdapter().collect(spec, transport, Path("."), lambda _: False, TOKEN)

    async def test_known_posts_are_not_returned_again(self):
        body = {"elements": [{"id": "urn:li:share:111", "commentary": "Known"}],
                "paging": {"start": 0, "count": 1, "total": 1}}
        transport = FakeTransport([(200, body, {})])
        spec = {"operations": ["posts"], "authorized_actors": [{"urn": ORG, "type": "organization"}],
                "allowed_resources": [ORG]}
        rows = await ReadonlyLinkedInAPIAdapter().collect(spec, transport, Path("."), lambda _: True, TOKEN)
        self.assertEqual(rows, [])

    async def test_comments_require_explicit_post_ids_and_read_scope(self):
        post_id = "urn:li:share:900"
        body = {"elements": [{"id": "9001", "message": {"text": "Original comment text"},
                              "created": {"time": 1700000000000}}],
                "paging": {"start": 0, "count": 1, "total": 1}}
        transport = FakeTransport([(200, body, {})])
        spec = {"operations": ["comments"], "authorized_actors": [{"urn": ORG, "type": "organization"}],
                "allowed_resources": [ORG, post_id], "post_ids": [post_id]}
        rows = await ReadonlyLinkedInAPIAdapter().collect(spec, transport, Path("."), lambda _: False, TOKEN)
        self.assertEqual(rows[0]["text"], "Original comment text")
        self.assertEqual(rows[0]["content_type"], "linkedin_comment")
        self.assertIn("/socialActions/urn%3Ali%3Ashare%3A900/comments", transport.calls[0][0])
        self.assertEqual(len(transport.calls), 1)

    async def test_org_metadata_and_analytics_require_explicit_verified_scope(self):
        metadata_spec = {"operations": ["organization"], "actors": [{"urn": ORG, "type": "organization"}],
                         "allowed_resources": [ORG]}
        transport = FakeTransport([])
        with self.assertRaises(ConfigurationError):
            await ReadonlyLinkedInAPIAdapter().collect(metadata_spec, transport, Path("."), lambda _: False, TOKEN)
        self.assertEqual(transport.calls, [])
        stats = {"elements": [{"organizationalEntity": ORG, "timeRange": {"start": 1700000000000},
                                "totalShareStatistics": {"impressions": 7}}],
                 "paging": {"start": 0, "count": 1, "total": 1}}
        transport = FakeTransport([(200, stats, {})])
        spec = {**metadata_spec, "operations": ["analytics"],
                "required_scopes": {"analytics": "r_organization_social"}}
        rows = await ReadonlyLinkedInAPIAdapter().collect(spec, transport, Path("."), lambda _: False, TOKEN)
        self.assertEqual(rows[0]["content_type"], "linkedin_organization_analytics")
        self.assertEqual(rows[0]["permissions"]["required_scope"], "r_organization_social")

    async def test_page_cap_reports_incomplete_result(self):
        first = {"elements": [{"id": "urn:li:share:1", "commentary": "A"}],
                 "paging": {"start": 0, "count": 1, "total": 2}}
        transport = FakeTransport([(200, first, {})])
        spec = {"operations": ["posts"], "max_pages": 1,
                "authorized_actors": [{"urn": ORG, "type": "organization"}], "allowed_resources": [ORG]}
        with self.assertRaisesRegex(CollectionError, "page cap reached"):
            await ReadonlyLinkedInAPIAdapter().collect(spec, transport, Path("."), lambda _: False, TOKEN)

    async def test_callback_preserves_first_page_records_before_later_access_stop(self):
        first = {"elements": [{"id": "urn:li:share:333", "commentary": "Persist this first"}],
                 "paging": {"start": 0, "count": 1, "total": 2}}
        transport = FakeTransport([(200, first, {}), (403, {"message": "redact me"}, {})])
        spec = {"operations": ["posts"], "actors": [{"urn": ORG, "type": "organization"}],
                "allowed_resources": [ORG], "permitted_methods": ["GET"]}
        with tempfile.TemporaryDirectory() as directory:
            store = Store(Path(directory))
            try:
                with self.assertRaises(AccessSuspended):
                    await ReadonlyLinkedInAPIAdapter().collect(spec, transport, Path(directory), lambda _: False,
                                                               TOKEN, on_record=store.ingest)
                self.assertEqual(store.counts()["records"], 1)
                pending = store.pending()[0]
                self.assertEqual(pending["external_id"], "urn:li:share:333")
                self.assertEqual(store.raw_bytes(pending["raw_sha256"]), json.dumps(first).encode())
            finally:
                store.close()
        self.assertEqual(len(transport.calls), 2)


if __name__ == "__main__":
    unittest.main()
