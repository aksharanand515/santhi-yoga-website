/* Santhi School of Yoga & Vedanta Studies — "lux" behaviour.
   No libraries. Everything here is an enhancement: the pages read, link and
   book without it. */
(function () {
  'use strict';
  var d = document, root = d.documentElement;
  var $ = function (s, c) { return (c || d).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || d).querySelectorAll(s)); };
  var WA = 'https://wa.me/917907714144', EMAIL = 'santhiyogacochin@gmail.com';
  function track(name, params) { if (typeof window.gtag === 'function') window.gtag('event', name, params || {}); }

  /* ---------- Reveal on scroll ---------- */
  var items = $$('[data-r], [data-reveal], [data-clip]');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      var n = 0;
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        e.target.style.setProperty('--d', n++);
        e.target.classList.add('in');
        io.unobserve(e.target);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    items.forEach(function (el) { io.observe(el); });
  } else { root.classList.add('show-all'); }

  /* ---------- Header: solid after the hero's first lines, away while reading down ---------- */
  var hd = $('#hd'), dock = $('#dock'), last = 0, ticking = false;
  function onScroll() {
    var y = window.scrollY;
    hd.classList.toggle('is-solid', y > 24);
    hd.classList.toggle('is-away', y > 600 && y > last && !root.classList.contains('menu-open'));
    if (dock) {
      var nearEnd = y + innerHeight > d.body.scrollHeight - 500;
      dock.setAttribute('data-show', y > innerHeight * 0.7 && !nearEnd ? 'true' : 'false');
    }
    last = y; ticking = false;
  }
  addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(onScroll); } }, { passive: true });
  onScroll();

  /* ---------- Hero: the photographs in the doorway change, and the page leans to the pointer ---------- */
  (function () {
    var hero = $('[data-hero]'); if (!hero) return;
    var calm = matchMedia('(prefers-reduced-motion: reduce)').matches;
    var box = $('[data-hero-slides]', hero), slides = $$('.hero-slide', box), cap = $('.hero-cap', hero);
    var num = $('[data-hero-n]', hero), label = $('[data-hero-cap]', hero);
    var i = 0, timer = 0, seen = true;

    // Later photographs carry only a name, so nothing competes with the first one while the page loads
    function load(slide) {
      var im = $('img', slide), name = im.getAttribute('data-img');
      if (!name) return im;
      var base = 'assets/img/' + name + '-';
      im.removeAttribute('data-img');
      im.srcset = base + '480.webp 480w, ' + base + '800.webp 800w, ' + base + '1200.webp 1200w';
      im.src = base + '800.webp';
      return im;
    }
    function queue() {
      clearTimeout(timer);
      timer = setTimeout(function () { if (seen && !d.hidden) show((i + 1) % slides.length); else queue(); }, 6500);
    }
    function show(n) {
      var next = slides[n], im = load(next);
      function go() {
        slides.forEach(function (s) { s.classList.remove('is-prev'); });
        slides[i].classList.replace('is-on', 'is-prev');
        next.classList.add('is-on');
        i = n;
        num.textContent = '0' + (n + 1);
        label.textContent = next.getAttribute('data-cap');
        cap.classList.remove('run'); void cap.offsetWidth; cap.classList.add('run');
        load(slides[(n + 1) % slides.length]);
        queue();
      }
      if (im.complete && im.naturalWidth) go();
      else { im.addEventListener('load', go, { once: true }); im.addEventListener('error', queue, { once: true }); }
    }
    if (!calm && slides.length > 1) {
      var start = function () { box.classList.add('is-live'); cap.classList.add('run'); load(slides[1]); queue(); };
      if (d.readyState === 'complete') start(); else addEventListener('load', start);
    }
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (e) { seen = e[0].isIntersecting; hero.classList.toggle('is-off', !seen); }).observe(hero);
    }

    if (calm || !matchMedia('(hover: hover) and (pointer: fine)').matches) return;
    var tx = 0, ty = 0, cx = 0, cy = 0, raf = 0;
    function frame() {
      cx += (tx - cx) * 0.06; cy += (ty - cy) * 0.06;
      hero.style.setProperty('--px', cx.toFixed(3));
      hero.style.setProperty('--py', cy.toFixed(3));
      raf = Math.abs(tx - cx) + Math.abs(ty - cy) > 0.002 ? requestAnimationFrame(frame) : 0;
    }
    function aim(x, y) { tx = x; ty = y; if (!raf) raf = requestAnimationFrame(frame); }
    hero.addEventListener('pointermove', function (e) {
      var r = hero.getBoundingClientRect();
      aim((e.clientX - r.left) / r.width * 2 - 1, (e.clientY - r.top) / r.height * 2 - 1);
    });
    hero.addEventListener('pointerleave', function () { aim(0, 0); });
  })();

  /* ---------- Menu ---------- */
  var burger = $('#burger'), menu = $('#menu');
  function setMenu(open) {
    root.classList.toggle('menu-open', open);
    burger.setAttribute('aria-expanded', open);
    menu.setAttribute('aria-hidden', !open);
    burger.firstElementChild.textContent = open ? 'Close menu' : 'Open menu';
    if (open) { var a = $('a', menu); if (a) setTimeout(function () { a.focus(); }, 350); }
  }
  if (burger) {
    $$('.menu-list li', menu).forEach(function (li, i) { li.style.setProperty('--i', i); });
    burger.addEventListener('click', function () { setMenu(!root.classList.contains('menu-open')); });
    menu.addEventListener('click', function (e) { if (e.target.closest('a')) setMenu(false); });
    addEventListener('keydown', function (e) { if (e.key === 'Escape' && root.classList.contains('menu-open')) { setMenu(false); burger.focus(); } });
  }

  /* ---------- The time in Fort Kochi, and the next class ----------
     Classes run every day, 7:30–9:30 am and 3:30–5:30 pm, India time. */
  (function () {
    var slots = [[450, 570, '7:30 am'], [930, 1050, '3:30 pm']];
    function tick() {
      var p = new Intl.DateTimeFormat('en-GB', { timeZone: 'Asia/Kolkata', hour: '2-digit', minute: '2-digit', hour12: false }).formatToParts(new Date());
      var h = +p[0].value % 24, m = +p[2].value, now = h * 60 + m, live = false, msg = '';
      for (var i = 0; i < slots.length; i++) {
        if (now >= slots[i][0] && now < slots[i][1]) { live = true; msg = 'A class is in session now'; break; }
        if (now < slots[i][0]) { var w = slots[i][0] - now; msg = 'Next class ' + slots[i][2] + ', in ' + (w >= 60 ? Math.floor(w / 60) + ' h ' : '') + (w % 60) + ' min'; break; }
      }
      if (!msg) msg = 'Next class 7:30 am tomorrow';
      var clock = (h < 10 ? '0' : '') + h + ':' + (m < 10 ? '0' : '') + m;
      $$('[data-now]').forEach(function (el) { el.hidden = false; el.classList.toggle('is-live', live); $('[data-now-text]', el).textContent = 'Fort Kochi ' + clock; el.title = msg; });
      $$('[data-live]').forEach(function (el) { el.hidden = false; el.classList.toggle('is-live', live); $('[data-live-text]', el).textContent = clock + ' in Fort Kochi · ' + msg; });
    }
    try { tick(); setInterval(tick, 30000); } catch (e) { /* no Intl time zones: leave the clock out */ }
  })();

  /* ---------- Numbers that count up once ---------- */
  if ('IntersectionObserver' in window && !matchMedia('(prefers-reduced-motion: reduce)').matches) {
    var co = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        co.unobserve(e.target);
        var el = e.target, to = +el.getAttribute('data-count-to'), t0 = performance.now();
        (function step(t) {
          var k = Math.min(1, (t - t0) / 1600), v = Math.round(to * (1 - Math.pow(1 - k, 4)));
          el.textContent = v.toLocaleString('en-GB');
          if (k < 1) requestAnimationFrame(step);
        })(t0);
      });
    }, { threshold: 0.6 });
    $$('[data-count-to]').forEach(function (el) { co.observe(el); });
  }

  /* ---------- Gallery: filter chips and a full-screen lightbox ---------- */
  $$('[data-chips]').forEach(function (bar) {
    var reel = bar.closest('section').querySelector('[data-reel]');
    bar.addEventListener('click', function (e) {
      var b = e.target.closest('.chip'); if (!b) return;
      var cat = b.getAttribute('data-cat');
      $$('.chip', bar).forEach(function (c) { var on = c === b; c.classList.toggle('on', on); c.setAttribute('aria-pressed', on); });
      $$('.reel-card', reel).forEach(function (c) { c.classList.toggle('off', cat !== 'all' && c.getAttribute('data-cat') !== cat); });
      reel.scrollTo({ left: 0, behavior: 'smooth' });
      track('gallery_filter', { category: cat });
    });
  });
  // The wheel always scrolls the page. With a mouse, the reel is dragged sideways
  // (touch and trackpads already scroll it), and a drag never opens a photograph.
  $$('[data-reel]').forEach(function (reel) {
    var x0 = 0, left0 = 0, down = false, moved = false;
    reel.addEventListener('pointerdown', function (e) {
      if (e.pointerType !== 'mouse' || e.button !== 0) return;
      down = true; moved = false; x0 = e.clientX; left0 = reel.scrollLeft;
    });
    addEventListener('pointermove', function (e) {
      if (!down) return;
      var dx = e.clientX - x0;
      if (!moved && Math.abs(dx) < 6) return;
      if (!moved) { moved = true; reel.classList.add('is-drag'); }
      reel.scrollLeft = left0 - dx;
    });
    addEventListener('pointerup', function () {
      if (!down) return;
      down = false;
      if (moved) setTimeout(function () { reel.classList.remove('is-drag'); moved = false; }, 0);
    });
    reel.addEventListener('dragstart', function (e) { e.preventDefault(); });
    reel.addEventListener('click', function (e) { if (moved) { e.preventDefault(); e.stopPropagation(); } }, true);
  });
  (function () {
    var lb, img, cap, num, set = [], at = 0, opener;
    function build() {
      lb = d.createElement('dialog'); lb.className = 'lb'; lb.setAttribute('aria-label', 'Photograph');
      lb.innerHTML = '<div class="lb-top"><span data-n></span><button class="rnd" type="button" data-x aria-label="Close"><svg class="ic" viewBox="0 0 24 24"><path d="M6 6l12 12M18 6 6 18" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg></button></div>' +
        '<div class="lb-stage"><img alt=""></div>' +
        '<div class="lb-bot"><p></p><div><button class="rnd" type="button" data-p aria-label="Previous photograph"><svg class="ic flip"><use href="#i-arrow"/></svg></button><button class="rnd" type="button" data-nx aria-label="Next photograph"><svg class="ic"><use href="#i-arrow"/></svg></button></div></div>';
      d.body.appendChild(lb);
      img = $('img', lb); cap = $('.lb-bot p', lb); num = $('[data-n]', lb);
      $('[data-x]', lb).addEventListener('click', function () { lb.close(); });
      $('[data-p]', lb).addEventListener('click', function () { show(at - 1); });
      $('[data-nx]', lb).addEventListener('click', function () { show(at + 1); });
      lb.addEventListener('keydown', function (e) { if (e.key === 'ArrowLeft') show(at - 1); if (e.key === 'ArrowRight') show(at + 1); });
      lb.addEventListener('close', function () { if (opener) opener.focus(); });
      var x0 = null;
      lb.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
      lb.addEventListener('touchend', function (e) { if (x0 === null) return; var dx = e.changedTouches[0].clientX - x0; if (Math.abs(dx) > 50) show(at + (dx < 0 ? 1 : -1)); x0 = null; }, { passive: true });
    }
    function show(i) {
      at = (i + set.length) % set.length;
      var a = set[at], small = $('img', a), fresh = img.cloneNode();
      fresh.src = a.href; fresh.alt = small.alt;
      img.replaceWith(fresh); img = fresh;
      cap.textContent = $('b', a).textContent + ' · ' + $('i', a).textContent;
      num.textContent = (at + 1 < 10 ? '0' : '') + (at + 1) + ' / ' + (set.length < 10 ? '0' : '') + set.length;
    }
    d.addEventListener('click', function (e) {
      var a = e.target.closest('a[data-lb]');
      if (!a || !('HTMLDialogElement' in window) || e.metaKey || e.ctrlKey) return;
      e.preventDefault();
      if (!lb) build();
      set = $$('a[data-lb]:not(.off)', a.parentNode); opener = a;
      show(set.indexOf(a)); lb.showModal();
      track('gallery_open', { photo: $('b', a).textContent });
    });
  })();

  /* ---------- Student stories ---------- */
  $$('[data-stories]').forEach(function (rail) {
    var sec = rail.closest('section'), n = rail.children.length, count = $('[data-count]', sec);
    function at() { return Math.round(rail.scrollLeft / (rail.scrollWidth / n)); }
    function go(i) { var k = (i + n) % n; rail.scrollTo({ left: rail.children[k].offsetLeft - rail.offsetLeft, behavior: 'smooth' }); }
    $('[data-prev]', sec).addEventListener('click', function () { go(at() - 1); });
    $('[data-next]', sec).addEventListener('click', function () { go(at() + 1); });
    rail.addEventListener('keydown', function (e) { if (e.key === 'ArrowRight') go(at() + 1); if (e.key === 'ArrowLeft') go(at() - 1); });
    var t; rail.addEventListener('scroll', function () { clearTimeout(t); t = setTimeout(function () { count.textContent = (at() + 1) + ' / ' + n; }, 80); }, { passive: true });
  });

  /* ---------- The booking journey ---------- */
  (function () {
    var f = $('#journey'); if (!f) return;
    var step = 1, steps = $$('.jr-steps li', f), back = $('[data-back]', f), status = $('#jr-status');
    var wa = $('#wa-send'), mail = $('#mail-send'), reserve = $('[data-reserve]', f), letter = $('[data-letter]', f);
    var preset = f.getAttribute('data-preset');
    var first = $(preset === 'ttc' ? 'input[data-kind="batch"]' : 'input[name="what"]', f);
    first.checked = true;
    var date = f.elements.date, today = new Date();
    date.min = new Date(today.getTime() - today.getTimezoneOffset() * 6e4).toISOString().slice(0, 10);
    // arriving from a link such as #book?batch=April or ?batch=April picks that month
    var q = (location.search + location.hash).match(/batch=(\w+)/);
    if (q) $$('input[name="batch"]', f).forEach(function (r) { if (r.value.toLowerCase() === q[1].toLowerCase()) { r.checked = true; $('input[data-kind="batch"]', f).checked = true; } });

    function what() { return $('input[name="what"]:checked', f); }
    function isBatch() { return what().getAttribute('data-kind') === 'batch'; }
    function nice(v) { var p = v.split('-'); return new Date(p[0], p[1] - 1, p[2]).toLocaleDateString('en-GB', { weekday: 'long', day: 'numeric', month: 'long' }); }
    function text() {
      var name = f.elements.name.value.trim(), from = f.elements.country.value.trim(), note = f.elements.note.value.trim(), w = what();
      var when = isBatch() ? 'in the ' + f.elements.batch.value + ' 2027 batch' : (date.value ? 'on ' + nice(date.value) : 'on a date of my choice');
      return 'Namaste Achu,\n\nMy name is ' + (name || '…') + (from ? ', writing from ' + from : '') + ', and I would love to join ' + w.value + ' ' + when + ' for ' + f.elements.people.value + '. ' + w.getAttribute('data-ask') +
        (note ? '\n\n' + note : '') + '\n\nWith thanks,\n' + (name || '');
    }
    function paint() {
      f.setAttribute('data-at', step);
      steps.forEach(function (li, i) { li.classList.toggle('on', i < step); });
      back.hidden = step === 1;
      var b = isBatch();
      $('[data-when="batch"]', f).hidden = !b; $('[data-when="date"]', f).hidden = b;
      $('[data-when-title]', f).textContent = b ? 'Which month would you like?' : 'When would you like to come?';
      reserve.hidden = !(b && step === 3);
      if (b) reserve.href = reserve.href.split('?')[0] + '?batch=' + f.elements.batch.value;
      var t = text();
      letter.textContent = t;
      if (f.elements.name.value.trim()) {
        wa.href = WA + '?text=' + encodeURIComponent(t);
        mail.href = 'mailto:' + EMAIL + '?subject=' + encodeURIComponent('Booking: ' + what().value.replace(/^(a|an|the) /, '')) + '&body=' + encodeURIComponent(t);
      } else { wa.removeAttribute('href'); mail.removeAttribute('href'); }
    }
    function move(to) {
      step = to; paint();
      var target = $('[data-step="' + step + '"] input, [data-step="' + step + '"] select', f);
      if (step === 3) target = f.elements.name;
      if (target && matchMedia('(hover: hover)').matches) target.focus({ preventScroll: true });
      var r = f.getBoundingClientRect(); if (r.top < 0) scrollTo({ top: scrollY + r.top - 90, behavior: 'smooth' });
    }
    $('[data-next]', f).addEventListener('click', function () { move(step + 1); track('booking_step', { step: step, what: what().value }); });
    back.addEventListener('click', function () { move(step - 1); });
    f.addEventListener('input', paint); f.addEventListener('change', paint);
    f.addEventListener('submit', function (e) { e.preventDefault(); });
    [wa, mail].forEach(function (a) {
      a.addEventListener('click', function (e) {
        var name = f.elements.name;
        if (!name.value.trim()) {
          name.setAttribute('aria-invalid', 'true'); name.focus();
          status.textContent = 'Add your name so Achu knows who is writing.'; status.className = 'status err';
          return;
        }
        name.removeAttribute('aria-invalid');
        status.textContent = 'Your letter is open in ' + (a === wa ? 'WhatsApp' : 'your email') + '. Press send there, and Achu will reply personally.'; status.className = 'status';
      });
    });
    paint();
  })();

  /* ---------- Newsletter: tonight's moon, and the letter ----------
     The moon is drawn at tonight's phase from the mean synodic month. With a
     data-endpoint the form posts to the Apps Script in tools/newsletter;
     without one it opens a prefilled email instead. */
  (function () {
    var form = $('#nl-form'); if (!form) return;
    var DAY = 864e5, MONTH = 29.530588853, NEW_MOON = Date.UTC(2000, 0, 6, 18, 14);
    var status = $('#nl-status'), note = $('[data-moon-note]'), lit = $('#nl-lit');
    var age = (((Date.now() - NEW_MOON) / DAY) % MONTH + MONTH) % MONTH, phase = age / MONTH;
    var nextFull = new Date(Date.now() + (((MONTH / 2 - age) % MONTH + MONTH) % MONTH) * DAY);
    var c = Math.cos(2 * Math.PI * phase), waxing = phase < 0.5;
    function day(x) { return x.toLocaleDateString('en-GB', { day: 'numeric', month: 'long', timeZone: 'Asia/Kolkata' }); }
    if (lit) lit.setAttribute('d', 'M60,6 A54,54 0 0,' + (waxing ? 1 : 0) + ' 60,114 A' + (Math.abs(c) * 54).toFixed(2) + ',54 0 0,' + ((waxing ? c > 0 : c < 0) ? 0 : 1) + ' 60,6Z');
    if (note) note.innerHTML = Math.abs(age - MONTH / 2) < 0.75
      ? 'The moon is <b>full</b> over Fort Kochi tonight'
      : 'Tonight the moon is <b>' + Math.round((1 - c) * 50) + '% full</b>. The next full moon is on <b>' + day(nextFull) + '</b>';

    function say(msg, ok) { status.textContent = msg; status.className = 'status' + (ok ? '' : ' err'); }
    function posted(name, method) {
      track('newsletter_signup', { method: method, page_path: location.pathname });
      $$('input', form).forEach(function (i) { i.readOnly = true; });
      $('button', form).disabled = true; $('[data-nl-label]', form).textContent = 'Sealed';
      say('Posted' + (name ? ', ' + name : '') + '. A short note is on its way now, and the letters follow each full moon. The next one rises on ' + day(nextFull) + '.', true);
    }
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var email = form.elements.email, address = email.value.trim(), name = form.elements.name.value.trim();
      email.removeAttribute('aria-invalid');
      if (!address || !email.checkValidity()) { email.setAttribute('aria-invalid', 'true'); email.focus(); say('Add an email address so the letters can find you.', false); return; }
      if (form.elements.website.value) return;
      var endpoint = form.getAttribute('data-endpoint');
      if (!endpoint) {
        location.href = 'mailto:' + EMAIL + '?subject=' + encodeURIComponent('Please send me the full moon letter') + '&body=' + encodeURIComponent('Dear Santhi,\n\nPlease write to me' + (name ? '. My name is ' + name : '') + ', and my letters can find me at ' + address + '.\n\nWith thanks' + (name ? ',\n' + name : ''));
        track('newsletter_signup', { method: 'email', page_path: location.pathname });
        say('Your email is open with the request written out. Press send, and the letters follow each full moon.', true);
        return;
      }
      say('Sealing your letter…', true);
      fetch(endpoint, { method: 'POST', mode: 'no-cors', body: new URLSearchParams({ name: name, email: address, page: location.pathname }) })
        .then(function () { posted(name, 'form'); })
        .catch(function () { say('The letter could not be posted just now. Please try again, or write to ' + EMAIL + '.', false); });
    });
  })();
})();
