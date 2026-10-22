# Outspoken V3 editable catalog

88 native SVG surfaces: 11 in each of banner, poster, editorial block, heading, video frame, caption/emphasis, schema and publication. The first seven categories contain 77 new layouts. Publications reuse ten current masters and add one new review checklist. `manifest.json` is the canonical inventory; `index.html` is the native preview atlas.

Use `CatalogSurface` with a manifest ID. Editable props are native `data-slot` values. `slots` accepts an exact slot map; `titleLines`, `bodyLines`, `eyebrow` and `caption` are convenience props. `mediaSrc` changes the marked original-photo image. Keep the listed line count and font sizes. If new copy does not fit, create a reviewed variant rather than shrinking or hiding meaning. SVG text remains text for Figma editing.

`Catalog.stories.tsx` reads the same manifest and source. It provides eight category galleries plus one editable story. Storybook discovery/build must be verified by the integrating root; file presence alone is not an executed Storybook proof. Existing Archivo/Inter font loading is required in the host. The component escapes replacement text and accepts no arbitrary HTML input.

Metadata records use context, dimensions, editable props, spacing, angle, type and colours. Native frames rest flat. Perspective is a reversible website presentation layer with a front-facing focus state; it does not become a native LinkedIn interaction. Video frames are editable poster/frame art, not playable media by themselves.

Every surface is an illustrative design specimen. No customer outcome, implemented architecture or published client work is claimed. M2Lab informed practical catalog breadth and signs, not copied composition or lime styling. Sources use original generated nature imagery and existing licensed project fonts.
