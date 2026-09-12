import { prefersReducedMotion } from './dom.js';

export function initChrome() {
  const header = document.querySelector('.site-header');
  const chrome = document.querySelector('.site-chrome');
  const progress = document.querySelector('.scroll-progress');
  const heroBg = document.querySelector('.hero-cinematic .hero-bg');
  const backToTop = document.querySelector('.back-to-top');
  const state = { compact: false, ticking: false };

  function scrollY() {
    return window.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop || 0;
  }

  function measureChrome() {
    if (!chrome) return;
    const tb = chrome.querySelector('.top-bar');
    const hd = chrome.querySelector('.site-header');
    if (tb) document.documentElement.style.setProperty('--topbar-h', Math.max(tb.offsetHeight, 1) + 'px');
    if (hd) document.documentElement.style.setProperty('--nav-h', hd.offsetHeight + 'px');
  }
  measureChrome();
  window.addEventListener('resize', function () {
    requestAnimationFrame(measureChrome);
  });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(measureChrome);

  function applyScrollFrame() {
    state.ticking = false;
    const y = scrollY();
    const navOpen = document.body.classList.contains('nav-open');
    const scrolled = y > 8;

    if (header) header.classList.toggle('scrolled', scrolled);
    if (chrome) {
      chrome.classList.toggle('is-scrolled', scrolled);
      state.compact = scrolled && !navOpen;
      chrome.classList.toggle('is-compact', state.compact);
    }

    if (progress) {
      const max = document.documentElement.scrollHeight - window.innerHeight;
      progress.style.width = (max > 0 ? Math.min(100, (y / max) * 100) : 0) + '%';
    }

    if (backToTop) backToTop.classList.toggle('show', y > 600);

    if (heroBg && !prefersReducedMotion) {
      heroBg.style.setProperty('--hero-parallax', (y * 0.18) + 'px');
    }
  }

  window.addEventListener('scroll', function onScroll() {
    if (!state.ticking) {
      state.ticking = true;
      requestAnimationFrame(applyScrollFrame);
    }
  }, { passive: true, capture: true });
  applyScrollFrame();

  initMobileNav(chrome, state);

  if (backToTop) {
    backToTop.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: prefersReducedMotion ? 'auto' : 'smooth' });
    });
  }
}

function initMobileNav(chrome, state) {
  const navToggle = document.querySelector('.nav-toggle');
  const navLinks = document.querySelector('.nav-links');
  let navBackdrop = document.querySelector('.nav-backdrop');
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
      state.compact = false;
      chrome.classList.remove('is-compact');
    }
    if (!open && opts && opts.focusToggle) navToggle.focus();
    if (!open) closeSubmenus();
  }

  if (!navToggle || !navLinks) return;

  function isMobileNav() {
    return window.matchMedia('(max-width: 1180px)').matches;
  }

  function closeSubmenus(except) {
    navLinks.querySelectorAll('.has-sub').forEach((item) => {
      if (item === except) return;
      setSubmenuOpen(item, false);
    });
  }

  function setSubmenuOpen(item, open) {
    const toggle = item.querySelector('.nav-sub-toggle');
    const parentLink = item.querySelector('.nav-parent a');
    item.classList.toggle('is-open', open);
    if (toggle) {
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      toggle.setAttribute('aria-label', open ? 'Close Services menu' : 'Open Services menu');
    }
    if (parentLink) {
      if (isMobileNav()) {
        parentLink.setAttribute('aria-expanded', open ? 'true' : 'false');
      } else {
        parentLink.removeAttribute('aria-expanded');
      }
    }
  }

  navLinks.querySelectorAll('.has-sub').forEach((item) => {
    const toggle = item.querySelector('.nav-sub-toggle');
    const parentLink = item.querySelector('.nav-parent a');

    function toggleSubmenu(e) {
      e.preventDefault();
      e.stopPropagation();
      const open = !item.classList.contains('is-open');
      closeSubmenus(open ? item : null);
      setSubmenuOpen(item, open);
    }

    if (toggle) toggle.addEventListener('click', toggleSubmenu);
    if (parentLink) {
      parentLink.addEventListener('click', function (e) {
        if (!isMobileNav()) return;
        toggleSubmenu(e);
      });
    }
  });

  if (!navToggle.querySelector('.nav-toggle-box')) {
    navToggle.innerHTML = '<span class="nav-toggle-box" aria-hidden="true"><span></span><span></span><span></span></span>';
  }
  if (!navLinks.querySelector('.nav-close')) {
    const closeItem = document.createElement('li');
    closeItem.className = 'nav-close-item';
    closeItem.innerHTML = '<button type="button" class="nav-close" aria-label="Close menu"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg></button>';
    navLinks.insertBefore(closeItem, navLinks.firstChild);
  }

  navToggle.addEventListener('click', function (e) {
    e.stopPropagation();
    setNavOpen(!navLinks.classList.contains('open'));
  });
  navLinks.addEventListener('click', function (e) {
    const parentLink = e.target.closest('.nav-parent a');
    if (parentLink && isMobileNav()) return;
    if (e.target.closest('a') || e.target.closest('.nav-close')) {
      setNavOpen(false);
    }
  });
  navBackdrop.addEventListener('click', function () {
    setNavOpen(false);
  });
  document.addEventListener('pointerdown', function (e) {
    const drawerOpen = navLinks.classList.contains('open');
    if (!drawerOpen && !e.target.closest('.has-sub')) closeSubmenus();
    if (!drawerOpen) return;
    if (navLinks.contains(e.target) || navToggle.contains(e.target)) return;
    setNavOpen(false);
  });
  document.addEventListener('keydown', function (e) {
    if (e.key !== 'Escape') return;
    if (navLinks.classList.contains('open')) {
      setNavOpen(false, { focusToggle: true });
      return;
    }
    closeSubmenus();
  });
}
