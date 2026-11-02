# Outspoken launch film (proposed)

40.00 s, 16:9 (1920x1080). Announces the public repository and shows how the work was built: the repository tree, the security gate for agent skills (15 installed after a SkillSpector 2.9.6 scan, 13 not installed, 5 written for this repository), the open tool stack, the research sample (279 posts, 61 accounts), the logo work (30 concepts, one stencil mark kept), the five depth layers, and measured results (Lighthouse 100 accessibility and 100 best practices on the assembled build, 100 lead-function tests, 168 media files verified by hash, film QA). Every number comes from the repository records; tool names are plain text, no third-party logos. One check warning remains by design: the 33 skill names on the security-gate wall are under the 28 px reading floor; the scene's message is carried by the 72 px headline and the counts.

Status: proposed, owner acceptance false, nothing published. Music, effects and the guide voice are **synthetic stand-ins** (numpy and scipy synthesis; macOS `say` for the guide voice). The narration in `VOICEOVER.md` is written for a human voice to be recorded later. Renders are not committed; build them with the steps below.

## Files
- `build.py`: generates the HyperFrames root composition (`index.html`) from the shared kit `../filmkit.py`; `--audio` synthesises the stems; `--guide` points the film at the mix with the guide voice.
- `VOICEOVER.md` (timed narration table), `voiceover.txt` (narration only), `captions.srt`.
- Shared: `../filmkit.py` (fonts, the OS mark as animatable parts from `design-system/identity-r13/os-stencil-paths.json`, audio synthesis, voiceover files) and `../qa_films.py` (measured QA with `--duration`).

## Build and render (HyperFrames 0.9.2, FFmpeg, Python 3 with numpy and scipy, Google Chrome)
```bash
P=/tmp/outspoken-launch            # any scratch folder outside the repository
python3 -c "import sys; sys.path.insert(0, 'design and website/film'); import filmkit; filmkit.sync_assets('$P', 'design and website/assets/public/assets/identity')"
cp "design and website/film/cut30/hyperframes/node_modules/gsap/dist/gsap.min.js" "$P/assets/"   # after npm ci in film/cut30/hyperframes
python3 "design and website/film/launch/build.py" "$P" "design and website/design-system/identity-r13/os-stencil-paths.json" --audio
cd "$P" && HYPERFRAMES_SKIP_SKILLS=1 npx hyperframes@0.9.2 check && npx hyperframes@0.9.2 render . -w 2 -o renders/a.mp4 && npx hyperframes@0.9.2 render . -w 2 -o renders/b.mp4
python3 "<repository>/design and website/film/qa_films.py" renders/a.mp4 renders/b.mp4 --size 1920x1080 --duration 40
```
Render on an idle machine: a heavily loaded machine can break the determinism comparison.

## Measured (2 November 2026, two renders on an idle machine)
- Master (voice-ready mix): 40.000 s, 1200 frames, H.264 yuv420p 30 fps, AAC 48 kHz, -19.3 LUFS, -6.9 dBTP, 0 isolated-spike frames, 0 flashes, 10 of 10 sampled frames identical across two renders: PASS
- Guide-voice version: -16.3 LUFS, -7.1 dBTP: PASS
- `hyperframes check`: zero errors.
