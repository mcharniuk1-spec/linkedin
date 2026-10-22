# Portable LinkedIn research runtime

This is the public, portable copy of the local v0.5.0 research implementation. It contains the collector, parser, immutable observations, media/transcript preparation, quality checks, release builder and offline tests. The public repository's derived data viewer is separate from this raw-evidence release builder.

The sample config starts with **no discovery queries, no approved authors, no corpus and no schedule**. Nothing logs in, imports cookies, installs a dependency, downloads a model or calls a paid provider automatically. Use only authorized public sources. Access stops and blocked URLs are retained; do not bypass an authentication wall or challenge.

## Offline verification

From the repository root, use an existing Python 3.9+ environment on macOS or Linux with BeautifulSoup installed. Windows execution is not verified; the overlap lock uses POSIX `fcntl`:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -W ignore::ResourceWarning -m unittest discover -s research/tests
```

Node.js is used for deterministic viewer tests. Pillow, FFmpeg and Whisper are not needed for the offline suite; calls are mocked or use explicitly synthetic byte fixtures. Observed local verification used Python 3.9.6, BeautifulSoup 4.15.0 and an existing Node.js binary. Optional frame-sheet preparation used the existing Pillow 11.3.0 installation. The requirements files declare dependencies; they do not install them.

`tests/fixtures/cycle/` contains original invented legacy and guest-layout HTML. `tests/fixtures/release/` contains invented Alice/Bob-style records and dummy media bytes. None is an actual LinkedIn post or playable reference video. Regenerate them only when deliberately updating fixture data:

```sh
python3 research/tests/fixtures/cycle/generate.py
python3 research/tests/fixtures/release/_generate.py
```

The same 147 behavioral tests from the local implementation are retained with synthetic inputs; eight additional tests cover portable config paths, environment overrides, tool discovery and empty default operation. This does **not** establish parity with every live LinkedIn layout or the private reference corpus.

## Local operation

All paths in `pipeline/config.json` resolve relative to the config file. The default work directory is `research/work/`. Run a zero-network status check:

```sh
python3 research/pipeline/cycle.py --config research/pipeline/config.json status
```

For a real run, create a separate dated work folder and a task-specific config. Supply an explicit allowlist of prior corpus NDJSON and snapshot files. Each NDJSON record's relative `source.raw_path` resolves from its owning run folder (`data/..`). Snapshot `raw_path` values resolve the same way. Preserve original observations and hashes; re-parsing old bytes is not a new observation.

The sequential command blocks are:

```text
import-baseline → due-only refresh or bounded discovery/capture
→ approved-source media → transcribe → prepare → transcript-qa
→ supervisor content/media review → qualify → queue → release
```

Run only the authorized blocks. Source acquisition and local preparation are ordinary bounded processes; business relevance and semantic/media judgments require a supervisor. An event file is not an agent wakeup. This repository creates no cron, service or recurring automation.

`refresh` requires at least six hours since the latest actual capture. Public reaction change is not reach, impressions, buyer quality, conversion or global trend rank. Meaning, creative relevance, descriptive performance and prospect fit remain separate decisions.

The sample discovery lists are empty. If an approved research brief requires discovery, the adapter can use an existing `mcporter` installation with the keyless Exa endpoint in `pipeline/mcporter.json`. Free quota and public-index coverage are not guaranteed. Native LinkedIn search is not connected by this code.

## Existing local tools

FFmpeg and ffprobe resolve through `tools.ffmpeg` / `tools.ffprobe` in the config, or through PATH. A configured relative executable path resolves from the config directory. Missing tools fail with an explicit message; no installer runs.

Whisper uses an existing interpreter and cached model. Local overrides are:

```text
LINKEDIN_WHISPER_PYTHON  existing interpreter or executable name
LINKEDIN_WHISPER_MODEL   existing cached model file
```

The config's `whisper.python` / `whisper.model` are the alternative. An empty interpreter uses the currently running Python. The default model location is the user's standard Whisper cache. Model downloads remain disabled. Original captions, ASR and alternatives stay separate; mechanical QA does not certify audio accuracy. A source-bound actual audio review is required to clear an audio-adjudication flag.

## Release-builder demo

Copy synthetic fixtures into an untracked temporary directory before running a demonstration; do not overwrite committed fixture evidence. The raw-evidence viewer expects two method guides in each selected run. Provision them from the bundled repository docs before the demo or a real release (the public derived viewer does not need these copies):

```sh
mkdir -p /path/to/copied-fixtures/v4/methodology
cp docs/CATEGORY-GUIDE.md docs/SEARCH-AND-QUALIFICATION.md /path/to/copied-fixtures/v4/methodology/
```

Use the analogous new dated run path for a real release. Pass the run and base explicitly:

```sh
python3 research/release.py --root /path/to/copied-fixtures/v4 --base /path/to/copied-fixtures/v3 --template research/viewer-template.html --as-of 2026-10-22
```

`--dry-run` verifies without promoting outputs. The base default points only to the bundled synthetic example, never to a private device folder. Real releases need explicit source-bound analysis and media evidence. The analytical SQLite, JSON, CSV and HTML must pass their joins, hashes, identity coverage and reconciliation checks before promotion.

Raw HTML, full third-party posts, captions, media, personal device paths and operational databases can be local evidence. They are **not** automatically eligible for public commit. Build the public derived projection separately and run the repository's public-safety checks before pushing. Public availability does not establish media reuse rights.

## Export record

See `SOURCE-PROVENANCE.json`, `verification/portable-tests.json` and `verification/portable-tests.txt`. The public fixture substitution and portable path/tool changes are documented; no claim is made that an installed dependency, connected account or external service is ready merely because instructions exist.
