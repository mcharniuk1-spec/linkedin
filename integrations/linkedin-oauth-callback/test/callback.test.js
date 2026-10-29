"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const callback = require("../api/linkedin/callback.js");

function responseRecorder() {
  return {
    headers: {},
    statusCode: null,
    body: null,
    setHeader(name, value) { this.headers[name.toLowerCase()] = value; },
    end(body) { this.body = body; },
  };
}

test("GET returns a constant safe page and never reflects synthetic OAuth values", () => {
  const syntheticCode = "SYNTHETIC_CODE_MUST_NOT_LEAK_8f273";
  const syntheticState = "SYNTHETIC_STATE_MUST_NOT_LEAK_5a19c";
  const req = {
    method: "GET",
    url: `/api/linkedin/callback?code=${syntheticCode}&state=${syntheticState}`,
    headers: { host: "www.arch-flow.dev", referer: `https://www.arch-flow.dev/?code=${syntheticCode}` },
    body: { code: syntheticCode, state: syntheticState },
  };
  const res = responseRecorder();
  const logs = [];
  const oldLog = console.log;
  const oldError = console.error;
  console.log = (...args) => logs.push(args.join(" "));
  console.error = (...args) => logs.push(args.join(" "));
  try {
    callback(req, res);
  } finally {
    console.log = oldLog;
    console.error = oldError;
  }

  assert.equal(res.statusCode, 200);
  assert.match(res.body, /copy the entire URL from this browser's address bar/i);
  assert.match(res.body, /hidden prompt/i);
  assert.doesNotMatch(res.body, new RegExp(syntheticCode));
  assert.doesNotMatch(res.body, new RegExp(syntheticState));
  assert.equal(logs.length, 0);
  assert.equal(res.headers["cache-control"], "no-store, max-age=0");
  assert.equal(res.headers["referrer-policy"], "no-referrer");
  assert.match(res.headers["content-security-policy"], /default-src 'none'/);
  assert.match(res.headers["content-security-policy"], /frame-ancestors 'none'/);
  assert.equal(res.headers["content-type"], "text/html; charset=utf-8");
});

test("non-GET methods are rejected without reading or reflecting the request body", () => {
  const syntheticCode = "SYNTHETIC_POST_CODE_MUST_NOT_LEAK";
  const res = responseRecorder();
  callback({ method: "POST", body: { code: syntheticCode, state: "unused" } }, res);
  assert.equal(res.statusCode, 405);
  assert.equal(res.headers.allow, "GET");
  assert.equal(res.body, "Method Not Allowed");
  assert.doesNotMatch(res.body, new RegExp(syntheticCode));
});

test("HEAD and other methods are rejected", () => {
  const res = responseRecorder();
  callback({ method: "HEAD" }, res);
  assert.equal(res.statusCode, 405);
  assert.equal(res.body, "Method Not Allowed");
});
