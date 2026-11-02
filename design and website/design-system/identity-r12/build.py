#!/usr/bin/env python3
"""OS monogram directions (R12, proposed): rebuilds three shortlisted concepts as editable SVG with outlined type from the bundled OFL fonts
(Fraunces and Mona Sans, instantiated with fontTools; brotli is needed to read woff2). Run from this folder: python3 build.py (PYTHONPATH may point at a brotli install).
Outputs: os-d1/d2/d3 each in colour, inverse and mono, plus the 24 px small versions where they differ. Concepts only; none is approved."""
import pathlib
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

HERE = pathlib.Path(__file__).resolve().parent
FONTS = HERE.parent.parent / "assets/public/assets/identity/font-source"
NAVY, PEARL, SILVER, MARI, MARI3 = "#162760", "#F1F3F6", "#A9AFBA", "#EAA93C", "#F6D591"
fr = instantiateVariableFont(TTFont(FONTS / "fraunces/fraunces-latin-full-normal.woff2"), {"wght": 400, "opsz": 96, "SOFT": 0, "WONK": 0}, inplace=False)
mo = instantiateVariableFont(TTFont(FONTS / "mona-sans/mona-sans-latin-wght-normal.woff2"), {"wght": 500}, inplace=False)

def text_path(font, text, size, x=0.0, y=0.0, track=0.0):
    """Outlined text: returns (svg path data, advance width). Origin at the baseline."""
    gs, cmap, upm = font.getGlyphSet(), font.getBestCmap(), font["head"].unitsPerEm
    sc = size / upm; pen = SVGPathPen(gs); cx = x
    for ch in text:
        g = cmap[ord(ch)]
        gs[g].draw(TransformPen(pen, (sc, 0, 0, -sc, cx, y)))
        cx += gs[g].width * sc + track
    return pen.getCommands(), cx - x - track

def svg(w, h, body, title, bg=None):
    r = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img"><title>{title}</title>{r}{body}</svg>\n'

def d1(ink, orb, bg=None, small=False):
    """Serif OS with a marigold orbit: the O and S in Fraunces, a tilted orbit passing behind and in front."""
    d, wd = text_path(fr, "OS", 150, 0, 0, -6); x0 = (240 - wd) / 2
    d, wd = text_path(fr, "OS", 150, x0, 168, -6)
    sw = 9 if small else 5
    back = f'<g transform="rotate(-18 120 120)"><path d="M 22 120 A 98 40 0 0 1 218 120" fill="none" stroke="{orb}" stroke-width="{sw}" stroke-linecap="round"/></g>'
    front = f'<g transform="rotate(-18 120 120)"><path d="M 22 120 A 98 40 0 0 0 218 120" fill="none" stroke="{orb}" stroke-width="{sw}" stroke-linecap="round"/></g>'
    return svg(240, 240, back + f'<path d="{d}" fill="{ink}"/>' + front, "OS monogram direction 1: serif OS with a marigold orbit (concept, proposed)", bg)

def d2(ink, mark, bg=None, small=False):
    """Bracket OS: Mona Sans OS inside four marigold corner brackets with square handles (the site's selection gesture)."""
    d, wd = text_path(mo, "OS", 128, 0, 0, 4); x0 = (240 - wd) / 2
    d, wd = text_path(mo, "OS", 128, x0, 160, 4)
    s = 10 if small else 7; a, b = 34, 206; L = 44
    br = f'<g fill="none" stroke="{mark}" stroke-width="{s}" stroke-linecap="square"><path d="M{a} {a+L}V{a}H{a+L}"/><path d="M{b-L} {a}H{b}V{a+L}"/><path d="M{b} {b-L}V{b}H{b-L}"/><path d="M{a+L} {b}H{a}V{b-L}"/></g>'
    hs = "" if small else "".join(f'<rect x="{x-8}" y="{y-8}" width="16" height="16" rx="2" fill="{bg or PEARL}" stroke="{ink}" stroke-width="3.5"/>' for x, y in ((a, a), (b, a), (a, b), (b, b)))
    return svg(240, 240, f'<path d="{d}" fill="{ink}"/>' + br + hs, "OS monogram direction 2: bracketed OS, the selection gesture (concept, proposed)", bg)

def d3(plate, ink, wave, bg=None, small=False):
    """Badge OS: a rounded navy plate with a pearl serif OS and a marigold wave."""
    d, wd = text_path(fr, "OS", 120, 0, 0, -4); x0 = (240 - wd) / 2
    d, wd = text_path(fr, "OS", 120, x0, 140, -4)
    sw = 10 if small else 7
    wv = f'<path d="M52 176 C 82 154, 100 198, 130 176 S 176 154, 188 170" fill="none" stroke="{wave}" stroke-width="{sw}" stroke-linecap="round"/>'
    return svg(240, 240, f'<rect x="20" y="20" width="200" height="200" rx="58" fill="{plate}"/><path d="{d}" fill="{ink}"/>' + wv, "OS monogram direction 3: badge OS with a marigold wave (concept, proposed)", bg)

out = {
    "os-d1-serif-orbit.svg": d1(NAVY, MARI), "os-d1-serif-orbit-inverse.svg": d1(PEARL, MARI, "#0D1A3B"), "os-d1-serif-orbit-mono.svg": d1(NAVY, NAVY),
    "os-d1-serif-orbit-24.svg": d1(NAVY, MARI, small=True),
    "os-d2-bracket.svg": d2(NAVY, MARI), "os-d2-bracket-inverse.svg": d2(PEARL, MARI, "#0D1A3B"), "os-d2-bracket-mono.svg": d2(NAVY, NAVY), "os-d2-bracket-24.svg": d2(NAVY, MARI, small=True),
    "os-d3-badge.svg": d3(NAVY, PEARL, MARI), "os-d3-badge-inverse.svg": d3(PEARL, NAVY, MARI, "#0D1A3B"), "os-d3-badge-mono.svg": d3(NAVY, PEARL, PEARL), "os-d3-badge-24.svg": d3(NAVY, PEARL, MARI, small=True),
}
for k, v in out.items(): (HERE / k).write_text(v)
print(len(out), "svg files")
