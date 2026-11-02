# Outspoken launch film R15, 4:5 recomposition (proposed)

42.00 s, 4:5 (1080x1350), 30 fps. An independent recomposition of the 16:9 launch film (`../build.py`) for the tall frame, not a crop or a scaled copy: the same eight stages, the same cut times (5, 10, 14, 19, 24, 29, 34 s), the same narration windows and captions (`CUTS`, `LINES` and `SCENES` are copied verbatim, so one voice recording fits both frames) and the same story logic, but every stage is laid out and choreographed again on the vertical axis. One marigold strand carries the founder's material, and each object turns into the next one.

Status: proposed, owner acceptance false, nothing published. Music and effects are synthetic stand-ins (numpy/scipy); there is no voice in the master. The narration in `VOICEOVER.md` is Codex's proposed wording for the owner to record. Renders are not committed.

| Time | Stage | Object and transformation | Transition into the next stage |
|---|---|---|---|
| 0–5 | Your thinking | Seeded particles drift down into the frame, gather into three stacked clusters (experience, product decisions, evidence), then line up from top to bottom as the strand | The pearl ground opens out of the strand as a vertical slit (clipped colour field) |
| 5–10 | Interview | The strand speaks as a vertical waveform, then unfolds sideways into three stacked source cards whose small waveforms keep moving | The cards slide together and overlap |
| 10–14 | Position | The OS stencil cuts the surplus from the overlapping cards (a two-clip aperture: the silhouette closes while the counter and slits open) and leaves the O; the strand wraps into the outline of the slash and the slash fills; the S is revealed by a mask | A marigold band leads the navy field along the slash diagonal (the only diagonal wipe in the film); the mark recolours to its inverse as the edge passes it |
| 14–19 | Market | The mark shrinks into a lens; three parallax layers of market strands travel top to bottom through it and turn marigold inside the lens; three stacked buyer questions | The strand pinches into the lens, the lens flattens into the calendar's top edge, and pearl folds down from the top |
| 19–24 | Plan | A 3D fold opens the calendar (4 columns x 6 rows); cells fill row by row with themes, proof and formats; three cells are outlined in marigold | Three cells lift out |
| 24–29 | Create | The three cells become a founder profile, a post and a carousel (pages fan out), stacked in one column; the calendar folds back and the strand drops underneath the cards | Navy grows out of the post card as a circle |
| 29–34 | Conversations | The three pieces iris down to discs and fly up to buyer nodes in a mesh; replies fall as signals to three separate stacked rings (engagement, qualified replies, attributed leads), with no numbers | The three rings fill and open into package cards |
| 34–42 | Packages | Three package cards in one column with the current names and prices from `pricing.json` and the on-screen note that prices are indicative, then the stacked OS lockup, the protected hero line and "Book an intro call" | Final hold of about 2.3 s |

## Transition mechanisms (at least five different ones)
- **Path morph:** the strand is one SVG path with a fixed 64-point count and morphs between a vertical line, a speaking waveform, the outline of the slash, the line through the lens, a single point, the calendar's top edge, an underline and an arc.
- **Mask and clip reveals:** the stencil aperture in stage 3 (two polygon clips built from the OS stencil's own outline: the silhouette closes, a frame with a hole opens the counter and slits), the mask that reveals the S, the market scene clipped by the pearl fold front, circular iris clips (pieces become discs, rings open into cards) and the slit reveal of the final lockup.
- **Camera travel with parallax:** three layers of market strands travel top to bottom at different speeds while the marigold highlight stays fixed in the lens; slow vertical camera drifts in the quiet stages.
- **3D fold:** the calendar opens downward from its top edge (`rotateX`, with perspective) and folds back up when the cells lift out.
- **Clipped colour fields:** the pearl slit (stage 1 to 2), the marigold band and the navy field on the slash diagonal (stage 3 to 4), the pearl fold from the top (stage 4 to 5) and the navy circle out of the post card (stage 6 to 7).

All type is native HTML type at 28 px or more at its effective size, inside a 64 px safe margin at rest (x 64 to 1016, y 64 to 1286, captions included). The captions follow the narration windows. Package names, prices, the price note and the protected lines are read from the site's JSON at build time, so the film cannot drift from the site.

## Build and render (HyperFrames 0.9.2, FFmpeg, Python 3 with numpy and scipy, Google Chrome)
```bash
P=/tmp/outspoken-launch-r15-4x5
python3 -c "import sys; sys.path.insert(0, 'design and website/film'); import filmkit; filmkit.sync_assets('$P', 'design and website/assets/public/assets/identity')"
cp "design and website/film/cut30/hyperframes/node_modules/gsap/dist/gsap.min.js" "$P/assets/"   # after npm ci in film/cut30/hyperframes
python3 "design and website/film/launch-r15/build_4x5.py" "$P" "design and website/design-system/identity-r13/os-stencil-paths.json" --audio
cd "$P" && HYPERFRAMES_SKIP_SKILLS=1 npx hyperframes@0.9.2 check && npx hyperframes@0.9.2 render . -w 2 -o renders/a.mp4 && npx hyperframes@0.9.2 render . -w 2 -o renders/b.mp4
python3 "<repository>/design and website/film/qa_films.py" renders/a.mp4 renders/b.mp4 --size 1080x1350 --duration 42
```
The build script also copies `lockup-os-stacked-inverse.svg` from `assets/public/assets/identity/v13/` into the project (the shared kit copies only the horizontal lockups), writes the three ground bitmaps into the project's `assets` folder, and writes `VOICEOVER.md`, `voiceover.txt` and `captions.srt` into this folder through `filmkit.write_vo`.

## Build notes for the next maintainer
- HyperFrames animates transforms, opacity, colours, clip-path and SVG `d` only; each element has one `fromTo` and then `to` tweens; no `left`, `top`, `width` or `height` tweens.
- GSAP interpolates `clip-path` strings only when every number is written in the browser's shortest form (`640px`, not `640.0px`); otherwise the start value holds until the tween ends. The script formats its clip strings with one helper for that reason, and `path()` strings are avoided (the browser rewrites them).
- The linter warns when a composition carries about 40 elements with clip-path, blur or radial-gradient styling (black frames in the capture layer): this composition stays well under that count.
- **No live CSS gradients.** Chrome dithers a gradient again whenever it re-rasters the tiles next to moving content, and that dither differs by a few levels between runs. Two renders then differed by a few pixels in a handful of frames, x264 took a different path from there, and the difference spread across the rest of its group of pictures (250 frames), which failed the two-render determinism check. The soft grounds are therefore bitmaps (`ground-navy.png`, `ground-navy-b.png`, `ground-pearl.png`) that the script draws with the same stops, radii and positions as the CSS it replaced, dithers once with a fixed ordered pattern and writes with the standard library (no Pillow); they match the CSS gradients to within one level. Keep new grounds and glows flat or baked.
- The renders for this film are deterministic by construction: seeded Python randomness for the layout, no wall clock and no network in the script.

## Measured
See `QA.md` in this folder.

## Not done
- The owner's recorded voice (the master carries music and effects only; the synthetic music and effects are stand-ins).
- Owner acceptance of the 4:5 composition, the wording and the identity (acceptance stays false; nothing is published).
- A human viewing and listening pass in a player; sound is checked by measurement only.
- The generated R15 style frames are not used (rights and visual review pending, see `../../../R15-INTEGRATION.md`).
