#!/usr/bin/env python3
"""Synthesises the 30-second film's score, effects and (optional) guide voice. Deterministic: seeded numpy, no network.
Outputs in assets/audio/: music.wav, sfx.wav, mix-voice-ready.wav (music + effects, ducked under speech windows), guide-voice.wav (macOS say, timing reference only),
mix-with-guide.wav. Everything here is a synthetic stand-in for a composed score and a recorded voice."""
import subprocess, sys, pathlib, tempfile
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 48000
DUR = 30.0
N = int(SR * DUR)
OUT = pathlib.Path(__file__).resolve().parent.parent / "assets" / "audio"
OUT.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(20261102)

# speech windows (VOICEOVER-30S.md): start, end
SPEECH = [(0.30, 3.00), (3.40, 5.40), (5.80, 10.80), (11.20, 13.60), (14.00, 17.20), (17.60, 21.00), (21.60, 28.80)]
CUTS = [3.30, 5.70, 10.90, 13.85, 17.50, 21.30]
LINES = ["You know your product better than anyone.", "Your buyers decide in seconds.",
         "We start with your experience, then find the question your buyer already asks.", "We write it in your voice.",
         "Then show it clearly: posts, stories, carousels, video.", "Profile, content and campaigns. One connected message.",
         "Make the right buyers care about you and what you're building. Outspoken. Book an intro call."]

def hz(m): return 440.0 * 2 ** ((m - 69) / 12)
def env_ar(n, a, r, shape=2.0):
    e = np.ones(n); na = max(1, int(a * SR)); nr = max(1, int(r * SR))
    e[:na] = np.linspace(0, 1, na) ** shape; e[-nr:] *= np.linspace(1, 0, nr) ** shape; return e
def lp(x, fc, order=2):
    sos = butter(order, fc / (SR / 2), btype="low", output="sos"); return sosfilt(sos, x, axis=0)
def hp(x, fc, order=2):
    sos = butter(order, fc / (SR / 2), btype="high", output="sos"); return sosfilt(sos, x, axis=0)
def bp(x, f1, f2, order=2):
    sos = butter(order, [f1 / (SR / 2), f2 / (SR / 2)], btype="band", output="sos"); return sosfilt(sos, x, axis=0)
def place(buf, sig, t0, pan=0.0, gain=1.0):
    i = int(t0 * SR)
    if i >= len(buf): return
    sig = sig[: len(buf) - i] if i >= 0 else sig
    l = gain * np.cos((pan + 1) * np.pi / 4); r = gain * np.sin((pan + 1) * np.pi / 4)
    buf[i:i + len(sig), 0] += sig * l; buf[i:i + len(sig), 1] += sig * r
def smooth_mask(windows, floor, fade=0.18):
    g = np.ones(N)
    for a, b in windows:
        ia, ib, f = int(a * SR), int(b * SR), int(fade * SR)
        g[max(0, ia - f):ia] = np.minimum(g[max(0, ia - f):ia], np.linspace(1, floor, ia - max(0, ia - f)))
        g[ia:ib] = floor
        g[ib:ib + f] = np.minimum(g[ib:ib + f], np.linspace(floor, 1, len(g[ib:ib + f])))
    return g

# ------------------------------------------------------------------ music
CH = [  # start, end, chord midi notes (pad), root
    (0.0, 4.8, [53, 57, 60, 64], 41), (4.8, 9.6, [57, 60, 64, 67], 45), (9.6, 14.4, [60, 64, 67, 71], 48),
    (14.4, 19.2, [55, 59, 62, 66], 43), (19.2, 24.0, [53, 57, 60, 64], 41), (24.0, 30.0, [60, 64, 67, 71], 48)]
music = np.zeros((N, 2))
for a, b, notes, root in CH:
    n = int((b - a + 1.4) * SR); t = np.arange(n) / SR
    pad = np.zeros(n)
    for k, m in enumerate(notes):
        f = hz(m)
        for det in (-0.12, 0.0, 0.14):
            ff = f * 2 ** (det / 12 * 0.2)
            pad += (np.sin(2 * np.pi * ff * t) + .35 * np.sin(4 * np.pi * ff * t) + .12 * np.sin(6 * np.pi * ff * t)) * (0.55 if det == 0 else 0.3)
    pad = lp(pad, 1500) * env_ar(n, 0.9, 1.3) * 0.045
    place(music, pad, a, pan=-0.25); place(music, pad * 0.9, a + 0.012, pan=0.25)
    # bass: root notes on beats 1 and 3 of each 2.4 s bar
    for bar in np.arange(a, b, 2.4):
        for off in (0.0, 1.2):
            tt = np.arange(int(1.1 * SR)) / SR
            bsig = np.sin(2 * np.pi * hz(root) * tt) * np.exp(-tt * 2.2) * env_ar(len(tt), .02, .3) * 0.16
            place(music, bsig, bar + off, 0.0)
    # arpeggio plucks, 8th notes at 100 bpm
    step = 0.3; seq = [0, 2, 1, 3, 2, 3, 1, 2]
    for j, tpos in enumerate(np.arange(a + 0.15, b, step)):
        m = notes[seq[j % 8]] + 12 + (12 if j % 8 == 3 else 0)
        tt = np.arange(int(0.55 * SR)) / SR; f = hz(m)
        p = (np.sin(2 * np.pi * f * tt) + .28 * np.sin(4 * np.pi * f * tt) + .1 * np.sin(6 * np.pi * f * tt)) * np.exp(-tt * 7.5) * env_ar(len(tt), .004, .12)
        vel = 0.075 * (1.25 if j % 4 == 0 else 1.0)
        place(music, p * vel, tpos, pan=(-0.5 if j % 2 else 0.5))
# intensity: calm -> build into 21.3 -> hold -> tail
tgrid = np.arange(N) / SR
inten = np.interp(tgrid, [0, 3, 8, 17.5, 21.3, 22.0, 26.5, 28.2, 30.0], [.5, .62, .75, .85, 1.1, 1.0, 1.0, .7, 0.0])
music *= inten[:, None]
music[:, 0] = lp(music[:, 0], 9000); music[:, 1] = lp(music[:, 1], 9000)

# ------------------------------------------------------------------ effects
sfx = np.zeros((N, 2))
def noise(n): return rng.standard_normal(n)
def swell(t0, dur, f1, f2, gain, pan=0.0):
    n = int(dur * SR); x = noise(n); y = np.zeros(n); seg = 24
    for k in range(seg):
        a, b = k * n // seg, (k + 1) * n // seg; fc = f1 * (f2 / f1) ** (k / (seg - 1))
        y[a:b] = bp(x[a:b], max(60, fc * .7), min(SR / 2 - 100, fc * 1.4), 1)
    y *= (np.linspace(0, 1, n) ** 2.2) * gain; place(sfx, y, t0, pan)
def hit(t0, f=55, gain=0.55, dur=0.9):
    tt = np.arange(int(dur * SR)) / SR; ff = f * (1 + 1.6 * np.exp(-tt * 18))
    y = np.sin(2 * np.pi * np.cumsum(ff) / SR) * np.exp(-tt * 4.2) * gain; y += lp(noise(len(tt)), 400) * np.exp(-tt * 30) * gain * .5
    place(sfx, y, t0, 0.0)
def sparkle(t0, gain=0.22, dur=1.1, n=70):
    for _ in range(n):
        tt0 = t0 + rng.random() * dur * .8; f = 2500 + rng.random() * 6000; ll = int(.06 * SR)
        tt = np.arange(ll) / SR; y = np.sin(2 * np.pi * f * tt) * np.exp(-tt * 55) * gain * rng.random()
        place(sfx, y, tt0, rng.random() * 2 - 1)
def whoosh(t0, dur, gain, direction=1):
    n = int(dur * SR); x = noise(n); y = np.zeros(n); seg = 20
    for k in range(seg):
        a, b = k * n // seg, (k + 1) * n // seg; p = k / (seg - 1); fc = (500 + 5200 * np.sin(p * np.pi)) 
        y[a:b] = bp(x[a:b], fc * .6, min(SR / 2 - 100, fc * 1.5), 1)
    env = np.sin(np.linspace(0, np.pi, n)) ** 1.5; y *= env * gain
    l = np.linspace(1, 0, n) if direction > 0 else np.linspace(0, 1, n); i = int(t0 * SR)
    sfx[i:i + n, 0] += y * (0.4 + .6 * l); sfx[i:i + n, 1] += y * (0.4 + .6 * (1 - l))
def bell(t0, f=880, gain=0.16, dur=3.2):
    tt = np.arange(int(dur * SR)) / SR; y = np.zeros(len(tt))
    for mult, amp, dec in [(1, 1, 1.4), (2.76, .5, 2.4), (5.4, .25, 3.2), (1.5, .35, 1.8), (2.0, .4, 1.6)]:
        y += amp * np.sin(2 * np.pi * f * mult * tt) * np.exp(-tt * dec)
    place(sfx, y * gain * env_ar(len(tt), .003, .4), t0, 0.0)
def tick(t0, gain=0.10, f=2400):
    ll = int(.05 * SR); tt = np.arange(ll) / SR; y = (np.sin(2 * np.pi * f * tt) * .6 + hp(noise(ll), 3000) * .4) * np.exp(-tt * 70) * gain; place(sfx, y, t0, 0.15)

# T1 ink flood (3.30): wet swell and a low thump
swell(2.45, 0.85, 220, 1400, 0.34); hit(3.30, 52, 0.62)
# T2 spark burst (5.70): crackle, sweep, impact
swell(5.20, 0.5, 1800, 7000, 0.16); sparkle(5.66, 0.26, 1.0, 90); hit(5.70, 62, 0.55, 0.7)
# T3 paint wipe (10.90)
whoosh(10.62, 0.75, 0.24, 1); hit(10.92, 70, 0.30, 0.5)
# T4 whip pan (13.85)
whoosh(13.52, 0.62, 0.36, -1); hit(13.86, 66, 0.28, 0.45)
# T5 iris (17.50): sub swell and a ring ping
swell(16.85, 0.7, 120, 900, 0.26); hit(17.50, 48, 0.5, 1.1); bell(17.52, 1320, 0.10, 2.2)
# T6 selection expansion + shutter (21.30): riser into a big hit with shimmer
swell(19.6, 1.7, 160, 4800, 0.34); hit(21.30, 44, 0.78, 1.6); sparkle(21.32, 0.2, 1.4, 80)
# hero line completion chime (about 25.5) and end
bell(25.55, 880, 0.18, 3.6); bell(25.62, 1318, 0.09, 3.2); bell(28.9, 440, 0.07, 1.4)
# small selection ticks: S1 product (0.95+...), S2 seconds, S3 question card, S4 voice, S5 clearly, S6 connected, S7 care
for t0 in [1.45, 4.25, 8.45, 11.55, 14.55, 20.45, 24.15, 4.05, 1.0]:
    tick(t0)
for t0 in [2.05, 2.20, 2.35, 2.50, 6.55, 6.69, 6.83, 6.97]:
    tick(t0, 0.06, 1700)
sfx = np.tanh(sfx * 1.1)

# ------------------------------------------------------------------ mixes
duck = smooth_mask(SPEECH, 0.42)
mus_d = music * duck[:, None]
mix = mus_d + sfx * 0.9
def lufs_gain(x, target):
    import subprocess, tempfile
    with tempfile.NamedTemporaryFile(suffix=".wav") as f:
        wavfile.write(f.name, SR, (np.clip(x, -1, 1) * 32767).astype(np.int16))
        r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", f.name, "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True)
    import re
    m = re.search(r"I:\s+(-?\d+\.\d+) LUFS", r.stderr.split("Summary:")[-1]); cur = float(m.group(1)) if m else -23.0
    return 10 ** ((target - cur) / 20), cur
def w16(path, x): wavfile.write(path, SR, (np.clip(x, -1, 1) * 32767).astype(np.int16))
g, cur = lufs_gain(mix, -19.0); mix *= g
# true-peak guard
pk = np.max(np.abs(mix)); lim = 10 ** (-1.7 / 20)
if pk > lim: mix *= lim / pk
w16(OUT / "mix-voice-ready.wav", mix)
w16(OUT / "music.wav", np.clip(music * g, -1, 1)); w16(OUT / "sfx.wav", np.clip(sfx * 0.9 * g, -1, 1))
print(f"voice-ready mix: measured {cur:.1f} LUFS before gain {20*np.log10(g):+.1f} dB, peak {20*np.log10(np.max(np.abs(mix))):.1f} dBFS")

# ------------------------------------------------------------------ guide voice (timing reference only)
import shutil
if "--no-guide" not in sys.argv and shutil.which("say"):
    guide = np.zeros((N, 2))
    voice = "Samantha"
    for (a, b), text in zip(SPEECH, LINES):
        with tempfile.TemporaryDirectory() as d:
            aiff = pathlib.Path(d) / "l.aiff"; wav = pathlib.Path(d) / "l.wav"
            subprocess.run(["say", "-v", voice, "-o", str(aiff), text], check=True)
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(aiff), "-ar", str(SR), "-ac", "1", str(wav)], check=True)
            sr, x = wavfile.read(wav); x = x.astype(np.float64) / 32768
        want = b - a
        if len(x) / SR > want:  # speed up to fit the window with ffmpeg atempo (max 1.35)
            ratio = min(1.35, len(x) / SR / want)
            with tempfile.TemporaryDirectory() as d:
                src = pathlib.Path(d) / "s.wav"; dst = pathlib.Path(d) / "d.wav"; wavfile.write(src, SR, (x * 32767).astype(np.int16))
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-filter:a", f"atempo={ratio:.4f}", str(dst)], check=True)
                sr, x = wavfile.read(dst); x = x.astype(np.float64) / 32768
        place(guide, x * 0.9, a, 0.0)
    gl, gcur = lufs_gain(guide, -17.0); guide *= gl
    w16(OUT / "guide-voice.wav", np.clip(guide, -1, 1))
    both = mix + guide; gm, bcur = lufs_gain(both, -16.0); both *= gm
    pk = np.max(np.abs(both));
    if pk > lim: both *= lim / pk
    w16(OUT / "mix-with-guide.wav", both)
    print(f"with guide: {bcur:.1f} LUFS before gain {20*np.log10(gm):+.1f} dB")
