#!/usr/bin/env python3
"""Regenerate the release-builder fixture tree (v2/, v3/, v4/) deterministically.

    python3 _generate.py        # rewrites the fixture files next to this script

v2 = oldest media holder, v3 = base cycle (data/dataset.json), v4 = the run being released.
Shapes mirror the live pipeline: list snapshots/velocity/cohorts, object-shaped transcript QA with
file-backed alternative decodes, a list-shaped held-author queue, empty-able inputs.
"""
import hashlib
import json
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
for d in ('v2', 'v3', 'v4'):
    shutil.rmtree(HERE / d, ignore_errors=True)


def sha(b):
    return hashlib.sha256(b).hexdigest()


def put(rel, data):
    p = HERE / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    b = data if isinstance(data, bytes) else (json.dumps(data, indent=2, ensure_ascii=False) + '\n').encode()
    p.write_bytes(b)
    return sha(b), len(b)


def put_ndjson(rel, rows):
    p = HERE / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows))


def metric(v):
    return {'value': v, 'status': 'observed' if v is not None else 'not_exposed', 'source_path': None}


def metrics(r, c, rp=None):
    base = {k: metric(None) for k in ['reactions', 'comments', 'reposts', 'impressions', 'reach', 'views', 'clicks', 'saves']}
    base.update(reactions=metric(r), comments=metric(c), reposts=metric(rp))
    return base


def post(pid, slug, name, path, text, published, captured, r, c, raw_rel, raw_owner, share):
    raw = ('<html><article data-activity-urn="urn:li:activity:%d">%s</article></html>' % (pid, slug)).encode()
    h, _ = put(raw_owner + '/' + raw_rel, raw)
    return {'schema_version': 1, 'parser_version': '0.2.1', 'id': 'urn:li:activity:%d' % pid,
            'url': 'https://www.linkedin.com/posts/%s-activity-%d-AbCd' % (slug, pid), 'attributed_urn': share,
            'captured_at': captured,
            'source': {'method': 'captured_public_guest_html', 'raw_path': raw_rel, 'sha256': h, 'rights': 'research_only_unverified_reuse',
                       'coverage': 'single_public_page_subset', 'all_author_posts': False},
            'author': {'name': name, 'url': 'https://www.linkedin.com' + path, 'type': 'Person', 'followers': 1000},
            'published_at': published, 'text': text, 'text_status': 'captured_dom_completeness_unverified',
            'metrics': metrics(r, c), 'media': [], 'transcript': {'text': None, 'origin': None, 'status': 'not_exposed', 'language': None, 'timing': None},
            'warnings': []}


# ---------------------------------------------------------------- base cycle (v3), media in v2/v3
B1 = post(7000000000000000001, 'alice-base-first', 'Alice Base', '/in/alice-base', 'Alice base post one about positioning for founders.', '2026-09-01T10:00:00.000Z', '2026-10-20T10:00:00+00:00', 100, 10, 'raw/b1.html', 'v3', 'urn:li:share:7000000000000000101')
B2 = post(7000000000000000002, 'bob-base-image', 'Bob Base', '/in/bob-base', 'Bob base post two with an image about outbound sales.', '2026-08-15T09:00:00.000Z', '2026-10-20T10:00:00+00:00', 50, 5, 'raw/b2.html', 'v3', 'urn:li:share:7000000000000000102')
B3 = post(7000000000000000003, 'alice-base-video', 'Alice Base', '/in/alice-base', 'Alice base post three with a video about demand generation.', '2026-10-15T09:00:00.000Z', '2026-10-22T08:00:00+00:00', 200, 20, 'raw/b3.html', 'v3', 'urn:li:share:7000000000000000103')
B4 = post(7000000000000000004, 'carol-base-doc', 'Carol Base', '/company/carol-base', 'Carol base post four, an undated document preview about SaaS.', None, '2026-10-22T08:00:00+00:00', 10, 1, 'raw/b4.html', 'v3', None)
img_b2, n_img_b2 = put('v2/media/b2-image-0.jpg', b'v2 image bytes b2')
vid_b3, n_vid_b3 = put('v3/media/b3-video-0.mp4', b'v3 video bytes b3')
doc_b4, n_doc_b4 = put('v3/media/b4-doc-0.png', b'v3 document preview bytes b4')
asset = lambda pid, kind, rel, h, n, i=0: {'post_id': 'urn:li:activity:%d' % pid, 'asset_id': 'urn:li:activity:%d:%s:%d' % (pid, 'video' if kind == 'video' else 'image' if kind == 'image' else 'image', i),
                                           'kind': kind, 'url': 'https://media.licdn.com/dms/image/x', 'filename': Path(rel).name, 'status': 'acquired', 'path': rel,
                                           'bytes': n, 'sha256': h, 'rights': 'Internal analysis only', 'review_status': 'not_reviewed'}
A_B2 = {**asset(7000000000000000002, 'image', '../v2/media/b2-image-0.jpg', img_b2, n_img_b2), 'collection': 'baseline'}
A_B3 = {**asset(7000000000000000003, 'video', 'media/b3-video-0.mp4', vid_b3, n_vid_b3), 'collection': 'new',
        'ffprobe': {'format': {'duration': '74.1'}}}
A_B4 = {**asset(7000000000000000004, 'document_preview', 'media/b4-doc-0.png', doc_b4, n_doc_b4), 'asset_id': 'urn:li:activity:7000000000000000004:document:0', 'collection': 'new'}
asr_b3 = {'post_id': B3['id'], 'asset_id': A_B3['asset_id'], 'origin': 'local_cached_whisper_ASR', 'text': ' Alice talks about demand generation. You You You You You',
          'segments': [{'id': 0, 'start': 0.0, 'end': 70.0, 'text': ' Alice talks about demand generation.'}, {'id': 1, 'start': 70.0, 'end': 76.36, 'text': ' You You You You You'}],
          'source_video_sha256': vid_b3, 'audio_verified': False, 'review_status': 'transcript_available_not_audio_verified'}
sha_asr_b3, _ = put('v3/transcripts/b3-asr.json', asr_b3)
alt_b3 = {'schema': 'linkedin-transcript-alternative/1', 'post_id': B3['id'], 'asset_id': A_B3['asset_id'], 'origin': 'local_whisper_ASR_alternative_decode',
          'source_video_sha256': vid_b3, 'language': 'en', 'text': ' Alice talks about demand generation and the funnel.',
          'segments': [{'id': 0, 'start': 0.0, 'end': 62.9, 'text': ' Alice talks about demand generation and the funnel.'}],
          'review_status': 'alternative_decode_unreviewed', 'supersedes_original': False}
sha_alt_b3, _ = put('v4/transcripts/alternatives/b3-alt.json', alt_b3)

vis = lambda a, coll: {'asset_id': a['asset_id'], 'post_id': a['post_id'], 'source_sha256': a['sha256'], 'review_status': 'reviewed', 'review_mode': 'contact_sheet_actual_view',
                       'description': {'form': 'screenshot', 'composition': 'fixture composition for ' + a['asset_id']}, 'caveats': ['fixture only'], 'collection': coll}
vid_review_b3 = {'asset_id': A_B3['asset_id'], 'post_id': B3['id'], 'source_sha256': vid_b3, 'review_status': 'reviewed', 'full_watch': False, 'audio_review': False,
                 'review_mode': 'dense_sampled_timeline_plus_transcript', 'description': {'format': 'talking head'}, 'story_summary': 'A founder explains demand generation.',
                 'onscreen_text_observed': [{'sample_seconds': 4, 'text': 'Demand gen'}], 'collection': 'new'}
base_trans = {'post_id': B3['id'], 'asset_id': A_B3['asset_id'], 'origin': 'local_cached_whisper_ASR', 'text': asr_b3['text'], 'source_path': 'transcripts/b3-asr.json',
              'source_video_sha256': vid_b3, 'source_sha256': sha_asr_b3, 'audio_verified': False, 'timing_overrun_seconds': 2.26,
              'timing_warning': 'ASR segments exceed source duration; repeated tail may be hallucinated. Original output preserved; audio verification required.', 'collection': 'new'}
prospect = lambda i, fit: {'id': 'P0%d' % i, 'stable_key': 'company%d.example' % i, 'name': 'Company %d' % i, 'website': 'https://company%d.example/' % i,
                           'linkedin_url': 'https://www.linkedin.com/company/company%d/' % i, 'description': 'Fixture company %d builds software.' % i,
                           'reviewed_at': '2026-10-22T08:00:00+00:00', 'fit_status': fit, 'fit_is_not_sales_qualification': True,
                           'country_and_base': {'value': 'Germany'}, 'headcount': {'value': '11-50'}, 'business': {'value': 'software'}, 'funding': {'value': 'Seed', 'announcement_date': '2024-01-01'},
                           'linkedin_presence': {'status': 'public_company_about_page_observed', 'scope': 'General presence only; no post text or media harvested.'},
                           'content_opportunity': {'status': 'HYPOTHESIS', 'angle': 'fixture angle'}, 'expressed_need': {'status': 'unknown'}, 'buying_interest': {'status': 'unknown'},
                           'next_step': 'verify', 'gaps': ['need unknown']}
qrec = lambda p, **k: {'post_id': p['id'], 'publication_date_verified': p['published_at'] is not None, 'age_days': 30.0 if p['published_at'] else None,
                       'reference_class': 'recent_reference' if p['published_at'] else 'date_unverified', 'trending_status': 'not_established', 'sales_effectiveness': 'unknown', **k}
base_posts = [{**B1, 'collection': 'baseline'}, {**B2, 'collection': 'baseline'}, {**B3, 'collection': 'new'}, {**B4, 'collection': 'new'}]
put('v3/data/dataset.json', {
    'summary': {'run_id': 'v3', 'schedule_active': False, 'external_supervisor_wakeup': False, 'paid_provider_spend': 0},
    'posts': base_posts, 'assets': [A_B2, A_B3, A_B4], 'visual_reviews': [vis(A_B2, 'baseline'), vis(A_B4, 'new')], 'video_reviews': [vid_review_b3],
    'transcripts': [base_trans], 'qualification': [qrec(B1), qrec(B2), qrec(B3), qrec(B4)],
    'accounts': [{'id': 'x', 'name': 'Alice Base', 'url': B1['author']['url'], 'posts': 2, 'within90': 1, 'distinct_weeks90': 1}],
    'prospects': [prospect(1, 'observed_icp_fit'), prospect(2, 'plausible_pending_evidence')]})

# ---------------------------------------------------------------- this run (v4)
N1 = post(7100000000000000001, 'alice-base-new-image', 'Alice Base', '/in/alice-base', 'Alice new post about messaging with an image that is not yet reviewed.', '2026-10-21T09:00:00.000Z', '2026-10-22T09:00:00+00:00', 15, 1, 'raw/objects/n1.html', 'v4', 'urn:li:share:7100000000000000101')
N2 = post(7100000000000000002, 'dave-new-video', 'Dave New', '/in/dave-new', 'Dave new post with a video about founder stories.', '2026-10-20T09:00:00.000Z', '2026-10-22T09:00:00+00:00', 30, 2, 'raw/objects/n2.html', 'v4', 'urn:li:share:7100000000000000102')
N3 = post(7100000000000000003, 'erin-held-text', 'Erin Held', '/in/erin-held', 'Erin held post text only, her account is waiting for qualification.', '2026-10-19T09:00:00.000Z', '2026-10-22T09:00:00+00:00', 8, 0, 'raw/objects/n3.html', 'v4', 'urn:li:share:7100000000000000103')
N4 = post(7100000000000000004, 'dave-new-silent', 'Dave New', '/in/dave-new', 'Dave second post with a video that has no transcript yet.', '2026-10-18T09:00:00.000Z', '2026-10-22T09:00:00+00:00', 4, 0, 'raw/objects/n4.html', 'v4', 'urn:li:share:7100000000000000104')
N5 = post(7100000000000000005, 'alice-base-no-snapshot', 'Alice Base', '/in/alice-base', 'Alice fifth new post that has no snapshot or qualification record.', '2026-10-17T09:00:00.000Z', '2026-10-22T09:00:00+00:00', 3, 0, 'raw/objects/n5.html', 'v4', None)
put_ndjson('v4/data/new-posts.ndjson', [N1, N2, N3, N4, N5])
img_n1, n_img_n1 = put('v4/media/n1-image-0.jpg', b'v4 image bytes n1')
vid_n2, n_vid_n2 = put('v4/media/n2-video-0.mp4', b'v4 video bytes n2')
pos_n2, n_pos_n2 = put('v4/media/n2-poster-0.jpg', b'v4 poster bytes n2')
vid_n4, n_vid_n4 = put('v4/media/n4-video-0.mp4', b'v4 video bytes n4')
a_n1 = {**asset(7100000000000000001, 'image', 'media/n1-image-0.jpg', img_n1, n_img_n1)}
a_n1.pop('review_status')
a_n2 = {**asset(7100000000000000002, 'video', 'media/n2-video-0.mp4', vid_n2, n_vid_n2), 'ffprobe': {'format': {'duration': '3.0'}}}
a_n2.pop('review_status')
a_n2p = {**asset(7100000000000000002, 'image', 'media/n2-poster-0.jpg', pos_n2, n_pos_n2), 'kind': 'poster', 'asset_id': 'urn:li:activity:7100000000000000002:poster:0'}
a_n2p.pop('review_status')
a_n4 = {**asset(7100000000000000004, 'video', 'media/n4-video-0.mp4', vid_n4, n_vid_n4), 'ffprobe': {'format': {'duration': '5.0'}}}
a_n4.pop('review_status')
put('v4/data/media-manifest.json', [a_n1, a_n2, a_n2p, a_n4])
put('v4/analysis/videos-a/reviews.json', [{'asset_id': a_n2['asset_id'], 'post_id': N2['id'], 'source_sha256': vid_n2, 'review_status': 'reviewed', 'full_watch': False, 'audio_review': False,
                                           'review_mode': 'dense_sampled_timeline_plus_transcript', 'description': {'format': 'screen recording'}, 'story_summary': 'A short fixture demo.',
                                           'onscreen_text_observed': [{'sample_seconds': 1, 'text': 'Hello fixture'}], 'caveats': ['sampled frames only']}])
tr_n2 = {'post_id': N2['id'], 'asset_id': a_n2['asset_id'], 'origin': 'local_whisper_ASR', 'text': ' Hello from the fixture video.', 'segments': [{'id': 0, 'start': 0.0, 'end': 2.5, 'text': ' Hello from the fixture video.'}],
         'source_video_sha256': vid_n2, 'audio_verified': False, 'review_status': 'transcript_available_not_audio_verified'}
sha_tr_n2, _ = put('v4/transcripts/n2-1111.json', tr_n2)
put('v4/transcripts/index.json', [{'asset_id': a_n2['asset_id'], 'post_id': N2['id'], 'path': 'transcripts/n2-1111.json', 'source_video_sha256': vid_n2}])
put('v4/data/qualification.json', [qrec(N1), qrec(N2), qrec(N3, account_watchlist_approved=False), qrec(N4)])

# snapshots (list), one per capture; baseline copies reference the base raw files relatively
def snap(post, kind, at, r, c, rp=None, raw=None, rawpath=None, run='v4'):
    sid = sha(('%s|%s|%s' % (post['id'], at, kind)).encode())
    return {'snapshot_id': sid, 'post_id': post['id'], 'url': post['url'], 'captured_at': at, 'capture_kind': kind, 'source_run': run,
            'raw_sha256': raw or post['source']['sha256'], 'raw_path': rawpath, 'parser_version': '0.2.1', 'published_at': post['published_at'],
            'date_status': 'verified_source_date' if post['published_at'] else 'date_missing', 'text_sha256': sha(post['text'].encode()),
            'reobservation_flags': [], 'metrics': {'reactions': {'value': r, 'status': 'observed' if r is not None else 'not_exposed'},
                                                    'comments': {'value': c, 'status': 'observed' if c is not None else 'not_exposed'},
                                                    'reposts': {'value': rp, 'status': 'observed' if rp is not None else 'not_exposed'}}}
re_html = lambda name, body: put('v4/raw/objects/' + name, body.encode())[0]
h_b1r = re_html('b1-re.html', 'reobservation of b1')
h_b2r = re_html('b2-re.html', 'reobservation of b2')
h_b4r = re_html('b4-re.html', 'reobservation of b4')
h_n2r = re_html('n2-re.html', 'reobservation of n2')
S = [snap(B1, 'baseline_import', '2026-10-20T10:00:00+00:00', 100, 10, None, rawpath='../v3/raw/b1.html', run='v2'),
     snap(B1, 'reobservation', '2026-10-21T12:30:00+00:00', 112, 12, None, h_b1r, 'raw/objects/b1-re.html'),
     snap(B2, 'baseline_import', '2026-10-20T10:00:00+00:00', 50, 5, None, rawpath='../v3/raw/b2.html', run='v2'),
     snap(B2, 'reobservation', '2026-10-20T13:00:00+00:00', 52, 5, None, h_b2r, 'raw/objects/b2-re.html'),
     snap(B3, 'baseline_import', '2026-10-22T08:00:00+00:00', 200, 20, None, rawpath='../v3/raw/b3.html', run='v3'),
     snap(B4, 'baseline_import', '2026-10-22T08:00:00+00:00', 10, 1, None, rawpath='../v3/raw/b4.html', run='v3'),
     snap(B4, 'reobservation', '2026-10-22T20:00:00+00:00', None, None, None, h_b4r, 'raw/objects/b4-re.html'),
     snap(N1, 'new_discovery', '2026-10-22T09:00:00+00:00', 15, 1, rawpath='raw/objects/n1.html'),
     snap(N2, 'new_discovery', '2026-10-22T09:00:00+00:00', 30, 2, None, rawpath='raw/objects/n2.html'),
     snap(N2, 'reobservation', '2026-10-23T09:00:00+00:00', 36, 3, 1, h_n2r, 'raw/objects/n2-re.html'),
     snap(N3, 'new_discovery', '2026-10-22T09:00:00+00:00', 8, 0, rawpath='raw/objects/n3.html'),
     snap(N4, 'new_discovery', '2026-10-22T09:00:00+00:00', 4, 0, rawpath='raw/objects/n4.html')]
put('v4/data/snapshots.json', S)
vrow = lambda p, a, b, **k: {'post_id': p['id'], 'snapshots': 2 if a != b else 1, 'first_captured_at': a, 'last_captured_at': b, 'eligible': False, 'reason': 'single_capture', 'span_hours': 0.0,
                             'reactions_first': None, 'reactions_last': None, 'reaction_delta': None, 'reactions_per_hour': None, 'comments_delta': None, 'counter_decreased': False,
                             'age_days_at_first_capture': 5.0, 'media_kind': 'text_or_other', 'cohort': 'age_31_90d|text_or_other', 'publication_date_status': 'verified_source_date',
                             'measure': 'public reaction counter change; not reach, impressions, engagement rate or trend rank', **k}
V = [vrow(B1, '2026-10-20T10:00:00+00:00', '2026-10-21T12:30:00+00:00', eligible=True, reason=None, span_hours=26.5, reactions_first=100, reactions_last=112, reaction_delta=12,
          reactions_per_hour=round(12 / 26.5, 4), comments_delta=2),
     vrow(B2, '2026-10-20T10:00:00+00:00', '2026-10-20T13:00:00+00:00', reason='span_below_minimum', span_hours=3.0, reactions_first=50, reactions_last=52),
     vrow(B3, '2026-10-22T08:00:00+00:00', '2026-10-22T08:00:00+00:00', media_kind='video', cohort='age_0_7d|video'),
     vrow(B4, '2026-10-22T08:00:00+00:00', '2026-10-22T20:00:00+00:00', reason='reaction_counter_not_exposed', span_hours=12.0, reactions_first=10, publication_date_status='date_missing', age_days_at_first_capture=None, media_kind='document', cohort='age_unknown|document'),
     vrow(N1, '2026-10-22T09:00:00+00:00', '2026-10-22T09:00:00+00:00', media_kind='image', cohort='age_0_7d|image'),
     vrow(N2, '2026-10-22T09:00:00+00:00', '2026-10-23T09:00:00+00:00', eligible=True, reason=None, span_hours=24.0, reactions_first=30, reactions_last=36, reaction_delta=6, reactions_per_hour=0.25, comments_delta=1, media_kind='video', cohort='age_0_7d|video'),
     vrow(N3, '2026-10-22T09:00:00+00:00', '2026-10-22T09:00:00+00:00'),
     vrow(N4, '2026-10-22T09:00:00+00:00', '2026-10-22T09:00:00+00:00', media_kind='video', cohort='age_0_7d|video')]
put('v4/data/velocity.json', V)
put('v4/data/cohorts.json', [{'cohort': 'age_31_90d|text_or_other', 'n': 2, 'median_reactions_per_hour': 0.4528, 'ranked': True, 'min_n': 2, 'members': [B1['id'], B2['id']]},
                             {'cohort': 'age_0_7d|video', 'n': 1, 'median_reactions_per_hour': 0.25, 'ranked': False, 'min_n': 8, 'members': [N2['id']]}])
put('v4/data/transcript-qa.json', {
    'schema': 'linkedin-transcript-qa/1', 'statement': 'Mechanical checks only.',
    'records': [{'post_id': B3['id'], 'asset_id': A_B3['asset_id'], 'transcript_path': 'transcripts/b3-asr.json', 'transcript_sha256': sha_asr_b3, 'source_video_sha256': vid_b3,
                 'origin': 'local_cached_whisper_ASR', 'flags': ['timing_overrun', 'repeated_tail'], 'status': 'flagged',
                 'details': {'timing_overrun': {'duration_seconds': 74.1, 'last_segment_end': 76.36, 'overrun_seconds': 2.26}, 'repeated_tail': {'excerpt': 'You'}},
                 'audio_verified': False, 'accuracy_verified': False,
                 'alternative': {'path': 'transcripts/alternatives/b3-alt.json', 'sha256': sha_alt_b3, 'review_status': 'alternative_decode_unreviewed', 'supersedes_original': False,
                                 'adjudication': 'none: neither transcript is declared correct; a human must review the audio',
                                 'side_by_side': {'original': {'status': 'flagged', 'text_chars': 56, 'segments': 2}, 'alternative': {'status': 'pass', 'text_chars': 50, 'segments': 1}}}},
                {'post_id': N2['id'], 'asset_id': a_n2['asset_id'], 'transcript_path': 'transcripts/n2-1111.json', 'transcript_sha256': sha_tr_n2, 'source_video_sha256': vid_n2,
                 'origin': 'local_whisper_ASR', 'flags': [], 'status': 'pass', 'details': {}, 'audio_verified': False, 'accuracy_verified': False, 'alternative': None}],
    'gap_records': []})
put('v4/operations/account-qualification-queue.json', [
    {'post_id': N3['id'], 'url': N3['url'], 'author': N3['author'], 'published_at': N3['published_at'], 'status': 'awaiting_reference_account_qualification', 'media_downloaded': False,
     'required': 'supervisor confirms public B2B role/topic relevance before watchlist and media collection'},
    {'post_id': 'urn:li:activity:7100000000000000999', 'url': 'https://www.linkedin.com/posts/frank-held-queued-activity-7100000000000000999-AbCd',
     'author': {'name': 'Frank Held', 'url': 'https://www.linkedin.com/in/frank-held'}, 'published_at': '2026-10-10T09:00:00.000Z', 'status': 'awaiting_reference_account_qualification',
     'media_downloaded': False, 'required': 'supervisor confirms public B2B role/topic relevance before watchlist and media collection'}])
put('v4/pipeline/config.json', {'qualification': {'as_of': 'runtime-resolved-Europe/Sofia', 'as_of_mode': 'runtime', 'velocity_min_observation_span_hours': 6,
                                                   'account_regular_min_posts90': 8, 'account_regular_min_distinct_weeks90': 6}, 'analysis': {'continuous_watch_claim_allowed': False}})
put('v4/README.md', b'# fixture run\n')
print('fixtures written under', HERE)
