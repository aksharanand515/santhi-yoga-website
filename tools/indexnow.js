#!/usr/bin/env node
/* ------------------------------------------------------------------
   Santhi Yoga India — tell search engines what changed

   IndexNow pushes URLs to Bing and Yandex straight away instead of
   waiting to be crawled. Bing matters beyond Bing itself: ChatGPT's
   search and Microsoft Copilot both read its index.

   Usage:
     node tools/indexnow.js            submit pages changed today
     node tools/indexnow.js 2026-09-20 submit pages changed on or after a date
     node tools/indexnow.js --all      submit every page in the sitemap

   Reads sitemap.xml, so run it after tools/build.js.
   ------------------------------------------------------------------ */
const fs = require('fs');
const path = require('path');
const https = require('https');

const ROOT = path.join(__dirname, '..');
const HOST = 'santhiyogaindia.com';
const KEY = '1fdd5937419f091330fd702f6be09c9b';

const keyFile = path.join(ROOT, KEY + '.txt');
if (!fs.existsSync(keyFile)) {
  console.error(`Missing ${KEY}.txt in the site root — IndexNow needs it to prove the site is yours.`);
  process.exit(1);
}

const sitemap = fs.readFileSync(path.join(ROOT, 'sitemap.xml'), 'utf8');
const entries = [...sitemap.matchAll(/<loc>([^<]+)<\/loc>\s*<lastmod>([^<]+)<\/lastmod>/g)]
  .map(([, loc, lastmod]) => ({ loc, lastmod }));

const arg = process.argv[2];
const since = arg === '--all' ? null : (arg || new Date().toISOString().slice(0, 10));
const urls = since ? entries.filter((e) => e.lastmod >= since).map((e) => e.loc) : entries.map((e) => e.loc);

if (!urls.length) {
  console.log(since ? `Nothing changed on or after ${since}.` : 'The sitemap is empty.');
  process.exit(0);
}

console.log(`Submitting ${urls.length} URL${urls.length === 1 ? '' : 's'}${since ? ` changed on or after ${since}` : ''}:`);
for (const u of urls) console.log('  ' + u);

const body = JSON.stringify({ host: HOST, key: KEY, keyLocation: `https://${HOST}/${KEY}.txt`, urlList: urls });

const req = https.request({
  hostname: 'api.indexnow.org', path: '/indexnow', method: 'POST',
  headers: { 'Content-Type': 'application/json; charset=utf-8', 'Content-Length': Buffer.byteLength(body) },
}, (res) => {
  let text = '';
  res.on('data', (d) => { text += d; });
  res.on('end', () => {
    // 200 and 202 both mean accepted; 202 means the key is still being checked.
    if (res.statusCode === 200 || res.statusCode === 202) console.log(`\nAccepted (HTTP ${res.statusCode}).`);
    else { console.error(`\nRejected (HTTP ${res.statusCode}). ${text.trim()}`); process.exit(1); }
  });
});
req.on('error', (e) => { console.error('\nCould not reach IndexNow: ' + e.message); process.exit(1); });
req.end(body);
