// S4 helper: category labels, the white post card born from the core, the founder avatar disc, and the headline block.
import React from 'react';
import {useCurrentFrame} from 'remotion';
import {ease} from '../kit/ease';
import {C, SHAPE, T} from '../kit/tokens';
import {Words} from '../kit/Type';
import {BOOM, clamp01, CORE, TICKS} from './S4.field';
import {InkMarker} from './S4.S9.shared';

// ---------- category labels (one at a time, label 56) ----------
const LABELS = [
  {text: 'Decisions', glyph: 'diamond' as const},
  {text: 'Trade-offs', glyph: 'pair' as const},
  {text: 'Product', glyph: 'hex' as const},
];
const IN = 8;
const HOLD = 20;
const OUT = 6;

const Glyph: React.FC<{kind: 'diamond' | 'pair' | 'hex'}> = ({kind}) => {
  const hexPts = Array.from({length: 6}, (_, k) => `${(28 + Math.cos(((60 * k - 90) * Math.PI) / 180) * 24).toFixed(1)},${(28 + Math.sin(((60 * k - 90) * Math.PI) / 180) * 24).toFixed(1)}`).join(' ');
  return (
    <svg width={56} height={56} viewBox="0 0 56 56" style={{flex: 'none'}}>
      {kind === 'diamond' && <polygon points="28,3 53,28 28,53 3,28" fill={C.m400} />}
      {kind === 'pair' && (
        <>
          <line x1={17} y1={28} x2={39} y2={28} stroke={C.nickel} strokeWidth={3} strokeDasharray="4 4" />
          <circle cx={11} cy={28} r={9} fill="none" stroke={C.pearl} strokeWidth={4} />
          <circle cx={45} cy={28} r={9} fill="none" stroke={C.pearl} strokeWidth={4} />
        </>
      )}
      {kind === 'hex' && <polygon points={hexPts} fill={C.nickel} />}
    </svg>
  );
};

export const Labels: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <>
      {LABELS.map((l, i) => {
        const at = TICKS[i];
        const inP = ease.out(clamp01((f - at) / IN));
        const outP = clamp01((f - (at + IN + HOLD)) / OUT);
        const a = inP * (1 - outP);
        if (a <= 0.005) return null;
        return (
          <div key={l.text} style={{position: 'absolute', left: 0, right: 0, top: 822, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 24, opacity: a, transform: `translateY(${(1 - inP) * 16 - outP * 8}px)`}}>
            <Glyph kind={l.glyph} />
            <span style={{...T.label, color: C.pearl}}>{l.text}</span>
          </div>
        );
      })}
    </>
  );
};

// ---------- the post card ----------
export const CARD = {x: 1030, y: 270, w: 640, h: 540} as const;
const CARD_C = {x: CARD.x + CARD.w / 2, y: CARD.y + CARD.h / 2};
const AV_LOCAL = {x: 40 + 36, y: 40 + 36};
export const HEAD_AT = BOOM + 30; // the headline starts after the 30 frames of calm
export const LABEL_AT = BOOM + 56;
const EXIT_AT = 258;
const EXIT_DUR = 28;

/** Card transform: starts as a small white square at the core and settles to its place; leaves again at the end of the scene. */
const cardT = (f: number) => {
  const e = ease.out(clamp01((f - BOOM) / 32));
  const sc = 0.14 + 0.86 * e;
  return {e, sc, tx: (1 - e) * (CORE.x - CARD_C.x), ty: 0};
};
const exitP = (f: number) => ease.inOut(clamp01((f - EXIT_AT) / EXIT_DUR));
const fadeP = (f: number) => clamp01((f - EXIT_AT) / 14);

const appear = (f: number, at: number, dur = 10) => ease.out(clamp01((f - at) / dur));
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

const Bar: React.FC<{x: number; y: number; w: number; h: number; a: number; o: number}> = ({x, y, w, h, a, o}) => (
  <div style={{position: 'absolute', left: x, top: y, width: w * a, height: h, borderRadius: h / 2, background: C.nickel, opacity: o * a}} />
);

export const Card: React.FC = () => {
  const f = useCurrentFrame();
  if (f < BOOM) return null;
  const {e, sc, tx, ty} = cardT(f);
  const ex = exitP(f);
  const fd = fadeP(f);
  const body = clamp01((e - 0.5) / 0.4);
  const wave = Array.from({length: 9}, (_, i) => {
    const base = [34, 58, 84, 48, 100, 62, 88, 44, 30][i];
    return base * (0.78 + 0.22 * Math.sin(f * 0.17 + i * 0.95));
  });
  return (
    <div
      style={{
        position: 'absolute',
        left: CARD.x,
        top: CARD.y,
        width: CARD.w,
        height: CARD.h,
        borderRadius: SHAPE.radiusPanel,
        background: C.white,
        opacity: 1 - fd,
        transform: `translate(${tx}px, ${ty}px) scale(${sc * (1 - 0.05 * fd)})`,
        transformOrigin: '50% 50%',
        overflow: 'hidden',
      }}
    >
      <div style={{position: 'absolute', inset: 0, opacity: body}}>
        <Bar x={136} y={52} w={250} h={22} a={appear(f, BOOM + 9)} o={0.9} />
        <Bar x={136} y={86} w={160} h={16} a={appear(f, BOOM + 11)} o={0.55} />
        <Bar x={40} y={148} w={560} h={22} a={appear(f, BOOM + 13, 12)} o={0.85} />
        <Bar x={40} y={186} w={560} h={22} a={appear(f, BOOM + 16, 12)} o={0.85} />
        <Bar x={40} y={224} w={380} h={22} a={appear(f, BOOM + 19, 12)} o={0.85} />
        <div style={{position: 'absolute', left: 40, top: 282, width: 560, height: 218, borderRadius: SHAPE.radiusMedia, background: `linear-gradient(135deg, ${C.cobalt} 0%, ${C.navy} 100%)`, opacity: appear(f, BOOM + 12, 14), overflow: 'hidden'}}>
          <div style={{position: 'absolute', left: 0, right: 0, top: 109 - 56, height: 112, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 14}}>
            {wave.map((h, i) => (
              <div key={i} style={{width: 14, height: h, borderRadius: 7, background: C.pearl, opacity: 0.92}} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// ---------- founder avatar disc: sits on the card, then travels to (960, 540) for S5 ----------
export const Avatar: React.FC = () => {
  const f = useCurrentFrame();
  if (f < BOOM) return null;
  const {sc, tx, ty} = cardT(f);
  const ex = exitP(f);
  const onCard = {x: CARD_C.x + tx + sc * (AV_LOCAL.x + CARD.x - CARD_C.x), y: CARD_C.y + ty + sc * (AV_LOCAL.y + CARD.y - CARD_C.y)};
  const x = lerp(onCard.x, CORE.x, ex);
  const y = lerp(onCard.y, CORE.y, ex);
  const pop = ease.out(clamp01((f - (BOOM + 4)) / 10));
  const size = 72 * sc * pop;
  return (
    <div style={{position: 'absolute', left: x - size / 2, top: y - size / 2, width: size, height: size, borderRadius: '50%', background: C.m500, border: `${Math.max(2, 4 * sc)}px solid ${C.navy}`, boxSizing: 'border-box'}} />
  );
};

// ---------- headline block (left, safe area) ----------
export const Post: React.FC = () => {
  const f = useCurrentFrame();
  if (f < HEAD_AT - 2) return null;
  const out = 1 - clamp01((f - 262) / 14);
  if (out <= 0) return null;
  const labelA = appear(f, LABEL_AT, 8);
  const bob = Math.sin(f * 0.045) * 3;
  return (
    <div style={{position: 'absolute', left: 170, top: 392 + bob, width: 780, opacity: out}}>
      <div style={{...T.sub, color: C.pearl}}>
        <Words text="Your thinking," at={HEAD_AT} stagger={3} dur={14} rise={30} blur={8} />
        <br />
        <Words text="in *public*." at={HEAD_AT + 6} stagger={3} dur={14} rise={30} blur={8} />
      </div>
      <div style={{marginTop: 46, opacity: labelA, transform: `translateY(${(1 - labelA) * 10}px)`, color: C.pearl, ...T.label}}>
        <InkMarker at={LABEL_AT}>In your voice</InkMarker>
      </div>
    </div>
  );
};
