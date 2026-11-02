#!/usr/bin/env python3
"""Outspoken launch film R15 (proposed): 42 s, 16:9 1920x1080, HyperFrames root composition generated from this script.
One marigold strand carries the founder's material through eight stages (Codex FILM-DIRECTION-R15, 2 November 2026):
thought, interview, position, market, plan, create, conversations, packages. Objects keep identity across each seam;
transitions use path morph, mask reveal, camera travel and parallax, a 3D fold and clipped colour fields.
Usage: python3 build.py <project_dir> <paths_json> [--audio] [--guide]"""
import sys, pathlib, json, math, random
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import filmkit as K
PROJ = pathlib.Path(sys.argv[1]); PATHS = sys.argv[2]; GUIDE = "--guide" in sys.argv
SITE = pathlib.Path(__file__).resolve().parents[2] / "website" / "website-v3"
PROT = json.loads((SITE / "content.json").read_text())["protected"]
PRICING = json.loads((SITE / "pricing.json").read_text())
W, H, DUR = 1920, 1080, 42.0
CUTS = [5.0, 10.0, 14.0, 19.0, 24.0, 29.0, 34.0]
LINES = [(0.35, 4.6, "Your best material starts with the work."),
         (5.3, 9.6, "We listen to how you build and decide."),
         (10.3, 13.6, "Together, we find a clear position."),
         (14.3, 18.6, "We map the market and the buyer’s questions."),
         (19.3, 23.6, "We plan the ideas, evidence and formats."),
         (24.3, 28.6, "We shape them into content in your voice."),
         (29.3, 33.7, "We prepare the next conversation and review the response."),
         (34.5, 37.8, "Choose the right starting point.")]
SCENES = ["S1 thought", "S2 interview", "S3 position", "S4 market", "S5 plan", "S6 create", "S7 conversations", "S8 packages"]
EVENTS = [("shimmer", .2), ("tick", 1.5, 12, .17), ("swoosh", 4.15), ("pop", 4.9), ("tick", 5.9, 10, .17), ("pop", 7.7), ("pop", 7.95), ("pop", 8.2),
          ("swoosh", 10.0), ("thump", 10.8), ("riser", 11.2), ("thump", 11.85), ("shimmer", 12.6), ("swoosh", 14.0), ("tick", 15.6, 3, .45),
          ("riser", 18.0), ("thump", 19.0), ("tick", 20.0, 20, .13), ("swoosh", 24.1), ("pop", 24.9), ("pop", 25.15), ("pop", 25.4), ("swoosh", 26.6, 3, .18),
          ("riser", 27.7), ("thump", 28.4), ("tick", 29.4, 3, .3), ("pop", 30.4, 12, .1), ("tick", 31.5, 9, .12), ("swoosh", 34.0), ("pop", 35.0), ("pop", 35.35),
          ("pop", 35.7), ("shimmer", 36.8), ("swoosh", 37.8), ("thump", 38.5), ("pop", 39.1), ("shimmer", 39.15)]
rnd = random.Random(1515)
N = 64
def path(pts): return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
def line(x0, y0, x1, y1): return path([(x0 + (x1 - x0) * i / (N - 1), y0 + (y1 - y0) * i / (N - 1)) for i in range(N)])
def wave(ph, amp, x0=360, x1=1560, y=540):
    out = []
    for i in range(N):
        u = i / (N - 1)
        out.append((x0 + (x1 - x0) * u, y + amp * math.sin(2 * math.pi * 6 * u + ph) * math.sin(math.pi * u) ** 1.2 * (.6 + .4 * math.sin(5 * u + ph))))
    return path(out)
def curve(x0, x1, y, bend):
    return path([(x0 + (x1 - x0) * i / (N - 1), y + bend * math.sin(math.pi * i / (N - 1))) for i in range(N)])
SH = {"flat": line(360, 540, 1560, 540), "w1": wave(0, 150), "w2": wave(1.9, 115), "w3": wave(3.6, 160), "thread": curve(360, 1560, 540, 0),
      "slash": line(880, 700, 1050, 390), "lens": line(-40, 540, 1960, 540), "cal": line(325, 262, 1595, 262),
      "cards": curve(300, 1620, 880, 26), "net": curve(560, 1760, 540, -60), "under": line(240, 930, 1680, 930)}
# S1 particles: random field -> three structured clusters -> the strand
CL = [(560, 500, "Experience"), (960, 450, "Product decisions"), (1360, 500, "Evidence")]
parts_xy = []
for i in range(96):
    c = CL[i % 3]; k = i // 3; ring = 1 + k // 10; ang = (k % 10) / 10 * 2 * math.pi + ring * .5
    parts_xy.append({"s": [rnd.uniform(80, 1840), rnd.uniform(80, 1000)], "c": [c[0] + math.cos(ang) * 34 * ring, c[1] + math.sin(ang) * 34 * ring],
                     "l": [360 + 1200 * (i / 95), 540]})
# S5 calendar grid, S6 three cells lift into cards
KINDS = ["Theme", "Proof", "Format", "Post", "Carousel", "Video"]
cells = []
for r in range(4):
    for c in range(6):
        cells.append({"x": 325 + c * 214, "y": 300 + r * 132, "w": 200, "h": 118, "t": KINDS[(r * 2 + c) % 6], "on": (r * 6 + c) not in (5, 13, 22)})
LIFT = [7, 9, 16]
CARDS = [{"x": 300, "y": 330, "w": 400, "h": 440, "t": "Founder profile"}, {"x": 760, "y": 290, "w": 400, "h": 500, "t": "Post"},
         {"x": 1220, "y": 330, "w": 400, "h": 440, "t": "Carousel"}]
# S7 buyer nodes and the instrument rings
NODES = []
for i in range(12):
    a = -1.25 + i * (2.5 / 11); rr = 300 + (i % 3) * 95
    NODES.append([1260 + math.cos(a) * rr * .95, 540 + math.sin(a) * rr * .78])
RINGS = [(420, 330, "Engagement"), (420, 540, "Qualified replies"), (420, 750, "Attributed leads")]
PK = PRICING["packages"][:3]
PKR = [{"x": 240 + i * 500, "y": 300, "w": 440, "h": 470} for i in range(3)]
CFG = {"parts": parts_xy, "sh": SH, "cells": cells, "lift": LIFT, "cards": CARDS, "nodes": NODES, "rings": [[x, y] for x, y, _ in RINGS], "pkr": PKR}
mk = K.mark_parts(PATHS)
MW = 600; MH = MW * mk[1] / mk[0]

css = """
.g{position:absolute;inset:0}
#gN{background:radial-gradient(1100px 800px at 82% 12%,rgba(49,87,213,.24),transparent 62%),radial-gradient(900px 700px at 6% 96%,rgba(234,169,60,.09),transparent 60%),#0D1A3B}
.pearl{background:linear-gradient(160deg,#fff 8%,#F1F3F6 60%,#E6EBF1)}
.navy{background:radial-gradient(1000px 760px at 20% 10%,rgba(49,87,213,.22),transparent 60%),#0D1A3B}
#gA{clip-path:circle(0% at 50% 50%)}
#gB{clip-path:polygon(0% 100%,0% 100%,0% 100%,0% 100%)}
#gBb{background:#EAA93C;clip-path:polygon(0% 100%,0% 100%,0% 100%,0% 100%)}
#gC{clip-path:inset(0% 0% 100% 0%)}
#gD{clip-path:circle(0% at 960px 540px)}
#cam{position:absolute;inset:0;transform-origin:50% 50%}
.sc{position:absolute;inset:0;opacity:0}
#c1{opacity:1}
.mono{font-family:'Geist Mono',monospace;font-weight:500;letter-spacing:.08em;text-transform:uppercase}
.disp{font-family:'Fraunces',serif;font-weight:400;letter-spacing:-.02em;line-height:1.06}
.kick{position:absolute;left:120px;top:96px;font-size:30px;opacity:0}
.lt{color:#B9C7DA}.dk{color:#3A4A75}
.pt{position:absolute;left:-7px;top:-7px;width:14px;height:14px;border-radius:50%;background:#F2F5FA;opacity:0}
.pt.m{background:#EAA93C}.pt.s{background:#B9C7DA}
.cl{position:absolute;width:420px;margin-left:-210px;text-align:center;font-size:30px;color:#F2F5FA;opacity:0}
#sv{position:absolute;inset:0;z-index:30;overflow:visible}
#strand{fill:none;stroke:#EAA93C;stroke-width:7;stroke-linecap:round;stroke-linejoin:round}
.src{position:absolute;width:380px;height:300px;margin-left:-190px;margin-top:-150px;border-radius:26px;background:#fff;border:2px solid #E1E6EE;box-shadow:0 26px 50px -30px rgba(22,39,96,.55);opacity:0;transform-origin:50% 50%}
.src b{position:absolute;left:32px;top:30px;font-family:'Geist Mono',monospace;font-weight:500;font-size:28px;color:#666F7F;letter-spacing:.06em}
.src p{position:absolute;left:32px;right:28px;bottom:34px;font-family:'Fraunces',serif;font-size:42px;line-height:1.1;color:#162760}
#mkw{position:absolute;left:%MX%px;top:%MY%px;width:%MW%px;height:%MH%px;opacity:0;z-index:31}
#pos{position:absolute;left:0;right:0;top:770px;text-align:center;font-size:84px;color:#F2F5FA;opacity:0}
.mkt{position:absolute;left:0;top:0;width:3000px;height:1080px}
.mkt svg{position:absolute;inset:0;overflow:visible}
.mkt path{fill:none;stroke-width:4;stroke-linecap:round}
#ring{position:absolute;left:760px;top:340px;width:400px;height:400px;border-radius:50%;border:7px solid #EAA93C;opacity:0;z-index:32}
.q{position:absolute;padding:16px 28px;border-radius:18px;background:rgba(242,245,250,.10);border:2px solid rgba(185,199,218,.35);color:#F2F5FA;font-size:32px;white-space:nowrap;opacity:0}
#calw{position:absolute;inset:0;perspective:1700px;perspective-origin:50% 0%}
#cal{position:absolute;inset:0;transform-origin:50% 262px;transform-style:preserve-3d}
.cell{position:absolute;border-radius:16px;background:rgba(22,39,96,.05);border:2px solid #D9DEE7}
.cell i{position:absolute;inset:8px;border-radius:11px;opacity:0;display:flex;align-items:center;justify-content:center;font-style:normal;font-family:'Geist Mono',monospace;font-weight:500;font-size:31px;letter-spacing:.03em}
.k-Theme i{background:#162760;color:#F2F5FA}.k-Proof i{background:#FFF6E3;color:#162760;box-shadow:inset 0 0 0 3px #EAA93C}.k-Format i{background:#E6EBF1;color:#3A4A75}
.k-Post i{background:#162760;color:#F6D591}.k-Carousel i{background:#fff;color:#162760;box-shadow:inset 0 0 0 2px #B9C7DA}.k-Video i{background:#EAA93C;color:#0D1A3B}
.lift{position:absolute;border-radius:26px;transform-origin:0 0;background:#fff;border:2px solid #E1E6EE;box-shadow:0 30px 60px -34px rgba(22,39,96,.6);opacity:0;overflow:hidden}
.lift .tt{position:absolute;left:34px;bottom:30px;font-family:'Fraunces',serif;font-size:46px;color:#162760;opacity:0}
.lift .ln{position:absolute;left:34px;height:16px;border-radius:8px;background:#E1E6EE;opacity:0}
.lift .av{position:absolute;left:34px;top:34px;width:110px;height:110px;border-radius:50%;background:#162760;opacity:0}
.lift .av::after{content:'';position:absolute;right:-6px;bottom:6px;width:30px;height:30px;border-radius:50%;background:#EAA93C}
.pg{position:absolute;left:34px;top:34px;width:250px;height:250px;border-radius:14px;opacity:0;transform-origin:0% 50%}
.node{position:absolute;width:34px;height:34px;margin:-17px 0 0 -17px;border-radius:50%;border:4px solid #B9C7DA;background:#0D1A3B;opacity:0}
.sig{position:absolute;left:0;top:0;width:16px;height:16px;margin:-8px 0 0 -8px;border-radius:50%;background:#F6D591;opacity:0}
.rg{position:absolute;width:140px;height:140px;margin:-70px 0 0 -70px;border-radius:50%;border:5px solid #B9C7DA;opacity:0}
.rl{position:absolute;left:530px;font-size:34px;color:#F2F5FA;opacity:0;white-space:nowrap}
#ins{position:absolute;left:120px;top:900px;font-size:31px;opacity:0}
.pk{position:absolute;border:5px solid #EAA93C;border-radius:28px;opacity:0;overflow:hidden;transform-origin:0 0}
.pk .in{position:absolute;inset:0;padding:40px 38px;opacity:0}
.pk h3{font-family:'Fraunces',serif;font-weight:400;font-size:48px;line-height:1.05;color:#162760}
.pk .pr{margin-top:22px;font-family:'Geist Mono',monospace;font-weight:500;font-size:46px;color:#162760;letter-spacing:-.02em}
.pk .pe{font-family:'Geist Mono',monospace;font-size:28px;color:#666F7F;letter-spacing:.06em;text-transform:uppercase}
.pk .ds{margin-top:26px;font-size:30px;line-height:1.3;color:#3A4A75}
.pk .ac{position:absolute;left:38px;right:38px;bottom:38px;height:8px;border-radius:4px;background:#EAA93C;transform:scaleX(0);transform-origin:0 50%}
#pkl{position:absolute;left:0;right:0;top:206px;text-align:center;font-size:30px;opacity:0}
#lock{position:absolute;left:50%;top:250px;width:560px;margin-left:-280px;opacity:0}
#hero{position:absolute;left:260px;right:260px;top:420px;text-align:center;font-size:64px;color:#F2F5FA;opacity:0}
#cta{position:absolute;left:50%;top:690px;transform:translateX(-50%);height:96px;padding:0 54px;border-radius:999px;background:#EAA93C;color:#0D1A3B;font-size:38px;font-weight:600;display:flex;align-items:center;white-space:nowrap;opacity:0}
#note{position:absolute;left:0;right:0;top:830px;text-align:center;font-size:28px;opacity:0}
#cap{position:absolute;left:0;right:0;bottom:44px;display:flex;justify-content:center;z-index:60}
#cap span{max-width:1500px;padding:14px 30px;border-radius:16px;background:rgba(13,26,59,.80);color:#F1F3F6;font-size:34px;line-height:1.3;text-align:center;opacity:0}
""".replace("%MX%", f"{(W - MW) / 2:.1f}").replace("%MY%", f"{540 - MH / 2 - 40:.1f}").replace("%MW%", str(MW)).replace("%MH%", f"{MH:.1f}")

def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;")
def rect(d): return f'left:{d["x"]}px;top:{d["y"]}px;width:{d["w"]}px;height:{d["h"]}px'
mkt_paths = []
for layer, (col, op, n) in enumerate([("#B9C7DA", .22, 5), ("#B9C7DA", .34, 4), ("#666F7F", .55, 3)]):
    ps = []
    for j in range(n):
        y0 = 180 + (j + .5) * 720 / n + layer * 22; pts = []
        for i in range(N):
            x = -100 + 3200 * i / (N - 1); pts.append((x, y0 + 60 * math.sin(x / (380 + 90 * layer) + j * 1.7 + layer)))
        ps.append(path(pts))
    mkt_paths.append((layer, col, op, ps))
mkt_html = "".join(
    f'<div class="mkt" id="mk{L}"><svg viewBox="0 0 3000 1080" width="3000" height="1080">'
    + "".join(f'<path d="{p}" stroke="{col}" opacity="{op}"/>' for p in ps)
    + f'</svg><svg class="hl" viewBox="0 0 3000 1080" width="3000" height="1080" style="clip-path:circle(196px at 960px 540px)">'
    + "".join(f'<path d="{p}" stroke="#EAA93C" opacity=".95"/>' for p in ps) + '</svg></div>'
    for L, col, op, ps in mkt_paths)
pk_html = "".join(
    f'<div class="pk" id="pk{i}" style="{rect(PKR[i])}"><div class="in"><h3>{esc(p["name"])}</h3>'
    f'<div class="pr">{esc(p["display_price"].split(" /")[0])}</div><div class="pe">{"one-off" if p["period"] == "one-off" else "per month"}</div>'
    f'<div class="ds">{esc(p["descriptor"])}</div></div><div class="ac"></div></div>' for i, p in enumerate(PK))
body = f"""
      <div class="g" id="gN"></div><div class="g pearl" id="gA"></div><div class="g" id="gBb"></div><div class="g navy" id="gB"></div><div class="g pearl" id="gC"></div><div class="g navy" id="gD"></div>
      <div id="cam">
        <div class="sc" id="c1">
          {''.join(f'<div class="pt{" m" if i % 7 == 0 else (" s" if i % 3 == 1 else "")}" id="p{i}"></div>' for i in range(len(parts_xy)))}
          {''.join(f'<div class="cl mono" id="cl{i}" style="left:{x}px;top:{y + 150}px">{t}</div>' for i, (x, y, t) in enumerate(CL))}
          <div class="kick mono lt" id="k1">Your thinking</div>
        </div>
        <div class="sc" id="c2">
          <div class="kick mono dk" id="k2">Interview</div>
          <div class="src" id="sc0" style="left:560px;top:540px"><b>01</b><p>A product decision</p></div>
          <div class="src" id="sc1" style="left:960px;top:540px"><b>02</b><p>A customer question</p></div>
          <div class="src" id="sc2" style="left:1360px;top:540px"><b>03</b><p>The proof behind it</p></div>
        </div>
        <div class="sc" id="c3"><div class="disp" id="pos">Position</div></div>
        <div class="sc" id="c4">
          {mkt_html}
          <div class="kick mono lt" id="k4">Market</div>
          <div class="q" id="q0" style="left:250px;top:250px">Why does this matter now?</div>
          <div class="q" id="q1" style="left:1240px;top:210px">What changes for my team?</div>
          <div class="q" id="q2" style="left:1150px;top:800px">Why trust this founder?</div>
        </div>
        <div class="sc" id="c5">
          <div class="kick mono dk" id="k5">Plan</div>
          <div id="calw"><div id="cal">{''.join(f'<div class="cell k-{c["t"]}" id="ce{i}" style="left:{c["x"]}px;top:{c["y"]}px;width:{c["w"]}px;height:{c["h"]}px"><i>{c["t"] if c["on"] else ""}</i></div>' for i, c in enumerate(cells))}</div></div>
        </div>
        <div class="sc" id="c6">
          <div class="kick mono dk" id="k6">Create</div>
          <div class="lift" id="lf0" style="{rect(CARDS[0])}"><div class="av"></div><div class="ln" style="top:176px;width:300px"></div><div class="ln" style="top:212px;width:240px"></div><div class="ln" style="top:248px;width:270px"></div><div class="tt">{CARDS[0]["t"]}</div></div>
          <div class="lift" id="lf1" style="{rect(CARDS[1])}"><div class="ln" style="top:44px;width:320px;background:#162760"></div><div class="ln" style="top:84px;width:300px"></div><div class="ln" style="top:120px;width:320px"></div><div class="ln" style="top:156px;width:250px"></div><div class="ln" style="top:192px;width:290px"></div><div class="tt">{CARDS[1]["t"]}</div></div>
          <div class="lift" id="lf2" style="{rect(CARDS[2])}"><div class="pg" style="background:#162760"></div><div class="pg" style="background:#F6D591"></div><div class="pg" style="background:#E6EBF1"></div><div class="tt">{CARDS[2]["t"]}</div></div>
        </div>
        <div class="sc" id="c7">
          <div class="kick mono lt" id="k7">Conversations</div>
          {''.join(f'<div class="node" id="nd{i}" style="left:{x:.0f}px;top:{y:.0f}px"></div>' for i, (x, y) in enumerate(NODES))}
          {''.join(f'<div class="sig" id="sg{i}"></div>' for i in range(9))}
          {''.join(f'<div class="rg" id="rg{i}" style="left:{x}px;top:{y}px"></div><div class="rl" id="rl{i}" style="top:{y - 24}px">{t}</div>' for i, (x, y, t) in enumerate(RINGS))}
          <div class="mono lt" id="ins">Each measure reviewed on its own</div>
        </div>
        <div class="sc" id="c8">
          <div class="mono lt" id="pkl">{esc(PRICING["public_label"])}</div>
          {pk_html}
          <img id="lock" src="assets/brand/lockup-os-inverse.svg" alt="">
          <div class="disp" id="hero">{esc(PROT["hero"])}</div>
          <div id="cta">{esc(PROT["cta"])}</div>
        </div>
      </div>
      <div id="mkw">{K.mark_svg(mk, "mk", width=MW)}</div>
      <svg id="sv" viewBox="0 0 {W} {H}" width="{W}" height="{H}"><path id="strand" d="{SH['flat']}" opacity="0"/></svg>
      <div id="cap"><span id="capt"></span></div>
"""
js = "const CFG = " + json.dumps(CFG) + ";\nconst LINES = " + json.dumps(LINES) + ";\n" + """
        const q = s => document.querySelector(s), qa = s => [...document.querySelectorAll(s)];
        const SM = 'power3.inOut', SO = 'power3.out';
        const show = (id, t) => tl.set(id, {opacity: 1}, t), hide = (id, t) => tl.set(id, {opacity: 0}, t);
        // S1 0-5: particles drift in, assemble into three clusters, then line up as the strand
        tl.fromTo('#cam', {scale: 1, x: 0}, {scale: 1.07, duration: 5, ease: 'sine.inOut'}, 0);
        CFG.parts.forEach((p, i) => {
          const el = q('#p' + i);
          tl.fromTo(el, {x: p.s[0], y: p.s[1], opacity: 0, scale: .4}, {opacity: .9, scale: 1, duration: .9, ease: SO}, .1 + (i % 24) * .03);
          tl.to(el, {x: p.c[0], y: p.c[1], duration: 1.6, ease: SM}, 1.3 + (i % 12) * .035);
          tl.to(el, {x: p.l[0], y: p.l[1], duration: 1.0, ease: 'power2.in'}, 3.9 + (i % 16) * .012);
        });
        CFG.parts.forEach((p, i) => tl.to('#p' + i, {opacity: 0, duration: .25}, 5.0));
        qa('.cl').forEach((c, i) => { tl.fromTo(c, {opacity: 0, y: 14}, {opacity: 1, y: 0, duration: .5, ease: SO}, 2.6 + i * .15); tl.to(c, {opacity: 0, duration: .3}, 3.8); });
        tl.fromTo('#k1', {opacity: 0}, {opacity: 1, duration: .5}, .6); tl.to('#k1', {opacity: 0, duration: .3}, 3.9);
        // seam 1: pearl ground bleeds out from the strand as a circle; the strand draws over the particles
        tl.fromTo('#gA', {clipPath: 'circle(0% at 50% 50%)'}, {clipPath: 'circle(75% at 50% 50%)', duration: 1.2, ease: SM}, 4.2);
        tl.fromTo('#strand', {opacity: 0, strokeDasharray: '1300 1300', strokeDashoffset: 1300}, {opacity: 1, strokeDashoffset: 0, duration: .8, ease: SO}, 4.45);
        tl.set('#strand', {strokeDasharray: 'none'}, 5.3);
        tl.to('#cam', {scale: 1, duration: .6, ease: SO}, 5.0);
        hide('#c1', 5.4); show('#c2', 5.0);
        // S2 5-10: the strand becomes an interview waveform, then folds into three source cards
        tl.fromTo('#k2', {opacity: 0}, {opacity: 1, duration: .4}, 5.4);
        tl.to('#strand', {attr: {d: CFG.sh.w1}, duration: .8, ease: SM}, 5.1);
        tl.to('#strand', {attr: {d: CFG.sh.w2}, duration: .55, ease: 'sine.inOut'}, 5.9);
        tl.to('#strand', {attr: {d: CFG.sh.w3}, duration: .55, ease: 'sine.inOut'}, 6.45);
        tl.to('#strand', {attr: {d: CFG.sh.w1}, duration: .55, ease: 'sine.inOut'}, 7.0);
        tl.to('#strand', {attr: {d: CFG.sh.thread}, duration: .5, ease: SM}, 7.55);
        tl.to('#cam', {x: -36, duration: 4.4, ease: 'sine.inOut'}, 5.4);
        [0, 1, 2].forEach(i => tl.fromTo('#sc' + i, {opacity: 0, scaleY: .02, scaleX: .7}, {opacity: 1, scaleY: 1, scaleX: 1, duration: .6, ease: 'back.out(1.4)'}, 7.7 + i * .25));
        // S3 10-14: the cards overlap, the stencil cut removes the surplus, the slash becomes the position
        tl.to('#k2', {opacity: 0, duration: .3}, 9.8);
        tl.to('#cam', {x: 0, duration: .5, ease: SO}, 9.8);
        tl.to('#sc0', {x: 400, rotation: -6, duration: .8, ease: SM}, 10.0); tl.to('#sc2', {x: -400, rotation: 6, duration: .8, ease: SM}, 10.0);
        tl.to('#sc1', {scale: 1.05, duration: .8, ease: SM}, 10.0);
        tl.to('#strand', {attr: {d: CFG.sh.slash}, duration: .8, ease: SM}, 10.1);
        tl.to(['#sc0 p', '#sc1 p', '#sc2 p', '#sc0 b', '#sc1 b', '#sc2 b'], {opacity: 0, duration: .25}, 10.45);
        tl.to(['#sc0', '#sc1', '#sc2'], {clipPath: 'inset(46% 46% 46% 46% round 26px)', opacity: 0, duration: .5, ease: 'power2.in'}, 10.55);
        tl.fromTo('#mkw', {opacity: 0, scale: 1.25}, {opacity: 1, scale: 1, duration: .7, ease: SO}, 10.95);
        tl.fromTo('#mk .mg', {scale: 0, transformOrigin: '50% 50%'}, {scale: 1, duration: .5, ease: 'back.out(1.8)'}, 11.1);
        tl.to('#strand', {opacity: 0, duration: .3}, 11.3);
        show('#c3', 10.0); hide('#c2', 11.5);
        // seam 2: a marigold band leads the navy field along the slash diagonal
        tl.fromTo('#gBb', {clipPath: 'polygon(0% 100%,0% 100%,0% 100%,0% 100%)'}, {clipPath: 'polygon(0% 100%,0% -60%,150% -60%,150% 100%)', duration: 1.0, ease: SM}, 11.75);
        tl.fromTo('#gB', {clipPath: 'polygon(0% 100%,0% 100%,0% 100%,0% 100%)'}, {clipPath: 'polygon(0% 100%,0% -60%,150% -60%,150% 100%)', duration: 1.0, ease: SM}, 11.9);
        tl.to('#mk .ol, #mk .or', {fill: '#F2F5FA', duration: .6}, 12.0); tl.to('#mk .ms', {fill: '#B9C7DA', duration: .6}, 12.0);
        tl.fromTo('#pos', {opacity: 0, y: 26}, {opacity: 1, y: 0, duration: .6, ease: SO}, 12.5);
        tl.to('#mkw', {scale: 1.08, duration: 1.6, ease: 'sine.inOut'}, 12.2);
        // S4 14-19: the mark becomes a lens that travels across the market; strands inside it align
        tl.to('#pos', {opacity: 0, y: -20, duration: .4}, 13.9);
        tl.to('#mkw', {scale: .25, opacity: 0, duration: .6, ease: 'power2.in'}, 14.0);
        tl.fromTo('#ring', {opacity: 0, scale: .2}, {opacity: 1, scale: 1, duration: .7, ease: 'back.out(1.4)'}, 14.25);
        show('#c4', 14.0); hide('#c3', 14.6);
        [0, 1, 2].forEach(L => tl.fromTo('#mk' + L, {x: 0, opacity: 0}, {opacity: 1, duration: .5}, 14.2 + L * .1));
        const TR = [-260, -520, -820];
        [0, 1, 2].forEach(L => {
          tl.to('#mk' + L, {x: TR[L], duration: 4.2, ease: 'sine.inOut'}, 14.5);
          tl.fromTo('#mk' + L + ' .hl', {clipPath: 'circle(196px at 960px 540px)'}, {clipPath: 'circle(196px at ' + (960 - TR[L]) + 'px 540px)', duration: 4.2, ease: 'sine.inOut'}, 14.5);
        });
        tl.set('#strand', {attr: {d: CFG.sh.lens}}, 14.55); tl.to('#strand', {opacity: 1, duration: .5}, 14.6);
        tl.fromTo('#k4', {opacity: 0}, {opacity: 1, duration: .4}, 14.6);
        [0, 1, 2].forEach(i => tl.fromTo('#q' + i, {opacity: 0, y: 20}, {opacity: 1, y: 0, duration: .5, ease: SO}, 15.6 + i * .45));
        // seam 3: the lens flattens into the calendar's top edge; pearl folds down from the top
        tl.to(['#q0', '#q1', '#q2', '#k4'], {opacity: 0, duration: .3}, 18.1);
        tl.to('#ring', {scaleY: .02, scaleX: 3.2, y: -278, duration: .7, ease: SM}, 18.2);
        tl.to('#ring', {opacity: 0, duration: .2}, 18.9);
        tl.to('#strand', {attr: {d: CFG.sh.cal}, duration: .7, ease: SM}, 18.2);
        tl.fromTo('#gC', {clipPath: 'inset(0% 0% 100% 0%)'}, {clipPath: 'inset(0% 0% 0% 0%)', duration: .9, ease: SM}, 18.35);
        show('#c5', 18.9); hide('#c4', 19.3);
        // S5 19-24: a 3D fold opens the calendar; cells fill with themes, proof and formats
        tl.fromTo('#cal', {rotationX: -88}, {rotationX: 0, duration: 1.0, ease: SO}, 18.95);
        tl.fromTo('#k5', {opacity: 0}, {opacity: 1, duration: .4}, 19.3);
        CFG.cells.forEach((c, i) => { if (c.on) tl.fromTo('#ce' + i + ' i', {opacity: 0, scale: .6}, {opacity: 1, scale: 1, duration: .3, ease: 'back.out(1.7)'}, 20.0 + (i % 6) * .13 + Math.floor(i / 6) * .5); });
        tl.to('#cal', {rotationX: 14, scale: .96, duration: 1.4, ease: 'sine.inOut'}, 22.6);
        // S6 24-29: three cells lift and become a profile, a post and a carousel; the strand stays attached
        tl.to('#cal', {rotationX: 0, scale: 1, duration: .5, ease: SO}, 24.0);
        tl.to('#k5', {opacity: 0, duration: .3}, 24.0);
        CFG.lift.forEach((ci, j) => {
          const c = CFG.cells[ci], d = CFG.cards[j], el = '#lf' + j;
          tl.fromTo(el, {x: c.x - d.x, y: c.y - d.y, scaleX: c.w / d.w, scaleY: c.h / d.h, opacity: 0}, {opacity: 1, duration: .01}, 24.3);
          tl.to(el, {x: 0, y: 0, scaleX: 1, scaleY: 1, duration: .9, ease: SM}, 24.35 + j * .12);
          tl.to(el + ' .tt, ' + el + ' .ln, ' + el + ' .av', {opacity: 1, duration: .4, stagger: .05}, 25.1 + j * .12);
        });
        CFG.cells.forEach((c, i) => tl.to('#ce' + i, {opacity: 0, y: 30, duration: .45, ease: 'power2.in'}, 24.3 + ((i * 7) % 24) * .015));
        show('#c6', 24.3);
        tl.to('#strand', {attr: {d: CFG.sh.cards}, duration: .9, ease: SM}, 24.4);
        tl.fromTo('#k6', {opacity: 0}, {opacity: 1, duration: .4}, 24.6);
        qa('#lf2 .pg').forEach((p, i) => { tl.fromTo(p, {opacity: 0, x: 0, rotationY: 0}, {opacity: 1, duration: .3}, 25.3); tl.to(p, {x: i * 34, y: i * 10, rotationY: -i * 14, duration: .7, ease: SO}, 26.6 + i * .18); });
        tl.to('#cam', {x: -60, duration: 3.6, ease: 'sine.inOut'}, 24.6);
        hide('#c5', 25.2);
        // seam 4: navy grows out of the post card
        tl.to('#k6', {opacity: 0, duration: .3}, 27.9);
        tl.fromTo('#gD', {clipPath: 'circle(0% at 960px 540px)'}, {clipPath: 'circle(1300px at 960px 540px)', duration: 1.1, ease: SM}, 28.2);
        // S7 29-34: the pieces travel out to buyer nodes; replies return to a calm instrument
        show('#c7', 28.9);
        tl.to('#cam', {x: 0, duration: .6, ease: SO}, 28.6);
        [0, 1, 2].forEach(j => { const n = CFG.nodes[[1, 5, 9][j]], d = CFG.cards[j];
          tl.to('#lf' + j, {x: n[0] - 30 - d.x, y: n[1] - 30 - d.y, scaleX: 60 / d.w, scaleY: 60 / d.h, borderRadius: '220px', duration: 1.0, ease: SM}, 29.0 + j * .12);
          tl.to('#lf' + j + ' > *', {opacity: 0, duration: .25}, 29.0);
          tl.to('#lf' + j, {opacity: 0, duration: .3}, 30.1 + j * .12); });
        hide('#c6', 30.6);
        tl.to('#strand', {attr: {d: CFG.sh.net}, duration: 1.0, ease: SM}, 29.0);
        tl.to('#strand', {opacity: .35, duration: .6}, 30.0);
        tl.fromTo('#k7', {opacity: 0}, {opacity: 1, duration: .4}, 29.3);
        CFG.nodes.forEach((n, i) => { tl.fromTo('#nd' + i, {opacity: 0, scale: .3}, {opacity: 1, scale: 1, duration: .35, ease: 'back.out(2)'}, 29.4 + i * .05);
          tl.to('#nd' + i, {backgroundColor: '#EAA93C', borderColor: '#EAA93C', duration: .2}, 30.4 + i * .1); });
        CFG.rings.forEach((r, i) => { tl.fromTo('#rg' + i, {opacity: 0, scale: .5}, {opacity: 1, scale: 1, duration: .45, ease: SO}, 30.6 + i * .15);
          tl.fromTo('#rl' + i, {opacity: 0, x: -16}, {opacity: 1, x: 0, duration: .45, ease: SO}, 30.75 + i * .15); });
        for (let i = 0; i < 9; i++) { const n = CFG.nodes[(i * 5) % 12], r = CFG.rings[i % 3], t0 = 31.5 + i * .12;
          tl.fromTo('#sg' + i, {x: n[0], y: n[1], opacity: 0}, {opacity: 1, duration: .1}, t0);
          tl.to('#sg' + i, {x: r[0], y: r[1], duration: .75, ease: 'power2.inOut'}, t0);
          tl.to('#sg' + i, {opacity: 0, duration: .12}, t0 + .75);
          tl.fromTo('#rg' + (i % 3), {borderColor: '#B9C7DA', scale: 1}, {borderColor: '#EAA93C', scale: 1.08, duration: .15, yoyo: true, repeat: 1, immediateRender: false}, t0 + .72); }
        tl.fromTo('#ins', {opacity: 0}, {opacity: 1, duration: .5}, 31.3);
        tl.to('#cam', {scale: .95, duration: 2.6, ease: 'sine.inOut'}, 30.6);
        // S8 34-42: the instrument rings fold into three package cards; then the mark and the call to action
        tl.to('#cam', {scale: 1, duration: .6, ease: SO}, 33.8);
        tl.to(['#k7', '#ins', '.rl', '.node', '#strand'], {opacity: 0, duration: .35}, 33.8);
        show('#c8', 33.9);
        CFG.rings.forEach((r, i) => { const d = CFG.pkr[i];
          tl.fromTo('#pk' + i, {x: r[0] - 70 - d.x, y: r[1] - 70 - d.y, scaleX: 140 / d.w, scaleY: 140 / d.h, borderRadius: '240px', opacity: 0, backgroundColor: 'rgba(242,245,250,0)'}, {opacity: 1, duration: .01}, 34.0);
          tl.to('#pk' + i, {x: 0, y: 0, scaleX: 1, scaleY: 1, borderRadius: '28px', backgroundColor: '#F2F5FA', borderColor: '#F2F5FA', duration: .9, ease: SM}, 34.0 + i * .14);
          tl.to('#pk' + i + ' .in', {opacity: 1, duration: .45}, 34.95 + i * .35);
          tl.to('#pk' + i + ' .ac', {scaleX: 1, duration: .5, ease: SO}, 36.6 + i * .15); });
        tl.to('.rg', {opacity: 0, duration: .2}, 34.0); hide('#c7', 34.4);
        tl.fromTo('#pkl', {opacity: 0, y: 12}, {opacity: 1, y: 0, duration: .5, ease: SO}, 34.7);
        tl.to(['#pk0', '#pk1', '#pk2'], {y: 60, opacity: 0, duration: .55, ease: 'power2.in', stagger: .06}, 37.8);
        tl.to('#pkl', {opacity: 0, duration: .3}, 37.8);
        tl.fromTo('#lock', {opacity: 0, y: 24}, {opacity: 1, y: 0, duration: .7, ease: SO}, 38.4);
        tl.fromTo('#hero', {opacity: 0, y: 24}, {opacity: 1, y: 0, duration: .8, ease: SO}, 38.7);
        tl.fromTo('#cta', {opacity: 0, y: 26}, {opacity: 1, y: 0, duration: .6, ease: 'back.out(1.6)'}, 39.1);
        // captions are native lower-third type that follows the narration windows
        LINES.forEach(([a, b, t]) => {
          tl.set('#capt', {textContent: t}, a);
          tl.fromTo('#capt', {opacity: 0, y: 12}, {opacity: 1, y: 0, duration: .25, ease: SO, immediateRender: false}, a);
          tl.to('#capt', {opacity: 0, duration: .2}, b);
        });
        tl.to({}, {duration: .01}, %DUR% - .01);
""".replace("%DUR%", str(DUR))
body = body.replace('<div class="sc" id="c4">', '<div id="ring"></div><div class="sc" id="c4">')
PROJ.mkdir(parents=True, exist_ok=True)
(PROJ / "index.html").write_text(K.root_html(W, H, DUR, css, body, js, "assets/audio/" + ("mix-with-guide.wav" if GUIDE else "mix-voice-ready.wav")))
(PROJ / "hyperframes.json").write_text(json.dumps({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json", "paths": {"blocks": "compositions", "assets": "assets"}}, indent=2))
(PROJ / "meta.json").write_text(json.dumps({"id": "outspoken-launch-r15", "name": "outspoken-launch-r15"}, indent=2))
if "--audio" in sys.argv:
    print(K.make_audio(PROJ / "assets" / "audio", DUR, CUTS, LINES, chords=[50, 45, 47, 43], bpm=100, seed=1515, events=EVENTS))
K.write_vo(pathlib.Path(__file__).resolve().parent, "Outspoken launch film R15", DUR, LINES, SCENES, "Narration for a human voice (wording proposed by Codex, R15); the synthetic guide voice in the renders is a timing reference only.")
print("built", PROJ / "index.html")
