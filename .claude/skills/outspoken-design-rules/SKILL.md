---
name: outspoken-design-rules
description: Apply the Outspoken design system (navy, nickel, marigold; Fraunces, Mona Sans, Geist Mono; wordmark and fictional-label rules) to a website block, document or film. Use before changing any visual or copy.
---

# Outspoken design rules (V10, proposed values marked)

Truth lives in `design and website/design-system/` (`tokens.json`, `type-roles.json`, `DESIGN.md`, `style-grammar.json`) and `film-tokens.json` (proposed, film only). Read `film/DESIGN-FIT.md` for known defects before trusting a document over a token.

- **Colour:** navy `#162760` ground; marigold scale (500 `#EAA93C` accent and button fill, 400 text on navy, 300 marker, 800 text on light); nickel/silver `#A9AFBA`; pearl `#F1F3F6`; cobalt `#3157D5` as glow or rim on pearl only. Contrast (measured): pearl on navy 12.65, marigold-500 on navy 6.86, silver on navy 6.38, navy on marker 9.94, marigold-800 on pearl 6.13; **fails:** silver on pearl 1.98, marigold-500 on pearl 1.85, cobalt on navy 2.31. Never silver or marigold as text on pearl.
- **Type (OFL, bundled):** headings Fraunces 400 (-2 % tracking), text Mona Sans 400, buttons 600, labels Geist Mono 500 uppercase +9 %. No italics (roman files only), no arrow glyphs (draw SVG).
- **Shape:** radii 6 / 10 / 14 px (x2 for film), hairline 1-2 px, one dominant focal object, no standalone service-icon row, no marigold corner arrows, no glossy 3D plates.
- **Wordmark:** only the supplied outlined SVGs; never re-typeset; keep the first-O notch; no rotation, glow or scale > 6 %; inverse on navy, primary on pearl, never on marigold.
- **Mark (R13, proposed):** the OS stencil mark with the unchanged V5 wordmark, only in the supplied lockups (`assets/identity/v13/`). Use the solid build below 48 px. On light grounds the S and SPOKEN use Nickel 600 `#666F7F` (4.56:1 on pearl); the old Nickel `#A9AFBA` is 2.2:1 on white and stays for borders and rules only. The marigold slash is an accent. See `design-system/identity-r13/ADAPTATION-R13.md`.
- **Honesty:** fictional founders, accounts, posts and reviews carry a visible label; no invented statistics, clients, quotes, real people or guarantees; protected copy (hero line, value proposition, "Book an intro call", prices) is not edited without the owner.
- **Motion:** brand ease `cubic-bezier(0.22,1,0.36,1)`; respect reduced motion on the website; film motion is frame-driven.
- **Tokens:** change `tokens.json`, run `node scripts/generate-tokens.mjs` in `website/`, never hard-code hex values in components.
