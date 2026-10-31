import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {ease} from './ease';
import {C} from './tokens';

export type Enter = {
  type: 'none' | 'bloom' | 'shutter' | 'iris' | 'wipe' | 'push';
  frames: number;
  x?: number; // bloom centre px
  y?: number;
  color?: string; // ring colour
};

/**
 * Scene wrapper. Place inside a <Sequence>: the incoming scene is revealed over the tail of the previous one,
 * so the previous scene must be mounted for `enter.frames` frames longer than its own length.
 */
export const Scene: React.FC<{enter?: Enter; background?: string; children?: React.ReactNode}> = ({enter, background = C.navy, children}) => {
  const frame = useCurrentFrame();
  const {width, height} = useVideoConfig();
  const e = enter ?? {type: 'none', frames: 1};
  const p = e.type === 'none' ? 1 : interpolate(frame, [0, e.frames], [0, 1], {easing: ease.inOut, extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const style: React.CSSProperties = {background};
  let overlay: React.ReactNode = null;
  if (p < 1) {
    const cx = e.x ?? width / 2;
    const cy = e.y ?? height / 2;
    if (e.type === 'bloom') {
      const maxR = Math.hypot(Math.max(cx, width - cx), Math.max(cy, height - cy));
      const r = p * maxR;
      style.clipPath = `circle(${r}px at ${cx}px ${cy}px)`;
      overlay = (
        <svg width={width} height={height} style={{position: 'absolute', inset: 0}}>
          <circle cx={cx} cy={cy} r={r} fill="none" stroke={e.color ?? C.m500} strokeWidth={Math.max(2, 14 * (1 - p))} opacity={1 - p * 0.6} />
        </svg>
      );
    } else if (e.type === 'shutter') {
      const strips = 12;
      const w = width / strips;
      style.WebkitMaskImage = `repeating-linear-gradient(90deg, #000 0px, #000 ${w * p}px, transparent ${w * p}px, transparent ${w}px)`;
      style.maskImage = style.WebkitMaskImage;
    } else if (e.type === 'iris') {
      const ix = (1 - p) * (width / 2 - 40);
      const iy = (1 - p) * (height / 2 - 40);
      style.clipPath = `inset(${iy}px ${ix}px ${iy}px ${ix}px round ${28 + (1 - p) * 60}px)`;
    } else if (e.type === 'wipe') {
      const edge = p * (width + 400) - 200;
      style.clipPath = `polygon(0 0, ${edge + 200}px 0, ${edge}px ${height}px, 0 ${height}px)`;
    } else if (e.type === 'push') {
      style.transform = `translate3d(${(1 - p) * width * 0.35}px,0,0)`;
      style.opacity = Math.min(1, p * 2.2);
    }
  }
  return (
    <AbsoluteFill style={style}>
      {children}
      {overlay}
    </AbsoluteFill>
  );
};
