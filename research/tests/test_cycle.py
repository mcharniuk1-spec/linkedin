"""Offline tests for pipeline/cycle.py v4. No network, model or media decode calls.

Fixtures are original synthetic legacy and guest pages; every test writes only to
a fresh temporary run root and a temporary corpus file.
"""
from pathlib import Path
from datetime import datetime, timedelta, timezone
import json, os, re, sqlite3, sys, tempfile, unittest, urllib.request
HERE=Path(__file__).resolve().parent;RUN=HERE.parent;sys.path.insert(0,str(RUN/'pipeline'))
import cycle, normalizer
from synthetic_cycle import records, LINKED
V3POSTS,V2POSTS,GUEST_FIXTURES=records()
def iso(d):return d.isoformat()
def with_reactions(raw,n):
    """Rewrite the main-post reaction counter in a captured page (simulates a later capture)."""
    return re.sub(rb'(data-test-id="social-actions__reaction-count"[^>]*>\s*)[0-9][0-9,]*',lambda m:m.group(1)+str(n).encode(),raw,count=1)

class Base(unittest.TestCase):
    def setUp(self):
        self.tmp=Path(tempfile.mkdtemp(prefix='v4cycle-'));(self.tmp/'corpus/data').mkdir(parents=True)
        self.corpus=[p for p in V3POSTS[:6]]
        if not any(p['id']==LINKED for p in self.corpus):self.corpus.append(next(p for p in V3POSTS if p['id']==LINKED))
        self.write_corpus()
        cfg=json.loads((RUN/'pipeline/config.json').read_text());cfg['run_root']=str(self.tmp/'run');cfg['corpus_posts']=[str(self.tmp/'corpus/data/posts.ndjson')]
        cfg['discovery']['queries']=['fixture topic '+str(i) for i in range(4)];cfg['discovery']['max_queries']=4;cfg['discovery']['author_queries_per_cycle']=3;cfg['collection_approval']['approved_author_paths']=['/in/synthetic-author-1','/in/synthetic-author-2','/in/synthetic-link-author'];cfg['capture']['wave_delay_seconds']=0;cfg['media']['prior_post_ids']=[];cfg['corpus_snapshots']=[];cfg['transcript_qa']={'corpus_datasets':[]};self.cfg=cfg;self.cfgp=self.tmp/'config.json';self.cfgp.write_text(json.dumps(cfg))
        self.calls=[]
    def write_corpus(self):(self.tmp/'corpus/data/posts.ndjson').write_text(''.join(json.dumps(p)+'\n' for p in self.corpus))
    def cyc(self,**kw):
        c=cycle.Cycle(self.cfgp,**kw);c.config_path=self.cfgp;return c
    def fake(self,c,pages,at):
        """Serve fixed bytes per URL with a controlled capture time; record every call."""
        def get(url,kind='page'):
            self.calls.append(url);c.requests_made+=1;b=pages.get(url)
            r={'url':url,'captured_at':iso(at),'kind':kind,'cookies':False}
            if b is None:r.update(status='stopped',http_status=429,error='HTTPError');return r,None
            r.update(status='acquired',http_status=200,final_url=url,sha256=cycle.sha(b),bytes=len(b));return r,b
        c.get=get
    def tearDown(self):
        import shutil;shutil.rmtree(self.tmp,ignore_errors=True)

class Identity(Base):
    def test_baseline_import_idempotent_and_hash_checked(self):
        c=self.cyc();a=c.import_baseline();b=c.import_baseline()
        self.assertEqual(a['imported_or_verified'],len(self.corpus));self.assertEqual(b['errors'],0)
        self.assertEqual(c.db.execute('select count(*) from captures').fetchone()[0],len(self.corpus))
        bad=dict(self.corpus[0]);bad['source']=dict(bad['source'],sha256='0'*64);self.corpus[0]=bad;self.write_corpus();c.db.close();c.lockfile.close()
        c2=self.cyc();r=c2.import_baseline();self.assertEqual(r['errors'],1)
    def test_reobservation_is_snapshot_not_publication(self):
        c=self.cyc();c.import_baseline();p=self.corpus[0];raw=Path(p['source']['raw_path']).read_bytes()
        later=datetime.fromisoformat(p['captured_at'])+timedelta(hours=7)
        self.fake(c,{p['url']:with_reactions(raw,(p['metrics']['reactions']['value'] or 0)+40)},later)
        r=c.capture([p['url']+'/?trk=feed']);self.assertEqual((r['reobservation'],r['new_discovery']),(1,0))
        self.assertEqual(c.posts(),[]);self.assertEqual((c.root/'data/new-posts.ndjson').read_text(),'')
        q=c.qualify();v=next(x for x in json.loads((c.root/'data/velocity.json').read_text()) if x['post_id']==p['id'])
        self.assertTrue(v['eligible']);self.assertEqual(v['reaction_delta'],40);self.assertAlmostEqual(v['span_hours'],7,places=1)
        kinds=[s['capture_kind'] for s in json.loads((c.root/'data/snapshots.json').read_text()) if s['post_id']==p['id']]
        self.assertEqual(sorted(kinds),['baseline_import','reobservation'])
    def test_prior_run_reobservations_carry_into_new_store(self):
        c=self.cyc();c.import_baseline();p=self.corpus[0];raw=Path(p['source']['raw_path']).read_bytes()
        self.fake(c,{p['url']:with_reactions(raw,(p['metrics']['reactions']['value'] or 0)+7)},datetime.fromisoformat(p['captured_at'])+timedelta(hours=9));c.capture([p['url']]);c.qualify()
        c.db.close();c.lockfile.close();snaps=c.root/'data/snapshots.json'
        cfg=dict(self.cfg,run_root=str(self.tmp/'run2'),corpus_snapshots=[str(snaps)]);p2=self.tmp/'config2.json';p2.write_text(json.dumps(cfg))
        c2=cycle.Cycle(p2);r=c2.import_baseline();self.assertEqual((r['prior_reobservations'],r['errors']),(1,0));c2.import_baseline()
        self.assertEqual(c2.db.execute('select count(*) from captures where post_id=?',(p['id'],)).fetchone()[0],2)
        c2.qualify();v=next(x for x in json.loads((c2.root/'data/velocity.json').read_text()) if x['post_id']==p['id'])
        self.assertTrue(v['eligible']);self.assertEqual(v['reaction_delta'],7);c2.lockfile.close()
    def test_span_below_policy_is_not_velocity(self):
        c=self.cyc();c.import_baseline();p=self.corpus[1];raw=Path(p['source']['raw_path']).read_bytes()
        self.fake(c,{p['url']:with_reactions(raw,999999)},datetime.fromisoformat(p['captured_at'])+timedelta(hours=2));c.capture([p['url']]);c.qualify()
        v=next(x for x in json.loads((c.root/'data/velocity.json').read_text()) if x['post_id']==p['id'])
        self.assertFalse(v['eligible']);self.assertEqual(v['reason'],'span_below_min');self.assertIsNone(v['reactions_per_hour'])
    def test_duplicate_text_under_other_activity_rejected(self):
        c=self.cyc();c.import_baseline();p=self.corpus[2];old=p['id'].split(':')[-1];new='7999999999999999999'
        raw=Path(p['source']['raw_path']).read_bytes().replace(old.encode(),new.encode());url=p['url'].replace(old,new)
        self.fake(c,{url:raw},datetime.now(timezone.utc));r=c.capture([url])
        self.assertEqual(r['new_discovery'],0);err=json.loads((c.root/'operations/capture-result.json').read_text())['errors'][0]['error']
        self.assertIn('Duplicate',err)
    def test_unapproved_new_author_held_before_media(self):
        c=self.cyc();c.import_baseline();p=V2POSTS[0];raw=Path(p['source']['raw_path']).read_bytes()
        self.fake(c,{p['url']:raw},datetime.now(timezone.utc));r=c.capture([p['url']]);self.assertEqual(r['new_discovery'],1)
        self.calls.clear();m=c.media();self.assertEqual(m['held_new_author_posts'],1);self.assertEqual(self.calls,[])
        held=json.loads((c.root/'operations/account-qualification-queue.json').read_text());self.assertEqual(held[0]['media_downloaded'],False)
        self.assertEqual(c.queue()['state'],'AWAITING_ACCOUNT_QUALIFICATION')

class Dates(Base):
    def test_date_status(self):
        cap='2026-10-22T10:00:00+00:00'
        self.assertEqual(cycle.date_status(None,cap),'date_missing');self.assertEqual(cycle.date_status('22/10/2026',cap),'date_malformed')
        self.assertEqual(cycle.date_status('2026-10-25T00:00:00Z',cap),'future_date_hold');self.assertEqual(cycle.date_status('2026-10-21T00:00:00Z',cap),'verified_source_date')
    def test_conflicting_dates_hold(self):
        c=self.cyc();c.import_baseline();p=self.corpus[3];raw=Path(p['source']['raw_path']).read_bytes()
        rec=normalizer.parse_post(p['source']['raw_path'],p['url'],iso(datetime.fromisoformat(p['captured_at'])+timedelta(hours=8)));rec['published_at']='2020-01-01T00:00:00Z'
        c.store_capture(rec,raw,'reobservation','test');c.qualify()
        v=next(x for x in json.loads((c.root/'data/velocity.json').read_text()) if x['post_id']==p['id'])
        self.assertEqual(v['publication_date_status'],'date_conflict_hold');self.assertIsNone(v['age_days_at_first_capture']);self.assertEqual(v['cohort'].split('|')[0],'age_unknown')
    def test_comment_dates_never_substituted(self):
        p=normalizer.parse_post(self.corpus[0]['source']['raw_path'],self.corpus[0]['url'],self.corpus[0]['captured_at'])
        self.assertEqual(p['published_at'],self.corpus[0]['published_at'])  # JSON-LD datePublished/uploadDate only

class Access(Base):
    def test_stop_persists_and_blocks_future_requests(self):
        c=self.cyc();c.import_baseline();urls=[p['url'] for p in self.corpus[:4]]
        self.fake(c,{},datetime.now(timezone.utc));r=c.capture(urls)
        self.assertEqual(r['state'],'ACCESS_STOPPED');self.assertEqual(len(self.calls),2);self.assertEqual(r['deferred'],4)  # 429 URLs are re-deferred, not lost
        self.assertTrue((c.root/'operations/access-stop.json').exists());self.calls.clear()
        r2=c.capture(urls);self.assertEqual(self.calls,[]);self.assertEqual(r2['state'],'ACCESS_STOPPED')
        self.assertEqual(c.queue()['state'],'ACCESS_STOPPED')
    def test_deferred_queue_survives_later_capture_and_resumes(self):
        c=self.cyc();c.import_baseline();urls=[p['url'] for p in self.corpus[:4]];raws={p['url']:Path(p['source']['raw_path']).read_bytes() for p in self.corpus}
        self.fake(c,{},datetime.now(timezone.utc));c.capture(urls)
        deferred=json.loads((c.root/'operations/deferred-capture-queue.json').read_text());self.assertEqual(deferred,urls)
        (c.root/'operations/access-stop.json').unlink();self.fake(c,raws,datetime.now(timezone.utc))
        c.capture([self.corpus[5]['url']]);self.assertEqual(json.loads((c.root/'operations/deferred-capture-queue.json').read_text()),urls)
        self.calls.clear();r=c.resume();self.assertEqual(sorted(self.calls),sorted(urls));self.assertEqual(r['reobservation'],4)
        self.assertEqual(json.loads((c.root/'operations/deferred-capture-queue.json').read_text()),[])
    def test_auth_wall_final_url_stops(self):
        c=self.cyc()
        class Resp:
            url='https://www.linkedin.com/authwall?trk=x';status=200;headers={'Content-Type':'text/html'}
            def read(self,n):return b'<html>sign in</html>'
            def __enter__(self):return self
            def __exit__(self,*a):return False
        class Opener:
            def open(self,req,timeout=None):return Resp()
        orig=urllib.request.build_opener;urllib.request.build_opener=lambda *a:Opener()
        try:r,b=c.get('https://www.linkedin.com/posts/x_y-activity-7400000000000000000-abcd')
        finally:urllib.request.build_opener=orig
        self.assertIsNone(b);self.assertEqual(r['status'],'stopped');self.assertEqual(r['error'],'auth_or_challenge_page')
    def test_lock_prevents_overlap(self):
        c=self.cyc()
        with self.assertRaises(cycle.Locked):cycle.Cycle(self.cfgp)
        c.lockfile.close();c2=self.cyc();self.assertIsNotNone(c2)
    def test_refresh_requests_only_due_posts(self):
        c=self.cyc();c.import_baseline();self.fake(c,{},datetime.now(timezone.utc))
        r=c.refresh();due_expected=sum((datetime.now(timezone.utc)-datetime.fromisoformat(p['captured_at'])).total_seconds()>=6*3600 for p in self.corpus)
        self.assertEqual(r['due'],due_expected);self.assertEqual(r['requested_urls'],min(due_expected,self.cfg['refresh']['max_urls']))
        if not due_expected:self.assertEqual(self.calls,[]);self.assertIsNotNone(r['next_due_at'])
    def test_refresh_due_post_is_requested_and_not_due_is_not(self):
        old=self.corpus[0];self.corpus[0]=dict(old,captured_at=iso(datetime.now(timezone.utc)-timedelta(hours=10)));self.write_corpus()
        fresh=self.corpus[1];self.corpus[1]=dict(fresh,captured_at=iso(datetime.now(timezone.utc)-timedelta(hours=1)));self.write_corpus()
        c=self.cyc();c.import_baseline();raw=Path(old['source']['raw_path']).read_bytes()
        self.fake(c,{old['url']:with_reactions(raw,123456)},datetime.now(timezone.utc));r=c.refresh()
        self.assertIn(old['url'],self.calls);self.assertNotIn(fresh['url'],self.calls);self.assertGreaterEqual(r['due'],1)
        self.assertEqual((r['due'],r['result']['reobservation']),(1,1))
        v=next(x for x in (c.qualify() and json.loads((c.root/'data/velocity.json').read_text())) if x['post_id']==old['id'])
        self.assertTrue(v['eligible']);self.assertEqual(v['reactions_last'],123456)

class Discovery(Base):
    def test_exposed_links_exclude_known_and_classify_author(self):
        c=self.cyc();c.import_baseline();cands=c.exposed_links();known={p['id'] for p in self.corpus}
        self.assertTrue(cands);self.assertTrue(all('urn:li:activity:'+cycle.activity(x['url']) not in known for x in cands))
        same=[x for x in cands if x['source']=='exposed_same_author'];self.assertTrue(same)
        self.assertTrue(all(x['author_slug_from_url']=='synthetic-link-author' for x in same if x['source_page_post_id']==LINKED))
        self.assertTrue(all(x['order_hint_is_not_date_evidence'] for x in cands));self.assertEqual(len({x['url'] for x in cands}),len(cands))

class Queue(Base):
    def video_state(self,c,tx_hash=None,review=False):
        v={'post_id':'urn:li:activity:1','asset_id':'a:video:0','kind':'video','status':'acquired','path':'media/objects/x.mp4','sha256':'f'*64,'ffprobe':{'streams':[{'codec_type':'video'},{'codec_type':'audio'}]}}
        cycle.dump(c.root/'data/media-manifest.json',[v]);t=c.root/'transcripts/a.json'
        cycle.dump(t,{'asset_id':v['asset_id'],'source_video_sha256':tx_hash or v['sha256'],'review_status':'transcript_available_not_audio_verified','text':'hello'})
        cycle.dump(c.root/'transcripts/index.json',[{'asset_id':v['asset_id'],'post_id':v['post_id'],'path':'transcripts/a.json','source_video_sha256':tx_hash or v['sha256']}])
        cycle.dump(c.root/'analysis/media-reviews.json',[{'asset_id':v['asset_id'],'source_sha256':v['sha256'],'review_status':'reviewed'}] if review else [])
        return c.queue()['state']
    def test_no_false_ready(self):
        c=self.cyc();c.import_baseline()
        self.assertEqual(self.video_state(c,tx_hash='e'*64),'TRANSCRIPTION_PENDING')  # stale transcript for another file
        self.assertEqual(self.video_state(c),'AWAITING_SUPERVISOR_REVIEW')
        self.assertEqual(self.video_state(c,review=True),'AWAITING_SUPERVISOR_REVIEW')  # mechanical QA is required before READY
        cycle.dump(c.root/'data/transcript-qa.json',[{'asset_id':'a:video:0','post_id':'urn:li:activity:1','status':'flagged','flags':['repeated_tail']}])
        self.assertEqual(c.queue()['state'],'AWAITING_SUPERVISOR_REVIEW')
    def test_media_cache_not_reused_after_source_change(self):
        c=self.cyc();p=V3POSTS[0];raw=Path(p['source']['raw_path']).read_bytes();self.fake(c,{p['url']:raw},datetime.now(timezone.utc))
        self.corpus=[];self.write_corpus();c._corpus=[]
        c.capture([p['url']]);post=c.posts()[0];imgs=[m for m in post['media'] if m['type']=='image']
        if not imgs:self.skipTest('fixture post has no image')
        stale={'asset_id':imgs[0]['id'],'post_id':post['id'],'kind':'image','url':imgs[0]['url'],'source_capture_sha256':'0'*64,'status':'acquired','path':'media/objects/old.jpg','sha256':'1'*64}
        cycle.dump(c.root/'data/media-manifest.json',[stale]);self.calls.clear();c.media();self.assertIn(imgs[0]['url'],self.calls)

class ReviewFixes(Base):
    def test_auth_wall_url_blocked_not_retried_and_queue_stays_stopped(self):
        c=self.cyc();c.import_baseline();u=self.corpus[0]['url']
        def get(url,kind='page',probe=False):
            self.calls.append(url);r={'url':url,'captured_at':cycle.now(),'kind':kind,'status':'stopped','error':'auth_or_challenge_page','http_status':200,'final_url':'https://www.linkedin.com/signup/cold-join'};return r,None
        c.get=get;r=c.capture([u]);self.assertEqual(r['deferred'],0)
        self.assertIn(u,json.loads((c.root/'operations/blocked-urls.json').read_text()));self.assertEqual(c.queue()['state'],'ACCESS_STOPPED')
        (c.root/'operations/access-stop.json').unlink();self.calls.clear();c.capture([u]);self.assertEqual(self.calls,[])  # blocked URL never auto-retried
    def test_get_refuses_during_stop_unless_probe(self):
        c=self.cyc();cycle.dump(c.root/'operations/access-stop.json',{'stopped_at':cycle.now(),'reason':'test'})
        r,b=c.get('https://www.linkedin.com/posts/x_y-activity-7400000000000000000-abcd');self.assertEqual((r['status'],b,c.requests_made),('refused_access_stop',None,0))
    def test_media_cache_survives_stop_and_off_host_url_does_not_abort(self):
        c=self.cyc();p=V3POSTS[0];raw=Path(p['source']['raw_path']).read_bytes();self.corpus=[];self.write_corpus();c._corpus=[]
        self.fake(c,{p['url']:raw},datetime.now(timezone.utc));c.capture([p['url']]);post=c.posts()[0];imgs=[m for m in post['media'] if m['type']=='image']
        if not imgs:self.skipTest('fixture post has no image')
        f=c.root/'media/objects/a.jpg';f.write_bytes(b'img');good={'asset_id':imgs[0]['id'],'post_id':post['id'],'kind':'image','url':imgs[0]['url'],'source_capture_sha256':post['source']['sha256'],'status':'acquired','path':'media/objects/a.jpg','sha256':cycle.sha(b'img')}
        cycle.dump(c.root/'data/media-manifest.json',[good]);cycle.dump(c.root/'operations/access-stop.json',{'stopped_at':cycle.now(),'reason':'test'})
        c.media();m={a['asset_id']:a for a in json.loads((c.root/'data/media-manifest.json').read_text())};self.assertEqual(m[good['asset_id']]['status'],'acquired')
        (c.root/'operations/access-stop.json').unlink();post['media'][0]=dict(imgs[0],url='https://evil.example.com/x.jpg');c.db.execute('UPDATE posts SET payload=? WHERE id=?',(json.dumps(post),post['id']));c.db.commit()
        fake=c.get;real=cycle.Cycle.get.__get__(c);c.get=lambda url,kind='page',probe=False:real(url,kind) if not (cycle.urlsplit(url).hostname or '').endswith('licdn.com') else fake(url,kind)
        cycle.dump(c.root/'data/media-manifest.json',[]);out=c.media();self.assertTrue(any(a['status']=='failed' for a in json.loads((c.root/'data/media-manifest.json').read_text())))
    def test_rotation_advances_only_by_executed_author_queries(self):
        c=self.cyc();c.import_baseline();n=[0]
        def exa(q,k):n[0]+=1;return {'query':q,'raw_sha256':'x','matching_post_urls':[],'limited_or_failed':n[0]==1}
        c.exa=exa;c.discover();st=json.loads((c.root/'operations/discovery-state.json').read_text());self.assertEqual((st['author_rotation_index'],st['last_rotation']),(0,[]))
    def test_unknown_age_and_small_cohorts_not_ranked(self):
        c=self.cyc();c.cfg['qualification']['same_cohort_min_posts']=1;c.import_baseline()
        for i,p in enumerate(self.corpus[:2]):
            rec=normalizer.parse_post(p['source']['raw_path'],p['url'],cycle.iso(datetime.fromisoformat(p['captured_at'])+timedelta(hours=8))) if hasattr(cycle,'iso') else normalizer.parse_post(p['source']['raw_path'],p['url'],(datetime.fromisoformat(p['captured_at'])+timedelta(hours=8)).isoformat())
            if i==0:rec['published_at']='bad-date'
            c.store_capture(rec,Path(p['source']['raw_path']).read_bytes(),'reobservation','test')
        c.qualify();rows={r['cohort']:r for r in json.loads((c.root/'data/cohorts.json').read_text())}
        unk=[r for k,r in rows.items() if k.startswith('age_unknown')];self.assertTrue(unk);self.assertTrue(all(not r['ranked'] and r['median_reactions_per_hour'] is None for r in unk))
        self.assertTrue(all(not r['ranked'] for k,r in rows.items() if not k.startswith('age_unknown')))  # all zero/tied growth is not a meaningful rank
    def test_repeated_failures_skipped_by_refresh(self):
        old=self.corpus[0];self.corpus[0]=dict(old,captured_at=iso(datetime.now(timezone.utc)-timedelta(hours=10)));self.write_corpus()
        c=self.cyc();c.import_baseline();self.fake(c,{old['url']:b'<html>no article</html>'},datetime.now(timezone.utc))
        c.refresh();c.refresh();self.calls.clear();r=c.refresh();self.assertNotIn(old['url'],self.calls);self.assertEqual(r['skipped_failures_or_blocked'],1)

class RereviewFixes(Base):
    def test_refresh_drops_blocked_before_slice(self):
        old=[dict(p,captured_at=iso(datetime.now(timezone.utc)-timedelta(hours=10))) for p in self.corpus];self.corpus=old;self.write_corpus()
        cfg=dict(self.cfg);cfg['refresh']=dict(cfg['refresh'],max_urls=1);self.cfgp.write_text(json.dumps(cfg))
        c=self.cyc();c.import_baseline();cycle.dump(c.root/'operations/blocked-urls.json',{old[0]['url']:{'reason':'x'}} if sorted(p['url'] for p in old)[0]==old[0]['url'] else {u:{'reason':'x'} for u in [sorted(p['url'] for p in old)[0]]})
        self.fake(c,{p['url']:Path(p['source']['raw_path']).read_bytes() for p in old},datetime.now(timezone.utc));r=c.refresh()
        self.assertEqual(r['requested_urls'],1);self.assertEqual(len(self.calls),1);self.assertNotIn(list(json.loads((c.root/'operations/blocked-urls.json').read_text()))[0],self.calls)
    def test_unresolved_blocked_url_keeps_collection_partial(self):
        c=self.cyc();c.import_baseline();cycle.dump(c.root/'operations/blocked-urls.json',{'https://www.linkedin.com/posts/x':{'reason':'auth_or_challenge_page'}})
        self.assertEqual(c.queue()['state'],'COLLECTION_PARTIAL')
        cycle.dump(c.root/'operations/blocked-urls.json',{'https://www.linkedin.com/posts/x':{'reason':'auth_or_challenge_page','resolution':'accepted_gap'}})
        self.assertNotEqual(c.queue()['state'],'COLLECTION_PARTIAL')
    def test_failed_author_query_does_not_advance_rotation(self):
        c=self.cyc();c.import_baseline();n=[0]
        def exa(q,k):n[0]+=1;return {'query':q,'raw_sha256':'x','matching_post_urls':[],'limited_or_failed':n[0]==5}
        c.exa=exa;c.discover();st=json.loads((c.root/'operations/discovery-state.json').read_text());self.assertEqual(st['author_rotation_index'],0)
    def test_missing_snapshot_file_is_recorded(self):
        cfg=dict(self.cfg,corpus_snapshots=[str(self.tmp/'missing.json')]);self.cfgp.write_text(json.dumps(cfg))
        c=self.cyc();r=c.import_baseline();self.assertEqual(r['errors'],1);self.assertTrue((c.root/'operations/baseline-import.json').exists())
    def test_capture_skips_repeatedly_failing_candidate(self):
        c=self.cyc();u='https://www.linkedin.com/posts/x_y-activity-7400000000000000001-abcd';cycle.dump(c.root/'operations/capture-failures.json',{u:{'count':2}})
        self.fake(c,{},datetime.now(timezone.utc));c.capture([u]);self.assertEqual(self.calls,[])


class V5Repairs(Base):
    def test_synthetic_guest_layout_fixtures_have_only_target_counters(self):
        inv=GUEST_FIXTURES
        expected={str(7100000000000000000+i):v for i,v in enumerate([(57,27,1),(233,53,2),(95,28,1),(26,None,None),(325,26,7)])}
        for item in inv[:5]:
            p=normalizer.validate_record(normalizer.parse_post(item['path'],item['url'],'2026-10-22T10:00:00+00:00'))
            self.assertEqual(tuple(p['metrics'][k]['value'] for k in ['reactions','comments','reposts']),expected[p['id'].split(':')[-1]])
            self.assertEqual(p['source']['layout'],'guest_component');self.assertGreater(len(p['text']),60)
        with self.assertRaises(ValueError):normalizer.parse_post(inv[5]['path'],inv[5]['url'],'2026-10-22T10:00:00+00:00')
    def test_guest_layout_rejects_wrong_target_and_missing_actor(self):
        inv=GUEST_FIXTURES[0];raw=Path(inv['path']).read_bytes();f=self.tmp/'guest.html'
        f.write_bytes(raw.replace(b'7100000000000000000',b'7999999999999999999'))
        with self.assertRaises(ValueError):normalizer.parse_post(f,inv['url'],'2026-10-22T10:00:00+00:00')
        soup=cycle.BeautifulSoup(raw,'html.parser');a=soup.select_one('[componentkey^="update-card-focus"]')
        for node in a.select('a[href]'):
            if '/in/synthetic-guest-0' in node['href']:node['href']='https://www.linkedin.com/in/wrong-actor/'
        f.write_text(str(soup))
        with self.assertRaises(ValueError):normalizer.parse_post(f,inv['url'],'2026-10-22T10:00:00+00:00')
    def test_three_consecutive_unsupported200_pages_persistently_stop(self):
        c=self.cyc();c.cfg['capture']['workers']=1;urls=[p['url'] for p in self.corpus[:5]];self.fake(c,{u:b'<html>not supported</html>' for u in urls},datetime.now(timezone.utc))
        result=c.capture(urls);self.assertEqual(len(self.calls),3);self.assertEqual(result['state'],'ACCESS_STOPPED');self.assertEqual(result['deferred'],2)
        self.assertEqual(json.loads((c.root/'operations/access-stop.json').read_text())['reason'],'consecutive_200_without_supported_post')
        self.calls.clear();c.capture(urls);self.assertEqual(self.calls,[])
    def test_valid_page_resets_consecutive200_failures_across_calls(self):
        c=self.cyc();c.cfg['capture']['workers']=1;bad=[p['url'] for p in self.corpus[:2]];good=self.corpus[2]
        self.fake(c,{**{u:b'<html>not supported</html>' for u in bad},good['url']:Path(good['source']['raw_path']).read_bytes()},datetime.now(timezone.utc))
        c.capture(bad+[good['url']]);self.assertIsNone(c.access_stop());self.assertEqual(json.loads((c.root/'operations/layout-health.json').read_text())['consecutive_unparseable_200'],0)
    def test_four_megabyte_cap_accepts_three_megabyte_page(self):
        c=self.cyc();self.assertEqual(c.cfg['capture']['max_html_bytes'],4000000)
        class Resp:
            status=200;url=self.corpus[0]['url'];headers={'Content-Type':'text/html'}
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def read(self,n):return b'x'*3000000
        class Opener:
            def open(self,*args,**kwargs):return Resp()
        original=cycle.urllib.request.build_opener;cycle.urllib.request.build_opener=lambda *a,**kw:Opener()
        try:r,b=c.get(self.corpus[0]['url']);self.assertEqual(r['status'],'acquired');self.assertEqual(len(b),3000000)
        finally:cycle.urllib.request.build_opener=original
    def test_prior_media_selection_requires_known_ids_and_watchlist(self):
        c=self.cyc();p=next(p for p in self.corpus if any(m['type']=='image' for m in p['media']));c.cfg['media']['prior_post_ids']=[p['id']]
        c.cfg['collection_approval']['approved_author_paths']=[];c.get=lambda *a,**kw:self.fail('unapproved prior asset fetch')
        self.assertEqual(c.media()['held_new_author_posts'],1);self.assertEqual(c.posts(),[])
        c.cfg['collection_approval']['approved_author_paths']=[cycle.urlsplit(p['author']['url']).path.rstrip('/').lower()];calls=[]
        def fake_media(url,kind='media'):
            calls.append(url);b=b'\x89PNG'+b'fixture';return {'status':'acquired','http_status':200,'captured_at':cycle.now(),'rights':'research'},b
        c.get=fake_media;self.assertGreater(c.media()['acquired'],0);self.assertTrue(calls);self.assertEqual(c.posts(),[])
        source=[json.loads(x) for x in (c.root/'data/media-source-posts.ndjson').read_text().splitlines()];self.assertEqual([x['id'] for x in source],[p['id']])
        c.cfg['media']['prior_post_ids']=['urn:li:activity:unknown']
        with self.assertRaises(ValueError):c.media()
    def test_qa_stage_flags_hash_bound_record_and_keeps_original(self):
        c=self.cyc();v={'post_id':'urn:li:activity:1','asset_id':'a:video:0','kind':'video','status':'acquired','path':'media/objects/x.mp4','sha256':'f'*64,'ffprobe':{'streams':[{'codec_type':'video'},{'codec_type':'audio'}],'format':{'duration':'2'}}}
        cycle.dump(c.root/'data/media-manifest.json',[v]);t=c.root/'transcripts/a.json'
        cycle.dump(t,{'asset_id':v['asset_id'],'source_video_sha256':v['sha256'],'origin':'local_whisper_ASR','review_status':'transcript_available_not_audio_verified','text':'repeat again repeat again repeat again','segments':[{'start':0,'end':4,'text':'repeat again'},{'start':4,'end':5,'text':'repeat again'},{'start':5,'end':6,'text':'repeat again'}]})
        before=t.read_bytes();cycle.dump(c.root/'transcripts/index.json',[{'asset_id':v['asset_id'],'post_id':v['post_id'],'path':'transcripts/a.json','source_video_sha256':v['sha256'],'origin':'local_whisper_ASR'}]);result=c.transcript_qa()
        self.assertEqual(result['records'],1);qa=json.loads((c.root/'data/transcript-qa.json').read_text())['records'][0]
        self.assertEqual(qa['status'],'flagged');self.assertEqual(qa['source_video_sha256'],v['sha256']);self.assertEqual(qa['transcript_sha256'],cycle.sha(before));self.assertEqual(t.read_bytes(),before)
    def test_same_zero_velocity_values_are_not_ranked(self):
        c=self.cyc();c.cfg['qualification']['same_cohort_min_posts']=1;c.import_baseline();p=self.corpus[0];rec=normalizer.parse_post(p['source']['raw_path'],p['url'],(datetime.fromisoformat(p['captured_at'])+timedelta(hours=8)).isoformat());c.store_capture(rec,Path(p['source']['raw_path']).read_bytes(),'reobservation','test');c.qualify()
        cohort=next(x for x in json.loads((c.root/'data/cohorts.json').read_text()) if p['id'] in x['members']);self.assertFalse(cohort['ranked']);self.assertEqual(cohort['not_ranked_reason'],'all_tied_or_no_positive_growth')
    def test_counter_decrease_is_observed_but_excluded_from_rank(self):
        c=self.cyc();c.cfg['qualification']['same_cohort_min_posts']=1;c.import_baseline();p=self.corpus[0];rec=normalizer.parse_post(p['source']['raw_path'],p['url'],(datetime.fromisoformat(p['captured_at'])+timedelta(hours=8)).isoformat());rec['metrics']['reactions']['value']=0;c.store_capture(rec,Path(p['source']['raw_path']).read_bytes(),'reobservation','test');c.qualify()
        v=next(x for x in json.loads((c.root/'data/velocity.json').read_text()) if x['post_id']==p['id']);self.assertTrue(v['eligible']);self.assertTrue(v['counter_decreased']);cohort=next(x for x in json.loads((c.root/'data/cohorts.json').read_text()) if p['id'] in x['excluded_counter_decrease_members']);self.assertEqual(cohort['n'],0)


class V5AudioAdjudication(Base):
    def fixture(self,c):
        c.import_baseline();t={'asset_id':'video:flagged','post_id':self.corpus[0]['id'],'source_video_sha256':'a'*64,'transcript_sha256':'b'*64,'status':'flagged','flags':['timing_overrun'],'supervisor_reviewed':True};t['qa_record_sha256']=cycle.qa_record_sha256(t);cycle.dump(c.root/'data/transcript-qa.json',{'records':[t]})
        r={k:t[k] for k in ('asset_id','source_video_sha256','transcript_sha256','qa_record_sha256')};r.update(reviewed_at=cycle.now(),reviewer='source-reviewer',reviewer_type='human',review_status='reviewed',audio_review=True,audio_review_scope='Original audio from 00:00 through00:30; flagged tail checked.',outcome='accepted_with_limitations');return t,r
    def test_standalone_reviewed_boolean_never_releases_flag(self):
        c=self.cyc();t,r=self.fixture(c);self.assertEqual(c.queue()['state'],'AWAITING_SUPERVISOR_REVIEW')
    def test_exact_audio_adjudication_can_release_structural_flag(self):
        c=self.cyc();t,r=self.fixture(c);cycle.dump(c.root/'analysis/transcript-reviews.json',[r]);self.assertEqual(c.queue()['state'],'READY_FOR_VERIFICATION')
    def test_stale_video_transcript_or_qa_hash_never_releases(self):
        c=self.cyc();t,r=self.fixture(c)
        for key in ('asset_id','source_video_sha256','transcript_sha256','qa_record_sha256'):
            bad={**r,key:'stale'};cycle.dump(c.root/'analysis/transcript-reviews.json',[bad]);self.assertEqual(c.queue()['state'],'AWAITING_SUPERVISOR_REVIEW',key)
        changed={**t,'flags':['different_flag']};cycle.dump(c.root/'data/transcript-qa.json',{'records':[changed]});cycle.dump(c.root/'analysis/transcript-reviews.json',[r]);self.assertEqual(c.queue()['state'],'AWAITING_SUPERVISOR_REVIEW')
    def test_missing_reviewer_scope_audio_time_or_error_state_blocks(self):
        c=self.cyc();t,r=self.fixture(c)
        cases=[{'reviewer':'unknown'},{'reviewer':''},{'reviewer_type':'unknown'},{'audio_review':False},{'audio_review_scope':''},{'review_status':'error'},{'reviewed_at':'invalid'},{'reviewed_at':'2099-01-01T00:00:00+00:00'},{'outcome':'rejected'}]
        for changes in cases:
            cycle.dump(c.root/'analysis/transcript-reviews.json',[{**r,**changes}]);self.assertEqual(c.queue()['state'],'AWAITING_SUPERVISOR_REVIEW',changes)

if __name__=='__main__':unittest.main()
