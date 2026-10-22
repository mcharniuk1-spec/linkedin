"""Offline tests for release.py and viewer-template.html, run against tests/fixtures/release.

    python3 -m unittest discover tests -p 'test_release.py'

The fixture tree holds three sibling run folders: v2 (oldest media), v3 (base cycle with
data/dataset.json) and v4 (the run being released). Each test copies it to a temp dir, so the
real run folder is never written. Viewer tests execute the page script under node with a tiny
DOM stub and are skipped when node is not installed.
"""
import contextlib
import copy
import hashlib
import io
import json
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

RUN = Path(__file__).resolve().parents[1]
FIX = Path(__file__).resolve().parent / 'fixtures' / 'release'
sys.path.insert(0, str(RUN))
import release  # noqa: E402

TEMPLATE = RUN / 'viewer-template.html'
NODE = shutil.which('node')
ENTITY_KEYS = [e[0] for e in release.ENTITIES]
HARNESS = r"""
const fs=require('fs');
const html=fs.readFileSync(process.argv[2],'utf8');
const ds=html.match(/<script id="dataset" type="application\/json">([\s\S]*?)<\/script>/)[1];
const code=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1])[0];
class El{constructor(id){this.id=id;this.innerHTML='';this.textContent='';this.value='';this.hidden=false;this.attrs={};this.ls={}}
 addEventListener(t,f){(this.ls[t]=this.ls[t]||[]).push(f)} setAttribute(k,v){this.attrs[k]=v} fire(t){(this.ls[t]||[]).forEach(f=>f())}}
const els={};global.document={getElementById:id=>els[id]||(els[id]=new El(id))};
els.dataset=new El('dataset');els.dataset.textContent=ds;
new Function(code)();
const g=id=>document.getElementById(id);
const out={default_value:g('collection').value,default_count:g('post-count').textContent,totals:g('totals').textContent,notice:g('notice').innerHTML,
 links:g('links').innerHTML,cohort_note:g('cohort-note').innerHTML,cohort:g('cohort-table').innerHTML,held_hidden:g('held-section').hidden,
 held:g('held-table').innerHTML,collection_options:g('collection').innerHTML};
const set=(id,v)=>{els[id].value=v;els[id].fire(id==='post-search'?'input':'change')};
set('collection','all');out.all=els['post-list'].innerHTML;out.all_count=els['post-count'].textContent;
const count=(f,v)=>{set(f,v);const n=(els['post-list'].innerHTML.match(/<article /g)||[]).length;set(f,'');return n};
out.filter_counts={velocity_eligible:count('velocity-filter','eligible'),velocity_ineligible:count('velocity-filter','ineligible'),velocity_none:count('velocity-filter','none'),
 held:count('attention-filter','held'),gaps:count('attention-filter','gaps'),qaflag:count('attention-filter','qaflag'),reobserved:count('attention-filter','reobserved'),
 video:count('media-filter','video'),image:count('media-filter','image'),doc:count('media-filter','document_preview')};
set('collection','new');out.new=els['post-list'].innerHTML;set('collection','v3');out.v3_count=(els['post-list'].innerHTML.match(/<article /g)||[]).length;
els['target-tab'].onclick();out.company=els['company-list'].innerHTML;out.target_note=els['target-note'].textContent;out.target_hidden=els['target-pane'].hidden;out.ref_hidden=els['reference-pane'].hidden;
console.log(JSON.stringify(out));
"""


def jread(p):
    return json.loads(Path(p).read_text())


def jwrite(p, x):
    Path(p).write_text(json.dumps(x, indent=2))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='release-test-'))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        for d in ('v2', 'v3', 'v4'):
            shutil.copytree(FIX / d, self.tmp / d)
        self.root, self.base = self.tmp / 'v4', self.tmp / 'v3'

    def run_release(self, **kw):
        rel = release.Release(self.root, self.base, TEMPLATE, **kw)
        with contextlib.redirect_stdout(io.StringIO()):
            code = rel.run()
        self.rel = rel
        return code

    def failed(self):
        return [c['name'] for c in self.rel.checks if c['status'] == 'fail']

    def checks(self):
        return {c['name']: c for c in self.rel.checks}

    def dataset(self):
        return jread(self.root / 'data/dataset.json')

    def edit(self, rel, fn):
        p = self.root / rel
        d = jread(p)
        out = fn(d)
        jwrite(p, d if out is None else out)

    def assert_fails(self, name):
        code = self.run_release()
        self.assertEqual(code, 1, self.failed())
        self.assertIn(name, self.failed())
        return self.rel

    def pid(self, n):
        return 'urn:li:activity:%d' % (7100000000000000000 + n)


class TestSuccessorCycle(Base):
    def test_successor_preserves_entity_cycle_provenance(self):
        self.assertEqual(self.run_release(), 0, self.failed())
        before = self.dataset()
        nxt = self.tmp / 'v5'
        (nxt / 'pipeline').mkdir(parents=True)
        jwrite(nxt / 'pipeline/config.json', {'qualification': {}})
        with contextlib.redirect_stdout(io.StringIO()):
            rel = release.Release(nxt, self.root, TEMPLATE)
            code = rel.run()
        self.assertEqual(code, 0, [c for c in rel.checks if c['status'] == 'fail'])
        after = jread(nxt / 'data/dataset.json')
        for key, identity in [('posts','id'), ('assets','asset_id'), ('visual_reviews','asset_id'), ('video_reviews','asset_id'), ('transcripts','asset_id'), ('transcript_qa','asset_id'), ('snapshots','snapshot_id'), ('velocity','post_id')]:
            if key in ['snapshots','velocity','transcript_qa']:
                self.assertEqual({x[identity] for x in before[key]}, {x[identity] for x in after[key]}, key)
            else:
                self.assertEqual({x[identity]: x['cycle'] for x in before[key]}, {x[identity]: x['cycle'] for x in after[key]}, key)


class TestBuild(Base):
    def test_fixture_release_passes_with_derived_counts(self):
        self.assertEqual(self.run_release(), 0, self.failed())
        ds = self.dataset()
        base = jread(self.base / 'data/dataset.json')
        new = [json.loads(l) for l in (self.root / 'data/new-posts.ndjson').read_text().splitlines() if l.strip()]
        self.assertEqual(len(ds['posts']), len(base['posts']) + len(new))
        self.assertEqual(ds['summary']['new_posts'], len(new))
        self.assertEqual(len(ds['snapshots']), len(jread(self.root / 'data/snapshots.json')))
        self.assertEqual(len(ds['velocity']), len(jread(self.root / 'data/velocity.json')))
        self.assertEqual(len(ds['cohorts']), len(jread(self.root / 'data/cohorts.json')))
        self.assertEqual(len(ds['assets']), len(base['assets']) + len(jread(self.root / 'data/media-manifest.json')))
        self.assertEqual({p['cycle'] for p in ds['posts']}, {'v2', 'v3', 'v4'})
        self.assertEqual(ds['summary']['posts_by_cycle'], {'v2': 2, 'v3': 2, 'v4': 5})
        self.assertEqual(len(ds['qualification']), len(ds['posts']))
        for key in ENTITY_KEYS:
            self.assertIn(key, ds)

    def test_release_checks_file_is_complete(self):
        self.assertEqual(self.run_release(), 0)
        rc = jread(self.root / 'verification/release-checks.json')
        self.assertEqual(rc['status'], 'pass')
        self.assertTrue(rc['checks'])
        for c in rc['checks']:
            self.assertEqual(set(c) - {'detail'}, {'name', 'status', 'expected', 'observed'}, c['name'])
            self.assertIn(c['status'], ('pass', 'fail', 'skipped'))
        names = {c['name'] for c in rc['checks']}
        for must in ['dedupe_activity_id', 'dedupe_attributed_share_urn', 'dedupe_canonical_url', 'dedupe_normalized_text_sha256',
                     'every_media_asset_has_analysis_or_gap', 'every_video_has_transcript_or_visible_text_or_gap', 'media_paths_resolve_from_index_html',
                     'sqlite_integrity_check', 'sqlite_table_per_entity_counts_equal_json', 'html_embeds_dataset_exactly', 'held_posts_have_no_media']:
            self.assertIn(must, names)
        for i in rc['inputs']:
            self.assertEqual(set(i) >= {'role', 'path', 'status', 'sha256', 'count'}, True)
            if i['status'] != 'missing':
                self.assertRegex(i['sha256'], r'^[0-9a-f]{64}$')
                self.assertEqual(i['sha256'], sha(self.root / i['path']), i['path'])
        self.assertEqual(rc['code']['release_py_sha256'], sha(RUN / 'release.py'))
        self.assertEqual(rc['code']['viewer_template_sha256'], sha(TEMPLATE))
        self.assertEqual({o['path'] for o in rc['outputs']}, {'data/dataset.json', 'data/posts.csv', 'data/new-posts.csv', 'data/snapshots.csv', 'data/velocity.csv', 'data/linkedin.sqlite', 'index.html', 'data/interpretations.json', 'data/performance.json', 'data/qualification-table.csv'})
        for o in rc['outputs']:
            self.assertEqual(o['sha256'], sha(self.root / o['path']), o['path'])
        self.assertEqual(rc['counts']['entities']['posts'], len(self.dataset()['posts']))
        self.assertFalse(list(self.root.rglob('*.tmp')))

    def test_sqlite_has_one_table_per_entity_and_matching_counts(self):
        self.assertEqual(self.run_release(), 0)
        ds = self.dataset()
        con = sqlite3.connect(self.root / 'data/linkedin.sqlite')
        self.addCleanup(con.close)
        self.assertEqual(con.execute('PRAGMA integrity_check').fetchone()[0], 'ok')
        tables = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        self.assertEqual(tables, {t for _k, t, _f, _p in release.ENTITIES})
        for key, table, _f, _p in release.ENTITIES:
            self.assertEqual(con.execute('SELECT count(*) FROM %s' % table).fetchone()[0], len(ds[key]), table)
        for table in ('snapshots', 'velocity', 'cohorts', 'transcript_qa', 'held_authors'):
            self.assertIn(table, tables)

    def test_html_embeds_dataset_exactly(self):
        self.assertEqual(self.run_release(), 0)
        html = (self.root / 'index.html').read_text()
        raw = re.search(r'<script id="dataset" type="application/json">(.*?)</script>', html, re.S).group(1)
        self.assertNotIn('<', raw)
        self.assertEqual(release.canon(json.loads(raw)), release.canon(self.dataset()))
        self.assertEqual(self.rel.html_hashes['embedded_canonical_sha256'], self.rel.html_hashes['dataset_json_canonical_sha256'])
        self.assertEqual(html.count('__DATASET__'), 0)

    def test_outputs_are_deterministic(self):
        self.assertEqual(self.run_release(), 0)
        first = {p: sha(self.root / p) for p in ['data/dataset.json', 'index.html', 'data/posts.csv', 'data/snapshots.csv']}
        self.assertEqual(self.run_release(), 0)
        self.assertEqual(first, {p: sha(self.root / p) for p in first})

    def test_dry_run_writes_nothing(self):
        before = sorted(str(p.relative_to(self.root)) for p in self.root.rglob('*'))
        self.assertEqual(self.run_release(dry_run=True), 0)
        self.assertEqual(before, sorted(str(p.relative_to(self.root)) for p in self.root.rglob('*')))

    def test_cli_main(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = release.main(['--root', str(self.root), '--base', str(self.base), '--template', str(TEMPLATE)])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out.getvalue().split('release: staging exports\n')[-1])['status'], 'pass')

    def test_missing_v4_inputs_are_treated_as_empty_and_reported(self):
        for rel in ['data/new-posts.ndjson', 'data/media-manifest.json', 'data/qualification.json', 'transcripts/index.json', 'data/snapshots.json', 'data/velocity.json',
                    'data/cohorts.json', 'data/transcript-qa.json', 'operations/account-qualification-queue.json', 'analysis/videos-a/reviews.json']:
            (self.root / rel).unlink()
        self.assertEqual(self.run_release(), 0, self.failed())
        ds, base = self.dataset(), jread(self.base / 'data/dataset.json')
        self.assertEqual(len(ds['posts']), len(base['posts']))
        self.assertEqual(ds['summary']['new_posts'], 0)
        for key in ('snapshots', 'velocity', 'cohorts', 'transcript_qa', 'held_authors', 'media_gaps'):
            self.assertEqual(ds[key], [], key)
        status = {i['role']: i['status'] for i in self.rel.inputs}
        for role in ('new_posts', 'snapshots', 'velocity', 'cohorts', 'transcript_qa', 'account_qualification_queue', 'media_manifest'):
            self.assertEqual(status[role], 'missing', role)

    def test_empty_files_are_accepted(self):
        for rel in ['data/media-manifest.json', 'data/qualification.json', 'transcripts/index.json', 'data/snapshots.json', 'data/velocity.json', 'data/cohorts.json',
                    'operations/account-qualification-queue.json', 'analysis/videos-a/reviews.json']:
            (self.root / rel).write_text('[]')
        (self.root / 'data/new-posts.ndjson').write_text('')
        (self.root / 'data/transcript-qa.json').write_text('')
        self.assertEqual(self.run_release(), 0, self.failed())
        self.assertEqual({i['role']: i['status'] for i in self.rel.inputs}['new_posts'], 'empty')
        self.assertEqual(self.dataset()['summary']['velocity_rows'], 0)

    def test_qa_accepts_list_shape_and_object_shape(self):
        self.assertEqual(self.run_release(), 0)
        obj = self.dataset()['transcript_qa']
        self.edit('data/transcript-qa.json', lambda d: d['records'])
        self.assertEqual(self.run_release(), 0, self.failed())
        self.assertEqual(self.dataset()['transcript_qa'], obj)

    def test_qa_gap_records_become_rows(self):
        a2 = 'urn:li:activity:7100000000000000002:video:0'
        def f(d):
            d['records'] = [r for r in d['records'] if r['asset_id'] != a2]
            d['gap_records'] = [{'asset_id': a2, 'reason': 'qa could not run'}]
        self.edit('data/transcript-qa.json', f)
        self.assertEqual(self.run_release(), 0, self.failed())
        row = next(r for r in self.dataset()['transcript_qa'] if r['asset_id'] == a2)
        self.assertEqual(row['status'], 'qa_gap')
        self.assertIn(('transcript_qa_gap', a2), {(g['kind'], g['ref']) for g in self.rel.gaps})

    def test_stale_manifest_review_status_is_derived_from_joined_reviews(self):
        self.assertEqual(self.run_release(), 0)
        a = next(a for a in self.dataset()['assets'] if a['asset_id'].endswith('0002:image:0'))
        self.assertEqual((a['manifest_review_status'], a['review_status']), ('not_reviewed', 'reviewed'))


class TestJoin(Base):
    def test_media_and_transcript_gaps_are_explicit(self):
        self.assertEqual(self.run_release(), 0)
        ds = self.dataset()
        gaps = {g['asset_id']: g for g in ds['media_gaps']}
        self.assertEqual(set(gaps), {'urn:li:activity:7100000000000000001:image:0', 'urn:li:activity:7100000000000000004:video:0'})
        for g in gaps.values():
            self.assertEqual(g['review_status'], 'not_reviewed')
            self.assertTrue(g['reason'])
        self.assertEqual([g['asset_id'] for g in ds['transcript_gaps']], ['urn:li:activity:7100000000000000004:video:0'])
        reviewed = {r['asset_id'] for r in ds['visual_reviews'] + ds['video_reviews']}
        analysed = {a['asset_id'] for a in ds['assets'] if a['kind'] in ('image', 'document_preview', 'video')}
        self.assertEqual(analysed, reviewed | set(gaps))
        self.assertFalse(reviewed & set(gaps))
        poster = next(a for a in ds['assets'] if a['kind'] == 'poster')
        self.assertEqual(poster['review_status'], 'not_applicable')
        self.assertTrue(any(g['kind'] == 'media_not_reviewed' for g in self.rel.gaps))

    def test_visible_text_counts_as_transcript_entry(self):
        # N2 loses its transcript record but keeps on-screen text in the video review: not a transcript gap
        (self.root / 'transcripts/index.json').write_text('[]')
        self.edit('data/transcript-qa.json', lambda d: d.update(records=d['records'][:1]))
        self.assertEqual(self.run_release(), 0, self.failed())
        gap_ids = {g['asset_id'] for g in self.dataset()['transcript_gaps']}
        self.assertNotIn('urn:li:activity:7100000000000000002:video:0', gap_ids)
        self.assertIn('urn:li:activity:7100000000000000004:video:0', gap_ids)

    def test_snapshots_velocity_and_cohorts_attach_by_post(self):
        self.assertEqual(self.run_release(), 0)
        ds = self.dataset()
        by_post = {}
        for s in ds['snapshots']:
            by_post.setdefault(s['post_id'], []).append(s)
        self.assertEqual(len(by_post['urn:li:activity:7000000000000000001']), 2)
        vel = {v['post_id']: v for v in ds['velocity']}
        elig = [v for v in vel.values() if v['eligible']]
        self.assertEqual(len(elig), 2)
        for v in elig:
            self.assertAlmostEqual(v['reactions_per_hour'], v['reaction_delta'] / v['span_hours'], places=3)
        for v in vel.values():
            if not v['eligible']:
                self.assertTrue(v['reason'])
        self.assertEqual(ds['summary']['velocity_eligible'], 2)
        self.assertEqual(ds['summary']['cohorts_not_ranked'], 1)
        self.assertNotIn(self.pid(5), vel)  # no snapshot -> no velocity record
        self.assertIn(('snapshot_missing', self.pid(5)), {(g['kind'], g['ref']) for g in self.rel.gaps})

    def test_unknown_metrics_stay_null_never_zero(self):
        self.assertEqual(self.run_release(), 0)
        ds = self.dataset()
        s = next(s for s in ds['snapshots'] if s['post_id'] == 'urn:li:activity:7000000000000000004' and s['capture_kind'] == 'reobservation')
        self.assertIsNone(s['metrics']['reactions']['value'])
        rows = (self.root / 'data/snapshots.csv').read_text().splitlines()
        hdr = rows[0].split(',')
        line = next(l for l in rows if s['snapshot_id'] in l).split(',')
        self.assertEqual(line[hdr.index('reactions')], '')
        self.assertEqual(line[hdr.index('comments')], '')

    def test_held_authors_and_queue(self):
        self.assertEqual(self.run_release(), 0)
        held = {h['author_key']: h for h in self.dataset()['held_authors']}
        self.assertEqual(set(held), {'/in/erin-held', '/in/frank-held'})
        self.assertEqual(held['/in/erin-held']['post_ids'], [self.pid(3)])
        self.assertEqual(held['/in/frank-held']['posts_missing_from_corpus'], ['urn:li:activity:7100000000000000999'])
        self.assertFalse([a for a in self.dataset()['assets'] if a['post_id'] == self.pid(3)])
        self.assertIn('held_post_not_in_corpus', {w['kind'] for w in self.rel.warnings})

    def test_accounts_cover_new_and_existing_authors(self):
        self.assertEqual(self.run_release(), 0)
        acc = {a['name']: a for a in self.dataset()['accounts']}
        self.assertEqual(acc['Alice Base']['posts'], 4)
        self.assertEqual(acc['Alice Base']['collection'], 'baseline')
        self.assertEqual(acc['Alice Base']['cycles'], ['v2', 'v3', 'v4'])
        self.assertEqual(acc['Alice Base']['first_cycle'], 'v2')
        self.assertEqual(acc['Dave New']['collection'], 'new')
        self.assertEqual(sum(a['posts'] for a in acc.values()), 9)

    def test_new_transcript_carries_timing_and_visible_text_fields(self):
        self.assertEqual(self.run_release(), 0)
        t = next(t for t in self.dataset()['transcripts'] if t['asset_id'].startswith('urn:li:activity:7100000000000000002'))
        self.assertEqual(t['cycle'], 'v4')
        self.assertEqual(t['timing_overrun_seconds'], 0)
        self.assertIsNone(t['timing_warning'])
        self.assertEqual(t['source_path'], 'transcripts/n2-1111.json')

    def test_alternative_is_loaded_beside_original_and_original_is_preserved(self):
        self.assertEqual(self.run_release(), 0)
        ds = self.dataset()
        qa = next(q for q in ds['transcript_qa'] if q.get('alternative'))
        self.assertEqual(qa['flags'], ['timing_overrun', 'repeated_tail'])
        self.assertIn('funnel', qa['alternative']['text'])
        self.assertIs(qa['alternative']['supersedes_original'], False)
        orig = next(t for t in ds['transcripts'] if t['asset_id'] == qa['asset_id'])
        base_t = jread(self.base / 'data/dataset.json')['transcripts'][0]
        self.assertEqual(orig['text'], base_t['text'])
        self.assertNotIn('funnel', orig['text'])
        self.assertEqual(qa['alternative']['path'], 'transcripts/alternatives/b3-alt.json')

    def test_target_audience_records_hold_no_posts_or_media(self):
        self.assertEqual(self.run_release(), 0)
        self.assertEqual(len(self.dataset()['prospects']), 2)
        self.edit('../v3/data/dataset.json', lambda d: d['prospects'][0].update(media=[{'x': 1}]))
        self.assert_fails('prospects_hold_no_posts_or_media')


@unittest.skipUnless(sys.platform == 'darwin', 'uses BSD file flags to stand in for iCloud-evicted files')
class TestDataless(Base):
    def setUp(self):
        super().setUp()
        import os
        import stat
        self.patch = unittest.mock.patch.object(release, 'SF_DATALESS', stat.UF_HIDDEN)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        for f in (self.base / 'media').glob('*'):
            os.chflags(f, stat.UF_HIDDEN)
        (self.base / 'media/b3-video-0.mp4').write_bytes(b'changed bytes, same flag')

    def test_evicted_files_are_checked_for_existence_but_not_read(self):
        (self.base / 'media/b3-video-0.mp4').write_bytes(b'v3 video bytes b3')  # keep the size; bytes would differ only if read
        self.assertEqual(self.run_release(), 0, self.failed())
        c = self.checks()['base_asset_files_exist_size_hash']
        self.assertEqual(c['observed']['skipped_dataless'], 2)  # the v2 image is not flagged
        self.assertEqual(c['observed']['hash_verified'], 1)
        self.assertIn('evicted to iCloud', c['detail'])

    def test_missing_evicted_file_still_fails(self):
        (self.base / 'media/b4-doc-0.png').unlink()
        self.assert_fails('base_asset_files_exist_size_hash')

    def test_hash_dataless_option_reads_them(self):
        (self.base / 'media/b3-video-0.mp4').write_bytes(b'v3 video bytes b3'.replace(b'v3', b'xx'))
        self.assertEqual(self.run_release(), 0, self.failed())  # same size, skipped
        self.assertEqual(self.run_release(hash_dataless=True), 1)
        self.assertIn('base_asset_files_exist_size_hash', self.failed())


class TestFailures(Base):
    """Every integrity violation must fail loudly and leave existing outputs untouched."""

    def prepare_old_outputs(self):
        (self.root / 'index.html').write_text('OLD INDEX')
        (self.root / 'data').mkdir(exist_ok=True)
        (self.root / 'data/dataset.json').write_text('OLD DATASET')

    def assert_blocked(self, name):
        self.prepare_old_outputs()
        rel = self.assert_fails(name)
        self.assertEqual((self.root / 'index.html').read_text(), 'OLD INDEX')
        self.assertEqual((self.root / 'data/dataset.json').read_text(), 'OLD DATASET')
        self.assertFalse(list(self.root.rglob('*.tmp')))
        rc = jread(self.root / 'verification/release-checks.json')
        self.assertEqual(rc['status'], 'fail')
        self.assertIn(name, rc['failed_checks'])
        return rel

    def add_post(self, **override):
        p = json.loads((self.root / 'data/new-posts.ndjson').read_text().splitlines()[0])
        n = 90
        p.update(id='urn:li:activity:%d' % (7200000000000000000 + n), url='https://www.linkedin.com/posts/dup-case-activity-%d-AbCd' % (7200000000000000000 + n),
                 attributed_urn='urn:li:share:%d' % (7200000000000000100 + n), text='A completely different dup test text number one.')
        p.update(override)
        with (self.root / 'data/new-posts.ndjson').open('a') as f:
            f.write(json.dumps(p) + '\n')
        return p

    def test_duplicate_text_against_base_fails(self):
        base_text = jread(self.base / 'data/dataset.json')['posts'][0]['text']
        self.add_post(text='  ' + base_text.upper() + '\n')
        self.assert_blocked('dedupe_normalized_text_sha256')

    def test_duplicate_activity_id_fails(self):
        base_id = jread(self.base / 'data/dataset.json')['posts'][0]['id']
        self.add_post(id=base_id)
        self.assert_blocked('dedupe_activity_id')

    def test_duplicate_canonical_url_fails_even_with_query_and_slash(self):
        url = jread(self.base / 'data/dataset.json')['posts'][0]['url']
        p = self.add_post()
        p['url'] = url  # exact duplicate URL; id differs
        lines = (self.root / 'data/new-posts.ndjson').read_text().splitlines()[:-1]
        (self.root / 'data/new-posts.ndjson').write_text('\n'.join(lines + [json.dumps(p)]) + '\n')
        self.assert_blocked('dedupe_canonical_url')

    def test_duplicate_attributed_share_urn_fails(self):
        urn = jread(self.base / 'data/dataset.json')['posts'][0]['attributed_urn']
        self.add_post(attributed_urn=urn)
        self.assert_blocked('dedupe_attributed_share_urn')

    def test_malformed_new_post_fails(self):
        self.add_post(metrics={'reactions': {'value': 0, 'status': 'not_exposed', 'source_path': None}})
        self.assert_blocked('new_posts_schema_valid')

    def test_snapshot_for_unknown_post_fails(self):
        self.edit('data/snapshots.json', lambda d: d[0].update(post_id='urn:li:activity:1'))
        self.assert_blocked('snapshots_valid')

    def test_duplicate_snapshot_id_fails(self):
        self.edit('data/snapshots.json', lambda d: d.append(copy.deepcopy(d[0])))
        self.assert_blocked('snapshots_unique_ids')

    def test_snapshot_raw_hash_mismatch_fails(self):
        self.edit('data/snapshots.json', lambda d: d[1].update(raw_sha256='0' * 64))
        self.assert_blocked('snapshot_raw_capture_bytes')

    def test_snapshot_zero_for_missing_counter_fails(self):
        self.edit('data/snapshots.json', lambda d: d[0]['metrics']['comments'].update(value=0, status='not_exposed'))
        self.assert_blocked('snapshots_valid')

    def test_velocity_arithmetic_must_hold(self):
        self.edit('data/velocity.json', lambda d: d[0].update(reactions_per_hour=9.9))
        self.assert_blocked('velocity_rows_valid')

    def test_velocity_endpoint_must_be_backed_by_snapshots(self):
        self.edit('data/velocity.json', lambda d: d[0].update(reactions_last=500, reaction_delta=400, reactions_per_hour=round(400 / 26.5, 4)))
        self.assert_blocked('velocity_rows_valid')

    def test_velocity_below_minimum_span_cannot_be_eligible(self):
        self.edit('data/velocity.json', lambda d: d[1].update(eligible=True, reason=None, reaction_delta=2, reactions_per_hour=round(2 / 3, 4)))
        self.assert_blocked('velocity_rows_valid')

    def test_velocity_snapshot_count_must_match(self):
        self.edit('data/velocity.json', lambda d: d[0].update(snapshots=5))
        self.assert_blocked('velocity_rows_valid')

    def test_ranked_cohort_below_min_n_fails(self):
        self.edit('data/cohorts.json', lambda d: d[1].update(ranked=True))
        self.assert_blocked('cohorts_valid')

    def test_cohort_n_must_equal_members(self):
        self.edit('data/cohorts.json', lambda d: d[0].update(n=7))
        self.assert_blocked('cohorts_valid')

    def test_missing_asset_file_fails(self):
        (self.root / 'media/n1-image-0.jpg').unlink()
        self.assert_blocked('new_asset_files_exist_size_hash')
        self.assertIn('media_paths_resolve_from_index_html', self.failed())

    def test_changed_asset_bytes_fail_hash(self):
        (self.root / 'media/n1-image-0.jpg').write_bytes(b'tampered')
        self.assert_blocked('new_asset_files_exist_size_hash')

    def test_review_for_different_bytes_fails(self):
        self.edit('analysis/videos-a/reviews.json', lambda d: d[0].update(source_sha256='1' * 64))
        self.assert_blocked('reviews_bound_to_asset_bytes')

    def test_review_for_unknown_asset_fails(self):
        self.edit('analysis/videos-a/reviews.json', lambda d: d.append({**d[0], 'asset_id': 'urn:li:activity:7100000000000000002:video:9'}))
        self.assert_blocked('reviews_reference_known_assets')

    def test_continuous_watch_claim_is_rejected(self):
        self.edit('analysis/videos-a/reviews.json', lambda d: d[0].update(full_watch=True))
        self.assert_blocked('no_unsupported_watch_or_audio_claims')

    def test_transcript_bound_to_other_bytes_fails(self):
        self.edit('transcripts/n2-1111.json', lambda d: d.update(source_video_sha256='2' * 64))
        self.assert_blocked('transcript_records_valid')

    def test_duplicate_asset_id_fails(self):
        self.edit('data/media-manifest.json', lambda d: d.append(copy.deepcopy(d[0])))
        self.assert_blocked('assets_unique_ids')

    def test_qa_for_unknown_asset_fails(self):
        self.edit('data/transcript-qa.json', lambda d: d['records'].append({**d['records'][1], 'asset_id': 'urn:li:activity:7100000000000000002:video:9'}))
        self.assert_blocked('transcript_qa_valid')

    def test_qa_bound_to_other_video_bytes_fails(self):
        self.edit('data/transcript-qa.json', lambda d: d['records'][1].update(source_video_sha256='3' * 64))
        self.assert_blocked('transcript_qa_valid')

    def test_alternative_file_hash_mismatch_fails(self):
        self.edit('transcripts/alternatives/b3-alt.json', lambda d: d.update(text='changed after hashing'))
        self.assert_blocked('transcript_qa_files_exist_hash')

    def test_alternative_must_not_supersede_original(self):
        self.edit('data/transcript-qa.json', lambda d: d['records'][0]['alternative'].update(supersedes_original=True))
        self.assert_blocked('transcript_qa_valid')

    def test_held_post_with_media_fails(self):
        self.edit('data/media-manifest.json', lambda d: d.append({**d[0], 'post_id': self.pid(3), 'asset_id': self.pid(3) + ':image:0'}))
        self.assert_blocked('held_posts_have_no_media')

    def test_queue_claiming_downloaded_media_fails(self):
        self.edit('operations/account-qualification-queue.json', lambda d: d[0].update(media_downloaded=True))
        self.assert_blocked('held_posts_have_no_media')

    def test_unreadable_input_aborts_with_failed_check(self):
        (self.root / 'data/snapshots.json').write_text('[{"a": 1, "a": 2}]')
        rel = self.assert_blocked('input_parses:snapshots')
        self.assertFalse(rel.counts)

    def test_truncated_json_aborts(self):
        (self.root / 'data/velocity.json').write_text('[{"post_id": ')
        self.assert_blocked('input_parses:velocity')

    def test_missing_base_dataset_aborts(self):
        (self.base / 'data/dataset.json').unlink()
        self.assert_blocked('input_present:base_dataset')

    def test_qualification_for_unknown_post_fails(self):
        self.edit('data/qualification.json', lambda d: d.append({'post_id': 'urn:li:activity:2'}))
        self.assert_blocked('qualification_references_known_posts')


class TestViewer(Base):
    @classmethod
    def setUpClass(cls):
        if not NODE:
            raise unittest.SkipTest('node is not installed')

    def render(self):
        self.assertEqual(self.run_release(), 0, self.failed())
        h = self.tmp / 'harness.js'
        h.write_text(HARNESS)
        r = subprocess.run([NODE, str(h), str(self.root / 'index.html')], capture_output=True, text=True, timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)

    def card(self, html, post_id):
        parts = re.split(r'(?=<article data-post-id=)', html)
        return next(p for p in parts if 'data-post-id="%s"' % post_id in p[:80])

    def test_defaults_and_filters(self):
        o = self.render()
        self.assertEqual(o['default_value'], 'new')
        self.assertTrue(o['default_count'].startswith('5 matching'))
        self.assertTrue(o['all_count'].startswith('9 matching'))
        self.assertIn('9 posts across 5 accounts', o['totals'])
        fc = o['filter_counts']
        self.assertEqual((fc['velocity_eligible'], fc['velocity_ineligible'], fc['velocity_none']), (2, 6, 1))
        self.assertEqual(fc['held'], 1)
        self.assertEqual(fc['qaflag'], 1)
        self.assertEqual(fc['reobserved'], 4)
        self.assertEqual((fc['video'], fc['image'], fc['doc']), (3, 2, 1))
        self.assertEqual(o['v3_count'], 2)
        self.assertIn('Cycle v2 only', o['collection_options'])
        self.assertFalse(o['target_hidden'] and not o['ref_hidden'])

    def test_default_collection_is_all_when_cycle_has_no_new_posts(self):
        (self.root / 'data/new-posts.ndjson').write_text('')
        for rel in ['data/media-manifest.json', 'data/qualification.json', 'transcripts/index.json', 'data/snapshots.json', 'data/velocity.json', 'data/cohorts.json',
                    'operations/account-qualification-queue.json']:
            (self.root / rel).write_text('[]')
        (self.root / 'analysis/videos-a/reviews.json').write_text('[]')
        self.edit('data/transcript-qa.json', lambda d: d.update(records=[], gap_records=[]))
        o = self.render()
        self.assertEqual(o['default_value'], 'all')
        self.assertTrue(o['default_count'].startswith('4 matching'))
        self.assertIn('No cohort records in this release', o['cohort'])
        self.assertTrue(o['held_hidden'])

    def test_velocity_line_wording_and_ineligible_reasons(self):
        o = self.render()
        eligible = self.card(o['all'], 'urn:li:activity:7000000000000000001')
        self.assertIn('observed reaction change +12 over 26.5 h (0.45/h); public counter, not reach/impressions/trend rank', eligible)
        short = self.card(o['all'], 'urn:li:activity:7000000000000000002')
        self.assertIn('Velocity: not computed', short)
        self.assertIn('span below minimum', short)
        self.assertNotIn('observed reaction change', short)
        single = self.card(o['all'], self.pid(3))
        self.assertIn('single capture', single)
        none = self.card(o['all'], self.pid(5))
        self.assertIn('Velocity: unknown', none)
        self.assertIn('no velocity record', none)

    def test_snapshot_history_table_and_unknown_values(self):
        o = self.render()
        c = self.card(o['all'], 'urn:li:activity:7000000000000000004')
        for col in ('captured_at', 'kind', 'reactions', 'comments', 'reposts'):
            self.assertIn('>%s<' % col, c)
        self.assertEqual(len(re.findall(r'<td>(?:2026)', c)), 2)  # two snapshot rows
        row = re.findall(r'<tr><td>2026-10-22T20:00:00\+00:00</td>.*?</tr>', c)[0]
        self.assertEqual(row.count('>unknown<'), 3)  # reactions, comments, reposts not exposed -> unknown, not 0
        self.assertIn('reobservation', row)
        implicit = self.card(o['all'], self.pid(5))
        self.assertIn('no snapshot record (post capture shown)', implicit)

    def test_cohort_table_labels_unranked_cohorts(self):
        o = self.render()
        self.assertIn('n &lt; min_n, not ranked', o['cohort'])
        self.assertIn('<td>ranked</td>', o['cohort'])
        self.assertIn('age_0_7d|video', o['cohort'])
        self.assertIn('2 of 8 velocity rows are eligible', o['cohort_note'])
        self.assertIn('span below minimum', o['cohort_note'])
        self.assertIn('not reach/impressions/trend rank', o['cohort_note'])

    def test_transcript_dropdown_shows_qa_flags_and_side_by_side_alternative(self):
        o = self.render()
        c = self.card(o['all'], 'urn:li:activity:7000000000000000003')
        self.assertIn('QA flagged (2 flags)', c)
        self.assertIn('timing overrun', c)
        self.assertIn('repeated tail', c)
        self.assertIn('unreviewed alternative; original preserved', c)
        self.assertIn('Original transcript (preserved)', c)
        self.assertIn('class="cols"', c)
        self.assertLess(c.index('Alice talks about demand generation. You You'), c.index('and the funnel'))
        n2 = self.card(o['all'], self.pid(2))
        self.assertIn('QA pass', n2)
        self.assertNotIn('unreviewed alternative', n2)

    def test_every_asset_keeps_its_analysis_dropdown_and_every_video_its_transcript(self):
        o = self.render()
        ds = self.dataset()
        media = [a for a in ds['assets'] if a['kind'] in ('image', 'document_preview', 'video')]
        videos = [a for a in media if a['kind'] == 'video']
        self.assertEqual(o['all'].count('class="media-analysis"'), len(media))  # includes the open "not reviewed" ones
        self.assertEqual(o['all'].count('class="media-transcript"'), len(videos))
        self.assertIn('Not reviewed: no analysis record found in analysis inputs', o['all'])
        n4 = self.card(o['all'], self.pid(4))
        self.assertIn('Gap: no transcript record and no visible-text record', n4)
        self.assertIn('Transcript — gap', n4)

    def test_held_authors_panel_and_badge(self):
        o = self.render()
        self.assertFalse(o['held_hidden'])
        self.assertIn('Erin Held', o['held'])
        self.assertIn('Frank Held', o['held'])
        self.assertIn('held author', self.card(o['all'], self.pid(3)))

    def test_target_tab_has_company_links_and_evidence_only(self):
        o = self.render()
        t = o['company']
        self.assertIn('Company 1', t)
        self.assertIn('LinkedIn company', t)
        self.assertIn('Qualification gaps and source references', t)
        for forbidden in ('<img', '<video', 'data-post-id', 'class="media"', 'Snapshot history'):
            self.assertNotIn(forbidden, t)
        self.assertIn('no harvested prospect post histories, media or employee lists', o['target_note'])
        self.assertTrue(o['ref_hidden'] and not o['target_hidden'])

    def test_links_are_limited_to_existing_files(self):
        o = self.render()
        for href in re.findall(r'href="([^"]+)"', o['links']):
            self.assertTrue((self.root / href).exists(), href)
        self.assertNotIn('handoff/CLAUDE-PROMPT.md', o['links'])  # absent in the fixture run, so not linked
        self.assertIn('README.md', o['links'])

    def test_media_paths_in_page_resolve_and_match_safe_pattern(self):
        o = self.render()
        rx = re.compile(release.SAFE_PATH_PATTERN)
        paths = re.findall(r'(?:src|href)="((?:\.\./[A-Za-z0-9._-]+/)?(?:media|transcripts)/[^"]+)"', o['all'])
        self.assertTrue(paths)
        for p in paths:
            self.assertRegex(p, rx)
            self.assertTrue((self.root / p).exists(), p)
        self.assertIn('../v2/media/b2-image-0.jpg', paths)
        self.assertIn('../v3/media/b3-video-0.mp4', paths)
        self.assertIn('media/n1-image-0.jpg', paths)


if __name__ == '__main__':
    unittest.main()
