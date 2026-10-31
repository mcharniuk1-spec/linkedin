// Shared by S4 and S9. Same look as the kit's Marker (marigold-300 bar wiping in from the left, navy ink), but the ink is exact per letter:
// pearl text sits underneath and a navy copy is clipped to the bar's current width on top, so no letter is ever navy on navy mid-wipe.
import React from 'react';
import {interpolate, useCurrentFrame} from 'remotion';
import {ease} from '../kit/ease';
import {C} from '../kit/tokens';

export const InkMarker: React.FC<{children: string; at: number; dur?: number; base?: string}> = ({children, at, dur = 10, base = C.pearl}) => {
  const frame = useCurrentFrame();
  const p = interpolate(frame, [at, at + dur], [0, 1], {easing: ease.out, extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <span style={{position: 'relative', display: 'inline-block', padding: '0 0.14em', whiteSpace: 'pre'}}>
      <span style={{position: 'absolute', inset: '8% 0 4% 0', background: C.m300, transformOrigin: 'left center', transform: `scaleX(${p})`}} />
      <span style={{position: 'relative', color: base}}>{children}</span>
      <span style={{position: 'absolute', inset: 0, padding: '0 0.14em', color: C.navy, whiteSpace: 'pre', clipPath: `inset(0 ${(1 - p) * 100}% 0 0)`}}>{children}</span>
    </span>
  );
};
