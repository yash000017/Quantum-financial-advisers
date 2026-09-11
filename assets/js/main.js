/* Quantum Financial Advisers — shared interactions */
(function () {
  'use strict';
  document.documentElement.classList.add('js');

  var prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- Fixed chrome: one rAF scroll loop ---------- */
  var header = document.querySelector('.site-header');
  var chrome = document.querySelector('.site-chrome');
  var progress = document.querySelector('.scroll-progress');
  var heroBg = document.querySelector('.hero-bg img');
  var backToTop = document.querySelector('.back-to-top');
  var lastY = window.scrollY || 0;
  var compact = false;
  var dirTravel = 0;
  var ticking = false;
  var SHOW_TOP = 16;
  var DIR_LOCK = 28;

  function measureChrome() {
    if (!chrome) return;
    var tb = chrome.querySelector('.top-bar');
    var hd = chrome.querySelector('.site-header');
    if (tb) document.documentElement.style.setProperty('--topbar-h', tb.offsetHeight + 'px');
    if (hd) document.documentElement.style.setProperty('--nav-h', hd.offsetHeight + 'px');
  }
  measureChrome();
  window.addEventListener('resize', measureChrome);

  function applyScrollFrame() {
    ticking = false;
    var y = window.scrollY || document.documentElement.scrollTop || 0;
    var dy = y - lastY;
    lastY = y;

    var scrolled = y > 16;
    if (header) header.classList.toggle('scrolled', scrolled);
    if (chrome) chrome.classList.toggle('is-scrolled', scrolled);

    if (chrome) {
      var next = compact;
      if (document.body.classList.contains('nav-open') || y <= SHOW_TOP) {
        next = false;
        dirTravel = 0;
      } else if (dy > 0) {
        dirTravel = dirTravel > 0 ? dirTravel + dy : dy;
        if (dirTravel >= DIR_LOCK) next = true;
      } else if (dy < 0) {
        dirTravel = dirTravel < 0 ? dirTravel + dy : dy;
        if (dirTravel <= -DIR_LOCK) next = false;
      }
      compact = next;
      chrome.classList.toggle('is-compact', compact);
    }

    if (progress) {
      var max = document.documentElement.scrollHeight - window.innerHeight;
      progress.style.width = (max > 0 ? Math.min(100, (y / max) * 100) : 0) + '%';
    }

    if (backToTop) backToTop.classList.toggle('show', y > 600);

    if (heroBg && !prefersReducedMotion) {
      heroBg.style.transform = 'translate3d(0,' + (y * 0.22) + 'px,0) scale(1.08)';
    }
  }

  function onScroll() {
    if (!ticking) {
      ticking = true;
      requestAnimationFrame(applyScrollFrame);
    }
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  applyScrollFrame();

  /* ---------- Mobile navigation ---------- */
  var navToggle = document.querySelector('.nav-toggle');
  var navLinks = document.querySelector('.nav-links');
  var navBackdrop = document.querySelector('.nav-backdrop');
  if (!navBackdrop) {
    navBackdrop = document.createElement('div');
    navBackdrop.className = 'nav-backdrop';
    navBackdrop.setAttribute('aria-hidden', 'true');
    document.body.appendChild(navBackdrop);
  }
  function setNavOpen(open, opts) {
    if (!navToggle || !navLinks) return;
    navLinks.classList.toggle('open', open);
    navToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    navToggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    document.body.classList.toggle('nav-open', open);
    if (open && chrome) {
      compact = false;
      chrome.classList.remove('is-compact');
    }
    if (!open && opts && opts.focusToggle) navToggle.focus();
  }
  if (navToggle && navLinks) {
    if (!navToggle.querySelector('.nav-toggle-box')) {
      navToggle.innerHTML = '<span class="nav-toggle-box" aria-hidden="true"><span></span><span></span><span></span></span>';
    }
    if (!navLinks.querySelector('.nav-close')) {
      var closeItem = document.createElement('li');
      closeItem.className = 'nav-close-item';
      closeItem.innerHTML = '<button type="button" class="nav-close" aria-label="Close menu"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg></button>';
      navLinks.insertBefore(closeItem, navLinks.firstChild);
    }
    navToggle.addEventListener('click', function (e) {
      e.stopPropagation();
      setNavOpen(!navLinks.classList.contains('open'));
    });
    navLinks.addEventListener('click', function (e) {
      if (e.target.closest('a') || e.target.closest('.nav-close')) {
        setNavOpen(false);
      }
    });
    navBackdrop.addEventListener('click', function () {
      setNavOpen(false);
    });
    document.addEventListener('pointerdown', function (e) {
      if (!navLinks.classList.contains('open')) return;
      if (navLinks.contains(e.target) || navToggle.contains(e.target)) return;
      setNavOpen(false);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && navLinks.classList.contains('open')) {
        setNavOpen(false, { focusToggle: true });
      }
    });
  }

  /* ---------- Scroll reveal ---------- */
  var revealEls = document.querySelectorAll('.reveal');
  function inViewport(el) {
    var r = el.getBoundingClientRect();
    return r.top < window.innerHeight && r.bottom > 0;
  }
  if (revealEls.length && 'IntersectionObserver' in window && !prefersReducedMotion) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.14, rootMargin: '0px 0px -40px 0px' });
    revealEls.forEach(function (el) {
      // Reveal immediately if already on screen; observe the rest.
      if (inViewport(el)) {
        el.classList.add('visible');
      } else {
        observer.observe(el);
      }
    });
    // Safety net: never leave content hidden if the observer misbehaves.
    setTimeout(function () {
      revealEls.forEach(function (el) {
        if (inViewport(el)) el.classList.add('visible');
      });
    }, 1200);
    window.addEventListener('scroll', function () {
      revealEls.forEach(function (el) {
        if (!el.classList.contains('visible') && inViewport(el)) el.classList.add('visible');
      });
    }, { passive: true });
  } else {
    revealEls.forEach(function (el) { el.classList.add('visible'); });
  }

  /* ---------- Animated counters ---------- */
  var counters = document.querySelectorAll('[data-count]');
  function animateCounter(el) {
    if (el.dataset.done) return;
    el.dataset.done = '1';
    var target = parseInt(el.getAttribute('data-count'), 10);
    var suffix = el.getAttribute('data-suffix') || '';
    if (prefersReducedMotion) {
      el.textContent = target + suffix;
      return;
    }
    var start = null;
    var duration = 1400;
    function step(ts) {
      if (!start) start = ts;
      var progress = Math.min((ts - start) / duration, 1);
      var eased = 1 - Math.pow(1 - progress, 3);
      el.textContent = Math.round(eased * target) + suffix;
      if (progress < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  if (counters.length) {
    if ('IntersectionObserver' in window && !prefersReducedMotion) {
      var counterObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          counterObserver.unobserve(entry.target);
          animateCounter(entry.target);
        });
      }, { threshold: 0.5 });
      counters.forEach(function (el) {
        if (inViewport(el)) {
          animateCounter(el);
        } else {
          counterObserver.observe(el);
        }
      });
      window.addEventListener('scroll', function () {
        counters.forEach(function (el) {
          if (!el.dataset.done && inViewport(el)) animateCounter(el);
        });
      }, { passive: true });
    } else {
      counters.forEach(animateCounter);
    }
  }

  /* ---------- FAQ accordion ---------- */
  document.querySelectorAll('.faq-question').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var item = btn.closest('.faq-item');
      var isOpen = item.classList.contains('open');
      item.classList.toggle('open', !isOpen);
      btn.setAttribute('aria-expanded', String(!isOpen));
    });
  });

  /* ---------- Back to top ---------- */
  if (backToTop) {
    backToTop.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: prefersReducedMotion ? 'auto' : 'smooth' });
    });
  }

  /* ---------- Contact form UX ---------- */
  var form = document.querySelector('.enquiry-form');
  if (form) {
    var params = new URLSearchParams(window.location.search);
    var subject = params.get('subject');
    var select = form.querySelector('select[name="enquiry_type"]');
    if (subject && select) {
      Array.prototype.forEach.call(select.options, function (opt) {
        if (opt.value.toLowerCase() === subject.toLowerCase()) select.value = opt.value;
      });
    }
    form.addEventListener('submit', function () {
      var btn = form.querySelector('button[type="submit"]');
      if (btn) {
        btn.disabled = true;
        btn.textContent = 'Sending…';
      }
    });
  }

  /* ---------- Footer year ---------- */
  var yearEl = document.querySelector('[data-year]');
  if (yearEl) yearEl.textContent = new Date().getFullYear();


  /* ---------- Pointer glow ---------- */
  var glow = document.querySelector('.cursor-glow');
  if (glow && window.matchMedia('(pointer: fine)').matches && !prefersReducedMotion) {
    window.addEventListener('pointermove', function (e) {
      glow.style.transform = 'translate(' + e.clientX + 'px,' + e.clientY + 'px)';
      glow.classList.add('is-on');
    }, { passive: true });
    document.addEventListener('mouseleave', function () {
      glow.classList.remove('is-on');
    });
  }

  /* ---------- Native FAQ details ---------- */
  document.querySelectorAll('details.faq-item').forEach(function (item) {
    item.addEventListener('toggle', function () {
      var summary = item.querySelector('summary.faq-question');
      if (summary) summary.setAttribute('aria-expanded', item.open ? 'true' : 'false');
    });
  });

  /* ---------- 3D tilt (desktop pointers only, never blocks content) ---------- */
  var canTilt = !prefersReducedMotion
    && window.matchMedia('(pointer: fine)').matches
    && window.matchMedia('(hover: hover)').matches;
  if (canTilt) {
    document.querySelectorAll('[data-tilt]').forEach(function (el) {
      var raf = 0;
      var px = 0;
      var py = 0;
      function paint() {
        raf = 0;
        el.style.transform = 'rotateX(' + (py * -7) + 'deg) rotateY(' + (px * 9) + 'deg) translateZ(10px)';
      }
      el.addEventListener('pointermove', function (e) {
        var r = el.getBoundingClientRect();
        if (!r.width || !r.height) return;
        px = ((e.clientX - r.left) / r.width) - 0.5;
        py = ((e.clientY - r.top) / r.height) - 0.5;
        if (!raf) raf = requestAnimationFrame(paint);
      }, { passive: true });
      el.addEventListener('pointerleave', function () {
        el.style.transform = '';
      });
    });

    var fx = document.querySelector('.hero-cinematic .fx-layer');
    if (fx) {
      var fxRaf = 0;
      var fxX = 0;
      var fxY = 0;
      window.addEventListener('pointermove', function (e) {
        fxX = (e.clientX / window.innerWidth - 0.5) * 14;
        fxY = (e.clientY / window.innerHeight - 0.5) * 10;
        if (!fxRaf) {
          fxRaf = requestAnimationFrame(function () {
            fxRaf = 0;
            fx.style.transform = 'translate3d(' + fxX + 'px,' + fxY + 'px,0)';
          });
        }
      }, { passive: true });
    }
  }
})();
