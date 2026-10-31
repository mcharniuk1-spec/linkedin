// S3 The Silence (19.43 to 25.47 s). Near-silent: the drained map leaves one empty profile card, a buyer disc
// stops over it for one beat and slides away. Restraint is the point: no burst, wind-like dust only.
// Pure function of useCurrentFrame(); timings come from S3.events.json (frame = round(t * 30)).
import React from 'react';
import {AbsoluteFill, interpolateColors, useCurrentFrame} from 'remotion';
import {CameraRig, Layer} from '../kit/Camera';
import {FictionalTag, Vignette} from '../kit/Chrome';
import {ease} from '../kit/ease';
import {HEAD_PATH} from '../kit/head';
import {mulberry32, noise1} from '../kit/rng';
import {Scramble, Words} from '../kit/Type';
import {C, SAFE, SHAPE, T} from '../kit/tokens';
import {sceneById} from '../timeline';
import events from './S3.events.json';
import {bakeKeys, clamp01, Dust, frameOf, lerp, makeMotes, SceneEvent, seg} from './S1.S3.shared';

const EV = events as SceneEvent[];
const F = {
  card: frameOf(EV, 'tick', 0), // 36: the empty card has settled
  fly: frameOf(EV, 'whoosh', 0), // 54: buyer glides in
  land: frameOf(EV, 'tick', 1), // 78: buyer stops over the card
  leave: frameOf(EV, 'whoosh', 1), // 102: buyer slides off
  low: frameOf(EV, 'low'), // 159: anticipation drone
};
const FOUNDER_AT = F.land - 2; // 76: the single word is revealed as the buyer stops
const GONE = F.leave + 18; // 120: buyer is off screen
const NOTHING = 145; // 4.85 s: "Nothing else." (VO window)
/** The scene stays mounted 14 frames past its length while S4 wipes in over it (Film.tsx); hold the final state. */
const END = sceneById('S3').frames + 14;

/* ---------- camera: one slow constant push, a small pan that follows the buyer in and lets go ---------- */
const CAM = bakeKeys((f) => {
  const pan = 26 * ease.inOut(seg(f, F.fly, F.land, 0, 1)) - 34 * ease.inOut(seg(f, F.leave, F.leave + 36, 0, 1)) - 6 * seg(f, F.leave + 36, END, 0, 1);
  return {
    zoom: 1 + 0.065 * (f / END),
    x: pan + 3 * noise1(f / 70, 9),
    y: 2.5 * noise1(f / 83, 21),
    rot: 0.4 * noise1(f / 90, 5),
  };
}, 0, END);

/* ---------- baked layouts ---------- */
const MOTES_FAR = makeMotes(301, 36, {r: [1.3, 2.4], a: [0.15, 0.3], vx: [0.14, 0.3], bob: [3, 9]});
const MOTES_MID = makeMotes(302, 30, {r: [1.8, 3.2], a: [0.18, 0.36], vx: [0.22, 0.45], bob: [4, 12]});
const MOTES_ONE = makeMotes(303, 18, {r: [2.5, 4.2], a: [0.2, 0.4], vx: [0.32, 0.6], bob: [5, 14]});
const MOTES_NEAR = makeMotes(304, 6, {r: [14, 30], a: [0.06, 0.12], vx: [0.5, 0.9], bob: [8, 20]}); // 90 motes in total

const HEAD_S = 620 / 900; // the S2 head outline: about 620 px tall, centred slightly right
const HEAD_X = 1020 - 400 * HEAD_S;
const HEAD_Y = 540 - 450 * HEAD_S;

/** The map's last nodes, already gathered near the centre when S2 ends; they drain downward and fade. */
const REMNANTS = (() => {
  const r = mulberry32(77);
  return Array.from({length: 34}, (_, i) => ({dx: (r() - 0.5) * 190, dy: (r() - 0.5) * 150, k: i % 3, s: 5 + r() * 4, fall: 120 + r() * 180, lag: Math.floor(r() * 8), warm: r() < 0.28}));
})();

const CARD = {x: 440, y: 240, w: 1040, h: 600};
const BUYER = {x0: 2250, y0: 465, x1: 1270, y1: 545, xOut: 2400, d: 200};

const buyerPos = (f: number) => {
  if (f < F.land) {
    const p = ease.out(clamp01((f - F.fly) / (F.land - F.fly)));
    return {x: lerp(BUYER.x0, BUYER.x1, p), y: lerp(BUYER.y0, BUYER.y1, p)};
  }
  if (f < F.leave) {
    const p = (f - F.land) / (F.leave - F.land);
    return {x: BUYER.x1 - 20 * ease.inOut(p), y: BUYER.y1 + 5 * Math.sin(p * Math.PI)}; // leans a little toward the card
  }
  const p = ease.in(clamp01((f - F.leave) / (GONE - F.leave)));
  return {x: lerp(BUYER.x1 - 20, BUYER.xOut, p), y: lerp(BUYER.y1, BUYER.y1 + 50, p)};
};

/* ---------- pieces ---------- */
const Head: React.FC = () => {
  const f = useCurrentFrame();
  const erase = seg(f, 12, 46, 0, 1, ease.inOut);
  if (erase >= 1) return null;
  return (
    <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
      <g transform={`translate(${HEAD_X} ${HEAD_Y}) scale(${HEAD_S})`}>
        <path d={HEAD_PATH} fill="none" stroke={C.nickel} strokeWidth={2 / HEAD_S} strokeLinecap="round" strokeLinejoin="round" pathLength={1} strokeDasharray="1 1" strokeDashoffset={erase} opacity={0.85} />
      </g>
    </svg>
  );
};

const NodeShape: React.FC<{k: number; x: number; y: number; s: number; fill: string; o: number}> = ({k, x, y, s, fill, o}) => {
  if (k === 0) return <circle cx={x} cy={y} r={s} fill={fill} opacity={o} />;
  if (k === 1) return <polygon points={`${x},${y - s * 1.3} ${x + s * 1.3},${y} ${x},${y + s * 1.3} ${x - s * 1.3},${y}`} fill={fill} opacity={o} />;
  const pts = Array.from({length: 6}, (_, i) => {
    const a = (Math.PI / 3) * i + Math.PI / 6;
    return `${x + Math.cos(a) * s * 1.2},${y + Math.sin(a) * s * 1.2}`;
  }).join(' ');
  return <polygon points={pts} fill={fill} opacity={o} />;
};

const Remnants: React.FC = () => {
  const f = useCurrentFrame();
  if (f > 40) return null;
  return (
    <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
      {REMNANTS.map((n, i) => {
        const p = seg(f, n.lag, n.lag + 28, 0, 1);
        const y = 540 + n.dy + n.fall * ease.in(p);
        return <NodeShape key={i} k={n.k} x={1020 + n.dx * (1 - 0.25 * p)} y={y} s={n.s} fill={n.warm ? C.m400 : C.nickel} o={0.85 * (1 - p)} />;
      })}
    </svg>
  );
};

const Card: React.FC = () => {
  const f = useCurrentFrame();
  const p = seg(f, 30, 52, 0, 1, ease.out);
  if (p <= 0) return null;
  const inner = seg(f, 40, 56, 0, 1, ease.out);
  const dim = seg(f, NOTHING, NOTHING + 15, 1, 0.5, ease.inOut); // "Nothing else.": the avatar and name bar sink back
  return (
    <div
      style={{
        position: 'absolute',
        left: CARD.x,
        top: CARD.y,
        width: CARD.w,
        height: CARD.h,
        borderRadius: SHAPE.radiusPanel,
        background: C.pearl,
        opacity: p,
        transform: `translateY(${(1 - p) * 26}px) scale(${0.96 + 0.04 * p})`,
        boxShadow: '0 40px 90px rgba(7,16,36,0.55)',
      }}
    >
      <div style={{position: 'absolute', left: 60, top: 60, width: 160, height: 160, borderRadius: '50%', background: C.nickel, opacity: 0.8 * inner * dim}} />
      <div style={{position: 'absolute', left: 260, top: 125, width: 420, height: 30, borderRadius: 15, background: C.nickel, opacity: 0.55 * inner * dim}} />
      <div style={{position: 'absolute', left: 60, top: 345, color: C.navy, whiteSpace: 'nowrap'}}>
        <Words text="Founder." at={FOUNDER_AT} stagger={3} dur={16} rise={30} blur={8} style={{...T.headline, color: C.navy}} />
      </div>
    </div>
  );
};

/** Abstract buyer: a disc with a ring, never a face. Pearl and lit while it looks, then it greys out and leaves. */
const BuyerDisc: React.FC<{x: number; y: number; grey: number; alpha: number; ghost?: boolean}> = ({x, y, grey, alpha, ghost}) => {
  const r = BUYER.d / 2;
  const fill = interpolateColors(grey, [0, 1], [C.pearl, C.nickel]);
  const ring = interpolateColors(grey, [0, 1], [C.cobalt, C.nickel]);
  return (
    <svg width={BUYER.d + 20} height={BUYER.d + 20} style={{position: 'absolute', left: x - r - 10, top: y - r - 10, overflow: 'visible'}} opacity={alpha}>
      <circle cx={r + 10} cy={r + 10} r={r} fill={fill} stroke={C.navy} strokeWidth={6} />
      {ghost ? null : <circle cx={r + 10} cy={r + 10} r={r * 0.62} fill="none" stroke={ring} strokeWidth={4} />}
      {ghost ? null : <circle cx={r + 10} cy={r + 10} r={9} fill={ring} />}
    </svg>
  );
};

const Buyer: React.FC = () => {
  const f = useCurrentFrame();
  if (f < F.fly || f > GONE + 4) return null;
  const {x, y} = buyerPos(f);
  const grey = seg(f, F.leave - 6, F.leave + 14, 0, 1, ease.inOut);
  const alpha = lerp(1, 0.55, grey);
  const moving = (f < F.land || f >= F.leave) && f <= GONE;
  return (
    <>
      {moving
        ? [3, 2, 1].map((lag, i) => {
            const g = buyerPos(Math.max(F.fly, f - lag));
            return <BuyerDisc key={lag} x={g.x} y={g.y} grey={grey} alpha={alpha * [0.1, 0.17, 0.26][i]} ghost />;
          })
        : null}
      <BuyerDisc x={x} y={y} grey={grey} alpha={alpha} />
      <div
        style={{
          position: 'absolute',
          left: x - 210,
          top: y + BUYER.d / 2 + 18,
          width: 420,
          boxSizing: 'border-box',
          padding: '12px 20px',
          borderRadius: SHAPE.radiusPanel,
          background: C.navy,
          border: `2px solid ${C.nickel}`,
          color: interpolateColors(grey, [0, 1], [C.pearl, C.nickel]),
          textAlign: 'center',
          ...T.caption,
          fontSize: 44,
          lineHeight: 1.25,
        }}
      >
        Buyer · illustrative
      </div>
    </>
  );
};

export const S3: React.FC = () => {
  const f = useCurrentFrame();
  const fade = seg(f, 0, 20, 0, 1);
  const gust = 70 * ease.inOut(seg(f, F.leave - 4, F.leave + 36, 0, 1)); // the exit leans the dust left
  const t = f + gust;
  const glow = 0.4 * ease.out(seg(f, F.low - 9, END, 0, 1));
  return (
    <AbsoluteFill>
      <AbsoluteFill style={{background: C.navy}} />
      <CameraRig keys={CAM}>
        <Layer depth={0.6}>
          <div style={{position: 'absolute', left: 960 - 800, top: 515 - 480, width: 1600, height: 960, background: `radial-gradient(closest-side, rgba(49,87,213,${glow}), rgba(49,87,213,0))`}} />
        </Layer>
        <Dust motes={MOTES_FAR} depth={0.3} fade={fade} t={t} id="s3far" />
        <Dust motes={MOTES_MID} depth={0.6} fade={fade} t={t} id="s3mid" />
        <Layer depth={1}>
          <Head />
          <Remnants />
        </Layer>
        <Dust motes={MOTES_ONE} depth={1} fade={fade} t={t} id="s3one" />
        <Layer depth={1}>
          <Card />
          <Buyer />
        </Layer>
        <Dust motes={MOTES_NEAR} depth={1.6} fade={fade} t={t} id="s3near" soft color={C.pearl} />
      </CameraRig>
      <Vignette strength={lerp(0.5, 0.78, seg(f, 110, END, 0, 1, ease.inOut))} />
      <div style={{position: 'absolute', left: SAFE.titleX, top: SAFE.titleTop, opacity: seg(f, NOTHING, NOTHING + 15, 1, 0.6, ease.inOut)}}>
        <Scramble text="Out here" at={18} dur={14} seed={9} style={{...T.label, color: C.nickel}} />
      </div>
      <FictionalTag text="Illustrative · fictional founder" at={-12} />
    </AbsoluteFill>
  );
};
