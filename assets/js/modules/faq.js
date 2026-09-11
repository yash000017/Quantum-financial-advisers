export function initFaq() {
  document.querySelectorAll('.faq-question').forEach(function (btn) {
    if (btn.tagName === 'SUMMARY') return;
    btn.addEventListener('click', function () {
      const item = btn.closest('.faq-item');
      if (!item) return;
      const isOpen = item.classList.contains('open');
      item.classList.toggle('open', !isOpen);
      btn.setAttribute('aria-expanded', String(!isOpen));
    });
  });

  document.querySelectorAll('details.faq-item').forEach(function (item) {
    item.addEventListener('toggle', function () {
      const summary = item.querySelector('summary.faq-question');
      if (summary) summary.setAttribute('aria-expanded', item.open ? 'true' : 'false');
    });
  });
}
