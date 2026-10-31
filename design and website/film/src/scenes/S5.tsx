import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {CameraRig, Layer, useCam, CamKey} from '../kit/Camera';
import {Particles, Burst} from '../kit/Particles';
import {Scramble} from '../kit/Type';
import {FictionalTag, Vignette} from '../kit/Chrome';
import {ease} from '../kit/ease';
import {headPoints} from '../kit/head';
import {mulberry32, noise1} from '../kit/rng';
import {C, SAFE, T} from '../kit/tokens';
import events from './S5.events.json';
import {Bokeh, Ev, framesOf, HEAD_D, hc, HUB, lerp, Motes, popEase, prog, Pt, rgba} from './S2.shared';

// ---------------------------------------------------------------------------------------------------------------------
// Sync: every timed visual reads its frame from S5.events.json (Math.round(t * 30)).
// ---------------------------------------------------------------------------------------------------------------------
const EV = events as unknown as Ev[];
const one = (prefix: string) => framesOf(EV, prefix)[0];
const F_FOUND = one('Founder disc');
const F_R1 = one('Team ring: first');
const F_R2 = framesOf(EV, 'Buyers ring: tick')[0];
const F_R3 = one('Partners ring starts');
const F_GLITCH = one('Partners ring: glitch');
const F_WAVE = one('One voice:');
const F_LABEL_END = one('Label One voice');
const F_LAND = one('Network lands');

const CX = HUB[0];
const CY = HUB[1];
const Z_END = 0.55;
const ROT_END = -2;
const LAND_DUR = 20;

// ---------------------------------------------------------------------------------------------------------------------
// Account network layout (seeded, baked once): founder + rings of 6, 14 and 28 abstract accounts.
// ---------------------------------------------------------------------------------------------------------------------
type Acct = {ring: number; x: number; y: number; r: number; kind: number; style: number; appear: number; parent: number; rot: number; ang: number};
const RINGS = [
  {n: 6, R: 215, r: 38, jr: 10, start: F_R1, step: 3},
  {n: 14, R: 405, r: 30, jr: 40, start: F_R2, step: 1.6},
  {n: 28, R: 600, r: 25, jr: 44, start: F_R3, step: 0.85},
];
const rnd = mulberry32(5055);
const ACCTS: Acct[] = [{ring: -1, x: CX, y: CY, r: 36, kind: 0, style: 0, appear: 0, parent: -1, rot: 0, ang: 0}];
const RING_IDX: number[][] = [[], [], []];
RINGS.forEach((rg, ri) => {
  const phase = ri * 0.41 + 0.2;
  for (let k = 0; k < rg.n; k++) {
    const ang = -Math.PI / 2 + phase + (2 * Math.PI * k) / rg.n + (rnd() - 0.5) * 0.3 * ((2 * Math.PI) / rg.n);
    const rad = rg.R + (rnd() - 0.5) * rg.jr;
    const order = (k * 5) % rg.n; // interleaved arrival, so rings fill like a network and not like a sweep
    RING_IDX[ri].push(ACCTS.length);
    ACCTS.push({ring: ri, x: CX + Math.cos(ang) * rad, y: CY + Math.sin(ang) * rad, r: rg.r, kind: (k + ri * 2) % 5, style: Math.floor(rnd() * 5), appear: Math.round(rg.start + order * rg.step), parent: 0, rot: Math.floor(rnd() * 4) * 90, ang});
  }
});
const dist2 = (a: {x: number; y: number}, b: {x: number; y: number}) => Math.hypot(a.x - b.x, a.y - b.y);
RING_IDX.forEach((idxs, ri) => {
  idxs.forEach((i) => {
    const pool = ri === 0 ? [0] : RING_IDX[ri - 1];
    ACCTS[i].parent = pool.reduce((best, j) => (dist2(ACCTS[j], ACCTS[i]) < dist2(ACCTS[best], ACCTS[i]) ? j : best), pool[0]);
  });
});

type Edge = {a: number; b: number; start: number; mesh: boolean};
const EDGES: Edge[] = [];
ACCTS.forEach((n, i) => {
  if (n.parent >= 0 && i > 0) EDGES.push({a: n.parent, b: i, start: Math.max(ACCTS[n.parent].appear, n.appear) + 2, mesh: false});
});
RING_IDX.forEach((idxs, ri) => {
  const byAng = [...idxs].sort((p, q) => ACCTS[p].ang - ACCTS[q].ang);
  const every = ri === 0 ? 1 : ri === 1 ? 2 : 3;
  byAng.forEach((i, k) => {
    if (k % every !== 0) return;
    const j = byAng[(k + 1) % byAng.length];
    EDGES.push({a: i, b: j, start: Math.max(ACCTS[i].appear, ACCTS[j].appear) + 6, mesh: true});
  });
});

// Landing: nodes ease onto points of the S2 head outline (pre-rotated so the camera roll cancels out).
const toWorld = (s: Pt): Pt => {
  const th = (-ROT_END * Math.PI) / 180;
  const dx = (s[0] - CX) / Z_END;
  const dy = (s[1] - CY) / Z_END;
  return [CX + dx * Math.cos(th) - dy * Math.sin(th), CY + dx * Math.sin(th) + dy * Math.cos(th)];
};
const TARGETS: Pt[] = headPoints(48).map(([x, y]) => toWorld(hc(x, y)));
const angOf = (p: Pt) => Math.atan2(p[1] - CY, p[0] - CX);
const LAND: Pt[] = [[CX, CY]];
{
  const nodes = ACCTS.map((a, i) => ({i, ang: Math.atan2(a.y - CY, a.x - CX)})).filter((o) => o.i > 0).sort((p, q) => p.ang - q.ang);
  const tg = [...TARGETS].sort((p, q) => angOf(p) - angOf(q));
  nodes.forEach((o, k) => {
    LAND[o.i] = tg[k];
  });
}
const LAND_DELAY = ACCTS.map((_, i) => (i * 37) % 9);
const HEAD_WORLD_D = (() => {
  const pts = HEAD_D.slice(1).split(' L').map((s) => s.split(' ').map(Number) as Pt);
  return 'M' + pts.map((p) => toWorld(p)).map(([x, y]) => `${x.toFixed(1)} ${y.toFixed(1)}`).join(' L');
})();

// The wave: linear from the founder, 28 frames to reach the outer ring; each account flashes when it hits.
const WAVE_DUR = 28;
const WAVE_R0 = 40;
const WAVE_R1 = 760;
const hitFrame = (i: number) => F_WAVE + Math.round((WAVE_DUR * Math.max(0, Math.hypot(ACCTS[i].x - CX, ACCTS[i].y - CY) - WAVE_R0)) / (WAVE_R1 - WAVE_R0));

// ---------------------------------------------------------------------------------------------------------------------
// Bursts. P3 shards (the one big burst of this scene): 3 per account + 18 at the founder = 162 in all, <= 220.
// The canvas covers a world area K times larger than the frame, because the network reaches beyond the 1920 x 1080 box.
// ---------------------------------------------------------------------------------------------------------------------
const K = 1.8;
const toBitmap = (x: number, y: number): [number, number] => [CX + (x - CX) / K, CY + (y - CY) / K];
const SHARD_COLORS = [C.m500, C.m400, C.m300, C.white];
const sparkAt = (f: number, x: number, y: number, n: number, seed: number, colors: string[], speed: [number, number] = [1.2, 3.2]): Burst => {
  const [bx, by] = toBitmap(x, y);
  return {f, x: bx, y: by, n, seed, speed, drag: 0.08, life: [24, 30], size: [2, 3.2], colors, shape: 'spark', trail: 3};
};
const BURSTS: Burst[] = [
  // the founder's first signal: ten sparks leave toward ring 1
  sparkAt(one('Signal'), CX, CY, 10, 501, [C.m500, C.m300, C.white], [1.6, 3.4]),
  // the wave
  sparkAt(F_WAVE, CX, CY, 18, 502, SHARD_COLORS, [1.8, 4.2]),
  ...ACCTS.map((_, i) => i)
    .filter((i) => i > 0)
    .map((i) => sparkAt(hitFrame(i), ACCTS[i].x, ACCTS[i].y, 3, 600 + i, SHARD_COLORS)),
  // small pings as each account arrives (3 dots each)
  ...ACCTS.map((_, i) => i)
    .filter((i) => i > 0)
    .map((i): Burst => {
      const [bx, by] = toBitmap(ACCTS[i].x, ACCTS[i].y);
      return {f: ACCTS[i].appear, x: bx, y: by, n: 3, seed: 900 + i, speed: [0.6, 1.8], drag: 0.09, life: [24, 32], size: [3, 5], colors: [C.pearl, C.white, C.m300]};
    }),
];

// ---------------------------------------------------------------------------------------------------------------------
// Camera: hold for the first ripples, then one 150-frame pull-back from 1.0 to 0.55 with a 2 degree roll.
// ---------------------------------------------------------------------------------------------------------------------
const CAM: CamKey[] = [
  {f: 0, zoom: 1, rot: 0, x: 0, y: 0},
  {f: 60, zoom: 1, rot: 0},
  {f: 210, zoom: Z_END, rot: ROT_END},
  {f: 251, zoom: Z_END, rot: ROT_END},
];

// ---------------------------------------------------------------------------------------------------------------------
// Pieces
// ---------------------------------------------------------------------------------------------------------------------
const STYLES: {fill: string; rim: string | null}[] = [
  {fill: C.pearl, rim: null},
  {fill: C.nickel, rim: null},
  {fill: C.cobalt, rim: C.pearl},
  {fill: C.navy, rim: C.nickel},
  {fill: C.pearl, rim: C.cobalt},
];

const Avatar: React.FC<{kind: number; style: number; r: number; rot: number; override?: string}> = ({kind, style, r, rot, override}) => {
  const st = STYLES[style];
  const fill = override ?? st.fill;
  const rim = override ? null : st.rim;
  const rimProps = rim ? {stroke: rim, strokeWidth: 3.5} : {};
  switch (kind) {
    case 0:
      return <circle r={r} fill={fill} {...rimProps} />;
    case 1:
      return <rect x={-r} y={-r} width={2 * r} height={2 * r} rx={r * 0.32} fill={fill} {...rimProps} />;
    case 2:
      return <path d={`M${-r} 0 A${r} ${r} 0 0 1 ${r} 0 Z`} fill={fill} transform={`rotate(${rot})`} {...rimProps} />;
    case 3:
      return <circle r={r * 0.82} fill="none" stroke={override ?? (st.fill === C.cobalt ? C.pearl : st.fill === C.navy ? (st.rim as string) : st.fill)} strokeWidth={r * 0.34} />;
    default:
      return <rect x={-r * 0.6} y={-r} width={r * 1.2} height={2 * r} rx={r * 0.6} fill={fill} {...rimProps} />;
  }
};

const Defs: React.FC = () => (
  <defs>
    <radialGradient id="s5-gM">
      <stop offset="0" stopColor={C.m400} stopOpacity="0.55" />
      <stop offset="0.5" stopColor={C.m400} stopOpacity="0.16" />
      <stop offset="1" stopColor={C.m400} stopOpacity="0" />
    </radialGradient>
    <radialGradient id="s5-cobalt">
      <stop offset="0" stopColor={C.cobalt} stopOpacity="0.55" />
      <stop offset="0.5" stopColor={C.cobalt} stopOpacity="0.22" />
      <stop offset="1" stopColor={C.cobalt} stopOpacity="0" />
    </radialGradient>
  </defs>
);

/** Far layer (depth 0.35): soft cobalt glow, faint concentric rings and slow dust. */
const FarLayer: React.FC = () => {
  const f = useCurrentFrame();
  const cam = useCam();
  const sc = 1 + (cam.zoom - 1) * 0.35;
  const o = 0.5 + 0.5 * prog(f, 0, 60);
  return (
    <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
      <Defs />
      <circle cx={CX} cy={CY} r={1250} fill="url(#s5-cobalt)" opacity={0.5 * o} />
      {[520, 820, 1150, 1500, 1900].map((r, i) => (
        <circle key={i} cx={CX} cy={CY} r={r} fill="none" stroke={C.nickel} strokeWidth={2 / sc} opacity={0.17 - i * 0.02} />
      ))}
    </svg>
  );
};

/** Mid layer (depth 0.6): ghost accounts beyond the visible network, joined by very faint threads. */
const GHOSTS: {x: number; y: number; r: number; kind: number; a: number}[] = (() => {
  const r = mulberry32(8080);
  return Array.from({length: 38}, (_, i) => {
    const ang = (i / 38) * Math.PI * 2 + (r() - 0.5) * 0.3;
    const rad = 820 + r() * 900;
    return {x: CX + Math.cos(ang) * rad, y: CY + Math.sin(ang) * rad * 0.82, r: 16 + r() * 14, kind: Math.floor(r() * 5), a: 0.14 + r() * 0.12};
  });
})();
const GHOST_LINKS: [number, number][] = GHOSTS.map((g, i) => {
  let best = (i + 1) % GHOSTS.length;
  GHOSTS.forEach((h, j) => {
    if (j !== i && Math.hypot(h.x - g.x, h.y - g.y) < Math.hypot(GHOSTS[best].x - g.x, GHOSTS[best].y - g.y)) best = j;
  });
  return [i, best];
});
const GhostLayer: React.FC = () => {
  const f = useCurrentFrame();
  const cam = useCam();
  const sc = 1 + (cam.zoom - 1) * 0.6;
  const o = prog(f, 40, 150, ease.inOut);
  return (
    <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}} opacity={o}>
      {GHOST_LINKS.map(([a, b], i) => (
        <line key={i} x1={GHOSTS[a].x} y1={GHOSTS[a].y} x2={GHOSTS[b].x} y2={GHOSTS[b].y} stroke={C.nickel} strokeWidth={2 / sc} opacity={0.14} />
      ))}
      {GHOSTS.map((g, i) => (
        <g key={i} transform={`translate(${g.x + 10 * noise1(f / 90 + i, 3 + i)} ${g.y + 10 * noise1(f / 100 + i * 2, 17 + i)})`} opacity={g.a / 0.26}>
          <g opacity={0.9}>
            <Avatar kind={g.kind} style={1} r={g.r} rot={0} override={C.nickel} />
          </g>
        </g>
      ))}
    </svg>
  );
};

const Network: React.FC = () => {
  const f = useCurrentFrame();
  const cam = useCam();
  const z = cam.zoom;
  const hair = 2 / z; // 2 px non-scaling strokes
  const landP = (i: number) => prog(f, F_LAND + LAND_DELAY[i], LAND_DUR, ease.inOut);
  const landFade = prog(f, F_LAND - 4, 14);

  const P: Pt[] = ACCTS.map((a, i) => {
    if (i === 0) return [CX, CY];
    const bob = 1 - landP(i);
    const bx = a.x + 3.2 * noise1(f / 70 + i * 1.3, 11 + i) * bob;
    const by = a.y + 3.2 * noise1(f / 77 + i * 1.9, 41 + i) * bob;
    const lp = landP(i);
    return [lerp(bx, LAND[i][0], lp), lerp(by, LAND[i][1], lp)];
  });
  const hit = ACCTS.map((_, i) => (i === 0 ? F_WAVE : hitFrame(i)));

  // ---- ripples from the founder: every 14 frames, the first is marigold
  const ripples: React.ReactNode[] = [];
  const grads: React.ReactNode[] = [];
  for (let k = 0; k < 14; k++) {
    const s0 = F_FOUND + 14 * k;
    const u = (f - s0) / 54;
    if (u < 0 || u > 1) continue;
    const R = 40 + 760 * ease.out(u);
    const a = Math.pow(1 - u, 1.4);
    const id = `s5-rg${k}`;
    const inner = Math.max(0, (R - 30) / (R + 34));
    grads.push(
      <radialGradient key={id} id={id} gradientUnits="userSpaceOnUse" cx={CX} cy={CY} r={R + 34}>
        <stop offset={inner} stopColor={C.cobalt} stopOpacity="0" />
        <stop offset={Math.min(0.985, (R + 2) / (R + 34))} stopColor={C.cobalt} stopOpacity="0.34" />
        <stop offset="1" stopColor={C.cobalt} stopOpacity="0" />
      </radialGradient>,
    );
    ripples.push(<circle key={`rb${k}`} cx={CX} cy={CY} r={R + 34} fill={`url(#${id})`} opacity={a} />);
    ripples.push(<circle key={`rc${k}`} cx={CX} cy={CY} r={R} fill="none" stroke={k === 0 ? C.m400 : C.pearl} strokeWidth={hair} opacity={(k === 0 ? 0.95 : 0.4) * a} />);
  }
  const lastSpawn = Math.max(0, Math.floor((f - F_FOUND) / 14));
  const pulse = 1 + 0.12 * Math.max(0, 1 - ((f - F_FOUND) % 14) / 8) * (lastSpawn < 14 ? 1 : 0);

  // ---- wave
  const wu = (f - F_WAVE) / WAVE_DUR;
  const waveR = WAVE_R0 + (WAVE_R1 - WAVE_R0) * Math.min(1, Math.max(0, wu));
  const wavePieces: React.ReactNode[] = [];
  if (wu >= 0 && wu <= 1.25) {
    const a = 1 - Math.max(0, wu - 0.8) / 0.45;
    grads.push(
      <radialGradient key="s5-wg" id="s5-wg" gradientUnits="userSpaceOnUse" cx={CX} cy={CY} r={waveR + 70}>
        <stop offset={Math.max(0, (waveR - 60) / (waveR + 70))} stopColor={C.m300} stopOpacity="0" />
        <stop offset={Math.min(0.98, (waveR + 4) / (waveR + 70))} stopColor={C.m300} stopOpacity="0.4" />
        <stop offset="1" stopColor={C.m300} stopOpacity="0" />
      </radialGradient>,
    );
    wavePieces.push(<circle key="wb" cx={CX} cy={CY} r={waveR + 70} fill="url(#s5-wg)" opacity={a} />);
    wavePieces.push(<circle key="wc" cx={CX} cy={CY} r={waveR} fill="none" stroke={C.m400} strokeWidth={3.6 / z} opacity={a * 0.95} />);
  }

  const out: React.ReactNode[] = [];

  // ---- edges (draw with stroke-dashoffset, 14 f) with a short spark trail while drawing
  EDGES.forEach((e, i) => {
    const p = prog(f, e.start, 14, ease.out);
    if (p <= 0) return;
    const A = P[e.a];
    const B = P[e.b];
    const len = Math.hypot(B[0] - A[0], B[1] - A[1]);
    const base = (e.mesh ? 0.32 : 0.55) * (1 - landFade);
    out.push(<line key={`e${i}`} x1={A[0]} y1={A[1]} x2={B[0]} y2={B[1]} stroke={C.nickel} strokeWidth={hair} opacity={base} strokeDasharray={len + 1} strokeDashoffset={(1 - p) * len} />);
    if (p < 1) {
      const tip: Pt = [lerp(A[0], B[0], p), lerp(A[1], B[1], p)];
      const back = Math.min(0.3, 34 / Math.max(1, len));
      const tail: Pt = [lerp(A[0], B[0], Math.max(0, p - back)), lerp(A[1], B[1], Math.max(0, p - back))];
      out.push(<line key={`tr${i}`} x1={tail[0]} y1={tail[1]} x2={tip[0]} y2={tip[1]} stroke={C.m300} strokeWidth={9 / z} strokeLinecap="round" opacity={0.3} />);
      out.push(<line key={`tc${i}`} x1={tail[0]} y1={tail[1]} x2={tip[0]} y2={tip[1]} stroke={C.m300} strokeWidth={3.4 / z} strokeLinecap="round" opacity={0.95} />);
    } else if (!e.mesh && f >= hit[e.b] && f < hit[e.b] + 14) {
      // the wave passes: the edge lights up in marigold for a moment
      const t = (f - hit[e.b]) / 14;
      out.push(<line key={`ew${i}`} x1={A[0]} y1={A[1]} x2={B[0]} y2={B[1]} stroke={C.m400} strokeWidth={3.5 / z} opacity={0.8 * (1 - t)} />);
    }
  });

  // ---- message packets: pearl dots that keep travelling along a few finished edges (keeps the middle of the scene moving)
  EDGES.forEach((e, i) => {
    if (e.mesh || ACCTS[e.b].ring !== 2 || i % 3 !== 0) return;
    const done = f - (e.start + 14);
    if (done < 0 || landFade >= 1) return;
    const q = ((done + (i % 7) * 9) % 62) / 62;
    const A = P[e.a];
    const B = P[e.b];
    out.push(<circle key={`pk${i}`} cx={lerp(A[0], B[0], q)} cy={lerp(A[1], B[1], q)} r={4.5} fill={C.pearl} opacity={0.75 * (1 - landFade)} />);
  });

  // ---- accounts, by ring (ring 3 takes the 2-frame glitch offset)
  const gl = f === F_GLITCH ? 8 : f === F_GLITCH + 1 ? -8 : 0;
  [0, 1, 2].forEach((ri) => {
    const nodes: React.ReactNode[] = [];
    RING_IDX[ri].forEach((i) => {
      const a = ACCTS[i];
      const t = f - a.appear;
      if (t < 0) return;
      const lp = landP(i);
      const s = popEase(Math.min(1, t / 12)) * (1 - 0.38 * lp);
      const th = f - hit[i];
      const wv = th >= 0 && th < 14 ? 1 - th / 14 : 0; // scale pulse and halo
      const wFill = th >= 0 && th < 9 ? (th < 6 ? 1 : 1 - (th - 6) / 3) : 0; // marigold fill, short and saturated
      const arrive = t < 11 ? (t < 6 ? 1 : 1 - (t - 6) / 5) : 0;
      nodes.push(
        <g key={`n${i}`}>
          <g transform={`translate(${P[i][0]} ${P[i][1]}) scale(${s * (1 + 0.22 * wv)})`}>
            <Avatar kind={a.kind} style={a.style} r={a.r} rot={a.rot} />
            {arrive > 0 ? <Avatar kind={a.kind} style={a.style} r={a.r} rot={a.rot} override={C.m500} /> : null}
          </g>
          {arrive > 0 ? <circle cx={P[i][0]} cy={P[i][1]} r={a.r * 3.6} fill="url(#s5-gM)" opacity={arrive * 0.85} /> : null}
          {wFill > 0 ? (
            <g transform={`translate(${P[i][0]} ${P[i][1]}) scale(${s * (1 + 0.22 * wv)})`} opacity={wFill}>
              <Avatar kind={a.kind} style={a.style} r={a.r} rot={a.rot} override={C.m500} />
            </g>
          ) : null}
          {wv > 0 ? <circle cx={P[i][0]} cy={P[i][1]} r={a.r * (1.3 + 1.3 * (1 - wv))} fill="none" stroke={C.m400} strokeWidth={3 / z} opacity={0.8 * wv} /> : null}
          {t < 18 ? <circle cx={P[i][0]} cy={P[i][1]} r={lerp(a.r, a.r * 2.6, ease.out(t / 18))} fill="none" stroke={C.pearl} strokeWidth={hair} opacity={0.55 * (1 - t / 18)} /> : null}
        </g>,
      );
    });
    out.push(
      <g key={`ring${ri}`} transform={ri === 2 && gl !== 0 ? `translate(${gl} 0)` : undefined}>
        {nodes}
      </g>,
    );
  });

  // ---- the head outline, drawn behind the landing mesh
  const outlineA = prog(f, F_LAND + 4, 20, ease.out);

  // ---- founder disc (the S4 avatar): pearl disc with a marigold rim; it relaxes into the small marigold dot of S2
  const fl = prog(f, F_LAND, 24, ease.inOut);
  const fr = lerp(36, 22, fl);

  return (
    <svg width={1920} height={1080} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
      <Defs />
      <defs>{grads}</defs>
      {ripples}
      {wavePieces.slice(0, 1)}
      <path d={HEAD_WORLD_D} fill="none" stroke={C.nickel} strokeWidth={hair} strokeLinecap="round" strokeLinejoin="round" opacity={0.75 * outlineA} />
      {out}
      <g>
        <circle cx={CX} cy={CY} r={130 * pulse} fill="url(#s5-gM)" opacity={0.85 - 0.35 * fl} />
        <circle cx={CX} cy={CY} r={fr} fill={C.pearl} opacity={1 - fl} />
        <circle cx={CX} cy={CY} r={fr} fill={C.m500} opacity={fl} />
        <circle cx={CX} cy={CY} r={fr} fill="none" stroke={C.m500} strokeWidth={4.5} />
      </g>
      {wavePieces.slice(1)}
    </svg>
  );
};

// ---------------------------------------------------------------------------------------------------------------------
// HUD: pinned labels (one at a time) with a small ring-index icon.
// ---------------------------------------------------------------------------------------------------------------------
const RingIcon: React.FC<{active: number}> = ({active}) => (
  <svg width={80} height={64} viewBox="0 0 80 64" style={{flexShrink: 0, marginTop: 2}}>
    {[11, 21, 31].map((r, i) => {
      const on = active === i + 1;
      const all = active === 4;
      return <circle key={r} cx={40} cy={32} r={r} fill="none" stroke={on ? C.m400 : all ? C.pearl : C.nickel} strokeWidth={on ? 4 : 2.5} opacity={on || all ? 1 : 0.5} />;
    })}
    <circle cx={40} cy={32} r={6} fill={C.m500} />
  </svg>
);

const LABELS: {text: string; ring: number; in: number; out: number; dur: number; color: string}[] = [
  {text: 'From you', ring: 0, in: F_FOUND + 28, out: F_R1 - 2, dur: 10, color: C.pearl},
  {text: 'Team', ring: 1, in: F_R1 - 2, out: F_R2 - 6, dur: 8, color: C.pearl},
  {text: 'Buyers (illustrative)', ring: 2, in: F_R2 - 6, out: F_R3 - 2, dur: 10, color: C.pearl},
  {text: 'Partners', ring: 3, in: F_R3 - 2, out: F_LABEL_END, dur: 10, color: C.pearl},
  {text: 'One voice, many accounts', ring: 4, in: F_LABEL_END, out: 99999, dur: 12, color: C.m400},
];

const Hud: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <>
      {LABELS.map((l, i) => {
        const o = prog(f, l.in, 4) * (1 - prog(f, l.out - 6, 6));
        if (o <= 0) return null;
        return (
          <div key={l.text} style={{position: 'absolute', left: SAFE.titleX, top: SAFE.titleTop, display: 'flex', alignItems: 'flex-start', gap: 26, opacity: o}}>
            <RingIcon active={l.ring} />
            <div style={{...T.label, color: l.color, whiteSpace: 'nowrap'}}>
              <Scramble text={l.text} at={l.in} dur={l.dur} seed={9 + i} />
            </div>
          </div>
        );
      })}
    </>
  );
};

export const S5: React.FC = () => (
  <AbsoluteFill style={{background: C.navy}}>
    <CameraRig keys={CAM} drift={3} seed={9}>
      <Layer depth={0.35}>
        <FarLayer />
        <Motes seed={81} count={34} color={C.nickel} alpha={[0.1, 0.22]} size={[2, 4]} wander={40} area={[-900, -600, 2800, 1700]} />
      </Layer>
      <Layer depth={0.6}>
        <GhostLayer />
      </Layer>
      <Layer depth={1}>
        <Network />
        <div style={{position: 'absolute', left: 0, top: 0, width: 1920, height: 1080, transformOrigin: '0 0', transform: `translate(${CX - CX * K}px, ${CY - CY * K}px) scale(${K})`}}>
          <Particles bursts={BURSTS} />
        </div>
      </Layer>
      <Layer depth={1.35}>
        <Bokeh seed={91} count={9} idp="s5" colors={[C.pearl, C.m300]} alpha={[0.05, 0.1]} size={[60, 140]} area={[-1800, -1000, 3700, 2100]} wander={60} />
      </Layer>
    </CameraRig>
    <Vignette strength={0.4} />
    <div style={{position: 'absolute', left: 0, top: 0, width: 1920, height: 250, background: `linear-gradient(180deg, ${rgba(C.navy, 0.92)} 0%, ${rgba(C.navy, 0.55)} 55%, ${rgba(C.navy, 0)} 100%)`, pointerEvents: 'none'}} />
    <div style={{position: 'absolute', left: 0, bottom: 0, width: 1920, height: 210, background: `linear-gradient(0deg, ${rgba(C.navy, 0.94)} 0%, ${rgba(C.navy, 0.6)} 55%, ${rgba(C.navy, 0)} 100%)`, pointerEvents: 'none'}} />
    <Hud />
    <FictionalTag text="Illustrative accounts · not a result" at={-10} />
  </AbsoluteFill>
);
