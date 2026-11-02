# Prompts for the next Claude (two variations)

The prompts assume the agent starts in a clean checkout of `https://github.com/mcharniuk1-spec/linkedin` and nothing else. Paste one as the first message. Variation A needs no connectors. Variation B adds Figma and Vercel. Variation C continues the website design and code-generated motion work and needs no connector (add Vercel only if you want it deployed).

> **Newest prompt (2 November 2026):** use `../prompts/CLOUD-CLAUDE-R11.md`; it replaces Variations A to C for the remaining tasks (image ingestion, site design pass, the 30-second film in 16:9 and 4:5, SEO and GEO, deployment, Figma) and holds the Git rules. The variations below remain valid for the 80-second Remotion film.

## Current state (31 October 2026, after commit `acf8655`)
- **Identity:** the client chose **B01** (matte capsule microphone mark) and **D05** (monoline icons with a marigold marker). Vectors and generator: `design and website/design-system/identity-v10/`. They are live in the header, footer, hero mark, closing panel, experience chips and services.
- **First screens:** hero photographs are **graded in code** (`design-system/identity-v10/grade-heroes.py`), not generated. Codex is no longer used for images; do not write Codex requests for heroes. The first screens use a dotted ground, a kicker pill, one selected accent word (`Sel`), an illustrative people strip (`HeroPeople`) and a statement beat before the proof beat (`website/website-v3/HeroPeople.tsx`, `hero-v10.css`, `hero-phases.ts`).
- **Live review site:** https://outspoken-voice-7c4e2.vercel.app/ (production `dpl_Hx1irxvPivqP2n9hqMRZb2meRiCo`, previous `dpl_HVZUSzP32nqQaBgj3XnogHAqvJPo`). Anonymous hash readback matched; checked in a browser pane at 375 px and desktop width with no console errors. No physical device was used. Nothing is owner-accepted.
- **Still open:** Brand Studio documents V5; Figma not updated (no edit access); recorded voiceover; 4:5 film; desktop hero is not centred; later site blocks are not yet restyled to the first-screen style; HyperFrames is not installed (reading-only).

## How to start the cloud session (branch instructions)
1. Open Claude Code on the web (claude.ai/code), choose the repository `mcharniuk1-spec/linkedin` and the base branch **`main`**: it holds the film, the plan, the owned skills in `.claude/skills/` and this file.
2. The agent must **not commit to `main`**. Its first action is to create a working branch from `main`, one per task: `claude/film-4x5`, `claude/film-retime`, `claude/logo-vectors`, `claude/site-update`. It pushes only to that branch, without force.
3. You review the branch (diff or pull request) and merge it yourself. Before merging, the agent rebases on `main` if `main` moved (the repository's collection workflow may add commits).
4. Variation A needs no connector. Variation B needs the Figma connector signed in to the design account and the Vercel connector; for Vercel, tell the agent not to pass `teamId` (see `.claude/skills/outspoken-site-deploy/SKILL.md`).
   Variation C needs no connector; its branch names are `claude/site-style-pass` and `claude/motion-clips`.
5. Paste the prompt as the first message; the agent reads the skills automatically from `.claude/skills/`.

---

## Variation A: repository only (film, retime, 4:5 cut, teaser)

You are the production engineer for the Outspoken launch film, working only inside the repository `mcharniuk1-spec/linkedin`. Outspoken is a founder-led LinkedIn services studio for Europe-based B2B AI SaaS founders. You have no Figma, Vercel, social-media or other accounts, and you must not ask for credentials.

Read first, in this order: `AGENTS.md` (repository root), `design and website/HANDOFF.md`, `design and website/film/README.md`, `film/SPEC.md`, `film/DESIGN-FIT.md`, `film/PLAN-NEXT.md`, `film/voiceover/VOICEOVER.md`, `film/RESEARCH.md`. The film is a Remotion + React + FFmpeg project in `design and website/film/`. All creative elements are proposals; owner acceptance is false and you must keep it false.

Do, in order, and verify each with commands you actually ran:
1. Rebuild the current film from a clean install (`npm ci --ignore-scripts`, `npm run sync`, `npm run typecheck`, `npm run vo`, `npm run audio`, render `Master` and `Teaser` with `render.mjs`, mux sound, run `scripts/qa/qa.py`). Report each check's PASS or FAIL with the numbers. If a browser is missing, use the one the Remotion renderer downloads in this cloud environment and say so.
2. Fix everything the QA reports and everything in `PLAN-NEXT.md` task 3. Do not change the script wording, the protected hero line "Make the right buyers care about you and what you're building." or the call to action "Book an intro call".
3. Build the 4:5 variation (1080x1350, 30-35 s) as a re-composition, not a reframe, from the same kit: new layouts for scenes S1, S4, S5, S7, S9, type at 96 px or more, bottom 20 % reserved, fictional labels present. Render it, run `qa.py --size 1080x1350`, and add the contact sheet.
4. If the owner has added a recorded voiceover (`film/voiceover/takes/`), write `scripts/retime-from-vo.mjs` as described in `PLAN-NEXT.md` task 2 and retime. If there is no recording, say so and stop at task 3.

Rules: no social publication; no force-push; no invented statistics, clients, quotes or real people; every fictional element stays labelled; spend stays 0 and you install nothing beyond the pinned lockfile; the audio is code-synthesised and is a stand-in for a recorded orchestra (say so in every report, and never call the film fully complete on that score unless the owner has chosen it); run `scripts/public_safety_scan.py` and the release verifiers, regenerate `release-manifest.json` for changed files, commit to a branch, and push without force. Finish with: what you changed, the commit hash, commands and results, remaining gaps. Do not report anything as done that you did not run.

---

## Variation B: with Figma and Vercel connectors

Same role and rules as Variation A, plus these connectors, used only when each is actually reachable. At the start, call the Figma `whoami` and the Vercel project listing and state exactly which account and scope each returns. If the Figma account is not the owner's design account with edit access to file `m7zSeYVpEI88i9qwTrnUQt`, or if Vercel returns 403 for the Outspoken project's team, stop that part, report the exact message, and continue with the rest.

Additional tasks, after Variation A's task 1:
- **Figma:** apply the V10 design values from `design and website/design-system` (variables from `tokens.json`, text styles from `type-roles.json`, button and media-frame components, home frames at 1440 and 390 wide) and add the film's nine storyboard frames. Keep exactly three pages, create no new file, record every node ID in `design and website/FIGMA-FRAME-MAP.md`, and read back a screenshot of each frame. Variables must not contain the old `#D4DD67`.
- **Vercel:** follow `design and website/deploy/vercel/README.md`: build from a commit of this repository, supply the eleven media files only if the owner has provided them, create a production deployment in the existing Outspoken project, and verify anonymously (all routes 200, asset file names match the HTML, fonts and founder photos load, no console errors, no `citron` in the DOM). Record the deployment ID, the previous deployment ID and the rollback path.
- Report all deployments and pushes in one table: target, identifier, readback evidence, and gaps.

---

## Variation C: website design pass and code-generated motion (repository only)

You are the designer-developer for the Outspoken website, working only inside the repository `mcharniuk1-spec/linkedin`. You have no Figma, Vercel or social accounts and must not ask for credentials. Outspoken is a founder-led LinkedIn services studio for Europe-based B2B AI SaaS founders.

Read first: `AGENTS.md` (root), `design and website/HANDOFF.md`, `design and website/design-system/DESIGN.md`, `design-system/identity-v10/README.md`, `film/DESIGN-FIT.md`, and the skills in `.claude/skills/` (`outspoken-design-rules`, `outspoken-logo-icon-direction`, `outspoken-film-build`, `outspoken-site-deploy`). The current state is in the section "Current state" at the top of this file. Everything is proposed; owner acceptance is false and stays false.

Goal: make the rest of the site match the first screens, and add looping motion clips generated by code.
1. **Style pass.** Carry the first-screen language (dotted ground, kicker pill, one selected accent word with marker, dashed outline and four handles, people strip, soft rounded cards, chapter counters such as "01 / 05") into the experience story, Why Outspoken, services, FAQ/prices and the closing panel. Principles only: the light founder-marketing reference pages the owner pointed to (an AI-marketing founder site, a Windmill-style growth site, Behance case studies) are inspiration, never copy layout, text, artwork or logos. Use only navy `#162760`, nickel `#A9AFBA`, marigold, pearl `#F1F3F6`, Fraunces / Mona Sans / Geist Mono, and the brand ease.
2. **Mobile first.** Review the first three screens and every block at 375 and 390 px: no horizontal overflow, headline centred and narrow, tap targets at least 44 px, no empty full-screen navy beats. Keep the hero phase story (intro, shadow flood, statement, proof) and the protected copy ("Make the right buyers care about you and what you're building.", "Book an intro call", prices).
3. **Brand Studio.** Update the `/design-system` page from the V5 capsule to the V10 identity (B01 mark, D05 icons, heroes grade, rules). Keep V5 files as history.
4. **Motion clips by code.** Build 3-5 looped clips (6-10 s, 16:9 and 4:5) with the existing Remotion kit in `film/`: selection-accent reveal, chapter counter, post-card stack, people-strip entrance. They must read on a muted phone, respect the film QA thresholds, and carry the "illustrative" labels. Do **not** install HyperFrames or any new tool: it is reading-only until the owner approves and the safe installer plus static scan pass. If you think HyperFrames would help, write the reason and stop.
5. **Verify and record.** `npm ci --ignore-scripts && npm run typecheck && npm run build` in `design and website/website/`; `python3 scripts/verify_release.py`, `node "design and website/scripts/verify-package.mjs"`, `python3 scripts/public_safety_scan.py`; screenshots at 375, 768 and 1440 px plus reduced motion (emulate `prefers-reduced-motion`; say if you could not); regenerate `release-manifest.json`; commit to your branch; push without force.

Rules: no social publication; no force-push; no invented statistics, clients, quotes or real people; every fictional element stays labelled; spend stays 0; do not edit protected copy; do not claim a deployment unless you ran it and read it back. Finish with what changed, the commit hash, commands and results, and remaining gaps.
