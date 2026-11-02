# Outspoken OS motion film R15, 16:9 (proposed)

28.00 s, 16:9 (1920x1080), 30 fps. An independent composition of the six scenes of the 4:5 film in `../build.py` (Codex `FILM-DIRECTION-R15`, 2 November 2026): it is not a crop and not a scaled copy. Cut times (4, 8, 12, 17 and 22 s), narration windows, captions and story are the same as in the 4:5 film, copied verbatim, so one voice recording fits both frames. Layout and choreography are new and use the horizontal axis: a wide interview frame, notes in a row, a tri-fold calendar of 6 columns x 4 rows, a buyer network that grows from left to right, three rings and three package cards in a row, and a centred close.

Status: proposed, owner acceptance false, nothing published. Music and effects are synthetic stand-ins (numpy/scipy); the master carries music and effects only and no voice. The narration in `VOICEOVER.md` is the 4:5 film's wording for the owner to record. Renders are not committed.

Source: `../build_16x9.py`. This folder holds the narration files that script writes (`VOICEOVER.md`, `voiceover.txt`, `captions.srt`) so the files of the 4:5 film in `../` are not overwritten.

## Scenes

| Time | Stage | Object and transformation | Transition into the next stage |
|---|---|---|---|
| 0–4 | S1 Thought into the O | 120 seeded thought particles (three sizes) cross the frame and contract onto the outline of the stencil O, which is sampled from `os-stencil-paths.json`; the O fills in, the S slides in and the slash pops, in the inverse colours on navy | 3.2–4.3: pearl opens out of the O's counter as a growing circle; the same circle clips a navy-ink copy of the mark, so the recolouring is exact |
| 4–8 | S2 Interview frame | The S and the slash step back; the O moves to the centre and its two halves part to the sides of the frame (brackets at about x 96–327 and 1593–1824); the strand fills the gap from the centre and becomes a speaking waveform (four path morphs, then flat) | 7.25–8.7: camera travel with parallax; the frame stays fixed on the lens while pale dots, two rulers (far and mid) and the three notes pass from the right at different depths |
| 8–12 | S3 The cut | Three portrait notes rest in the frame; the strand morphs into one diagonal that crosses all three; a marigold slash is drawn along it; the outer notes fly out, the frame leaves through the sides and the middle note scales up into the "Position" card | 10.4–11.95: a marigold curtain (a clipped field with a vertical edge) sweeps left to right behind the card and leaves the way it came |
| 12–17 | S4 Plan and post | The Position card is the middle panel of a tri-fold; the two wings unfold (3D fold) into a 6 x 4 calendar that fills left to right with themes, proof, formats and posts; the wings fold shut as one Post cell lifts into a post | 16.3–17.3: navy grows out of the post as a circle |
| 17–22 | S5 Conversations | The post shrinks into a node at the left; the strand grows left to right (path morph) and sprouts a network of 12 buyer nodes on links; nodes light up; signals return to three separate rings (engagement, qualified replies, attributed leads) with no numbers; the network drifts with parallax | 20.95–22.3: each ring flips edge-on (3D fold) and unfolds as a package card |
| 22–28 | S6 Packages and close | Three package cards with the current names and prices from `pricing.json` under its public label; at 23.3 the cards sink into one marigold bar that becomes "Book an intro call"; the OS lockup and the protected hero line appear centred; the final composition is complete at about 24.6 s and holds with a very slow push-in | Final hold |

## Transition mechanisms (five or more, none repeated as a plain fade)
- **Clipped colour field:** the pearl circle from the O's counter (3.2–4.3), the marigold curtain (10.4–11.95) and the navy circle from the post (16.3–17.3), each a clip-path on a ground layer; no full-frame fade of a colour.
- **Path morph:** one strand (fixed point count) goes flat, waveform, four waveform shapes, flat, the diagonal cut, then reappears as the trunk that grows into the buyer network; each buyer link grows by a path morph from its anchor.
- **Camera travel with parallax:** S2 into S3 (pale dots, far ruler, mid ruler and three notes at three depths against a fixed frame) and the slow drift of the buyer network and two faint strand layers in S5.
- **3D fold:** the tri-fold wings that open the calendar and fold shut behind the post (12.0 and 15.1 s), and the rings that flip into cards (20.95–22.3 s).
- **Mask and clip reveals:** the strand fills the gap of the parting O from its centre, the slash is drawn along the cut, the lockup, hero line and call to action are revealed by clip, and the cards sink into the call to action (shape morph to pill corners).
- Objects keep their identity across every seam: the O (particles, mark, interview frame), the middle note (note, Position card, calendar panel), the Post cell (cell, post, node), the rings (rings, cards) and the cards (cards, call to action). The only diagonal band in the film is the cut slash.

## Build and render (HyperFrames 0.9.2, FFmpeg, Python 3 with numpy and scipy, Google Chrome)
Run from the repository root; the scratch folder is outside the repository.
```bash
P=/tmp/outspoken-os-r15-16x9
python3 -c "import sys; sys.path.insert(0, 'design and website/film'); import filmkit; filmkit.sync_assets('$P', 'design and website/assets/public/assets/identity')"
cp "design and website/film/cut30/hyperframes/node_modules/gsap/dist/gsap.min.js" "$P/assets/"   # after npm ci in film/cut30/hyperframes
python3 "design and website/film/motion-os-r15/build_16x9.py" "$P" "design and website/design-system/identity-r13/os-stencil-paths.json" --audio
cd "$P" && HYPERFRAMES_SKIP_SKILLS=1 npx hyperframes@0.9.2 check && npx hyperframes@0.9.2 render . -w 2 -o renders/a.mp4 && npx hyperframes@0.9.2 render . -w 2 -o renders/b.mp4
python3 "<repository>/design and website/film/qa_films.py" renders/a.mp4 renders/b.mp4 --size 1920x1080 --duration 28
```
`npx hyperframes@0.9.2 check --at-transitions` samples every tween boundary as well. `--guide` is accepted for parity with the 4:5 build, but the timing-guide voice needs the macOS `say` command and is skipped elsewhere; the master never contains a voice.

## Rules kept in the source
Package names, prices, the public label, the hero line (with its curly apostrophe) and the call to action are read from `website/website-v3/pricing.json` and `content.json` at build time. Palette navy `#162760`, deep navy `#0D1A3B`, pearl `#F1F3F6`, marigold `#EAA93C` and `#F6D591`, Nickel 600 `#666F7F`, inverse `#F2F5FA` and `#B9C7DA`; Fraunces, Mona Sans and Geist Mono. No client names, results, outcome numbers, testimonials, faces or invented quotes; engagement, qualified replies and attributed leads are three separate, unquantified rings. All type is native HTML type of 28 px or more at rest and inside the 64 px safe margin; the caption pill sits at y 937–1012. Decorative lines (the two rulers, the pale dots and the faint strand layers) run off the canvas on purpose; every object that carries meaning stays inside the margin at rest. Only transforms, opacity, colours, clip-path and SVG `d` are animated. Seeded randomness only, no wall clock, no network, no absolute paths.

## Measured
See `QA.md` (written from the independent verifier's run).

## Not done
- The owner's recorded voice for both frames; the master has no voice. Music and effects are synthetic stand-ins and were checked by measurement only, not by listening.
- Owner acceptance of the composition, the identity and the copy. No human viewing pass on a phone, a TV or another browser; frames were inspected as stills and strips only.
- The package descriptors from `pricing.json` are not shown on the cards: the cards are on screen for about 1.5 s and the HyperFrames reading-time floor for a seven or eight word line is 2.6 to 2.9 s.
- The generated R15 images are not used (not in the repository; rights and review pending).
- The timing-guide voice (`mix-with-guide.wav`) is not produced in this build (no `say` command on the cloud machine); it is not part of the master.
