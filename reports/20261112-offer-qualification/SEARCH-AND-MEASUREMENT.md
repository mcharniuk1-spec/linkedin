# outspoken.digital: search and measurement plan

12 November 2026. Tasks 87–91 are Backlog and unassigned until execution starts. This plan is delivered. Google account setup, tags and API/MCP connections are not yet live. Every website source change starts on a fresh codex/ branch.

## Observed baseline

The established owned-site checker returned 200 for the homepage, robots.txt and sitemap.xml. Robots permits crawling and points to https://outspoken.digital/sitemap.xml. The sitemap lists the canonical homepage. The captured homepage response has no X-Robots-Tag. These checks do not prove Google has indexed the site.

A default urllib request received Cloudflare error1010, while the established checker returned200. Verify crawler access in Search Console instead of assuming every user agent can fetch the page. Current source/task18 records no installed analytics and a disabled Privacy template. Google property ownership and measurement/container IDs are unverified.

## Execution order

|Task|Work|Completion evidence|
|---|---|---|
|87 — search and Search Console|Check canonical, title, description, headings, rendered links, robots directives and mobile access. Verify the outspoken.digital Domain property through owner-controlled DNS. Submit sitemap; inspect the homepage and request crawling where appropriate.|Verified property identity, sitemap result and actual URL Inspection/index state. No indexing guarantee.|
|88 — GA4/GTM foundation|Confirm business questions, Google owner, property and web stream. Choose one Google tag/GTM configuration path. Record IDs, access, timezone and retention. Resolve Privacy/consent with18 before tag release.|Property/container readback, approved measurement/consent plan and rollback.|
|89 — events|Implement the contract below on a new website branch. Bind success to the actual booking response, not the submit click. Test consent, validation, failures, retries and duplicates.|Tag Assistant/DebugView and network evidence on desktop/mobile; correct parameters and single success event.|
|90 — API/MCP reporting|Configure the official read-only Analytics MCP with Admin/Data APIs and minimum property access. Connect Search Console API for the verified property.|An authenticated report query for the correct property and date window. Configuration files alone do not prove connection.|
|91 — measurement QA|Reconcile visits, CTA clicks, booking starts and confirmed bookings. Review index state, sitemap, events, consent, duplication and PageSpeed mobile/desktop.|Actual checks, first report, known gaps and baseline; no invented conversion improvement.|

Search Console verification does not depend on GA4. The official Analytics MCP is read-only; it cannot create properties or change tags. Configuration needs the appropriate Admin UI/API or GTM workflow. No supported direct GA4/Search Console connector is configured in this session; unrelated Ahrefs tools do not establish property access.

## Event contract

|Event|Trigger|Safe context|Does not establish|
|---|---|---|---|
|page_view|One page view through the chosen configuration path.|Sanitized page path and approved campaign fields.|A qualified visitor.|
|cta_click|Intro-call CTA activated.|Placement and offer variant.|A booking.|
|booking_open|Booking interface actually opens.|Entry placement and interface version.|A form start or meeting.|
|booking_form_start|First interaction with the actual form.|Form type and entry placement; no field values.|A successful lead.|
|booking_validation_error|Validation prevents progression.|Coarse error category.|A buyer objection.|
|booking_request_failed|Request fails without confirmed creation.|Safe error category.|A booking.|
|generate_lead|Booking API confirms creation or a verified success callback arrives; fire once.|Safe call/form type. Keep dedupe keys internal.|A qualified or attended meeting, or client.|
|contact_click|Email/contact link activated.|Link type and placement.|Sent email or a reply.|

The proposed generate_lead mapping must be checked against actual booking behavior. Do not send names, email, phone, profile URLs, company names, free text, raw booking IDs or personal query strings to GA4/GTM. Prevent overlap with automatic form tracking. FAQ/scroll events are optional and need a business question.

## Consent and validation

Use the approved basic/advanced consent approach. Set defaults before tags and update them after the actual choice; check custom tags too. Consent Mode is a technical mechanism, not a legal determination. Task18 must account for the new processors, retention and data flows before release.

Test: valid booking, invalid field, API failure, timeout, double click, retry, reopen, consent denied/accepted, desktop/mobile and personal-data inspection. Reconcile confirmed bookings with internal records. A synthetic test booking is not a prospect.

Use consistent nonpersonal UTMs for owned LinkedIn placements. Separate personal/company placements, preserve campaign parameters and avoid UTMs on internal navigation. Keep LinkedIn distribution, website actions and CRM-qualified conversations separate.

## Primary sources checked12 November2026

[Google indexing guidance](https://developers.google.com/search/docs/fundamentals/get-on-google) · [Search Console verification](https://support.google.com/webmasters/answer/9008080) · [Search Console API](https://developers.google.com/webmaster-tools) · [GA4 events](https://developers.google.com/analytics/devguides/collection/ga4/events) · [Official Analytics MCP](https://developers.google.com/analytics/devguides/MCP) · [Consent implementation](https://developers.google.com/tag-platform/security/guides/consent)
