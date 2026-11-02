# Outspoken OS motion film (proposed)

28.00 s, 4:5 (1080x1350) for the LinkedIn feed. A clean motion-design piece of the identity system: the stencil OS mark assembles and a marigold cut line leaves the slash; the five depth layers of `design-system/DEPTH.md` build with their names; palette (navy, deep navy, pearl, marigold, Nickel 600) and type (Fraunces, Mona Sans, Geist Mono); the protected hero line word by word with the selection marker on 'care'; the lockup and the call to action. Scenes are joined by one designed seam, a slash panel in the next ground colour with a marigold leading edge, following the HyperFrames seam guidance.

Status: proposed, owner acceptance false, nothing published. Music, effects and the guide voice are **synthetic stand-ins** (numpy and scipy synthesis; macOS `say` for the guide voice). The narration in `VOICEOVER.md` is written for a human voice to be recorded later. Renders are not committed; build them with the steps below.

## Files
- `build.py`: generates the HyperFrames root composition (`index.html`) from the shared kit `../filmkit.py`; `--audio` synthesises the stems; `--guide` points the film at the mix with the guide voice.
- `VOICEOVER.md` (timed narration table), `voiceover.txt` (narration only), `captions.srt`.
- Shared: `../filmkit.py` (fonts, the OS mark as animatable parts from `design-system/identity-r13/os-stencil-paths.json`, audio synthesis, voiceover files) and `../qa_films.py` (measured QA with `--duration`).

## Build and render (HyperFrames 0.9.2, FFmpeg, Python 3 with numpy and scipy, Google Chrome)
```bash
P=/tmp/outspoken-os-motion            # any scratch folder outside the repository
python3 -c "import sys; sys.path.insert(0, 'design and website/film'); import filmkit; filmkit.sync_assets('$P', 'design and website/assets/public/assets/identity')"
cp "design and website/film/cut30/hyperframes/node_modules/gsap/dist/gsap.min.js" "$P/assets/"   # after npm ci in film/cut30/hyperframes
python3 "design and website/film/motion-os/build.py" "$P" "design and website/design-system/identity-r13/os-stencil-paths.json" --audio
cd "$P" && HYPERFRAMES_SKIP_SKILLS=1 npx hyperframes@0.9.2 check && npx hyperframes@0.9.2 render . -w 2 -o renders/a.mp4 && npx hyperframes@0.9.2 render . -w 2 -o renders/b.mp4
python3 "<repository>/design and website/film/qa_films.py" renders/a.mp4 renders/b.mp4 --size 1080x1350 --duration 28
```
Render on an idle machine: a heavily loaded machine can break the determinism comparison.

## Measured (2 November 2026, two renders on an idle machine)
- Master (voice-ready mix): 28.000 s, 840 frames, H.264 yuv420p 30 fps, AAC 48 kHz, -19.3 LUFS, -7.0 dBTP, 0 isolated-spike frames, 10 of 10 sampled frames identical across two renders: PASS
- Guide-voice version: -16.3 LUFS: PASS
- `hyperframes check`: zero errors.
