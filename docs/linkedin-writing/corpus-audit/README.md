# Historical corpus coverage audit

Audit date: 10 November 2026. Source snapshot: [9d54e58e85b5c90a8bc674c73b5e87d68baeb0a5](https://github.com/mcharniuk1-spec/linkedin/commit/9d54e58e85b5c90a8bc674c73b5e87d68baeb0a5).

This package audits **all 61 reference accounts and all 279 post records** in the existing public projection. It supports the [writing architecture](../../LINKEDIN-WRITING-ARCHITECTURE.md) by distinguishing usable prior assessments from missing primary material. It contains counts, labels, missingness, source identities and join checks. It contains no copied post bodies, full transcripts, private originals, account-performance values or rankings.

## Files

| File | Grain and purpose |
|---|---|
| [audit.json](audit.json) | Aggregate diagnostics, input hashes, category coverage, authority boundaries and migration recommendations. No full account/post analysis text. |
| [accounts.csv](accounts.csv) | One row per reference account: URL, post count, category coverage, derived-assessment availability and missingness. |
| [posts.csv](posts.csv) | One row per post ID: locator, dates/hashes, prior labels, evidence availability and join status. No post body or claim-summary text. |

CSV dictionaries such as `topic_counts` are JSON objects within a quoted cell. Booleans are written as `true` or `false`. Unknown fields retain their original markers.

## Inputs and method

The two corpus inputs are [the report](../../../reports/20261105/data.json) and [the public derived dataset](../../../datasets/current/dataset.json). The historical source-ID check uses [editorial-methods.json](../../../editorial/sources/editorial-methods.json) and [references.json](../../../editorial/sources/references.json).

The underlying source run is `20261022-linkedin-pipeline-v6`, with a dataset date of 22 October 2026. The report was generated on 5 November. That export date does not make the historical observations current. The exact byte SHA256, Git blob SHA and pinned GitHub URL for every input are in `audit.json`.

Post joins use exact IDs. Account joins verify the LinkedIn host and use the lower-case `/in/<slug>` or `/company/<slug>` pathname, removing a trailing slash. Regional host variants do not create a new account; original URLs are retained. No fuzzy matching or guessed identity is used.

## Coverage findings

| Check | Result |
|---|---:|
| Dataset and report post rows | 279 each |
| Account rows and unique joined accounts | 61 |
| Sum of account post counts | 279 |
| Duplicate post IDs | 0 |
| Post/account/media/snapshot join orphans | 0 |
| Cross-file post, author, topic or editorial-job mismatch | 0 |
| Prior derived summary, claim, caveat, hook and adaptation assessment | 279 each |
| Original post bodies distributed in the projection | 0 |
| Full-source close readings performed in this audit | 0 |
| Posts with `messenger_role`, `experience`, `message_origin` not coded | 279 each |
| Posts with unknown author type | 5 |
| Accounts with a separate author-decision record | 38 |
| Accounts without a separate author-decision record | 23 |
| Media metadata rows | 207 |
| Posts with acquired asset metadata | 143 |
| Transcript metadata rows | 24 |
| Full transcript texts or original media bytes distributed here | 0 |

Every post has `original_post_distribution=full_text_retained_locally`. Every report row has `text_status=captured_dom_completeness_unverified`. The source hashes identify earlier material; they do not make that material available or prove text completeness.

The availability of a `central_claim` or `claim_caveat` means that a prior derived assessment exists. It does not verify the author's statement. This audit checks the fields and joins, not the correctness of every earlier literary interpretation.

The five unknown author-type rows concern Anthony Pierri, Cognism, Refine Labs, Richard van der Blom and Smarter SaaS Growth. Other rows for an account may have a type. Missing type is preserved, not inferred from a name or URL.

There are 144 posts with a non-text media label but asset metadata for 143. The remaining Grameen HealthTech Limited image-labelled post, `urn:li:activity:7488486895841136641`, already records `media_evidence_basis=unavailable_when_held`. It remains a coverage gap; it is not a broken foreign key.

Historical media metadata marks 169 rows as reviewed and leaves that field absent on 38. Assets include captions and posters as well as images, document previews and video, so these statuses are not interchangeable with a count of complete audiovisual reviews. This audit did not view source media, listen to audio or read full transcripts.

## Prior category labels

These are frequency counts of existing classifications. They describe this selected corpus and do not establish optimal content allocation or performance.

| Editorial job | Posts |
|---|---:|
| announce_offer | 63 |
| build_in_public | 8 |
| challenge_belief | 46 |
| entertain | 6 |
| show_proof | 23 |
| start_discussion | 6 |
| teach_method | 91 |
| tell_story | 36 |

| Media class | Posts |
|---|---:|
| document | 9 |
| image | 111 |
| text | 135 |
| video | 24 |

The twelve topic counts and all field-level missingness are in `audit.json`. Per-account topic/job/media distributions are in `accounts.csv`.

## Seven unresolved historical source IDs

The old methods file requests 12 source IDs. Five resolve against its sibling 34-entry reference file; seven do not:

- LI-FEED-2026
- LI-NEWSLETTER-FAQ
- LI-B2B-CONTENT-STUDY
- LI-INDIVIDUAL-V-CORP
- LI-FEED-SR-PAPER
- LI-ENGAGEMENT-PREDICTORS-2025
- SOCIALINSIDER-2026

This is a local historical mapping gap, not a finding that the external publications do not exist. Preserve the dated record. A new claim needs a resolved source and a checked relevant passage, or it must be narrowed, held or removed.

## How the writing method may use this corpus

Existing labels, claim summaries and adaptation ideas may guide question selection or suggest a pattern to investigate. Preserve their status as prior derived assessments. Do not call them fresh source readings or evidence that a technique caused results.

New annotations belong in a versioned sidecar keyed by `post_id`, with reviewer, date, source hash, evidence locator, actual source access and review scope. Keep `messenger_role`, `experience` and `message_origin` unknown until supported review supplies those labels. `tell_story` does not by itself establish personal experience.

The 61 reference accounts are distinct from the commercial competitor workbook, the collector allowlist and the separate 20-prospect list. This package does not complete the 15-competitor register or evaluate their websites.

No source acquisition, private workbook access, collector-hold change or social publication occurred. A zero join-error count establishes consistency within these files; it does not establish complete LinkedIn coverage, source truth or publication rights.
