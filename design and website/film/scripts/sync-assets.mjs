// Copies the brand fonts, identity SVGs and tokens from the sibling website package into this film project.
// Source of truth stays in ../assets/public and ../design-system; run `npm run sync` after those change.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, '..');
const assets = path.resolve(root, '../assets/public/assets');
const copy = async (from, to) => {
  await fs.mkdir(path.dirname(to), {recursive: true});
  await fs.copyFile(from, to);
  console.log('copy', path.relative(root, to));
};

const fonts = [
  ['fraunces', 'fraunces-latin-full-normal.woff2'],
  ['mona-sans', 'mona-sans-latin-wght-normal.woff2'],
  ['geist-mono', 'geist-mono-latin-wght-normal.woff2'],
];
for (const [family, file] of fonts) {
  await copy(path.join(assets, 'identity/font-source', family, file), path.join(root, 'public/fonts', file));
  await copy(path.join(assets, 'identity/font-source', family, 'OFL.txt'), path.join(root, 'public/fonts', `OFL-${family}.txt`));
}
const brand = ['wordmark-inverse.svg', 'wordmark-marigold.svg', 'wordmark-gradient.svg', 'lockup-inverse.svg', 'flat.svg', 'flat-inverse.svg'];
for (const file of brand) await copy(path.join(assets, 'revisions/v5/identity', file), path.join(root, 'public/brand', file));

const tokens = JSON.parse(await fs.readFile(path.resolve(root, '../design-system/tokens.json'), 'utf8'));
const palette = {};
for (const [name, token] of Object.entries(tokens.palette)) palette[name] = token.$extensions['outspoken.hex'];
const num = (group) => Object.fromEntries(Object.entries(tokens[group]).map(([k, v]) => [k, v.$value.value]));
const out = {source: 'design-system/tokens.json', palette, radius: num('radius'), stroke: num('stroke'), space: num('space')};
await fs.writeFile(path.join(root, 'src/generated/tokens.json'), JSON.stringify(out, null, 2) + '\n');
console.log('tokens', Object.keys(palette).length, 'colours');
