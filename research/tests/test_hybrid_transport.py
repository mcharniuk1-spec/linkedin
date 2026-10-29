import asyncio
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys
import threading
import unittest
import httpx

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from collector.contracts import AccessSuspended, ConfigurationError, CollectionError
from collector.transport import HttpxTransport, UrllibTransport


class State:
    def __init__(self):
        self.suspended = {}
        self.logs = []

    def get_suspension(self, key):
        return self.suspended.get(key)

    def suspend(self, key, reason, retry_after_seconds=None):
        self.suspended[key] = {"reason": reason, "retry_after_seconds": retry_after_seconds}

    def log_request(self, source_id, event):
        self.logs.append((source_id, dict(event)))


class StubHTTPX(HttpxTransport):
    def __init__(self, *args, responses, **kwargs):
        super().__init__(*args, **kwargs)
        self.responses = list(responses)
        self.calls = []

    async def _once(self, url, headers):
        self.calls.append((url, headers))
        item = self.responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


def spec(**kw):
    return {"source_id": "fixture", "access_group": "fixture-group", "allowed_hosts": ["example.test"],
            "permitted_methods": ["GET"], "permissions": {"public_read": True},
            "rate_per_second": 100000, "timeout_seconds": 1, "max_bytes": 5, "max_attempts": 3, **kw}


class TransportTests(unittest.IsolatedAsyncioTestCase):
    async def test_actual_urllib_local_fixture_redirect_and_stop(self):
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/redirect":
                    self.send_response(302); self.send_header("Location", "/ok"); self.end_headers(); return
                if self.path == "/429":
                    self.send_response(429); self.send_header("Retry-After", "4"); self.end_headers(); return
                body = b"fixture"
                self.send_response(200); self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
            def log_message(self, *_):
                return
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        try:
            base = f"http://127.0.0.1:{server.server_port}"
            state = State()
            t = UrllibTransport(spec(allowed_hosts=[], allow_local_test=True, max_bytes=32), state)
            self.assertEqual((await t.fetch(base + "/redirect")).body, b"fixture")
            with self.assertRaises(AccessSuspended):
                await t.fetch(base + "/429")
            self.assertEqual(state.suspended["fixture-group"]["retry_after_seconds"], 4.0)
        finally:
            server.shutdown(); thread.join(timeout=2); server.server_close()

    async def test_actual_httpx_mock_transport_strips_auth_cookies_and_follows_same_host(self):
        seen, clients = [], []
        def handler(request):
            seen.append(request)
            if request.url.path == "/start":
                return httpx.Response(302, headers={"Location": "/done", "Set-Cookie": "sid=private"})
            return httpx.Response(200, content=b"ok", headers={"Set-Cookie": "sid=private"})
        def factory(**kwargs):
            clients.append(1)
            return httpx.AsyncClient(transport=httpx.MockTransport(handler), **kwargs)
        t = HttpxTransport(spec(max_bytes=64), State(), client_factory=factory)
        result = await t.fetch("https://example.test/start", headers={"Authorization": "secret", "Cookie": "session=secret"})
        self.assertEqual(result.body, b"ok")
        await asyncio.gather(t.fetch("https://example.test/check-a"), t.fetch("https://example.test/check-b"))
        self.assertEqual([r.url.path for r in seen], ["/start", "/done", "/check-a", "/check-b"])
        self.assertEqual(len(clients), 1)
        self.assertTrue(all("cookie" not in r.headers and "authorization" not in r.headers for r in seen))
        await t.aclose()
        self.assertIsNone(t._client)

    async def test_allowlist_https_credentials_and_local_exception(self):
        state = State()
        t = StubHTTPX(spec(), state, responses=[(200, {}, b"ok", "https://www.example.test/page")])
        result = await t.fetch("https://example.test/page")
        self.assertEqual(result.body, b"ok")
        for url in ("http://example.test/", "https://badexample.test/", "https://user:pw@example.test/"):
            with self.assertRaises(ConfigurationError):
                await t.fetch(url)
        with self.assertRaises(ConfigurationError):
            await StubHTTPX(spec(allow_local_test=False), state, responses=[]).fetch("http://127.0.0.1:8/")
        local = StubHTTPX(spec(allow_local_test=True, allowed_hosts=[]), state,
                          responses=[(200, {}, b"ok", "http://127.0.0.1:8/")])
        self.assertEqual((await local.fetch("http://127.0.0.1:8/" )).body, b"ok")

    async def test_stop_is_persistent_and_never_retried(self):
        state = State()
        t = StubHTTPX(spec(), state, responses=[(429, {"retry-after": "7"}, b"", "https://example.test/")])
        with self.assertRaises(AccessSuspended):
            await t.fetch("https://example.test/")
        self.assertEqual(len(t.calls), 1)
        self.assertEqual(state.suspended["fixture-group"]["retry_after_seconds"], 7.0)
        with self.assertRaises(AccessSuspended):
            await t.fetch("https://example.test/next")
        self.assertEqual(len(t.calls), 1)
        self.assertNotIn("url", state.logs[0][1])

    async def test_transient_retry_after_then_success(self):
        state, sleeps = State(), []
        async def sleep(delay):
            sleeps.append(delay)
        t = StubHTTPX(spec(), state, responses=[(503, {"retry-after": "2"}, b"", "https://example.test/"),
                                               (200, {}, b"ok", "https://example.test/")], sleep=sleep)
        result = await t.fetch("https://example.test/")
        self.assertEqual(result.body, b"ok")
        self.assertEqual(len(t.calls), 2)
        self.assertEqual(sleeps, [2.0])

    async def test_challenge_and_byte_cap_stop_or_fail_closed(self):
        state = State()
        t = StubHTTPX(spec(max_bytes=64), state, responses=[(200, {}, b"<form id='captcha'>check</form>", "https://example.test/")])
        with self.assertRaises(AccessSuspended):
            await t.fetch("https://example.test/")
        t2 = StubHTTPX(spec(max_bytes=5), State(), responses=[(200, {}, b"123456", "https://example.test/")])
        with self.assertRaises(CollectionError):
            await t2.fetch("https://example.test/")

    async def test_same_host_redirect_limit_and_no_cross_host(self):
        t = StubHTTPX(spec(), State(), responses=[])
        self.assertEqual(t._redirect("https://example.test/a", "/b", "example.test", 0), "https://example.test/b")
        with self.assertRaises(CollectionError):
            t._redirect("https://example.test/a", "https://other.test/b", "example.test", 0)
        with self.assertRaises(CollectionError):
            t._redirect("https://example.test/a", "/b", "example.test", 2)

    async def test_urllib_and_httpx_share_spec_policy(self):
        t = UrllibTransport(spec(), State())
        with self.assertRaises(ConfigurationError):
            await t.fetch("https://outside.test/")
        await t.aclose()


if __name__ == "__main__":
    unittest.main()
