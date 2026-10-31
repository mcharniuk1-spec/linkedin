import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {ease} from './ease';
import {C, SAFE, T} from './tokens';

/** Persistent disclosure for anything fictional (founder, accounts, posts). Lower-left, just above the bottom 15 % player-controls zone, never hidden. */
export const FictionalTag: React.FC<{text?: string; at?: number; color?: string; align?: 'left' | 'right'}> = ({text = 'Illustrative · fictional', at = 0, color = C.nickel, align = 'left'}) => {
  const frame = useCurrentFrame();
  const o = interpolate(frame, [at, at + 10], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <div style={{position: 'absolute', ...(align === 'left' ? {left: SAFE.x + 16} : {right: SAFE.x + 16}), bottom: 128, opacity: o * 0.92, color, ...T.caption, fontSize: 40, textShadow: '0 0 18px rgba(7,16,36,0.85)'}}>
      {text}
    </div>
  );
};

/** Marker highlight behind a short phrase: bar wipes in from the left, ink text stays navy (9.94:1). */
export const Marker: React.FC<{children: React.ReactNode; at: number; dur?: number; style?: React.CSSProperties}> = ({children, at, dur = 10, style}) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [at, at + dur], [0, 1], {easing: ease.out, extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <span style={{position: 'relative', display: 'inline-block', padding: '0 0.14em', color: p > 0.5 ? C.navy : undefined, ...style}}>
      <span style={{position: 'absolute', inset: '8% 0 4% 0', background: C.m300, transformOrigin: 'left center', transform: `scaleX(${p})`, zIndex: 0}} />
      <span style={{position: 'relative', zIndex: 1}}>{children}</span>
    </span>
  );
};

/** Soft navy vignette that keeps the corners calm under particle light. */
export const Vignette: React.FC<{strength?: number}> = ({strength = 0.5}) => (
  <AbsoluteFill style={{background: `radial-gradient(120% 100% at 50% 45%, transparent 55%, rgba(7,16,36,${strength}) 100%)`, pointerEvents: 'none'}} />
);

/** Full-frame colour flash obeying the photosensitivity rule (<= 3 frames, alpha <= 0.2). */
export const Flash: React.FC<{at: number; color?: string; alpha?: number}> = ({at, color = C.m500, alpha = 0.2}) => {
  const frame = useCurrentFrame();
  const a = interpolate(frame, [at, at + 1, at + 3], [0, alpha, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{background: color, opacity: a, pointerEvents: 'none'}} />;
};
