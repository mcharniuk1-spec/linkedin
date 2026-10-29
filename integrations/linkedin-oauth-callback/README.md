# LinkedIn OAuth callback page

Proposed exact callback URI: **`https://www.arch-flow.dev/api/linkedin/callback`**.

The owner must register this exact URI in the LinkedIn developer application and then verify that LinkedIn exposes the selected read scopes for that app. The canonical host is `www.arch-flow.dev`; `arch-flow.dev` currently redirects, so do not register the redirecting host. This package is staged source only. No deployment, Vercel route mount, OAuth application change, or live callback has been performed.

## Request behavior

The Vercel Node handler accepts GET and returns a fixed HTML instruction page. It does not parse, store, forward, log or reflect query parameters, request headers, or request bodies. The page tells the operator to copy the entire callback URL from the address bar and paste it into the hidden prompt of the existing local `oauth-finish` command. The page has no scripts, stylesheets, images, forms, analytics, storage or third-party requests. It sends `Cache-Control: no-store`, `Referrer-Policy: no-referrer`, a restrictive Content Security Policy and `X-Robots-Tag`.

The existing local flow remains responsible for checking the saved encrypted OAuth `state`, exact redirect URI, and authorization code, exchanging the code, and storing the resulting token in the local encrypted token vault. The website must never receive a client secret or access/refresh token. The callback page does not validate OAuth success; if LinkedIn returns an error, the operator still hands the exact URL to the local command, which rejects invalid code/state data.

Before live use, verify Vercel request/access-log behavior and retention for query strings. This handler emits no application logs, but this package cannot control provider or edge-level request logs. Do not proceed with OAuth until those logs do not expose callback codes/state, or the platform logging configuration has been reviewed and made safe.

## Read scope selection

Request only the read scope required for the owner's exact authorized resources. Do not request write scopes.

- For organization posts, the collector requires `r_organization_social`. LinkedIn product access and the consenting member's organization-page role still control access.
- For member posts, the collector requires `r_member_social`. LinkedIn restricts this permission to approved users; it does not provide general member/profile or employee-directory access.
- The API adapter does not offer global post search, trend discovery, or arbitrary profile enumeration. It reads posts for explicitly allowlisted actors and requires explicit post IDs for comments. Organization metadata/analytics need a separately verified read scope and explicit resource configuration.

These are conditional API requirements, not proof that this application has access. The app owner must confirm the exact scopes in the LinkedIn developer portal and choose the matching source type. Do not configure both scopes unless both resource classes are approved and needed. See LinkedIn's [authorization-code flow](https://learn.microsoft.com/en-us/linkedin/shared/authentication/authorization-code-flow), [Posts API](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/posts-api?view=li-lms-2026-09), and [programmatic refresh-token rules](https://learn.microsoft.com/en-us/linkedin/shared/authentication/programmatic-refresh-tokens). Refresh access is not assumed and is available only to eligible approved partners.

## Local flow

From the repository root, after the exact redirect and approved read scopes are set in the private local config/environment and credentials are placed in the protected local secret route, run:

```sh
python -m research.collector.cli oauth-preflight --config research/collector/config.json
python -m research.collector.cli oauth-start --config research/collector/config.json
```

Open the local authorization page, review the app name and read scopes, and complete member consent in LinkedIn. LinkedIn returns to the registered HTTPS URL. Copy the complete URL, including query parameters, from the address bar and paste it only into:

```sh
python -m research.collector.cli oauth-finish --config research/collector/config.json
```

That command uses hidden input; do not paste the callback URL into a shell command, issue, message, or terminal that records commands. A token exchange still does not prove access to a particular organization or post. The source config must separately contain the owner's explicit actor/resource allowlist before any API read.

The existing local CLI currently reads client ID/secret from `LINKEDIN_CLIENT_ID` and `LINKEDIN_CLIENT_SECRET`, or from a protected file named by `LINKEDIN_CREDENTIALS_FILE`. It reads the exact redirect from `LINKEDIN_REDIRECT_URI`. The website callback uses none of these values.

## Vercel integration

The route must be mounted as `/api/linkedin/callback` in the deployed project associated with `www.arch-flow.dev`. This package is not a standalone complete site and must not replace or redeploy the site's existing source. The site owner must review and integrate this route into the actual deployable source, verify the mapped domain and provider logging configuration, run the tests below, then separately approve and perform deployment. Do not claim the callback is live until a deployment and route readback confirm it.

## Tests

This package uses only Node's built-in test runner and has no runtime dependencies:

```sh
npm test
```

Tests use synthetic callback code/state values. They check that the GET body and captured application logs do not contain those values, security headers are present, and POST/HEAD are rejected. They do not make a network request or prove Vercel's edge logs are safe.

## Deployment29October2026

The registered callback is deployed and verified; see `../../research/verification/hybrid-v7.json`. This does not prove OAuth consent or data-read permission. Current owner-reported app permissions do not grant the collector's post reads. No token exchange was executed.
