# Image-generation requests

`R11-visual-library.md` is the request issued to the image generator on 2 November 2026 (about 320 images in three priority tiers: faces, speaking shadows, service illustrations, sparks and ink splashes on black or white, interview scenes, brand-mark renders, then people poses, backgrounds, post covers and more). The generated originals stay with the designer; they are **not** in this repository.

## Ingestion rules
1. The designer places finished packs under `design and website/assets/inbox/r11/<PACK>/` (each with `manifest.json` and `contact-sheet.png`). The folder is excluded from release manifests.
2. A cloud agent or the designer runs the ingestion described in `../prompts/CLOUD-CLAUDE-R11.md` task A: validate against the request's quality gate, convert to WebP (at most 300 KB), keep at most six shortlisted variants per slot under `assets/public/assets/library-r11/`, add a rights-ledger entry per file (owned, fictional, AI-generated), refresh the manifest with `scripts/refresh-manifest.py`.
3. Generated people are fictional and stay labelled "Illustrative". Blend-ready effects: images on pure black are used with `screen`, on pure white with `multiply`.
