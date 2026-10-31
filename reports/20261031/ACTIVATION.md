# Collection activation — 31 October 2026

The owner authorized collection every **30 minutes**. The workflow on `main` uses `*/30 * * * *` with `Europe/Sofia`, serialized state mutation and no overlapping collector jobs. GitHub can delay schedule starts. A job is not a full scan of every account.

## Verified live execution

| Actions run | Result | New posts | Duplicate rows skipped | Checkpoint |
|---|---|---:|---:|---:|
| [41192228402](https://github.com/mcharniuk1-spec/linkedin/actions/runs/41192228402) | Success | 8 | 0 | 1 |
| [41192415348](https://github.com/mcharniuk1-spec/linkedin/actions/runs/41192415348) | Success | 7 | 1 | 2 |
| [41192661122](https://github.com/mcharniuk1-spec/linkedin/actions/runs/41192661122) | Success, corrected restore path | 8 | 0 | 3 |

All three were bounded manual dispatches of the same scheduled workflow. Encrypted artifacts were uploaded; the public checksum pointer was advanced with compare-and-swap and readback. Owner-key authenticated local restores verified revisions 1, 2 and 3, with SQLite integrity checks. Revision 3 contains **23 new records**, no suspensions and no executed media/semantic analysis. Its discovery cursors are topic 2 / author 1, confirming alternation. The 23 records are private pending evidence, outside the frozen 279-post/61-author report.

Repository variable `COLLECTOR_ENABLED=true`. First-bootstrap gate is now `COLLECTOR_BOOTSTRAP_ALLOWED=false`. The encryption key was installed through secure stdin; no key, credentials, copied posts, transcripts, raw HTML or decrypted state is committed or uploaded as plaintext. The state branch contains a small public pointer, not the database.

## Defect caught and corrected

A live restore initially failed because GitHub artifact IDs were assumed chronological. The older artifact had a larger ID. Collection was temporarily disabled while this was corrected. Restore now checks validated timezone-aware artifact creation timestamps; missing/malformed ordering, ties or a genuinely newer orphan stop collection. Pointed state must exist, be unexpired and authenticate. The corrected local revision-2 restore and third live workflow/revision-3 restore passed. Synthetic tests also preserve newer-orphan, inverted-ID, malformed-time, missing-state and integrity rejection cases.

The final runtime source is commit `4d7899c94b55545e464598f084edf2d19651f4e5` (report packaging can follow). The full offline suite passed **240 tests**. [Hosted checks](https://github.com/mcharniuk1-spec/linkedin/actions/runs/41192651083) passed on that source. This is evidence of functional execution, not a production uptime or coverage benchmark.

## What runs autonomously

`Actions → restore encrypted state → one bounded discovery query → validate/deduplicate candidate URLs → public HTTP capture/parse → validate/deduplicate/store → seal/upload ciphertext → advance/read back checkpoint`.

One Exa topic query alternates with one rotating approved-author query, at most eight search results per query. With 48 approved author paths, one complete author-query rotation is about 48 hours at an uninterrupted 30-minute cadence. Search order is not an engagement rank, and an indexed URL may be older or delayed. New actors wait for qualification before supervised media collection. Known identities are seeded across the existing corpus; new records have durable aliases and content hashes. This schedule does not refresh old post counters, download media bytes, run Whisper or interpret images/videos.

## Limits and recovery

The free/keyless discovery route has no verified unlimited quota or coverage guarantee. Public access holds persist on authentication walls, challenges and 401/403/429/999; no runner/browser/proxy fallback clears them. Official LinkedIn post-reading API access remains disabled because the app grants only `r_verify`, `r_profile_basicinfo` and `w_member_social`.

Each run has bounded requests/runtime and at most 20 inserted records. The 24 MiB database limit now produces an explicit storage-capacity hold. Seven-day encrypted artifact retention keeps about 336 scheduled checkpoints below the bounded 1,000-artifact scan in normal operation. Artifacts are recovery checkpoints, not permanent archives. An outage beyond retention, an orphan, missing state or shared artifact-list overload requires recovery review; never bootstrap over it. A private restored revision-3 backup was retained locally.

For manual analysis, use `scripts/update-run-linkedin`, then inspect actual pending source/media, qualify authors, prepare ASR/frame evidence, review its quality and save source-bound conclusions. Keep generated interpretations distinct from facts. No automatic social publication, outreach, ads, provider spend or analysis service was activated.
