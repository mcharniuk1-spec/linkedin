"""Offline unit tests for pipeline/transcript_qa.py (synthetic fixtures; no network, no model).

Run from this directory:  PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v
"""
import contextlib
import hashlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline"))
import transcript_qa as q  # noqa: E402

NATURAL = ("We started the quarter by rewriting our positioning page, because the old copy talked about features "
           "while buyers kept asking about outcomes. After three weeks of calls with customers we learned that the "
           "real trigger was a failed pilot, not a missing integration. So we changed the headline, rebuilt the demo "
           "around that story, and watched reply rates climb. The lesson is simple: listen first, then write, then "
           "measure what moves.")


def ffprobe(duration=60.0, audio=True, video=True, with_format=True):
    streams = []
    if video:
        streams.append({"codec_type": "video"})
    if audio:
        streams.append({"codec_type": "audio"})
    out = {"streams": streams}
    if with_format:
        out["format"] = {"duration": str(duration) if duration is not None else "N/A"}
    return out


def units(*triples):
    return [{"start": s, "end": e, "text": t} for s, e, t in triples]


def natural_units(end_last=40.0):
    words = NATURAL.split(" ")
    chunk = len(words) // 5 + 1
    parts = [" ".join(words[i:i + chunk]) for i in range(0, len(words), chunk)]
    step = end_last / len(parts)
    return units(*[(round(i * step, 3), round((i + 1) * step, 3), p) for i, p in enumerate(parts)])


def tr(kind="whisper_segments", text=None, us=None, exists=True):
    us = natural_units() if us is None else us
    if text is None:
        text = " ".join(u["text"] for u in us)
    return {"kind": kind, "text": text, "units": us, "exists": exists, "path_rel": "x.json", "error": None if exists else "file_not_found"}


def ev(family="whisper_asr", probe_dict=None, transcript=None, extra=None):
    probe = q.probe_info(ffprobe() if probe_dict is None else probe_dict)
    return q.evaluate(family, probe, transcript or tr(), extra)


class EvaluateTests(unittest.TestCase):
    def test_clean_pass(self):
        res = ev()
        self.assertEqual(res["status"], "pass")
        self.assertEqual(res["flags"], [])
        self.assertEqual(res["details"], {})

    def test_timing_overrun_and_boundary(self):
        res = ev(transcript=tr(us=units((0, 30, NATURAL[:200]), (30, 62.5, NATURAL[200:]))))
        self.assertEqual(res["status"], "flagged")
        self.assertIn("timing_overrun", res["flags"])
        self.assertEqual(res["details"]["timing_overrun"]["overrun_seconds"], 2.5)
        # exactly duration + 1.0 s is tolerated; just above is flagged
        at_limit = ev(transcript=tr(us=units((0, 30, NATURAL[:200]), (30, 61.0, NATURAL[200:]))))
        self.assertEqual(at_limit["status"], "pass")
        above = ev(transcript=tr(us=units((0, 30, NATURAL[:200]), (30, 61.01, NATURAL[200:]))))
        self.assertIn("timing_overrun", above["flags"])

    def test_non_monotonic_and_overlap(self):
        res = ev(transcript=tr(us=units((0, 10, NATURAL[:150]), (9.0, 20, NATURAL[150:300]), (20, 30, NATURAL[300:]))))
        self.assertEqual(res["status"], "flagged")
        self.assertIn("non_monotonic_or_overlap", res["flags"])
        self.assertEqual(res["details"]["non_monotonic_or_overlap"]["examples"][0]["reason"], "starts_before_previous_end")
        tiny = ev(transcript=tr(us=units((0, 10, NATURAL[:150]), (9.96, 20, NATURAL[150:300]), (20, 30, NATURAL[300:]))))
        self.assertNotIn("non_monotonic_or_overlap", tiny["flags"])  # 0.04 s overlap is within tolerance
        backwards = ev(transcript=tr(us=units((0, 10, NATURAL[:150]), (12, 11, NATURAL[150:300]), (12, 30, NATURAL[300:]))))
        self.assertIn("non_monotonic_or_overlap", backwards["flags"])
        self.assertEqual(backwards["details"]["non_monotonic_or_overlap"]["examples"][0]["reason"], "end_before_start")

    def test_repeated_tail_identical_segments(self):
        base = natural_units(30.0)
        tail = units((30, 32, "You"), (32, 34, "you."), (34, 36, "You!"))
        res = ev(transcript=tr(us=base + tail))
        self.assertEqual(res["status"], "flagged")
        self.assertIn("repeated_tail", res["flags"])
        self.assertEqual(res["details"]["repeated_tail"]["identical_tail_segments"]["identical_trailing_segments"], 3)
        self.assertLessEqual(len(res["details"]["repeated_tail"]["excerpt"]), 80)
        two = ev(transcript=tr(us=base + tail[:2]))
        self.assertNotIn("repeated_tail", two["flags"])

    def test_repeated_tail_ngram_and_excerpt_limit(self):
        loop = "we need to be there " * 4
        us = natural_units(30.0) + units((30, 40, loop))
        res = ev(transcript=tr(us=us))
        self.assertIn("repeated_tail", res["flags"])
        info = res["details"]["repeated_tail"]
        self.assertIn("repeated_ngram", info)
        self.assertNotIn("identical_tail_segments", info)
        self.assertGreaterEqual(info["repeated_ngram"]["tail_coverage"], 0.4)
        self.assertGreaterEqual(info["repeated_ngram"]["ngram_tokens"], 4)
        long_loop = ("alpha bravo charlie delta echo foxtrot golf hotel india juliet kilo lima mike november oscar papa "
                     "quebec romeo sierra tango uniform victor whiskey xray yankee zulu ") * 3
        res2 = ev(transcript=tr(us=natural_units(30.0) + units((30, 40, long_loop))))
        self.assertIn("repeated_tail", res2["flags"])
        self.assertLessEqual(len(res2["details"]["repeated_tail"]["excerpt"]), 80)
        self.assertNotIn("repeated_tail", ev()["flags"])  # natural text does not trigger

    def test_high_compression(self):
        words = "the same words again " * 80
        res = ev(transcript=tr(us=units((0, 40, words))))
        self.assertIn("high_compression", res["flags"])
        self.assertGreater(res["details"]["high_compression"]["ratio"], 2.4)
        self.assertNotIn("high_compression", ev()["flags"])

    def test_caption_vs_duration_and_tolerance(self):
        cues = units((0.1, 20, NATURAL[:200]), (20, 62.5, NATURAL[200:]))
        res = ev(family="captions", transcript=tr(kind="caption_cues", us=cues))
        self.assertEqual(res["status"], "flagged")
        self.assertIn("caption_vs_duration", res["flags"])
        self.assertNotIn("timing_overrun", res["flags"])
        ok = ev(family="captions", transcript=tr(kind="caption_cues", us=units((0.1, 20, NATURAL[:200]), (20, 60.9, NATURAL[200:]))))
        self.assertEqual(ok["status"], "pass")

    def test_timing_unavailable_is_never_pass(self):
        cap = ev(family="captions", transcript=tr(kind="text_only", us=[], text=NATURAL))
        self.assertEqual(cap["status"], "flagged")
        self.assertIn("timing_unavailable", cap["flags"])
        asr = ev(transcript=tr(kind="text_only", us=[], text=NATURAL))
        self.assertIn("timing_unavailable", asr["flags"])

    def test_empty_text_with_audio_is_missing_transcript(self):
        res = ev(transcript=tr(kind="text_only", us=[], text=""))
        self.assertEqual(res["status"], "missing_transcript")
        self.assertIn("empty_text_with_audio", res["flags"])

    def test_known_no_audio_is_not_applicable(self):
        res = ev(family="no_audio", probe_dict=ffprobe(audio=False), transcript=tr(kind="text_only", us=[], text=""))
        self.assertEqual(res["status"], "not_applicable_no_audio")
        self.assertEqual(res["flags"], [])

    def test_no_audio_origin_but_audio_stream_present(self):
        res = ev(family="no_audio", probe_dict=ffprobe(audio=True), transcript=tr(kind="text_only", us=[], text=NATURAL))
        self.assertEqual(res["status"], "flagged")
        self.assertIn("origin_audio_mismatch", res["flags"])
        empty = ev(family="no_audio", probe_dict=ffprobe(audio=True), transcript=tr(kind="text_only", us=[], text=""))
        self.assertEqual(empty["status"], "missing_transcript")  # audio exists, nothing transcribed

    def test_speech_text_without_audio_stream_is_flagged(self):
        res = ev(family="whisper_asr", probe_dict=ffprobe(audio=False))
        self.assertEqual(res["status"], "flagged")
        self.assertIn("origin_audio_mismatch", res["flags"])

    def test_unknown_probe_is_blocked_never_silence(self):
        for bad in (None, {}, {"streams": []}, {"streams": [{"codec_type": "audio"}]}, "garbage"):
            probe = q.probe_info(bad)
            self.assertFalse(probe["ok"])
            for text in ("", NATURAL):
                us = [] if not text else natural_units()
                res = q.evaluate("whisper_asr", probe, tr(kind="whisper_segments" if us else "text_only", us=us, text=text))
                self.assertEqual(res["status"], "blocked_unknown_probe", bad)
                self.assertNotIn(res["status"], ("pass", "not_applicable_no_audio"))
        res = q.evaluate("probe_unavailable", q.probe_info(None), tr(kind="text_only", us=[], text=""))
        self.assertEqual(res["status"], "blocked_unknown_probe")
        # a known no-audio origin with an unknown probe must not be accepted as silence
        res = q.evaluate("no_audio", q.probe_info(None), tr(kind="text_only", us=[], text=""))
        self.assertEqual(res["status"], "blocked_unknown_probe")

    def test_duration_unknown_is_not_pass(self):
        for fp in (ffprobe(with_format=False), ffprobe(duration=None), ffprobe(duration=0), ffprobe(duration=-3),
                   {"streams": [{"codec_type": "video"}, {"codec_type": "audio"}], "format": {"duration": "nan"}}):
            res = ev(probe_dict=fp)
            self.assertEqual(res["status"], "duration_unknown", fp)
            self.assertIn("duration_unknown", res["flags"])
        self.assertIsNone(q.probe_info(ffprobe(with_format=False))["duration"])
        # other findings outrank duration_unknown but the flag stays visible
        bad = ev(probe_dict=ffprobe(with_format=False), transcript=tr(us=natural_units(30.0) + units((30, 32, "You"), (32, 34, "You"), (34, 36, "You"))))
        self.assertEqual(bad["status"], "flagged")
        self.assertIn("duration_unknown", bad["flags"])
        self.assertIn("repeated_tail", bad["flags"])
        self.assertNotIn("timing_overrun", bad["flags"])

    def test_missing_transcript_file(self):
        res = ev(transcript=tr(kind="none", us=[], text="", exists=False))
        self.assertEqual(res["status"], "missing_transcript")
        self.assertIn("transcript_file_missing", res["flags"])
        self.assertNotIn("empty_text_with_audio", res["flags"])

    def test_origin_family(self):
        cases = {"local_whisper_ASR": "whisper_asr", "local_cached_whisper_ASR": "whisper_asr",
                 "platform_captions": "captions", "public_platform_captions": "captions",
                 "no_audio_stream_in_acquired_file": "no_audio", "audio_probe_unavailable": "probe_unavailable",
                 "public_page_transcript": "page_text", None: "other"}
        for origin, fam in cases.items():
            self.assertEqual(q.origin_family(origin), fam, origin)


class ParsingTests(unittest.TestCase):
    def test_srt_and_vtt(self):
        srt = "1\n00:00:00,080 --> 00:00:01,370\nMorning.\n\n2\n00:00:01,370 --> 00:00:04,648\nline <i>one</i>\nline two\n"
        cues, bad = q.parse_cues(srt)
        self.assertEqual(bad, 0)
        self.assertEqual(len(cues), 2)
        self.assertAlmostEqual(cues[1]["end"], 4.648)
        self.assertEqual(cues[1]["text"], "line one line two")
        vtt = "WEBVTT\n\nNOTE x\n\n00:00.500 --> 00:02.000 align:start\nHi there\n\n01:00:00.000 --> 01:00:01.250\nLate\n\n00:xx --> 00:03.000\nbroken\n"
        cues, bad = q.parse_cues(vtt)
        self.assertEqual(len(cues), 2)
        self.assertEqual(bad, 1)
        self.assertAlmostEqual(cues[0]["start"], 0.5)
        self.assertAlmostEqual(cues[1]["start"], 3600.0)

    def test_tokens_and_excerpt(self):
        self.assertEqual(q.normalize("You’re HERE, again!"), "you're here again")
        self.assertEqual(q.normalize("You."), q.normalize("you!"))
        self.assertLessEqual(len(q.excerpt("x " * 200)), 80)
        self.assertEqual(q.excerpt("short  text"), "short text")


class FixtureRun(unittest.TestCase):
    """End-to-end run on a synthetic multi-run directory layout."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        base = Path(self._tmp.name)
        self.v3, self.v2, self.v4 = base / "runs/v3", base / "runs/v2", base / "runs/v4"
        for d in (self.v3 / "transcripts", self.v3 / "data", self.v3 / "media/objects", self.v2 / "media", self.v4 / "data"):
            d.mkdir(parents=True)
        segs_ok = [{"id": i, "start": u["start"], "end": u["end"], "text": u["text"]} for i, u in enumerate(natural_units(40.0))]
        segs_bad = [{"id": i, "start": u["start"], "end": u["end"], "text": u["text"]} for i, u in enumerate(natural_units(30.0))]
        segs_bad += [{"id": 90, "start": 30, "end": 34, "text": "We need to be there."}, {"id": 91, "start": 34, "end": 38, "text": "We need to be there."},
                     {"id": 92, "start": 38, "end": 45, "text": "We need to be there."}]
        write = lambda p, o: p.write_text(json.dumps(o, indent=2) + "\n")
        write(self.v3 / "transcripts/a-asr.json", {"origin": "local_whisper_ASR", "text": " ".join(s["text"] for s in segs_ok), "segments": segs_ok})
        write(self.v3 / "transcripts/b-asr.json", {"origin": "local_whisper_ASR", "text": " ".join(s["text"] for s in segs_bad), "segments": segs_bad})
        srt = "1\n00:00:00,100 --> 00:00:30,000\n%s\n\n2\n00:00:30,000 --> 00:01:02,500\n%s\n" % (NATURAL[:200], NATURAL[200:])
        (self.v3 / "media/objects/cap.srt").write_text(srt)
        write(self.v3 / "transcripts/c-cap.json", {"origin": "platform_captions", "text": NATURAL, "original_path": "media/objects/cap.srt"})
        write(self.v3 / "transcripts/d-silent.json", {"origin": "no_audio_stream_in_acquired_file", "text": ""})
        (self.v2 / "media/e-captions-0.srt").write_text("1\n00:00:00,100 --> 00:00:30,000\n%s\n\n2\n00:00:30,000 --> 00:00:59,000\n%s\n" % (NATURAL[:200], NATURAL[200:]))
        write(self.v3 / "transcripts/index.json", [{"asset_id": "A", "path": "transcripts/a-asr.json"}, {"asset_id": "B", "path": "transcripts/b-asr.json"},
                                                    {"asset_id": "C", "path": "transcripts/c-cap.json"}, {"asset_id": "D", "path": "transcripts/d-silent.json"}])
        self.e_sha = hashlib.sha256((self.v2 / "media/e-captions-0.srt").read_bytes()).hexdigest()

        def asset(aid, audio=True, dur=60.0, status="acquired"):
            return {"post_id": "P" + aid, "asset_id": aid, "kind": "video", "status": status, "path": "media/objects/%s.mp4" % aid,
                    "sha256": "v" + aid, "ffprobe": ffprobe(duration=dur, audio=audio)}
        self.dataset = {
            "transcripts": [
                {"post_id": "PA", "asset_id": "A", "origin": "local_whisper_ASR", "source_video_sha256": "vA"},
                {"post_id": "PB", "asset_id": "B", "origin": "local_whisper_ASR", "source_video_sha256": "vB"},
                {"post_id": "PC", "asset_id": "C", "origin": "platform_captions", "source_video_sha256": "vC"},
                {"post_id": "PD", "asset_id": "D", "origin": "no_audio_stream_in_acquired_file", "source_video_sha256": "vD"},
                {"post_id": "PE", "asset_id": "E", "origin": "public_platform_captions", "source_video_sha256": "vE",
                 "source_path": "../v2/media/e-captions-0.srt", "source_sha256": self.e_sha},
            ],
            "assets": [asset("A"), asset("B", dur=40.0), asset("C"), asset("D", audio=False), asset("E"), asset("G"),
                       asset("H", status="failed"), {"post_id": "PI", "asset_id": "I", "kind": "image", "status": "acquired"}],
        }
        write(self.v3 / "data/dataset.json", self.dataset)
        self.out = self.v4 / "data/transcript-qa.json"

    def tearDown(self):
        self._tmp.cleanup()

    def snapshot(self):
        return {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path(self._tmp.name).rglob("*"))
                if p.is_file() and "v4" not in p.parts}

    def go(self, **kw):
        return q.run(self.v3 / "data/dataset.json", self.v3, self.out, **kw)[0]

    def test_records_gaps_and_reconciliation(self):
        before = self.snapshot()
        out = self.go()
        self.assertEqual(before, self.snapshot(), "inputs must stay byte-identical")
        recs = {r["asset_id"]: r for r in out["records"]}
        self.assertEqual(len(out["records"]), len(self.dataset["transcripts"]))
        self.assertEqual(recs["A"]["status"], "pass")
        self.assertEqual(recs["B"]["status"], "flagged")
        self.assertEqual({"timing_overrun", "repeated_tail"}, set(recs["B"]["flags"]))
        self.assertEqual(recs["C"]["flags"], ["caption_vs_duration"])
        self.assertEqual(recs["C"]["transcript_kind"], "caption_cues")
        self.assertEqual(recs["C"]["timing_source"]["cues"], 2)
        self.assertEqual(recs["D"]["status"], "not_applicable_no_audio")
        self.assertEqual(recs["E"]["status"], "pass")
        self.assertEqual(recs["E"]["transcript_path"], "../v2/media/e-captions-0.srt")
        self.assertEqual(recs["E"]["transcript_sha256"], self.e_sha)
        for r in out["records"]:
            for key in ("post_id", "asset_id", "transcript_path", "transcript_sha256", "source_video_sha256", "origin",
                        "duration_seconds", "flags", "status", "details", "audio_verified", "accuracy_verified"):
                self.assertIn(key, r)
            self.assertIs(r["audio_verified"], False)
            self.assertIs(r["accuracy_verified"], False)
            self.assertIn(r["status"], q.STATUSES)
        self.assertEqual([g["asset_id"] for g in out["gap_records"]], ["G"])  # H failed, I is an image
        self.assertEqual(out["gap_records"][0]["status"], "missing_transcript")
        rec = out["reconciliation"]
        self.assertTrue(rec["ok"])
        self.assertEqual(rec["expected_asset_ids"], rec["observed_asset_ids"])
        self.assertEqual(rec["status_counts"], {"flagged": 2, "not_applicable_no_audio": 1, "pass": 2})
        self.assertEqual(rec["acquired_video_count"], 6)
        self.assertEqual(rec["inputs_changed_during_run"], [])

    def test_deterministic_bytes(self):
        self.go()
        first = self.out.read_bytes()
        self.go()
        self.assertEqual(first, self.out.read_bytes())

    def test_source_hash_mismatch_flagged(self):
        self.dataset["transcripts"][4]["source_sha256"] = "0" * 64
        self.dataset["transcripts"][0]["source_video_sha256"] = "other"
        (self.v3 / "data/dataset.json").write_text(json.dumps(self.dataset))
        out = self.go()
        recs = {r["asset_id"]: r for r in out["records"]}
        self.assertEqual(recs["E"]["status"], "flagged")
        self.assertIn("source_hash_mismatch", recs["E"]["flags"])
        self.assertIn("source_hash_mismatch", recs["A"]["flags"])

    def test_missing_transcript_file_and_asset(self):
        (self.v3 / "transcripts/a-asr.json").unlink()
        self.dataset["transcripts"].append({"post_id": "PZ", "asset_id": "Z", "origin": "local_whisper_ASR", "source_video_sha256": "vZ"})
        (self.v3 / "data/dataset.json").write_text(json.dumps(self.dataset))
        out = self.go()
        recs = {r["asset_id"]: r for r in out["records"]}
        self.assertEqual(recs["A"]["status"], "missing_transcript")
        self.assertEqual(recs["Z"]["status"], "blocked_unknown_probe")  # no asset record -> unknown probe, not silence
        self.assertEqual(len(out["records"]), 6)
        self.assertTrue(out["reconciliation"]["ok"])

    def test_media_manifest_gap(self):
        manifest = [{"post_id": "PM", "asset_id": "M", "kind": "video", "status": "acquired", "sha256": "vM", "ffprobe": ffprobe()}]
        (self.v3 / "data/media-manifest.json").write_text(json.dumps(manifest))
        out = self.go()
        self.assertEqual(sorted(g["asset_id"] for g in out["gap_records"]), ["G", "M"])

    def test_decode_candidates_and_alternative_attach(self):
        out = self.go()
        cands = out["alternative_summary"]["candidates"]
        self.assertEqual([c["asset_id"] for c in cands], ["B"])  # captions and passing ASR are never candidates
        alt_dir = self.v4 / "transcripts/alternatives"
        alt_dir.mkdir(parents=True)
        rec_b = next(r for r in out["records"] if r["asset_id"] == "B")
        alt_segments = [{"id": i, "start": u["start"], "end": u["end"], "text": u["text"]} for i, u in enumerate(natural_units(40.0))]
        alt = {"schema": q.ALT_SCHEMA, "post_id": "PB", "asset_id": "B", "source_video_sha256": "vB", "model_sha256": "m" * 64,
               "decode_parameters": {"temperature": 0.0}, "text": " ".join(s["text"] for s in alt_segments), "segments": alt_segments,
               "review_status": q.ALT_REVIEW_STATUS, "supersedes_original": False,
               "original": {"path": rec_b["transcript_path"], "sha256": rec_b["transcript_sha256"]}}
        (alt_dir / q.alt_filename("PB", "B")).write_text(json.dumps(alt))
        out2 = self.go()
        rb = next(r for r in out2["records"] if r["asset_id"] == "B")
        self.assertEqual(rb["status"], "flagged")  # original result untouched
        self.assertEqual(rb["alternative"]["qa"]["status"], "pass")
        self.assertIs(rb["alternative"]["supersedes_original"], False)
        self.assertEqual(rb["alternative"]["review_status"], "alternative_decode_unreviewed")
        self.assertTrue(all(rb["alternative"]["validation"].values()))
        self.assertIn("none", rb["alternative"]["adjudication"])
        self.assertEqual(rb["alternative"]["side_by_side"]["original"]["status"], "flagged")
        self.assertEqual(rb["alternative"]["side_by_side"]["alternative"]["status"], "pass")
        self.assertEqual(out2["alternative_summary"]["alternatives_attached"], ["B"])
        self.assertEqual(out2["alternative_summary"]["candidates_without_alternative"], [])
        self.assertIsNone(next(r for r in out2["records"] if r["asset_id"] == "A")["alternative"])

    def test_cli_main(self):
        with contextlib.redirect_stdout(io.StringIO()) as captured:
            code = q.main(["--dataset", str(self.v3 / "data/dataset.json"), "--run-root", str(self.v3), "--out", str(self.out)])
        self.assertEqual(json.loads(captured.getvalue())["records"], 5)
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(self.out.read_text())["schema"], q.SCHEMA)


class DecodeGuardTests(unittest.TestCase):
    def rec(self, **kw):
        base = {"asset_id": "B", "post_id": "PB", "source_video_sha256": "x", "transcript_path": "t.json",
                "transcript_sha256": "y", "origin": "local_whisper_ASR", "status": "flagged", "flags": ["timing_overrun"]}
        base.update(kw)
        return base

    def test_selection_is_capped_and_whisper_only(self):
        records = []
        for i in range(5):
            records.append({"asset_id": "W%d" % i, "origin_family": "whisper_asr", "flags": ["timing_overrun"],
                            "details": {"timing_overrun": {"overrun_seconds": float(i)}}})
        records.append({"asset_id": "C", "origin_family": "captions", "flags": ["caption_vs_duration", "repeated_tail"], "details": {}})
        records.append({"asset_id": "N", "origin_family": "whisper_asr", "flags": ["high_compression"], "details": {}})
        picked, over = q.select_decode_candidates(records, 3)
        self.assertEqual([c["asset_id"] for c in picked], ["W4", "W3", "W2"])
        self.assertEqual([c["asset_id"] for c in over], ["W1", "W0"])

    def test_guards_return_before_loading_any_model(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            asset = {"path": "v.mp4", "sha256": "x"}
            opts = {"model": str(root / "no-model.pt"), "language": "en", "threads": 1}
            self.assertEqual(q.decode_alternative(self.rec(), asset, root, root / "alt.json", opts)["error"], "video_file_not_found")
            (root / "v.mp4").write_bytes(b"not a video")
            self.assertEqual(q.decode_alternative(self.rec(), asset, root, root / "alt.json", opts)["error"], "video_sha256_mismatch")
            sha = hashlib.sha256(b"not a video").hexdigest()
            good = {"path": "v.mp4", "sha256": sha}
            res = q.decode_alternative(self.rec(source_video_sha256=sha), good, root, root / "alt.json", opts)
            self.assertEqual(res["error"], "cached_model_missing_no_download_permitted")
            self.assertFalse((root / "alt.json").exists())


class PriorCaptionRoot(unittest.TestCase):
    def test_prior_caption_timing_uses_original_transcript_root(self):
        with tempfile.TemporaryDirectory() as d:
            top=Path(d);old=top/'prior';new=top/'current';(old/'transcripts').mkdir(parents=True);(old/'media').mkdir();new.mkdir()
            cap=old/'media/captions.srt';cap.write_text('1\n00:00:00,000 --> 00:00:05,000\nsource words\n')
            tr=old/'transcripts/video.json';tr.write_text(json.dumps({'origin':'platform_captions','text':'source words','original_path':'media/captions.srt'}))
            asset={'sha256':'a'*64,'ffprobe':ffprobe(duration=2)}
            rec={'post_id':'p','asset_id':'v','origin':'platform_captions','source_path':str(tr),'source_video_sha256':'a'*64,'transcript_source_root':str(old)}
            result,loaded,_=q.build_record(new,rec,asset,None)
            self.assertEqual(result['timed_units'],1);self.assertEqual(result['last_timed_end'],5);self.assertIn('caption_vs_duration',result['flags']);self.assertEqual((new/loaded['timing_source']['path']).resolve(),cap.resolve())


if __name__ == "__main__":
    unittest.main()
