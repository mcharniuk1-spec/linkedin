# Outspoken publication review edition

10 November 2026 · OUTSP-47/48 · draft for founder review.

[Open the gallery](assets/index.html). It contains ten revised captions and two visual directions for each concept: five pairs of five-page carousels and five pairs of single images. The release has **60 PNGs at 1080 × 1350, ten five-page PDFs, 60 editable SVG compositions and ten caption files**. Earlier packages remain unchanged.

## What changed

The existing R13 identity, Fraunces/Mona Sans/Geist Mono typography, navy/paper/marigold palette, graphic objects and fictional people are retained. Reused source pixels are unchanged. New native text/vector compositions increase body type from 31 to 42 px, diagram/context text to 32 px and fictional-scene disclosure to 30 px. These are verified design choices for this package, not an established platform optimum.

All ten concepts now follow the tested writing skills and their reader jobs. The research panels use the exact 22 October metric date and separate denominators. Positioning visibly delivers all four promised checks. The proof carousel uses a clearly hypothetical worked workflow without inventing a benchmark. The visuals and measurement posts show actual question-to-representation/evidence mappings. The offer shows **Book an intro call**. Comparison/checklist boxes have equal weight; arrows show actual relationships.

The [application ledger](skill-applications.json) maps both skills, source claims, openings, payoffs and remaining author inputs to every concept. The [content source](content.json) is canonical for captions and panel copy. Both directions use the same claims; the people-led images retain visible illustrative labels and do not represent customers, employees or founders.

## Rebuild

Use a full repository clone with the preserved shared source-art/font package at `../20261105-evidence-v1/assets/`. Sources are repository-relative and do not depend on the author's machine or an old local run. No dependency is installed by the scripts.

Requirements: Node.js, macOS Swift with AppKit/CoreText/PDFKit, and the existing shared cleared assets. From this folder:

```sh
node build.js
swift render.swift
swift pdf.swift
```

If the compiler cache is restricted, set `CLANG_MODULE_CACHE_PATH` and `SWIFT_MODULECACHE_PATH` to a writable temporary directory. `ASSET_ROOT` can select the same shared asset package in another local location. The SVGs keep native editable text and vector diagrams and use relative shared image/font references; they are not self-contained single-file exports.

Build jobs and arithmetic checks go to `generated-review/` locally. Native export resolves the unchanged shared PNG bytes in memory. The source build is portable across compatible macOS machines; a Linux rendering implementation has not been supplied or tested.

## Verification and limits

All 60 final PNGs have unique hashes and exact dimensions. Full native rendering and all ten PDF exports were executed. All 50 actual PDF pages were rasterized and matched against their expected PNG pages to verify order, with a maximum mean absolute RGB error below 0.47 at the stated QA scale. Layout checks retain at least 92 px before the footer. Separate source review covered all ten captions and all 60 panel-text records.

The [skills/evidence delivery record](../../reports/20261110-skills-publications/README.md) records scanner, behavioral, source, visual and public-boundary checks. Static layout arithmetic is distinct from rendered inspection. Mobile image-scale and browser checks are recorded at their actual scope; physical-device and native LinkedIn preview are not claimed.

This is a review edition, not a social publication or a performance result. Real founder facts, voice, service capability and final author acceptance remain required. The saved reference observations do not establish a viral formula, format advantage, reach or sales lift. No collector, automation, account activity, outreach, Figma mutation or deployment was started.

## Complete text-alternative handoff

[Asset-specific alt text and all ten transcripts](accessibility/README.md) cover every one of the sixty images. The gallery includes each exact description and ten direct transcript links. Fourteen scoped checks and actual desktop/mobile browser link checks pass. This preparation does not assert tagged-PDF, screen-reader or native LinkedIn compliance.
