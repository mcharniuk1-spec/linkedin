// S9 The Invitation (70.47-79.9 s, 283 frames): converge into the inverse wordmark, drum-synced coronas, the hero line, the CTA capsule, a held end card.
import React from 'react';
import {AbsoluteFill, Img, spring, staticFile, useCurrentFrame} from 'remotion';
import {CamKey, CameraRig, Layer} from '../kit/Camera';
import {FictionalTag, Flash, Vignette} from '../kit/Chrome';
import {ease} from '../kit/ease';
import {mulberry32, noise1} from '../kit/rng';
import {C, T} from '../kit/tokens';
import {Words} from '../kit/Type';
import events from './S9.events.json';
import {Fx, Hit, Rect} from './S9.fx';
import {InkMarker} from './S4.S9.shared';

type Ev = {t: number; type: string; gain?: number; dur?: number; dir?: string; pan?: number; note: string};
const EV = events as Ev[];
const F = (t: number) => Math.round(t * 30);
const HITS_F = EV.filter((e) => e.type === 'hit').map((e) => F(e.t)); // [14, 50, 189]
const TICKS = EV.filter((e) => e.type === 'tick').map((e) => F(e.t)); // [44, 80, 227]
const SPARKLE = F(EV.find((e) => e.type === 'sparkle')!.t); // CTA pop
const SLIDE = F(EV.find((e) => e.type === 'whoosh')!.t); // wordmark glides up
const [HIT1, HIT2, HIT3] = HITS_F;
const [MONO_AT, CARE_AT, PRESS] = TICKS;
const CTA_AT = SPARKLE;

const clamp01 = (v: number) => Math.max(0, Math.min(1, v));
const rgba = (hex: string, a: number) => {
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255}, ${a})`;
};

// ---------- layout (1920 x 1080) ----------
const WM_W = 720;
const WM_H = (WM_W * 84) / 641.09;
const WM_CY_FINAL = 118 + WM_H / 2;
const wmCy = (f: number) => 540 + (WM_CY_FINAL - 540) * ease.cam(clamp01((f - SLIDE) / 24));
const MONO_TOP = 242;
const HERO_TOP = 349;
const HERO_LINE = 134.4;
const CTA_TOP = 792;
const CTA = {cx: 960, hw: 395, top: CTA_TOP, h: 117};
const HERO_AT = HIT2 + 1;
const HERO_STAGGER = 7;

// ---------- the three coronas ----------
const HITS: Hit[] = [
  // hit 1: ellipse around the wordmark's keep-out box (box + 1x height), 160 particles
  {f: HIT1, cx: 960, cy: 540, hw: WM_W / 2 + WM_H, hh: WM_H / 2 + WM_H, d0: 26, n: 160, seed: 9101, speed: [2.5, 12], drag: 0.045, life: [48, 66], size: [1.6, 4], streaks: 0.4},
  // hit 2: circle through the middle of the stage as the hero line begins, 190 particles (dimmed over the text block)
  {f: HIT2, cx: 960, cy: 560, hw: 0, hh: 0, d0: 60, n: 190, seed: 9102, speed: [4, 15], drag: 0.045, life: [46, 66], size: [1.8, 4.6], streaks: 0.35},
  // hit 3: the biggest corona is born around the CTA capsule, 220 particles
  {f: HIT3, cx: CTA.cx, cy: CTA.top + CTA.h / 2, hw: CTA.hw, hh: CTA.h / 2, d0: 26, n: 220, seed: 9103, speed: [3.5, 14], drag: 0.042, life: [50, 66], size: [2, 5], streaks: 0.35},
];

const hardRects = (f: number): Rect[] => {
  const cy = wmCy(f);
  const out: Rect[] = [{x0: 960 - WM_W / 2 - WM_H, x1: 960 + WM_W / 2 + WM_H, y0: cy - WM_H / 2 - WM_H, y1: cy + WM_H / 2 + WM_H}];
  if (f >= MONO_AT - 6) out.push({x0: 221, x1: 1699, y0: MONO_TOP - 24, y1: MONO_TOP + 67 + 24});
  out.push({x0: 96, x1: 560, y0: 904, y1: 960}); // the persistent FictionalTag stays fully legible
  return out;
};
const softRects = (f: number): Rect[] => {
  const out: Rect[] = [
    {x0: 300, x1: 1620, y0: HERO_TOP - 24, y1: HERO_TOP + 3 * HERO_LINE + 24},
  ];
  if (f >= CTA_AT - 4) out.push({x0: CTA.cx - CTA.hw - 24, x1: CTA.cx + CTA.hw + 24, y0: CTA.top - 24, y1: CTA.top + CTA.h + 24});
  return out;
};

// ---------- camera: one slow push (text never zooms faster than 1 % per second); the drums thump the background layers instead ----------
const CAM: CamKey[] = [
  {f: 0, zoom: 1.0, rot: 0},
  {f: 40, zoom: 1.01, rot: 0},
  {f: 185, zoom: 1.045, rot: 0},
  {f: 283, zoom: 1.055, rot: 0},
  {f: 310, zoom: 1.06, rot: 0},
];

/** Drum thump: the faint network and the bokeh swell by a few per cent on each hit; the wordmark and all text are untouched. */
const Thump: React.FC<{children: React.ReactNode}> = ({children}) => {
  const f = useCurrentFrame();
  const amp = (hf: number, a: number) => {
    const t = f - hf;
    return t < 0 ? 0 : a * Math.min(1, t / 2) * Math.exp(-t / 9);
  };
  const sc = 1 + amp(HIT1, 0.03) + amp(HIT2, 0.025) + amp(HIT3, 0.04);
  return <AbsoluteFill style={{transform: `scale(${sc})`, transformOrigin: '50% 50%'}}>{children}</AbsoluteFill>;
};

// ---------- background: glows (pinned), faint illustrative network (d 0.6), bokeh (d 1.6) ----------
const Glows: React.FC = () => {
  const f = useCurrentFrame();
  const disc = (x: number, y: number, rad: number, stops: string, o: number, blend?: 'screen') => (
    <div key={`${x}-${y}-${rad}`} style={{position: 'absolute', left: x - rad, top: y - rad, width: rad * 2, height: rad * 2, borderRadius: '50%', background: stops, opacity: o, mixBlendMode: blend}} />
  );
  const pulse = (hf: number, k: number) => (f >= hf ? Math.exp(-(f - hf) / 22) * k : 0);
  return (
    <>
      {disc(960, 540, 1000, `radial-gradient(circle, ${rgba(C.cobalt, 0.5)} 0%, ${rgba(C.cobalt, 0)} 66%)`, 0.55 + pulse(HIT1, 0.25) + pulse(HIT2, 0.15) + pulse(HIT3, 0.25))}
      {f >= HIT1 && disc(960, 540, 760, `radial-gradient(circle, ${rgba(C.m500, 1)} 0%, ${rgba(C.m500, 0)} 68%)`, pulse(HIT1, 0.16), 'screen')}
      {f >= HIT2 && disc(960, 560, 760, `radial-gradient(circle, ${rgba(C.m500, 1)} 0%, ${rgba(C.m500, 0)} 68%)`, pulse(HIT2, 0.1), 'screen')}
      {f >= HIT3 && disc(960, 851, 820, `radial-gradient(circle, ${rgba(C.m500, 1)} 0%, ${rgba(C.m500, 0)} 68%)`, pulse(HIT3, 0.16), 'screen')}
    </>
  );
};

const nr = mulberry32(7117);
const NET = Array.from({length: 46}, (_, i) => ({x: -40 + nr() * 2000, y: -40 + nr() * 1160, kind: Math.floor(nr() * 5), i}));
const EDGES: [number, number][] = [];
{
  const seen = new Set<string>();
  NET.forEach((a, i) => {
    NET.map((b, j) => ({j, d: Math.hypot(a.x - b.x, a.y - b.y)}))
      .filter((o) => o.j !== i && o.d < 340)
      .sort((p, q) => p.d - q.d)
      .slice(0, 2)
      .forEach((o) => {
        const key = i < o.j ? `${i}-${o.j}` : `${o.j}-${i}`;
        if (!seen.has(key)) {
          seen.add(key);
          EDGES.push([i, o.j]);
        }
      });
  });
}
const ACTIVE = new Set([5, 19, 33]);

const Network: React.FC = () => {
  const f = useCurrentFrame();
  const at = (n: (typeof NET)[number]) => ({x: n.x + noise1(f / 110 + n.i * 3.1, n.i + 1) * 18, y: n.y + noise1(f / 130 + n.i * 2.3, n.i + 77) * 18});
  const pos = NET.map(at);
  return (
    <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
      {EDGES.map(([a, b], k) => {
        const start = 58 + k * 2.2;
        const p = ease.out(clamp01((f - start) / 14));
        if (p <= 0) return null;
        return <path key={k} d={`M${pos[a].x.toFixed(1)} ${pos[a].y.toFixed(1)}L${pos[b].x.toFixed(1)} ${pos[b].y.toFixed(1)}`} stroke={C.nickel} strokeWidth={2} fill="none" pathLength={1} strokeDasharray="1" strokeDashoffset={1 - p} opacity={0.11} />;
      })}
      {NET.map((n) => {
        const q = pos[n.i];
        const act = ACTIVE.has(n.i);
        const pulse = act ? Math.max(0, Math.exp(-(f - HIT2) / 20) * (f >= HIT2 ? 1 : 0), Math.exp(-(f - HIT3) / 20) * (f >= HIT3 ? 1 : 0)) : 0;
        const col = act ? C.m400 : C.nickel;
        const o = act ? 0.1 + 0.05 * pulse : 0.13;
        switch (n.kind) {
          case 0:
            return <circle key={n.i} cx={q.x} cy={q.y} r={7} fill={col} opacity={o} />;
          case 1:
            return <rect key={n.i} x={q.x - 6} y={q.y - 6} width={12} height={12} rx={3} fill={col} opacity={o} />;
          case 2:
            return <path key={n.i} d={`M${q.x - 8} ${q.y}A8 8 0 0 1 ${q.x + 8} ${q.y}Z`} fill={col} opacity={o} />;
          case 3:
            return <circle key={n.i} cx={q.x} cy={q.y} r={7} fill="none" stroke={col} strokeWidth={2.5} opacity={o} />;
          default:
            return <rect key={n.i} x={q.x - 4} y={q.y - 8} width={8} height={16} rx={4} fill={col} opacity={o} />;
        }
      })}
    </svg>
  );
};

const BOKEH = [
  {x: 140, y: 170, r: 110, i: 0},
  {x: 1800, y: 120, r: 90, i: 1},
  {x: 1700, y: 900, r: 130, i: 2},
  {x: 230, y: 880, r: 100, i: 3},
];
const Bokeh: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <>
      {BOKEH.map((b) => {
        const x = b.x + noise1(f / 170 + b.i * 9, b.i + 5) * 34;
        const y = b.y + noise1(f / 200 + b.i * 7, b.i + 41) * 34;
        return <div key={b.i} style={{position: 'absolute', left: x - b.r, top: y - b.r, width: b.r * 2, height: b.r * 2, borderRadius: '50%', background: `radial-gradient(circle, ${rgba(C.pearl, 0.08)} 0%, ${rgba(C.pearl, 0)} 70%)`}} />;
      })}
    </>
  );
};

// ---------- stage: wordmark, audience line, hero line, CTA ----------
const Wordmark: React.FC = () => {
  const f = useCurrentFrame();
  const p = ease.out(clamp01((f - 6) / 9));
  if (p <= 0) return null;
  return (
    <div style={{position: 'absolute', left: 960 - WM_W / 2, top: wmCy(f) - WM_H / 2, width: WM_W, height: WM_H, opacity: Math.min(1, p * 3), clipPath: `inset(0 ${(1 - p) * 50}% 0 ${(1 - p) * 50}%)`}}>
      <Img src={staticFile('brand/wordmark-inverse.svg')} style={{width: WM_W, height: WM_H, display: 'block'}} />
    </div>
  );
};

const HERO = [
  ['Make', 'the', 'right', 'buyers'],
  ['care', 'about', 'you', 'and'],
  ['what', 'you\u2019re', 'building.'],
];

const Hero: React.FC = () => {
  const f = useCurrentFrame();
  let k = 0;
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: HERO_TOP, textAlign: 'center', color: C.pearl, ...T.headline}}>
      {HERO.map((line, li) => (
        <div key={li} style={{whiteSpace: 'nowrap', height: HERO_LINE}}>
          {line.map((w, wi) => {
            const start = HERO_AT + k++ * HERO_STAGGER;
            const p = ease.out(clamp01((f - start) / 16));
            const isCare = li === 1 && wi === 0;
            return (
              <span key={wi} style={{display: 'inline-block', marginRight: wi < line.length - 1 ? '0.26em' : 0, opacity: p, transform: `translateY(${(1 - p) * 36}px)`, filter: p < 1 ? `blur(${(1 - p) * 10}px)` : undefined}}>
                {isCare ? <InkMarker at={CARE_AT + 4} dur={12}>{w}</InkMarker> : w}
              </span>
            );
          })}
        </div>
      ))}
    </div>
  );
};

const mix = (a: string, b: string, t: number) => {
  const x = parseInt(a.slice(1), 16);
  const y = parseInt(b.slice(1), 16);
  const c = (s: number) => Math.round(((x >> s) & 255) * (1 - t) + ((y >> s) & 255) * t);
  return `rgb(${c(16)}, ${c(8)}, ${c(0)})`;
};

const Cta: React.FC = () => {
  const f = useCurrentFrame();
  if (f < CTA_AT) return null;
  const sp = spring({frame: f - CTA_AT, fps: 30, config: {damping: 16, stiffness: 180, mass: 0.8}});
  const press = clamp01((f - PRESS) / 4) * (1 - clamp01((f - PRESS - 8) / 8));
  const rp = clamp01((f - PRESS) / 16);
  const d = 60 + 760 * ease.out(rp);
  return (
    <div style={{position: 'absolute', left: 0, right: 0, top: CTA_TOP, display: 'flex', justifyContent: 'center'}}>
      <div
        style={{
          position: 'relative',
          overflow: 'hidden',
          height: CTA.h,
          boxSizing: 'border-box',
          padding: '0 80px',
          display: 'flex',
          alignItems: 'center',
          borderRadius: 999,
          background: mix(C.m500, C.m600, press),
          color: C.navy,
          fontFamily: T.body.fontFamily,
          fontWeight: 600,
          fontSize: 64,
          lineHeight: 1,
          letterSpacing: '0',
          opacity: clamp01((f - CTA_AT) / 6),
          transform: `scale(${(0.9 + 0.1 * sp) * (1 - 0.05 * press)})`,
        }}
      >
        {f >= PRESS && rp < 1 && <span style={{position: 'absolute', left: '50%', top: '50%', width: d, height: d, marginLeft: -d / 2, marginTop: -d / 2, borderRadius: '50%', background: C.white, opacity: 0.32 * (1 - rp)}} />}
        <span style={{position: 'relative'}}>Book an intro call</span>
      </div>
    </div>
  );
};

export const S9: React.FC = () => {
  return (
    <AbsoluteFill style={{background: C.navy}}>
      <CameraRig keys={CAM} drift={4} seed={31}>
        <Layer depth={0}>
          <Glows />
        </Layer>
        <Layer depth={0.6}>
          <Thump>
            <Network />
          </Thump>
        </Layer>
        <Layer depth={1.6}>
          <Thump>
            <Bokeh />
          </Thump>
        </Layer>
        <Layer depth={0.3}>
          <Fx hits={HITS} hard={hardRects} soft={softRects} />
          <Wordmark />
          <div style={{position: 'absolute', left: 0, right: 0, top: MONO_TOP, textAlign: 'center', color: C.pearl, ...T.label}}>
            <Words text="For Europe-based B2B AI SaaS founders" at={MONO_AT} stagger={3} dur={14} rise={20} blur={6} />
          </div>
          <Hero />
          <Cta />
        </Layer>
      </CameraRig>
      <Vignette strength={0.5} />
      <Flash at={HIT1} alpha={0.2} color={C.m100} />
      <Flash at={HIT3} alpha={0.14} color={C.m100} />
      <FictionalTag text="Illustrative" at={30} />
    </AbsoluteFill>
  );
};
