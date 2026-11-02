// Search and AI-answer readiness for the one-page site (proposed). Runs after `vite build`.
// - JSON-LD (Organization, WebSite, ProfessionalService with its offers, FAQPage) generated from the same JSON the page renders
// - <noscript> copy of the page's text for crawlers that do not run JavaScript (the same words the page shows, not extra text)
// - robots.txt, sitemap.xml and llms.txt
// - robots meta: the review edition stays noindex unless OUTSPOKEN_INDEXABLE=1 is set for a launch build
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const src = path.join(root, 'website-v3');
const dist = path.join(root, 'dist');
const read = f => JSON.parse(fs.readFileSync(path.join(src, f), 'utf8'));
const content = read('content.json'), pricing = read('pricing.json'), founders = read('founders.json'), details = read('service-details.json');
const SITE = (process.env.SITE_URL || 'https://outspoken-voice-7c4e2.vercel.app').replace(/\/$/, '');
const INDEXABLE = process.env.OUTSPOKEN_INDEXABLE === '1';
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
const plain = s => String(s).replace(/\*/g, '');
const modules = content.services.modules;
const faq = content.services.faq;
const packages = pricing.packages;

const jsonld = [
  {
    '@context': 'https://schema.org', '@type': 'Organization', '@id': SITE + '/#organization', name: 'OUTSPOKEN', url: SITE + '/',
    logo: SITE + '/assets/identity/v13/avatar-os-800.png', description: content.home.seo.description,
    founder: founders.founders.map(f => ({'@type': 'Person', name: f.name, jobTitle: f.role, sameAs: [f.href]})),
  },
  {'@context': 'https://schema.org', '@type': 'WebSite', '@id': SITE + '/#website', url: SITE + '/', name: 'OUTSPOKEN', inLanguage: 'en', publisher: {'@id': SITE + '/#organization'}},
  {
    '@context': 'https://schema.org', '@type': 'ProfessionalService', '@id': SITE + '/#service', name: 'OUTSPOKEN founder-led LinkedIn marketing', url: SITE + '/',
    description: content.home.seo.description, provider: {'@id': SITE + '/#organization'}, areaServed: 'Europe', inLanguage: 'en',
    audience: {'@type': 'BusinessAudience', audienceType: 'Europe-based B2B AI SaaS founders, seed to Series B'},
    hasOfferCatalog: {
      '@type': 'OfferCatalog', name: 'Services and indicative packages',
      itemListElement: [
        ...modules.map(m => ({'@type': 'Offer', itemOffered: {'@type': 'Service', name: m.title.replace(/,\s+/g, ', '), description: m.short + ' ' + m.body}})),
        ...packages.map(p => ({'@type': 'Offer', name: p.name, description: p.descriptor + ' Indicative package; final scope is confirmed together.', priceSpecification: {'@type': 'UnitPriceSpecification', price: p.price, priceCurrency: p.currency, unitText: p.period === 'month' ? 'month' : 'one-off'}})),
      ],
    },
  },
  {'@context': 'https://schema.org', '@type': 'FAQPage', mainEntity: [{question: details.definition.question, answer: details.definition.answer}, ...faq].map(f => ({'@type': 'Question', name: f.question, acceptedAnswer: {'@type': 'Answer', text: f.answer}}))},
];

const list = a => '<ul>' + a.map(x => '<li>' + esc(x) + '</li>').join('') + '</ul>';
const noscript = `<noscript><main data-static-copy="true">
<h1>${esc(content.protected.hero)}</h1>
<p>${esc(content.protected.vp)}</p>
<p>${esc(content.home.proofline)}</p>
<h2>${esc(plain(details.title))}</h2><p>${esc(details.intro)}</p>
<h3>${esc(details.definition.question)}</h3><p>${esc(details.definition.answer)}</p>
${modules.map(m => { const a = details.arguments[m.id]; return `<section><h3>${esc(m.number + ' ' + m.title.replace(/,\s+/g, ', '))}</h3><p><strong>${esc(plain(a.headline))}</strong></p><p>${esc(a.why)}</p><p>${esc(a.check)}</p><p>${esc(m.short)} ${esc(m.body)}</p>${list(m.deliverables)}<p>${esc(m.boundary)}</p></section>`; }).join('\n')}
<h2>${esc(pricing.public_label)}</h2>
${packages.map(p => `<section><h3>${esc(p.name)}: ${esc(p.display_price)}</h3><p>${esc(p.descriptor)}</p>${list(p.deliverables)}</section>`).join('\n')}
<p>${esc(pricing.tax_and_cost_note)}</p>
<h2>Before we begin</h2>
${faq.map(f => `<h3>${esc(f.question)}</h3><p>${esc(f.answer)}</p>`).join('\n')}
<h2>${esc(founders.title)}</h2><p>${esc(plain(founders.quote))}</p>
<ul>${founders.founders.map(f => `<li>${esc(f.name)}, ${esc(f.role)}: ${esc(f.bio)}</li>`).join('')}</ul>
<h2>Contact</h2><p>Tell us about the product, the people it helps and the part that is hard to explain. The contact form needs JavaScript. This is a design review edition: no call is booked and no email is sent from this page. Example people, posts and emails shown on the site are illustrative.</p>
</main></noscript>`;

let html = fs.readFileSync(path.join(dist, 'index.html'), 'utf8');
const robots = INDEXABLE ? 'index,follow,max-image-preview:large,max-snippet:-1' : 'noindex,nofollow';
html = html.replace(/<meta name="robots" content="[^"]*">/, `<meta name="robots" content="${robots}">`);
html = html.replace(/<link rel="canonical" href="[^"]*">/, `<link rel="canonical" href="${SITE}/">`);
const seo = content.home.seo, OG = SITE + '/assets/og/og-outspoken-1200x630.png';
html = html.replace(/<title>[^<]*<\/title>/, `<title>${esc(seo.title)}</title>`);
html = html.replace(/<meta name="description" content="[^"]*">/, `<meta name="description" content="${esc(seo.description)}">`);
html = html.replace(/<meta property="og:title" content="[^"]*">/, `<meta property="og:title" content="${esc(seo.title)}">`);
html = html.replace(/<meta property="og:description" content="[^"]*">/, `<meta property="og:description" content="${esc(seo.description)}"><meta property="og:url" content="${SITE}/"><meta property="og:image" content="${OG}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="OUTSPOKEN: founder-led LinkedIn marketing for B2B AI SaaS founders"><meta property="og:locale" content="en"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="${esc(seo.title)}"><meta name="twitter:description" content="${esc(seo.description)}"><meta name="twitter:image" content="${OG}">`);
html = html.replace('</head>', jsonld.map(o => `<script type="application/ld+json">${JSON.stringify(o).replace(/</g, '\\u003c')}</script>`).join('') + '</head>');
html = html.replace('<div id="root"></div>', '<div id="root"></div>' + noscript);
fs.writeFileSync(path.join(dist, 'index.html'), html);

fs.writeFileSync(path.join(dist, 'robots.txt'), `# OUTSPOKEN. The review edition keeps the page-level noindex until the owner launches (build with OUTSPOKEN_INDEXABLE=1).\nUser-agent: *\nAllow: /\n\nSitemap: ${SITE}/sitemap.xml\n`);
const today = new Date().toISOString().slice(0, 10);
fs.writeFileSync(path.join(dist, 'sitemap.xml'), `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n  <url><loc>${SITE}/</loc><lastmod>${today}</lastmod><changefreq>monthly</changefreq><priority>1.0</priority></url>\n  <url><loc>${SITE}/credits</loc><lastmod>${today}</lastmod><changefreq>yearly</changefreq><priority>0.2</priority></url>\n</urlset>\n`);
const llms = `# OUTSPOKEN

> ${content.home.seo.description}

OUTSPOKEN is a founder-led LinkedIn marketing studio for Europe-based B2B AI SaaS founders, seed to Series B. This is a one-page site; every section below is a block of ${SITE}/.

## What we do
${modules.map(m => `- [${m.title.replace(/,\s+/g, ', ')}](${SITE}/#services): ${m.short}`).join('\n')}

## Indicative packages (EUR; final scope is confirmed together; taxes, tools and media spend are extra)
${packages.map(p => `- ${p.name}: ${p.display_price}. ${p.descriptor}`).join('\n')}

## Answers
${faq.map(f => `- ${f.question} ${f.answer}`).join('\n')}

## Notes
- The people, posts and emails shown on the site are illustrative. No customer result is claimed.
- We do not guarantee leads, rankings or sales.
- Contact: use the form at ${SITE}/#contact (review edition: no call is booked and no email is sent).
`;
fs.writeFileSync(path.join(dist, 'llms.txt'), llms);
console.log(JSON.stringify({site: SITE, robots, jsonld: jsonld.length, noscript_bytes: noscript.length, files: ['robots.txt', 'sitemap.xml', 'llms.txt']}));
