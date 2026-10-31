import {Easing} from 'remotion';

export const ease = {
  out: Easing.bezier(0.22, 1, 0.36, 1), // website brand curve (motion/presets.ts): the default for arrivals
  inOut: Easing.bezier(0.65, 0, 0.35, 1),
  cam: Easing.bezier(0.45, 0, 0.15, 1), // camera moves: slow start, long glide
  snap: Easing.bezier(0.2, 0.8, 0.2, 1), // slightly punchier settle for particle cores and stamps
  in: Easing.bezier(0.7, 0, 0.84, 0),
} as const;
