# Design system: integrity and fitness for the launch film

Date: 31 October 2026. Scope: `design-system/` (tokens, type roles, style grammar, DESIGN.md, START-HERE.md, requirements), `website/packages/{tokens,motion,video,ui}`, the brand fonts and identity SVGs. Question: is the system internally consistent, and how well does it carry an 80 s, 1920x1080, mostly-muted LinkedIn film with particle bursts?

Method. A read-only audit agent read the files, parsed the font files, and computed contrast ratios; the film builder agents applied the resulting rules; the main session re-read the V10 block, `tokens.json`, `type-roles.json` and `style-grammar.json` and independently recomputed the contrast ratios below (all matched). The audit did not open every `.tsx` file, did not test with viewers, and the phone-feed width (about 390 px) is an assumption: LinkedIn's spec page gives no layout.

## 1. Verdict
The **colour, type families, geometry and wordmark rules transfer well** to film. The system is **not film-ready as written**: it has no motion, particle, camera or film-type tokens; its web type sizes are far too small for a phone feed; and a few documents contradict the V10 decisions. The film therefore adds a clearly marked proposal, `design-system/film-tokens.json`, and does not change the web tokens. Particle bursts and a navy-dominant look are an **extension** of a quiet, light editorial system and need owner sign-off.

## 2. Integrity findings
| # | Finding | Status |
|---|---|---|
| 1 | Find-and-replace damage in the public copies: `START-HERE.md` line 1 and `DESIGN.md` line 4 read "marigold replaces marigold" (should say citron). The canonical local files were correct. | **Fixed** in this commit |
| 2 | Stale citron `#D4DD67` still ships: `v5/identity/wordmark-citron.svg`, `lockup-citron.svg` (rights-registered), `packages/video/revisions/v5/scenes.html`, `stage-plan.md`, `generation-recipes.md`. Website CSS has none. The film does not use them. | Open |
| 3 | `requirements.json` rows OS-R051 and one near line 287 describe "Out marigold; spoken navy", which contradicts the current primary wordmark (OUT navy, SPOKEN silver `#A9AFBA`). | Open (historical requirement text; needs an owner decision) |
| 4 | `DESIGN.md` "Typography and readability correction" still prescribes Archivo/Inter, weights 700-800, labels >= 14 px; the V10 block, `type-roles.json` and tokens say Fraunces 400, Mona Sans 400, Geist Mono labels. DESIGN.md also repeats whole blocks. | Open |
| 5 | `packages/ui/src/styles.css` still declares Archivo and Inter; only `website-v3/website.css` loads the V10 families. `tokens.json` has no font-family tokens. | Open |
| 6 | Tokens are generated correctly but bypassed: 41 of 93 `--os-*` variables are never read via `var()`; `#EAA93C` is hard-coded 20 times; 102 distinct off-palette hex values (e.g. warm paper `#FAFAF7` instead of pearl `#F1F3F6`). | Open |
| 7 | Shape and tilt limits disagree across documents (radii 6/10/14 in tokens vs 7-18 px in CSS; tilt 3 deg in DESIGN.md, 6.3-8.6 deg measured, +/-18 deg in the style grammar). | Open |
| 8 | `DESIGN.md` says marigold-800 on "white or paper" is 6.81:1; true for white only (6.13 on pearl). `qa/contrast-v10.json` was measured on `#FAFAF7`/`#F6F4EE`, not pearl, and omits silver, cobalt and wordmark pairs. marigold-700 on pearl is 4.10 (fails AA for normal text). | Open |
| 9 | Existing video precedent is inconsistent and too small: `frame-adapter.json` (8 scenes, 48 s), the v5 manifest (6 scenes, 18 s, 960x540, CRF 28), templates OS-V001-008 (6 s each, 4 s minimum hold). None fits a 80 s, 1080p film. | Not used |
| 10 | Naming gap: the film brief says paper/silver/marker/ink; tokens say pearl/nickel/marigold-300/navy. Inverse-wordmark colours (`#F2F5FA`, `#B9C7DA`) and the capsule-mark blues exist only inside SVGs. | Aliases proposed in `film-tokens.json` |

## 3. Fit table
| Element | Fit for film | Note |
|---|---|---|
| Palette: navy, marigold 50-950, nickel, pearl, cobalt | Good | Explosions only on navy: marigold-500 is 6.86:1 on navy but 1.85:1 on pearl. Cobalt is 2.31:1 on navy (soft glow only), 5.47:1 on pearl (rim). |
| Fraunces 400 | Good at >= 80 px | Hairlines die below; roman file only (no italics); no arrow glyphs in any family. |
| Mona Sans 400 / Geist Mono 500 | Good at >= 60 / >= 56 px | Web sizes (12-18 px) become 2.4-4.9 CSS px on a 390 px phone; the film scale is 200 / 128 / 88 / 64 / 56 / 52. |
| Radii 6/10/14, strokes 1/2 | Good at x2 | Hairlines need >= 2 px at 1080p to survive compression; rims >= 6 px. |
| Wordmark and capsule mic SVGs | Good, restricted | End card only (+ one earlier reveal), width 640-900 px, inverse on navy, never on marigold (silver on marigold is 1.07:1); never re-typeset. V10 microphone redesign is still open, so the mark sits behind one swappable component. |
| Brand ease `cubic-bezier(0.22,1,0.36,1)` | Good | The only motion token that exists (in `motion/presets.ts`). |
| Hover/focus/disabled states, tilt button, WebGL plate | Not applicable | Pointer behaviour; only a scripted default-to-pressed on the CTA capsule is used. |
| NeuronField (HRA brain mesh) | Unsuitable | WebGL, scroll-driven, not frame-deterministic, CC BY 4.0 credit duty; the film draws its own SVG head map. |
| Scroll/dialog/`motion/react` interactions | Unsuitable | Time-based, not frame-driven. |
| "No unreadable particle storm", quiet light editorial mood | Tension | Bursts are capped (see below) and need owner sign-off. |

## 4. Film rules adopted (see `src/kit` and `SPEC.md`)
- Scene mix: quiet mind scenes navy 72-80 %, marigold <= 5 %; burst scenes navy >= 55 %, marigold family 15-25 %; explain scenes on pearl; the film keeps navy+pearl+white >= 70 % of every frame except peak burst frames.
- Text: accent text on pearl only in marigold-800; marigold-500 and silver only on navy and only at >= 60 px; no marigold, silver or cobalt text on pearl.
- Bursts: at most 8 big ones, dots/short streaks/thin rings only, <= 220 particles (ignition 320), calm for >= 30 frames afterwards; flashes <= 3 frames, alpha <= 0.2; everything a pure function of `useCurrentFrame()`.
- Camera: zoom 1.00-1.18, drift <= 6 px, parallax depths 0.3 / 0.6 / 1.0 / 1.6 (S2's 1.6 start and S5's 0.55 zoom with a -2 deg roll are scene-specified exceptions).
- Disclosure: every fictional founder, account, buyer or post is labelled while visible; no LinkedIn logo or UI, no statistics, no clients.

## 5. Deviations and decisions made while building
- The film opens with a typed first line ("Let's talk about you.") instead of a pure silent cursor, because two independent reviews found that a silent, wordless first second reads as a broken file on muted autoplay.
- Cobalt appears only as soft glow or as a filled shape with a pearl rim on navy, never as a line or particle there (rule resolved against the original S4/S5 storyboards).
- The persistent fictional tag moved above the bottom 15 % and is 40 px (the spec asks >= 40 px for disclosures, >= 56 px for other mono labels).
- The marker highlight and `Flash` helpers have small defects noted by the builders (ink flips to navy at 50 % of the wipe; a marigold flash at alpha 0.2 over navy looks muddy). Scenes use local fixes (`InkMarker`, `C.m100`); promoting them into the kit is a follow-up.

## 6. Follow-ups for the design owner (not changed here)
Resolve findings 2-8 above; add font-family tokens and `film-tokens.json` (after sign-off) to the generated token pipeline; remove or archive the citron SVGs and the v5 video proofs; re-measure `qa/contrast-v10.json` on pearl with the silver, cobalt and wordmark pairs; decide the microphone identity so the film's end card can be finalised.
