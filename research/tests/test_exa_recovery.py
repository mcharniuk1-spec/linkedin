import gzip
import hashlib
import json
import tempfile
import unittest
from research.collector.contracts import ConfigurationError,utcnow
from research.collector.exa_recovery import reconcile
from research.collector.store import Store


class ExaRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.store=Store(self.tmp.name)
        self.store.db.execute('CREATE TABLE discoveries (id TEXT PRIMARY KEY,payload TEXT NOT NULL)')
    def tearDown(self):self.store.close();self.tmp.cleanup()
    def evidence(self,text,is_error=False):
        raw=json.dumps({'content':[{'type':'text','text':text}],'isError':is_error}).encode()
        digest=hashlib.sha256(raw).hexdigest()
        with self.store.db:
            self.store.db.execute('INSERT INTO raw_objects VALUES (?,?)',(digest,gzip.compress(raw)))
            self.store.db.execute('INSERT INTO discoveries VALUES (?,?)',('fixture',json.dumps({'source_id':'exa-search','raw_sha256':digest,'collected_at':utcnow()})))
        self.store.suspend('exa-search','discovery_tool_quota_or_error')
        self.store.suspend('linkedin-public','challenge_page')
    def test_manual_reconciliation_preserves_linkedin_hold(self):
        self.evidence('Title: Lessons about quota\nURL: https://example.test')
        self.assertEqual(reconcile(self.store)['status'],'exa_false_positive_reconciled')
        self.assertIsNone(self.store.get_suspension('exa-search'))
        self.assertEqual(self.store.get_suspension('linkedin-public')['reason'],'challenge_page')
    def test_provider_error_or_no_proven_result_keeps_hold(self):
        for text,is_error in [('Quota exceeded',False),('Title: quota',True),('Title: ordinary',False),('Title: quota\nERROR: quota exceeded',False)]:
            with self.subTest(text=text),tempfile.TemporaryDirectory() as td:
                old=self.store;self.store=Store(td);self.store.db.execute('CREATE TABLE discoveries (id TEXT PRIMARY KEY,payload TEXT NOT NULL)')
                self.evidence(text,is_error)
                with self.assertRaises(ConfigurationError):reconcile(self.store)
                self.assertIsNotNone(self.store.get_suspension('exa-search'))
                self.store.close();self.store=old


if __name__=='__main__':unittest.main()
