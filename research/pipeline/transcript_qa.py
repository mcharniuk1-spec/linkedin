#!/usr/bin/env python3
"""Deterministic transcript quality checks for LinkedIn reference-post videos.

Reads a pipeline dataset.json (transcript + asset records with ffprobe output), runs
mechanical checks on every transcript record and writes one QA record per transcript
(plus explicit gap records for acquired videos that have no transcript record).
Original transcripts are only read, never modified.

Standard library only for QA. The optional bounded alternative decode
(--decode-flagged) imports openai-whisper lazily and must run under the interpreter
that has it installed; QA output is identical whichever interpreter attaches existing
alternatives.

Checks and statuses are documented next to the constants below. Nothing here verifies
audio or accuracy: every record carries audio_verified=false and accuracy_verified=false.
"""
import argparse
import hashlib
import json
import math
import os
import re
import sys
import time
import zlib
from pathlib import Path

SCHEMA = "linkedin-transcript-qa/1"
ALT_SCHEMA = "linkedin-transcript-alternative/1"

# Thresholds (from the task contract).
OVERRUN_TOLERANCE_S = 1.0        # segment/cue end may exceed video duration by this much
OVERLAP_TOLERANCE_S = 0.05       # segment start may precede previous end by this much
COMPRESSION_MAX = 2.4            # Whisper's own hallucination heuristic
IDENTICAL_TAIL_SEGMENTS = 3      # last >=3 segments with identical normalized text
TAIL_FRACTION = 0.25             # final 25% of tokens
NGRAM_MIN = 4                    # repeated n-gram, n >= 4
NGRAM_COVERAGE = 0.40            # covering >= 40% of the tail
TAIL_MIN_TOKENS = 8              # below this the n-gram check is skipped (cannot repeat twice)
EXCERPT_CHARS = 80

STATUSES = ("pass", "flagged", "not_applicable_no_audio", "blocked_unknown_probe",
            "missing_transcript", "duration_unknown")
DECODE_TRIGGER_FLAGS = ("timing_overrun", "repeated_tail")
ALT_REVIEW_STATUS = "alternative_decode_unreviewed"

DEFAULT_WHISPER_MODEL = os.environ.get("LINKEDIN_WHISPER_MODEL", str(Path.home() / ".cache/whisper/large-v3-turbo.pt"))


# --------------------------------------------------------------------------- helpers

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def excerpt(s, limit=EXCERPT_CHARS):
    s = " ".join(str(s).split())
    return s if len(s) <= limit else s[: limit - 3] + "..."


_TOKEN_RE = re.compile(r"[^\W_]+(?:'[^\W_]+)*", re.UNICODE)


def tokens(text):
    return _TOKEN_RE.findall(str(text).lower().replace("’", "'"))


def normalize(text):
    return " ".join(tokens(text))


def is_number(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


_TS_RE = re.compile(r"^(?:(\d+):)?(\d{1,2}):(\d{2})[.,](\d{1,3})$")
_CUE_RE = re.compile(r"^\s*(\S+)\s*-->\s*(\S+)")
_TAG_RE = re.compile(r"<[^>]+>")


def parse_timestamp(s):
    m = _TS_RE.match(str(s).strip())
    if not m:
        return None
    hours = int(m.group(1) or 0)
    return hours * 3600 + int(m.group(2)) * 60 + int(m.group(3)) + int(m.group(4).ljust(3, "0")) / 1000.0


def parse_cues(raw):
    """Parse SRT or WebVTT text. Returns (cues, unparsed_cue_count)."""
    cues, unparsed = [], 0
    for block in re.split(r"\r?\n[ \t]*\r?\n", raw.replace("﻿", "")):
        lines = block.splitlines()
        idx = next((i for i, line in enumerate(lines) if "-->" in line), None)
        if idx is None:
            continue
        m = _CUE_RE.match(lines[idx])
        start = parse_timestamp(m.group(1)) if m else None
        end = parse_timestamp(m.group(2)) if m else None
        if start is None or end is None:
            unparsed += 1
            continue
        body = " ".join(_TAG_RE.sub("", ln).strip() for ln in lines[idx + 1:] if ln.strip())
        cues.append({"start": start, "end": end, "text": body})
    return cues, unparsed


def origin_family(origin):
    o = (origin or "").lower()
    if "no_audio" in o:
        return "no_audio"
    if "probe_unavailable" in o:
        return "probe_unavailable"
    if "whisper" in o or "_asr" in o:
        return "whisper_asr"
    if "caption" in o:
        return "captions"
    if "page_transcript" in o:
        return "page_text"
    return "other"


def probe_info(ffprobe):
    """Mirror asr_worker: probe is usable only if a video stream is listed."""
    info = {"ok": False, "has_audio": None, "duration": None, "reason": None}
    if not isinstance(ffprobe, dict):
        info["reason"] = "ffprobe_missing"
        return info
    streams = ffprobe.get("streams")
    if not isinstance(streams, list) or not streams:
        info["reason"] = "ffprobe_streams_missing"
        return info
    types = [s.get("codec_type") for s in streams if isinstance(s, dict)]
    if "video" not in types:
        info["reason"] = "ffprobe_no_video_stream"
        return info
    info["ok"] = True
    info["has_audio"] = "audio" in types
    fmt = ffprobe.get("format")
    raw = fmt.get("duration") if isinstance(fmt, dict) else None
    if isinstance(raw, (int, float, str)) and not isinstance(raw, bool):
        try:
            val = float(raw)
        except ValueError:
            val = None
        if val is not None and math.isfinite(val) and val > 0:
            info["duration"] = val
    return info


# ----------------------------------------------------------------------------- checks

def check_timing_overrun(units, duration):
    over = [(i, u["end"]) for i, u in enumerate(units) if round(u["end"] - duration, 6) > OVERRUN_TOLERANCE_S]
    if not over:
        return None
    last_end = max(u["end"] for u in units)
    return {"duration_seconds": duration, "last_segment_end": round(last_end, 3),
            "overrun_seconds": round(last_end - duration, 3), "segments_over_tolerance": len(over),
            "first_over_index": over[0][0], "tolerance_seconds": OVERRUN_TOLERANCE_S}


def check_caption_vs_duration(units, duration):
    last_end = max(u["end"] for u in units)
    if round(last_end - duration, 6) <= OVERRUN_TOLERANCE_S:
        return None
    return {"duration_seconds": duration, "last_cue_end": round(last_end, 3),
            "overrun_seconds": round(last_end - duration, 3), "tolerance_seconds": OVERRUN_TOLERANCE_S}


def check_non_monotonic(units):
    bad = []
    prev_end = None
    for i, u in enumerate(units):
        if round(u["end"] - u["start"], 6) < 0:
            bad.append({"index": i, "start": round(u["start"], 3), "end": round(u["end"], 3), "reason": "end_before_start"})
        if prev_end is not None and round(prev_end - u["start"], 6) > OVERLAP_TOLERANCE_S:
            bad.append({"index": i, "start": round(u["start"], 3), "previous_end": round(prev_end, 3), "reason": "starts_before_previous_end"})
        prev_end = u["end"]
    if not bad:
        return None
    return {"violations": len(bad), "examples": bad[:3], "overlap_tolerance_seconds": OVERLAP_TOLERANCE_S}


def identical_tail(units):
    if len(units) < IDENTICAL_TAIL_SEGMENTS:
        return None
    last = normalize(units[-1]["text"])
    count = 0
    for u in reversed(units):
        if normalize(u["text"]) != last:
            break
        count += 1
    if count < IDENTICAL_TAIL_SEGMENTS:
        return None
    return {"identical_trailing_segments": count, "excerpt": excerpt(units[-1]["text"])}


def repeated_ngram_tail(text):
    toks = tokens(text)
    tail_len = max(1, math.ceil(len(toks) * TAIL_FRACTION))
    tail = toks[-tail_len:]
    if len(tail) < TAIL_MIN_TOKENS:
        return None
    best = None  # (coverage, n, gram, occurrences)
    for n in range(NGRAM_MIN, len(tail) // 2 + 1):
        positions = {}
        for i in range(len(tail) - n + 1):
            positions.setdefault(tuple(tail[i:i + n]), []).append(i)
        for gram, ps in positions.items():
            if len(ps) < 2:
                continue
            covered = set()
            for p in ps:
                covered.update(range(p, p + n))
            cov = len(covered) / len(tail)
            if cov >= NGRAM_COVERAGE and (best is None or cov > best[0] or (cov == best[0] and n > best[1])):
                best = (cov, n, gram, len(ps))
    if best is None:
        return None
    return {"ngram_tokens": best[1], "occurrences": best[3], "tail_coverage": round(best[0], 3),
            "tail_tokens": len(tail), "excerpt": excerpt(" ".join(best[2]))}


def check_repeated_tail(units, text):
    info = {}
    seg = identical_tail(units) if units else None
    if seg:
        info["identical_tail_segments"] = seg
    gram = repeated_ngram_tail(text)
    if gram:
        info["repeated_ngram"] = gram
    if not info:
        return None
    info["excerpt"] = (seg or gram)["excerpt"]
    return info


def compression_ratio(text):
    data = text.encode("utf-8")
    return len(data) / len(zlib.compress(data)) if data else 0.0


def check_compression(text):
    ratio = compression_ratio(text.strip())
    if ratio <= COMPRESSION_MAX:
        return None
    return {"ratio": round(ratio, 3), "threshold": COMPRESSION_MAX, "chars": len(text.strip())}


def evaluate(family, probe, tr, extra=None):
    """Run all checks. Returns {'status', 'flags', 'details'}.

    family: origin_family() value. probe: probe_info() result. tr: transcript dict with
    kind ('whisper_segments'|'caption_cues'|'text_only'|'none'), text, units, exists, error.
    extra: [(flag, details)] integrity flags raised by the caller.
    """
    flags, details = [], {}

    def add(flag, info):
        if flag not in details:
            flags.append(flag)
        details[flag] = info

    for flag, info in (extra or []):
        add(flag, info)
    text = tr.get("text") or ""
    units = tr.get("units") or []
    kind = tr.get("kind") or "none"
    has_text = bool(text.strip())
    file_ok = bool(tr.get("exists"))
    no_audio_ok = False

    if not file_ok and family != "no_audio":
        add("transcript_file_missing", {"reason": tr.get("error") or "file_not_found", "path": tr.get("path_rel")})

    if not probe.get("ok"):
        add("unknown_probe", {"reason": probe.get("reason") or "ffprobe_unusable"})
    elif probe["has_audio"] is False:
        if family == "no_audio" and not has_text:
            no_audio_ok = True
        else:
            add("origin_audio_mismatch", {"reason": "ffprobe shows no audio stream but origin/text disagree",
                                          "origin_family": family, "text_chars": len(text.strip())})
    elif family == "no_audio":
        add("origin_audio_mismatch", {"reason": "origin says no audio stream but ffprobe shows an audio stream",
                                      "origin_family": family})

    if not no_audio_ok:
        if probe.get("ok") and probe["has_audio"] and file_ok and not has_text:
            add("empty_text_with_audio", {"reason": "audio stream present but transcript text is empty"})
        duration = probe.get("duration") if probe.get("ok") else None
        if probe.get("ok") and duration is None:
            add("duration_unknown", {"reason": "ffprobe format.duration absent or not a positive number"})
        if has_text:
            if kind == "whisper_segments" and units:
                res = check_timing_overrun(units, duration) if duration is not None else None
                if res:
                    add("timing_overrun", res)
            elif kind == "caption_cues" and units:
                res = check_caption_vs_duration(units, duration) if duration is not None else None
                if res:
                    add("caption_vs_duration", res)
            else:
                add("timing_unavailable", {"reason": "no segment or cue timing for transcript kind '%s'" % kind})
        if units:
            res = check_non_monotonic(units)
            if res:
                add("non_monotonic_or_overlap", res)
        if has_text:
            res = check_repeated_tail(units, text)
            if res:
                add("repeated_tail", res)
            res = check_compression(text)
            if res:
                add("high_compression", res)

    if "unknown_probe" in details:
        status = "blocked_unknown_probe"
    elif "empty_text_with_audio" in details or "transcript_file_missing" in details:
        status = "missing_transcript"
    elif [f for f in flags if f != "duration_unknown"]:
        status = "flagged"
    elif "duration_unknown" in details:
        status = "duration_unknown"
    elif no_audio_ok:
        status = "not_applicable_no_audio"
    else:
        status = "pass"
    return {"status": status, "flags": flags, "details": details}


# ------------------------------------------------------------------ transcript loading

def rel_path(run_root, p):
    return os.path.normpath(os.path.relpath(str(p), str(run_root)))


def valid_units(raw):
    """Segments with numeric start/end -> units. Returns (units, malformed_count)."""
    units, bad = [], 0
    for seg in raw if isinstance(raw, list) else []:
        if isinstance(seg, dict) and is_number(seg.get("start")) and is_number(seg.get("end")):
            units.append({"start": float(seg["start"]), "end": float(seg["end"]), "text": str(seg.get("text") or "")})
        else:
            bad += 1
    return units, bad


def load_transcript(run_root, rel, caption_root=None):
    """Load a transcript file (json, srt, vtt). Never writes."""
    run_root = Path(run_root)
    tr = {"path_rel": os.path.normpath(rel) if rel else None, "exists": False, "sha256": None, "kind": "none",
          "text": "", "units": [], "file_origin": None, "timing_source": None, "malformed_segments": 0,
          "unparsed_cues": 0, "error": None}
    if not rel:
        tr["error"] = "no_transcript_path_in_dataset_or_index"
        return tr
    path = run_root / rel
    if not path.is_file():
        tr["error"] = "file_not_found"
        return tr
    tr["exists"] = True
    tr["sha256"] = sha256_file(path)
    suffix = path.suffix.lower()
    try:
        if suffix in (".srt", ".vtt"):
            raw = path.read_text(encoding="utf-8", errors="replace")
            cues, unparsed = parse_cues(raw)
            tr["unparsed_cues"] = unparsed
            tr["units"] = cues
            tr["kind"] = "caption_cues" if cues else "text_only"
            tr["text"] = " ".join(c["text"] for c in cues).strip()
        elif suffix == ".json":
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                tr["error"] = "transcript_json_not_an_object"
                return tr
            tr["file_origin"] = data.get("origin")
            tr["text"] = str(data.get("text") or "")
            units, bad = valid_units(data.get("segments"))
            tr["malformed_segments"] = bad
            if units:
                tr["units"], tr["kind"] = units, "whisper_segments"
            else:
                tr["kind"] = "text_only"
                orig = data.get("original_path")
                if orig:
                    cpath = Path(caption_root or run_root) / orig
                    if cpath.is_file():
                        cues, unparsed = parse_cues(cpath.read_text(encoding="utf-8", errors="replace"))
                        tr["unparsed_cues"] = unparsed
                        tr["timing_source"] = {"path": rel_path(run_root,cpath), "sha256": sha256_file(cpath), "cues": len(cues)}
                        if cues:
                            tr["units"], tr["kind"] = cues, "caption_cues"
                    else:
                        tr["timing_source"] = {"path": rel_path(run_root,cpath), "sha256": None, "cues": 0, "error": "file_not_found"}
        else:
            tr["error"] = "unsupported_transcript_format:" + suffix
            tr["exists"] = False
    except (OSError, ValueError) as exc:
        tr["error"] = "unreadable:%s" % type(exc).__name__
        tr["exists"] = False
    return tr


# ------------------------------------------------------------------------ record build

def build_record(run_root, rec, asset, index_entry):
    asset = asset or {}
    rel = rec.get("source_path") or (index_entry or {}).get("path")
    tr = load_transcript(run_root, rel, rec.get("transcript_source_root"))
    origin = rec.get("origin") or (index_entry or {}).get("origin") or tr["file_origin"]
    family = origin_family(origin)
    probe = probe_info(asset.get("ffprobe")) if asset else {"ok": False, "has_audio": None, "duration": None, "reason": "asset_record_not_found"}
    video_sha = rec.get("source_video_sha256") or (index_entry or {}).get("source_video_sha256") or asset.get("sha256")
    extra = []
    mismatches = []
    if asset.get("sha256") and video_sha and asset["sha256"] != video_sha:
        mismatches.append({"what": "source_video_sha256", "transcript_record": video_sha, "asset_record": asset["sha256"]})
    if rec.get("source_sha256") and tr["sha256"] and rec["source_sha256"] != tr["sha256"]:
        mismatches.append({"what": "transcript_file_sha256", "dataset_record": rec["source_sha256"], "actual_file": tr["sha256"]})
    if mismatches:
        extra.append(("source_hash_mismatch", {"mismatches": mismatches}))
    res = evaluate(family, probe, tr, extra)
    units = tr["units"]
    out = {
        "post_id": rec.get("post_id"),
        "asset_id": rec.get("asset_id"),
        "transcript_path": tr["path_rel"],
        "transcript_sha256": tr["sha256"],
        "source_video_sha256": video_sha,
        "origin": origin,
        "duration_seconds": probe.get("duration"),
        "flags": res["flags"],
        "status": res["status"],
        "details": res["details"],
        "audio_verified": False,
        "accuracy_verified": False,
        "origin_family": family,
        "transcript_kind": tr["kind"],
        "text_chars": len(tr["text"].strip()),
        "timed_units": len(units),
        "last_timed_end": round(max(u["end"] for u in units), 3) if units else None,
        "timing_source": tr["timing_source"],
        "collection": rec.get("collection"),
        "alternative": None,
    }
    if tr["malformed_segments"] or tr["unparsed_cues"]:
        out["details"]["parse_notes"] = {"malformed_segments": tr["malformed_segments"], "unparsed_cues": tr["unparsed_cues"]}
    return out, tr, probe


# --------------------------------------------------------------- alternative decode

def alt_filename(post_id, asset_id):
    return "%s-%s.json" % (str(post_id).split(":")[-1], hashlib.sha256(asset_id.encode()).hexdigest()[:8])


def select_decode_candidates(records, limit):
    """Whisper-ASR records flagged timing_overrun or repeated_tail, worst overrun first, capped."""
    cands = []
    for order, r in enumerate(records):
        if r["origin_family"] != "whisper_asr":
            continue
        hit = [f for f in DECODE_TRIGGER_FLAGS if f in r["flags"]]
        if not hit:
            continue
        overrun = (r["details"].get("timing_overrun") or {}).get("overrun_seconds", 0.0)
        cands.append((-overrun, order, r["asset_id"], hit))
    cands.sort()
    return [{"asset_id": c[2], "trigger_flags": c[3]} for c in cands[:max(0, limit)]], [
        {"asset_id": c[2], "trigger_flags": c[3]} for c in cands[max(0, limit):]]


def _json_default(o):
    for caster in (int, float):
        try:
            if hasattr(o, "item"):
                return o.item()
            return caster(o)
        except (TypeError, ValueError):
            continue
    raise TypeError("not JSON serializable: %r" % type(o))


def decode_alternative(record, asset, run_root, alt_path, opts):
    """One bounded local decode. Cached model by path only; no download, no network."""
    video = Path(run_root) / asset["path"]
    if not video.is_file():
        return {"error": "video_file_not_found", "path": str(video)}
    video_sha = sha256_file(video)
    expected = {record["source_video_sha256"], asset.get("sha256")} - {None}
    if expected != {video_sha}:
        return {"error": "video_sha256_mismatch", "actual": video_sha, "expected": sorted(expected)}
    model_path = Path(opts["model"])
    if not model_path.is_file():
        return {"error": "cached_model_missing_no_download_permitted", "path": str(model_path)}
    import torch  # lazy: only the decode path needs the Whisper runtime
    import whisper
    t_wall, t_cpu = time.perf_counter(), time.process_time()
    model_sha = sha256_file(model_path)
    torch.set_num_threads(opts["threads"])
    model = whisper.load_model(str(model_path), device="cpu")
    kwargs = {"language": opts["language"], "fp16": False, "temperature": 0.0,
              "condition_on_previous_text": False, "verbose": False}
    t_dec = time.perf_counter()
    result = model.transcribe(str(video), **kwargs)
    decode_elapsed = time.perf_counter() - t_dec
    alt = {
        "schema": ALT_SCHEMA,
        "post_id": record["post_id"],
        "asset_id": record["asset_id"],
        "origin": "local_whisper_ASR_alternative_decode",
        "source_video_path": rel_path(run_root, video),
        "source_video_sha256": video_sha,
        "model_path": str(model_path),
        "model_sha256": model_sha,
        "whisper_version": getattr(whisper, "__version__", None),
        "torch_version": torch.__version__,
        "python_version": sys.version.split()[0],
        "decode_parameters": dict(kwargs, device="cpu", torch_threads=opts["threads"], model_loaded_from="path"),
        "language": result.get("language"),
        "text": result["text"],
        "segments": result["segments"],
        "elapsed_seconds": round(decode_elapsed, 2),
        "total_elapsed_seconds_incl_model_load_and_hash": round(time.perf_counter() - t_wall, 2),
        "cpu_seconds": round(time.process_time() - t_cpu, 2),
        "review_status": ALT_REVIEW_STATUS,
        "supersedes_original": False,
        "original": {"path": record["transcript_path"], "sha256": record["transcript_sha256"],
                     "origin": record["origin"], "qa_status": record["status"], "qa_flags": list(record["flags"])},
        "audio_verified": False,
        "accuracy_verified": False,
        "external_provider": False,
    }
    alt_path = Path(alt_path)
    alt_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = alt_path.with_name(alt_path.name + ".tmp")
    tmp.write_text(json.dumps(alt, indent=2, ensure_ascii=False, default=_json_default) + "\n", encoding="utf-8")
    os.replace(str(tmp), str(alt_path))
    return {"error": None, "path": str(alt_path), "cpu_seconds": alt["cpu_seconds"], "elapsed_seconds": alt["elapsed_seconds"]}


def summarize_side(rec_like, last_end, chars, nseg):
    return {"status": rec_like["status"], "flags": rec_like["flags"], "text_chars": chars,
            "segments": nseg, "last_segment_end": last_end}


def attach_alternative(record, alt_path, run_root, probe):
    """Load an existing alternative decode, run the same QA on it, return the 'alternative' block."""
    alt_path = Path(alt_path)
    data = json.loads(alt_path.read_text(encoding="utf-8"))
    units, bad = valid_units(data.get("segments"))
    tr = {"kind": "whisper_segments" if units else "text_only", "text": str(data.get("text") or ""),
          "units": units, "exists": True}
    res = evaluate("whisper_asr", probe, tr)
    orig = data.get("original") or {}
    validation = {
        "asset_id_matches": data.get("asset_id") == record["asset_id"],
        "original_sha256_matches_current": orig.get("sha256") == record["transcript_sha256"],
        "source_video_sha256_matches_record": data.get("source_video_sha256") == record["source_video_sha256"],
    }
    return {
        "path": rel_path(alt_path.parent.parent.parent, alt_path),
        "sha256": sha256_file(alt_path),
        "review_status": data.get("review_status"),
        "supersedes_original": data.get("supersedes_original"),
        "adjudication": "none: neither transcript is declared correct; a human or supervisor must review the audio",
        "validation": validation,
        "model_sha256": data.get("model_sha256"),
        "decode_parameters": data.get("decode_parameters"),
        "qa": res,
        "side_by_side": {
            "original": summarize_side(record, record["last_timed_end"], record["text_chars"], record["timed_units"]),
            "alternative": summarize_side(res, round(max(u["end"] for u in units), 3) if units else None,
                                          len(tr["text"].strip()), len(units)),
        },
    }


# ------------------------------------------------------------------------------- run

def acquired_videos(assets, manifest):
    found = {}
    for a in assets or []:
        if a.get("kind") == "video" and a.get("status") == "acquired":
            found.setdefault(a["asset_id"], {"post_id": a.get("post_id"), "asset": a, "found_in": ["dataset.assets"]})
    for m in manifest or []:
        if m.get("kind") == "video" and m.get("status") == "acquired":
            if m["asset_id"] in found:
                found[m["asset_id"]]["found_in"].append("media-manifest")
            else:
                found[m["asset_id"]] = {"post_id": m.get("post_id"), "asset": m, "found_in": ["media-manifest"]}
    return found


def count_by(items, key):
    out = {}
    for it in items:
        for v in (it[key] if isinstance(it[key], list) else [it[key]]):
            out[v] = out.get(v, 0) + 1
    return dict(sorted(out.items()))


def run(dataset_path, run_root, out_path, alternatives_dir=None, media_manifest=None, decode=False,
        max_decodes=3, cpu_budget_seconds=900.0, model=DEFAULT_WHISPER_MODEL, language="en", threads=4):
    dataset_path, run_root, out_path = Path(dataset_path), Path(run_root), Path(out_path)
    dataset = json.loads(dataset_path.read_text(encoding="utf-8"))
    transcripts = dataset.get("transcripts") or []
    assets = dataset.get("assets") or []
    assets_by_id = {}
    dup_assets = []
    for a in assets:
        if a["asset_id"] in assets_by_id:
            dup_assets.append(a["asset_id"])
        assets_by_id[a["asset_id"]] = a
    index_path = run_root / "transcripts" / "index.json"
    index = {}
    if index_path.is_file():
        for e in json.loads(index_path.read_text(encoding="utf-8")):
            index[e.get("asset_id")] = e
    manifest = None
    mm = Path(media_manifest) if media_manifest else run_root / "data" / "media-manifest.json"
    if mm.is_file():
        manifest = json.loads(mm.read_text(encoding="utf-8"))
    if alternatives_dir is None:
        alternatives_dir = out_path.parent.parent / "transcripts" / "alternatives"
    alternatives_dir = Path(alternatives_dir)

    records, loaded, probes, hashes_before = [], {}, {}, {}
    for rec in transcripts:
        r, tr, probe = build_record(run_root, rec, assets_by_id.get(rec.get("asset_id")), index.get(rec.get("asset_id")))
        records.append(r)
        loaded[r["asset_id"]], probes[r["asset_id"]] = tr, probe
        for p in (tr["path_rel"], (tr["timing_source"] or {}).get("path")):
            if p and (run_root / p).is_file():
                hashes_before[p] = sha256_file(run_root / p)

    candidates, over_cap = select_decode_candidates(records, max_decodes)
    decode_log = []
    if decode:
        cpu_start = time.process_time()
        by_id = {r["asset_id"]: r for r in records}
        for c in candidates:
            r = by_id[c["asset_id"]]
            alt_path = alternatives_dir / alt_filename(r["post_id"], r["asset_id"])
            if alt_path.exists():
                decode_log.append({"asset_id": r["asset_id"], "outcome": "skipped_existing_alternative_file"})
                continue
            used = time.process_time() - cpu_start
            if used >= cpu_budget_seconds:
                decode_log.append({"asset_id": r["asset_id"], "outcome": "skipped_cpu_budget_exhausted", "cpu_used_seconds": round(used, 2)})
                continue
            res = decode_alternative(r, assets_by_id[r["asset_id"]], run_root, alt_path,
                                     {"model": model, "language": language, "threads": threads})
            decode_log.append(dict(res, asset_id=r["asset_id"], outcome="decode_error" if res.get("error") else "decoded"))
        print(json.dumps({"decode_log": decode_log}, ensure_ascii=False), file=sys.stderr, flush=True)

    attached = []
    for r in records:
        alt_path = alternatives_dir / alt_filename(r["post_id"], r["asset_id"])
        if alt_path.is_file():
            r["alternative"] = attach_alternative(r, alt_path, run_root, probes[r["asset_id"]])
            attached.append(r["asset_id"])

    transcript_ids = [r["asset_id"] for r in records]
    videos = acquired_videos(assets, manifest)
    gaps = []
    for aid, v in sorted(videos.items()):
        if aid in set(transcript_ids):
            continue
        a = v["asset"]
        pr = probe_info(a.get("ffprobe"))
        gaps.append({
            "post_id": v["post_id"], "asset_id": aid, "transcript_path": None, "transcript_sha256": None,
            "source_video_sha256": a.get("sha256"), "origin": None, "duration_seconds": pr.get("duration"),
            "flags": ["no_transcript_record"], "status": "missing_transcript",
            "details": {"no_transcript_record": {"reason": "acquired video has no transcript record in dataset.transcripts",
                                                 "found_in": v["found_in"], "has_audio": pr.get("has_audio"),
                                                 "probe_ok": pr["ok"]}},
            "audio_verified": False, "accuracy_verified": False,
        })

    expected_ids = sorted(set(t.get("asset_id") for t in transcripts))
    observed_ids = sorted(set(transcript_ids))
    dup_transcripts = sorted({x for x in transcript_ids if transcript_ids.count(x) > 1})
    hashes_after = {p: sha256_file(run_root / p) for p in hashes_before}
    changed = sorted(p for p in hashes_before if hashes_before[p] != hashes_after.get(p))
    cands_without_alt = [c["asset_id"] for c in candidates if c["asset_id"] not in attached]
    reconciliation = {
        "expected_transcript_record_count": len(transcripts),
        "observed_record_count": len(records),
        "expected_asset_ids": expected_ids,
        "observed_asset_ids": observed_ids,
        "missing_from_output": sorted(set(expected_ids) - set(observed_ids)),
        "unexpected_in_output": sorted(set(observed_ids) - set(expected_ids)),
        "duplicate_transcript_asset_ids": dup_transcripts,
        "duplicate_asset_records": sorted(set(dup_assets)),
        "acquired_video_count": len(videos),
        "gap_record_count": len(gaps),
        "gap_asset_ids": [g["asset_id"] for g in gaps],
        "status_counts": count_by(records, "status"),
        "flag_counts": count_by(records, "flags"),
        "gap_status_counts": count_by(gaps, "status"),
        "inputs_hashed_before_after": len(hashes_before),
        "inputs_changed_during_run": changed,
    }
    reconciliation["ok"] = (not reconciliation["missing_from_output"] and not reconciliation["unexpected_in_output"]
                            and not dup_transcripts and not dup_assets and not changed
                            and len(records) == len(transcripts))
    output = {
        "schema": SCHEMA,
        "thresholds": {"timing_overrun_seconds": OVERRUN_TOLERANCE_S, "overlap_seconds": OVERLAP_TOLERANCE_S,
                       "compression_ratio_max": COMPRESSION_MAX, "identical_tail_segments": IDENTICAL_TAIL_SEGMENTS,
                       "tail_fraction": TAIL_FRACTION, "ngram_min": NGRAM_MIN, "ngram_tail_coverage": NGRAM_COVERAGE,
                       "ngram_min_tail_tokens": TAIL_MIN_TOKENS},
        "inputs": {"dataset": str(dataset_path), "run_root": str(run_root),
                   "dataset_sha256": sha256_file(dataset_path),
                   "media_manifest_used": bool(manifest is not None)},
        "statement": "Mechanical checks only. audio_verified and accuracy_verified are false for every record; "
                     "a flag means 'needs human audio review', and a pass means 'no mechanical flag fired'.",
        "records": records,
        "gap_records": gaps,
        "alternative_summary": {
            "trigger_flags": list(DECODE_TRIGGER_FLAGS),
            "max_decodes": max_decodes,
            "candidates": candidates,
            "candidates_over_cap": over_cap,
            "alternatives_attached": attached,
            "candidates_without_alternative": cands_without_alt,
        },
        "reconciliation": reconciliation,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output, decode_log


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dataset", required=True, type=Path, help="dataset.json with transcripts + assets")
    ap.add_argument("--run-root", type=Path, default=None,
                    help="root that dataset-relative paths resolve against (default: dataset's run, i.e. dataset parent's parent)")
    ap.add_argument("--out", required=True, type=Path, help="transcript-qa.json to write")
    ap.add_argument("--alternatives-dir", type=Path, default=None,
                    help="alternative decodes (default: <out>/../../transcripts/alternatives)")
    ap.add_argument("--media-manifest", type=Path, default=None, help="optional; default <run-root>/data/media-manifest.json")
    ap.add_argument("--decode-flagged", action="store_true",
                    help="run ONE bounded local Whisper alternative decode on flagged Whisper-ASR records (needs openai-whisper)")
    ap.add_argument("--max-decodes", type=int, default=3)
    ap.add_argument("--cpu-budget-seconds", type=float, default=900.0)
    ap.add_argument("--whisper-model", default=DEFAULT_WHISPER_MODEL)
    ap.add_argument("--language", default="en")
    ap.add_argument("--threads", type=int, default=4)
    a = ap.parse_args(argv)
    run_root = a.run_root or a.dataset.resolve().parent.parent
    out, _ = run(a.dataset, run_root, a.out, a.alternatives_dir, a.media_manifest, a.decode_flagged,
                 a.max_decodes, a.cpu_budget_seconds, a.whisper_model, a.language, a.threads)
    rec = out["reconciliation"]
    print(json.dumps({"records": rec["observed_record_count"], "expected": rec["expected_transcript_record_count"],
                      "gap_records": rec["gap_record_count"], "status_counts": rec["status_counts"],
                      "flag_counts": rec["flag_counts"], "alternatives": out["alternative_summary"]["alternatives_attached"],
                      "reconciled": rec["ok"]}, ensure_ascii=False))
    return 0 if rec["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
