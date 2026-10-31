import React, {createContext, useContext} from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {ease} from './ease';
import {noise1} from './rng';

export type CamKey = {f: number; x?: number; y?: number; zoom?: number; rot?: number};
type Cam = {x: number; y: number; zoom: number; rot: number};

const CamCtx = createContext<Cam>({x: 0, y: 0, zoom: 1, rot: 0});

const channel = (keys: CamKey[], frame: number, pick: 'x' | 'y' | 'zoom' | 'rot', fallback: number) => {
  const frames: number[] = [];
  const values: number[] = [];
  let last = fallback;
  for (const k of keys) {
    const v = k[pick];
    if (v !== undefined) last = v;
    frames.push(k.f);
    values.push(last);
  }
  if (frames.length === 1) return values[0];
  return interpolate(frame, frames, values, {easing: ease.cam, extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
};

/**
 * Virtual camera for one scene. Keys are scene-local frames. `drift` adds a slow handheld-like wander (px).
 * Children wrapped in <Layer depth={d}> move by -camera*d (parallax) and scale by 1 + (zoom-1)*d.
 */
export const CameraRig: React.FC<{keys: CamKey[]; drift?: number; seed?: number; children: React.ReactNode}> = ({keys, drift = 0, seed = 7, children}) => {
  const frame = useCurrentFrame();
  const cam: Cam = {
    x: channel(keys, frame, 'x', 0) + drift * noise1(frame / 70, seed),
    y: channel(keys, frame, 'y', 0) + drift * noise1(frame / 83, seed + 11),
    zoom: channel(keys, frame, 'zoom', 1),
    rot: channel(keys, frame, 'rot', 0) + drift * 0.004 * noise1(frame / 97, seed + 23),
  };
  return <CamCtx.Provider value={cam}>{children}</CamCtx.Provider>;
};

export const useCam = () => useContext(CamCtx);

/** depth 0 = pinned background, 1 = the focal plane, >1 = foreground that sweeps faster. */
export const Layer: React.FC<{depth?: number; style?: React.CSSProperties; children?: React.ReactNode}> = ({depth = 1, style, children}) => {
  const c = useCam();
  const z = 1 + (c.zoom - 1) * depth;
  return (
    <AbsoluteFill style={{transform: `translate3d(${-c.x * depth}px, ${-c.y * depth}px, 0) rotate(${c.rot * depth}deg) scale(${z})`, transformOrigin: '50% 50%', ...style}}>
      {children}
    </AbsoluteFill>
  );
};
