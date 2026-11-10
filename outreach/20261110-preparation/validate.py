#!/usr/bin/env python3
"""Validate outreach-preparation structures. No networking or sending capability.

Checks completeness, explicit source/permission/stop state and common unsupported
result patterns. It cannot verify source truth, consent, legal compliance or intent.
"""
from pathlib import Path
from datetime import date
from urllib.parse import urlsplit
import argparse
import csv
import json
import re
import sys

FIT_HEADERS = ['record_id','company_name','company_url','recipient_role','source_id','source_url','source_checked_at','source_observation','rights_state','permission_state','firmographic_fit_state','topic_fit_state','expressed_need_state','expressed_need_source_id','buying_interest_state','buying_interest_source_id','exclusions_or_unknowns','stop_status','stop_reason','send_authorization','review_state']
CONVERSATION_HEADERS = ['record_id','company_record_id','conversation_at','channel','source_note_id','rights_state','permission_state','privacy_state','firmographic_fit_state','expressed_need_state','buying_interest_state','stated_problem','budget_state','budget_note','objection','response_used','next_step_state','next_step_owner_role','follow_up_permission','stop_status','stop_reason','counts_as_qualifying_conversation','qualifying_definition_version','offer_yes','yes_definition_version','learning_trigger_review','send_authorization']
JSON_CONTRACTS = {
    'warm-intro-context.template.json': ('outspoken-warm-context/1','template'),
    'first-message.template.json': ('outspoken-first-message/1','template'),
    'follow-up-and-stop.template.json': ('outspoken-follow-up/1','template'),
    'discovery-and-mini-audit.template.json': ('outspoken-discovery-mini-audit/1','template'),
    'synthetic-example.json': ('outspoken-outreach-worked-example/1','synthetic'),
}
JSON_FILES = list(JSON_CONTRACTS)
EXPECTED_FILES = {'README.md','fit-source-verification.csv','conversation-log.csv',*JSON_FILES,'validate.py','test_validate.py'}
STOP_FLAGS = ['recipient_declined','asked_to_stop','wrong_recipient','permission_unresolved','source_uncertain','prior_reply_needs_review']
PERMISSIONS = ['source_use','relationship_context_use','third_party_name_use','channel_and_legal_review']
PERMISSION_STATES = {'pending','reference_only','permission_verified','not_applicable','synthetic_only'}
KINDS = {'public_observation','proposed_service','result','relationship','expressed_need','buying_interest'}
RESULT_CONTEXT = {'population','baseline','comparison','sample_size','unit','period','measurement_source','human_review_record'}
SCHEMAS = {'outspoken-warm-context/1','outspoken-first-message/1','outspoken-follow-up/1','outspoken-discovery-mini-audit/1','outspoken-outreach-worked-example/1'}


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key: '+key)
        result[key] = value
    return result


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=unique_pairs)


def validate_document(doc, label='document'):
    errors = []
    def err(message): errors.append(label+': '+message)
    if not isinstance(doc, dict): return [label+': root must be an object']
    required = {'schema','record_mode','record_id','provenance','source_records','permissions','stop','send_authorization','review_state'}
    if not required <= doc.keys(): err('missing common fields: '+','.join(sorted(required-doc.keys())))
    if doc.get('schema') not in SCHEMAS: err('unknown schema')
    mode = doc.get('record_mode')
    if mode not in {'template','synthetic','preparation'}: err('invalid record_mode')
    if mode != 'template' and not doc.get('record_id'): err('non-template needs record_id')
    if doc.get('send_authorization') != 'not_authorized': err('kit is preparation only; send_authorization must be not_authorized')
    if doc.get('review_state') not in {'pending_founder_review','preparation_reviewed'}: err('invalid preparation review_state')
    prov = doc.get('provenance', {})
    if not isinstance(prov,dict) or not all(prov.get(k) for k in ['owner','source_type','rights_state','created_on','use_limit']): err('provenance/source rights are incomplete')
    elif mode == 'synthetic' and prov['source_type'] != 'owned_synthetic_example': err('synthetic example needs explicit owned_synthetic_example provenance')
    perms = doc.get('permissions',{})
    if not isinstance(perms,dict):
        err('permissions must be an object')
        perms = {}
    if not set(PERMISSIONS) <= perms.keys(): err('missing permission fields')
    elif any(perms[k] not in PERMISSION_STATES for k in PERMISSIONS): err('invalid permission state')
    stop = doc.get('stop',{})
    if not isinstance(stop,dict):
        err('stop must be an object')
        stop = {}
    if not set(STOP_FLAGS+['status','reason']) <= stop.keys(): err('missing stop fields')
    else:
        if any(stop[k] not in {'unchecked','yes','no'} for k in STOP_FLAGS): err('invalid stop flag state')
        if stop['status'] not in {'unchecked','clear','stop'}: err('invalid stop status')
        if stop['status']=='clear' and any(stop[k]!='no' for k in STOP_FLAGS): err('clear stop state requires every flag checked no')
        if any(stop[k]=='yes' for k in STOP_FLAGS) and (stop['status']!='stop' or not stop['reason']): err('positive stop flag requires stop disposition and reason')
    sources = doc.get('source_records',[])
    if not isinstance(sources,list): err('source_records must be an array'); sources=[]
    ids=set()
    for source in sources:
        if not isinstance(source,dict): err('source record must be an object'); continue
        keys={'source_id','url','checked_at','observation','evidence_status','rights_state','permission_state'}
        if not keys <= source.keys() or any(not source.get(k) for k in keys): err('missing source identity/date/observation/rights/permission'); continue
        if source['source_id'] in ids: err('duplicate source ID')
        ids.add(source['source_id'])
        parsed=urlsplit(source['url'])
        if parsed.scheme not in {'http','https'} or not parsed.netloc: err('source locator must be explicit HTTP(S) URL')
        if mode!='synthetic' and parsed.hostname and parsed.hostname.endswith('.invalid'): err('synthetic .invalid source cannot be a real preparation record')
        if mode=='synthetic' and not (parsed.hostname or '').endswith('.invalid'): err('worked synthetic source must use an .invalid domain')
        try: date.fromisoformat(source['checked_at'])
        except (TypeError,ValueError): err('source checked_at must be a valid ISO date')
        if source['permission_state'] not in PERMISSION_STATES: err('invalid source permission_state')
        if mode=='synthetic' and source['evidence_status']!='synthetic': err('synthetic source must stay labelled synthetic')
    if mode=='preparation' and not sources: err('real preparation needs its source set')
    if 'lead_score' in doc: err('keep fit, expressed need and buying interest separate; no blended lead_score')

    claims=[]
    def claim_walk(obj):
        if isinstance(obj,dict):
            if 'claims' in obj:
                if not isinstance(obj['claims'],list): err('claims must be an array')
                else: claims.extend(obj['claims'])
            for key,value in obj.items():
                if key!='claims': claim_walk(value)
        elif isinstance(obj,list):
            for value in obj: claim_walk(value)
    claim_walk(doc)
    for claim in claims:
        if not isinstance(claim,dict) or not {'text','kind','support_state','source_ids'} <= claim.keys(): err('malformed claim'); continue
        if not isinstance(claim['text'],str) or not claim['text'] or claim['kind'] not in KINDS or not isinstance(claim['source_ids'],list): err('malformed claim value'); continue
        if not set(claim['source_ids']) <= ids: err('claim references an unknown source ID')
        kind=claim['kind']; support=claim['support_state']
        if kind=='proposed_service':
            if support!='proposed': err('proposed service cannot be promoted to delivered performance')
        elif kind=='result':
            context=claim.get('measurement_context',{})
            if support!='source_confirmed' or not claim['source_ids'] or not isinstance(context,dict) or not RESULT_CONTEXT <= context.keys() or any(context.get(k) in ('',None,[]) for k in RESULT_CONTEXT): err('unsupported result claim or missing measurement/review context')
        elif kind=='relationship':
            if support!='source_confirmed' or not claim['source_ids'] or perms.get('relationship_context_use')!='permission_verified': err('unconfirmed relationship or missing permission')
        elif kind in {'expressed_need','buying_interest'}:
            if support!='source_confirmed' or not claim['source_ids']: err('need/interest requires explicit source support')
        elif kind=='public_observation':
            if not claim['source_ids'] or support not in ({'synthetic'} if mode=='synthetic' else {'observed','source_confirmed'}): err('unsupported public observation')

    # Narrow lint, deliberately not a claim of exhaustive semantic verification.
    message_texts=[]
    for key in ['message','first_message']:
        m=doc.get(key,{})
        if isinstance(m,dict):
            message_texts += [m[k] for k in ['opening','body','closing_question_or_next_step'] if isinstance(m.get(k),str)]
    for key in ['follow_up_draft','decline_acknowledgment_draft']:
        if isinstance(doc.get(key),str): message_texts.append(doc[key])
    if isinstance(doc.get('follow_up'),dict):
        message_texts += [doc['follow_up'][k] for k in ['draft','decline_acknowledgment_draft'] if isinstance(doc['follow_up'].get(k),str)]
    text='\n'.join(message_texts)
    if re.search(r'\b(?:we|i|outspoken)\s+(?:guarantee|promise)\b[^.!?\n]{0,80}\b(?:reach|leads|sales|revenue|meetings)\b',text,re.I): err('unsupported guaranteed business outcome in message')
    for metric in re.findall(r'\b\d+(?:\.\d+)?\s*(?:%|leads|meetings|sales|customers|clients|hours)\b',text,re.I):
        if not any(isinstance(c,dict) and c.get('kind')=='result' and c.get('support_state')=='source_confirmed' and metric in c.get('text','') for c in claims): err('unmapped quantitative result in message: '+metric)

    schema=doc.get('schema')
    if schema=='outspoken-warm-context/1':
        need={'company_record_id','relationship_owner_role','relationship_state','how_the_parties_actually_know_each_other','context_source_id','connector_role','permission_to_name_connector','intro_draft','review_questions'}
        if not need<=doc.keys(): err('incomplete warm-context structure')
        if doc.get('relationship_state') not in {'not_established','source_confirmed'}: err('invalid relationship_state')
        if doc.get('relationship_state')=='source_confirmed' and (doc.get('context_source_id') not in ids or perms.get('relationship_context_use')!='permission_verified'): err('warm relationship lacks source or permission')
    if schema=='outspoken-first-message/1':
        need={'company_record_id','recipient_role','channel','firmographic_fit_state','expressed_need_state','buying_interest_state','message','claims'}
        if not need<=doc.keys():err('incomplete first-message structure')
        m=doc.get('message',{})
        if not isinstance(m,dict) or not {'subject_optional','opening','body','closing_question_or_next_step'}<=m.keys() or any(not isinstance(v,str) for v in m.values()): err('malformed message fields')
        if mode=='template' and any(m.values()):err('empty template must not contain a real message')
        for key in ['firmographic_fit_state','expressed_need_state','buying_interest_state']:
            if doc.get(key) not in {'not_established','hypothesis','source_confirmed','excluded'}:err('invalid separate fit/need/interest state')
        for key,kind in [('expressed_need_state','expressed_need'),('buying_interest_state','buying_interest')]:
            if doc.get(key)=='source_confirmed' and not any(isinstance(c,dict) and c.get('kind')==kind for c in claims):err('confirmed need/interest lacks its own claim/source row')
    if schema=='outspoken-follow-up/1':
        need={'company_record_id','first_message_record_id','first_message_actually_sent','first_message_source_note_id','prior_reply_state','follow_up_limit','follow_ups_actually_sent','manual_eligibility','follow_up_draft','decline_acknowledgment_draft','stop_action','no_reply_action','claims'}
        if not need<=doc.keys():err('incomplete follow-up structure')
        if type(doc.get('first_message_actually_sent')) is not bool:err('first_message_actually_sent must be a boolean')
        if type(doc.get('follow_up_limit')) is not int or doc.get('follow_up_limit')!=1 or type(doc.get('follow_ups_actually_sent')) is not int or not 0<=doc.get('follow_ups_actually_sent',-1)<=1:err('one-follow-up limit violated')
        eligible=doc.get('manual_eligibility')=='eligible_for_owner_review'
        if eligible and (not doc.get('first_message_actually_sent') or stop.get('status')!='clear' or doc.get('follow_ups_actually_sent')!=0):err('follow-up eligibility conflicts with contact/stop/count state')
    if schema=='outspoken-discovery-mini-audit/1':
        if not {'company_record_id','session_scope','note_or_recording_permission','founder_questions','mini_audit','scope_and_price_decisions','claims'}<=doc.keys():err('incomplete discovery/audit structure')
        questions=doc.get('founder_questions',[])
        if not isinstance(questions,list) or [q.get('id') for q in questions if isinstance(q,dict)]!=[f'D{i:02d}' for i in range(1,9)]:err('discovery question IDs missing/duplicated')
        audit=doc.get('mini_audit',{})
        if not isinstance(audit,dict) or not {'exact_surfaces_reviewed','observations','interpretations','proposed_changes','unreviewed_surfaces','confidence_limit'}<=audit.keys():err('incomplete mini-audit fields')
        else:
            for observation in audit['observations']:
                if not isinstance(observation,dict) or not observation.get('text') or not observation.get('source_ids') or not set(observation['source_ids'])<=ids:err('mini-audit observation lacks a reviewed source')
    if schema=='outspoken-outreach-worked-example/1':
        if mode!='synthetic' or not {'fit_record','warm_context','first_message','follow_up','discovery_example','mini_audit_example','conversation_log_example'}<=doc.keys():err('worked example must be complete and explicitly synthetic')
        if not (doc.get('fit_record',{}).get('company_url','').startswith('https://example.invalid')):err('example company must use example.invalid')
        follow=doc.get('follow_up',{})
        if follow.get('first_message_actually_sent') is not False or follow.get('follow_ups_actually_sent')!=0 or follow.get('manual_eligibility')!='hold_first_message_not_sent':err('synthetic preparation must not imply actual sending')
    return errors


def validate_csv(path, expected_headers):
    errors=[]
    with Path(path).open(newline='',encoding='utf-8') as f:
        reader=csv.DictReader(f)
        if reader.fieldnames!=expected_headers:return [Path(path).name+': exact source/permission/stop headers do not match']
        rows=list(reader)
    ids=[]
    for n,row in enumerate(rows,2):
        prefix=Path(path).name+': row '+str(n)+': '
        if None in row or any(v is None for v in row.values()):errors.append(prefix+'malformed CSV row');continue
        for key in ['record_id','rights_state','permission_state','stop_status','send_authorization']:
            if not row.get(key):errors.append(prefix+'missing '+key)
        if row.get('send_authorization')!='not_authorized':errors.append(prefix+'sending not authorized by this kit')
        if row.get('stop_status') not in {'unchecked','clear','stop'}:errors.append(prefix+'invalid stop_status')
        source_key='source_id' if 'source_id' in row else 'source_note_id'
        if not row.get(source_key):errors.append(prefix+'missing source identity')
        if row.get('stop_status')=='stop' and not row.get('stop_reason'):errors.append(prefix+'stop requires reason')
        if row.get('expressed_need_state')=='source_confirmed' and 'expressed_need_source_id' in row and not row['expressed_need_source_id']:errors.append(prefix+'need source is missing')
        if row.get('buying_interest_state')=='source_confirmed' and 'buying_interest_source_id' in row and not row['buying_interest_source_id']:errors.append(prefix+'interest source is missing')
        if row.get('counts_as_qualifying_conversation')=='yes' and not row.get('qualifying_definition_version'):errors.append(prefix+'qualifying conversation definition is missing')
        if row.get('offer_yes') in {'yes','no'} and not row.get('yes_definition_version'):errors.append(prefix+'offer-yes definition is missing')
        ids.append(row.get('record_id'))
    if len(ids)!=len(set(ids)):errors.append(Path(path).name+': duplicate record IDs')
    return errors


def validate_pack(root):
    root=Path(root);errors=[]
    actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    if actual!=EXPECTED_FILES:errors.append('package file set mismatch: missing='+str(sorted(EXPECTED_FILES-actual))+' extra='+str(sorted(actual-EXPECTED_FILES)))
    for name in JSON_FILES:
        try:
            doc = read_json(root/name)
            schema,mode = JSON_CONTRACTS[name]
            if not isinstance(doc,dict) or doc.get('schema') != schema:
                errors.append(name+': filename/schema mismatch; expected '+schema)
            if not isinstance(doc,dict) or doc.get('record_mode') != mode:
                errors.append(name+': filename/record_mode mismatch; expected '+mode)
            errors.extend(validate_document(doc,name))
        except (OSError,ValueError,TypeError) as e:errors.append(name+': '+str(e))
    for name,headers in [('fit-source-verification.csv',FIT_HEADERS),('conversation-log.csv',CONVERSATION_HEADERS)]:
        try:errors.extend(validate_csv(root/name,headers))
        except (OSError,ValueError,csv.Error) as e:errors.append(name+': '+str(e))
    return {'status':'PASS' if not errors else 'FAIL','expected_files':10,'json_templates_and_examples':5,'csv_templates':2,'errors':errors,'limits':'Preparation structure and narrow unsupported-claim checks only. No truth, permission, law, real prospect, message approval, outcome or send readiness certification.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('root',nargs='?',type=Path,default=Path(__file__).resolve().parent);args=parser.parse_args();result=validate_pack(args.root);print(json.dumps(result,indent=2));return 0 if result['status']=='PASS' else 1

if __name__=='__main__':sys.exit(main())
