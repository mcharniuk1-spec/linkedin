"""Static-page, feed and explicitly configured JSON source adapters."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup

from .contracts import AccessSuspended, ConfigurationError, record
from .transport import _safe_host


def _authorized(spec: dict, method="GET"):
    if method not in spec.get("permitted_methods", []):
        raise ConfigurationError(f"{method} is not permitted by this source specification")
    permissions = spec.get("permissions") or {}
    if not (permissions.get("collection") is True or permissions.get("public_read") is True):
        raise ConfigurationError("Source specification does not grant collection permission")


def _urls(spec):
    values = spec.get("urls", [spec.get("url")])
    return [u for u in values if isinstance(u, str) and u]


def _store_raw(workspace, body, suffix):
    digest = hashlib.sha256(body).hexdigest()
    path = Path(workspace) / "raw" / (digest + suffix)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != body:
            raise ValueError("Content-addressed source hash collision")
    else:
        path.write_bytes(body)
    return digest, path


def _selector(soup, selector):
    if not selector:
        return None
    return soup.select_one(selector)


def _emit(out, row, on_record):
    out.append(row)
    if on_record is not None:
        on_record(row)


class StaticHTTPAdapter:
    async def collect(self, spec, transport, workspace, known_url, on_record=None):
        _authorized(spec)
        source_id = spec.get("source_id", "static")
        linkedin = any(h == "linkedin.com" or h.endswith(".linkedin.com") for h in spec.get("allowed_hosts", []))
        selector = spec.get("text_selector")
        if not linkedin and not selector:
            raise ConfigurationError("Generic static pages require an explicit text_selector")
        root = Path(workspace)
        out = []
        max_pages = min(int(spec.get("max_pages", 100)), len(_urls(spec)))
        for url in _urls(spec)[:max_pages]:
            _safe_host(url, spec)
            canonical = _canonical_linkedin(url) if linkedin else url
            if known_url(canonical):
                continue
            result = await transport.fetch(url)
            digest, raw_path = _store_raw(root, result.body, ".html")
            soup = BeautifulSoup(result.body, "html.parser")
            if linkedin:
                _emit(out, _linkedin_record(source_id, canonical, result, raw_path, soup, spec), on_record)
            else:
                node = _selector(soup, selector)
                if node is None:
                    continue
                text = node.get_text(" ", strip=True)
                if not text:
                    continue
                ext_node = _selector(soup, spec.get("id_selector"))
                external_id = (ext_node.get(spec.get("id_attribute", "id")) if ext_node else None) or canonical
                author_node = _selector(soup, spec.get("author_selector"))
                date_node = _selector(soup, spec.get("date_selector"))
                _emit(out, record(source_id=source_id, external_id=str(external_id), source_url=canonical,
                                  content_type="static_page", text=text,
                                  author=author_node.get_text(" ", strip=True) if author_node else None,
                                  published_at=(date_node.get(spec.get("date_attribute", "datetime")) or date_node.get_text(" ", strip=True)) if date_node else None,
                                  extracted_fields={"raw_sha256": digest, "raw_path": str(raw_path)},
                                  permissions=spec["permissions"], identity_aliases=["url:" + canonical], raw=result.body), on_record)
        return out


def _canonical_linkedin(url):
    try:
        from ..pipeline import normalizer
    except ImportError:
        from pipeline import normalizer
    return normalizer.canonical(url)


def _linkedin_record(source_id, url, result, raw_path, soup, spec):
    try:
        from ..pipeline import normalizer
    except ImportError:
        from pipeline import normalizer
    legacy = normalizer.parse_post(raw_path, url, result.collected_at)
    normalizer.validate_record(legacy)
    text_hash = hashlib.sha256(re.sub(r"\s+", " ", legacy["text"]).strip().lower().encode()).hexdigest()
    activity = legacy["id"].rsplit(":", 1)[-1]
    aliases = ["id:" + legacy["id"], "url:" + url, "text:" + text_hash]
    if legacy.get("attributed_urn"):
        aliases.append("id:" + legacy["attributed_urn"])
    # Keep the numeric activity identity as an additive compatibility alias.
    aliases.append("activity:" + activity)
    return record(source_id=source_id, external_id=legacy["id"], source_url=url,
                  content_type="linkedin_post", text=legacy["text"], author=legacy["author"],
                  published_at=legacy["published_at"],
                  extracted_fields={"source_sha256": result.sha256, "raw_path": str(raw_path),
                                    "parser_version": legacy["parser_version"], "layout": legacy["source"].get("layout")},
                  permissions=spec["permissions"], identity_aliases=aliases,
                  raw=result.body, legacy_record=legacy)


class FeedAdapter:
    """Bounded RSS 2.0 / Atom parser. DTD/entity declarations are refused."""
    async def collect(self, spec, transport, workspace, known_url, on_record=None):
        _authorized(spec)
        max_items = max(0, int(spec.get("max_items", 100)))
        if max_items == 0:
            return []
        out = []
        for url in _urls(spec):
            _safe_host(url, spec)
            if known_url(url):
                continue
            result = await transport.fetch(url)
            raw_sha, raw_path = _store_raw(workspace, result.body, ".xml")
            if re.search(rb"<!\s*(DOCTYPE|ENTITY)\b", result.body.replace(b"\x00", b""), re.I):
                raise ConfigurationError("Feed with DTD/entity declaration refused")
            try:
                root = ET.fromstring(result.body)
            except ET.ParseError:
                raise ConfigurationError("Feed XML is malformed") from None
            for item in _feed_items(root):
                link = item.get("link") or url
                try:
                    _safe_host(link, spec)
                except ConfigurationError:
                    continue
                if known_url(link):
                    continue
                title = item.get("title", "")
                summary = item.get("summary", "")
                content = "\n".join(x for x in (title, summary) if x).strip()
                if not content:
                    continue
                _emit(out, record(source_id=spec.get("source_id", "feed"),
                                  external_id=item.get("id") or link, source_url=link,
                                  content_type="feed_item", text=content,
                                  author=item.get("author"), published_at=item.get("published"),
                                  extracted_fields={"feed_url": url, "raw_sha256": raw_sha, "raw_path": str(raw_path)}, permissions=spec["permissions"],
                                  identity_aliases=["url:" + link, "id:" + str(item.get("id") or link)], raw=result.body), on_record)
                if len(out) >= max_items:
                    return out
        return out


def _feed_items(root):
    local = lambda tag: tag.rsplit("}", 1)[-1].lower()
    if local(root.tag) == "feed":  # Atom
        for entry in root:
            if local(entry.tag) != "entry":
                continue
            fields = {local(c.tag): "".join(c.itertext()).strip() for c in entry}
            link = next((c.attrib.get("href") for c in entry if local(c.tag) == "link" and c.attrib.get("rel", "alternate") == "alternate"), None)
            yield {"id": fields.get("id"), "title": fields.get("title"), "summary": fields.get("summary") or fields.get("content"),
                   "author": fields.get("name"), "published": fields.get("published") or fields.get("updated"), "link": link}
    else:  # RSS
        channel = next((c for c in root if local(c.tag) == "channel"), root)
        for item in channel:
            if local(item.tag) != "item":
                continue
            fields = {local(c.tag): "".join(c.itertext()).strip() for c in item}
            yield {"id": fields.get("guid"), "title": fields.get("title"), "summary": fields.get("description") or fields.get("encoded"),
                   "author": fields.get("creator") or fields.get("author"), "published": fields.get("pubdate") or fields.get("date"), "link": fields.get("link")}


def _path_value(obj, path):
    if not path:
        return obj
    for key in path.split("."):
        if isinstance(obj, dict):
            obj = obj.get(key)
        elif isinstance(obj, list) and key.isdigit() and int(key) < len(obj):
            obj = obj[int(key)]
        else:
            return None
    return obj


class GenericAPIAdapter:
    """Public, explicitly configured JSON endpoints; no auth or fallback behavior."""
    async def collect(self, spec, transport, workspace, known_url, on_record=None):
        _authorized(spec)
        if spec.get("token") or spec.get("authorization"):
            raise ConfigurationError("Credentialed API access belongs to a separately authorized API adapter")
        item_path = spec.get("items_path")
        if not item_path:
            raise ConfigurationError("Generic API requires an explicit items_path")
        max_items = max(0, int(spec.get("max_items", 100)))
        if max_items == 0:
            return []
        max_pages = min(20, max(1, int(spec.get("max_pages", 1))))
        out, visited = [], set()
        queue = _urls(spec)[:1]
        page_param = spec.get("page_param")
        next_path = spec.get("next_url_path")
        for _ in range(max_pages):
            if not queue:
                break
            url = queue.pop(0)
            if url in visited or known_url(url):
                continue
            visited.add(url)
            _safe_host(url, spec)
            result = await transport.fetch(url)
            raw_sha, raw_path = _store_raw(workspace, result.body, ".json")
            try:
                payload = json.loads(result.body)
            except (ValueError, UnicodeDecodeError):
                raise ConfigurationError("JSON endpoint returned malformed JSON") from None
            items = _path_value(payload, item_path)
            if not isinstance(items, list):
                raise ConfigurationError("Configured items_path does not select a list")
            for item in items:
                if not isinstance(item, dict):
                    continue
                item_url = str(_path_value(item, spec.get("url_path", "url")) or url)
                try:
                    _safe_host(item_url, spec)
                except ConfigurationError:
                    continue
                if known_url(item_url):
                    continue
                text = _path_value(item, spec.get("text_path", "text"))
                if not isinstance(text, str) or not text.strip():
                    continue
                ext = _path_value(item, spec.get("id_path", "id"))
                _emit(out, record(source_id=spec.get("source_id", "json_api"), external_id=str(ext or item_url),
                                  source_url=item_url, content_type="json_item", text=text,
                                  author=_path_value(item, spec.get("author_path", "author")),
                                  published_at=_path_value(item, spec.get("date_path", "published_at")),
                                  extracted_fields={"endpoint": url, "raw_sha256": raw_sha, "raw_path": str(raw_path)}, permissions=spec["permissions"],
                                  identity_aliases=["url:" + item_url, "id:" + str(ext or item_url)], raw=result.body), on_record)
                if len(out) >= max_items:
                    return out
            if next_path:
                next_url = _path_value(payload, next_path)
                if isinstance(next_url, str) and next_url:
                    queue.append(next_url)
            elif page_param:
                from urllib.parse import parse_qsl, urlencode, urlunsplit
                p = urlsplit(url)
                query = dict(parse_qsl(p.query, keep_blank_values=True))
                query[page_param] = str(int(query.get(page_param, "1")) + 1)
                queue.append(urlunsplit((p.scheme, p.netloc, p.path, urlencode(query), "")))
        return out


class PlaywrightAdapter:
    """Optional JS rendering for non-LinkedIn sources; never uses a user profile."""
    async def collect(self, spec, transport, workspace, known_url, on_record=None):
        _authorized(spec)
        if spec.get("js_required") is not True or spec.get("method") != "permitted_js_rendering":
            raise ConfigurationError("Playwright requires explicit JS-required and permitted-method declarations")
        if any("linkedin.com" in h.lower() for h in spec.get("allowed_hosts", [])):
            raise ConfigurationError("Playwright collection is disabled for LinkedIn")
        state_key = spec.get("access_group") or spec.get("source_id", "javascript")
        if transport.state.get_suspension(state_key):
            raise AccessSuspended("Source access is suspended")
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            raise ConfigurationError("Playwright is unavailable; no browser or package will be installed") from None
        source_id = spec.get("source_id", "javascript")
        max_pages = min(20, max(0, int(spec.get("max_pages", 1))))
        max_bytes = int(spec.get("max_bytes", 4_000_000))
        results = []
        async with async_playwright() as p:
            try:
                browser = await p.chromium.launch(channel="chrome", headless=True)
            except Exception:
                raise ConfigurationError("Existing Chrome is unavailable; Playwright will not install a browser") from None
            context = await browser.new_context(service_workers="block")
            request_count = 0
            stop_code = None
            async def route_handler(route):
                nonlocal request_count
                req_url = route.request.url
                request_count += 1
                if request_count > int(spec.get("max_requests", 100)):
                    await route.abort()
                    return
                if route.request.resource_type in {"image", "media", "font"}:
                    await route.abort()
                    return
                try:
                    _safe_host(req_url, spec)
                except Exception:
                    await route.abort()
                    return
                headers = {k: v for k, v in route.request.headers.items() if k.lower() not in {"cookie", "authorization", "proxy-authorization"}}
                await route.continue_(headers=headers)
            await context.route("**/*", route_handler)
            page = await context.new_page()
            async def response_handler(response):
                nonlocal stop_code
                if response.status in {401, 403, 429, 999}:
                    stop_code = response.status
                    retry_after = response.headers.get("retry-after")
                    from .transport import _retry_after
                    transport._suspend(state_key, f"http_{response.status}", _retry_after(retry_after))
                    state.log_request(source_id, {"event": "access_suspended", "status_code": response.status})
            page.on("response", response_handler)
            try:
                for url in _urls(spec)[:max_pages]:
                    _safe_host(url, spec)
                    if known_url(url):
                        continue
                    await transport._pace(urlsplit(url).hostname.lower().rstrip("."))
                    await page.goto(url, wait_until="domcontentloaded", timeout=int(float(spec.get("timeout_seconds", 18)) * 1000))
                    if stop_code:
                        raise AccessSuspended(f"Browser access suspended after HTTP {stop_code}")
                    body = (await page.content()).encode("utf-8")
                    if len(body) > max_bytes:
                        raise ConfigurationError("Rendered page exceeds byte cap")
                    if transport._challenge(url, body):
                        transport._suspend(state_key, "challenge_page")
                        state.log_request(source_id, {"event": "access_suspended", "error_code": "challenge_page"})
                        raise AccessSuspended("Browser access suspended after challenge page")
                    root = Path(workspace) / "raw"
                    root.mkdir(parents=True, exist_ok=True)
                    digest = hashlib.sha256(body).hexdigest()
                    target = root / (digest + ".html")
                    if not target.exists():
                        target.write_bytes(body)
                    soup = BeautifulSoup(body, "html.parser")
                    node = soup.select_one(spec.get("text_selector", ""))
                    if node and node.get_text(" ", strip=True):
                        text = node.get_text(" ", strip=True)
                        _emit(results, record(source_id=source_id, external_id=url, source_url=url,
                                              content_type="javascript_page", text=text,
                                              extracted_fields={"raw_sha256": digest, "raw_path": str(target)},
                                              permissions=spec["permissions"],
                                              identity_aliases=["url:" + url], raw=body), on_record)
            finally:
                await context.close()
                await browser.close()
        return results


class ScrapyAdapter:
    """Optional finite Scrapy engine; every network request uses the shared transport."""
    async def collect(self, spec, transport, workspace, known_url, on_record=None):
        _authorized(spec)
        if spec.get("high_volume") is not True or spec.get("method") != "permitted_scrapy_crawl":
            raise ConfigurationError("Scrapy requires an explicit permitted high-volume method")
        from .scrapy_worker import collect_scrapy
        return await collect_scrapy(spec, transport, workspace, known_url, on_record)
