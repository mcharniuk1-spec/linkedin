import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {CamKey, CameraRig, Layer} from '../kit/Camera';
import {Marker} from '../kit/Chrome';
import {ease} from '../kit/ease';
import {mulberry32} from '../kit/rng';
import {Scramble, Words} from '../kit/Type';
import {C, SAFE, T} from '../kit/tokens';
import events from './S8.events.json';
import {Dust, evFrame, pr} from './S7.S8.shared';

/**
 * S8 Five Things To Watch. Calm pearl scene: no burst, no additive light. Headline with a struck-out word on the left,
 * five unconnected nodes on a pentagon on the right, a small funnel that draws and shatters.
 */

// ---------- sync frames (from S8.events.json) ----------
const F = {
  words: evFrame(events, 'tick', 0),
  outcomes: evFrame(events, 'tick', 1),
  strike: evFrame(events, 'glitch', 0),
  rings: evFrame(events, 'sparkle', 0),
  caption: evFrame(events, 'tick', 2),
  funnel: evFrame(events, 'riser', 0),
  shatter: evFrame(events, 'glitch', 1),
  time: evFrame(events, 'tick', 3),
  recog: evFrame(events, 'sparkle', 1),
  voice: evFrame(events, 'tick', 4),
  sales: evFrame(events, 'sparkle', 2),
  conv: evFrame(events, 'tick', 5),
  outro: evFrame(events, 'whoosh', 1),
};

// ---------- pentagon ----------
const PC = {x: 1300, y: 540};
const PR = 250;
const NODE_R = 36;
const vert = (k: number) => {
  const a = ((-90 + 72 * k) * Math.PI) / 180;
  return {x: PC.x + PR * Math.cos(a), y: PC.y + PR * Math.sin(a)};
};

type NodeDef = {key: string; v: number; lines: string[]; at: number; above?: boolean; pop: number};
// Spoken order is Time, Recognition, Voice, Sales usefulness, Conversations. The positions make that order jump
// around the pentagon (lower left, upper left, lower right, upper right, top): separate things, never a sequence.
const NODES: NodeDef[] = [
  {key: 'conv', v: 0, lines: ['Conversations'], at: F.conv, above: true, pop: 0},
  {key: 'sales', v: 1, lines: ['Sales', 'usefulness'], at: F.sales, pop: 2},
  {key: 'voice', v: 2, lines: ['Voice'], at: F.voice, pop: 4},
  {key: 'time', v: 3, lines: ['Time'], at: F.time, pop: 1},
  {key: 'recog', v: 4, lines: ['Recognition'], at: F.recog, pop: 3},
];

// ---------- funnel (left column, under the caption) ----------
type Seg = {x1: number; y1: number; x2: number; y2: number};
const split = (x1: number, y1: number, x2: number, y2: number, n: number): Seg[] =>
  Array.from({length: n}, (_, i) => ({x1: x1 + ((x2 - x1) * i) / n, y1: y1 + ((y2 - y1) * i) / n, x2: x1 + ((x2 - x1) * (i + 1)) / n, y2: y1 + ((y2 - y1) * (i + 1)) / n}));
const FUNNEL: Seg[] = [
  ...split(154, 772, 454, 772, 3),
  ...split(154, 772, 276, 854, 3),
  ...split(454, 772, 332, 854, 3),
  ...split(276, 854, 276, 913, 2),
  ...split(332, 854, 332, 913, 2),
  ...split(190, 796, 418, 796, 2),
  ...split(225, 820, 383, 820, 2),
];
const SHARDS = (() => {
  const rnd = mulberry32(88);
  return FUNNEL.map((s) => {
    const cx = (s.x1 + s.x2) / 2;
    const cy = (s.y1 + s.y2) / 2;
    const ax = cx - 304;
    const ay = cy - 838;
    const len = Math.hypot(ax, ay) || 1;
    const dist = 18 + rnd() * 30;
    return {cx, cy, dx: (ax / len) * dist + (rnd() - 0.5) * 16, dy: Math.max(-4, (ay / len) * dist * 0.5 + (rnd() - 0.5) * 18), spin: (rnd() - 0.5) * 80, delay: Math.floor(rnd() * 4)};
  });
})();

const KEYS: CamKey[] = [
  {f: 0, zoom: 1.0, x: 0, y: 0, rot: 0},
  {f: 120, zoom: 1.025, x: 10, y: -4, rot: -0.3},
  {f: 208, zoom: 1.045, x: 18, y: -8, rot: -0.55},
  {f: 246, zoom: 1.07, x: 22, y: -10, rot: -0.7},
];

// ---------- left column ----------
const Strike: React.FC<{at: number; dur?: number}> = ({at, dur = 14}) => {
  const f = useCurrentFrame();
  const p = pr(f, at, at + dur, ease.out);
  return <div style={{position: 'absolute', left: -12, right: -12, top: '57%', height: 10, background: C.navy, borderRadius: 2, transformOrigin: 'left center', transform: `scaleX(${p})`}} />;
};

const LeftColumn: React.FC = () => {
  const f = useCurrentFrame();
  const settle = pr(f, F.strike + 14, F.strike + 40, ease.inOut);
  return (
    <>
      <div style={{position: 'absolute', left: SAFE.titleX, top: 140, ...T.headline, color: C.navy, whiteSpace: 'nowrap'}}>
        <div><Words text="We don’t" at={F.words - 3} /></div>
        <div><Words text="promise" at={F.words + 3} /></div>
        <div style={{position: 'relative', display: 'inline-block'}}>
          <span style={{opacity: 1 - 0.14 * settle}}>
            <Words text="*outcomes.*" at={F.outcomes} emphasis={C.m800} />
          </span>
          <Strike at={F.strike} />
        </div>
      </div>

      <div style={{position: 'absolute', left: SAFE.titleX, top: 596, ...T.caption, fontSize: 56, lineHeight: 1.2, color: C.navy, whiteSpace: 'nowrap'}}>
        <div><Words text="Separate." at={F.caption} dur={14} rise={24} blur={6} /></div>
        <div><Words text="Never a funnel." at={F.caption + 3} dur={14} rise={24} blur={6} /></div>
      </div>

      <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
        {FUNNEL.map((s, i) => {
          const sh = SHARDS[i];
          const draw = pr(f, F.funnel + i * 0.75, F.funnel + i * 0.75 + 9, ease.out);
          if (draw <= 0) return null;
          const u = pr(f, F.shatter + sh.delay, F.shatter + sh.delay + 34, ease.out);
          const a = 1 - pr(f, F.shatter + 4, F.shatter + 36, ease.in);
          if (a <= 0.01) return null;
          const tremble = f >= F.shatter - 5 && f < F.shatter ? (f % 2 === 0 ? 1.6 : -1.6) : 0;
          const dx = sh.dx * u + tremble;
          const dy = sh.dy * u + 12 * u * u;
          return (
            <g key={i} opacity={a} transform={`translate(${dx.toFixed(2)} ${dy.toFixed(2)}) rotate(${(sh.spin * u).toFixed(2)} ${sh.cx} ${sh.cy})`}>
              <line x1={s.x1} y1={s.y1} x2={s.x1 + (s.x2 - s.x1) * draw} y2={s.y1 + (s.y2 - s.y1) * draw} stroke={C.navy} strokeWidth={4} strokeLinecap="round" />
            </g>
          );
        })}
      </svg>
    </>
  );
};

// ---------- pentagon of nodes ----------
const Pentagon: React.FC = () => {
  const f = useCurrentFrame();
  const hush = Math.sin(Math.PI * pr(f, F.conv + 4, 246, ease.inOut));
  return (
    <>
      <svg width={1920} height={1080} style={{position: 'absolute', inset: 0}}>
        <defs>
          <radialGradient id="s8glow">
            <stop offset="0" stopColor={C.cobalt} stopOpacity={0.3} />
            <stop offset="0.6" stopColor={C.cobalt} stopOpacity={0.1} />
            <stop offset="1" stopColor={C.cobalt} stopOpacity={0} />
          </radialGradient>
        </defs>
        {NODES.map((n) => {
          const p = vert(n.v);
          const pop = pr(f, F.rings + n.pop * 9, F.rings + n.pop * 9 + 14, ease.snap);
          if (pop <= 0) return null;
          const lit = pr(f, n.at, n.at + 10, ease.out);
          const dot = pr(f, n.at, n.at + 9, ease.snap);
          const rip = pr(f, n.at, n.at + 26, ease.out);
          const bump = 1 + 0.12 * Math.sin(Math.PI * pr(f, n.at, n.at + 9, ease.out));
          return (
            <g key={n.key} transform={`translate(${p.x.toFixed(1)} ${p.y.toFixed(1)})`}>
              {lit > 0 && <circle r={104 * (1 + 0.1 * hush)} fill="url(#s8glow)" opacity={lit} />}
              {rip > 0 && rip < 1 && <circle r={NODE_R + 52 * rip} fill="none" stroke={C.cobalt} strokeWidth={2} opacity={0.5 * (1 - rip)} />}
              <circle r={NODE_R * (0.4 + 0.6 * pop) * bump} fill={C.white} stroke={C.cobalt} strokeWidth={6 + 3 * lit} opacity={Math.min(1, pop * 1.6)} />
              {dot > 0 && <circle r={17 * dot} fill={C.m500} stroke={C.navy} strokeWidth={3} />}
            </g>
          );
        })}
      </svg>
      {NODES.map((n) => {
        const p = vert(n.v);
        const h = n.lines.length * 67;
        const top = n.above ? p.y - NODE_R - 18 - h : p.y + NODE_R + 18;
        return (
          <div key={n.key} style={{position: 'absolute', left: p.x, top, transform: 'translateX(-50%)', textAlign: 'center', whiteSpace: 'nowrap', ...T.label, lineHeight: 1.2, color: C.navy}}>
            {n.lines.map((line, i) => (
              <div key={i}>
                <Marker at={n.at + 3 + i * 3} dur={10}>
                  <Scramble text={line} at={n.at + i * 2} dur={10} seed={n.v * 7 + i + 2} />
                </Marker>
              </div>
            ))}
          </div>
        );
      })}
    </>
  );
};

export const S8: React.FC = () => {
  return (
    <AbsoluteFill style={{background: C.pearl, overflow: 'hidden'}}>
      <CameraRig keys={KEYS} drift={3} seed={4}>
        {/* far: soft white and cobalt light (parallax 0.6) and dust (0.3) */}
        <Layer depth={0.6}>
          <div style={{position: 'absolute', left: -200, top: -300, width: 1300, height: 1100, background: 'radial-gradient(closest-side, rgba(255,255,255,0.7), rgba(255,255,255,0) 100%)'}} />
          <div style={{position: 'absolute', left: PC.x - 700, top: PC.y - 640, width: 1400, height: 1280, background: 'radial-gradient(closest-side, rgba(49,87,213,0.07), rgba(49,87,213,0) 100%)'}} />
        </Layer>
        <Layer depth={0.3}>
          <Dust count={30} seed={21} color={C.navy} alpha={[0.07, 0.17]} size={[1.5, 3]} vx={-0.06} vy={-0.1} twinkle={0.25} />
        </Layer>

        {/* text column is pinned to the title-safe margin */}
        <Layer depth={0}>
          <LeftColumn />
        </Layer>

        <Layer depth={1} style={{transformOrigin: `${PC.x}px ${PC.y}px`}}>
          <Pentagon />
        </Layer>

        {/* near cobalt bokeh (parallax 1.6), very faint */}
        <Layer depth={1.6}>
          <Dust count={3} seed={33} color={C.cobalt} alpha={[0.035, 0.07]} size={[70, 130]} vx={0.1} vy={-0.07} twinkle={0.2} soft />
        </Layer>
      </CameraRig>
    </AbsoluteFill>
  );
};
