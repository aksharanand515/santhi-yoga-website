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

  /* ---------- Split headings into words (accessible) ---------- */
  function splitWords(el) {
    if (el.dataset.splitDone) return $$('.split-i', el);
    el.setAttribute('aria-label', el.textContent.replace(/\s+/g, ' ').trim());
    (function walk(node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (child) {
        if (child.nodeType === 3) {
          var parts = child.textContent.split(/(\s+)/);
          var frag = document.createDocumentFragment();
          parts.forEach(function (part) {
            if (!part) return;
            if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(' ')); return; }
            var w = document.createElement('span'); w.className = 'split-w'; w.setAttribute('aria-hidden', 'true');
            var i = document.createElement('span'); i.className = 'split-i'; i.textContent = part;
            w.appendChild(i); frag.appendChild(w);
          });
          node.replaceChild(frag, child);
        } else if (child.nodeType === 1 && child.tagName !== 'BR') {
          child.setAttribute('aria-hidden', 'true');
          walk(child);
        }
      });
    })(el);
    el.dataset.splitDone = '1';
    return $$('.split-i', el);
  }

  /* ---------- Fallback reveals (no GSAP) ---------- */
  function revealFallback() {
    root.classList.add('reveal-io');
    var items = $$('[data-reveal], [data-split]');
    if (!('IntersectionObserver' in window)) { items.forEach(function (el) { el.classList.add('is-in'); }); return; }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) { entry.target.classList.add('is-in'); io.unobserve(entry.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px' });
    items.forEach(function (el) { io.observe(el); });
  }
  function showAll() { $$('[data-reveal], [data-split]').forEach(function (el) { el.classList.add('is-in'); }); }

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

  function initHomeHero() {
    if (!$('.hero')) return;
    var intro = gsap.timeline({ defaults: { ease: 'expo.out' } });
    intro.from('.hero-scene', { opacity: 0.4, duration: 2.4, ease: 'power2.out' }, 0)
      .from('.hero-layer', { scale: 0.965, duration: 3.2, stagger: 0.12, ease: 'power3.out' }, 0)
      .from('[data-hero="eyebrow"]', { autoAlpha: 0, y: 14, duration: 1.6 }, 0.4)
      .from('.hero-line > span', { yPercent: 108, duration: 1.8, stagger: 0.16 }, 0.55)
      .from('[data-hero="copy"]', { autoAlpha: 0, y: 22, duration: 1.6, stagger: 0.14 }, 1.05)
      .from('[data-hero="meta"]', { autoAlpha: 0, y: 12, duration: 1.4, stagger: 0.12 }, 1.7);
    intro.eventCallback('onComplete', function () {
      gsap.set('[data-hero], .hero-line > span', { clearProps: 'opacity,visibility,transform' });
    });

    var trigger = { trigger: '.hero', start: 'top top', end: 'bottom top', scrub: true };
    $$('.hero-layer').forEach(function (layer) {
      gsap.to(layer, { yPercent: (parseFloat(layer.dataset.depth) || 0.3) * 14, ease: 'none', scrollTrigger: trigger });
    });
    gsap.to('.hero-inner', { y: -70, autoAlpha: 0, ease: 'none', scrollTrigger: { trigger: '.hero', start: 'top top', end: 'bottom 25%', scrub: true } });
    gsap.to('.hero-meta', { autoAlpha: 0, ease: 'none', scrollTrigger: { trigger: '.hero', start: 'top top', end: '+=240', scrub: true } });

    if (finePointer) {
      var movers = $$('.hero-layer').map(function (layer) {
        return {
          depth: parseFloat(layer.dataset.depth) || 0.3,
          x: gsap.quickTo(layer, 'x', { duration: 2.4, ease: 'power3.out' }),
          y: gsap.quickTo(layer, 'y', { duration: 2.4, ease: 'power3.out' })
        };
      });
      var heroEl = $('.hero'); var ticking = false; var last = null;
      window.addEventListener('pointermove', function (e) {
        last = e; if (ticking) return; ticking = true;
        requestAnimationFrame(function () {
          ticking = false;
          if (window.scrollY > heroEl.offsetHeight) return;
          var px = last.clientX / window.innerWidth - 0.5, py = last.clientY / window.innerHeight - 0.5;
          movers.forEach(function (m) { m.x(px * m.depth * -28); m.y(py * m.depth * -18); });
        });
      }, { passive: true });
      var resetLayers = function () { movers.forEach(function (m) { m.x(0); m.y(0); }); };
      window.addEventListener('blur', resetLayers);
      document.addEventListener('visibilitychange', function () { if (document.hidden) resetLayers(); });
    }
  }

  function initPageHero() {
    var ph = $('.phero');
    if (!ph) return;
    var tl = gsap.timeline({ defaults: { ease: 'expo.out' } });
    var media = $('.phero-media .frame', ph);
    if (media) tl.fromTo(media, { clipPath: 'inset(100% 0% 0% 0% round 999px 999px 24px 24px)' }, { clipPath: 'inset(0% 0% 0% 0% round 999px 999px 24px 24px)', duration: 1.8, ease: 'power3.inOut', clearProps: 'clipPath' }, 0.1);
    var img = $('.phero-media img', ph);
    if (img) {
      tl.from(img, { scale: 1.18, duration: 2.2, ease: 'power3.out' }, 0.1);
      gsap.to(img, { yPercent: 8, ease: 'none', scrollTrigger: { trigger: ph, start: 'top top', end: 'bottom top', scrub: true } });
    }
    var tag = $('.phero-tag', ph);
    if (tag) tl.from(tag, { autoAlpha: 0, y: 20, duration: 1.2 }, 1.1);
  }

  function initReveals() {
    // Headings: word by word
    $$('[data-split]').forEach(function (el) {
      var words = splitWords(el);
      el.classList.add('is-in');
      gsap.set(words, { yPercent: 110 });
      var inHero = el.closest('.phero');
      gsap.to(words, {
        yPercent: 0, duration: 1.2, ease: 'expo.out', stagger: 0.045, delay: inHero ? 0.25 : 0,
        scrollTrigger: inHero ? null : { trigger: el, start: 'top 88%', once: true }
      });
    });

    // Supporting copy, cards and media: fade-rise in sequence
    var items = $$('[data-reveal]');
    items.forEach(function (el) { el.classList.add('is-in'); });
    gsap.set(items, { autoAlpha: 0, y: 32 });
    function play(batch) {
      var fresh = batch.filter(function (el) { return !el._shown; });
      if (!fresh.length) return;
      fresh.forEach(function (el) { el._shown = true; });
      gsap.to(fresh, { autoAlpha: 1, y: 0, duration: 1.1, ease: 'expo.out', stagger: 0.08, overwrite: true,
        onComplete: function () { gsap.set(fresh, { clearProps: 'opacity,visibility,transform' }); } });
    }
    // onLeave covers content skipped over by anchor links or fast scrolling
    ScrollTrigger.batch(items, { start: 'top 90%', once: true, onEnter: play, onLeave: play, onEnterBack: play });

    // Photos: soft wipe upwards
    $$('[data-clip]').forEach(function (el) {
      gsap.fromTo(el, { clipPath: 'inset(18% 6% 18% 6% round 24px)' }, {
        clipPath: 'inset(0% 0% 0% 0% round 0px)', duration: 1.6, ease: 'power3.out', clearProps: 'clipPath',
        scrollTrigger: { trigger: el, start: 'top 85%', once: true }
      });
      var img = $('img', el);
      if (img) gsap.fromTo(img, { scale: 1.15 }, { scale: 1, duration: 2, ease: 'power3.out', clearProps: 'transform', scrollTrigger: { trigger: el, start: 'top 85%', once: true } });
    });
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
    if (reduceMotion) { showAll(); return; }
    if (!(window.gsap && window.ScrollTrigger)) { revealFallback(); return; }
    gsap.registerPlugin(ScrollTrigger);
    root.classList.add('has-gsap');
    initLenis();
    initHomeHero();
    initPageHero();
    initReveals();
    initJourney();
    initCounters();
    window.addEventListener('load', function () { ScrollTrigger.refresh(); });
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { ScrollTrigger.refresh(); });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', initMotion);
  else initMotion();

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
