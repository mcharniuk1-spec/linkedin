#!/usr/bin/env python3
"""Measured QA for a rendered film: container, loudness, silence, freezes, motion energy, safe margins, contact sheet.

    python3 scripts/qa/qa.py out/master.mp4 --report out/qa-master.json --sheet out/contact-master.png [--check-times 5,12,20]

It reports numbers and PASS/FAIL against explicit thresholds. It does not judge taste: music quality, voice, and brand feel still need a human listening/viewing pass.
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np

TH = {
    "fps": 30,
    "width_height": None,  # set per file: must match the composition
    "lufs_min": -17.5, "lufs_max": -14.0,
    "true_peak_max": -1.0,
    "max_freeze_s": 1.0,  # a frozen picture longer than this is a defect
    "max_low_motion_s": 2.0,  # consecutive seconds with motion energy under the floor
    "motion_floor": 0.6,  # mean absolute luma difference (0-255) per sampled step
    "max_silence_s": 2.0,
    "margin_pct": 5.0,  # edge band used for the safe-margin check
}


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def probe(path):
    r = run(["ffprobe", "-v", "error", "-print_format", "json", "-show_streams", "-show_format", str(path)])
    return json.loads(r.stdout)


def faststart(path):
    head = Path(path).read_bytes()[:200000]
    moov, mdat = head.find(b"moov"), head.find(b"mdat")
    return moov != -1 and (mdat == -1 or moov < mdat)


def loudness(path):
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "ebur128=peak=true", "-f", "null", "-"])
    tail = r.stderr[r.stderr.rfind("Summary:"):]
    g = lambda pat: float(re.search(pat, tail).group(1))
    return {"integrated_lufs": g(r"I:\s+(-?[\d.]+) LUFS"), "lra": g(r"LRA:\s+([\d.]+) LU"), "true_peak_dbtp": g(r"Peak:\s+(-?[\d.]+) dBFS")}


def intervals(stderr, start_key, end_key):
    out, cur = [], None
    for line in stderr.splitlines():
        a = re.search(start_key + r":\s*([\d.]+)", line)
        b = re.search(end_key + r":\s*([\d.]+)", line)
        if a:
            cur = float(a.group(1))
        if b and cur is not None:
            out.append((cur, float(b.group(1))))
            cur = None
    return out


def silences(path):
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-af", "silencedetect=noise=-50dB:d=0.4", "-vn", "-f", "null", "-"])
    return [(round(a, 2), round(b, 2)) for a, b in intervals(r.stderr, "silence_start", "silence_end")]


def freezes(path):
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-vf", "freezedetect=n=0.001:d=0.5", "-an", "-f", "null", "-"])
    return [(round(a, 2), round(b, 2)) for a, b in intervals(r.stderr, "lavfi.freezedetect.freeze_start", "lavfi.freezedetect.freeze_end")]


def blacks(path):
    r = run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path), "-vf", "blackdetect=d=0.2:pix_th=0.04", "-an", "-f", "null", "-"])
    return [(float(a), float(b)) for a, b in re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", r.stderr)]


def frames_gray(path, fps, w=480, h=270):
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(path), "-vf", f"fps={fps},scale={w}:{h}", "-pix_fmt", "gray", "-f", "rawvideo", "-"]
    raw = subprocess.run(cmd, capture_output=True).stdout
    n = len(raw) // (w * h)
    return np.frombuffer(raw[: n * w * h], dtype=np.uint8).reshape(n, h, w).astype(np.float32)


def motion_energy(path, step_fps=6):
    f = frames_gray(path, step_fps)
    d = np.abs(np.diff(f, axis=0)).mean(axis=(1, 2))
    per_s = [float(d[i:i + step_fps].mean()) for i in range(0, len(d), step_fps)]
    return per_s


def longest_run(flags):
    best = cur = 0
    for x in flags:
        cur = cur + 1 if x else 0
        best = max(best, cur)
    return best


def margin_check(path, times, pct):
    """Share of bright (text-like) pixels inside the outer edge band at the given times (hold frames of each scene)."""
    res = []
    for t in times:
        cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", str(t), "-i", str(path), "-frames:v", "1", "-vf", "scale=960:540", "-pix_fmt", "gray", "-f", "rawvideo", "-"]
        raw = subprocess.run(cmd, capture_output=True).stdout
        if len(raw) < 960 * 540:
            continue
        img = np.frombuffer(raw[: 960 * 540], dtype=np.uint8).reshape(540, 960)
        mx, my = int(960 * pct / 100), int(540 * pct / 100)
        band = np.ones_like(img, dtype=bool)
        band[my:-my, mx:-mx] = False
        light_ground = float(np.median(img)) > 128
        textlike = (img[band] < 90) if light_ground else (img[band] > 200)
        res.append({"t": t, "ground": "pearl" if light_ground else "navy", "text_like_share_in_margin_pct": round(float(textlike.mean() * 100), 2)})
    return res


def contact_sheet(path, out, every=2.5, cols=6, width=320):
    dur = float(probe(path)["format"]["duration"])
    n = int(dur / every)
    rows = (n + cols - 1) // cols
    vf = f"fps=1/{every},scale={width}:-1,tile={cols}x{rows}:padding=4:color=0x101218"
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(path), "-vf", vf, "-frames:v", "1", str(out)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--report", default=None)
    ap.add_argument("--sheet", default=None)
    ap.add_argument("--size", default="1920x1080")
    ap.add_argument("--check-times", default="")
    ap.add_argument("--timeline", default=None, help="src/timeline.json: scene events used as the action-cadence check")
    a = ap.parse_args()
    p = probe(a.video)
    v = next(s for s in p["streams"] if s["codec_type"] == "video")
    au = next((s for s in p["streams"] if s["codec_type"] == "audio"), None)
    num, den = map(int, v["r_frame_rate"].split("/"))
    fps = num / den
    checks = []

    def chk(name, ok, detail, warn=False):
        checks.append({"check": name, "pass": bool(ok), "detail": detail, "warn": warn})

    w, h = map(int, a.size.split("x"))
    chk("container/codec", p["format"]["format_name"].startswith("mov") and v["codec_name"] == "h264" and v["pix_fmt"] == "yuv420p", f'{p["format"]["format_name"]} {v["codec_name"]} {v["profile"]} {v["pix_fmt"]}')
    chk("resolution", int(v["width"]) == w and int(v["height"]) == h, f'{v["width"]}x{v["height"]}')
    chk("frame rate", abs(fps - TH["fps"]) < 0.01, f"{fps:.3f}")
    chk("faststart (moov before mdat)", faststart(a.video), "")
    chk("audio present AAC stereo", au is not None and au["codec_name"] == "aac" and int(au["channels"]) == 2, "none" if au is None else f'{au["codec_name"]} {au["channels"]}ch {au["sample_rate"]} Hz')
    if au is not None:
        dv, da = float(v.get("duration", p["format"]["duration"])), float(au.get("duration", p["format"]["duration"]))
        chk("A/V duration match (<=0.15 s)", abs(dv - da) <= 0.15, f"video {dv:.2f}s audio {da:.2f}s")
        lo = loudness(a.video)
        chk("integrated loudness", TH["lufs_min"] <= lo["integrated_lufs"] <= TH["lufs_max"], f'{lo["integrated_lufs"]} LUFS, LRA {lo["lra"]}')
        chk("true peak", lo["true_peak_dbtp"] <= TH["true_peak_max"], f'{lo["true_peak_dbtp"]} dBTP')
        sil = [s for s in silences(a.video) if s[1] - s[0] >= 0.4]
        long_sil = [s for s in sil if s[1] - s[0] > TH["max_silence_s"]]
        chk("no long silence", not long_sil, f"gaps >=0.4 s: {sil}")
    fr = freezes(a.video)
    dur_total = float(p["format"]["duration"])
    allowed = [(0.0, 1.6), (dur_total - 3.0, dur_total + 0.1)]  # the silent typed open and the end-card hold
    bad = [(a_, b) for a_, b in fr if b - a_ > TH["max_freeze_s"] and not any(a_ >= lo - 0.05 and b <= hi + 0.05 for lo, hi in allowed)]
    chk("no frozen picture >1 s (open and end card exempt)", not bad, f"offending: {bad}; all freezes >=0.5 s: {fr}")
    bl = blacks(a.video)
    chk("no black frames", not bl, f"{bl}")
    me = motion_energy(a.video)
    low = [x < TH["motion_floor"] for x in me]
    chk("motion energy: no low-energy run over 2 s (WARN only: mean luminance difference under-reads small changes on pale scenes)", longest_run(low) * 1.0 <= TH["max_low_motion_s"], f"longest low-motion run {longest_run(low)} s; low seconds {[i for i, x in enumerate(me) if x < TH['motion_floor']]}; per-second energy min {min(me):.2f} median {float(np.median(me)):.2f} max {max(me):.2f}", warn=True)
    if a.timeline:
        tl = json.loads(Path(a.timeline).read_text())
        ts = sorted(c["t"] for c in tl["cues"])
        gaps = [(round(y - x, 2), round(x, 2)) for x, y in zip(ts, ts[1:])]
        chk("action cadence from build metadata: gap between visual events <= 3.0 s", max(g[0] for g in gaps) <= 3.0, f"{len(ts)} events, max gap {max(gaps)}, gaps over 2 s: {[g for g in gaps if g[0] > 2.0]}")
    times = [float(x) for x in a.check_times.split(",") if x]
    mc = margin_check(a.video, times, TH["margin_pct"]) if times else []
    report = {"file": str(a.video), "duration_s": float(p["format"]["duration"]), "size_bytes": int(p["format"]["size"]), "bitrate_kbps": round(int(p["format"]["bit_rate"]) / 1000), "checks": checks, "motion_energy_per_second": [round(x, 2) for x in me], "margin_samples": mc}
    if a.report:
        Path(a.report).write_text(json.dumps(report, indent=1))
    if a.sheet:
        contact_sheet(a.video, a.sheet)
    for c in checks:
        print(("PASS " if c["pass"] else ("WARN " if c.get("warn") else "FAIL ")) + c["check"] + " :: " + c["detail"])
    return 0 if all(c["pass"] or c.get("warn") for c in checks) else 1


if __name__ == "__main__":
    sys.exit(main())
