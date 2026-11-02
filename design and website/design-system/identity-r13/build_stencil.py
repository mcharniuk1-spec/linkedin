#!/usr/bin/env python3
"""Builds the OS stencil identity family (R13, proposed) from `os-stencil-paths.json`: the left OS mark of Codex concept LOGO-03, traced by `trace_stencil.py`.
Outputs SVG sources next to this file and served copies plus PNG/ICO exports in assets/public/assets/identity/v13/. The OUTSPOKEN wordmark paths are the unchanged V5 outlines.
Usage: python3 build_stencil.py [--variant smooth] [--chrome "/path/to/chrome"]    Needs Pillow and Google Chrome (PNG export only).
--variant smooth builds the alternate from `os-smooth-paths.json` (Codex concept LOGO-06 left, no stencil bridges) into identity/v13-smooth/ and ./smooth/ with the same file names."""
import json, pathlib, re, struct, subprocess, sys, tempfile
HERE = pathlib.Path(__file__).resolve().parent; DW = HERE.parent.parent
SMOOTH = "--variant" in sys.argv and sys.argv[sys.argv.index("--variant") + 1] == "smooth"
OUT = DW / ("assets/public/assets/identity/v13-smooth" if SMOOTH else "assets/public/assets/identity/v13"); OUT.mkdir(parents=True, exist_ok=True)
SRC = HERE / "smooth" if SMOOTH else HERE; SRC.mkdir(exist_ok=True)
CH = sys.argv[sys.argv.index("--chrome") + 1] if "--chrome" in sys.argv else "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
NAVY, DEEP, MARI, NICKEL, NICKEL600 = "#162760", "#0D1A3B", "#EAA93C", "#A9AFBA", "#666F7F"   # Nickel 600 (proposed): 4.56:1 on pearl, 5.07:1 on white
INV_O, INV_S = "#F2F5FA", "#B9C7DA"                                                          # canonical inverse pair from lockup-b01-inverse.svg
P = json.loads((HERE / ("os-smooth-paths.json" if SMOOTH else "os-stencil-paths.json")).read_text()); MW, MH = P["width"], P["height"]
WM = (DW / "assets/public/assets/revisions/v5/identity/wordmark-mono.svg").read_text()
wm_w, wm_h = [float(x) for x in re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', WM).groups()]
wm_tags = re.findall(r'<path data-letter="[^"]*"[^>]*/>', WM)
assert len(wm_tags) == 9 and all(t.count('fill="#162760"') == 1 and t.count('stroke="#162760"') == 1 and "transform=" in t for t in wm_tags)
def wm_group(c1, c2): return "".join(t.replace('fill="#162760"', f'fill="{c}"').replace('stroke="#162760"', f'stroke="{c}"') for t, c in zip(wm_tags, [c1] * 3 + [c2] * 6))
def svg(w, h, vb, body, title): return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="{vb}" role="img"><title>{title}</title>{body}</svg>\n'
def mark(o, s, g, solid=False, cls=False):
    c = (lambda k: f' class="{k}"') if cls else (lambda k: "")
    return f'<path{c("o")} fill="{o}" d="{P["navy_solid" if solid else "navy"]}"/><path{c("s")} fill="{s}" d="{P["silver"]}"/><path{c("g")} fill="{g}" d="{P["gold"]}"/>'
SETS = {"": (NAVY, NICKEL600, MARI), "-inverse": (INV_O, INV_S, MARI), "-mono": (NAVY, NAVY, NAVY), "-mono-inverse": (INV_O, INV_O, INV_O)}
T = "OUTSPOKEN OS " + ("smooth alternate" if SMOOTH else "stencil") + " mark (proposed)"
files = {}
for k, (o, s, g) in SETS.items():
    files[f"mark-os{k}.svg"] = svg(round(MW * 4), MH * 4, f"0 0 {MW} {MH}", mark(o, s, g), T + (", " + k.strip("-") if k else ""))
    files[f"mark-os-solid{k}.svg"] = svg(round(MW * 4), MH * 4, f"0 0 {MW} {MH}", mark(o, s, g, True), T + ", gap-closed small-size build")
def lockup(k, stacked=False, ground=False):  # ground=True adds the deep-navy rectangle for standalone use; the site files are transparent like the B01 inverse
    o, s, g = SETS[k]; c1, c2 = {"": (NAVY, NICKEL600), "-inverse": (INV_O, INV_S), "-mono": (NAVY, NAVY)}[k]
    bg = f'<rect width="{{W}}" height="{{H}}" fill="{DEEP}"/>' if ground else ""
    if not stacked:
        ms = 72 / MH; wms = 36 / wm_h; gap = 30; W = round(MW * ms + gap + wm_w * wms, 1); H = 72
        body = f'<g transform="scale({ms:.5f})">{mark(o, s, g)}</g><g transform="translate({MW*ms+gap:.2f} {(H-36)/2:.2f}) scale({wms:.5f})">{wm_group(c1, c2)}</g>'
    else:
        mw = 200; ms = mw / MW; wms = 280 / wm_w; W = 280; mh = MH * ms; H = round(mh + 22 + wm_h * wms, 1)
        body = f'<g transform="translate({(280-mw)/2:.2f} 0) scale({ms:.5f})">{mark(o, s, g)}</g><g transform="translate(0 {mh+22:.2f}) scale({wms:.5f})">{wm_group(c1, c2)}</g>'
    return svg(W, H, f"0 0 {W} {H}", bg.format(W=W, H=H) + body, "OUTSPOKEN lockup: OS stencil mark with the V5 outlined wordmark (proposed)")
for k in SETS:
    if k == "-mono-inverse": continue
    files[f"lockup-os{k}.svg"] = lockup(k); files[f"lockup-os-stacked{k}.svg"] = lockup(k, True)
    if k == "-inverse": files["lockup-os-inverse-ground.svg"] = lockup(k, False, True); files["lockup-os-stacked-inverse-ground.svg"] = lockup(k, True, True)
files["wordmark-nickel600.svg"] = f'<svg xmlns="http://www.w3.org/2000/svg" width="{wm_w}" height="{wm_h:.0f}" viewBox="0 0 {wm_w} {wm_h:.0f}" role="img"><title>OUTSPOKEN wordmark: V5 outlines, navy OUT, Nickel 600 SPOKEN for light grounds (proposed)</title>{wm_group(NAVY, NICKEL600)}</svg>\n'
def centred(wid, S, solid, rx=0, bg=NAVY):  # inverse mark centred in an S x S tile
    k = wid / MW; return svg(S, S, f"0 0 {S} {S}", f'<rect width="{S}" height="{S}" rx="{rx}" fill="{bg}"/><g transform="translate({(S-wid)/2:.2f} {(S-MH*k)/2:.2f}) scale({k:.5f})">{mark(INV_O, INV_S, MARI, solid)}</g>', "OUTSPOKEN OS stencil mark on navy (proposed)")
files["avatar-os.svg"] = centred(560, 800, False); files["avatar-os-24.svg"] = centred(600, 800, True)
files["favicon-os.svg"] = centred(57, 64, True, 12); files["favicon-os-16.svg"] = centred(15, 16, True, 3); files["apple-touch-os.svg"] = centred(130, 180, False)
css = ".o,.s{opacity:0;animation:in .7s cubic-bezier(.22,1,.36,1) forwards}.o{transform:translateX(-14px)}.s{transform:translateX(14px);animation-delay:.12s}.g{opacity:0;transform-box:fill-box;transform-origin:center;transform:scaleX(.2) skewX(-30deg);animation:slash .45s cubic-bezier(.34,1.56,.64,1) .55s forwards}@keyframes in{to{opacity:1;transform:none}}@keyframes slash{to{opacity:1;transform:none}}@media (prefers-reduced-motion:reduce){.o,.s,.g{animation:none;opacity:1;transform:none}}"
files["mark-os-animated.svg"] = svg(round(MW * 4), MH * 4, f"0 0 {MW} {MH}", f"<style>{css}</style>" + mark(NAVY, NICKEL600, MARI, cls=True), "OUTSPOKEN OS mark, animated entrance (respects reduced motion; proposed)")
for n, v in files.items(): (SRC / n).write_text(v); (OUT / n).write_text(v)
def png(name, w, h, dest, bg="transparent"):
    with tempfile.TemporaryDirectory() as t:
        html = pathlib.Path(t) / "p.html"; html.write_text(f'<!doctype html><body style="margin:0;background:{bg}"><img src="file://{SRC / name}" width="{w}" height="{h}" style="display:block">')
        subprocess.run([CH, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files", "--virtual-time-budget=2000", "--default-background-color=00000000", f"--window-size={w},{h}", f"--screenshot={OUT / dest}", f"file://{html}"], capture_output=True)
png("avatar-os.svg", 800, 800, "avatar-os-800.png"); png("avatar-os.svg", 400, 400, "avatar-os-400.png")
for s in (64, 48, 32): png("favicon-os.svg", s, s, f"favicon-os-{s}.png")
png("favicon-os-16.svg", 16, 16, "favicon-os-16.png"); png("favicon-os-16.svg", 32, 32, "favicon-os-16-2x.png"); png("apple-touch-os.svg", 180, 180, "apple-touch-os-180.png")
lw = float(re.search(r'width="([\d.]+)"', files["lockup-os.svg"]).group(1)); png("lockup-os.svg", round(lw * 3), 216, "lockup-os-3x.png"); png("mark-os.svg", 1200, round(1200 * MH / MW), "mark-os-1200.png")
def ico(entries, dest):
    blobs = [(w, (OUT / n).read_bytes()) for w, n in entries]; off = 6 + 16 * len(blobs); d = b""
    for w, b in blobs: d += struct.pack("<BBBBHHII", w % 256, w % 256, 0, 0, 1, 32, len(b), off); off += len(b)
    dest.write_bytes(struct.pack("<HHH", 0, 1, len(blobs)) + d + b"".join(b for _, b in blobs))
ico([(16, "favicon-os-16.png"), (32, "favicon-os-32.png"), (48, "favicon-os-48.png")], OUT / "favicon-os.ico")
print(len(files), "svg written; png and ico exports done")
