# Outspoken launch film (Remotion + React + FFmpeg)

An animated, HTML-graphics promo film of about 80 s for founder-led LinkedIn services, built from the Outspoken design system. The owner records the English voiceover later; this folder holds everything needed to build, retime and re-render the picture and the code-synthesised sound.

Status: **proposed**. Every creative element (script, graphics, sound) is a proposal. Owner acceptance, founder approval of the wording, and a human viewing/listening pass are all still open. See `DESIGN-FIT.md` for what the design system does and does not cover for film, and `PLAN-NEXT.md` for the work that remains.

## Read first
- `SPEC.md`: the build specification (rules, kit API, scene contract, nine storyboards).
- `voiceover/VOICEOVER.md`: the voiceover script with timing for the owner's recording.
- `DESIGN-FIT.md`: design-system integrity and film-fit audit.
- `../design-system/film-tokens.json`: proposed film-only tokens.

## Layout
```
film/
  src/kit/            tokens, fonts, camera rig, particles, kinetic type, chrome helpers, head outline
  src/scenes/         S1..S9 scenes and their events.json (sound/visual sync lists)
  src/script.json     scene timing and voiceover windows (single source of truth)
  src/timeline.json   generated: scenes, energy, cues, silences, voiceover windows (for the audio synth)
  scripts/            sync-assets, build-timeline, make-vo-sheet, audio/synth.py, qa/qa.py
  render.mjs          bundle + render with an existing Chrome (no browser download)
  voiceover/          VOICEOVER.md, captions.srt, vo-timing.csv (generated)
```

## Build and render
```bash
npm ci --ignore-scripts --no-audit --no-fund   # pinned Remotion 4.0.520, React 19.1.1 (same lockfile as the studio runtime)
npm run sync                                    # fonts, wordmark/mic SVGs, tokens from ../assets and ../design-system
npm run typecheck
npm run vo                                      # voiceover sheet, SRT, CSV
npm run audio                                   # timeline.json, then audio-out/mix.wav (+ stems)
node render.mjs --comp Master --out out/master.mp4 --browser "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
ffmpeg -i out/master.mp4 -i audio-out/mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -movflags +faststart out/film.mp4
python3 scripts/qa/qa.py out/film.mp4 --report out/qa.json --sheet out/contact.png
```
`render.mjs` also renders one frame (`--still 120`), a frame range (`--frames 0-89`) or a single scene (`--comp Scene-S4`). `node_modules`, `out/` and `audio-out/` are not committed.

## Honest limits
- The music is **synthesised in code** (detuned additive string ensemble, Karplus-Strong plucks, synthesised toms and kick, filtered-noise wind). It is a production stand-in, not a recorded orchestra and not licensed library music. A composed or licensed score can replace the stems; `audio-out/` stems are kept separate for that.
- The numbers from `qa.py` (loudness, true peak, freezes, motion energy, margins) are measured. Whether it sounds good, whether the voice sits well, and whether the film feels on-brand need a human.
- No real people, clients, quotes or statistics appear. Every fictional founder, account, buyer and post carries an on-screen label.
- Remotion is source-available; organisations of four or more people need a paid licence (check `https://www.remotion.pro/license` against Outspoken's headcount before a commercial release).
- Fonts are Fraunces, Mona Sans and Geist Mono (SIL OFL 1.1, texts beside the files). Zodiak is not bundled.

## 30-second film (HyperFrames), 2 November 2026
`cut30/` holds a second, shorter film for LinkedIn: `SPEC-30S.md` (storyboard and QA gates), `VOICEOVER-30S.md` with `voiceover-30s.txt` and `captions-30s.srt` (voiceover text and timing; the film is built to be voiced afterwards) and `hyperframes/` (the project; see its README to rebuild). The 80-second Remotion film above is unchanged.
