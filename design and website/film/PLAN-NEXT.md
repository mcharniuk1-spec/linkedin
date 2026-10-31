# Next-step plan: continuing from the repository alone (cloud Claude, optionally with Figma and Vercel)

Written 31 October 2026. Audience: a Claude agent working in the cloud that is connected **only to `github.com/mcharniuk1-spec/linkedin`**, and, where stated, to Figma and Vercel connectors the owner has authorised. Nothing here is owner-accepted; all creative work is proposed.

## 1. What the repository already contains (verified by building from it)
- `design and website/website/`: React 19 + Vite site, Storybook sources, tokens, components. `npm ci && npm run typecheck && npm run build` work without private files.
- `design and website/film/`: the launch film (Remotion 4.0.520 + React + FFmpeg): kit, nine scenes, voiceover sheet, procedural audio, QA script, README, SPEC, DESIGN-FIT, RESEARCH, teaser re-cut. Rebuilding needs only Node 22, Chrome or Chrome headless shell, FFmpeg and Python 3 with numpy and scipy.
- `design and website/deploy/vercel/`: a rehearsed (not yet executed on Vercel) recipe to deploy the site from a commit.
- `design and website/design-system/`: tokens, type roles, DESIGN.md, `film-tokens.json` (proposed).

## 2. What is not in the repository (and what that blocks)
| Missing | Consequence | How to close it |
|---|---|---|
| Eleven rights-excluded media files the live site still references (`selected/beauty.webp`, `selected-microphone-transparent.webp`, `v3/people/01-interview.webp`, `reference-studies/approved-study-01..08.png`) | A repo-only site build shows a broken image in the closing panel | Owner supplies the files, or the code stops referencing them |
| Figma file `m7zSeYVpEI88i9qwTrnUQt` access | The Figma update (variables, text styles, button and frame components, home frames 1440/390, film storyboard frames) cannot be done | The Figma connector must be signed in as the owner's design account with edit access (the connected account had view-only access on 31 Oct) |
| Vercel | Done once for commit d5f5880 (anonymous readback matched all 181 files) | Re-run `deploy/vercel/README.md` after each site change; never pass `teamId` for this personal scope |
| Recorded voiceover | The film cannot be retimed to the real read | Owner records per `film/voiceover/VOICEOVER.md`; word timestamps from the Whisper model on the owner's machine, or any aligner |
| A composed or licensed score | The music is code-synthesised | Owner decision; the stems interface is `film/audio-out/*.wav` plus `src/timeline.json` |
| Microphone series (20 concepts) | The film's end card keeps the V5 capsule | Image-generation agent, separate request files; owner chooses |
| The example film the owner mentioned | It was not attached to the request that created this plan | Owner supplies a link or file; add to `film/reference/` (no copying; principles only) |

## 3. Task queue, in order (each item: acceptance checks)
1. **Human review of the film.** Watch `out/film.mp4` (rebuild per `film/README.md`) on a phone and a laptop, with and without sound. Collect a numbered fix list. Acceptance: owner sign-off recorded; until then `owner_accepted` stays false.
2. **Retime to the real voiceover.** Add `scripts/retime-from-vo.mjs`: read word timestamps, rewrite `src/script.json` (scene frames, VO windows) and every `src/scenes/S*.events.json` time that is tied to a spoken word, rebuild `timeline.json`, re-synthesise, re-render. Acceptance: `qa.py` passes; each text beat lands on or before its word (spot-check 10 words by stills); picture-to-word offset <= 0.3 s.
3. **Fix list from the build notes** (all in `SPEC.md` and the scene files): promote `InkMarker` and a corrected `Flash` default into the kit; give the camera rig per-key easing; document `Particles.speed` as px per frame at birth; scenes S5/S6/S8 are the busiest, so check them first on a phone; confirm there are no garbled frames (render at concurrency 2-3 on an otherwise idle machine and run a frame-difference outlier check).
4. **Four-by-five variation (1080x1350).** Re-compose, do not reframe: a vertical layout needs its own safe areas (action 5 %, bottom 20 % reserved), type at 96 px or more, fewer simultaneous elements. Build `Cut4x5` from the same kit with its own scene layouts for S1, S4, S5, S7 and S9 (about 30-35 s). Acceptance: `qa.py --size 1080x1350`, text readable at 360 px width, all fictional labels present.
5. **Teaser polish (16:9, about 30 s).** `Teaser` exists as a re-cut with the master's transitions; mux its audio from the master mix with equal-length crossfades (see `scripts/make-teaser.sh` in the next step) and review. LinkedIn's ad guidance recommends 15-30 s for paid placements.
6. **Score upgrade (owner decision).** Option A: keep the synthesised score and finish it. Option B: replace the stems with a licensed or composed score (keep stem names, keep the loudness target about -16 LUFS integrated, true peak <= -1.5 dBTP). Option C: sampled strings via FluidSynth with a freely licensed soundfont, after a provenance review. Do not call the film complete with the stand-in score if the owner expects a real orchestra.
7. **Figma sync (needs the Figma connector with edit access).** Apply `design and website/design-system` values per the V10 Figma update spec (variables, text styles, button and media-frame components, home frames), add film storyboard frames, keep exactly the three existing pages, and record node IDs in a new `FIGMA-FRAME-MAP.md`. Acceptance: screenshot readback of every frame; variable bindings contain no `#D4DD67`.
8. **Vercel deployment (done once on 31 Oct 2026; repeat after each site change).** Follow `deploy/vercel/README.md`; verify anonymously (all routes 200, asset names match, fonts and founder photos load, no console errors, no `citron` in the DOM); record the deployment ID, previous deployment ID and rollback path.
9. **Design-system follow-ups** from `film/DESIGN-FIT.md` section 6, including sign-off on `film-tokens.json`.
10. **Storybook rebuild** and a render check of the Buttons, Media frame, Experience and Why Outspoken stories.
11. **Cleanup** of legacy local design material only after tasks 7 and 8 are read back, listing what is deleted and proving a copy exists. Never delete research data, private workbooks or other projects.

## 4. Guardrails for every task
No social publication. No force-push. No invented statistics, clients, quotes or real people; fictional elements stay labelled. Spend stays 0 unless the owner approves a provider. Keep secrets, private enquiry data and absolute local paths out of the public tree; run `scripts/public_safety_scan.py` and the release verifiers before any push, and regenerate `release-manifest.json` when files change. Claim only what was executed: a rendered file is not an accepted design, a pushed commit is not a deployment, and a connector listed in a document is not a working connection.

## 5. Records to write after each task
A dated note in the repository handoff (`design and website/HANDOFF.md`), the commit hash, the commands run with their pass/fail result, and the open gaps. If a task cannot be finished, write the exact blocker.
