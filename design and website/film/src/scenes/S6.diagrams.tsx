// S6 mini-scene diagrams. Every component is a pure function of the diagram-local frame `t`
// (frames since that job's label cut) and of the scale `s` it is drawn at. No timers, no randomness at render time.
import React from 'react';
import {ease} from '../kit/ease';
import {mulberry32} from '../kit/rng';
import {C, T} from '../kit/tokens';

export const DW = 740;
export const DH = 300;

export const clamp01 = (x: number) => (x < 0 ? 0 : x > 1 ? 1 : x);
export const lerp = (a: number, b: number, u: number) => a + (b - a) * u;
/** eased progress of t between a and b */
export const pr = (t: number, a: number, b: number, e: (x: number) => number = ease.out) => e(clamp01((t - a) / (b - a)));
/** linear progress */
export const prl = (t: number, a: number, b: number) => clamp01((t - a) / (b - a));

const NS = 'non-scaling-stroke';

/** Rounded-rectangle path (so a stroke can be drawn on with a dash offset). */
const rr = (x: number, y: number, w: number, h: number, r: number) =>
  `M${x + r} ${y} H${x + w - r} A${r} ${r} 0 0 1 ${x + w} ${y + r} V${y + h - r} A${r} ${r} 0 0 1 ${x + w - r} ${y + h} H${x + r} A${r} ${r} 0 0 1 ${x} ${y + h - r} V${y + r} A${r} ${r} 0 0 1 ${x + r} ${y} Z`;

/** Dash props that draw a path (pathLength 1) on from its start; solid once complete. */
const draw = (p: number): React.SVGProps<SVGPathElement> => (p >= 0.999 ? {} : {pathLength: 1, strokeDasharray: '1 1', strokeDashoffset: 1 - p});

const Dia: React.FC<{s: number; children: React.ReactNode}> = ({s, children}) => (
  <svg width={DW * s} height={DH * s} viewBox={`0 0 ${DW} ${DH}`} style={{display: 'block', overflow: 'visible'}}>
    {children}
  </svg>
);

// ---------------------------------------------------------------------------------------------------------------------
// 1 POSITIONING: forty nickel dots, one marigold dot leaves the crowd and settles inside an empty cobalt-rimmed frame.
// ---------------------------------------------------------------------------------------------------------------------
const g1 = mulberry32(6101);
const CROWD = Array.from({length: 40}, (_, i) => ({
  x: 40 + (i % 8) * 52 + (g1() - 0.5) * 26,
  y: 40 + Math.floor(i / 8) * 52 + (g1() - 0.5) * 22,
  r: 9 + g1() * 3.5,
  ph: g1() * 6.283,
}));
const M = 20;
const FR = {x: 450, y: 60, w: 250, h: 180};
const FR_C = {x: FR.x + FR.w / 2, y: FR.y + FR.h / 2};

export const Positioning: React.FC<{t: number; s?: number}> = ({t, s = 1}) => {
  const mu = pr(t, 16, 40, ease.inOut);
  const home = CROWD[M];
  const mx = (1 - mu) * (1 - mu) * home.x + 2 * mu * (1 - mu) * 380 + mu * mu * FR_C.x;
  const my = (1 - mu) * (1 - mu) * home.y + 2 * mu * (1 - mu) * 30 + mu * mu * FR_C.y;
  const pop = pr(t, M * 0.22, M * 0.22 + 10);
  const settle = prl(t, 40, 54);
  const mr = 15 * pop * (1 + 0.4 * Math.sin(Math.PI * settle));
  const ringU = prl(t, 8, 22);
  const small = s < 0.9;
  const dim = (small ? 0.85 : 1) - (small ? 0.15 : 0.38) * prl(t, 24, 44);
  return (
    <Dia s={s}>
      <path d={rr(FR.x, FR.y, FR.w, FR.h, 20)} fill={C.white} fillOpacity={prl(t, 36, 48)} stroke={C.cobalt} strokeWidth={4} vectorEffect={NS} {...draw(pr(t, 4, 22))} />
      {CROWD.map((d, i) => {
        if (i === M) return null;
        const sc = pr(t, i * 0.22, i * 0.22 + 10);
        if (sc < 0.01) return null;
        let x = d.x + 2.2 * Math.sin(t * 0.07 + d.ph);
        let y = d.y + 2.2 * Math.cos(t * 0.06 + d.ph * 1.3);
        const dx = x - mx;
        const dy = y - my;
        const dist = Math.hypot(dx, dy) || 1;
        if (dist < 90 && mu > 0.02) {
          const push = ((90 - dist) / 90) * 22 * Math.min(1, mu * 5);
          x += (dx / dist) * push;
          y += (dy / dist) * push;
        }
        return <circle key={i} cx={x} cy={y} r={d.r * sc * (small ? 1.45 : 1)} fill={C.nickel} opacity={dim} />;
      })}
      {ringU > 0 && ringU < 1 && <circle cx={mx} cy={my} r={18 + 26 * ringU} fill="none" stroke={C.cobalt} strokeWidth={3} vectorEffect={NS} opacity={1 - ringU} />}
      {pop > 0.01 && <circle cx={mx} cy={my} r={mr} fill={C.m500} stroke={C.navy} strokeWidth={4} vectorEffect={NS} />}
    </Dia>
  );
};

// ---------------------------------------------------------------------------------------------------------------------
// 2 PROFILE: a profile skeleton (banner, avatar, headline bar, three lines) assembles from particles.
// ---------------------------------------------------------------------------------------------------------------------
const g2 = mulberry32(6202);
type Spark = {tx: number; ty: number; sx: number; sy: number; r: number};
const swarm = (n: number, bx: number, by: number, bw: number, bh: number): Spark[] =>
  Array.from({length: n}, () => {
    const tx = bx + g2() * bw;
    const ty = by + g2() * bh;
    const ang = g2() * 6.283;
    const d = 120 + g2() * 160;
    return {tx, ty, sx: tx + Math.cos(ang) * d, sy: ty + Math.sin(ang) * d, r: 3.5 + g2() * 2.5};
  });
const BANNER = {x: 100, y: 8, w: 540, h: 104};
const AVATAR = {x: 200, y: 118, r: 50};
const HEADBAR = {x: 270, y: 128, w: 300, h: 26};
const LINES = [
  {x: 150, y: 196, w: 440, h: 18, a: 24},
  {x: 150, y: 230, w: 380, h: 18, a: 30},
  {x: 150, y: 264, w: 300, h: 18, a: 36},
];
const SW = {
  banner: swarm(18, BANNER.x, BANNER.y, BANNER.w, BANNER.h),
  avatar: swarm(10, AVATAR.x - 40, AVATAR.y - 40, 80, 80),
  head: swarm(8, HEADBAR.x, HEADBAR.y, HEADBAR.w, HEADBAR.h),
  lines: LINES.map((l) => swarm(8, l.x, l.y, l.w, l.h)),
};

const Swarm: React.FC<{items: Spark[]; t: number; a: number; color: string; stroke?: string}> = ({items, t, a, color, stroke}) => {
  const p = pr(t, a, a + 14);
  const op = prl(t, a, a + 3) * (1 - prl(t, a + 10, a + 20));
  if (op <= 0.01) return null;
  return (
    <g>
      {items.map((d, i) => (
        <circle key={i} cx={lerp(d.sx, d.tx, p)} cy={lerp(d.sy, d.ty, p)} r={d.r} fill={color} stroke={stroke} strokeWidth={stroke ? 2 : 0} vectorEffect={NS} opacity={op} />
      ))}
    </g>
  );
};

export const Profile: React.FC<{t: number; s?: number}> = ({t, s = 1}) => (
  <Dia s={s}>
    <path d={rr(BANNER.x, BANNER.y, BANNER.w, BANNER.h, 16)} fill={C.white} stroke={C.cobalt} strokeWidth={4} vectorEffect={NS} opacity={prl(t, 8, 18)} />
    <Swarm items={SW.banner} t={t} a={0} color={C.cobalt} />
    <Swarm items={SW.avatar} t={t} a={8} color={C.m500} stroke={C.navy} />
    <circle cx={AVATAR.x} cy={AVATAR.y} r={AVATAR.r * pr(t, 18, 28, ease.snap)} fill={C.m500} stroke={C.navy} strokeWidth={5} vectorEffect={NS} />
    <Swarm items={SW.head} t={t} a={16} color={C.navy} />
    <rect x={HEADBAR.x} y={HEADBAR.y} width={HEADBAR.w * pr(t, 26, 38)} height={HEADBAR.h} rx={13} fill={C.navy} />
    {LINES.map((l, i) => (
      <g key={i}>
        <Swarm items={SW.lines[i]} t={t} a={l.a} color={C.cobalt} />
        <rect x={l.x} y={l.y} width={l.w * pr(t, l.a + 8, l.a + 20)} height={l.h} rx={9} fill={C.nickel} />
      </g>
    ))}
  </Dia>
);

// ---------------------------------------------------------------------------------------------------------------------
// 3 CONTENT STRATEGY: seven dots on a shallow arc light one by one, a cadence.
// ---------------------------------------------------------------------------------------------------------------------
const A0 = {x: 50, y: 232};
const A1 = {x: 370, y: -48};
const A2 = {x: 690, y: 232};
const bez = (u: number) => ({
  x: (1 - u) * (1 - u) * A0.x + 2 * u * (1 - u) * A1.x + u * u * A2.x,
  y: (1 - u) * (1 - u) * A0.y + 2 * u * (1 - u) * A1.y + u * u * A2.y,
});
const ARC_N = 240;
const arcCum: number[] = [0];
{
  let prev = bez(0);
  for (let i = 1; i <= ARC_N; i++) {
    const q = bez(i / ARC_N);
    arcCum.push(arcCum[i - 1] + Math.hypot(q.x - prev.x, q.y - prev.y));
    prev = q;
  }
}
const ARC_PATH = `M${A0.x} ${A0.y} Q${A1.x} ${A1.y} ${A2.x} ${A2.y}`;
const DOTS = Array.from({length: 7}, (_, i) => ({...bez(i / 6), lit: 4 + i * 6, s: arcCum[Math.round((i / 6) * ARC_N)] / arcCum[ARC_N]}));
const litFraction = (t: number) => {
  if (t <= DOTS[0].lit) return 0;
  for (let i = 1; i < DOTS.length; i++) {
    if (t <= DOTS[i].lit) return lerp(DOTS[i - 1].s, DOTS[i].s, (t - DOTS[i - 1].lit) / (DOTS[i].lit - DOTS[i - 1].lit));
  }
  return 1;
};
const BASE_Y = 284;

export const Strategy: React.FC<{t: number; s?: number}> = ({t, s = 1}) => {
  const head = t >= 48 ? (((t - 48) / 6) % 7) : -1;
  const hi = Math.floor(head);
  const hf = head - hi;
  return (
    <Dia s={s}>
      <line x1={30} y1={BASE_Y} x2={30 + 680 * pr(t, 0, 14)} y2={BASE_Y} stroke={C.nickel} strokeWidth={3} vectorEffect={NS} strokeLinecap="round" />
      <path d={ARC_PATH} fill="none" stroke={C.nickel} strokeWidth={3} vectorEffect={NS} strokeLinecap="round" {...draw(pr(t, 0, 14))} />
      {litFraction(t) > 0.001 && <path d={ARC_PATH} fill="none" stroke={C.cobalt} strokeWidth={5} vectorEffect={NS} strokeLinecap="round" {...draw(litFraction(t))} />}
      {DOTS.map((d, i) => {
        const p = prl(t, d.lit, d.lit + 7);
        const lit = p > 0.3;
        const r = lerp(15, 20, p) + 5 * Math.sin(Math.PI * p);
        const stem = pr(t, d.lit + 2, d.lit + 12);
        const ring = prl(t, d.lit, d.lit + 14);
        const idle = hi === i ? hf : -1;
        return (
          <g key={i}>
            <line x1={d.x} y1={d.y + r} x2={d.x} y2={lerp(d.y + r, BASE_Y, stem)} stroke={C.navy} strokeWidth={3} vectorEffect={NS} opacity={stem > 0 ? 1 : 0} />
            <circle cx={d.x} cy={BASE_Y} r={6 * stem} fill={C.navy} />
            {ring > 0 && ring < 1 && <circle cx={d.x} cy={d.y} r={20 + 24 * ring} fill="none" stroke={C.cobalt} strokeWidth={3} vectorEffect={NS} opacity={1 - ring} />}
            {idle >= 0 && <circle cx={d.x} cy={d.y} r={24 + 14 * idle} fill="none" stroke={C.cobalt} strokeWidth={3} vectorEffect={NS} opacity={1 - idle} />}
            <circle cx={d.x} cy={d.y} r={r} fill={lit ? C.m500 : C.nickel} stroke={lit ? C.navy : 'none'} strokeWidth={4} vectorEffect={NS} />
          </g>
        );
      })}
    </Dia>
  );
};

// ---------------------------------------------------------------------------------------------------------------------
// 4 WRITING: a generic draft line is struck through, then a replacement line of live type that sounds human.
// ---------------------------------------------------------------------------------------------------------------------
const DRAFT = ['Innovative', 'solutions.'];
const REPLACEMENT = 'Here’s what broke.';

export const Writing: React.FC<{t: number; s?: number; mix?: number}> = ({t, s = 1, mix = 0}) => {
  const strike = pr(t, 26, 33, ease.inOut);
  const typed = Math.floor(prl(t, 48, 66) * REPLACEMENT.length);
  const typing = t >= 48 && t < 66;
  const caretOn = typing || (t >= 66 && t < 90 && Math.floor((t - 66) / 7) % 2 === 0);
  const dotPop = pr(t, 44, 52, ease.snap);
  // the struck draft hands over to a quiet bar (the draft is spent), so only the new line stays as text
  const draftText = 1 - prl(t, 36, 42);
  const draftBar = prl(t, 36, 43);
  const textOp = 1 - clamp01(mix * 2);
  const barOp = clamp01(mix * 2 - 1);
  return (
    <div style={{position: 'relative', width: DW * s, height: DH * s}}>
      <svg width={DW * s} height={DH * s} viewBox={`0 0 ${DW} ${DH}`} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
        <g opacity={draftBar * (1 - barOp) + barOp}>
          <rect x={20} y={41} width={640} height={20} rx={10} fill={C.navy} opacity={0.3} />
          <line x1={10} y1={51} x2={670} y2={51} stroke={C.navy} strokeWidth={5} vectorEffect={NS} strokeLinecap="round" />
        </g>
        <g opacity={barOp}>
          <circle cx={34} cy={196} r={20} fill={C.m500} stroke={C.navy} strokeWidth={4} vectorEffect={NS} />
          <rect x={72} y={186} width={400} height={20} rx={10} fill={C.navy} />
        </g>
      </svg>
      {textOp > 0.001 && (
        <div style={{position: 'absolute', left: 0, top: 0, width: DW, height: DH, transform: `scale(${s})`, transformOrigin: '0 0', opacity: textOp}}>
          {draftText > 0.001 && (
            <div style={{position: 'absolute', left: 14, top: 10, ...T.body, color: C.navy, opacity: draftText, whiteSpace: 'nowrap'}}>
              <span style={{position: 'relative', display: 'inline-block'}}>
                {DRAFT.map((w, i) => {
                  const p = pr(t, 3 + i * 3, 3 + i * 3 + 10);
                  return (
                    <span key={i} style={{display: 'inline-block', opacity: p, transform: `translateY(${(1 - p) * 16}px)`, marginRight: i === 0 ? '0.28em' : 0}}>
                      {w}
                    </span>
                  );
                })}
                {strike > 0.001 && <span style={{position: 'absolute', left: -8, top: '52%', height: 6, width: `calc(${strike * 100}% + 16px)`, background: C.navy, borderRadius: 3}} />}
              </span>
            </div>
          )}
          <div style={{position: 'absolute', left: 14, top: 161, width: 40, height: 40, borderRadius: 20, background: C.m500, border: `4px solid ${C.navy}`, boxSizing: 'border-box', transform: `scale(${dotPop})`, opacity: dotPop > 0 ? 1 : 0}} />
          <div style={{position: 'absolute', left: 72, top: 140, ...T.body, color: C.navy, whiteSpace: 'nowrap'}}>
            {REPLACEMENT.slice(0, typed)}
            <span style={{display: 'inline-block', width: 6, height: '0.88em', background: C.navy, marginLeft: 4, verticalAlign: '-0.1em', opacity: caretOn ? 1 : 0}} />
          </div>
        </div>
      )}
    </div>
  );
};

// ---------------------------------------------------------------------------------------------------------------------
// 5 VISUALS: a publication frame splits into background / subject / label planes and re-locks.
// ---------------------------------------------------------------------------------------------------------------------
const PF = {x: 245, y: 8, w: 250, h: 284};

export const Visuals: React.FC<{t: number; s?: number}> = ({t, s = 1}) => {
  const split = pr(t, 18, 32, ease.out) * (1 - pr(t, 40, 52, ease.inOut));
  const planeOp = prl(t, 6, 16);
  const lockPulse = 1 + 0.035 * Math.sin(Math.PI * prl(t, 50, 60));
  const bob = 3 * Math.sin(t * 0.09);
  const skew = -9 * split;
  const cx = PF.x + PF.w / 2;
  return (
    <Dia s={s}>
      <g transform={`translate(${cx} ${PF.y + PF.h / 2}) scale(${lockPulse}) translate(${-cx} ${-(PF.y + PF.h / 2)})`}>
        <path d={rr(PF.x, PF.y, PF.w, PF.h, 20)} fill={C.white} fillOpacity={prl(t, 4, 14)} stroke={C.cobalt} strokeWidth={4} vectorEffect={NS} strokeDasharray={split > 0.05 ? '10 8' : undefined} {...(split > 0.05 ? {} : draw(pr(t, 0, 14)))} />
        {/* background plane */}
        <g opacity={planeOp} transform={`translate(${-150 * split} ${26 * split}) translate(${cx} 150) skewX(${skew}) translate(${-cx} -150)`}>
          <rect x={PF.x + 14} y={22} width={PF.w - 28} height={PF.h - 28} rx={12} fill={C.cobalt} fillOpacity={0.14} stroke={C.cobalt} strokeWidth={3} vectorEffect={NS} strokeOpacity={split} />
        </g>
        {/* subject plane */}
        <g opacity={planeOp} transform={`translate(0 ${-30 * split + bob * (0.4 + split)}) translate(${cx} 148) scale(${1 + 0.15 * split}) translate(${-cx} -148)`}>
          <circle cx={cx} cy={148} r={56} fill={C.m500} stroke={C.navy} strokeWidth={5} vectorEffect={NS} />
        </g>
        {/* label plane */}
        <g opacity={planeOp} transform={`translate(${150 * split} ${30 * split}) translate(${cx} 249) skewX(${skew}) translate(${-cx} -249)`}>
          <rect x={PF.x + 30} y={220} width={PF.w - 60} height={58} rx={10} fill={C.white} stroke={C.navy} strokeWidth={3} vectorEffect={NS} />
          <rect x={PF.x + 46} y={236} width={118} height={14} rx={7} fill={C.navy} />
          <rect x={PF.x + 46} y={258} width={78} height={10} rx={5} fill={C.nickel} />
        </g>
      </g>
    </Dia>
  );
};

// ---------------------------------------------------------------------------------------------------------------------
// 6 CAMPAIGNS: a dots rhythm and the tag "LinkedIn ads included".
// ---------------------------------------------------------------------------------------------------------------------
const ROW_A = Array.from({length: 14}, (_, i) => ({x: 30 + i * 52.5, w: i % 3 === 0 ? 1 : 0.55}));
const ROW_B = Array.from({length: 7}, (_, i) => ({x: 56 + i * 105}));

export const Campaigns: React.FC<{t: number; s?: number; mix?: number}> = ({t, s = 1, mix = 0}) => {
  const tagIn = pr(t, 15, 23);
  return (
    <div style={{position: 'relative', width: DW * s, height: DH * s}}>
      <svg width={DW * s} height={DH * s} viewBox={`0 0 ${DW} ${DH}`} style={{position: 'absolute', left: 0, top: 0, overflow: 'visible'}}>
        {ROW_A.map((d, i) => {
          const pop = pr(t, i * 1.1, i * 1.1 + 9);
          const ph = (((t - 6 - i * 3) % 24) + 24) % 24 / 24;
          const a = t < 6 ? 0 : ph < 0.25 ? Math.sin((Math.PI * ph) / 0.25) * d.w : 0;
          const on = a > 0.45;
          return <circle key={i} cx={d.x} cy={34} r={12 * pop * (1 + 0.5 * a)} fill={on ? C.m500 : C.nickel} stroke={on ? C.navy : 'none'} strokeWidth={3} vectorEffect={NS} />;
        })}
        {ROW_B.map((d, j) => {
          const pop = pr(t, 12 + j * 1.5, 12 + j * 1.5 + 9);
          const ph = (((t - 10 - j * 6) % 48) + 48) % 48 / 48;
          const a = t < 10 ? 0 : ph < 0.22 ? Math.sin((Math.PI * ph) / 0.22) : 0;
          return <circle key={j} cx={d.x} cy={92} r={(15 + 9 * a) * pop} fill={a > 0.5 ? C.m500 : C.white} stroke={a > 0.5 ? C.navy : C.cobalt} strokeWidth={4} vectorEffect={NS} />;
        })}
        {mix > 0.5 && (
          <g opacity={clamp01(mix * 2 - 1)}>
            <path d={rr(8, 140, 330, 150, 18)} fill="none" stroke={C.navy} strokeWidth={3} vectorEffect={NS} />
            <rect x={36} y={176} width={230} height={18} rx={9} fill={C.navy} />
            <rect x={36} y={214} width={150} height={18} rx={9} fill={C.navy} />
          </g>
        )}
      </svg>
      {mix < 0.5 && tagIn > 0.001 && (
        <div
          style={{
            position: 'absolute', left: 0, top: 136, width: 520, boxSizing: 'border-box', padding: '8px 18px', border: `3px solid ${C.navy}`, borderRadius: 18,
            ...T.label, color: C.navy, opacity: tagIn * (1 - clamp01(mix * 2)), transform: `translateY(${(1 - tagIn) * 14}px) scale(${s})`, transformOrigin: '0 0',
          }}
        >
          LinkedIn ads included
        </div>
      )}
    </div>
  );
};
