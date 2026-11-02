// Unit tests for api/lead.js (the contact-form function).
// Run: cd deploy/vercel && node --test test/        (Node 22; node:test and node:assert only, no packages, no network)
//
// What is real and what is faked:
//  - The handler under test is the real api/lead.js, loaded once with require().
//  - globalThis.fetch is replaced by FakeNeon, a tiny in-memory stand-in for Neon's SQL-over-HTTP endpoint.
//    It understands exactly the two statements the function sends (the rate-limit count and the insert).
//    It reads the 10-minute window out of the SQL text and uses its own virtual clock, so the window
//    expiry in these tests follows what the function really asks the database for.
//    Any other statement is recorded and fails the test.
//  - Real Postgres behaviour (column types, role permissions, the actual now()) is NOT covered here.
//  - All data below is fictional. Never put a real lead into this file.
import { describe, it, beforeEach, afterEach, mock } from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import crypto from 'node:crypto';

const require = createRequire(import.meta.url);
const handler = require('../api/lead.js');

const DUMMY_URL = 'postgresql://user:pass@db.example.invalid/neondb';
const SITE_HOST = 'outspoken.example';
const MINUTE = 60 * 1000;
const COUNT_SQL = "select count(*)::int as n from leads where ip_hash = $1 and created_at > now() - interval '10 minutes'";
const INSERT_SQL = 'insert into leads (name, email, company, service, context, consent, source, user_agent, ip_hash) values ($1,$2,$3,$4,$5,$6,$7,$8,$9) returning id';
const SECRET_FRAGMENTS = ['user:pass', 'pass@', 'db.example.invalid', 'postgresql', 'neondb', 'LEADS_DATABASE_URL'];

const ipHash = (ip) => crypto.createHash('sha256').update(ip + '|outspoken-leads').digest('hex').slice(0, 24);

const validBody = (over = {}) => ({
  name: 'Ada Example',
  email: 'ada@example.com',
  company: 'Example Labs',
  service: 'Positioning and profile',
  context: 'We build a developer tool and need a clearer story.',
  consent: true,
  source: 'website one-pager',
  ...over,
});

// Request stub. A header set to undefined is removed.
function makeReq(o = {}) {
  const headers = {
    host: SITE_HOST,
    origin: 'https://' + SITE_HOST,
    'user-agent': 'node-test-agent/1.0',
    'x-forwarded-for': '198.51.100.7',
    'content-type': 'application/json',
    ...(o.headers || {}),
  };
  for (const k of Object.keys(headers)) if (headers[k] === undefined) delete headers[k];
  return {
    method: o.method || 'POST',
    headers,
    body: 'body' in o ? o.body : validBody(),
    socket: { remoteAddress: o.remoteAddress || '192.0.2.99' },
  };
}

// Response stub that records status, headers and the body, and counts end() calls.
function makeRes() {
  const res = { statusCode: 200, headers: {}, ended: 0, raw: '' };
  res.setHeader = (k, v) => { res.headers[k.toLowerCase()] = v; };
  res.end = (s) => { res.ended += 1; res.raw = s == null ? '' : String(s); };
  Object.defineProperty(res, 'json', { get() { return res.raw ? JSON.parse(res.raw) : undefined; } });
  return res;
}

async function call(req) {
  const res = makeRes();
  await handler(req, res);
  assert.equal(res.ended, 1, 'the handler must answer exactly once');
  assert.equal(res.headers['content-type'], 'application/json; charset=utf-8');
  assert.equal(res.headers['cache-control'], 'no-store');
  return res;
}

function assertNoSecrets(res) {
  for (const s of SECRET_FRAGMENTS) assert.ok(!res.raw.includes(s), 'response must not contain "' + s + '": ' + res.raw);
}

class FakeNeon {
  constructor() {
    this.now = Date.UTC(2026, 10, 2, 12, 0, 0); // virtual clock, milliseconds
    this.rows = [];
    this.calls = [];
    this.unexpected = [];
    this.nextId = 1;
    this.failWhen = null; // (payload) => Response | throws | undefined
  }
  install() { this.original = globalThis.fetch; globalThis.fetch = (url, init) => this.fetch(url, init); }
  restore() { globalThis.fetch = this.original; }
  seed(hash, count, ageMs = 0) {
    for (let i = 0; i < count; i++) this.rows.push({ id: this.nextId++, ip_hash: hash, created_at: this.now - ageMs });
  }
  get inserts() { return this.calls.filter((c) => /^insert into leads/i.test(c.query)); }
  json(status, obj) { return new Response(JSON.stringify(obj), { status, headers: { 'Content-Type': 'application/json' } }); }
  async fetch(url, init) {
    const payload = JSON.parse(init.body);
    this.calls.push({ url: String(url), method: init.method, headers: init.headers, query: payload.query, params: payload.params });
    if (this.failWhen) {
      const out = this.failWhen(payload);
      if (out) return out;
    }
    const count = /^select count\(\*\)::int as n from leads where ip_hash = \$1 and created_at > now\(\) - interval '(\d+) minutes'$/.exec(payload.query);
    if (count) {
      const since = this.now - Number(count[1]) * MINUTE;
      const n = this.rows.filter((r) => r.ip_hash === payload.params[0] && r.created_at > since).length;
      return this.json(200, { rows: [{ n }] });
    }
    const ins = /^insert into leads \(([^)]+)\) values \(([^)]+)\) returning id$/.exec(payload.query);
    if (ins) {
      const cols = ins[1].split(',').map((s) => s.trim());
      const holders = ins[2].split(',').map((s) => s.trim());
      assert.equal(cols.length, holders.length);
      assert.equal(payload.params.length, cols.length);
      const row = { id: this.nextId++, created_at: this.now };
      cols.forEach((c, i) => { row[c] = payload.params[Number(holders[i].slice(1)) - 1]; });
      this.rows.push(row);
      return this.json(200, { rows: [{ id: row.id }] });
    }
    this.unexpected.push(payload.query);
    return this.json(400, { message: 'statement not supported by the test double' });
  }
}

describe('api/lead.js', () => {
  let neon;
  let savedEnv;

  beforeEach(() => {
    savedEnv = { L: process.env.LEADS_DATABASE_URL, D: process.env.DATABASE_URL, P: process.env.POSTGRES_URL };
    process.env.LEADS_DATABASE_URL = DUMMY_URL;
    delete process.env.DATABASE_URL;
    delete process.env.POSTGRES_URL;
    neon = new FakeNeon();
    neon.install();
  });

  afterEach(() => {
    neon.restore();
    mock.restoreAll();
    const restore = (k, v) => { if (v === undefined) delete process.env[k]; else process.env[k] = v; };
    restore('LEADS_DATABASE_URL', savedEnv.L);
    restore('DATABASE_URL', savedEnv.D);
    restore('POSTGRES_URL', savedEnv.P);
    assert.deepEqual(neon.unexpected, [], 'the function sent a statement the test double does not know');
  });

  describe('method', () => {
    for (const method of ['GET', 'HEAD', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']) {
      it(method + ' is refused with 405 and an Allow header, and nothing reaches the database', async () => {
        const res = await call(makeReq({ method }));
        assert.equal(res.statusCode, 405);
        assert.equal(res.headers.allow, 'POST');
        assert.deepEqual(res.json, { error: 'Use POST.' });
        assert.equal(neon.calls.length, 0);
      });
    }
  });

  describe('body and content type', () => {
    // The function does not look at Content-Type. Vercel gives a parsed object for application/json
    // and a string for other types; the function parses a string as JSON itself.
    it('accepts a JSON string body, whatever the Content-Type header says', async () => {
      const res = await call(makeReq({ headers: { 'content-type': 'text/plain' }, body: JSON.stringify(validBody()) }));
      assert.equal(res.statusCode, 200);
      assert.equal(neon.inserts.length, 1);
    });

    it('treats a string that is not JSON as an empty body (400, no database call)', async () => {
      const res = await call(makeReq({ body: 'name=Ada&email=ada%40example.com' }));
      assert.equal(res.statusCode, 400);
      assert.equal(res.json.error, 'Please add your name.');
      assert.equal(neon.calls.length, 0);
    });

    for (const [label, body] of [['undefined', undefined], ['null', null], ['a number', 42], ['an array', []], ['the JSON text "null"', 'null']]) {
      it('answers 400 (not a crash) when the body is ' + label, async () => {
        const res = await call(makeReq({ body }));
        assert.equal(res.statusCode, 400);
        assert.equal(neon.calls.length, 0);
      });
    }
  });

  describe('origin check', () => {
    it('allows a browser request whose Origin host equals the Host header', async () => {
      const res = await call(makeReq());
      assert.equal(res.statusCode, 200);
    });

    it('compares the port too (local development)', async () => {
      const ok = await call(makeReq({ headers: { host: 'localhost:3000', origin: 'http://localhost:3000' } }));
      assert.equal(ok.statusCode, 200);
      const bad = await call(makeReq({ headers: { host: 'localhost:3000', origin: 'http://localhost:4000' } }));
      assert.equal(bad.statusCode, 403);
    });

    it('lets a request with no Origin header through (non-browser clients are not blocked by this check)', async () => {
      const res = await call(makeReq({ headers: { origin: undefined } }));
      assert.equal(res.statusCode, 200);
    });

    for (const [label, origin] of [
      ['a foreign site', 'https://evil.example'],
      ['a look-alike that starts with the real host', 'https://' + SITE_HOST + '.evil.example'],
      ['a subdomain of the real host', 'https://sub.' + SITE_HOST],
      ['the real host on another port', 'https://' + SITE_HOST + ':8443'],
      ['a value that is not a URL', 'not a url'],
      ['the literal string "null"', 'null'],
    ]) {
      it('rejects ' + label + ' with 403 and does not touch the database', async () => {
        const res = await call(makeReq({ headers: { origin } }));
        assert.equal(res.statusCode, 403);
        assert.deepEqual(res.json, { error: 'Not allowed.' });
        assert.equal(neon.calls.length, 0);
      });
    }

    it('rejects an Origin when the Host header is missing', async () => {
      const res = await call(makeReq({ headers: { host: undefined } }));
      assert.equal(res.statusCode, 403);
    });

    it('runs before the honeypot check: a foreign origin with the honeypot filled still gets 403', async () => {
      const res = await call(makeReq({ headers: { origin: 'https://evil.example' }, body: validBody({ ref_code: 'http://spam.example' }) }));
      assert.equal(res.statusCode, 403);
    });
  });

  describe('honeypot field "ref_code"', () => {
    it('answers 200 {ok:true} and stores nothing when the field is filled', async () => {
      const res = await call(makeReq({ body: validBody({ ref_code: 'http://spam.example' }) }));
      assert.equal(res.statusCode, 200);
      assert.deepEqual(res.json, { ok: true }); // no id, so a bot learns nothing
      assert.equal(neon.calls.length, 0);
      assert.equal(neon.rows.length, 0);
    });

    it('is checked before validation and before the database setting (works with invalid fields and no env var)', async () => {
      delete process.env.LEADS_DATABASE_URL;
      const res = await call(makeReq({ body: { ref_code: 'x', name: '', email: 'nope', consent: false } }));
      assert.equal(res.statusCode, 200);
      assert.deepEqual(res.json, { ok: true });
      assert.equal(neon.calls.length, 0);
    });

    it('an empty honeypot is a normal submission', async () => {
      const res = await call(makeReq({ body: validBody({ ref_code: '' }) }));
      assert.equal(res.statusCode, 200);
      assert.equal(typeof res.json.id, 'number');
      assert.equal(neon.rows.length, 1);
    });

    it('honeypot hits do not use up the rate-limit quota (nothing is stored for them)', async () => {
      for (let i = 0; i < 10; i++) await call(makeReq({ body: validBody({ ref_code: 'spam' }) }));
      const res = await call(makeReq());
      assert.equal(res.statusCode, 200);
    });
  });

  describe('required fields', () => {
    const NAME = 'Please add your name.';
    const EMAIL = 'Please add a valid email address.';
    const CONTEXT = 'Please tell us a little more about what you are building.';
    const CONSENT = 'Please confirm that we may store your details to reply.';

    const refused = [
      ['name is missing', { name: undefined }, NAME],
      ['name is empty', { name: '' }, NAME],
      ['name is only spaces', { name: '   ' }, NAME],
      ['name is only control characters', { name: '\u0000\u0007\u001f' }, NAME],
      ['name is null', { name: null }, NAME],
      ['email is missing', { email: undefined }, EMAIL],
      ['email is empty', { email: '' }, EMAIL],
      ['email has no @', { email: 'plainaddress' }, EMAIL],
      ['email has no dot in the domain', { email: 'ada@example' }, EMAIL],
      ['email top-level part is one character', { email: 'ada@example.c' }, EMAIL],
      ['email has a space inside', { email: 'ada lovelace@example.com' }, EMAIL],
      ['email has no local part', { email: '@example.com' }, EMAIL],
      ['email has two @', { email: 'ada@@example.com' }, EMAIL],
      ['email is a number', { email: 12345 }, EMAIL],
      ['context is missing', { context: undefined }, CONTEXT],
      ['context is 9 characters', { context: '123456789' }, CONTEXT],
      ['context is 9 characters plus padding spaces', { context: '  123456789   ' }, CONTEXT],
      ['consent is missing', { consent: undefined }, CONSENT],
      ['consent is false', { consent: false }, CONSENT],
      ['consent is the string "false"', { consent: 'false' }, CONSENT],
      ['consent is the string "off"', { consent: 'off' }, CONSENT],
      ['consent is the number 1', { consent: 1 }, CONSENT],
    ];
    for (const [label, over, message] of refused) {
      it('400 "' + message + '" when ' + label + ', with no database call', async () => {
        const res = await call(makeReq({ body: validBody(over) }));
        assert.equal(res.statusCode, 400);
        assert.deepEqual(res.json, { error: message });
        assert.equal(neon.calls.length, 0);
      });
    }

    it('reports the first problem in the order name, email, context, consent', async () => {
      const res = await call(makeReq({ body: { consent: false } }));
      assert.equal(res.json.error, NAME);
      const res2 = await call(makeReq({ body: { name: 'Ada', consent: false } }));
      assert.equal(res2.json.error, EMAIL);
      const res3 = await call(makeReq({ body: { name: 'Ada', email: 'ada@example.com', consent: false } }));
      assert.equal(res3.json.error, CONTEXT);
      const res4 = await call(makeReq({ body: { name: 'Ada', email: 'ada@example.com', context: '0123456789', consent: false } }));
      assert.equal(res4.json.error, CONSENT);
    });

    it('accepts context of exactly 10 characters', async () => {
      const res = await call(makeReq({ body: validBody({ context: '0123456789' }) }));
      assert.equal(res.statusCode, 200);
    });

    for (const email of ['a@b.co', 'founder@startup.eu', 'first.last+tag@sub.domain.io']) {
      it('accepts the email ' + email, async () => {
        const res = await call(makeReq({ body: validBody({ email }) }));
        assert.equal(res.statusCode, 200);
        assert.equal(neon.inserts[neon.inserts.length - 1].params[1], email);
      });
    }

    for (const consent of [true, 'true', 'on']) {
      it('accepts consent given as ' + JSON.stringify(consent) + ' and stores the boolean true', async () => {
        const res = await call(makeReq({ body: validBody({ consent }) }));
        assert.equal(res.statusCode, 200);
        assert.strictEqual(neon.inserts[0].params[5], true);
      });
    }
  });

  describe('maximum lengths (the function cuts to the limit, it does not reject)', () => {
    // [field, limit, index of the field in the insert parameters]
    const limits = [['name', 120, 0], ['company', 160, 2], ['service', 80, 3], ['context', 4000, 4], ['source', 80, 6]];
    for (const [field, max, idx] of limits) {
      it(field + ': a value of exactly ' + max + ' characters is kept whole', async () => {
        const res = await call(makeReq({ body: validBody({ [field]: 'x'.repeat(max) }) }));
        assert.equal(res.statusCode, 200);
        assert.equal(neon.inserts[0].params[idx].length, max);
      });
      it(field + ': a value of ' + (max + 50) + ' characters is cut to ' + max, async () => {
        const res = await call(makeReq({ body: validBody({ [field]: 'x'.repeat(max + 50) }) }));
        assert.equal(res.statusCode, 200);
        assert.equal(neon.inserts[0].params[idx], 'x'.repeat(max));
      });
    }

    it('user agent: cut to 300 characters', async () => {
      const res = await call(makeReq({ headers: { 'user-agent': 'u'.repeat(500) } }));
      assert.equal(res.statusCode, 200);
      assert.equal(neon.inserts[0].params[7], 'u'.repeat(300));
    });

    it('email: exactly 200 characters is kept whole', async () => {
      const email = 'a'.repeat(188) + '@example.com';
      assert.equal(email.length, 200);
      const res = await call(makeReq({ body: validBody({ email }) }));
      assert.equal(res.statusCode, 200);
      assert.equal(neon.inserts[0].params[1], email);
    });

    it('email: a very long value is cut at 200 characters and then fails the format check', async () => {
      const res = await call(makeReq({ body: validBody({ email: 'a'.repeat(250) + '@example.com' }) }));
      assert.equal(res.statusCode, 400);
      assert.equal(res.json.error, 'Please add a valid email address.');
      assert.equal(neon.calls.length, 0);
    });

    // Fixed after the first test run exposed it: a 201-character address used to be cut to 200 characters and could be stored as a different, valid-looking address.
    it('email: a 201-character address is rejected, never stored as a different address', async () => {
      const email = 'a'.repeat(189) + '@example.com';
      const res = await call(makeReq({ body: validBody({ email }) }));
      assert.equal(res.statusCode, 400);
      assert.equal(res.json.error, 'Please add a valid email address.');
      assert.equal(neon.calls.length, 0);
    });

    it('email: a 200-character address is still accepted unchanged', async () => {
      const email = 'a'.repeat(188) + '@example.com';
      assert.equal(email.length, 200);
      const res = await call(makeReq({ body: validBody({ email }) }));
      assert.equal(res.statusCode, 200);
      assert.equal(neon.inserts[0].params[1], email);
    });
  });

  describe('cleaning of values', () => {
    it('trims spaces and removes control characters but keeps line breaks and tabs', async () => {
      const res = await call(makeReq({ body: validBody({ name: '  A\u0000d\u0007a  ', context: 'Line one\nLine two\twith tab, plus\u0008 more' }) }));
      assert.equal(res.statusCode, 200);
      const p = neon.inserts[0].params;
      assert.equal(p[0], 'Ada');
      assert.equal(p[4], 'Line one\nLine two\twith tab, plus more');
    });

    it('stores empty optional fields as null', async () => {
      const res = await call(makeReq({ body: validBody({ company: '', service: '   ', source: undefined }), headers: { 'user-agent': undefined } }));
      assert.equal(res.statusCode, 200);
      const p = neon.inserts[0].params;
      assert.strictEqual(p[2], null);
      assert.strictEqual(p[3], null);
      assert.strictEqual(p[6], null);
      assert.strictEqual(p[7], null);
    });
  });

  describe('successful insert', () => {
    it('sends the rate-limit check first and then one parameterised insert with the cleaned values', async () => {
      const res = await call(makeReq());
      assert.equal(res.statusCode, 200);
      assert.deepEqual(neon.calls.map((c) => c.query), [COUNT_SQL, INSERT_SQL]);
      assert.deepEqual(neon.calls[0].params, [ipHash('198.51.100.7')]);
      assert.deepEqual(neon.calls[1].params, [
        'Ada Example', 'ada@example.com', 'Example Labs', 'Positioning and profile',
        'We build a developer tool and need a clearer story.', true, 'website one-pager', 'node-test-agent/1.0', ipHash('198.51.100.7'),
      ]);
    });

    it('never puts submitted values into the SQL text (hostile input stays in the parameters)', async () => {
      const hostile = "Robert'); drop table leads; --";
      const res = await call(makeReq({ body: validBody({ name: hostile, context: hostile + ' padding', company: hostile }) }));
      assert.equal(res.statusCode, 200);
      for (const c of neon.calls) {
        assert.ok(!c.query.includes('Robert'), 'value found inside SQL text');
        assert.ok(!c.query.includes('drop table'), 'value found inside SQL text');
        assert.match(c.query, /\$1/);
      }
      assert.equal(neon.inserts[0].params[0], hostile);
    });

    it('calls the Neon SQL endpoint of the connection-string host, with the connection string only in a header', async () => {
      await call(makeReq());
      const c = neon.calls[0];
      assert.equal(c.url, 'https://db.example.invalid/sql');
      assert.equal(c.method, 'POST');
      assert.equal(c.headers['Neon-Connection-String'], DUMMY_URL);
      assert.equal(c.headers['Content-Type'], 'application/json');
      assert.ok(!c.url.includes('pass') && !c.url.includes('user'), 'credentials must not be in the URL');
    });

    it('answers 200 with only ok and the new id; it does not echo the submitted details or any secret', async () => {
      const res = await call(makeReq());
      assert.equal(res.statusCode, 200);
      assert.deepEqual(res.json, { ok: true, id: 1 });
      assertNoSecrets(res);
      for (const v of ['ada@example.com', 'Ada Example', 'Example Labs', '198.51.100.7', ipHash('198.51.100.7')]) {
        assert.ok(!res.raw.includes(v), 'response echoes "' + v + '"');
      }
    });

    it('stores a SHA-256 hash of the first forwarded address, never the address itself', async () => {
      const ip = '203.0.113.5';
      await call(makeReq({ headers: { 'x-forwarded-for': ip + ', 10.0.0.1, 10.0.0.2' } }));
      const all = JSON.stringify(neon.calls);
      assert.ok(!all.includes(ip), 'the raw address was sent to the database');
      assert.ok(!all.includes('10.0.0.1'));
      assert.equal(neon.inserts[0].params[8], ipHash(ip));
      assert.match(neon.inserts[0].params[8], /^[0-9a-f]{24}$/);
    });

    it('falls back to the socket address when there is no usable X-Forwarded-For', async () => {
      for (const xff of [undefined, '']) {
        neon.calls.length = 0;
        await call(makeReq({ headers: { 'x-forwarded-for': xff }, remoteAddress: '192.0.2.44' }));
        assert.equal(neon.inserts[0].params[8], ipHash('192.0.2.44'));
      }
    });
  });

  describe('rate limit (5 messages per connection in 10 minutes)', () => {
    const post = (ip) => call(makeReq({ headers: { 'x-forwarded-for': ip } }));

    it('accepts 5 messages from one connection and refuses the 6th with 429, storing nothing for it', async () => {
      for (let i = 1; i <= 5; i++) assert.equal((await post('198.51.100.7')).statusCode, 200, 'message ' + i);
      assert.equal(neon.rows.length, 5);
      const sixth = await post('198.51.100.7');
      assert.equal(sixth.statusCode, 429);
      assert.deepEqual(sixth.json, { error: 'Too many messages from this connection. Please try again later.' });
      assert.equal(neon.rows.length, 5);
      assert.equal(neon.calls[neon.calls.length - 1].query, COUNT_SQL, 'no insert after a refused request');
    });

    it('counts per connection: a different address is still accepted while the first is blocked', async () => {
      for (let i = 0; i < 5; i++) await post('198.51.100.7');
      assert.equal((await post('198.51.100.7')).statusCode, 429);
      assert.equal((await post('198.51.100.8')).statusCode, 200);
    });

    it('uses the first X-Forwarded-For entry as the connection (extra proxies do not change the bucket)', async () => {
      for (let i = 0; i < 5; i++) await post('203.0.113.5, 10.0.0.1');
      assert.equal((await post('203.0.113.5')).statusCode, 429);
      assert.equal((await post('10.0.0.1')).statusCode, 200);
    });

    it('boundary: 4 recent messages are allowed, 5 or more are refused', async () => {
      neon.seed(ipHash('198.51.100.7'), 4);
      assert.equal((await post('198.51.100.7')).statusCode, 200); // this is now the 5th
      assert.equal((await post('198.51.100.7')).statusCode, 429);
    });

    it('asks the database for the last 10 minutes only, filtered by the hash as a parameter', async () => {
      await post('198.51.100.7');
      assert.equal(neon.calls[0].query, COUNT_SQL);
      assert.deepEqual(neon.calls[0].params, [ipHash('198.51.100.7')]);
    });

    it('the window expires: blocked at 9 minutes, accepted again after 10 minutes', async () => {
      for (let i = 0; i < 5; i++) await post('198.51.100.7');
      neon.now += 9 * MINUTE;
      assert.equal((await post('198.51.100.7')).statusCode, 429);
      neon.now += 61 * 1000; // 10 minutes and 1 second after the 5 messages
      assert.equal((await post('198.51.100.7')).statusCode, 200);
    });

    it('older messages (11 minutes) do not count', async () => {
      neon.seed(ipHash('198.51.100.7'), 9, 11 * MINUTE);
      assert.equal((await post('198.51.100.7')).statusCode, 200);
    });

    it('invalid submissions are not stored and so do not use up the quota', async () => {
      for (let i = 0; i < 8; i++) await call(makeReq({ body: validBody({ email: 'bad' }) }));
      assert.equal((await post('198.51.100.7')).statusCode, 200);
    });
  });

  describe('database failure', () => {
    const SAFE = 'The message could not be saved. Please try again in a moment.';
    const leaky = () => new Error('connect ECONNREFUSED ' + DUMMY_URL + ' (host db.example.invalid)');

    it('network error that mentions the connection string: 500 with a fixed safe message', async () => {
      const spies = ['log', 'info', 'warn', 'error', 'debug'].map((m) => mock.method(console, m, () => {}));
      neon.failWhen = () => { throw leaky(); };
      const res = await call(makeReq());
      assert.equal(res.statusCode, 500);
      assert.deepEqual(res.json, { error: SAFE });
      assertNoSecrets(res);
      for (const spy of spies) {
        for (const c of spy.mock.calls) assert.ok(!JSON.stringify(c.arguments).includes('pass'), 'a secret was logged');
      }
    });

    it('Neon answers with an error message that contains the connection string: 500, message not passed on', async () => {
      neon.failWhen = () => neon.json(401, { message: 'password authentication failed for ' + DUMMY_URL });
      const res = await call(makeReq());
      assert.equal(res.statusCode, 500);
      assert.deepEqual(res.json, { error: SAFE });
      assertNoSecrets(res);
    });

    it('Neon answers with something that is not JSON: 500, safe message', async () => {
      neon.failWhen = () => new Response('<html>Bad gateway ' + DUMMY_URL + '</html>', { status: 502 });
      const res = await call(makeReq());
      assert.equal(res.statusCode, 500);
      assert.deepEqual(res.json, { error: SAFE });
      assertNoSecrets(res);
    });

    it('failure on the rate-limit query: 500 and no insert is attempted', async () => {
      neon.failWhen = (p) => (/^select count/.test(p.query) ? neon.json(500, { message: 'boom' }) : undefined);
      const res = await call(makeReq());
      assert.equal(res.statusCode, 500);
      assert.equal(neon.inserts.length, 0);
    });

    it('failure on the insert (the check passed): 500, safe message, nothing stored', async () => {
      neon.failWhen = (p) => (/^insert/.test(p.query) ? neon.json(500, { message: 'relation "leads" does not exist ' + DUMMY_URL }) : undefined);
      const res = await call(makeReq());
      assert.equal(res.statusCode, 500);
      assert.deepEqual(res.json, { error: SAFE });
      assertNoSecrets(res);
      assert.equal(neon.rows.length, 0);
    });

    it('a connection string that is not a URL fails safely (500) and is not echoed', async () => {
      process.env.LEADS_DATABASE_URL = 'this is not a url';
      const res = await call(makeReq());
      assert.equal(res.statusCode, 500);
      assert.deepEqual(res.json, { error: SAFE });
      assert.ok(!res.raw.includes('this is not a url'));
      assert.equal(neon.calls.length, 0);
    });
  });

  describe('environment variable LEADS_DATABASE_URL', () => {
    it('is read at call time: unset gives 503, setting it later works without reloading the module', async () => {
      delete process.env.LEADS_DATABASE_URL;
      const off = await call(makeReq());
      assert.equal(off.statusCode, 503);
      assert.deepEqual(off.json, { error: 'The form is not connected yet. Please try again later.' });
      assert.equal(neon.calls.length, 0);
      assertNoSecrets(off);

      process.env.LEADS_DATABASE_URL = DUMMY_URL;
      const on = await call(makeReq());
      assert.equal(on.statusCode, 200);
      assert.equal(neon.calls[0].url, 'https://db.example.invalid/sql');
    });

    it('an empty value counts as missing (503)', async () => {
      process.env.LEADS_DATABASE_URL = '';
      const res = await call(makeReq());
      assert.equal(res.statusCode, 503);
      assert.equal(neon.calls.length, 0);
    });

    it('a changed value is used on the next call (no caching of the host)', async () => {
      await call(makeReq());
      process.env.LEADS_DATABASE_URL = 'postgresql://other:secret@other-db.example.invalid/neondb';
      await call(makeReq());
      const hosts = [...new Set(neon.calls.map((c) => c.url))];
      assert.deepEqual(hosts, ['https://db.example.invalid/sql', 'https://other-db.example.invalid/sql']);
      assert.equal(neon.calls[neon.calls.length - 1].headers['Neon-Connection-String'], 'postgresql://other:secret@other-db.example.invalid/neondb');
    });

    it('does not fall back to DATABASE_URL or POSTGRES_URL', async () => {
      delete process.env.LEADS_DATABASE_URL;
      process.env.DATABASE_URL = DUMMY_URL;
      process.env.POSTGRES_URL = DUMMY_URL;
      const res = await call(makeReq());
      assert.equal(res.statusCode, 503);
      assert.equal(neon.calls.length, 0);
    });

    it('validation comes first: an invalid message gets 400 even when the variable is missing', async () => {
      delete process.env.LEADS_DATABASE_URL;
      const res = await call(makeReq({ body: validBody({ email: 'bad' }) }));
      assert.equal(res.statusCode, 400);
    });
  });
});
