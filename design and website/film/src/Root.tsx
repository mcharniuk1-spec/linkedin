import React from 'react';
import {AbsoluteFill, Composition} from 'remotion';
import {FontLoader} from './kit/fonts';
import {Film, SCENE_COMPONENTS} from './Film';
import {FPS, SCENES, TOTAL_FRAMES} from './timeline';
import {TEASER_FRAMES, Teaser} from './Teaser';

const standalone = (id: string): React.FC => {
  const Comp = SCENE_COMPONENTS[id];
  return () => (
    <AbsoluteFill>
      <FontLoader />
      <Comp />
    </AbsoluteFill>
  );
};

export const Root: React.FC = () => (
  <>
    <Composition id="Master" component={Film} durationInFrames={TOTAL_FRAMES} fps={FPS} width={1920} height={1080} />
    <Composition id="Teaser" component={Teaser} durationInFrames={TEASER_FRAMES} fps={FPS} width={1920} height={1080} />
    {SCENES.map((s) => (
      <Composition key={s.id} id={`Scene-${s.id}`} component={standalone(s.id)} durationInFrames={s.frames} fps={FPS} width={1920} height={1080} />
    ))}
  </>
);
