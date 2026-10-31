---
name: outspoken-film-build
description: Build, render, mux, QA and retime the Outspoken launch film (Remotion 4.0.520, React, FFmpeg, numpy/scipy) in "design and website/film". Use for any film, teaser, 4:5 cut, audio change or voiceover retime.
---

# Outspoken film: build, QA, retime

Read first: `design and website/film/README.md`, `SPEC.md`, `DESIGN-FIT.md`, `PLAN-NEXT.md`, `voiceover/VOICEOVER.md`. All creative work is **proposed**; owner acceptance stays false. The score is code-synthesised (a stand-in for an orchestra): say so in every report.

## Build (from `design and website/film`)
```
npm ci --ignore-scripts --no-audit --no-fund
npm run sync && npm run typecheck && npm run vo && npm run audio
node render.mjs --comp Master --out out/master-video.mp4 --chunk 480 --concurrency 4
ffmpeg -i out/master-video.mp4 -i audio-out/mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -ar 48000 -ac 2 -movflags +faststart out/film.mp4
python3 scripts/qa/qa.py out/film.mp4 --report out/qa.json --sheet out/contact.png --timeline src/timeline.json
node render.mjs --comp Teaser --out out/teaser-video.mp4 --chunk 480 && node scripts/make-teaser.mjs out/teaser-video.mp4 out/teaser.mp4
```
Gotchas learned: keep `node_modules` on fast local disk (cloud-synced folders hang the bundler); render the master on an otherwise idle machine and run a frame-difference outlier check (spikes must coincide with scripted events); use an existing Chrome or the browser Remotion downloads in a cloud sandbox; picture is rendered muted, sound is muxed with FFmpeg.

## Rules for scenes (details in SPEC.md section 2)
Everything is a pure function of `useCurrentFrame()` (no CSS animation, no `Math.random`, no `Date.now`); colours and type only from `src/kit/tokens.ts`; explosions only on navy; accent text on pearl only in marigold-800; type >= 80 px Fraunces / 60 px Mona Sans / 56 px Geist Mono; bursts <= 8, calm for 30 frames after each, flashes <= 3 frames at alpha <= 0.2; every fictional element labelled; no invented statistics, clients, quotes or real people; wordmark only from the supplied SVGs.

## Sync and events
Each scene has `src/scenes/S{n}.events.json` (seconds from scene start, type, gain/dur/dir/pan). The component and the audio synth read the same file, so picture and sound cannot drift. After changing events or `src/script.json` run `npm run audio` and re-render.

## Retime to a recorded voiceover
1. Put takes in `voiceover/takes/` (WAV 48 kHz, one per line, names in `VOICEOVER.md`).
2. Get word timestamps with a local aligner (the Whisper CLI where available); never invent them.
3. Rewrite `src/script.json` (VO windows, scene frames) and every event tied to a spoken word; keep picture-to-word offset <= 0.3 s.
4. `npm run audio`, re-render, re-run QA, spot-check ten words by stills. Report PASS/FAIL with numbers.

## Report
List commands run and their results; state what was not run (human viewing, listening, phone test). Never call the film complete while the score is the stand-in and the voice is not recorded.
