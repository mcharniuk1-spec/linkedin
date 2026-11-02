#!/usr/bin/env python3
"""Renders the Outspoken LinkedIn publication drafts (carousels and single images, 1080x1350) from HTML with the design-system fonts and assets,
using headless Chrome, and assembles each carousel into a PDF (LinkedIn document format).
Usage (repository root): python3 "design and website/scripts/make_publications.py" [--chrome "/path/to/chrome"] [--out <dir>]
Numbers on the chart slides come from reports/20261031/data.json (descriptive medians, not causal)."""
import json, os, subprocess, sys, tempfile, pathlib, html
from PIL import Image
Image.init()

ROOT = pathlib.Path(__file__).resolve().parents[2]          # repository root
DW = ROOT / "design and website"
ID = DW / "assets/public/assets/identity"
OUT = pathlib.Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else DW / "assets/public/assets/publications-r12"
CHROME = sys.argv[sys.argv.index("--chrome") + 1] if "--chrome" in sys.argv else "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
data = json.loads((ROOT / "reports/20261031/data.json").read_text())["queries"]
fm = {r["label"]: r for r in data["formats"]["rows"]}; tp = {r["label"]: r for r in data["topics"]["rows"]}; jb = {r["label"]: r for r in data["jobs"]["rows"]}

CSS = f"""
@font-face{{font-family:Fraunces;src:url('file://{ID}/font-source/fraunces/fraunces-latin-full-normal.woff2');font-weight:100 900}}
@font-face{{font-family:'Mona Sans';src:url('file://{ID}/font-source/mona-sans/mona-sans-latin-wght-normal.woff2');font-weight:200 900}}
@font-face{{font-family:'Geist Mono';src:url('file://{ID}/font-source/geist-mono/geist-mono-latin-wght-normal.woff2');font-weight:100 900}}
*{{margin:0;box-sizing:border-box}}html,body{{width:1080px;height:1350px;overflow:hidden}}
body{{position:relative;font-family:'Mona Sans',sans-serif;color:#162760;background:linear-gradient(160deg,#fff 6%,#F1F3F6 58%,#E4EAF0)}}
body.dark{{color:#F1F3F6;background:radial-gradient(800px 800px at 82% 8%,rgba(49,87,213,.30),transparent 62%),radial-gradient(640px 640px at 6% 96%,rgba(234,169,60,.14),transparent 60%),#0D1A3B}}
.dots{{position:absolute;inset:0;background:radial-gradient(rgba(22,39,96,.14) 2.5px,transparent 3.5px) 0 0/48px 48px}}body.dark .dots{{background:radial-gradient(rgba(241,243,246,.12) 2.5px,transparent 3.5px) 0 0/48px 48px}}
.top{{position:absolute;left:72px;right:72px;top:64px;display:flex;justify-content:space-between;align-items:center}}
.top img{{height:46px}}.cnt{{font:500 26px 'Geist Mono';letter-spacing:.09em;padding:10px 22px;border:2px solid #D9DEE7;border-radius:999px;background:rgba(255,255,255,.9);color:#475477}}
body.dark .cnt{{background:rgba(241,243,246,.1);border-color:rgba(241,243,246,.3);color:#F1F3F6}}
.kick{{position:absolute;left:72px;font:500 28px 'Geist Mono';letter-spacing:.09em;text-transform:uppercase;color:#824F19}}body.dark .kick{{color:#F3C15D}}
.h{{position:absolute;left:72px;right:72px;font-family:Fraunces;font-weight:400;letter-spacing:-.02em;line-height:1.04}}
.p{{position:absolute;left:72px;right:90px;font-size:42px;line-height:1.42;color:#1F2D55}}body.dark .p{{color:#D0D9E5}}
.sel{{display:inline-block;padding:0 .12em;border-radius:12px;background:#F6D591;color:#162760;outline:3px dashed rgba(22,39,96,.6);outline-offset:10px}}
.num{{position:absolute;left:60px;font:400 380px/1 Fraunces;color:rgba(22,39,96,.07);letter-spacing:-.04em}}
.note{{position:absolute;left:72px;right:72px;bottom:64px;font-size:27px;line-height:1.45;color:#475477}}body.dark .note{{color:#A9AFBA}}
.btn{{position:absolute;left:72px;display:inline-flex;gap:18px;align-items:center;padding:30px 52px;border-radius:999px;background:#F1F3F6;color:#162760;font:600 42px 'Mona Sans'}}
.bar{{position:absolute;left:72px;height:62px;border-radius:14px;background:#C8D0DD}}.bar.hi{{background:#EAA93C}}.bl{{position:absolute;left:72px;font-size:34px;font-weight:600}}.bv{{position:absolute;font:500 34px 'Geist Mono'}}
"""
LOCK = f"file://{ID}/v13/lockup-os.svg"; LOCKI = f"file://{ID}/v13/lockup-os-inverse.svg"

def page(body_cls, inner, idx, total):
    lock = LOCKI if body_cls == "dark" else LOCK
    cnt = f'<div class="cnt">{idx:02d} / {total:02d}</div>' if total > 1 else ""
    return f'<!doctype html><meta charset="utf-8"><style>{CSS}</style><body class="{body_cls}"><div class="dots"></div><div class="top"><img src="{lock}">{cnt}</div>{inner}</body>'

def sel(t): return f'<span class="sel">{t}</span>'

def chart(rows, top, hi_first=True, maxv=None, unit=""):
    maxv = maxv or max(v for _, v, _ in rows); out = ""
    for i, (lab, v, n) in enumerate(rows):
        y = top + i * 128; w = max(40, int(780 * v / maxv))
        out += f'<div class="bl" style="top:{y}px">{html.escape(lab)} <span style="font:500 26px \'Geist Mono\';color:#475477">n={n}</span></div><div class="bar{" hi" if i == 0 and hi_first else ""}" style="top:{y+50}px;width:{w}px"></div><div class="bv" style="top:{y+57}px;left:{72+w+20}px">{v:g}</div>'
    return out

DECKS = {}
# ---- P1 carousel: one product decision, one post buyers can use
P1 = [
 ("dark", f'<div class="kick" style="top:260px">A five-step method for founders</div><div class="h" style="top:330px;font-size:132px">One product decision. One post {sel("buyers")} can use.</div><div class="note">Swipe: the method, in five steps. OUTSPOKEN studies are illustrative.</div>'),
 ("", '<div class="num" style="top:150px">1</div><div class="kick" style="top:250px">Step 1</div><div class="h" style="top:320px;font-size:104px">Start with a decision, not a feature.</div><div class="p" style="top:760px">Pick one choice your team made and can defend: what you built, what you left out, and why.</div>'),
 ("", f'<div class="num" style="top:150px">2</div><div class="kick" style="top:250px">Step 2</div><div class="h" style="top:320px;font-size:104px">Name the {sel("buyer&rsquo;s")} question.</div><div class="p" style="top:760px">Write the question the buyer is already asking, in the buyer&rsquo;s words, before you write any answer.</div>'),
 ("", '<div class="num" style="top:150px">3</div><div class="kick" style="top:250px">Step 3</div><div class="h" style="top:320px;font-size:104px">Show the trade-off.</div><div class="p" style="top:700px">Say what you gave up. A founder who can name the cost is easier to trust than one who lists only benefits.</div>'),
 ("", '<div class="num" style="top:150px">4</div><div class="kick" style="top:250px">Step 4</div><div class="h" style="top:320px;font-size:104px">Add one piece of evidence.</div><div class="p" style="top:700px">A diagram, a screenshot, a number you can source, or a quote a customer approved. Nothing invented.</div>'),
 ("", f'<div class="num" style="top:150px">5</div><div class="kick" style="top:250px">Step 5</div><div class="h" style="top:320px;font-size:104px">End with a {sel("lesson")} to use.</div><div class="p" style="top:760px">One sentence a buyer can apply this week. Then stop.</div>'),
 ("dark", f'<div class="kick" style="top:250px">Why this order</div><div class="h" style="top:320px;font-size:96px">Personal-brand and positioning topics led our sample.</div><div class="p" style="top:760px;font-size:38px">In 279 reviewed posts, personal-brand topics had a median of {tp["Content personal brand"]["reaction_median"]:g} reactions and positioning topics {tp["Positioning messaging"]["reaction_median"]:g}. Descriptive only: author, age and topic differ.</div><div class="btn" style="top:1110px">Book an intro call</div>'),
]
P1_CAPTION = """Most founder posts explain a feature. Buyers are asking about a decision.

Here is the five-step method we use to turn one product decision into one post a buyer can use:
1. Start with a decision, not a feature.
2. Name the buyer's question.
3. Show the trade-off.
4. Add one piece of evidence.
5. End with a lesson to use.

Why this order: in a sample of 279 reviewed LinkedIn posts from 61 accounts, personal-brand topics had a median of 258 reactions and positioning topics 179 (descriptive; author, age and topic differ, and no reach data was available).

If you want this voice on your profile, book an intro call.
#founderledmarketing #B2BSaaS"""
DECKS["p1-method-carousel"] = (P1, P1_CAPTION)

# ---- P2 single image
P2 = [("", f'<div class="kick" style="top:250px">Belief to challenge</div><div class="h" style="top:320px;font-size:128px">Posting daily is not a strategy. A {sel("buyer")} question is.</div><div class="p" style="top:900px;font-size:36px">Founder-building posts had a median of {tp["Founder building"]["reaction_median"]:g} reactions in our sample; demand-generation posts {tp["Demand generation"]["reaction_median"]:g}. Descriptive only.</div><div class="note">OUTSPOKEN &middot; sample of 279 posts, 61 accounts, counters captured 20&ndash;22 October 2026</div>')]
P2_CAPTION = """Posting daily is not a strategy. A buyer question is.

A calendar fills slots. A strategy decides which buyer question each post answers, and which founder decision or piece of evidence answers it.

In the sample we reviewed (279 posts, 61 accounts), founder-building posts had a median of 203.5 reactions and demand-generation posts 26. These medians are descriptive: authors, post age and topics differ, and no impressions or conversions were observed. We use them to choose where to look first, not to promise a result.

What is the one buyer question your next post answers?
#linkedinstrategy #founderled"""
DECKS["p2-belief-image"] = (P2, P2_CAPTION)

# ---- P3 carousel: what 279 posts showed
frows = [("Image", fm["Image"]["reaction_median"], fm["Image"]["posts"]), ("Document", fm["Document"]["reaction_median"], fm["Document"]["posts"]), ("Text", fm["Text"]["reaction_median"], fm["Text"]["posts"]), ("Video", fm["Video"]["reaction_median"], fm["Video"]["posts"])]
trows = [(k, tp[k]["reaction_median"], tp[k]["posts"]) for k in ("Content personal brand", "Founder building", "Positioning messaging", "Buyer research", "Sales outbound")]
trows = [(a.replace("Content personal brand", "Personal brand").replace("Positioning messaging", "Positioning"), b, c) for a, b, c in trows]
jrows = [(k, jb[k]["reaction_median"], jb[k]["posts"]) for k in ("Tell story", "Challenge belief", "Show proof", "Teach method", "Announce offer")]
P3 = [
 ("dark", f'<div class="kick" style="top:260px">A LinkedIn sample, read honestly</div><div class="h" style="top:330px;font-size:124px">279 posts, 61 accounts. What to copy, and what we {sel("do not")} know.</div><div class="note">Counters captured 20&ndash;22 October 2026. Descriptive medians.</div>'),
 ("", f'<div class="kick" style="top:230px">Formats</div><div class="h" style="top:290px;font-size:84px">Images and documents led; video trailed.</div>{chart(frows, 560)}<div class="note">Median observed reactions. Author, age and topic differ; this is not a causal effect.</div>'),
 ("", f'<div class="kick" style="top:230px">Topics</div><div class="h" style="top:290px;font-size:84px">Personal brand and founder building led.</div>{chart(trows, 560)}<div class="note">Median observed reactions, topics with at least 20 posts, top 5 shown plus sales outbound.</div>'),
 ("", f'<div class="kick" style="top:230px">Jobs of a post</div><div class="h" style="top:290px;font-size:84px">Stories beat offers.</div>{chart(jrows, 560)}<div class="note">Median observed reactions by editorial purpose.</div>'),
 ("", f'<div class="kick" style="top:230px">What we do not know</div><div class="h" style="top:290px;font-size:92px">No reach, no clicks, no conversions.</div><div class="p" style="top:640px;font-size:40px">No impressions or video views were observed. Ten posts hold 33% of observed reactions. Author size matters. A strong post here is a strong reference, not a live trend winner.</div>'),
 ("dark", f'<div class="kick" style="top:250px">Our rule</div><div class="h" style="top:320px;font-size:96px">One buyer problem. One founder decision. One proof. One {sel("lesson")}.</div><div class="btn" style="top:1000px">Book an intro call</div>'),
]
P3_CAPTION = """We read 279 LinkedIn posts from 61 accounts so you do not have to guess.

What the medians show (descriptive, not causal):
- Formats: image 186.5 reactions, document 178, text 94, video 30.
- Topics: personal brand 258, founder building 203.5, positioning 179, sales outbound 48, demand generation 26.
- Jobs: telling a story 267, challenging a belief 108, showing proof 107, teaching a method 106, announcing an offer 67.

What we do not know: reach, clicks, video views and conversions were not observed, and ten posts hold 33% of all reactions.

Our rule for our own posts: one buyer problem, one founder decision, one proof, one lesson.
#linkedindata #B2BSaaS #founderled"""
DECKS["p3-sample-carousel"] = (P3, P3_CAPTION)

def shoot(html_path, png):
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files", "--virtual-time-budget=3000", "--window-size=1080,1350", f"--screenshot={png}", f"file://{html_path}"], check=True, capture_output=True)

OUT.mkdir(parents=True, exist_ok=True)
manifest = []
with tempfile.TemporaryDirectory() as tmp:
    for name, (slides, caption) in DECKS.items():
        pngs = []
        for i, (cls, inner) in enumerate(slides, 1):
            h = pathlib.Path(tmp) / f"{name}-{i}.html"; h.write_text(page(cls, inner, i, len(slides)))
            png = OUT / f"{name}-{i:02d}.png"; shoot(h, png); pngs.append(png)
            im = Image.open(png).convert("RGB"); im.save(png, optimize=True)
        if len(pngs) > 1:
            ims = [Image.open(p).convert("RGB") for p in pngs]; ims[0].save(OUT / f"{name}.pdf", save_all=True, append_images=ims[1:], resolution=96)
        (OUT / f"{name}-caption.txt").write_text(caption + "\n")
        manifest.append({"id": name, "slides": len(slides), "files": [p.name for p in pngs]})
(OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps(manifest))
