// Helpers shared by S7 (The Verdict) and S8 (Five Things To Watch). Everything is a pure function of the frame.
import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {ease} from '../kit/ease';
import {mulberry32} from '../kit/rng';

export type Ev = {t: number; type: string; gain?: number; dur?: number; dir?: string; pan?: number; note: string; f?: number; base?: number};

/** Frame (scene-local) of the nth event of a type, using the same Math.round(t * 30) as the sound sync list. */
export const evFrame = (events: readonly Ev[], type: string, nth = 0) => {
  const list = events.filter((e) => e.type === type);
  return Math.round(list[nth].t * 30);
};

/** 0..1 progress between two frames, clamped, eased. */
export const pr = (frame: number, a: number, b: number, easing: (t: number) => number = ease.out) =>
  interpolate(frame, [a, b], [0, 1], {easing, extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

/** Smooth closed Catmull-Rom spline through the points, as an SVG cubic path. */
export const closedSplinePath = (pts: [number, number][]) => {
  const n = pts.length;
  let d = `M${pts[0][0].toFixed(1)} ${pts[0][1].toFixed(1)}`;
  for (let i = 0; i < n; i++) {
    const p0 = pts[(i - 1 + n) % n];
    const p1 = pts[i];
    const p2 = pts[(i + 1) % n];
    const p3 = pts[(i + 2) % n];
    const c1x = p1[0] + (p2[0] - p0[0]) / 6;
    const c1y = p1[1] + (p2[1] - p0[1]) / 6;
    const c2x = p2[0] - (p3[0] - p1[0]) / 6;
    const c2y = p2[1] - (p3[1] - p1[1]) / 6;
    d += ` C${c1x.toFixed(1)} ${c1y.toFixed(1)} ${c2x.toFixed(1)} ${c2y.toFixed(1)} ${p2[0].toFixed(1)} ${p2[1].toFixed(1)}`;
  }
  return d + ' Z';
};

/** Periodic smooth value noise around a ring: vals are lattice values in [-1, 1], u is the position in [0, 1) (wraps). */
export const ringNoise = (vals: readonly number[], u: number) => {
  const n = vals.length;
  const x = (((u % 1) + 1) % 1) * n;
  const i = Math.floor(x);
  const f = x - i;
  const s = f * f * (3 - 2 * f);
  return vals[i % n] * (1 - s) + vals[(i + 1) % n] * s;
};

export const seededRing = (seed: number, k: number) => {
  const rnd = mulberry32(seed);
  return Array.from({length: k}, () => rnd() * 2 - 1);
};

type DustProps = {
  count: number;
  seed: number;
  color: string;
  alpha: [number, number];
  size: [number, number]; // radius px
  vx: number; // px per frame
  vy: number;
  twinkle?: number; // 0..1 alpha wobble
  stroke?: boolean; // draw as rims instead of filled dots (bokeh)
  soft?: boolean; // radial-gradient discs instead of hard dots (out-of-focus bokeh)
};

/** Drifting specks wrapped inside an over-sized box so parallax never shows an edge. One SVG, no filters. */
export const Dust: React.FC<DustProps> = ({count, seed, color, alpha, size, vx, vy, twinkle = 0.3, stroke = false, soft = false}) => {
  const frame = useCurrentFrame();
  const W = 2400;
  const H = 1500;
  const rnd = mulberry32(seed);
  const items = Array.from({length: count}, () => ({
    x: rnd() * W,
    y: rnd() * H,
    r: size[0] + rnd() * (size[1] - size[0]),
    a: alpha[0] + rnd() * (alpha[1] - alpha[0]),
    ph: rnd() * Math.PI * 2,
    k: 0.6 + rnd() * 0.8,
  }));
  const wrap = (v: number, m: number) => ((v % m) + m) % m;
  return (
    <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
      {soft && (
        <defs>
          <radialGradient id={`bk${seed}`}>
            <stop offset="0" stopColor={color} stopOpacity={0.55} />
            <stop offset="0.72" stopColor={color} stopOpacity={0.4} />
            <stop offset="1" stopColor={color} stopOpacity={0} />
          </radialGradient>
        </defs>
      )}
      {items.map((it, i) => {
        const x = wrap(it.x + vx * it.k * frame, W) - 240;
        const y = wrap(it.y + vy * it.k * frame, H) - 210;
        const a = it.a * (1 - twinkle + twinkle * (0.5 + 0.5 * Math.sin(frame / 24 + it.ph)));
        if (soft) return <circle key={i} cx={x} cy={y} r={it.r} fill={`url(#bk${seed})`} opacity={a} />;
        return stroke ? (
          <circle key={i} cx={x} cy={y} r={it.r} fill="none" stroke={color} strokeWidth={2} opacity={a} />
        ) : (
          <circle key={i} cx={x} cy={y} r={it.r} fill={color} opacity={a} />
        );
      })}
    </svg>
  );
};
