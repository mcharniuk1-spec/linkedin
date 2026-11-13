# OutSpoken publication brand edition

16 original captions and company introductions,19 graphics and one 4-page PDF. Source snapshot for author review. No social posts were sent by this run.

- [Interactive gallery](index.html)
- [All exact captions and graphics](CAPTIONS.md)
- [Application and reference map](applications.json)
- [Methods, data, client templates and competitors](../../reports/20261112-publication-catalog/README.md)
- [Font/render checks](render-checks.json)
- [Rights and hashes](release-manifest.json)

## Design

Fraunces400 display, Mona Sans400 body/600 emphasis and Geist Mono500 labels. Navy#162760, cobalt#3157D5 and marigold#EAA93C/marker#F6D591 follow the current canonical brand. Licensed font files and OFL notices are included. Use the exported PNGs or PDF for social media. SVGs preserve editable text and embed the font data.

The first carousel contains 4slides. The other 15 posts each contain 1 graphic. Graphic 06 uses an AI-generated scene as selection context. Its text and annotations remain native, editable elements. This scene is illustrative, not customer evidence.

## Rebuild

Use Python 3.12+ to run `python3 build_visuals.py`. On macOS with Swift/AppKit/CoreText, run `swift render.swift . /path/to/a/local/qa-directory` to export 19 PNGs, the PDF and font/bounds checks. The QA directory must exist. No font conversion, dependency installation or global font installation is required. Other platforms can inspect the browser gallery or render the self-contained SVGs with a suitable engine. Matching the native raster output on another engine is not verified.

A font name check alone missed the first SVG renderer's fallback. The final renderer draws each text run through the verified exact CoreText face. The corrected files were visually reviewed after rendering. Owner artistic acceptance remains pending.
