#!/usr/bin/env python3
"""Build source-bound text alternatives. No account access or publication."""
from pathlib import Path
import hashlib
import html
import json
import re

ROOT = Path(__file__).resolve().parent
IDS = ['01-the-reason', '02-what-we-actually-saw', '03-the-interview', '04-positioning', '05-proof', '06-product-to-buyer', '07-two-voices', '08-visuals', '09-measure', '10-the-delivery']

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def diagram_description(panel):
    labels = panel['diagram']
    kind = panel.get('diagram_type', 'comparison')
    if kind == 'sequence':
        return 'Sequence, connected left to right: ' + ' then '.join(labels) + '.'
    if kind == 'mapping':
        assert len(labels) == 2
        pairs = [re.split(r'\s*(?:→|->)\s*', value) for value in labels]
        assert all(len(pair) == 2 for pair in pairs)
        return 'Two independent mappings: ' + '; '.join(a + ' maps to ' + b for a, b in pairs) + '. The rows are not connected.'
    if kind == 'checklist':
        return 'Equal-weight checks, read across each row: ' + '; '.join(labels) + '.'
    if kind == 'unknown':
        return 'Parallel boxes: ' + '; '.join(labels) + '. The last box has a dashed outline.'
    assert kind == 'comparison'
    return 'Equal-weight comparison boxes: ' + '; '.join(labels) + '.'

def main():
    content = json.loads((ROOT / 'content.json').read_text())
    assert [x['id'] for x in content] == IDS
    output = ROOT / 'accessibility'
    output.mkdir(exist_ok=True)
    records, sections, markdown = [], [], ['# Outspoken publication text transcripts', '', 'Drafts for founder review. These text alternatives do not establish tagged-PDF compliance or native LinkedIn accessibility.', '']
    for item in content:
        assert item['variants']['graphic'] == item['variants']['people']
        text = [f"## {item['id']} — {item['title']}", '', '### Caption', '', item['caption'], '']
        rendered = [f'<section id="{item["id"]}"><h2>{html.escape(item["title"])}</h2><p>{html.escape(item["id"])}</p><h3>Caption</h3><p class="caption">{html.escape(item["caption"])}</p>']
        for variant in ['graphic', 'people']:
            title = 'Graphic direction' if variant == 'graphic' else 'Illustrative people direction'
            text += [f'### {title}', '']
            rendered += [f'<h3>{title}</h3>']
            for index, panel in enumerate(item['variants'][variant], 1):
                count = len(item['variants'][variant])
                image = f'assets/{item["id"]}/{variant}-{index:02d}.png'
                svg = f'assets/source-svg/{item["id"][:2]}-{variant}-{index:02d}.svg'
                key = f'{item["id"]}-{variant}-{index:02d}'
                diagram = diagram_description(panel)
                # All important panel text is present; decorative artwork is not invented.
                scene = 'Illustrative scene; people are fictional. ' if variant == 'people' else ''
                alt = (f'{scene}Page {index} of {count}. {panel["headline"]} {panel["body"]} {diagram} {panel["context"]}' + ('. ' + panel['cta'] if panel.get('cta') else ''))
                assert 40 <= len(alt) <= 800
                record = {'post_id': item['id'], 'direction': variant, 'page': index, 'pages': count, 'asset': image, 'asset_sha256': sha(ROOT / image), 'source_svg': svg, 'source_svg_sha256': sha(ROOT / svg), 'alt_text': alt, 'diagram_description': diagram, 'transcript_anchor': key, 'rights_state': 'owned_editorial_text'}
                records.append(record)
                visible = [f'Page {index} of {count}', f'FOUNDER NOTES / {item["id"][:2]} · {index:02d}', panel['headline'], panel['body'], diagram, panel['context']]
                if variant == 'graphic':
                    visible += [('THE IDEA' if index == 1 else 'FIELD NOTE') + f' — {item["id"][:2]}.{index:02d}']
                if variant == 'people':
                    visible += ['ILLUSTRATIVE SCENE — people are fictional, not customers or founders.']
                if panel.get('cta'):
                    visible += [panel['cta']]
                visible += ['OUTSPOKEN / DRAFT FOR FOUNDER REVIEW']
                text += [f'#### Page {index} of {count}', '', *[x + '\n' for x in visible[1:]], '']
                rendered += [f'<article id="{key}"><h4>Page {index} of {count}</h4>' + ''.join('<p>' + html.escape(x) + '</p>' for x in visible[1:]) + '</article>']
        rendered += ['</section>']
        sections.append(''.join(rendered))
        markdown += text
    assert len(records) == len({x['asset'] for x in records}) == 60
    result = {'schema': 'outspoken-text-alternatives/1', 'date': '2026-11-10', 'source_content_sha256': sha(ROOT / 'content.json'), 'status': 'source_bound_preparation', 'records': records, 'limits': ['No tagged-PDF, screen-reader or native LinkedIn conformance claim.', 'Alt text is meaningful reader information, not a reach or ranking tactic.', 'If source copy or artwork changes, regenerate and review this handoff.']}
    (output / 'alt-text.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    (output / 'transcripts.md').write_text('\n'.join(markdown))
    toc = '<nav aria-label="Publication transcripts"><ul>' + ''.join(f'<li><a href="#{x["id"]}">{html.escape(x["title"])}</a></li>' for x in content) + '</ul></nav>'
    (output / 'transcripts.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Outspoken publication text transcripts</title><style>body{max-width:900px;margin:auto;padding:24px;color:#162760;background:#fff;font:18px/1.6 system-ui,sans-serif}.caption{white-space:pre-wrap}article{border-left:3px solid #d6dde7;padding-left:18px}section{margin:40px 0}a{color:#162760}a:focus-visible{outline:3px solid #162760;outline-offset:3px}</style><main><h1>Publication text transcripts</h1><p>Ten drafts for founder review. Graphic and illustrative people directions contain the same argument. Native LinkedIn and screen-reader testing remain separate.</p>' + toc + ''.join(sections) + '</main></html>')
    print(json.dumps({'status': 'PASS', 'alt_text_records': len(records), 'concept_transcripts': len(content), 'maximum_alt_characters': max(len(x['alt_text']) for x in records)}))

if __name__ == '__main__':
    main()
