"""OAuth authorization-code support for explicitly approved LinkedIn access.

This module does not log in, discover actors, or grant product permissions.
The application owner must configure the exact registered redirect and scopes.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
import hmac
import json
import os
import re
import secrets
import stat
import tempfile
import time

import httpx
import yaml
from cryptography.fernet import Fernet, InvalidToken

from .contracts import ConfigurationError, CollectionError

AUTHORIZATION_ENDPOINT = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_ENDPOINT = "https://www.linkedin.com/oauth/v2/accessToken"
_DEFAULT_STATE_TTL = 600


class _UniqueLoader(yaml.SafeLoader):
    pass


def _construct_unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise ConfigurationError("Duplicate credential field")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


_UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping)


def _normalized_key(value):
    return "".join(ch.lower() for ch in str(value) if ch.isalnum())


@dataclass(frozen=True, repr=False)
class Credentials:
    client_id: str
    client_secret: str

    def __repr__(self):
        return "Credentials(client_id=<redacted>, client_secret=<redacted>)"

    @classmethod
    def from_yaml(cls, path):
        path = Path(path)
        try:
            if path.is_symlink():
                raise ConfigurationError("Credential file must not be a symlink")
            flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
            fd = os.open(path, flags)
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode):
                os.close(fd)
                raise ConfigurationError("Credential file must be a regular file")
            if os.name == "posix" and stat.S_IMODE(info.st_mode) & 0o077:
                os.close(fd)
                raise ConfigurationError("Credential file permissions must be 0600 or stricter")
            with os.fdopen(fd, "r", encoding="utf-8") as handle:
                raw = handle.read()
            data = yaml.load(raw, Loader=_UniqueLoader)
        except ConfigurationError:
            raise
        except (OSError, UnicodeError, yaml.YAMLError) as exc:
            raise ConfigurationError("Credential file could not be read") from None
        if not isinstance(data, dict):
            raise ConfigurationError("Credential file must contain a mapping")
        fields = {}
        aliases = {
            "clientid": "client_id", "clientidentifier": "client_id",
            "clientsecret": "client_secret", "primaryclientsecret": "client_secret",
            "secretkey": "client_secret", "secret": "client_secret",
        }
        for key, value in data.items():
            target = aliases.get(_normalized_key(key))
            if target:
                if target in fields:
                    raise ConfigurationError("Ambiguous credential aliases")
                fields[target] = value
        if set(fields) != {"client_id", "client_secret"} or not all(
            isinstance(v, str) and v.strip() for v in fields.values()
        ):
            raise ConfigurationError("Credential file needs one client ID and one client secret")
        return cls(fields["client_id"].strip(), fields["client_secret"].strip())


def validate_redirect_uri(uri, *, allow_loopback_http=False):
    from urllib.parse import urlsplit
    if not isinstance(uri, str) or not uri:
        raise ConfigurationError("An exact registered redirect URI is required")
    parts = urlsplit(uri)
    loopback = parts.hostname in {"localhost", "127.0.0.1", "::1"}
    allowed = parts.scheme == "https" or (allow_loopback_http and loopback and parts.scheme == "http")
    if not allowed or not parts.hostname or parts.username or parts.password or parts.fragment:
        raise ConfigurationError("Redirect URI must be HTTPS or explicitly enabled loopback HTTP")
    if parts.port not in (None, 80, 443) and not (allow_loopback_http and loopback):
        raise ConfigurationError("Redirect URI has an unsupported port")
    return uri


def _safe_scope_list(scopes):
    if isinstance(scopes, str):
        scopes = re.split(r"[\s,]+", scopes.strip())
    if not isinstance(scopes, (tuple, list, set)):
        raise ConfigurationError("OAuth scopes must be a sequence")
    result = []
    for scope in scopes:
        if not isinstance(scope, str) or not scope.strip() or any(ch.isspace() for ch in scope.strip()):
            raise ConfigurationError("OAuth scope is malformed")
        scope = scope.strip()
        if scope.lower().startswith("w_") or scope.lower().startswith("rw_"):
            raise ConfigurationError("Write scopes are not requested by this read-only client")
        if scope not in result:
            result.append(scope)
    if not result:
        raise ConfigurationError("At least one explicitly approved read scope is required")
    return result


class OAuthClient:
    def __init__(self, credentials, redirect_uri, *, http_client=None,
                 allow_loopback_http=False, state_ttl_seconds=_DEFAULT_STATE_TTL,
                 refresh_entitled=False):
        self.credentials = credentials if isinstance(credentials, Credentials) else Credentials.from_yaml(credentials)
        self.redirect_uri = validate_redirect_uri(redirect_uri, allow_loopback_http=allow_loopback_http)
        if http_client is not None and getattr(http_client, "_trust_env", False):
            raise ConfigurationError("OAuth HTTP client must disable environment proxy settings")
        # Delay client construction until a token exchange is explicitly invoked.
        # Merely preparing an authorization URL must not initialize a network client.
        self.http = http_client
        self.state_ttl_seconds = int(state_ttl_seconds)
        if self.state_ttl_seconds < 1:
            raise ConfigurationError("State lifetime must be positive")
        self.refresh_entitled = bool(refresh_entitled)
        self._pending = {}

    def begin(self, scopes, *, now=None):
        scopes = _safe_scope_list(scopes)
        now = int(time.time() if now is None else now)
        state = secrets.token_urlsafe(32)
        expires_at = now + self.state_ttl_seconds
        self._pending[state] = {"expires_at": expires_at, "scopes": list(scopes)}
        params = {"response_type": "code", "client_id": self.credentials.client_id,
                  "redirect_uri": self.redirect_uri, "scope": " ".join(scopes), "state": state}
        return {"authorization_url": AUTHORIZATION_ENDPOINT + "?" + urlencode(params),
                "state": state, "expires_at": expires_at}

    def _consume_state(self, state, *, now=None):
        if not isinstance(state, str):
            raise ConfigurationError("OAuth state is invalid or expired")
        match = next((issued for issued in self._pending if hmac.compare_digest(issued, state)), None)
        if match is None:
            raise ConfigurationError("OAuth state is invalid or expired")
        pending = self._pending.pop(match)
        now = int(time.time() if now is None else now)
        if now >= pending["expires_at"]:
            raise ConfigurationError("OAuth state is invalid or expired")
        return pending["scopes"]

    def _http(self):
        if self.http is None:
            self.http = httpx.Client(timeout=20, follow_redirects=False, trust_env=False)
        return self.http

    def exchange(self, code, state, *, now=None):
        requested_scopes = set(self._consume_state(state, now=now))
        if not isinstance(code, str) or not code:
            raise ConfigurationError("Authorization code is required")
        try:
            response = self._http().post(TOKEN_ENDPOINT, data={
                "grant_type": "authorization_code", "code": code,
                "redirect_uri": self.redirect_uri,
                "client_id": self.credentials.client_id,
                "client_secret": self.credentials.client_secret,
            }, headers={"Accept": "application/json"}, follow_redirects=False)
        except httpx.HTTPError:
            raise CollectionError("OAuth token exchange failed") from None
        if response.status_code != 200:
            raise CollectionError("OAuth token exchange failed")
        try:
            payload = response.json()
        except (ValueError, json.JSONDecodeError):
            raise CollectionError("OAuth token response was invalid") from None
        token = self._normalize_token(payload, now=now)
        if not set(token["scope"].split()).issubset(requested_scopes):
            raise CollectionError("OAuth token returned unrequested scopes")
        return token

    @staticmethod
    def _normalize_token(payload, *, now=None):
        now = int(time.time() if now is None else now)
        if not isinstance(payload, dict) or not isinstance(payload.get("access_token"), str) or not payload["access_token"]:
            raise CollectionError("OAuth token response was invalid")
        expires = payload.get("expires_at")
        if expires is None:
            try:
                expires = now + int(payload["expires_in"])
            except (KeyError, TypeError, ValueError):
                raise CollectionError("OAuth token expiry is missing") from None
        try:
            expires = int(expires)
        except (TypeError, ValueError):
            raise CollectionError("OAuth token expiry is invalid") from None
        if expires <= now:
            raise CollectionError("OAuth access token is already expired")
        scope = payload.get("scope", "")
        if not isinstance(scope, str) or not scope.strip():
            raise CollectionError("OAuth token scope is invalid")
        scope = " ".join(re.split(r"[\s,]+", scope.strip()))
        if any(item.lower().startswith(("w_", "rw_")) for item in scope.split()):
            raise CollectionError("OAuth response contains a write scope")
        actors = payload.get("authorized_actors", [])
        if not isinstance(actors, list):
            raise CollectionError("OAuth authorized actor list is invalid")
        token = {"access_token": payload["access_token"], "expires_at": expires,
                 "scope": scope, "authorized_actors": actors}
        if "refresh_token" in payload:
            if not isinstance(payload["refresh_token"], str) or not payload["refresh_token"]:
                raise CollectionError("OAuth refresh token is invalid")
            token["refresh_token"] = payload["refresh_token"]
        if "refresh_token_expires_in" in payload:
            try:
                token["refresh_expires_at"] = now + int(payload["refresh_token_expires_in"])
            except (TypeError, ValueError):
                raise CollectionError("OAuth refresh expiry is invalid") from None
            if token["refresh_expires_at"] <= now:
                raise CollectionError("OAuth refresh token is already expired")
        elif "refresh_expires_at" in payload:
            try:
                token["refresh_expires_at"] = int(payload["refresh_expires_at"])
            except (TypeError, ValueError):
                raise CollectionError("OAuth refresh expiry is invalid") from None
            if token["refresh_expires_at"] <= now:
                raise CollectionError("OAuth refresh token is already expired")
        return token

    def refresh(self, token, *, now=None):
        now = int(time.time() if now is None else now)
        if not isinstance(token, dict):
            raise ConfigurationError("Token payload is invalid")
        if not self.refresh_entitled or not token.get("refresh_token"):
            raise ConfigurationError("Refresh is unavailable without app entitlement and an issued refresh token")
        try:
            refresh_expires = int(token["refresh_expires_at"]) if token.get("refresh_expires_at") is not None else None
        except (TypeError, ValueError):
            raise ConfigurationError("Refresh expiry is invalid") from None
        if refresh_expires is not None and now >= refresh_expires:
            raise ConfigurationError("Refresh token has expired")
        try:
            response = self._http().post(TOKEN_ENDPOINT, data={
                "grant_type": "refresh_token", "refresh_token": token["refresh_token"],
                "client_id": self.credentials.client_id,
                "client_secret": self.credentials.client_secret,
            }, headers={"Accept": "application/json"}, follow_redirects=False)
        except httpx.HTTPError:
            raise CollectionError("OAuth token refresh failed") from None
        if response.status_code != 200:
            raise CollectionError("OAuth token refresh failed")
        try:
            payload = response.json()
        except ValueError:
            raise CollectionError("OAuth token response was invalid") from None
        if not isinstance(payload, dict):
            raise CollectionError("OAuth token response was invalid")
        # Refresh responses may omit fields that remain unchanged. Preserve only
        # the prior values that the server did not replace.
        if isinstance(token, dict):
            payload.setdefault("authorized_actors", token.get("authorized_actors", []))
            payload.setdefault("scope", token.get("scope", ""))
            if "refresh_token" not in payload and token.get("refresh_token"):
                payload["refresh_token"] = token["refresh_token"]
                if token.get("refresh_expires_at") is not None:
                    payload.setdefault("refresh_expires_at", token["refresh_expires_at"])
            elif payload.get("refresh_token") == token.get("refresh_token") and token.get("refresh_expires_at") is not None:
                payload.setdefault("refresh_expires_at", token["refresh_expires_at"])
        return self._normalize_token(payload, now=now)


class EncryptedTokenVault:
    """Small encrypted file vault. The Fernet key must come from a secret manager."""
    def __init__(self, path, key):
        self.path = Path(path)
        try:
            self.fernet = Fernet(key.encode() if isinstance(key, str) else key)
        except (TypeError, ValueError):
            raise ConfigurationError("Token vault key is invalid") from None

    def save(self, token):
        if not isinstance(token, dict) or not token.get("access_token"):
            raise ConfigurationError("Token payload is invalid")
        payload = self.fernet.encrypt(json.dumps(token, sort_keys=True, separators=(",", ":")).encode())
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.is_symlink():
            raise ConfigurationError("Token vault must not be a symlink")
        fd, temp_name = tempfile.mkstemp(prefix=".token-", dir=self.path.parent)
        try:
            if os.name == "posix":
                os.fchmod(fd, 0o600)
            with os.fdopen(fd, "wb") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, self.path)
            if os.name == "posix":
                os.chmod(self.path, 0o600)
        finally:
            try:
                os.unlink(temp_name)
            except FileNotFoundError:
                pass

    def load(self, *, now=None, allow_expired=False):
        try:
            if self.path.is_symlink():
                raise ConfigurationError("Token vault must not be a symlink")
            fd = os.open(self.path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
            info = os.fstat(fd)
            if not stat.S_ISREG(info.st_mode):
                os.close(fd)
                raise ConfigurationError("Token vault must be a regular file")
            if os.name == "posix" and stat.S_IMODE(info.st_mode) & 0o077:
                os.close(fd)
                raise ConfigurationError("Token vault permissions must be 0600 or stricter")
            with os.fdopen(fd, "rb") as handle:
                payload = self.fernet.decrypt(handle.read())
            token = json.loads(payload)
        except ConfigurationError:
            raise
        except (OSError, InvalidToken, ValueError, TypeError):
            raise ConfigurationError("Token vault could not be read or decrypted") from None
        if not isinstance(token, dict) or not isinstance(token.get("access_token"), str):
            raise ConfigurationError("Token vault contents are invalid")
        try:
            expires = int(token["expires_at"])
        except (KeyError, TypeError, ValueError):
            raise ConfigurationError("Token expiry is invalid") from None
        if not allow_expired and int(time.time() if now is None else now) >= expires:
            raise ConfigurationError("Access token has expired")
        return token
