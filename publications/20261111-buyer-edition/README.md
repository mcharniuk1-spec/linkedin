# OutSpoken buyer publication edition

11 November2026. Ten rewritten company/founder concepts: five four-page carousels and five single images,25editableSVGs/PNGs and ten captions. Uses the owner-selected current Figma foundation/landing: Young Serif,Mona Sans,porcelain#FCFFFC,navy#162760,one pale-yellow emphasis. The earlier Fraunces/R13 direction is preserved in prior releases, not reused as the current source.

Consumer panels omit founder-note counters, draft/review labels, arrows and generic diagram boxes. Editorial comparison, annotated language, decision prompts, measured numbers and checklists carry the explanation. No scene is inserted merely to fill space. Captions tell the real work of developing/revising Outspoken; product examples remain explicitly illustrative and no customer anecdote is invented.

Open assets/index.html for the PNG/SVG gallery and captions. Five carousel.pdf files contain four pages each. Rendered text is editable in SVG; fonts are bundled with OFL licenses. No social publication occurred.

Rebuild on macOS: python3 build.py --review generated-review; set PUBLICATION_REVIEW to the absolute generated-review directory, run swift render.swift --root=<package>, then swift pdf.swift --root=<package>. Existing renderer reused with variable25-panel/five-document contract. Source context and limits remain in content.json and release-manifest.json, away from consumer artwork.
