> Dated method record from22October2026. Source evidence bytes remain local; use the current dataset state for later observations and gaps.

# Search, ranking and qualification: what each tool can establish

Checked 22 October 2026. The objective is a useful reference library for Europe-based B2B AI SaaS founders, plus a separate company-level prospect list. Discovery, relevance, performance and buying interest are different decisions.

## Tools and their actual roles

| Need | Tool / route | Current state | Limits and decision |
|---|---|---|---|
| Find posts about a business problem | Keyless Exa hosted MCP, called through the installed `mcporter` CLI with `imports:[]` | Two fresh v5 CLI probes succeeded: four post locators and four profile locators. v4 also ran seven successful searches. | Free keyless route; numeric quota and coverage unknown. It searches the public web index, not an unrestricted LinkedIn feed. Preserve the query/results and check actual post dates and counters. |
| Find founders / accounts | Exa profile/company queries, then captured professional role and product evidence | Working for candidate discovery; the four new profile locators are not automatically approved prospects. | Country words and profile slugs do not establish business base, current role or funding. Do not infer a role merely because someone writes about B2B. |
| Expand a known reference account | Rotating Exa author queries; exposed same-author public post links | Implemented and tested in v4. | Link expansion is biased toward what the page exposes. It does not retrieve all account history or prove regularity. |
| Use LinkedIn's own post filters | Native Posts search → All filters | Documented route; no signed-in session connected by this run. | LinkedIn documents Sort by, Date posted, Content type, From member/company, Posted by, Mentioning member/company, Author industry/company. Availability can vary. Top match is relevance, not a global most-reactions leaderboard. |
| Find people / companies natively | Native People / Companies search → All filters | Optional human seed route. | Verify available account filters in the UI. Company size bands and location are screening hints; verify Europe base, exact size fit, business model and latest funding separately. Sales Navigator's richer filters are a distinct paid product. |
| Get top-account seeds | LinkedIn Top Voices; public Favikon rankings | Documentation reviewed; not used as performance truth. | Top Voices is editorial/invite-only. Favikon Free shows only three entries per ranking, with broader filtering restricted by plan. Neither establishes which of our sampled posts is trending. |
| Find popular-content inspiration | Kleo public product; native search results | Assessed, not connected. | No verified free unattended API or unlimited free corpus access was established. Advertised templates/free gifts are not an API entitlement. Keep optional, not a dependency. |
| Automate signed-in LinkedIn search | `stickerdaniel/linkedin-mcp-server` | Source reviewed; not installed/activated. | Advertises post/people/company search, but authenticates through a saved session and defaults to importing a local browser session. This run does not authorize or use cookie import. Open source does not mean anonymous LinkedIn access. |
| Route existing capabilities | Agent Reach | Previously assessed; no verified active LinkedIn backend. | A router does not create data access. Use the actual working backend, not the Agent Reach label, as readiness evidence. |
| Capture actual counters/media | Local Python guest-page collector + BeautifulSoup + bounded HTTPS requests | Working on exposed public pages; layout variants are tested. | Preserve unknown counters, access stops and coverage gaps. No impressions, private analytics, bypass or paid fallback. |
| Transcribe / prepare video evidence | Cached local Whisper; FFmpeg/ffprobe | Existing tools; no new installation or model download. | Original captions and alternatives remain separate. Mechanical QA is not audio validation. |
| Understand media and post meaning | Native supervisor agent reviewing source text and actual media evidence | Source-bound interpretation stage. | Existing AI media reviews are explicitly prior evidence. Sampled frames are not continuous watching. No ComfyUI/VLM connection is claimed. |

Primary sources: [Exa MCP](https://exa.ai/mcp), [LinkedIn Posts search](https://www.linkedin.com/help/linkedin/answer/a526104), [LinkedIn search](https://www.linkedin.com/help/linkedin/answer/a523136/search-on-linkedin), [Top Voices](https://www.linkedin.com/help/linkedin/answer/a776208/linkedin-top-voices?lang=en), [Favikon plan limits](https://help.favikon.com/en/articles/10683306-what-rankings-can-i-see), [Sales Navigator filter definitions](https://www.linkedin.com/help/sales-navigator/answer/a1461507), [Kleo](https://kleo.so/), [LinkedIn MCP source](https://github.com/stickerdaniel/linkedin-mcp-server).

## Search recipes

Start with the buyer problem, then discover authors from relevant posts. Search these themes separately: positioning and differentiation; buyer objections and proof; founder decisions and building; AI product use cases; founder-led sales; demand generation; content and personal-brand systems. A broad AI keyword alone produces a noisy candidate pool.

Examples of tested CLI query shapes:

```text
site:linkedin.com/posts/ "B2B" "positioning" after:2026-10-15
site:linkedin.com/in/ "founder" "AI" "SaaS" "Netherlands"
site:linkedin.com/posts/{approved_author_slug}_ after:{since90} before:{tomorrow}
```

The first v5 topic query returned two already-known posts published before the requested `after:` date. This is direct evidence that the hint does not enforce source publication age. Keep candidate results, then validate source dates. See `free-route-probes.json`, `probe-locators.json` and `probe-evaluation.json`.

For optional native search, open [Posts](https://www.linkedin.com/search/results/content/?keywords=B2B%20AI%20SaaS), choose a recent window and Latest for fresh candidates, then Top match for a complementary relevance view. Filter by the actual member/company where available. Use [People](https://www.linkedin.com/search/results/people/?keywords=founder%20AI%20SaaS) and [Companies](https://www.linkedin.com/search/results/companies/?keywords=AI%20SaaS) separately. Do not equate the two result sets with a population ranking. This run neither logged in nor verified a signed-in filter combination.

Google Trends is optional search-demand context. It does not measure LinkedIn post interactions. No free unrestricted all-LinkedIn trend API was found. The operational method is therefore discovery → source checks → qualified watchlist → actual counter observations.

## Decision ladder

1. **Identity and eligibility:** actual target activity/author, public source, valid date state, original post versus explicit sponsored/repost, exact-corpus duplicate keys. Preserve real variants as separate publications but group near-identical ideas for synthesis.
2. **Reference-account fit:** claimed professional role/product/company and a useful transfer role. A B2B reference need not be a European AI SaaS prospect. Approval means a candidate is suitable to study; it does not mean top-performing, verified expert or interested buyer.
3. **Post meaning:** read the full post, then distinguish its main subject, editorial job, intended reader, central claim, hook and practical adaptation. Read source-bound image/video evidence separately. Missing media is a gap, not evidence that a post is text-only.
4. **Observed performance:** use the latest actual snapshot, displaying its timestamp, source hash and counters. Compare only a selected same-author, format, age-band and language cohort with at least eight usable records. Use midpoint ranks for ties; all-equal values do not become winners. A strong sample reference must exceed the sample median and reach the upper 20% band. This is a proposed descriptive rule, not a LinkedIn standard.
5. **Measured change:** two genuinely different observations at least six hours apart, normalized with matching parser version and code hash. Re-running a parser on old bytes is not a new observation. Negative counters are preserved as possible corrections/removals, excluded from positive-growth comparisons.
6. **Trend claim:** positive change alone is insufficient. Require fresh comparable peers, meaningful positive separation, several real intervals and enough coverage before a local emerging-trend claim. A global trend claim remains unsupported. Flat historical cohorts are not trends.

The dataset gives separate reasons for content qualification, relative performance and trend status. A compelling hook or useful diagram is an interpretation of the creative material. It does not prove that the hook or diagram caused engagement. Mechanism explanations are hypotheses for original content experiments.

## Prospect lane

Search official company/product/funding sources and public company profiles for Europe-based B2B AI software, 10–50 people and Seed–Series B. Keep self-reported size bands provisional. Europe includes the UK under the approved positioning. A profile's country or employee-affiliation count does not prove company base or payroll. Latest funding, recurring SaaS model and conflicts need explicit evidence/holds.

Keep description, links and field-level evidence only. No full prospect post corpus, employee directory, media or private contacts. A weak company page or irregular founder content is a possible service opportunity, not expressed need. No buying-interest score follows from low activity. The existing 20 company summaries stay separate from reference publications.

## Architecture choice

Retain SQLite plus content-addressed files and a source-bound supervisor queue. This dataset does not need a vector database, cloud warehouse or new paid orchestration service. Improve parser coverage, provenance, semantic rows and real measurements before adding infrastructure. Native collaboration proves messages inside this active task; it does not establish an unattended future wake/ack adapter. A durable event remains a queue until that adapter is actually verified.

## Later v6 access observation

The keyless Exa route returned exact Sohail profile-role evidence, then the exact Akshay query hit its free MCP rate limit. No numeric quota is inferred, no key was created, and no further search was attempted. Previously known-post observation does not require this search backend. Direct profile reads by the web reader were separately blocked and stopped. Backend limitations stay explicit.
