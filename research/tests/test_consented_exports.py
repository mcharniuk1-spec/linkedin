import csv
import os
import tempfile
import unittest
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from research.collector.consented_exports import ConsentedStore, ExportError, parse_export

NOW = datetime(2026, 10, 31, 12, tzinfo=timezone.utc)


class OwnerExportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir='/private/tmp' if os.path.isdir('/private/tmp') else None)
        self.base = Path(self.tmp.name).resolve()
        self.path = self.base / 'input.csv'
        self.store = ConsentedStore(self.base / 'private')

    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def write(self, headers, *rows):
        with self.path.open('w', newline='', encoding='utf-8') as out:
            writer = csv.writer(out)
            writer.writerow(headers)
            writer.writerows(rows)

    def grant(self, **kwargs):
        opts = {'consent_reference':'signed-agreement-123', 'purpose':'consented_account_analytics',
                'expires_at':NOW+timedelta(days=50), 'retention_days':2, 'now':NOW}
        opts.update(kwargs)
        return self.store.grant('account-123', **opts)

    def import_(self, **kwargs):
        opts = {'observed_at':NOW, 'granularity':'post', 'now':NOW}
        opts.update(kwargs)
        return self.store.import_file('account-123', self.path, **opts)

    def test_import_requires_consent_and_preserves_counters_and_unknowns(self):
        self.write(['Post ID','Post URL','Date','Reactions','Likes','Comments','Impressions','secret text'],
                   ['123','https://www.linkedin.com/posts/123?trk=x','2026-10-30','12','','3','','private text'])
        with self.assertRaisesRegex(ExportError,'active_consent_required'): self.import_()
        self.grant()
        result=self.import_()
        self.assertEqual((result['inserted'], result['duplicates']),(1,0))
        self.assertEqual(self.import_()['duplicates'],1)
        row=self.store.get_snapshots('account-123',now=NOW)[0]
        self.assertEqual(row['metrics']['reactions'],12)
        self.assertIsNone(row['metrics']['likes'])
        self.assertEqual(row['metrics']['comments'],3)
        self.assertIsNone(row['metrics']['impressions'])
        self.assertEqual(row['post_url'],'https://www.linkedin.com/posts/123')
        self.assertNotIn('private text',str(row))
        self.assertEqual(os.stat(self.store.root).st_mode & 0o777,0o700)
        self.assertEqual(os.stat(self.store.path).st_mode & 0o777,0o600)
        self.assertTrue(self.path.exists())

    def test_reobservation_aliases_and_conflicts(self):
        self.grant()
        self.write(['Post ID','Post URL','Reactions'],['123','https://linkedin.com/posts/123',10])
        self.import_()
        self.write(['Post URL','Reactions'],['https://linkedin.com/posts/123',10])
        self.assertEqual(self.import_()['duplicates'],1)
        six=NOW+timedelta(hours=6)
        self.write(['Post URL','Reactions'],['https://linkedin.com/posts/123',20])
        self.assertEqual(self.import_(observed_at=six,now=six)['inserted'],1)
        rows=self.store.get_snapshots('account-123',now=six)
        self.assertEqual(len(rows),2)
        self.assertEqual(rows[0]['subject_id'],rows[1]['subject_id'])
        self.write(['Post URL','Reactions'],['https://linkedin.com/posts/123',21])
        with self.assertRaisesRegex(ExportError,'conflicting_same_observation'):
            self.import_(observed_at=six,now=six)
        self.assertEqual(len(self.store.get_snapshots('account-123',now=six)),2)

    def test_daily_aggregate_stays_distinct_from_posts(self):
        self.grant()
        self.write(['Date','Impressions','Comments'],['2026-10-29','100',''])
        with self.assertRaisesRegex(ExportError,'post_identity_column_required'):self.import_()
        result=self.import_(granularity='daily_aggregate')
        self.assertEqual(result['granularity'],'daily_aggregate')
        self.assertEqual(self.store.get_snapshots('account-123',now=NOW)[0]['subject_id'],'day:2026-10-29')

    def test_purge_and_revocation_remove_private_rows_and_aliases(self):
        self.grant()
        self.write(['Post ID','Reactions'],['123',10])
        self.import_()
        self.assertEqual(self.store.purge_expired(now=NOW+timedelta(days=2))['expired_rows_deleted'],1)
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM aliases').fetchone()[0],0)
        self.import_(observed_at=NOW+timedelta(days=3),now=NOW+timedelta(days=3))
        result=self.store.revoke('account-123',now=NOW+timedelta(days=3))
        self.assertEqual(result['rows_deleted'],1)
        self.assertFalse(result['source_file_deleted'])
        self.assertFalse(result['external_backups_deleted'])
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM snapshots').fetchone()[0],0)
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM aliases').fetchone()[0],0)
        with self.assertRaisesRegex(ExportError,'active_consent_required'):
            self.import_(now=NOW+timedelta(days=3))
        self.assertTrue(self.path.exists())

    def test_validation_failures_do_not_import(self):
        self.grant()
        for headers, rows, error in [
            (['Post ID','Likes','Like'],[['a','1','1']],'ambiguous_duplicate_header'),
            (['Post ID','Likes'],[['a','-3']],'invalid_nonnegative_count'),
            (['Post ID','Likes'],[['a','1,5']],'invalid_nonnegative_count'),
            (['Post ID','Likes'],[['a','1'],['a','2']],'duplicate_identity_in_export'),
            (['Post URL','Likes'],[['https://example.com/x','1']],'invalid_linkedin_post_url'),
            (['Post ID','Date','Likes'],[['a','2027-01-01','1']],'future_publication_or_aggregate_date')]:
            self.write(headers,*rows)
            with self.subTest(error=error),self.assertRaisesRegex(ExportError,error):self.import_()
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM snapshots').fetchone()[0],0)
        with self.assertRaisesRegex(ExportError,'api_ingestion_not_enabled'):self.import_(source_kind='api')
        with self.assertRaisesRegex(ExportError,'future_observation_not_allowed'):self.import_(observed_at=NOW+timedelta(seconds=1))

    def test_consent_limits_and_existing_database_separation(self):
        with self.assertRaisesRegex(ExportError,'explicit_allowed_purpose_required'):self.grant(purpose='unlimited')
        with self.assertRaisesRegex(ExportError,'invalid_consent_expiry_or_retention'):self.grant(retention_days=0)
        self.grant(expires_at=NOW+timedelta(hours=1))
        self.write(['Post ID','Likes'],['a',1])
        self.import_()
        self.assertEqual(self.store.purge_expired(now=NOW+timedelta(hours=1))['expired_rows_deleted'],1)
        with self.assertRaisesRegex(ExportError,'active_consent_required'):
            self.store.get_snapshots('account-123',now=NOW+timedelta(hours=1))
        (self.base/'collector.sqlite').touch()
        with self.assertRaisesRegex(ExportError,'separate_private_store_required'):
            ConsentedStore(self.base/'other')

    def test_xlsx_parsing_and_explicit_unsupported_xls(self):
        p=self.base/'input.xlsx'
        book='''<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Report" sheetId="1" r:id="rId1"/></sheets></workbook>'''
        rels='''<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Target="worksheets/sheet1.xml"/></Relationships>'''
        sheet='''<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData><row r="1"><c r="A1" t="inlineStr"><is><t>Post ID</t></is></c><c r="B1" t="inlineStr"><is><t>Likes</t></is></c></row><row r="2"><c r="A2" t="inlineStr"><is><t>abc</t></is></c><c r="B2"><v>5</v></c></row></sheetData></worksheet>'''
        def make(s):
            with zipfile.ZipFile(p,'w') as z:
                z.writestr('xl/workbook.xml',book)
                z.writestr('xl/_rels/workbook.xml.rels',rels)
                z.writestr('xl/worksheets/sheet1.xml',s)
        make(sheet)
        self.assertEqual(parse_export(p,granularity='post')['rows'][0]['metrics']['likes'],5)
        with self.assertRaisesRegex(ExportError,'xlsx_sheet_not_found'):
            parse_export(p,granularity='post',sheet_name='wrong')
        make(sheet.replace('<v>5</v>','<f>2+3</f><v>5</v>'))
        with self.assertRaisesRegex(ExportError,'xlsx_formula_cells_not_supported'):
            parse_export(p,granularity='post')
        xls=self.base/'page.xls';xls.write_bytes(b'not-an-xlsx')
        with self.assertRaisesRegex(ExportError,'binary_xls_unsupported'):
            parse_export(xls,granularity='post')

    def test_explicit_excel_date_format(self):
        self.write(['Date','Impressions'],['2','5'])
        parsed=parse_export(self.path,granularity='daily_aggregate',date_format='excel1900')
        self.assertEqual(parsed['rows'][0]['date'],'1900-01-02')
        self.write(['Date','Impressions'],['60','5'])
        with self.assertRaisesRegex(ExportError,'invalid_excel_date_serial'):
            parse_export(self.path,granularity='daily_aggregate',date_format='excel1900')


if __name__ == '__main__':
    unittest.main()
