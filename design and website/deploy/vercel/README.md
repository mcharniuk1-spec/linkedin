# Deploying the Outspoken review site to Vercel from a repository commit

Status: **rehearsed locally, not yet executed on Vercel** (the Vercel connector had no access to the owner's team on 31 Oct 2026). Treat it as a recipe to verify, not a record of a deployment.

## Why this exists
A Vercel deployment made from uploaded files has to carry every file inline (the main JS bundle is about 1 MB). Building from the public repository commit avoids that: the deployment holds `vercel.json`, `vercel-build.sh` and the media that is not in the public tree, and Vercel builds the rest.

## What the recipe does
1. `vercel.json` skips the install step, runs `bash scripts/vercel-build.sh` as the build command, serves the `site/` folder, and rewrites every path to `/index.html` (the site is a single-page app).
2. `vercel-build.sh` downloads the tarball of one commit (`SHA`) of `mcharniuk1-spec/linkedin`, extracts only `design and website/`, runs `npm ci --ignore-scripts && npm run build` in `website/`, copies the pre-uploaded media from the deployment into `site/`, overlays the build, and fails if the built JS or CSS references a missing `/assets/...` or `/video/...` file.

## Known gap: media that the public repo does not carry
Eleven files that the live site references are rights-excluded from the public tree: `assets/revisions/v5/identity/selected/beauty.webp`, `selected-microphone-transparent.webp`, `assets/revisions/v3/people/01-interview.webp`, and `reference-studies/approved-study-01..08.png`. Deployments made so far carried them as pre-uploaded files referenced by SHA-1. Without them the closing panel shows a broken image. Either supply those files from the owner's local copy in the deployment's `files` list, or change the code to stop referencing them.

## How to run it (needs Vercel access to the target project)
Create a production deployment with `files` = `vercel.json`, `scripts/vercel-build.sh` (inline text), the pre-uploaded media (by SHA-1 and size), and `projectSettings` left unchanged. Set `SHA` in the build environment. Then verify anonymously: every route returns 200, the JS/CSS file names in the HTML exist, fonts and images load, no console errors, and the page contains no `citron`.

## Rollback
Keep the previous deployment ID. A failed build does not move the production alias.
