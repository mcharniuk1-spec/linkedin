# Manual update and analysis workflow

## Before the update

Read the repository `CURRENT-STATE.md`, `datasets/current/STATE.json` and `datasets/current/gaps.json`. Confirm the active run pointer and inspect only the relevant handoff. Use the current allowlisted source and query configuration; do not add authors, queries or sources as an implementation convenience. A source must have a permitted access route and an explicit identity/qualification path.

Run the repository's manual `update-run` command from its root:

```sh
python -m research.collector.cli update-run --config research/collector/config.json
```

Treat the returned analysis packet and data export as outputs to inspect. Check identity resolution, source publication date, deduplication, capture status, parser/provenance and unresolved gaps. A hold stays a hold. If the command reports an access stop, auth wall, challenge, or rate/access denial, stop requests to that source. Do not switch to cookies, login, proxies, CAPTCHA workarounds or a paid fallback.

Before using remote state, follow the restore instructions in docs/HYBRID-COLLECTOR.md. The encrypted artifact, checksum pointer and key must match. A missing or orphaned checkpoint is a recovery hold, never permission to start from an empty database.

Query the bounded writing graph with `graphify query "founder" --graph knowledge/writing/graph.json --budget 160` when the installed version supports that syntax; check `graphify --help` first. Verify retrieved relationships against the five original documents. A graph contains navigation relationships, not proven SEO or writing performance.

The older `research.pipeline` media/transcription/frame stages consume their own run schema. The new collector packet is not directly imported into those stages. Before a requested media stage, the supervising agent must create a source-bound compatible run or use the bounded media tools directly, preserving IDs/hashes and testing the bridge. Until that mapping exists, report the integration gap; do not present an old-run transcript as a new-record result.

## Requested local preparation

Collection does not imply media analysis. Only execute a downstream stage named in the user's request. Reuse the configured cached local Whisper model; do not download a model or call a hosted provider. Preserve original audio, source transcript and any machine transcript as separate artifacts. A known silent clip gets no speech transcript. Unknown audio is not silence.

Prepare frames with the repository's existing bounded frame tool only when requested. Keep timestamps and distinguish sampled frames from continuous video review. Inspect the actual images or video and the corresponding transcript/visible-text evidence before writing a media description. State clearly whether audio was heard and whether the full video was watched. A transcript, sampled frame or automated QA result does not establish those facts.

## Analysis and release

Use `docs/SERVICES-AND-WRITING.md`, `docs/CATEGORY-GUIDE.md`, `docs/SEARCH-AND-QUALIFICATION.md`, `docs/APPROVED-POSITIONING.json` and `docs/positioning-and-copy.md` as the writing-method sources. Keep the owner's agency positioning separate from any client's evidence and voice pack. Use one primary subject, the dominant editorial job and the observed format. Treat adaptation ideas as hypotheses, not guaranteed performance recipes.

Keep distinct: reference role-fit, post meaning/quality, observed interactions, measured change, prospect firmographics, opportunity hypothesis, expressed need and buying interest. Publication dates come from the source page. Missing, malformed, conflicting or future dates remain holds. Reaction counts do not establish impressions, reach, conversion or causality. Low posting activity does not establish a buyer need.

Preserve source IDs, hashes, locators, observation times, rights/use limits, claim links and exact original wording. Never replace original text/transcripts with normalized or translated versions. A new release or export must use the repository's existing QA, review and source-to-claim gates. If a gate is missing or fails, return the packet and precise gap instead of marking the result reviewed or ready.

## Output

Return the exact run/output locations, the requested stages completed, sample and coverage limits, source/identity holds, media review limits, and remaining gaps. Do not say a queue delivered a notice. Do not publish, schedule, message prospects, access a social account, spend money or activate recurring collection.
