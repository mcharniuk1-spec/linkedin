#!/usr/bin/env python3
"""Outspoken launch film (proposed): 40 s, 16:9 1920x1080, HyperFrames root composition generated from this script.
Usage: python3 build.py <project_dir> <paths_json> [--guide]   (--guide uses the mix with the synthetic guide voice)"""
import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import filmkit as K
PROJ = pathlib.Path(sys.argv[1]); PATHS = sys.argv[2]; GUIDE = "--guide" in sys.argv
W, H, DUR = 1920, 1080, 40.0
CUTS = [5.2, 10.6, 16.6, 21.8, 28.8, 34.6]
LINES = [(0.35, 4.75, "Outspoken is open. Every file lives in one public repository."),
         (5.55, 10.25, "The site, the design system, the research and the films sit side by side, so anyone can see how the work is made."),
         (10.95, 16.25, "Fifteen agent skills passed a security scan before we used them. Thirteen did not. Five more were written for this project."),
         (16.95, 21.45, "The stack is open too: React, Vite, Storybook, HyperFrames, Vercel and Neon."),
         (22.15, 28.45, "We studied two hundred and seventy-nine LinkedIn posts from sixty-one accounts, scored thirty logo concepts, and kept one clear mark."),
         (29.15, 34.25, "Then we measured: accessibility one hundred, a hundred tests, and a deployment verified by hash."),
         (34.95, 39.4, "Outspoken. Founder-led LinkedIn marketing for B2B AI SaaS. Book an intro call.")]
SCENES = ["S1 open", "S2 repository", "S3 security gate", "S4 stack", "S5 the work", "S6 proof", "S7 close"]
PASS = ["geo-content-optimizer", "serp-markup-builder", "content-writer", "page-play-builder", "on-page-seo-checker", "technical-seo-checker", "site-structure-optimizer", "keyword-research", "seo-geo", "seo-sxo", "seo-page", "hyperframes-registry", "seam-craft", "cut-the-curve", "captions-overlay"]
REJ = ["hyperframes", "media-use", "motion-doctrine", "hyperframes-cli", "remotion-to-hyperframes", "geo-audit", "geo-fix-schema", "geo-compare", "geo-fix-llmstxt", "motion-designer", "product-film", "content-quality-auditor", "geo-fix-content"]
OWN = ["outspoken-design-rules", "outspoken-film-build", "outspoken-logo-icon-direction", "outspoken-site-deploy", "update-run-linkedin"]
TOOLS = ["React 19", "Vite 8", "TypeScript 5.9", "Storybook 10", "Motion 14", "Three.js", "HyperFrames 0.9.2", "GSAP", "FFmpeg", "Vercel", "Neon Postgres", "Lighthouse", "fontTools", "potrace", "Claude Code", "Codex"]
TREE = [("mcharniuk1-spec/linkedin", ""), ("├─ design and website/", ""), ("│  ├─ website/", "one-page site"), ("│  ├─ design-system/", "tokens, identity, depth"), ("│  ├─ film/", "motion films"), ("│  └─ deploy/vercel/", "build and lead function"),
        ("├─ research/", "public-source collector"), ("├─ reports/", "279 posts · 61 accounts"), ("├─ skills/", "agent skills"), ("└─ AGENTS.md", "rules for every agent")]
EVENTS = [("swoosh", .15), ("shimmer", 1.05), ("thump", 1.15), ("pop", 1.7), ("tick", 2.3), ("tick", 5.45, 10, .26), ("pop", 6.3), ("pop", 10.8), ("tick", 11.5, 15, .07), ("tick", 12.9, 13, .05), ("thump", 14.0), ("pop", 14.4, 5, .1),
          ("pop", 16.8), ("tick", 17.2, 16, .12), ("pop", 22.0), ("tick", 22.2, 18, .075), ("tick", 23.3, 12, .06), ("swoosh", 24.6), ("thump", 25.2), ("shimmer", 25.25), ("swoosh", 26.2, 5, .28),
          ("pop", 29.0), ("pop", 29.4, 4, .2), ("tick", 29.6, 14, .1), ("tick", 30.4), ("swoosh", 34.9), ("pop", 35.5), ("thump", 36.3), ("tick", 36.9)]
parts = K.mark_parts(PATHS)
css = """
.sc{position:absolute;inset:0;opacity:0}
#s1{opacity:1}
.deep{position:absolute;inset:0;background:radial-gradient(1100px 800px at 82% 12%,rgba(49,87,213,.26),transparent 62%),radial-gradient(900px 700px at 6% 96%,rgba(234,169,60,.10),transparent 60%),#0D1A3B}
.pearl{position:absolute;inset:0;background:linear-gradient(160deg,#fff 8%,#F1F3F6 60%,#E6EBF1)}
.dots{position:absolute;inset:0;background:radial-gradient(rgba(22,39,96,.13) 2.4px,transparent 3.4px) 0 0/44px 44px}
.dots.lt{background:radial-gradient(rgba(241,243,246,.11) 2.4px,transparent 3.4px) 0 0/44px 44px}
.mono{font-family:'Geist Mono',monospace;font-weight:500;letter-spacing:.08em;text-transform:uppercase}
.disp{font-family:'Fraunces',serif;font-weight:400;letter-spacing:-.02em;line-height:1.04}
.ctr{position:absolute;left:0;right:0;text-align:center}
.kick{position:absolute;font-size:28px;color:#B9C7DA}
.kick.dk{color:#3A4A75}
.wm{position:absolute;opacity:.055;pointer-events:none}
#wipe{position:absolute;top:-15%;height:130%;width:3000px;left:0;transform:translateX(-3200px) skewX(-18deg);z-index:50;opacity:0}
#wipe i{position:absolute;right:0;top:0;bottom:0;width:30px;background:#EAA93C}
#cap{position:absolute;left:0;right:0;bottom:46px;display:flex;justify-content:center;z-index:60}
#cap span{max-width:1500px;padding:14px 30px;border-radius:16px;background:rgba(13,26,59,.78);color:#F1F3F6;font-size:34px;line-height:1.3;text-align:center;opacity:0}
.tree{position:absolute;left:150px;top:250px;font-family:'Geist Mono',monospace;font-size:31px;line-height:1.62;color:#162760;white-space:pre}
.tree .ln{opacity:0}.tree em{font-style:normal;color:#666F7F}
.card{position:absolute;height:62px;border-radius:14px;display:flex;align-items:center;gap:14px;padding:0 22px;font-family:'Geist Mono',monospace;font-size:24px;white-space:nowrap;opacity:0}
.card.ok{background:#F2F5FA;color:#162760;box-shadow:0 14px 28px -18px rgba(0,0,0,.6)}
.card.ok b{width:30px;height:30px;border-radius:50%;background:#EAA93C;display:grid;place-items:center;color:#0D1A3B;font-size:20px}
.card.no{background:rgba(185,199,218,.10);color:#B9C7DA;border:2px solid rgba(185,199,218,.28)}
.card.no s{text-decoration:none;position:relative}
.card.own{background:transparent;color:#F3C15D;border:2px solid #EAA93C}
.chip{position:absolute;height:84px;padding:0 34px;border-radius:999px;background:#fff;border:2px solid #D9DEE7;box-shadow:0 18px 30px -22px rgba(22,39,96,.55);display:flex;align-items:center;font-size:34px;font-weight:600;color:#162760;white-space:nowrap;opacity:0}
.chip.hi{background:#162760;color:#F1F3F6;border-color:#162760}
.big{font-family:'Geist Mono',monospace;font-weight:500;color:#F2F5FA;letter-spacing:-.02em}
.tile{position:absolute;width:64px;height:64px;border-radius:10px;border:2px solid rgba(185,199,218,.45);background:rgba(185,199,218,.08)}
.layer{position:absolute;width:680px;height:340px;border-radius:24px;opacity:0;box-shadow:0 20px 40px -28px rgba(0,0,0,.7)}
.stat{position:absolute;width:380px;height:300px;border-radius:24px;background:#fff;border:2px solid #E1E6EE;box-shadow:0 24px 46px -30px rgba(22,39,96,.6);opacity:0}
.stat .n{position:absolute;left:34px;top:34px;font-family:'Geist Mono',monospace;font-size:120px;color:#162760;letter-spacing:-.04em}
.stat .l{position:absolute;left:36px;bottom:36px;right:30px;font-size:30px;line-height:1.25;color:#3A4A75}
.cta{position:absolute;left:50%;transform:translateX(-50%);top:720px;height:96px;padding:0 46px;border-radius:999px;background:#EAA93C;color:#0D1A3B;display:flex;align-items:center;gap:18px;font-size:38px;font-weight:600;opacity:0}
"""
def sc(i, ground, inner): return f'<div class="sc" id="s{i}"><div class="{ground}"></div><div class="dots{" lt" if ground == "deep" else ""}"></div>{inner}</div>'
s1 = sc(1, "deep", f'<div style="position:absolute;left:0;right:0;top:170px;display:flex;justify-content:center">{K.mark_svg(parts, "m1", o="#F2F5FA", s="#B9C7DA", width=430)}</div>'
        '<div class="disp ctr" id="s1h" style="top:470px;font-size:118px;color:#F2F5FA;opacity:0">Outspoken is open.</div>'
        '<div class="mono ctr" id="s1u" style="top:650px;font-size:36px;color:#F3C15D;text-transform:none;letter-spacing:.02em;opacity:0">github.com/mcharniuk1-spec/linkedin</div>')
tree = "".join(f'<div class="ln">{a}{(" " * max(2, 30 - len(a)))}<em>{b}</em></div>' for a, b in TREE)
s2 = sc(2, "pearl", f'<div class="mono kick dk" style="left:150px;top:170px">Public repository</div><div class="tree">{tree}</div>'
        '<div class="disp" id="s2h" style="position:absolute;left:1180px;top:330px;width:620px;font-size:76px;color:#162760;opacity:0">Everything we built, in one public repository.</div>'
        f'<img class="wm" src="assets/brand/mark-os.svg" style="left:1250px;top:640px;width:560px;opacity:.07">')
cards = []
for i, n in enumerate(PASS):
    r, c = divmod(i, 4); cards.append(f'<div class="card ok" style="left:{120 + c * 430}px;top:{290 + r * 74}px;font-size:22px"><b>✓</b>{n}</div>')
for i, n in enumerate(REJ):
    r, c = divmod(i, 5); cards.append(f'<div class="card no" style="left:{120 + c * 336}px;top:{604 + r * 60}px;height:52px;font-size:20px;padding:0 16px">{n}</div>')
for i, n in enumerate(OWN):
    cards.append(f'<div class="card own" style="left:{120 + i * 356}px;top:{806}px;height:52px;font-size:18px;padding:0 14px">{n}</div>')
s3 = sc(3, "deep", '<div class="disp" id="s3h" style="position:absolute;left:120px;top:120px;font-size:72px;color:#F2F5FA;opacity:0">15 skills passed a security scan.</div>'
        '<div class="mono kick" id="s3k" style="left:122px;top:220px;opacity:0">SkillSpector 2.9.6 · 13 not installed · 5 written for this repository</div>' + "".join(cards))
chips = []
for i, n in enumerate(TOOLS):
    r, c = divmod(i, 4); chips.append(f'<div class="chip{" hi" if n.startswith("HyperFrames") else ""}" style="left:{230 + c * 380}px;top:{330 + r * 118}px">{n}</div>')
s4 = sc(4, "pearl", '<div class="disp ctr" id="s4h" style="top:150px;font-size:80px;color:#162760;opacity:0">Built with open tools.</div>' + "".join(chips))
tiles = "".join(f'<div class="tile" style="left:{1140 + (i % 6) * 84}px;top:{250 + (i // 6) * 84}px"></div>' for i in range(30))
layers = "".join(f'<div class="layer" style="left:{1000 + k * 40}px;top:{190 + k * 72}px;background:{bg};border:2px solid {bd}"><span class="mono" style="position:absolute;left:26px;top:18px;font-size:28px;color:{tc}">{nm}</span></div>'
                 for k, (nm, bg, bd, tc) in enumerate([("ground", "#13224f", "rgba(185,199,218,.18)", "#B9C7DA"), ("far · OS watermark", "rgba(185,199,218,.10)", "rgba(185,199,218,.22)", "#B9C7DA"), ("mid · glow", "rgba(49,87,213,.20)", "rgba(185,199,218,.22)", "#B9C7DA"), ("edge · slash seam", "rgba(234,169,60,.16)", "rgba(234,169,60,.6)", "#F3C15D"), ("front · card", "#F2F5FA", "#F2F5FA", "#162760")]))
s5 = sc(5, "deep", '<div class="mono kick" style="left:150px;top:190px">The work</div>'
        '<div id="s5a" style="position:absolute;left:150px;top:290px;opacity:0"><div class="big" style="font-size:190px"><span id="n279">0</span></div><div style="font-size:36px;color:#B9C7DA;margin-top:-6px">LinkedIn posts studied, from <span id="n61" style="color:#F3C15D">0</span> accounts</div></div>'
        f'<div id="s5b" style="position:absolute;inset:0;opacity:0">{tiles}<div style="position:absolute;left:1140px;top:690px;font-size:34px;color:#B9C7DA">30 logo concepts, scored by three reviewers</div><div id="s5m" style="position:absolute;left:1180px;top:300px;opacity:0">{K.mark_svg(parts, "m5", o="#F2F5FA", s="#B9C7DA", width=420)}</div></div>'
        f'<div id="s5c" style="position:absolute;inset:0;opacity:0">{layers}<div class="disp" style="position:absolute;left:150px;top:640px;width:820px;font-size:64px;color:#F2F5FA">One page. Five layers of depth.</div></div>')
stats = [("100", "Accessibility<br>(Lighthouse)"), ("100", "Best practices<br>(Lighthouse)"), ("100", "Unit tests for<br>the lead form"), ("168", "Media files verified<br>by hash on deploy")]
st = "".join(f'<div class="stat" style="left:{130 + i * 420}px;top:300px"><div class="n" id="st{i}">0</div><div class="l">{l}</div></div>' for i, (_, l) in enumerate(stats))
s6 = sc(6, "pearl", '<div class="disp" id="s6h" style="position:absolute;left:130px;top:140px;font-size:76px;color:#162760;opacity:0">Then we measured.</div>' + st +
        '<div class="mono" id="s6f" style="position:absolute;left:132px;top:680px;font-size:28px;color:#3A4A75;opacity:0;text-transform:none;letter-spacing:.02em">Film QA: 30.000 s, −19.1 LUFS, identical repeat renders</div>')
s7 = sc(7, "deep", '<img id="s7l" src="assets/brand/lockup-os-inverse.svg" style="position:absolute;left:50%;top:250px;width:820px;transform:translateX(-50%);opacity:0">'
        '<div class="disp ctr" id="s7h" style="top:480px;font-size:66px;color:#F2F5FA;opacity:0">Founder-led LinkedIn marketing for B2B AI SaaS.</div>'
        '<div class="cta" id="s7c">Book an intro call <svg width="34" height="34" viewBox="0 0 14 14" fill="none"><path d="M3 11 11 3M5 3h6v6" stroke="#0D1A3B" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg></div>'
        '<div class="mono ctr" id="s7u" style="top:860px;font-size:30px;color:#F3C15D;text-transform:none;letter-spacing:.02em;opacity:0">github.com/mcharniuk1-spec/linkedin</div>'
        '<div class="ctr" id="s7n" style="top:930px;font-size:28px;color:#B9C7DA;opacity:0">Proposed. Music and guide voice are synthetic.</div>')
body = "\n".join([s1, s2, s3, s4, s5, s6, s7, '<div id="wipe"><i></i></div>', '<div id="cap"><span id="capt"></span></div>'])
GROUND = {1: "#0D1A3B", 2: "#F1F3F6", 3: "#0D1A3B", 4: "#F1F3F6", 5: "#0D1A3B", 6: "#F1F3F6", 7: "#0D1A3B"}
js = f"""
        const CUTS = {json.dumps(CUTS)}, LINES = {json.dumps(LINES)}, GROUND = {json.dumps(GROUND)};
        const q = (s) => document.querySelector(s), qa = (s) => document.querySelectorAll(s);
        // S1: the stencil mark assembles, then the line and the address
        tl.fromTo('#m1 .ol', {{x: -16}}, {{x: 0, duration: 1.0, ease: E}}, .15);
        tl.fromTo('#m1 .or', {{x: 16}}, {{x: 0, duration: 1.0, ease: E}}, .15);
        tl.fromTo('#m1 .ms', {{x: 22}}, {{x: 0, duration: 1.0, ease: E}}, .3);
        tl.fromTo('#m1 .mg', {{scaleX: 0, transformOrigin: '0% 50%'}}, {{scaleX: 1, duration: .5, ease: 'power3.out'}}, 1.05);
        tl.fromTo('#s1h', {{y: 40, opacity: 0}}, {{y: 0, opacity: 1, duration: .8, ease: E}}, 1.7);
        tl.fromTo('#s1u', {{y: 20, opacity: 0}}, {{y: 0, opacity: 1, duration: .7, ease: E}}, 2.3);
        tl.to('#m1', {{scale: 1.035, duration: 3.0, ease: 'none', transformOrigin: '50% 50%'}}, 1.8);
        // slash wipe between scenes: a panel in the next ground colour with a marigold leading edge
        CUTS.forEach((c, k) => {{
          tl.set('#wipe', {{backgroundColor: GROUND[k + 2], opacity: 1}}, c - .5);
          tl.fromTo('#wipe', {{x: -3200}}, {{x: -500, duration: .5, ease: 'power2.in', immediateRender: false}}, c - .5);
          tl.set('#s' + (k + 1), {{opacity: 0}}, c); tl.set('#s' + (k + 2), {{opacity: 1}}, c);
          tl.to('#wipe', {{opacity: 0, duration: .4, ease: 'power1.out'}}, c + .02);
        }});
        // S2: the repository tree types out line by line
        qa('#s2 .tree .ln').forEach((l, i) => tl.fromTo(l, {{opacity: 0, x: -14}}, {{opacity: 1, x: 0, duration: .3, ease: E}}, 5.45 + i * .26));
        tl.fromTo('#s2h', {{y: 30, opacity: 0}}, {{y: 0, opacity: 1, duration: .8, ease: E}}, 6.3);
        // S3: the security gate
        tl.fromTo('#s3h', {{y: 30, opacity: 0}}, {{y: 0, opacity: 1, duration: .7, ease: E}}, 10.8);
        tl.fromTo('#s3k', {{opacity: 0}}, {{opacity: 1, duration: .6}}, 11.3);
        qa('#s3 .card.ok').forEach((c, i) => tl.fromTo(c, {{y: 18, opacity: 0}}, {{y: 0, opacity: 1, duration: .35, ease: E}}, 11.5 + i * .07));
        qa('#s3 .card.no').forEach((c, i) => tl.fromTo(c, {{y: 18, opacity: 0}}, {{y: 0, opacity: .9, duration: .3, ease: E}}, 12.9 + i * .05));
        tl.to('#s3 .card.no', {{opacity: .38, duration: .5}}, 14.0);
        qa('#s3 .card.own').forEach((c, i) => tl.fromTo(c, {{x: -20, opacity: 0}}, {{x: 0, opacity: 1, duration: .4, ease: E}}, 14.4 + i * .1));
        // S4: tool chips assemble
        tl.fromTo('#s4h', {{y: 30, opacity: 0}}, {{y: 0, opacity: 1, duration: .7, ease: E}}, 16.8);
        const rnd = mulberry32(41);
        qa('#s4 .chip').forEach((c, i) => tl.fromTo(c, {{y: 40 + rnd() * 40, opacity: 0, scale: .92}}, {{y: 0, opacity: 1, scale: 1, duration: .5, ease: 'back.out(1.6)'}}, 17.2 + i * .12));
        // S5: research counter, 30 concepts to one mark, five layers of depth
        tl.fromTo('#s5a', {{opacity: 0, y: 24}}, {{opacity: 1, y: 0, duration: .6, ease: E}}, 22.0);
        const ctr = {{a: 0, b: 0}};
        tl.to(ctr, {{a: 279, b: 61, duration: 1.4, ease: 'power2.out', onUpdate: () => {{ q('#n279').textContent = Math.round(ctr.a); q('#n61').textContent = Math.round(ctr.b); }}}}, 22.2);
        tl.fromTo('#s5b', {{opacity: 0}}, {{opacity: 1, duration: .5}}, 23.2);
        qa('#s5 .tile').forEach((t, i) => tl.fromTo(t, {{scale: .4, opacity: 0}}, {{scale: 1, opacity: 1, duration: .3, ease: E}}, 23.3 + i * .025));
        qa('#s5 .tile').forEach((t, i) => tl.to(t, {{x: (1390 - (1140 + (i % 6) * 84)) * .9, y: (440 - (250 + Math.floor(i / 6) * 84)) * .9, opacity: 0, scale: .3, duration: .7, ease: 'power3.in'}}, 24.6 + (i % 7) * .02));
        tl.fromTo('#s5m', {{opacity: 0, scale: .8}}, {{opacity: 1, scale: 1, duration: .6, ease: 'back.out(1.5)'}}, 25.2);
        tl.to('#s5a', {{opacity: 0, duration: .4}}, 25.9); tl.to('#s5b', {{opacity: 0, duration: .4}}, 26.0);
        tl.fromTo('#s5c', {{opacity: 0}}, {{opacity: 1, duration: .3}}, 26.1);
        qa('#s5 .layer').forEach((l, i) => tl.fromTo(l, {{x: 120, opacity: 0}}, {{x: 0, opacity: 1, duration: .45, ease: E}}, 26.2 + i * .28));
        // S6: proof counters
        tl.fromTo('#s6h', {{y: 30, opacity: 0}}, {{y: 0, opacity: 1, duration: .7, ease: E}}, 29.0);
        const vals = [100, 100, 100, 168];
        qa('#s6 .stat').forEach((s, i) => {{
          tl.fromTo(s, {{y: 40, opacity: 0}}, {{y: 0, opacity: 1, duration: .55, ease: E}}, 29.4 + i * .2);
          const o = {{v: 0}}; tl.to(o, {{v: vals[i], duration: 1.1, ease: 'power2.out', onUpdate: () => {{ q('#st' + i).textContent = Math.round(o.v); }}}}, 29.6 + i * .2);
        }});
        tl.fromTo('#s6f', {{opacity: 0}}, {{opacity: 1, duration: .6}}, 30.4);
        // S7: close
        tl.fromTo('#s7l', {{y: 24, opacity: 0}}, {{y: 0, opacity: 1, duration: .8, ease: E}}, 34.9);
        tl.fromTo('#s7h', {{y: 24, opacity: 0}}, {{y: 0, opacity: 1, duration: .8, ease: E}}, 35.5);
        tl.fromTo('#s7c', {{y: 30, opacity: 0}}, {{y: 0, opacity: 1, duration: .7, ease: 'back.out(1.7)'}}, 36.3);
        tl.fromTo('#s7u', {{opacity: 0}}, {{opacity: 1, duration: .6}}, 36.9);
        tl.fromTo('#s7n', {{opacity: 0}}, {{opacity: 1, duration: .6}}, 37.4);
        // captions follow the narration windows
        LINES.forEach(([a, b, t]) => {{
          tl.set('#capt', {{textContent: t}}, a);
          tl.fromTo('#capt', {{opacity: 0, y: 12}}, {{opacity: 1, y: 0, duration: .25, ease: E, immediateRender: false}}, a);
          tl.to('#capt', {{opacity: 0, duration: .2}}, b);
        }});
        tl.to({{}}, {{duration: .01}}, {DUR} - .01);
"""
PROJ.mkdir(parents=True, exist_ok=True)
(PROJ / "index.html").write_text(K.root_html(W, H, DUR, css, body, js, "assets/audio/" + ("mix-with-guide.wav" if GUIDE else "mix-voice-ready.wav")))
(PROJ / "hyperframes.json").write_text(json.dumps({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json", "paths": {"blocks": "compositions", "assets": "assets"}}, indent=2))
(PROJ / "meta.json").write_text(json.dumps({"id": "outspoken-launch", "name": "outspoken-launch"}, indent=2))
if "--audio" in sys.argv:
    print(K.make_audio(PROJ / "assets" / "audio", DUR, CUTS, LINES, chords=[50, 45, 47, 43], bpm=96, seed=1414, events=EVENTS))
K.write_vo(pathlib.Path(__file__).resolve().parent, "Outspoken launch film", DUR, LINES, SCENES, "Narration for a human voice; the synthetic guide voice in the renders is a timing reference only.")
print("built", PROJ / "index.html")
