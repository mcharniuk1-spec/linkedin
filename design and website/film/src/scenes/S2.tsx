import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {CameraRig, Layer, CamKey} from '../kit/Camera';
import {Particles, Burst} from '../kit/Particles';
import {Scramble} from '../kit/Type';
import {FictionalTag, Marker, Vignette} from '../kit/Chrome';
import {ease} from '../kit/ease';
import {noise1} from '../kit/rng';
import {C, SAFE, SHAPE, T} from '../kit/tokens';
import events from './S2.events.json';
import {Bokeh, DIAMONDS, Ev, framesOf, HeadOutline, HEXES, HUB, lerp, Motes, mst, PAIRS, Pt, popEase, prog, rgba} from './S2.shared';

// ---------------------------------------------------------------------------------------------------------------------
// Sync: every timed visual below reads its frame from S2.events.json (Math.round(t * 30)).
// ---------------------------------------------------------------------------------------------------------------------
const EV = events as unknown as Ev[];
const one = (prefix: string) => framesOf(EV, prefix)[0];
const FD = framesOf(EV, 'Decision diamond'); // 8 diamonds
const FP = framesOf(EV, 'Trade-off pair'); // 6 pairs
const FH = framesOf(EV, 'Product hexagon'); // 8 hexagons
const F_EXH = one('Label Exhibit A');
const F_SD = one('Cluster Decisions');
const F_ST = one('Cluster Trade-offs');
const F_ANT = one('Anticipation');
const F_SNAP = one('Scar snap');
const F_SCAR = one('Scar: a notch');
const F_SP = one('Cluster Product');
const F_ALL = one('All of it');
const F_SEAL = one('Glass wall seals');
const F_HEADLBL = one('Label In your head');
const F_DRIFT = one('Nodes drift');
const F_CONV = F_DRIFT - 30;
const F_GLASS = F_ALL; // the glass wall starts closing with the `low`

// ---------------------------------------------------------------------------------------------------------------------
// Node indices: diamonds 0..7, pair circles 8..19 (A chosen = 8 + 2k, B unchosen = 9 + 2k), hexagons 20..27, hub 28.
// ---------------------------------------------------------------------------------------------------------------------
const HUB_I = 28;
const REST: Pt[] = [...DIAMONDS, ...PAIRS.flatMap((p) => [p.a, p.b]), ...HEXES, HUB];
const LIT: number[] = [...FD, ...PAIRS.flatMap((_, k) => [FP[k], FP[k]]), ...FH, 0];
const R_A = 16;
const R_B = 19;
const R_DIA = 20;
const R_HEX = 19;

const dist = (a: Pt, b: Pt) => Math.hypot(a[0] - b[0], a[1] - b[1]);
const nearestIn = (from: number, set: number[]) => set.reduce((best, i) => (dist(REST[i], REST[from]) < dist(REST[best], REST[from]) ? i : best), set[0]);
const IDX_D = Array.from({length: 8}, (_, i) => i);
const IDX_T = Array.from({length: 12}, (_, i) => 8 + i);
const IDX_H = Array.from({length: 8}, (_, i) => 20 + i);
const closestAcross = (s1: number[], s2: number[]): [number, number] => {
  let best: [number, number] = [s1[0], s2[0]];
  let bd = 1e9;
  for (const i of s1) for (const j of s2) {
    const d = dist(REST[i], REST[j]);
    if (d < bd) {
      bd = d;
      best = [i, j];
    }
  }
  return best;
};

type Edge = {a: number; b: number};
const EDGES: Edge[] = [];
mst(DIAMONDS).forEach(([i, j]) => EDGES.push({a: i, b: j}));
mst(HEXES).forEach(([i, j]) => EDGES.push({a: 20 + i, b: 20 + j}));
mst(PAIRS.map((p) => p.m)).forEach(([i, j]) => {
  const [a, b] = closestAcross([8 + 2 * i, 9 + 2 * i], [8 + 2 * j, 9 + 2 * j]);
  EDGES.push({a, b});
});
[IDX_D, IDX_T, IDX_H].forEach((set) => EDGES.push({a: HUB_I, b: nearestIn(HUB_I, set)}));
[[IDX_D, IDX_T], [IDX_T, IDX_H], [IDX_D, IDX_H]].forEach(([s1, s2]) => {
  const [a, b] = closestAcross(s1, s2);
  EDGES.push({a, b});
});

// The scar pair: close to the founder dot, so the camera push reads.
const SCAR = PAIRS.reduce((best, p, k) => (Math.abs(dist(p.m, HUB) - 120) < Math.abs(dist(PAIRS[best].m, HUB) - 120) ? k : best), 0);

const centroid = (pts: Pt[]): Pt => [pts.reduce((s, p) => s + p[0], 0) / pts.length, pts.reduce((s, p) => s + p[1], 0) / pts.length];
const C_D = centroid(DIAMONDS);
const C_T = centroid(PAIRS.flatMap((p) => [p.a, p.b]));
const C_H = centroid(HEXES);
const SCAR_MID = PAIRS[SCAR].m;

// ---------------------------------------------------------------------------------------------------------------------
// Bursts: all small sparkles (<= 24 particles). There is no big burst in S2.
// ---------------------------------------------------------------------------------------------------------------------
const SPARK_COLORS = [C.m500, C.m400, C.m300, C.white];
const FRAME_BOX = {x: 748, y: 252, w: 566, h: 644};
const BURSTS: Burst[] = [
  {f: F_SD, x: C_D[0], y: C_D[1], n: 18, seed: 11, speed: [1.2, 3.4], drag: 0.07, life: [24, 36], size: [4, 6], colors: SPARK_COLORS},
  {f: F_ST, x: C_T[0], y: C_T[1], n: 18, seed: 12, speed: [1.2, 3.4], drag: 0.07, life: [24, 36], size: [4, 6], colors: [C.pearl, C.white, C.m300, C.nickel]},
  {f: F_SNAP, x: SCAR_MID[0], y: SCAR_MID[1], n: 14, seed: 13, speed: [2, 5.5], drag: 0.09, life: [24, 34], size: [2, 3], colors: [C.m500, C.m300, C.white], shape: 'spark', trail: 3},
  {f: F_SP, x: C_H[0], y: C_H[1], n: 18, seed: 14, speed: [1.2, 3.4], drag: 0.07, life: [24, 36], size: [4, 6], colors: [C.nickel, C.pearl, C.white, C.m300]},
  {f: F_ALL, x: HUB[0], y: HUB[1], n: 22, seed: 15, speed: [2, 5], drag: 0.06, life: [26, 40], size: [4, 6], colors: [C.pearl, C.m300, C.nickel, C.white]},
  ...([[FRAME_BOX.x, FRAME_BOX.y, Math.PI, Math.PI * 1.5], [FRAME_BOX.x + FRAME_BOX.w, FRAME_BOX.y, Math.PI * 1.5, Math.PI * 2], [FRAME_BOX.x + FRAME_BOX.w, FRAME_BOX.y + FRAME_BOX.h, 0, Math.PI * 0.5], [FRAME_BOX.x, FRAME_BOX.y + FRAME_BOX.h, Math.PI * 0.5, Math.PI]] as [number, number, number, number][]).map(
    ([x, y, a0, a1], i): Burst => ({f: F_SEAL, x, y, n: 5, seed: 20 + i, speed: [1.5, 4], drag: 0.08, life: [24, 32], size: [2, 3], colors: [C.pearl, C.white, C.m300], angle: [a0, a1], shape: 'spark', trail: 3}),
  ),
];

// ---------------------------------------------------------------------------------------------------------------------
// Camera: pull-back from the founder dot, a slow push, a push-in on the scar, then a settle.
// ---------------------------------------------------------------------------------------------------------------------
const clampPan = (v: number) => Math.max(-120, Math.min(120, v));
const CAM_X = clampPan(0.55 * 1.11 * (SCAR_MID[0] - HUB[0]));
const CAM_Y = clampPan(0.55 * 1.11 * (SCAR_MID[1] - HUB[1]));
const CAM: CamKey[] = [
  {f: 0, zoom: 1.6, x: 0, y: 0, rot: 0.6},
  {f: 45, zoom: 1.0, rot: 0.35},
  {f: 112, zoom: 1.11, x: CAM_X, y: CAM_Y, rot: 0},
  {f: 142, zoom: 1.11, x: CAM_X, y: CAM_Y, rot: -0.15},
  {f: 186, zoom: 1.04, x: 0, y: 0, rot: -0.5},
  {f: 251, zoom: 1.0, rot: -0.2},
];

// ---------------------------------------------------------------------------------------------------------------------
// Pieces
// ---------------------------------------------------------------------------------------------------------------------
const hexPts = (r: number) => Array.from({length: 6}, (_, i) => `${(Math.cos((i * Math.PI) / 3) * r).toFixed(1)},${(Math.sin((i * Math.PI) / 3) * r).toFixed(1)}`).join(' ');
const diaPts = (r: number) => `0,${-r} ${r},0 0,${r} ${-r},0`;
const HEX_OUTER = hexPts(R_HEX);
const HEX_INNER = hexPts(R_HEX * 0.52);
const DIA = diaPts(R_DIA);

const Defs: React.FC = () => (
  <defs>
    {[
      ['gM', C.m400],
      ['gP', C.pearl],
      ['gN', C.nickel],
    ].map(([id, col]) => (
      <radialGradient key={id} id={`s2-${id}`}>
        <stop offset="0" stopColor={col} stopOpacity="0.5" />
        <stop offset="0.5" stopColor={col} stopOpacity="0.16" />
        <stop offset="1" stopColor={col} stopOpacity="0" />
      </radialGradient>
    ))}
    <radialGradient id="s2-cobalt">
      <stop offset="0" stopColor={C.cobalt} stopOpacity="0.62" />
      <stop offset="0.55" stopColor={C.cobalt} stopOpacity="0.24" />
      <stop offset="1" stopColor={C.cobalt} stopOpacity="0" />
    </radialGradient>
  </defs>
);

const CobaltGlow: React.FC = () => {
  const f = useCurrentFrame();
  const o = 0.3 + 0.55 * prog(f, 16, 110) + 0.05 * Math.sin(f / 23);
  return (
    <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
      <Defs />
      <circle cx={992} cy={575} r={560} fill="url(#s2-cobalt)" opacity={o} />
    </svg>
  );
};

/** Ring that expands from a node when it lights. */
const LightRing: React.FC<{p: Pt; t: number; color?: string; r0?: number; r1?: number; dur?: number}> = ({p, t, color = C.pearl, r0 = 14, r1 = 50, dur = 18}) => {
  if (t < 0 || t > dur) return null;
  const u = t / dur;
  return <circle cx={p[0]} cy={p[1]} r={lerp(r0, r1, ease.out(u))} fill="none" stroke={color} strokeWidth={2} opacity={0.6 * (1 - u)} />;
};

const MindMap: React.FC = () => {
  const f = useCurrentFrame();
  const conv = prog(f, F_CONV, 46, ease.inOut);
  const k = 1 - 0.3 * conv;

  // pair separation: spring-joined (circles start apart and snap together with a damped overshoot)
  const sepOf = (j: number) => {
    const Fc = FP[j] + 6;
    let s = 1.38;
    if (f >= Fc) {
      const u = (f - Fc) / 30;
      s = 1 + 0.38 * Math.exp(-6 * u) * Math.cos(14 * u);
    }
    s *= 1 + 0.032 * Math.sin(f / 17 + j * 1.7);
    if (j === SCAR) s *= 1 + 0.16 * prog(f, F_SNAP, 14, ease.out);
    return s;
  };

  const P: Pt[] = REST.map((rest, i) => {
    let base = rest;
    if (i >= 8 && i < 20) {
      const j = Math.floor((i - 8) / 2);
      const m = PAIRS[j].m;
      base = [m[0] + (rest[0] - m[0]) * sepOf(j), m[1] + (rest[1] - m[1]) * sepOf(j)];
    }
    const wx = i === HUB_I ? 0 : 2.2 * noise1(f / 55 + i * 1.7, 21 + i);
    const wy = i === HUB_I ? 0 : 2.2 * noise1(f / 61 + i * 2.3, 57 + i);
    return [HUB[0] + (base[0] - HUB[0]) * k + wx, HUB[1] + (base[1] - HUB[1]) * k + wy];
  });
  const nodeScale = 1 - 0.18 * conv;

  // glass wall
  const gp = prog(f, F_GLASS, 18, ease.out);
  const gs = 1.34 - 0.34 * gp;
  const gcx = FRAME_BOX.x + FRAME_BOX.w / 2;
  const gcy = FRAME_BOX.y + FRAME_BOX.h / 2;
  const sheen = prog(f, F_SEAL, 20, ease.inOut);
  const sheenX = -260 + (FRAME_BOX.w + 520) * sheen;

  const out: React.ReactNode[] = [];

  // --- edges (silver hairlines between and inside clusters)
  EDGES.forEach((e, i) => {
    const start = Math.max(LIT[e.a], LIT[e.b]) + 3;
    const p = prog(f, start, 16, ease.out);
    if (p <= 0) return;
    const len = dist(P[e.a], P[e.b]);
    out.push(<line key={`e${i}`} x1={P[e.a][0]} y1={P[e.a][1]} x2={P[e.b][0]} y2={P[e.b][1]} stroke={C.nickel} strokeWidth={2} opacity={0.5} strokeDasharray={len + 1} strokeDashoffset={(1 - p) * len} />);
  });

  // --- dormant ghosts (the field that is about to be lit)
  REST.forEach((_, i) => {
    if (i === HUB_I || f >= LIT[i]) return;
    const a = prog(f, 22 + (i % 9) * 3, 12, ease.out);
    out.push(<circle key={`g${i}`} cx={P[i][0]} cy={P[i][1]} r={3.6} fill={C.nickel} opacity={0.38 * a} />);
  });

  // --- decisions: diamonds
  DIAMONDS.forEach((_, i) => {
    const t = f - FD[i];
    if (t < 0) return;
    const s = popEase(Math.min(1, t / 12)) * nodeScale * (1 + 0.05 * Math.sin(f / 14 + i));
    const w = Math.max(0, 1 - t / 10);
    out.push(
      <g key={`d${i}`}>
        <circle cx={P[i][0]} cy={P[i][1]} r={46} fill="url(#s2-gM)" opacity={0.7 * Math.min(1, t / 8)} />
        <g transform={`translate(${P[i][0]} ${P[i][1]}) scale(${s})`}>
          <polygon points={DIA} fill={C.m500} />
          {w > 0 ? <polygon points={DIA} fill={C.white} opacity={w * 0.85} /> : null}
        </g>
        <LightRing p={P[i]} t={t} color={C.m300} />
      </g>,
    );
  });

  // --- trade-offs: spring-joined pairs
  PAIRS.forEach((_, j) => {
    const a = 8 + 2 * j;
    const b = 9 + 2 * j;
    const t = f - FP[j];
    if (t < 0) return;
    const s = popEase(Math.min(1, t / 11)) * nodeScale;
    const A = P[a];
    const B = P[b];
    const L = dist(A, B);
    const rB = R_B * (j === SCAR ? 1 + 0.38 * prog(f, F_SNAP, 12, ease.out) : 1); // the scarred circle settles larger
    const ux = (B[0] - A[0]) / L;
    const uy = (B[1] - A[1]) / L;
    const pA: Pt = [A[0] + ux * (R_A + 4), A[1] + uy * (R_A + 4)];
    const pB: Pt = [B[0] - ux * (rB + 4), B[1] - uy * (rB + 4)];
    const Fc = FP[j] + 6;
    const pe = prog(f, Fc, 14, ease.out);
    const parts: React.ReactNode[] = [];

    // dashed edge
    if (pe > 0) {
      const dash = '9 8';
      if (j === SCAR && f >= F_SNAP) {
        const u = prog(f, F_SNAP, 10, ease.out);
        const g0 = 0.5 - 0.36 * u;
        const g1 = 0.5 + 0.36 * u;
        const at = (q: number): Pt => [pA[0] + (pB[0] - pA[0]) * q, pA[1] + (pB[1] - pA[1]) * q];
        const e0 = at(g0);
        const e1 = at(g1);
        parts.push(<line key="s0" x1={pA[0]} y1={pA[1]} x2={e0[0]} y2={e0[1]} stroke={C.pearl} strokeWidth={2.5} strokeDasharray={dash} opacity={0.9} />);
        parts.push(<line key="s1" x1={e1[0]} y1={e1[1]} x2={pB[0]} y2={pB[1]} stroke={C.pearl} strokeWidth={2.5} strokeDasharray={dash} opacity={0.9} />);
      } else {
        const end: Pt = [pA[0] + (pB[0] - pA[0]) * pe, pA[1] + (pB[1] - pA[1]) * pe];
        parts.push(<line key="e" x1={pA[0]} y1={pA[1]} x2={end[0]} y2={end[1]} stroke={C.pearl} strokeWidth={2.5} strokeDasharray={dash} opacity={0.9} />);
      }
    }

    // circle A (the choice taken): solid
    parts.push(
      <g key="a" transform={`translate(${A[0]} ${A[1]}) scale(${s})`}>
        <circle r={R_A} fill={C.pearl} />
      </g>,
    );

    // circle B (the road not taken): hollow, with the scar after the snap
    const notch = j === SCAR && f > F_SNAP ? 72 * (Math.PI / 180) * ease.snap(prog(f, F_SNAP + 1, 6)) : 0;
    if (notch > 0.001) {
      const phi = Math.atan2(A[1] - B[1], A[0] - B[0]);
      const h = notch / 2;
      const r = rB;
      const p1: Pt = [B[0] + r * Math.cos(phi + h), B[1] + r * Math.sin(phi + h)];
      const p2: Pt = [B[0] + r * Math.cos(phi - h), B[1] + r * Math.sin(phi - h)];
      const tip: Pt = [B[0] + r * 0.46 * Math.cos(phi), B[1] + r * 0.46 * Math.sin(phi)];
      const arc = `M${p1[0].toFixed(1)} ${p1[1].toFixed(1)} A${r} ${r} 0 1 1 ${p2[0].toFixed(1)} ${p2[1].toFixed(1)}`;
      parts.push(<path key="bf" d={`${arc} L${tip[0].toFixed(1)} ${tip[1].toFixed(1)} Z`} fill={C.navy} />);
      parts.push(<path key="bs" d={arc} fill="none" stroke={C.pearl} strokeWidth={3} strokeLinecap="round" />);
      parts.push(<polyline key="bm" points={`${p2[0].toFixed(1)},${p2[1].toFixed(1)} ${tip[0].toFixed(1)},${tip[1].toFixed(1)} ${p1[0].toFixed(1)},${p1[1].toFixed(1)}`} fill="none" stroke={C.m400} strokeWidth={4.5} strokeLinejoin="round" strokeLinecap="round" />);
    } else {
      parts.push(
        <g key="b" transform={`translate(${B[0]} ${B[1]}) scale(${s})`}>
          <circle r={rB} fill={C.navy} stroke={C.pearl} strokeWidth={3} />
        </g>,
      );
    }
    out.push(
      <g key={`p${j}`}>
        <circle cx={(A[0] + B[0]) / 2} cy={(A[1] + B[1]) / 2} r={78} fill="url(#s2-gP)" opacity={0.55 * Math.min(1, t / 10)} />
        {parts}
        <LightRing p={A} t={t} />
        <LightRing p={B} t={t - 2} />
      </g>,
    );
  });

  // pre-snap pulses on the chosen pair
  if (f >= F_ANT && f < F_SNAP + 6) {
    const mid: Pt = [(P[8 + 2 * SCAR][0] + P[9 + 2 * SCAR][0]) / 2, (P[8 + 2 * SCAR][1] + P[9 + 2 * SCAR][1]) / 2];
    [0, 10].forEach((d, i) => {
      const t = f - F_ANT - d;
      if (t >= 0 && t < 18) out.push(<circle key={`ant${i}`} cx={mid[0]} cy={mid[1]} r={lerp(34, 92, ease.out(t / 18))} fill="none" stroke={C.m400} strokeWidth={2} opacity={0.65 * (1 - t / 18)} />);
    });
  }

  // --- product knowledge: hexagons
  HEXES.forEach((_, i) => {
    const idx = 20 + i;
    const t = f - FH[i];
    if (t < 0) return;
    const s = popEase(Math.min(1, t / 12)) * nodeScale * (1 + 0.045 * Math.sin(f / 16 + i * 1.3));
    const w = Math.max(0, 1 - t / 10);
    out.push(
      <g key={`h${i}`}>
        <circle cx={P[idx][0]} cy={P[idx][1]} r={46} fill="url(#s2-gN)" opacity={0.7 * Math.min(1, t / 8)} />
        <g transform={`translate(${P[idx][0]} ${P[idx][1]}) scale(${s})`}>
          <polygon points={HEX_OUTER} fill={C.nickel} />
          <polygon points={HEX_INNER} fill="none" stroke={C.navy} strokeWidth={2.5} opacity={0.55} />
          {w > 0 ? <polygon points={HEX_OUTER} fill={C.white} opacity={w * 0.8} /> : null}
        </g>
        <LightRing p={P[idx]} t={t} color={C.nickel} />
      </g>,
    );
  });

  // --- the founder dot (from S1) and its pulses at each beat
  out.push(
    <g key="hub">
      <circle cx={HUB[0]} cy={HUB[1]} r={50} fill="url(#s2-gM)" opacity={0.85} />
      {[F_SD, F_ST, F_SP].map((s0, i) => {
        const t = f - s0;
        if (t < 0 || t > 24) return null;
        return <circle key={i} cx={HUB[0]} cy={HUB[1]} r={lerp(12, 100, ease.out(t / 24))} fill="none" stroke={C.m400} strokeWidth={2} opacity={0.55 * (1 - t / 24)} />;
      })}
      {[0, 7].map((d, i) => {
        const t = f - F_ALL - d;
        if (t < 0 || t > 36) return null;
        return <circle key={`all${i}`} cx={HUB[0]} cy={HUB[1]} r={lerp(12, 190, ease.out(t / 36))} fill="none" stroke={i === 0 ? C.m400 : C.pearl} strokeWidth={2} opacity={0.6 * (1 - t / 36)} />;
      })}
      <circle cx={HUB[0]} cy={HUB[1]} r={12 * (1 + 0.08 * Math.sin(f / 12))} fill={C.m500} />
    </g>,
  );

  return (
    <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
      <Defs />
      <HeadOutline p={prog(f, 6, 44, ease.inOut)} />
      {out}
      {/* glass wall: closes around the head on "All of it" */}
      {gp > 0 ? (
        <g transform={`translate(${gcx} ${gcy}) scale(${gs}) translate(${-gcx} ${-gcy})`} opacity={gp}>
          <defs>
            <linearGradient id="s2-sheen" gradientUnits="userSpaceOnUse" x1={FRAME_BOX.x + sheenX - 120} y1={FRAME_BOX.y} x2={FRAME_BOX.x + sheenX + 120} y2={FRAME_BOX.y + FRAME_BOX.h * 0.4}>
              <stop offset="0" stopColor={C.white} stopOpacity="0" />
              <stop offset="0.5" stopColor={C.white} stopOpacity={sheen > 0 && sheen < 1 ? 0.13 : 0} />
              <stop offset="1" stopColor={C.white} stopOpacity="0" />
            </linearGradient>
          </defs>
          <rect x={FRAME_BOX.x} y={FRAME_BOX.y} width={FRAME_BOX.w} height={FRAME_BOX.h} rx={SHAPE.radiusPanel} fill={rgba(C.pearl, 0.04)} />
          <rect x={FRAME_BOX.x} y={FRAME_BOX.y} width={FRAME_BOX.w} height={FRAME_BOX.h} rx={SHAPE.radiusPanel} fill="url(#s2-sheen)" />
          <rect x={FRAME_BOX.x} y={FRAME_BOX.y} width={FRAME_BOX.w} height={FRAME_BOX.h} rx={SHAPE.radiusPanel} fill="none" stroke={C.pearl} strokeWidth={2} opacity={0.9} />
        </g>
      ) : null}
    </svg>
  );
};

// ---------------------------------------------------------------------------------------------------------------------
// HUD: pinned, never moved by the camera, so text is read at a constant size.
// ---------------------------------------------------------------------------------------------------------------------
type Glyph = 'd' | 't' | 'h' | 'g';
const GlyphIcon: React.FC<{g: Glyph}> = ({g}) => (
  <svg width={80} height={60} viewBox="0 0 80 60" style={{flexShrink: 0, marginTop: 4}}>
    {g === 'd' ? <polygon points={diaPts(24).replace(/(-?[\d.]+),(-?[\d.]+)/g, (_, x, y) => `${Number(x) + 40},${Number(y) + 30}`)} fill={C.m500} /> : null}
    {g === 't' ? (
      <>
        <circle cx={18} cy={30} r={14} fill={C.pearl} />
        <circle cx={60} cy={30} r={16} fill={C.navy} stroke={C.pearl} strokeWidth={3} />
        <line x1={36} y1={30} x2={42} y2={30} stroke={C.pearl} strokeWidth={3} />
      </>
    ) : null}
    {g === 'h' ? <polygon points={hexPts(26).replace(/(-?[\d.]+),(-?[\d.]+)/g, (_, x, y) => `${Number(x) + 40},${Number(y) + 30}`)} fill={C.nickel} /> : null}
    {g === 'g' ? <rect x={8} y={6} width={64} height={48} rx={10} fill="none" stroke={C.m400} strokeWidth={3.5} /> : null}
  </svg>
);

const LABELS: {text: string; g: Glyph; in: number; out: number; color: string}[] = [
  {text: 'Decisions', g: 'd', in: F_SD - 10, out: F_ST + 2, color: C.pearl},
  {text: 'Trade-offs', g: 't', in: F_ST + 4, out: F_SP - 2, color: C.pearl},
  {text: 'Product knowledge', g: 'h', in: F_SP, out: F_HEADLBL - 2, color: C.pearl},
  {text: 'In your head', g: 'g', in: F_HEADLBL, out: 99999, color: C.m400},
];

const Hud: React.FC = () => {
  const f = useCurrentFrame();
  const exh = prog(f, F_EXH - 3, 6);
  return (
    <>
      <div style={{position: 'absolute', left: SAFE.titleX, top: SAFE.titleTop, ...T.label, color: C.pearl, opacity: exh}}>
        <Marker at={F_EXH + 2}>Exhibit A</Marker>
      </div>
      {LABELS.map((l, i) => {
        const o = prog(f, l.in, 4) * (1 - prog(f, l.out - 6, 6));
        if (o <= 0) return null;
        return (
          <div key={l.text} style={{position: 'absolute', left: SAFE.titleX, top: 470, display: 'flex', alignItems: 'flex-start', gap: 26, opacity: o}}>
            <GlyphIcon g={l.g} />
            <div style={{...T.label, color: l.color, maxWidth: 560}}>
              <Scramble text={l.text} at={l.in} dur={12} seed={5 + i} />
            </div>
          </div>
        );
      })}
    </>
  );
};

export const S2: React.FC = () => (
  <AbsoluteFill style={{background: C.navy}}>
    <CameraRig keys={CAM} drift={4} seed={4}>
      <Layer depth={0.3}>
        <Motes seed={31} count={26} color={C.nickel} alpha={[0.1, 0.24]} size={[1.6, 3.6]} wander={36} />
      </Layer>
      <Layer depth={0.6}>
        <CobaltGlow />
        <Motes seed={47} count={18} color={C.pearl} alpha={[0.14, 0.3]} size={[1.8, 3.2]} wander={28} />
      </Layer>
      <Layer depth={1}>
        <MindMap />
        <Particles bursts={BURSTS} />
      </Layer>
      <Layer depth={1.6}>
        <Bokeh seed={63} count={6} idp="s2" colors={[C.pearl, C.m300]} alpha={[0.04, 0.075]} size={[40, 90]} wander={44} />
      </Layer>
    </CameraRig>
    <Vignette strength={0.42} />
    <Hud />
    <FictionalTag text="Illustrative · fictional founder" at={-10} />
  </AbsoluteFill>
);

