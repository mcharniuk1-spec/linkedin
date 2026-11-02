# Offer deck R15 (proposed)

Eleven 16:9 slides in the Outspoken design system: the offer for founder personal branding and company LinkedIn, the service map, the process, three indicative packages, scope, measurement, boundaries and the next step. Drafted by Codex (R15, 2 November 2026) from the approved positioning, the site's `pricing.json` and the 15-company competitor review; integrated by Claude after a text and render check.

Status: proposed. Owner acceptance false. Prices are the site's indicative packages, not final terms.

## Files
- `index.html`: the editable deck (HTML and CSS, no external requests). Fonts: Fraunces, Mona Sans, Geist Mono. Lockups: `lockup.svg`, `lockup-inverse.svg` (R13 OS stencil and the unchanged V5 wordmark).
- `../assets/offer-deck-r15/slides/01.png` to `11.png` and `../assets/offer-deck-r15/offer-deck.pdf`: renders of `index.html` (binaries live under `assets/` with rights entries). Fonts and their OFL notices: `../assets/offer-deck-r15/fonts/`.
- `render.mjs`: re-renders the PNGs and PDF. `npm i playwright && npx playwright install chromium`, then `node render.mjs . ../assets/offer-deck-r15` from this folder (uses the local Chrome channel).

## Checks (2 November 2026)
- Slide text read in full against `website/website-v3/pricing.json` and `content.json`: package names, prices, the eight and twelve pieces, the two 45-minute interviews and the four company adaptations match. The protected hero line (curly apostrophe) and "Book an intro call" are unchanged.
- Slides 01 and 07 inspected at full resolution. Codex inspected the full contact sheet and the pricing slide, and its PDF font check found the three brand families plus an Arial fallback; full glyph and weight parity is not verified.
- One line goes beyond the site copy: slide 08 says "Taxes and platform costs may be additional." Keep it only if the owner confirms it.
- A native editable Figma version (11 slides, simpler layout) exists in the Outspoken Figma file, board `242:1417`, built by Codex under the owner's account. See `../R15-INTEGRATION.md`.
