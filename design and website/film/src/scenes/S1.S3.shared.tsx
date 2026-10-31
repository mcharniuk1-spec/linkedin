// Helpers shared by S1 (The Charge) and S3 (The Silence). Pure functions of the frame only.
import React from 'react';
import {interpolate} from 'remotion';
import {CamKey, Layer} from '../kit/Camera';
import {Burst, Particles} from '../kit/Particles';
import {mulberry32} from '../kit/rng';
import {C} from '../kit/tokens';

export type SceneEvent = {t: number; type: string; gain?: number; dur?: number; dir?: string; pan?: number; note: string};

/** Frame (scene-local, 30 fps) of the nth event of a given type in the scene's events.json. */
export const frameOf = (events: SceneEvent[], type: string, nth = 0) => {
  const hit = events.filter((e) => e.type === type)[nth];
  if (!hit) throw new Error(`events.json has no ${type} #${nth}`);
  return Math.round(hit.t * 30);
};

export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
export const clamp01 = (t: number) => Math.min(1, Math.max(0, t));
/** Clamped, eased interpolation between two frames. */
export const seg = (f: number, f0: number, f1: number, a: number, b: number, easing?: (t: number) => number) =>
  interpolate(f, [f0, f1], [a, b], {easing, extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

/** One camera key per frame: lets a scene describe an arbitrary camera curve (punch, shake) as a pure function. */
export const bakeKeys = (fn: (f: number) => Omit<CamKey, 'f'>, from: number, to: number): CamKey[] =>
  Array.from({length: to - from + 1}, (_, i) => ({f: from + i, ...fn(from + i)}));

/* ---------- ambient motes ---------- */
export type Mote = {x: number; y: number; r: number; a: number; vx: number; bob: number; per: number; ph: number};

export const makeMotes = (
  seed: number,
  n: number,
  o: {r: [number, number]; a: [number, number]; vx: [number, number]; bob: [number, number]},
): Mote[] => {
  const rnd = mulberry32(seed);
  const pick = (r: [number, number]) => r[0] + rnd() * (r[1] - r[0]);
  return Array.from({length: n}, () => {
    const x = rnd() * 1920;
    const y = rnd() * 1080;
    return {x, y, r: pick(o.r), a: pick(o.a), vx: pick(o.vx), bob: pick(o.bob), per: 30 + rnd() * 40, ph: rnd() * 6.283};
  });
};

const PAD = 80;
const W = 1920 + PAD * 2;
const wrapX = (x: number) => ((((x + PAD) % W) + W) % W) - PAD;

/**
 * A parallax plane of drifting motes (nickel/pearl only). `t` is the drift clock in frames (callers may add gusts),
 * `fade` multiplies every alpha. `soft` draws bokeh discs with a radial falloff instead of hard dots.
 */
export const Dust: React.FC<{motes: Mote[]; depth: number; fade: number; t: number; id: string; soft?: boolean; color?: string}> = ({motes, depth, fade, t, id, soft, color = C.nickel}) => {
  if (fade <= 0.001) return null;
  return (
    <Layer depth={depth}>
      <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
        {soft ? (
          <defs>
            <radialGradient id={id}>
              <stop offset="0" stopColor={color} stopOpacity="1" />
              <stop offset="0.55" stopColor={color} stopOpacity="0.55" />
              <stop offset="1" stopColor={color} stopOpacity="0" />
            </radialGradient>
          </defs>
        ) : null}
        {motes.map((m, i) => {
          const x = wrapX(m.x - m.vx * t);
          const y = m.y + m.bob * Math.sin(t / m.per + m.ph) - 0.04 * t * (m.r > 6 ? 1 : 0.5);
          const a = m.a * fade * (0.78 + 0.22 * Math.sin(t / 26 + m.ph));
          return <circle key={i} cx={x} cy={((y % 1080) + 1080) % 1080} r={m.r} fill={soft ? `url(#${id})` : color} opacity={a} />;
        })}
      </svg>
    </Layer>
  );
};

/**
 * Particle bursts that never cover type: full strength outside the keep-out box, at `inside` opacity within it.
 * `box` is in 1920 x 1080 layer coordinates (text box + 24 px margin already applied by the caller).
 */
export const KeepOutParticles: React.FC<{bursts: Burst[]; box: {x0: number; y0: number; x1: number; y1: number} | null; inside?: number}> = ({bursts, box, inside = 0.3}) => {
  if (!box) return <Particles bursts={bursts} />;
  const {x0, y0, x1, y1} = box;
  const outer = `path(evenodd, "M0 0H1920V1080H0Z M${x0} ${y0}H${x1}V${y1}H${x0}Z")`;
  const innerClip = `inset(${y0}px ${1920 - x1}px ${1080 - y1}px ${x0}px)`;
  return (
    <>
      <div style={{position: 'absolute', inset: 0, clipPath: outer}}>
        <Particles bursts={bursts} />
      </div>
      <div style={{position: 'absolute', inset: 0, clipPath: innerClip}}>
        <Particles bursts={bursts} opacity={inside} />
      </div>
    </>
  );
};
