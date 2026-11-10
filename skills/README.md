# Owned LinkedIn writing skills — 10 November 2026

- [linkedin-publication-architecture](linkedin-publication-architecture/SKILL.md): reader job, truthful story/argument, proof, hook payoff, voice and caption/panel handoff.
- [linkedin-reference-pattern-review](linkedin-reference-pattern-review/SKILL.md): bounded source evidence, actual review modality, construction analysis and qualified pattern transfer.

These original script-free bundles include their own references and require no provider or account. [Executed tests and limits](../reports/20261110-skills-publications/README.md) record static scanning, installed-copy readback, explicit use and behavioral cases. Availability in a fresh turn and actual publishing/account authority are separate.

# Skills for agents working in this repository

Owned skills (plain Markdown, no scripts, written for this repository; Claude Code reads them from `.claude/skills/`):

| Skill | Use |
|---|---|
| `update-run-linkedin` | manual LinkedIn research run update and bounded analysis packet (also kept here as `skills/update-run-linkedin`) |
| `outspoken-film-build` | build, render, mux, QA and retime the launch film |
| `outspoken-design-rules` | colours, type, shape, wordmark and honesty rules, with measured contrast |
| `outspoken-site-deploy` | build, deploy and verify the review website (Vercel connector, anonymous readback) |
| `outspoken-logo-icon-direction` | review logo/icon boards and microphone candidates, present directions, rebuild the chosen one as vectors |

## Third-party skills installed on the owner's machine (2 November 2026)
Installed with the owner's safe installer after a SkillSpector 2.9.6 static scan (`--no-llm`, LOW and SAFE only) and a read of every file (all are text-only, no code). They live in the owner's `~/.claude/skills`, **not in this repository**: a cloud agent cannot use them and should read the pinned sources instead (raw files at the commit below). Third-party code is never copied into this repository.

| Skill | Source and commit | Licence | Use |
|---|---|---|---|
| `geo-content-optimizer`, `serp-markup-builder`, `content-writer`, `page-play-builder`, `on-page-seo-checker`, `technical-seo-checker`, `site-structure-optimizer`, `keyword-research` | `aaron-he-zhu/aaron-marketing-skills`, path `seo-geo/<implement|tune|survey>/<name>`, commit bf5c11edb7b195fef8b334b220ecd4232fe9dcb0 | Apache-2.0 | GEO citability, head markup and JSON-LD, SEO copy, programmatic pages, on-page and technical audits, site structure, keyword research |
| `seo-geo`, `seo-sxo`, `seo-page` | `AgriciDaniel/claude-seo`, path `skills/<name>`, commit 6be93f45064ffbadced572b5d5c95f55fd263af0 | MIT | AI-search audit, search-experience diagnosis, single-page review |
| `hyperframes-registry`, `seam-craft`, `cut-the-curve`, `captions-overlay` | `heygen-com/hyperframes`, paths `skills/hyperframes-registry` and `.agents/skills/<name>`, commit 5e50ac1c475f9446cd17a04f218194b555fa311f | Apache-2.0 | HyperFrames block registry, seam and transition doctrine, captions overlay doctrine |

Rejected by the gate (not installed): `hyperframes` (core, HIGH), `media-use` (CRITICAL), `motion-doctrine` (HIGH), `hyperframes-cli`, `remotion-to-hyperframes` (MEDIUM), `geo-audit`, `geo-fix-schema` (HIGH), `geo-compare`, `geo-fix-llmstxt` (MEDIUM), `motion-designer` (CRITICAL), `product-film` (MEDIUM); `content-quality-auditor` and `geo-fix-content` were scanned LOW/SAFE but the installer failed closed ("high or critical issue despite SAFE"). Most findings of the HyperFrames skills are unpinned `npx` mentions, a credential-path word and whitespace padding; they were read as reading material only. The older `seo-geo-claude-skills` repository is now a signpost with stub files: do not use it.

**HyperFrames runtime.** The film uses the CLI `hyperframes@0.9.2` (Apache-2.0) as a pinned npm dependency installed with `--ignore-scripts`, telemetry disabled (`npx hyperframes telemetry disable`) and skill installer skipped (`HYPERFRAMES_SKIP_SKILLS=1`). Feasibility on the build machine (Node 22, FFmpeg 8.1, Chrome headless shell): a 30 s 1080x1920 film renders in about 16 s.

## Earlier reading-only sources (31 October 2026)
Remotion agent skills `remotion-dev/skills` (commit 30d4553ecd46fbc5212fd0ff006ae43af522158b), `iart-ai/motion-design-skills` (MIT, 3c129f769d90a1328c209c386492333c9ac62312), `dev-isaacmello/extreme-motion-design` (MIT, 5ae58839564de9df71b116026f5631b2c0b364e5; its scripts download dependencies and music: do not run them), `emilkowalski/skills` (MIT). Never install cloud music or video generators for the films (spend stays 0). The Remotion licence is free for individuals and for-profit organisations of up to 3 people.

## Not available to a cloud agent
Skills installed on the owner's own machine (personal or global) are not in this repository and cannot be assumed. If a task needs one, say so; the owned skills above are written to cover the film, design, deployment and logo work without them.

