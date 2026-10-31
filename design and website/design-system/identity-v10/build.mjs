// Builds the V10 identity vectors from geometry in this file: the B01 matte-capsule microphone mark (colour, inverse, mono,
// 24 px versions), two lockups that reuse the V5 outlined wordmark geometry unchanged, and the D05 monoline icon set
// (sprite plus single files). Run: node design-system/identity-v10/build.mjs   (from "design and website/")
// Status: PROPOSED. The client chose B01 (mark) and D05 (icons) on 31 Oct 2026; final acceptance is still pending.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const out = path.join(root, 'assets/public/assets/identity/v10');
const v5 = path.join(root, 'assets/public/assets/revisions/v5/identity');
fs.mkdirSync(path.join(out, 'icons'), {recursive: true});
const w = (f, s) => fs.writeFileSync(path.join(out, f), s);

const C = {navy: '#162760', nickel: '#A9AFBA', marigold: '#EAA93C', pearl: '#F1F3F6', white: '#FFFFFF', marker: '#F6D591'};
const T = 'OUTSPOKEN V10 proposed microphone mark B01 (matte capsule)';

// ---------- B01 mark, large (viewBox 160 x 212): head, band + ring, body, yoke, stem, base ----------
const markLarge = ({ink, band, accent, id, mesh = true, mono = false}) => {
  const head = `<path id="head" d="M46 88V48a34 34 0 0 1 68 0v40z" fill="${ink}"/>` +
    (mesh ? `<path d="M46 88V48a34 34 0 0 1 68 0v40z" fill="url(#mesh-${id})"/>` : '');
  const bandRing = mono
    ? `<rect id="ring" x="46" y="94.5" width="68" height="3" fill="${ink}"/>`
    : `<rect id="band" x="46" y="88" width="68" height="16" fill="${band}"/><rect id="ring" x="46" y="93" width="68" height="6" fill="${accent}"/>`;
  const bodyY = mono ? 104 : 104;
  return `<defs><pattern id="mesh-${id}" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="3" cy="3" r="1" fill="${band}" opacity=".22"/></pattern></defs>` +
    `<g id="mark-b01">${head}${bandRing}` +
    `<path id="body" d="M46 ${bodyY}h68v12a34 34 0 0 1-68 0z" fill="${ink}"/>` +
    `<path id="yoke" d="M34 112v14a46 46 0 0 0 92 0v-14" fill="none" stroke="${ink}" stroke-width="6" stroke-linecap="round"/>` +
    `<circle id="knob-l" cx="34" cy="112" r="6.5" fill="${mono ? ink : band}"/><circle id="knob-r" cx="126" cy="112" r="6.5" fill="${mono ? ink : band}"/>` +
    `<rect id="stem" x="75" y="170" width="10" height="16" fill="${ink}"/><rect id="base" x="38" y="184" width="84" height="12" rx="6" fill="${ink}"/></g>`;
};
// ---------- B01 mark, 24 px (viewBox 24 x 24): fewer parts, strokes >= 1.2 px at 24 ----------
const mark24 = ({ink, accent}) =>
  // No nickel band at 24 px: the marigold ring touches navy (6.86:1) and stays visible at 16-32 px.
  `<g id="mark-b01-24"><path d="M8 9.2V5.5a4 4 0 0 1 8 0v3.7z" fill="${ink}"/>` +
  `<rect x="8" y="9.2" width="8" height="1.6" fill="${accent}"/>` +
  `<path d="M8 10.8h8v2a4 4 0 0 1-8 0z" fill="${ink}"/>` +
  `<path d="M6 11.6v2.4a6 6 0 0 0 12 0v-2.4" fill="none" stroke="${ink}" stroke-width="1.3" stroke-linecap="round"/>` +
  `<rect x="11.3" y="19.6" width="1.4" height="1.8" fill="${ink}"/><rect x="7" y="21" width="10" height="1.8" rx=".9" fill="${ink}"/></g>`;

const svg = (vb, title, body, extra = '') => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${vb}" role="img"${extra}><title>${title}</title>${body}</svg>\n`;
const sizeAttr = (wd, ht) => ` width="${wd}" height="${ht}"`;
w('mark-b01.svg', svg('0 0 160 212', T, markLarge({ink: C.navy, band: C.nickel, accent: C.marigold, id: 'a'}), sizeAttr(160, 212)));
w('mark-b01-inverse.svg', svg('0 0 160 212', T + ', inverse for navy grounds', markLarge({ink: C.pearl, band: C.nickel, accent: C.marigold, id: 'b'}), sizeAttr(160, 212)));
w('mark-b01-mono.svg', svg('0 0 160 212', T + ', one colour', markLarge({ink: C.navy, band: C.navy, accent: C.navy, id: 'c', mesh: false, mono: true}), sizeAttr(160, 212)));
w('mark-b01-24.svg', svg('0 0 24 24', T + ', 24 px version', mark24({ink: C.navy, accent: C.marigold}), sizeAttr(24, 24)));
w('mark-b01-24-inverse.svg', svg('0 0 24 24', T + ', 24 px inverse', mark24({ink: C.pearl, accent: C.marigold}), sizeAttr(24, 24)));
w('favicon.svg', svg('0 0 32 32', 'OUTSPOKEN favicon', `<rect width="32" height="32" rx="7" fill="${C.navy}"/><g transform="translate(4 3.5) scale(1)">${mark24({ink: C.pearl, accent: C.marigold})}</g>`, sizeAttr(32, 32)));

// ---------- Lockups: V5 outlined wordmark geometry unchanged; the 24 px mark (cap-height match) takes the old microphone's slot ----------
for (const [name, src, inv] of [['lockup-b01.svg', 'lockup-gradient.svg', false], ['lockup-b01-inverse.svg', 'lockup-inverse.svg', true]]) {
  let s = fs.readFileSync(path.join(v5, src), 'utf8');
  const slot = /<g transform="translate\(4 0\) scale\(\.62\)">[\s\S]*?<\/g>/;
  if (!slot.test(s)) throw new Error('mic slot not found in ' + src);
  const mk = mark24({ink: inv ? C.pearl : C.navy, accent: C.marigold});
  s = s.replace(slot, `<g transform="translate(2 4) scale(3.1)">${mk}</g>`);
  s = s.replace(/<title>[^<]*<\/title>/, `<title>OUTSPOKEN V10 proposed lockup: B01 microphone mark with the V5 outlined wordmark${inv ? ', inverse' : ''}</title>`);
  w(name, s);
}

// ---------- D05 monoline icons: 24 grid, 1.8 stroke, round caps, offset marigold marker ----------
const marker = (cx = 16.5, cy = 7.5, r = 4.6) => `<circle cx="${cx}" cy="${cy}" r="${r}"/>`;
const ICONS = {
  mic: {lines: '<rect x="8.5" y="2.5" width="7" height="9.5" rx="3.5"/><path d="M5.5 10.5v2a6.5 6.5 0 0 0 13 0v-2M12 19v2.5M8 21.5h8"/>', marker: marker(16.5, 6.5)},
  time: {lines: '<circle cx="12" cy="12" r="8.5"/><path d="M12 7v5l3.4 2.1"/>', marker: marker()},
  recognition: {lines: '<path d="M12 3.2l2.3 6.1 6.2 2.7-6.2 2.7L12 20.8l-2.3-6.1L3.5 12l6.2-2.7z"/>', marker: marker(17.2, 6.8, 4.2)},
  voice: {lines: '<path d="M4.5 10v4M8.2 7v10M12 3.5v17M15.8 8v8M19.5 10.5v3"/>', marker: marker(17, 7, 4.4)},
  usefulness: {lines: '<circle cx="12" cy="12" r="8.5"/><path d="M8.2 12.4l2.6 2.6 5-5.6"/>', marker: marker()},
  conversations: {lines: '<path d="M4 5.5h9.5A2 2 0 0 1 15.5 7.5V11a2 2 0 0 1-2 2H9.5L6 16v-3H4A2 2 0 0 1 2 11V7.5a2 2 0 0 1 2-2z"/><path d="M16.5 9.5h3.5a2 2 0 0 1 2 2V15a2 2 0 0 1-2 2h-.8v3l-3.2-3h-3a2 2 0 0 1-1.7-1"/>', marker: marker(17.5, 6, 4)},
  profile: {lines: '<rect x="3" y="5" width="18" height="14" rx="2.5"/><circle cx="9" cy="11" r="2.1"/><path d="M5.6 16.2c.7-1.7 2-2.5 3.4-2.5s2.7.8 3.4 2.5M14.5 10h4M14.5 13.5h3"/>', marker: marker(17, 6.5, 4.2)},
  strategy: {lines: '<rect x="3.5" y="5" width="17" height="15" rx="2.5"/><path d="M3.5 9.5h17M8 3v4M16 3v4M8 14h.01M12 14h.01M16 14h.01"/>', marker: marker(17, 6.5, 4.2)},
  writing: {lines: '<path d="M4 20l1-4L16.4 4.6a2.1 2.1 0 0 1 3 3L8 19z"/><path d="M14.4 6.6l3 3"/>', marker: marker(17.5, 6, 4)},
  design: {lines: '<rect x="3" y="4.5" width="18" height="15" rx="2.5"/><circle cx="8.5" cy="10" r="1.8"/><path d="M3.5 17l5-4.4 3.6 3 3.2-2.6 5.2 4"/>', marker: marker(17, 8, 4.2)},
  automation: {lines: '<circle cx="5.5" cy="7" r="2.2"/><circle cx="5.5" cy="17" r="2.2"/><circle cx="18.5" cy="12" r="2.2"/><path d="M7.5 7.8l8.8 3.2M7.5 16.2l8.8-3.2"/>', marker: marker(12, 12, 4.4)},
  marketing: {lines: '<path d="M3.5 11.5L20.5 4l-4.5 16-4.2-6.4z"/><path d="M11.8 13.6L20.5 4"/>', marker: marker(7.5, 16.5, 4)},
  advertising: {lines: '<path d="M4 10v4h3l7.5 4V6L7 10z"/><path d="M17.8 9.4a4 4 0 0 1 0 5.2"/>', marker: marker(17, 6.5, 4)},
  measurement: {lines: '<path d="M4 20h16"/><rect x="5.5" y="13" width="3" height="7" rx=".6"/><rect x="10.5" y="9" width="3" height="11" rx=".6"/><rect x="15.5" y="5" width="3" height="15" rx=".6"/>', marker: marker(7, 8, 4.2)},
};
const strokeAttrs = 'fill="none" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"';
const symbol = (n, d) => `<symbol id="${n}" viewBox="0 0 24 24"><title>${n}</title><g fill="var(--icon-marker, ${C.marigold})" stroke="none">${d.marker}</g><g ${strokeAttrs} stroke="currentColor">${d.lines}</g></symbol>`;
w('icons-d05.svg', `<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-label="OUTSPOKEN D05 monoline icons"><title>OUTSPOKEN D05 monoline icon sprite (proposed): use with currentColor; marker colour through --icon-marker</title>${Object.entries(ICONS).map(([n, d]) => symbol(n, d)).join('')}</svg>\n`);
for (const [n, d] of Object.entries(ICONS)) {
  w(`icons/${n}.svg`, svg('0 0 24 24', `OUTSPOKEN icon: ${n}`, `<g fill="${C.marigold}" stroke="none">${d.marker}</g><g ${strokeAttrs} stroke="${C.navy}">${d.lines}</g>`, sizeAttr(24, 24)));
}
fs.writeFileSync(path.join(root, 'design-system/identity-v10/icons.json'), JSON.stringify(Object.fromEntries(Object.entries(ICONS).map(([n, d]) => [n, {lines: d.lines, marker: d.marker}])), null, 1) + '\n');
console.log('identity v10:', fs.readdirSync(out).length, 'entries,', Object.keys(ICONS).length, 'icons');
