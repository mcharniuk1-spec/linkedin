# Copy contract for writing and design

## Audience and offer

Agency ICP: Europe-based B2B AI SaaS founders; company size 10–50 people; Seed–Series B; founder-led LinkedIn. These are targeting constraints, not evidence of willingness to buy. A client's buyers need their own industry, roles, business job, trigger, alternatives and proof.

Keep the exact hero, VP and CTA in START-HERE. Approved positioning is an owner decision. Buyer validation, keyword demand, conversion improvement and AI citation performance remain unvalidated until observed.

## Execution order

| Stage | Execute | Skill route | Review artifact |
|---|---|---|---|
| 1. Evidence and voice | Use the approved documents, interviews and voice samples; map claims, buyer problem, objections, offer and next step; select natural voice before drafting | `product-marketing`, `content-strategy`, `humanize-writing` | Buyer/voice brief, source and claim IDs, protected literals |
| 2. Intent and page plan | Record dated query evidence and locale; distinguish a search sample from measured demand; choose useful pages and internal links | `site-architecture`, `seo-audit`, `content-strategy` | Page/intent map and demand state |
| 3. Draft | Write specific, credible buyer-facing copy; preserve approved hero/VP/CTA; connect claims to evidence; match ad and landing-page promises | `copywriting`; `social` for LinkedIn; `content-research-writer` for sourced articles | Draft with proof map, headings, CTA and channel variants |
| 4. Search and conversion | Check title/description, headings, crawlable text, links, appropriate schema and CTA clarity; retain necessary claim qualifiers | `seo-audit`, corrected `ai-seo` route, `schema`, `cro`, `conversion-landing-page-audit` | SEO/CRO checks and implementation requirements |
| 5. Natural-language edit | Improve argument, rhythm, specificity and transitions; check every protected fact, quote, citation and term against the draft/source | `copy-editing`, `humanize-writing`, `human-like-rewrite-with-fact-preservation` | Edited revision, invariant diff and claim review |
| 6. Design handoff | Freeze reviewed exact copy, IDs and hashes; map to editable slots/components/stories/Figma nodes; inspect real mobile/long-copy states | `brand-system-delivery`, stage-specific Figma/UI/accessibility skills | Content pack and design mapping |
| 7. Measure | Collect actual search/citation/qualified-conversion evidence with date, scope and denominator; propose the next test | `analytics`, `ab-testing`, service measurement reference | Dated observations, causal limits and next test |

No Turnitout call runs in this workflow. Its public JavaScript includes a small replacement demonstration with simulated scores; the described Python engine is missing and the public license is proprietary. Do not copy that demo into the project or treat its score as copy quality. The owner has authorized writing optimization, not client-text uploads to its hosted service.

## Website pack

Create one JSON pack per page/revision from `content-pack.template.json`:

- Identity: stable ID, revision, client, artifact type, locale, audience, purpose and primary conversion action.
- Sources: source IDs, locators, versions/hashes, observation date, rights/use limits. Claims link to these IDs and carry `fact`, `opinion`, `interpretation`, `hypothesis` or `gap` state. A claimed outcome needs exact supporting evidence and scope.
- Protected text: exact approved strings and technical/factual literals. The pack's body slots must contain the protected strings selected for that artifact. A supporting page need not repeat the homepage hero; list only the owner-required strings for that artifact.
- Search: intent, query-evidence records (query, source, date, geography, metric type/value), demand state, URL, distinct title/description, index/canonical intent, internal links and structured-data decision. `null` means unknown; zero means observed zero. Empty evidence means unvalidated demand.
- Copy: each editable slot has a stable ID, role, text, claim IDs and optional design length constraint. Include heading roles, body, proof, CTA, alt/caption text as applicable. Store heading and link destinations as data, not baked into generated images.
- Review: status, evidence/SEO/voice reviewer records, unresolved gaps and approved copy SHA-256. Hash the canonical JSON serialization of the ordered `slots` array (UTF-8, sorted object keys, compact separators, no ASCII escaping). The supplied validator computes this exact value.

The template is deliberately unfinished and is expected to fail release validation. For this agency homepage the validator additionally requires exact text in the `hero-title`/`h1`, `hero-body`/`body` and `hero-cta`/`cta` slots. Use the current owner-selected name from the project route where needed; missing domain, CTA destination and proof stay unresolved. Do not fabricate them to make a template pass.

Run `python3 writing-system/validate_content_pack.py /absolute/path/to/pack.json` from the LinkedIn project root. Add `--release` only for an actual approved pack; that requires reviewer/approval records and an exact hash. All errors must be resolved or explicitly left as a draft gap. The helper checks structure and exact values; a reviewer must still inspect claims, rights, grammar, search usefulness and actual rendered output.

## Channel differences

LinkedIn posts need a relevant founder viewpoint, source-grounded specifics, readable paragraphs and useful conversation. Keywords and profile terminology support clarity and discovery, but website metadata/schema rules do not apply to an ordinary post. Do not invent reach effects, comment pods or relationship automation.

Website pages need a clear buyer task, credible offer and next step, crawlable readable text, a coherent hierarchy and truthful metadata. Avoid duplicate thin pages or irrelevant topic expansion for search. Generic SEO skill quotas, speculative platform statistics, forced FAQ markup and blanket AI-bot allowlists are not project requirements. Use the installed writing wrapper's current-primary-source corrections.

Video packs add source-linked spoken beats, on-screen slots, timing assumptions, captions, footage/rights and actual export checks. Scripts do not prove footage exists or grant voice/likeness authority.

## Search evidence and limits

Use Search Console/Bing Webmaster property data when authorized and available; optionally compare provider estimates or Google Trends with date/market and method. No client property or keyword subscription was connected in this setup. Current target-keyword demand and baseline ranking are unknown.

[Google](https://developers.google.com/search/docs/appearance/ai-features) says normal SEO practices apply to its AI Search features and no special files/schema are needed. Preserve readable content and proper technical eligibility. This does not guarantee indexing or appearance. Search/AI visibility and sales are measured outcomes, not copy certifications.

[OpenAI](https://developers.openai.com/api/docs/bots) distinguishes search crawling, model training and user-triggered retrieval. Do not turn training access on as an SEO prerequisite. [Bing AI Performance](https://blogs.bing.com/webmaster/2026/2/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview/) provides citation observations for supported surfaces; it is not a universal AI ranking score. Record engine-specific evidence and avoid causal claims from simple before/after counts.

## Design changes

Copy remains canonical in the approved content file, tokens in the token source, components in shared source and image masters in the asset register. Link the content hash to the design release. If design changes text or truncates meaning, return that slot for review, revise the hash and rerun affected previews/SEO checks. Do not shrink type or hide essential copy to fit a component. Maintain the master plan's component states, mobile/long-copy, accessibility and motion checks.
