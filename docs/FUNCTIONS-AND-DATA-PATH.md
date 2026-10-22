> Dated method record from22October2026. Source evidence bytes remain local; use the current dataset state for later observations and gaps.

# Worker blocks and data path

The current executable is `pipeline/cycle.py` v0.5.0. Each CLI command is a bounded ordinary process. It does not require an LLM for extraction. The source-bound meaning/media review is a supervisor stage. A worker role name or event file is not an unattended agent service.

| Block | Implemented function / command | Input → output | Autonomous boundary |
|---|---|---|---|
| Discover topic posts | `Cycle.exa`, `discover`, `exposed_links`, `prioritize` / `discover` | Configured problem/author queries + cached pages → raw search receipt, `operations/discovery*.json`, URL queue | Installed mcporter calls keyless Exa. Rate/quota failures stop search. Same-author links are exposed page links, not full history. Native LinkedIn filters and account/company probes are seed routes, not an authenticated collector. |
| Normalize and deduplicate | `normalizer.post_context`, `parse_post`, `Cycle.accept`, `keys` | Exact target page → author, post text/date/media/counters and identity keys | Main target actor/text/counters only. Exact activity/share/canonical/text identity checked against corpus. Real similar publications retain identities; semantic variant groups prevent extra pattern/comparison weight. |
| Capture and observe | `get`, `waves`, `capture`, `store_capture` / `capture`, `refresh`, `resume` | Qualified/queued public URLs → content-hash raw HTML + immutable captures + request receipts | HTTPS public LinkedIn only,2 workers, size/redirect/time caps, auth/rate/challenge and unsupported-layout stops, failed/blocked queues and overlap lock. `refresh` checks latest actual observation and6h minimum before requesting. |
| Import old evidence | `import_baseline` | Explicit original NDJSON + snapshot allowlist → current operational captures | Re-parses the same bytes under the current parser hash while retaining original observation identity/time/raw hash and derivative provenance. No new observation or request. |
| Gate reference media | `approved`, `media_posts`, `media` | New posts or explicit known prior IDs + approved author paths → media tasks or account-qualification holds | A supervisor first verifies public B2B role/topic fit.15 holds remain. Prior IDs cannot fabricate publication rows. |
| Acquire photos/video/doc previews | `media` | Exposed licdn URL/renditions → `media/objects/<sha>.<ext>`, `data/media-manifest.json`, `data/documents.json` | Lowest exposed video rendition under80MB; other files under12MB; only exposed document cover pages, explicitly incomplete document. SHA-bound source/cached files, no auth/private download. Exposed captions/posters separate from video bytes. |
| Transcribe | `transcribe` → `asr_worker.py` | Acquired video and captions → per-asset original JSON + `transcripts/index.json` | Original platform captions first; cached local Whisper fallback when needed, downloads disabled. Silent video remains explicit. v5's three new videos had exposed captions; no new Whisper decode was needed. Prior Whisper outputs/two alternative decodes remain distinct. |
| Mechanical quality | `transcript_qa` → `transcript_qa.py` | Current/inherited exact video/transcript evidence → `data/transcript-qa.json` | Checks timing, repetition, compression and reconciliation. Does not certify accuracy. Flags close only with a truthful exact-source audio adjudication ledger.10 still open. |
| Prepare visual evidence | `prepare` → `prepare_evidence.py` | Actual video/ffprobe metadata → timestamped frames/contact sheets + source-bound preparation record | FFmpeg/ffprobe; up to96 frames/video. A frame sheet does not establish events between timestamps or continuous watching. |
| Interpret meaning/media | Native supervisor + `operations/integrate_media_semantics.py` | Full post text and actual stills/frame sheets/captions → source-bound media reviews and `analysis/post-interpretations.json` | Semantic analysis is outside the ordinary extraction loop. Must inspect actual inputs and retain evidence scope, caveats and hypotheses. No verified ComfyUI backend. |
| Measure | `qualify`, `snapshots`; `performance.py` during release | Immutable snapshots and interpretation/variant state → velocity/cohort records + descriptive performance assessments | Same parser version/hash and >=6h for measured change. Latest snapshot counters, n>=8 same-author/format/age/language comparisons; selected sample and confounding explicit. No search rank/global popularity, reach or sales inference. |
| Queue supervisor work | `queue`, `event` | Holds, failed/missing assets, transcripts and reviews → SQLite events + `operations/supervisor-event.json`, review queue | Durable local event only. No actual wake adapter or schedule active. Account holds and QA flags remain visible. |
| Validate/export/view | `release.py` + `viewer-template.html` | Prior joined release + current explicit inputs → analytical SQLite, dataset JSON, CSV and static viewer | Source/digest/schema/coverage/identity/payload checks block a failed release. Dated inputs inherit only when no current replacement file exists. Explicit empty current input stays authoritative. |

## Where records live

```text
public locator + search receipt
  → raw/objects/<HTML SHA>.html
  → operations/cycle.sqlite: posts / captures / requests / assets / events
  → snapshots.json: actual observed time + raw hash + exact normalizer provenance
  → media/objects/<media SHA>.<ext> and per-asset manifest
  → transcripts/<record>.json + separate alternatives + mechanical QA
  → analysis/<review>.json and fulltext interpretations (source/asset/text hashes)
  → release.py validation
  → data/linkedin.sqlite (18 analytical tables) + dataset.json + qualification-table.csv
  → index.html (embedded checked data; relative sibling-run media URLs)
```

The operational database and analytical database have separate jobs. The analytical store is rebuilt from versioned evidence; it is not an unlogged mutable truth source. Observation time, publication time, normalization time and semantic review time remain distinct. A repaired parser is recorded as a derivative of the old observation.

The prospect lane uses lightweight public company/official-source review → firmographic evidence/holds →20 company summaries in the Target audience tab. It does not enter the reference media/post/employee pipeline.

## Operating state

Current extraction/processing: complete for the approved v5 media tasks. Current queue:15 account evidence holds and10 audio-review flags. Next genuine observation gate: v3 after14:40 UTC on22 October2026. No current trend winner is established. Nothing is scheduled. To support unattended cycles later, first obtain the separate schedule/wake authorization, then test real event delivery/acknowledgement, no overlap, stop/resume and a source-bound supervisor review. Merely running the worker on cron would not complete the semantic stage.
