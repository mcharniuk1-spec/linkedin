Implementation update, 10 November 2026: the two specifications below are now implemented as owned 1.0.0 skill bundles and explicitly tested/applied. Read the [current evidence and limitations](../../reports/20261110-skills-publications/README.md) for actual readiness. The specification text below is preserved as the earlier design record; its proposed/not-activated wording describes that checkpoint.

# Writing skill requirements

10 November 2026 · OUTSP-46 · specifications delivered for review.

Use the existing [writing architecture](../LINKEDIN-WRITING-ARCHITECTURE.md), [agent workflow](AGENT-ROUTING.md), [patterns](PATTERN-LIBRARY.md) and [templates](templates/README.md). The immediate need is consistent use of that method. Another collection of generic writing instructions would add maintenance without filling an observed gap.

The two specifications below define future reusable capabilities. They are usable as manual task contracts now. They are not activated `SKILL.md` bundles, connected services, trained models or publication authority. The [evaluation cases](skill-evaluation-cases.json) are designed fixtures; no skill-runtime or audience-performance pass is claimed.

## 1. Publication architecture wrapper

Proposed name: `linkedin-publication-architecture`.

**Trigger:** A user requests an original LinkedIn publication outline or a revision of an existing post's argument, story, proof, hook or ending. Use for composition, not account management or collection. One wrapper can route the brief, structure, evidence and revision work; these do not need separate installed skills.

**Inputs:** Intended author and reader; one reader question or decision; desired publication job; approved positioning; source packet with locators, dates, rights and hashes; available first-person material; protected literals; selected output scope. A client's buyer brief remains distinct from Outspoken's own founder ICP.

**Output:** Completed brief, one P01–P14 pattern, two opening options and their payoff, a functional outline, claim/evidence/reasoning/limit map, an earned conclusion, an optional reader response, unresolved inputs, and exact source/revision identities. For a revision, include the invariant comparison and explain material changes. Use the current templates rather than embedding copies in the wrapper.

**Routing decisions that matter:**

| Input condition | Required decision |
|---|---|
| No confirmed founder episode | Use a method, diagnosis or explicitly illustrative example. Hold the actual story; do not invent an event to fill its structure. |
| A number lacks its denominator, comparator or period | Request the missing component, narrow the wording, or omit the numerical claim. |
| Evidence is correlational or selected | Explain the observation and alternatives. Do not write a causal or universal promise. |
| The post has a complete conclusion | Close there unless a specific response serves the reader's job. |
| Humor makes a factual limitation ambiguous | Keep the limitation literal; move, rewrite or remove the joke. Humor is optional. |
| Caption wording changes a claim shown in artwork | Mark the artwork handoff pending and identify the affected panel. Text approval does not approve old pixels. |

**Existing capabilities to reuse:** `founder-content-writing` for author/buyer/evidence preparation; `content-strategy` for job and topic choices; `copy-editing` for focused review passes; `humanize-writing` for argument, specificity and voice; `human-like-rewrite-with-fact-preservation` for the final invariant check. `brand-system-delivery` receives a reviewed content pack when a later design task begins. Actual account and integration readiness require their own evidence.

**Corrections when reusing generic guidance:** Website keyword plans are not LinkedIn caption requirements. Searchable-first prioritization and weighted topic scores are optional planning heuristics. Numerical specificity must come from a source; an editing example is not a fact to insert. Do not manufacture emotion, testimonials, guarantees or founder vulnerability. Simulated reviewers are not customers, independent experts or calibrated quality probabilities. Do not optimize for AI-detector scores.

**Acceptance:** The structure answers one reader job; every material assertion has a matching support or explicit hold; the reasoning makes the evidence-to-conclusion link visible; the opening is fulfilled; protected facts, quotations, dates, links, uncertainty and the required CTA survive editing; first-person claims have author confirmation; the ending fits the job; and the handoff states whether only a skeleton or a complete caption was reviewed. A good style assessment cannot override a failed evidence gate.

## 2. Competitor pattern reviewer

Proposed name: `linkedin-reference-pattern-review`.

**Trigger:** A user supplies or authorizes a bounded source set and asks what writing functions can be learned from it. It does not discover identities, scrape accounts, bypass access stops or rank creators by inferred sales.

**Inputs:** Explicit cohort and exclusions, original source locators and versions, authorized saved text/media, access/rights state, comparison question and observation timestamps. Use the [competitor audit](COMPETITOR-WRITING-AUDIT.md) for the recovered business cohort. The 61-account research corpus is a different population.

**Output:** One row per expected item; evidence tier and actual review modality; observed opening/body/proof/ending functions where the full source permits them; a short original structural abstraction; boundary and alternative explanations; applicability to our reader; adopt/adapt/reject decision; unresolved coverage. Missing full text must produce `not_observable`, not a guessed paragraph sequence.

**Acceptance:** Reconcile missing, duplicate, extra and excluded items. A website service promise remains a self-description. A saved semantic assessment remains a prior interpretation. Only a read source can support exact sequencing or quotation. Counts require dates and denominators; no reach, buyer intent, revenue or causal advantage is inferred from reactions. Transferring a function does not authorize copying distinctive wording, scenes or media.

**Reuse:** Existing corpus IDs and source ledgers, the current claim ledger, the [research applicability filters](RESEARCH-AND-REVIEW.md), and targeted deterministic deduplication. This capability should remain a task protocol until repeated work demonstrates that installation adds value.

## Implementation order and evaluation

1. Use both contracts on an explicitly authorized writing task with the current templates. Record specific errors and useful outputs.
2. If repeated routing failures justify a bundle, build the smallest project-owned wrapper with links to the canonical references. Keep third-party skills and global settings outside it.
3. Validate the exact staged bundle through the supported safe installer, static scan and proportionate source review before activation. Validate references and any scripts. A frontmatter check alone does not establish safe behavior.
4. Use isolated synthetic fixtures and a separate reviewer. Keep the expected behavior fixed before running candidates. Record the exact input/output hashes, actual failures and exposed usage. No live posts, messages or collection runs are replayed for a writing evaluation.
5. Add authorized real founder samples only when their use and privacy boundaries are clear. Founder review remains the authority for stance, personal facts and voice; audience outcomes require actual observation.

The fixtures cover fabricated experience, numerical provenance, causal overreach, hook payoff, humor near disclosure, fair counterarguments, exact CTA, source-tier confusion, caption/media drift and embedded source instructions. They test editorial decisions. They do not predict distribution or establish launch readiness.

## Current execution evidence

This local review read the installed instructions for `founder-content-writing`, `brand-system-delivery`, `content-strategy`, `copy-editing`, `humanize-writing`, `human-like-rewrite-with-fact-preservation` and `skill-creator`. They supplied workflow guidance; no remote humanizer, model training or skill installation was used. The earlier architecture's cloud-skill receipt remains its dated execution record. Available instructions, actual invocation, behavioral verification and account access are different states.

