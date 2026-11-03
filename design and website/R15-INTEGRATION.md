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
| OS motion film | `film/motion-os-r15/`: the OS motion film rebuilt on its six R15 scenes, 28 s 4:5. | `film/motion-os-r15/QA.md`: check passed, QA PASS, deterministic. |
| 4:5 launch film (R15b) | `film/launch-r15/build_4x5.py`: the eight-stage story recomposed for the tall frame, 42 s 1080x1350. | `film/launch-r15/4x5/QA.md`: check and `--at-transitions` pass, two byte-identical renders, QA PASS, independent verification and review. |
| 16:9 OS motion film (R15b) | `film/motion-os-r15/build_16x9.py`: the six OS scenes recomposed for the wide frame, 28 s 1920x1080. | `film/motion-os-r15/16x9/QA.md`: same gates. |
| Deployment | Vercel production `dpl_4Upo1DvbrxGYxBZawjHmpn7EUzRn` from commit `26aa01d`, aliased to the review domain. | Anonymous readback: bundles byte-identical to the local build, 109 identity/OG/library files and 168 media files matched, routes 200, R15 copy in the bundle, lead endpoint 405/200/400/403. |
| Offer deck | `offer-deck-r15/`: Codex's 11-slide HTML deck, renders and PDF; render script made portable (a local absolute import removed). | `offer-deck-r15/README.md`. |

Not changed: prices, package scope and exclusions, the identity (R13 OS stencil and V5 wordmark), the LinkedIn collection pipeline. The site uses no citron; the design review's citron note concerns the older Figma buttons.

## Held, with reasons
- **Generated elements and film frames (48 images, about 79 MB):** not added to the public repository or the site. The generator handoff records no rights or IP review, three frames have opaque edge pixels, seven images are flagged for excessive glow, and only contact sheets were inspected. They stay in the private run folder until the owner reviews them at full resolution and confirms the rights.
- **The 4:5 launch cut and the 16:9 OS motion composition:** not built in the first R15 round; built on 3 November 2026, see "R15b" below.
- **Figma:** Codex, working under the owner's Figma account, added to the existing file `m7zSeYVpEI88i9qwTrnUQt` a proposed variable collection (14 variables), four native specimen components and four text styles, an 11-slide raster deck board, an 11-slide native editable deck (board `242:1417`) and two boards with the 48 generated images. Claude's Figma connection has a view seat; a readback of `242:1417` on 2 November returned "you don't have edit access", so Claude has not verified these nodes. The complete native design system (OS and lockup family, button states, depth, service and price variants, bound variables) is still open.
- **Competitor coverage:** the detailed matrix was a cloud placeholder for Codex; full advertising, SEO/GEO and proof coverage across the 15 companies is not established; search volumes unknown.

## Gaps
Owner acceptance of copy, deck, films and identity; the owner's voice recordings; legal review of the privacy draft; Safari and iOS checks; a Figma edit seat for Claude or an owner-run readback; the launch steps in `seo/SEO-GEO-AEO-R14.md`.

## Film masters added (owner request, 2 November 2026)
The two R15 masters are in `assets/film-r15/` (launch 16:9, 42 s, 10.1 MB; OS motion 4:5, 28 s, 4.5 MB), registered as owned in `asset-rights.json` and the release manifest. They carry music and effects only, are proposed and are not published.

## R15b: the 4:5 launch cut and the 16:9 OS motion composition (3 November 2026, proposed)
The cloud session that was to build these two films (`prompts/CLOUD-CLAUDE-R15.md`) never produced a branch or a pull request, so the website lane built them directly on branch `r15-films`: `film/launch-r15/build_4x5.py` (42 s, 1080x1350) and `film/motion-os-r15/build_16x9.py` (28 s, 1920x1080), on the shared `film/filmkit.py` (a small patch lets the kit run where the macOS `say` command is missing; the master never contains a voice).

- **Verification.** Independent agents rebuilt each film from source in fresh folders (build, `hyperframes check`, two renders, `qa_films.py`, 1-second contact sheets, 0.25-second seam strips, text-size, margin and occlusion measurement, protected-text check) and an art-direction reviewer judged the pictures; failed or revised rounds were fixed and re-verified (4:5: 2 rounds; 16:9: 3 rounds, then one more fix verified by the lead). Both films were accepted by the reviewer with minor polish items open. Records: `film/launch-r15/4x5/QA.md` and `film/motion-os-r15/16x9/QA.md` with the raw `qa.json`.
- **Masters.** `assets/film-r15/launch-r15-4x5-master.mp4` (7.6 MB) and `assets/film-r15/os-motion-r15-16x9-master.mp4` (6.2 MB), registered as owned in `asset-rights.json` and the release manifest, with the same conditions as the first two masters (proposed, not published, music and effects only, indicative prices).
- **Publications.** Two drafts for the OUTSPOKEN profile, L3 (launch film, 4:5) and L4 (OS motion film, 16:9), in `linkedin-analysis/PUBLICATIONS-R15.md` with a Figma placement spec. Nothing is posted and nothing is written to Figma: Claude's seat on the owner's plan is View, so the placement is specified for someone with an edit seat.
- **Still open:** the owner's recorded voice; the rights review of the 48 generated images; Figma verification and placement with an edit seat; Safari and iOS playback checks; owner acceptance of the films, the wording and the identity (false).
