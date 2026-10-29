import base64
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile
from unittest.mock import patch

from cryptography.fernet import Fernet

from research.collector import ci_state
from research.collector.contracts import ConfigurationError, record
from research.collector.store import Store


REPOSITORY = "example/linkedin"


def checkpoint(*, artifact_id=7, revision=1, key_id="0123456789ab", encrypted=b"sealed"):
    return {"schema": ci_state.SCHEMA, "repository": REPOSITORY, "revision": revision,
            "artifact_id": artifact_id, "encrypted_sha256": hashlib.sha256(encrypted).hexdigest(),
            "encrypted_bytes": len(encrypted), "key_id": key_id, "updated_at": "synthetic",
            "privacy": "encrypted"}


class CIStateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.key = Fernet.generate_key().decode()
        self.env = patch.dict(os.environ, {"COLLECTOR_STATE_KEY": self.key}, clear=False)
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.temp.cleanup()

    def seeded_store(self, path):
        store = Store(path)
        store.seed({"publications": [], "profiles": []})
        item = record(source_id="synthetic", external_id="urn:li:share:1",
                      source_url="https://www.linkedin.com/feed/update/urn:li:share:1",
                      content_type="linkedin_post", text="Synthetic owner supplied source text",
                      author={"url": "https://www.linkedin.com/company/example"}, published_at=None,
                      collected_at="2026-10-29T10:00:00+00:00",
                      extracted_fields={"source_response_sha256": hashlib.sha256(b"fixture-response").hexdigest()},
                      permissions={"required_scope": "synthetic-read", "authorization_basis": "test"},
                      raw=b"synthetic-source-response")
        store.ingest(item)
        return store

    def make_sealed_state(self, source_dir, dest_dir, *, revision=3, checkpoint_sha="f" * 64):
        store = self.seeded_store(source_dir)
        store.close()
        vault_bytes = Fernet(self.key.encode()).encrypt(b"synthetic-token-vault")
        (Path(source_dir) / "tokens.enc").write_bytes(vault_bytes)
        output = self.root / "artifact" / "state.enc"
        report = ci_state.seal(source_dir, output,
            {"repository": REPOSITORY, "revision": revision, "checkpoint_sha256": checkpoint_sha})
        expected = {"repository": REPOSITORY, "revision": report["revision"],
                    "encrypted_sha256": report["sha256"], "encrypted_bytes": report["bytes"],
                    "key_id": report["key_id"]}
        return output.read_bytes(), report, expected, vault_bytes

    def test_seal_unseal_roundtrip_with_real_store_and_token_ciphertext(self):
        source = self.root / "source-state"
        destination = self.root / "restored-state"
        encrypted, report, expected, vault_bytes = self.make_sealed_state(source, destination)
        self.assertEqual(report["revision"], 4)
        self.assertEqual(ci_state.unseal(encrypted, destination, expected), {"restored": True, "revision": 4})
        store = Store(destination)
        try:
            self.assertEqual(store.counts()["records"], 1)
            row = store.pending()[0]
            self.assertEqual(store.raw_bytes(row["raw_sha256"]), b"synthetic-source-response")
            self.assertEqual((destination / "tokens.enc").read_bytes(), vault_bytes)
            self.assertEqual((destination / "collector.sqlite").stat().st_mode & 0o777, 0o600)
        finally:
            store.close()

    def test_ciphertext_digest_and_fernet_authentication_fail_closed(self):
        encrypted, _, expected, _ = self.make_sealed_state(self.root / "source", self.root / "out")
        corrupted = encrypted[:-1] + bytes([encrypted[-1] ^ 1])
        with self.assertRaisesRegex(ConfigurationError, "state_artifact_hash_mismatch"):
            ci_state.unseal(corrupted, self.root / "bad-digest", expected)
        expected_bad_digest = {**expected, "encrypted_sha256": hashlib.sha256(corrupted).hexdigest()}
        with self.assertRaisesRegex(ConfigurationError, "invalid_encrypted_state"):
            ci_state.unseal(corrupted, self.root / "bad-fernet", expected_bad_digest)
        with patch.object(ci_state, "MAX_ENCRYPTED", 1):
            with self.assertRaisesRegex(ConfigurationError, "state_artifact_hash_mismatch"):
                ci_state.unseal(b"larger-than-cap", self.root / "oversized", expected)

    def test_authenticated_envelope_with_bad_database_digest_is_rejected(self):
        key, cipher = ci_state.key()
        db = b"not-the-database"
        envelope = {"schema": ci_state.SCHEMA, "repository": REPOSITORY, "revision": 9,
                    "previous_checkpoint_sha256": None, "database_sha256": "0" * 64,
                    "database": base64.b64encode(db).decode()}
        encrypted = cipher.encrypt(gzip.compress(ci_state.canonical(envelope), mtime=0))
        expected = {"repository": REPOSITORY, "revision": 9,
                    "encrypted_sha256": hashlib.sha256(encrypted).hexdigest(),
                    "key_id": hashlib.sha256(key).hexdigest()[:12]}
        with self.assertRaisesRegex(ConfigurationError, "invalid_encrypted_state"):
            ci_state.unseal(encrypted, self.root / "bad-db", expected)

    def test_python_optimized_mode_still_rejects_invalid_sqlite_database(self):
        script = r'''import base64,gzip,hashlib,json,os,tempfile
from cryptography.fernet import Fernet
from research.collector import ci_state
from research.collector.contracts import ConfigurationError
k=Fernet.generate_key();os.environ['COLLECTOR_STATE_KEY']=k.decode();db=b'not sqlite'
env={'schema':ci_state.SCHEMA,'repository':'example/linkedin','revision':2,
     'database_sha256':hashlib.sha256(db).hexdigest(),'database':base64.b64encode(db).decode()}
blob=Fernet(k).encrypt(gzip.compress(ci_state.canonical(env),mtime=0))
expected={'repository':'example/linkedin','revision':2,'encrypted_sha256':hashlib.sha256(blob).hexdigest(),
          'encrypted_bytes':len(blob),'key_id':hashlib.sha256(k).hexdigest()[:12]}
try:
    with tempfile.TemporaryDirectory() as td:ci_state.unseal(blob,td,expected)
except ConfigurationError as e:
    if str(e)=='invalid_state_database':print('rejected');raise SystemExit(0)
raise SystemExit('invalid database was restored')'''
        env = {**os.environ, "COLLECTOR_STATE_KEY_FILE": ""}
        env.pop("COLLECTOR_STATE_KEY", None)
        proc = subprocess.run([sys.executable, "-O", "-c", script], cwd=Path.cwd(), env=env,
                              capture_output=True, timeout=20, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout.strip(), "rejected")

    def test_key_file_requires_private_regular_nonsymlink_bounded_file(self):
        key_path = self.root / "state.key"
        key_path.write_text(self.key)
        key_path.chmod(0o600)
        with patch.dict(os.environ, {"COLLECTOR_STATE_KEY": "", "COLLECTOR_STATE_KEY_FILE": str(key_path)}, clear=False):
            self.assertEqual(ci_state.key()[0], self.key.encode())
            if os.name == "posix":
                key_path.chmod(0o640)
                with self.assertRaisesRegex(ConfigurationError, "invalid_state_key_file"):
                    ci_state.key()
                key_path.chmod(0o600)
            key_path.write_text("x" * (ci_state.MAX_KEY_FILE + 1))
            key_path.chmod(0o600)
            with self.assertRaisesRegex(ConfigurationError, "invalid_state_key_file"):
                ci_state.key()

    def test_github_subprocess_output_and_timeout_are_bounded(self):
        class FakeProc:
            def __init__(self, output=b"", *, hang=False):
                self.stdin=None;self.stdout=io.BytesIO(output);self.stderr=io.BytesIO(b"")
                self.hang=hang;self.killed=False;self.returncode=0 if not hang else None
            def poll(self):return None if self.hang and not self.killed else self.returncode
            def kill(self):self.killed=True;self.returncode=-9
            def wait(self,timeout=None):
                if self.hang and not self.killed:raise subprocess.TimeoutExpired("gh",timeout)
                return self.returncode
        too_big=FakeProc(b"123456")
        with patch.object(ci_state.subprocess,"Popen",return_value=too_big):
            with self.assertRaisesRegex(ConfigurationError,"github_response_too_large"):
                ci_state._bounded_gh_run(["gh"],None,5,timeout=.5)
        hanging=FakeProc(hang=True)
        with patch.object(ci_state.subprocess,"Popen",return_value=hanging):
            with self.assertRaisesRegex(ConfigurationError,"github_state_api_timeout"):
                ci_state._bounded_gh_run(["gh"],None,5,timeout=.02)

    def test_key_file_symlink_is_rejected(self):
        key_path = self.root / "state.key"
        target = self.root / "target.key"
        target.write_text(self.key)
        target.chmod(0o600)
        key_path.symlink_to(target)
        with patch.dict(os.environ, {"COLLECTOR_STATE_KEY": "", "COLLECTOR_STATE_KEY_FILE": str(key_path)}, clear=False):
            with self.assertRaisesRegex(ConfigurationError, "invalid_state_key_file"):
                ci_state.key()

    def test_restore_holds_for_orphan_or_missing_checkpoint_artifact(self):
        point = checkpoint(artifact_id=7)
        with patch.object(ci_state, "pointer", return_value=(point, "blob-sha")), \
             patch.object(ci_state, "artifacts", return_value=[{"id": 8, "name": "linkedin-private-state-x",
                                                                  "expired": False, "size_in_bytes": 10}]), \
             patch.object(ci_state, "gh") as gh:
            with self.assertRaisesRegex(ConfigurationError, "orphan_state_artifact_requires_recovery"):
                ci_state.restore(REPOSITORY, self.root / "state", self.root / "context.json")
            gh.assert_not_called()
        with patch.object(ci_state, "pointer", return_value=(point, "blob-sha")), \
             patch.object(ci_state, "artifacts", return_value=[]), patch.object(ci_state, "gh") as gh:
            with self.assertRaisesRegex(ConfigurationError, "state_artifact_missing_or_oversized"):
                ci_state.restore(REPOSITORY, self.root / "state", self.root / "context.json")
            gh.assert_not_called()

    def test_restore_rejects_archive_members_outside_exact_state_file(self):
        point = checkpoint(artifact_id=7)
        artifact = {"id": 7, "name": "linkedin-private-state-7", "expired": False, "size_in_bytes": 0}
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as z:
            z.writestr("state.enc", b"encrypted")
            z.writestr("extra.txt", b"unexpected")
        artifact["size_in_bytes"] = len(buffer.getvalue())
        with patch.object(ci_state, "pointer", return_value=(point, "blob-sha")), \
             patch.object(ci_state, "artifacts", return_value=[artifact]), \
             patch.object(ci_state, "gh", return_value=buffer.getvalue()), \
             patch.object(ci_state, "unseal") as unseal:
            with self.assertRaisesRegex(ConfigurationError, "unexpected_state_archive_members"):
                ci_state.restore(REPOSITORY, self.root / "state", self.root / "context.json")
            unseal.assert_not_called()

    def test_restore_rejects_oversized_state_zip_member_before_read(self):
        point = checkpoint(artifact_id=7)
        artifact = {"id": 7, "name": "linkedin-private-state-7", "expired": False, "size_in_bytes": len(b"zip bytes")}

        class FakeZip:
            def __init__(self, *_args, **_kwargs): pass
            def __enter__(self): return self
            def __exit__(self, *_args): return False
            def infolist(self):
                return [type("Info", (), {"filename": "state.enc", "file_size": ci_state.MAX_ENCRYPTED + 1,
                                           "compress_size": 10})()]
            def read(self, _name): raise AssertionError("oversized member must not be decompressed")
            def open(self, *_args, **_kwargs): raise AssertionError("oversized member must not be decompressed")

        with patch.object(ci_state, "pointer", return_value=(point, "blob-sha")), \
             patch.object(ci_state, "artifacts", return_value=[artifact]), \
             patch.object(ci_state, "gh", return_value=b"zip bytes"), \
             patch.object(ci_state.zipfile, "ZipFile", FakeZip):
            with self.assertRaisesRegex(ConfigurationError, "unexpected_state_archive_members"):
                ci_state.restore(REPOSITORY, self.root / "state", self.root / "context.json")

    def test_bootstrap_needs_first_run_flag_empty_artifact_set_and_valid_key(self):
        with patch.object(ci_state, "pointer", return_value=(None, None)), \
             patch.object(ci_state, "artifacts", return_value=[]), \
             patch.object(ci_state, "gh", return_value=None), \
             patch.dict(os.environ, {"GITHUB_ACTIONS": "true", "GITHUB_EVENT_NAME": "schedule",
                                     "COLLECTOR_BOOTSTRAP_ALLOWED": "true"}, clear=False):
            with self.assertRaisesRegex(ConfigurationError, "missing_state_checkpoint_requires"):
                ci_state.restore(REPOSITORY, self.root / "state", self.root / "context.json", bootstrap=True)
        with patch.object(ci_state, "pointer", return_value=(None, None)), \
             patch.object(ci_state, "artifacts", return_value=[{"id": 1, "name": "linkedin-private-state-1",
                                                                  "expired": True, "size_in_bytes": 1}]), \
             patch.object(ci_state, "gh", return_value=None), \
             patch.dict(os.environ, {"GITHUB_ACTIONS": "true", "GITHUB_EVENT_NAME": "workflow_dispatch",
                                     "COLLECTOR_BOOTSTRAP_ALLOWED": "true"}, clear=False):
            with self.assertRaisesRegex(ConfigurationError, "missing_state_checkpoint_requires"):
                ci_state.restore(REPOSITORY, self.root / "state", self.root / "context.json", bootstrap=True)
        with patch.object(ci_state, "pointer", return_value=(None, None)), \
             patch.object(ci_state, "artifacts", return_value=[]), \
             patch.object(ci_state, "gh", return_value={"ref": "refs/heads/collector-state"}), \
             patch.dict(os.environ, {"GITHUB_ACTIONS": "true", "GITHUB_EVENT_NAME": "workflow_dispatch",
                                     "COLLECTOR_BOOTSTRAP_ALLOWED": "true"}, clear=False):
            with self.assertRaisesRegex(ConfigurationError, "state_branch_exists_without_checkpoint"):
                ci_state.restore(REPOSITORY, self.root / "state", self.root / "context.json", bootstrap=True)
        with patch.object(ci_state, "pointer", return_value=(None, None)), \
             patch.object(ci_state, "artifacts", return_value=[]), \
             patch.object(ci_state, "gh", return_value=None), \
             patch.dict(os.environ, {"GITHUB_ACTIONS": "true", "GITHUB_EVENT_NAME": "workflow_dispatch",
                                     "COLLECTOR_BOOTSTRAP_ALLOWED": "true", "COLLECTOR_STATE_KEY": "",
                                     "COLLECTOR_STATE_KEY_FILE": ""}, clear=False):
            with self.assertRaisesRegex(ConfigurationError, "missing_state_encryption_key"):
                ci_state.restore(REPOSITORY, self.root / "state", self.root / "context.json", bootstrap=True)
            self.assertFalse((self.root / "context.json").exists())

    def test_local_bootstrap_is_explicit_and_ci_bootstrap_needs_dispatch_gate(self):
        with patch.object(ci_state,"pointer",return_value=(None,None)), \
             patch.object(ci_state,"artifacts",return_value=[]), \
             patch.object(ci_state,"gh",return_value=None), \
             patch.dict(os.environ,{"GITHUB_ACTIONS":"","GITHUB_EVENT_NAME":"","COLLECTOR_BOOTSTRAP_ALLOWED":""},clear=False):
            result=ci_state.restore(REPOSITORY,self.root/"local-state",self.root/"local-context.json",bootstrap=True)
            self.assertTrue(result["bootstrap"])
        with patch.object(ci_state,"pointer",return_value=(None,None)), \
             patch.object(ci_state,"artifacts",return_value=[]), \
             patch.object(ci_state,"gh",return_value=None), \
             patch.dict(os.environ,{"GITHUB_ACTIONS":"true","GITHUB_EVENT_NAME":"workflow_dispatch",
                                    "COLLECTOR_BOOTSTRAP_ALLOWED":"true"},clear=False):
            result=ci_state.restore(REPOSITORY,self.root/"ci-state",self.root/"ci-context.json",bootstrap=True)
            self.assertTrue(result["bootstrap"])

    def test_artifact_listing_page_cap_and_invalid_member_count(self):
        all_artifacts = [{"id": i, "name": "linkedin-private-state-x", "expired": False} for i in range(100)]
        with patch.object(ci_state, "gh", return_value={"artifacts": all_artifacts}) as gh:
            with self.assertRaisesRegex(ConfigurationError, "artifact_listing_page_cap"):
                ci_state.artifacts(REPOSITORY)
            self.assertEqual(gh.call_count, 10)

    def test_publish_compare_and_swap_readback_and_conflict(self):
        current = checkpoint(artifact_id=3, revision=3)
        current_blob = "checkpoint-blob-3"
        context = {"repository": REPOSITORY, "revision": 3,
                   "checkpoint_sha256": hashlib.sha256(ci_state.canonical(current)).hexdigest(),
                   "blob_sha": current_blob}
        source = self.root / "publish-source"
        store = self.seeded_store(source);store.close()
        report = ci_state.seal(source, self.root / "publish-state.enc", context)
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("state.enc", (self.root / "publish-state.enc").read_bytes())
        zip_bytes = buffer.getvalue()
        artifact = {"id": 99, "name": "linkedin-private-state-99", "expired": False,
                    "size_in_bytes": len(zip_bytes)}
        next_pointer = None
        put_bodies = []

        def fake_gh(path, *, method="GET", body=None, binary=False, missing=False, response_limit=None):
            nonlocal next_pointer
            if path.endswith("/actions/artifacts/99/zip"):
                return zip_bytes
            if path.startswith("repos/") and "/contents/" in path:
                if method == "PUT":
                    put_bodies.append(body)
                    next_pointer = json.loads(base64.b64decode(body["content"]))
                    return {"ok": True}
                selected = next_pointer or current
                blob = "checkpoint-blob-4" if next_pointer else current_blob
                return {"content": base64.b64encode(ci_state.canonical(selected)).decode(), "sha": blob}
            raise AssertionError("unexpected mocked GitHub API path")

        with patch.object(ci_state, "gh", side_effect=fake_gh), patch.object(ci_state, "artifacts", return_value=[artifact]):
            result = ci_state.publish(REPOSITORY, "99", report, context)
        self.assertTrue(result["verified"])
        self.assertEqual(result["checkpoint_revision"], 4)
        self.assertEqual(len(put_bodies), 1)
        self.assertEqual(put_bodies[0]["sha"], current_blob)

        with patch.object(ci_state, "pointer", return_value=(current, current_blob)), patch.object(ci_state, "gh") as gh:
            with self.assertRaisesRegex(ConfigurationError, "concurrent_checkpoint_change"):
                ci_state.publish(REPOSITORY, "99", report, {**context, "checkpoint_sha256": "0" * 64})
            gh.assert_not_called()

        with patch.object(ci_state, "gh") as gh:
            with self.assertRaisesRegex(ConfigurationError, "invalid_seal_report"):
                ci_state.publish(REPOSITORY, "99", {**report, "revision": 7}, context)
            gh.assert_not_called()


if __name__ == "__main__":
    unittest.main()
