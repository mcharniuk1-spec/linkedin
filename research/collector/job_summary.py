"""Only aggregate operational information is written to the Actions summary."""
import json
import os
from pathlib import Path


def summary(path):
    try:
        data=json.loads(Path(path).read_text())
    except (OSError,ValueError):
        return '### Collection status\n\nNo completed collection report; inspect failed steps.\n'
    daily=data.get('daily_progress',{})
    lines=['### Collection status', '',
        '- LinkedIn: '+('blocked by persistent access hold' if data.get('linkedin_status')=='blocked_by_persistent_access_hold' or any(x.get('source_id')=='linkedin-public' and x.get('error_code')=='source_access_hold' for x in data.get('errors',[])) else 'see collection result'),
        '- Newly collected LinkedIn posts today: '+str(daily.get('new_unique_posts','unknown'))+' / 100 target',
        '- Distinct observed accounts today: '+str(daily.get('distinct_observed_accounts','unknown'))+' / 10 target',
        '- Duplicate records in this run: '+str(data.get('duplicates','unknown')),
        '- Missed or delayed scheduled runs: unknown; check Actions history.',
        '- Quota usage: unknown unless reported by the provider.',
        '', 'Independent topic sources (not LinkedIn engagement):']
    for source in data.get('external_discovery',{}).get('source_results',[]):
        if source.get('source_id') not in {'hacker-news-top','huggingface-blog-rss'}:continue
        lines.append('- '+source['source_id']+': '+source.get('status','unknown')+', '+str(source.get('successful_requests','unknown'))+'/'+str(source.get('requests','unknown'))+' requests succeeded; '+str(source.get('new_items','unknown'))+' new topic leads.')
    lines.append('- Exa candidate links added: '+str(data.get('discovery_candidates_new','unknown'))+'.')
    lines.append('\nThis summary does not contain source content, credentials or private analytics.\n')
    return '\n'.join(lines)


if __name__=='__main__':
    text=summary('research/work/collector/last-run.json')
    path=os.environ.get('GITHUB_STEP_SUMMARY')
    if path:
        with open(path,'a',encoding='utf-8') as f:f.write(text)
    else:print(text)
