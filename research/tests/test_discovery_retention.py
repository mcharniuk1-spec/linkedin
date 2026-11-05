import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

from research.collector.store import Store
from research.collector.discovery_retention import RetentionError, expire, register


class DiscoveryRetentionTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.store=Store(self.tmp.name)
        self.store.db.execute('CREATE TABLE discoveries (id TEXT PRIMARY KEY,payload TEXT NOT NULL)')
        self.now=datetime(2026,11,1,tzinfo=timezone.utc);self.digest='a'*64
    def tearDown(self):self.store.close();self.tmp.cleanup()
    def observe(self, ident, digest=None, offset=0, new=1):
        digest=digest or self.digest; at=(self.now+timedelta(days=offset)).isoformat()
        with self.store.db:
            rowcount=self.store.db.execute('INSERT OR IGNORE INTO raw_objects VALUES (?,?)',(digest,b'fixture')).rowcount
            self.assertEqual(rowcount,new)
            self.store.db.execute('INSERT INTO discoveries VALUES (?,?)',(ident,json.dumps(
                {'source_id':'exa-search','raw_sha256':digest,'collected_at':at})))
            return register(self.store,ident,digest,observed_at=at,created_new_raw=rowcount,registered_at=at)
    def purge(self, days):
        with self.store.db:return expire(self.store,now=(self.now+timedelta(days=days)).isoformat())
    def raw_exists(self,digest=None):
        return bool(self.store.db.execute('SELECT 1 FROM raw_objects WHERE sha256=?',(digest or self.digest,)).fetchone())

    def test_exact_thirty_day_boundary_preserves_provenance(self):
        self.assertEqual(self.observe('a'),'managed')
        self.assertEqual(self.purge(29)['expired_raw_objects'],0);self.assertTrue(self.raw_exists())
        self.assertEqual(self.purge(30)['expired_raw_objects'],1);self.assertFalse(self.raw_exists())
        payload=json.loads(self.store.db.execute('SELECT payload FROM discoveries WHERE id="a"').fetchone()[0])
        self.assertEqual(payload['raw_sha256'],self.digest)
        self.assertEqual(payload['raw_retention']['status'],'expired')

    def test_reobservation_extends_shared_raw_lifetime(self):
        self.observe('a');self.observe('b',offset=5,new=0)
        self.assertEqual(self.purge(30)['expired_raw_objects'],0);self.assertTrue(self.raw_exists())
        self.assertEqual(self.purge(35)['expired_raw_objects'],1);self.assertFalse(self.raw_exists())

    def test_expired_tombstone_does_not_block_later_reacquired_same_digest(self):
        self.observe('first');self.assertEqual(self.purge(30)['expired_raw_objects'],1)
        self.observe('second',offset=40,new=1)
        self.assertEqual(self.purge(70)['expired_raw_objects'],1)
        self.assertFalse(self.raw_exists())

    def test_late_registration_never_shortens_retention(self):
        observed=self.now.isoformat();registered=(self.now+timedelta(days=10)).isoformat()
        with self.store.db:
            self.store.db.execute('INSERT INTO raw_objects VALUES (?,?)',(self.digest,b'fixture'))
            self.store.db.execute('INSERT INTO discoveries VALUES (?,?)',('late',json.dumps(
                {'source_id':'exa-search','raw_sha256':self.digest,'collected_at':observed})))
            register(self.store,'late',self.digest,observed_at=observed,created_new_raw=1,registered_at=registered)
        self.assertEqual(self.purge(39)['expired_raw_objects'],0)
        self.assertEqual(self.purge(40)['expired_raw_objects'],1)

    def test_unregistered_raw_and_unregistered_shared_reference_are_preserved(self):
        self.store.db.execute('INSERT INTO raw_objects VALUES (?,?)',('b'*64,b'legacy'))
        self.assertEqual(self.observe('legacy','b'*64,new=0),'unmanaged_existing')
        self.observe('new')
        self.store.db.execute('INSERT INTO discoveries VALUES (?,?)',('older',json.dumps({'raw_sha256':self.digest})))
        result=self.purge(60)
        self.assertEqual(result['blocked_shared_objects'],1)
        self.assertTrue(self.raw_exists());self.assertTrue(self.raw_exists('b'*64))

    def test_any_other_table_text_reference_blocks_deletion(self):
        self.observe('a')
        self.store.db.execute('CREATE TABLE arbitrary (data BLOB)')
        self.store.db.execute('INSERT INTO arbitrary VALUES (?)',('prefix '+self.digest,))
        self.assertEqual(self.purge(30)['blocked_shared_objects'],1);self.assertTrue(self.raw_exists())

    def test_malformed_date_fails_closed_without_partial_deletion(self):
        self.observe('a');self.observe('b','b'*64)
        self.store.db.execute('UPDATE exa_retention_refs SET expires_at=? WHERE discovery_id=?',('not-a-date','b'))
        with self.assertRaises(RetentionError):self.purge(90)
        self.assertTrue(self.raw_exists());self.assertTrue(self.raw_exists('b'*64))

    def test_malformed_payload_and_unexpected_schema_fail_closed(self):
        self.observe('a')
        self.store.db.execute('UPDATE discoveries SET payload=? WHERE id=?',('[]','a'))
        with self.assertRaises(RetentionError):self.purge(90)
        self.assertTrue(self.raw_exists())
        self.store.db.execute('ALTER TABLE exa_retention_objects ADD COLUMN unexpected TEXT')
        with self.assertRaises(RetentionError):self.purge(90)

    def test_reject_short_retention_and_uncertain_insert_state(self):
        at=self.now.isoformat()
        self.store.db.execute('INSERT INTO raw_objects VALUES (?,?)',(self.digest,b'fixture'))
        self.store.db.execute('INSERT INTO discoveries VALUES (?,?)',('a',json.dumps(
            {'source_id':'exa-search','raw_sha256':self.digest,'collected_at':at})))
        with self.assertRaises(RetentionError):register(self.store,'a',self.digest,observed_at=at,created_new_raw=1,retention_days=29)
        with self.assertRaises(RetentionError):register(self.store,'a',self.digest,observed_at=at,created_new_raw=True)
        self.assertTrue(self.raw_exists())


if __name__=='__main__':unittest.main()
