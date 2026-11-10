#!/usr/bin/env python3
"""Verify the LinkedIn architecture's deterministic source and coverage contract.

This checks this dated package, not persuasion, author acceptance or runtime
collection. Uses standard Python plus PyYAML for the two reusable templates.
"""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
from urllib.parse import unquote, urlsplit
import csv
import hashlib
import json
import re
import statistics
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / 'docs/linkedin-writing'
OVERLAY = ROOT / 'publications/20261110-writing-architecture'
BASE = '9d54e58e85b5c90a8bc674c73b5e87d68baeb0a5'
EXPECTED = [
    '01-the-reason', '02-what-we-actually-saw', '03-the-interview',
    '04-positioning', '05-proof', '06-product-to-buyer', '07-two-voices',
    '08-visuals', '09-measure', '10-the-delivery',
]
checks = []

def check(name, condition, detail=None):
    checks.append({'check': name, 'status': 'PASS' if condition else 'FAIL', 'detail': detail})

def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key: ' + key)
        result[key] = value
    return result

def read_json(path):
    return json.loads(path.read_text(), object_pairs_hook=unique_pairs)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()

def csv_rows(path):
    with path.open(newline='') as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames
        rows = list(reader)
    check('CSV rectangular: ' + path.name,
          bool(columns) and len(columns) == len(set(columns)) and all(None not in r and all(v is not None for v in r.values()) for r in rows))
    return columns, rows

def main():
    import yaml
    pattern_data = read_json(PACKAGE / 'patterns.json')
    patterns = pattern_data['patterns']
    check('Fourteen unique pattern IDs', [p['id'] for p in patterns] == [f'P{i:02d}' for i in range(1, 15)])
    required = {'id', 'name', 'job', 'use_when', 'hook', 'sequence', 'evidence', 'reasoning', 'conclusion', 'audience', 'humor', 'stop', 'variation'}
    check('Pattern fields and nonempty sequences', all(required <= p.keys() and p['sequence'] and all(p[k] for k in required) for p in patterns))

    overlay = read_json(OVERLAY / 'post-structures.json')
    posts = overlay['posts']
    check('Exact current concept IDs', [p['id'] for p in posts] == EXPECTED)
    check('Known pattern assignments', all(p['pattern_id'] in {x['id'] for x in patterns} for p in posts))
    refs = [r for p in posts for r in p['source_variants']]
    check('Twenty unique source references', len(refs) == 20 and len({(r['path'], r['json_pointer']) for r in refs}) == 20)
    for source in overlay['source_bundles']:
        path = ROOT / source['path']
        rows = read_json(path)
        check('Source bundle hash: ' + source['path'], digest(path) == source['sha256'])
        check('Source bundle IDs: ' + source['path'], [r['id'] for r in rows] == EXPECTED == source['ids'])
    for post in posts:
        for ref in post['source_variants']:
            path = ROOT / ref['path']
            row = read_json(path)[int(ref['json_pointer'][1:])]
            row_hash = hashlib.sha256(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
            check('Source row identity/hash: ' + post['id'] + ':' + path.parent.name,
                  row['id'] == post['id'] == ref['id'] and row_hash == ref['row_sha256'] and digest(path) == ref['file_sha256'])
    check('Shared evidence hashes', all(digest(ROOT / s['path']) == s['sha256'] for s in overlay['shared_evidence']))
    protected = ['publications/20261105-evidence-v1', 'publications/20261105-humanized', 'docs/APPROVED-POSITIONING.json', 'datasets/current', 'reports/20261105']
    check('Original evidence, drafts and positioning unchanged', not git('diff', BASE, '--name-only', '--', *protected))
    approved = read_json(ROOT / 'docs/APPROVED-POSITIONING.json')
    offer = next(p for p in posts if p['id'] == '10-the-delivery')
    check('Approved CTA preserved', offer['conclusion'] == offer['interaction']['text'] == approved['cta'] == 'Book an intro call')
    ending_counts = dict(Counter(p['interaction']['type'] for p in posts))
    check('Recorded ending mix', ending_counts == {'none': 4, 'application': 3, 'diagnostic_question': 1, 'bounded_question': 1, 'offer': 1}, ending_counts)

    report = read_json(ROOT / 'reports/20261105/data.json')
    report_posts = report['queries']['posts']['rows']
    counts = {key: [p[key] for p in report_posts if isinstance(p.get(key), (int, float))] for key in ['reactions', 'comments']}
    check('Recomputed historical statistics', len(report_posts) == 279 and len(report['queries']['authors']['rows']) == 61 and len(counts['reactions']) == 276 and statistics.median(counts['reactions']) == 107.5 and len(counts['comments']) == 256 and statistics.median(counts['comments']) == 36.5)
    times = sorted(p['metric_captured_at'] for p in report_posts)
    check('Displayed report metric dates', {t[:10] for t in times} == {'2026-10-22'}, {'min': times[0], 'max': times[-1]})

    for name in ['brief.yaml', 'review.yaml']:
        template = yaml.safe_load((PACKAGE / 'templates' / name).read_text())
        check('YAML parses: ' + name, isinstance(template, dict) and bool(template.get('schema')))
    _, ledger = csv_rows(PACKAGE / 'templates/claim-ledger.csv')
    check('Claim ledger demonstration is singular', len(ledger) == 1)
    account_columns, accounts = csv_rows(PACKAGE / 'corpus-audit/accounts.csv')
    post_columns, coverage = csv_rows(PACKAGE / 'corpus-audit/posts.csv')
    check('Full corpus row coverage', len(accounts) == 61 and len(coverage) == 279)
    check('Coverage CSV excludes performance value columns', not ({'reactions', 'comments', 'impressions', 'reach', 'clicks', 'sales', 'followers_reported'} & set(account_columns + post_columns)))
    check('Coverage post identities match report', {p['post_id'] for p in coverage} == {p['post_id'] for p in report_posts} and len({p['post_id'] for p in coverage}) == 279)

    registry = read_json(PACKAGE / 'source-registry.json')
    sources = registry['sources']
    ids = [s['id'] for s in sources]
    check('Unique source IDs', len(ids) == len(set(ids)))
    required_sources = {f'L2-O{i:02d}' for i in range(1, 21)} | {f'LWT{i:02d}' for i in range(1, 10)} | {f'L2-B{i:02d}' for i in range(1, 4)}
    check('Official, theory and identified agency sources resolved', required_sources <= set(ids))
    check('External source URLs and local source paths resolve', all(
        bool(s.get('url')) and (
            (s.get('type') == 'L' and (PACKAGE / s['url']).resolve().is_file())
            or (s.get('type') != 'L' and urlsplit(s['url']).scheme in {'https', 'http'})
        ) for s in sources))
    docs = list(PACKAGE.rglob('*.md')) + list(OVERLAY.glob('*.md')) + [ROOT / 'docs/LINKEDIN-WRITING-ARCHITECTURE.md', Path(__file__).with_name('README.md')]
    used_ids = set()
    for path in docs:
        used_ids |= set(re.findall(r'\b(?:LWT\d{2}|L2-[OBC]\d{2})\b', path.read_text()))
    check('Document source IDs resolve', used_ids <= set(ids), {'missing': sorted(used_ids - set(ids))})

    known_files = set(git('ls-tree', '-r', '--name-only', BASE).splitlines())
    known_files.update(p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.parts)
    missing_links = []
    for path in docs:
        for link in re.findall(r'\[[^\]]+\]\(([^)]+)\)', path.read_text()):
            if urlsplit(link).scheme or link.startswith('#'):
                continue
            target = unquote(link.split('#', 1)[0])
            resolved = (path.parent / target).resolve()
            try:
                rel = resolved.relative_to(ROOT).as_posix()
            except ValueError:
                missing_links.append({'file': path.relative_to(ROOT).as_posix(), 'link': link})
                continue
            if rel not in known_files and not any(f.startswith(rel.rstrip('/') + '/') for f in known_files):
                missing_links.append({'file': path.relative_to(ROOT).as_posix(), 'link': link})
    check('Local Markdown links resolve in checkout or full Git tree', not missing_links, missing_links)

    allowed_prefixes = ('docs/linkedin-writing/', 'publications/20261110-writing-architecture/', 'reports/20261110-writing-methodology/')
    allowed_exact = {'AGENTS.md', 'CURRENT-STATE.md', 'README.md', 'docs/CATEGORY-GUIDE.md', 'docs/SERVICES-AND-WRITING.md', 'docs/LINKEDIN-WRITING-ARCHITECTURE.md'}
    paths = set(filter(None, git('diff', BASE, '--name-only').splitlines())) | set(filter(None, git('ls-files', '--others', '--exclude-standard').splitlines()))
    check('Change scope is writing methodology only', all(p in allowed_exact or p.startswith(allowed_prefixes) for p in paths), sorted(paths))
    check('No installed skill or binary added', all(not p.endswith('/SKILL.md') and Path(p).suffix in {'.md', '.json', '.csv', '.yaml', '.py'} for p in paths))
    payload_files = sorted(p for p in paths if not p.startswith('reports/20261110-writing-methodology/'))
    result = {'schema': 'linkedin-writing-verification/2', 'checked_at': datetime.now(timezone.utc).isoformat(), 'base_commit': BASE,
              'status': 'PASS' if all(c['status'] == 'PASS' for c in checks) else 'FAIL',
              'check_count': len(checks), 'checks': checks,
              'payload_files': [{'path': p, 'sha256': digest(ROOT / p)} for p in payload_files],
              'limits': ['Deterministic checks do not establish writing performance or founder approval.',
                         'Public safety scan is run separately on the materialized sparse checkout; unchanged omitted assets are not re-audited.',
                         'Independent editorial review and source access limitations are recorded in README and the research record.']}
    Path(__file__).with_name('verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'checks': len(checks), 'failures': [c for c in checks if c['status'] == 'FAIL']}, ensure_ascii=False, indent=2))
    return 0 if result['status'] == 'PASS' else 1

if __name__ == '__main__':
    sys.exit(main())
