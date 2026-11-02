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
Only the 1080x1920 master is composed. A 16:9 and a 4:5 re-composition are open tasks (see `../../PLAN-NEXT.md`); a pillarboxed 16:9 export can be made with FFmpeg as a stop-gap. The HyperFrames core skill was not installed (its static scan was HIGH); this project uses only the CLI (0.9.2, pinned) and plain GSAP. Optional image overlays from Codex pack R11 (sparks, ink and paint splashes on black or white) can replace or enrich the procedural effects after ingestion.
