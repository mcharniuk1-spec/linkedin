# Depth of background (OS identity, proposed)

Source: `website/website-v3/depth.css`. Import it **last** (after `App`) in `main.tsx` so equal-specificity rules resolve in its favour. It only adds background layers and pseudo-elements. It does not change any content box (checked: all section tops and heights at 1440 px match the build without it). No new image, font or request: the only assets are `/assets/identity/v13/mark-os-mono.svg` and `mark-os-mono-inverse.svg`, used as CSS masks.

## Layers (same vocabulary in every block)

| # | Layer | How |
| --- | --- | --- |
| 1 | Ground | White main ground, pearl `#F1F3F6` bands, deep navy scenes `#0D1A3B` / `#162760` (centre-to-edge gradient). Order: hero (pearl, navy flood) / approach white / why navy / opinions pearl / pricing white / services pearl / contact navy / footer white. |
| 2 | Far | One cropped OS stencil per block: `::before` with `mask: url(mark) ... ; background: rgba(...)` (3.5 to 6 percent). 22 px dots at 7 to 10 percent on light grounds. |
| 3 | Mid | Radial glows behind the focal object: cobalt 6 to 8 percent, marigold 6 to 9 percent. |
| 4 | Edge | `::after` seam on the top of each block: previous-block colour above a gently rising cut, nickel hairline along the cut, and a 32 degree marigold slash (box 1.6 : 1 with a diagonal gradient) crossing it. Straight rules in the service block (`.process-section`, `.faq-section`, footer `small`) become a slash-led hairline. |
| 5 | Front | Hairline + two-stage shadow (`0 1px 2px` + `0 24px 48px -30px`) on `.xs-card`, `.xs__frame`, `.mail-card`, `.price-plan`, `.svc`, `.svc-def`, `.svc-index ol`, `.publication-card`, `.why__card`, `.contact-block form`. Price card and form hairlines are outside rings, so box sizes stay the same. |
| 6 | Drift | `@supports (animation-timeline:view())` and `prefers-reduced-motion:no-preference` and width above 800 px: `depth-drift` (translate 48 px to -48 px) on why / pricing / services / contact. The tall pinned blocks (`.xs`, `.opinion-section`) keep the far layer pinned (`position:sticky`, 100dvh) so it moves slower than the content. Without support or with reduced motion the layer is a static, finished background. |

## Selectors and tokens

- Blocks: `.atmosphere-hero` stage (`.v7-opening-stage`, flood `.v7-shadow-cover`, static card `.v7-film-scene`), `#approach.xs`, `#why.why`, `#opinions.opinion-section`, `#pricing.pricing-section`, `#services.svc-section`, `#contact.contact-block`, `.site-footer`. Phones: `.m-hero__scene`, `.m-opinions` plus the same section classes inside `.m-flow`.
- Per-block custom properties: `--wm-img`, `--wm-col`, `--wm-pos`, `--wm-size`, `--seam-prev` (colour of the block above). Global: `--depth-seam` (26 to 44 px), `--depth-dots`, `--depth-card-shadow`, `--silver-600: #666F7F`.
- Base pseudo rules use `:where()` (zero specificity), so per-block overrides win.
- Phones (max-width 800 px): watermark 84 vw, no drift, no pinning, seam 20 to 28 px, shorter slash rule.

## Contrast (WCAG 2.x, computed with a small Python script, 2 Nov 2026 build)

Worst case = every layer stacked on one pixel (dots treated as a flat overlay, navy mark, cobalt glow and marigold glow at their maximum). Realistic = no dots, mark plus the stronger glow.

| Block | Worst-case ground | Text | Conservative | Realistic | Need |
| --- | --- | --- | --- | --- | --- |
| hero | `#BDC1CC` | ink `#162760` | 7.78 | 10.48 | 3 / 4.5 |
| hero | `#BDC1CC` | audience line and cue `#3A4A75` 12 px (was `#475477`, 4.11 at worst case) | 4.81 | 6.48 | 4.5 |
| approach | `#D0D0D6` | ink / lede `#3A4A75` | 9.15 / 5.65 | 11.06 / 6.84 | 4.5 |
| opinions | `#CFCED4` | ink | 9.01 | 11.00 | 4.5 |
| pricing | `#D1D1D7` | ink | 9.22 | 11.16 | 4.5 |
| services | `#CBCDD7` | ink / `#29375F` | 8.90 / 7.36 | 10.85 / 8.97 | 4.5 |
| footer | `#F3F4F7` | `#4F5B7C` 11 px | 6.13 | 6.13 | 4.5 |
| why (dark) | `#37416C` | white / marigold 400 / `#B4BFD8` 14 px / marigold 300 11 px | 9.85 / 5.91 / 5.34 / 6.96 | n/a | 4.5 |
| contact (dark) | `#343F6E` | white / `#D0D9E5` / `#9FB0C8` 12 px | 10.05 / 7.05 / 4.56 | n/a | 4.5 |
| hero flood and card (dark) | `#323E6C` | white / `#E7EBF2` | 10.31 / 8.63 | n/a | 4.5 |

`#666F7F` on pearl 4.56:1, on white 5.07:1. Text inside opaque cards (`.svc`, `.price-plan`, `.xs-card`, `.mail-card`, form) sits on its own surface, not on the layers.

## Checks run

Build into a scratch directory (vite, success), `tsc --noEmit -p tsconfig.json` (exit 0), `scrollWidth` equals viewport width at 1440 px and at 390 px, section tops and heights at 1440 px identical to a build without `depth.css`. Not run: a pixel diff on real iOS Safari (mask with SVG and `animation-timeline` need a check there), Lighthouse, a screen reader pass.
