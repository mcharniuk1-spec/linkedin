---
name: outspoken-logo-icon-direction
description: Review the logo and icon boards and microphone candidates, present the strongest distinct directions for client selection, then rebuild the chosen logo and icons as editable vectors and adapt them to the website blocks and animations.
---

# Logo and icon directions: review, present, rebuild

Inputs: the OS and OUTSPOKEN logo boards and icon boards named in the handoff, the V5 identity (`assets/public/assets/revisions/v5/identity/`), and the twenty microphone candidates R10 (contact sheet and shortlist under `assets/public/assets/identity/mic-candidates-r10/`; full-size originals are local to the owner). The OS monogram board is **superseded**; the selected live identity stays the V5 capsule + outlined wordmark until the client chooses.

1. **Review** every board and candidate against the design rules (`outspoken-design-rules`): palette (navy, nickel, warm marigold only), spelling of OUTSPOKEN, small-size legibility (render each at 64, 32 and 24 px and look), contrast pairs, no glossy/glass/chrome, original forms only.
2. **Present** at most five strongest, clearly distinct directions on one board with the reasoning for each (what it keeps, what it changes, where it fails) and one recommendation marked "recommended, not client-approved". Stop and wait for the client's choice: never mark a direction selected yourself.
3. **Rebuild the selected logo and icons as editable vectors** (clean SVG, named layers/groups, no embedded raster, no live text for the wordmark: use the supplied outlined geometry). Provide mono, inverse (navy ground) and on-pearl variants plus a 24 px minimum version.
4. **Adapt** to the design system, website blocks and animations: keep the previous site story and animation logic (hero, merged experience story, Why Outspoken, closing panel) and improve them with the V10 tokens, the brand ease and matte surfaces. Provide a reduced-motion rendering (static, no parallax or flash).
5. **Check and record:** spelling, contrast ratios (computed), legibility at 24/32/64 px, reduced-motion behaviour (matchMedia, real checks), keyboard focus where interactive; update `release-manifest.json` and the rights ledger; report passes, failures and what was not run.
