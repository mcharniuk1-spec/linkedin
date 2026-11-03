# Launch film R15, 4:5 recomposition, 42 s, 1080x1350: measured QA (3 November 2026)

Source: `film/launch-r15/build_4x5.py` (HyperFrames 0.9.2, FFmpeg, numpy and scipy). Final page `index.html` sha256 `28fbb2ba6f49fc0ec0e6d67fbe372b398773b56c64b4ed02621feadc6b6ad0df`.
Master: `assets/film-r15/launch-r15-4x5-master.mp4`, 7,596,445 bytes, sha256 `d221aeb81d06a11c5f633a69ab914857f494a668c954ba2fc5ce0b178ab2aad0`. Raw numbers: `qa.json` (this folder). The master carries music and effects only, no voice.

## Gates
- `hyperframes check`: passed, 0 errors and 0 warnings in every section (lint, runtime, layout 0 issues across 9 samples, motion, contrast 19/19 text checks pass WCAG AA, craft, audio). The motion and snapshot modules are not active in this install (they report no findings without running).
- `hyperframes check --at-transitions`: passed, 0 issues across 930 layout samples. The first run of this stricter check reported 11 errors and 3 warnings at two intentional hand-offs (the calendar labels under the three cards that lift out, 24.4 to 25.07 s; the package cards clipped to the opening circle, 34.0 to 34.6 s). Both spots are now marked as intentional layering (`data-layout-allow-occlusion`, `data-layout-allow-overflow`). That is a markup-only change: a render of the marked build is byte-identical to the verified master.
- Two renders with `-w 2`, one at a time on an otherwise idle machine (45.2 s and 45.6 s): `a.mp4` and `b.mp4` are byte-identical (7,596,445 bytes, sha256 above), so all 1260 frames match, not only the ten sampled ones. These two renders are the independent verifier's (round 2); a third render of the final page, with the layout marks, gave the same hash again.

`qa_films.py a.mp4 b.mp4 --size 1080x1350 --duration 42`:

```
PASS duration: 42.000 s (expected 42.000)
PASS frame_size: 1080x1350
PASS video_codec: h264 yuv420p
PASS fps: 30/1
PASS audio_present: {"codec_name": "aac", "codec_type": "audio", "sample_rate": "48000", "channels": 2, "r_frame_rate": "0/0"}
PASS loudness: -19.3 LUFS integrated (voice-ready mix without voice; with the voice the target is about -16)
PASS true_peak: -6.8 dBTP
PASS frame_count: 1260 frames (expected 1260)
PASS isolated_spike_frames: 0 []
PASS flash_rate: luminance jumps > 70 at frames []; max 0 per second
PASS determinism_two_renders: 10/10 sampled frames identical ([0, 140, 280, 420, 560, 700, 840, 980, 1120, 1259])
OVERALL PASS
```

## Text and content
- `measure_text.cjs` (seeks the timeline every 0.25 s, 64 px safe margin, 28 px floor at the effective size, occlusion by painted shapes, text overlap): 55 text elements, **no persistent finding** of any kind (small, margin, occluded, overlap) and no page error. Smallest effective size 26.2 px, in motion only.
- Transient findings (entries and exits that last one 0.25 s sample or less): small [["Carousel", [[25, 25]]]]; margin []; occluded [["Post", [[24.5, 24.75]]], ["Profile", [[24.5, 24.5]]], ["Carousel", [[24.5, 24.75]]]]. The calendar labels fall to 26.2 px (25.6 px at 30 fps) for under 0.1 s while the grid folds back (24.94 to 25.04 s); the labels under the lifting cards (24.5 to 24.75 s) are intentional layering.
- The protected hero line (with its curly apostrophe), "Book an intro call", the public price label, the three package names and prices are read from `content.json` and `pricing.json` and appear byte for byte in the built page. No client names, results, outcome numbers, testimonials, faces or quotes; engagement, qualified replies and attributed leads are three separate unquantified rings.

## Picture
Inspected by the independent verifier and the art-direction reviewer as 1-second contact sheets, seven 0.25-second strips of nine frames across the cuts at 5, 10, 14, 19, 24, 29 and 34 s, and 22 full-resolution frames (package cards, hero line, call to action, lockup, calendar, labels, the diagonal band, the lens, the stencil and the card unfold). The lead viewed the contact sheets of the final render. No empty frame; five transition mechanisms are present (path morph of the 64-point strand, mask and clip reveals, camera travel with parallax, a 3D fold, clipped colour fields); the diagonal band appears once (12.0 to 13.0 s).

Reading time: the three package cards are complete and still from 35.05 to 38.65 s (3.6 s) with the indicative-price note visible throughout; the end card (lockup, protected hero line, "Book an intro call") is complete from 39.85 to 42.0 s (2.15 s) and the hero line starts to build at 39.0 s (the craft audit counts it readable for 2.90 s, above its 2.85 s floor; the reviewer measured it fully formed from about 39.25 s and the call to action from about 39.55 s). Captions hold 3.2 to 4.3 s; the three interview cards are readable 1.1 to 1.6 s.

## Independent verification and review
- Round 1: the independent verifier passed every mechanical gate; the reviewer asked for a revision (the package cards were readable together for only about 2.0 s). Fix: the card build was shortened and the hand-off to the end card moved 0.85 s later (hold 3.6 s, end card 2.15 s).
- Round 2: the independent verifier passed again (build, check, two byte-identical renders, qa_films, text and content measurements, picture); the reviewer **accepted** the film ("calm, on-brand, native 4:5; every seam is a geometric hand-off"). The master is render a of that run.
- After round 2 only two layout marks were added to the script (see the gates above); the render did not change.

## Open polish (minor, none blocks the release)
- The closing hero line and call to action are fully formed for about 2.8 s and 2.5 s (the whole end card is complete for 2.15 s), against 3.2 to 4.3 s for the captions; the pricing scene is motionless for about 3.6 s and reads like a slide.
- The three interview phrases leave after 1.1 to 1.6 s; a few mid-morph frames show blank cards (24.75 to 25.3 s, 29.0 to 29.5 s) or a near-empty field (34.07 to 34.27 s); at 39.0 s fragments of the previous scene show through the slit reveal.
- The lone waveform is drawn from straight segments and reads as a polyline; the strand's slash outline and the shrinking mark overlap for about 0.2 s at 14.3 to 14.5 s.
- Mono labels and period tags are 26 to 30 px, small for a phone; the caption pill is 82 % opaque over the market strands.
- The stencil recolours about 0.1 s before the diagonal band reaches it (12.35 to 12.45 s); the band's swoosh leads the picture by 0.2 to 0.4 s; the kit's fixed final bell rings at 37.8 s, before the hand-off.

## Limits
Sound was checked by measurement and by matching the script's event times to the picture, not by listening. Pictures were judged from stills, strips and contact sheets, not by continuous playback, in a Linux container with software WebGL; no Safari, iOS, TV or phone playback. Owner acceptance of the film, the wording and the identity stays false; nothing is published.
