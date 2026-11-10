#!/usr/bin/env python3
"""Focused deterministic checks for the writing-methodology follow-up.

Standard library only. An isolated projection can use --source-root for exact
unchanged inputs and --known-paths for a saved full repository file inventory.
Those options never collect sources or change publication authority.
"""
from pathlib import Path, PurePosixPath
from collections import Counter
from urllib.parse import unquote, urlsplit
import argparse
import hashlib
import json
import posixpath
import re
import statistics
import subprocess
import sys

PACKAGE = 'docs/linkedin-writing/'
REPORT = 'reports/20261110-writing-methodology-followup/'
EXPECTED_COMPANIES = ['Notus', 'Inkiro', 'Hat Tip', 'Windmill Growth', 'Stop The Scroll', 'Kurogo', 'storyarb', 'Understory', 'Rallyup', 'Concurate', 'Linkedist', 'Compound Content Studio', 'Shake Content', 'Contender Creative', 'Hivemind Marketing']
EXPECTED_POSTS = ['01-the-reason', '02-what-we-actually-saw', '03-the-interview', '04-positioning', '05-proof', '06-product-to-buyer', '07-two-voices', '08-visuals', '09-measure', '10-the-delivery']
SOURCE_FILES = ['README.md', 'parts/01_foundations.md', 'parts/02_genres.md', 'parts/03_narrative_workflows.md', 'parts/04_agents.md', 'parts/14_linkedin.md', 'templates/editorial_brief.yaml', 'templates/paragraph_map.csv', 'templates/claims_template.csv', 'templates/review_rubric.csv', 'templates/genre_router.md', 'templates/evaluation_cases.md', 'templates/agent_brief.md']
CHANGED_FILES = [
    'README.md', 'CURRENT-STATE.md', 'docs/LINKEDIN-WRITING-ARCHITECTURE.md',
    PACKAGE+'AGENT-ROUTING.md', PACKAGE+'RESEARCH-AND-REVIEW.md', PACKAGE+'source-registry.json',
    PACKAGE+'COMPETITOR-WRITING-AUDIT.md', PACKAGE+'competitor-writing-audit.json',
    PACKAGE+'METHOD-INTEGRATION.md', PACKAGE+'supplied-source-manifest.json',
    PACKAGE+'SKILL-SPECIFICATIONS.md', PACKAGE+'skill-evaluation-cases.json',
    'publications/20261110-writing-architecture/STRUCTURE-REVIEW.md',
    REPORT+'README.md', REPORT+'verify.py',
]
RESULT_FILES = [REPORT+'verification.json', REPORT+'public-safety.json']


def pairs(rows):
    out = {}
    for key, value in rows:
        if key in out:
            raise ValueError('Duplicate JSON key: '+key)
        out[key] = value
    return out


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--source-root', type=Path)
    parser.add_argument('--known-paths', type=Path)
    parser.add_argument('--projection', action='store_true')
    args = parser.parse_args()
    root = args.root.resolve()
    source_root = (args.source_root or root).resolve()
    checks = []

    def check(name, condition, detail=None):
        checks.append({'check': name, 'status': 'PASS' if condition else 'FAIL', 'detail': detail})

    def locate(name):
        p = root/name
        return p if p.is_file() else source_root/name

    def read(name):
        return json.loads(locate(name).read_text(), object_pairs_hook=pairs)

    check('All fifteen expected payload files exist', all((root/p).is_file() for p in CHANGED_FILES))
    if args.projection:
        actual = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
        check('Exact isolated projection scope', set(CHANGED_FILES) <= actual <= set(CHANGED_FILES+RESULT_FILES), sorted(actual-set(CHANGED_FILES+RESULT_FILES)))
    for name in CHANGED_FILES:
        p = root/name
        if p.suffix == '.json':
            read(name)
    check('Every changed JSON parsed with duplicate-key detection', True)

    cohort = read(PACKAGE+'competitor-writing-audit.json')
    rows = cohort['rows']
    actual = [r['company'] for r in rows if r['cohort'] == 'original_workbook_15']
    check('Original fifteen identities match authoritative expected cohort', actual == EXPECTED_COMPANIES == cohort['expected_original_companies'])
    additions = [r['company'] for r in rows if r['cohort'] != 'original_workbook_15']
    check('Exactly Cleverly and Belkins are plan additions', additions == ['Cleverly', 'Belkins'] == cohort['plan_only_additions'] and len(rows) == 17)
    check('Seventeen unique company IDs, names and official domains', len({r['id'] for r in rows}) == len({r['company'] for r in rows}) == len({urlsplit(r['official_website']).netloc.lower() for r in rows}) == 17)
    required = {'company','cohort','official_website','accessed_on','current_sources','evidence_level','reusable_editorial_lesson','do_not_infer','open_gaps','social_locator_status','actual_social_posts_newly_read'}
    check('Every company has complete evidence and limitation fields', all(required <= r.keys() and all(r[k] for k in required-{'actual_social_posts_newly_read'}) for r in rows))
    check('All new social-post review counts remain zero', all(r['actual_social_posts_newly_read'] == 0 for r in rows))
    check('Company sources are explicit HTTPS with current review dates', all(r['accessed_on']=='2026-11-10' and all(urlsplit(s['url']).scheme=='https' and s['accessed_on']=='2026-11-10' and s['access_scope'] for s in r['current_sources']) for r in rows))
    check('SalesBread stays supplemental', cohort['supplemental_baseline_company']['company']=='SalesBread' and 'SalesBread' not in actual+additions)
    w = cohort['workbook_identity']
    check('Workbook identity and complete table counts', w['sha256']=='906da6a25a0b57e6aa1d2f544178700040bb5922f854a9cd9665875a8634e5a8' and w['sheet_count']==21 and w['company_sheet_count']==15 and w['comparison_rows']==15 and w['materials_rows']==54 and w['pricing_rows']==47 and w['social_locator_rows']==42 and w['source_rows']==192)
    check('Eighteen source pages across seventeen companies', sum(len(r['current_sources']) for r in rows)==18)

    manifest = read(PACKAGE+'supplied-source-manifest.json')
    check('All thirteen expected supplied-file identities present', [r['relative_file'] for r in manifest]==SOURCE_FILES and [r['source_id'] for r in manifest]==[f'WM-{i:02d}' for i in range(1,14)])
    check('Supplied identities retain hashes, bytes and research-only use', all(re.fullmatch('[a-f0-9]{64}',r['sha256']) and isinstance(r['bytes'],int) and r['bytes']>0 and r['rights_state']=='user_supplied_research_only_no_redistribution_assumed' for r in manifest))

    registry = read(PACKAGE+'source-registry.json')
    ids = [s['id'] for s in registry['sources']]
    check('Forty-six unique sources with both new annex identities', len(ids)==len(set(ids))==registry['source_counts']['total']==46 and {'L3-R01','L3-R02'} <= set(ids))
    check('Source categories reconcile', sum(v for k,v in registry['source_counts'].items() if k!='total')==46)
    cov = registry['coverage_limits']
    check('Coverage correction keeps identity and social-read states separate', cov['remaining_competitors_unresolved']==0 and cov['original_competitor_identities_recovered']==15 and cov['plan_only_company_additions']==2 and cov['current_competitor_social_posts_reviewed']==0 and cov['official_pages_in_followup']==18 and cov['artifact_26_agency_cohort_fully_available'] is False)

    cases = read(PACKAGE+'skill-evaluation-cases.json')
    check('Exact ten nonempty synthetic fixtures', [r['id'] for r in cases['cases']]==[f'E{i:02d}' for i in range(1,11)] and all(all(r.get(k) for k in ['capability','input','expected_behavior','critical_failure','evidence_needed']) for r in cases['cases']))
    check('Prepared cases do not assert skill-runtime execution', cases['status']=='designed_not_executed_as_skill_runtime' and cases['evaluation_record']['runtime_runs']==0 and cases['evaluation_record']['independent_behavioral_pass_claimed'] is False)

    patterns = read(PACKAGE+'patterns.json')['patterns']
    check('Fourteen preserved publication pattern IDs', [p['id'] for p in patterns]==[f'P{i:02d}' for i in range(1,15)])
    overlay = read('publications/20261110-writing-architecture/post-structures.json')
    posts = overlay['posts']
    check('Exact ten current structure IDs', [p['id'] for p in posts]==EXPECTED_POSTS)
    required_post = {'reader_job','dominant_question','thesis','hooks','hook_payoff','paragraphs','claim_plan','reasoning','conclusion','interaction','founder_inputs','source_variants','status'}
    check('Every structure retains its full reader/evidence/reasoning contract', all(required_post <= p.keys() and all(p[k] for k in required_post) and p['pattern_id'] in {x['id'] for x in patterns} for p in posts))
    refs = [r for p in posts for r in p['source_variants']]
    check('Twenty unique source-variant references', len(refs)==len({(r['path'],r['json_pointer']) for r in refs})==20)
    for bundle in overlay['source_bundles']:
        check('Exact unchanged bundle bytes: '+bundle['path'], sha(locate(bundle['path']))==bundle['sha256'] and [p['id'] for p in read(bundle['path'])]==EXPECTED_POSTS)
    for post in posts:
        for ref in post['source_variants']:
            row = read(ref['path'])[int(ref['json_pointer'][1:])]
            h = hashlib.sha256(json.dumps(row,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
            check('Exact source row: '+post['id']+':'+PurePosixPath(ref['path']).parent.name, row['id']==post['id']==ref['id'] and h==ref['row_sha256'] and sha(locate(ref['path']))==ref['file_sha256'])
    check('All shared evidence bytes match migration ledger', all(sha(locate(s['path']))==s['sha256'] for s in overlay['shared_evidence']))
    approved = read('docs/APPROVED-POSITIONING.json')
    offer = posts[-1]
    check('Exact approved offer CTA preserved', approved['cta']==offer['conclusion']==offer['interaction']['text']=='Book an intro call')
    check('Distinct reader questions in the ten supplied structures', len({p['dominant_question'] for p in posts})==10)
    check('Ending mix remains job-dependent', dict(Counter(p['interaction']['type'] for p in posts))=={'none':4,'application':3,'diagnostic_question':1,'bounded_question':1,'offer':1})
    report = read('reports/20261105/data.json')
    rp = report['queries']['posts']['rows']
    reactions = [p['reactions'] for p in rp if isinstance(p.get('reactions'),(int,float))]
    comments = [p['comments'] for p in rp if isinstance(p.get('comments'),(int,float))]
    check('Historical sample and observation denominators recompute', len(rp)==279 and len(report['queries']['authors']['rows'])==61 and len(reactions)==276 and statistics.median(reactions)==107.5 and len(comments)==256 and statistics.median(comments)==36.5 and {p['metric_captured_at'][:10] for p in rp}=={'2026-10-22'})

    known = set(CHANGED_FILES+RESULT_FILES)
    if args.known_paths:
        known.update(x['path'] if isinstance(x,dict) else x for x in json.loads(args.known_paths.read_text(),object_pairs_hook=pairs))
    else:
        try:
            known.update(subprocess.check_output(['git','ls-files'],cwd=root,text=True).splitlines())
        except (OSError,subprocess.CalledProcessError):
            known.update(p.relative_to(source_root).as_posix() for p in source_root.rglob('*') if p.is_file() and '.git' not in p.parts)
    missing = []
    used_ids = set()
    for name in CHANGED_FILES:
        if not name.endswith('.md'):
            continue
        text = (root/name).read_text()
        used_ids.update(re.findall(r'\b(?:LWT\d{2}|L[23]-[OBCR]\d{2})\b',text))
        for link in re.findall(r'\[[^\]]+\]\(([^)]+)\)',text):
            if urlsplit(link).scheme or link.startswith('#'):
                continue
            target = posixpath.normpath(posixpath.join(posixpath.dirname(name),unquote(link.split('#')[0])))
            if target.startswith('../') or (target not in known and not any(k.startswith(target.rstrip('/')+'/') for k in known)):
                missing.append({'file':name,'link':link})
    check('Every changed Markdown local link resolves in full repository inventory', not missing, missing)
    check('Every literal source ID in changed guides resolves', used_ids <= set(ids), sorted(used_ids-set(ids)))
    check('No activated skill, binary, runtime or private source path is in change scope', all(not p.endswith('SKILL.md') and PurePosixPath(p).suffix in {'.md','.json','.py'} for p in CHANGED_FILES))

    result = {'schema':'linkedin-writing-followup-verification/1','base_commit':'23b8a1ab076fccdaebd4c0394b9afd015707528e','status':'PASS' if all(c['status']=='PASS' for c in checks) else 'FAIL','check_count':len(checks),'checks':checks,'payload_files':[{'path':p,'sha256':sha(root/p)} for p in CHANGED_FILES], 'limits':['Structural/provenance checks are not source truth, editorial quality, skill-runtime evaluation or founder approval.','This projection excludes unchanged repository assets and raw source material.','Social locators are historical; no current competitor social posts are certified.']}
    output = root/REPORT/'verification.json'
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'checks':len(checks),'failures':[c for c in checks if c['status']=='FAIL']},indent=2))
    return 0 if result['status']=='PASS' else 1


if __name__=='__main__':
    sys.exit(main())
