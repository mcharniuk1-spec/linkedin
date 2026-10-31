// S1 The Charge (0 to 11.07 s). Silence, a blinking cursor, one hard hit, then type that gets quieter.
// Pure function of useCurrentFrame(); every timing below is read from S1.events.json (frame = round(t * 30)).
import React from 'react';
import {AbsoluteFill, interpolateColors, useCurrentFrame} from 'remotion';
import {CameraRig, Layer} from '../kit/Camera';
import {FictionalTag, Flash, Vignette} from '../kit/Chrome';
import {ease} from '../kit/ease';
import {Burst} from '../kit/Particles';
import {noise1} from '../kit/rng';
import {Scramble} from '../kit/Type';
import {C, FONT, HEAT, T} from '../kit/tokens';
import {sceneById} from '../timeline';
import events from './S1.events.json';
import {bakeKeys, clamp01, Dust, frameOf, KeepOutParticles, lerp, makeMotes, seg, SceneEvent} from './S1.S3.shared';

const EV = events as SceneEvent[];
const F = {
  impact: frameOf(EV, 'boom'), // 39: ground rises, flash, ring, burst, punch
  you: frameOf(EV, 'hit'), // 42: YOU slams in
  glitch: frameOf(EV, 'glitch'), // 108: hard cut to BRILLIANT
  sweep: frameOf(EV, 'sparkle', 0), // 128: gold glint across BRILLIANT
  quietCut: frameOf(EV, 'tick', 0), // 153: hard cut to QUIET
  quietShrink: frameOf(EV, 'whoosh', 0), // 174: QUIET gets quieter
  dot: frameOf(EV, 'sparkle', 1), // 207: the founder dot
  label: frameOf(EV, 'tick', 1), // 216: label under the dot
  heard: frameOf(EV, 'sparkle', 2), // 294: "heard" is spoken
  inhale: frameOf(EV, 'whoosh', 1), // 312: dot inhales ahead of the S2 bloom
};
/** The scene stays mounted 18 frames past its length while S2 blooms over it (Film.tsx); hold the final state. */
const END = sceneById('S1').frames + 18;
const CX = 960;
const CY = 540;

/* ---------- camera ---------- */
const punchShape = (t: number) => (t < 0 ? 0 : t < 3 ? ease.out(t / 3) : 1 - ease.cam(clamp01((t - 3) / 21)));
const driftFade = (f: number) => 1 - ease.inOut(clamp01((f - 296) / 30));
const camAt = (f: number) => {
  let zoom: number;
  if (f < F.glitch) {
    const base = f < F.impact ? 1 + 0.012 * (f / F.impact) : lerp(1.012, 1.045, ease.inOut(clamp01((f - F.impact - 24) / (F.glitch - F.impact - 24))));
    zoom = base + 0.068 * punchShape(f - F.impact); // 1.0 to 1.08 in 3 f, back over 21 f
  } else if (f < F.quietCut) {
    zoom = lerp(1.0, 1.05, ease.cam(clamp01((f - F.glitch) / (F.quietCut - F.glitch))));
  } else {
    zoom = lerp(1.0, 1.06, ease.cam(clamp01((f - F.quietCut) / (END - F.quietCut))));
  }
  const t = f - F.impact;
  const amp = t >= 0 && t < 6 ? 8 * (1 - t / 6) : 0; // 8 px shake decaying in 6 f
  const fade = driftFade(f); // wander dies out so the dot sits exactly at (960, 540) at the end
  return {
    zoom,
    x: amp * Math.cos(t * 2.7 + 0.5) + 3 * noise1(f / 70, 7) * fade,
    y: amp * Math.sin(t * 3.3 + 1.1) + 2.5 * noise1(f / 83, 18) * fade,
    rot: 0.5 * noise1(f / 60, 31) * fade,
  };
};
const CAM = bakeKeys(camAt, 0, END);

/* ---------- baked layouts ---------- */
const MOTES_FAR = makeMotes(11, 24, {r: [1.4, 2.8], a: [0.14, 0.34], vx: [0.12, 0.34], bob: [4, 12]});
const MOTES_MID = makeMotes(23, 12, {r: [2.4, 4.2], a: [0.16, 0.3], vx: [0.2, 0.5], bob: [6, 16]});
const MOTES_NEAR = makeMotes(37, 6, {r: [16, 34], a: [0.05, 0.11], vx: [0.4, 0.9], bob: [10, 24]});

/**
 * P1: 36 particles, drag 0.1, life 28 f, marigold heat ramp. "260-620 px/s equivalent" is read as the average speed over the
 * 28 f life, which with drag 0.1 means a birth speed of 26 to 62 px/f (travel 250 to 580 px): the burst clears the YOU box.
 */
const RAMP = [...HEAT.slice(0, 5)];
const P1: Burst[] = [
  {f: F.impact, x: CX, y: CY, n: 24, seed: 101, speed: [26, 62], drag: 0.1, life: [22, 28], size: [2.2, 4.5], colors: RAMP, shape: 'dot'},
  {f: F.impact, x: CX, y: CY, n: 12, seed: 102, speed: [30, 62], drag: 0.1, life: [20, 28], size: [1.6, 3], colors: RAMP, shape: 'spark', trail: 1.2},
];
/** YOU box + 24 px keep-out for the burst (inside it the burst renders at 30 %). */
const YOU_BOX = {x0: 700, y0: 410, x1: 1220, y1: 670};

/* ---------- pieces ---------- */
const Ground: React.FC = () => {
  const f = useCurrentFrame();
  const dark = seg(f, F.impact, F.impact + 10, 0.88, 0, ease.out); // near-black (navy under #071024 at 88 %) up to navy
  return (
    <>
      <AbsoluteFill style={{background: C.navy}} />
      <AbsoluteFill style={{background: `rgba(7,16,36,${dark})`}} />
    </>
  );
};

const TYPED = 'Let\u2019s talk about you.';

/**
 * The silent open. A 6 px silver cursor blinks in steps and types the first spoken line, so the very first second already
 * carries a readable phrase for muted autoplay (design-review decision: the open must never read as a broken file).
 */
const Cursor: React.FC = () => {
  const f = useCurrentFrame();
  if (f >= F.impact) return null;
  const n = Math.max(0, Math.min(TYPED.length, Math.floor((f - 2) / 1.4)));
  const typing = n > 0 && n < TYPED.length;
  const on = typing || Math.floor(f / 15) % 2 === 0;
  return (
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
      <div style={{position: 'relative', ...T.body, color: C.pearl}}>
        <span style={{visibility: 'hidden', whiteSpace: 'pre'}}>{TYPED}</span>
        <span style={{position: 'absolute', left: 0, top: 0, whiteSpace: 'pre', opacity: 0.94}}>
          {TYPED.slice(0, n)}
          <span style={{display: on ? 'inline-block' : 'none', width: 6, height: 84, background: C.nickel, marginLeft: 4, verticalAlign: '-14px'}} />
        </span>
      </div>
    </AbsoluteFill>
  );
};

const Glow: React.FC = () => {
  const f = useCurrentFrame();
  if (f < F.impact) return null;
  const a = 0.14 + 0.36 * Math.exp(-(f - F.impact) / 14);
  return (
    <Layer depth={0.6}>
      <div style={{position: 'absolute', left: CX - 760, top: CY - 480, width: 1520, height: 960, background: `radial-gradient(closest-side, rgba(49,87,213,${a}), rgba(49,87,213,0))`}} />
    </Layer>
  );
};

const Rings: React.FC = () => {
  const f = useCurrentFrame();
  const p1 = clamp01((f - F.impact) / 21);
  const p2 = clamp01((f - F.impact - 3) / 21);
  if (f < F.impact || p1 >= 1) return null;
  return (
    <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
      <circle cx={CX} cy={CY} r={900 * ease.out(p1)} fill="none" stroke={C.m300} strokeWidth={2} opacity={0.95 * (1 - p1 * p1)} />
      {p2 > 0 ? <circle cx={CX} cy={CY} r={560 * ease.out(p2)} fill="none" stroke={C.m500} strokeWidth={2} opacity={0.5 * (1 - p2)} /> : null}
    </svg>
  );
};

/** A word whose pearl face is replaced by navy ink exactly where the marker bar has swept: legible at every frame. */
const InkWord: React.FC<{text: string; p: number}> = ({text, p}) => {
  const copy = (color: string, clip: string) => (
    <span style={{position: 'absolute', inset: 0, padding: '0 0.14em', color, clipPath: clip, whiteSpace: 'pre'}}>{text}</span>
  );
  return (
    <span style={{position: 'relative', display: 'inline-block', padding: '0 0.14em', whiteSpace: 'pre', ...T.display}}>
      <span style={{position: 'absolute', inset: '8% 0 4% 0', background: C.m300, transformOrigin: 'left center', transform: `scaleX(${p})`}} />
      <span style={{visibility: 'hidden'}}>{text}</span>
      {copy(C.pearl, `inset(0 0 0 ${p * 100}%)`)}
      {copy(C.navy, `inset(0 ${(1 - p) * 100}% 0 0)`)}
    </span>
  );
};

const You: React.FC = () => {
  const f = useCurrentFrame();
  const lf = f - F.you;
  const s = seg(lf, 0, 9, 1.6, 1, ease.snap);
  const o = seg(lf, 0, 2, 0, 1);
  const p = seg(f, F.you + 4, F.you + 12, 0, 1, ease.out);
  const settle = 1 + 0.025 * ease.cam(clamp01((lf - 9) / 60)); // keeps breathing so the hold never freezes
  return (
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
      <div style={{transform: `scale(${s * settle})`, opacity: o}}>
        <InkWord text="YOU" p={p} />
      </div>
    </AbsoluteFill>
  );
};

const Brilliant: React.FC = () => {
  const f = useCurrentFrame();
  const lf = f - F.glitch;
  const g = lf === 0 ? 6 : lf === 1 ? -6 : 0;
  const base: React.CSSProperties = {...T.headline, color: C.pearl, whiteSpace: 'pre', letterSpacing: `${lerp(-0.02, 0.012, ease.cam(clamp01(lf / 45)))}em`};
  const sw = seg(f, F.sweep, F.sweep + 20, -0.15, 1.15, ease.inOut);
  const glint = f >= F.sweep && f <= F.sweep + 20;
  return (
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
      <div style={{position: 'relative'}}>
        {g !== 0 ? (
          <>
            <div style={{...base, clipPath: 'inset(0 0 45% 0)', transform: `translateX(${g}px)`}}>BRILLIANT</div>
            <div style={{...base, position: 'absolute', inset: 0, clipPath: 'inset(50% 0 0 0)', transform: `translateX(${-g}px)`}}>BRILLIANT</div>
          </>
        ) : (
          <div style={base}>BRILLIANT</div>
        )}
        {glint ? (
          <div
            style={{
              ...base,
              position: 'absolute',
              inset: 0,
              color: 'transparent',
              backgroundImage: `linear-gradient(105deg, transparent ${(sw - 0.1) * 100}%, ${C.m300} ${sw * 100}%, transparent ${(sw + 0.1) * 100}%)`,
              WebkitBackgroundClip: 'text',
              backgroundClip: 'text',
            }}
          >
            BRILLIANT
          </div>
        ) : null}
      </div>
    </AbsoluteFill>
  );
};

/** Mona Sans 600 shrinks 120 to 64 px while tracking widens and the colour falls to 0.45 nickel; then it folds into the dot. */
const Quiet: React.FC = () => {
  const f = useCurrentFrame();
  const sp = seg(f, F.quietShrink, F.quietShrink + 24, 0, 1, ease.inOut);
  const track = lerp(0.02, 0.3, sp);
  const collapse = seg(f, F.dot - 5, F.dot + 3, 0, 1, ease.in);
  const opacity = lerp(1, 0.45, sp) * (1 - collapse);
  return (
    <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
      <div
        style={{
          fontFamily: FONT.text,
          fontWeight: 600,
          fontSize: lerp(120, 64, sp),
          lineHeight: 1,
          letterSpacing: `${track}em`,
          paddingLeft: `${track}em`,
          color: interpolateColors(sp, [0, 1], [C.pearl, C.nickel]),
          opacity,
          transform: `scale(${lerp(1, 0.15, collapse)})`,
        }}
      >
        QUIET
      </div>
    </AbsoluteFill>
  );
};

const SW: React.FC<{at: number; em?: boolean; children: string}> = ({at, em, children}) => {
  const f = useCurrentFrame();
  const p = seg(f, at, at + 14, 0, 1, ease.out);
  const bump = em ? Math.sin(Math.PI * clamp01((f - F.heard) / 18)) : 0; // "heard" pulses when it is spoken
  return (
    <span
      style={{
        display: 'inline-block',
        opacity: p,
        transform: `translateY(${(1 - p) * 30}px) scale(${1 + 0.06 * bump})`,
        filter: p < 1 ? `blur(${(1 - p) * 8}px)` : undefined,
        color: em ? interpolateColors(bump, [0, 1], [C.m400, C.m200]) : C.pearl,
        whiteSpace: 'pre',
      }}
    >
      {children}
    </span>
  );
};

const Founder: React.FC = () => {
  const f = useCurrentFrame();
  const dp = seg(f, F.dot, F.dot + 14, 0, 1, ease.snap);
  const ping = clamp01((f - F.dot) / 24);
  const inh = clamp01((f - (F.inhale - 6)) / 36); // ring contracts into the dot
  const grow = seg(f, F.inhale - 6, F.inhale + 24, 0, 1, ease.inOut);
  const line = {display: 'flex', justifyContent: 'center', columnGap: '0.25em'} as const;
  const t0 = F.label + 6; // 222
  return (
    <>
      <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
        <defs>
          <radialGradient id="s1dot">
            <stop offset="0" stopColor={C.m500} stopOpacity="0.55" />
            <stop offset="1" stopColor={C.m500} stopOpacity="0" />
          </radialGradient>
        </defs>
        {ping < 1 ? <circle cx={CX} cy={CY} r={130 * ease.out(ping)} fill="none" stroke={C.m400} strokeWidth={2} opacity={0.75 * (1 - ping)} /> : null}
        {inh > 0 && inh < 1 ? <circle cx={CX} cy={CY} r={lerp(250, 30, ease.in(inh))} fill="none" stroke={C.m400} strokeWidth={2} opacity={0.4 * Math.sin(Math.PI * inh)} /> : null}
        <circle cx={CX} cy={CY} r={(56 + 34 * grow) * dp} fill="url(#s1dot)" />
        <circle cx={CX} cy={CY} r={(16 + 4 * grow) * dp} fill={C.m500} />
      </svg>
      <div style={{position: 'absolute', left: 0, right: 0, top: 181, textAlign: 'center', ...T.headline}}>
        <div style={line}>
          <SW at={t0}>The</SW>
          <SW at={t0 + 6}>right</SW>
          <SW at={t0 + 12}>buyers</SW>
        </div>
        <div style={line}>
          <SW at={t0 + 36}>haven’t</SW>
          <SW at={t0 + 43} em>
            heard
          </SW>
          <SW at={t0 + 49}>of</SW>
          <SW at={t0 + 56}>you.</SW>
        </div>
      </div>
      <div style={{position: 'absolute', left: 0, right: 0, top: 590, textAlign: 'center'}}>
        <Scramble text="B2B AI software · Europe" at={F.label} dur={14} seed={5} style={{...T.label, color: C.nickel}} />
      </div>
    </>
  );
};

export const S1: React.FC = () => {
  const f = useCurrentFrame();
  const fade = seg(f, F.impact, F.impact + 40, 0, 1);
  return (
    <AbsoluteFill>
      <Ground />
      <CameraRig keys={CAM}>
        <Glow />
        <Dust motes={MOTES_FAR} depth={0.3} fade={fade} t={f} id="s1far" />
        <Dust motes={MOTES_MID} depth={0.6} fade={fade} t={f} id="s1mid" />
        <Layer depth={1}>
          <Rings />
          <KeepOutParticles bursts={P1} box={f < F.glitch ? YOU_BOX : null} inside={0.3} />
          {f >= F.you && f < F.glitch ? <You /> : null}
          {f >= F.glitch && f < F.quietCut ? <Brilliant /> : null}
          {f >= F.quietCut && f < F.dot + 4 ? <Quiet /> : null}
          {f >= F.dot ? <Founder /> : null}
        </Layer>
        <Dust motes={MOTES_NEAR} depth={1.6} fade={fade} t={f} id="s1near" soft color={C.pearl} />
      </CameraRig>
      <Vignette strength={0.45} />
      <Cursor />
      <Flash at={F.impact} alpha={0.2} />
      <FictionalTag text="Illustrative · fictional founder" at={180} />
    </AbsoluteFill>
  );
};
