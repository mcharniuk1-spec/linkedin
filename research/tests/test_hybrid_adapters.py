import asyncio
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
from pathlib import Path
import sys
import threading
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "pipeline"))
from collector.adapters import FeedAdapter, GenericAPIAdapter, PlaywrightAdapter, ScrapyAdapter, StaticHTTPAdapter
from collector.contracts import AccessSuspended, ConfigurationError, FetchResult
from collector.transport import UrllibTransport
from synthetic_cycle import FIXTURES, records


class FakeTransport:
    def __init__(self, bodies):
        self.bodies = bodies
        self.calls = []

    async def fetch(self, url, *, headers=None):
        self.calls.append(url)
        value = self.bodies[url]
        if isinstance(value, Exception):
            raise value
        if isinstance(value, FetchResult):
            return value
        return FetchResult(url=url, body=value, status_code=200)


def source(**kw):
    return {"source_id": "fixture", "allowed_hosts": ["example.test"], "permitted_methods": ["GET"],
            "permissions": {"public_read": True}, **kw}


class AdapterTests(unittest.IsolatedAsyncioTestCase):
    async def test_generic_static_requires_selector_and_skips_known_before_fetch(self):
        url = "https://example.test/page"
        transport = FakeTransport({url: b"<main><p>Selected text</p><aside>Noise</aside></main>"})
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ConfigurationError):
                await StaticHTTPAdapter().collect(source(url=url), transport, td, lambda _: False)
            rows = await StaticHTTPAdapter().collect(source(url=url, text_selector="main p"), transport, td, lambda u: u == url)
            self.assertEqual(rows, [])
            self.assertEqual(transport.calls, [])
            rows = await StaticHTTPAdapter().collect(source(url=url, text_selector="main p"), transport, td, lambda _: False)
            self.assertEqual(rows[0]["text"], "Selected text")
            self.assertNotIn("Noise", rows[0]["text"])
            self.assertTrue(Path(rows[0]["extracted_fields"]["raw_path"]).exists())

    async def test_linkedin_static_reuses_normalizer_and_emits_identity_aliases(self):
        posts, _, _ = records()
        post = posts[0]
        body = Path(post["source"]["raw_path"]).read_bytes()
        url = post["url"]
        transport = FakeTransport({url: body})
        cfg = source(source_id="linkedin_public", allowed_hosts=["linkedin.com"], url=url)
        with tempfile.TemporaryDirectory() as td:
            rows = await StaticHTTPAdapter().collect(cfg, transport, td, lambda _: False)
        row = rows[0]
        aliases = set(row["identity_aliases"])
        self.assertIn("id:" + post["id"], aliases)
        self.assertIn("url:" + post["url"], aliases)
        if post["attributed_urn"]:
            self.assertIn("id:" + post["attributed_urn"], aliases)
        self.assertEqual(row["legacy_record"]["source"]["sha256"], post["source"]["sha256"])

    async def test_feed_rss_atom_and_dtd_rejection(self):
        rss_url = "https://example.test/feed.xml"
        rss = b'<rss><channel><item><guid>x</guid><title>T</title><description>S</description><link>https://example.test/x</link></item></channel></rss>'
        transport = FakeTransport({rss_url: rss})
        with tempfile.TemporaryDirectory() as td:
            rows = await FeedAdapter().collect(source(url=rss_url), transport, td, lambda _: False)
        self.assertEqual(rows[0]["text"], "T\nS")
        atom_url = "https://example.test/atom"
        atom = b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><id>1</id><title>A</title><summary>B</summary><link href="https://example.test/a"/></entry></feed>'
        with tempfile.TemporaryDirectory() as td:
            rows = await FeedAdapter().collect(source(url=atom_url), FakeTransport({atom_url: atom}), td, lambda _: False)
        self.assertEqual(rows[0]["source_url"], "https://example.test/a")
        evil = b'<!DOCTYPE x [<!ENTITY e "bad">]><rss><channel/></rss>'
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ConfigurationError):
                await FeedAdapter().collect(source(url=rss_url), FakeTransport({rss_url: evil}), td, lambda _: False)

    async def test_json_api_bounded_pagination_and_known_url(self):
        p1, p2 = "https://example.test/api?page=1", "https://example.test/api?page=2"
        payload1 = b'{"data":[{"id":"1","url":"https://example.test/a","text":"first"}],"next":"https://example.test/api?page=2"}'
        payload2 = b'{"data":[{"id":"2","url":"https://example.test/b","text":"second"}],"next":null}'
        transport = FakeTransport({p1: payload1, p2: payload2})
        cfg = source(url=p1, items_path="data", next_url_path="next", max_pages=2)
        with tempfile.TemporaryDirectory() as td:
            rows = await GenericAPIAdapter().collect(cfg, transport, td, lambda u: u.endswith("/a"))
        self.assertEqual([x["external_id"] for x in rows], ["2"])
        self.assertEqual(transport.calls, [p1, p2])
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ConfigurationError):
                await GenericAPIAdapter().collect(source(url=p1, items_path="data", token="secret"), transport, td, lambda _: False)

    async def test_callback_commits_partial_page_before_later_access_stop(self):
        from collector.contracts import AccessSuspended
        p1, p2 = "https://example.test/api?page=1", "https://example.test/api?page=2"
        payload1 = b'{"data":[{"id":"1","url":"https://example.test/a","text":"first"}],"next":"https://example.test/api?page=2"}'
        transport = FakeTransport({p1: payload1, p2: AccessSuspended("stopped")})
        persisted = []
        cfg = source(url=p1, items_path="data", next_url_path="next", max_pages=2)
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(AccessSuspended):
                await GenericAPIAdapter().collect(cfg, transport, td, lambda _: False, on_record=persisted.append)
        self.assertEqual([row["external_id"] for row in persisted], ["1"])
        self.assertEqual(transport.calls, [p1, p2])

    async def test_optional_workers_require_explicit_method_and_never_target_linkedin(self):
        cfg = source(url="https://linkedin.com/posts/x", allowed_hosts=["linkedin.com"], js_required=True,
                     method="permitted_js_rendering")
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ConfigurationError):
                await PlaywrightAdapter().collect(cfg, FakeTransport({}), td, lambda _: False)
            with self.assertRaises(ConfigurationError):
                await ScrapyAdapter().collect(source(url="https://example.test/"), FakeTransport({}), td, lambda _: False)

    @unittest.skipUnless(importlib.util.find_spec("scrapy"), "optional Scrapy 2.19 runtime not installed")
    async def test_scrapy_local_fixture_persists_before_later_stop_and_sends_no_later_request(self):
        hits = []
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                hits.append(self.path)
                if self.path == "/two":
                    self.send_response(429); self.send_header("Retry-After", "0"); self.end_headers(); return
                body = b"<main><p>Observed source text for this local fixture page.</p></main>"
                self.send_response(200); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
            def log_message(self, *_):
                return
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        try:
            base = f"http://127.0.0.1:{server.server_port}"
            urls = [base + "/one", base + "/two", base + "/three"]
            state = type("State", (), {
                "__init__": lambda self: (setattr(self, "suspensions", {}), setattr(self, "logs", [])) and None,
                "get_suspension": lambda self, key: self.suspensions.get(key),
                "suspend": lambda self, key, reason, retry_after_seconds=None: self.suspensions.__setitem__(key, {"reason": reason, "retry_after_seconds": retry_after_seconds}),
                "log_request": lambda self, source, event: self.logs.append((source, event)),
            })()
            spec_scrapy = {"source_id": "local_fixture", "access_group": "local_fixture", "allowed_hosts": [],
                           "permitted_methods": ["GET"], "permissions": {"collection": True}, "allow_local_test": True,
                           "urls": urls, "high_volume": True, "method": "permitted_scrapy_crawl", "max_urls": 3,
                           "concurrency": 1, "rate_per_second": 10000, "timeout_seconds": 2,
                           "max_bytes": 10000, "text_selector": "main p"}
            transport = UrllibTransport(spec_scrapy, state)
            persisted = []
            with tempfile.TemporaryDirectory() as td:
                with self.assertRaises(AccessSuspended):
                    await ScrapyAdapter().collect(spec_scrapy, transport, td, lambda _: False, on_record=persisted.append)
            self.assertEqual([x["text"] for x in persisted], ["Observed source text for this local fixture page."])
            self.assertEqual(hits, ["/one", "/two"])
            self.assertTrue(state.suspensions["local_fixture"])
        finally:
            server.shutdown(); thread.join(timeout=2); server.server_close()


if __name__ == "__main__":
    unittest.main()
