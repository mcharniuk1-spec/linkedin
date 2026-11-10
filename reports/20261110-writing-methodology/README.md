# LinkedIn writing methodology — execution record

Date: 10 November 2026. Task: **OUTSP-45**. Output status: **delivered for founder review**. Scope: LinkedIn publication patterns and general story architecture.

## Delivered

- [Canonical writing architecture](../../docs/LINKEDIN-WRITING-ARCHITECTURE.md), with fourteen publication patterns and distinct decisions for topic, reader job, pattern, medium and voice.
- [Hooks, evidence, reasoning and endings](../../docs/linkedin-writing/HOOKS-PROOF-ENDINGS.md), plus [humor and interest](../../docs/linkedin-writing/HUMOR-AND-INTEREST.md).
- [Research and review](../../docs/linkedin-writing/RESEARCH-AND-REVIEW.md), [source registry](../../docs/linkedin-writing/source-registry.json), and a [complete coverage audit](../../docs/linkedin-writing/corpus-audit/README.md) of the existing 61-account/279-post projection.
- [Six template files](../../docs/linkedin-writing/templates/README.md) and an [agent protocol](../../docs/linkedin-writing/AGENT-ROUTING.md) that distinguish actual use, reference analysis and historical skill availability.
- [Ten updated post structures](../../publications/20261110-writing-architecture/README.md), covering twenty source variants, with [a filled research-post example](../../publications/20261110-writing-architecture/WORKED-EXAMPLE.md).

The original November 5 captions, rendered artworks, source evidence, approved positioning and collector code are preserved. The structure overlay is the current composition handoff. It does not represent rebuilt artwork, author-approved final captions or live LinkedIn posts.

## Source snapshot and change boundary

Base commit: `9d54e58e85b5c90a8bc674c73b5e87d68baeb0a5`. Working branch: `codex/linkedin-writing-architecture-20261110`. Destination repository: [mcharniuk1-spec/linkedin](https://github.com/mcharniuk1-spec/linkedin).

This is a sparse source checkout. New and modified paths contain original methodology, derived coverage metadata, templates, source locators and the verification record. No source post bodies, private interviews, transcripts, uncleared media, private workbook, credentials or copied upstream skills are introduced. Unchanged omitted assets and the existing collector runtime are not re-audited by this task.

Git synchronization and its exact remote commit are recorded in the OUTSP-45 handoff after remote verification. The commit containing this record is the versioned source of the delivery; no self-referential commit identifier is embedded in the document. Founder acceptance remains a separate workflow state.

## Verification

Run from the repository root:

```sh
python3 reports/20261110-writing-methodology/verify.py
python3 scripts/public_safety_scan.py
git diff --check
```

The verifier uses Python and PyYAML. Its [machine-readable result](verification.json) records exact source row identities, hashes, expected coverage, protected files, approved CTA, source IDs, local links, template parsing and change scope. It also recomputes the descriptive sample statistics. The executed verifier passed all **51 checks**. The separate public safety scan passed with no findings; it checks the materialized tree. A passing scan is not a rights determination or proof of factual accuracy.

The current report contains 279 posts and 61 accounts. Recomputed medians are 107.5 reactions across 276 observed counts and 36.5 comments across 256. All `metric_captured_at` timestamps used in that report are on **22 October 2026**; the wider historical collection window was 20–22 October. These observations do not establish reach, buyer quality, conversion or causal format effects. See the preserved [report](../20261105/README.md) and [data](../20261105/data.json).

Only the relevant documentation and deterministic data checks are required for this update. No collector tests, website build, image render or native LinkedIn preview is claimed.

## Independent review and resolved findings

Work was assigned to separate, non-overlapping paths. A second worker reviewed the core architecture and current-post overlay against both original source bundles, approved positioning and report data. Another worker reviewed the integration and public boundary outside the files they authored. Agent review is editorial and mechanical assistance; it does not add independent empirical evidence.

Resolved during review:

1. The positioning hook now promises four checks, matching the four criteria it supplies.
2. The post 05 survey statistic is recorded as a candidate with unverified applicability and is not carried forward into the new structure.
3. The post 09 diagnosis distinguishes repeated medians in the humanized version from the missingness approach already present in evidence-v1.
4. Date labels distinguish the wider collection window from the report’s metric timestamps.
5. The agent protocol now uses the same separate status vocabularies as the review template.
6. The older writing graph is explicitly marked as a historical index because two of its source hashes predate this revision. Current composition tasks read the new canon directly.

The exact check results and any remaining findings must be read alongside [verification.json](verification.json), rather than inferred from the presence of a file.

## Remaining inputs and practical limits

The 61 reference accounts are not the fifteen commercial competitors named as a group in earlier planning. Three agencies could be identified and reviewed from accessible project records: Windmill, HatTip and SalesBread. The remaining twelve identities and their earlier workbook remain unavailable. SalesBread is an adjacent outbound service, so its claims are not evidence about organic writing effectiveness.

The public corpus contains derived assessments rather than original post bodies. Its 279 records were checked for identity, completeness and usable fields; this is not a new close reading of 279 full posts. Seven unresolved historical source IDs remain explicitly recorded. New method sources are registered separately.

Before adapting a structure into a real founder story, obtain the specific confirmed decision, alternatives, consequence and permission to share. Before releasing a current caption, obtain founder voice/capability review and reconcile its changed claims with the media package. The methodology is complete as a reviewable architecture; these inputs concern factual stories and publication readiness.

OUTSP-45 moves to **Review** after the verified Git handoff. The project’s founder-review rule keeps it out of Done until the appropriate author review occurs. No unrelated tasks were claimed.
