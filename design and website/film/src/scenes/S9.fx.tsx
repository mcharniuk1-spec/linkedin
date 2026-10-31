// S9 helper: P7 convergence and the three P4 coronas, drawn on one additive canvas as closed-form functions of the frame.
// A corona is born on an ellipse that encloses its subject and moves outward along the ellipse's normals,
// so by construction no particle can enter the subject. Per-particle masks add the hard keep-out around the wordmark
// (box + 1x its height) and a 35 % dimming over text blocks.
import React, {useLayoutEffect, useRef} from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';
import {ease} from '../kit/ease';
import {mulberry32} from '../kit/rng';
import {C, HEAT} from '../kit/tokens';

export type Rect = {x0: number; y0: number; x1: number; y1: number};
export type Hit = {
  f: number;
  cx: number;
  cy: number;
  hw: number; // half width of the subject rectangle (0 gives a circle)
  hh: number;
  d0: number; // distance of the birth outline from the subject rectangle
  n: number;
  seed: number;
  speed: [number, number]; // px per frame at birth
  drag: number;
  life: [number, number];
  size: [number, number];
  streaks: number; // share of particles drawn as short streaks
};

const hexRgb = (hex: string): [number, number, number] => {
  const n = parseInt(hex.slice(1), 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
};
const HEAT_RGB = HEAT.map(hexRgb);
const heat = (u: number): string => {
  const x = Math.max(0, Math.min(1, u)) * (HEAT_RGB.length - 1);
  const i = Math.min(HEAT_RGB.length - 2, Math.floor(x));
  const k = x - i;
  const q = (c: number) => Math.round(((HEAT_RGB[i][c] * (1 - k) + HEAT_RGB[i + 1][c] * k) / 8)) * 8;
  const h = (v: number) => Math.min(255, v).toString(16).padStart(2, '0');
  return `#${h(q(0))}${h(q(1))}${h(q(2))}`;
};

const sprites = new Map<string, HTMLCanvasElement>();
const sprite = (color: string) => {
  let s = sprites.get(color);
  if (!s) {
    s = document.createElement('canvas');
    s.width = s.height = 64;
    const g = s.getContext('2d')!;
    const [r, gg, b] = hexRgb(color);
    const grad = g.createRadialGradient(32, 32, 0, 32, 32, 32);
    grad.addColorStop(0, `rgba(${r},${gg},${b},1)`);
    grad.addColorStop(0.35, `rgba(${r},${gg},${b},1)`);
    grad.addColorStop(1, `rgba(${r},${gg},${b},0)`);
    g.fillStyle = grad;
    g.fillRect(0, 0, 64, 64);
    sprites.set(color, s);
  }
  return s;
};

// ---- the convergence (frames 0-13) ----
const cr = mulberry32(9090);
const CONV = Array.from({length: 110}, () => {
  const ang = cr() * Math.PI * 2;
  const r0 = 150 + cr() * 310;
  const arr = 9 + cr() * 4;
  const size = 2.2 + cr() * 2.6;
  const curl = (cr() - 0.5) * 1.3;
  const pick = cr();
  return {ang, r0, arr, size, curl, col: pick < 0.45 ? C.white : pick < 0.75 ? C.m300 : C.m200};
});
const CENTER = {x: 960, y: 540};
const convPos = (p: (typeof CONV)[number], f: number) => {
  const e = ease.in(Math.max(0, Math.min(1, f / p.arr)));
  const rad = p.r0 * (1 - e);
  const a = p.ang + p.curl * e;
  return {x: CENTER.x + Math.cos(a) * rad * 1.15, y: CENTER.y + Math.sin(a) * rad * 0.8, e};
};

// ---- point on the birth ellipse, with its outward normal. The ellipse encloses the subject rectangle (it passes d0 outside its corners),
// and every particle then moves along the outward normal of a convex curve, so it can never re-enter the subject. ----
const outline = (h: Hit, u: number): [number, number, number, number] => {
  const a = h.hw * Math.SQRT2 + h.d0;
  const b = h.hh * Math.SQRT2 + h.d0;
  const th = u * Math.PI * 2;
  const nx = Math.cos(th) / a;
  const ny = Math.sin(th) / b;
  const l = Math.hypot(nx, ny);
  return [h.cx + a * Math.cos(th), h.cy + b * Math.sin(th), nx / l, ny / l];
};

const distOutside = (r: Rect, x: number, y: number) => Math.hypot(Math.max(r.x0 - x, 0, x - r.x1), Math.max(r.y0 - y, 0, y - r.y1));
const maskAt = (x: number, y: number, hard: Rect[], soft: Rect[]) => {
  let m = 1;
  for (const r of hard) m *= Math.min(1, distOutside(r, x, y) / 40);
  for (const r of soft) m *= 0.35 + 0.65 * Math.min(1, distOutside(r, x, y) / 24);
  return m;
};

export const Fx: React.FC<{hits: Hit[]; hard: (f: number) => Rect[]; soft: (f: number) => Rect[]}> = ({hits, hard, soft}) => {
  const frame = useCurrentFrame();
  const {width, height} = useVideoConfig();
  const ref = useRef<HTMLCanvasElement>(null);
  useLayoutEffect(() => {
    const cv = ref.current;
    if (!cv) return;
    const g = cv.getContext('2d')!;
    g.clearRect(0, 0, width, height);
    g.globalCompositeOperation = 'lighter';
    g.lineCap = 'round';

    // convergence
    if (frame < 15) {
      for (const p of CONV) {
        const q = convPos(p, frame);
        const a = 1 - Math.max(0, Math.min(1, (frame - (p.arr - 2)) / 2));
        if (a <= 0.01) continue;
        const b = convPos(p, Math.max(0, frame - 1.6));
        g.globalAlpha = a * 0.55;
        g.strokeStyle = p.col;
        g.lineWidth = Math.max(1.5, p.size * 0.6);
        g.beginPath();
        g.moveTo(b.x, b.y);
        g.lineTo(q.x, q.y);
        g.stroke();
        g.globalAlpha = a;
        const r = p.size * 2.2;
        g.drawImage(sprite(p.col), q.x - r, q.y - r, r * 2, r * 2);
      }
    }

    // coronas
    const hr = hard(frame);
    const sr = soft(frame);
    for (const h of hits) {
      const t = frame - h.f;
      if (t < 0 || t > h.life[1]) continue;
      const rnd = mulberry32(h.seed);
      for (let i = 0; i < h.n; i++) {
        const u0 = rnd();
        const sp = h.speed[0] + rnd() * (h.speed[1] - h.speed[0]);
        const life = h.life[0] + rnd() * (h.life[1] - h.life[0]);
        const size = h.size[0] + rnd() * (h.size[1] - h.size[0]);
        const streak = rnd() < h.streaks;
        const jit = (rnd() - 0.5) * 12;
        if (t > life) continue;
        const [ox, oy, nx, ny] = outline(h, u0);
        const d = (1 - Math.exp(-h.drag * t)) / h.drag;
        const px = ox + nx * sp * d - ny * jit;
        const py = oy + ny * sp * d + nx * jit;
        const u = t / life;
        const m = maskAt(px, py, hr, sr);
        const alpha = Math.max(0, 1 - u * u) * m * Math.min(1, 0.25 + t / 3);
        if (alpha <= 0.01) continue;
        const col = heat(u * 0.92);
        if (streak) {
          const len = sp * Math.exp(-h.drag * t) * 3;
          g.globalAlpha = alpha;
          g.strokeStyle = col;
          g.lineWidth = Math.max(1.5, size * (1 - u * 0.5));
          g.beginPath();
          g.moveTo(px - nx * len, py - ny * len);
          g.lineTo(px, py);
          g.stroke();
        } else {
          const r = size * (1 - u * 0.5) * 2.2;
          g.globalAlpha = alpha;
          g.drawImage(sprite(col), px - r, py - r, r * 2, r * 2);
        }
      }
    }
    g.globalAlpha = 1;
    g.globalCompositeOperation = 'source-over';
  });
  return <canvas ref={ref} width={width} height={height} style={{position: 'absolute', inset: 0, width, height, pointerEvents: 'none'}} />;
};
