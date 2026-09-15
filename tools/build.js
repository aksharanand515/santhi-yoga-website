#!/usr/bin/env node
/* ------------------------------------------------------------------
   Santhi Yoga India — page build
   Stamps the shared head, header, footer and icon sprite into every
   page between <!-- build:NAME --> ... <!-- /build:NAME --> markers.
   Pages stay plain HTML that any host can serve as-is.

   Usage: node tools/build.js
   ------------------------------------------------------------------ */
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const read = (p) => fs.readFileSync(path.join(ROOT, p), 'utf8');

const pages = [
  { file: 'index.html',                  base: '',    key: 'home',     cta: true },
  { file: 'services/index.html',         base: '../', key: 'services', cta: true },
  { file: 'teacher-training/index.html', base: '../', key: 'ttc',      cta: true },
  { file: 'gallery/index.html',          base: '../', key: 'gallery',  cta: true },
  { file: 'contact/index.html',          base: '../', key: 'contact',  cta: false },
];

// Solar icon set (480 Design, CC BY 4.0), fetched from the Iconify API into tools/icons/solar.json
const ICONS = {
  arrow: 'arrow-right-linear', 'arrow-left': 'arrow-left-linear', 'arrow-up-right': 'arrow-right-up-linear',
  chevron: 'alt-arrow-down-linear', check: 'check-circle-linear', phone: 'phone-calling-linear', mail: 'letter-linear',
  pin: 'map-point-linear', chat: 'chat-round-dots-linear', calendar: 'calendar-linear', sunrise: 'sunrise-linear',
  moon: 'moon-linear', user: 'user-linear', users: 'users-group-rounded-linear', book: 'book-2-linear',
  home: 'home-2-linear', cup: 'cup-hot-linear', compass: 'compass-linear', diploma: 'diploma-linear',
  wind: 'wind-linear', leaf: 'leaf-linear', heart: 'heart-linear', monitor: 'monitor-linear', send: 'plain-linear',
  close: 'close-circle-linear', gallery: 'gallery-wide-linear', clock: 'clock-circle-linear', star: 'star-bold',
  plus: 'add-circle-linear', map: 'map-linear', meditation: 'meditation-round-linear', notebook: 'notebook-linear',
  sun: 'sun-2-linear', zoom: 'magnifer-zoom-in-linear', global: 'global-linear', camera: 'camera-linear',
  route: 'routing-2-linear', question: 'question-circle-linear',
};
const solar = JSON.parse(read('tools/icons/solar.json'));
const lookup = (name) => {
  if (solar.icons[name]) return solar.icons[name];
  const alias = solar.aliases && solar.aliases[name];
  return alias ? Object.assign({}, lookup(alias.parent), alias) : null;
};
const symbols = Object.entries(ICONS).map(([id, name]) => {
  const icon = lookup(name);
  if (!icon) throw new Error('Missing Solar icon: ' + name);
  const w = icon.width || solar.width || 24, h = icon.height || solar.height || 24;
  return `    <symbol id="i-${id}" viewBox="0 0 ${w} ${h}">${icon.body}</symbol>`;
}).join('\n');
const sprite = `  <!-- Icons: Solar by 480 Design (CC BY 4.0) via Iconify -->\n  <svg xmlns="http://www.w3.org/2000/svg" style="display:none" aria-hidden="true">\n${symbols}\n  </svg>`;

const partials = { head: read('partials/head.html'), header: read('partials/header.html'), footer: read('partials/footer.html') };

function render(tpl, page) {
  let out = tpl
    .replace(/\{\{base\}\}/g, page.base)
    .replace(/\{\{home\}\}/g, page.base || './')
    .replace(/\{\{cur:([a-z]+)\}\}/g, (_, k) => (k === page.key ? ' aria-current="page"' : ''));
  if (!page.cta) out = out.replace(/\s*<!--cta-->[\s\S]*?<!--\/cta-->/, '');
  else out = out.replace(/<!--\/?cta-->\n?/g, '');
  return out.replace(/\s+$/, '');
}

function stamp(html, name, content, file) {
  const re = new RegExp(`(<!-- build:${name} -->)[\\s\\S]*?(<!-- /build:${name} -->)`);
  if (!re.test(html)) throw new Error(`${file}: missing build:${name} markers`);
  return html.replace(re, (_, open, close) => `${open}\n${content}\n  ${close}`);
}

let errors = 0;
for (const page of pages) {
  const file = path.join(ROOT, page.file);
  if (!fs.existsSync(file)) { console.error('missing page ' + page.file); errors++; continue; }
  let html = fs.readFileSync(file, 'utf8').replace(/\r\n/g, '\n');
  html = stamp(html, 'head', render(partials.head, page), page.file);
  html = stamp(html, 'sprite', sprite, page.file);
  html = stamp(html, 'header', render(partials.header, page), page.file);
  html = stamp(html, 'footer', render(partials.footer, page), page.file);
  // Sanity checks
  const ids = [...html.matchAll(/<use href="#i-([a-z-]+)"/g)].map((m) => m[1]).filter((id) => !ICONS[id]);
  if (ids.length) { console.error(`${page.file}: unknown icons ${[...new Set(ids)].join(', ')}`); errors++; }
  if ((html.match(/<h1[\s>]/g) || []).length !== 1) { console.error(`${page.file}: expected exactly one <h1>`); errors++; }
  fs.writeFileSync(file, html);
  console.log('built ' + page.file);
}
if (errors) { console.error(errors + ' problem(s)'); process.exit(1); }
