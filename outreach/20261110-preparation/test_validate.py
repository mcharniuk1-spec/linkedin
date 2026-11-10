"""Synthetic regression cases for preparation boundaries; no external effects."""
from pathlib import Path
import csv
import json
import shutil
import tempfile
import unittest
import validate as v

HERE=Path(__file__).resolve().parent

class PreparationTests(unittest.TestCase):
    def template(self,name='first-message.template.json'):
        return v.read_json(HERE/name)

    def test_complete_empty_package_and_labelled_example_pass(self):
        self.assertEqual(v.validate_pack(HERE)['errors'],[])

    def test_result_without_source_and_measurement_is_rejected(self):
        d=self.template();d['claims']=[{'text':'We saved 4 hours','kind':'result','support_state':'proposed','source_ids':[]}]
        self.assertTrue(any('unsupported result' in e for e in v.validate_document(d)))

    def test_unmapped_numeric_result_is_rejected(self):
        d=self.template();d['record_mode']='preparation';d['record_id']='X';d['message']['body']='We saved 4 hours.'
        self.assertTrue(any('unmapped quantitative result' in e for e in v.validate_document(d)))

    def test_guaranteed_meetings_are_rejected(self):
        d=self.template();d['message']['body']='We guarantee qualified meetings.'
        self.assertTrue(any('guaranteed business outcome' in e for e in v.validate_document(d)))

    def test_missing_permission_object_is_rejected(self):
        d=self.template();del d['permissions'];self.assertTrue(v.validate_document(d))

    def test_missing_stop_flag_is_rejected(self):
        d=self.template();del d['stop']['asked_to_stop'];self.assertTrue(any('missing stop fields' in e for e in v.validate_document(d)))

    def test_missing_source_date_is_rejected(self):
        d=v.read_json(HERE/'synthetic-example.json');del d['source_records'][0]['checked_at'];self.assertTrue(any('missing source identity/date' in e for e in v.validate_document(d)))

    def test_unknown_claim_source_is_rejected(self):
        d=v.read_json(HERE/'synthetic-example.json');d['first_message']['claims'][0]['source_ids']=['ABSENT'];self.assertTrue(any('unknown source ID' in e for e in v.validate_document(d)))

    def test_synthetic_source_cannot_become_real_preparation(self):
        d=v.read_json(HERE/'synthetic-example.json');d['record_mode']='preparation';self.assertTrue(any('.invalid source' in e for e in v.validate_document(d)))

    def test_more_than_one_follow_up_is_rejected(self):
        d=self.template('follow-up-and-stop.template.json');d['follow_ups_actually_sent']=2;self.assertTrue(any('one-follow-up limit' in e for e in v.validate_document(d)))

    def test_decline_cannot_remain_clear(self):
        d=self.template();d['stop']={k:'no' for k in v.STOP_FLAGS};d['stop'].update({'status':'clear','reason':''});d['stop']['recipient_declined']='yes';self.assertTrue(any('stop disposition' in e for e in v.validate_document(d)))

    def test_missing_actual_first_message_blocks_follow_up_eligibility(self):
        d=self.template('follow-up-and-stop.template.json');d['manual_eligibility']='eligible_for_owner_review';self.assertTrue(any('eligibility conflicts' in e for e in v.validate_document(d)))

    def test_sending_authority_cannot_be_created_by_template(self):
        d=self.template();d['send_authorization']='authorized';self.assertTrue(any('preparation only' in e for e in v.validate_document(d)))

    def test_fake_relationship_is_rejected(self):
        d=self.template();d['claims']=[{'text':'As we discussed','kind':'relationship','support_state':'proposed','source_ids':[]}];self.assertTrue(any('unconfirmed relationship' in e for e in v.validate_document(d)))

    def test_malformed_claim_array_is_rejected(self):
        d=self.template();d['claims']={};self.assertTrue(any('claims must be an array' in e for e in v.validate_document(d)))

    def test_missing_csv_source_permission_or_stop_header_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=HERE) as temp:
            p=Path(temp)/'test.csv'
            with p.open('w',newline='') as f:csv.writer(f).writerow([h for h in v.FIT_HEADERS if h not in ['source_id','permission_state','stop_status']])
            self.assertTrue(v.validate_csv(p,v.FIT_HEADERS))

    def test_ragged_csv_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=HERE) as temp:
            p=Path(temp)/'test.csv'
            with p.open('w',newline='') as f:
                w=csv.writer(f);w.writerow(v.FIT_HEADERS);w.writerow(['too','short'])
            self.assertTrue(any('malformed CSV row' in e for e in v.validate_csv(p,v.FIT_HEADERS)))

    def test_valid_schema_in_the_wrong_template_file_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=HERE) as temp:
            pack=Path(temp)
            for name in v.EXPECTED_FILES:shutil.copyfile(HERE/name,pack/name)
            (pack/'warm-intro-context.template.json').write_text((HERE/'first-message.template.json').read_text())
            result=v.validate_pack(pack)
            self.assertTrue(any('filename/schema mismatch' in e for e in result['errors']))

    def test_filename_record_mode_contract_is_enforced(self):
        with tempfile.TemporaryDirectory(dir=HERE) as temp:
            pack=Path(temp)
            for name in v.EXPECTED_FILES:shutil.copyfile(HERE/name,pack/name)
            p=pack/'first-message.template.json';d=v.read_json(p);d['record_mode']='preparation';p.write_text(json.dumps(d))
            result=v.validate_pack(pack)
            self.assertTrue(any('filename/record_mode mismatch' in e for e in result['errors']))

    def test_non_object_permissions_fails_cleanly_for_relationship_claim(self):
        d=self.template();d['permissions']=[];d['claims']=[{'text':'As we discussed','kind':'relationship','support_state':'source_confirmed','source_ids':[]}]
        self.assertTrue(any('permissions must be an object' in e for e in v.validate_document(d)))

    def test_non_object_stop_fails_cleanly_for_follow_up(self):
        d=self.template('follow-up-and-stop.template.json');d['stop']=None;d['manual_eligibility']='eligible_for_owner_review'
        self.assertTrue(any('stop must be an object' in e for e in v.validate_document(d)))

    def test_boolean_follow_up_limit_is_not_integer_one(self):
        d=self.template('follow-up-and-stop.template.json');d['follow_up_limit']=True
        self.assertTrue(any('one-follow-up limit' in e for e in v.validate_document(d)))

    def test_duplicate_json_keys_are_rejected_before_parsing_discards_them(self):
        with tempfile.TemporaryDirectory(dir=HERE) as temp:
            p=Path(temp)/'test.json';p.write_text('{"record_mode":"template","record_mode":"preparation"}')
            with self.assertRaises(ValueError):v.read_json(p)

if __name__=='__main__':unittest.main()
