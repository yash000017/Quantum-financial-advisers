export const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

export function inViewport(el) {
  const r = el.getBoundingClientRect();
  return r.top < window.innerHeight && r.bottom > 0;
}
