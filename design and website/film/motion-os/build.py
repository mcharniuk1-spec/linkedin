#!/usr/bin/env python3
"""Outspoken OS motion film (proposed): 28 s, 4:5 1080x1350, a clean motion-design piece of the OS stencil identity system.
Usage: python3 build.py <project_dir> <paths_json> [--guide] [--audio]"""
import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import filmkit as K
PROJ = pathlib.Path(sys.argv[1]); PATHS = sys.argv[2]; GUIDE = "--guide" in sys.argv
W, H, DUR = 1080, 1350, 28.0
CUTS = [6.0, 13.0, 18.2, 24.6]
LINES = [(0.45, 5.45, "Two letters, cut like a stencil. A marigold slash that marks the point."),
         (6.4, 12.6, "Underneath, a system: ground, depth, light, a clean edge, and one card in focus."),
         (13.4, 17.8, "Navy and pearl, a touch of marigold. Three typefaces, each with one job."),
         (18.45, 24.35, "All of it serves one promise. Make the right buyers care about you and what you're building."),
         (24.9, 27.5, "Outspoken. Book an intro call.")]
SCENES = ["S1 the mark", "S2 the system", "S3 palette and type", "S4 the promise", "S5 close"]
EVENTS = [("swoosh", .1), ("riser", 1.15), ("shimmer", 1.75), ("thump", 1.8), ("swoosh", 2.6), ("tick", 3.2, 3, .25), ("pop", 4.0),
          ("pop", 6.2), ("swoosh", 6.7, 5, .95), ("tick", 6.8, 5, .95), ("swoosh", 11.6), ("pop", 13.2, 5, .14), ("thump", 15.4), ("tick", 15.7, 3, .3),
          ("tick", 18.5, 14, .3), ("swoosh", 20.0), ("shimmer", 20.05), ("pop", 20.45, 4, .06), ("swoosh", 24.8), ("thump", 25.4), ("tick", 25.5)]
parts = K.mark_parts(PATHS)
css = """
.sc{position:absolute;inset:0;opacity:0}
#s1{opacity:1}
.pearl{position:absolute;inset:0;background:linear-gradient(165deg,#fff 10%,#F1F3F6 62%,#E8EDF2)}
.deep{position:absolute;inset:0;background:radial-gradient(900px 760px at 84% 8%,rgba(49,87,213,.26),transparent 62%),radial-gradient(760px 640px at 4% 98%,rgba(234,169,60,.10),transparent 60%),#0D1A3B}
.dots{position:absolute;inset:0;background:radial-gradient(rgba(22,39,96,.13) 2.4px,transparent 3.4px) 0 0/44px 44px}
.dots.lt{background:radial-gradient(rgba(241,243,246,.11) 2.4px,transparent 3.4px) 0 0/44px 44px}
.mono{font-family:'Geist Mono',monospace;font-weight:500;letter-spacing:.08em;text-transform:uppercase}
.disp{font-family:'Fraunces',serif;font-weight:400;letter-spacing:-.02em;line-height:1.05}
.ctr{position:absolute;left:0;right:0;text-align:center}
#cutln{position:absolute;left:-460px;top:595px;width:2000px;height:4px;background:#EAA93C;transform-origin:50% 50%;transform:rotate(-56deg) scaleX(0);opacity:.9}
.lead{position:absolute;height:2px;background:#666F7F;transform-origin:0 50%;transform:scaleX(0)}
.tag{position:absolute;font-size:28px;color:#3A4A75;opacity:0}
.lyr{position:absolute;width:560px;height:330px;border-radius:24px;overflow:hidden;opacity:0;box-shadow:0 26px 48px -30px rgba(0,0,0,.8)}
.lbl{position:absolute;left:70px;font-size:28px;color:#B9C7DA;opacity:.0}
.lbl b{font-weight:500;color:#F3C15D}
.sw{position:absolute;width:170px;height:420px;border-radius:20px;transform-origin:50% 100%;transform:scaleY(0)}
.swn{position:absolute;width:190px;font-size:30px;color:#162760;opacity:0}
.swn span{display:block;font-family:'Geist Mono',monospace;font-size:28px;color:#3A4A75;margin-top:4px}
.spec{position:absolute;font-size:36px;color:#162760;opacity:0}
.w{display:inline-block;opacity:0}
.sel{position:relative;display:inline-block;margin:0 .2em;padding:0 .12em;border-radius:12px;color:#F2F5FA;background:linear-gradient(#F6D591,#F6D591) left center/0% 100% no-repeat;outline:3px dashed rgba(242,245,250,0);outline-offset:12px}
.sel i{position:absolute;width:22px;height:22px;background:#0D1A3B;border:3px solid #F2F5FA;border-radius:4px;opacity:0;transform:scale(.3)}
.sel i:nth-of-type(1){left:-22px;top:-20px}.sel i:nth-of-type(2){right:-22px;top:-20px}.sel i:nth-of-type(3){left:-22px;bottom:-20px}.sel i:nth-of-type(4){right:-22px;bottom:-20px}
.cta{position:absolute;left:50%;transform:translateX(-50%);top:790px;height:100px;padding:0 48px;border-radius:999px;background:#EAA93C;color:#0D1A3B;display:flex;align-items:center;gap:18px;font-size:40px;font-weight:600;white-space:nowrap;opacity:0}
#wipe{position:absolute;top:-20%;height:140%;width:2600px;left:0;transform:translateX(-2800px) skewX(-18deg);z-index:50;opacity:0}
#wipe i{position:absolute;right:0;top:0;bottom:0;width:26px;background:#EAA93C}
#cap{position:absolute;left:0;right:0;bottom:56px;display:flex;justify-content:center;z-index:60}
#cap span{max-width:960px;padding:14px 26px;border-radius:16px;background:rgba(13,26,59,.78);color:#F1F3F6;font-size:34px;line-height:1.3;text-align:center;opacity:0}
"""
def sc(i, ground, inner): return f'<div class="sc" id="s{i}"><div class="{ground}"></div><div class="dots{" lt" if ground == "deep" else ""}"></div>{inner}</div>'
s1 = sc(1, "pearl", '<div class="mono ctr" id="s1k" style="top:150px;font-size:28px;color:#3A4A75">OUTSPOKEN · OS mark</div>'
        f'<div id="s1m" style="position:absolute;left:260px;top:330px">{K.mark_svg(parts, "m1", width=560)}</div><div id="cutln"></div>'
        '<div class="lead" id="ld1" style="left:250px;top:720px;width:120px;transform:rotate(90deg) scaleX(0)"></div>'
        '<div class="tag mono" id="tg1" style="left:120px;top:850px">stencil cut</div>'
        '<div class="tag mono" id="tg2" style="left:470px;top:850px">marigold slash</div>'
        '<div class="tag mono" id="tg3" style="left:770px;top:850px">Nickel 600</div>'
        '<div class="disp ctr" id="s1h" style="top:990px;font-size:64px;color:#162760;opacity:0">Two letters. One point.</div>')
LY = [("Ground", "background:#13224f;background-image:radial-gradient(rgba(241,243,246,.16) 2.4px,transparent 3.4px);background-size:40px 40px"),
      ("Far · watermark", "background:#13224f"), ("Mid · glow", "background:radial-gradient(300px 220px at 60% 45%,rgba(49,87,213,.55),transparent 70%),#13224f"),
      ("Edge · slash seam", "background:#13224f"), ("Front · card", "background:#F2F5FA")]
lyrs = []
for k, (nm, st) in enumerate(LY):
    inner = ""
    if k == 1: inner = K.mark_svg(parts, f"wm{k}", o="#F2F5FA", s="#F2F5FA", g="#F2F5FA", width=520, extra="position:absolute;left:30px;top:70px;opacity:.12")
    if k == 3: inner = '<div style="position:absolute;left:-40px;top:150px;width:700px;height:3px;background:#B9C7DA;transform:rotate(-4deg)"></div><div style="position:absolute;left:230px;top:118px;width:70px;height:6px;background:#EAA93C;transform:rotate(-56deg)"></div>'
    if k == 4: inner = '<div class="mono" style="position:absolute;left:34px;top:30px;font-size:28px;color:#3A4A75">Founder voice</div><div style="position:absolute;left:34px;top:96px;width:380px;height:22px;border-radius:11px;background:#D9DEE7"></div><div style="position:absolute;left:34px;top:136px;width:300px;height:22px;border-radius:11px;background:#E4E8EF"></div><div style="position:absolute;left:34px;top:206px;width:170px;height:58px;border-radius:29px;background:#162760"></div>'
    lyrs.append(f'<div class="lyr" style="left:{388 + k * 22}px;top:{300 + k * 84}px;{st}">{inner}</div>')
    lyrs.append(f'<div class="lbl mono" id="lb{k}" style="top:{318 + k * 84}px"><b>0{k + 1}</b> {nm}</div>')
s2 = sc(2, "deep", '<div class="disp" id="s2h" style="position:absolute;left:70px;top:130px;font-size:64px;color:#F2F5FA;opacity:0">The system underneath.</div>' + "".join(lyrs))
PAL = [("Navy", "#162760", "#162760"), ("Deep navy", "#0D1A3B", "#0D1A3B"), ("Pearl", "#F1F3F6", "#F1F3F6;border:2px solid #D9DEE7"), ("Marigold", "#EAA93C", "#EAA93C"), ("Nickel 600", "#666F7F", "#666F7F")]
sw = "".join(f'<div class="sw" style="left:{70 + i * 190}px;top:250px;background:{bg}"></div><div class="swn" style="left:{70 + i * 190}px;top:690px">{n}<span>{hx}</span></div>' for i, (n, hx, bg) in enumerate(PAL))
s3 = sc(3, "pearl", '<div class="mono" style="position:absolute;left:70px;top:150px;font-size:28px;color:#3A4A75">Palette</div>' + sw +
        '<div class="disp" id="aa" style="position:absolute;left:62px;top:850px;font-size:230px;color:#162760;opacity:0">Aa</div>'
        '<div class="spec" style="left:400px;top:900px;font-family:Fraunces">Fraunces · display</div>'
        '<div class="spec" style="left:400px;top:972px">Mona Sans · text</div>'
        '<div class="spec mono" style="left:400px;top:1046px;font-size:32px">Geist Mono · labels</div>')
words = ["Make", "the", "right", "<br>", "buyers", "@care", "about", "<br>", "you", "and", "what", "<br>", "you’re", "building."]
hl = " ".join("<br>" if w == "<br>" else (f'<span class="w"><span class="sel" id="selc">care<i></i><i></i><i></i><i></i></span></span>' if w.startswith("@") else f'<span class="w">{w}</span>') for w in words)
s4 = sc(4, "deep", f'<div class="disp ctr" style="top:330px;font-size:100px;line-height:1.2;color:#F2F5FA">{hl}</div>')
s5 = sc(5, "deep", '<img id="s5l" src="assets/brand/lockup-os-inverse.svg" style="position:absolute;left:50%;top:450px;width:820px;transform:translateX(-50%);opacity:0">'
        '<div class="cta" id="s5c">Book an intro call <svg width="34" height="34" viewBox="0 0 14 14" fill="none"><path d="M3 11 11 3M5 3h6v6" stroke="#0D1A3B" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg></div>'
        '<div class="ctr" id="s5n" style="top:1000px;font-size:28px;color:#B9C7DA;opacity:0">Proposed. Music and guide voice are synthetic.</div>')
body = "\n".join([s1, s2, s3, s4, s5, '<div id="wipe"><i></i></div>', '<div id="cap"><span id="capt"></span></div>'])
GROUND = {1: "#F1F3F6", 2: "#0D1A3B", 3: "#F1F3F6", 4: "#0D1A3B", 5: "#0D1A3B"}
js = f"""
        const CUTS = {json.dumps(CUTS)}, LINES = {json.dumps(LINES)}, GROUND = {json.dumps(GROUND)};
        const q = (s) => document.querySelector(s), qa = (s) => document.querySelectorAll(s);
        // S1: the halves close, the S settles, a cut line crosses and leaves the slash
        tl.fromTo('#m1 .ol', {{x: -8}}, {{x: 0, duration: 1.1, ease: E}}, .1);
        tl.fromTo('#m1 .or', {{x: 8}}, {{x: 0, duration: 1.1, ease: E}}, .1);
        tl.fromTo('#m1 .ms', {{x: 16}}, {{x: 0, duration: 1.1, ease: E}}, .3);
        tl.fromTo('#cutln', {{scaleX: 0, opacity: .9}}, {{scaleX: 1, duration: .45, ease: 'power3.in'}}, 1.35);
        tl.fromTo('#m1 .mg', {{scaleX: 0, transformOrigin: '0% 50%'}}, {{scaleX: 1, duration: .35, ease: 'power3.out'}}, 1.75);
        tl.to('#cutln', {{opacity: 0, duration: .35}}, 1.85);
        tl.to('#s1m', {{scale: .9, y: -30, duration: 1.0, ease: E, transformOrigin: '50% 50%'}}, 2.6);
        qa('#s1 .tag').forEach((g, i) => tl.fromTo(g, {{opacity: 0, y: 14}}, {{opacity: 1, y: 0, duration: .5, ease: E}}, 3.2 + i * .25));
        tl.fromTo('#s1h', {{opacity: 0, y: 24}}, {{opacity: 1, y: 0, duration: .7, ease: E}}, 4.0);
        // scene seams: a slash panel in the next ground colour with a marigold leading edge
        CUTS.forEach((c, k) => {{
          tl.set('#wipe', {{backgroundColor: GROUND[k + 2], opacity: 1}}, c - .5);
          tl.fromTo('#wipe', {{x: -2800}}, {{x: -400, duration: .5, ease: 'power2.in', immediateRender: false}}, c - .5);
          tl.set('#s' + (k + 1), {{opacity: 0}}, c); tl.set('#s' + (k + 2), {{opacity: 1}}, c);
          tl.to('#wipe', {{opacity: 0, duration: .4, ease: 'power1.out'}}, c + .02);
        }});
        // S2: five depth layers, each with its label
        tl.fromTo('#s2h', {{opacity: 0, y: 24}}, {{opacity: 1, y: 0, duration: .7, ease: E}}, 6.2);
        qa('#s2 .lyr').forEach((l, i) => tl.fromTo(l, {{opacity: 0, y: 70}}, {{opacity: 1, y: 0, duration: .6, ease: E}}, 6.7 + i * .95));
        qa('#s2 .lbl').forEach((l, i) => {{ tl.fromTo(l, {{opacity: 0, x: -14}}, {{opacity: 1, x: 0, duration: .45, ease: E}}, 6.8 + i * .95); }});
        tl.to('#s2 .lyr', {{y: (i) => -i * 10, duration: 1.2, ease: E}}, 11.6);
        // S3: palette grows, then type
        qa('#s3 .sw').forEach((s, i) => tl.fromTo(s, {{scaleY: 0}}, {{scaleY: 1, duration: .7, ease: E}}, 13.2 + i * .14));
        qa('#s3 .swn').forEach((s, i) => tl.fromTo(s, {{opacity: 0, y: 12}}, {{opacity: 1, y: 0, duration: .45, ease: E}}, 13.7 + i * .14));
        tl.fromTo('#aa', {{opacity: 0, y: 30}}, {{opacity: 1, y: 0, duration: .8, ease: E}}, 15.4);
        qa('#s3 .spec').forEach((s, i) => tl.fromTo(s, {{opacity: 0, x: 20}}, {{opacity: 1, x: 0, duration: .5, ease: E}}, 15.7 + i * .3));
        // S4: the promise, word by word, with the selection marker on 'care'
        qa('#s4 .w').forEach((w, i) => tl.fromTo(w, {{opacity: 0, y: 34}}, {{opacity: 1, y: 0, duration: .5, ease: E}}, 18.5 + i * .3));
        tl.to('#selc', {{backgroundSize: '100% 100%', color: '#0D1A3B', duration: .5, ease: E}}, 20.0);
        tl.to('#selc', {{outlineColor: 'rgba(242,245,250,.75)', duration: .3}}, 20.35);
        tl.to('#selc i', {{opacity: 1, scale: 1, duration: .3, ease: 'back.out(2)', stagger: .06}}, 20.45);
        // S5: lockup and the call to action
        tl.fromTo('#s5l', {{opacity: 0, y: 24}}, {{opacity: 1, y: 0, duration: .8, ease: E}}, 24.8);
        tl.fromTo('#s5c', {{opacity: 0, y: 30}}, {{opacity: 1, y: 0, duration: .7, ease: 'back.out(1.7)'}}, 25.4);
        tl.fromTo('#s5n', {{opacity: 0}}, {{opacity: 1, duration: .6}}, 25.5);
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
(PROJ / "meta.json").write_text(json.dumps({"id": "outspoken-os-motion", "name": "outspoken-os-motion"}, indent=2))
if "--audio" in sys.argv:
    print(K.make_audio(PROJ / "assets" / "audio", DUR, CUTS, LINES, chords=[52, 57, 48, 55], bpm=84, seed=2026, rate=165, events=EVENTS))
K.write_vo(pathlib.Path(__file__).resolve().parent, "Outspoken OS motion film", DUR, LINES, SCENES, "Narration for a human voice; the synthetic guide voice in the renders is a timing reference only.")
print("built", PROJ / "index.html")
