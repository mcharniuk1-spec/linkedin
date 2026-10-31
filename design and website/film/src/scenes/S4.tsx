// S4 Ignition (25.47-35.0 s, 286 frames). The head map converges into one marigold core, the core detonates on "make it public"
// and becomes a white post card; the founder disc then travels to (960, 540) to continue into S5.
import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {CamKey, CameraRig, Layer} from '../kit/Camera';
import {FictionalTag, Flash, Vignette} from '../kit/Chrome';
import {ease} from '../kit/ease';
import {Burst, Particles} from '../kit/Particles';
import {mulberry32, noise1} from '../kit/rng';
import {C} from '../kit/tokens';
import {BOOM, clamp01, Core, CORE, Field, rgba, SCAN, TICKS} from './S4.field';
import {Avatar, Card, Labels, Post} from './S4.post';

// ---------- P2 idea burst: 320 particles in total (white -> marker -> marigold; cobalt appears only as a soft glow) ----------
const SPARK_COLORS = [C.white, C.m200, C.m300, C.m400];
const BURSTS: Burst[] = [
  {f: BOOM, x: CORE.x, y: CORE.y, n: 130, seed: 4101, speed: [4, 22], drag: 0.04, gravity: -0.01, life: [26, 36], size: [1.8, 4.2], colors: [C.white, C.m200, C.m300, C.m300, C.m400, C.m500], shape: 'dot'},
  {f: BOOM, x: CORE.x, y: CORE.y, n: 100, seed: 4102, speed: [12, 38], drag: 0.05, gravity: -0.006, life: [22, 34], size: [1.6, 3.0], colors: SPARK_COLORS, shape: 'spark', trail: 3},
  {f: BOOM, x: CORE.x, y: CORE.y, n: 14, seed: 4103, speed: [3, 12], drag: 0.045, life: [30, 40], size: [3, 6], colors: [C.m300, C.m400, C.white], shape: 'ring'},
  // slow embers drift to the right only, away from the text block; they may live longer
  {f: BOOM, x: CORE.x, y: CORE.y, n: 76, seed: 4104, speed: [1.5, 7], drag: 0.03, gravity: -0.02, life: [38, 48], size: [1.6, 3], colors: [C.white, C.m200, C.m300], angle: [-Math.PI / 2.2, Math.PI / 2.2], shape: 'dot'},
];

// ---------- camera: slow push, punch to 1.25 on the boom, long settle, back to 1.0 with the disc at the exact centre ----------
const CAM: CamKey[] = [
  {f: 0, zoom: 1.0, rot: 0},
  {f: BOOM - 6, zoom: 1.12, rot: 0.8},
  {f: BOOM, zoom: 1.12, rot: 0.8},
  {f: BOOM + 4, zoom: 1.25, rot: -0.9},
  {f: BOOM + 8, zoom: 1.17, rot: -0.9},
  {f: BOOM + 70, zoom: 1.04, rot: 0},
  {f: 286, zoom: 1.0, rot: 0},
  {f: 310, zoom: 1.0, rot: 0},
];

// ---------- background pieces ----------
const dustRnd = mulberry32(881);
const DUST = Array.from({length: 44}, (_, i) => ({x: dustRnd() * 1920, y: dustRnd() * 1080, r: 2 + dustRnd() * 2.6, a: 0.12 + dustRnd() * 0.2, i}));
const Dust: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
      {DUST.map((d) => (
        <circle key={d.i} cx={d.x + noise1(f / 120 + d.i * 5.3, d.i + 1) * 22} cy={d.y + noise1(f / 140 + d.i * 3.1, d.i + 57) * 22 - f * 0.06} r={d.r} fill={C.nickel} opacity={d.a} />
      ))}
    </svg>
  );
};

const BOKEH = [
  {x: 150, y: 190, r: 120, i: 0},
  {x: 1790, y: 150, r: 90, i: 1},
  {x: 1650, y: 880, r: 140, i: 2},
  {x: 260, y: 850, r: 100, i: 3},
  {x: 1060, y: 60, r: 70, i: 4},
];
const Bokeh: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <>
      {BOKEH.map((b) => {
        const x = b.x + noise1(f / 160 + b.i * 9, b.i + 5) * 30;
        const y = b.y + noise1(f / 190 + b.i * 7, b.i + 41) * 30;
        return <div key={b.i} style={{position: 'absolute', left: x - b.r, top: y - b.r, width: b.r * 2, height: b.r * 2, borderRadius: '50%', background: `radial-gradient(circle, ${rgba(C.pearl, 0.1)} 0%, ${rgba(C.pearl, 0)} 70%)`}} />;
      })}
    </>
  );
};

/** Soft cobalt glow behind the map (wakes up, pulses with each label), a cobalt bloom at the boom, a warm halo behind the card. */
const Glows: React.FC = () => {
  const f = useCurrentFrame();
  const wake = ease.out(clamp01(f / 30));
  const pulse = TICKS.reduce((acc, t) => acc + (f >= t ? Math.max(0, 1 - (f - t) / 16) * 0.18 : 0), 0);
  const pre = f < BOOM ? wake * (0.72 + pulse) : 0;
  const t = f - BOOM;
  const bloom = t >= 0 ? ease.out(clamp01(t / 22)) : 0;
  const bloomA = t >= 0 ? (1 - clamp01((t - 8) / 52)) * 0.6 : 0;
  const warm = t >= 0 ? clamp01(t / 14) * (1 - clamp01((t - 36) / 50)) * 0.16 : 0;
  const disc = (x: number, y: number, rad: number, stops: string, o: number): React.ReactNode => (
    <div style={{position: 'absolute', left: x - rad, top: y - rad, width: rad * 2, height: rad * 2, borderRadius: '50%', background: stops, opacity: o}} />
  );
  return (
    <>
      {pre > 0 && disc(CORE.x, CORE.y, 560, `radial-gradient(circle, ${rgba(C.cobalt, 0.5)} 0%, ${rgba(C.cobalt, 0)} 66%)`, Math.min(1, pre))}
      {bloomA > 0 && disc(CORE.x, CORE.y, 120 + 760 * bloom, `radial-gradient(circle, ${rgba(C.cobalt, 0.7)} 0%, ${rgba(C.cobalt, 0)} 70%)`, bloomA)}
      {warm > 0 && disc(1350, 540, 520, `radial-gradient(circle, ${rgba(C.m500, 1)} 0%, ${rgba(C.m500, 0)} 68%)`, warm)}
    </>
  );
};

/** Scan ring on the whoosh, then the shockwave rings of the detonation (marigold lines on navy, never cobalt lines). */
const Rings: React.FC = () => {
  const f = useCurrentFrame();
  const out: React.ReactNode[] = [];
  const s = f - SCAN;
  if (s >= 0 && s < 26) out.push(<circle key="scan" cx={CORE.x} cy={CORE.y} r={30 + 540 * ease.out(s / 26)} fill="none" stroke={C.m300} strokeWidth={2} opacity={0.55 * (1 - s / 26)} />);
  const t = f - BOOM;
  if (t >= 0 && t < 44) {
    const p = ease.out(t / 44);
    out.push(<circle key="s1" cx={CORE.x} cy={CORE.y} r={20 + 940 * p} fill="none" stroke={C.m200} strokeWidth={Math.max(1.5, 7 * (1 - p))} opacity={Math.pow(1 - t / 44, 1.2)} />);
  }
  if (t >= 3 && t < 44) {
    const p = ease.out((t - 3) / 41);
    out.push(<circle key="s2" cx={CORE.x} cy={CORE.y} r={20 + 760 * p} fill="none" stroke={C.m500} strokeWidth={Math.max(1.5, 4 * (1 - p))} opacity={0.7 * (1 - (t - 3) / 41)} />);
  }
  return (
    <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
      {out}
    </svg>
  );
};

export const S4: React.FC = () => {
  const f = useCurrentFrame();
  // handheld wander fades out so the founder disc lands exactly on (960, 540)
  const drift = 5 * (1 - clamp01((f - 240) / 30));
  return (
    <AbsoluteFill style={{background: C.navy}}>
      <CameraRig keys={CAM} drift={drift} seed={11}>
        <Layer depth={0.3}>
          <Glows />
          <Dust />
        </Layer>
        <Layer depth={1}>
          <Field />
          <Core />
          <Rings />
          <Card />
          <Avatar />
        </Layer>
        <Layer depth={1.6}>
          <Bokeh />
        </Layer>
        <Layer depth={1}>
          <Particles bursts={BURSTS} />
        </Layer>
        <Layer depth={0.2}>
          <Labels />
          <Post />
        </Layer>
      </CameraRig>
      <Vignette strength={0.45} />
      <Flash at={BOOM} color={C.m100} />
      <FictionalTag text="Illustrative · fictional founder" at={4} />
    </AbsoluteFill>
  );
};
