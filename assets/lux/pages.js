/* Santhi School of Yoga & Vedanta Studies — page behaviour carried over from the first site:
   the services sub-navigation, the gallery page, the contact form, the reserve page and
   conversion tracking. lux.js holds everything written for the new design. */
(function () {
  'use strict';
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var $ = function (sel, ctx) { return (ctx || document).querySelector(sel); };
  var $$ = function (sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); };
  var lenis = null;

  /* ---------- Services page: sub-navigation highlights the section in view ---------- */
  (function () {
    var links = $$('.subnav a');
    if (!links.length || !('IntersectionObserver' in window)) return;
    var map = {};
    links.forEach(function (a) { var s = document.querySelector(a.getAttribute('href')); if (s) map[s.id] = a; });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        links.forEach(function (a) { a.classList.remove('is-current'); a.removeAttribute('aria-current'); });
        var a = map[entry.target.id];
        if (a) { a.classList.add('is-current'); a.setAttribute('aria-current', 'true'); a.scrollIntoView({ block: 'nearest', inline: 'center' }); }
      });
    }, { rootMargin: '-40% 0px -55% 0px' });
    Object.keys(map).forEach(function (id) { io.observe(document.getElementById(id)); });
  })();

  /* ---------- Gallery: filters + lightbox ---------- */
  (function () {
    var grid = $('[data-gallery]');
    if (!grid) return;
    var tiles = $$('.tile', grid), filters = $$('[data-filter]');
    filters.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var f = btn.dataset.filter;
        filters.forEach(function (b) { b.setAttribute('aria-pressed', String(b === btn)); });
        tiles.forEach(function (t) { t.hidden = !(f === 'all' || t.dataset.cat.split(' ').indexOf(f) > -1); });
        if (window.ScrollTrigger) ScrollTrigger.refresh();
      });
    });
    var box = $('#lightbox');
    if (!box || typeof box.showModal !== 'function') return;
    var bImg = $('img', box), bCap = $('.lightbox-caption', box), current = 0;
    function visible() { return tiles.filter(function (t) { return !t.hidden; }); }
    function show(tile) {
      var img = $('img', tile);
      bImg.src = img.dataset.large || img.currentSrc || img.src;
      bImg.alt = img.alt;
      bCap.textContent = $('figcaption b', tile) ? $('figcaption b', tile).textContent : '';
      current = visible().indexOf(tile);
    }
    tiles.forEach(function (tile) {
      $('.tile-btn', tile).addEventListener('click', function () { show(tile); box.showModal(); if (lenis) lenis.stop(); });
    });
    function step(d) { var v = visible(); if (!v.length) return; show(v[(current + d + v.length) % v.length]); }
    $('[data-lb-prev]', box).addEventListener('click', function () { step(-1); });
    $('[data-lb-next]', box).addEventListener('click', function () { step(1); });
    $('[data-lb-close]', box).addEventListener('click', function () { box.close(); });
    box.addEventListener('close', function () { if (lenis) lenis.start(); });
    box.addEventListener('click', function (e) { if (e.target === box) box.close(); });
    box.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft') step(-1);
      if (e.key === 'ArrowRight') step(1);
      if (e.key === 'Escape') { e.preventDefault(); box.close(); }
    });
  })();

  /* ---------- Contact: enquiry form (mailto by default, endpoint-ready) ---------- */
  (function () {
    var form = $('#enquiry-form');
    if (!form) return;
    var status = $('#form-status'), EMAIL = 'santhiyogacochin@gmail.com';
    var params = new URLSearchParams(window.location.search);
    if (params.get('interest')) {
      var sel = form.elements.interest;
      Array.prototype.forEach.call(sel.options, function (o) { if (o.text === params.get('interest')) sel.value = o.text; });
    }
    function setStatus(msg, ok) { status.textContent = msg; status.className = 'form-status ' + (ok ? 'is-ok' : 'is-error'); }
    function sent(method, interest) {
      if (typeof window.gtag === 'function') window.gtag('event', 'contact_form_send', { method: method, interest: interest });
    }
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var required = $$('[required]', form), invalid = required.filter(function (f) { return !f.checkValidity(); });
      required.forEach(function (f) { f.removeAttribute('aria-invalid'); });
      if (invalid.length) {
        invalid.forEach(function (f) { f.setAttribute('aria-invalid', 'true'); });
        invalid[0].focus();
        setStatus('Please add your name, a valid email address and what you are interested in.', false);
        return;
      }
      var d = {
        name: form.elements.name.value.trim(), email: form.elements.email.value.trim(), phone: form.elements.phone.value.trim(),
        interest: form.elements.interest.value, dates: form.elements.dates.value.trim(), message: form.elements.message.value.trim()
      };
      var endpoint = form.dataset.endpoint;
      if (endpoint) {
        setStatus('Sending…', true);
        fetch(endpoint, { method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify(d) })
          .then(function (r) { if (!r.ok) throw new Error(); sent('form', d.interest); form.reset(); setStatus('Thank you — your enquiry has been sent. We will reply soon.', true); })
          .catch(function () { setStatus('Your enquiry could not be sent. Email ' + EMAIL + ' or message us on WhatsApp.', false); });
        return;
      }
      var subject = 'Booking Inquiry - Santhi School of Yoga & Vedanta Studies' + (d.interest ? ' (' + d.interest + ')' : '');
      var body = ['Name: ' + d.name, 'Email: ' + d.email, 'WhatsApp / Phone: ' + (d.phone || '-'), 'Interested in: ' + d.interest, 'Preferred dates: ' + (d.dates || '-'), '', 'Message:', d.message || '-'].join('\r\n');
      sent('email', d.interest);
      window.location.href = 'mailto:' + EMAIL + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
      setStatus('Your email app should open with the enquiry ready to send. If it doesn’t, write to ' + EMAIL + '.', true);
    });

  })();

  /* ---------- Reserve: hold a teacher training place ----------
     Choosing a batch and typing a name fill in the ticket, the Wise payment
     reference and the confirmation message together. Batches that have
     already begun are closed, each one counts down to its first morning,
     and the choices are remembered on this device so a visitor who leaves
     to find a card comes back to the same reservation. /reserve/?batch=April
     (or ?month=April, as the booking page uses) preselects a batch. */
  (function () {
    var form = $('#reserve-form');
    if (!form) return;
    var WA = 'https://wa.me/917907714144', EMAIL = 'santhiyogacochin@gmail.com', KEY = 'santhi-reserve';
    var DEPOSIT = 90, BALANCE = 809, DAY = 864e5;
    var MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
    var batches = $$('.rsv-batch', form);
    var nameIn = $('#rv-name'), emailIn = $('#rv-email'), countryIn = $('#rv-country');
    var ticket = $('.ticket', form), status = $('#rv-status');
    var steps = $$('.rsv-step', form);
    var bar = $('#rsv-bar'), section = $('#reserve');
    var store = {
      get: function () { try { return JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) { return {}; } },
      set: function (v) { try { localStorage.setItem(KEY, JSON.stringify(v)); } catch (e) { /* private mode: nothing to keep */ } }
    };
    function track(name, params) { if (typeof window.gtag === 'function') window.gtag('event', name, params || {}); }

    // Dates are the school's: midnight in Kerala, whatever the visitor's clock says
    var now = Date.now();
    function startOf(label) { return new Date(label.dataset.start + 'T00:00:00+05:30').getTime(); }
    function daysTo(t) { return Math.ceil((t - now) / DAY); }
    function info(label) {
      var start = new Date(label.dataset.start + 'T12:00:00Z');
      var month = MONTHS[start.getUTCMonth()], year = start.getUTCFullYear();
      var due = new Date(start.getTime() + 2 * DAY);
      return {
        label: label, value: $('input', label).value, month: month, year: year,
        range: start.getUTCDate() + ' – ' + (start.getUTCDate() + 27) + ' ' + month + ' ' + year,
        due: due.getUTCDate() + ' ' + MONTHS[due.getUTCMonth()],
        days: daysTo(startOf(label)),
        code: month.slice(0, 3).toUpperCase() + String(year).slice(2)
      };
    }

    // Close batches that are under way; count down to the rest
    var open = batches.filter(function (label) {
      var d = daysTo(startOf(label)), soon = $('[data-soon]', label), input = $('input', label);
      if (d <= 0) {
        label.classList.add('is-past'); input.disabled = true; input.checked = false;
        if (soon) soon.textContent = 'Under way';
        return false;
      }
      if (soon) soon.textContent = d === 1 ? 'Begins tomorrow' : 'Begins in ' + d + ' days';
      return true;
    });

    // The next batch, for the hero and the bar
    var next = open.length ? info(open[0]) : null;
    $$('[data-next-month]').forEach(function (el) { if (next) el.textContent = next.month + ' ' + next.year; });
    $$('[data-next-countdown]').forEach(function (el) {
      if (next) el.textContent = 'Next batch · begins in ' + next.days + (next.days === 1 ? ' day' : ' days');
    });

    function current() {
      var input = $('input[name="batch"]:checked', form);
      return input ? info(input.closest('.rsv-batch')) : null;
    }
    function select(value) {
      var match = batches.filter(function (l) { return !l.classList.contains('is-past') && $('input', l).value.toLowerCase() === String(value || '').toLowerCase(); })[0];
      if (!match) match = open[0];
      if (match) $('input', match).checked = true;
    }

    // Restore: the address wins over what was remembered
    var saved = store.get();
    var params = new URLSearchParams(location.search);
    select(params.get('batch') || params.get('month') || saved.batch);
    if (saved.name) nameIn.value = saved.name;
    if (saved.email) emailIn.value = saved.email;
    if (saved.country) countryIn.value = saved.country;

    function setText(id, text) {
      var el = document.getElementById(id);
      if (!el || el.textContent === text) return;
      el.textContent = text;
      if (!reduceMotion) { el.classList.remove('is-new'); void el.offsetWidth; el.classList.add('is-new'); }
    }

    function reference(b) {
      var who = nameIn.value.trim().replace(/\s+/g, ' ').toUpperCase().slice(0, 22);
      return 'TTC ' + b.code + (who ? ' ' + who : '');
    }

    function message(b) {
      var name = nameIn.value.trim(), email = emailIn.value.trim(), country = countryIn.value.trim();
      var lines = [
        'Namaste Achu,',
        '',
        'I have paid the €' + DEPOSIT + ' deposit ' + (PAID_BY[method()] || 'by bank transfer') + ' to reserve my place on the 200-hour Teacher Training, ' + b.month + ' ' + b.year + ' batch (' + b.range + ').',
        '',
        'Name: ' + (name || '—'),
      ];
      if (email) lines.push('Email: ' + email);
      if (country) lines.push('Travelling from: ' + country);
      lines.push('Payment reference: ' + reference(b), '', 'I understand the balance of €' + BALANCE + ' is due by ' + b.due + ', within the first three days of the course. Could you confirm my place?', '', 'With thanks,', name || '');
      return lines.join('\n').trim();
    }

    // How the deposit is sent: the radios in step 3, remembered with the rest
    var PAID_BY = { card: 'by card', wise: 'with Wise', revolut: 'with Revolut', bank: 'by bank transfer', india: 'by IMPS/NEFT from India' };
    function method() { var m = $('input[name="method"]:checked', form); return m ? m.value : 'wise'; }
    // Card is the easiest way to pay, so it is chosen first whenever it is offered
    var cardOpt = $('.pm-opt--card', form), cardOn = cardOpt && !cardOpt.hidden;
    var want = saved.method && PAID_BY[saved.method] && (saved.method !== 'card' || cardOn) ? saved.method : (cardOn ? 'card' : '');
    if (want) { var mIn = $('input[name="method"][value="' + want + '"]', form); if (mIn) mIn.checked = true; }

    function update(fromUser) {
      var b = current();
      batches.forEach(function (l) { l.classList.toggle('is-on', $('input', l).checked); });
      if (!b) return;
      var name = nameIn.value.trim();
      setText('tk-month', b.month);
      setText('tk-year', String(b.year));
      setText('tk-range', b.range);
      setText('tk-due', b.due);
      var tkName = $('#tk-name');
      tkName.classList.toggle('is-empty', !name);
      setText('tk-name', name || 'your name');
      var soon = $('#tk-soon');
      soon.hidden = false;
      soon.textContent = 'Your first morning is ' + b.days + (b.days === 1 ? ' day' : ' days') + ' away';
      setText('rv-ref', reference(b));
      setText('rv-ref-wise', reference(b));
      // Achu's Wise link, opened with the amount and the booking reference filled in
      var wise = $('#rv-wise');
      if (wise && /wise\.com\/pay\//.test(wise.href)) {
        var base = wise.dataset.base || (wise.dataset.base = wise.href.split('?')[0]);
        wise.href = base + '?amount=' + DEPOSIT + '&currency=EUR&description=' + encodeURIComponent(reference(b));
      }
      var bm = $('#bar-month'); if (bm) bm.textContent = b.month + ' ' + b.year;

      var text = message(b);
      $('#rv-confirm').href = WA + '?text=' + encodeURIComponent(text);
      $('#rv-mail').href = 'mailto:' + EMAIL + '?subject=' + encodeURIComponent('Teacher training deposit paid: ' + b.month + ' ' + b.year + (name ? ', ' + name : '')) + '&body=' + encodeURIComponent(text);
      var ask = $('#rv-ask');
      if (ask) ask.href = WA + '?text=' + encodeURIComponent('Namaste Achu, I am thinking about the ' + b.month + ' ' + b.year + ' teacher training and have a question: ');

      // Which step is next
      var done = [true, !!name, !!saved.paid, false];
      steps.forEach(function (s, i) { s.classList.toggle('is-done', done[i]); });
      var active = done.indexOf(false);
      steps.forEach(function (s, i) { s.classList.toggle('is-active', i === active); });

      saved = Object.assign(saved, { method: method(), batch: b.value, name: name, email: emailIn.value.trim(), country: countryIn.value.trim() });
      store.set(saved);
      if (fromUser && ticket && !reduceMotion) { ticket.classList.remove('is-changing'); void ticket.offsetWidth; ticket.classList.add('is-changing'); }
    }

    form.addEventListener('change', function (e) {
      if (e.target.name === 'batch') {
        update(true);
        var b = current();
        track('reserve_select_batch', { batch: b.value + ' ' + b.year });
      } else if (e.target.name === 'method') {
        update(false);
        track('reserve_select_method', { method: e.target.value });
      }
    });
    [nameIn, emailIn, countryIn].forEach(function (el) {
      el.addEventListener('input', function () { el.removeAttribute('aria-invalid'); update(false); });
    });
    form.addEventListener('submit', function (e) { e.preventDefault(); });

    function setStatus(text, ok) {
      status.textContent = text;
      status.className = 'form-status ' + (ok ? 'is-ok' : 'is-error');
    }
    function needName() {
      if (nameIn.value.trim()) return false;
      nameIn.setAttribute('aria-invalid', 'true');
      nameIn.focus({ preventScroll: true });
      nameIn.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'center' });
      return true;
    }

    // Paying is never blocked; a missing name only means a vaguer reference
    $('#rv-wise').addEventListener('click', function () {
      var b = current();
      saved.paid = true; store.set(saved);
      steps[3].classList.add('is-ready');
      update(false);
      track('begin_checkout', { currency: 'EUR', value: DEPOSIT, items: [{ item_name: '200-hour TTC deposit', item_variant: b ? b.value + ' ' + b.year : '' }] });
    });

    var cardBtn = $('#rv-card');
    if (cardBtn) cardBtn.addEventListener('click', function () {
      var b = current();
      saved.paid = true; store.set(saved);
      steps[3].classList.add('is-ready');
      update(false);
      track('begin_checkout', { currency: 'EUR', value: DEPOSIT, payment_type: 'card', items: [{ item_name: '200-hour TTC deposit', item_variant: b ? b.value + ' ' + b.year : '' }] });
    });

    // The invoice: filled from the reservation, then printed, which on every
    // phone and computer can be saved as a PDF. The page title names the file.
    var invoice = $('#invoice');
    $$('[data-invoice]', form).forEach(function (btn) {
      btn.addEventListener('click', function () {
        if (!invoice || needName()) return;
        var b = current(), d = new Date();
        var fill = {
          ref: reference(b), name: nameIn.value.trim(), email: emailIn.value.trim(), country: countryIn.value.trim(),
          range: b.range, due: b.due + ' ' + b.year,
          date: d.getDate() + ' ' + MONTHS[d.getMonth()] + ' ' + d.getFullYear()
        };
        $$('[data-inv]', invoice).forEach(function (el) { el.textContent = fill[el.dataset.inv] || ''; });
        var title = document.title;
        document.title = 'Invoice ' + fill.ref;
        document.body.classList.add('is-invoicing');
        var done = function () { document.body.classList.remove('is-invoicing'); document.title = title; window.removeEventListener('afterprint', done); };
        window.addEventListener('afterprint', done);
        track('reserve_invoice', { batch: b.value + ' ' + b.year });
        window.print();
      });
    });

    // Copying a bank detail counts as starting to pay, by whichever method is chosen
    var bankBox = $('#rv-bank');
    if (bankBox) bankBox.addEventListener('click', function (e) {
      if (!e.target.closest('.rsv-copybtn') || saved.paid) return;
      saved.paid = true; store.set(saved);
      steps[3].classList.add('is-ready');
      update(false);
      track('begin_checkout', { currency: 'EUR', value: DEPOSIT, payment_type: method() });
    });

    ['#rv-confirm', '#rv-mail'].forEach(function (sel) {
      $(sel).addEventListener('click', function (e) {
        if (needName()) {
          e.preventDefault();
          setStatus('Add your name in step 2, so Achu can match your deposit to your place.', false);
          return;
        }
        var b = current();
        setStatus('Your confirmation is written out and ready to send. Achu will reply to confirm your place.', true);
        track('reserve_confirm', { method: sel === '#rv-confirm' ? 'whatsapp' : 'email', batch: b ? b.value + ' ' + b.year : '', currency: 'EUR', value: DEPOSIT });
      });
    });

    // Copy the amount and the reference
    $$('.rsv-copybtn', form).forEach(function (btn) {
      btn.addEventListener('click', function () {
        var text = btn.dataset.copy || (document.getElementById(btn.dataset.copyFrom) || {}).textContent || '';
        var label = btn.dataset.label || (btn.dataset.label = btn.textContent);
        var done = function () {
          btn.textContent = 'Copied'; btn.classList.add('is-copied');
          setTimeout(function () { btn.textContent = label; btn.classList.remove('is-copied'); }, 1800);
        };
        if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(done, function () {});
        else {
          var t = document.createElement('textarea'); t.value = text; t.setAttribute('readonly', ''); t.style.position = 'fixed'; t.style.opacity = '0';
          document.body.appendChild(t); t.select();
          try { document.execCommand('copy'); done(); } catch (err) { /* the text is on screen to copy by hand */ }
          t.remove();
        }
      });
    });

    // The bar: shown once the hero has gone, hidden while the reservation itself is in view
    if (bar && section && 'IntersectionObserver' in window) {
      var heroEl = $('.rsv-hero'), heroGone = false, inReserve = false, closing = false;
      var show = function () { bar.setAttribute('data-show', heroGone && !inReserve && !closing ? 'true' : 'false'); };
      new IntersectionObserver(function (en) { heroGone = !en[0].isIntersecting; show(); }).observe(heroEl);
      new IntersectionObserver(function (en) { inReserve = en[0].isIntersecting; show(); }, { rootMargin: '-35% 0px -35% 0px' }).observe(section);
      var close = $('.cta-band');
      if (close) new IntersectionObserver(function (en) { closing = en[0].isIntersecting; show(); }).observe(close);
    }

    update(false);
  })();

  /* ---------- Tools for AI agents in the browser (WebMCP) -------------
     A browser with an AI assistant built in can ask the page what it can
     do for the visitor. These are the four tools of the MCP server at /mcp,
     worked out here from llms.txt and the Markdown copy of each page that
     tools/build.js writes. They only read: the booking tool writes a
     WhatsApp message and returns the link, and the visitor presses send.
     WebMCP is still a draft, on document.modelContext in the spec and on
     navigator.modelContext in earlier builds, so both are tried. */
  (function () {
    var hosts = [document.modelContext, navigator.modelContext].filter(function (mc, i, all) {
      return mc && typeof mc.registerTool === 'function' && all.indexOf(mc) === i;
    });
    if (!hosts.length) return;

    var WA = 'https://wa.me/917907714144', EMAIL = 'santhiyogacochin@gmail.com';
    var readOnly = { readOnlyHint: true };
    var text = function (s, isError) { return { content: [{ type: 'text', text: s }], isError: !!isError }; };
    var get = function (path) {
      return fetch(path, { headers: { Accept: 'text/markdown, text/plain' } }).then(function (r) {
        if (!r.ok) throw new Error(path + ' answered ' + r.status);
        return r.text();
      });
    };
    var llms = null;
    var getLlms = function () { return llms || (llms = get('/llms.txt')); };
    // Every page listed in llms.txt; the "For AI agents" links are not pages
    var pages = function (doc) {
      var re = /^- \[([^\]]+)\]\(([^)]+\/)\): (.*)$/gm, m, out = [];
      while ((m = re.exec(doc))) out.push({ title: m[1], url: m[2], desc: m[3] });
      return out;
    };
    // "/about/", "about" or a full address on this site, as the path of its Markdown copy
    var mdPath = function (page) {
      var u = new URL(String(page || '/'), location.origin);
      if (u.origin !== location.origin && u.hostname !== 'santhiyogaindia.com') throw new Error('not this site');
      return u.pathname.replace(/index\.(html|md)$/, '').replace(/\/?$/, '/') + 'index.md';
    };

    var tools = [
      {
        name: 'get_school_facts',
        title: 'Key facts about the school',
        description: 'The current key facts about Santhi School of Yoga & Vedanta Studies in Fort Kochi, Kerala: address, class times, prices, teacher training dates and fees, the teacher, and how to get in touch.',
        inputSchema: { type: 'object', properties: {} },
        annotations: readOnly,
        execute: function () {
          return getLlms().then(function (doc) {
            var cut = doc.indexOf('\n## Main pages');
            return text((cut > 0 ? doc.slice(0, cut) : doc).trim());
          });
        }
      },
      {
        name: 'search_site',
        title: 'Search the site',
        description: 'Search the school\'s pages and its Journal of yoga, Ayurveda and Kerala travel guides. Returns the best matching pages with their address and a summary; read one with get_page.',
        inputSchema: {
          type: 'object',
          properties: {
            query: { type: 'string', description: 'What to look for, e.g. "pranayama for beginners" or "airport to Fort Kochi"' },
            limit: { type: 'integer', minimum: 1, maximum: 20, default: 8, description: 'How many pages to return' }
          },
          required: ['query']
        },
        annotations: readOnly,
        execute: function (input) {
          var terms = String((input && input.query) || '').toLowerCase().split(/[^\p{L}\p{N}]+/u).filter(function (t) { return t.length > 1; });
          var limit = Math.max(1, Math.min(20, (input && input.limit) || 8));
          if (!terms.length) return Promise.resolve(text('Give a query to search for.', true));
          return getLlms().then(function (doc) {
            var hits = pages(doc).map(function (p) {
              var t = p.title.toLowerCase(), d = p.desc.toLowerCase(), score = 0;
              terms.forEach(function (term) { score += 6 * t.split(term).length + 3 * d.split(term).length - 9; });
              return { p: p, score: score };
            }).filter(function (h) { return h.score > 0; }).sort(function (a, b) { return b.score - a.score; });
            if (!hits.length) return text('Nothing on the site matches that. The key facts are in get_school_facts; every page is listed at /llms.txt.');
            return text(hits.slice(0, limit).map(function (h) { return '- [' + h.p.title + '](' + h.p.url + '): ' + h.p.desc; }).join('\n'));
          });
        }
      },
      {
        name: 'get_page',
        title: 'Read a page',
        description: 'Read one page of santhiyogaindia.com as Markdown, e.g. "/teacher-training/", "/services/" or a Journal article address from search_site.',
        inputSchema: {
          type: 'object',
          properties: { path: { type: 'string', description: 'The page address or path, e.g. "/teacher-training/"' } },
          required: ['path']
        },
        annotations: readOnly,
        execute: function (input) {
          return Promise.resolve().then(function () { return get(mdPath(input && input.path)); }).then(function (md) { return text(md); }, function () {
            return text('No page at that address. Use search_site to find one, or see /llms.txt for every page.', true);
          });
        }
      },
      {
        name: 'draft_booking_message',
        title: 'Draft a booking message',
        description: 'Write an enquiry or booking message to the school and return a WhatsApp link and an email link that open with it filled in. Nothing is sent: the visitor opens a link and presses send. Classes need no booking; this is for questions, private sessions, retreats and the teacher training.',
        inputSchema: {
          type: 'object',
          properties: {
            name: { type: 'string', description: 'The name of the person enquiring' },
            interest: { type: 'string', enum: ['a daily Hatha Yoga class', 'a private session', 'the 200-hour teacher training', 'a retreat', 'a workshop', 'online classes', 'something else'], description: 'What they would like to join' },
            dates: { type: 'string', description: 'When, e.g. "12 to 15 March" or "the January 2027 batch"' },
            people: { type: 'integer', minimum: 1, maximum: 20, default: 1, description: 'How many people' },
            note: { type: 'string', description: 'Anything else the teacher should know: a question, an injury, where they are staying' }
          },
          required: ['name', 'interest']
        },
        annotations: readOnly,
        execute: function (input) {
          input = input || {};
          var who = String(input.name || '').trim(), what = String(input.interest || '').trim();
          if (!who || !what) return Promise.resolve(text('A name and what they would like to join are both needed.', true));
          var people = Math.max(1, Math.min(20, +input.people || 1));
          var dates = String(input.dates || '').trim(), note = String(input.note || '').trim();
          var msg = 'Namaste Achu,\n\nMy name is ' + who + ', and I would love to join ' + what +
            (dates ? ' (' + dates + ')' : '') + (people > 1 ? ' for ' + people + ' people' : '') + '.' +
            (note ? '\n\n' + note : '') + '\n\nWith thanks,\n' + who;
          return Promise.resolve(text('Message:\n\n' + msg +
            '\n\nSend it on WhatsApp (the school replies fastest there): ' + WA + '?text=' + encodeURIComponent(msg) +
            '\n\nOr by email: mailto:' + EMAIL + '?subject=' + encodeURIComponent('Enquiry: ' + what) + '&body=' + encodeURIComponent(msg) +
            '\n\nNothing has been sent. The visitor opens one of the links and presses send.'));
        }
      }
    ];

    hosts.forEach(function (mc) {
      tools.forEach(function (tool) {
        try {
          var done = mc.registerTool(tool);
          if (done && typeof done.catch === 'function') done.catch(function () {});
        } catch (err) { /* a tool the browser refuses is simply not offered */ }
      });
    });
  })();

  /* ---------- Conversion tracking -------------------------------------
     Sends a GA4 event when someone takes an action that could turn into a
     booking. booking_send, reserve_confirm, whatsapp_click and
     contact_form_send (sent by the contact form above) are marked as key
     events in GA4, so the "Key events" figure counts real enquiries. Analytics is optional: if the
     tag is blocked or absent, gtag() is simply undefined and nothing here
     runs. Clicks are captured on the document so links added later (the
     floating WhatsApp button, the booking preview) are covered too. */
  (function () {
    function track(name, params) {
      if (typeof window.gtag !== 'function') return;
      window.gtag('event', name, params || {});
    }

    /* Someone arriving from an ad (?utm_campaign=… or a Google gclid) keeps
       that name for the visit, and plain WhatsApp links end their message with
       it, e.g. "(ref: meta-ttc-jan)". Most enquiries arrive on WhatsApp, where
       Analytics can't see them, so this is how Achu knows which ad a chat came
       from. The booking and reserve forms write their own message, so they're left alone. */
    var adRef = '';
    try {
      var q = new URLSearchParams(location.search);
      adRef = q.get('utm_campaign') || (q.get('gclid') ? 'google-ad' : '');
      if (adRef) sessionStorage.setItem('santhi-ad', adRef.slice(0, 40));
      adRef = sessionStorage.getItem('santhi-ad') || '';
    } catch (err) { /* storage blocked: the ref is simply left off */ }

    document.addEventListener('click', function (e) {
      var link = e.target.closest ? e.target.closest('a[href]') : null;
      if (!link) return;
      if (adRef && link.hostname === 'wa.me' && link.id !== 'wa-send' && link.id !== 'rv-confirm') {
        var u = new URL(link.href), text = u.searchParams.get('text') || 'Namaste, I would like to know more about the teacher training.';
        if (text.indexOf('(ref: ') < 0) { u.searchParams.set('text', text + '\n\n(ref: ' + adRef + ')'); link.href = u.toString(); }
      }
      // The reserve page reports its own confirmation links as reserve_confirm
      if (link.id === 'rv-confirm' || link.id === 'rv-mail') return;
      var href = link.getAttribute('href') || '';
      var where = link.id === 'wa-send' ? 'booking_form'
        : link.closest('.dock') ? 'floating_button'
        : link.closest('.ft') ? 'footer'
        : link.closest('.hd, .menu') ? 'header'
        : 'page';

      if (link.id === 'wa-send' || link.id === 'mail-send') {
        // The booking form's send buttons carry the whole enquiry, so they are
        // the strongest signal of intent on the site.
        track('booking_send', {
          method: link.id === 'wa-send' ? 'whatsapp' : 'email',
          page_path: location.pathname
        });
      } else if (href.indexOf('wa.me') > -1) {
        track('whatsapp_click', { link_location: where, page_path: location.pathname });
      } else if (href.indexOf('tel:') === 0) {
        track('phone_click', { link_location: where, page_path: location.pathname });
      } else if (href.indexOf('mailto:') === 0) {
        track('email_click', { link_location: where, page_path: location.pathname });
      }
    }, true);
  })();
})();
