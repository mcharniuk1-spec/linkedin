// POST /api/lead: stores an enquiry from the contact form in a private Neon (Postgres) table. No dependencies; Neon's SQL-over-HTTP endpoint is called with fetch.
// Env: LEADS_DATABASE_URL (postgres connection string of a role that can INSERT and SELECT on table `leads` only). The table is created by the owner (see deploy/vercel/README.md).
const crypto = require('crypto');
const clean = (v, max) => String(v == null ? '' : v).replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F]/g, '').trim().slice(0, max);
const send = (res, code, obj) => { res.statusCode = code; res.setHeader('Content-Type', 'application/json; charset=utf-8'); res.setHeader('Cache-Control', 'no-store'); res.end(JSON.stringify(obj)); };
async function sql(cs, query, params) {
  const host = new URL(cs).host;
  const r = await fetch('https://' + host + '/sql', { method: 'POST', headers: { 'Neon-Connection-String': cs, 'Content-Type': 'application/json' }, body: JSON.stringify({ query, params }) });
  const j = await r.json();
  if (!r.ok) throw new Error(j && j.message ? j.message : 'database error');
  return j.rows || [];
}
module.exports = async function handler(req, res) {
  if (req.method !== 'POST') { res.setHeader('Allow', 'POST'); return send(res, 405, { error: 'Use POST.' }); }
  const origin = req.headers.origin, host = req.headers.host;
  if (origin) { try { if (new URL(origin).host !== host) return send(res, 403, { error: 'Not allowed.' }); } catch (e) { return send(res, 403, { error: 'Not allowed.' }); } }
  let body = req.body;
  if (typeof body === 'string') { try { body = JSON.parse(body); } catch (e) { body = {}; } }
  if (!body || typeof body !== 'object') body = {};
  if (body.website) return send(res, 200, { ok: true });                       // honeypot: bots fill it, people do not see it
  const name = clean(body.name, 120), email = clean(body.email, 200), company = clean(body.company, 160), service = clean(body.service, 80), context = clean(body.context, 4000);
  const consent = body.consent === true || body.consent === 'true' || body.consent === 'on';
  if (!name) return send(res, 400, { error: 'Please add your name.' });
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) return send(res, 400, { error: 'Please add a valid email address.' });
  if (context.length < 10) return send(res, 400, { error: 'Please tell us a little more about what you are building.' });
  if (!consent) return send(res, 400, { error: 'Please confirm that we may store your details to reply.' });
  const cs = process.env.LEADS_DATABASE_URL;
  if (!cs) return send(res, 503, { error: 'The form is not connected yet. Please try again later.' });
  const ip = String((req.headers['x-forwarded-for'] || '').split(',')[0] || req.socket.remoteAddress || '').trim();
  const ipHash = crypto.createHash('sha256').update(ip + '|outspoken-leads').digest('hex').slice(0, 24);
  try {
    const recent = await sql(cs, "select count(*)::int as n from leads where ip_hash = $1 and created_at > now() - interval '10 minutes'", [ipHash]);
    if (recent[0] && recent[0].n >= 5) return send(res, 429, { error: 'Too many messages from this connection. Please try again later.' });
    const rows = await sql(cs, 'insert into leads (name, email, company, service, context, consent, source, user_agent, ip_hash) values ($1,$2,$3,$4,$5,$6,$7,$8,$9) returning id', [name, email, company || null, service || null, context, true, clean(body.source, 80) || null, clean(req.headers['user-agent'], 300) || null, ipHash]);
    return send(res, 200, { ok: true, id: rows[0] && rows[0].id });
  } catch (e) {
    return send(res, 500, { error: 'The message could not be saved. Please try again in a moment.' });
  }
};
