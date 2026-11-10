# Outspoken outreach preparation kit

10 November 2026 · OUTSP-50 · owned templates and one explicitly synthetic example.

Use this kit to prepare a small, source-specific conversation. It contains no real prospect list, contact details, customer evidence, sent messages or sending capability. A complete template is not an approved offer, verified lead, legally reviewed channel choice or authorization to contact anyone.

## Files and decisions

| File | Fill it with | Keep separate |
|---|---|---|
| `fit-source-verification.csv` | Company/source identity, actual observation, source date, use rights, fit, unknowns and stop state | Firmographic/topic fit, expressed need and buying interest are different fields. No blended sales-readiness score. |
| `warm-intro-context.template.json` | A real relationship, its owner, exact shared context and permission to use or name it | A public follow, connection, shared community or old mention does not prove familiarity or permission for an introduction. |
| `first-message.template.json` | One source-specific observation, why it may matter, and one proportionate question | A plausible pain is a hypothesis until the person states it. Do not claim you audited, met, helped or were referred by someone unless confirmed. |
| `follow-up-and-stop.template.json` | Original message identity, actual contact history, reply/stop check and at most one manually reviewed follow-up | No reply is neither consent nor buying interest. A reply must be read before any further action. No automatic sequence or universal delay is prescribed. |
| `discovery-and-mini-audit.template.json` | Permission-aware interview notes and a review of exact named source surfaces | Observation, interpretation and proposed change are separate. A mini-audit is not an account-wide performance, product or legal audit. |
| `conversation-log.csv` | Minimal factual notes: problem, budget state, objections, response, actual next step and stop state | A courteous reply, booked call and acceptance of an offer are different observations. Define a qualifying conversation and “yes” before counting them. |
| `synthetic-example.json` | A complete fictional preparation case using `example.invalid` | No real person, company, relationship, conversation or product result is represented. Nothing was sent. |
| `validate.py`, `test_validate.py` | Structure checks and deliberately failing fixtures | Structural checks do not verify facts, consent, laws, account access, buyer intent or commercial outcomes. |

The four JSON templates are intentionally empty: they provide complete fields and questions, not fabricated answers. The CSVs contain headers only. Copy them to an approved private working location before adding real prospect or conversation information. Do not commit filled private records, personal details, copied source posts or unapproved quotations into the public repository.

## Prepare the contact

1. Verify the exact company and professional role from permitted sources. Record a locator, what was actually seen, date, rights/use state and unresolved identity or fit. The current agency ICP is Europe-based B2B AI SaaS founders, 10–50 people, Seed–Series B; it is a targeting choice, not evidence that a company needs the service or wants to buy.
2. Keep public observation separate from an inferred opportunity. Keep a prospect’s explicit statement of need separate from fit. Record buying interest only when a source supports the exact claim, such as an agreed next step; do not derive it from funding, posting frequency, a connection or reactions.
3. Use a warm route only with real, permissioned context. If no relationship is established, say so internally. Do not invent a connector or imply that a source suggested the outreach.
4. Draft one precise message. Identify the source observation, offer a bounded reason it could be useful, and ask one answerable question. State the service as proposed where its scope still needs agreement. Do not add an unsupported case, testimonial, time saving, revenue claim, guarantee, scarcity or discount.
5. Record founder review of the exact message and channel, any applicable legal/privacy review, contact history and stop state. This kit keeps `send_authorization` at `not_authorized`; a validator pass never changes it. Actual sending requires its own current authorization and approved workflow.

## One restrained follow-up; clear exits

The follow-up file is a draft and a manual decision record. First check whether the original was actually sent, whether a reply changes the situation, whether the source/context is still accurate, and whether the person declined, asked to stop or is the wrong recipient. An unchecked field is a hold, not a checked “no.”

Allow at most one follow-up under this preparation plan. Its job is to make one useful point or offer an easy exit, without guilt, pressure, invented urgency or a claim that silence means interest. Timing depends on the real context and owner review; this kit sets no schedule. If the person declines or asks to stop, record the minimum stop information and do not continue, switch channels or use another account to evade that choice. An optional acknowledgment may be drafted, but it is not automatically sent. After a further non-response, leave the thread.

## Discovery and a source-based mini-audit

Use the eight interview questions to learn the actual reader, decision, alternatives, product truth, outcome evidence, approval role and scope constraints. Ask permission for the proposed note/recording use; this kit records no calls. Budget and pricing remain questions, not assumptions. The existing package and regular-price tasks remain founder decisions.

Keep private interview notes in the approved private source ledger and reference them by source-note ID; do not upload a note merely to obtain a URL. The JSON source-record URL fields are for the permitted public surfaces used in the contact or mini-audit. For each mini-audit observation, name the exact surface and source unit inspected. Explain what the reader can observe, then label your interpretation and a proposed revision. Do not infer performance, demand, product reliability, the founder’s motives or the rest of an account from a screenshot or one post. A source can be incomplete; mark unreviewed surfaces. Give a useful recommendation only at the level its evidence supports. Public availability is not permission to republish media or private details.

For example, a hypothetical product note may name proposed flags and human review but omit the decision the reviewer retains. A bounded recommendation is to confirm and explain that decision. It is not a claim that the product saves time or that the founder has a marketing problem. The worked JSON preserves precisely that boundary.

## Plan handoff

| Existing task | This kit supplies | Still required |
|---|---|---|
| OUTSP-15 · qualification criteria | Separate fit/need/interest fields and explicit exclusions/unknowns | Founder-approved accept/reject criteria and method of checking them. |
| OUTSP-42 · 50–80-company ICP list | Source-verification headers | Real company/role checks, complete source set and manual review. No prospect rows are supplied here. |
| OUTSP-41 · warm circle | Relationship/context/permission record | The founders’ actual contacts and permissioned introduction choices. |
| OUTSP-31 · booking | Discovery and next-step questions | A verified booking destination and approved qualification flow. No link is invented. |
| OUTSP-43 · first messages | Individually sourced first-message and one-follow-up drafts | Actual recipient/source context, approved exact copy and channel. The plan also depends on OUTSP-37 publications, OUTSP-41, OUTSP-42 and OUTSP-35 website. This kit does not clear those dependencies. |
| OUTSP-44 · conversation learning | Objection/budget/response/next-step log and explicit counting definitions | Real conversations. Define “qualifying conversation” and “yes”; after ten qualifying conversations without an offer yes, review the offer and objections with the founders rather than sending more volume automatically. |

OUTSP-10/11 package and regular-price decisions remain undecided founder work. The kit does not choose Plan 1/2 content, prices, free work, access terms or an outbound policy. It does not claim to complete any existing launch task whose acceptance criteria require those decisions, a real dataset, published work or conversations.

## Validation

Run from this directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 validate.py .
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_validate.py
```

The validator checks the complete ten-file set, duplicate JSON keys, filename/schema/mode identity, JSON/CSV shape, required source/permission/stop fields, separate states, follow-up count/eligibility and a limited set of unsupported result-claim patterns. Typed result claims need source and measurement/review context. Common quantitative promises without a matching result record are rejected. These checks cannot prove that a source or approval is genuine, or detect every misleading statement in free prose. A person must still inspect the exact source, message, inference and permission state.

Header-only CSVs and empty templates may pass **template-completeness validation**. They do not pass real-prospect, conversation, offer or send-readiness review. The synthetic case must remain labelled synthetic, retain its `example.invalid` sources and claim no actual sending.

## Source and rights record

All prose, template structures, examples and validation code in this kit are original owned project work. The example company/product note and draft copy are synthetic; its locators are non-operational examples and were not fetched. No third-party messages, posts, media, personal contact records or paid-provider output are included.

The approved service position and writing boundaries come from the project’s [positioning](../../docs/APPROVED-POSITIONING.json), [writing architecture](../../docs/LINKEDIN-WRITING-ARCHITECTURE.md) and [source-bound method](../../skills/linkedin-reference-pattern-review/SKILL.md). Plan dependencies above are an original summary of the owner’s current task packet, not a copied private task export. `founder-content-writing` supplied author/buyer/evidence discipline; the email-sequence guide was consulted only for one-message/one-job and relevant context. Its automation, timing, length and sequence-size suggestions were not adopted as cold-outreach rules. No new provider, dependency, account connection or sending integration was installed or used.
