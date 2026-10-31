import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {CameraRig, Layer} from '../kit/Camera';
import {FictionalTag, Marker} from '../kit/Chrome';
import {ease} from '../kit/ease';
import {Words} from '../kit/Type';
import {C, T} from '../kit/tokens';
import {sceneById} from '../timeline';
import events from './S6.events.json';
import {Campaigns, DH, DW, Positioning, Profile, Strategy, Visuals, Writing, clamp01, lerp, pr, prl} from './S6.diagrams';

// S6 The Work: pearl ground, six one-job mini-scenes cut on the spoken words, then six modules dock around the founder disc.
// Everything is a pure function of the scene-local frame. The sync events come from S6.events.json (the same file the audio uses).
type Ev = {t: number; type: string; gain?: number; dur?: number; dir?: string; pan?: number; note: string};
const EV = events as unknown as Ev[];
const FRAMES = sceneById('S6').frames;
const ef = (e: Ev) => Math.round(e.t * 30);

/** Label cuts: the six "cut n" ticks. */
const CUT = EV.filter((e) => e.note.startsWith('cut ')).map(ef);
/** Hub ripples: the label ticks (gain >= 0.45) and the two dock sparkles. */
const RIPPLES = EV.filter((e) => (e.gain ?? 0) >= 0.45 && (e.type === 'tick' || e.type === 'sparkle')).map((e) => ({f: ef(e), big: e.type === 'sparkle'}));

// ---- layout (1920 x 1080) --------------------------------------------------------------------------------------------
const HUB = {x: 960, y: 540, r: 36};
const LX = 154;
const RX = 1026;
type CellId = 'TL' | 'TR' | 'BL' | 'BR';
const CELL: Record<CellId, {x: number; y: number}> = {TL: {x: LX, y: 126}, TR: {x: RX, y: 126}, BL: {x: LX, y: 536}, BR: {x: RX, y: 536}};
const DIA_DY = 75; // label height + gap

type SlotId = 'TL' | 'TR' | 'L' | 'R' | 'BL' | 'BR';
const SLOT: Record<SlotId, {x: number; y: number}> = {TL: {x: 650, y: 330}, TR: {x: 1270, y: 330}, L: {x: 350, y: 540}, R: {x: 1570, y: 540}, BL: {x: 650, y: 750}, BR: {x: 1270, y: 750}};
const TW = 340;
const TH = 156;
const PADX = 22;
const PADY = 18;
const DS = 0.4;

type JobKey = 'pos' | 'prof' | 'cont' | 'writ' | 'vis' | 'camp';
type Job = {key: JobKey; text: string; cell: CellId; a: number; labelOut: number; slot: SlotId; dockStart: number; dockDur: number; fly?: 'left' | 'right'; exit?: number};
const JOBS: Job[] = [
  {key: 'pos', text: 'Positioning', cell: 'TL', a: CUT[0] ?? 12, labelOut: 44, slot: 'L', dockStart: 158, dockDur: 26, fly: 'left', exit: 74},
  {key: 'prof', text: 'Profile', cell: 'TR', a: CUT[1] ?? 33, labelOut: 65, slot: 'R', dockStart: 162, dockDur: 26, fly: 'right', exit: 87},
  {key: 'cont', text: 'Content strategy', cell: 'BL', a: CUT[2] ?? 48, labelOut: 80, slot: 'BL', dockStart: 156, dockDur: 22},
  {key: 'writ', text: 'Writing', cell: 'BR', a: CUT[3] ?? 71, labelOut: 99, slot: 'BR', dockStart: 166, dockDur: 22},
  {key: 'vis', text: 'Visuals', cell: 'TL', a: CUT[4] ?? 84, labelOut: 112, slot: 'TL', dockStart: 150, dockDur: 22},
  {key: 'camp', text: 'Campaigns', cell: 'TR', a: CUT[5] ?? 97, labelOut: 140, slot: 'TR', dockStart: 153, dockDur: 22},
];
const land = (j: Job) => j.dockStart + j.dockDur;

const THREAD_START = 206;
const THREAD_END = 248;

// ---- thread geometry -------------------------------------------------------------------------------------------------
const LOOP = [SLOT.TL, SLOT.TR, SLOT.R, SLOT.BR, SLOT.BL, SLOT.L];
const SEG = LOOP.map((p, i) => {
  const q = LOOP[(i + 1) % LOOP.length];
  return Math.hypot(q.x - p.x, q.y - p.y);
});
const LOOP_LEN = SEG.reduce((a, b) => a + b, 0);
const LOOP_D = 'M' + LOOP.map((p) => `${p.x} ${p.y}`).join(' L') + ' Z';
const loopPoint = (s0: number) => {
  let s = ((s0 % LOOP_LEN) + LOOP_LEN) % LOOP_LEN;
  let i = 0;
  while (i < SEG.length - 1 && s > SEG[i]) {
    s -= SEG[i];
    i++;
  }
  const p = LOOP[i];
  const q = LOOP[(i + 1) % LOOP.length];
  const u = s / SEG[i];
  return {x: lerp(p.x, q.x, u), y: lerp(p.y, q.y, u)};
};
/** Docking port: middle of the tile edge that faces the hub. */
const portOf = (slot: {x: number; y: number}) => {
  const dx = HUB.x - slot.x;
  const dy = HUB.y - slot.y;
  if (Math.abs(dx) / (TW / 2) > Math.abs(dy) / (TH / 2)) return {x: slot.x + Math.sign(dx) * (TW / 2), y: slot.y};
  return {x: slot.x, y: slot.y + Math.sign(dy) * (TH / 2)};
};

// ---- backgrounds -----------------------------------------------------------------------------------------------------
const Grid: React.FC = () => (
  <svg width={2200} height={1300} style={{position: 'absolute', left: -140, top: -110}}>
    <defs>
      <pattern id="s6dots" width={80} height={80} patternUnits="userSpaceOnUse" x={60} y={50}>
        <circle cx={40} cy={40} r={2.6} fill={C.nickel} opacity={0.7} />
      </pattern>
    </defs>
    <rect width={2200} height={1300} fill="url(#s6dots)" />
  </svg>
);

const Glows: React.FC<{f: number}> = ({f}) => (
  <>
    <div style={{position: 'absolute', left: 80 + Math.sin(f / 70) * 20, top: 40, width: 1000, height: 800, background: 'radial-gradient(closest-side, rgba(49,87,213,0.11), rgba(49,87,213,0))'}} />
    <div style={{position: 'absolute', left: 980 - Math.sin(f / 80) * 20, top: 380, width: 1000, height: 800, background: 'radial-gradient(closest-side, rgba(49,87,213,0.09), rgba(49,87,213,0))'}} />
  </>
);

const MARKS: {x: number; y: number; k: 'plus' | 'ring'}[] = [
  {x: 62, y: 160, k: 'plus'}, {x: 1858, y: 118, k: 'plus'}, {x: 52, y: 640, k: 'ring'}, {x: 1868, y: 560, k: 'plus'},
  {x: 1850, y: 930, k: 'ring'}, {x: 70, y: 870, k: 'plus'}, {x: 930, y: 46, k: 'ring'}, {x: 1300, y: 1020, k: 'plus'},
];
const Near: React.FC = () => (
  <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
    {MARKS.map((m, i) =>
      m.k === 'plus' ? (
        <g key={i} stroke={C.cobalt} strokeWidth={3} vectorEffect="non-scaling-stroke" opacity={0.55} strokeLinecap="round">
          <line x1={m.x - 14} y1={m.y} x2={m.x + 14} y2={m.y} vectorEffect="non-scaling-stroke" />
          <line x1={m.x} y1={m.y - 14} x2={m.x} y2={m.y + 14} vectorEffect="non-scaling-stroke" />
        </g>
      ) : (
        <circle key={i} cx={m.x} cy={m.y} r={11} fill="none" stroke={C.nickel} strokeWidth={3} vectorEffect="non-scaling-stroke" opacity={0.8} />
      ),
    )}
  </svg>
);

// ---- label (one job name, mono 56, marker bar) -----------------------------------------------------------------------
const JobLabel: React.FC<{job: Job; f: number}> = ({job, f}) => {
  const inP = pr(f, job.a, job.a + 8);
  const outP = pr(f, job.labelOut, job.labelOut + 6, ease.in);
  const op = inP * (1 - outP);
  if (op <= 0.002) return null;
  const c = CELL[job.cell];
  return (
    <div
      style={{
        position: 'absolute', left: c.x, top: c.y, ...T.label, color: C.navy, whiteSpace: 'nowrap', opacity: op,
        transform: `translateY(${(1 - inP) * 20 - outP * 14}px)`, filter: inP < 1 ? `blur(${(1 - inP) * 5}px)` : undefined,
      }}
    >
      <Marker at={job.a + 5} dur={10}>
        {job.text}
      </Marker>
    </div>
  );
};

const renderDia = (key: JobKey, t: number, s: number, mix: number) => {
  switch (key) {
    case 'pos': return <Positioning t={t} s={s} />;
    case 'prof': return <Profile t={t} s={s} />;
    case 'cont': return <Strategy t={t} s={s} />;
    case 'writ': return <Writing t={t} s={s} mix={mix} />;
    case 'vis': return <Visuals t={t} s={s} />;
    default: return <Campaigns t={t} s={s} mix={mix} />;
  }
};

/** A job's diagram in its cell (full size), used while it is the active mini-scene; fades out when its cell is taken over. */
const CellDia: React.FC<{job: Job; f: number}> = ({job, f}) => {
  const t = f - job.a;
  const ex = job.exit ?? 9999;
  const out = pr(f, ex, ex + 8, ease.in);
  if (t < 0 || out >= 0.999) return null;
  const c = CELL[job.cell];
  const dir = job.cell === 'TL' || job.cell === 'BL' ? -1 : 1;
  return <div style={{position: 'absolute', left: c.x + dir * 36 * out, top: c.y + DIA_DY, opacity: 1 - out}}>{renderDia(job.key, t, 1, 0)}</div>;
};

/** The docked module: a tile with the job's diagram at 0.4 scale. Cell jobs morph from their cell; fly jobs arrive from the side. */
const Module: React.FC<{job: Job; f: number; idx: number}> = ({job, f, idx}) => {
  const slot = SLOT[job.slot];
  const t = f - job.a;
  if (t < 0) return null;
  const mix = prl(f, job.dockStart - 8, job.dockStart - 2);
  let x: number;
  let y: number;
  let w: number;
  let h: number;
  let sc: number;
  let ox: number;
  let oy: number;
  let tile: number;
  let alpha = 1;
  let p: number;
  if (job.fly) {
    p = pr(f, job.dockStart, job.dockStart + job.dockDur, ease.out);
    if (f < job.dockStart) return null;
    x = slot.x - TW / 2 + (job.fly === 'left' ? -1 : 1) * (1 - p) * 640;
    y = slot.y - TH / 2;
    w = TW;
    h = TH;
    sc = DS;
    ox = PADX;
    oy = PADY;
    tile = 1;
    alpha = prl(p, 0, 0.15);
  } else {
    p = pr(f, job.dockStart, job.dockStart + job.dockDur, ease.inOut);
    const c = CELL[job.cell];
    x = lerp(c.x, slot.x - TW / 2, p);
    y = lerp(c.y + DIA_DY, slot.y - TH / 2, p);
    w = lerp(DW, TW, p);
    h = lerp(DH, TH, p);
    sc = lerp(1, DS, p);
    ox = lerp(0, PADX, p);
    oy = lerp(0, PADY, p);
    tile = prl(p, 0.1, 0.5);
  }
  const landed = f >= land(job);
  const breathe = landed ? 1 + 0.012 * Math.sin((f - land(job)) / 15 + idx * 1.3) : 1;
  return (
    <div style={{position: 'absolute', left: x, top: y, width: w, height: h, opacity: alpha, transform: `scale(${breathe})`, transformOrigin: '50% 50%'}}>
      <div style={{position: 'absolute', inset: 0, boxSizing: 'border-box', background: C.white, border: `4px solid ${C.cobalt}`, borderRadius: 20, opacity: tile}} />
      <div style={{position: 'absolute', left: ox, top: oy}}>{renderDia(job.key, t, sc, mix)}</div>
    </div>
  );
};

// ---- the scene -------------------------------------------------------------------------------------------------------
export const S6: React.FC = () => {
  const f = useCurrentFrame();
  const hubK = (1 + 0.28 * pr(f, 150, 170, ease.inOut)) * (1 + 0.02 * Math.sin(f * 0.1));
  const hubR = HUB.r * hubK;

  // thread + beads
  const threadP = pr(f, THREAD_START, THREAD_END, ease.out);
  const beadV = LOOP_LEN / 170;
  const gx = (x: number) => (x < 0 ? 0 : x < 20 ? (x * x) / 40 : x - 10);
  const travel = beadV * gx(f - 250);
  const beads: {x: number; y: number; k: number}[] = [];
  if (f >= THREAD_START) {
    const lead = f < THREAD_END ? loopPoint(threadP * LOOP_LEN) : loopPoint(LOOP_LEN + travel);
    beads.push({...lead, k: 1});
    for (let i = 1; i <= 2; i++) {
      const k = pr(f, THREAD_END, THREAD_END + 8, ease.snap);
      if (k > 0.01) beads.push({...loopPoint(LOOP_LEN + travel + (i * LOOP_LEN) / 3), k});
    }
  }

  return (
    <AbsoluteFill style={{background: C.pearl, overflow: 'hidden'}}>
      <CameraRig
        keys={[
          {f: 0, zoom: 1.0, x: 0, y: 0, rot: 0},
          {f: 105, zoom: 1.035, x: -12, y: 4, rot: -0.25},
          {f: 150, zoom: 1.0, x: 0, y: 0, rot: 0},
          {f: FRAMES - 1, zoom: 1.02, x: 8, y: -4, rot: 0.35},
        ]}
        drift={3}
        seed={61}
      >
        <Layer depth={0.3}>
          <Grid />
        </Layer>
        <Layer depth={0.6}>
          <Glows f={f} />
        </Layer>

        <Layer depth={1}>
          {/* hub ripples */}
          <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
            <circle cx={HUB.x} cy={HUB.y} r={170} fill="url(#s6halo)" />
            <defs>
              <radialGradient id="s6halo">
                <stop offset="0" stopColor={C.cobalt} stopOpacity={0.14} />
                <stop offset="1" stopColor={C.cobalt} stopOpacity={0} />
              </radialGradient>
            </defs>
            {RIPPLES.map((r, i) => {
              const u = prl(f, r.f, r.f + (r.big ? 44 : 28));
              if (u <= 0 || u >= 1) return null;
              const e = ease.out(u);
              return <circle key={i} cx={HUB.x} cy={HUB.y} r={lerp(hubR + 6, r.big ? 330 : 170, e)} fill="none" stroke={C.cobalt} strokeWidth={3} vectorEffect="non-scaling-stroke" opacity={0.75 * (1 - u) * (1 - u * 0.3)} />;
            })}
          </svg>

          {/* spokes, thread, beads: under the tiles */}
          <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
            {JOBS.map((j) => {
              const port = portOf(SLOT[j.slot]);
              const sp = pr(f, land(j) - 10, land(j) + 4);
              if (sp <= 0.001) return null;
              return <line key={j.key} x1={HUB.x} y1={HUB.y} x2={lerp(HUB.x, port.x, sp)} y2={lerp(HUB.y, port.y, sp)} stroke={C.cobalt} strokeWidth={3} vectorEffect="non-scaling-stroke" strokeLinecap="round" opacity={0.9} />;
            })}
            {threadP > 0.001 && (
              <>
                <path d={LOOP_D} fill="none" stroke={C.navy} strokeWidth={8} strokeLinejoin="round" strokeLinecap="round" pathLength={1} strokeDasharray={threadP >= 0.999 ? undefined : '1 1'} strokeDashoffset={1 - threadP} />
                <path d={LOOP_D} fill="none" stroke={C.m500} strokeWidth={3.5} strokeLinejoin="round" strokeLinecap="round" pathLength={1} strokeDasharray={threadP >= 0.999 ? undefined : '1 1'} strokeDashoffset={1 - threadP} />
              </>
            )}
            {beads.map((b, i) => (
              <circle key={i} cx={b.x} cy={b.y} r={11 * b.k} fill={C.m500} stroke={C.navy} strokeWidth={4} vectorEffect="non-scaling-stroke" />
            ))}
          </svg>

          {/* mini-scenes in their cells */}
          {JOBS.filter((j) => j.fly).map((j) => (
            <CellDia key={j.key} job={j} f={f} />
          ))}
          {/* modules (cell jobs morph from their cell into the ring; fly jobs arrive from the sides) */}
          {JOBS.map((j, i) => (
            <Module key={j.key} job={j} f={f} idx={i} />
          ))}

          {/* docking ports and the founder disc */}
          <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
            {JOBS.map((j) => {
              const port = portOf(SLOT[j.slot]);
              const k = pr(f, land(j) - 2, land(j) + 8, ease.snap);
              if (k <= 0.01) return null;
              return <circle key={j.key} cx={port.x} cy={port.y} r={9 * k} fill={C.m500} stroke={C.navy} strokeWidth={3} vectorEffect="non-scaling-stroke" />;
            })}
            <g transform={`translate(${HUB.x} ${HUB.y}) scale(${hubK})`}>
              <circle r={HUB.r} fill={C.m500} stroke={C.navy} strokeWidth={5} vectorEffect="non-scaling-stroke" />
              <circle cx={0} cy={-9} r={11} fill={C.white} />
              <path d="M-22 27 Q-22 6 0 6 Q22 6 22 27 Z" fill={C.white} />
            </g>
          </svg>

          {/* labels */}
          {JOBS.map((j) => (
            <JobLabel key={j.key} job={j} f={f} />
          ))}

          {/* title: "Six jobs" on the spoken words, "one difference" as the thread runs */}
          {f >= 154 && (
            <div style={{position: 'absolute', left: 0, right: 0, top: 108, textAlign: 'center', ...T.sub, color: C.navy, whiteSpace: 'nowrap', transform: `translateX(${272 * (1 - pr(f, 214, 238, ease.out))}px)`}}>
              <Words text="Six jobs" at={156} stagger={4} dur={14} rise={22} blur={6} />
              <span style={{display: 'inline-block', whiteSpace: 'pre', opacity: clamp01((f - 218) / 10)}}>{' · '}</span>
              <Marker at={246} dur={10}>
                <Words text="one difference" at={224} stagger={4} dur={14} rise={22} blur={6} />
              </Marker>
            </div>
          )}
        </Layer>

        <Layer depth={1.6}>
          <Near />
        </Layer>
      </CameraRig>
      <FictionalTag text="Illustrative · fictional founder" color={C.navy} align="right" />
    </AbsoluteFill>
  );
};
