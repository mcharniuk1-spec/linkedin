# LinkedIn writing templates

These are original working templates for the [writing architecture](../../LINKEDIN-WRITING-ARCHITECTURE.md) and [P01–P14 pattern library](../PATTERN-LIBRARY.md). They contain no installed agent skill and do not operate a LinkedIn account.

## Use the templates

1. Copy [brief.yaml](brief.yaml) into the agreed working area. Define the reader's job, then choose one dominant pattern from [patterns.json](../patterns.json). Topic, editorial job, reader job, pattern, media and voice remain separate fields.
2. Assemble a bounded source packet and fill [claim-ledger.csv](claim-ledger.csv). Replace the clearly synthetic example row. Record what was actually accessed, not what a link title appears to promise.
3. Complete the suitable route in [story-skeleton.md](story-skeleton.md). Functions can share a paragraph or span several paragraphs. The skeleton is not a fixed paragraph or slide count.
4. Use [agent-task.md](agent-task.md) to delegate a defined part of the work. Assign non-overlapping output paths and give the reviewer the same evidence packet.
5. Complete [review.yaml](review.yaml). Resolve the evidence, source, voice and privacy gates before describing a draft as ready for release. An architecture may still be complete for review while a source-dependent passage remains on hold.

For a client post, use the client's reader and voice. Do not automatically copy Outspoken's agency audience into that brief. For agency copy, preserve the approved wording in `docs/APPROVED-POSITIONING.json`.

## What each file contributes

| File | Working output |
|---|---|
| brief.yaml | Reader decision, pattern selection, voice, media role, source needs and scope. |
| story-skeleton.md | Hook-to-payoff contract and a functional argument or confirmed founder-decision sequence. |
| claim-ledger.csv | Claim-level source, support, reasoning, limits and disposition. |
| review.yaml | Separate hard gates, editorial findings and a recorded handoff decision. |
| agent-task.md | Scoped inputs, outputs, author/editor responsibilities and source checks. |

Empty strings, nulls and pending statuses are deliberate placeholders. They do not record completed research or approval. Delete unused example items after copying. Paths inside filled-in templates must be repository-relative or approved source locators; keep private source bytes and machine paths out of a public export.

## Claim ledger conventions

The supplied CSV has one **synthetic demonstration row**. It is an illustrative workflow sentence, not a product capability, customer case or actual past event.

Use a claim type that matches the sentence: `observation`, `attributed_statement`, `inference`, `recommendation`, `forecast`, `personal_recollection`, `hypothetical_example` or `offer_or_capability`. A factual claim embedded inside an example needs its own evidence row.

`source_access` records the material actually read: `full`, `excerpt`, `abstract_only`, `metadata_only`, `not_accessed` or `not_applicable`. `support_status` records `supports`, `partly_supports`, `does_not_support`, `unverified` or `not_applicable`. An accessible source can still fail to support a claim.

Keep the source locator and the relevant passage, table, record or timecode locator precise. Do not paste full third-party posts or private interviews into the ledger. Record permission and quotation checks separately. For numbers, retain the population, period, numerator, denominator, unit and comparison basis that give the number meaning.

`disposition` can be `keep`, `qualify`, `attribute`, `replace`, `remove` or `hold`. Neither a populated row nor an agent's agreement proves the statement. A second reviewer should inspect the underlying source.

## Source and story boundaries

Existing corpus assessments can suggest a question or structure. The [coverage audit](../corpus-audit/README.md) explains why they cannot be presented as new full-source close reading. Do not infer a personal experience from a `tell_story` label.

P02 and P03 need author-confirmed experience. If the interview material is absent, identify the gap and select a suitable explanation, checklist, working question or observation. Optional humor may improve recognition; it must not manufacture a client, quotation or personal memory. P14 can end on a payoff without an argument or sales CTA.

This template package ends at editorial handoff. Social posting, scheduling, outreach, ads and any new source acquisition require their own task scope and actual permissions.
