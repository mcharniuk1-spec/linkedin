"""Read-only adapter for explicitly authorized LinkedIn REST resources.

The adapter only reads a declared actor/resource allowlist. It is not a global
search API and never falls back to anonymous pages or browser automation.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urlencode, urljoin, urlsplit, parse_qs
from email.utils import parsedate_to_datetime
import hashlib
import json
import re
import time

from .contracts import AccessSuspended, CollectionError, ConfigurationError, record

API_ROOT = "https://api.linkedin.com/rest"
DEFAULT_VERSION = "202610"
_SCOPE = {
    "posts": {"organization": "r_organization_social", "member": "r_member_social"},
    "comments": {"organization": "r_organization_social_feed", "member": "r_member_social_feed"},
    # The exact organization metadata/analytics scope depends on the approved
    # product surface. Require it in source config instead of guessing.
    "organization": {"organization": None},
    "analytics": {"organization": None},
}


def _version(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{6}", value):
        raise ConfigurationError("LinkedIn REST version must use YYYYMM")
    month = int(value[4:])
    if not 1 <= month <= 12:
        raise ConfigurationError("LinkedIn REST version month is invalid")
    return value


def _scopes(token):
    raw = token.get("scope", "")
    if not isinstance(raw, str):
        raise ConfigurationError("Token scope list is invalid")
    return set(re.split(r"[\s,]+", raw.strip())) - {""}


def _permission_metadata(spec, scope, version, endpoint):
    result = {"required_scope": scope, "api_version": version, "source_endpoint": endpoint}
    spec = {**spec.get("permissions", {}), **spec}
    for key, aliases in (("licensing", ("licensing", "license")),
                         ("authorization_basis", ("authorization_basis", "auth_basis"))):
        for name in aliases:
            if name in spec:
                result[key] = spec[name]
                break
    return result


def _actor_id(actor):
    if not isinstance(actor, dict):
        raise ConfigurationError("Authorized actor must be a mapping")
    urn, kind = actor.get("urn"), actor.get("type")
    if kind not in ("organization", "member") or not isinstance(urn, str):
        raise ConfigurationError("Authorized actor identity is invalid")
    if kind == "organization" and not re.fullmatch(r"urn:li:organization:\d+", urn):
        raise ConfigurationError("Organization actor URN is invalid")
    if kind == "member" and not re.fullmatch(r"urn:li:person:[A-Za-z0-9_-]+", urn):
        raise ConfigurationError("Member actor URN is invalid")
    return urn, kind


def _resource_id(value):
    if not isinstance(value, str) or not value.startswith("urn:li:") or len(value) > 512:
        raise ConfigurationError("Resource identity is invalid")
    return value


def _published_at(value):
    if isinstance(value, dict):
        value = value.get("time")
    if isinstance(value, (int, float)) and value > 0:
        try:
            return datetime.fromtimestamp(value / 1000, timezone.utc).isoformat()
        except (OverflowError, OSError, ValueError):
            return None
    return None


def _text(value):
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        text = value.get("text")
        return text if isinstance(text, str) else ""
    return ""


class ReadonlyLinkedInAPIAdapter:
    def __init__(self, *, default_version=DEFAULT_VERSION, page_cap=50, item_cap=10000):
        self.default_version = _version(default_version)
        self.page_cap = max(1, min(int(page_cap), 100))
        self.item_cap = max(1, min(int(item_cap), 100000))

    async def collect(self, spec, transport, workspace: Path, known_url, token, *, on_record=None):
        if not isinstance(spec, dict) or not isinstance(token, dict):
            raise ConfigurationError("API collection spec and token are required")
        access_token = token.get("access_token")
        try:
            expires_at = int(token.get("expires_at", 0))
        except (TypeError, ValueError):
            expires_at = 0
        if not isinstance(access_token, str) or not access_token or expires_at <= int(datetime.now(timezone.utc).timestamp()):
            raise ConfigurationError("A current access token is required")
        version = _version(spec.get("api_version", self.default_version))
        scopes = _scopes(token)
        token_actors = token.get("authorized_actors", [])
        configured = spec.get("actors", spec.get("authorized_actors", []))
        if not isinstance(token_actors, list) or not isinstance(configured, list) or not configured:
            raise ConfigurationError("Token and collection spec need explicit authorized actors")
        token_ids = {_actor_id(a)[0] for a in token_actors}
        actors = []
        for actor in configured:
            urn, kind = _actor_id(actor)
            if urn not in token_ids:
                raise ConfigurationError("Requested actor is not authorized by the token")
            actors.append((urn, kind))
        operations = spec.get("operations", ["posts"])
        if not isinstance(operations, list) or not operations or any(op not in _SCOPE for op in operations):
            raise ConfigurationError("Only supported read operations may be requested")
        if len(set(operations)) != len(operations):
            raise ConfigurationError("Duplicate API operations are not allowed")
        methods = spec.get("permitted_methods", ["GET"])
        if not isinstance(methods, list) or not methods or any(method != "GET" for method in methods):
            raise ConfigurationError("This LinkedIn API adapter permits GET only")
        allowed_resources = spec.get("allowed_resources", [])
        if not isinstance(allowed_resources, list):
            raise ConfigurationError("Resource allowlist is invalid")
        allowed_resources = {_resource_id(x) for x in allowed_resources}
        headers = {"Authorization": "Bearer " + access_token, "LinkedIn-Version": version,
                   "X-Restli-Protocol-Version": "2.0.0", "Accept": "application/json"}
        source_id = str(spec.get("source_id", "linkedin-official-api"))
        access_group = str(spec.get("access_group", source_id))
        output = []
        known = known_url or (lambda _: False)

        def emit(value):
            output.append(value)
            if on_record is not None:
                on_record(value)

        for operation in operations:
            for urn, kind in actors:
                required = _SCOPE[operation].get(kind)
                if required is None and kind == "organization":
                    configured_scopes = spec.get("required_scopes", {})
                    required = configured_scopes.get(operation) if isinstance(configured_scopes, dict) else None
                    if (not isinstance(required, str) or not required.strip()
                            or required.lower().startswith(("w_", "rw_"))):
                        raise ConfigurationError("This operation needs its verified read scope in source config")
                if required is None or required not in scopes:
                    raise ConfigurationError("Token lacks the read scope required for this operation")
                if operation == "posts":
                    if urn not in allowed_resources:
                        raise ConfigurationError("Post actor is outside the resource allowlist")
                    path, params = "/posts", {"q": "author", "author": urn, "start": 0, "count": 100}
                    async for item, raw_body, page_sha in self._pages(path, params, transport, headers, source_id, access_group, spec):
                        item_id = item.get("id")
                        if not isinstance(item_id, str) or not item_id.startswith("urn:li:"):
                            continue
                        url = "https://www.linkedin.com/feed/update/" + item_id
                        if known(url):
                            continue
                        emit(record(
                            source_id=source_id, external_id=item_id, source_url=url,
                            content_type="linkedin_post", text=_text(item.get("commentary")),
                            author={"urn": urn, "type": kind}, published_at=_published_at(item.get("createdAt")),
                            extracted_fields={"media_refs": self._media_refs(item), "source_response_sha256": page_sha,
                                              "counters": self._counters(item),
                                              "status": item.get("lifecycleState")},
                            permissions=_permission_metadata(spec, required, version, "/rest/posts?q=author"),
                            identity_aliases=["id:"+x for x in [item.get("id"), item.get("originalPost")]
                                              if isinstance(x, str)], raw=raw_body))
                elif operation == "comments":
                    post_ids = spec.get("post_ids", [])
                    if not isinstance(post_ids, list) or not post_ids:
                        raise ConfigurationError("Comments require an explicit authorized post ID list")
                    for post_id in post_ids:
                        post_id = _resource_id(post_id)
                        if post_id not in allowed_resources:
                            raise ConfigurationError("Comment target is outside the resource allowlist")
                        path = "/socialActions/" + quote(post_id, safe="") + "/comments"
                        async for item, raw_body, page_sha in self._pages(path, {"start": 0, "count": 100}, transport, headers, source_id, access_group, spec):
                            item_id = item.get("id")
                            if item_id is None:
                                continue
                            external_id = "urn:li:comment:(" + post_id + "," + str(item_id) + ")"
                            url = "https://www.linkedin.com/feed/update/" + post_id
                            if known(url + "#comment-" + external_id):
                                continue
                            emit(record(source_id=source_id, external_id=external_id,
                                source_url=url + "#comment-" + external_id, content_type="linkedin_comment",
                                text=_text(item.get("message")), author=item.get("actor"),
                                published_at=_published_at(item.get("created")),
                                extracted_fields={"post_id": post_id, "source_response_sha256": page_sha},
                                permissions=_permission_metadata(spec, required, version, "/rest" + path), raw=raw_body))
                elif operation == "organization":
                    if kind != "organization" or urn not in allowed_resources:
                        raise ConfigurationError("Organization metadata target is outside the allowlist")
                    org_id = urn.rsplit(":", 1)[-1]
                    endpoint = "/rest/organizations/" + org_id
                    async for item, raw_body, page_sha in self._pages("/organizations/" + org_id, {}, transport, headers,
                                                                       source_id, access_group, spec, single=True):
                        emit(record(source_id=source_id, external_id=urn,
                            source_url="https://www.linkedin.com/company/" + org_id,
                            content_type="linkedin_organization_metadata",
                            text="", author={"urn": urn, "type": kind},
                            extracted_fields={"localized_name": item.get("localizedName"),
                                              "localized_website": item.get("localizedWebsite"),
                                              "staff_count_range": item.get("staffCountRange"),
                                              "source_response_sha256": page_sha},
                            permissions=_permission_metadata(spec, required, version, endpoint), raw=raw_body))
                elif operation == "analytics":
                    if kind != "organization" or urn not in allowed_resources:
                        raise ConfigurationError("Analytics target is outside the allowlist")
                    params = {"q": "organizationalEntity", "organizationalEntity": urn,
                              "timeIntervals.timeGranularityType": "DAY"}
                    endpoint = "/rest/organizationalEntityShareStatistics"
                    async for item, raw_body, page_sha in self._pages("/organizationalEntityShareStatistics", params,
                                                                       transport, headers, source_id, access_group, spec):
                        emit(record(source_id=source_id,
                            external_id=str(item.get("organizationalEntity", urn)) + ":" + str((item.get("timeRange") or {}).get("start", "unknown")),
                            source_url="https://api.linkedin.com/rest/organizationalEntityShareStatistics?" + urlencode({"organizationalEntity": urn,"start":str((item.get("timeRange") or {}).get("start", "unknown"))}),
                            content_type="linkedin_organization_analytics", text="",
                            author={"urn": urn, "type": kind},
                            extracted_fields={"time_range": item.get("timeRange"),
                                              "total_share_statistics": item.get("totalShareStatistics"),
                                              "source_response_sha256": page_sha},
                            permissions=_permission_metadata(spec, required, version, endpoint), raw=raw_body))
        return output

    async def _pages(self, path, params, transport, headers, source_id, access_group, spec, *, single=False):
        max_pages = min(self.page_cap, max(1, int(spec.get("max_pages", self.page_cap))))
        max_items = min(self.item_cap, max(1, int(spec.get("max_items", self.item_cap))))
        url = API_ROOT + path + (("?" + urlencode(params)) if params else "")
        seen_urls, item_count = set(), 0
        state = spec.get("state", getattr(transport, "state", None))
        if state is not None and callable(getattr(state, "get_suspension", None)):
            if state.get_suspension(access_group):
                raise AccessSuspended("LinkedIn API access is suspended")
        next_url = None
        for _ in range(1 if single else max_pages):
            parsed = urlsplit(url)
            if parsed.scheme != "https" or parsed.hostname != "api.linkedin.com" or not parsed.path.startswith("/rest/"):
                raise ConfigurationError("Pagination URL is outside the LinkedIn REST allowlist")
            if url in seen_urls:
                raise CollectionError("LinkedIn pagination cycle detected")
            seen_urls.add(url)
            try:
                    response = await transport.fetch(url, headers=headers)
            except AccessSuspended:
                raise
            except Exception:
                raise CollectionError("LinkedIn API request failed") from None
            status = getattr(response, "status_code", None)
            if status in (401, 403, 429, 999):
                if state is not None:
                    retry_after = None
                    response_headers = getattr(response, "headers", {}) or {}
                    raw_retry = next((v for k, v in response_headers.items() if k.lower() == "retry-after"), None)
                    if raw_retry:
                        try:
                            retry_after = max(0, int(raw_retry))
                        except (TypeError, ValueError):
                            try:
                                retry_after = max(0, int(parsedate_to_datetime(raw_retry).timestamp() - time.time()))
                            except (TypeError, ValueError, OverflowError):
                                retry_after = None
                    try:
                        state.suspend(access_group, f"http_{status}", retry_after)
                    except TypeError:
                        state.suspend(access_group, f"http_{status}")
                raise AccessSuspended(f"LinkedIn API access suspended ({status})")
            if status != 200:
                raise CollectionError("LinkedIn API returned an unsuccessful response")
            raw_body = response.body
            if not isinstance(raw_body, bytes):
                raise CollectionError("LinkedIn API response body is not bytes")
            page_sha = hashlib.sha256(raw_body).hexdigest()
            try:
                body = json.loads(raw_body)
            except (TypeError, ValueError):
                raise CollectionError("LinkedIn API response was not valid JSON") from None
            if not isinstance(body, dict):
                raise CollectionError("LinkedIn API response shape was invalid")
            elements = body.get("elements")
            if single and elements is None:
                elements = [body]
            if not isinstance(elements, list):
                raise CollectionError("LinkedIn API page has no elements list")
            for item in elements:
                if isinstance(item, dict):
                    item_count += 1
                    if item_count > max_items:
                        raise CollectionError("LinkedIn API item cap reached; result is incomplete")
                    yield item, raw_body, page_sha
            if single:
                return
            next_url = self._next_url(body, url, len(seen_urls))
            if item_count >= max_items and next_url is not None:
                raise CollectionError("LinkedIn API item cap reached; result is incomplete")
            if next_url is None:
                return
            url = next_url
        else:
            if next_url is not None:
                raise CollectionError("LinkedIn API page cap reached; result is incomplete")

    @staticmethod
    def _next_url(body, current_url, pages_seen):
        paging = body.get("paging", {})
        if not isinstance(paging, dict):
            return None
        for link in paging.get("links", []) if isinstance(paging.get("links"), list) else []:
            if isinstance(link, dict) and link.get("rel") == "next" and isinstance(link.get("href"), str):
                candidate = urljoin(current_url, link["href"])
                p = urlsplit(candidate)
                if p.scheme != "https" or p.hostname != "api.linkedin.com" or not p.path.startswith("/rest/"):
                    raise ConfigurationError("LinkedIn pagination link is outside the REST allowlist")
                return candidate
        start, count, total = paging.get("start"), paging.get("count"), paging.get("total")
        if all(isinstance(x, int) and x >= 0 for x in (start, count, total)) and count and start + count < total:
            p = urlsplit(current_url)
            q = parse_qs(p.query, keep_blank_values=True)
            q["start"] = [str(start + count)]
            q.setdefault("count", [str(count)])
            query = urlencode([(k, val) for k, values in q.items() for val in values])
            return p._replace(query=query).geturl()
        return None

    @staticmethod
    def _media_refs(item):
        content = item.get("content")
        if not isinstance(content, dict):
            return []
        refs = []
        for key in ("media", "article", "multiImage"):
            value = content.get(key)
            if isinstance(value, dict):
                urn = value.get("id") or value.get("media")
                if isinstance(urn, str):
                    refs.append({"type": key, "urn": urn})
        return refs

    @staticmethod
    def _counters(item):
        stats = item.get("socialDetail") or item.get("statistics") or {}
        if not isinstance(stats, dict):
            return {}
        keys = ("numLikes", "numComments", "numShares", "reactionCount", "commentCount", "shareCount")
        return {key: stats[key] for key in keys if isinstance(stats.get(key), (int, float))}
