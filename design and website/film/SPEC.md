# Outspoken launch film: build specification

Film: about 80 s, 1920x1080, 30 fps, Remotion 4.0.520 + React + FFmpeg. Voiceover is recorded later by the owner in English; the picture must read without sound (LinkedIn autoplays muted). All sound is synthesised in code (`scripts/audio/synth.py`). No stock footage, no licensed samples, no people's likenesses.

Status of every creative element below: **proposed**. Owner acceptance is not implied.

## 1. Story in one line
A silent frame, a hard hit of colour, and a voice that tells the brilliant, unknown founder what staying quiet costs; their private mind map breaks out, becomes a public voice that travels from one account to many, and ends on one invitation: "Book an intro call".

## 2. Hard rules (design-system audit, 31 Oct 2026)
- Colours only from `src/kit/tokens.ts` (`C.*`): navy `#162760` ground, marigold scale (500 `#EAA93C` accent, 400 text-on-navy, 300 marker), nickel/silver `#A9AFBA`, pearl `#F1F3F6`, cobalt `#3157D5` (soft glow or rim on pearl only: 2.31:1 on navy, never a line or particle there), black `#101218` for the dark open (never `#000`).
- Explosions happen only on navy. On pearl/white marigold-500 is 1.5 to 2.1:1 and vanishes; light scenes stay calm. Accent text on pearl: marigold-800 only. Never silver or marigold as text on pearl.
- Type (`T.*`): display 200, headline 128, sub 88, body 64, label 56 (Geist Mono 500 uppercase +0.09em), caption 52. Fraunces 400 only at >= 80 px, Mona Sans >= 60 px, Geist Mono >= 56 px. Only roman font files ship: never italic or faux italic; emphasise with colour, `Marker`, or Mona Sans 600. No arrow glyphs in the fonts (draw arrows as SVG). Line limits: headline <= 7 words, <= 3 lines, <= 28 characters per line; <= 3 text elements per beat; one idea per beat.
- Reading hold: 20 frames + 9 frames per word beyond 3 (7 words = 56 frames). Hold fully revealed text >= 20 frames before it moves. No per-letter scramble on meaning-bearing text (labels only).
- Safe area: action 96 x 54 px, titles inside x 154 / top 108 / bottom 162. Nothing meaningful in the bottom 15 % (player controls).
- Motion: arrive curve `ease.out` (0.22,1,0.36,1); camera `ease.cam`; in-out `ease.inOut`. Durations at 30 fps: micro 5-8 f, arrival 14-17 f, diagram draw 15-24 f, camera 36-54 f, word stagger 3 f. A new visual event every 24-90 f (0.8-3.0 s); nothing holds still > 90 f without drift or camera motion. Camera: zoom 1.00-1.18 per shot (punch to 1.25 for <= 8 f), pan <= 8 % width, roll <= 1.5 deg, drift <= 6 px, parallax depths 0.3 / 0.6 / 1.0 / 1.6. Never zoom text > 6 % per second while it is being read.
- Everything is a pure function of `useCurrentFrame()`. No CSS animation/transition, no `useState` animation, no `Math.random`/`Date.now` (use `mulberry32(seed)` from `kit/rng.ts`), no `requestAnimationFrame`.
- Particle bursts: dots, short streaks, thin rings; <= 220 per burst (the ignition may use 320), 4-10 px, life 24-48 f (finale 66 f); text keep-out: bursts render behind text; keep them out of the text box + 24 px or at <= 35 % opacity inside it. Max 2 additive layers overlapping. The whole film has <= 8 big bursts; each is followed by >= 30 frames of calm in type and motion. Flashes: <= 3 frames, alpha <= 0.2, <= 3 per second (`Flash`).
- Every fictional element (founder, accounts, posts, buyer) carries a persistent `FictionalTag` or an on-element label while visible, >= 40 px. No LinkedIn logo or UI chrome, no reaction icons, no invented statistics, clients, quotes, competitor names, or real people. No guarantees. No standalone service-icon row, no marigold corner arrows/L-ornaments.
- Wordmark: only the supplied SVGs (`public/brand/*.svg`, loaded with `staticFile`); never re-typeset OUTSPOKEN; no rotation/3D/glow/scale > 6 %; keep particles out of the wordmark box + 1x height; inverse version on navy, width 640-900 px. Capsule mic `public/brand/flat.svg` (120x160): <= 1 meaningful use, >= 160 px tall, uncoloured.
- Highlight: `Marker` (marigold-300 bar, navy ink) once per beat, <= 4 words.

## 3. Kit API (`src/kit`, read-only for builders)
- `tokens.ts`: `C` colours, `T` type styles (spread into `style`), `FONT`, `SAFE`, `HEAT`, `PARTICLE_COLOURS`, `SHAPE`.
- `ease.ts`: `ease.out | inOut | cam | snap | in`.
- `rng.ts`: `mulberry32(seed)`, `noise1(x, seed)`.
- `Camera.tsx`: `<CameraRig keys={[{f, x?, y?, zoom?, rot?}]} drift seed>` and `<Layer depth>`; `useCam()`.
- `Particles.tsx`: `<Particles bursts={Burst[]} blend opacity />`; `Burst = {f, x, y, n, seed, speed:[a,b], drag?, gravity?, life:[a,b], size:[a,b], colors, angle?, shape?: 'dot'|'spark'|'ring', trail?}` (frame-local start, px coordinates in the 1920x1080 canvas).
- `Type.tsx`: `<Words text at stagger dur rise blur emphasis style />` (wrap words in `*asterisks*` for marigold emphasis), `<Scramble text at dur seed />` (labels only).
- `Chrome.tsx`: `FictionalTag`, `Marker`, `Vignette`, `Flash`.
- `Scene.tsx`: transition wrapper used by `Film.tsx` (builders do not use it).
- `head.ts`: `HEAD_PATH`, `HEAD_BOX` (800x900), `headPoints(n)`, `insideHead(x, y)`: the shared abstract head outline (S2 and S5).
- Fonts: loaded by the composition (`FontLoader`); use `T.*` or `FONT.*`.

## 4. Scene contract
Each scene is `src/scenes/S{n}.tsx` exporting `const S{n}: React.FC` (rendering its own full-frame ground) plus `src/scenes/S{n}.events.json`: the sound/visual sync list, an array of `{ "t": seconds from scene start, "type": "boom|hit|low|sparkle|whoosh|riser|tick|glitch", "gain"?: 0-1.5, "dur"?: seconds (whoosh/riser), "dir"?: "up|down", "pan"?: -1..1, "note": "what happens on screen" }`. The component imports the same JSON to time its bursts and flashes (`Math.round(t * 30)`), so picture and sound cannot drift. Helper files go in `src/scenes/S{n}.*.tsx`. Scene length in frames: `sceneById('S{n}').frames` (from `src/timeline.ts`); local frame 0 is the first frame of the scene. Voiceover windows (scene-local seconds) are in `src/script.json`; text beats should land on or just before the words they illustrate, hold through them, and the picture must still move while a line is read.

Standalone checks: `node render.mjs --comp Scene-S{n} --still <frame> --out out/s{n}-<frame>.png` and `--frames a-b --out out/clip.mp4` for short clips (no audio).

## 5. Scenes (global time from `src/script.json`)

### S1 The Charge (0-11.07 s, 332 f), ground near-black (navy under #071024 at 88 %)
VO: "Let's talk about you. The brilliant one. The quiet one. The one the right buyers still haven't heard of." (starts 1.8 s)
- 0-1.3 s: only a 6 px silver cursor, 120 px tall, blinking at centre every 15 f (steps, not eased). It exists so the silence reads as intentional.
- 1.3 s IMPACT (`boom`): ground rises from near-black to navy over 10 f, 3-frame marigold `Flash` (alpha 0.2), a 2-px marker ring grows from the centre (0 to 900 px over 21 f, `ease.out`), a P1 burst (36 particles, speed 260-620 px/s equivalent, drag 0.1, life 28 f, marigold ramp) from the centre, camera punch 1.0 to 1.08 and back over 24 f, 8 px shake decaying in 6 f.
- 1.4 s: the word YOU (display 200, pearl, Fraunces 400) slams from scale 1.6 to 1.0 over 9 f with a `Marker` bar behind it (navy ink).
- 3.2 s (`glitch`): hard cut to BRILLIANT (headline 128) with a 2-frame horizontal offset glitch (+/-6 px).
- 4.6 s (`tick`): QUIET in Mona Sans 600 shrinks from 120 to 64 px over 24 f while its tracking widens and its opacity drops to 0.45 nickel: the type literally gets quieter.
- 6.9-10.7 s: headline "The right buyers haven't heard of you." (`*heard*` emphasised, <= 3 lines) assembles by word; label "B2B AI software · Europe" (label 56) beneath a small marigold dot (the founder); `FictionalTag` appears from 6 s. The dot at the end sits exactly at (960, 540) so S2 can continue from it (`whoosh` up at 10.4 s).

### S2 Exhibit A (11.07-19.43 s, 251 f), navy
VO: "Exhibit A. Every decision, a trade-off. Every trade-off, a scar. All of it. In your head." (starts 0.35 s)
- Mono label "Exhibit A" (label 56) top-left inside the safe area, `Marker` bar.
- Camera pull-back from zoom 1.6 to 1.0 over 45 f; the dot from S1 becomes the first node. The founder's mind is a map drawn inside the head outline (`HEAD_PATH`, 1 px nickel hairline drawn at 2 px, scaled to ~620 px tall, centred slightly right): 8 diamonds = DECISIONS, 6 spring-joined pairs of circles = TRADE-OFFS (dashed 2 px edge), 8 hexagons = PRODUCT KNOWLEDGE; silver hairlines between clusters; cobalt soft glow behind; node labels only for the three categories (label 56) revealed as each cluster lights (`sparkle`).
- Sync to VO: "Every decision, a trade-off" (about 1.7 s): diamonds light one after another, pairs connect (dashed edge draws in 14 f); "Every trade-off, a scar" (about 3.9 s): one pair's dashed edge snaps and a small notch is cut out of the unchosen circle (a quiet marigold mark, not the wordmark's first-O notch); "All of it. In your head." (about 5.9 s, `low`): a 2-px glass-wall frame closes around the head and the label "In your head" appears.
- Persistent `FictionalTag` "Illustrative · fictional founder". Use `headPoints`/`insideHead` to place nodes (seeded). End: all nodes drift toward the centre ready for S3's silence (`whoosh` at 7.8 s).

### S3 The Silence (19.43-25.47 s, 181 f), navy, no strings, wind only
VO: "And out here? One word. Founder. Nothing else." (starts 0.35 s; real silence between lines)
- Everything drains: the map fades to a single hairline head outline, then to an empty profile card (pearl card on navy, 10-radius x2, avatar disc, one name bar, headline "Founder." in Fraunces 128 navy; nothing else, no LinkedIn chrome). Mono label "Out here" (label 56).
- A buyer disc (abstract, label "Buyer · illustrative" at 40+ px) slides in at 1.8 s, pauses over the card (0.8 s), and slides off (0.6 s, `ease.in`) and greys out: the stake of the scene. Sparse seeded dust motes drift (P5: 90 motes, nickel at alpha 0.15-0.4, one slow horizontal drift). `tick` at the buyer's arrival, `whoosh` down at its exit, `low` at 5.3 s (anticipation drone). No burst in this scene.

### S4 Ignition (25.47-35.0 s, 286 f), navy to a white card
VO: "We take what's in your head: the decisions, the trade-offs, the product. Then we make it public. In your voice." ("make it public" lands at about 5.85 s)
- 0-5.8 s: the head map returns small; its nodes converge into one bright marigold core (P7 convergence: ~150 nodes ease to the centre over 0-5 s with a growing `riser`), camera pushes 1.0 to 1.12; word beats: "Decisions", "Trade-offs", "Product" (labels, one at a time, label 56) as clusters are absorbed.
- 5.85 s DETONATION (`boom`): P2 idea burst (up to 320 particles, white to marker to marigold to cobalt, gravity slightly negative), 3-frame `Flash`, shockwave ring, camera punch to 1.25 for 8 f then settle. The core becomes the post card: white card (radius 20), 72 px avatar disc (the founder; this disc continues into S5), three nickel text bars (bars, not words), a cobalt-to-navy publication image slot; headline "Your thinking, in public." (sub 88, `*public*` marigold-400) placed outside the card in the safe area; label "In your voice" with `Marker`. `FictionalTag` from the burst. Calm for >= 30 frames after the burst.

### S5 The Spread (35.0-43.4 s, 252 f), navy
VO: "Then it can travel. From you, to your team, to buyers, to partners. One voice, many accounts."
- The avatar disc from S4 sits at (960, 540). Ripple rings (2 px non-scaling stroke, cobalt, the first marigold) expand every ~14 f. Three rings of abstract accounts grow (6, 14, 28 accounts; geometric avatars: disc, rounded square, half-moon, ring, capsule; navy/cobalt/nickel/pearl, marigold only on the active node). Edges draw with stroke-dashoffset (14 f) and a short spark trail (P6). Ring labels (label 56, one at a time): "Team", "Buyers (illustrative)", "Partners". Persistent `FictionalTag` text "Illustrative accounts · not a result".
- Escalation (sync to `events.json`): ring 1 = one `tick` + `sparkle`, ring 2 = denser ticks + `sparkle`, ring 3 = `sparkle` + glitch; at about 5.9 s ("One voice") a single marigold wave runs through all rings (P3 shards, `boom` gain 0.6). Camera pull-back 1.0 to 0.55 over 150 f, roll to -2 deg. Parallax: far rings d 0.35, edges 0.6, nodes 1.0, near bokeh 1.35 (alpha <= 0.2). Last 20 f: nodes ease toward `headPoints` positions so the network redraws the outline of the head from S2 (if the landing fails, fade the outline in behind the mesh instead). End with `whoosh` at 7.8 s.

### S6 The Work (43.4-52.73 s, 280 f), pearl ground (calm explain scene; the S5 to S6 change is an iris)
VO: "Positioning. Your profile. Content strategy. Writing. Visuals. Campaigns, LinkedIn ads included. Six jobs, each built on what makes you different." (first line 0.35-4.9 s, second line 5.2-8.95 s)
- Navy text on pearl, cobalt rims (5.47:1), marigold only as small filled shapes with a navy outline or as marker bar. No standalone icon row: each job gets its own 1.4-1.6 s mini-scene with a mono label (56) and a small moving diagram in context, cut on the spoken word (`tick` each): POSITIONING (40 nickel dots; one marigold dot leaves the crowd and settles inside an empty cobalt-rimmed frame), PROFILE (a profile skeleton assembles from particles: banner, avatar, headline bar, three lines fill), CONTENT STRATEGY (seven dots on a shallow arc light one by one, a cadence), WRITING (a struck-through generic draft line, 3 f stagger, then a replacement line of live type that sounds human; text must be generic, no claim, no brand names), VISUALS (a publication frame splits into background/subject/label planes and re-locks), CAMPAIGNS (dots rhythm, small mono tag "LinkedIn ads included").
- 5.2-8.9 s: six small modules dock around the founder disc (from S4/S5 continuity) forming a ring; a thin marigold thread, "what makes you different", runs through all six; on-screen: "Six jobs · one difference" (sub 88 at most 6 words). `whoosh` at transitions between mini-scenes (quiet), `tick` per word, `sparkle` at the dock.

### S7 The Verdict (52.73-62.27 s, 286 f), navy
VO: "The verdict. Anyone can list features. Only you can explain why you chose them. That difference is the asset."
- Mono label "The verdict". 7 x 7 grid of 49 identical nickel discs (r 22 px equivalents, evenly spaced) as the camera pushes in: "Anyone can list features." (headline 128). Then one disc's outline morphs into a closed 64-point spline (radius r x (1 + 0.18 x noise)), turns marigold-500, grows to centre while the other 48 dim; inside it a tiny callback of the S2 head map. "Only you can explain why you chose them." (<= 3 lines). `boom` (small) + `sparkle` at the morph.
- 7.0-9.2 s: "That difference is the asset." with `Marker` on "the asset"; kicker label "Looking for clients on LinkedIn? Start with what only you know." (caption 52, two lines max, bottom of the safe area but above the bottom 15 %: place it between 70 and 84 % of the height). `low` at 6.8 s; the last 1.2 s is a hush (no new events) ahead of the pale scene.

### S8 Five Things To Watch (62.27-70.47 s, 246 f), pearl ground, sober
VO: "We don't promise outcomes. We agree five things to observe, separately: time, recognition, voice, sales usefulness, conversations."
- Left: headline "We don't promise *outcomes.*" with a navy strike-through drawn across OUTCOMES (not marigold text on pearl: use marigold-800 for emphasis) . Right: five unconnected nodes on a pentagon (cobalt rim, navy mono labels "Time", "Recognition", "Voice", "Sales usefulness", "Conversations", label 56, two lines where needed), lit one by one on the spoken words (not in ascending order of size or pitch: use deliberately non-ascending `tick`/`sparkle` pitches via `gain` and `pan`), marker bar under each as it lights. A small funnel line draws and shatters under the caption "Separate. Never a funnel." The last 1.2 s is a clean hush before the finale; `whoosh` at the end uses `dir: up` leading into the S9 reveal.

### S9 The Invitation (70.47-79.9 s, 283 f), navy finale (bloom from centre)
VO: "Outspoken. Make the right buyers care about you and what you're building. Book an intro call."
- 0-0.45 s: converge: particles (P7) fly to the centre and become the inverse wordmark (`wordmark-inverse.svg`, 640-900 px wide, centred, reveal by straight clip-path or opacity; keep particles out of its box). `hit` at 0.45 s (drums enter; P4 corona behind, finale 66 f life, colours HEAT), second `hit` at 1.65 s as the hero line begins: headline "Make the right buyers *care* about you and what you're building." (verbatim, <= 3 lines, `*care*` on a `Marker`), mono line under the wordmark "For Europe-based B2B AI SaaS founders" (label 56 may wrap to two lines).
- From about 4.5 s the CTA capsule "Book an intro call" (marigold-500 fill, navy text, 6.86:1, capsule radius, scripted default-to-pressed) pops in with scale 0.9 to 1 (spring {16,180,0.8}, <= 6 % overshoot); it is not a link and shows no URL or placeholder. Final `hit` + `low` at 6.3 s with the biggest corona (<= 220 particles, 66 f). Faint illustrative network behind the hero line (alpha <= 0.15, labelled "Illustrative accounts" if visible). Tail: held end card for >= 75 frames, wind tail, drums fade. No flash after 7 s.

## 6. Audio plan (generated by `scripts/audio/synth.py` from `src/timeline.json`)
Soft bright string ensemble (D major colour: Dmaj9, Bm7, Gmaj7, A6/9; finale G, A, Bm, D), Karplus-Strong plucked arpeggio from the second third, wind bed that follows scene energy, risers/whooshes/glitches/ticks/sparkles from `events.json`, tom roll into drums only in the finale, true silences before S1 hit, S3, and before the finale. Output: `audio-out/mix.wav` (-16 LUFS, true peak <= -1.5 dBTP) and `mix-vo-bed.wav` (music/wind ducked 7 dB in the voiceover windows). This is a code-synthesised stand-in for a recorded orchestra; a licensed or composed score can replace the stems later.

## 7. Verification
`python3 scripts/qa/qa.py out/master.mp4 ...` reports container, resolution, loudness, true peak, silence gaps, freezes, black frames, motion energy per second, safe-margin samples, and a contact sheet. Taste, music quality, voice and brand feel need a human viewing/listening pass.
