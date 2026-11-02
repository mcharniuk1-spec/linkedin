# Direction A, bracket OS: production candidates (proposed)

Status: **proposed**. The owner chose direction A ("Bracket OS") on 2 November 2026. That choice selects a concept for adaptation. It does not accept a new identity. The live identity stays the B01 microphone mark with the V5 outlined wordmark until the owner accepts a change. Nothing here is deployed to the website.

Source: `build_bracket.py` (run `build.py` first). Output: this folder and a copy in `assets/public/assets/identity/r12/`.

## What was built

| File | Use | Notes |
|---|---|---|
| `os-bracket-lockup.svg` | Light backgrounds | Monogram, then the V5 wordmark: navy OUT, nickel SPOKEN (the primary wordmark rule). |
| `os-bracket-lockup-inverse.svg` | Dark backgrounds | Same construction on deep navy. SPOKEN and OUT use the canonical inverse pair `#B9C7DA` and `#F2F5FA`. |
| `os-bracket-lockup-mono.svg` | Small reading sizes, single-colour print | All navy. Use this wherever SPOKEN in nickel is too light (see findings). |
| `os-bracket-avatar.svg`, `-800.png`, `-400.png` | Profile picture | 800 px square, navy ground. The whole monogram sits inside the circular crop. |
| `os-bracket-avatar-24.svg` | 24 px build | Heavier letters (Mona Sans 680), thicker arms, no handles. |
| `os-bracket-favicon.svg`, `-favicon-64.png`, `-apple-touch-180.png` | Favicon candidate | 64 px tile with rounded corners, heavier letters, no handles. |
| `os-bracket-animated.svg` | Motion | Arms draw in, handles pop, letters fade. `prefers-reduced-motion` shows the final state at once. |

The wordmark paths are the exact V5 outlines with their original per-letter transforms (checked: 9 paths, 9 transforms kept). Nothing is re-typeset. The two letters "OS" are outlines of Mona Sans, so the files carry no font dependency.

## Change from the direction board (deliberate)

On the board the letters were set at 128 units. Measured with fontTools, "OS" at that size is 180 units wide, and the bracket frame was 172 units wide. The letters overshot the frame by about 4 units on each side, so the "O" touched the arms. The adaptation sets the letters at 112 units (156 wide, 84 high) and widens the frame to 26 to 214. That leaves about 12.5 units of clearance, and the arms (44 units long) end before the letter band starts. The construction is unchanged: square selection frame, four corner arms, four handles, two letters.

## Usage rules

- The monogram is a **companion mark**: profile avatar, favicon candidate, video corner bug, social tile. It never replaces the B01 microphone plus V5 wordmark header lockup on the website until the owner says so.
- Keep the wordmark and the monogram together only in the supplied lockups. Do not re-typeset, recolour or stretch either part.
- Clear space: one handle width (16 units of the 240 box) around the monogram. Smallest sizes: monogram 24 px, favicon 32 px, lockup 112 px wide on screen.
- Marigold arms are decoration. The letters and the handle outlines carry the shape, so a viewer who cannot see marigold still reads "OS" inside a frame.
- Animation plays once. Do not loop it in running text or beside body copy.

## Checks (measured)

| Check | Result |
|---|---|
| Navy `#162760` on pearl `#F1F3F6` (letters, OUT) | 12.65:1, passes 4.5:1 |
| Pearl on navy (avatar and favicon letters) | 12.65:1, passes 4.5:1 |
| Marigold `#EAA93C` on navy (arms) | 6.86:1, passes 3:1 for graphics |
| Pearl `#F2F5FA` on deep navy `#0D1A3B` (inverse letters) | above 15:1 |
| Lettering | Wordmark outline letters read `OUTSPOKEN` (9 paths, `data-letter` attributes). Monogram letters are the string `OS`. |
| SVG well-formedness | All 7 SVG files parse as XML. |
| Rendering | Lockup, avatar, favicon, apple-touch and the 24 px build were rendered with headless Chrome and inspected at 4x. Letters clear the arms at every size. |

## Findings for the owner (not changed here)

1. **SPOKEN in nickel `#A9AFBA` on pearl is 1.98:1**, below the 3:1 minimum for large text. This comes from the primary wordmark rule in `design-system/START-HERE.md`, not from this adaptation. That file already says to use mono navy for small reading signatures, so the mono lockup is the safe variant on light grounds at small sizes. The owner may want to decide whether the primary wordmark needs a darker silver for pearl.
2. **Marigold arms on pearl are 1.85:1.** They are decorative here, but a light-ground use of the monogram looks weaker than the navy-ground use. Prefer the navy ground for the avatar and favicon, which is how they were built.
3. **At 16 px the letters are not legible.** The 64 and 32 px favicons read well. For a 16 px browser tab, keep the current favicon (`assets/public/assets/identity/v10/favicon.svg`) or ask for a bracket-only mark. No 16 px build was made, to avoid claiming something that fails.
4. Not done: Figma update (view-only seat), site integration of the favicon or avatar, owner acceptance, 3D or video use of the monogram.

## Rebuild

```bash
cd "design and website/design-system/identity-r12"
python3 build.py && python3 build_bracket.py
```

Needs Pillow, fontTools and brotli (for the woff2 sources) and Google Chrome for the PNG exports. Pass `--chrome "/path/to/chrome"` to use another binary.
