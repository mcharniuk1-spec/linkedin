#!/usr/bin/env python3
"""Outspoken OS motion film R15, 16:9 composition (proposed): 28 s, 1920x1080, HyperFrames root composition generated from this script.

An independent re-composition of the six scenes of build.py (the 4:5 film), not a crop and not a scaled copy. The narration windows,
cut times, captions and story are the same, so one voice recording fits both frames; layout, choreography and transitions are new
for the wide frame and use the horizontal axis throughout:
  S1  thought field contracts onto the outline of the stencil O; the mark resolves; pearl opens out of the O's counter
  S2  the O parts into a wide interview frame (two brackets), the strand threads through as a speaking waveform, camera travel
  S3  three notes ride in with parallax, the strand becomes the cut, two notes leave, one becomes "Position"; a marigold curtain sweeps
  S4  the Position card is the middle panel of a tri-fold that opens into a 6 x 4 calendar; one cell lifts into a post; navy grows out of it
  S5  the post shrinks to a node and the strand grows left to right into a buyer network; signals return to three separate rings
  S6  the rings fold into package cards; the cards sink into the call to action; lockup, hero line and call to action centred

Usage: python3 build_16x9.py <project_dir> <paths_json> [--audio] [--guide]
Deterministic: seeded random only, no wall clock, no network, no absolute paths. Package names, prices, the hero line and the call
to action are read from the site JSON at build time. The OS stencil comes from the paths JSON (never re-typeset)."""
import sys, pathlib, json, math, random, re
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import filmkit as K

PROJ = pathlib.Path(sys.argv[1]); PATHS = sys.argv[2]; GUIDE = "--guide" in sys.argv
SITE = HERE.parents[1] / "website" / "website-v3"
PROT = json.loads((SITE / "content.json").read_text(encoding="utf-8"))["protected"]
PRICING = json.loads((SITE / "pricing.json").read_text(encoding="utf-8"))
W, H, DUR = 1920, 1080, 28.0

# ---- timing and narration: copied verbatim from the 4:5 film (build.py) so one voice recording fits both frames
CUTS = [4.0, 8.0, 12.0, 17.0, 22.0]
LINES = [(0.3, 3.7, "Start with what you know."),
         (4.3, 7.7, "Put the thinking into words."),
         (8.3, 11.7, "Choose the position."),
         (12.3, 16.6, "Build a plan and make it visible."),
         (17.3, 21.0, "Make the next conversation useful."),
         (21.6, 24.0, "Choose where to start.")]
SCENES = ["S1 thought into the O", "S2 interview frame", "S3 the cut", "S4 plan and post", "S5 conversations", "S6 packages and close"]
# one designed sound for each visual beat of THIS choreography (kind, time[, count, spacing]); times match the timeline below
EVENTS = [("shimmer", .2), ("tick", 1.15, 14, .1), ("swoosh", 1.9), ("pop", 2.55), ("swoosh", 2.85), ("pop", 3.05), ("swoosh", 3.2),            # S1: field, O, S, slash, circle
          ("swoosh", 4.45), ("pop", 4.8), ("tick", 5.25, 11, .18), ("riser", 6.4), ("swoosh", 7.2), ("pop", 8.0), ("pop", 8.15), ("pop", 8.3),  # S2: frame parts, wave, travel, notes land
          ("riser", 8.85), ("thump", 9.8), ("swoosh", 10.0), ("swoosh", 10.4), ("shimmer", 10.8),                                                # S3: the cut, notes leave, curtain, Position
          ("swoosh", 12.05), ("tick", 12.95, 24, .085), ("pop", 15.15), ("riser", 15.55), ("thump", 16.35),                                    # S4: wings open, cells fill, post lifts, navy grows
          ("swoosh", 17.65), ("pop", 17.7), ("pop", 17.85, 12, .09), ("tick", 18.4, 12, .07), ("pop", 18.5, 3, .13), ("tick", 19.2, 9, .12),    # S5: node, sprouts, activation, rings, signals
          ("pop", 19.9, 9, .12), ("swoosh", 20.95), ("pop", 21.3, 3, .1),                                                                      # S5-S6: ring pulses, rings fold, cards land
          ("swoosh", 23.3), ("thump", 23.95), ("pop", 24.1), ("shimmer", 24.15)]                                                               # S6: cards sink, call to action
# ---- stage geometry (px). Safe zone x 64..1856, y 64..1016; captions sit in the band y 937..1012 and nothing else lives there
CX, CY = 960, 500                       # centre of the working area: the working band is y 130..920, the caption band is below
mk = K.mark_parts(PATHS)                # (width, height, O left half, O right half, S, slash) in viewBox units, 184.16 x 100
MW = 880; U = MW / mk[0]; MH = U * mk[1]; MX = (W - MW) / 2; MY = CY - MH / 2
def mxp(x): return MX + x * U
def myp(y): return MY + y * U

def parse_path(d, per=14):
    """Closed polylines (viewBox units) for every subpath of an M/C/L/Z path, cubic segments sampled at `per` points."""
    toks = re.findall(r"[MCLZ]|-?\d+(?:\.\d+)?", d); subs, cur, pos, cmd, i = [], None, None, None, 0
    while i < len(toks):
        if toks[i] in ("M", "C", "L", "Z"):
            cmd = toks[i]; i += 1
            if cmd == "Z":
                if cur: cur.append(cur[0]); subs.append(cur); cur = None
                continue
        if cmd == "M": pos = (float(toks[i]), float(toks[i + 1])); i += 2; cur = [pos]; cmd = "L"
        elif cmd == "L": pos = (float(toks[i]), float(toks[i + 1])); i += 2; cur.append(pos)
        elif cmd == "C":
            p1, p2, p3 = [(float(toks[i + j]), float(toks[i + j + 1])) for j in (0, 2, 4)]; i += 6
            for k in range(1, per + 1):
                u = k / per; a, b, c, e = (1 - u) ** 3, 3 * (1 - u) ** 2 * u, 3 * (1 - u) * u * u, u ** 3
                cur.append((a * pos[0] + b * p1[0] + c * p2[0] + e * p3[0], a * pos[1] + b * p1[1] + c * p2[1] + e * p3[1]))
            pos = p3
    if cur: subs.append(cur)
    return subs

def resample(polys, n):
    """n points evenly spaced along the combined outline of closed polylines."""
    segs = [(a, b, math.dist(a, b)) for poly in polys for a, b in zip(poly, poly[1:])]
    total = sum(s[2] for s in segs); out = []; acc = 0.0; k = 0
    for j in range(n):
        target = (j + .5) * total / n
        while acc + segs[k][2] < target: acc += segs[k][2]; k += 1
        a, b, l = segs[k]; u = (target - acc) / l if l else 0
        out.append((a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u))
    return out

def bbox(polys):
    xs = [p[0] for poly in polys for p in poly]; ys = [p[1] for poly in polys for p in poly]
    return min(xs), min(ys), max(xs), max(ys)

OL_BOX = bbox(parse_path(mk[2])); OR_BOX = bbox(parse_path(mk[3]))     # the two halves of the stencil O, in viewBox units
OCU = (OL_BOX[0] + OR_BOX[2]) / 2                                       # x of the O's centre (viewBox units)
OC = (mxp(OCU), CY)                                                     # centre of the O's counter on screen
SHIFT = CX - OC[0]                                                      # moves the O to the centre of the frame in S2
FRAME_EDGE = 96                                                         # outer edge of the left bracket when the O has parted
PART = (CX - FRAME_EDGE - (OCU - OL_BOX[0]) * U) / U                    # how far each half travels, in viewBox units
rnd = random.Random(2828)

# ---- shared strand paths: always 64 points so that attr d morphs interpolate in GSAP core
N = 160
def path(pts): return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
def line(x0, y0, x1, y1): return path([(x0 + (x1 - x0) * i / (N - 1), y0 + (y1 - y0) * i / (N - 1)) for i in range(N)])
def wave(ph, amp, cyc=7, x0=0, x1=W, y=CY, lo=.06, hi=.94):
    pts = []
    for i in range(N):
        u = i / (N - 1); env = math.sin(math.pi * (u - lo) / (hi - lo)) ** 1.25 if lo < u < hi else 0
        pts.append((x0 + (x1 - x0) * u, y + amp * math.sin(2 * math.pi * cyc * u + ph) * env * (.72 + .28 * math.sin(3.1 * u + ph))))
    return path(pts)
CUT_A, CUT_B = (330, 760), (1590, 240)                                  # the cut: one diagonal that crosses all three notes
SRC = (300, 420)                                                        # the post becomes this node; the strand grows from it
def trunk_y(x): return 420 + 30 * math.sin((x - 300) / 240.0)
def trunk(frac):
    """The S5 strand from the source node to the right edge; frac < 1 gives the growing tip (all 64 points stay on the curve)."""
    x0, x1 = SRC[0] + 30, 1840
    return path([(x0 + (x1 - x0) * frac * i / (N - 1), trunk_y(x0 + (x1 - x0) * frac * i / (N - 1))) for i in range(N)])
SH = {"flat": line(0, CY, W, CY), "w1": wave(0, 150), "w2": wave(1.9, 112), "w3": wave(3.6, 158), "w4": wave(5.3, 120),
      "cut": line(*CUT_A, *CUT_B), "t0": trunk(0.0001), "t1": trunk(1.0)}

# ---- S1: thought particles contract onto the outline of the stencil O (outline points sampled from the paths JSON)
NP = 120
targets = [(mxp(x), myp(y)) for x, y in resample(parse_path(mk[2]) + parse_path(mk[3]), NP)]
starts = [(rnd.uniform(90, 1830), rnd.uniform(80, 1000)) for _ in range(NP)]
ang = lambda p: math.atan2(p[1] - CY, p[0] - OC[0])
starts.sort(key=ang); targets.sort(key=ang)                              # neighbours go to neighbouring outline points: a clean inward collapse
SIZES = [9, 14, 20]
pts = []
for i in range(NP):
    d = i % 3; size = SIZES[d]
    pts.append({"s": [round(starts[i][0], 1), round(starts[i][1], 1)], "c": [round(targets[i][0], 1), round(targets[i][1], 1)], "r": size / 2,
                "t0": round(1.0 + d * .12 + rnd.uniform(0, .35), 3), "dur": round(1.45 + d * .1 + rnd.uniform(0, .2), 3), "k": i % 7 == 0, "s2": i % 3 == 1})

# ---- S3: three portrait notes in the interview frame; the plate they grow into is the middle panel of the S4 tri-fold
NOTE_W, NOTE_H = 340, 373
NOTES = [{"cx": 575, "t": "A product decision", "n": "01"}, {"cx": 960, "t": "A customer question", "n": "02"}, {"cx": 1345, "t": "The proof behind it", "n": "03"}]
NOTE_DEPTH = [1.3, 1.1, .9]                                              # parallax depth: the nearest note travels the farthest
TRAVEL = 1300
CUT_LEN = math.dist(CUT_A, CUT_B); CUT_ANG = math.degrees(math.atan2(CUT_B[1] - CUT_A[1], CUT_B[0] - CUT_A[0]))
PW, PH, PGAP = 530, 582, 24                                             # calendar panels
PANELS = [{"id": "A", "x": 960 - PW / 2 - PGAP - PW, "y": CY - PH / 2}, {"id": "B", "x": 960 - PW / 2, "y": CY - PH / 2}, {"id": "C", "x": 960 + PW / 2 + PGAP, "y": CY - PH / 2}]
NOTE_TO_PLATE = PW / NOTE_W                                              # the middle note scales up to the panel
# ---- S4: 6 columns x 4 rows, two columns per panel
CW, CH, CG, CPAD = 232, 120, 18, 24
GRID = [["Theme", "Proof", "Format", "Post", "Theme", "Proof"],
        ["Format", "Post", "Theme", "Post", "Proof", "Format"],
        ["Proof", "Format", "Post", "Proof", "Format", "Post"],
        ["Post", "Theme", "Proof", "Format", "Post", "Theme"]]
EMPTY = {(1, 0), (3, 3), (2, 5)}
LIFT = (1, 3)
cells = []
for r in range(4):
    for c in range(6):
        pn = PANELS[c // 2]; lc = c % 2
        cells.append({"r": r, "c": c, "p": c // 2, "lx": CPAD + lc * (CW + CG), "ly": CPAD + r * (CH + CG), "x": pn["x"] + CPAD + lc * (CW + CG), "y": pn["y"] + CPAD + r * (CH + CG),
                      "w": CW, "h": CH, "t": GRID[r][c], "on": (r, c) not in EMPTY})
LIFT_I = LIFT[0] * 6 + LIFT[1]
POST = {"x": 550, "y": 260, "w": 820, "h": 480}
PCX, PCY = POST["x"] + POST["w"] / 2, POST["y"] + POST["h"] / 2

# ---- S5: buyer network (two staggered rows along the strand), signals, three separate rings
nodes = []
for k in range(12):
    x = 560 + k * 104 + rnd.uniform(-12, 12); up = k % 2 == 0
    off = (118, 170, 140, 188, 124, 160)[k % 6] if up else (100, 136, 118, 150, 108, 128)[k % 6]
    nodes.append({"x": round(x, 1), "y": round(trunk_y(x - 60) + (-off if up else off), 1), "ax": round(x - 70, 1), "ay": round(trunk_y(x - 70), 1), "r": 14 + (k * 5) % 9})
def link(nd, frac):
    """A link from its anchor on the strand to the node, an S curve with 12 points (frac < 1 collapses it onto the anchor)."""
    pts = []
    for i in range(12):
        u = i / 11; s = u * u * (3 - 2 * u)
        pts.append((nd["ax"] + (nd["x"] - nd["ax"]) * (u * .55 + s * .45) * frac, nd["ay"] + (nd["y"] - nd["ay"]) * s * frac))
    return path(pts)
RINGS = [(480, 710, "Engagement"), (960, 710, "Qualified replies"), (1440, 710, "Attributed leads")]
TRUNK_T0, TRUNK_T1 = 17.65, 18.75                                       # linear growth of the strand, so node sprouts can be timed exactly
for nd in nodes: nd["t"] = round(TRUNK_T0 + (nd["ax"] - (SRC[0] + 30)) / (1840 - (SRC[0] + 30)) * (TRUNK_T1 - TRUNK_T0), 3)
# far and mid layers of faint strands for the parallax in S5
def faint(y0, amp, wl, ph):
    return path([(-100 + 2600 * i / (N - 1), y0 + amp * math.sin((-100 + 2600 * i / (N - 1)) / wl + ph)) for i in range(N)])
FAINT = [("far", faint(210, 40, 330, .4)), ("far", faint(560, 55, 420, 2.1)), ("far", faint(900, 36, 360, 4.0)),
         ("mid", faint(330, 50, 270, 1.3)), ("mid", faint(690, 60, 310, 3.3))]

# ---- S6: three package cards (names, prices, descriptors read from pricing.json) and the final stack
PK = PRICING["packages"][:3]
PKW, PKH, PKG = 544, 360, 48
PKR = [{"x": 96 + i * (PKW + PKG), "y": 330, "w": PKW, "h": PKH} for i in range(3)]
CTA = {"w": 600, "h": 108, "cy": 744}

CFG = {"pts": pts, "sh": SH, "oc": list(OC), "shift": SHIFT, "part": PART, "mw": MW, "mh": MH, "u": U,
       "notes": [{"cx": n["cx"], "d": NOTE_DEPTH[i]} for i, n in enumerate(NOTES)], "travel": TRAVEL, "noteScale": NOTE_TO_PLATE,
       "cut": {"cx": (CUT_A[0] + CUT_B[0]) / 2, "cy": (CUT_A[1] + CUT_B[1]) / 2, "len": CUT_LEN, "ang": CUT_ANG},
       "panels": PANELS, "cells": cells, "lift": LIFT_I, "post": POST, "src": SRC,
       "nodes": nodes, "links": [[link(nd, 0.0001), link(nd, 1)] for nd in nodes], "trunkT": [TRUNK_T0, TRUNK_T1],
       "rings": [[x, y] for x, y, _ in RINGS], "pkr": PKR, "cta": CTA}

def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;")
def rect(d): return f'left:{d["x"]:.0f}px;top:{d["y"]:.0f}px;width:{d["w"]}px;height:{d["h"]}px'

css = """
.g{position:absolute;inset:0}
#gN{background:radial-gradient(1200px 820px at 84% 10%,rgba(49,87,213,.24),transparent 62%),radial-gradient(1000px 700px at 6% 98%,rgba(234,169,60,.09),transparent 60%),#0D1A3B}
.pearl{background:linear-gradient(160deg,#fff 8%,#F1F3F6 60%,#E6EBF1)}
.navy{background:radial-gradient(1100px 780px at 18% 8%,rgba(49,87,213,.22),transparent 60%),#0D1A3B}
#gA{clip-path:circle(0px at %OCX%px %OCY%px)}
#gM{background:#EAA93C;clip-path:inset(0 100% 0 0)}
#gD{clip-path:circle(0px at %PCX%px %PCY%px)}
#cam{position:absolute;inset:0}
.sc{position:absolute;inset:0;opacity:0}
#c1{opacity:1}
.mono{font-family:'Geist Mono',monospace;font-weight:500;letter-spacing:.08em;text-transform:uppercase}
.disp{font-family:'Fraunces',serif;font-weight:400;letter-spacing:-.02em;line-height:1.06}
.kick{position:absolute;left:96px;top:84px;font-size:30px;opacity:0}
.lt{color:#B9C7DA}.dk{color:#3A4A75}
.pt{position:absolute;left:0;top:0;border-radius:50%;background:#F2F5FA;opacity:0}
.pt.m{background:#EAA93C}.pt.s{background:#B9C7DA}
.mk{position:absolute;left:%MX%px;top:%MY%px;width:%MW%px;height:%MH%px}
#mkLw{position:absolute;inset:0;z-index:32;clip-path:circle(0px at %OCX%px %OCY%px)}
#sv{position:absolute;inset:0;z-index:30;overflow:visible;clip-path:inset(0 50% 0 50%)}
#strand{fill:none;stroke:#EAA93C;stroke-width:7;stroke-linecap:round;stroke-linejoin:round}
#fdots{position:absolute;inset:0}
.fd{position:absolute;border-radius:50%;background:#D3DAE7}
.rule{position:absolute;left:0;top:0;width:1920px;height:60px;overflow:visible}
.rule path{fill:none}
#play{position:absolute;left:958px;top:132px;width:4px;height:52px;border-radius:2px;background:#EAA93C;opacity:0}
.note{position:absolute;left:0;top:%NOTETOP%px;width:%NW%px;height:%NH%px;border-radius:26px;background:#fff;border:2px solid #E1E6EE;box-shadow:0 26px 50px -30px rgba(22,39,96,.55)}
.note b{position:absolute;left:30px;top:26px;font-family:'Geist Mono',monospace;font-weight:500;font-size:30px;color:#666F7F;letter-spacing:.06em}
.note p{position:absolute;left:30px;right:24px;bottom:30px;font-family:'Fraunces',serif;font-size:48px;line-height:1.06;color:#162760}
#cut{position:absolute;left:0;top:0;width:%CUTLEN%px;height:28px;border-radius:14px;background:#EAA93C;z-index:33;clip-path:inset(0 100% 0 0)}
#pos{position:absolute;left:0;right:0;top:438px;text-align:center;font-size:112px;color:#162760;opacity:0;z-index:5}
#calw{position:absolute;inset:0;perspective:2600px;perspective-origin:50% 50%}
.pnl{position:absolute;width:%PW%px;height:%PH%px;border-radius:28px;background:#fff;border:2px solid #E1E6EE;box-shadow:0 30px 60px -34px rgba(22,39,96,.6);opacity:0}
.cell{position:absolute;width:%CW%px;height:%CH%px;border-radius:16px;background:rgba(22,39,96,.05);border:2px solid #D9DEE7}
.cell i{position:absolute;inset:8px;border-radius:11px;opacity:0;display:flex;align-items:center;justify-content:center;font-style:normal;font-family:'Geist Mono',monospace;font-weight:500;font-size:31px;letter-spacing:.02em}
.k-Theme i{background:#162760;color:#F2F5FA}.k-Proof i{background:#FFF6E3;color:#162760;box-shadow:inset 0 0 0 3px #EAA93C}.k-Format i{background:#E6EBF1;color:#3A4A75}.k-Post i{background:#EAA93C;color:#0D1A3B}
#post{position:absolute;border-radius:28px;background:#EAA93C;border:2px solid #E1E6EE;box-shadow:0 30px 60px -34px rgba(22,39,96,.6);opacity:0;transform-origin:0 0;overflow:hidden;z-index:6}
#post .av{position:absolute;left:52px;top:48px;width:104px;height:104px;border-radius:50%;background:#162760;opacity:0}
#post .ln{position:absolute;height:20px;border-radius:10px;background:#E1E6EE;opacity:0}
#post .art{position:absolute;left:520px;top:48px;width:248px;height:300px;border-radius:20px;background:#E6EBF1;opacity:0}
#post .art::after{content:'';position:absolute;left:40px;top:40px;width:70px;height:70px;border-radius:50%;background:#EAA93C}
#post .tt{position:absolute;left:52px;bottom:44px;font-family:'Fraunces',serif;font-size:64px;color:#162760;opacity:0}
#nets{position:absolute;inset:0;overflow:visible}
#far{position:absolute;inset:0;opacity:0}
.lk{fill:none;stroke:#B9C7DA;stroke-width:2.5;stroke-linecap:round;opacity:0}
.fs{fill:none;stroke:#B9C7DA;stroke-width:2;stroke-linecap:round}
.node{position:absolute;left:0;top:0;border-radius:50%;border:4px solid #B9C7DA;background:#0D1A3B;opacity:0}
.sig{position:absolute;left:0;top:0;width:16px;height:16px;margin:-8px 0 0 -8px;border-radius:50%;background:#F6D591;opacity:0}
.rg{position:absolute;left:0;top:0;width:140px;height:140px;margin:-70px 0 0 -70px;border-radius:50%;border:5px solid #B9C7DA;opacity:0}
.rl{position:absolute;left:0;top:0;width:360px;margin-left:-180px;text-align:center;font-size:32px;color:#F2F5FA;opacity:0}
.pk{position:absolute;border:5px solid #B9C7DA;border-radius:28px;opacity:0;overflow:hidden;transform-origin:0 0;background:rgba(242,245,250,0)}
.pk .in{position:absolute;inset:0;padding:44px 40px;opacity:0}
.pk h3{font-family:'Fraunces',serif;font-weight:400;font-size:52px;line-height:1.05;color:#162760;letter-spacing:-.01em;white-space:nowrap}
.pk .pr{margin-top:40px;font-family:'Geist Mono',monospace;font-weight:500;font-size:76px;line-height:1.05;color:#162760;letter-spacing:-.04em}
.pk .pe{margin-top:10px;font-family:'Geist Mono',monospace;font-weight:500;font-size:30px;line-height:1.2;color:#666F7F;letter-spacing:.08em;text-transform:uppercase}
.pk .ac{position:absolute;left:40px;right:40px;bottom:40px;height:8px;border-radius:4px;background:#EAA93C;transform:scaleX(0);transform-origin:0 50%}
#pkl{position:absolute;left:0;right:0;top:242px;text-align:center;font-size:30px;opacity:0}
#lock{position:absolute;left:50%;top:230px;width:780px;margin-left:-390px}
#hero{position:absolute;left:300px;right:300px;top:430px;text-align:center;font-size:84px;color:#F2F5FA;text-wrap:balance;opacity:0}
#cta{position:absolute;left:0;top:%CTATOP%px;width:%CTAW%px;height:%CTAH%px;border-radius:999px;background:#EAA93C;color:#0D1A3B;font-size:44px;font-weight:600;display:flex;align-items:center;justify-content:center;white-space:nowrap;opacity:0}
#cap{position:absolute;left:0;right:0;bottom:68px;display:flex;justify-content:center;z-index:60}
#cap span{max-width:1400px;padding:14px 32px;border-radius:16px;background:rgba(13,26,59,.88);color:#F1F3F6;font-size:36px;line-height:1.3;text-align:center;opacity:0}
"""
for a, b in {"%OCX%": f"{OC[0]:.0f}", "%OCY%": f"{OC[1]:.0f}", "%PCX%": f"{PCX:.0f}", "%PCY%": f"{PCY:.0f}", "%MX%": f"{MX:.1f}", "%MY%": f"{MY:.1f}", "%MW%": str(MW), "%MH%": f"{MH:.1f}",
             "%NW%": str(NOTE_W), "%NH%": str(NOTE_H), "%NOTETOP%": f"{CY - NOTE_H / 2:.0f}", "%CUTLEN%": f"{CUT_LEN:.0f}", "%PW%": str(PW), "%PH%": str(PH),
             "%CW%": str(CW), "%CH%": str(CH), "%CTATOP%": f"{CTA['cy'] - CTA['h'] / 2:.0f}", "%CTAW%": str(CTA["w"]), "%CTAH%": str(CTA["h"])}.items():
    css = css.replace(a, b)

parts_html = "".join(f'<div class="pt{" m" if p["k"] else (" s" if p["s2"] else "")}" id="p{i}" style="width:{p["r"] * 2:.0f}px;height:{p["r"] * 2:.0f}px;margin:{-p["r"]:.0f}px 0 0 {-p["r"]:.0f}px"></div>' for i, p in enumerate(pts))
notes_html = "".join(f'<div class="note" id="n{i}" data-layout-allow-overflow style="left:{n["cx"] - NOTE_W / 2:.0f}px"><b>{n["n"]}</b><p>{esc(n["t"])}</p></div>' for i, n in enumerate(NOTES))
def tick_path(pitch, h, col, op):
    return f'<path d="M-600,{h / 2} H2700" stroke="{col}" stroke-width="{h}" stroke-dasharray="3 {pitch - 3}" opacity="{op}"/>'
far_dots = [(rnd.uniform(40, 1880), rnd.uniform(230, 960), rnd.choice((8, 11, 14))) for _ in range(30)]
dots_html = '<div id="fdots">' + "".join(f'<div class="fd" style="left:{x:.0f}px;top:{y:.0f}px;width:{r}px;height:{r}px;margin:{-r // 2}px 0 0 {-r // 2}px"></div>' for x, y, r in far_dots) + '</div>'
rule_html = (f'<svg class="rule" id="ruleF" style="top:156px" viewBox="0 0 1920 60">{tick_path(48, 16, "#C9D2E0", 1)}</svg>'
             f'<svg class="rule" id="ruleM" style="top:148px" viewBox="0 0 1920 60">{tick_path(240, 34, "#9AA6BD", 1)}</svg>')
panels_html = ""
for pn in PANELS:
    cs = "".join(f'<div class="cell k-{c["t"]}" id="ce{c["r"] * 6 + c["c"]}" style="left:{c["lx"]}px;top:{c["ly"]}px"><i>{c["t"] if c["on"] else ""}</i></div>' for c in cells if PANELS[c["p"]]["id"] == pn["id"])
    panels_html += f'<div class="pnl" id="pn{pn["id"]}" style="left:{pn["x"]:.0f}px;top:{pn["y"]:.0f}px">{cs}</div>'
post_html = (f'<div id="post" data-layout-allow-occlusion style="{rect(POST)}"><div class="av"></div><div class="ln" style="left:176px;top:62px;width:300px;background:#162760"></div>'
             '<div class="ln" style="left:176px;top:100px;width:200px"></div><div class="ln" style="left:52px;top:200px;width:420px"></div>'
             '<div class="ln" style="left:52px;top:240px;width:380px"></div><div class="ln" style="left:52px;top:280px;width:410px"></div><div class="art"></div><div class="tt">Post</div></div>')
faint_html = "".join(f'<svg class="fsv" id="fs{i}" style="position:absolute;inset:0;overflow:visible;opacity:{.12 if L == "far" else .2}" viewBox="0 0 {W} {H}"><path class="fs" d="{d}"/></svg>' for i, (L, d) in enumerate(FAINT))
net_html = (f'<svg id="nets" viewBox="0 0 {W} {H}" width="{W}" height="{H}">' + "".join(f'<path class="lk" id="lk{i}" d="{CFG["links"][i][0]}"/>' for i in range(len(nodes))) + '</svg>'
            + "".join(f'<div class="node" id="nd{i}" style="width:{nd["r"] * 2}px;height:{nd["r"] * 2}px;margin:{-nd["r"]}px 0 0 {-nd["r"]}px"></div>' for i, nd in enumerate(nodes))
)
rings_html = "".join(f'<div class="rg" id="rg{i}"></div><div class="rl" id="rl{i}">{t}</div>' for i, (x, y, t) in enumerate(RINGS))
pk_html = "".join(
    f'<div class="pk" id="pk{i}" style="{rect(PKR[i])}"><div class="in"><h3>{esc(p["name"])}</h3>'
    f'<div class="pr">{esc(p["display_price"].split(" /")[0])}</div><div class="pe">{"one-off" if p["period"] == "one-off" else "per month"}</div>'
    f'</div><div class="ac"></div></div>' for i, p in enumerate(PK))
body = f"""
      <div class="g" id="gN"></div>
      <div class="mk" id="mkD">{K.mark_svg(mk, "mkDs", o="#F2F5FA", s="#B9C7DA", width=MW)}</div>
      <div class="g pearl" id="gA"></div><div class="g" id="gM"></div><div class="g navy" id="gD"></div>
      <div id="cam">
        <div class="sc" id="c1">{parts_html}<div class="kick mono lt" id="k1">Your thinking</div></div>
        <div class="sc" id="c2">{dots_html}<div class="kick mono dk" id="k2">Interview</div>{rule_html}<div id="play"></div></div>
        <div class="sc" id="c3">{notes_html}<div id="cut" data-layout-allow-occlusion></div></div>
        <div class="sc" id="c4">
          <div class="kick mono dk" id="k4">Plan</div>
          <div id="calw">{panels_html}</div>
          <div class="disp" id="pos">Position</div>
          {post_html}
        </div>
        <div id="far">{faint_html}</div>
        <div class="sc" id="c5">
          <div class="kick mono lt" id="k5">Conversations</div>
          <div id="net">{net_html}</div>
          {"".join(f'<div class="sig" id="sg{i}"></div>' for i in range(9))}
          {rings_html}
        </div>
        <div class="sc" id="c6">
          <div class="mono lt" id="pkl">{esc(PRICING["public_label"])}</div>
          {pk_html}
          <img id="lock" src="assets/brand/lockup-os-inverse.svg" alt="">
          <div class="disp" id="hero">{esc(PROT["hero"])}</div>
          <div id="cta">{esc(PROT["cta"])}</div>
        </div>
      </div>
      <div id="mkLw"><div class="mk" id="mkL">{K.mark_svg(mk, "mkLs", width=MW)}</div></div>
      <svg id="sv" viewBox="0 0 {W} {H}" width="{W}" height="{H}"><path id="strand" d="{SH['flat']}"/></svg>
      <div id="cap"><span id="capt"></span></div>
"""

js = "const CFG = " + json.dumps(CFG) + ";\nconst LINES = " + json.dumps(LINES) + ";\n" + r"""
        const q = s => document.querySelector(s), qa = s => [...document.querySelectorAll(s)];
        const SM = 'power3.inOut', SO = 'power3.out';
        const show = (id, t) => tl.set(id, {opacity: 1}, t), hide = (id, t) => tl.set(id, {opacity: 0}, t);
        const at = (r) => 'at ' + r[0] + 'px ' + r[1] + 'px)';
        const DRIFT0 = 17.4, DRIFT_DUR = 4.0, DRIFT_X = -90;                      // slow left drift of the buyer network in S5
        const drift = t => DRIFT_X * gsap.parseEase('sine.inOut')(Math.min(1, Math.max(0, (t - DRIFT0) / DRIFT_DUR)));
        // static placement of elements that are moved by transforms only (no layout property is ever tweened)
        tl.set('#cut', {x: CFG.cut.cx - CFG.cut.len / 2, y: CFG.cut.cy - 14, rotation: CFG.cut.ang, transformOrigin: '50% 50%'}, 0);
        tl.set('#cta', {x: 960 - CFG.cta.w / 2}, 0);
        tl.set('#pnA', {transformOrigin: (CFG.panels[1].x - CFG.panels[0].x) + 'px 50%'}, 0);
        tl.set('#pnC', {transformOrigin: (CFG.panels[1].x + 530 - CFG.panels[2].x) + 'px 50%'}, 0);

        // ===== S1 0-4: the thought field contracts onto the O's outline; the mark resolves; pearl opens out of the O's counter
        tl.fromTo('#k1', {opacity: 0}, {opacity: 1, duration: .4}, .5); tl.to('#k1', {opacity: 0, duration: .3}, 2.9);
        CFG.pts.forEach((p, i) => {
          tl.fromTo('#p' + i, {x: p.s[0], y: p.s[1], opacity: 0, scale: .4}, {opacity: .9, scale: 1, duration: .8, ease: SO}, .1 + (i % 20) * .03);
          tl.to('#p' + i, {x: p.c[0], duration: p.dur, ease: 'power2.inOut'}, p.t0);      // different eases on x and y bend each path inwards
          tl.to('#p' + i, {y: p.c[1], duration: p.dur, ease: 'power3.inOut'}, p.t0);
          tl.to('#p' + i, {opacity: 0, scale: .3, duration: .35}, 2.85 + (i % 8) * .02);
        });
        tl.fromTo('#mkD .ol, #mkD .or', {opacity: 0}, {opacity: 1, duration: .5, ease: 'power2.out'}, 2.55);
        tl.fromTo('#mkD .ms', {x: 14, opacity: 0}, {x: 0, opacity: 1, duration: .55, ease: SO}, 2.85);
        tl.fromTo('#mkD .mg', {scale: 0, opacity: 0, transformOrigin: '50% 50%'}, {scale: 1, opacity: 1, duration: .45, ease: 'back.out(1.8)'}, 3.05);
        // seam: the pearl ground and the navy-ink copy of the mark share one circle that grows from the O's counter (the colour change is exact)
        ['#gA', '#mkLw'].forEach(id => tl.fromTo(id, {clipPath: 'circle(0px ' + at(CFG.oc)}, {clipPath: 'circle(1500px ' + at(CFG.oc), duration: 1.1, ease: SM}, 3.2));
        hide('#mkD', 4.35); hide('#c1', 4.0); show('#c2', 3.9);

        // ===== S2 4-8: the S and slash step back, the O moves to the centre and parts into a wide interview frame; the strand threads through
        tl.to('#mkL .ms', {x: 18, scale: .9, opacity: 0, duration: .6, ease: 'power2.in'}, 4.0);
        tl.to('#mkL .mg', {x: 18, scale: .6, opacity: 0, duration: .5, ease: 'power2.in'}, 4.0);
        tl.to('#mkL', {x: CFG.shift, duration: .9, ease: SM}, 4.0);
        tl.to('#mkL .ol', {x: -CFG.part, duration: 1.05, ease: SM}, 4.5);
        tl.to('#mkL .or', {x: CFG.part, duration: 1.05, ease: SM}, 4.5);
        tl.fromTo('#k2', {opacity: 0}, {opacity: 1, duration: .4}, 4.4); tl.to('#k2', {opacity: 0, duration: .3}, 7.9);
        tl.fromTo('#sv', {clipPath: 'inset(0% 50% 0% 50%)'}, {clipPath: 'inset(0% 0% 0% 0%)', duration: .9, ease: SO}, 4.75);   // the strand fills the gap as it opens
        tl.to('#strand', {attr: {d: CFG.sh.w1}, duration: .55, ease: SM}, 5.15);
        tl.to('#strand', {attr: {d: CFG.sh.w2}, duration: .5, ease: 'sine.inOut'}, 5.7);
        tl.to('#strand', {attr: {d: CFG.sh.w3}, duration: .5, ease: 'sine.inOut'}, 6.2);
        tl.to('#strand', {attr: {d: CFG.sh.w4}, duration: .45, ease: 'sine.inOut'}, 6.7);
        tl.to('#strand', {attr: {d: CFG.sh.flat}, duration: .5, ease: SM}, 7.15);
        // camera travel with parallax: the frame stays fixed on the lens; pale dots, far ticks, mid ticks and three notes pass at different depths
        tl.fromTo('#fdots', {x: 0, opacity: 0}, {x: -CFG.travel * .14, duration: 4.2, ease: 'power2.inOut'}, 4.2);
        tl.fromTo('#ruleF', {x: 0, opacity: 0}, {x: -CFG.travel * .3, duration: 4.0, ease: 'power2.inOut'}, 4.4);
        tl.fromTo('#ruleM', {x: 0, opacity: 0}, {x: -CFG.travel * .62, duration: 4.0, ease: 'power2.inOut'}, 4.4);
        tl.to(['#fdots', '#ruleF', '#ruleM'], {opacity: 1, duration: .5}, 4.1);
        tl.fromTo('#play', {opacity: 0}, {opacity: 1, duration: .5}, 4.6);
        show('#c3', 7.1);
        CFG.notes.forEach((n, i) => {
          tl.fromTo('#n' + i, {x: CFG.travel * n.d, scale: 1 + (n.d - .9) * .15}, {x: 0, scale: 1, duration: 1.4 - i * .06, ease: SO}, 7.25 + i * .1);
        });
        tl.to(['#fdots', '#ruleF', '#ruleM', '#play'], {opacity: 0, duration: .4}, 8.2);
        hide('#c2', 8.8);

        // ===== S3 8-12: the strand becomes the cut, a marigold slash crosses the notes, two notes leave, one becomes "Position"
        tl.to('#strand', {attr: {d: CFG.sh.cut}, duration: .75, ease: SM}, 8.9);
        tl.to('#cut', {clipPath: 'inset(0% 0% 0% 0%)', duration: .5, ease: 'power3.in'}, 9.6);
        tl.to('#strand', {opacity: 0, duration: .25}, 10.05);
        tl.to('#n0', {x: -1000, y: -330, rotation: -14, duration: .65, ease: 'power2.inOut'}, 10.0);
        tl.to('#n2', {x: 1000, y: 330, rotation: 14, duration: .65, ease: 'power2.inOut'}, 10.0);
        tl.to('#n1 b, #n1 p', {opacity: 0, duration: .25}, 10.1);
        tl.to('#n1', {scale: CFG.noteScale, duration: .7, ease: SM}, 10.25);
        tl.to('#cut', {clipPath: 'inset(0% 0% 0% 100%)', duration: .5, ease: 'power3.out'}, 10.2);
        tl.to('#mkL .ol', {x: -CFG.part - 110, duration: .75, ease: 'power3.in'}, 10.5);    // the frame leaves through the sides
        tl.to('#mkL .or', {x: CFG.part + 110, duration: .75, ease: 'power3.in'}, 10.5);
        hide('#mkLw', 11.3);
        // the marigold curtain: a clipped field that sweeps across behind the notes, then leaves the way it came
        tl.fromTo('#gM', {clipPath: 'inset(0% 100% 0% 0%)'}, {clipPath: 'inset(0% 0% 0% 0%)', duration: .65, ease: SM}, 10.4);
        tl.to('#gM', {clipPath: 'inset(0% 0% 0% 100%)', duration: .75, ease: SM}, 11.2);
        show('#c4', 10.3);
        tl.fromTo('#pos', {opacity: 0, y: 22}, {opacity: 1, y: 0, duration: .55, ease: SO}, 10.8);
        hide('#c3', 12.5);

        // ===== S4 12-17: the Position card is the middle panel of a tri-fold; the wings open into a 6 x 4 calendar; one cell lifts into a post
        tl.set('#pnB', {opacity: 1}, 11.85); tl.set('#n1', {opacity: 0}, 11.85);
        tl.set(['#pnA', '#pnC'], {opacity: 1}, 11.95);
        tl.fromTo('#pnA', {rotationY: -90}, {rotationY: 0, duration: .95, ease: SO}, 12.0);
        tl.fromTo('#pnC', {rotationY: 90}, {rotationY: 0, duration: .95, ease: SO}, 12.0);
        tl.to('#pos', {opacity: 0, y: -14, duration: .3}, 12.2);
        tl.fromTo('#pnB .cell', {opacity: 0}, {opacity: 1, duration: .3}, 12.35);
        tl.fromTo('#k4', {opacity: 0}, {opacity: 1, duration: .4}, 12.3);
        CFG.cells.forEach((c, i) => { if (c.on) tl.fromTo('#ce' + i + ' i', {opacity: 0, scale: .8}, {opacity: 1, scale: 1, duration: .28, ease: 'back.out(1.7)'}, 12.95 + (c.c * 4 + c.r) * .085); });
        { const c = CFG.cells[CFG.lift], d = CFG.post;
          tl.fromTo('#post', {x: c.x - d.x, y: c.y - d.y, scaleX: c.w / d.w, scaleY: c.h / d.h, opacity: 0, backgroundColor: '#EAA93C'}, {opacity: 1, duration: .01}, 15.1);
          tl.to('#post', {x: 0, y: 0, scaleX: 1, scaleY: 1, backgroundColor: '#FFFFFF', duration: .8, ease: SM}, 15.15);
          tl.to('#post .av, #post .ln, #post .art, #post .tt', {opacity: 1, duration: .35, stagger: .05}, 15.8); }
        tl.to('#pnA', {rotationY: -90, duration: .75, ease: 'power3.in'}, 15.1);              // the wings fold shut behind the post
        tl.to('#pnC', {rotationY: 90, duration: .75, ease: 'power3.in'}, 15.1);
        tl.to('#pnB', {opacity: 0, duration: .5}, 15.4);
        tl.to('#pnA, #pnC', {opacity: 0, duration: .3}, 15.55);
        CFG.cells.forEach((c, i) => tl.to('#ce' + i, {opacity: 0, y: 26, duration: .4, ease: 'power2.in'}, 15.1 + ((i * 7) % 24) * .012));
        tl.to('#k4', {opacity: 0, duration: .3}, 16.0);
        tl.fromTo('#gD', {clipPath: 'circle(0px at ' + (CFG.post.x + CFG.post.w / 2) + 'px ' + (CFG.post.y + CFG.post.h / 2) + 'px)'}, {clipPath: 'circle(1500px at ' + (CFG.post.x + CFG.post.w / 2) + 'px ' + (CFG.post.y + CFG.post.h / 2) + 'px)', duration: 1.0, ease: SM}, 16.3);

        // ===== S5 17-22: the post shrinks into a node; the strand grows left to right into a buyer network; signals return to three rings
        show('#c5', 17.05);
        tl.to('#post > *', {opacity: 0, duration: .2}, 17.0);
        tl.to('#post', {x: CFG.src[0] - 28 - CFG.post.x, y: CFG.src[1] - 28 - CFG.post.y, scaleX: 56 / CFG.post.w, scaleY: 56 / CFG.post.h, borderRadius: '50%', borderColor: '#F2F5FA', duration: .85, ease: SM}, 17.0);
        tl.fromTo('#k5', {opacity: 0}, {opacity: 1, duration: .4}, 17.3);
        tl.fromTo('#far', {opacity: 0}, {opacity: 1, duration: .6}, 17.05);                                    // faint strands stay to the end and keep drifting
        tl.fromTo('#far svg:nth-child(-n+3)', {x: 0}, {x: -165, duration: 11, ease: 'none'}, 17.0);          // far and mid strands drift at their own speeds
        tl.fromTo('#far svg:nth-child(n+4)', {x: 0}, {x: -385, duration: 11, ease: 'none'}, 17.0);
        tl.fromTo('#net', {x: 0}, {x: DRIFT_X, duration: DRIFT_DUR, ease: 'sine.inOut'}, DRIFT0);
        tl.set('#strand', {attr: {d: CFG.sh.t0}}, 16.95);
        tl.set('#strand', {opacity: 1}, 17.62);
        tl.to('#strand', {attr: {d: CFG.sh.t1}, duration: CFG.trunkT[1] - CFG.trunkT[0], ease: 'none'}, CFG.trunkT[0]);
        CFG.nodes.forEach((n, i) => {                                                                       // each link and node sprouts where the growing tip passes
          tl.fromTo('#lk' + i, {opacity: 0}, {opacity: .55, duration: .2}, n.t);
          tl.to('#lk' + i, {attr: {d: CFG.links[i][1]}, duration: .45, ease: SO}, n.t);
          tl.fromTo('#nd' + i, {x: n.ax, y: n.ay, opacity: 0, scale: .3}, {opacity: 1, duration: .25}, n.t);
          tl.to('#nd' + i, {x: n.x, y: n.y, scale: 1, duration: .45, ease: SO}, n.t);
          tl.to('#nd' + i, {backgroundColor: '#EAA93C', borderColor: '#EAA93C', duration: .2}, 18.4 + i * .07);
        });
        CFG.rings.forEach((r, i) => {
          tl.fromTo('#rg' + i, {x: r[0], y: r[1], opacity: 0, scale: .5}, {opacity: 1, scale: 1, duration: .45, ease: SO}, 18.5 + i * .13);
          tl.fromTo('#rl' + i, {x: r[0], y: r[1] + 106, opacity: 0}, {opacity: 1, duration: .45, ease: SO}, 18.65 + i * .13);
        });
        for (let i = 0; i < 9; i++) {                                                                       // replies return to the three rings; no numbers anywhere
          const n = CFG.nodes[(i * 5 + 2) % 12], r = CFG.rings[i % 3], t0 = 19.2 + i * .12;
          tl.fromTo('#sg' + i, {x: n.x + drift(t0), y: n.y, opacity: 0}, {opacity: 1, duration: .1}, t0);
          tl.to('#sg' + i, {x: r[0], duration: .7, ease: 'power2.inOut'}, t0);
          tl.to('#sg' + i, {y: r[1], duration: .7, ease: 'power3.in'}, t0);
          tl.to('#sg' + i, {opacity: 0, duration: .1}, t0 + .68);
          tl.fromTo('#rg' + (i % 3), {borderColor: '#B9C7DA', scale: 1}, {borderColor: '#EAA93C', scale: 1.08, duration: .15, yoyo: true, repeat: 1, immediateRender: false}, t0 + .65);
        }

        // ===== S6 22-28: the rings fold into package cards; the cards sink into the call to action; lockup and hero line
        tl.to(['#k5', '#net', '#strand', '#post'], {opacity: 0, duration: .3}, 20.9);
        tl.to('.rl', {opacity: 0, duration: .25}, 20.95);
        show('#c6', 20.85);
        tl.fromTo('#pkl', {opacity: 0, y: 12}, {opacity: 1, y: 0, duration: .5, ease: SO}, 20.95);
        CFG.rings.forEach((r, i) => { const d = CFG.pkr[i], s = 140 / d.w, sy = 140 / d.h;
          tl.to('#rg' + i, {rotationY: 90, transformPerspective: 1400, duration: .3, ease: 'power2.in'}, 20.95 + i * .1);
          tl.set('#rg' + i, {opacity: 0}, 21.26 + i * .1);
          tl.fromTo('#pk' + i, {x: r[0] - 70 - d.x, y: r[1] - 70 - d.y, scaleX: s, scaleY: sy, rotationY: -90, transformPerspective: 1400, borderRadius: '50%', opacity: 0}, {opacity: 1, duration: .01}, 21.2 + i * .1);
          tl.to('#pk' + i, {rotationY: 0, duration: .55, ease: SO}, 21.2 + i * .1);
          tl.to('#pk' + i, {x: 0, y: 0, scaleX: 1, scaleY: 1, borderRadius: '28px', backgroundColor: '#F2F5FA', borderColor: '#F2F5FA', duration: .85, ease: SM}, 21.25 + i * .1);
          tl.to('#pk' + i + ' .in', {opacity: 1, duration: .4}, 21.6 + i * .1);
          tl.to('#pk' + i + ' .ac', {scaleX: 1, duration: .5, ease: SO}, 22.1 + i * .1); });
        hide('#c5', 21.7); hide('#c4', 21.5);
        // the cards sink into one marigold bar (pill corners) that becomes the call to action
        tl.to(['#pk0 .in', '#pk1 .in', '#pk2 .in', '#pk0 .ac', '#pk1 .ac', '#pk2 .ac'], {opacity: 0, duration: .22}, 23.2);
        tl.to('#pkl', {opacity: 0, duration: .25}, 23.3);
        [0, 1, 2].forEach(i => {                                                                              // transform-origin is the top left corner of each card
          const d = CFG.pkr[i], sx = CFG.cta.w / d.w, sy = CFG.cta.h / d.h, rx = (CFG.cta.h / 2) / sx + 'px ' + (CFG.cta.h / 2) / sy + 'px';
          tl.to('#pk' + i, {x: 960 - CFG.cta.w / 2 - d.x, y: CFG.cta.cy - CFG.cta.h / 2 - d.y, scaleY: sy, scaleX: sx, backgroundColor: '#EAA93C', borderColor: '#EAA93C', duration: .7, ease: SM}, 23.3);
          tl.to('#pk' + i, {borderTopLeftRadius: rx, borderTopRightRadius: rx, borderBottomLeftRadius: rx, borderBottomRightRadius: rx, duration: .7, ease: SM}, 23.3);
        });
        tl.to(['#pk0', '#pk2'], {opacity: 0, duration: .15}, 23.9);
        tl.fromTo('#lock', {clipPath: 'inset(0% 100% 0% 0%)', y: 18}, {clipPath: 'inset(0% 0% 0% 0%)', y: 0, duration: .55, ease: SO}, 23.95);
        show('#hero', 23.99); show('#cta', 24.01);
        tl.fromTo('#hero', {clipPath: 'inset(-5% -5% 100% -5%)', y: 28}, {clipPath: 'inset(-5% -5% -20% -5%)', y: 0, duration: .6, ease: SO}, 24.0);   // the clip box is taller than the line box so descenders stay whole
        tl.fromTo('#cta', {clipPath: 'inset(0% 100% 0% 0%)'}, {clipPath: 'inset(0% 0% 0% 0%)', duration: .28, ease: SO}, 24.02);
        tl.set('#pk1', {opacity: 0}, 24.32);
        tl.to('#far', {opacity: 0, duration: .5}, 23.95);                                                   // the lockup keeps its clear space
        tl.fromTo('#c6', {scale: 1}, {scale: 1.025, duration: 3.5, ease: 'none'}, 24.5);                       // a very slow push-in carries the final hold

        // ===== captions: native lower-third type that follows the narration windows (each fades out as its window ends)
        LINES.forEach(([a, b, t]) => {
          tl.set('#capt', {textContent: t}, a);
          tl.fromTo('#capt', {opacity: 0, y: 12}, {opacity: 1, y: 0, duration: .25, ease: SO, immediateRender: false}, a);
          tl.to('#capt', {opacity: 0, duration: .2}, b - .2);
        });
        tl.to({}, {duration: .01}, %DUR% - .01);
""".replace("%DUR%", str(DUR))

PROJ.mkdir(parents=True, exist_ok=True)
(PROJ / "index.html").write_text(K.root_html(W, H, DUR, css, body, js, "assets/audio/" + ("mix-with-guide.wav" if GUIDE else "mix-voice-ready.wav")), encoding="utf-8")
(PROJ / "hyperframes.json").write_text(json.dumps({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json", "paths": {"blocks": "compositions", "assets": "assets"}}, indent=2))
(PROJ / "meta.json").write_text(json.dumps({"id": "outspoken-os-motion-r15-16x9", "name": "outspoken-os-motion-r15-16x9"}, indent=2))
if "--audio" in sys.argv:
    print(K.make_audio(PROJ / "assets" / "audio", DUR, CUTS, LINES, chords=[48, 43, 45, 41], bpm=104, seed=2828, events=EVENTS))
K.write_vo(HERE / "16x9", "Outspoken OS motion film R15 (16:9)", DUR, LINES, SCENES,
           "Narration for a human voice (wording proposed by Codex, R15; identical to the 4:5 film, so one recording fits both frames). The render carries music and effects only; no voice is generated.")
print("built", PROJ / "index.html")
