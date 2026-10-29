# Hybrid LinkedIn collector

Status: source and local synthetic tests are implemented in this run. This document describes the current v7 code and the checked-in Actions workflow. It does not prove that GitHub Actions is enabled, that OAuth is configured, that any source is reachable, or that a scheduled run has completed.

## Current path

The active collector is `research.collector`, separate from the older `research.pipeline` v5 cycle. The current route is:

1. **Source policy and discovery.** `research/collector/config.json` supplies adapter, exact allowed hosts, GET permission, permission basis, rate/cap settings and source URLs. `discovery.discover()` probes the configured Exa MCP endpoint, reads its current tool schema, and uses `web_search_exa` only to seed LinkedIn post permalinks. Search rank, snippets and indexed dates are not source truth. Results are restricted to LinkedIn post/activity URLs and checked against existing aliases.
2. **Fetch.** `cli.collect()` acquires the local SQLite lock, seeds identity aliases, and invokes the configured `Transport.fetch()` through `TimedTransport`. The checked-in default is pooled HTTPX (`default_transport: "httpx"`), selected after two same-fixture comparisons; urllib remains the comparator. Both transports apply source host/method/permission policy, pacing, concurrency, timeout and byte limits, redirect and retry limits, and persistent access stops. A 401/403/429/999 or challenge suspends the access group. An adapter does not fall back to another transport or source method after a denial.
3. **Parse and normalize.** `StaticHTTPAdapter` sends LinkedIn post HTML through `research.pipeline.normalizer.canonical`, `parse_post` and `validate_record`. Generic static HTML requires an explicit text selector. `FeedAdapter` parses bounded RSS/Atom after rejecting DTD/entity declarations. `GenericAPIAdapter` accepts only configured public JSON paths and pagination. `ReadonlyLinkedInAPIAdapter` is a separate, disabled-by-default, read-only authorized API adapter. Scrapy and Playwright are optional, separately gated methods; see below.
4. **Validate, deduplicate and commit.** `Store.ingest()` checks the record contract, source URL, permissions, content hash and timezone-aware collection timestamp. It deduplicates by seeded/current URL and external-ID aliases, plus normalized text when eligible. LinkedIn identity aliases include activity/share URNs and canonical URL/text hash. `on_record` commits each emitted row immediately. The CLI processes static candidate URLs one at a time, so an earlier success remains in SQLite if a later URL is denied. The store is a one-writer SQLite database with a non-overlap lock, bounded size, restrictive local permissions and durable access suspensions.
5. **Local evidence and manual packet.** Raw HTML/XML/JSON bytes are saved by content hash under the local collector workspace and compressed into SQLite's `raw_objects`; normalized observations retain source locators and hashes. API media references are metadata only. `update-run` exports pending records and raw source material to a private local manual folder and writes `insights.csv` plus `analysis-packet.json`, including a small deterministic writing graph. These are review inputs, not an automatically completed analysis or public release.

The workflow's `collect` step does **not** run refresh, media-byte acquisition, ASR, frame extraction, visual/audio analysis, prospect qualification, or publication. Media references and captured raw HTML remain available for a later explicitly requested, local review stage. The packet calls out that actual source inspection and any later media work remain human-reviewed. A public post's author description/name/URL is an observation about that post actor only; it does not establish a complete employee, account, or profile history. Prospect qualification stays limited to reviewed public evidence and description-level facts.

## Legacy boundary

`research/pipeline/cycle.py`, `research/pipeline/mcporter.json` and older `research/README.md` describe the previous sequential urllib / mcporter Exa / media-download / Whisper and transcript-QA route. That code remains in the repository for compatibility and historical use; it is not the v7 Actions entry point. The v7 collector uses its own transport/adapters, direct schema-aware Exa MCP discovery, bounded SQLite store and separate `collect`/`update-run` commands. In particular, old `cycle` or `refresh` documentation must not be read as permission or behavior of the current scheduled workflow.

## Adapter and storage limits

- HTTPX is the config default after two reviewed policy-class loopback runs. Both transports captured20/20 exact fixture IDs; HTTPX averaged about1.04ms versus4.61–4.63ms for urllib. A benchmark fixture does not measure LinkedIn coverage or service performance.
- Playwright requires an explicit `js_required` source, `permitted_js_rendering` method, collection/public-read permission, non-LinkedIn host and an already installed supported Chrome channel. It blocks media/image/font subrequests and caps requests; it does not install a browser or bypass access controls.
- Scrapy requires explicit `high_volume`, `permitted_scrapy_crawl`, an explicit text selector, a bounded URL set and non-LinkedIn source. Its optional asynchronous runner delegates network requests to the approved transport so the same host, stop, rate and size policy applies. It does not retry through another crawler after denial. Neither Scrapy nor Playwright is the default route.
- PostgreSQL and Redis are deferred. The present workload and single-writer semantics use SQLite plus an encrypted state artifact/checkpoint. Revisit only if measured volume or concurrent-writer requirements exceed those bounds.

## Commands and offline checks

Run from the repository root with the existing supported Python environment and locked dependencies already available. These commands do not install dependencies.

```sh
python -m research.collector.cli status --config research/collector/config.json
python -m research.collector.cli collect --config research/collector/config.json
python -m research.collector.cli update-run --config research/collector/config.json
python -m research.collector.cli oauth-preflight --config research/collector/config.json
python -m unittest discover -s research/tests -p 'test_hybrid*.py' -v
python -m research.collector.benchmark --output research/verification/hybrid-transport-benchmark.json
```

`status` is a local zero-outbound state check. `collect` can make discovery/source requests and is not an offline test. `update-run` only creates the private manual packet; it does not invoke an LLM. The benchmark uses frozen loopback fixtures and must be run before changing the default transport. For transport parity, require all 20 fixture IDs exactly once, no errors, and the JavaScript capability result to stay outside the static latency denominator. Compare `urllib-policy` with `httpx-policy` from the same policy classes, and report nearest-rank p95, mean latency, wall time, CPU and sampled peak RSS with source hashes. `httpx-pooled` is a diagnostic, not adoption evidence. Repeat comparable runs before making an adoption decision; fixture latency alone cannot predict public-source performance. The focused hybrid suite is the relevant synthetic regression set; it should also prove host/method/permission rejection, no cookies/proxies or cross-host redirects, byte/time/rate/concurrency caps, retry and Retry-After behavior, persistent stops, parser/identity parity, and record commit before later-page denial. The older broad README test totals are not evidence for v7 behavior.

If a source is suspended, stop collection. Inspect the local hold and source evidence, correct only a verified configuration/source issue, then use the explicit source-backed resume command:

```sh
python -m research.collector.cli resume-source --config research/collector/config.json --access-group linkedin-public --reason "<source-backed reason for clearing this hold>"
```

Do not clear 401/403/429/999, challenge or repeated-layout holds by waiting, switching adapters, or trying a second method. Resolve authorization or source conditions first. For capacity, parse, schema, OAuth, checkpoint, missing-state or orphan-artifact holds, preserve current state and investigate; do not delete state or bootstrap over it. State restore accepts an empty destination only. A missing checkpoint is a first-run bootstrap only when explicitly requested and no artifacts exist; an artifact newer than the pointer is an orphan and requires recovery review.

The encrypted-state utility is used by the workflow; it is not a routine local operator command. For reference, the workflow calls `python -m research.collector.ci_state restore`, `seal` and `publish --artifact-id …`. Do not run `publish` manually without a verified GitHub checkpoint context and uploaded encrypted artifact.

## Schedule and GitHub state

`.github/workflows/linkedin-collect.yml` is present in source. It declares two daily schedules at 12:00 and 20:00 with the IANA timezone `Europe/Sofia`, plus a manually dispatched first-bootstrap input. A repository variable `COLLECTOR_ENABLED == 'true'` and the default `main` ref gate collection. The job serializes runs, restores an authenticated encrypted state, collects, seals state even after a collection failure when restore succeeded, uploads only ciphertext, and advances a small public-safe `collector-state` branch checkpoint with compare-and-swap and readback. The checkpoint stores checksums/revision/artifact identifiers, not raw posts or tokens. Restore fails closed on missing/orphaned state, bad hashes/keys, nonempty targets or invalid SQLite; it retains two ciphertext checkpoints. No raw records, transcripts, media or plaintext token vault should be uploaded or committed.

The workflow file is not proof of activation. At this review, `gh` authentication returned HTTP 401; the connected GitHub repository read showed admin access, but the available connector did not expose secret-setting, and `COLLECTOR_ENABLED`, Actions secrets/variables, default-branch state and a successful run have not been verified. User login/configuration is pending. GitHub's schedule support uses an IANA timezone, but scheduled events can be delayed under load; the default branch and repository activity also affect delivery. See [workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax) and [scheduled event behavior](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows).

## Known gaps

- A protected credential-file preflight confirmed configuration presence without printing values. No OAuth consent or LinkedIn API resource access was exercised.
- The config's public HTTP source has an empty URL list. A bounded live Exa query returned4new LinkedIn candidate permalinks. No source post was fetched in that discovery probe; this proves query reachability only.
- A successful OAuth token exchange would still not prove actor/resource access. The official API source is disabled and has no configured actors/resources/scopes.
- No Actions schedule activation or live checkpoint roundtrip has been verified. Local benchmark adoption evidence is in docs/HYBRID-AUDIT-AND-PLAN.md; fixture performance is not production performance.
- These adapters preserve observations and locators. They do not establish source rights for reuse, publication dates where the source is ambiguous, completeness of author profiles, buyer intent, popularity, or market coverage.

## First activation and manual handoff

The repository needs a valid authenticated GitHub CLI with `repo,workflow` access (or equivalent fine-grained permissions). Keep `COLLECTOR_STATE_KEY` in Actions Secrets and retain its protected owner copy. Set `COLLECTOR_BOOTSTRAP_ALLOWED=true` only for a reviewed first activation, then set `COLLECTOR_ENABLED=true` and dispatch `linkedin-collect.yml` with `bootstrap=true`. A bootstrap requires an explicit workflow dispatch, no artifact history (including expired artifacts), no existing state branch and no local database. After a successful encrypted upload, checkpoint CAS/readback and restore verification, set `COLLECTOR_BOOTSTRAP_ALLOWED=false`. Never use bootstrap to repair lost state. If a prior artifact is orphaned, recover the newest authentic state and reconcile the pointer under operator review; do not collect until recovery passes.

A collection source hold returns a failure exit status so GitHub can expose it. Successful earlier records and the persistent stop are still sealed/uploaded/checkpointed by the workflow's `always()` path. A workflow timeout or missing-state failure is a gap requiring inspection. Do not call a workflow file or a green skipped job an active collector.

To analyze remote pending records, inject the owner-held key through a private key file, authenticate `gh`, and run `python -m research.collector.ci_state restore --repository mcharniuk1-spec/linkedin --state-dir research/work/collector --context research/work/manual-context.json` into an empty state directory. Then run `scripts/update-run-linkedin` (or the Python `update-run` CLI). Keep custom outputs within the private state subtree. The output is `records.ndjson`, exact raw objects, `analysis-packet.json` and an unfilled `insights.csv`. Legacy media/ASR/frame commands use a separate schema; a tested source-ID/hash bridge is still required before they consume these new collector records. The skill describes this integration gap and the required actual-source review.

## Access detector correction and live check —29 October 2026

The initial detector incorrectly treated generic login/CAPTCHA scripts as a challenge. It rejected all four sampled cached public pages. The corrected detector checks actual gate paths, visible gate headings and CAPTCHA widgets/forms, with synthetic positive/negative tests. HTTP401/403/429/999 stop behavior is unchanged. Future stop responses are retained privately by hash in `access_evidence` and included in the manual packet; source text and response bodies never enter logs.

After the source-backed correction, one bounded authorized public post capture succeeded: one post, one actor metadata entry, a verified source date, available counters and one media reference. A repeated run fetched zero source pages and inserted zero records. The public HTTP source is enabled again. This proves one source path, not all LinkedIn pages or sustained coverage. The API source remains disabled for missing read entitlement. Bootstrap identities now include288publications and62observed actor metadata entries; the released279post analytical dataset is preserved.
