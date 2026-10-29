import json
import os
from pathlib import Path
import tempfile
import unittest
from urllib.parse import parse_qs, urlsplit

import httpx

from research.collector.contracts import ConfigurationError, CollectionError
from research.collector.oauth import Credentials, EncryptedTokenVault, OAuthClient


class OAuthTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.cred = self.root / "synthetic.yaml"
        self.cred.write_text("clientID: demo-client\nclientSecret: demo-secret\n")
        if os.name == "posix":
            self.cred.chmod(0o600)

    def tearDown(self):
        self.temp.cleanup()

    def test_credentials_aliases_and_duplicate_rejection(self):
        self.assertEqual(Credentials.from_yaml(self.cred).client_id, "demo-client")
        self.cred.write_text("Client ID: alias-id\nprimaryClientSecret: alias-secret\n")
        self.assertEqual(Credentials.from_yaml(self.cred).client_secret, "alias-secret")
        self.cred.write_text("clientID: alias-id\nsecretKey: alias-secret\n")
        self.assertEqual(Credentials.from_yaml(self.cred).client_id, "alias-id")
        self.assertEqual(Credentials.from_yaml(self.cred).client_secret, "alias-secret")
        self.cred.write_text("clientID: alias-id\nclientSecret: one\nsecretKey: two\n")
        with self.assertRaises(ConfigurationError):
            Credentials.from_yaml(self.cred)
        self.cred.write_text("client_id: a\nclientID: b\nclient_secret: s\n")
        with self.assertRaises(ConfigurationError):
            Credentials.from_yaml(self.cred)

    def test_credential_symlink_is_rejected(self):
        link = self.root / "credential-link.yaml"
        link.symlink_to(self.cred)
        with self.assertRaises(ConfigurationError):
            Credentials.from_yaml(link)
        self.cred.write_text("client_id: a\nclient_id: b\nclient_secret: s\n")
        with self.assertRaises(ConfigurationError):
            Credentials.from_yaml(self.cred)

    def test_credentials_reject_group_or_world_readable_mode(self):
        if os.name != "posix":
            self.skipTest("POSIX mode bits are not available")
        self.cred.chmod(0o640)
        with self.assertRaises(ConfigurationError):
            Credentials.from_yaml(self.cred)

    def test_authorization_state_single_use_expiry_and_exact_redirect(self):
        client = OAuthClient(Credentials("id", "secret"), "https://example.test/callback", state_ttl_seconds=5)
        start = client.begin("r_organization_social, r_member_social", now=10)
        parsed = parse_qs(urlsplit(start["authorization_url"]).query)
        self.assertEqual(parsed["redirect_uri"], ["https://example.test/callback"])
        self.assertEqual(parsed["state"], [start["state"]])
        self.assertEqual(parsed["scope"], ["r_organization_social r_member_social"])
        with self.assertRaises(ConfigurationError):
            client._consume_state(start["state"], now=16)
        with self.assertRaises(ConfigurationError):
            client._consume_state(start["state"], now=10)

    def test_exchange_posts_only_to_token_endpoint_and_never_exposes_secret(self):
        calls = []
        def handler(request):
            calls.append(request)
            return httpx.Response(200, json={"access_token": "synthetic-token", "expires_in": 3600,
                                             "scope": "r_organization_social, r_member_social",
                                             "refresh_token": "refresh-demo", "refresh_token_expires_in": 7200})
        http = httpx.Client(transport=httpx.MockTransport(handler), trust_env=False)
        client = OAuthClient(Credentials("id", "secret"), "https://example.test/callback", http_client=http)
        start = client.begin(["r_organization_social", "r_member_social"], now=100)
        token = client.exchange("code-demo", start["state"], now=100)
        self.assertEqual(calls[0].url, "https://www.linkedin.com/oauth/v2/accessToken")
        self.assertEqual(token["expires_at"], 3700)
        self.assertEqual(token["scope"], "r_organization_social r_member_social")
        self.assertEqual(token["refresh_expires_at"], 7300)
        self.assertNotIn("demo-secret", repr(client.credentials))
        self.assertNotIn("secret", str(token))
        http.close()

    def test_write_scopes_and_non_https_redirect_are_rejected(self):
        client = OAuthClient(Credentials("id", "secret"), "https://example.test/callback")
        with self.assertRaises(ConfigurationError):
            client.begin(["w_member_social"])
        with self.assertRaises(ConfigurationError):
            OAuthClient(Credentials("id", "secret"), "http://example.test/callback")
        self.assertEqual(OAuthClient(Credentials("id", "secret"), "http://127.0.0.1:8080/cb",
                                     allow_loopback_http=True).redirect_uri, "http://127.0.0.1:8080/cb")

    def test_refresh_requires_entitlement_issued_token_and_nonexpired_token(self):
        calls = []
        http = httpx.Client(transport=httpx.MockTransport(lambda request: (calls.append(request) or
            httpx.Response(200, json={"access_token": "new", "expires_in": 50}))), trust_env=False)
        client = OAuthClient(Credentials("id", "secret"), "https://example.test/callback", http_client=http)
        token = {"access_token": "old", "expires_at": 100, "scope": "r_organization_social", "refresh_token": "r"}
        with self.assertRaises(ConfigurationError):
            client.refresh(token, now=10)
        entitled = OAuthClient(Credentials("id", "secret"), "https://example.test/callback",
                               http_client=http, refresh_entitled=True)
        with self.assertRaises(ConfigurationError):
            entitled.refresh({"access_token": "old", "expires_at": 100, "scope": "x"}, now=10)
        with self.assertRaises(ConfigurationError):
            entitled.refresh({**token, "refresh_expires_at": 9}, now=10)
        token = {**token, "authorized_actors": [{"urn": "urn:li:organization:123", "type": "organization"}],
                 "refresh_expires_at": 200, "refresh_token": "r"}
        result = entitled.refresh(token, now=10)
        self.assertEqual(result["expires_at"], 60)
        self.assertEqual(result["authorized_actors"], token["authorized_actors"])
        self.assertEqual(result["refresh_token"], "r")
        self.assertEqual(result["refresh_expires_at"], 200)
        self.assertEqual(len(calls), 1)
        http.close()

    def test_encrypted_vault_is_private_and_expiry_is_enforced(self):
        key = __import__("cryptography.fernet", fromlist=["Fernet"]).Fernet.generate_key()
        path = self.root / "tokens.enc"
        vault = EncryptedTokenVault(path, key)
        token = {"access_token": "synthetic-secret", "expires_at": 100, "scope": "r_member_social"}
        vault.save(token)
        self.assertNotIn(b"synthetic-secret", path.read_bytes())
        if os.name == "posix":
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        self.assertEqual(vault.load(now=99), token)
        with self.assertRaises(ConfigurationError):
            vault.load(now=100)
        self.assertEqual(vault.load(now=100, allow_expired=True), token)

    def test_vault_symlink_is_rejected(self):
        key = __import__("cryptography.fernet", fromlist=["Fernet"]).Fernet.generate_key()
        target = self.root / "target.enc"
        EncryptedTokenVault(target, key).save({"access_token": "x", "expires_at": 100, "scope": "s"})
        link = self.root / "link.enc"
        link.symlink_to(target)
        with self.assertRaises(ConfigurationError):
            EncryptedTokenVault(link, key).load(now=1)


if __name__ == "__main__":
    unittest.main()
