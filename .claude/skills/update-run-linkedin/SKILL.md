---
name: update-run-linkedin
description: Manually update the LinkedIn research run and prepare a bounded analysis packet when the user asks to refresh or review the dataset. Never start recurring collection.
---

# Update a LinkedIn research run

Use this skill only for an owner-requested manual LinkedIn data update or follow-up analysis. It does not grant authority for account access, publication, outreach, paid providers, recurring collection or a new source route.

Locate the LinkedIn repository from the current workspace or an owner-supplied path; do not search the device. Read its AGENTS.md and docs/HYBRID-COLLECTOR.md. Apply this skill only inside this LinkedIn project. If the state is in GitHub Actions, restore its verified encrypted checkpoint to an empty private directory with the owner-held state key and authenticated GitHub access before preparing analysis. Do not overwrite an existing local database. The update command exports existing pending observations; it does not fetch new posts. Run the separate `collect` command only when the user also requests collection and the current source permissions allow it.

For a requested run update, inspect the repository's current state and gaps, then invoke the bounded manual update command from the repository root:

```sh
python -m research.collector.cli update-run --config research/collector/config.json
```

Read the command's actual result and named output paths. Report what it captured, skipped, held or could not reach. A collection receipt or queued item is not proof of review, analysis or a delivered notification. Do not infer a successful update from an existing export.

Collection and analysis are separate. The update command must not run refresh, transcription, frame extraction, or image, video, audio or text supervision. Run a local cached transcription, frame preparation or transcript QA stage only when the user requests that stage. Review actual media and source-bound evidence before making descriptive claims; label sampled frames as samples, and do not claim continuous watching or listening unless that occurred.

The returned `insights.csv` is an unfilled analysis template. Legacy media commands use a separate run schema and are not yet wired to this collector packet. Model-cache and executable-presence flags are hints, not proof of an operational analysis runtime.

Use the source and review route in [the workflow reference](references/workflow.md). Preserve source identities, original text and transcripts, rights and uncertainty. Keep reference-account fit, post meaning, observed performance, prospect fit, opportunity hypothesis, expressed need and buying interest as separate fields. Do not infer reach, causality or purchase intent from reactions or low activity.

Only prepare an existing reviewed release or derived export when requested and when its source, QA and review gates pass. Otherwise return the bounded analysis packet, its gaps and the next concrete review step. Never publish, schedule, message, spend, activate a recurring trigger, or claim the skill is installed without its separate installer receipt.
