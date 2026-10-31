import React from 'react';
import {AbsoluteFill, Sequence} from 'remotion';
import {FontLoader} from './kit/fonts';
import {Enter, Scene} from './kit/Scene';
import {C} from './kit/tokens';
import {SCENE_COMPONENTS} from './Film';
import {FPS, sf} from './timeline';
import teaser from './teaser.json';

const XF = teaser.crossfadeFrames;
type Seg = {scene: string; from: number; to: number; enter: string};

/** Start frame of each segment on the teaser timeline (segments overlap by the crossfade). */
const layout = (segs: Seg[]) => {
  let at = 0;
  return segs.map((s, i) => {
    const frames = sf(s.to) - sf(s.from);
    const start = i === 0 ? 0 : at - XF;
    at = start + frames;
    return {...s, start, frames};
  });
};
export const TEASER_SEGMENTS = layout(teaser.segments as Seg[]);
export const TEASER_FRAMES = TEASER_SEGMENTS[TEASER_SEGMENTS.length - 1].start + TEASER_SEGMENTS[TEASER_SEGMENTS.length - 1].frames;

const enterFor = (type: string): Enter =>
  type === 'none' ? {type: 'none', frames: 1} : ({type, frames: XF, x: 960, y: 540, color: C.m500} as Enter);

/** A re-cut of the master: segments of scenes with negative offsets so each starts mid-scene, joined with the master's own transitions. */
export const Teaser: React.FC = () => (
  <AbsoluteFill style={{background: C.navy}}>
    <FontLoader />
    {TEASER_SEGMENTS.map((s, i) => {
      const Comp = SCENE_COMPONENTS[s.scene];
      const next = TEASER_SEGMENTS[i + 1];
      return (
        <Sequence key={i} from={s.start} durationInFrames={s.frames + (next ? XF : 0)} name={`${s.scene} ${s.from}-${s.to}s`} layout="none">
          <Scene enter={enterFor(s.enter)} background="transparent">
            <Sequence from={-sf(s.from)} layout="none">
              <Comp />
            </Sequence>
          </Scene>
        </Sequence>
      );
    })}
  </AbsoluteFill>
);

export const TEASER_FPS = FPS;
