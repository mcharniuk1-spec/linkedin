import React from 'react';
import {AbsoluteFill, Sequence} from 'remotion';
import {FontLoader} from './kit/fonts';
import {Enter, Scene} from './kit/Scene';
import {C} from './kit/tokens';
import {SCENES} from './timeline';
import {S1} from './scenes/S1';
import {S2} from './scenes/S2';
import {S3} from './scenes/S3';
import {S4} from './scenes/S4';
import {S5} from './scenes/S5';
import {S6} from './scenes/S6';
import {S7} from './scenes/S7';
import {S8} from './scenes/S8';
import {S9} from './scenes/S9';

export const SCENE_COMPONENTS: Record<string, React.FC> = {S1, S2, S3, S4, S5, S6, S7, S8, S9};

/** How each scene is revealed over the tail of the previous one. S1 has no entry. */
export const ENTER: Record<string, Enter> = {
  S1: {type: 'none', frames: 1},
  S2: {type: 'bloom', frames: 18, x: 960, y: 540, color: C.m500},
  S3: {type: 'iris', frames: 20},
  S4: {type: 'wipe', frames: 14},
  S5: {type: 'bloom', frames: 18, x: 960, y: 540, color: C.m400},
  S6: {type: 'iris', frames: 22},
  S7: {type: 'shutter', frames: 18},
  S8: {type: 'wipe', frames: 14},
  S9: {type: 'bloom', frames: 24, x: 960, y: 540, color: C.m500},
};

export const Film: React.FC = () => (
  <AbsoluteFill style={{background: C.navy}}>
    <FontLoader />
    {SCENES.map((s, i) => {
      const Comp = SCENE_COMPONENTS[s.id];
      const next = SCENES[i + 1];
      const overlap = next ? ENTER[next.id].frames : 0;
      return (
        <Sequence key={s.id} from={s.startFrame} durationInFrames={s.frames + overlap} name={`${s.id} ${s.title}`} layout="none">
          <Scene enter={ENTER[s.id]} background="transparent">
            <Comp />
          </Scene>
        </Sequence>
      );
    })}
  </AbsoluteFill>
);
