"""Optional finite Scrapy runner backed only by the approved collector transport."""
from __future__ import annotations

import hashlib
from pathlib import Path
from urllib.parse import urlsplit

from bs4 import BeautifulSoup

from .contracts import AccessSuspended, CollectionError, ConfigurationError, record
from .transport import _safe_host
from .adapters import _store_raw


async def collect_scrapy(spec, transport, workspace, known_url, on_record=None):
    """Run a finite list of explicitly permitted static pages through Scrapy's async engine.

    Scrapy never opens a socket here: its custom HTTP/HTTPS handlers delegate every
    request to ``transport.fetch``. This keeps host, stop, retry, cookie, proxy,
    redirect, byte, concurrency, and rate controls in the shared transport.
    """
    try:
        import scrapy
        from scrapy.crawler import AsyncCrawlerRunner
        from scrapy.exceptions import CloseSpider
        from scrapy.http import HtmlResponse
        from scrapy.settings import Settings
    except ImportError:
        raise ConfigurationError("Scrapy 2.19 async support is unavailable; no package will be installed") from None
    import re
    version = tuple(int(x) for x in re.findall(r"\d+", scrapy.__version__)[:2])
    if version < (2, 19):
        raise ConfigurationError("Optional Scrapy route requires version 2.19 or newer")

    urls = spec.get("urls", [spec.get("url")])
    urls = [u for u in urls if isinstance(u, str) and u]
    limit = min(500, max(0, int(spec.get("max_urls", spec.get("max_pages", 0)))))
    if not limit:
        return []
    urls = urls[:limit]
    if not spec.get("text_selector"):
        raise ConfigurationError("Scrapy static collection requires an explicit text_selector")
    if any("linkedin.com" == h.lower().lstrip(".") or h.lower().endswith(".linkedin.com") for h in spec.get("allowed_hosts", [])):
        raise ConfigurationError("Scrapy static adapter does not collect LinkedIn; use its dedicated normalizer adapter")

    selected = []
    for url in urls:
        _safe_host(url, spec)
        if not known_url(url):
            selected.append(url)
    if not selected:
        return []
    rows, failures = [], []
    source_id = spec.get("source_id", "scrapy_static")
    workspace = Path(workspace)

    class PolicyDownloadHandler:
        lazy = True

        @classmethod
        def from_crawler(cls, crawler):
            return cls()

        async def download_request(self, request):
            try:
                # Scrapy's headers are deliberately not forwarded; the shared transport owns headers.
                result = await transport.fetch(request.url)
                return HtmlResponse(url=result.url, status=result.status_code,
                                    headers=result.headers, body=result.body,
                                    request=request, encoding="utf-8")
            except Exception as exc:
                failures.append(exc)
                # Scrapy receives a request failure, but cannot retry or use another downloader.
                raise scrapy.exceptions.IgnoreRequest("Shared source transport refused request") from None

        async def close(self):
            return None

    class FiniteStaticSpider(scrapy.Spider):
        name = "permission_bounded_static_source"

        async def start(self):
            for url in selected:
                yield scrapy.Request(url, callback=self.parse, dont_filter=False,
                                     headers={"User-Agent": "OutspokenPublicResearch/0.5"})

        def parse(self, response):
            body = response.body
            if transport._challenge(response.url, body):
                key = spec.get("access_group") or source_id
                transport._suspend(key, "challenge_page")
                transport.state.log_request(source_id, {"event": "access_suspended", "error_code": "challenge_page"})
                exc = AccessSuspended("Source access suspended after challenge page")
                failures.append(exc)
                raise scrapy.exceptions.CloseSpider("source_access_suspended")
            digest, raw_path = _store_raw(workspace, body, ".html")
            soup = BeautifulSoup(body, "html.parser")
            node = soup.select_one(spec["text_selector"])
            if node is None:
                return None
            text = node.get_text(" ", strip=True)
            if not text:
                return None
            id_node = soup.select_one(spec.get("id_selector", "")) if spec.get("id_selector") else None
            external_id = (id_node.get(spec.get("id_attribute", "id")) if id_node else None) or response.url
            author_node = soup.select_one(spec.get("author_selector", "")) if spec.get("author_selector") else None
            date_node = soup.select_one(spec.get("date_selector", "")) if spec.get("date_selector") else None
            row = record(source_id=source_id, external_id=str(external_id), source_url=response.url,
                         content_type="static_page", text=text,
                         author=author_node.get_text(" ", strip=True) if author_node else None,
                         published_at=(date_node.get(spec.get("date_attribute", "datetime")) or date_node.get_text(" ", strip=True)) if date_node else None,
                         extracted_fields={"raw_sha256": digest, "raw_path": str(raw_path)},
                         permissions=spec["permissions"], identity_aliases=["url:" + response.url], raw=body)
            rows.append(row)
            if on_record is not None:
                try:
                    on_record(row)
                except Exception as exc:
                    failures.append(exc)
                    raise CloseSpider("store_callback_failed") from None
            return None

    settings = Settings({
        "TWISTED_REACTOR_ENABLED": False,
        "LOG_ENABLED": False,
        "TELNETCONSOLE_ENABLED": False,
        "COOKIES_ENABLED": False,
        "ROBOTSTXT_OBEY": False,
        "RETRY_ENABLED": False,
        "REDIRECT_ENABLED": False,
        "DOWNLOAD_HANDLERS": {"http": PolicyDownloadHandler, "https": PolicyDownloadHandler},
        "DOWNLOADER_MIDDLEWARES": {
            "scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware": None,
            "scrapy.downloadermiddlewares.cookies.CookiesMiddleware": None,
            "scrapy.downloadermiddlewares.retry.RetryMiddleware": None,
            "scrapy.downloadermiddlewares.redirect.RedirectMiddleware": None,
        },
        "CONCURRENT_REQUESTS": min(transport._concurrency, max(1, int(spec.get("concurrency", transport._concurrency)))),
        "DOWNLOAD_TIMEOUT": transport._timeout,
        "DOWNLOAD_MAXSIZE": transport._max_bytes,
        "USER_AGENT": "OutspokenPublicResearch/0.5",
    })
    runner = AsyncCrawlerRunner(settings)
    await runner.crawl(FiniteStaticSpider)
    if failures:
        # Preserve already emitted records and surface the first failure to the caller.
        raise failures[0]
    return rows
