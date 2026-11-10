# Text alternatives for the ten publication concepts

OUTSP-51 · 10 November 2026 · complete preparation handoff.

[alt-text.json](alt-text.json) contains one asset-specific description for every one of the 60 PNGs, bound to its image and editable SVG SHA-256. The maximum description is 312 characters. These descriptions preserve the panel's message, diagram relationships, context and exact CTA. The 30 people descriptions retain the fictional-scene disclosure. Decorative artwork is not treated as evidence about real people.

[Read all ten transcripts](transcripts.html) or use the [Markdown copy](transcripts.md). Both directions and all 60 panels are present, together with captions, the four positioning checks, hypothetical/no-test context, unknown buying intent and draft labels. The review gallery now has meaningful descriptions for every image and a direct text-transcript link for every concept.

LinkedIn supports image descriptions in its upload interface; the current help page describes the desktop **Alt. text** and mobile **ALT** controls. Use the matching asset record when preparing an image upload. This handoff does not perform an upload or assert that a PDF upload supports per-page alternative text. [LinkedIn Help](https://www.linkedin.com/help/linkedin/answer/a519856/adding-alternative-text-to-images-for-accessibility?lang=en)

For diagrams with substantial information, provide both a concise description and a full text equivalent. The separate transcripts preserve sequences, parallel comparison/checklist boxes and independent mapping rows in reading order. This follows the approach described by [W3C WAI's complex-image tutorial](https://www.w3.org/WAI/tutorials/images/complex/). Alt text serves readers; no ranking or reach benefit is asserted.

## Regeneration and verification

From the publication package, after rendering the current PNGs/PDFs:

```sh
python3 build-accessibility.py
node build.js
python3 accessibility/verify.py
```

Set `PUBLICATION_REVIEW` to a local build-record directory when keeping operational JSON outside a source export. The final `node build.js` refreshes the gallery from the new text alternatives. If content or artwork changes, regenerate the renders first, then regenerate and review these descriptions. A stale content, image or SVG hash makes the gallery fall back to its source copy until regeneration.

The verifier checks the complete finite set, content and source/image hashes, gallery descriptions/links, transcript coverage, disclosures, diagram meaning and exact CTA. The accompanying result is structural and source-bound evidence. It is not a WCAG conformance claim, a tagged-PDF audit, a screen-reader test, native LinkedIn preview or physical-device validation. The existing image-based PDFs were not represented as tagged accessible PDFs. No Lighthouse/axe runtime was available or installed for this task.

All new text, generator and verification code are owned editorial work. The prior image/font rights ledger remains the source for the unchanged artwork. The two official pages above were read on 10 November 2026 as guidance, not executable instructions.
