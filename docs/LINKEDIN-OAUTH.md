# LinkedIn read-only OAuth and API boundary

Status: OAuth and the official API path are implemented but not configured or exercised against LinkedIn. The checked-in configuration has an empty scope list, a disabled API source, and empty actor/resource allowlists. No credentials, consent, real API request or API access proof is present in this run.

## What the adapter can request

`research/collector/oauth.py` implements the OAuth 2.0 authorization-code flow with an exact registered redirect URI, random short-lived `state`, callback validation and read-scope checks. It rejects write scopes, uses a no-environment-proxy HTTP client without redirects for token exchange, and stores tokens in an encrypted local vault. OAuth state is also encrypted. A token exchange reports `resource_access_proven: false` because an exchanged token does not prove access to a specific LinkedIn resource.

`research/collector/linkedin_api.py` is a separate read-only REST adapter. It accepts GET only; requires a current token, explicit actor URNs, explicit resource allowlists, a declared API version and the scope required for the operation. Posts are requested for an exact author actor (`/posts?q=author`), not by global search. Comments require explicit post IDs. Organization metadata and analytics require an explicitly verified configured read scope; the code does not guess one. The adapter has bounded pages/items and does not fall back to anonymous HTML, Playwright or Scrapy after an API denial.

This is not an arbitrary LinkedIn profile, employee-directory, trend or platform-wide search API. Member social read access is restricted to approved users, and organization social read access depends on the application's LinkedIn product and the member's page role. The exact eligible scopes/resources must be confirmed for the registered app and the consenting member. See LinkedIn's [authorization-code flow](https://learn.microsoft.com/en-us/linkedin/shared/authentication/authorization-code-flow), [Posts API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api?view=li-lms-2026-10), and [programmatic refresh-token rules](https://learn.microsoft.com/en-us/linkedin/shared/authentication/programmatic-refresh-tokens). These documents describe the platform; they do not establish this app's entitlement.

## Required owner setup

Before any real authorization, the owner must supply and verify:

1. The exact LinkedIn developer application and the exact HTTPS callback URI registered for it. The value supplied in `LINKEDIN_REDIRECT_URI` must match that registration. Loopback HTTP is accepted only when explicitly opted in for a loopback URI; it is not a substitute for a mismatched registered callback.
2. The approved read scopes available to that app, the exact actor URNs, and the exact post/resource IDs the owner authorizes. Scope configuration is currently empty. A token alone does not authorize every LinkedIn actor or resource.
3. The consenting member's informed approval of the requested scopes, and confirmation that the relevant LinkedIn product grants those scopes. Do not request write scopes.
4. A secret storage route for the client ID/secret and an encryption key for the local state/token vault. Do not put secret values in source control, command arguments, shell history, workflow artifacts, issue comments or chat.

No real credential or token should be copied into this document. The workflow's encrypted state key must be stored as a GitHub Actions secret; the client secret belongs in an Actions secret only after the owner has authorized and configured OAuth. The redirect URI is configuration, not a secret, and is a repository variable only after it is confirmed.

## Local secret inputs

The CLI accepts either environment variables `LINKEDIN_CLIENT_ID` and `LINKEDIN_CLIENT_SECRET`, or a YAML file whose path is named by `LINKEDIN_CREDENTIALS_FILE`. The YAML file must be a regular non-symlink file with mode `0600` or stricter on POSIX. The parser accepts one unambiguous alias for each field: client ID aliases `client_id`/`client identifier`; secret aliases `client_secret`, `primary_client_secret`, `secret_key` or `secret`. Duplicate or ambiguous aliases fail closed. The actual secret values are never printed by preflight.

`COLLECTOR_STATE_KEY` or `COLLECTOR_STATE_KEY_FILE` supplies the Fernet key for encrypted state and token storage. `COLLECTOR_STATE_KEY_FILE` must point to a local protected file. In GitHub Actions, use the secret name `COLLECTOR_STATE_KEY`; do not put its value in a YAML workflow literal. The encrypted token vault is `research/work/collector/tokens.enc` locally and is included only inside the encrypted state envelope. Do not commit it or expose it as a standalone artifact.

## Explicit local sequence

Run from the repository root with the existing supported Python environment. The commands below do not install software. They do not run until an operator invokes them.

```sh
python -m research.collector.cli oauth-preflight --config research/collector/config.json
python -m research.collector.cli oauth-start --config research/collector/config.json
python -m research.collector.cli oauth-finish --config research/collector/config.json
```

`oauth-preflight` reports whether credential configuration, callback, scopes and encrypted token file are present; it does not print secret values and always reports API access as unproven. `oauth-start` creates a local encrypted pending state and a local authorization page. Open it only after verifying the app and read scopes. LinkedIn member consent occurs in LinkedIn's own flow. `oauth-finish` prompts with hidden input for the exact returned callback URL; do not pass an authorization code or token in argv or shell history. It checks that the callback origin/path match and consumes the saved state before token exchange. The stored token's granted scopes are reported, but resource access remains unproven until a separately authorized, bounded read succeeds.

Only after the owner confirms the exact scope, actor, resource, registered callback and consent should the API source be explicitly enabled in a reviewed config. Keep `operations`, `authorized_actors`, `allowed_resources`, `required_scopes`, page count and source caps narrowly bounded. A 401/403/429/999 or challenge is a persistent stop, not a cue to switch to public scraping. Resume only after source-backed review and an explicit `resume-source` action. Token refresh is not assumed: LinkedIn refresh tokens are available only to eligible approved partners, and this configuration does not assert that entitlement.

## Current access gap

Repository inspection confirmed that `LINKEDIN_REDIRECT_URI`, `LINKEDIN_CLIENT_ID`, `LINKEDIN_CLIENT_SECRET`/credential file, scopes and token are not supplied by the checked-in config. No OAuth command that exchanges a code and no LinkedIn API request was executed. `gh` CLI authentication returned 401. The connected GitHub repository read showed admin access, but its available connector did not expose a secret-setting operation. Therefore Actions secrets/variables, the `COLLECTOR_ENABLED` gate and a successful scheduled run remain unverified. User login and app setup are pending; no credential or external write was attempted.

## Safe test boundary

Use offline OAuth/API tests with synthetic credentials, fake callbacks and mocked HTTP responses. Do not use a real LinkedIn token to test against arbitrary actors or endpoints. The complete offline collector suite is run by `.github/workflows/collector-tests.yml`; focused local tests can be run with:

```sh
python -m unittest discover -s research/tests -p 'test_hybrid*.py' -v
```

Passing tests validate local policy and parser behavior only. They do not establish LinkedIn product approval, member consent, scope grant, actor-role access or API availability.

## App status confirmed by owner —29October2026

The owner registered `https://www.arch-flow.dev/api/linkedin/callback` and reported only `r_verify`, `r_profile_basicinfo` and `w_member_social` in Auth. These do not grant the intended post/comment/analytics reads. The collection API stays disabled and requested OAuth scopes stay empty. Do not authorize identity access or publishing merely to obtain a token for this research task.

For future approval, request only the needed approved product and exact read scope: `r_organization_social` for eligible organization post reads; `r_organization_social_feed` for the current comments/reactions surface; restricted `r_member_social`/`r_member_social_feed` only if explicitly granted; `r_member_postAnalytics` for the consenting member's own eligible analytics. Organization reporting scope/product support must be checked for the exact endpoint before configuration. No combination creates global competitor/profile/trend search. See [current permission/product mapping](https://learn.microsoft.com/en-us/linkedin/marketing/increasing-access) and [Comments API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/comments-api?view=li-lms-2026-10).

The callback package is in `integrations/linkedin-oauth-callback/`. It returns a constant page without reading, echoing or logging query values. The owner completes an explicitly requested consent locally: open the private authorization page from `oauth-start`, then copy the returned callback URL only into the hidden `oauth-finish` terminal prompt. Client-secret exchange, random-state verification and encrypted token storage stay in the local collector. Never send that URL in chat or logs. The standard confidential-client flow uses the registered HTTPS callback; do not assume the separate native-client PKCE/loopback entitlement.

## Callback deployment verification

The callback is now live at the registered URL. Deployment `dpl_2B5jM4jjTkkHTdAZ1zMP12a69xCo` serves an isolated dependency-free Node function. One exact-path/host rewrite on the existing ArchFlow project was promoted as routing version `364ea13d-3e9e-4ff9-824d-73b28fc9ffc0`. GET returned200, POST405, and a synthetic code/state query produced the identical constant page without reflected values. Responses use no-store, no-referrer and restrictive CSP. The main website HTML hash was unchanged; a neighboring callback path remains404. No real authorization code or token was used. Application code never logs query data; provider edge-log retention remains unverified and is a gap before any real consent. Rollback restores the prior routing version recorded in the verification JSON.
