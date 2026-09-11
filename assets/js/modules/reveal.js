import { prefersReducedMotion, inViewport } from './dom.js';

export function initReveal() {
  const revealEls = document.querySelectorAll('.reveal');
  if (!revealEls.length) return;

  if (!('IntersectionObserver' in window) || prefersReducedMotion) {
    revealEls.forEach(function (el) { el.classList.add('visible'); });
    return;
  }

  const observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.14, rootMargin: '0px 0px -40px 0px' });

  revealEls.forEach(function (el) {
    if (inViewport(el)) {
      el.classList.add('visible');
    } else {
      observer.observe(el);
    }
  });

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
}
