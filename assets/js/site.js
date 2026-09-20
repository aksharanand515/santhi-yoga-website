/* ==================================================================
   Santhi Yoga India — shared site script
   Vanilla JS. GSAP + ScrollTrigger drive motion; Lenis is the only
   smooth-scroll engine. Everything degrades to a complete static page
   when scripts fail or the visitor prefers reduced motion.
   ================================================================== */
(function () {
  'use strict';

  var root = document.documentElement;
  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  var $ = function (sel, ctx) { return (ctx || document).querySelector(sel); };
  var $$ = function (sel, ctx) { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); };
  var lenis = null;

  /* ---------- Header state + floating WhatsApp ---------- */
  var header = $('#site-header');
  var floatWa = $('#float-wa');
  var hero = $('.hero') || $('.phero');
  var footer = $('.site-footer');
  function onScroll() {
    var y = window.scrollY || window.pageYOffset;
    if (header) header.classList.toggle('is-scrolled', y > 10);
    if (floatWa) {
      var past = hero ? y > hero.offsetHeight * 0.7 : y > 400;
      var nearFooter = footer ? footer.getBoundingClientRect().top < window.innerHeight * 0.9 : false;
      floatWa.setAttribute('data-show', past && !nearFooter ? 'true' : 'false');
    }
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ---------- Full-screen menu ---------- */
  var toggle = $('#menu-toggle');
  var menu = $('#menu');
  function setMenu(open) {
    if (!toggle || !menu) return;
    toggle.setAttribute('aria-expanded', String(open));
    $('.sr-only', toggle).textContent = open ? 'Close menu' : 'Open menu';
    menu.classList.toggle('is-open', open);
    menu.inert = !open;
    document.body.style.overflow = open ? 'hidden' : '';
    if (lenis) { if (open) lenis.stop(); else lenis.start(); }
    if (open) { var first = $('a', menu); if (first) first.focus({ preventScroll: true }); }
  }
  if (toggle && menu) {
    menu.inert = true;
    toggle.addEventListener('click', function () { setMenu(toggle.getAttribute('aria-expanded') !== 'true'); });
    menu.addEventListener('click', function (e) { if (e.target.closest('a')) setMenu(false); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') { setMenu(false); toggle.focus(); }
    });
    window.matchMedia('(min-width: 1040px)').addEventListener('change', function (m) { if (m.matches) setMenu(false); });
  }

  /* ---------- Scroll reveals ----------
     Headings are split into words at build time (tools/build.js) and all
     content starts visible, so the page reads the same before and after
     scripts run. Only content still below the fold is held back here; it
     plays in on arrival and the helper classes are removed afterwards. */
  function initReveals() {
    if (reduceMotion || !('IntersectionObserver' in window)) return;
    var kinds = [
      { sel: '[data-reveal]', wait: 'rv-wait', play: 'rv-in', ms: 1100 },
      { sel: '[data-split]', wait: 'sp-wait', play: 'sp-in', ms: 1200 },
      { sel: '[data-clip]', wait: 'cl-wait', play: 'cl-in', ms: 2000 }
    ];
    var io = new IntersectionObserver(function (entries) {
      var batch = 0;
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var el = entry.target, k = el._reveal, extra = 0;
        io.unobserve(el);
        if (k.play === 'rv-in') { var d = Math.min(batch++, 4); if (d) { el.classList.add('rv-d' + d); extra = d * 80; } }
        if (k.play === 'sp-in') extra = $$('.split-i', el).length * 45;
        el.classList.remove(k.wait);
        el.classList.add(k.play);
        setTimeout(function () { el.classList.remove(k.play, 'rv-d1', 'rv-d2', 'rv-d3', 'rv-d4'); }, k.ms + extra + 150);
      });
    }, { rootMargin: '0px 0px -10% 0px' });
    var fold = window.innerHeight;
    kinds.forEach(function (k) {
      $$(k.sel).forEach(function (el) {
        // Already on screen (or inside closed/hidden content): leave it to the CSS load animation
        if (el.getBoundingClientRect().top < fold) return;
        el._reveal = k;
        el.classList.add(k.wait);
        io.observe(el);
      });
    });
  }

  /* ---------- Motion (GSAP) ---------- */
  function initLenis() {
    if (!window.Lenis) return;
    lenis = new window.Lenis({ duration: 1.1, easing: function (t) { return Math.min(1, 1.001 - Math.pow(2, -10 * t)); } });
    lenis.on('scroll', ScrollTrigger.update);
    gsap.ticker.add(function (time) { lenis.raf(time * 1000); });
    gsap.ticker.lagSmoothing(0);
    document.addEventListener('click', function (e) {
      var link = e.target.closest && e.target.closest('a[href^="#"]');
      if (!link || e.defaultPrevented) return;
      var hash = link.getAttribute('href');
      if (hash.length < 2) return;
      var target = document.querySelector(hash);
      if (!target) return;
      e.preventDefault();
      lenis.scrollTo(target, { offset: -(header ? header.offsetHeight + 8 : 0) });
      if (history.pushState) history.pushState(null, '', hash);
    });
    window.addEventListener('pagehide', function () { if (lenis) lenis.destroy(); });
  }

  // Home hero: the intro plays in CSS. GSAP only adds depth once it has loaded:
  // the photograph drifts as the hero scrolls away and leans towards the pointer.
  function initHomeHero() {
    var photo = $('.hero-photo');
    if (!photo) return;
    gsap.fromTo(photo, { '--py': '0%' }, {
      '--py': '9%', ease: 'none',
      scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: true }
    });
    gsap.to('.hero-inner', { y: -60, autoAlpha: 0, ease: 'none', scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom 30%', scrub: true } });
    gsap.fromTo('.hero-scroll', { autoAlpha: 1 }, { autoAlpha: 0, ease: 'none', immediateRender: false, scrollTrigger: { trigger: '.hero', start: 'top top', end: '+=240', scrub: true } });

    if (finePointer) {
      var moveX = gsap.quickTo(photo, '--mx', { duration: 2, ease: 'power3.out' });
      var moveY = gsap.quickTo(photo, '--my', { duration: 2, ease: 'power3.out' });
      var heroEl = $('.hero'), ticking = false, last = null;
      gsap.set(photo, { '--mx': '0px', '--my': '0px' });
      window.addEventListener('pointermove', function (e) {
        last = e; if (ticking) return; ticking = true;
        requestAnimationFrame(function () {
          ticking = false;
          if (window.scrollY > heroEl.offsetHeight) return;
          var px = last.clientX / window.innerWidth - 0.5, py = last.clientY / window.innerHeight - 0.5;
          moveX(px * -18 + 'px'); moveY(py * -14 + 'px');
        });
      }, { passive: true });
      var rest = function () { moveX('0px'); moveY('0px'); };
      window.addEventListener('blur', rest);
      document.addEventListener('visibilitychange', function () { if (document.hidden) rest(); });
    }
  }

  // Inner page hero: the clip reveal plays in CSS; the photo drifts as the hero scrolls away
  function initPageHero() {
    var img = $('.phero-media img');
    if (!img) return;
    gsap.fromTo(img, { '--py': '0%' }, { '--py': '8%', ease: 'none', scrollTrigger: { trigger: '.phero', start: 'top top', end: 'bottom top', scrub: true } });
  }

  // Home: photo journey pins and travels sideways on large screens
  function initJourney() {
    var section = $('.journey');
    var track = $('.journey-track');
    if (!section || !track) return;
    var mm = gsap.matchMedia();
    mm.add('(min-width: 1040px)', function () {
      section.classList.add('is-pinned');
      var distance = function () { return Math.max(0, track.scrollWidth - window.innerWidth + parseFloat(getComputedStyle(track).paddingLeft)); };
      var tween = gsap.to(track, {
        x: function () { return -distance(); }, ease: 'none',
        scrollTrigger: { trigger: section, start: 'top top', end: function () { return '+=' + distance(); }, pin: true, scrub: 0.8, invalidateOnRefresh: true, anticipatePin: 1 }
      });
      return function () { section.classList.remove('is-pinned'); tween.scrollTrigger && tween.scrollTrigger.kill(); gsap.set(track, { clearProps: 'transform' }); };
    });
  }

  function initCounters() {
    $$('[data-count]').forEach(function (el) {
      var target = parseFloat(el.dataset.count), decimals = parseInt(el.dataset.decimals || '0', 10);
      var fmt = function (n) { var s = n.toFixed(decimals); return el.dataset.comma ? Number(s).toLocaleString('en-US') : s; };
      var obj = { v: 0 };
      gsap.to(obj, { v: target, duration: 1.8, ease: 'power2.out', scrollTrigger: { trigger: el, start: 'top 90%', once: true },
        onUpdate: function () { el.textContent = fmt(obj.v); }, onComplete: function () { el.textContent = fmt(target); } });
    });
  }

  function initMotion() {
    initReveals();
    if (reduceMotion || !(window.gsap && window.ScrollTrigger)) return;
    gsap.registerPlugin(ScrollTrigger);
    root.classList.add('has-gsap');
    initLenis();
    initHomeHero();
    initPageHero();
    initJourney();
    initCounters();
    window.addEventListener('load', function () { ScrollTrigger.refresh(); });
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { ScrollTrigger.refresh(); });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initMotion);
  else initMotion();

  /* ---------- Home hero: fade the photograph in once it has decoded ---------- */
  (function () {
    var heroEl = $('.hero'), img = $('.hero-photo img');
    if (!heroEl || !img) return;
    var show = function () { heroEl.classList.add('is-ready'); };
    if (img.complete && img.naturalWidth) show();
    else img.addEventListener('load', show);
    img.addEventListener('error', show);
    setTimeout(show, 3000);
  })();
  /* ---------- Home: service list swaps the preview photo ---------- */
  (function () {
    var preview = $('.svc-preview');
    if (!preview) return;
    var imgs = $$('img', preview), caption = $('figcaption', preview), rows = $$('.svc-row');
    function activate(i) {
      imgs.forEach(function (img, n) { img.classList.toggle('is-active', n === i); });
      rows.forEach(function (row, n) { row.classList.toggle('is-active', n === i); });
      if (caption && rows[i]) caption.textContent = rows[i].dataset.caption || '';
    }
    rows.forEach(function (row, i) {
      row.addEventListener('mouseenter', function () { activate(i); });
      row.addEventListener('focus', function () { activate(i); });
    });
    activate(0);
  })();

  /* ---------- Testimonials ---------- */
  $$('[data-quotes]').forEach(function (box) {
    var slides = $$('.quote', box), idx = 0, count = $('.quote-count', box), live = $('.quote-stage', box);
    function go(n) {
      idx = (n + slides.length) % slides.length;
      slides.forEach(function (s, i) { s.classList.toggle('is-active', i === idx); s.setAttribute('aria-hidden', i === idx ? 'false' : 'true'); });
      if (count) count.textContent = (idx + 1) + ' / ' + slides.length;
    }
    var prev = $('[data-prev]', box), next = $('[data-next]', box);
    if (prev) prev.addEventListener('click', function () { go(idx - 1); });
    if (next) next.addEventListener('click', function () { go(idx + 1); });
    var startX = null;
    live.addEventListener('pointerdown', function (e) { startX = e.clientX; });
    live.addEventListener('pointerup', function (e) { if (startX === null) return; var dx = e.clientX - startX; if (Math.abs(dx) > 40) go(idx + (dx < 0 ? 1 : -1)); startX = null; });
    go(0);
  });

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

  /* ---------- Booking page: writes the WhatsApp message for the visitor ---------- */
  (function () {
    var form = $('#booking-form');
    if (!form) return;
    var WA = 'https://wa.me/917907714144', EMAIL = 'santhiyogacochin@gmail.com';
    var preview = $('#wa-text'), waBtn = $('#wa-send'), mailBtn = $('#mail-send'), status = $('#booking-status');
    var nameField = form.elements.name, whenField = $('#b-when'), whenLabel = $('label[for="b-when"]');

    var offerings = {
      'walk-in': {
        want: 'I would like to join your daily walk-in Hatha Yoga classes in Fort Kochi',
        ask: 'Could you let me know the class times and anything I should bring?',
        when: 'For example: 12-15 March, or next week',
        whenLabel: 'When are you coming?',
        subject: 'Walk-in classes'
      },
      private: {
        want: 'I would like to book a private one-to-one yoga session',
        ask: 'Could you let me know which times are free and what a session costs?',
        when: 'For example: any morning next week',
        whenLabel: 'When would suit you?',
        subject: 'Private class'
      },
      workshop: {
        want: 'I am interested in your yoga workshops',
        ask: 'Could you tell me which workshops are coming up?',
        when: 'For example: while I am in Kochi in March',
        whenLabel: 'When are you in Kochi?',
        subject: 'Workshop'
      },
      retreat: {
        want: 'I am interested in your yoga retreats in Kerala',
        ask: 'Could you tell me when the next retreat is and what it includes?',
        when: 'For example: sometime this winter',
        whenLabel: 'When are you hoping to come?',
        subject: 'Retreat'
      },
      ttc: {
        want: 'I am interested in your 28-day 200-hour Yoga Teacher Training in Fort Kochi',
        ask: 'Could you tell me how to reserve a place and what I should prepare?',
        when: 'For example: the April 2027 batch',
        whenLabel: 'Which 2027 batch?',
        subject: '200-hour Teacher Training'
      }
    };
    var levels = {
      beginner: 'I am a complete beginner',
      some: 'I have practised a little before',
      regular: 'I practise regularly',
      teacher: 'I teach yoga myself'
    };
    var groups = { '2': 'There will be two of us', '3': 'There will be three of us', '4': 'There will be four or more of us' };

    function chosen() {
      var picked = form.querySelector('input[name="offering"]:checked');
      return offerings[picked ? picked.value : 'walk-in'] || offerings['walk-in'];
    }

    // One short paragraph, the way a person would actually write it
    function message() {
      var o = chosen();
      var name = nameField.value.trim();
      var when = whenField.value.trim();
      var note = $('#b-note').value.trim();
      var people = groups[form.elements.people.value];
      var level = levels[form.elements.level.value];
      var parts = [];
      parts.push(name ? 'Hello Santhi Yoga India, my name is ' + name + '.' : 'Hello Santhi Yoga India.');
      parts.push(o.want + '.');
      if (when) parts.push('I am looking at ' + when + '.');
      if (people) parts.push(people + '.');
      if (level) parts.push(level + '.');
      if (note) parts.push(note.replace(/\s+/g, ' ') + (/[.!?]$/.test(note) ? '' : '.'));
      parts.push(o.ask);
      parts.push('Thank you.');
      return parts.join(' ');
    }

    function refresh() {
      var o = chosen(), text = message();
      preview.textContent = text;
      waBtn.href = WA + '?text=' + encodeURIComponent(text);
      mailBtn.href = 'mailto:' + EMAIL + '?subject=' + encodeURIComponent('Booking enquiry - ' + o.subject) + '&body=' + encodeURIComponent(text);
      whenField.placeholder = o.when;
      if (whenLabel) whenLabel.firstChild.nodeValue = o.whenLabel + ' ';
    }

    // A name makes the reply personal, so ask for it before sending
    function guard(e) {
      if (nameField.value.trim()) { status.textContent = ''; status.className = 'form-status'; return; }
      e.preventDefault();
      nameField.setAttribute('aria-invalid', 'true');
      nameField.focus();
      status.textContent = 'Please add your name first, so Achu knows who he is replying to.';
      status.className = 'form-status is-error';
    }

    form.addEventListener('input', refresh);
    form.addEventListener('change', refresh);
    form.addEventListener('submit', function (e) { e.preventDefault(); });
    nameField.addEventListener('input', function () { nameField.removeAttribute('aria-invalid'); });
    waBtn.addEventListener('click', guard);
    mailBtn.addEventListener('click', guard);

    // Links elsewhere on the site can preselect, e.g. /book/?for=ttc
    var wanted = new URLSearchParams(window.location.search).get('for');
    if (wanted && offerings[wanted]) {
      var input = form.querySelector('input[name="offering"][value="' + wanted + '"]');
      if (input) input.checked = true;
    }
    var month = new URLSearchParams(window.location.search).get('month');
    if (month) whenField.value = month.replace(/[^A-Za-z0-9 ]/g, '') + ' 2027';
    refresh();
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
          .then(function (r) { if (!r.ok) throw new Error(); form.reset(); setStatus('Thank you — your enquiry has been sent. We will reply soon.', true); })
          .catch(function () { setStatus('Your enquiry could not be sent. Email ' + EMAIL + ' or message us on WhatsApp.', false); });
        return;
      }
      var subject = 'Booking Inquiry - Santhi Yoga India' + (d.interest ? ' (' + d.interest + ')' : '');
      var body = ['Name: ' + d.name, 'Email: ' + d.email, 'WhatsApp / Phone: ' + (d.phone || '-'), 'Interested in: ' + d.interest, 'Preferred dates: ' + (d.dates || '-'), '', 'Message:', d.message || '-'].join('\r\n');
      window.location.href = 'mailto:' + EMAIL + '?subject=' + encodeURIComponent(subject) + '&body=' + encodeURIComponent(body);
      setStatus('Your email app should open with the enquiry ready to send. If it doesn’t, write to ' + EMAIL + '.', true);
    });

    var mapBtn = $('#load-map');
    if (mapBtn) mapBtn.addEventListener('click', function () {
      var frame = document.createElement('iframe');
      frame.src = 'https://www.google.com/maps?q=' + encodeURIComponent('Chirattapalam, Fort Kochi, Kerala, India') + '&output=embed';
      frame.title = 'Map showing Chirattapalam, Fort Kochi, Kerala';
      frame.loading = 'lazy';
      frame.referrerPolicy = 'no-referrer-when-downgrade';
      $('.map-box').appendChild(frame);
      mapBtn.closest('.map-cta').remove();
    });
  })();
})();
