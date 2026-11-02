#!/usr/bin/env python3
"""Adapts the owner-selected direction A (bracket OS, R12) into production candidates: lockup with the V5 outlined wordmark (unchanged geometry),
profile avatar, favicon and apple-touch tiles, an animated SVG, and PNG exports. Run build.py first. Needs Pillow, fontTools and brotli (see build.py); PNGs use headless Chrome.
Usage: python3 build_bracket.py [--chrome "/path/to/chrome"]"""
import pathlib, re, subprocess, sys, tempfile
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import build as B                     # reuses the font instances and text_path
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
mb = instantiateVariableFont(TTFont(B.FONTS / "mona-sans/mona-sans-latin-wght-normal.woff2"), {"wght": 680}, inplace=False)  # heavier cut for favicon and 24 px
# Geometry in the 240 box, measured with fontTools bounds: OS at 112 is 156 wide x 84 high; frame 26..214 leaves 12.5 clearance, arms (44) stay clear of the letter band (78..162).
LT, FA, FB, FL = dict(size=112, x=120, y=162, track=2), 26, 214, 44
HERE = pathlib.Path(__file__).resolve().parent; DW = HERE.parent.parent
OUT = DW / "assets/public/assets/identity/r12"; OUT.mkdir(parents=True, exist_ok=True)
CH = sys.argv[sys.argv.index("--chrome") + 1] if "--chrome" in sys.argv else "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
NAVY, PEARL, SILVER, MARI, DEEP = B.NAVY, B.PEARL, B.SILVER, B.MARI, "#0D1A3B"
WM = (DW / "assets/public/assets/revisions/v5/identity/wordmark-mono.svg").read_text()
wm_w, wm_h = [float(x) for x in re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', WM).groups()]
wm_paths = re.findall(r'<path data-letter="[^"]*" d="([^"]+)"[^>]*? transform="([^"]+)"', WM)
assert len(wm_paths) == 9, len(wm_paths)

def letters(font, size, x, y, track):
    d, w = B.text_path(font, "OS", size, 0, 0, track); x0 = x - w / 2
    return B.text_path(font, "OS", size, x0, y, track)[0]
def brackets(a, b, L, s, col, cap="square"):
    return f'<g fill="none" stroke="{col}" stroke-width="{s}" stroke-linecap="{cap}"><path d="M{a} {a+L}V{a}H{a+L}"/><path d="M{b-L} {a}H{b}V{a+L}"/><path d="M{b} {b-L}V{b}H{b-L}"/><path d="M{a+L} {b}H{a}V{b-L}"/></g>'
def handles(a, b, r, ink, fill):
    return "".join(f'<rect x="{x-r}" y="{y-r}" width="{2*r}" height="{2*r}" rx="2" fill="{fill}" stroke="{ink}" stroke-width="3.5"/>' for x, y in ((a, a), (b, a), (a, b), (b, b)))
def svg(w, h, vb, body, title): return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="{vb}" role="img"><title>{title}</title>{body}</svg>\n'

def os_path(font=None): return letters(font or B.mo, LT["size"], LT["x"], LT["y"], LT["track"])
def monogram(ink, mark, fill):  # 240 box, as direction A
    return f'<path d="{os_path()}" fill="{ink}"/>' + brackets(FA, FB, FL, 7, mark) + handles(FA, FB, 8, ink, fill)
def lockup(ink1, ink2, mark, fill, bg=None):
    sc = 112 / 240; wmh = 56; wms = wmh / wm_h; gap = 30; W = round(112 + gap + wm_w * wms); H = 112
    r = f'<rect width="{W}" height="{H}" fill="{bg}"/>' if bg else ""
    g = f'<g transform="scale({sc:.5f})">{monogram(ink1, mark, fill)}</g>'
    cols = [ink1] * 3 + [ink2] * 6
    wmk = f'<g transform="translate({112+gap} {(H-wmh)/2:.2f}) scale({wms:.5f})">' + "".join(f'<path d="{d}" transform="{tr}" fill="{c}"/>' for (d, tr), c in zip(wm_paths, cols)) + "</g>"
    return svg(W, H, f"0 0 {W} {H}", r + g + wmk, "OUTSPOKEN lockup: bracket OS monogram with the V5 outlined wordmark (proposed)")
def avatar(small=False):  # 800 square, brackets inside the circular crop
    k = 800 / 240; inner = f'<g transform="translate(400 400) scale({k*0.66:.4f}) translate(-120 -120)">'
    s = 9.5 if small else 7
    return svg(800, 800, "0 0 800 800", f'<rect width="800" height="800" fill="{NAVY}"/>{inner}<path d="{os_path(mb if small else None)}" fill="{PEARL}"/>{brackets(FA,FB,FL,s,MARI)}{"" if small else handles(FA,FB,8,PEARL,NAVY)}</g>', "OUTSPOKEN profile avatar: bracket OS (proposed)")
def favicon():  # 64 tile, no handles, thick brackets
    return svg(64, 64, "0 0 64 64", f'<rect width="64" height="64" rx="14" fill="{NAVY}"/><g transform="translate(6 6) scale({52/240:.4f})"><path d="{letters(mb,112,120,162,2)}" fill="{PEARL}"/>{brackets(22,218,46,16,MARI)}</g>', "OUTSPOKEN favicon candidate: bracket OS (proposed)")
def animated():
    a, b, L = FA, FB, FL; segs = [f"M{a} {a+L}V{a}H{a+L}", f"M{b-L} {a}H{b}V{a+L}", f"M{b} {b-L}V{b}H{b-L}", f"M{a+L} {b}H{a}V{b-L}"]
    css = ".br{stroke-dasharray:132;stroke-dashoffset:132;animation:draw .7s cubic-bezier(.22,1,.36,1) forwards}.hd{opacity:0;transform-box:fill-box;transform-origin:center;animation:pop .35s cubic-bezier(.34,1.56,.64,1) forwards}.ltr{opacity:0;animation:fade .5s .1s forwards}@keyframes draw{to{stroke-dashoffset:0}}@keyframes pop{from{opacity:0;transform:scale(.3)}to{opacity:1;transform:scale(1)}}@keyframes fade{to{opacity:1}}@media (prefers-reduced-motion:reduce){.br,.hd,.ltr{animation:none;stroke-dashoffset:0;opacity:1}}"  # delays are inline so they do not depend on child order
    br = "".join(f'<path class="br" style="animation-delay:{i*.12:.2f}s" d="{s}" fill="none" stroke="{MARI}" stroke-width="7" stroke-linecap="square"/>' for i, s in enumerate(segs))
    hd = "".join(f'<rect class="hd" style="animation-delay:{.7+i*.08:.2f}s" x="{x-8}" y="{y-8}" width="16" height="16" rx="2" fill="{PEARL}" stroke="{NAVY}" stroke-width="3.5"/>' for i, (x, y) in enumerate(((a, a), (b, a), (a, b), (b, b))))
    return svg(240, 240, "0 0 240 240", f"<style>{css}</style><path class=\"ltr\" d=\"{os_path()}\" fill=\"{NAVY}\"/>{br}{hd}", "OUTSPOKEN bracket OS, animated selection (respects reduced motion; proposed)")
files = {"os-bracket-lockup.svg": lockup(NAVY, SILVER, MARI, PEARL), "os-bracket-lockup-inverse.svg": lockup("#F2F5FA", "#B9C7DA", MARI, DEEP, DEEP), "os-bracket-lockup-mono.svg": lockup(NAVY, NAVY, NAVY, PEARL),
         "os-bracket-avatar.svg": avatar(), "os-bracket-avatar-24.svg": avatar(True), "os-bracket-favicon.svg": favicon(), "os-bracket-animated.svg": animated()}
for k, v in files.items(): (HERE / k).write_text(v); (OUT / k).write_text(v)
def png(svgname, w, h, name, bg="transparent"):
    with tempfile.TemporaryDirectory() as t:
        html = pathlib.Path(t) / "p.html"; html.write_text(f'<!doctype html><body style="margin:0;background:{bg}"><img src="file://{HERE / svgname}" width="{w}" height="{h}" style="display:block">')
        subprocess.run([CH, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files", "--virtual-time-budget=2000", f"--window-size={w},{h}", f"--screenshot={OUT / name}", f"file://{html}"], capture_output=True)
png("os-bracket-avatar.svg", 800, 800, "os-bracket-avatar-800.png"); png("os-bracket-avatar.svg", 400, 400, "os-bracket-avatar-400.png")
png("os-bracket-favicon.svg", 64, 64, "os-bracket-favicon-64.png", "#F1F3F6"); png("os-bracket-favicon.svg", 180, 180, "os-bracket-apple-touch-180.png", "#F1F3F6")
lw = re.search(r'width="(\d+)"', files["os-bracket-lockup.svg"]).group(1); png("os-bracket-lockup.svg", int(lw) * 2, 224, "os-bracket-lockup-2x.png", "#F1F3F6")
print(len(files), "svg and 5 png written")
