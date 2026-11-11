# Waalaxy free tools: first-pass review for OutSpoken

Reviewed: 2026-11-11 (Europe/Sofia). Scope: ten distinct tools discovered through the English catalog and the bounded related-tool link pass; canonical/blog duplicates are grouped. Method: official Waalaxy pages read via web search/open; no tool forms submitted, no accounts created, no personal data used, no LinkedIn media downloaded. **Proof level for every item: page read only; no runtime test.** Embedded iframe/app content was not consistently visible in indexed page text; field-level detail below is what Waalaxy's page text describes, not independently verified behavior.

## Practical tool notes

### 1. Employee Search Builder
Official page: https://www.waalaxy.com/free-tools/employee-search-builder
- Solves: creates a LinkedIn employee search URL.
- Input: embedded app linked; page text does not show its fields. Related Waalaxy material mentions company, title, industry, location, and connection level, but exact controls remain unverified.
- Output/gating: URL claimed; app behavior, login, and limits unverified.
- OutSpoken: deterministic criteria-to-URL builder; preview criteria and URL. No scraping or complete-coverage claim; user opens LinkedIn.

### 2. Enrich LinkedIn URL (CSV enricher)
Official page: https://www.waalaxy.com/free-tools/enrich-linkedin-url
- Solves: adds structured profile data to a list of LinkedIn URLs.
- How / input: CSV only, LinkedIn profile URLs; up to 20 profiles per file. Page says upload, click Enrich, then receive an updated CSV. No specific output columns were listed in the text inspected.
- Output / gating: enriched CSV claimed. Page describes it as free; linked tool is app.waalaxy.com, so signup/access gate is unclear from inspected text. The marketing page separately states 20 profiles/file.
- OutSpoken version: only offer with an authorized, compliant data source and disclosed provenance; no direct LinkedIn scraping or implied completeness. Prefer a user-uploaded export and deterministic mapping, marking unavailable fields blank/unknown.

### 3. LinkedIn Video Downloader
Official page: https://www.waalaxy.com/free-tools/linkedin-video-downloader
- Solves: extracts an MP4 from a public LinkedIn post URL.
- How / input: paste public post URL, click Download. Page claims no login, watermark, or extension; public posts only; private/restricted/removed may fail.
- Output / gating: MP4 download claimed, free/no account claimed. No actual download attempted. Waalaxy itself warns to respect copyright and LinkedIn terms.
- OutSpoken version: exclude from an optimization service unless client owns the video or documents permission. For owned assets, use direct client upload or official export, not a public-post downloader. Do not reproduce this workflow for third-party media.

### 4. LinkedIn URL Finder
Official page: https://www.waalaxy.com/free-tools/linkedin-url-finder
- Solves: resolves LinkedIn profile URLs from contact details.
- Input: CSV with first/last name and company; company required. Hero copy also mentions email, but detailed steps omit it.
- Output/gating: profile URLs and enriched CSV claimed; page says free/no account. Duplicate names can be ambiguous.
- OutSpoken: require lawful basis and trusted source; label candidates with evidence/confidence and require human identity confirmation. Input-field inconsistency unresolved.

### 5. LinkedIn Headline Generator
Official page: https://www.waalaxy.com/blog/free-tools/linkedin-headline-generator
- Solves: drafts profile headlines for copy/paste.
- How / input: job title/value, audience and optional keywords; choose tone (professional, creative, witty, minimalist). Waalaxy says five headline variants using different formulas (value proposition, credibility, keywords, hook, minimalist).
- Output / gating: five English headlines claimed; free, no sign-up, five generations/day. No generation performed.
- OutSpoken version: combine a deterministic intake/checklist with LLM drafting; ask for substantiated role, audience, offer, proof and tone. Flag unsupported metrics/claims; deliver options plus rationale and a character count, then founder approves.

### 6. LinkedIn Summary Generator
Official page: https://www.waalaxy.com/blog/free-tools/linkedin-summary-generator
- Solves: drafts a LinkedIn About section.
- How / input: job title, up to three achievements or skills, optional years of experience, chosen tone (professional, storytelling, creative, punchy).
- Output / gating: copy-ready About text; free, no sign-up, five generations/day. Waalaxy says AI uses supplied achievements and does not invent them. No generation performed.
- OutSpoken version: LLM may organize only owner/client-provided facts; keep claims source-linked, distinguish metrics from aspiration, and mark missing evidence. Provide editable draft and fact-check table; no auto-posting.

### 7. LinkedIn Boolean Search Generator
Official page: https://www.waalaxy.com/blog/free-tools/linkedin-boolean-search-generator
- Solves: formats Boolean searches for LinkedIn, Sales Navigator, Recruiter.
- How / input: comma-separated job titles (OR), required keywords (AND), excluded keywords (NOT). Multiword titles are quoted and alternatives grouped.
- Output / gating: copyable Boolean string; page claims free/no sign-up and unlimited searches. No query submitted. Page recommends combining with native filters and warns long queries may be truncated.
- OutSpoken version: deterministic string builder, not LLM. Escape/quote terms consistently; show the exact logic and warn that search results depend on LinkedIn and user access. Do not imply a generated query guarantees audience fit.

### 8. LinkedIn Search Generator
Official page: https://www.waalaxy.com/free-tools/linkedin-search-generator
- Solves: creates a filtered LinkedIn search URL. Distinct from Boolean Search Generator, which outputs Boolean text.
- Input: title, location, industry, connection level per page. A related guide also shows company/keywords, country, degree, and LinkedIn/Sales Navigator mode; exact controls unverified.
- Output/gating: shareable URL claimed; page calls it free, signup unclear. Not generated.
- OutSpoken: deterministic URL builder. Show filters/mode; no completeness or ICP-fit claim.

### 9. Website Roaster
Tool page: https://www.waalaxy.com/free-tools/website-roaster
Related blog: https://www.waalaxy.com/blog/free-tools/website-roaster
- Solves: tool page claims UX/design/copy review; it links an app but exposes no fields/report details.
- Input/output: blog says public page URL; claims visible-copy analysis, /100 score across seven pillars, five before/after recommendations, four-week plan, three competitors, LinkedIn sequence.
- Gating/proof: blog claims free/no signup/about one minute. These details are blog claims only; no runtime report generated.
- OutSpoken: prioritize for landing task 59 as critique only; verify against current page and requirements. Treat scores/competitor claims as hypotheses. For profile/posts, use approved facts → evidence ledger → ICP/positioning → drafts → human review → authorized measurement. No fake proof or automated publishing/outreach.

### 10. ICP Generator
Official page: https://www.waalaxy.com/free-tools/ideal-customer-profile-generator
Related blog: https://www.waalaxy.com/blog/free-tools/ideal-customer-profile-generator
- Solves: structures a company's best-fit target profile; key benchmark for OutSpoken qualification task 15.
- Input: company, offer/value proposition, uniqueness per tool page; blog specifies product, problem solved, target industry.
- Output/gating: page claims structured ICP; blog claims three ranked profiles with size, revenue, decision-maker, pain, buying trigger, rationale. Blog says free/no sign-up/five analyses daily. Not runtime-verified.
- OutSpoken: build on client discovery and source evidence; label outputs as hypotheses, not verified demand or buying intent. Human approves criteria before outreach.

## Bounded link closure and evidence status

I re-read the official English `/free-tools` index and the nine previously reviewed official tool pages, following their internal `/free-tools/` recommendations and deduplicating repeated cards/routes. This bounded closure found **10 distinct named tools**: Employee Search Builder, Enrich LinkedIn URL, LinkedIn Video Downloader, LinkedIn URL Finder, Headline Generator, Summary Generator, Boolean Search Generator, Search Generator, Website Roaster, and ICP Generator. Search URL generation and Boolean string generation are separate behaviors, not aliases. The index rendering varied: navigation exposed four generators/finders, body cards varied (four or five, including Website Roaster); child pages exposed Search Generator and ICP Generator. The four creator tools' article URLs use `/blog/free-tools/`, and are included as separately read tool pages.

All 10 tools have an official tool page or Waalaxy tool article read for functional claims; **all runtime interfaces/reports are untested**. Website Roaster is special: its official tool page supports only the broad UX/design/copy claim and an embedded app link; detailed scoring/report claims above come only from its related blog article. ICP Generator's official page documents company/value-proposition input and structured ICP output; the three-ranked-profile detail and five-per-day limit come from its blog article. No other unique internal `/free-tools/` target was found in the bounded set of index plus reviewed tool pages. This does not claim completeness across all Waalaxy products, locales, or unrelated blog articles.

## Cross-tool implementation recommendation for OutSpoken

For website task 59, start with Website Roaster-style critique because the immediate deliverable concerns the landing page. Use its URL-based checklist only as a prompt; verify each item on the current page and apply the approved design system. For qualification task 15, make ICP discovery core: client intake → qualification evidence ledger → company-fit hypotheses → evidence-backed ICP criteria → human approval. For OutSpoken profile and post optimization, use this sequence: approved facts/proof → positioning → profile headline/About outline → source-grounded post themes and drafts → human founder/client review → measure against authorized baseline analytics.

Build a small service menu around three client outcomes: (1) profile copy drafting (headline/About) with client-supplied facts and human fact review; (2) deterministic audience/search planning (Boolean and search URL builders); (3) profile/process audit with clearly labeled recommendations. Treat URL enrichment and identity finding as a separate, consented data service with a documented source, lawful basis, accuracy and retention rules. Do not offer third-party video downloading as an optimization feature. Never promise engagement, leads, reach, or conversion based on generated copy or search URLs; measure those only from client-authorized analytics and report their actual denominator and period. Keep all outputs drafts; no automatic LinkedIn edits, connection requests, messages, or publishing.

## Provenance and evidence boundary

Sources are Waalaxy's public first-party pages linked above, read on 2026-11-11. The review records page claims, not independent validation. In particular, embedded applications, signup conditions on app subdomains, runtime output accuracy, terms/data retention, and current limits beyond explicit page claims were not tested. Do not reuse Waalaxy code, copy, design assets, or media; this is functional benchmarking only.
