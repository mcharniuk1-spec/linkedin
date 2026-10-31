import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {ease} from './ease';
import {mulberry32} from './rng';
import {C} from './tokens';

type WordsProps = {
  text: string; // wrap words in *asterisks* to mark the marigold emphasis
  at: number; // scene-local frame where the first word starts
  stagger?: number; // frames between words
  dur?: number; // frames each word takes to settle
  rise?: number; // px each word travels
  blur?: number; // px of blur at start
  emphasis?: string; // colour of *emphasised* words
  style?: React.CSSProperties;
};

/** Word-by-word reveal with rise, blur-in and settle. Static once every word has landed. */
export const Words: React.FC<WordsProps> = ({text, at, stagger = 3, dur = 16, rise = 36, blur = 10, emphasis = C.m400, style}) => {
  const frame = useCurrentFrame();
  const tokens = text.split(/(\*[^*]+\*)/).filter(Boolean).flatMap((part) => {
    const em = part.startsWith('*') && part.endsWith('*');
    return (em ? part.slice(1, -1) : part).split(/(\s+)/).filter(Boolean).map((w) => ({w, em}));
  });
  let wi = 0;
  return (
    <span style={{display: 'inline', ...style}}>
      {tokens.map((t, i) => {
        if (/^\s+$/.test(t.w)) return <span key={i}>{t.w}</span>;
        const start = at + wi++ * stagger;
        const p = interpolate(frame, [start, start + dur], [0, 1], {easing: ease.out, extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
        return (
          <span key={i} style={{display: 'inline-block', opacity: p, transform: `translateY(${(1 - p) * rise}px)`, filter: p < 1 && blur ? `blur(${(1 - p) * blur}px)` : undefined, color: t.em ? emphasis : undefined, whiteSpace: 'pre'}}>
            {t.w}
          </span>
        );
      })}
    </span>
  );
};

const GLYPHS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/+#%';

/** Characters resolve left to right from deterministic noise: for labels and numbers, not for body copy. */
export const Scramble: React.FC<{text: string; at: number; dur?: number; seed?: number; style?: React.CSSProperties}> = ({text, at, dur = 18, seed = 3, style}) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [at, at + dur], [0, 1], {easing: ease.inOut, extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  if (frame < at) return <span style={{...style, opacity: 0}}>{text}</span>;
  const rnd = mulberry32(seed + Math.floor(frame / 2));
  const done = Math.floor(p * text.length);
  const out = text.split('').map((ch, i) => (ch === ' ' || i < done ? ch : GLYPHS[Math.floor(rnd() * GLYPHS.length)])).join('');
  return <span style={style}>{out}</span>;
};
