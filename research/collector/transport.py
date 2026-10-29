"""Policy-enforcing bounded HTTP transports. No cookies, ambient proxy, or fallback."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import random
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from .contracts import AccessSuspended, CollectionError, ConfigurationError, FetchResult


STOP_CODES = {401, 403, 429, 999}
TRANSIENT_CODES = {408, 425, 500, 502, 503, 504}


def _safe_host(url: str, spec: dict) -> str:
    try:
        p = urlsplit(url)
        if not p.hostname or p.username or p.password:
            raise ValueError
        host = p.hostname.lower().rstrip(".")
    except (ValueError, TypeError):
        raise ConfigurationError("URL must be an HTTPS origin URL without credentials or a custom port") from None
    local = host in {"localhost", "127.0.0.1", "::1"}
    if local:
        if not spec.get("allow_local_test", False) or p.scheme not in {"http", "https"}:
            raise ConfigurationError("Local test URL is disabled")
        return host
    if p.scheme != "https" or p.port not in (None, 443):
        raise ConfigurationError("Non-local source URLs must use HTTPS")
    allowed = [str(h).lower().rstrip(".") for h in spec.get("allowed_hosts", [])]
    if not any(host == h or host.endswith("." + h) for h in allowed):
        raise ConfigurationError("URL host is outside the source allowlist")
    return host


def _retry_after(value: str | None) -> float | None:
    if not value:
        return None
    try:
        return max(0.0, float(value.strip()))
    except (ValueError, TypeError):
        try:
            dt = parsedate_to_datetime(value)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return max(0.0, (dt - datetime.now(timezone.utc)).total_seconds())
        except (TypeError, ValueError, OverflowError):
            return None


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class _BaseTransport:
    def __init__(self, spec: dict, state, *, sleep=asyncio.sleep, rand=random.random):
        self.spec = dict(spec)
        self.state = state
        self._sleep = sleep
        self._rand = rand
        self._locks: dict[str, asyncio.Semaphore] = {}
        self._last_request: dict[str, float] = {}
        self._rate_locks: dict[str, asyncio.Lock] = {}
        methods = self.spec.get("permitted_methods", [])
        if "GET" not in methods:
            raise ConfigurationError("GET is not permitted for this source")
        permissions = self.spec.get("permissions") or {}
        if not (permissions.get("collection") is True or permissions.get("public_read") is True):
            raise ConfigurationError("Source specification does not grant collection permission")
        self._max_bytes = int(self.spec.get("max_bytes", 4_000_000))
        self._timeout = float(self.spec.get("timeout_seconds", 18))
        self._concurrency = max(1, int(self.spec.get("concurrency", 2)))
        self._rate = max(0.01, float(self.spec.get("rate_per_second", 0.5)))
        # Three total attempts is the protocol maximum. Stop statuses are never retried.
        self._attempts = min(3, max(1, int(self.spec.get("max_attempts", 3))))
        if self._max_bytes < 1 or self._timeout <= 0:
            raise ConfigurationError("Invalid response byte or timeout bound")

    def _log(self, *, status=None, attempt=1, byte_count=0, event="response", error_code=None):
        data = {"event": event, "attempt": attempt, "bytes": byte_count}
        if status is not None:
            data["status_code"] = status
        if error_code:
            data["error_code"] = error_code
        self.state.log_request(self.spec.get("source_id", "unknown"), data)

    async def _pace(self, host: str):
        lock = self._rate_locks.setdefault(host, asyncio.Lock())
        async with lock:
            wait = 1.0 / self._rate - (time.monotonic() - self._last_request.get(host, 0.0))
            if wait > 0:
                await self._sleep(wait)
            self._last_request[host] = time.monotonic()

    def _suspended(self):
        key = self.spec.get("access_group") or self.spec.get("source_id") or "unknown"
        suspension = self.state.get_suspension(key)
        if suspension:
            raise AccessSuspended("Source access is suspended")
        return key

    def _suspend(self, key, reason, retry_after=None):
        self.state.suspend(key, reason, retry_after_seconds=retry_after)

    async def _backoff(self, attempt: int, retry_after: float | None = None):
        # Never retry before the server's Retry-After. Long waits suspend this bounded job.
        if retry_after is not None and retry_after > 30:
            key = self.spec.get('access_group') or self.spec.get('source_id') or 'unknown'
            self._suspend(key, 'retry_after_exceeds_job_wait', retry_after)
            raise AccessSuspended('Source suspended until explicit review of Retry-After')
        delay = retry_after if retry_after is not None else min(8.0, 0.25 * (2 ** (attempt - 1)))
        if retry_after is None:
            delay += self._rand() * min(0.25, delay / 4)
        await self._sleep(delay)

    def _redirect(self, current: str, location: str, original_host: str, redirects: int):
        if redirects >= 2:
            raise CollectionError("Redirect limit exceeded")
        target = urljoin(current, location)
        host = _safe_host(target, self.spec)
        if host != original_host:
            raise CollectionError("Cross-host redirect refused")
        return target

    @staticmethod
    def _challenge(url: str, body: bytes) -> bool:
        path = urlsplit(url).path.lower()
        sample = body[:65536].lower()
        challenge_form = b"captcha" in sample and (b"<form" in sample or b"data-sitekey" in sample)
        return any(s in path for s in ("/authwall", "/checkpoint", "/challenge")) or challenge_form or any(
            s in sample for s in (b"verify you are human", b"security check", b"authwall")
        )

    async def aclose(self):
        return None


class HttpxTransport(_BaseTransport):
    """Async HTTPX transport with one pooled client, no ambient proxy, and no cookie storage."""
    def __init__(self, spec: dict, state, *, client_factory=None, **kwargs):
        super().__init__(spec, state, **kwargs)
        self._client_factory = client_factory
        self._client = None
        self._client_lock = asyncio.Lock()

    async def _get_client(self):
        if self._client is not None:
            return self._client
        async with self._client_lock:
            if self._client is None:
                try:
                    import httpx
                except ImportError:
                    raise ConfigurationError("HTTPX is unavailable; install only through the approved project workflow") from None

                class NoCookieStore(httpx.Cookies):
                    def extract_cookies(self, response):
                        # Prevent Set-Cookie from entering the shared client's jar.
                        return None

                factory = self._client_factory or httpx.AsyncClient
                self._client = factory(follow_redirects=False, trust_env=False, timeout=self._timeout,
                                       cookies=NoCookieStore())
        return self._client

    async def _once(self, url, headers):
        client = await self._get_client()
        current = url
        origin_host = urlsplit(url).hostname.lower().rstrip(".")
        for redirects in range(3):
            # Strip sensitive caller headers even when requests share a pooled client.
            api_auth = self.spec.get("adapter") == "linkedin_api" and origin_host == "api.linkedin.com"
            safe_headers = {k: v for k, v in (headers or {}).items()
                            if k.lower() not in {"cookie", "proxy-authorization"}
                            and (k.lower() != "authorization" or (api_auth and isinstance(v,str) and v.startswith("Bearer ")))}
            client.cookies.clear()
            try:
                async with client.stream("GET", current, headers=safe_headers) as response:
                    code = response.status_code
                    rh = {k.lower(): v for k, v in response.headers.items()}
                    if code in {301, 302, 303, 307, 308}:
                        if api_auth:
                            raise CollectionError("Official API redirects are refused")
                        location = rh.get("location")
                        if not location:
                            return code, rh, b"", current
                        current = self._redirect(current, location, origin_host, redirects)
                        continue
                    chunks = bytearray()
                    async for chunk in response.aiter_bytes():
                        chunks.extend(chunk)
                        if len(chunks) > self._max_bytes:
                            raise CollectionError("Response exceeds configured byte cap")
                    return code, rh, bytes(chunks), current
            finally:
                client.cookies.clear()
        raise CollectionError("Redirect limit exceeded")

    async def aclose(self):
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def fetch(self, url, *, headers=None):
        host = _safe_host(url, self.spec)
        key = self._suspended()
        sem = self._locks.setdefault(host, asyncio.Semaphore(self._concurrency))
        async with sem:
            self._suspended()
            for attempt in range(1, self._attempts + 1):
                await self._pace(host)
                self._suspended()
                try:
                    code, response_headers, body, final_url = await self._once(url, headers)
                    if len(body) > self._max_bytes:
                        raise CollectionError("Response exceeds configured byte cap")
                    if code in STOP_CODES:
                        retry_after = _retry_after(response_headers.get("retry-after"))
                        self._suspend(key, f"http_{code}", retry_after)
                        self._log(status=code, attempt=attempt, event="access_suspended")
                        raise AccessSuspended(f"Source access suspended after HTTP {code}")
                    if code == 200 and self._challenge(final_url, body):
                        self._suspend(key, "challenge_page")
                        self._log(status=code, attempt=attempt, event="access_suspended", error_code="challenge_page")
                        raise AccessSuspended("Source access suspended after challenge page")
                    if code in TRANSIENT_CODES and attempt < self._attempts:
                        self._log(status=code, attempt=attempt, event="transient_retry")
                        await self._backoff(attempt, _retry_after(response_headers.get("retry-after")))
                        continue
                    if code < 200 or code >= 300:
                        self._log(status=code, attempt=attempt, event="failed")
                        raise CollectionError(f"Source returned HTTP {code}")
                    self._log(status=code, attempt=attempt, byte_count=len(body))
                    return FetchResult(url=final_url, body=body, status_code=code, headers=response_headers)
                except AccessSuspended:
                    raise
                except CollectionError:
                    raise
                except Exception as exc:
                    if attempt >= self._attempts:
                        self._log(attempt=attempt, event="failed", error_code=type(exc).__name__)
                        raise CollectionError("Transport failed after bounded retries") from None
                    self._log(attempt=attempt, event="transient_retry", error_code=type(exc).__name__)
                    await self._backoff(attempt)
        raise CollectionError("Transport failed")

class UrllibTransport(_BaseTransport):
    """Async-compatible stdlib comparator for same-input transport benchmarks."""
    def _sync_once(self, url, headers):
        current = url
        origin_host = urlsplit(url).hostname.lower().rstrip(".")
        opener = build_opener(ProxyHandler({}), _NoRedirect())
        for redirects in range(3):
            req_headers = {k: v for k, v in (headers or {}).items() if k.lower() not in {"cookie", "authorization", "proxy-authorization"}}
            req = Request(current, headers=req_headers, method="GET")
            try:
                response = opener.open(req, timeout=self._timeout)
            except HTTPError as exc:
                response = exc
            except (URLError, TimeoutError, OSError):
                raise
            code = getattr(response, "status", response.code)
            rh = {k.lower(): v for k, v in response.headers.items()}
            if code in {301, 302, 303, 307, 308}:
                location = rh.get("location")
                response.close()
                if not location:
                    return code, rh, b"", current
                current = self._redirect(current, location, origin_host, redirects)
                continue
            body = response.read(self._max_bytes + 1)
            response.close()
            if len(body) > self._max_bytes:
                raise CollectionError("Response exceeds configured byte cap")
            return code, rh, body, current
        raise CollectionError("Redirect limit exceeded")

    async def fetch(self, url, *, headers=None):
        host = _safe_host(url, self.spec)
        key = self._suspended()
        sem = self._locks.setdefault(host, asyncio.Semaphore(self._concurrency))
        async with sem:
            self._suspended()
            for attempt in range(1, self._attempts + 1):
                await self._pace(host)
                self._suspended()
                try:
                    code, response_headers, body, final_url = await asyncio.to_thread(self._sync_once, url, headers)
                    if len(body) > self._max_bytes:
                        raise CollectionError("Response exceeds configured byte cap")
                    if code in STOP_CODES:
                        retry_after = _retry_after(response_headers.get("retry-after"))
                        self._suspend(key, f"http_{code}", retry_after)
                        self._log(status=code, attempt=attempt, event="access_suspended")
                        raise AccessSuspended(f"Source access suspended after HTTP {code}")
                    if code == 200 and HttpxTransport._challenge(final_url, body):
                        self._suspend(key, "challenge_page")
                        self._log(status=code, attempt=attempt, event="access_suspended", error_code="challenge_page")
                        raise AccessSuspended("Source access suspended after challenge page")
                    if code in TRANSIENT_CODES and attempt < self._attempts:
                        self._log(status=code, attempt=attempt, event="transient_retry")
                        await self._backoff(attempt, _retry_after(response_headers.get("retry-after")))
                        continue
                    if code < 200 or code >= 300:
                        self._log(status=code, attempt=attempt, event="failed")
                        raise CollectionError(f"Source returned HTTP {code}")
                    self._log(status=code, attempt=attempt, byte_count=len(body))
                    return FetchResult(url=final_url, body=body, status_code=code, headers=response_headers)
                except AccessSuspended:
                    raise
                except CollectionError:
                    raise
                except Exception as exc:
                    if attempt >= self._attempts:
                        self._log(attempt=attempt, event="failed", error_code=type(exc).__name__)
                        raise CollectionError("Transport failed after bounded retries") from None
                    self._log(attempt=attempt, event="transient_retry", error_code=type(exc).__name__)
                    await self._backoff(attempt)
        raise CollectionError("Transport failed")


# Preferred spelling retained alongside the documented class name.
HTTPXTransport = HttpxTransport
