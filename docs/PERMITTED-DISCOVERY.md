# Free-first discovery and owner-provided analytics

The LinkedIn public source remains suspended on its recorded security challenge. Do not clear the suspension, change transports, use cookies or another account, or route around the challenge. Discovery uses search indexes and independent sources; it never fetches LinkedIn while held. GitHub Actions still exits nonzero for a held source, seals the state, and reports the hold; a discovery result is not a LinkedIn post or engagement measurement. The existing 30-minute schedule is best effort; missed or delayed executions are unknown unless separately verified in Actions history.

## Data paths

1. Exa keyless MCP: at most one query per run, alternating topics and approved account seeds. The collector queues new, canonical LinkedIn publication links with `permission_state=unverified` and `review_status=pending`. Search rank and snippets do not establish publication date, engagement or popularity. Exa quota and terms can change. An access/quota denial persists a hold for Exa only.
2. Hacker News official API: at most 20 top-story identifiers and five details per run; its scores and discussion descendants belong to Hacker News. Hugging Face blog RSS: at most 20 feed entries. These are external topic leads, not LinkedIn posts. Sources are exact-URL allowlisted. Source metadata reuse is unverified; inspect applicable terms before further use. Every source stops on a denial, while independent sources may continue.
3. Owner-provided LinkedIn CSV/XLSX analytics: explicit owned/consented account, purpose, consent reference, expiry, retention, source hash and observation time. This manual route uses a separate private SQLite database, never the public research checkpoint. Actual LinkedIn export formats have not been tested; unsupported schemas and legacy `.xls` are rejected. See [member exports](https://www.linkedin.com/help/linkedin/answer/a701208) and [Page exports](https://www.linkedin.com/help/linkedin/answer/a551206). Ask the owner to supply the export through an agreed private channel.
4. Official API: **disabled and fail-closed** in the collection controller because its historical adapter would write into the research store. Enabling the config does not enable API collection. Production needs a separate access-controlled API store, exact granted scopes and Page role, endpoint-specific access checks, consent withdrawal, applicable agreement and data-type-specific automated expiry and deletion. [Community Management API access](https://learn.microsoft.com/en-us/linkedin/marketing/increasing-access); [storage requirements](https://learn.microsoft.com/en-us/linkedin/marketing/data-storage-requirements). Owner-provided exports must not be represented as API data. No universal competitor search is implied.

## Owner export example

Run locally in a private environment. Replace placeholders yourself; never commit exports, snapshots, credentials or the private store. Account and consent identifiers are locally hashed, not proof of consent. Keep the consent record and source file in the owner's approved private system. Choose a documented retention period for the agreed purpose.

```python
from datetime import datetime, timezone
from research.collector.consented_exports import ConsentedStore
s = ConsentedStore('/absolute/private/dedicated-directory')
s.grant('account-identifier', consent_reference='consent-record-reference',
        purpose='consented_account_analytics',
        expires_at=datetime(2027, 1, 1, tzinfo=timezone.utc), retention_days=30)
s.import_file('account-identifier', '/absolute/private/export.csv',
              observed_at=datetime.now(timezone.utc), granularity='post', date_format='iso')
s.purge_expired()
s.close()
```

Use `granularity='daily_aggregate'` for aggregate exports; aggregates are never invented as posts. For an XLSX with multiple sheets supply `sheet_name`; supported date modes are `iso`, `dmy`, `mdy`, `excel1900`. Parser explicitly requires known headers and post IDs/URLs for post rows. Record the time the export was produced; do not substitute an upload time if unknown. `s.revoke('account-identifier')` deletes stored rows and aliases. Purge is called on import/read but must also be scheduled or run manually to meet a deadline when the store is idle. Source files, exported snapshots, backups and other copies are not automatically deleted: the operator must track and delete them. SQLite file permissions are not encryption; use an encrypted local volume and access controls. Do not publish or upload this database.

## Queues and local viewer

Add a candidate locally, for example:

```sh
python -m research.collector.cli queue-candidate --category target_company --url https://www.linkedin.com/company/example --source-id manual-research --topic 'B2B AI SaaS'
python -m research.collector.viewer_projection --config research/collector/config.json --output /absolute/private/snapshot.json
python -m http.server 6077 --bind 127.0.0.1
```

Open `http://127.0.0.1:6077/research/permitted_viewer/` and select the snapshot. Add `--owner-store /absolute/private/dedicated-directory --account-id account-identifier` to include separately consented export observations. The browser reads the file locally; do not serve private snapshots. The snapshot is another sensitive copy that is not tied to later retention or revocation: delete it promptly and include it in your deletion procedure. The projection keeps authorized data, reference candidates, external topic signals and target companies in separate views. Media, transcripts and human visual interpretation remain supervised and require provenance and rights review; this discovery cycle does not fetch media.

New publications and accounts are Sofia-day counts from the existing LinkedIn record store; the 100/10 numbers are targets, not guarantees. The older corpus and owner-export rows are not automatically combined. Candidate queues are not collected posts. A change needs two compatible same-source/parser observations at least six hours apart and a verified publication timestamp; an increase alone is measured change, not causation or proof of a trend. Unknown counters remain unknown. Export dates often have only day precision; they cannot establish a reliable trend timestamp. Manual prospect fit, inferred content opportunity, expressed need, and buying intent stay separate.

## Operational limits

The encrypted checkpoint retains the legacy store, new candidate metadata, and external observations, with a hard 24 MiB capacity hold and seven-day artifact retention. The source code does not yet bound retained Exa raw discovery objects; external observations currently retain 30 days and items 90 days. At 30-minute cadence, growth can reach the capacity hold. Monitor real checkpoint size and implement a tested, source-aware retention/compaction policy before promising indefinite unattended operation. The system does not measure provider-side quota, true missed schedules, or public LinkedIn reach and impressions without authorized observations. Paid Metricool is a fallback only; LinkedIn connection is not included in its free plan. No purchase is authorized.
