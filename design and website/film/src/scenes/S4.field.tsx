// S4 helper: the small head map and its convergence into one marigold core (P7), plus shared timing constants.
// Everything is a pure function of the scene-local frame; the layout is baked once at module level from a seeded generator.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {ease} from '../kit/ease';
import {HEAD_PATH, headPoints, insideHead} from '../kit/head';
import {mulberry32, noise1} from '../kit/rng';
import {C} from '../kit/tokens';
import events from './S4.events.json';

type Ev = {t: number; type: string; gain?: number; dur?: number; dir?: string; pan?: number; note: string};
const EV = events as Ev[];

export const F = (t: number) => Math.round(t * 30);
/** Detonation frame (boom), the three label frames (ticks) and the scan-ring frame (first whoosh), all from S4.events.json. */
export const BOOM = F(EV.find((e) => e.type === 'boom')!.t);
export const TICKS = EV.filter((e) => e.type === 'tick').map((e) => F(e.t));
export const SCAN = F(EV.find((e) => e.type === 'whoosh')!.t);
export const INHALE = BOOM - 10;

export const clamp01 = (v: number) => Math.max(0, Math.min(1, v));
export const rgba = (hex: string, a: number) => {
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255}, ${a})`;
};

export const CORE = {x: 960, y: 540} as const;

// ---- layout of the map (head box 800 x 900 -> screen) ----
const S = 0.56;
const scr = (x: number, y: number): [number, number] => [CORE.x + (x - 400) * S, CORE.y + (y - 450) * S];

const rnd = mulberry32(2610);
const R = (a: number, b: number) => a + rnd() * (b - a);
const room = (x: number, y: number, m: number) => insideHead(x, y) && insideHead(x + m, y) && insideHead(x - m, y) && insideHead(x, y + m) && insideHead(x, y - m);
const taken: [number, number, number][] = [];
const spot = (rad: number, m: number): [number, number] => {
  let scale = 1;
  for (let tries = 1; ; tries++) {
    if (tries % 500 === 0) scale *= 0.94;
    const x = R(120, 780);
    const y = R(70, 690);
    if (!room(x, y, m)) continue;
    if (taken.every(([tx, ty, tr]) => Math.hypot(tx - x, ty - y) >= (tr + rad) * scale) || tries > 30000) {
      taken.push([x, y, rad]);
      return [x, y];
    }
  }
};

export type Kind = 'dot' | 'diamond' | 'ring' | 'hex';
export type FieldNode = {kind: Kind; x: number; y: number; s: number; d: number; curl: number; tone: number; cl: number; pair: number; id: number};
const NODES: FieldNode[] = [];
const add = (n: Omit<FieldNode, 'id'>) => NODES.push({...n, id: NODES.length});
const sign = () => (rnd() < 0.5 ? -1 : 1);

// trade-off pairs (cluster 1): two rings joined by a dashed edge
for (let k = 0; k < 6; k++) {
  const [cx, cy] = spot(54, 70);
  const th = R(0, Math.PI);
  const [ax, ay] = scr(cx - Math.cos(th) * 34, cy - Math.sin(th) * 34);
  const [bx, by] = scr(cx + Math.cos(th) * 34, cy + Math.sin(th) * 34);
  const s = TICKS[1] + 2 + k * 3;
  add({kind: 'ring', x: ax, y: ay, s, d: 34, curl: sign() * R(26, 60), tone: 0, cl: 1, pair: k});
  add({kind: 'ring', x: bx, y: by, s, d: 34, curl: sign() * R(26, 60), tone: 0, cl: 1, pair: k});
}
// decisions (cluster 0): diamonds
for (let i = 0; i < 8; i++) {
  const [x, y] = scr(...spot(32, 30));
  add({kind: 'diamond', x, y, s: TICKS[0] + 2 + i * 2.5, d: 34, curl: sign() * R(26, 60), tone: 0, cl: 0, pair: -1});
}
// product knowledge (cluster 2): hexagons
for (let i = 0; i < 8; i++) {
  const [x, y] = scr(...spot(32, 30));
  add({kind: 'hex', x, y, s: TICKS[2] + i * 2.2, d: 18, curl: sign() * R(20, 46), tone: 0, cl: 2, pair: -1});
}
// fine dots (cluster 3): 60 on the outline and 62 inside; they stream in from the start
headPoints(60).forEach(([hx, hy]) => {
  const [x, y] = scr(hx, hy);
  add({kind: 'dot', x, y, s: 4 + rnd() * 108, d: 40 + rnd() * 12, curl: sign() * R(18, 52), tone: Math.floor(rnd() * 3), cl: 3, pair: -1});
});
for (let i = 0; i < 62; i++) {
  let hx = 0;
  let hy = 0;
  for (let tries = 0; tries < 4000; tries++) {
    hx = R(120, 780);
    hy = R(70, 700);
    if (room(hx, hy, 14) && taken.every(([tx, ty, tr]) => Math.hypot(tx - hx, ty - hy) >= tr * 0.62 + 10)) break;
  }
  const [x, y] = scr(hx, hy);
  add({kind: 'dot', x, y, s: 4 + rnd() * 108, d: 40 + rnd() * 12, curl: sign() * R(18, 52), tone: Math.floor(rnd() * 3), cl: 3, pair: -1});
}
const N = NODES.length;
const DOT_R = NODES.map((n) => (n.kind === 'dot' ? 3.2 + ((n.id * 37) % 10) * 0.17 : 0));

const pos = (n: FieldNode, f: number) => {
  const p = clamp01((f - n.s) / n.d);
  const e = ease.inOut(p);
  const dx = CORE.x - n.x;
  const dy = CORE.y - n.y;
  const len = Math.hypot(dx, dy) || 1;
  const bend = n.curl * Math.sin(Math.PI * e);
  const sway = 1 - e;
  return {
    x: n.x + dx * e - (dy / len) * bend + noise1(f / 45 + n.id * 1.7, n.id + 3) * 2.6 * sway,
    y: n.y + dy * e + (dx / len) * bend + noise1(f / 52 + n.id * 2.3, n.id + 91) * 2.6 * sway,
    p,
    e,
  };
};

/** 0..1: how much of the map has been absorbed by the core at frame f. */
export const arrivedFrac = (f: number) => {
  let acc = 0;
  for (const n of NODES) acc += clamp01((f - (n.s + n.d) + 6) / 6);
  return acc / N;
};

const DOT_FILL = [C.nickel, C.pearl, C.m300];
const DOT_ALPHA = [0.85, 0.9, 0.9];

export const Field: React.FC = () => {
  const f = useCurrentFrame();
  if (f > BOOM + 2) return null;
  const nodes: React.ReactNode[] = [];
  const links: React.ReactNode[] = [];
  const halos: React.ReactNode[] = [];
  let trails = '';
  let trailsPearl = '';

  // outline: draws on over the first frames, then contracts into the core while fading (no stray leftovers)
  const dOn = ease.inOut(clamp01((f + 8) / 26));
  const sc = 1 - 0.88 * ease.inOut(clamp01((f - 96) / 70));
  const outlineA = (1 - clamp01((f - 118) / 40)) * 0.9;

  const byPair: Record<number, {x: number; y: number}[]> = {};
  for (const n of NODES) {
    const wake = ease.out(clamp01((f + 7 - (n.id % 40) * 0.4) / 12));
    if (wake <= 0) continue;
    const q = pos(n, f);
    const fade = (1 - clamp01((q.p - 0.82) / 0.18)) * wake;
    if (fade <= 0.01) continue;
    const shrink = (1 - 0.6 * q.e) * (0.6 + 0.4 * wake);
    const lit = n.cl < 3 ? f - TICKS[n.cl] : -1;
    const pop = lit >= 0 && lit < 14 ? 1 + 0.32 * Math.sin((Math.PI * lit) / 14) : 1;
    if (lit >= 0 && lit < 14) {
      halos.push(<circle key={`h${n.id}`} cx={q.x} cy={q.y} r={18 + 34 * ease.out(lit / 14)} fill="none" stroke={C.m400} strokeWidth={2} opacity={(1 - lit / 14) * 0.85} />);
    }
    if (n.kind === 'dot') {
      const r = DOT_R[n.id] * shrink;
      nodes.push(<circle key={n.id} cx={q.x} cy={q.y} r={r} fill={DOT_FILL[n.tone]} opacity={fade * DOT_ALPHA[n.tone]} />);
      if (q.p > 0 && q.p < 0.93) {
        const b = pos(n, f - 3);
        const seg = `M${b.x.toFixed(1)} ${b.y.toFixed(1)}L${q.x.toFixed(1)} ${q.y.toFixed(1)}`;
        if (n.tone === 1) trailsPearl += seg;
        else trails += seg;
      }
    } else if (n.kind === 'diamond') {
      const h = 19 * shrink * pop;
      nodes.push(<polygon key={n.id} points={`${q.x},${q.y - h} ${q.x + h},${q.y} ${q.x},${q.y + h} ${q.x - h},${q.y}`} fill={C.m400} opacity={fade} />);
    } else if (n.kind === 'hex') {
      const r = 17.5 * shrink * pop;
      const pts = Array.from({length: 6}, (_, k) => `${(q.x + Math.cos(((60 * k - 90) * Math.PI) / 180) * r).toFixed(1)},${(q.y + Math.sin(((60 * k - 90) * Math.PI) / 180) * r).toFixed(1)}`).join(' ');
      nodes.push(<polygon key={n.id} points={pts} fill={C.nickel} opacity={fade} />);
    } else {
      nodes.push(<circle key={n.id} cx={q.x} cy={q.y} r={11 * shrink * pop} fill="none" stroke={C.pearl} strokeWidth={3.5} opacity={fade} />);
      (byPair[n.pair] ??= []).push({x: q.x, y: q.y});
      if (byPair[n.pair].length === 2) {
        const [a, b] = byPair[n.pair];
        links.push(<line key={`l${n.pair}`} x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke={C.nickel} strokeWidth={2.5} strokeDasharray="6 6" opacity={fade * 0.8} />);
      }
    }
  }

  return (
    <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
      {outlineA > 0.01 && (
        <path
          d={HEAD_PATH}
          transform={`translate(${CORE.x} ${CORE.y}) scale(${S * sc}) translate(-400 -450)`}
          fill="none"
          stroke={C.nickel}
          strokeWidth={3 / (S * sc)}
          strokeLinejoin="round"
          strokeLinecap="round"
          pathLength={1}
          strokeDasharray={`${dOn} 3`}
          opacity={outlineA}
        />
      )}
      {links}
      <path d={trails} fill="none" stroke={C.nickel} strokeWidth={3} strokeLinecap="round" opacity={0.45} />
      <path d={trailsPearl} fill="none" stroke={C.pearl} strokeWidth={3} strokeLinecap="round" opacity={0.5} />
      {nodes}
      {halos}
    </svg>
  );
};

/** The bright marigold core. It grows with every absorbed node, pulses faster as the riser climbs, inhales just before the boom, then flares. */
export const Core: React.FC = () => {
  const f = useCurrentFrame();
  if (f > BOOM + 12) return null;
  const fr = arrivedFrac(f);
  const born = ease.out(clamp01((f + 8) / 18));
  let r = (9 + 43 * Math.pow(fr, 0.85)) * (1 + (0.03 + 0.07 * fr) * Math.sin(0.34 * f + 0.0024 * f * f));
  let a = born;
  if (f >= INHALE && f < BOOM) r *= 1 - 0.4 * ease.out(clamp01((f - INHALE) / 9));
  if (f >= BOOM) {
    const t = f - BOOM;
    r = 32 + 130 * ease.out(clamp01(t / 8));
    a = 1 - clamp01((t - 2) / 9);
  }
  const g = (rad: number, stops: string): React.CSSProperties => ({position: 'absolute', left: CORE.x - rad, top: CORE.y - rad, width: rad * 2, height: rad * 2, borderRadius: '50%', background: stops});
  return (
    <>
      <div style={{...g(r * 3.4, `radial-gradient(circle, ${rgba(C.m500, 0.32)} 0%, ${rgba(C.m500, 0)} 70%)`), opacity: a}} />
      <div style={{...g(r, `radial-gradient(circle, ${C.white} 0%, ${C.white} 16%, ${C.m200} 32%, ${C.m400} 54%, ${rgba(C.m500, 0.6)} 74%, ${rgba(C.m500, 0)} 100%)`), opacity: a}} />
    </>
  );
};
