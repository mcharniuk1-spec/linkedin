#!/usr/bin/env python3
"""Measured QA for a rendered Outspoken 30-second film. Usage: python3 scripts/qa.py <video.mp4> [<second-render.mp4>] [--size WxH] [--out qa.json]
Checks: duration, size, codec, fps, audio, loudness and true peak, isolated-spike (garbled) frames, flash rate, optional determinism against a second render."""
import json, re, subprocess, sys, hashlib
import numpy as np

args = [a for a in sys.argv[1:] if not a.startswith("--")]
video = args[0]; second = args[1] if len(args) > 1 else None
size = "1080x1920"; out = "qa.json"
for i, a in enumerate(sys.argv):
    if a == "--size": size = sys.argv[i + 1]
    if a == "--out": out = sys.argv[i + 1]
W, H = map(int, size.split("x"))
res = {"file": video, "checks": {}}

def probe():
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,codec_name,width,height,r_frame_rate,pix_fmt,sample_rate,channels", "-of", "json", video], capture_output=True, text=True)
    return json.loads(r.stdout)
p = probe(); v = [s for s in p["streams"] if s["codec_type"] == "video"][0]; a = [s for s in p["streams"] if s["codec_type"] == "audio"]
dur = float(p["format"]["duration"])
def chk(name, ok, detail): res["checks"][name] = {"pass": bool(ok), "detail": detail}
chk("duration", abs(dur - 30.0) <= 1 / 30 + 1e-3, f"{dur:.3f} s")
chk("frame_size", (v["width"], v["height"]) == (W, H), f"{v['width']}x{v['height']}")
chk("video_codec", v["codec_name"] == "h264" and v["pix_fmt"] == "yuv420p", f"{v['codec_name']} {v['pix_fmt']}")
chk("fps", v["r_frame_rate"] == "30/1", v["r_frame_rate"])
chk("audio_present", bool(a) and a[0]["codec_name"] == "aac" and a[0]["sample_rate"] == "48000", json.dumps(a[0]) if a else "no audio")

# loudness and true peak
r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", video, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
summ = r.stderr.split("Summary:")[-1]
I = float(re.search(r"I:\s+(-?\d+\.\d+) LUFS", summ).group(1)); tp = re.search(r"Peak:\s+(-?\d+\.\d+) dBFS", summ)
tpv = float(tp.group(1)) if tp else None
chk("loudness", -21.0 <= I <= -14.0, f"{I:.1f} LUFS integrated (voice-ready mix without voice; with the voice the target is about -16)")
chk("true_peak", tpv is not None and tpv <= -1.5, f"{tpv} dBTP" if tpv is not None else "not measured")

# frames: luminance and isolated spikes
raw = subprocess.run(["ffmpeg", "-v", "error", "-i", video, "-vf", "fps=30,scale=54:96,format=gray", "-f", "rawvideo", "-"], capture_output=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, 96, 54).astype(np.float32)
n = len(fr); lum = fr.mean(axis=(1, 2)); d = np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2))
chk("frame_count", n == 900, f"{n} frames")
spikes = []
for i in range(1, n - 1):
    a_, b_ = d[i - 1], d[i]; skip = float(np.abs(fr[i + 1] - fr[i - 1]).mean())
    if a_ > 14 and b_ > 14 and skip < 0.35 * min(a_, b_): spikes.append(int(i))
chk("isolated_spike_frames", len(spikes) == 0, f"{len(spikes)} {spikes[:10]}")
jumps = [int(i) for i in range(1, n) if abs(lum[i] - lum[i - 1]) > 70]
per_sec = {}
for j in jumps: per_sec[j // 30] = per_sec.get(j // 30, 0) + 1
chk("flash_rate", all(c <= 3 for c in per_sec.values()), f"luminance jumps > 70 at frames {jumps}; max {max(per_sec.values()) if per_sec else 0} per second")
res["frame0_mean_luma"] = float(lum[0]); res["max_frame_diff"] = float(d.max())

def frame_hashes(path, idx):
    h = {}
    for i in idx:
        b = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"select=eq(n\\,{i})", "-vframes", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        h[i] = hashlib.sha256(b).hexdigest()[:16]
    return h
if second:
    idx = [0, 95, 171, 330, 400, 560, 640, 780, 899]
    h1, h2 = frame_hashes(video, idx), frame_hashes(second, idx)
    same = [i for i in idx if h1[i] == h2[i]]
    chk("determinism_two_renders", len(same) == len(idx), f"{len(same)}/{len(idx)} sampled frames identical ({idx})")
res["pass"] = all(c["pass"] for c in res["checks"].values())
open(out, "w").write(json.dumps(res, indent=2) + "\n")
for k, c in res["checks"].items(): print(("PASS " if c["pass"] else "FAIL ") + k + ": " + c["detail"])
print("OVERALL", "PASS" if res["pass"] else "FAIL")
