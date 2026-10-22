# LinkedIn founder-content research and services

A public-safe research/runtime and service-method repository for Europe-based B2B AI SaaS founder-led LinkedIn work.

Start with [the consolidated current state](CURRENT-STATE.md), [the current derived dataset](datasets/current/index.html), [dataset state](datasets/current/STATE.json), [gaps](datasets/current/gaps.json) and [the project agent contract](AGENTS.md). The public projection contains original assessments, public counters and source locators. Full copied source posts, speech transcripts and uncleared third-party media remain in the owner's local evidence store; this repository does not distribute them or claim their reuse rights.

## Layout

- [research/](research/README.md): portable collector/parser, immutable observations, media/transcription/QA, qualification, analytical release and standalone synthetic tests.
- [datasets/current/](datasets/current/README.md): sanitized JSON/CSV/SQLite and a viewer with separate reference and prospect views.
- [docs/](docs/SERVICES-AND-WRITING.md): services, founder/website writing, search/category methods and exact tool/skill-name map.
- [design and website/](design%20and%20website/README.md): current V5 brand/V9 website source, shared components/Storybook, cleared assets, build inputs, QA and release hashes.
- [editorial/](editorial/README.md): twenty current publication drafts, thirteen diagrams and two video storyboards, with exact Figma frame links and rights/source maps.
- `scripts/`: deterministic public export, schema/identity/payload checks and public-safety scan.

## View locally

From the repository root:

```sh
python3 -m http.server 6071 --bind 127.0.0.1
```

Then open http://127.0.0.1:6071/datasets/current/index.html. Use another free local port if6071 already serves the owner's local research runs. Do not take the website lane's6051port. A static server is a viewer, not a recurring collector. GitHub repository file previews do not execute HTML; no Pages/website deployment is activated.

## Verify

Use an existing supported Python environment with BeautifulSoup and Node.js available:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -W ignore::ResourceWarning -m unittest discover -s research/tests
python3 -m unittest discover -s scripts -p 'test_*.py'
python3 scripts/verify_release.py
python3 scripts/public_safety_scan.py
```

Tests use invented source/byte fixtures. They do not establish live LinkedIn layout/market coverage. Missing FFmpeg/Whisper/model/account access remains explicit; this repository installs nothing automatically.

## Execution limits

Discovery seeds are not platform rankings. Public reaction counters are not impressions, reach, buyer quality or conversions. Meaning and performance remain separate; a current trend requires actual comparable observations. Preserve the six-hour measurement floor, original capture times, parser hashes and access stops. Source claims, including tool/free-access and customer-result claims, remain attributed and unverified where applicable.

This repository does not activate login/cookie import, paid providers, outreach, post publication, ad launch, website deployment, recurring runs or future agent wakes. The separately deployed current website is linked in the state record. The owner explicitly requested no recurring scheduling. The design and editorial manifests record the current owner-authorized Git source snapshot. Artistic/voice acceptance remains pending; build success does not establish it.

## Rights and provenance

Owned methods/code and independently generated synthetic fixtures are exported with source/provenance notes. Third-party dependencies retain their own licenses. No blanket rights are claimed over source posts, media, brands, fonts or proprietary candidate tools. See [research provenance](research/SOURCE-PROVENANCE.json), [public export provenance](datasets/current/provenance.json) and the current gaps.
