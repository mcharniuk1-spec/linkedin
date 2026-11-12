# Optional Monid company research workflow — OUTSP-92

## Decision and evidence

Treat Monid as one possible research adapter. It is not the service itself and does not establish who wants to buy. The connected MCP successfully returned discovery and input/pricing inspections on 12 November. No endpoint was executed, no prospect was collected, and no money was spent.

“Monit” is interpreted as the available Monid connector for this option. The spoken names “Jeff” and “Eat and Connect” are not sufficiently identified to select another product. The workflow uses a generic research agent; no named integration is invented.

## Step-by-step operation

| Step | What we do | Tool/input | Output and acceptance |
|---|---|---|---|
| 1 | Record the approved customer rules and exclusions. | OUTSP-15 + T01; a document/Sheet. | Geography, business model, product stage, buyer role and unknowns. Buying interest starts unknown. |
| 2 | Discover a bounded candidate set. | Optional Monid Context.dev company search, or public website search/native manual research. | Company names/domains with provider/date. A proposed pilot is 20 candidates, not a market census. No execution is authorized by this document alone. |
| 3 | Resolve company identity and deduplicate. | Canonical domain; optional akta company search. | One company record per verified domain. Name collisions and conflicting domains remain held. |
| 4 | Verify the facts that affect fit. | Official product/about/team pages; selective permitted enrichment only when needed. | A source and date per decisive fact. Unknown values stay null; provider text alone is not conclusive. |
| 5 | Verify the company and relevant person's LinkedIn links. | Official site links and manual native LinkedIn inspection when access is available. | Domain/name/company-role match with source/date. Do not confuse a company Page with a person's profile. Do not use a third-party scraper to bypass the existing LinkedIn collection hold. |
| 6 | Separate fit from need and interest. | T01 qualification record; agent explanation plus human review. | Fit may be supported while need, readiness or interest remain unknown. No blended sales-readiness score. |
| 7 | Prepare one relevant next action. | Approved service/resource and actual checked context. | A draft note, useful checklist or research hold, with the reason. No false familiarity or invented trigger. |
| 8 | The named owner reviews the candidate and exact draft. | Source record + draft in a document/CRM. | Approved recipient, content and next action. Discovery permission is not authority to send. |
| 9 | If separately requested, execute through the authorized account/channel. | Native account or verified supported integration. | Actual send/reply URL/date/status. No automatic connection or messaging system is implied. |
| 10 | Learn from actual answers. | CRM/Sheet; T07 export when implemented. | Update objections, fit and next step; feed permitted questions into content planning. Likes and profile data do not prove buying interest. |

## Inspected provider options and cost boundary

| Endpoint | What the connected catalog says | Status and use |
|---|---|---|
| Context.dev /company/search | Natural-language company query; country and employee-range filters; cursor pagination. Fast: 2 credits at $0.002 = $0.004/page. Ultra: 10 credits = $0.02/page. | Inspected, not run. Candidate for broad discovery. Results per page and actual useful-match rate are unverified. |
| akta /v1/company/search | Resolve a name/domain to candidate UUID/name/website. Listed at $0/call. | Inspected, not run. Identity resolution, not ICP discovery or proof of fit. |
| akta /v1/company/enrichment | Required company domain/UUID and selected sections. Detailed inspection lists section-specific prices, including firmographic $0.10 and digital_presence $0.025. | Inspected, not run. Generic catalog base $0.025 must not be treated as the price of every section. |

**Planning example, not a quote or bill:** Two fast search pages would be $0.008 at the listed rate. Firmographic plus digital_presence for 50 companies would be $6.25 at the detailed section prices. These amounts exclude other calls, seats, tax, retries, review time and integration work. They do not establish a cost per qualified lead. Reinspect the exact endpoint and pricing before any approved run; usage/result billing needs an explicit bounded budget and actual-cost readback.

No spend is authorized in this block. Default to public websites, manual/native research and a Sheet when the provider is unavailable, untested, too costly or cannot meet the source requirements. Do not replace the existing held LinkedIn collector with another scraper.

## Source and output contract

Each company row needs: stable ID, canonical domain/name, company and relevant person URLs if verified, individual fit facts with sources/dates, separate need/readiness/interest status, unknowns/conflicts, permitted-use state, draft next action and review status. Keep actual contacts and replies private. Public examples use synthetic fixtures or cleared owned material. The companion output contract lists the fields and boundaries; it is a proposed interface, not a running validator or proof of truthful identity, source rights or commercial fit.

[Catalog inspection snapshot](monid-catalog.json) contains the observed schemas and prices. Provider documentation links returned by the connector: [Context.dev company search](https://docs.context.dev/api-reference/company/search), [akta company search](https://agent-docs.akta.pro/api-reference/supporting-apis/company-search), [akta company data](https://agent-docs.akta.pro/api-reference/company-data). Those pages could not be opened through the web tool; no independent documentation, terms or live-output validation is claimed.

Before implementation: finish 14/84/15 choices; approve actual source/vendor terms and retention; select the output fields; time a small reviewed pilot; reconcile actual cost and usefulness; then decide whether Monid belongs in the client service. OUTSP-20 remains open for that full stack/cost selection.
