# REQUEST R11: Outspoken visual library (image generation only)

To: Codex (image generation). From: Claude Code designer/developer. Date: 2 November 2026. Run: R11 (site one-pager, service blocks, 30-second motion film).
Scope: **generate images only.** Do not edit the website, code, tokens, Figma pages, notices or any file outside the results folder. Written files go only under the results folder named in the paste prompt (a local folder of the designer; the repository does not hold the originals).

## 1. Why this exists
The Outspoken site is becoming a one-page site (hero, experience story, why Outspoken, opinions, pricing, **detailed service blocks**, FAQ, contact) and a new 30-second motion film is being built from the same design system. The designer needs **many** high-quality visual elements, in several variations each, to choose from and to composite in code. Quantity matters: about 320 images in total (P0 140, P1 116, P2 61), in priority order (section 6). Quality gate in section 5 applies to every file.

## 2. Style bible (prepend this to every generation prompt)
Outspoken editorial style: calm, premium, matte. Soft diffuse window light from the upper left, low contrast, restrained film grain, cool navy-silver shadow side, **one** small warm marigold accent (rim of light, a garment detail, an object marker or a background tone) covering at most 10 % of the image. Palette only: navy `#162760`, nickel `#A9AFBA`, marigold `#EAA93C`, pearl `#F1F3F6`, and cobalt `#3157D5` only as a faint glow. Matte materials, fabric and paper; no gloss, chrome, glass, neon, purple, teal, rainbow gradients or plastic 3D look. **No text, letters, numbers, logos, watermarks, readable UI or flags anywhere** (screens show abstract blurred shapes; paper shows blank bars). People are **fictional**: they must not resemble any real person or celebrity. Hands must be anatomically correct (five fingers, natural joints); reject and redo malformed hands, teeth, ears or eyes. People are Europe-based B2B AI SaaS founders and operators: ages 28 to 55, mixed genders and backgrounds, business-casual clothes in navy, nickel, pearl or deep neutral tones. Backgrounds calm and uncluttered. Photographic realism for people and scenes; clean matte still-life realism for objects.

Reference images (colour and mood only; do not copy layouts): `refs/live-desktop-first-screen.png`, `refs/live-mobile-first-screen.png` (the current live site), `refs/ref2-editorial-light.png`, `refs/ref3-marigold-palette.png`, the graded hero portraits `refs/h1-shadow.webp`, `h2-founder.webp`, `h3-avatar-a.webp`, `h4-avatar-b.webp` (the target photographic grade), and `refs/mark-b01.svg` / `refs/lockup-b01.svg` (the microphone mark). Do not use any logo board.

## 3. Technical conventions
- Format: PNG, sRGB, no transparency (image generation does not give reliable alpha). Instead use **blend-ready backgrounds**:
  - `W` = pure white `#FFFFFF` background, subject darker than white: the designer uses *multiply* so white disappears.
  - `K` = pure black `#000000` background, subject emissive on black: the designer uses *screen* so black disappears. No vignette, no grey haze, no floor reflection.
  - `P` = pearl `#F1F3F6` soft studio background (normal blend).
  - `G` = a flat chroma green `#00FF00` surface only where a pack says "chroma screen".
- Sizes (long edge in px): 1:1 = 2048x2048; 4:5 = 1600x2000; 16:9 = 2560x1440; 9:16 = 1440x2560; 4:3 = 2048x1536; 6:5 = 2400x2000. If a size cannot be matched, keep the aspect ratio and report the actual size; never crop a subject.
- Leave deliberate **safe space** where a pack says "text space left/right/top": a calm, plain area of about 35 % of the frame.
- File names: `<PACK>-<NNN>-<slug>-v<k>.png` (for example `D2-014-writing-flatlay-v2.png`); `<k>` is the variant number. Keep every attempt that passes section 5; delete or move rejected attempts to `_rejected/`.
- Per pack also write `<PACK>/manifest.json` (array of objects: `file`, `pack`, `title`, `prompt` (the exact final prompt), `aspect`, `size`, `background` (W/K/P/G), `blend` (normal/multiply/screen), `variant`, `intended_use`, `checks` {`no_text`, `hands_ok`, `faces_ok`, `palette_ok`, `safe_space_ok`}, `notes`) and `<PACK>/contact-sheet.png` (all files of the pack as numbered thumbnails, 6 per row).
- Keep a running `PROGRESS.md` at the results root: pack, files done / planned, rejected count, next action. A new session must be able to continue from it.

## 4. Process
1. Work pack by pack in the priority order of section 6. Finish one pack (all variants, manifest, contact sheet, `PROGRESS.md`) before the next.
2. For people packs, first generate a style test of 2 images and check them against the `refs/` grade; then do the rest.
3. Vary composition, crop, pose, clothing, background tone and light direction **inside the style bible**; do not repeat the same face or pose twice in a pack.
4. If a session or rate limit is reached, stop cleanly, record the exact state in `PROGRESS.md`, and say so in `RESULT-R11.md`. Do not invent files you did not generate; do not rename a rejected attempt to pass.
5. Optional, only if a Figma connector with **edit** access is available in your session: add one frame per finished pack with its contact sheet to the existing Figma file `m7zSeYVpEI88i9qwTrnUQt`, on an existing page (do not add pages, delete anything or change variables), and record the node ids in `RESULT-R11.md`. If edit access is missing, say so and skip.

## 5. Quality gate (every image)
No text or letters anywhere (check signs, paper, screens, clothing, books). Correct hands and faces. Palette respected (no purple, teal, neon). Matches the grade of the reference heroes. Background rule (W/K/P/G) honoured exactly, with no halo, gradient or colour cast on W or K. Subject fully inside the frame. Readable at 400 px wide. Every person fictional.

## 6. Packs, in priority order
Priority P0 first, then P1, then P2. Counts are image files including variants.

### P0
**A1: Faces (24).** 1:1, `P` background (soft pearl studio), shoulders-up fictional founder portraits, looking at the camera, calm, slight smile or neutral, 24 different people (12 women, 12 men, varied ages 28 to 55 and backgrounds). Use: avatar strips, testimonial placeholders, post-card avatars.

**B1: Speaking shadows (12).** 6:5, `W` background. A fictional person speaking or gesturing, lit from behind and rendered as a deep navy photographic silhouette with a thin marigold rim light along the shoulder and hair, edges clean and natural, the figure fading softly to white on the left side. 12 poses: speaking with open hand, pointing, hands together, leaning on a desk, holding a microphone, looking up, in profile, seated at a table, walking, arms crossed, turning toward camera, gesturing with both hands. Use: hero figures (multiply over pearl).

**D2: Service illustrations (32).** 4:3, `P` background. Matte editorial still-lifes, one focal object group, one small marigold marker, **no text** (use blank bars for any writing). Eight services, four variants each: (a) top-down flat lay, (b) three-quarter hero view, (c) macro close-up with shallow depth of field, (d) wide view with text space on the left. Subjects:
- 01 profile: a matte navy profile card with a soft abstract portrait and blank bars, a marigold pin.
- 02 strategy: a hand-built route board: navy base, nickel pins, one marigold route line joining four stations, small calendar blocks.
- 03 writing: a pen resting on blank paper, a small voice recorder, interview notes as blank bars, a faint ink line in the shape of a sound wave instead of letters.
- 04 design: a fan of 4:5 carousel cards with abstract shapes and one marigold marker.
- 05 automation: three matte stations on a tidy line with small blocks moving through them and a single hand-stamp approval mark (abstract, no letters), nickel cables.
- 06 marketing: two overlapping paper speech-bubble sculptures and an envelope connecting two small abstract figures.
- 07 advertising: concentric matte rings like a target dial with one marigold dot and a measured stack of blocks beside it.
- 08 measurement: matte bar blocks, a small loupe over a rising line, one marigold marker on a single point.

**E1: Sparks and streaks (24).** 16:9, `K` background. Bright thin sparks, embers and light streaks bursting from an off-centre point, motion-blurred; 8 marigold, 8 warm white, 8 cobalt-and-white. No smoke, no background. Use: transition accents (screen).

**E2: Ink and paint splashes (24).** 16:9. 12 deep-navy ink splashes and splatters on `W` (use: multiply), 12 marigold paint splashes and wipes on `K` (use: screen). Dynamic, crisp edges, droplets around the main shape, no text, no shadows. Include 4 long horizontal "wipe" strokes in each set.

**C1: Interview scenes, landscape (12).** 16:9, `P`-toned natural room. A fictional founder speaking to an off-camera interviewer or camera: cool window light, matte textures, a small capsule microphone on a stand, shallow depth of field, generous space on the left. Vary person, room, framing (medium, close, over-the-shoulder).

**H1: Brand mark renders (12).** 1:1. The Outspoken capsule-microphone mark (follow `refs/mark-b01.svg` for the geometry: matte capsule head with a fabric-mesh pattern, a nickel band with a marigold ring, yoke, stem, base) as a physical matte object: 4 on pearl, 4 on navy, 2 on marigold, 2 embossed into paper. Faithful geometry, soft studio light, no text.

### P1
**A2: Speaking poses (12).** 4:5, `P`. Half-body fictional founders mid-speech, natural gestures, looking slightly off camera. **A3: Thinking and writing (12).** 4:5, `P`. Half-body: listening, thinking, writing in a notebook, reading a phone, on a call with a headset, reviewing a printed page (blank bars only).

**C2: Vertical scenes (12).** 9:16, natural light. A fictional founder speaking to a phone camera on a balcony, in a meeting room, at a window desk, walking in a street (no landmarks, no text, no signs); phone not visible or blank. Text space at the top. **C3: Phone in hand with chroma screen (8).** 9:16, a hand (correct anatomy) holding a modern phone with a flat `G` chroma-green screen, calm blurred room background in the palette. Use: compositing the site and feed UI on screen.

**F1: Atmospheres (12).** 6 in 16:9 and 6 in 9:16: pearl-to-navy soft atmospheric gradients with gentle wave forms and fine grain, one faint marigold glow, empty centre. **F2: Sound-wave fields (12).** 16:9 on pearl, fine nickel and cobalt hairlines forming flowing sound-wave ribbons, 15 to 40 lines, calm. **F3: Textures (8).** 1:1 seamless-ish: paper, linen, fabric mesh like a microphone grille, brushed nickel (matte), speckled pearl stone, navy suede, dotted grid on pearl, fine noise. **F4: Overlays (8).** 16:9, 4 film-dust and scratches on `K`, 4 soft grain on `W`.

**G1: Post covers (24).** 4:5, `P`. Abstract conceptual editorial covers for sample LinkedIn posts: a decision, evidence, a buyer question, a story, a lesson, a launch, a metric, a team, a customer conversation, a product judgement, a before and after, a quiet idea; objects and shapes only, a calm text space at the top. **G2: Carousel backgrounds (8).** 4:5, neutral pearl or navy fields with a subtle motif and a plain text area.

### P2
**D1: General objects (20).** 1:1, `P`. Capsule microphone, headphones, notebook and pen, closed laptop, phone, fan of index cards, speech-bubble sculpture, sound-wave sculpture, magnifier, calendar block, envelope, compass, hourglass, stacked paper, desk lamp, coffee cup, key, bookmark, small plant, ticket stub (blank). One variant each is enough; two if it is strong.

**E3: Mist and light leaks (24).** 16:9. 8 soft mist or smoke wisps on `K`, 8 light-leak flares on `K` (marigold, cobalt, warm white), 8 radial particle bursts on `K`.

**I1: Pricing sculptures (9).** 1:1, `P`. Three tiers, three variants each: a single card (a focused sprint), a neat stack of cards (monthly presence), a fan of cards plus a small company block (founder plus company). Matte, one marigold marker.

**J1: Contact and closing (8).** 4 in 16:9, 4 in 4:5. A calm morning window and desk with a phone and a notebook, a fictional founder seen from behind looking out, a quiet European city skyline with no recognisable landmark, no signs. Text space left.

## 7. Deliverables and result file
All images and manifests under the results folder, a `PROGRESS.md`, and `RESULT-R11.md` (packs finished with counts, packs not started, files rejected and why, size deviations, any Figma node ids, anything you could not do). Then stop. Do not push or publish anything.

## 8. Notes for the person who ingests the files
Ingestion into the repository (webp conversion, rights ledger entries, manifest hashes, contact sheets) is done later by the designer or the cloud agent. Generated people are fictional; the site keeps the label "Illustrative". Rights state for generated images is recorded as owned, fictional, AI-generated.
