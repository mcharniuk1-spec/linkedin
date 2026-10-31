import React, {useEffect, useState} from 'react';
import {continueRender, delayRender, staticFile} from 'remotion';

const FACES = [
  {family: 'Fraunces', file: 'fonts/fraunces-latin-full-normal.woff2', weight: '100 900'},
  {family: 'Mona Sans', file: 'fonts/mona-sans-latin-wght-normal.woff2', weight: '200 900'},
  {family: 'Geist Mono', file: 'fonts/geist-mono-latin-wght-normal.woff2', weight: '100 900'},
];

/** Mount once per composition: holds the render until the three brand fonts are loaded. */
export const FontLoader: React.FC = () => {
  const [handle] = useState(() => delayRender('brand fonts'));
  useEffect(() => {
    Promise.all(
      FACES.map(async (f) => {
        const face = new FontFace(f.family, `url(${staticFile(f.file)}) format("woff2")`, {weight: f.weight});
        await face.load();
        document.fonts.add(face);
      }),
    )
      .then(() => continueRender(handle))
      .catch((e) => {
        console.error('font load failed', e);
        continueRender(handle);
      });
  }, [handle]);
  return null;
};
