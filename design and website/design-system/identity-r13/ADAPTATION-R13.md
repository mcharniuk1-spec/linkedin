# OS stencil identity (R13): review, choice, rebuild (proposed)

Status: **proposed**. On 2 November 2026 the owner set aside the square bracket mark (R12 direction A) and asked for an OS mark where the letters themselves are worked in a creative way, taken from the Codex concept boards. This record shows how the 30 concepts were reviewed, which one was rebuilt, and what was measured. Owner acceptance is still false: the site, film, publication cards and Brand Studio now carry the mark for review, and the B01 microphone identity stays in the repository as the earlier version.

## 1. Review of the Codex concepts

Source: Codex R11 pack `EXTRA-LOGO`, ten boards (`LOGO-01` to `LOGO-10`), three concepts each (-L, -C, -R), 30 in all. They are raster concepts, not vectors. The boards are kept in the local run folder, not in this repository.

Method: three independent reviewers (a brand designer, a legibility specialist, a systems engineer; AI reviewers reading the boards) scored every concept from 1 to 5 on six criteria: reads OS at a glance, palette fidelity, survival at 24 and 16 px, fit with the V5 wordmark, distinctiveness, readiness to rebuild as vector. They were not told any preferred concept. Scores are a structured second opinion, not user testing. Full scores and notes: `concept-review.json`.

| Rank | Concept | Mean of 30 | Notes |
|---|---|---|---|
| 1 (tie) | LOGO-04-L | 26.3 | Navy ring O, silver S, marigold lens at the overlap. Reads OS at once. Venn overlap is a common device. |
| 1 (tie) | LOGO-06-L | 26.3 | Navy O, marigold diagonal slash, silver S. Fewest parts, best wordmark fit, slash echoes the notch in the wordmark's first O. |
| 3 | LOGO-08-R | 24.0 | Italic parallelogram O reads close to 0S; sporty. |
| 4 | LOGO-05-R | 23.3 | Condensed navy OS cut by a marigold diagonal. |
| 5 | **LOGO-03-L** | **21.7** | Stencil navy O, silver S, marigold slash. Exact brand trio. Weak point: stencil bridges close up at small size. |
| 8 | LOGO-03-R | 20.3 | Octagonal navy O, marigold S. Marigold dominates, so it is not an accent. |

Findings that hold across the panel: seven concepts read as something other than OS to at least one reviewer (LOGO-01-C and -R read "CS", LOGO-03-C, LOGO-06-R, LOGO-08-L, LOGO-10-C, LOGO-10-R); the stencil wordmarks drawn on the boards have ambiguous E and K glyphs and are **not used**: the wordmark stays the unchanged V5 outline.

## 2. Choice

- **A (primary, built into the site): LOGO-03 left.** The owner attached it and its sibling as the wanted direction; it uses navy, Nickel silver and marigold exactly; it reads OS clearly. The panel ranked it fifth, mainly for stencil bridges at small size. That risk is handled by a gap-closed "solid" build for sizes under 48 px (section 5).
- **B (alternate, same file structure): LOGO-06 left**, the panel's joint first choice and the smooth sibling of A (no bridges, larger slash). Files: `smooth/` and `assets/public/assets/identity/v13-smooth/`. Trade-off measured: A is compact (1.84 : 1) and fills square avatars and favicons better; B is wide (2.77 : 1) and suits horizontal lockups but gets small in a square tile.
- **Owner decision, 2 November 2026: keep A (stencil).** B stays in the repository as a documented alternate and is not served by the site. This selects the mark; it does not accept the identity (acceptance is a separate owner step and stays false).
- To switch the site to B, replace `/assets/identity/v13/` by `/assets/identity/v13-smooth/` in the site, film and publication sources, then rebuild. No other change is needed.

## 3. Rebuild method and fidelity

`trace_stencil.py` separates the concept into its three colours (nearest palette colour at 4x resolution, median and Gaussian clean-up), traces each layer into Bezier paths with a pure-Python potrace port, and bakes the coordinates into a 100-unit-high box. The traced paths are committed in `os-stencil-paths.json` and `os-smooth-paths.json`; the source image is not. The paths are snapped to the exact brand colours; the Codex image colours drifted slightly.

Measured: the rendered vector matches the concept's colour layers with intersection over union of 0.998 (navy), 0.993 (silver), 0.996 (marigold) for A, and 0.997, 0.993, 0.998 for B.

## 4. What was built (served from `assets/public/assets/identity/v13/`, sources next to this file)

| Group | Files |
|---|---|
| Mark | `mark-os`, `-inverse`, `-mono`, `-mono-inverse`; `mark-os-solid` (and the same variants) for small sizes; `mark-os-animated` (entrance, reduced motion shows the final state) |
| Lockups | `lockup-os`, `-inverse`, `-mono`; `lockup-os-stacked` and its variants; `lockup-os-inverse-ground` and the stacked version add the deep-navy rectangle for standalone use. The site files are transparent. |
| Wordmark | `wordmark-nickel600.svg`: the V5 outlines with SPOKEN in Nickel 600 |
| Avatar | `avatar-os` (+ 800 and 400 px PNG), `avatar-os-24` (solid build) |
| Tab and device icons | `favicon-os`, `favicon-os-16` (+ 16, 32, 48, 64 px PNG), `favicon-os.ico` (16, 32 and 48 px entries), `apple-touch-os` (full-bleed square, 180 px PNG) |
| Preview | `mark-os-1200.png`, `lockup-os-3x.png` |

The wordmark paths are the nine V5 outlines with their original transforms, hairline stroke and paint order; only the two colour values change. Nothing is re-typeset.

## 5. Usage rules

- The OS mark and the V5 wordmark appear together only in the supplied lockups. Do not recolour, stretch, outline or re-typeset either part.
- Sizes are the mark's **height** in CSS pixels (the wide mark is 1.84 times as wide: 48 px high is about 88 px wide). Use the stencil mark from 48 px high. Below 48 px use the solid build (stencil gaps closed, same outer shape). In the 16 px favicon the mark is 15 px wide and about 8 px high, and it reads as an OS silhouette with the marigold slash, not as separate letters; that is the honest limit of a wide two-letter mark.
- Light grounds: navy O, Nickel 600 `#666F7F` S and SPOKEN, marigold slash. Dark grounds: O `#F2F5FA`, S and SPOKEN `#B9C7DA`, marigold slash. Mono: all navy or all `#F2F5FA`.
- Clear space: the height of the marigold slash (0.235 of the mark height) on every side.
- The marigold slash is an accent. Letters carry the meaning, so a viewer who cannot tell marigold apart still reads OS.
- Do not play the entrance animation in a loop beside body text.

## 6. Checks (measured)

| Pair | Contrast |
|---|---|
| Navy O on pearl `#F1F3F6` / on white | 12.65 : 1 / 14.06 : 1 |
| Nickel 600 S and SPOKEN on pearl / on white | 4.56 : 1 / 5.07 : 1 (passes 4.5 : 1) |
| Previous Nickel `#A9AFBA` on white | 2.20 : 1 (below 3 : 1; the reason for Nickel 600) |
| Navy O against Nickel 600 S (two-tone separation) | 2.78 : 1 |
| Inverse O `#F2F5FA` / inverse S `#B9C7DA` on deep navy `#0D1A3B` | 15.65 : 1 / 9.97 : 1 |
| Inverse O / S on the avatar navy `#162760` | 12.87 : 1 / 8.20 : 1 |
| Marigold slash on navy / on white | 6.86 : 1 / 2.05 : 1 (decorative on white) |

Also checked: all SVG files parse as XML; the lockups render with nine wordmark paths and nine transforms; the avatar fits inside a circular crop; favicons were rendered at 64, 48, 32 and 16 px and inspected.

## 6a. Where it is applied (R13, all proposed)

- Website: header and footer lockup, closing block mark, Brand Studio identity section, hero post card mark, favicon set (ICO, SVG, apple-touch), JSON-LD logo, share card (`og-outspoken-1200x630.png`; the previous one is kept as `-v10`).
- Film: the 30 s film's S4 mark pulse, end-card mark with sound rings and end lockup (S4 moved under the headline because the wide mark collided with the word "voice").
- Publications: the three LinkedIn drafts use the new lockups.
- Tokens: `silver-600`, `inverse-light`, `inverse-silver`, `navy-deep` added as proposed values; the existing `--silver` is unchanged.

## 7. Limits and open decisions

- Owner acceptance of a new identity is false. The scores come from AI reviewers; no buyer or user test was run.
- Nickel 600 is a proposed token. The existing `--silver` (`#A9AFBA`) stays for borders and rules.
- At 16 px the mark is a silhouette. A bracket-free alternative would be an O-only or S-only tile; none was built.
- Figma is not updated (view-only seat). The Codex boards remain concepts.

## 8. Rebuild

```bash
cd "design and website/design-system/identity-r13"
python3 build_stencil.py                    # stencil family (A)
python3 build_stencil.py --variant smooth   # smooth alternate (B)
# only if the paths must be re-traced (needs numpy, Pillow, scipy, potracer and the Codex board image):
python3 trace_stencil.py --source <LOGO-03.png> --out os-stencil-paths.json
python3 trace_stencil.py --source <LOGO-06.png> --box 60,190,740,480 --out os-smooth-paths.json
```

PNG and ICO exports need Google Chrome; pass `--chrome "/path/to/chrome"` to use another binary.
