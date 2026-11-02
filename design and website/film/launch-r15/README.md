# Outspoken launch film R15 (proposed)

42.00 s, 16:9 (1920x1080). Replaces the presentation-like R14 launch film with one continuous story that follows the offer, from Codex `FILM-DIRECTION-R15` (2 November 2026). One marigold strand carries the founder's material through eight stages, and each object turns into the next one instead of cutting to a new slide:

| Time | Stage | Object and transformation | Transition into the next stage |
|---|---|---|---|
| 0–5 | Your thinking | Seeded particles drift in, assemble into three clusters (experience, product decisions, evidence), then line up as the strand | Pearl ground bleeds out of the strand as a growing circle |
| 5–10 | Interview | The strand becomes a speaking waveform, then folds into three source cards | Cards slide together |
| 10–14 | Position | The cards overlap and the stencil cut removes the surplus; the strand becomes the slash of the OS mark | A marigold band leads the navy field along the slash diagonal; the mark recolours to its inverse |
| 14–19 | Market | The mark shrinks into a lens; three parallax layers of market strands travel through it, and the strands inside the lens turn marigold; three buyer questions | The lens flattens into the calendar's top edge; pearl folds down from the top |
| 19–24 | Plan | A 3D fold opens the calendar; cells fill with themes, proof and formats | Three cells lift out |
| 24–29 | Create | The three cells become a founder profile, a post and a carousel (pages fan out); the strand stays attached underneath | Navy grows out of the post card as a circle |
| 29–34 | Conversations | The three pieces travel to buyer nodes; replies return as signals to three separate rings (engagement, qualified replies, attributed leads), with no numbers | The three rings fold into cards |
| 34–42 | Packages | Three package cards with the current names and prices from `pricing.json`, then the OS lockup, the protected hero line and "Book an intro call" | Final hold |

Five transition mechanisms (path morph, mask and clip reveals, camera travel with parallax, a 3D fold, clipped colour fields); no repeated diagonal wipe. All type is native HTML type at 28 px or more, and captions follow the narration windows. Package names, prices and the protected lines are read from the site's JSON at build time, so the film cannot drift from the site.

Status: proposed, owner acceptance false, nothing published. Music and effects are synthetic stand-ins (numpy/scipy); the narration in `VOICEOVER.md` is Codex's proposed wording for the owner to record. Renders are not committed.

## Build and render (HyperFrames 0.9.2, FFmpeg, Python 3 with numpy and scipy, Google Chrome)
```bash
P=/tmp/outspoken-launch-r15
python3 -c "import sys; sys.path.insert(0, 'design and website/film'); import filmkit; filmkit.sync_assets('$P', 'design and website/assets/public/assets/identity')"
cp "design and website/film/cut30/hyperframes/node_modules/gsap/dist/gsap.min.js" "$P/assets/"   # after npm ci in film/cut30/hyperframes
python3 "design and website/film/launch-r15/build.py" "$P" "design and website/design-system/identity-r13/os-stencil-paths.json" --audio
cd "$P" && HYPERFRAMES_SKIP_SKILLS=1 npx hyperframes@0.9.2 check && npx hyperframes@0.9.2 render . -w 2 -o renders/a.mp4 && npx hyperframes@0.9.2 render . -w 2 -o renders/b.mp4
python3 "<repository>/design and website/film/qa_films.py" renders/a.mp4 renders/b.mp4 --size 1920x1080 --duration 42
```

## Measured (2 November 2026, two renders on an idle machine)
- `hyperframes check`: passed, 0 errors, 0 warnings (two layout notes about text blocks that overlap during a transition).
- Master (voice-ready mix): 42.000 s, 1260 frames, H.264 yuv420p 30 fps, AAC 48 kHz, -19.3 LUFS integrated, -6.8 dBTP true peak, 0 isolated-spike frames, 0 flashes, 10 of 10 sampled frames identical across two renders: PASS.
- Picture: inspected as a 2-second contact sheet and a 0.25-second strip across the position seam; the first render showed card text under the incoming mark, which was fixed before the final renders. Not yet inspected frame by frame at full resolution; sound checked by measurement only.

## Not done in R15
- The independently composed 4:5 version of this film (the OS motion film R15 is in `../motion-os-r15/`; its 16:9 composition is also open). Specified in `../../prompts/CLOUD-CLAUDE-R15.md`.
- The owner's recorded voice; the generated R15 style frames are not used (rights and visual review pending, see `../../R15-INTEGRATION.md`).
