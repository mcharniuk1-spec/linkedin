# Outspoken design system and website

Current source snapshot: **22 October 2026**, updated on **31 October 2026** (V10: marigold palette, new typography, merged experience block, founders block; see HANDOFF.md). Website V9, cumulative mobile/V7 refinements and the selected V5 brand system are consolidated here. The owner requested publication of the current work to this repository. Artistic acceptance remains pending; this snapshot does not claim a final approved design.

## Folders

- `design-system/`: canonical palette/tokens, typography, material/layout/motion rules, 53-requirement register, component index and protected copy.
- `website/`: editable React/TypeScript website, reusable UI/motion/components, component catalogues and Storybook source. The website imports these same components.
- `assets/public/`: cleared owned/generated assets, authored SVG/GLB models/renders, fictional photography, three silent 18-second brand films and licensed fonts/brain geometry. Every included asset has an exact rights/hash entry.
- `qa/`: checks for this portable projection and dated release evidence, with limitations.
- `source-revision-map.json`, `release-manifest.json`: upstream source identities, documented portability changes, exact file hashes, rights and exclusions.
- `releases/`: the earlier reservation handoff, preserved as history.

## Run and build

Use Node.js 22.12 or newer and the pinned `website/package-lock.json`. From `website/`:

```sh
npm ci
npm run typecheck
npm run build
npm run dev
npm run build:storybook
npm run storybook
```

Installation is a manual setup step; the export does not install packages. The website dev server binds loopback port 6046, and Storybook uses 6006. Production files are written to `website/dist/`; Storybook writes `website/storybook-static/`. Serve production files with an SPA fallback for `/services`, `/contact`, `/confirmation`, `/credits` and `/design-system`.

From this folder run `node scripts/verify-package.mjs` to check every manifest file/hash and asset right. From the repository root run `python3 scripts/verify_release.py` and `python3 scripts/public_safety_scan.py`.

## Public projection

The current website copy, prices, selected uppercase wordmark and V5 microphone model are preserved. The static public form is disabled; no private enquiry server, workbook, submission or secret configuration is distributed. Reference-derived beauty artwork and supplied identity-study crops remain local because redistribution rights are unresolved. The public preview uses the existing authored microphone model render and documented generated fictional photography. These explicit projection changes are recorded in the source map. The canonical local design remains unchanged.

Full native Figma editability lives in the existing [three-page library](https://www.figma.com/design/m7zSeYVpEI88i9qwTrnUQt). A link is not an offline Figma export or proof of acceptance. The current 20 publication drafts and their exact native frame links are in [the separate editorial package](../editorial/README.md).

Historical brand books/PDFs containing uncleared reference pixels, private operational records, copied research media and installed third-party skill directories remain local. Component source, current owned design assets and portable build inputs are provided here. Earlier research releases remain in Git history. The prior repository commit is `77776a0e7f1d17d909ed23845908f8a5f7725d4a`.

Current website build,155 research tests,20 export/boundary tests and128 rendered website/editorial checks pass. Strict TypeScript checked101 targets/1021 inputs with zero diagnostics, but complete type verification and the current Storybook rebuild are blocked by unreadable dataless files in the installed Storybook dependency. The exact pinned archive was not available in the existing cache; no substitute or dependency installation was used. Read qa/current-checks.json and qa/typecheck.json for the precise limits.

Owner artistic approval, physical iOS/Safari and assistive-technology checks remain separate. No website deployment, Figma mutation, social publication or recurring collection follows from this Git synchronization.
