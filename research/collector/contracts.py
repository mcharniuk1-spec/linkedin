"""Small shared contracts; source authorization never follows from adapter presence."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
from typing import Any


def utcnow():
    return datetime.now(timezone.utc).isoformat()


class CollectionError(RuntimeError):
    """Public-safe failure code; never include response bodies, tokens or query strings."""


class AccessSuspended(CollectionError):
    pass


class ConfigurationError(CollectionError):
    pass


@dataclass
class FetchResult:
    url: str
    body: bytes
    status_code: int
    headers: dict[str, str] = field(default_factory=dict)
    collected_at: str = field(default_factory=utcnow)

    @property
    def sha256(self):
        return hashlib.sha256(self.body).hexdigest()


def record(*, source_id, external_id, source_url, content_type, text='', author=None,
           published_at=None, collected_at=None, extracted_fields=None, permissions=None,
           identity_aliases=None, raw=None, legacy_record=None):
    """Extracted source material only. Do not place generated summaries in text."""
    result = dict(source_id=source_id, external_id=external_id, source_url=source_url,
                  author=author, published_at=published_at, collected_at=collected_at or utcnow(),
                  content_type=content_type, text=text, extracted_fields=extracted_fields or {},
                  content_hash=hashlib.sha256(text.encode('utf-8')).hexdigest(),
                  permissions=permissions or {}, processing_status='pending_review',
                  identity_aliases=identity_aliases or [])
    if raw is not None:
        result['_raw'] = raw
    if legacy_record is not None:
        result['legacy_record'] = legacy_record
    return result


# Transport policy dict fields:
# source_id, access_group, allowed_hosts, permitted_methods, permissions,
# rate_per_second(default0.5), concurrency(default2), timeout_seconds(default18),
# max_bytes(default4_000_000), max_attempts(default3), allow_local_test(defaultFalse).
# state interface: get_suspension(key)->dict|None;
# suspend(key, reason, retry_after_seconds=None)->None;
# log_request(source_id, event:dict)->None. No raw URLs/query/body/token logging.
# transport: async fetch(url, *, headers=None)->FetchResult; async aclose().
# Static/feed adapters: async collect(spec, transport, workspace:Path,
#                                  known_url:callable)->list[dict].
# API adapter uses the same collect signature plus token:dict, and never falls
# back to a public-page/browser adapter when authorization fails.
