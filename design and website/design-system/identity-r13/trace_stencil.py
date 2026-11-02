#!/usr/bin/env python3
"""Rebuilds the left OS mark of Codex concept LOGO-03 (R11 EXTRA-LOGO) as clean vector paths.
Usage: python3 trace_stencil.py --source <LOGO-03.png> [--box 100,150,720,500] [--out os-stencil-paths.json]
Needs numpy, Pillow, scipy and potracer (pure-Python potrace port). The source image stays outside the public repository; the traced paths are the committed result.
Steps: nearest-palette colour separation at 4x, median plus Gaussian clean-up, potrace per colour layer, coordinates baked into a 100-unit-high box, plus a gap-closed navy O for small sizes."""
import argparse, json, sys, numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage
import potrace
ap = argparse.ArgumentParser(); ap.add_argument("--source", required=True); ap.add_argument("--box", default="100,150,720,500"); ap.add_argument("--out", default="os-stencil-paths.json"); a = ap.parse_args()
BOX = tuple(int(v) for v in a.box.split(",")); UP = 4; HEIGHT = 100.0
PAL = {"bg": (238, 241, 245), "navy": (10, 31, 76), "silver": (159, 165, 177), "gold": (227, 159, 60)}
im = Image.open(a.source).convert("RGB").crop(BOX); im = im.resize((im.width * UP, im.height * UP), Image.LANCZOS)
arr = np.asarray(im).astype(float); names = list(PAL)
lab = np.stack([((arr - np.array(PAL[n])) ** 2).sum(-1) for n in names], -1).argmin(-1)
masks = {n: np.asarray(Image.fromarray(((lab == i) * 255).astype("uint8")).filter(ImageFilter.MedianFilter(7)).filter(ImageFilter.GaussianBlur(2.2))) > 127 for i, n in enumerate(names) if n != "bg"}
ys, xs = np.where(masks["navy"] | masks["silver"] | masks["gold"]); x0, y0, x1, y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
K = HEIGHT / (y1 - y0); W = round((x1 - x0) * K, 2)
masks["navy_solid"] = ndimage.binary_closing(masks["navy"], structure=np.ones((1, 61)), border_value=0) | masks["navy"]
def d_of(mask):
    pl = potrace.Bitmap(~mask).trace(turdsize=60, turnpolicy=potrace.POTRACE_TURNPOLICY_MINORITY, alphamax=1.05, opticurve=True, opttolerance=0.6)
    f = lambda p: f"{(p.x - x0) * K:.2f} {(p.y - y0) * K:.2f}"; out = []
    for c in pl:
        out.append("M" + f(c.start_point))
        for s in c.segments: out.append(f"L{f(s.c)}L{f(s.end_point)}" if s.is_corner else f"C{f(s.c1)} {f(s.c2)} {f(s.end_point)}")
        out.append("Z")
    return "".join(out)
res = {"width": W, "height": HEIGHT, "box_px_at_source": [int(x1 - x0) / UP, int(y1 - y0) / UP], **{n: d_of(m) for n, m in masks.items()}}
json.dump(res, open(a.out, "w"), indent=1); print("wrote", a.out, "box", W, "x", HEIGHT, {n: len(res[n]) for n in masks})
# fidelity reference masks (1x) for the checker
np.savez_compressed(a.out.replace(".json", "-ref.npz"), **{n: masks[n][y0:y1, x0:x1] for n in ("navy", "silver", "gold")})
