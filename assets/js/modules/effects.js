import { prefersReducedMotion } from './dom.js';

export function initPointerEffects() {
  const glow = document.querySelector('.cursor-glow');
  if (glow && window.matchMedia('(pointer: fine)').matches && !prefersReducedMotion) {
    window.addEventListener('pointermove', function (e) {
      glow.style.transform = 'translate(' + e.clientX + 'px,' + e.clientY + 'px)';
      glow.classList.add('is-on');
    }, { passive: true });
    document.addEventListener('mouseleave', function () {
      glow.classList.remove('is-on');
    });
  }

  const canTilt = !prefersReducedMotion
    && window.matchMedia('(pointer: fine)').matches
    && window.matchMedia('(hover: hover)').matches;
  if (!canTilt) return;

  document.querySelectorAll('[data-tilt]').forEach(function (el) {
    let raf = 0;
    let px = 0;
    let py = 0;
    function paint() {
      raf = 0;
      el.style.transform = 'rotateX(' + (py * -7) + 'deg) rotateY(' + (px * 9) + 'deg) translateZ(10px)';
    }
    el.addEventListener('pointermove', function (e) {
      const r = el.getBoundingClientRect();
      if (!r.width || !r.height) return;
      px = ((e.clientX - r.left) / r.width) - 0.5;
      py = ((e.clientY - r.top) / r.height) - 0.5;
      if (!raf) raf = requestAnimationFrame(paint);
    }, { passive: true });
    el.addEventListener('pointerleave', function () {
      el.style.transform = '';
    });
  });

  const fx = document.querySelector('.hero-cinematic .fx-layer');
  if (fx) {
    let fxRaf = 0;
    let fxX = 0;
    let fxY = 0;
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

  const heroBg = document.querySelector('.hero-cinematic .hero-bg');
  if (heroBg && canTilt) {
    let bgRaf = 0;
    window.addEventListener('pointermove', function (e) {
      const nx = (e.clientX / window.innerWidth) - 0.5;
      const ny = (e.clientY / window.innerHeight) - 0.5;
      if (!bgRaf) {
        bgRaf = requestAnimationFrame(function () {
          bgRaf = 0;
          heroBg.style.setProperty('--hero-mx', (nx * -18).toFixed(2) + 'px');
          heroBg.style.setProperty('--hero-my', (ny * -10).toFixed(2) + 'px');
          heroBg.style.setProperty('--hero-rx', (ny * -4.5).toFixed(2) + 'deg');
          heroBg.style.setProperty('--hero-ry', (nx * 6).toFixed(2) + 'deg');
        });
      }
    }, { passive: true });
  }
}
