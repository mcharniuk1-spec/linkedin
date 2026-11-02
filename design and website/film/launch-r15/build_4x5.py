#!/usr/bin/env python3
"""Outspoken launch film R15, 4:5 recomposition (proposed): 42 s, 1080x1350, 30 fps, HyperFrames root composition generated from this script.

An independent re-composition of film/launch-r15/build.py (16:9) for the tall frame, not a crop or a scaled copy: the same eight stages, cut times,
narration windows and captions (thought, interview, position, market, plan, create, conversations, packages), but every stage is laid out and
choreographed again on the vertical axis. One marigold strand carries the founder's material and every object turns into the next one:
  S1 particles -> three stacked clusters -> a vertical line (the strand)   | seam: pearl ground opens out of the strand as a vertical slit (clip field)
  S2 the strand speaks as a vertical waveform and unfolds into three stacked source cards | cards slide together
  S3 the stack is cut by the OS stencil (a two-clip aperture: silhouette closes, counter opens) and becomes the O; the strand wraps into the slash;
     the S is revealed by a mask | a marigold band leads the navy field along the slash diagonal (the only diagonal wipe in the film)
  S4 the mark shrinks into a lens; three parallax layers of market strands travel top to bottom through it; three stacked buyer questions
     | the lens flattens into the calendar's top edge, pearl folds down from the top
  S5 a 3D fold opens the calendar (4 columns x 6 rows) | three cells are selected and lift out
  S6 the cells become a founder profile, a post and a carousel (pages fan out), stacked; the strand stays attached underneath | navy grows out of the post card
  S7 the pieces travel up to buyer nodes; replies return as signals to three stacked, unquantified rings | the rings fold into package cards
  S8 three package cards (names and prices read from pricing.json), then the stacked OS lockup, the protected hero line and the call to action
Transition mechanisms: path morph (strand), mask and clip reveals (stencil aperture, S reveal, slit, lockup), camera travel with parallax (market
layers), 3D folds (calendar open and fold back), clipped colour fields (slit, diagonal band, top fold, circle).
Rules kept: HyperFrames 0.9.2 animates transforms, opacity, colours, clip-path and SVG d only; one fromTo per element, then to tweens; the strand has a
fixed point count; clip-path strings are written in the shortest browser form (a trailing .0 stops GSAP from interpolating them).
Safe zone at rest: x 64 to 1016, y 64 to 1286, captions included; type is 28 px or more.
Usage: python3 build_4x5.py <project_dir> <paths_json> [--audio] [--guide]"""
import sys, pathlib, json, math, random, re, shutil
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import filmkit as K
PROJ = pathlib.Path(sys.argv[1]); PATHS = sys.argv[2]; GUIDE = "--guide" in sys.argv
SITE = HERE.parents[1] / "website" / "website-v3"
IDENT = HERE.parents[1] / "assets" / "public" / "assets" / "identity" / "v13"
PROT = json.loads((SITE / "content.json").read_text(encoding="utf-8"))["protected"]
PRICING = json.loads((SITE / "pricing.json").read_text(encoding="utf-8"))
W, H, DUR = 1080, 1350, 42.0
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
# one designed sound for each visual beat of this choreography (kind, time[, count, spacing]); times follow the timeline below
EVENTS = [("shimmer", .2),                                                                    # S1 particles appear
          ("tick", 1.7, 10, .15), ("pop", 2.3), ("pop", 2.42), ("pop", 2.54),                 # gathering into clusters, three cluster labels
          ("swoosh", 3.85), ("pop", 4.5),                                                     # line-up, strand draws
          ("swoosh", 5.1), ("tick", 5.9, 3, .55),                                             # S2 waveform and its three swings
          ("pop", 7.7), ("pop", 7.95), ("pop", 8.2), ("tick", 8.5, 4, .3),                    # three cards unfold, their mini waves move
          ("swoosh", 10.0), ("riser", 10.7), ("thump", 11.3), ("swoosh", 11.25), ("pop", 11.5),  # S3 cards slide, stencil cut closes, O locks, S reveals, slash fills
          ("swoosh", 12.0), ("shimmer", 12.6),                                                # diagonal band, "Position"
          ("swoosh", 14.0), ("pop", 14.3), ("tick", 14.9, 8, .3),                             # S4 mark into lens, lens, market layers travel
          ("pop", 15.6), ("pop", 16.05), ("pop", 16.5), ("riser", 17.6), ("swoosh", 18.2),    # three questions, lens flattens
          ("thump", 18.95)] \
         + [("tick", 20.0 + r * .38, 4, .085) for r in range(6)] \
         + [("pop", 23.5), ("pop", 23.65), ("pop", 23.8),                                     # S5 calendar fills row by row, three cells are selected
          ("swoosh", 24.3, 3, .12), ("swoosh", 24.5), ("pop", 25.1, 3, .12),                  # S6 cells lift, calendar folds back, content appears
          ("swoosh", 26.6, 3, .18), ("riser", 27.6), ("swoosh", 28.2), ("thump", 28.5),       # pages fan out, navy grows from the post
          ("swoosh", 29.0, 3, .12), ("tick", 29.4, 12, .05), ("pop", 30.4, 12, .1),           # S7 pieces fly to nodes, nodes appear and light up
          ("pop", 30.6), ("pop", 30.75), ("pop", 30.9), ("tick", 31.5, 9, .12),               # three rings, signals return
          ("swoosh", 34.0), ("pop", 34.95), ("pop", 35.3), ("pop", 35.65), ("tick", 36.6, 3, .15),  # S8 rings open into cards, content, accent bars
          ("swoosh", 37.8), ("thump", 38.4), ("shimmer", 38.5), ("pop", 38.7), ("pop", 39.1), ("shimmer", 39.15)]  # lockup, hero line, call to action
rnd = random.Random(4545)
N = 64                      # fixed point count of every strand shape (attr d morphs need equal counts)
CX = W / 2

# ------------------------------------------------------------------ small geometry helpers
def num(v):
    """Shortest decimal form, as the browser writes it: GSAP only interpolates clip-path strings whose numbers match this form (no trailing .0)."""
    t = f"{v:.1f}"
    return (t.rstrip("0").rstrip(".") if "." in t else t) + "px"
def path(pts): return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
def seg(p0, p1): return [(p0[0] + (p1[0] - p0[0]) * i / (N - 1), p0[1] + (p1[1] - p0[1]) * i / (N - 1)) for i in range(N)]
def vline(x, y0, y1): return path(seg((x, y0), (x, y1)))
def hline(y, x0, x1): return path(seg((x0, y), (x1, y)))
def hcurve(x0, x1, y, bend): return path([(x0 + (x1 - x0) * i / (N - 1), y + bend * math.sin(math.pi * i / (N - 1))) for i in range(N)])
def vwave(ph, amp, y0=170, y1=1130):
    """The speaking waveform runs top to bottom: x oscillates around the centre axis, six swings with a soft envelope."""
    out = []
    for i in range(N):
        u = i / (N - 1)
        out.append((CX + amp * math.sin(2 * math.pi * 6 * u + ph) * math.sin(math.pi * u) ** 1.2 * (.6 + .4 * math.sin(5 * u + ph)), y0 + (y1 - y0) * u))
    return path(out)
def outline(corners):
    """Closed polygon sampled into N points by arc length (the strand wraps around a shape and ends where it started)."""
    n = len(corners); edges = [(corners[i], corners[(i + 1) % n]) for i in range(n)]
    L = [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in edges]; tot = sum(L); pts = []
    for i in range(N):
        d = tot * i / (N - 1); k = 0
        while k < n - 1 and d > L[k]: d -= L[k]; k += 1
        a, b = edges[k]; u = min(1.0, d / L[k]); pts.append((a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u))
    return path(pts)
def ease_p3io(t):                      # GSAP power3.inOut, used to time effects against the diagonal band
    return 4 * t ** 3 if t < .5 else 1 - (-2 * t + 2) ** 3 / 2
def solve_ease(p):                     # inverse of ease_p3io on [0,1]
    lo, hi = 0.0, 1.0
    for _ in range(50):
        m = (lo + hi) / 2
        if ease_p3io(m) < p: lo = m
        else: hi = m
    return (lo + hi) / 2

# ------------------------------------------------------------------ the OS mark: placement, slash outline, stencil aperture
mk = K.mark_parts(PATHS)
MW = 760; MH = MW * mk[1] / mk[0]; K_ = MW / mk[0]
MX = (W - MW) / 2; MCY = 520; MY = MCY - MH / 2
def mpx(x, y): return (MX + x * K_, MY + y * K_)
SLASH = [mpx(103.9, 75.7), mpx(130.9, 75.6), mpx(115.0, 98.9), mpx(87.8, 98.9)]   # corners of the marigold slash of the stencil mark

def sample_subpaths(d, seg_px=4.5):
    """Absolute M/L/C/Z path -> one polyline per subpath (curves sampled to chords of about seg_px at mark scale)."""
    toks = re.findall(r"[MLCZ]|-?\d+(?:\.\d+)?", d); subs, cur, pos, i = [], None, None, 0
    while i < len(toks):
        c = toks[i]; i += 1
        if c == "M": x, y = float(toks[i]), float(toks[i + 1]); i += 2; cur = [(x, y)]; subs.append(cur); pos = (x, y)
        elif c == "L": x, y = float(toks[i]), float(toks[i + 1]); i += 2; cur.append((x, y)); pos = (x, y)
        elif c == "C":
            x1, y1, x2, y2, x, y = (float(t) for t in toks[i:i + 6]); i += 6; x0, y0 = pos
            ln = (math.hypot(x1 - x0, y1 - y0) + math.hypot(x2 - x1, y2 - y1) + math.hypot(x - x2, y - y2)) * K_
            n = max(1, math.ceil(ln / seg_px))
            for s in range(1, n + 1):
                t = s / n; u = 1 - t
                cur.append((u ** 3 * x0 + 3 * u * u * t * x1 + 3 * u * t * t * x2 + t ** 3 * x, u ** 3 * y0 + 3 * u * u * t * y1 + 3 * u * t * t * y2 + t ** 3 * y))
            pos = (x, y)
    return subs
def dedupe(p):
    out = [p[0]]
    for q in p[1:]:
        if abs(q[0] - out[-1][0]) > 1e-6 or abs(q[1] - out[-1][1]) > 1e-6: out.append(q)
    if abs(out[0][0] - out[-1][0]) < 1e-6 and abs(out[0][1] - out[-1][1]) < 1e-6: out.pop()
    return out
def signed_area(p): return sum(p[i][0] * p[(i + 1) % len(p)][1] - p[(i + 1) % len(p)][0] * p[i][1] for i in range(len(p))) / 2
OC = (48.6, 50.1)                       # centre of the stencil O in mark units
def squircle(p): return ((abs(p[0] - OC[0]) / 48.6) ** 4 + (abs(p[1] - OC[1]) / 50.0) ** 4) ** .25
def split_runs(loop, top_to_bottom, thr=.80):
    """Splits one half of the stencil O into its outer arc (squircle norm above thr) and the inner run (counter edge and slit edges)."""
    n = len(loop)
    def runs(lp):
        fl = [squircle(p) >= thr for p in lp]; i0 = next(i for i in range(n) if not fl[i]); seq = [(i0 + j) % n for j in range(n)]
        cl = cs = bl = bs = 0
        for j, i in enumerate(seq):
            if fl[i]:
                if cl == 0: cs = j
                cl += 1
                if cl > bl: bl, bs = cl, cs
            else: cl = 0
        return [seq[(bs + j) % n] for j in range(bl)], [seq[(bs + bl + j) % n] for j in range(n - bl)]
    idx, rest = runs(loop)
    if (loop[idx[0]][1] < loop[idx[-1]][1]) != top_to_bottom:
        loop = loop[::-1]; idx, rest = runs(loop)
    return [loop[i] for i in idx], [loop[i] for i in rest]
halves = []
for d in (mk[2], mk[3]):
    pl = dedupe(sample_subpaths(d)[0]); halves.append(pl if signed_area(pl) > 0 else pl[::-1])
oL, iL = split_runs(halves[0], True); oR, iR = split_runs(halves[1], False)
SIL = oL + oR                           # outer silhouette of the O (the slit gaps closed by chords)
HOLE = oL[-8:] + iL + oL[:6] + oR[-7:] + iR + oR[:9]    # counter plus both slits (extended along the slit edges so the two clips overlap)
def spx(pts, fx, fy): return [mpx(OC[0] + (x - OC[0]) * fx, OC[1] + (y - OC[1]) * fy) for x, y in pts]
def poly(pts, evenodd=False): return "polygon(" + ("evenodd," if evenodd else "") + ",".join(f"{num(x)} {num(y)}" for x, y in pts) + ")"
RECT = [(-50, -50), (W + 50, -50), (W + 50, H + 50), (-50, H + 50)]
def frame_hole(pts): return poly(RECT + [RECT[0], pts[0]] + pts + [pts[0], RECT[0]], True)
AP_A0, AP_A1 = poly(spx(SIL, 4.4, 2.0)), poly(spx(SIL, 1, 1))              # clip A: the silhouette closes from wide to the O
AP_B0, AP_B1 = frame_hole(spx(HOLE, 0, 0)), frame_hole(spx(HOLE, 1, 1))    # clip B: a frame whose hole (counter and slits) opens

# ------------------------------------------------------------------ the diagonal band (the only diagonal wipe in the film)
LEAN = math.radians(55.7)                                   # the stencil slash leans about 55.7 degrees
SHIFT = (H + 100) / math.tan(LEAN)                          # horizontal run of the leaning edge over the frame height
XB0, XB1, BAND_W = -SHIFT - 420, W + 100, 170
def band(xb): return f"polygon(-400px -50px,{num(xb + SHIFT)} -50px,{num(xb)} {H + 50}px,-400px {H + 50}px)"
T_BAND, D_BAND = 12.0, 1.0
def t_edge_passes(x, y):                                    # time at which the navy edge reaches (x, y)
    xb = x - SHIFT * ((H + 50) - y) / (H + 100); p = (xb - XB0) / (XB1 - XB0)
    return T_BAND + D_BAND * solve_ease(min(1, max(0, p)))
def t_mid(x, y): return (t_edge_passes(x, y) + t_edge_passes(x - BAND_W, y)) / 2           # between the marigold lead and the navy edge
T_O, T_S, T_POS = t_mid(MX + 48.6 * K_, MCY) - .12, t_mid(MX + 140 * K_, MCY) - .12, t_edge_passes(810, 880) + .02

# ------------------------------------------------------------------ S1: seeded particles, three stacked clusters, the line
CLY = [290, 625, 960]; CLT = ["Experience", "Product decisions", "Evidence"]
parts = []
for i in range(96):
    c, k = i % 3, i // 3; r = 112 * math.sqrt((k + .5) / 32); a = k * 2.399963 + c * .7        # golden-angle disc: an organic cluster
    parts.append({"s": [round(rnd.uniform(90, 990)), round(rnd.uniform(160, 1140))], "c": [round(CX + r * math.cos(a)), round(CLY[c] + r * math.sin(a))],
                  "l": [CX, round(176 + 320 * c + 10 + k * (300 / 31))]})
# ------------------------------------------------------------------ S2/S3: three navy source cards (stacked)
SRC_X, SRC_W, SRC_H, SRC_TOP = 64, 952, 220, [280, 540, 800]
SRC_T = ["A product decision", "A customer question", "The proof behind it"]
def minwave(ph, amp, n=24, w=250, h=88):
    return path([(w * i / (n - 1), h / 2 + amp * math.sin(2 * math.pi * 2.5 * i / (n - 1) + ph) * math.sin(math.pi * i / (n - 1)) ** .8) for i in range(n)])
MINI = [[minwave(p0 + j * 1.7, a) for j, a in enumerate((26, 34, 20, 30))] for p0 in (0, 2.1, 4.2)]
# ------------------------------------------------------------------ S4: market strands, lens, questions
LENS = (CX, MCY, 220)
mkt_layers = []
for L, (col, op, n, sw, lam, amp) in enumerate([("#B9C7DA", .22, 5, 3, 380, 56), ("#B9C7DA", .36, 4, 4, 470, 64), ("#666F7F", .62, 3, 6, 560, 72)]):
    ps = []
    for j in range(n):
        x0 = 100 + (j + .5) * 880 / n + L * 18; pts = []
        for i in range(N):
            y = -100 + 3200 * i / (N - 1); pts.append((x0 + amp * math.sin(y / lam + j * 1.7 + L), y))
        ps.append(path(pts))
    mkt_layers.append((L, col, op, sw, ps))
TRY, TRX = [-300, -620, -980], [-14, 26, -44]
QS = ["Why does this matter now?", "What changes for my team?", "Why trust this founder?"]; QY = [826, 930, 1034]
# ------------------------------------------------------------------ S5: calendar 4 columns x 6 rows
CAL_X, CAL_Y, CAL_W, CAL_H, CAL_GX, CAL_GY = 64, 206, 226, 140, 16, 14
KINDS = ["Theme", "Proof", "Format", "Post", "Carousel", "Video"]
LIFT = [(1, 0, "Profile"), (2, 2, "Post"), (4, 1, "Carousel")]; EMPTY = {(1, 3), (3, 0), (5, 2)}
cells = []
for r in range(6):
    for c in range(4):
        t = KINDS[(r * 2 + c) % 6]
        for lr, lc, lt in LIFT:
            if (r, c) == (lr, lc): t = lt
        cells.append({"x": CAL_X + c * (CAL_W + CAL_GX), "y": CAL_Y + r * (CAL_H + CAL_GY), "w": CAL_W, "h": CAL_H, "t": t, "on": (r, c) not in EMPTY})
LIFTI = [r * 4 + c for r, c, _ in LIFT]
# ------------------------------------------------------------------ S6: the three pieces stacked, strand underneath
CARD_X, CARD_W, CARD_H, CARD_GAP, CARD_TOP = 64, 952, 280, 28, 190
CARDS = [{"x": CARD_X, "y": CARD_TOP + i * (CARD_H + CARD_GAP), "w": CARD_W, "h": CARD_H, "t": t} for i, t in enumerate(["Founder profile", "Post", "Carousel"])]
POST_C = (CARD_X + CARD_W / 2, CARD_TOP + CARD_H + CARD_GAP + CARD_H / 2)
# ------------------------------------------------------------------ S7: buyer nodes (upper), three stacked rings (lower)
NODES = []
for r in range(3):
    for c in range(4):
        NODES.append([round(150 + c * 256 + (64 if r % 2 else 0) + rnd.uniform(-26, 26)), round(250 + r * 132 + rnd.uniform(-18, 18))])
EDGES = []
for i, a in enumerate(NODES):
    near = sorted(((math.hypot(a[0] - b[0], a[1] - b[1]), j) for j, b in enumerate(NODES) if j != i))[:3]
    for d, j in near:
        if d < 320 and (j, i) not in EDGES and (i, j) not in EDGES: EDGES.append((i, j))
RING_X, RING_D = 960, 112; RINGS = [(RING_X, 800, "Engagement"), (RING_X, 940, "Qualified replies"), (RING_X, 1080, "Attributed leads")]
PIECE_NODES = [1, 6, 8]
# ------------------------------------------------------------------ S8: three package cards in one column
PK = PRICING["packages"][:3]; PK_X, PK_W, PK_H, PK_GAP, PK_TOP = 64, 952, 268, 28, 192
PKR = [{"x": PK_X, "y": PK_TOP + i * (PK_H + PK_GAP), "w": PK_W, "h": PK_H} for i in range(3)]
SH = {"line": vline(CX, 170, 1130), "w1": vwave(0, 150), "w2": vwave(1.9, 120), "w3": vwave(3.6, 165), "thread": vline(CX, 170, 1130),
      "slash": outline(SLASH), "lens": vline(CX, 150, 1140), "dot": path([(CX, MCY)] * N), "cal": hline(192, 64, 1016), "under": hcurve(64, 1016, 1130, 18), "net": hcurve(64, 1016, 604, -38)}
CFG = {"parts": parts, "sh": SH, "cells": cells, "lift": LIFTI, "cards": CARDS, "nodes": NODES, "edges": EDGES, "rings": [[x, y] for x, y, _ in RINGS], "pkr": PKR, "pieceNodes": PIECE_NODES,
       "apA0": AP_A0, "apA1": AP_A1, "apB0": AP_B0, "apB1": AP_B1, "band": [band(XB0), band(XB1), band(XB0 + BAND_W), band(XB1 + BAND_W)],
       "tO": round(T_O, 2), "tS": round(T_S, 2), "tPos": round(T_POS, 2), "tr": [TRY, TRX], "lens": LENS, "postC": POST_C, "mini": MINI}

# ------------------------------------------------------------------ styles
css = """
.g{position:absolute;inset:0}
#gN{background:radial-gradient(1000px 900px at 84% 6%,rgba(49,87,213,.24),transparent 62%),radial-gradient(900px 800px at 4% 98%,rgba(234,169,60,.09),transparent 60%),#0D1A3B}
.pearl{background:linear-gradient(170deg,#fff 6%,#F1F3F6 58%,#E6EBF1)}
.navy{background:radial-gradient(1000px 900px at 16% 8%,rgba(49,87,213,.22),transparent 60%),#0D1A3B}
#gA{clip-path:inset(0px 540px 0px 540px)}
#gBb{background:#EAA93C;clip-path:%B0M%}
#gB{clip-path:%B0%}
#gC{clip-path:inset(0% 0% 100% 0%)}
#gD{clip-path:circle(0px at %PCX%px %PCY%px)}
#sv{position:absolute;inset:0;overflow:visible}
#strand{fill:none;stroke:#EAA93C;stroke-width:7;stroke-linecap:round;stroke-linejoin:round}
#cam{position:absolute;inset:0;transform-origin:50% 50%}
.sc{position:absolute;inset:0;opacity:0}
#c1{opacity:1}
.mono{font-family:'Geist Mono',monospace;font-weight:500;letter-spacing:.08em;text-transform:uppercase}
.disp{font-family:'Fraunces',serif;font-weight:400;letter-spacing:-.02em;line-height:1.06}
.lt{color:#B9C7DA}.dk{color:#3A4A75}
#hud{position:absolute;inset:0;z-index:50;pointer-events:none}
.kick{position:absolute;left:66px;top:70px;font-size:30px;opacity:0}
#k1{opacity:1}
.pt{position:absolute;left:-7.5px;top:-7.5px;width:15px;height:15px;border-radius:50%;background:#F2F5FA;opacity:0}
.pt.m{background:#EAA93C}.pt.s{background:#B9C7DA}
.cl{position:absolute;left:50%;width:560px;margin-left:-280px;text-align:center;font-size:30px;color:#F2F5FA;opacity:0}
#stack,#stackin{position:absolute;inset:0}
.src{position:absolute;left:%SX%px;width:%SW%px;height:%SH%px;border-radius:28px;background:#162760;opacity:0;transform-origin:50% 50%}
.src .ed{position:absolute;inset:0;border-radius:28px;border:2px solid rgba(241,243,246,.20)}
.src b{position:absolute;left:42px;top:30px;opacity:0;font-family:'Geist Mono',monospace;font-weight:500;font-size:28px;color:#F6D591;letter-spacing:.06em}
.src p{position:absolute;left:42px;bottom:32px;opacity:0;font-family:'Fraunces',serif;font-size:52px;line-height:1.08;color:#F2F5FA}
.src svg{position:absolute;right:46px;top:50%;margin-top:-44px;width:250px;height:88px;overflow:visible;opacity:0}
.src svg path{fill:none;stroke:#EAA93C;stroke-width:5;stroke-linecap:round;stroke-linejoin:round}
#mkw{position:absolute;left:%MX%px;top:%MY%px;width:%MW%px;height:%MH%px;z-index:31}
#mk .ol,#mk .or,#mk .mg{opacity:0}
#mk .ms{opacity:1;clip-path:inset(0% 100% 0% 0%)}
#pos{position:absolute;left:0;right:0;top:812px;text-align:center;font-size:118px;color:#F2F5FA;opacity:0}
.mkt{position:absolute;left:0;top:0;width:1080px;height:3000px;opacity:0}
.mkt svg{position:absolute;left:0;top:0;overflow:visible}
.mkt path{fill:none;stroke-linecap:round}
#ring{position:absolute;left:%RL%px;top:%RT%px;width:440px;height:440px;border-radius:50%;border:7px solid #EAA93C;opacity:0;z-index:32;background:radial-gradient(circle at 50% 38%,rgba(242,245,250,.07),rgba(242,245,250,.01))}
.q{position:absolute;left:0;right:0;margin:0 auto;width:max-content;padding:18px 32px;border-radius:20px;background:#0D1A3B;border:2px solid rgba(185,199,218,.42);color:#F2F5FA;font-size:34px;line-height:1.3;white-space:nowrap;opacity:0}
#calw{position:absolute;inset:0;perspective:2200px;perspective-origin:50% 192px}
#cal{position:absolute;inset:0;transform-origin:50% 192px;transform-style:preserve-3d}
.cell{position:absolute;border-radius:16px;background:rgba(22,39,96,.05);border:2px solid #D9DEE7}
.cell i{position:absolute;inset:8px;border-radius:11px;opacity:0;display:flex;align-items:center;justify-content:center;font-style:normal;font-family:'Geist Mono',monospace;font-weight:500;font-size:30px;letter-spacing:.02em}
.k-Theme i{background:#162760;color:#F2F5FA}.k-Proof i{background:#FFF6E3;color:#162760;box-shadow:inset 0 0 0 3px #EAA93C}.k-Format i{background:#E6EBF1;color:#3A4A75}
.k-Post i{background:#162760;color:#F6D591}.k-Carousel i{background:#fff;color:#162760;box-shadow:inset 0 0 0 2px #B9C7DA}.k-Video i{background:#EAA93C;color:#0D1A3B}.k-Profile i{background:#F6D591;color:#0D1A3B}
.lift{position:absolute;border-radius:26px;transform-origin:0 0;background:#fff;border:2px solid #EAA93C;box-shadow:0 30px 60px -34px rgba(22,39,96,.6);opacity:0;overflow:hidden;clip-path:circle(620px at 476px 140px)}
.lift .tt{position:absolute;left:40px;bottom:30px;font-family:'Fraunces',serif;font-size:50px;color:#162760;opacity:0}
.lift .ln{position:absolute;height:18px;border-radius:9px;background:#E1E6EE;opacity:0}
.lift .av{position:absolute;left:40px;top:38px;width:116px;height:116px;border-radius:50%;background:#162760;opacity:0}
.lift .av::after{content:'';position:absolute;right:-6px;bottom:6px;width:32px;height:32px;border-radius:50%;background:#EAA93C}
.pg{position:absolute;left:372px;top:36px;width:170px;height:190px;border-radius:14px;opacity:0;transform-origin:0% 50%}
#nets{position:absolute;inset:0;opacity:0;overflow:visible}
#nets line{stroke:#B9C7DA;stroke-width:2.5;stroke-linecap:round}
.node{position:absolute;width:34px;height:34px;margin:-17px 0 0 -17px;border-radius:50%;border:4px solid #B9C7DA;background:#0D1A3B;opacity:0}
.sig{position:absolute;left:0;top:0;width:16px;height:16px;margin:-8px 0 0 -8px;border-radius:50%;background:#F6D591;opacity:0}
.rg{position:absolute;width:%RD%px;height:%RD%px;margin:-%RH%px 0 0 -%RH%px;border-radius:50%;border:6px solid #B9C7DA;background:rgba(242,245,250,0);opacity:0}
.rl{position:absolute;left:66px;font-size:36px;color:#F2F5FA;opacity:0;white-space:nowrap}
.rule{position:absolute;left:66px;width:948px;height:2px;background:rgba(185,199,218,.24);opacity:0}
#ins{position:absolute;left:66px;top:650px;font-size:28px;opacity:0;white-space:nowrap}
.pk{position:absolute;background:#F2F5FA;border:5px solid #F2F5FA;border-radius:28px;opacity:0;overflow:hidden;clip-path:circle(620px at 476px 134px)}
.pk .in{position:absolute;inset:0;padding:34px 40px;opacity:0}
.pk h3{font-family:'Fraunces',serif;font-weight:400;font-size:56px;line-height:1.05;color:#162760}
.pk .pr{position:absolute;right:40px;top:30px;text-align:right;font-family:'Geist Mono',monospace;font-weight:500;font-size:56px;color:#162760;letter-spacing:-.02em;line-height:1.05}
.pk .pe{display:block;margin-top:8px;font-size:28px;color:#666F7F;letter-spacing:.06em;text-transform:uppercase;font-weight:500}
.pk .ds{margin-top:16px;width:560px;font-size:32px;line-height:1.3;color:#3A4A75}
.pk .ac{position:absolute;left:40px;right:40px;bottom:30px;height:8px;border-radius:4px;background:#EAA93C;transform:scaleX(0);transform-origin:0 50%}
#pkl{position:absolute;left:66px;top:74px;width:920px;font-size:30px;line-height:1.4;opacity:0;text-wrap:balance}
#lock{position:absolute;left:50%;top:196px;width:580px;margin-left:-290px;opacity:0;clip-path:inset(0% 50% 0% 50%)}
#hero{position:absolute;left:66px;width:948px;top:622px;text-align:center;font-size:88px;color:#F2F5FA;opacity:0;text-wrap:balance}
#cta{position:absolute;left:0;right:0;top:986px;margin:0 auto;width:max-content;height:112px;padding:0 64px;border-radius:999px;background:#EAA93C;color:#0D1A3B;font-size:44px;font-weight:600;display:flex;align-items:center;white-space:nowrap;opacity:0}
#cap{position:absolute;left:0;right:0;bottom:64px;display:flex;justify-content:center;z-index:60}
#cap span{max-width:900px;padding:14px 30px;border-radius:18px;background:rgba(13,26,59,.82);color:#F1F3F6;font-size:34px;line-height:1.3;text-align:center;text-wrap:balance;opacity:0}
"""
for k_, v_ in {"%B0M%": band(XB0 + BAND_W), "%B0%": band(XB0), "%PCX%": f"{POST_C[0]:.0f}", "%PCY%": f"{POST_C[1]:.0f}", "%SX%": SRC_X, "%SW%": SRC_W, "%SH%": SRC_H,
               "%MX%": f"{MX:.1f}", "%MY%": f"{MY:.1f}", "%MW%": MW, "%MH%": f"{MH:.1f}", "%RL%": f"{LENS[0] - LENS[2]:.0f}", "%RT%": f"{LENS[1] - LENS[2]:.0f}",
               "%RD%": RING_D, "%RH%": RING_D // 2}.items(): css = css.replace(k_, str(v_))

# ------------------------------------------------------------------ markup
def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;")
def rect(d): return f'left:{d["x"]}px;top:{d["y"]}px;width:{d["w"]}px;height:{d["h"]}px'
mkt_html = "".join(
    f'<div class="mkt" id="mk{L}"><svg viewBox="0 0 1080 3000" width="1080" height="3000">' + "".join(f'<path d="{p}" stroke="{col}" stroke-width="{sw}" opacity="{op}"/>' for p in ps)
    + f'</svg><svg class="hl" viewBox="0 0 1080 3000" width="1080" height="3000" style="clip-path:circle({LENS[2] - 4}px at {LENS[0]}px {LENS[1]}px)">'
    + "".join(f'<path d="{p}" stroke="#EAA93C" stroke-width="{sw + 1}" opacity=".95"/>' for p in ps) + '</svg></div>' for L, col, op, sw, ps in mkt_layers)
src_html = "".join(
    f'<div class="src" id="sc{i}" data-layout-allow-overlap style="top:{SRC_TOP[i]}px"><div class="ed"></div><b>0{i + 1}</b><p>{SRC_T[i]}</p>'
    f'<svg viewBox="0 0 250 88"><path d="{MINI[i][0]}"/></svg></div>' for i in range(3))
cell_html = "".join(f'<div class="cell k-{c["t"]}" id="ce{i}" style="{rect(c)}"><i>{c["t"] if c["on"] else ""}</i></div>' for i, c in enumerate(cells))
pk_html = "".join(
    f'<div class="pk" id="pk{i}" style="{rect(PKR[i])}"><div class="in"><h3>{esc(p["name"])}</h3><div class="ds">{esc(p["descriptor"])}</div>'
    f'<div class="pr">{esc(p["display_price"].split(" /")[0])}<span class="pe">{"one-off" if p["period"] == "one-off" else "per month"}</span></div></div><div class="ac"></div></div>'
    for i, p in enumerate(PK))
lines_y = [(176, 300), (214, 240), (248, 270)]
body = f"""
      <div class="g" id="gN"></div><div class="g pearl" id="gA"></div><div class="g" id="gBb"></div><div class="g navy" id="gB"></div><div class="g pearl" id="gC"></div><div class="g navy" id="gD"></div>
      <svg id="sv" viewBox="0 0 {W} {H}" width="{W}" height="{H}"><path id="strand" d="{SH['line']}" opacity="0"/></svg>
      <div id="cam">
        <div class="sc" id="c1">
          {''.join(f'<div class="pt{" m" if i % 7 == 0 else (" s" if i % 3 == 1 else "")}" id="p{i}"></div>' for i in range(len(parts)))}
          {''.join(f'<div class="cl mono" id="cl{i}" style="top:{CLY[i] + 134}px">{t}</div>' for i, t in enumerate(CLT))}
        </div>
        <div class="sc" id="c2"><div id="stack"><div id="stackin">{src_html}</div></div></div>
        <div class="sc" id="c3"><div class="disp" id="pos">Position</div></div>
        <div id="ring"></div>
        <div class="sc" id="c4">
          {mkt_html}
          {''.join(f'<div class="q" id="q{i}" style="top:{QY[i]}px">{esc(t)}</div>' for i, t in enumerate(QS))}
        </div>
        <div class="sc" id="c5"><div id="calw"><div id="cal">{cell_html}</div></div></div>
        <div class="sc" id="c6">
          <div class="lift" id="lf0" style="{rect(CARDS[0])}"><div class="av"></div><div class="ln" style="left:184px;top:44px;width:380px;background:#162760"></div><div class="ln" style="left:184px;top:84px;width:320px"></div><div class="ln" style="left:184px;top:122px;width:420px"></div><div class="tt">{CARDS[0]["t"]}</div></div>
          <div class="lift" id="lf1" style="{rect(CARDS[1])}"><div class="ln" style="left:40px;top:40px;width:560px;background:#162760"></div><div class="ln" style="left:40px;top:80px;width:840px"></div><div class="ln" style="left:40px;top:118px;width:780px"></div><div class="ln" style="left:40px;top:156px;width:640px"></div><div class="tt">{CARDS[1]["t"]}</div></div>
          <div class="lift" id="lf2" style="{rect(CARDS[2])}"><div class="pg" style="background:#162760"></div><div class="pg" style="background:#F6D591"></div><div class="pg" style="background:#E6EBF1"></div><div class="tt">{CARDS[2]["t"]}</div></div>
        </div>
        <div class="sc" id="c7">
          <svg id="nets" viewBox="0 0 {W} {H}" width="{W}" height="{H}">{''.join(f'<line x1="{NODES[a][0]}" y1="{NODES[a][1]}" x2="{NODES[b][0]}" y2="{NODES[b][1]}"/>' for a, b in EDGES)}</svg>
          {''.join(f'<div class="node" id="nd{i}" style="left:{x}px;top:{y}px"></div>' for i, (x, y) in enumerate(NODES))}
          {''.join(f'<div class="sig" id="sg{i}"></div>' for i in range(9))}
          <div class="mono lt" id="ins">Each measure reviewed on its own</div>
          {''.join(f'<div class="rule" id="ru{i}" style="top:{y - 70}px"></div><div class="rg" id="rg{i}" style="left:{x}px;top:{y}px"></div><div class="rl" id="rl{i}" style="top:{y - 24}px">{t}</div>' for i, (x, y, t) in enumerate(RINGS))}
        </div>
        <div class="sc" id="c8">
          <div class="mono lt" id="pkl">{esc(PRICING["public_label"])}</div>
          {pk_html}
          <img id="lock" src="assets/brand/lockup-os-stacked-inverse.svg" alt="">
          <div class="disp" id="hero">{esc(PROT["hero"])}</div>
          <div id="cta">{esc(PROT["cta"])}</div>
        </div>
      </div>
      <div id="mkw">{K.mark_svg(mk, "mk", width=MW)}</div>
      <div id="hud"><div class="kick mono lt" id="k1">Your thinking</div><div class="kick mono dk" id="k2">Interview</div><div class="kick mono lt" id="k4">Market</div><div class="kick mono dk" id="k5">Plan</div><div class="kick mono dk" id="k6">Create</div><div class="kick mono lt" id="k7">Conversations</div></div>
      <div id="cap"><span id="capt"></span></div>
"""
# ------------------------------------------------------------------ timeline
js = "const CFG = " + json.dumps(CFG) + ";\nconst LINES = " + json.dumps(LINES) + ";\n" + r"""
        const q = s => document.querySelector(s), qa = s => [...document.querySelectorAll(s)];
        const SM = 'power3.inOut', SO = 'power3.out';
        const show = (id, t) => tl.set(id, {opacity: 1}, t), hide = (id, t) => tl.set(id, {opacity: 0}, t);
        // ---- S1 0-5 Your thinking: particles drift down into the frame, gather in three stacked clusters, then line up as the strand
        tl.fromTo('#cam', {y: 20}, {y: -20, duration: 5.0, ease: 'sine.inOut'}, 0);
        tl.to('#k1', {opacity: 0, duration: .3}, 4.0);
        CFG.parts.forEach((p, i) => {
          const el = '#p' + i;
          tl.fromTo(el, {x: p.s[0], y: p.s[1] - 140, opacity: i % 2 === 0 ? .75 : 0, scale: i % 2 === 0 ? .8 : .4}, {y: p.s[1], opacity: .9, scale: 1, duration: .8, ease: SO}, (i % 24) * .025);
          tl.to(el, {x: p.c[0], y: p.c[1], duration: 1.5, ease: SM}, 1.45 + (i % 12) * .03);
          tl.to(el, {x: p.l[0], y: p.l[1], duration: .95, ease: 'power2.in'}, 3.85 + (i % 16) * .01);
          tl.to(el, {opacity: 0, duration: .25}, 4.95);
        });
        qa('.cl').forEach((c, i) => { tl.fromTo(c, {opacity: 0, y: 14}, {opacity: 1, y: 0, duration: .5, ease: SO}, 2.3 + i * .12); tl.to(c, {opacity: 0, duration: .3}, 4.0); });
        // seam 1: the pearl ground opens out of the strand as a vertical slit; the strand draws top to bottom over the lined-up particles
        tl.fromTo('#gA', {clipPath: 'inset(0px 540px 0px 540px)'}, {clipPath: 'inset(0px 0px 0px 0px)', duration: 1.15, ease: SM}, 4.3);
        tl.fromTo('#strand', {opacity: 0, strokeDasharray: '1300 1300', strokeDashoffset: 1300}, {opacity: 1, strokeDashoffset: 0, duration: .7, ease: SO}, 4.25);
        tl.set('#strand', {strokeDasharray: 'none'}, 5.0);
        tl.to('#cam', {y: 0, duration: .4, ease: SO}, 5.0);
        hide('#c1', 5.4); show('#c2', 5.0);
        // ---- S2 5-10 Interview: the strand speaks as a vertical waveform, then unfolds sideways into three stacked source cards
        tl.fromTo('#k2', {opacity: 0}, {opacity: 1, duration: .4}, 5.4);
        tl.to('#strand', {attr: {d: CFG.sh.w1}, duration: .8, ease: SM}, 5.1);
        tl.to('#strand', {attr: {d: CFG.sh.w2}, duration: .55, ease: 'sine.inOut'}, 5.9);
        tl.to('#strand', {attr: {d: CFG.sh.w3}, duration: .55, ease: 'sine.inOut'}, 6.45);
        tl.to('#strand', {attr: {d: CFG.sh.w1}, duration: .55, ease: 'sine.inOut'}, 7.0);
        tl.to('#strand', {attr: {d: CFG.sh.thread}, duration: .5, ease: SM}, 7.55);
        tl.to('#cam', {y: -26, duration: 4.4, ease: 'sine.inOut'}, 5.4);
        [0, 1, 2].forEach(i => {
          tl.fromTo('#sc' + i, {opacity: 0, scaleX: .02}, {opacity: 1, scaleX: 1, duration: .6, ease: 'back.out(1.4)'}, 7.7 + i * .25);
          tl.to(['#sc' + i + ' b', '#sc' + i + ' p', '#sc' + i + ' svg'], {opacity: 1, duration: .35}, 8.3 + i * .25);
          [1, 2, 3].forEach(j => tl.to('#sc' + i + ' svg path', {attr: {d: CFG.mini[i][j]}, duration: .5, ease: 'sine.inOut'}, 8.4 + (j - 1) * .5 + i * .06));
        });
        // ---- S3 10-14 Position: the cards slide together, the OS stencil cuts the surplus and leaves the O; the strand wraps into the slash; the S is revealed
        tl.to('#k2', {opacity: 0, duration: .3}, 9.8);
        tl.to('#cam', {y: 0, duration: .5, ease: SO}, 9.8);
        tl.to('#sc0', {y: -30, rotation: -3, duration: .65, ease: SM}, 10.0);
        tl.to('#sc1', {y: -130, duration: .65, ease: SM}, 10.0);
        tl.to('#sc2', {y: -230, rotation: 3, duration: .65, ease: SM}, 10.0);
        tl.to(['#sc0 b', '#sc0 p', '#sc0 svg', '#sc1 b', '#sc1 p', '#sc1 svg', '#sc2 b', '#sc2 p', '#sc2 svg'], {opacity: 0, duration: .25}, 10.1);
        tl.to(['#sc0 .ed', '#sc1 .ed', '#sc2 .ed'], {opacity: 0, duration: .35}, 10.85);
        tl.fromTo('#stack', {clipPath: CFG.apA0}, {clipPath: CFG.apA1, duration: .9, ease: 'power2.inOut', immediateRender: false}, 10.45);
        tl.fromTo('#stackin', {clipPath: CFG.apB0}, {clipPath: CFG.apB1, duration: .9, ease: 'power2.inOut', immediateRender: false}, 10.45);
        show('#c3', 10.0);
        tl.set('#stack', {opacity: 0}, 11.36); tl.set('#mk .ol, #mk .or', {opacity: 1}, 11.36); hide('#c2', 11.4);
        tl.to('#strand', {attr: {d: CFG.sh.slash}, duration: 1.0, ease: SM}, 10.4);
        tl.fromTo('#mk .ms', {clipPath: 'inset(0% 100% 0% 0%)'}, {clipPath: 'inset(0% 0% 0% 0%)', duration: .7, ease: SO, immediateRender: false}, 11.25);
        tl.fromTo('#mk .mg', {opacity: 0, scale: .55, transformOrigin: '50% 50%'}, {opacity: 1, scale: 1, duration: .5, ease: 'back.out(1.6)'}, 11.4);
        // seam 2: a marigold band leads the navy field along the slash diagonal; the mark recolours to its inverse as the navy edge passes it
        tl.fromTo('#gBb', {clipPath: CFG.band[2]}, {clipPath: CFG.band[3], duration: %DB%, ease: SM}, %TB%);
        tl.fromTo('#gB', {clipPath: CFG.band[0]}, {clipPath: CFG.band[1], duration: %DB%, ease: SM}, %TB%);
        tl.to('#mk .ol, #mk .or', {fill: '#F2F5FA', duration: .3}, CFG.tO); tl.to('#mk .ms', {fill: '#B9C7DA', duration: .3}, CFG.tS);
        tl.fromTo('#pos', {opacity: 0, y: 22}, {opacity: 1, y: 0, duration: .5, ease: SO}, CFG.tPos);
        // ---- S4 14-19 Market: the mark shrinks into a lens; three layers of market strands travel top to bottom through it and turn marigold inside it
        tl.to('#pos', {opacity: 0, y: -18, duration: .35}, 13.9);
        tl.to('#mkw', {scale: .22, opacity: 0, duration: .6, ease: 'power2.in'}, 14.0);
        tl.fromTo('#ring', {opacity: 0, scale: .2}, {opacity: 1, scale: 1, duration: .7, ease: 'back.out(1.4)'}, 14.25);
        show('#c4', 14.0); hide('#c3', 14.6);
        tl.to('#strand', {attr: {d: CFG.sh.lens}, duration: .8, ease: SM}, 14.1);
        [0, 1, 2].forEach(L => {
          tl.fromTo('#mk' + L, {x: 0, y: 0, opacity: 0}, {opacity: 1, duration: .5}, 14.2 + L * .1);
          tl.to('#mk' + L, {x: CFG.tr[1][L], y: CFG.tr[0][L], duration: 4.2, ease: 'sine.inOut'}, 14.5);
          tl.fromTo('#mk' + L + ' .hl', {clipPath: 'circle(%LR%px at %LX%px %LY%px)'}, {clipPath: 'circle(%LR%px at ' + (CFG.lens[0] - CFG.tr[1][L]) + 'px ' + (CFG.lens[1] - CFG.tr[0][L]) + 'px)', duration: 4.2, ease: 'sine.inOut'}, 14.5);
        });
        tl.fromTo('#k4', {opacity: 0}, {opacity: 1, duration: .4}, 14.6);
        [0, 1, 2].forEach(i => tl.fromTo('#q' + i, {opacity: 0, y: 24}, {opacity: 1, y: 0, duration: .5, ease: SO}, 15.6 + i * .45));
        // seam 3: the lens flattens into the calendar's top edge and the strand follows; pearl folds down from the top
        tl.to(['#q0', '#q1', '#q2', '#k4'], {opacity: 0, duration: .3}, 18.1);
        tl.to('#ring', {scaleY: .02, scaleX: 2.2, y: 192 - CFG.lens[1], duration: .55, ease: SM}, 18.45);
        tl.to('#ring', {opacity: 0, duration: .2}, 19.0);
        tl.to('#strand', {attr: {d: CFG.sh.dot}, duration: .3, ease: 'power2.in'}, 18.2);
        tl.to('#strand', {attr: {d: CFG.sh.cal}, duration: .55, ease: SM}, 18.5);
        tl.fromTo('#gC', {clipPath: 'inset(0% 0% 100% 0%)'}, {clipPath: 'inset(0% 0% 0% 0%)', duration: .9, ease: SM}, 18.35);
        tl.fromTo('#c4', {clipPath: 'inset(0px 0px 0px 0px)'}, {clipPath: 'inset(1350px 0px 0px 0px)', duration: .9, ease: SM, immediateRender: false}, 18.35);
        show('#c5', 18.9); hide('#c4', 19.3);
        // ---- S5 19-24 Plan: a 3D fold opens the calendar (4 x 6); cells fill with themes, proof and formats; three cells are selected
        tl.fromTo('#cal', {rotationX: -88}, {rotationX: 0, duration: 1.0, ease: SO}, 18.95);
        tl.fromTo('#k5', {opacity: 0}, {opacity: 1, duration: .4}, 19.3);
        CFG.cells.forEach((c, i) => { if (c.on) tl.fromTo('#ce' + i + ' i', {opacity: 0, y: 14}, {opacity: 1, y: 0, duration: .32, ease: SO}, 20.0 + (i % 4) * .085 + Math.floor(i / 4) * .38); });
        CFG.lift.forEach((ci, j) => tl.to('#ce' + ci, {borderColor: '#EAA93C', duration: .3}, 23.5 + j * .15));
        // ---- S6 24-29 Create: the three selected cells lift out and become a founder profile, a post and a carousel; the calendar folds back; the strand drops underneath
        tl.to('#cam', {y: 0, duration: .5, ease: SO}, 24.0);
        tl.to('#k5', {opacity: 0, duration: .3}, 24.0);
        CFG.lift.forEach((ci, j) => {
          const c = CFG.cells[ci], d = CFG.cards[j], el = '#lf' + j;
          tl.fromTo(el, {x: c.x - d.x, y: c.y - d.y, scaleX: c.w / d.w, scaleY: c.h / d.h, opacity: 0}, {opacity: 1, duration: .25}, 24.3);
          tl.to(el, {borderColor: '#E1E6EE', duration: .6}, 24.9 + j * .12);
          tl.to(el, {x: 0, y: 0, scaleX: 1, scaleY: 1, duration: .9, ease: SM}, 24.35 + j * .12);
          tl.to(el + ' .tt, ' + el + ' .ln, ' + el + ' .av', {opacity: 1, duration: .4, stagger: .05}, 25.1 + j * .12);
        });
        CFG.cells.forEach((c, i) => tl.to('#ce' + i, {opacity: 0, y: 30, duration: .45, ease: 'power2.in'}, 24.3 + ((i * 7) % 24) * .015));
        tl.to('#cal', {rotationX: -88, duration: .8, ease: 'power2.in'}, 24.45);
        show('#c6', 24.3);
        tl.to('#strand', {attr: {d: CFG.sh.under}, duration: .9, ease: SM}, 24.4);
        tl.fromTo('#k6', {opacity: 0}, {opacity: 1, duration: .4}, 24.6);
        qa('#lf2 .pg').forEach((p, i) => { tl.fromTo(p, {opacity: 0, x: 0, rotationY: 0}, {opacity: 1, duration: .3}, 25.3); tl.to(p, {x: i * 150, rotationY: -i * 10, duration: .7, ease: SO}, 26.6 + i * .18); });
        tl.to('#cam', {y: -18, duration: 3.4, ease: 'sine.inOut'}, 24.8);
        hide('#c5', 25.3);
        // seam 4: navy grows out of the post card as a circle
        tl.to('#k6', {opacity: 0, duration: .3}, 27.9);
        tl.fromTo('#gD', {clipPath: 'circle(0px at %PCX%px %PCY%px)'}, {clipPath: 'circle(1300px at %PCX%px %PCY%px)', duration: 1.1, ease: SM}, 28.2);
        // ---- S7 29-34 Conversations: the pieces travel up to buyer nodes; replies fall back to three separate, unquantified rings
        show('#c7', 28.9);
        tl.to('#cam', {y: 0, duration: .6, ease: SO}, 28.6);
        [0, 1, 2].forEach(j => { const n = CFG.nodes[CFG.pieceNodes[j]], d = CFG.cards[j];
          tl.to('#lf' + j + ' > *', {opacity: 0, duration: .25}, 29.0);
          tl.to('#lf' + j, {clipPath: 'circle(17px at 476px 140px)', backgroundColor: '#EAA93C', borderColor: '#EAA93C', duration: .55, ease: SM}, 29.0 + j * .1);
          tl.to('#lf' + j, {x: n[0] - (d.x + d.w / 2), y: n[1] - (d.y + d.h / 2), duration: .75, ease: SM}, 29.5 + j * .1);
          tl.to('#lf' + j, {opacity: 0, duration: .25}, 30.25 + j * .1); });
        hide('#c6', 30.7);
        tl.to('#strand', {attr: {d: CFG.sh.net}, duration: 1.0, ease: SM}, 29.0);
        tl.to('#strand', {opacity: .35, duration: .6}, 30.0);
        tl.fromTo('#k7', {opacity: 0}, {opacity: 1, duration: .4}, 29.3);
        tl.fromTo('#nets', {opacity: 0}, {opacity: .3, duration: .6}, 29.8);
        CFG.nodes.forEach((n, i) => { tl.fromTo('#nd' + i, {opacity: 0, scale: .3}, {opacity: 1, scale: 1, duration: .35, ease: 'back.out(2)'}, 29.4 + i * .05);
          tl.to('#nd' + i, {backgroundColor: '#EAA93C', borderColor: '#EAA93C', duration: .2}, 30.4 + i * .1); });
        CFG.rings.forEach((r, i) => { tl.fromTo('#rg' + i, {opacity: 0, scale: .5}, {opacity: 1, scale: 1, duration: .45, ease: SO}, 30.6 + i * .15);
          tl.fromTo('#ru' + i, {opacity: 0}, {opacity: 1, duration: .45}, 30.6 + i * .15);
          tl.fromTo('#rl' + i, {opacity: 0, x: 16}, {opacity: 1, x: 0, duration: .45, ease: SO}, 30.75 + i * .15); });
        for (let i = 0; i < 9; i++) { const n = CFG.nodes[(i * 5) % 12], r = CFG.rings[i % 3], t0 = 31.5 + i * .12;
          tl.fromTo('#sg' + i, {x: n[0], y: n[1], opacity: 0}, {opacity: 1, duration: .1}, t0);
          tl.to('#sg' + i, {x: r[0], y: r[1], duration: .75, ease: 'power2.inOut'}, t0);
          tl.to('#sg' + i, {opacity: 0, duration: .12}, t0 + .75);
          tl.fromTo('#rg' + (i % 3), {borderColor: '#B9C7DA', scale: 1}, {borderColor: '#EAA93C', scale: 1.08, duration: .15, yoyo: true, repeat: 1, immediateRender: false}, t0 + .72); }
        tl.fromTo('#ins', {opacity: 0}, {opacity: 1, duration: .5}, 31.3);
        tl.to('#cam', {y: -14, duration: 2.6, ease: 'sine.inOut'}, 30.6);
        // ---- S8 34-42 Packages: the three rings fold into package cards; then the stacked lockup, the hero line and the call to action
        tl.to('#cam', {y: 0, duration: .6, ease: SO}, 33.8);
        tl.to(['#k7', '#ins', '.rl', '.rule', '.node', '#nets', '#strand'], {opacity: 0, duration: .35}, 33.8);
        show('#c8', 33.9);
        CFG.rings.forEach((r, i) => { const d = CFG.pkr[i];
          tl.to('#rg' + i, {backgroundColor: 'rgba(242,245,250,1)', borderColor: '#F2F5FA', duration: .25}, 33.85);
          tl.fromTo('#pk' + i, {x: r[0] - (d.x + d.w / 2), y: r[1] - (d.y + d.h / 2), clipPath: 'circle(56px at 476px 134px)', opacity: 0}, {opacity: 1, duration: .2}, 33.95);
          tl.to('#pk' + i, {x: 0, y: 0, clipPath: 'circle(620px at 476px 134px)', duration: .9, ease: SM}, 34.1 + i * .14);
          tl.to('#pk' + i + ' .in', {opacity: 1, duration: .45}, 34.95 + i * .35);
          tl.to('#pk' + i + ' .ac', {scaleX: 1, duration: .5, ease: SO}, 36.6 + i * .15); });
        tl.to('.rg', {opacity: 0, duration: .15}, 34.15); hide('#c7', 34.4);
        tl.fromTo('#pkl', {opacity: 0, y: 12}, {opacity: 1, y: 0, duration: .5, ease: SO}, 34.7);
        tl.to(['#pk0', '#pk1', '#pk2'], {y: 70, opacity: 0, duration: .55, ease: 'power2.in', stagger: .06}, 37.8);
        tl.to('#pkl', {opacity: 0, duration: .3}, 37.8);
        tl.fromTo('#lock', {opacity: 0, y: 24, clipPath: 'inset(0% 50% 0% 50%)'}, {opacity: 1, y: 0, clipPath: 'inset(0% 0% 0% 0%)', duration: .8, ease: SO}, 38.4);
        tl.fromTo('#hero', {opacity: 0, y: 24}, {opacity: 1, y: 0, duration: .8, ease: SO}, 38.7);
        tl.fromTo('#cta', {opacity: 0, y: 26}, {opacity: 1, y: 0, duration: .6, ease: 'back.out(1.6)'}, 39.1);
        // captions are native lower-third type that follows the narration windows
        LINES.forEach(([a, b, t]) => {
          tl.set('#capt', {textContent: t}, a);
          tl.fromTo('#capt', {opacity: 0, y: 12}, {opacity: 1, y: 0, duration: .25, ease: SO, immediateRender: false}, a);
          tl.to('#capt', {opacity: 0, duration: .2}, b);
        });
        tl.to({}, {duration: .01}, %DUR% - .01);
""".replace("%DUR%", str(DUR)).replace("%TB%", str(T_BAND)).replace("%DB%", str(D_BAND)).replace("%LR%", str(LENS[2] - 4)).replace("%LX%", str(LENS[0])).replace("%LY%", str(LENS[1])) \
   .replace("%PCX%", f"{POST_C[0]:.0f}").replace("%PCY%", f"{POST_C[1]:.0f}")
# the stacked lockup is not among the files filmkit.sync_assets copies, so this script copies it from the repository's identity folder
(PROJ / "assets" / "brand").mkdir(parents=True, exist_ok=True)
shutil.copy(IDENT / "lockup-os-stacked-inverse.svg", PROJ / "assets" / "brand" / "lockup-os-stacked-inverse.svg")
PROJ.mkdir(parents=True, exist_ok=True)
(PROJ / "index.html").write_text(K.root_html(W, H, DUR, css, body, js, "assets/audio/" + ("mix-with-guide.wav" if GUIDE else "mix-voice-ready.wav")), encoding="utf-8")
(PROJ / "hyperframes.json").write_text(json.dumps({"$schema": "https://hyperframes.heygen.com/schema/hyperframes.json", "paths": {"blocks": "compositions", "assets": "assets"}}, indent=2))
(PROJ / "meta.json").write_text(json.dumps({"id": "outspoken-launch-r15-4x5", "name": "outspoken-launch-r15-4x5"}, indent=2))
if "--audio" in sys.argv:
    print(K.make_audio(PROJ / "assets" / "audio", DUR, CUTS, LINES, chords=[50, 45, 47, 43], bpm=100, seed=4515, events=EVENTS))
K.write_vo(HERE / "4x5", "Outspoken launch film R15, 4:5", DUR, LINES, SCENES,
           "Narration for a human voice (wording proposed by Codex, R15). The windows are identical to the 16:9 launch film, so one recording fits both frames; the master carries music and effects only.")
print("built", PROJ / "index.html")
