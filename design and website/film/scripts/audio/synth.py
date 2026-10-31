#!/usr/bin/env python3
"""Procedural score for the Outspoken film. No samples, no downloads: everything is synthesised with numpy/scipy.

Reads src/timeline.json (scenes with an energy level, SFX cues, voiceover windows) and writes to audio-out/:
  music.wav   strings pad + plucked arpeggio + finale drums (no effects)
  wind.wav    air bed with slow gusts
  sfx.wav     booms, sparkles, whooshes, risers, ticks, glitches
  mix.wav     everything, loudness-normalised (stereo, 48 kHz, 24-bit)
  mix-vo-bed.wav  same, music and wind ducked while the voiceover windows are open (for the owner's recording)

The strings are additive-synthesis ensembles: they are a stand-in for a recorded orchestra, not a replacement for one.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy import signal
from scipy.io import wavfile

SR = 48000
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
OUT = ROOT / "audio-out"
rng = np.random.default_rng(20261031)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def smooth_env(n, a, r):
    """Smooth attack/release envelope for n samples (seconds a and r)."""
    t = np.arange(n) / SR
    d = n / SR
    return np.clip(np.minimum(t / max(a, 1e-3), (d - t) / max(r, 1e-3)), 0, 1) ** 1.6


def add(buf, sig, t0, pan=0.0, gain=1.0):
    """Mix a mono signal into a stereo buffer at time t0 with equal-power panning."""
    i = int(t0 * SR)
    if i >= buf.shape[0] or i + len(sig) <= 0:
        return
    if i < 0:
        sig = sig[-i:]
        i = 0
    n = min(len(sig), buf.shape[0] - i)
    ang = (pan + 1) * np.pi / 4
    buf[i:i + n, 0] += sig[:n] * np.cos(ang) * gain
    buf[i:i + n, 1] += sig[:n] * np.sin(ang) * gain


def lowpass(x, fc, order=2):
    sos = signal.butter(order, fc, btype="low", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def highpass(x, fc, order=2):
    sos = signal.butter(order, fc, btype="high", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


# ---------------------------------------------------------------- instruments

def string_note(f, dur, bright=0.6, voices=3, detune=(-8, 0, 9), vib=0.0035):
    """Ensemble of detuned additive voices with a slow bow attack and onset vibrato."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for v in range(voices):
        cents = detune[v % len(detune)]
        fv = f * 2 ** (cents / 1200)
        ramp = np.clip((t - 0.6) / 0.8, 0, 1)
        vph = -(fv * vib * ramp / 5.3) * np.cos(2 * np.pi * 5.3 * t + v * 1.7)
        phase0 = rng.uniform(0, 2 * np.pi)
        for h in range(1, 11):
            if fv * h > 9000:
                break
            amp = (1 / h) * bright ** (h - 1)
            out += amp * np.sin(2 * np.pi * fv * h * t + h * vph + phase0 * h)
    return out / voices * smooth_env(n, 1.0, 1.4)


def pluck(f, dur=2.4, decay=0.996, bright=0.5):
    """Karplus-Strong string, run as a vectorised IIR comb."""
    n = int(dur * SR)
    N = max(2, int(round(SR / f)))
    x = np.zeros(n)
    burst = rng.uniform(-1, 1, N)
    burst = lowpass(burst, 1500 + 6000 * bright, 1)
    x[:N] = burst
    a = np.zeros(N + 2)
    a[0] = 1.0
    a[N] = -0.5 * decay
    a[N + 1] = -0.5 * decay
    y = signal.lfilter([1.0], a, x)
    return y / (np.max(np.abs(y)) + 1e-9)


def kick(dur=0.7):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 46 + 90 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t * 6.5)
    click = highpass(rng.uniform(-1, 1, n), 2500) * np.exp(-t * 220) * 0.25
    return np.tanh(1.6 * (body + click))


def tom(f0=96, dur=1.1):
    """Timpani-like low tom: pitch drop, long body, soft mallet noise."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f0 * (1 + 0.55 * np.exp(-t * 22))
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t * 3.4) + 0.35 * np.sin(1.5 * ph) * np.exp(-t * 6)
    mallet = lowpass(rng.uniform(-1, 1, n), 1800) * np.exp(-t * 90) * 0.4
    return np.tanh(1.3 * (body + mallet))


def snare(dur=0.45):
    n = int(dur * SR)
    t = np.arange(n) / SR
    noise = highpass(rng.uniform(-1, 1, n), 1400) * np.exp(-t * 17)
    body = np.sin(2 * np.pi * 188 * t) * np.exp(-t * 28) * 0.7
    return np.tanh(1.4 * (noise * 0.8 + body))


def hat(dur=0.12):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return highpass(rng.uniform(-1, 1, n), 7000) * np.exp(-t * 55) * 0.5


def swell_noise(dur, f_start, f_end, width=0.55, level=1.0):
    """Band-limited noise whose centre frequency glides f_start -> f_end (whoosh / riser / wind core)."""
    n = int(dur * SR)
    x = rng.standard_normal(n)
    f, tt, Z = signal.stft(x, fs=SR, nperseg=2048, noverlap=1536)
    fc = np.geomspace(max(f_start, 30), max(f_end, 30), Z.shape[1])
    lf = np.log(np.maximum(f[:, None], 20))
    mask = np.exp(-0.5 * ((lf - np.log(fc)[None, :]) / width) ** 2)
    _, y = signal.istft(Z * mask, fs=SR, nperseg=2048, noverlap=1536)
    y = y[:n] if len(y) >= n else np.pad(y, (0, n - len(y)))
    return y / (np.max(np.abs(y)) + 1e-9) * level


def sparkle(dur=1.4, base=2400):
    """Glassy inharmonic shimmer for particle bursts."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for ratio in (1.0, 1.51, 2.04, 2.77, 3.9):
        out += np.sin(2 * np.pi * base * ratio * t + rng.uniform(0, 6.28)) * np.exp(-t * (5 + 3 * ratio)) / ratio
    out += highpass(rng.uniform(-1, 1, n), 5000) * np.exp(-t * 14) * 0.25
    return out / (np.max(np.abs(out)) + 1e-9)


def boom(dur=2.2):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 28 + 62 * np.exp(-t * 3.2)
    ph = 2 * np.pi * np.cumsum(f) / SR
    sub = np.sin(ph) * np.exp(-t * 1.5)
    crack = lowpass(rng.uniform(-1, 1, n), 5200) * np.exp(-t * 24) * 0.6
    body = lowpass(rng.uniform(-1, 1, n), 380) * np.exp(-t * 3.0) * 0.55
    return np.tanh(1.5 * (sub + crack + body))


def tick(dur=0.06, f=1900):
    n = int(dur * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) * np.exp(-t * 90) + highpass(rng.uniform(-1, 1, n), 4000) * np.exp(-t * 150) * 0.4) * 0.6


def glitch(dur=0.28):
    n = int(dur * SR)
    t = np.arange(n) / SR
    seg = np.floor(t * 38)
    g = np.sin(2 * np.pi * (300 + 520 * ((seg * 7) % 5)) * t) * (((seg * 3) % 2) * 0.6 + 0.2)
    g += highpass(rng.uniform(-1, 1, n), 3000) * 0.3
    return np.tanh(2.2 * g) * np.exp(-t * 6) * 0.6


def reverb(x, tau=1.9, wet=0.24, seed=3):
    """Stereo convolution reverb from a decaying noise impulse response."""
    r = np.random.default_rng(seed)
    n = int(tau * 2.2 * SR)
    t = np.arange(n) / SR
    out = np.zeros_like(x)
    for c in (0, 1):
        ir = r.standard_normal(n) * np.exp(-t / tau * 3.0)
        ir = lowpass(ir, 5500, 1)
        ir[: int(0.012 * SR)] *= np.linspace(0, 1, int(0.012 * SR))
        ir /= np.sqrt(np.sum(ir ** 2))
        out[:, c] = signal.fftconvolve(x[:, c], ir)[: x.shape[0]]
    return x * (1 - wet) + out * wet


# ---------------------------------------------------------------- composition

# D major colour: Dmaj9 | Bm7 | Gmaj7 | A6/9, then the finale lifts with G - A - Bm - D. MIDI note numbers.
CHORDS = {
    "Dmaj9": [38, 50, 57, 61, 64, 69],
    "Bm7": [35, 47, 54, 59, 62, 66],
    "Gmaj7": [31, 43, 50, 54, 59, 66],
    "A69": [33, 45, 52, 57, 61, 66],
    "G": [31, 43, 50, 55, 59, 67],
    "A": [33, 45, 52, 57, 61, 69],
    "Bm": [35, 47, 54, 59, 62, 69],
    "D": [38, 50, 57, 62, 66, 74],
}
PROGRESSION = ["Dmaj9", "Bm7", "Gmaj7", "A69"]
FINALE = ["G", "A", "Bm", "D"]


def energy_at(scenes, t):
    for s in scenes:
        if s["start"] <= t < s["end"]:
            return s.get("energy", 0.5)
    return scenes[-1].get("energy", 0.5)


def build(tl):
    dur = tl["duration"]
    n = int((dur + 3.0) * SR)  # tail for reverb ring-out
    music = np.zeros((n, 2))
    wind = np.zeros((n, 2))
    sfx = np.zeros((n, 2))
    scenes = tl["scenes"]
    bar = tl.get("bar", 3.0)
    off = tl.get("bar_offset", 0.0)
    finale_start = tl.get("finale_start", dur - 14.0)
    silence = tl.get("silence", [])  # [{start,end}] windows where music drops out before a hit

    def in_silence(t):
        return any(s["start"] <= t < s["end"] for s in silence)

    # strings: one chord per bar, crossfading by overlapping each note 20 %
    nb = int(np.ceil((dur - off) / bar))
    for b in range(nb):
        t0 = off + b * bar
        if t0 >= dur:
            break
        e = energy_at(scenes, t0 + bar * 0.5)
        name = (FINALE if t0 >= finale_start - 1e-6 else PROGRESSION)[b % 4]
        if in_silence(t0 + 0.3):
            continue
        notes = CHORDS[name]
        # fewer voices early, the full ensemble as energy rises
        take = notes[: 2 + int(round(e * 4))]
        bright = 0.35 + 0.5 * e
        for k, m in enumerate(take):
            d = bar * 1.25
            note = string_note(midi(m), d, bright=bright, voices=3 if m > 50 else 2)
            lvl = (0.5 if m < 45 else 0.34) * (0.55 + 0.45 * e)
            add(music, note, t0 - 0.15, pan=(-0.55 + 1.1 * k / max(1, len(take) - 1)) * (0.5 if m < 45 else 1.0), gain=lvl)
        # octave-up shimmer line in the last third of the film
        if e > 0.7 and name in ("G", "A", "Bm", "D"):
            top = string_note(midi(notes[-1] + 12), bar * 1.1, bright=0.8, voices=3)
            add(music, top, t0, pan=0.0, gain=0.16)

    # plucked arpeggio on top: appears once energy > 0.25, density follows energy
    step = bar / 8
    k = 0
    t = off
    while t < dur:
        e = energy_at(scenes, t)
        b = int((t - off) // bar)
        name = (FINALE if t >= finale_start - 1e-6 else PROGRESSION)[b % 4]
        if e > 0.25 and not in_silence(t) and (k % (4 if e < 0.55 else 2) == 0):
            notes = [m for m in CHORDS[name] if m >= 57] or CHORDS[name]
            m = notes[(k // 2) % len(notes)] + (12 if e > 0.75 and k % 4 == 0 else 0)
            add(music, pluck(midi(m), 2.0, bright=0.4 + 0.4 * e), t, pan=rng.uniform(-0.7, 0.7), gain=0.13 + 0.12 * e)
        t += step
        k += 1

    # finale drums: toms roll into a four-on-the-floor with snare accents
    fin_e = [s for s in scenes if s["end"] > finale_start]
    if fin_e:
        beat = bar / 4
        t = finale_start
        roll_len = tl.get("roll_len", bar)
        roll_start = max(finale_start - roll_len, 0)
        for i in range(12):  # accelerating tom roll into the finale
            tt = roll_start + roll_len * (i / 12) ** 1.4
            add(music, tom(88 + (i % 3) * 7, 0.9), tt, pan=(-0.3 + 0.3 * (i % 3)), gain=0.18 + 0.2 * i / 12)
        j = 0
        while t < dur - 0.5:
            if j % 4 in (0, 2):
                add(music, kick(), t, gain=0.5)
            if j % 4 in (1, 3):
                add(music, snare(), t, gain=0.22)
            add(music, hat(), t + beat / 2, pan=0.3, gain=0.16)
            if j % 8 == 0:
                add(music, tom(72, 1.5), t, gain=0.3)
            t += beat
            j += 1
        # closing hit and shimmer
        add(music, tom(64, 2.2), dur - 1.6, gain=0.5)
        add(sfx, swell_noise(2.6, 1200, 6500, 0.9, 0.5), dur - 3.0, gain=0.4)

    # wind: filtered noise whose centre wanders; level rises and falls with scene energy
    w = swell_noise(dur + 2.0, 260, 900, 0.9, 1.0)
    w = lowpass(w, 1400)
    tt = np.arange(len(w)) / SR
    wander = 0.5 + 0.5 * np.sin(2 * np.pi * (0.11 * tt) + 1.3) * np.sin(2 * np.pi * 0.047 * tt + 0.4)
    env = np.array([0.18 + 0.55 * energy_at(scenes, min(x, dur - 1e-3)) for x in tt[::480]])
    env = np.interp(tt, tt[::480], env)
    w = w * (0.35 + 0.65 * wander) * env
    wind[: len(w), 0] += w[: n] * 0.5
    wind[: len(w), 1] += np.roll(w, 1700)[: n] * 0.5

    # cues
    for c in tl.get("cues", []):
        t0, typ, g = c["t"], c["type"], c.get("gain", 1.0)
        pan = c.get("pan", 0.0)
        if typ == "boom":
            add(sfx, boom(), t0, pan, 0.8 * g)
            add(sfx, sparkle(1.6, c.get("base", 2200)), t0 + 0.02, pan, 0.22 * g)
        elif typ == "sparkle":
            add(sfx, sparkle(c.get("dur", 1.2), c.get("base", 2800)), t0, pan, 0.30 * g)
        elif typ == "whoosh":
            d = c.get("dur", 1.0)
            up = c.get("dir", "up") == "up"
            s = swell_noise(d, 350 if up else 4200, 4200 if up else 350, 0.7, 1.0) * smooth_env(int(d * SR), d * 0.55, d * 0.45)
            add(sfx, s, t0, pan, 0.42 * g)
        elif typ == "riser":
            d = c.get("dur", 3.0)
            s = swell_noise(d, 300, 7500, 0.8, 1.0) * (np.linspace(0, 1, int(d * SR)) ** 2.2)
            tone = np.sin(2 * np.pi * np.cumsum(np.geomspace(180, 1900, int(d * SR))) / SR) * (np.linspace(0, 1, int(d * SR)) ** 3) * 0.25
            add(sfx, s + tone, t0, pan, 0.5 * g)
        elif typ == "tick":
            add(sfx, tick(f=c.get("f", 1900)), t0, pan, 0.35 * g)
        elif typ == "glitch":
            add(sfx, glitch(), t0, pan, 0.35 * g)
        elif typ == "hit":
            add(sfx, kick(), t0, pan, 0.6 * g)
            add(sfx, swell_noise(0.5, 2500, 500, 0.9, 1.0) * np.exp(-np.arange(int(0.5 * SR)) / SR * 8), t0, pan, 0.3 * g)
        elif typ == "low":
            add(sfx, tom(c.get("f", 60), 1.8), t0, pan, 0.55 * g)

    return music, wind, sfx, dur


def duck_curve(n, windows, depth_db=-7.0, attack=0.25, release=0.6):
    env = np.ones(n)
    g = 10 ** (depth_db / 20)
    for w in windows:
        a, b = int(w["start"] * SR), int(w["end"] * SR)
        att, rel = int(attack * SR), int(release * SR)
        env[max(0, a - att):a] = np.minimum(env[max(0, a - att):a], np.linspace(1, g, a - max(0, a - att)))
        env[a:b] = np.minimum(env[a:b], g)
        env[b:b + rel] = np.minimum(env[b:b + rel], np.linspace(g, 1, len(env[b:b + rel])))
    return env


def write(name, x):
    OUT.mkdir(parents=True, exist_ok=True)
    peak = np.max(np.abs(x)) + 1e-9
    y = x / max(peak, 1.0)
    wavfile.write(OUT / name, SR, (y * 0.98).astype(np.float32))
    return OUT / name


def main():
    tl = json.loads((ROOT / "src" / "timeline.json").read_text())
    music, wind, sfx, dur = build(tl)
    sil = tl.get("silence", [])
    if sil:
        env = duck_curve(music.shape[0], sil, depth_db=-60.0, attack=0.35, release=0.2)
        music = music * env[:, None]
        wind = wind * duck_curve(wind.shape[0], sil, depth_db=-9.0, attack=0.5, release=0.4)[:, None]
    music = reverb(music, tau=2.0, wet=0.28, seed=11)
    sfx = reverb(sfx, tau=1.2, wet=0.18, seed=17)
    stems = {"music": music, "wind": wind, "sfx": sfx}
    for k, v in stems.items():
        write(f"{k}.wav", v)
    mix = music * 0.9 + wind * 0.55 + sfx * 1.0
    mix = np.tanh(mix * 0.9) / np.tanh(0.9)
    n_end = int(dur * SR)  # the film ends here; the last 1.2 s fades inside it
    mix = mix[:n_end]
    fade = np.ones(len(mix))
    tail = int(1.2 * SR)
    fade[-tail:] = np.linspace(1, 0, tail) ** 1.5
    mix = mix * fade[:, None]
    write("mix-raw.wav", mix)
    vo = tl.get("vo", [])
    if vo:
        d = duck_curve(len(mix), vo)
        bed = music[:n_end] * 0.9 * d[:, None] + wind[:n_end] * 0.55 * d[:, None] + sfx[:n_end]
        bed = np.tanh(bed * 0.9) / np.tanh(0.9) * fade[:, None]
        write("mix-vo-bed-raw.wav", bed)
    for raw, final, target in (("mix-raw.wav", "mix.wav", -16), ("mix-vo-bed-raw.wav", "mix-vo-bed.wav", -20)):
        if not (OUT / raw).exists():
            continue
        # two-pass loudness normalisation (-16 LUFS master, -20 LUFS voiceover bed) with -1.5 dBTP ceiling, 48 kHz 24-bit
        probe = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(OUT / raw), "-af", f"loudnorm=I={target}:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"], capture_output=True, text=True)
        m = json.loads(re.findall(r"\{[^{}]*\}", probe.stderr)[-1])
        af = (f"loudnorm=I={target}:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
        subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-y", "-i", str(OUT / raw), "-af", af, "-ar", "48000", "-c:a", "pcm_s24le", str(OUT / final)], check=True, capture_output=True)
        (OUT / raw).unlink()
        print(final, "measured input", m["input_i"], "LUFS, tp", m["input_tp"])
    print("done", dur, "s")


if __name__ == "__main__":
    sys.exit(main())
