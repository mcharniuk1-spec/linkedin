// Brand constants for the film. Colours and radii come from design-system/tokens.json through
// `npm run sync` (src/generated/tokens.json); sizes below are the 1080p film scale (see DESIGN-FIT.md).
import raw from '../generated/tokens.json';

const p = raw.palette;
export const C = {
  navy: p['navy'], cobalt: p['cobalt'], white: p['white'], pearl: p['pearl'], black: p['black'], nickel: p['nickel'],
  m50: p['marigold-50'], m100: p['marigold-100'], m200: p['marigold-200'], m300: p['marigold-300'], m400: p['marigold-400'],
  m500: p['marigold-500'], m600: p['marigold-600'], m700: p['marigold-700'], m800: p['marigold-800'], m900: p['marigold-900'], m950: p['marigold-950'],
} as const;

export const FILM = {fps: 30, w16x9: 1920, h16x9: 1080, w4x5: 1080, h4x5: 1350} as const;

export const FONT = {
  display: '"Fraunces", Georgia, "Times New Roman", serif',
  text: '"Mona Sans", Inter, system-ui, sans-serif',
  mono: '"Geist Mono", ui-monospace, Menlo, monospace',
} as const;

// Film type scale at 1080p (design-system audit, 31 Oct 2026): the web CSS sizes are far too small for a phone-sized feed.
// Fraunces 400 only at >= 80 px, Mona Sans 400 at >= 60 px, Geist Mono 500 uppercase at >= 56 px. Only roman font files ship: no italics.
export const T = {
  display: {fontFamily: FONT.display, fontWeight: 400, fontSize: 200, lineHeight: 1.0, letterSpacing: '-0.02em'},
  headline: {fontFamily: FONT.display, fontWeight: 400, fontSize: 128, lineHeight: 1.05, letterSpacing: '-0.02em'},
  sub: {fontFamily: FONT.display, fontWeight: 400, fontSize: 88, lineHeight: 1.1, letterSpacing: '-0.015em'},
  body: {fontFamily: FONT.text, fontWeight: 400, fontSize: 64, lineHeight: 1.3, letterSpacing: '0'},
  label: {fontFamily: FONT.mono, fontWeight: 500, fontSize: 56, lineHeight: 1.2, letterSpacing: '0.09em', textTransform: 'uppercase'},
  caption: {fontFamily: FONT.mono, fontWeight: 500, fontSize: 52, lineHeight: 1.3, letterSpacing: '0.09em', textTransform: 'uppercase'},
} as const;

/** Safe areas at 1920x1080: action 5 %, title/caption blocks inside the inner box. Nothing meaningful in the bottom 15 %. */
export const SAFE = {x: 96, y: 54, titleX: 154, titleTop: 108, titleBottom: 162} as const;

/** Burst heat ramp over a particle's life (white to deep marigold, then fade into the navy ground, never black). */
export const HEAT = ['#FFFFFF', C.m200, C.m300, C.m400, C.m500, C.m600, C.m800] as const;
/** Weighted particle colours: marigold-500 35 %, 400 25 %, 300 20 %, white 12 %, nickel 8 %. */
export const PARTICLE_COLOURS = [C.m500, C.m500, C.m500, C.m400, C.m400, C.m300, C.m300, C.white, C.nickel] as const;

export const SHAPE = {radiusControl: raw.radius.control * 2, radiusPanel: raw.radius.panel * 2, radiusMedia: raw.radius.media * 2, hairline: 2, frame: 4} as const;
