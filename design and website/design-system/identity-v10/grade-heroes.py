#!/usr/bin/env python3
"""Deterministic editorial grade for the four hero photographs (proposed, V10).

Keeps size, crop, pose and transparency; changes only colour, light and texture: royal blue -> navy, cooler navy shadows,
a little marigold warmth in the highlights, matte contrast, fine seeded grain, and a marigold rim light on the silhouette.
Needs numpy, scipy and Pillow (development only; the site ships the resulting WebP files).
    python3 design-system/identity-v10/grade-heroes.py     (from "design and website/")
"""
import colorsys
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "assets/public/assets/revisions"
OUT = ROOT / "assets/public/assets/identity/v10/heroes"
OUT.mkdir(parents=True, exist_ok=True)
NAVY = np.array([22, 39, 96], np.float32)
NIGHT = np.array([9, 16, 44], np.float32)
MARIGOLD = np.array([234, 169, 60], np.float32)
MARKER = np.array([246, 213, 145], np.float32)
PEARL = np.array([241, 243, 246], np.float32)
rng = np.random.default_rng(31102026)


def rgb_to_hsv(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx, mn = a.max(-1), a.min(-1)
    d = mx - mn
    h = np.zeros_like(mx)
    m = d > 1e-6
    rc = np.where(m, (mx - r) / np.where(m, d, 1), 0)
    gc = np.where(m, (mx - g) / np.where(m, d, 1), 0)
    bc = np.where(m, (mx - b) / np.where(m, d, 1), 0)
    h = np.where(mx == r, bc - gc, np.where(mx == g, 2.0 + rc - bc, 4.0 + gc - rc))
    h = (h / 6.0) % 1.0
    h = np.where(m, h, 0)
    s = np.where(mx > 1e-6, d / np.where(mx > 1e-6, mx, 1), 0)
    return h, s, mx


def hsv_to_rgb(h, s, v):
    i = np.floor(h * 6).astype(int) % 6
    f = h * 6 - np.floor(h * 6)
    p, q, t = v * (1 - s), v * (1 - f * s), v * (1 - (1 - f) * s)
    out = np.zeros(h.shape + (3,), np.float32)
    for k, (r, g, b) in enumerate([(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)]):
        m = i == k
        out[m] = np.stack([r[m], g[m], b[m]], -1)
    return out


def grade(img, strength=1.0, warm=0.07):
    a = np.asarray(img.convert("RGB"), np.float32) / 255.0
    h, s, v = rgb_to_hsv(a)
    # 1. royal / cobalt blue -> navy: pull hue toward 228 degrees, drop saturation and value (skin hues are untouched)
    deg = h * 360
    blue = np.clip(1 - np.abs(deg - 228) / 48, 0, 1) * np.clip(s * 1.6, 0, 1)
    h = np.where(blue > 0, (deg + (228 - deg) * 0.5 * blue) / 360, h)
    s = s * (1 - 0.42 * blue * strength)
    v = v * (1 - 0.30 * blue * strength)
    out = hsv_to_rgb(h, s, v) * 255.0
    # 2. matte S-curve and a navy lift in the shadows
    lum = (out @ np.array([0.2126, 0.7152, 0.0722], np.float32)) / 255.0
    curve = lum + 0.10 * (np.sin((lum - 0.5) * np.pi) * 0.5 + 0.5 - lum)
    out = out * (curve / np.maximum(lum, 1e-4))[..., None]
    sh = (np.clip(1 - lum * 1.6, 0, 1) ** 2)[..., None] * 0.34 * strength
    out = out * (1 - sh) + NIGHT * sh * 1.5
    # 3. warm marigold in the highlights, slight overall desaturation toward a quiet editorial look
    hi = (np.clip(lum, 0, 1) ** 3)[..., None] * warm * strength
    out = out * (1 - hi) + MARIGOLD * hi
    g = (out @ np.array([0.2126, 0.7152, 0.0722], np.float32))[..., None]
    out = out * 0.9 + g * 0.1
    # 4. seeded grain and a soft navy vignette
    out += rng.normal(0, 2.4, out.shape[:2])[..., None]
    yy, xx = np.mgrid[0:out.shape[0], 0:out.shape[1]]
    r = np.hypot((xx - out.shape[1] / 2) / (out.shape[1] / 2), (yy - out.shape[0] / 2) / (out.shape[0] / 2))
    vig = (np.clip(r - 0.55, 0, 1) ** 2)[..., None] * 0.30 * strength
    out = out * (1 - vig) + NAVY * vig
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def silhouette(img):
    """Dark figure with volume (navy gradient) and a marigold rim light on the upper-left edge. Alpha and framing are kept."""
    rgba = np.asarray(img.convert("RGBA"), np.float32)
    al = rgba[..., 3] / 255.0
    hgt, wid = al.shape
    t = np.linspace(0, 1, hgt)[:, None]
    body = NAVY * (1 - t[..., None]) * 0.55 + NIGHT * (0.45 + 0.55 * t[..., None])
    body = np.broadcast_to(body, (hgt, wid, 3)).copy()
    # soft top light across the shoulders
    xx = np.linspace(0, 1, wid)[None, :]
    body += (np.clip(1 - np.abs(xx - 0.38) * 2.4, 0, 1) * np.clip(1 - t * 1.6, 0, 1))[..., None] * np.array([26, 36, 62], np.float32)
    shifted = ndi.shift(al, (7, 7), order=1, mode="constant")
    rim = np.clip(al - shifted, 0, 1)
    rim = ndi.gaussian_filter(rim, 1.4)
    rim = np.clip(rim * 2.0, 0, 1)[..., None]
    core = ndi.gaussian_filter(np.clip(al - ndi.shift(al, (3, 3), order=1, mode="constant"), 0, 1), 0.8)[..., None]
    rgb = body * (1 - rim * 0.85) + MARIGOLD * rim * 0.85
    rgb = rgb * (1 - core * 0.6) + MARKER * core * 0.6
    rgb += rng.normal(0, 1.8, rgb.shape[:2])[..., None]
    out = np.dstack([np.clip(rgb, 0, 255), rgba[..., 3]]).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


jobs = [
    ("h1-shadow.webp", lambda: silhouette(Image.open(SRC / "v3/nature/05-real-human-shadow.webp"))),
    ("h2-founder.webp", lambda: grade(Image.open(SRC / "v5/people/founder-blue.webp"), 1.0, 0.07)),
    ("h3-avatar-a.webp", lambda: grade(Image.open(SRC / "v5/people/avatar-a.webp"), 1.0, 0.06)),
    ("h4-avatar-b.webp", lambda: grade(Image.open(SRC / "v5/people/avatar-b.webp"), 1.0, 0.06)),
]
for name, fn in jobs:
    im = fn()
    im.save(OUT / name, "WEBP", quality=88, method=6)
    print(name, im.size, im.mode, (OUT / name).stat().st_size // 1024, "KB")
