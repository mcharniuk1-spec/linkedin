# SEO, GEO and AEO pass (R14, proposed), 2 November 2026

Scope: the one-page review site (https://outspoken-voice-7c4e2.vercel.app/), its static SEO output (`website/scripts/seo-static.mjs`) and its content (`website/website-v3/content.json`). Earlier pass: `SEO-GEO-R11.md`. The review edition stays `noindex` until the owner launches; indexing is the owner's decision.

## 1. What was already in place (verified in the built HTML)
- Titles and descriptions per route: `/` (`Founder-led LinkedIn marketing for B2B AI SaaS | Outspoken`), `/privacy`, `/design-system`, `/credits`.
- JSON-LD, four blocks that parse without errors: `Organization` (logo `/assets/identity/v13/avatar-os-800.png`, founders as `Person` with role and profile link), `WebSite`, `ProfessionalService` (audience, area served, an offer catalogue built from the eight service modules and the three packages with their EUR prices), `FAQPage` (built from the visible FAQ).
- A full no-JavaScript copy of the page (`<noscript>`), `robots.txt`, `sitemap.xml` and `llms.txt` in the llmstxt.org shape (H1, summary quote, H2 sections with links).

## 2. Buyer questions (intent map, from the site's own content; no search-volume data was used, so every volume is unknown)
| Buyer question | Where the site answers it |
|---|---|
| Who is this for? | FAQ "Who is OUTSPOKEN for?", hero line, audience in JSON-LD |
| What exactly do you do? | Eight service modules, the definition answer in the service block |
| How does the work start? | **New FAQ item** (from the four process steps) |
| How much does it cost? | FAQ "How much does it cost?", three priced packages |
| What do you need from me? | FAQ "What do you need from the founder?" |
| Will it sound like me? | FAQ "Will the writing still sound like me?" |
| How soon will we see results? Can you guarantee leads? | Two FAQ items; no guarantee is made |
| Is the media budget included? | FAQ on advertising |
| Why the founder's profile and not only the company page? | FAQ item |
| What happens to my details if I use the form? | **New FAQ item** (from the lead function and the privacy draft) |

## 3. Changes in this pass
- **AEO:** two answer-first FAQ items (42 and 51 words; the first sentence answers the question), using only facts already on the site: "How does the work start?" and "What happens to the details I send through the form?". The FAQ and the `FAQPage` schema now carry 13 items plus the definition answer (14 questions in the schema).
- **GEO:** `llms-full.txt`, the complete page text as plain Markdown (14.9 KB), generated from the same source as the no-JavaScript copy, linked from `llms.txt` under "Optional", and copied by `deploy/vercel/vercel-build.sh`.
- **Agentic discovery:** the ARD specification (v0.91, proposal) was read. Its manifest is `/.well-known/ard.json` (`ai-catalog.json` is the predecessor path) and its entries describe agentic resources, not pages. The honest fit is the repository's five agent skills (`application/agent-skills+md`, linking the public `SKILL.md` files, all five URLs answered 200). Because ARD identifiers are bound to the publisher's domain and the review domain is temporary, the manifest is generated **only for the launch build** (`OUTSPOKEN_INDEXABLE=1`). The build script copies `.well-known/` when it exists.
- **Copy:** no approved body copy was rewritten. The protected hero line and call to action are unchanged.

## 4. Checks (2 November 2026)
- Type-check passed. Review build: robots `noindex,nofollow`, four JSON-LD blocks parse, 14 FAQ questions, `llms-full.txt` written. Launch build (`OUTSPOKEN_INDEXABLE=1 SITE_URL=https://launch-domain.example`): robots `index,follow,max-image-preview:large,max-snippet:-1`, `ard.json` with five valid entries (identifier, display name, media type, URL, two representative queries each).
- Lighthouse on the assembled build: accessibility 100, best practices 100. SEO is lower only because of the intentional `noindex`.

## 5. For launch (owner decisions and steps)
1. Choose the domain; build with `SITE_URL=https://<domain> OUTSPOKEN_INDEXABLE=1`; this also writes `ard.json` with the right publisher.
2. Verify the domain in Google Search Console and Bing Webmaster Tools; submit `sitemap.xml`.
3. When the OUTSPOKEN LinkedIn company page exists, add it to `Organization.sameAs` (do not add profiles that do not exist).
4. Review the privacy draft with a lawyer before indexing (eleven open questions in `privacy.json`).
5. Publish the founders' posts from the LinkedIn analysis on a steady rhythm; answer engines cite pages that other sources mention, which no on-page change can replace.
