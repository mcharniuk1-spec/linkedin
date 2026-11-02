# R15 integration record (proposed), 2 November 2026

Inputs: the Codex R15 review drafts (product analysis, competitor offer review, site copy patch, film review and direction, design-system review, offer deck, Figma frame map, 24 generated elements and 24 film frames), written against repository commit `e9176df`. They are proposals, not owner approval. Owner acceptance stays false; nothing is published; no outreach; spend 0.

## Applied in this repository
| Area | Change | Evidence |
|---|---|---|
| Site copy | `SITE-COPY-R15.json` applied key by key to `website/website-v3/content.json` (offer, experience, stack, services and closing blocks) and `service-details.json` (title, intro, the eight services, the definition). | `content.json` sha256 `43c07bc6…fd754` → `9d28e374…4e780`; `service-details.json` `c9175a8b…48d91` → `ec6b3913…bb82`; `pricing.json` unchanged `cadb0860…99be`. Version `3.1.0-copy-draft+r15`. |
| Protected text | `protected.hero`, `protected.vp`, `protected.cta`, `home.title`, `home.body`, `home.cta` checked byte for byte before and after (curly apostrophes kept). | Assertion in the apply script passed. |
| FAQ | Codex's five proposed questions merged with the current set instead of replacing it: kept the start, price, voice, founder-profile, search, automation, results and form-privacy questions; Codex's answers replace the overlapping profile-or-strategy, founder-time, ad-spend and guarantee questions. 13 questions. A missing-space typo in the search answer was fixed. | Every claim in the new answers checked against `pricing.json` (workshop, profile direction and 30-day direction; two 45-minute interviews; weekly 30-minute conversation; media spend separate). |
| Motion tokens | `design-system/motion-tokens.json` (proposed): durations, easings, stagger, distances and the four transition rules from the Codex design review. Kept apart from `tokens.json` so the token generator is unchanged. | Type-check and build passed. |
| Launch film | `film/launch-r15/`: a new 42 s 16:9 film on the eight-stage story. | `film/launch-r15/README.md`: check passed, QA PASS, deterministic. |
| Offer deck | `offer-deck-r15/`: Codex's 11-slide HTML deck, renders and PDF; render script made portable (a local absolute import removed). | `offer-deck-r15/README.md`. |

Not changed: prices, package scope and exclusions, the identity (R13 OS stencil and V5 wordmark), the LinkedIn collection pipeline. The site uses no citron; the design review's citron note concerns the older Figma buttons.

## Held, with reasons
- **Generated elements and film frames (48 images, about 79 MB):** not added to the public repository or the site. The generator handoff records no rights or IP review, three frames have opaque edge pixels, seven images are flagged for excessive glow, and only contact sheets were inspected. They stay in the private run folder until the owner reviews them at full resolution and confirms the rights.
- **The 4:5 launch cut and the rebuilt OS motion film** (28 s 4:5 and an independent 16:9): specified, not built in this round. See `prompts/CLOUD-CLAUDE-R15.md`.
- **Figma:** Codex, working under the owner's Figma account, added to the existing file `m7zSeYVpEI88i9qwTrnUQt` a proposed variable collection (14 variables), four native specimen components and four text styles, an 11-slide raster deck board, an 11-slide native editable deck (board `242:1417`) and two boards with the 48 generated images. Claude's Figma connection has a view seat; a readback of `242:1417` on 2 November returned "you don't have edit access", so Claude has not verified these nodes. The complete native design system (OS and lockup family, button states, depth, service and price variants, bound variables) is still open.
- **Competitor coverage:** the detailed matrix was a cloud placeholder for Codex; full advertising, SEO/GEO and proof coverage across the 15 companies is not established; search volumes unknown.

## Gaps
Owner acceptance of copy, deck, films and identity; the owner's voice recordings; legal review of the privacy draft; Safari and iOS checks; a Figma edit seat for Claude or an owner-run readback; the launch steps in `seo/SEO-GEO-AEO-R14.md`.
