# Claude cloud prompt R15: the remaining films (paste as one message)

You are the motion designer and release engineer for Outspoken, a founder-led LinkedIn studio for Europe-based B2B AI SaaS founders (seed to Series B). Work only in the public repository `mcharniuk1-spec/linkedin`. Read `AGENTS.md`, `design and website/HANDOFF.md` (sections R13 to R15), `design and website/R15-INTEGRATION.md`, `design and website/design-system/DESIGN.md`, `design and website/design-system/motion-tokens.json` and `design and website/film/launch-r15/README.md` and `build.py` before you start.

## Goal
Build the two remaining films on the model of `film/launch-r15/build.py` and `film/motion-os-r15/build.py` (shared kit `film/filmkit.py`): objects keep their identity across each seam and turn into the next stage; colour moves as clipped fields; no repeated diagonal wipe; no fade-only cuts; at least five transition mechanisms across a film (path morph, mask or clip reveal, camera travel with parallax, 3D fold, clipped colour field).

1. **Launch film, 4:5 (1080x1350), 42 s**, in `film/launch-r15/build_4x5.py`. An independent recomposition of the same eight stages and timings, not a crop: stack the clusters, cards, calendar (4 columns x 6 rows), package cards (one column, or one card at a time) and the final lockup vertically; keep every type element at 28 px or more and inside a 64 px safe margin.
2. **OS motion film R15, 16:9 (1920x1080), 28 s**, `film/motion-os-r15/build_16x9.py`: an independent composition of the six scenes already built in `film/motion-os-r15/build.py` (4:5, QA PASS); read its README for the scene table.

## Fixed inputs and rules
- Identity: the OS stencil from `design-system/identity-r13/os-stencil-paths.json` through `filmkit.mark_parts` and `mark_svg` (never re-typeset), the lockups in `assets/public/assets/identity/v13/`. Palette: navy #162760, deep navy #0D1A3B, pearl #F1F3F6, marigold #EAA93C / #F6D591, Nickel 600 #666F7F, inverse #F2F5FA / #B9C7DA. Fonts: Fraunces (display), Mona Sans (body), Geist Mono (labels).
- Read package names and prices from `website/website-v3/pricing.json` and the hero line and call to action from `content.json#protected` at build time; keep them byte for byte (curly apostrophe). Prices are indicative; say so on screen as the launch film does.
- No client names, results, numbers of outcomes, testimonials, faces or invented founder quotes. Measures (engagement, qualified replies, attributed leads) appear as separate, unquantified instruments.
- HyperFrames rules learned in R15: animate only transforms, opacity, colours, clip-path and SVG `d`; never tween `left`, `top`, `width` or `height` (the check fails); give each element one `fromTo` and then `to` tweens; keep `#strand`-type shared paths at a fixed point count so `attr: {d}` morphs work in GSAP core.
- Audio: `filmkit.make_audio` with cuts at the scene seams and event-synced sounds for each visual beat; the master carries music and effects only (the owner records the voice from `VOICEOVER.md`; never synthesize or imitate a real voice for the master).
- The generated R15 images are not in the repository and must not be used.

## Gates (all must pass before you commit a film)
`npx hyperframes@0.9.2 check` with 0 errors (fix every warning about type below 28 px or text held too briefly); two renders with `-w 2` on an idle machine; `python3 "design and website/film/qa_films.py" a.mp4 b.mp4 --size <WxH> --duration <s>` OVERALL PASS (exact duration, -19 LUFS ±1, true peak at or below -1.5 dBTP, no spikes or flashes, 10 of 10 frames identical). Inspect a 1-second contact sheet and a 0.25-second strip across every seam, and fix any overlap or empty frame. Write a README per film with the scene table, build commands and measured results, plus `VOICEOVER.md`, `voiceover.txt` and `captions.srt` (via `filmkit.write_vo`). Do not commit renders.

## Release
Run `python3 "design and website/scripts/refresh-manifest.py"` until it reports no change (two or three runs), `node "design and website/scripts/verify-package.mjs"`, `python3 scripts/public_safety_scan.py` and `python3 scripts/verify_release.py`. Inspect the exact diff (only `design and website/film/`, the manifest and the R15 sections of `HANDOFF.md`). Commit on a new branch `r15-films`, push it without force, and open a pull request to `main` that lists what passed and what remains. Do not deploy, publish to LinkedIn, change the website, change Figma or touch the LinkedIn collection pipeline. If a gate fails and you cannot fix it, commit nothing for that film and say so in the pull request.

## Report back
End with: the branch, the commit, the pull request link, a table of the two films with check, QA and determinism results, what you inspected, and anything left open.
