// Shared helpers for S2 (founder-mind map) and S5 (account network): head placement, motion helpers, ambient layers.
// Everything is a pure function of the frame; layouts come from seeded generators at module load.
import React from 'react';
import {Easing, useCurrentFrame} from 'remotion';
import {mulberry32, noise1} from '../kit/rng';
import {C} from '../kit/tokens';
import {HEAD_LENGTH, HEAD_PATH, headPoints, insideHead} from '../kit/head';

export type Pt = [number, number];

export const clamp01 = (v: number) => Math.min(1, Math.max(0, v));
/** Eased progress of a window [start, start + dur] at frame f, clamped to 0..1. */
export const prog = (f: number, start: number, dur: number, e: (t: number) => number = (t) => t) => e(clamp01((f - start) / dur));
export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
export const mixPt = (a: Pt, b: Pt, t: number): Pt => [lerp(a[0], b[0], t), lerp(a[1], b[1], t)];
/** Arrival with a very small overshoot (<= 6 %). */
export const popEase = Easing.out(Easing.back(1.0));
export const rgba = (hex: string, a: number) => {
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255}, ${a})`;
};

export type Ev = {t: number; type: string; gain?: number; dur?: number; dir?: string; pan?: number; note: string};
/** Frames (scene-local, sorted) of all events whose note starts with `prefix`. */
export const framesOf = (events: Ev[], prefix: string) =>
  events
    .filter((e) => e.note.startsWith(prefix))
    .map((e) => Math.round(e.t * 30))
    .sort((a, b) => a - b);

// ---------------------------------------------------------------------------------------------------------------------
// Head placement. S2 and S5 draw the same head at the same screen position; (960, 540) is local (350, 405): the founder dot.
// ---------------------------------------------------------------------------------------------------------------------
export const HS = 0.69; // head box 800 x 900 -> about 620 px tall
export const HUB: Pt = [960, 540];
export const HUB_LOCAL: Pt = [350, 405];
export const HEAD_OX = HUB[0] - HUB_LOCAL[0] * HS;
export const HEAD_OY = HUB[1] - HUB_LOCAL[1] * HS;
export const hc = (x: number, y: number): Pt => [HEAD_OX + x * HS, HEAD_OY + y * HS];

const canvasPts = HEAD_PATH.slice(1)
  .split(' L')
  .map((s) => {
    const [x, y] = s.split(' ').map(Number);
    return hc(x, y);
  });
/** The shared head outline in canvas pixels. */
export const HEAD_D = 'M' + canvasPts.map(([x, y]) => `${x.toFixed(1)} ${y.toFixed(1)}`).join(' L');
export const HEAD_LEN = HEAD_LENGTH * HS;

export const HeadOutline: React.FC<{p: number; alpha?: number; color?: string; width?: number}> = ({p, alpha = 1, color = C.nickel, width = 2}) => (
  <path
    d={HEAD_D}
    fill="none"
    stroke={color}
    strokeWidth={width}
    strokeLinecap="round"
    strokeLinejoin="round"
    opacity={alpha}
    strokeDasharray={HEAD_LEN + 4}
    strokeDashoffset={(1 - p) * (HEAD_LEN + 4)}
  />
);

/** Outline sample points on the canvas, used to keep nodes away from the line. */
const OUT: Pt[] = headPoints(180).map(([x, y]) => hc(x, y));
const distOut = (x: number, y: number) => {
  let m = 1e9;
  for (const [ox, oy] of OUT) {
    const d = Math.hypot(x - ox, y - oy);
    if (d < m) m = d;
  }
  return m;
};
const inHead = (x: number, y: number) => insideHead((x - HEAD_OX) / HS, (y - HEAD_OY) / HS);
export const okInside = (x: number, y: number, margin: number) => inHead(x, y) && distOut(x, y) > margin;

// ---------------------------------------------------------------------------------------------------------------------
// S2 layout: 8 diamonds (decisions), 6 pairs (trade-offs: A chosen, B unchosen), 8 hexagons (product knowledge).
// A jittered hex lattice is laid inside the head (seeded); each cluster takes the lattice points nearest its seed.
// ---------------------------------------------------------------------------------------------------------------------
const SPACING = 62;
const rnd = mulberry32(2026);
const bbox = {x0: HEAD_OX + 110 * HS, x1: HEAD_OX + 780 * HS, y0: HEAD_OY + 60 * HS, y1: HEAD_OY + 780 * HS};
let LATTICE: Pt[] = [];
for (let row = 0; ; row++) {
  const y = bbox.y0 + row * SPACING * 0.866;
  if (y > bbox.y1) break;
  for (let x = bbox.x0 + (row % 2) * (SPACING / 2); x < bbox.x1; x += SPACING) {
    const jx = x + (rnd() - 0.5) * 14;
    const jy = y + (rnd() - 0.5) * 14;
    if (okInside(jx, jy, 30) && Math.hypot(jx - HUB[0], jy - HUB[1]) >= 74) LATTICE.push([jx, jy]);
  }
}
const HUB_D = (p: Pt) => Math.hypot(p[0] - HUB[0], p[1] - HUB[1]);
const take = (seed: Pt, n: number): Pt[] => {
  const sorted = [...LATTICE].sort((a, b) => Math.hypot(a[0] - seed[0], a[1] - seed[1]) - Math.hypot(b[0] - seed[0], b[1] - seed[1]));
  const got = sorted.slice(0, n);
  LATTICE = LATTICE.filter((q) => !got.includes(q));
  return got;
};
// trade-off pairs: walk outward from the seed; each pair is a point and its nearest free neighbour
const T_SEED = hc(235, 385);
const T_PAIRS: [Pt, Pt][] = [];
for (let k = 0; k < 6; k++) {
  const [first] = take(T_SEED, 1);
  const [second] = take(first, 1);
  T_PAIRS.push([first, second]);
}
const D_POINTS = take(hc(505, 250), 8);
const H_POINTS = take(hc(505, 610), 8);

/** 8 diamonds, ordered outward from the founder dot so the light-up cascade sweeps away from it. */
export const DIAMONDS: Pt[] = D_POINTS.sort((a, b) => HUB_D(a) - HUB_D(b));
/** 8 hexagons, ordered the same way. */
export const HEXES: Pt[] = H_POINTS.sort((a, b) => HUB_D(a) - HUB_D(b));

export type PairRest = {a: Pt; b: Pt; m: Pt};
const pairs: PairRest[] = T_PAIRS.map(([u, v]) => {
  // the circle farther from the founder dot is the unchosen one (the road not taken)
  const [p0, p1] = HUB_D(u) <= HUB_D(v) ? [u, v] : [v, u];
  return {a: p0, b: p1, m: [(p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2] as Pt};
});
export const PAIRS: PairRest[] = pairs.sort((p, q) => HUB_D(p.m) - HUB_D(q.m));

/** Prim minimum spanning tree over points; returns index pairs. */
export const mst = (pts: Pt[]): [number, number][] => {
  const inTree = [0];
  const edges: [number, number][] = [];
  while (inTree.length < pts.length) {
    let best: [number, number] = [0, 0];
    let bd = 1e9;
    for (const i of inTree) {
      for (let j = 0; j < pts.length; j++) {
        if (inTree.includes(j)) continue;
        const d = Math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1]);
        if (d < bd) {
          bd = d;
          best = [i, j];
        }
      }
    }
    edges.push(best);
    inTree.push(best[1]);
  }
  return edges;
};

// ---------------------------------------------------------------------------------------------------------------------
// Ambient layers (seeded drifting motes and soft bokeh). Placed at different parallax depths by the scenes.
// ---------------------------------------------------------------------------------------------------------------------
export const Motes: React.FC<{seed: number; count: number; color: string; alpha: [number, number]; size: [number, number]; wander?: number; area?: [number, number, number, number]}> = ({seed, count, color, alpha, size, wander = 30, area = [-300, -200, 2220, 1280]}) => {
  const f = useCurrentFrame();
  const items = React.useMemo(() => {
    const r = mulberry32(seed);
    return Array.from({length: count}, () => ({
      x: lerp(area[0], area[2], r()),
      y: lerp(area[1], area[3], r()),
      s: lerp(size[0], size[1], r()),
      a: lerp(alpha[0], alpha[1], r()),
      sp: 70 + r() * 70,
      ph: r() * 100,
    }));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [seed, count]);
  return (
    <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
      {items.map((m, i) => (
        <circle key={i} cx={m.x + wander * noise1(f / m.sp + m.ph, seed + i)} cy={m.y + wander * noise1(f / (m.sp * 1.2) + m.ph + 40, seed + 91 + i)} r={m.s} fill={color} opacity={m.a} />
      ))}
    </svg>
  );
};

/** Soft out-of-focus discs (radial-gradient fills, no filters). Alpha stays well under 0.2. */
export const Bokeh: React.FC<{seed: number; count: number; idp: string; colors: string[]; alpha: [number, number]; size: [number, number]; area?: [number, number, number, number]; wander?: number}> = ({seed, count, idp, colors, alpha, size, area = [-200, -100, 2120, 1180], wander = 40}) => {
  const f = useCurrentFrame();
  const items = React.useMemo(() => {
    const r = mulberry32(seed);
    return Array.from({length: count}, (_, i) => ({
      x: lerp(area[0], area[2], r()),
      y: lerp(area[1], area[3], r()),
      s: lerp(size[0], size[1], r()),
      a: lerp(alpha[0], alpha[1], r()),
      c: i % colors.length,
      sp: 110 + r() * 80,
      ph: r() * 100,
    }));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [seed, count]);
  return (
    <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
      <defs>
        {colors.map((c, i) => (
          <radialGradient key={i} id={`${idp}-bk${i}`}>
            <stop offset="0" stopColor={c} stopOpacity="1" />
            <stop offset="0.6" stopColor={c} stopOpacity="0.7" />
            <stop offset="1" stopColor={c} stopOpacity="0" />
          </radialGradient>
        ))}
      </defs>
      {items.map((m, i) => (
        <circle key={i} cx={m.x + wander * noise1(f / m.sp + m.ph, seed + i)} cy={m.y + wander * noise1(f / (m.sp * 1.1) + m.ph + 30, seed + 53 + i)} r={m.s} fill={`url(#${idp}-bk${m.c})`} opacity={m.a} />
      ))}
    </svg>
  );
};
