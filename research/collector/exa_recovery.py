"""Manually reconcile only a verified Exa result-text false positive."""
import argparse
from datetime import datetime
import json
import re
from .cli import load_config
from .contracts import ConfigurationError
from .discovery import _tool_reported_access_error
from .store import Store


def reconcile(store):
    hold=store.get_suspension('exa-search') or {}
    if hold.get('reason')!='discovery_tool_quota_or_error':raise ConfigurationError('exa_hold_not_eligible')
    row=store.db.execute('SELECT payload FROM discoveries ORDER BY rowid DESC LIMIT 1').fetchone()
    if not row:raise ConfigurationError('exa_evidence_missing')
    try:
        observation=json.loads(row[0]); raw=json.loads(store.raw_bytes(observation['raw_sha256']))
        taken=datetime.fromisoformat(observation['collected_at'].replace('Z','+00:00'))
        stopped=datetime.fromisoformat(hold['suspended_at'].replace('Z','+00:00'))
        text='\n'.join(x.get('text','') for x in raw.get('content',[]) if x.get('type')=='text')
        if observation.get('source_id')!='exa-search' or not 0<=(stopped-taken).total_seconds()<60:
            raise ValueError('unmatched_hold')
        old_match=re.search(r'quota|rate.limit|unauthori[sz]ed|too many requests',text,re.I)
        first=re.search(r'(?im)^(?:title|url):\s*',text)
        if (not old_match or not first or old_match.start()<first.start() or
                _tool_reported_access_error(raw,text)):
            raise ValueError('source_error_not_disproved')
    except (KeyError,ValueError,TypeError,AttributeError) as exc:
        raise ConfigurationError('exa_false_positive_not_proven') from None
    store.resume('exa-search','Manual, source-backed reconciliation: indexed result wording caused an Exa error-detector false positive; LinkedIn hold unchanged.')
    return {'status':'exa_false_positive_reconciled','linkedin_hold_unchanged':True}


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',required=True);args=p.parse_args()
    cfg=load_config(args.config);store=Store(cfg['state_dir'])
    try:
        with store.lock():print(json.dumps(reconcile(store)))
    finally:store.close()


if __name__=='__main__':main()
