# Outspoken OS motion film R15 (proposed)

28.00 s, 4:5 (1080x1350). Rebuilds the R14 OS motion film on the six scenes of Codex `FILM-DIRECTION-R15` (2 November 2026). The OS stencil is the main object: it collects the founder's thinking, opens into an interview frame, its slash cuts the notes into a position, and the story ends on three packages and the lockup.

| Time | Object and transformation | Transition |
|---|---|---|
| 0–4 | A seeded field of thought particles contracts onto the O; the stencil mark resolves in its inverse colours on navy | Pearl opens out of the O's counter as a growing circle; the mark recolours to navy |
| 4–8 | The S and the slash step back; the two halves of the O part into an interview frame; the strand threads through as a speaking waveform | Camera travel |
| 8–12 | Three notes gather in the frame; the strand becomes the cut and a marigold slash crosses them; two notes fly out, one becomes "Position" | A marigold field sweeps across behind the cut |
| 12–17 | The position card folds open into a compact calendar (3D fold); cells fill with themes, proof, formats and posts; one cell lifts into a post | Navy grows out of the post as a circle |
| 17–22 | The post shrinks into a node that spreads into a buyer network; signals return to three separate, unquantified rings (engagement, qualified replies, attributed leads) | The three rings fold into cards |
| 22–28 | Three package cards with the current names and prices from `pricing.json`, then the OS lockup, the protected hero line and "Book an intro call" | Final hold of about 3.5 s |

All type is native and 28 px or more; package names, prices and the protected lines are read from the site's JSON at build time. Status: proposed, owner acceptance false, nothing published. Music and effects are synthetic stand-ins; the narration in `VOICEOVER.md` is Codex's proposed wording for the owner to record. Renders are not committed.

## Build and render
Same steps as `../launch-r15/README.md`, with this folder's `build.py`, a separate scratch folder, and `qa_films.py ... --size 1080x1350 --duration 28`.

## Measured (2 November 2026, two renders on an idle machine)
See `QA.md` in this folder: check passed; 28.000 s, -19.3 LUFS, -7.2 dBTP, 10 of 10 frames identical across two renders: PASS.

## Not done in R15
(Done on 3 November 2026: the independent 16:9 composition of this film is in `16x9/`, with its master in `../../assets/film-r15/`.)
