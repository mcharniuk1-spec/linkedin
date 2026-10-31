import React from 'react';
import {AbsoluteFill, interpolateColors, useCurrentFrame} from 'remotion';
import {CamKey, CameraRig, Layer} from '../kit/Camera';
import {FictionalTag, Marker, Vignette} from '../kit/Chrome';
import {ease} from '../kit/ease';
import {HEAD_PATH, insideHead} from '../kit/head';
import {Burst, Particles} from '../kit/Particles';
import {mulberry32} from '../kit/rng';
import {Scramble, Words} from '../kit/Type';
import {C, SAFE, T} from '../kit/tokens';
import events from './S7.events.json';
import {closedSplinePath, Dust, evFrame, lerp, pr, ringNoise, seededRing} from './S7.S8.shared';

/**
 * S7 The Verdict. A 7 x 7 grid of identical nickel discs; one of them breaks into a unique marigold spline,
 * glides to the centre of the stage and carries a tiny callback of the S2 head map. Text left, stage right.
 */

// ---------- sync frames (from S7.events.json) ----------
const F = {
  grid: evFrame(events, 'sparkle', 0),
  label: evFrame(events, 'tick', 0),
  h1: evFrame(events, 'tick', 1),
  riser: evFrame(events, 'riser', 0),
  lock: evFrame(events, 'tick', 2),
  boom: evFrame(events, 'boom', 0),
  glide: evFrame(events, 'whoosh', 0),
  arrive: evFrame(events, 'sparkle', 2),
  diamonds: evFrame(events, 'tick', 3),
  pairs: evFrame(events, 'tick', 4),
  hexes: evFrame(events, 'tick', 5),
  low: evFrame(events, 'low', 0),
  h4: evFrame(events, 'tick', 6),
  marker: evFrame(events, 'sparkle', 3),
};
const F_MORPH = F.boom - 3;
const GLIDE_LEN = 54;

// ---------- geometry ----------
const BC = {x: 1460, y: 450}; // stage centre (right half); the text column is left
const PITCH = 74;
const DISC_R = 22;
const BLOB_R = 215;
const BLOB_N = 64;
const CHOSEN = {c: 5, r: 1}; // upper right of the grid, so the glide has somewhere to go

type Disc = {i: number; x: number; y: number; dist: number; chosen: boolean};
const DISCS: Disc[] = Array.from({length: 49}, (_, i) => {
  const c = i % 7;
  const r = Math.floor(i / 7);
  return {i, x: BC.x + (c - 3) * PITCH, y: BC.y + (r - 3) * PITCH, dist: Math.hypot(c - 3, r - 3), chosen: c === CHOSEN.c && r === CHOSEN.r};
});
const CHOSEN_DISC = DISCS.find((d) => d.chosen)!;

const RING_A = seededRing(31, 5);
const RING_B = seededRing(47, 6);
const blobPoints = (f: number, cx: number, cy: number, R: number, amp: number): [number, number][] =>
  Array.from({length: BLOB_N}, (_, i) => {
    const u = i / BLOB_N;
    const n = Math.max(-1, Math.min(1, 1.35 * (0.66 * ringNoise(RING_A, u + 0.0011 * f) + 0.34 * ringNoise(RING_B, u - 0.0016 * f))));
    const r = R * (1 + amp * n);
    const th = u * Math.PI * 2 - Math.PI / 2;
    return [cx + Math.cos(th) * r, cy + Math.sin(th) * r];
  });

// ---------- tiny S2 head-map callback ----------
const HS = 0.34; // head box (800 x 900) to px
const hx = (x: number) => BC.x + (x - 430) * HS;
const hy = (y: number) => BC.y + (y - 480) * HS;
const HEAD_SCREEN = HEAD_PATH.replace(/(-?\d+\.?\d*) (-?\d+\.?\d*)/g, (_m, x: string, y: string) => `${hx(Number(x)).toFixed(1)} ${hy(Number(y)).toFixed(1)}`);

type HNode = {x: number; y: number; kind: 'd' | 'p' | 'h'; j: number};
const HEAD_NODES: HNode[] = (() => {
  const rnd = mulberry32(2026);
  const pts: [number, number][] = [];
  let guard = 0;
  while (pts.length < 22 && guard < 9000) {
    guard++;
    const minD = guard < 3500 ? 118 : guard < 6000 ? 105 : 90;
    const x = 170 + rnd() * 540;
    const y = 130 + rnd() * 580;
    const ok = [[0, 0], [52, 0], [-52, 0], [0, 52], [0, -52]].every(([dx, dy]) => insideHead(x + dx, y + dy));
    if (!ok || pts.some(([px, py]) => Math.hypot(px - x, py - y) < minD)) continue;
    pts.push([x, y]);
  }
  pts.sort((a, b) => a[1] - b[1]);
  const group = (from: number, to: number, kind: 'd' | 'p' | 'h') =>
    pts.slice(from, to).sort((a, b) => a[0] - b[0]).map(([x, y], j) => ({x: hx(x), y: hy(y), kind, j}));
  return [...group(0, 8, 'd'), ...group(8, 14, 'p'), ...group(14, 22, 'h')];
})();
const nearest = (n: HNode, kind: 'd' | 'p' | 'h') =>
  HEAD_NODES.filter((m) => m.kind === kind).reduce((best, m) => (Math.hypot(m.x - n.x, m.y - n.y) < Math.hypot(best.x - n.x, best.y - n.y) ? m : best));
const HEAD_LINKS: [HNode, HNode][] = [
  ...HEAD_NODES.filter((n) => n.kind === 'p').map((n) => [n, nearest(n, 'd')] as [HNode, HNode]),
  ...HEAD_NODES.filter((n) => n.kind === 'h').map((n) => [n, nearest(n, 'p')] as [HNode, HNode]),
];

// ---------- bursts (small: this is not one of the film's big explosions) ----------
const WARM = [C.m500, C.m400, C.m300, C.white];
const BURSTS: Burst[] = [
  {f: F.boom, x: CHOSEN_DISC.x, y: CHOSEN_DISC.y, n: 64, seed: 71, speed: [4, 13], drag: 0.07, life: [26, 44], size: [2, 4.2], colors: WARM},
  {f: F.boom, x: CHOSEN_DISC.x, y: CHOSEN_DISC.y, n: 16, seed: 72, speed: [5, 11], drag: 0.09, life: [18, 30], size: [1.6, 2.4], colors: [C.m300, C.white], shape: 'spark', trail: 3},
  {f: F.arrive, x: BC.x, y: BC.y, n: 110, seed: 73, speed: [26, 44], drag: 0.1, life: [30, 48], size: [2, 3.8], colors: [C.m400, C.m300, C.white, C.m500]},
];

const KEYS: CamKey[] = [
  {f: 0, zoom: 1.0, x: 0, y: 0, rot: 0},
  {f: 100, zoom: 1.08, x: -8, y: -4, rot: 0.2},
  {f: 108, zoom: 1.14, x: -10, y: -4, rot: 0.2}, // punch with the morph
  {f: 126, zoom: 1.1, x: -14, y: -6, rot: 0},
  {f: 200, zoom: 1.12, x: -20, y: -8, rot: -0.3},
  {f: 286, zoom: 1.15, x: -26, y: -10, rot: -0.5},
];

// ---------- stage ----------
const Stage: React.FC = () => {
  const f = useCurrentFrame();

  const popP = pr(f, F_MORPH, F_MORPH + 10, ease.out);
  const morphP = pr(f, F_MORPH, F_MORPH + 24, ease.out);
  const glideP = pr(f, F.glide, F.glide + GLIDE_LEN, ease.cam);
  const breathe = Math.sin(Math.PI * pr(f, F.low, F.low + 36, ease.inOut));
  const R0 = DISC_R + 9 * popP;
  const R = (R0 + (BLOB_R - R0) * glideP) * (1 + 0.035 * breathe);
  const cx = lerp(CHOSEN_DISC.x, BC.x, glideP);
  const cy = lerp(CHOSEN_DISC.y, BC.y, glideP);
  const blobOn = f >= F_MORPH;
  const dimP = pr(f, F.boom, F.boom + 22, ease.inOut);
  const blobFill = interpolateColors(pr(f, F_MORPH, F_MORPH + 12, ease.out), [0, 1], [C.nickel, C.m500]);

  const scanOn = f >= F.riser && f < F.lock + 12;
  const scanX = lerp(BC.x - 3 * PITCH - 70, CHOSEN_DISC.x + 20, pr(f, F.riser, F.lock, ease.inOut));
  const lockP = pr(f, F.lock, F.boom, ease.out);
  const lockA = lockP * (1 - pr(f, F.boom, F.boom + 3, ease.out));
  const ringU = pr(f, F.boom, F.boom + 26, ease.out);
  const arriveU = pr(f, F.arrive, F.arrive + 34, ease.out);
  const glowA = 0.4 * pr(f, F_MORPH, F_MORPH + 20, ease.out) * (1 + 0.25 * breathe);

  // head callback
  const outlineP = pr(f, F.arrive, F.arrive + 24, ease.out);
  const startOf = (n: HNode) => (n.kind === 'd' ? F.diamonds + n.j * 2 : n.kind === 'p' ? F.pairs + n.j * 3 : F.hexes + n.j * 2);

  return (
    <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
      <defs>
        <radialGradient id="s7glow">
          <stop offset="0" stopColor={C.m500} stopOpacity={1} />
          <stop offset="0.55" stopColor={C.m500} stopOpacity={0.35} />
          <stop offset="1" stopColor={C.m500} stopOpacity={0} />
        </radialGradient>
      </defs>

      {/* the grid: 49 identical discs, popping in as a wave from the centre, then dimming behind the blob */}
      {DISCS.map((d) => {
        if (d.chosen && blobOn) return null;
        const p = pr(f, 2 + d.dist * 4.2, 16 + d.dist * 4.2, ease.out);
        const wave = 1.2 * Math.sin(f / 16 - d.dist * 0.9);
        const k = 1 + 0.05 * dimP;
        const x = BC.x + (d.x - BC.x) * k;
        const y = BC.y + (d.y - BC.y) * k;
        const a = (0.25 + 0.75 * p) * (d.chosen ? 1 : 1 - 0.82 * dimP);
        // the scan: a soft diagonal front sweeps across the identical discs toward the chosen one while the riser builds
        const scan = scanOn ? Math.exp(-Math.pow((d.x - scanX + (d.y - BC.y) * 0.25) / (PITCH * 0.8), 2)) * (1 - pr(f, F.lock, F.lock + 10, ease.out)) : 0;
        return <circle key={d.i} cx={x} cy={y} r={(DISC_R + wave + 3 * scan) * (0.3 + 0.7 * p) * (1 - 0.1 * dimP)} fill={scan > 0.02 ? interpolateColors(scan, [0, 1], [C.nickel, C.pearl]) : C.nickel} opacity={a} />;
      })}

      {/* lock-on ring and morph ring */}
      {lockA > 0.01 && <circle cx={CHOSEN_DISC.x} cy={CHOSEN_DISC.y} r={64 - 34 * lockP} fill="none" stroke={C.m400} strokeWidth={2.5} opacity={lockA} />}
      {blobOn && ringU < 1 && <circle cx={CHOSEN_DISC.x} cy={CHOSEN_DISC.y} r={26 + 164 * ringU} fill="none" stroke={C.m300} strokeWidth={2} opacity={0.8 * Math.pow(1 - ringU, 1.6)} />}

      {/* the unique one: 64-point spline, radius R x (1 + 0.18 x noise) */}
      {blobOn && (
        <>
          <circle cx={cx} cy={cy} r={R * 1.75} fill="url(#s7glow)" opacity={glowA} />
          <path d={closedSplinePath(blobPoints(f, cx, cy, R, 0.18 * morphP))} fill={blobFill} stroke={C.m300} strokeWidth={2} strokeOpacity={0.6 * popP} />
        </>
      )}

      {/* S2 callback inside the blob: navy ink on marigold-500 (6.86:1) */}
      {f >= F.arrive && (
        <g>
          <path d={HEAD_SCREEN} pathLength={1} fill="none" stroke={C.navy} strokeWidth={2.4} strokeLinecap="round" strokeLinejoin="round" strokeDasharray="1 2" strokeDashoffset={1 - outlineP} opacity={0.9} />
          {HEAD_LINKS.map(([a, b], i) => {
            const lp = pr(f, F.hexes + 12 + i, F.hexes + 30 + i, ease.out);
            if (lp <= 0) return null;
            return <line key={i} x1={a.x} y1={a.y} x2={lerp(a.x, b.x, lp)} y2={lerp(a.y, b.y, lp)} stroke={C.navy} strokeWidth={1.6} opacity={0.38} />;
          })}
          {HEAD_NODES.map((n, i) => {
            const t0 = startOf(n);
            const p = pr(f, t0, t0 + 10, ease.snap);
            if (p <= 0) return null;
            const flare = pr(f, t0, t0 + 14, ease.out);
            const s = 0.3 + 0.7 * p;
            return (
              <g key={i} opacity={p}>
                {n.kind === 'd' && <polygon points={`${n.x},${n.y - 10 * s} ${n.x + 10 * s},${n.y} ${n.x},${n.y + 10 * s} ${n.x - 10 * s},${n.y}`} fill={C.navy} />}
                {n.kind === 'p' && (
                  <>
                    <circle cx={n.x - 9.5 * s} cy={n.y} r={6.5 * s} fill="none" stroke={C.navy} strokeWidth={2.4} />
                    <circle cx={n.x + 9.5 * s} cy={n.y} r={6.5 * s} fill="none" stroke={C.navy} strokeWidth={2.4} />
                    <line x1={n.x - 3 * s} y1={n.y} x2={n.x + 3 * s} y2={n.y} stroke={C.navy} strokeWidth={2} strokeDasharray="2 1.5" />
                  </>
                )}
                {n.kind === 'h' && (
                  <polygon
                    points={Array.from({length: 6}, (_, k) => `${(n.x + Math.cos((k * Math.PI) / 3) * 10 * s).toFixed(1)},${(n.y + Math.sin((k * Math.PI) / 3) * 10 * s).toFixed(1)}`).join(' ')}
                    fill="none"
                    stroke={C.navy}
                    strokeWidth={2.4}
                  />
                )}
                {flare < 1 && <circle cx={n.x} cy={n.y} r={10 + 12 * flare} fill="none" stroke={C.white} strokeWidth={1.6} opacity={0.8 * (1 - flare)} />}
              </g>
            );
          })}
        </g>
      )}

      {/* arrival ring */}
      {f >= F.arrive && arriveU < 1 && <circle cx={BC.x} cy={BC.y} r={BLOB_R * 1.02 + 100 * arriveU} fill="none" stroke={C.m400} strokeWidth={2.5} opacity={0.55 * Math.pow(1 - arriveU, 1.5)} />}
    </svg>
  );
};

// ---------- text ----------
const out = (f: number, a: number) => pr(f, a, a + 8, ease.in);

const TextLayer: React.FC = () => {
  const f = useCurrentFrame();
  const h1Out = out(f, 96);
  const b3In = F_MORPH;
  const b3Out = out(f, 198);
  const labelDim = 1 - 0.45 * pr(f, 200, 212, ease.inOut);
  return (
    <>
      <div style={{position: 'absolute', left: SAFE.titleX, top: 108, ...T.label, color: C.m400, opacity: labelDim}}>
        <Scramble text="The verdict" at={6} dur={16} seed={4} />
      </div>

      {/* beat 1: Anyone can list features. */}
      {f < 108 && (
        <div style={{position: 'absolute', left: SAFE.titleX, top: 335, ...T.headline, color: C.pearl, opacity: 1 - h1Out, transform: `translateY(${-22 * h1Out}px)`, whiteSpace: 'nowrap'}}>
          <div><Words text="Anyone can" at={F.h1} /></div>
          <div><Words text="list features." at={F.h1 + 6} /></div>
        </div>
      )}

      {/* beat 2: Only you can explain why you chose them. */}
      {f >= b3In - 2 && f < 208 && (
        <div style={{position: 'absolute', left: SAFE.titleX, top: 373, ...T.sub, color: C.pearl, opacity: 1 - b3Out, transform: `translateY(${-18 * b3Out}px)`, whiteSpace: 'nowrap'}}>
          <div><Words text="Only *you* can explain" at={b3In} stagger={2} dur={14} /></div>
          <div><Words text="why you chose them." at={b3In + 8} stagger={2} dur={14} /></div>
        </div>
      )}

      {/* beat 3: That difference is the asset. + kicker */}
      {f >= F.h4 - 2 && (
        <>
          <div style={{position: 'absolute', left: SAFE.titleX, top: 300, ...T.headline, color: C.pearl, whiteSpace: 'nowrap'}}>
            <div><Words text="That difference" at={F.h4 - 1} /></div>
            <div>
              <Words text="is " at={F.h4 + 5} />
              <Marker at={F.marker - 4} dur={10}>
                <Words text="the asset." at={F.h4 + 8} />
              </Marker>
            </div>
          </div>
          <div style={{position: 'absolute', left: SAFE.titleX, top: 760, ...T.caption, fontSize: 56, lineHeight: 1.2, color: C.pearl, whiteSpace: 'nowrap'}}>
            <div><Words text="Looking for clients on LinkedIn?" at={F.h4 + 9} stagger={1} dur={12} rise={20} blur={6} /></div>
            <div><Words text="Start with what only you know." at={F.h4 + 18} stagger={1} dur={12} rise={20} blur={6} /></div>
          </div>
        </>
      )}
    </>
  );
};

export const S7: React.FC = () => {
  const f = useCurrentFrame();
  const stageAt = {transformOrigin: `${BC.x}px ${BC.y}px`};
  const cobalt = 0.2 + 0.28 * pr(f, F.glide, F.glide + GLIDE_LEN, ease.cam) + 0.1 * Math.sin(Math.PI * pr(f, F.low, F.low + 36, ease.inOut));
  return (
    <AbsoluteFill style={{background: C.navy, overflow: 'hidden'}}>
      <CameraRig keys={KEYS} drift={5} seed={9}>
        {/* far: cobalt glow + dust (parallax 0.6 / 0.3) */}
        <Layer depth={0.6} style={stageAt}>
          <div style={{position: 'absolute', left: BC.x - 620, top: BC.y - 620, width: 1240, height: 1240, background: 'radial-gradient(closest-side, rgba(49,87,213,0.55), rgba(49,87,213,0) 100%)', opacity: cobalt}} />
        </Layer>
        <Layer depth={0.3}>
          <Dust count={34} seed={5} color={C.nickel} alpha={[0.12, 0.38]} size={[1.5, 3.2]} vx={-0.1} vy={-0.16} />
        </Layer>

        {/* stage: particles behind the discs, text keeps clear of them */}
        <Layer depth={1} style={stageAt}>
          <Particles bursts={BURSTS} />
          <Stage />
        </Layer>

        <Vignette strength={0.5 + 0.2 * pr(f, F.low, F.low + 30, ease.inOut)} />

        <Layer depth={0}>
          <TextLayer />
        </Layer>

        {/* near bokeh (parallax 1.6), very faint */}
        <Layer depth={1.6}>
          <Dust count={5} seed={12} color={C.pearl} alpha={[0.07, 0.13]} size={[56, 110]} vx={0.12} vy={-0.08} twinkle={0.2} soft />
        </Layer>
      </CameraRig>
      <FictionalTag at={F.arrive} text="Illustrative · fictional founder" />
    </AbsoluteFill>
  );
};
