# Skills for agents working in this repository

Owned skills (plain Markdown, no scripts, written for this repository; Claude Code reads them from `.claude/skills/`):

| Skill | Use |
|---|---|
| `update-run-linkedin` | manual LinkedIn research run update and bounded analysis packet (also kept here as `skills/update-run-linkedin`) |
| `outspoken-film-build` | build, render, mux, QA and retime the launch film |
| `outspoken-design-rules` | colours, type, shape, wordmark and honesty rules, with measured contrast |
| `outspoken-site-deploy` | build, deploy and verify the review website (Vercel connector, anonymous readback) |
| `outspoken-logo-icon-direction` | review logo/icon boards and microphone candidates, present directions, rebuild the chosen one as vectors |

## Third-party skills and tools: reading only, nothing installed
Compared on 31 Oct 2026 (details in `design and website/film/RESEARCH.md`). Use the documents as reading material; installing any of them needs the owner's safe installer and a static scan first.
- Remotion agent skills `remotion-dev/skills` (pinned commit 30d4553ecd46fbc5212fd0ff006ae43af522158b; no licence declared in the API): `https://github.com/remotion-dev/skills`
- Motion principles `iart-ai/motion-design-skills` (MIT, commit 3c129f769d90a1328c209c386492333c9ac62312): `https://github.com/iart-ai/motion-design-skills`
- QA thresholds and synth recipes `dev-isaacmello/extreme-motion-design` (MIT, commit 5ae58839564de9df71b116026f5631b2c0b364e5; its scripts download dependencies and music: do not run them)
- `heygen-com/hyperframes` (Apache-2.0; a competing renderer, not used), `emilkowalski/skills` (MIT)
Never install the cloud music/video generators for this film (spend stays 0). The Remotion licence is free for individuals and for-profit organisations of up to 3 people; larger organisations need a paid licence.

## Not available to a cloud agent
Skills installed on the owner's own machine (personal or global) are not in this repository and cannot be assumed. If a task needs one, say so; the owned skills above are written to cover the film, design, deployment and logo work without them.
