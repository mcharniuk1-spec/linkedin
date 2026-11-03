"""Shared kit for the Outspoken HyperFrames films (launch film and OS motion film). Deterministic: no wall clock, seeded noise.
Brand: navy #162760, deep navy #0D1A3B, pearl #F1F3F6, marigold #EAA93C/#F6D591/#F3C15D, Nickel 600 #666F7F, inverse S #B9C7DA, inverse O #F2F5FA."""
import json, pathlib, re, shutil, subprocess, tempfile
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 48000

def sync_assets(project, ident):
    """Copies fonts, OS identity files and GSAP into project/assets. ident = design and website/assets/public/assets/identity"""
    a = pathlib.Path(project) / "assets"; (a / "fonts").mkdir(parents=True, exist_ok=True); (a / "brand").mkdir(exist_ok=True)
    fs = pathlib.Path(ident) / "font-source"
    for src, dst in (("fraunces/fraunces-latin-full-normal.woff2", "fraunces.woff2"), ("mona-sans/mona-sans-latin-wght-normal.woff2", "mona-sans.woff2"), ("geist-mono/geist-mono-latin-wght-normal.woff2", "geist-mono.woff2")):
        shutil.copy(fs / src, a / "fonts" / dst)
    for n in ("lockup-os.svg", "lockup-os-inverse.svg", "mark-os.svg", "mark-os-inverse.svg"):
        shutil.copy(pathlib.Path(ident) / "v13" / n, a / "brand" / n)

FONTS = """@font-face{font-family:'Fraunces';src:url('assets/fonts/fraunces.woff2') format('woff2');font-weight:100 900}
@font-face{font-family:'Mona Sans';src:url('assets/fonts/mona-sans.woff2') format('woff2');font-weight:200 900}
@font-face{font-family:'Geist Mono';src:url('assets/fonts/geist-mono.woff2') format('woff2');font-weight:100 900}"""

def mark_parts(paths_json):
    """Returns (width, height, o_left_d, o_right_d, s_d, slash_d) from os-stencil-paths.json; the stencil O has two subpaths (left and right halves)."""
    P = json.loads(pathlib.Path(paths_json).read_text())
    subs = [s for s in re.split(r"(?=M)", P["navy"]) if s.strip()]
    def minx(d): return min(float(x) for x in re.findall(r"[ML C]?(-?\d+\.\d+) -?\d+\.\d+", d)[:40])
    subs.sort(key=minx)
    left = subs[0]; right = "".join(subs[1:])
    return P["width"], P["height"], left, right, P["silver"], P["gold"]

def mark_svg(parts, el_id, o="#162760", s="#666F7F", g="#EAA93C", width=None, extra=""):
    W, H, l, r, sd, gd = parts
    w = width or W
    return (f'<svg id="{el_id}" viewBox="0 0 {W} {H}" width="{w}" height="{w * H / W:.1f}" style="overflow:visible;{extra}">'
            f'<path class="ol" fill="{o}" d="{l}"/><path class="or" fill="{o}" d="{r}"/><path class="ms" fill="{s}" d="{sd}"/><path class="mg" fill="{g}" d="{gd}"/></svg>')

def root_html(W, H, dur, css, body, js, audio_src, lang="en"):
    res = "landscape" if W > H else "portrait"
    return f"""<!doctype html>
<html lang="{lang}" data-resolution="{res}">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="assets/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: {W}px; height: {H}px; overflow: hidden; background: #0D1A3B; }}
      #root {{ position: relative; width: {W}px; height: {H}px; overflow: hidden; font-family: 'Mona Sans', sans-serif; color: #162760; }}
{FONTS}
{css}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{dur}" data-width="{W}" data-height="{H}" data-fps="30">
{body}
      <audio id="mix" src="{audio_src}" data-start="0" data-duration="{dur}" data-volume="1"></audio>
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      (function () {{
        function mulberry32(a){{return function(){{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296}}}}
        const tl = gsap.timeline({{ paused: true }});
        const E = 'cubic-bezier(0.22,1,0.36,1)';
{js}
        window.__timelines['main'] = tl;
      }})();
    </script>
  </body>
</html>
"""

# ------------------------------------------------------------------ audio (synthetic stand-ins)
def _lp(x, fc): return sosfilt(butter(2, fc / (SR / 2), btype="low", output="sos"), x, axis=0)
def _hp(x, fc): return sosfilt(butter(2, fc / (SR / 2), btype="high", output="sos"), x, axis=0)
def _hz(m): return 440.0 * 2 ** ((m - 69) / 12)
def _place(buf, sig, t0, pan=0.0, gain=1.0):
    i = int(t0 * SR); n = min(len(sig), len(buf) - i)
    if n <= 0: return
    buf[i:i + n, 0] += sig[:n] * gain * (1 - max(0, pan)); buf[i:i + n, 1] += sig[:n] * gain * (1 + min(0, pan))
def _env(n, a, r):
    e = np.ones(n); na = max(1, int(a * SR)); nr = max(1, int(r * SR)); e[:na] = np.linspace(0, 1, na) ** 2; e[-nr:] *= np.linspace(1, 0, nr) ** 2; return e
def _lufs(x):
    with tempfile.NamedTemporaryFile(suffix=".wav") as f:
        wavfile.write(f.name, SR, (np.clip(x, -1, 1) * 32767).astype(np.int16))
        out = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", f.name, "-af", "ebur128", "-f", "null", "-"], capture_output=True, text=True).stderr
    vals = re.findall(r"I:\s+(-?\d+\.\d+) LUFS", out); return float(vals[-1]) if vals else -30.0
def _norm(x, target, peak_db=-2.2):
    """Iterative gain to the loudness target with a soft (tanh) limiter, so peaks cannot pull the level down."""
    lim = 10 ** (peak_db / 20)
    for _ in range(4):
        x = x * 10 ** ((target - _lufs(x)) / 20); x = lim * np.tanh(x / lim)
    return x

def make_audio(out_dir, dur, cuts, lines, chords, bpm=92, seed=7, voice="Daniel", rate=172, speech_duck=True, events=()):
    """Writes music.wav, sfx.wav, guide-voice.wav, mix-voice-ready.wav (-19 LUFS) and mix-with-guide.wav (-16 LUFS). lines: [(t0, t1, text)]."""
    out = pathlib.Path(out_dir); out.mkdir(parents=True, exist_ok=True); rng = np.random.default_rng(seed); N = int(dur * SR)
    t = np.arange(N) / SR; mus = np.zeros((N, 2)); sfx = np.zeros((N, 2))
    bar = 4 * 60 / bpm; nb = int(np.ceil(dur / bar))
    for b in range(nb):  # soft pad chords, one per bar, slow attack
        root = chords[b % len(chords)]; seg = int(bar * SR) + int(.6 * SR); tt = np.arange(seg) / SR
        sig = sum(np.sin(2 * np.pi * _hz(root + iv) * tt + k) * (0.9 if iv else 1.0) for k, iv in enumerate((0, 7, 12, 16, 19)))
        sig = _lp(sig * _env(seg, .9, .9), 1800) * 0.055; _place(mus, sig, b * bar, pan=(-.2 if b % 2 else .2))
    beat = 60 / bpm
    for k in range(int(dur / beat)):  # pulse: soft low thump on every beat, light tick off-beat
        t0 = k * beat
        if t0 > dur - 1.2: break
        n = int(.35 * SR); tt = np.arange(n) / SR; th = np.sin(2 * np.pi * (52 + 30 * np.exp(-tt * 18)) * tt) * np.exp(-tt * 9) * .22
        _place(mus, th, t0); tk = _hp(rng.standard_normal(int(.04 * SR)), 6000) * np.exp(-np.arange(int(.04 * SR)) / SR * 90) * .035; _place(mus, tk, t0 + beat / 2, pan=.3)
    for c in cuts:  # transition effects: a filtered whoosh into the cut and a soft hit on it
        n = int(.55 * SR); w = _lp(_hp(rng.standard_normal(n), 400), 5000) * np.linspace(0, 1, n) ** 2 * .10; _place(sfx, w, max(0, c - .55), pan=.15)
        n2 = int(.9 * SR); tt = np.arange(n2) / SR; h = (np.sin(2 * np.pi * 61 * tt) * np.exp(-tt * 6) + _lp(rng.standard_normal(n2), 900) * np.exp(-tt * 14) * .5) * .32; _place(sfx, h, c)
    # event-synced effects: one designed sound for each visual beat (kind, time[, count, spacing])
    def tick(t0, g=.07, f=3200):
        n = int(.035 * SR); tt = np.arange(n) / SR; _place(sfx, np.sin(2 * np.pi * f * tt) * np.exp(-tt * 140) * g, t0, pan=.2)
    def pop(t0, g=.10, f=720):
        n = int(.16 * SR); tt = np.arange(n) / SR; _place(sfx, (np.sin(2 * np.pi * f * tt) + .4 * np.sin(2 * np.pi * f * 2.01 * tt)) * np.exp(-tt * 34) * g, t0, pan=-.15)
    def swoosh(t0, g=.08, d=.38):
        n = int(d * SR); env = np.sin(np.linspace(0, np.pi, n)) ** 2; _place(sfx, _lp(_hp(rng.standard_normal(n), 900), 6500) * env * g, t0, pan=.1)
    def thump(t0, g=.26):
        n = int(.45 * SR); tt = np.arange(n) / SR; _place(sfx, np.sin(2 * np.pi * (48 + 40 * np.exp(-tt * 22)) * tt) * np.exp(-tt * 8) * g, t0)
    def shimmer(t0, g=.05):
        n = int(1.2 * SR); tt = np.arange(n) / SR; _place(sfx, sum(np.sin(2 * np.pi * f * tt) * a for f, a in ((1320, 1), (1980, .5), (2640, .3))) * np.exp(-tt * 3.2) * g, t0, pan=.25)
    def riser(t0, g=.06, d=.6):
        n = int(d * SR); _place(sfx, _hp(rng.standard_normal(n), 1500) * np.linspace(0, 1, n) ** 3 * g, t0)
    KIND = {"tick": tick, "pop": pop, "swoosh": swoosh, "thump": thump, "shimmer": shimmer, "riser": riser}
    for ev in events:
        kind, t0 = ev[0], ev[1]; count = ev[2] if len(ev) > 2 else 1; step = ev[3] if len(ev) > 3 else .08
        for k in range(count): KIND[kind](t0 + k * step)
    n = int(2.6 * SR); tt = np.arange(n) / SR  # final bell
    bell = sum(np.sin(2 * np.pi * f * tt) * a for f, a in ((880, 1), (1320, .4), (1760, .2))) * np.exp(-tt * 1.6) * .08; _place(sfx, bell, max(0, dur - 4.2))
    fade = np.ones(N); nf = int(1.0 * SR); fade[-nf:] = np.linspace(1, 0, nf) ** 1.5; mus *= fade[:, None]; sfx *= fade[:, None]
    if speech_duck:  # duck music 8 dB under speech windows
        g = np.ones(N)
        for a, b, _ in lines: g[int(a * SR):int(b * SR)] = 10 ** (-8 / 20)
        k = int(.18 * SR); g = np.convolve(g, np.ones(k) / k, mode="same"); mus *= g[:, None]
    w = lambda p, x: wavfile.write(out / p, SR, (np.clip(x, -1, 1) * 32767).astype(np.int16))
    w("music.wav", mus); w("sfx.wav", sfx)
    mix = _norm(mus + sfx * .9, -19.0); w("mix-voice-ready.wav", mix)
    if shutil.which("say") is None:  # the timing-guide voice needs the macOS `say` command; the master carries music and effects only, so skip it elsewhere
        return {"voice_ready_lufs": round(_lufs(mix), 1), "with_guide_lufs": None, "guide": "skipped: no `say` command on this machine"}
    guide = np.zeros((N, 2))
    with tempfile.TemporaryDirectory() as d:
        for i, (a, b, text) in enumerate(lines):
            aiff = pathlib.Path(d) / f"l{i}.aiff"; wav = pathlib.Path(d) / f"l{i}.wav"
            subprocess.run(["say", "-v", voice, "-r", str(rate), "-o", str(aiff), text], check=True)
            subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(aiff), "-ar", str(SR), "-ac", "1", str(wav)], check=True)
            sr, x = wavfile.read(wav); x = x.astype(np.float64) / 32768.0
            room = int((b - a) * SR)
            if len(x) > room:  # speed up slightly if the line is longer than its window
                tmp = pathlib.Path(d) / f"f{i}.wav"; fac = min(1.25, len(x) / room)
                subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(wav), "-filter:a", f"atempo={fac:.3f}", str(tmp)], check=True)
                sr, x = wavfile.read(tmp); x = x.astype(np.float64) / 32768.0
            _place(guide, x * .9, a)
    w("guide-voice.wav", guide)
    both = _norm(mix + guide * 1.0, -16.0); w("mix-with-guide.wav", both)
    return {"voice_ready_lufs": round(_lufs(mix), 1), "with_guide_lufs": round(_lufs(both), 1)}

def write_vo(folder, title, dur, lines, scenes, note):
    """VOICEOVER.md (timed table), voiceover.txt (narration only), captions.srt."""
    f = pathlib.Path(folder); f.mkdir(parents=True, exist_ok=True)
    ts = lambda s: f"{int(s // 3600):02d}:{int(s % 3600 // 60):02d}:{int(s % 60):02d},{int(round((s % 1) * 1000)):03d}"
    rows = "\n".join(f"| {i + 1} | {a:.2f} to {b:.2f} s | {sc} | {text} |" for i, ((a, b, text), sc) in enumerate(zip(lines, scenes)))
    words = sum(len(t.split()) for _, _, t in lines)
    (f / "VOICEOVER.md").write_text(f"# {title}: voiceover (proposed)\n\nDuration {dur:.2f} s. {words} words. {note}\n\nDelivery: warm, close to the microphone, confident and unhurried; one breath per line; leave the music to carry the cuts. Record each line separately; the picture is timed to the windows below, so a take may run shorter than its window, never longer.\n\n| # | Window | Scene | Narration |\n|---|---|---|---|\n{rows}\n")
    (f / "voiceover.txt").write_text("\n".join(t for _, _, t in lines) + "\n")
    (f / "captions.srt").write_text("\n".join(f"{i + 1}\n{ts(a)} --> {ts(b)}\n{t}\n" for i, (a, b, t) in enumerate(lines)))
