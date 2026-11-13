# Select and adapt one client tool

Use the client's actual task to select a module. A free follow-up may include a brief strategy and/or one bounded adaptation. It does not include the full catalog or a bespoke application by default.

## Module menu

| ID and module | Client job | Input | Inspectable output |
|---|---|---|---|
| T00 Evidence kit | Organize supportable claims | Approved facts, sources, voice and gaps | Source-linked fact and gap register |
| T01 Buyer/message brief | Choose relevant companies, buyers and message | Offer, customer evidence, exclusions and market | Reviewed ICP, fit criteria and message brief |
| T02 Profile studio | Explain the person or business clearly | Role, approved proof, buyer and offer | Headline/About options, Featured direction and rationale |
| T03 Decision-to-post workbench | Turn useful knowledge into a post | Buyer question, source, author stance and action | Original draft, structure and claim checks |
| T04 Visual/story planner | Make one idea easier to understand | Approved copy, design requirements and cleared assets | Layout brief, visual copy and alt text, or reviewed editable graphic if scoped |
| T05 Profile/landing review | Find relevant message and usability gaps | Public page URLs, target buyer and review question | Evidence-linked findings and prioritized recommendations |
| T06 Search planner | Make a repeatable manual search | Approved ICP, role, geography and exclusions | Search strings, filters and native-search checklist |
| T07 Research CSV workbench | Keep permitted research usable | Authorized records and deduplication keys | Clean file with source/date, fit, unknowns and review queue |
| T08 Owned-media intake | Reuse permitted client material | Authorized files or calls, rights and source metadata | Original preserved, separate reviewed notes and transcript QA state |
| T09 Email finding/verification, proposed | Identify a suitable business contact route | Approved company/person criteria and permitted sources | Source-linked candidate, verification date and hold status |
| T10 Campaign/reply planner, proposed | Plan relevant outreach and handoff | Approved audience, message, useful resource and stop rules | Sequence plan, reply categories and owner handoff |
| T11 Ads brief, proposed | Decide whether paid distribution fits | Objective, audience, creative, landing route and budget | Test brief, measurement plan and explicit media-cost line |

T09–T11 are proposed modules, not claims of tested software. No module automatically scrapes LinkedIn, sends messages or connects to a client account.

## Fill the adaptation brief

- **Client task:** [One job the client needs to complete]
- **Evidence for the need:** [Call fact, source and date]
- **Selected module:** [One ID]
- **User and operator:** [Who will use it and who maintains it]
- **Inputs:** [Required fields, format, source and permissions]
- **Configurable fields:** [Client-specific buyer, language, geography, tone, criteria, sources, limits or review role]
- **Output:** [Exact fields, file or response shape]
- **Worked example:** [Permitted synthetic or client-approved example, clearly labeled]
- **Acceptance check:** [A realistic task, expected output and reviewer]
- **Fallback:** [Manual steps if a tool or connection is unavailable]
- **Data handling:** [Owner, storage, retention, export and deletion route]
- **Costs and support:** [Tool payer, recurring charges, setup and correction/support boundary]

## Delivery format options

Choose the simplest format that fits the task and client environment.

| Format | Suitable when | Acceptance evidence | Limit |
|---|---|---|---|
| Agent prompt | The client already has an approved assistant and a human reviewer | Run an agreed sample and compare required fields and failure handling | Prompt text is not an installed or connected agent |
| JSON | Another verified workflow can consume a stable schema | Validate required fields, types, missing values and a sample | A valid file does not prove runtime compatibility |
| Sheet | A person needs to filter, review or update records | Client completes a sample row and export using permitted data | Sheet is not an automated research connection |
| Verified MCP/API configuration | A specific interface and client permission are confirmed | Test authorized input/output, errors, access limits and fallback in that environment | Do not offer until endpoint, permissions, terms, cost and test are verified |

## Acceptance and boundaries

A client accepts an adaptation when the named operator can complete the intended task in the agreed environment and the result meets the written checks. Record the sample, reviewer, result and open gaps. If an integration cannot be verified, deliver the agreed manual format or hold the integration promise for a later scope decision.

Do not include private customer records in a reusable example without permission. Do not convert uncertain facts into claims. Keep contact research, email finding, sending and ads as separate capabilities with separate approval, ownership and cost. A free adaptation is bounded by one selected useful task and its documented acceptance check.

## Working stack behind the modules

Use a shared document and Sheet/board for intake, evidence, review and the contact log. Use native LinkedIn for profile work, preview and permitted manual research. Use the owned design system and editable SVG/native exports for graphics. Use Figma only with the verified client identity and exact authority. Metricool or the official Posts API can support approved publishing when the actual account and applicable access pass a test.

Monid is an optional company discovery/enrichment route, not the only way to research prospects. Hunter is an optional business email finder/verifier and connected-mailbox sequence route. They are not tested client connections here. Keep sending separate from finding an address. Prefer the client’s existing authenticated business mailbox before buying another seat. Campaign Manager, Ad Library and a scoped conversion path cover an optional ads branch, not the default free output.

The [26-function tool matrix](../20261112-service-tool-architecture/tool-stack.json), [agency/client responsibilities and dated vendor observations](../20261112-service-tool-architecture/TOOL-SELECTION.md), [client-module schema](../20261112-service-tool-architecture/client-tools.json) and [cost ledger](../20261112-service-tool-architecture/pricing-ledger.csv) preserve the detailed function, input/output, payer, access, cost and fallback fields. Those dated prices need rechecking at selection. No paid run or purchase took place in this revision.

The [Waalaxy first review](../20261111-client-tools-first-review/README.md) remains an inspiration inventory. Hook, header and body functions belong inside T03. Competitor/profile analysis belongs inside T01/T05. A new label is not a new tool implementation.
