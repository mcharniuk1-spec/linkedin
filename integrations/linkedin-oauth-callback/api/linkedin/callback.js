"use strict";

const PAGE = `<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>LinkedIn authorization returned</title>
  </head>
  <body>
    <main>
      <h1>LinkedIn authorization returned</h1>
      <p>This page does not read or send your authorization details.</p>
      <p>To finish locally, copy the entire URL from this browser's address bar. Paste it into the hidden prompt in the local <code>oauth-finish</code> command. Do not send it in chat, email, or a support request.</p>
      <p>You can close this page after the local command confirms the result.</p>
    </main>
  </body>
</html>`;

function setHeaders(res) {
  res.setHeader("Content-Type", "text/html; charset=utf-8");
  res.setHeader("Cache-Control", "no-store, max-age=0");
  res.setHeader("Pragma", "no-cache");
  res.setHeader("Referrer-Policy", "no-referrer");
  res.setHeader("Content-Security-Policy", "default-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'");
  res.setHeader("X-Content-Type-Options", "nosniff");
  res.setHeader("X-Frame-Options", "DENY");
  res.setHeader("X-Robots-Tag", "noindex, nofollow, noarchive");
}

/** Stateless Vercel Node handler. Never inspect or reflect request URL/query/body. */
module.exports = function linkedinOAuthCallback(_req, res) {
  setHeaders(res);
  if (_req.method !== "GET") {
    res.setHeader("Allow", "GET");
    res.statusCode = 405;
    res.end("Method Not Allowed");
    return;
  }
  res.statusCode = 200;
  res.end(PAGE);
};
