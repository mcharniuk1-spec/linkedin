# Outspoken 30-second film (HyperFrames source)

Status: **proposed**; owner acceptance false. Specification: `../SPEC-30S.md`. Voiceover text and timing: `../VOICEOVER-30S.md` (+ `.txt`, `.srt`). The film is picture, music and effects only (no voice) and is built so a recorded voice can be laid on top without retiming.

## What is here
- `build.py` generates `index.html` and `compositions/*.html` (seven scenes, captions, chapter chips) from templates; `src/root.template.txt` holds the root: the six radical transitions (gooey ink flood, spark burst, paint wipe, whip pan, glowing iris, selection-box expansion) as pure functions of time (`hf-seek` canvas plus GSAP).
- `scripts/make_audio.py` synthesises the score, effects and an optional guide voice (macOS `say`, timing reference only). Everything is a synthetic stand-in.
- `scripts/qa.py` runs the measured checks (duration, size, codec, loudness, true peak, isolated-spike frames, flash rate, determinism across two renders).
- No binaries are stored here: fonts, graded portraits, marks and icons are copied from `../../../assets/public/assets/identity/` by `scripts/sync-assets.sh`.

## Rebuild
Requirements: Node 22 or newer, FFmpeg (8.x), Google Chrome or a Chrome headless shell, Python 3 with numpy and scipy. Disable HyperFrames telemetry once (`npx hyperframes telemetry disable`) and skip its skill installer (`export HYPERFRAMES_SKIP_SKILLS=1`).
```bash
npm ci --ignore-scripts
npm run sync       # copies assets, vendors GSAP, synthesises audio
npm run build      # generates index.html and compositions/
npm run check      # lint, runtime and layout gate (0 errors expected)
npm run render     # renders renders/cut30-9x16.mp4 (about 16 s on an M4 Pro)
npm run qa         # measured QA report
```
Render the same project twice and pass both files to `python3 scripts/qa.py first.mp4 second.mp4` to measure determinism.

## Known limits
Two aspect ratios are composed: 1080x1920 (`index.html`) and **4:5 reel 1080x1350** (`index-4x5.html`: the same scenes in a shifted 1080x1920 world cropped to 1350 px, with its own end scene `s7-4x5.html`). `npm run build` generates both; `npm run render:4x5` and `npm run qa:4x5` render and check the 4:5 film. A 16:9 re-composition is an open task (see `../../../prompts/CLOUD-CLAUDE-R11.md`). The HyperFrames core skill was not installed (its static scan was HIGH); this project uses only the CLI (0.9.2, pinned) and plain GSAP. Optional image overlays from Codex pack R11 (sparks, ink and paint splashes on black or white) can replace or enrich the procedural effects after ingestion.

## R13 identity swap (2 November 2026, proposed)
The S4 mark pulse, the end-card mark with sound rings and the end lockup now use the OS stencil mark (`assets/public/assets/identity/v13/`, copied by `scripts/sync-assets.sh`). The wide mark collided with the word "voice" beside the headline, so S4 places it centred under the headline. Measured on an idle machine, two renders per aspect: 9:16 (1080x1920) and 4:5 (1080x1350) both PASS the full QA (30.000 s, h264 yuv420p, 30 fps, -19.1 LUFS, -1.8 dBTP, 0 isolated-spike frames, flash rate within limit, 9 of 9 sampled frames identical between renders). `hyperframes check` passes with zero errors per root; run it on one root at a time (two roots in one folder trip the multiple-roots lint) and expect the two known GSAP baseline warnings for `#s7-mark .rg`. An earlier 9:16 run under heavy machine load failed the determinism comparison (6 of 9); render on an idle machine.
