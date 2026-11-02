# SEO and GEO pass, 2 November 2026 (proposed; owner decisions marked)

## What was done
- **One page.** `/services` and `/contact` no longer exist as pages: they redirect to `/#services` and `/#contact`. The header keeps Approach, Pricing, Services and Contact as buttons that scroll to blocks; the block in view is marked with `aria-current`. Order of blocks: hero, experience story, why Outspoken, opinions, pricing, **detailed service blocks** (eight parts, each with an argument, a check the reader can run, deliverables and scope; then process and FAQ), then the **contact block** (form) as the last block.
- **Answer-first content (GEO).** A visible, standalone definition under the service heading ("What is founder-led LinkedIn marketing?", 43 words) and five new FAQ answers (who it is for, cost, what we need from the founder, how soon, why a founder profile). Every claim keeps the honest limits already in the site; no statistics, clients or guarantees were added.
- **Head markup and structured data.** Title (58 characters, keyword first), meta description (142 characters, with a call to action), Open Graph and Twitter tags, a 1200x630 card, canonical, and four JSON-LD blocks in the static HTML (Organization with the two verified co-founders, WebSite, ProfessionalService with its eight services and three indicative packages, FAQPage with the definition and all answers). FAQ rich results were retired by Google for most sites on 2026-05-07, so FAQPage is kept for answer engines, not for a SERP promise.
- **Crawler and agent files** generated at build time by `website/scripts/seo-static.mjs`: `robots.txt`, `sitemap.xml`, `llms.txt`, and a `<noscript>` copy of the page text (the same words the page shows) for crawlers that do not run JavaScript.
- **Skills used** (installed through the safe installer, listed in `skills/README.md`): `geo-content-optimizer`, `serp-markup-builder` (method applied); `on-page-seo-checker`, `technical-seo-checker`, `content-writer`, `keyword-research`, `site-structure-optimizer`, `seo-geo`, `seo-sxo`, `seo-page` are installed for the next pass. `content-quality-auditor` and `geo-fix-content` failed the installer's gate and are not installed.

## Measured (Lighthouse 13, local build, 2 November 2026)
| Variant | Accessibility | Best practices | SEO | Agentic browsing |
|---|---:|---:|---:|---:|
| Review edition (default, `noindex`), mobile | 97 | 100 | 69 | 75 |
| Launch variant (`OUTSPOKEN_INDEXABLE=1`), desktop | 100 | 100 | 100 | 75 |
The only SEO failure of the review edition is the deliberate `noindex`. The only remaining agentic-browsing failure is a missing `ai-catalog.json` (the predecessor of `/.well-known/ard.json`; see open items). Contrast failures found in the first run were fixed (chips, footer note); icon-only index links now have names.
**Live deployment** (`dpl_8d1uND8HfnhAqYDpA4xDfuieorF4`, mobile, default `noindex` build, measured after the last fixes): accessibility 100, best practices 100, SEO 69 (the `noindex` only), agentic browsing 75 (the missing `ai-catalog.json` only).

## Open items and owner decisions
1. **Indexing.** The site stays `noindex,nofollow` (a review edition with fictional people). Launch needs the owner: choose the production domain, then build with `SITE_URL=https://<domain> OUTSPOKEN_INDEXABLE=1`.
2. **Real domain and Search Console** are not connected; nothing was submitted anywhere.
3. **ARD manifest.** The Agentic Resource Discovery spec (agenticresourcediscovery.org) names `/.well-known/ard.json` with an `entries` array (each entry: identifier, displayName, type and one of url or data). The allowed `type` values were not checked; read the spec before adding the file.
4. **No ranking, traffic or AI-citation result is claimed.** Citability can be probed after launch with an answer engine; surfacing is week-scale.
5. Copy that was not touched: the hero line, the value proposition, the call to action, the prices and the boundary (scope) sentences.
