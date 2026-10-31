# Identity V10 (proposed): B01 microphone mark and D05 icons

Status: **proposed**. On 31 October 2026 the client chose direction **B01 (matte capsule)** for the logo mark and **D05 (monoline with a marigold marker)** for icons from the Codex candidate set R10 (previews in `assets/public/assets/identity/mic-candidates-r10/`). Final acceptance is still pending. The V5 outlined wordmark geometry is unchanged; only the microphone changed.

Regenerate every file from geometry: `node design-system/identity-v10/build.mjs` (from `design and website/`). Output: `assets/public/assets/identity/v10/`.

## Files
| File | Use |
|---|---|
| `mark-b01.svg`, `mark-b01-inverse.svg`, `mark-b01-mono.svg` | large mark (160x212): colour on pearl/white, inverse on navy, one colour; head with fabric-mesh pattern, band + marigold ring, yoke, stem, base; named groups, no raster |
| `mark-b01-24.svg`, `mark-b01-24-inverse.svg` | 24 px version (16-48 px): no mesh, no nickel band, marigold ring touching navy; strokes >= 1.3 units |
| `lockup-b01.svg`, `lockup-b01-inverse.svg` | mark + the V5 outlined wordmark (geometry unchanged, first-O notch kept); the 24 px mark matches the cap height |
| `favicon.svg` | 32 px navy tile with the inverse 24 px mark |
| `icons-d05.svg` (sprite, `currentColor`, marker via `--icon-marker`) and `icons/*.svg` (single files) | 14 icons on a 24 grid, 1.8 stroke, round caps: mic; the five values (time, recognition, voice, usefulness, conversations); the eight services (profile, strategy, writing, design, automation, marketing, advertising, measurement) |

Site use: header and footer lockup (`Wordmark`), hero publication mark, closing panel (mark with three sound rings), experience-story chips, services titles, favicon. Icons are always attached to a label: no standalone icon row.

## Rules
- Large mark from 64 px tall; 24 px mark for 16-48 px; below 16 px use the favicon tile. Clear space: one quarter of the mark width. Never recolour outside navy, pearl, nickel and marigold; never add gloss, glow or tilt.
- Colour pairs (computed, WCAG): navy on pearl 12.65, pearl on navy 12.65, pearl on the closing panel 15.38, nickel band against navy 6.38, marigold ring against navy 6.86, icon stroke navy over the marigold marker 6.86. **Known weak pairs:** marigold ring against the nickel band 1.07 (decorative; the 24 px version drops the band), nickel knobs on pearl 1.98 (decorative; the silhouette carries recognition), pearl stroke over the marigold marker on dark grounds 1.85 (marker overlap only).
- Spelling: the only text is OUTSPOKEN (titles, alt text, wordmark outlines), checked by search; the wordmark is never typeset.
- Reduced motion: the closing-panel rings are CSS animations and are removed under `prefers-reduced-motion: reduce` (rule contents verified; the media query itself was not emulated in this browser).

## Not done
Brand Studio (`/design-system`) still documents the V5 capsule artefacts; Figma was not updated (no edit access); the film's end card keeps the wordmark only; icon set has no animation yet.
