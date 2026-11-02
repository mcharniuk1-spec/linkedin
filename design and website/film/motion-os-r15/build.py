#!/usr/bin/env python3
"""Outspoken OS motion film R15 (proposed): 28 s, 4:5 1080x1350, HyperFrames root composition generated from this script.
Six scenes from Codex FILM-DIRECTION-R15 (2 November 2026): thought field into the O, the O as an interview frame, the slash
cuts notes into a position, a compact calendar and a post, buyer nodes and returning signals, three packages and the lockup.
Usage: python3 build.py <project_dir> <paths_json> [--audio] [--guide]"""
import sys, pathlib, json, math, random
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import filmkit as K
PROJ = pathlib.Path(sys.argv[1]); PATHS = sys.argv[2]; GUIDE = "--guide" in sys.argv
SITE = pathlib.Path(__file__).resolve().parents[2] / "website" / "website-v3"
PROT = json.loads((SITE / "content.json").read_text())["protected"]
PRICING = json.loads((SITE / "pricing.json").read_text())
W, H, DUR = 1080, 1350, 28.0
CUTS = [4.0, 8.0, 12.0, 17.0, 22.0]
LINES = [(0.3, 3.7, "Start with what you know."),
         (4.3, 7.7, "Put the thinking into words."),
         (8.3, 11.7, "Choose the position."),
         (12.3, 16.6, "Build a plan and make it visible."),
         (17.3, 21.0, "Make the next conversation useful."),
         (21.6, 24.0, "Choose where to start.")]
SCENES = ["S1 thought into the O", "S2 interview frame", "S3 the cut", "S4 plan and post", "S5 conversations", "S6 packages and close"]
EVENTS = [("shimmer", .2), ("tick", 1.0, 10, .2), ("swoosh", 3.3), ("thump", 3.9), ("tick", 4.9, 9, .2), ("pop", 8.3), ("pop", 8.55), ("pop", 8.8),
          ("riser", 9.2), ("thump", 9.8), ("swoosh", 10.0), ("shimmer", 10.6), ("thump", 12.1), ("tick", 13.0, 17, .09), ("pop", 15.2), ("riser", 15.8),
          ("thump", 16.4), ("pop", 17.6, 10, .1), ("tick", 19.4, 9, .14), ("swoosh", 21.3), ("pop", 22.0), ("pop", 22.25), ("pop", 22.5), ("swoosh", 24.0),
          ("thump", 24.3), ("pop", 24.9), ("shimmer", 24.95)]
rnd = random.Random(2828)
N = 64
def path(pts): return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
def line(x0, y0, x1, y1): return path([(x0 + (x1 - x0) * i / (N - 1), y0 + (y1 - y0) * i / (N - 1)) for i in range(N)])
def wave(ph, amp, x0=60, x1=1020, y=640):
    return path([(x0 + (x1 - x0) * i / (N - 1), y + amp * math.sin(2 * math.pi * 5 * i / (N - 1) + ph) * math.sin(math.pi * i / (N - 1)) ** 1.3) for i in range(N)])
SH = {"flat": line(60, 640, 1020, 640), "w1": wave(0, 120), "w2": wave(2.0, 90), "w3": wave(3.8, 130), "cut": line(330, 980, 750, 300), "net": line(540, 640, 540, 640)}
mk = K.mark_parts(PATHS)
MW = 760; MH = MW * mk[1] / mk[0]; MX = (W - MW) / 2; MY = 640 - MH / 2
OC = (MX + MW * 0.245, 640)   # centre of the stencil O
pts = []
for i in range(84):
    a = i / 84 * 2 * math.pi
    pts.append({"s": [rnd.uniform(60, 1020), rnd.uniform(80, 1270)], "c": [OC[0] + math.cos(a) * 150, OC[1] + math.sin(a) * 190]})
cells = [{"x": 119 + c * 214, "y": 330 + r * 124, "w": 200, "h": 110, "t": ["Theme", "Proof", "Format", "Post"][(r + c) % 4], "on": (r * 4 + c) not in (3, 14)} for r in range(5) for c in range(4)]
LIFT = 9; POST = {"x": 190, "y": 300, "w": 700, "h": 700}
NODES = [[540 + math.cos(-math.pi / 2 + i * 2 * math.pi / 10) * 330, 600 + math.sin(-math.pi / 2 + i * 2 * math.pi / 10) * 260] for i in range(10)]
RINGS = [(230, 1010, "Engagement"), (540, 1010, "Qualified replies"), (850, 1010, "Attributed leads")]
PK = PRICING["packages"][:3]
PKR = [{"x": 140, "y": 300 + i * 225, "w": 800, "h": 195} for i in range(3)]
CFG = {"pts": pts, "sh": SH, "cells": cells, "lift": LIFT, "post": POST, "nodes": NODES, "rings": [[x, y] for x, y, _ in RINGS], "pkr": PKR, "oc": OC}
def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;")
def rect(d): return f'left:{d["x"]}px;top:{d["y"]}px;width:{d["w"]}px;height:{d["h"]}px'
css = """
.g{position:absolute;inset:0}
#gN{background:radial-gradient(900px 900px at 80% 10%,rgba(49,87,213,.24),transparent 62%),radial-gradient(800px 800px at 10% 96%,rgba(234,169,60,.09),transparent 60%),#0D1A3B}
.pearl{background:linear-gradient(160deg,#fff 8%,#F1F3F6 60%,#E6EBF1)}
.navy{background:radial-gradient(900px 900px at 20% 10%,rgba(49,87,213,.22),transparent 60%),#0D1A3B}
#gA{clip-path:circle(0px at %OCX%px %OCY%px)}
#gBb{background:#EAA93C;clip-path:polygon(160% 0%,200% 0%,140% 100%,100% 100%)}
#gD{clip-path:circle(0px at 540px 650px)}
#cam{position:absolute;inset:0;transform-origin:50% 50%}
.sc{position:absolute;inset:0;opacity:0}
#c1{opacity:1}
.mono{font-family:'Geist Mono',monospace;font-weight:500;letter-spacing:.08em;text-transform:uppercase}
.disp{font-family:'Fraunces',serif;font-weight:400;letter-spacing:-.02em;line-height:1.06}
.kick{position:absolute;left:84px;top:92px;font-size:30px;opacity:0}
.lt{color:#B9C7DA}.dk{color:#3A4A75}
.pt{position:absolute;left:-7px;top:-7px;width:14px;height:14px;border-radius:50%;background:#F2F5FA;opacity:0}
.pt.m{background:#EAA93C}.pt.s{background:#B9C7DA}
#sv{position:absolute;inset:0;z-index:30;overflow:visible}
#strand{fill:none;stroke:#EAA93C;stroke-width:7;stroke-linecap:round;stroke-linejoin:round}
#mkw{position:absolute;left:%MX%px;top:%MY%px;width:%MW%px;height:%MH%px;opacity:0;z-index:31}
.note{position:absolute;left:190px;width:700px;height:150px;border-radius:24px;background:#fff;border:2px solid #E1E6EE;box-shadow:0 26px 50px -30px rgba(22,39,96,.55);opacity:0;display:flex;align-items:center;padding:0 40px;gap:26px}
.note b{font-family:'Geist Mono',monospace;font-weight:500;font-size:30px;color:#666F7F}
.note p{font-family:'Fraunces',serif;font-size:50px;color:#162760;line-height:1.05}
#cut{position:absolute;left:-60px;top:627px;width:1200px;height:26px;border-radius:13px;background:#EAA93C;transform-origin:50% 50%;opacity:0;z-index:33}
#pos{position:absolute;left:0;right:0;top:575px;text-align:center;font-size:120px;color:#162760;opacity:0;z-index:34}
#calw{position:absolute;inset:0;perspective:1500px;perspective-origin:50% 0%}
#cal{position:absolute;inset:0;transform-origin:50% 330px;transform-style:preserve-3d}
.cell{position:absolute;border-radius:16px;background:rgba(22,39,96,.05);border:2px solid #D9DEE7}
.cell i{position:absolute;inset:8px;border-radius:11px;opacity:0;display:flex;align-items:center;justify-content:center;font-style:normal;font-family:'Geist Mono',monospace;font-weight:500;font-size:31px}
.k-Theme i{background:#162760;color:#F2F5FA}.k-Proof i{background:#FFF6E3;color:#162760;box-shadow:inset 0 0 0 3px #EAA93C}.k-Format i{background:#E6EBF1;color:#3A4A75}.k-Post i{background:#EAA93C;color:#0D1A3B}
#post{position:absolute;border-radius:28px;background:#fff;border:2px solid #E1E6EE;box-shadow:0 30px 60px -34px rgba(22,39,96,.6);opacity:0;transform-origin:0 0;overflow:hidden}
#post .av{position:absolute;left:56px;top:56px;width:120px;height:120px;border-radius:50%;background:#162760;opacity:0}
#post .ln{position:absolute;left:56px;height:20px;border-radius:10px;background:#E1E6EE;opacity:0}
#post .tt{position:absolute;left:56px;bottom:52px;font-family:'Fraunces',serif;font-size:60px;color:#162760;opacity:0}
.node{position:absolute;left:0;top:0;width:40px;height:40px;margin:-20px 0 0 -20px;border-radius:50%;border:4px solid #B9C7DA;background:#0D1A3B;opacity:0}
.sig{position:absolute;left:0;top:0;width:18px;height:18px;margin:-9px 0 0 -9px;border-radius:50%;background:#F6D591;opacity:0}
.rg{position:absolute;width:150px;height:150px;margin:-75px 0 0 -75px;border-radius:50%;border:5px solid #B9C7DA;opacity:0}
.rl{position:absolute;width:300px;margin-left:-150px;text-align:center;font-size:30px;color:#F2F5FA;opacity:0}
.pk{position:absolute;border:5px solid #EAA93C;border-radius:24px;opacity:0;overflow:hidden;transform-origin:0 0}
.pk .in{position:absolute;inset:0;padding:30px 40px;opacity:0;display:flex;flex-direction:column;justify-content:center}
.pk h3{font-family:'Fraunces',serif;font-weight:400;font-size:52px;line-height:1.05;color:#162760}
.pk .pr{margin-top:14px;font-family:'Geist Mono',monospace;font-weight:500;font-size:40px;color:#162760}
.pk .pr span{font-size:30px;color:#666F7F;letter-spacing:.06em;text-transform:uppercase;margin-left:14px}
#pkl{position:absolute;left:60px;right:60px;top:200px;text-align:center;font-size:30px;line-height:1.4;opacity:0}
#lock{position:absolute;left:50%;top:330px;width:640px;margin-left:-320px;opacity:0}
#hero{position:absolute;left:100px;right:100px;top:500px;text-align:center;font-size:72px;color:#F2F5FA;opacity:0}
#cta{position:absolute;left:50%;top:900px;transform:translateX(-50%);height:104px;padding:0 60px;border-radius:999px;background:#EAA93C;color:#0D1A3B;font-size:42px;font-weight:600;display:flex;align-items:center;white-space:nowrap;opacity:0}
#cap{position:absolute;left:0;right:0;bottom:70px;display:flex;justify-content:center;z-index:60}
#cap span{max-width:940px;padding:16px 30px;border-radius:16px;background:rgba(13,26,59,.80);color:#F1F3F6;font-size:36px;line-height:1.3;text-align:center;opacity:0}
""".replace("%MX%", f"{MX:.1f}").replace("%MY%", f"{MY:.1f}").replace("%MW%", str(MW)).replace("%MH%", f"{MH:.1f}").replace("%OCX%", f"{OC[0]:.0f}").replace("%OCY%", f"{OC[1]:.0f}")
pk_html = "".join(
    f'<div class="pk" id="pk{i}" style="{rect(PKR[i])}"><div class="in"><h3>{esc(p["name"])}</h3>'
    f'<div class="pr">{esc(p["display_price"].split(" /")[0])}<span>{"one-off" if p["period"] == "one-off" else "per month"}</span></div></div></div>' for i, p in enumerate(PK))
body = f"""
      <div class="g" id="gN"></div><div class="g pearl" id="gA"></div><div class="g" id="gBb"></div><div class="g navy" id="gD"></div>
      <div id="cam">
        <div class="sc" id="c1">{''.join(f'<div class="pt{" m" if i % 7 == 0 else (" s" if i % 3 == 1 else "")}" id="p{i}"></div>' for i in range(len(pts)))}<div class="kick mono lt" id="k1">Your thinking</div></div>
        <div class="sc" id="c2"><div class="kick mono dk" id="k2">Interview</div></div>
        <div class="sc" id="c3">
          <div class="note" id="n0" style="top:400px"><b>01</b><p>A product decision</p></div>
          <div class="note" id="n1" style="top:575px"><b>02</b><p>A customer question</p></div>
          <div class="note" id="n2" style="top:750px"><b>03</b><p>The proof behind it</p></div>
          <div id="cut"></div><div class="disp" id="pos">Position</div>
        </div>
        <div class="sc" id="c4">
          <div class="kick mono dk" id="k4">Plan</div>
          <div id="calw"><div id="cal">{''.join(f'<div class="cell k-{c["t"]}" id="ce{i}" style="{rect(c)}"><i>{c["t"] if c["on"] else ""}</i></div>' for i, c in enumerate(cells))}</div></div>
          <div id="post" style="{rect(POST)}"><div class="av"></div><div class="ln" style="top:220px;width:560px;background:#162760"></div><div class="ln" style="top:268px;width:520px"></div><div class="ln" style="top:310px;width:560px"></div><div class="ln" style="top:352px;width:440px"></div><div class="ln" style="top:394px;width:500px"></div><div class="tt">Post</div></div>
        </div>
        <div class="sc" id="c5">
          <div class="kick mono lt" id="k5">Conversations</div>
          {''.join(f'<div class="node" id="nd{i}"></div>' for i in range(len(NODES)))}
          {''.join(f'<div class="sig" id="sg{i}"></div>' for i in range(8))}
          {''.join(f'<div class="rg" id="rg{i}" style="left:{x}px;top:{y}px"></div><div class="rl" id="rl{i}" style="left:{x}px;top:{y + 96}px">{t}</div>' for i, (x, y, t) in enumerate(RINGS))}
        </div>
        <div class="sc" id="c6">
          <div class="mono lt" id="pkl">{esc(PRICING["public_label"])}</div>
          {pk_html}
          <img id="lock" src="assets/brand/lockup-os-inverse.svg" alt="">
          <div class="disp" id="hero">{esc(PROT["hero"])}</div>
          <div id="cta">{esc(PROT["cta"])}</div>
        </div>
      </div>
      <div id="mkw">{K.mark_svg(mk, "mk", o="#F2F5FA", s="#B9C7DA", width=MW)}</div>
      <svg id="sv" viewBox="0 0 {W} {H}" width="{W}" height="{H}"><path id="strand" d="{SH['flat']}" opacity="0"/></svg>
      <div id="cap"><span id="capt"></span></div>
"""
js = "const CFG = " + json.dumps(CFG) + ";\nconst LINES = " + json.dumps(LINES) + ";\n" + """
        const q = s => document.querySelector(s), qa = s => [...document.querySelectorAll(s)];
        const SM = 'power3.inOut', SO = 'power3.out';
        const show = (id, t) => tl.set(id, {opacity: 1}, t), hide = (id, t) => tl.set(id, {opacity: 0}, t);
        // S1 0-4: a field of thought contracts into the O; pearl opens from the O's counter
        tl.fromTo('#cam', {scale: 1.06}, {scale: 1, duration: 4, ease: 'sine.inOut'}, 0);
        tl.fromTo('#k1', {opacity: 0}, {opacity: 1, duration: .4}, .5); tl.to('#k1', {opacity: 0, duration: .3}, 2.9);
        CFG.pts.forEach((p, i) => {
          tl.fromTo('#p' + i, {x: p.s[0], y: p.s[1], opacity: 0, scale: .4}, {opacity: .9, scale: 1, duration: .8, ease: SO}, .1 + (i % 20) * .03);
          tl.to('#p' + i, {x: p.c[0], y: p.c[1], duration: 1.5, ease: SM}, 1.1 + (i % 14) * .03);
          tl.to('#p' + i, {opacity: 0, scale: .3, duration: .4}, 2.75 + (i % 8) * .02);
        });
        tl.fromTo('#mkw', {opacity: 0, scale: 1.12}, {opacity: 1, scale: 1, duration: .8, ease: SO}, 2.6);
        tl.fromTo('#gA', {clipPath: 'circle(0px at ' + CFG.oc[0] + 'px ' + CFG.oc[1] + 'px)'}, {clipPath: 'circle(1500px at ' + CFG.oc[0] + 'px ' + CFG.oc[1] + 'px)', duration: 1.1, ease: SM}, 3.3);
        tl.to('#mk .ol, #mk .or', {fill: '#162760', duration: .6}, 3.4); tl.to('#mk .ms', {fill: '#666F7F', duration: .6}, 3.4);
        hide('#c1', 4.0); show('#c2', 3.9);
        // S2 4-8: the O becomes an interview frame and the strand threads through it as a waveform
        tl.to('#mk .ms, #mk .mg', {opacity: 0, duration: .5}, 4.0);
        tl.to('#mkw', {x: 540 - CFG.oc[0], scale: 1.15, duration: .9, ease: SM}, 4.1);
        tl.to('#mk .ol', {x: -10, duration: .9, ease: SM}, 4.3); tl.to('#mk .or', {x: 10, duration: .9, ease: SM}, 4.3);
        tl.fromTo('#k2', {opacity: 0}, {opacity: 1, duration: .4}, 4.4);
        tl.fromTo('#strand', {opacity: 0, strokeDasharray: '1000 1000', strokeDashoffset: 1000}, {opacity: 1, strokeDashoffset: 0, duration: .7, ease: SO}, 4.7);
        tl.set('#strand', {strokeDasharray: 'none'}, 5.45);
        tl.to('#strand', {attr: {d: CFG.sh.w1}, duration: .6, ease: SM}, 5.4);
        tl.to('#strand', {attr: {d: CFG.sh.w2}, duration: .5, ease: 'sine.inOut'}, 6.0);
        tl.to('#strand', {attr: {d: CFG.sh.w3}, duration: .5, ease: 'sine.inOut'}, 6.5);
        tl.to('#strand', {attr: {d: CFG.sh.flat}, duration: .5, ease: SM}, 7.0);
        tl.to('#cam', {x: -24, duration: 3.4, ease: 'sine.inOut'}, 4.4);
        // S3 8-12: notes gather in the frame; the slash cuts them into one clear position
        tl.to('#k2', {opacity: 0, duration: .3}, 7.8); tl.to('#cam', {x: 0, duration: .5, ease: SO}, 7.8);
        show('#c3', 7.9);
        tl.to('#mkw', {opacity: .18, duration: .5}, 8.0);
        [0, 1, 2].forEach(i => tl.fromTo('#n' + i, {opacity: 0, x: (i - 1) * 90, scale: .9}, {opacity: 1, x: 0, scale: 1, duration: .5, ease: 'back.out(1.5)'}, 8.2 + i * .25));
        tl.to('#strand', {attr: {d: CFG.sh.cut}, duration: .7, ease: SM}, 8.9);
        tl.to('#strand', {opacity: 0, duration: .3}, 9.55);
        tl.fromTo('#cut', {opacity: 0, rotation: -58, scaleX: 0}, {opacity: 1, scaleX: 1, duration: .45, ease: 'power3.in'}, 9.4);
        tl.to('#n0', {x: -760, y: -90, rotation: -14, opacity: 0, duration: .7, ease: 'power2.in'}, 9.8);
        tl.to('#n2', {x: 760, y: 90, rotation: 14, opacity: 0, duration: .7, ease: 'power2.in'}, 9.8);
        tl.to('#n1 b, #n1 p', {opacity: 0, duration: .25}, 9.85);
        tl.to('#n1', {scaleX: 1.12, scaleY: 1.5, duration: .6, ease: SM}, 9.9);
        tl.to('#mkw', {opacity: 0, duration: .4}, 9.8);
        tl.fromTo('#gBb', {clipPath: 'polygon(160% 0%,200% 0%,140% 100%,100% 100%)'}, {clipPath: 'polygon(-100% 0%,200% 0%,140% 100%,-160% 100%)', duration: .9, ease: SM}, 9.95);
        tl.to('#gBb', {opacity: 0, duration: .8}, 11.0);
        tl.to('#cut', {scaleX: .04, opacity: 0, duration: .5, ease: 'power2.in'}, 10.2);
        tl.fromTo('#pos', {opacity: 0, y: 20}, {opacity: 1, y: 0, duration: .6, ease: SO}, 10.35);
        hide('#c2', 9.0);
        // S4 12-17: the position card folds open into a compact calendar; one cell becomes the post
        tl.to('#pos', {opacity: 0, duration: .3}, 11.9);
        tl.to('#n1', {scaleY: .05, y: -250, opacity: 0, duration: .5, ease: SM}, 11.9);
        show('#c4', 12.0); hide('#c3', 12.5);
        tl.fromTo('#cal', {rotationX: -86}, {rotationX: 0, duration: .9, ease: SO}, 12.05);
        tl.fromTo('#k4', {opacity: 0}, {opacity: 1, duration: .4}, 12.3);
        CFG.cells.forEach((c, i) => { if (c.on) tl.fromTo('#ce' + i + ' i', {opacity: 0, scale: .6}, {opacity: 1, scale: 1, duration: .28, ease: 'back.out(1.7)'}, 13.0 + i * .085); });
        { const c = CFG.cells[CFG.lift], d = CFG.post;
          tl.fromTo('#post', {x: c.x - d.x, y: c.y - d.y, scaleX: c.w / d.w, scaleY: c.h / d.h, opacity: 0}, {opacity: 1, duration: .01}, 15.1);
          tl.to('#post', {x: 0, y: 0, scaleX: 1, scaleY: 1, duration: .8, ease: SM}, 15.15);
          tl.to('#post .av, #post .ln, #post .tt', {opacity: 1, duration: .35, stagger: .05}, 15.8); }
        CFG.cells.forEach((c, i) => tl.to('#ce' + i, {opacity: 0, y: 26, duration: .4, ease: 'power2.in'}, 15.1 + ((i * 7) % 20) * .015));
        tl.to('#k4', {opacity: 0, duration: .3}, 16.0);
        tl.fromTo('#gD', {clipPath: 'circle(0px at 540px 650px)'}, {clipPath: 'circle(1700px at 540px 650px)', duration: 1.0, ease: SM}, 16.3);
        // S5 17-22: the post becomes buyer nodes; signals return to three separate measures
        show('#c5', 16.9);
        tl.to('#post', {x: 540 - 30 - CFG.post.x, y: 600 - 30 - CFG.post.y, scaleX: 60 / CFG.post.w, scaleY: 60 / CFG.post.h, borderRadius: '350px', duration: .8, ease: SM}, 17.0);
        tl.to('#post > *', {opacity: 0, duration: .2}, 17.0);
        tl.to('#post', {opacity: 0, duration: .3}, 17.8);
        tl.fromTo('#k5', {opacity: 0}, {opacity: 1, duration: .4}, 17.3);
        CFG.nodes.forEach((n, i) => { tl.fromTo('#nd' + i, {x: 540, y: 600, opacity: 0, scale: .3}, {x: n[0], y: n[1], opacity: 1, scale: 1, duration: .6, ease: SO}, 17.6 + i * .06);
          tl.to('#nd' + i, {backgroundColor: '#EAA93C', borderColor: '#EAA93C', duration: .2}, 18.5 + i * .1); });
        CFG.rings.forEach((r, i) => { tl.fromTo('#rg' + i, {opacity: 0, scale: .5}, {opacity: 1, scale: 1, duration: .45, ease: SO}, 18.6 + i * .15);
          tl.fromTo('#rl' + i, {opacity: 0, y: 12}, {opacity: 1, y: 0, duration: .45, ease: SO}, 18.75 + i * .15); });
        for (let i = 0; i < 8; i++) { const n = CFG.nodes[(i * 3 + 1) % 10], r = CFG.rings[i % 3], t0 = 19.4 + i * .14;
          tl.fromTo('#sg' + i, {x: n[0], y: n[1], opacity: 0}, {opacity: 1, duration: .1}, t0);
          tl.to('#sg' + i, {x: r[0], y: r[1], duration: .75, ease: 'power2.inOut'}, t0);
          tl.to('#sg' + i, {opacity: 0, duration: .12}, t0 + .75);
          tl.fromTo('#rg' + (i % 3), {borderColor: '#B9C7DA', scale: 1}, {borderColor: '#EAA93C', scale: 1.08, duration: .15, yoyo: true, repeat: 1, immediateRender: false}, t0 + .72); }
        hide('#c4', 17.9);
        // S6 22-28: the three measures fold into package cards, then the lockup and the call to action
        tl.to(['#k5', '.rl', '.node'], {opacity: 0, duration: .35}, 21.1);
        show('#c6', 21.2);
        CFG.rings.forEach((r, i) => { const d = CFG.pkr[i];
          tl.fromTo('#pk' + i, {x: r[0] - 75 - d.x, y: r[1] - 75 - d.y, scaleX: 150 / d.w, scaleY: 150 / d.h, borderRadius: '400px', opacity: 0, backgroundColor: 'rgba(242,245,250,0)'}, {opacity: 1, duration: .01}, 21.3);
          tl.to('#pk' + i, {x: 0, y: 0, scaleX: 1, scaleY: 1, borderRadius: '24px', backgroundColor: '#F2F5FA', borderColor: '#F2F5FA', duration: .85, ease: SM}, 21.3 + i * .14);
          tl.to('#pk' + i + ' .in', {opacity: 1, duration: .4}, 22.0 + i * .25); });
        tl.to('.rg', {opacity: 0, duration: .2}, 21.3); hide('#c5', 21.7);
        tl.fromTo('#pkl', {opacity: 0, y: 12}, {opacity: 1, y: 0, duration: .5, ease: SO}, 21.9);
        tl.to(['#pk0', '#pk1', '#pk2'], {y: 60, opacity: 0, duration: .3, ease: 'power2.in', stagger: .05}, 24.0);
        tl.to('#pkl', {opacity: 0, duration: .3}, 24.0);
        tl.fromTo('#lock', {opacity: 0, y: 24}, {opacity: 1, y: 0, duration: .7, ease: SO}, 24.45);
        tl.fromTo('#hero', {opacity: 0, y: 24}, {opacity: 1, y: 0, duration: .8, ease: SO}, 24.65);
        tl.fromTo('#cta', {opacity: 0, y: 26}, {opacity: 1, y: 0, duration: .6, ease: 'back.out(1.6)'}, 25.1);
        LINES.forEach(([a, b, t]) => {
          tl.set('#capt', {textContent: t}, a);
          tl.fromTo('#capt', {opacity: 0, y: 12}, {opacity: 1, y: 0, duration: .25, ease: SO, immediateRender: false}, a);
          tl.to('#capt', {opacity: 0, duration: .2}, b);
        });
        tl.to({}, {duration: .01}, %DUR% - .01);
""".replace("%DUR%", str(DUR))
PROJ.mkdir(parents=True, exist_ok=True)
(PROJ / "index.html").write_text(K.root_html(W, H, DUR, css, body, js, "assets/audio/" + ("mix-with-guide.wav" if GUIDE else "mix-voice-ready.wav")))
(PROJ / "hyperframes.json").write_text(json.dumps({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json", "paths": {"blocks": "compositions", "assets": "assets"}}, indent=2))
(PROJ / "meta.json").write_text(json.dumps({"id": "outspoken-os-motion-r15", "name": "outspoken-os-motion-r15"}, indent=2))
if "--audio" in sys.argv:
    print(K.make_audio(PROJ / "assets" / "audio", DUR, CUTS, LINES, chords=[48, 43, 45, 41], bpm=104, seed=2828, events=EVENTS))
K.write_vo(pathlib.Path(__file__).resolve().parent, "Outspoken OS motion film R15", DUR, LINES, SCENES, "Narration for a human voice (wording proposed by Codex, R15); the synthetic guide voice in the renders is a timing reference only.")
print("built", PROJ / "index.html")
