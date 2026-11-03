# OS motion film R15, 16:9, 28 s, 1920x1080: measured QA (3 November 2026)

Source: `film/motion-os-r15/build_16x9.py` (HyperFrames 0.9.2, FFmpeg, numpy and scipy). Final page `index.html` sha256 `a9738ce276f796cb33d6f69aa0bbecd2da1c851c8dbb15a343a997303fcd9cc2`.
Master: `assets/film-r15/os-motion-r15-16x9-master.mp4`, 6,208,384 bytes, sha256 `9b550f52a4b333800955e4abf04497161289863d66d21afc3fb3f9eda042a120`. Raw numbers: `qa.json` (this folder). The master carries music and effects only, no voice.

## Gates
- `hyperframes check`: passed, 0 errors and 0 warnings in every section (lint, runtime, layout 0 issues across 9 samples, motion, contrast 28/28 text checks pass WCAG AA, craft, audio). The motion and snapshot modules are not active in this install (they report no findings without running).
- `hyperframes check --at-transitions`: passed, 0 issues across 1233 layout samples. The card text and the full-frame ground carry `data-layout-allow-occlusion` where the layering is intentional.
- Two renders with `-w 2`, one at a time on an otherwise idle machine (37.9 s and 37.5 s): `a.mp4` and `b.mp4` are byte-identical (6,208,384 bytes, sha256 above), so all 840 frames match, not only the ten sampled ones.

`qa_films.py a.mp4 b.mp4 --size 1920x1080 --duration 28`:

```
PASS duration: 28.000 s (expected 28.000)
PASS frame_size: 1920x1080
PASS video_codec: h264 yuv420p
PASS fps: 30/1
PASS audio_present: {"codec_name": "aac", "codec_type": "audio", "sample_rate": "48000", "channels": 2, "r_frame_rate": "0/0"}
PASS loudness: -19.2 LUFS integrated (voice-ready mix without voice; with the voice the target is about -16)
PASS true_peak: -7.2 dBTP
PASS frame_count: 840 frames (expected 840)
PASS isolated_spike_frames: 0 []
PASS flash_rate: luminance jumps > 70 at frames []; max 0 per second
PASS determinism_two_renders: 10/10 sampled frames identical ([0, 93, 187, 280, 373, 467, 560, 653, 747, 839])
OVERALL PASS
```

## Text and content
- `measure_text.cjs` (seeks the timeline every 0.25 s, 64 px safe margin, 28 px floor at the effective size, occlusion by painted shapes, text overlap): 36 text elements, **no persistent finding** of any kind (small, margin, occluded, overlap) and no page error. Smallest effective size 25.3 px, in motion only.
- Transient findings (entries and exits that last one 0.25 s sample or less): small [["Post", [[14, 14]]], ["Format", [[14.5, 14.5]]], ["per month", [[21, 21]]]]; margin [["A customer question", [[7.5, 7.5]]]]; occluded [["01", [[10.25, 10.25]]], ["02", [[7.5, 7.5]]], ["03", [[7.75, 7.75]]], ["The proof behind it", [[7.75, 7.75]]], ["Post", [[15.25, 15.25]]]]. The unit labels fall to 25.3 px while the package cards unfold in 3D (21.0 s); the notes pass behind the interview brackets while they enter (7.5 to 7.75 s) and leave (10.25 s).
- The protected hero line (with its curly apostrophe), "Book an intro call", the public price label, the three package names and prices are read from `content.json` and `pricing.json` and appear byte for byte in the built page. No client names, results, outcome numbers, testimonials, faces or quotes; engagement, qualified replies and attributed leads are three separate unquantified rings.

## Picture
Inspected by the independent verifier and the art-direction reviewer as 1-second contact sheets, five 0.25-second strips of nine frames across the cuts at 4, 8, 12, 17 and 22 s, and full-resolution frames; the lead viewed the contact sheets and the exit frames of the final render. All 840 frames were scanned for empty frames (none). Five transition mechanisms are present (clipped colour fields, path morph, camera travel with parallax, 3D folds, mask and clip reveals); the only diagonal band is the cut slash (8 to 12 s). Every seam carries an object across it: the O (particles, mark, interview frame), the middle note (note, Position card, calendar panel), the Post cell (cell, post, node), the rings (rings, cards) and the cards (cards, call to action).

Reading time: the three package cards are legible for 3.7 to 3.9 s (at rest 3.5 to 3.7 s); the end card is complete from 25.53 s and holds 2.47 s, the hero line having been on screen since 25.04 s.

## Independent verification and review
- Round 1: the independent verifier failed the film on one major defect (the package cards were legible for only 1.1 to 1.5 s). Fix: the card text arrives with its card, and the hold and the sink into the call to action move 0.7 s later.
- Round 2: the verifier passed; the reviewer asked for a revision (cards settled for about 1.9 s). Fix: the rings fold 0.55 s earlier (from 20.4 s) and the closing segment was re-balanced inside the fixed 28 s (cards still for about 3.3 s, exit of a 0.4 s fade plus a 0.54 s sink, qualifier and units raised to 32 px).
- Round 3: the verifier passed (build, check, two byte-identical renders, qa_films, measurements, picture); the reviewer **accepted** the film ("one chain of morphs carries the story"). It listed one visible polish flaw: the three cards' rounded corners snapped square for about five frames at 24.9 s (GSAP padded the one-number start radius with 0).
- After round 3 the corner snap was fixed with one `tl.set` (the start radius written as an explicit pair) and the film was verified again by the lead with the same tools (the gates above are that run). Against round 3's render the audio is identical (md5 `5d8cbcc8bb608a5a4a59460b38977c0d`); frames before 24.83 s differ by at most x264 look-ahead noise (PSNR 63.8 dB or more) and the first frames that really differ are 24.87 to 25.3 s (PSNR 34.6 dB at 24.90 s, back above 58 dB by 25.27 s), where the corners now stay rounded.

## Open polish (minor, none blocks the release)
- The end card holds 2.5 s, the ring labels (engagement, qualified replies, attributed leads) 1.2 to 1.6 s and the three interview phrases about 1.9 s, shorter than the 3.3 to 4.2 s of the other beats; the package hold is nearly static.
- Murky transitional frames: the plan grid turning into the post card (15.4 to 15.8 s, a blank warm-white card), the cut and scatter of the notes (9.5 to 10.4 s, the slash crosses the card text and the outer cards pass behind the brackets), the rings flipping into cards (20.5 to 20.9 s). During the sink the three cards overlap as one cream plate with ghosted text for about 0.15 s (25.1 s).
- The 22 s seam has no picture event (the cards are already in place; the cut sound falls on static cards); the strand pokes out past the opening brackets for 0.4 s (4.9 to 5.3 s).
- The opening frame is a bare navy field of dots (a weak poster frame; the mark is at 3.5 s); the plan panels use 143 px side margins against 96 px elsewhere; chapter labels are 28 to 32 px in low-contrast slate; "Founder + Company" sits 35 px from the card's right edge.
- The package descriptors from `pricing.json` are not shown on these cards (see the README).

## Limits
Sound was checked by measurement and by matching the script's event times to the picture, not by listening. Pictures were judged from stills, strips and contact sheets, not by continuous playback, in a Linux container with software WebGL; no Safari, iOS, TV or phone playback. Owner acceptance of the film, the wording and the identity stays false; nothing is published.
