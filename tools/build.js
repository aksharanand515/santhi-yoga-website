#!/usr/bin/env node
/* ------------------------------------------------------------------
   Santhi Yoga India — page build
   Stamps the shared head, header, footer and icon sprite into every
   page between <!-- build:NAME --> ... <!-- /build:NAME --> markers, and
   prepares each page so it is fast and reads the same with or without
   JavaScript:
     • headings marked data-split are split into words here, not in the browser
     • photos get WebP srcsets from the files in assets/img (name-<width>.webp)
     • only the icons a page uses are inlined
     • assets/css/site.css and assets/js/site.js are minified to *.min.* with
       a cache-busting version
   Pages stay plain HTML that any host can serve as-is. Safe to run repeatedly.

   Usage: node tools/build.js
   ------------------------------------------------------------------ */
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

const ROOT = path.join(__dirname, '..');
const read = (p) => fs.readFileSync(path.join(ROOT, p), 'utf8');
const write = (p, s) => fs.writeFileSync(path.join(ROOT, p), s);

// Google Analytics 4 Measurement ID, e.g. 'G-ABC123XYZ'. Leave empty for no analytics.
const GA_ID = 'G-B04M93CEGM';

const pages = [
  { file: 'index.html',                  base: '',    key: 'home',     cta: true },
  { file: 'about/index.html',            base: '../', key: 'about',    cta: true },
  { file: 'services/index.html',         base: '../', key: 'services', cta: true },
  { file: 'teacher-training/index.html', base: '../', key: 'ttc',      cta: true },
  { file: 'gallery/index.html',          base: '../', key: 'gallery',  cta: true },
  { file: 'contact/index.html',          base: '../', key: 'contact',  cta: false },
  { file: 'book/index.html',             base: '../', key: 'book',     cta: false },
  // Served for any unknown address, so its links must be absolute, not relative.
  { file: '404.html',                    base: '/',   key: 'none',     cta: false },
];

/* Journal pages are discovered, not listed: drop a folder with an index.html
   under blog/ and it is built on the next run. blog/index.html is the hub,
   blog/<slug>/index.html an article. */
const blogDir = path.join(ROOT, 'blog');
if (fs.existsSync(blogDir)) {
  if (fs.existsSync(path.join(blogDir, 'index.html'))) {
    pages.push({ file: 'blog/index.html', base: '../', key: 'blog', cta: true });
  }
  for (const entry of fs.readdirSync(blogDir, { withFileTypes: true })) {
    if (!entry.isDirectory()) continue;
    const file = `blog/${entry.name}/index.html`;
    if (fs.existsSync(path.join(ROOT, file))) {
      pages.push({ file, base: '../../', key: 'blog', cta: false });
    }
  }
}

/* ---------- Minified CSS + JS with content versions ---------- */
function minifyCss(css) {
  const strings = [];
  return css
    .replace(/\/\*[\s\S]*?\*\//g, '') // comments first: they contain apostrophes
    .replace(/"[^"]*"|'[^']*'/g, (s) => `\u0000${strings.push(s) - 1}\u0000`)
    .replace(/\s+/g, ' ')
    .replace(/\s*([{};,>])\s*/g, '$1')
    .replace(/:\s+/g, ':')
    .replace(/;}/g, '}')
    .replace(/\u0000(\d+)\u0000/g, (_, i) => strings[i])
    .trim();
}
function minifyJs(js) {
  // Conservative: drop comments that start a line and indentation; keep line breaks
  return js
    .replace(/^\s*\/\*[\s\S]*?\*\/\s*$/gm, '')
    .replace(/^\s*\/\/.*$/gm, '')
    .replace(/^\s+/gm, '')
    .replace(/\n{2,}/g, '\n')
    .trim() + '\n';
}
const hash = (s) => crypto.createHash('sha1').update(s).digest('hex').slice(0, 8);
const css = minifyCss(read('assets/css/site.css'));
const js = minifyJs(read('assets/js/site.js'));
write('assets/css/site.min.css', css);
write('assets/js/site.min.js', js);
const versions = { css: hash(css), js: hash(js) };

/* ---------- Icons ---------- */
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
function sprite(ids) {
  const symbols = ids.map((id) => {
    const icon = lookup(ICONS[id]);
    if (!icon) throw new Error('Missing Solar icon: ' + ICONS[id]);
    const w = icon.width || solar.width || 24, h = icon.height || solar.height || 24;
    return `    <symbol id="i-${id}" viewBox="0 0 ${w} ${h}">${icon.body}</symbol>`;
  }).join('\n');
  return `  <!-- Icons: Solar by 480 Design (CC BY 4.0) via Iconify -->\n  <svg xmlns="http://www.w3.org/2000/svg" style="display:none" aria-hidden="true">\n${symbols}\n  </svg>`;
}

/* ---------- Partials ---------- */
const partials = { consent: read('partials/consent.html'), head: read('partials/head.html'), header: read('partials/header.html'), footer: read('partials/footer.html') };
const analytics = GA_ID ? `
  <!-- Google Analytics 4, loaded after the page has finished loading -->
  <script>
    window.dataLayer = window.dataLayer || []; function gtag() { dataLayer.push(arguments); }
    gtag('js', new Date()); gtag('config', '${GA_ID}');
    window.addEventListener('load', function () { var s = document.createElement('script'); s.async = true; s.src = 'https://www.googletagmanager.com/gtag/js?id=${GA_ID}'; document.head.appendChild(s); });
  </script>` : '';

function render(tpl, page) {
  let out = tpl
    .replace(/\{\{base\}\}/g, page.base)
    .replace(/\{\{home\}\}/g, page.base || './')
    .replace(/\{\{v:(css|js)\}\}/g, (_, k) => versions[k])
    .replace(/\s*<!--analytics-->/, analytics)
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

/* ---------- Headings split into words ----------
   <h2 data-split>Words <em>here</em></h2> becomes
   <h2 data-split aria-label="Words here"><span class="split-w" aria-hidden="true"><span class="split-i" style="--i:0">Words</span></span> <em aria-hidden="true">…</em></h2>
   The heading keeps its full text as its accessible name; the word spans are decorative. */
function unsplit(open, inner) {
  return [
    open.replace(/\s+aria-label="[^"]*"/, ''),
    inner.replace(/<span class="split-w" aria-hidden="true"><span class="split-i" style="--i:\d+">([\s\S]*?)<\/span><\/span>/g, '$1')
      .replace(/(<[a-z]+[^>]*?) aria-hidden="true"/g, '$1'),
  ];
}
function splitHeadings(html) {
  return html.replace(/(<(h[1-6])\b[^>]*\bdata-split\b[^>]*>)([\s\S]*?)(<\/\2>)/g, (m, openTag, tag, innerHtml, close) => {
    const [open, inner] = unsplit(openTag, innerHtml);
    const label = inner.replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim().replace(/"/g, '&quot;');
    let i = 0;
    const body = inner.split(/(<[^>]+>)/).map((part) => {
      if (!part) return '';
      if (part.startsWith('<')) {
        if (/^<\/|^<br\b/i.test(part)) return part;
        return part.replace(/^(<[a-z0-9]+)/i, '$1 aria-hidden="true"');
      }
      return part.split(/(\s+)/).map((w) => {
        if (!w) return '';
        if (/^\s+$/.test(w)) return ' ';
        return `<span class="split-w" aria-hidden="true"><span class="split-i" style="--i:${i++}">${w}</span></span>`;
      }).join('');
    }).join('');
    return `${open.replace(/>$/, ` aria-label="${label}">`)}${body}${close}`;
  });
}

/* ---------- Responsive WebP images ---------- */
const imgDir = path.join(ROOT, 'assets/img');
const variants = {};
for (const f of fs.readdirSync(imgDir)) {
  const m = f.match(/^(.+)-(\d+)\.webp$/);
  if (m) (variants[m[1]] = variants[m[1]] || []).push(Number(m[2]));
}
Object.values(variants).forEach((w) => w.sort((a, b) => a - b));

function responsiveImages(html, file, warn) {
  return html.replace(/<img\b[^>]*>/g, (tag) => {
    const m = tag.match(/\bsrc="((?:\.\.\/)*)assets\/img\/([a-z0-9-]+)-\d+\.(?:jpg|webp)"/);
    if (!m || !variants[m[2]]) return tag;
    const [, prefix, name] = m;
    const widths = variants[name];
    const url = (w) => `${prefix}assets/img/${name}-${w}.webp`;
    const fallback = widths.find((w) => w >= 800) || widths[widths.length - 1];
    let out = tag
      .replace(/\s+srcset="[^"]*"/, '')
      .replace(/\bsrc="[^"]*"/, `src="${url(fallback)}" srcset="${widths.map((w) => `${url(w)} ${w}w`).join(', ')}"`)
      .replace(/\bdata-large="[^"]*"/, `data-large="${url(widths[widths.length - 1])}"`);
    if (!/\bsizes="/.test(out)) warn(`${file}: image ${name} has no sizes attribute`);
    if (!/\balt="/.test(out)) warn(`${file}: image ${name} has no alt attribute`);
    return out;
  });
}

/* ---------- Build ---------- */
let errors = 0;
const warn = (msg) => { console.error(msg); errors++; };
for (const page of pages) {
  const file = path.join(ROOT, page.file);
  if (!fs.existsSync(file)) { warn('missing page ' + page.file); continue; }
  let html = fs.readFileSync(file, 'utf8').replace(/\r\n/g, '\n');
  html = stamp(html, 'consent', render(partials.consent, page), page.file);
  html = stamp(html, 'head', render(partials.head, page), page.file);
  html = stamp(html, 'header', render(partials.header, page), page.file);
  html = stamp(html, 'footer', render(partials.footer, page), page.file);
  html = splitHeadings(html);
  html = responsiveImages(html, page.file, warn);
  // Inline only the icons this page uses
  const used = [...new Set([...html.matchAll(/<use href="#i-([a-z-]+)"/g)].map((m) => m[1]))];
  const unknown = used.filter((id) => !ICONS[id]);
  if (unknown.length) warn(`${page.file}: unknown icons ${unknown.join(', ')}`);
  html = stamp(html, 'sprite', sprite(Object.keys(ICONS).filter((id) => used.includes(id))), page.file);
  // Sanity checks
  if ((html.match(/<h1[\s>]/g) || []).length !== 1) warn(`${page.file}: expected exactly one <h1>`);
  const title = (html.match(/<title>([^<]*)<\/title>/) || [])[1] || '';
  const desc = (html.match(/<meta name="description" content="([^"]*)"/) || [])[1] || '';
  const decode = (s) => s.replace(/&amp;/g, '&');
  if (decode(title).length > 60) warn(`${page.file}: title is ${decode(title).length} characters (keep it to 60)`);
  if (decode(desc).length < 110 || decode(desc).length > 160) warn(`${page.file}: meta description is ${decode(desc).length} characters (aim for 110–160)`);
  fs.writeFileSync(file, html);
  console.log('built ' + page.file);
}
if (errors) { console.error(errors + ' problem(s)'); process.exit(1); }
