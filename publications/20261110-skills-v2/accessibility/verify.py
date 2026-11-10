#!/usr/bin/env python3
"""Check the complete publication text-alternative handoff; no network."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
IDS = ['01-the-reason', '02-what-we-actually-saw', '03-the-interview', '04-positioning', '05-proof', '06-product-to-buyer', '07-two-voices', '08-visuals', '09-measure', '10-the-delivery']

class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(); self.tags = []; self.text = []; self.feed(text)
    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))
    def handle_data(self, data):
        self.text.append(data)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    package = ROOT / 'accessibility'
    data = json.loads((package / 'alt-text.json').read_text())
    content = json.loads((ROOT / 'content.json').read_text())
    checks = []
    def check(name, ok):
        checks.append({'check': name, 'status': 'PASS' if ok else 'FAIL'})
    expected = [(item_id, direction, page) for i, item_id in enumerate(IDS) for direction in ['graphic', 'people'] for page in range(1, 6 if i < 5 else 2)]
    rows = data['records']; actual = [(x['post_id'], x['direction'], x['page']) for x in rows]
    check('Exact sixty expected identities, order and no duplicates', actual == expected and len(set(actual)) == 60)
    check('Current canonical content identity', [x['id'] for x in content] == IDS and data['source_content_sha256'] == sha(ROOT / 'content.json'))
    images = {x.relative_to(ROOT).as_posix() for x in (ROOT / 'assets').rglob('*.png')}
    check('Every and only current PNG has a description', {x['asset'] for x in rows} == images and len(images) == 60)
    check('All sixty exact source and image hashes', all(sha(ROOT / x['asset']) == x['asset_sha256'] and sha(ROOT / x['source_svg']) == x['source_svg_sha256'] for x in rows))
    check('Descriptions are concise, meaningful and distinct', all(40 <= len(x['alt_text']) <= 800 and not x['alt_text'].startswith('Image of') for x in rows) and len({x['alt_text'] for x in rows}) == 60)
    panel_checks, diagrams, disclosures = [], [], []
    for row in rows:
        item = content[IDS.index(row['post_id'])]; panel = item['variants'][row['direction']][row['page'] - 1]
        panel_checks.append(all(panel[k] in row['alt_text'] for k in ['headline', 'body', 'context']) and (not panel.get('cta') or panel['cta'] in row['alt_text']))
        description = row['diagram_description']
        if panel['diagram_type'] == 'mapping':
            pairs = [re.split(r'\s*→\s*', x) for x in panel['diagram']]
            diagrams.append('independent mappings' in description and 'rows are not connected' in description and all(a + ' maps to ' + b in description for a, b in pairs))
        else:
            diagrams.append(all(label in description for label in panel['diagram']) and ('Equal-weight' in description if panel['diagram_type'] in ['comparison', 'checklist'] else True))
        if row['direction'] == 'people':
            disclosures.append('Illustrative scene; people are fictional.' in row['alt_text'])
    check('All sixty important panel messages and exact literals preserved', all(panel_checks))
    check('Diagram meaning preserves parallel versus sequential relationships', all(diagrams))
    check('Thirty actual people descriptions disclose fiction', len(disclosures) == 30 and all(disclosures))
    check('Every proof image preserves hypothetical/no-test context', all('Hypothetical' in x['alt_text'] and 'no product test reported' in x['alt_text'] for x in rows if x['post_id'] == '05-proof'))
    gallery = Page((ROOT / 'assets/index.html').read_text()); descriptions = {a['src']: a.get('alt') for tag, a in gallery.tags if tag == 'img'}
    check('Gallery uses every exact description', len(descriptions) == 60 and all(descriptions.get(x['asset'].removeprefix('assets/')) == x['alt_text'] for x in rows))
    links = {a.get('href') for tag, a in gallery.tags if tag == 'a'}
    check('Ten direct concept transcript links', all('../accessibility/transcripts.html#' + item_id in links for item_id in IDS))
    transcript = Page((package / 'transcripts.html').read_text()); anchors = [a.get('id') for tag, a in transcript.tags if tag == 'article']; sections = [a.get('id') for tag, a in transcript.tags if tag == 'section']
    text = '\n'.join(transcript.text); markdown = (package / 'transcripts.md').read_text()
    check('All ten concepts and sixty unique transcript anchors', sections == IDS and anchors == [x['transcript_anchor'] for x in rows] and len(set(anchors)) == 60)
    check('All captions, panel fields and diagram equivalents in text copies', all(item['caption'] in markdown for item in content) and all(x['diagram_description'] in text and x['diagram_description'] in markdown for x in rows) and all(panel[field] in text and panel[field] in markdown for item in content for panels in item['variants'].values() for panel in panels for field in ['headline', 'body', 'context']))
    check('Both offer descriptions retain the exact CTA', all(x['alt_text'].endswith('Book an intro call') for x in rows if x['post_id'] == '10-the-delivery'))
    result = {'schema': 'outspoken-text-alternative-verification/1', 'status': 'PASS' if all(x['status'] == 'PASS' for x in checks) else 'FAIL', 'checks': checks, 'check_count': len(checks), 'alt_text_records': len(rows), 'concept_transcripts': len(content), 'limits': ['Structural/source equivalence only; no screen-reader, native LinkedIn, tagged-PDF or WCAG conformance assertion.']}
    (package / 'verification.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'status': result['status'], 'checks': len(checks), 'failures': [x for x in checks if x['status'] == 'FAIL']}))
    return 0 if result['status'] == 'PASS' else 1

if __name__ == '__main__':
    raise SystemExit(main())
