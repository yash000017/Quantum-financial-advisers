export function initEnquiryForm() {
  const form = document.querySelector('.enquiry-form');
  if (!form) return;

  const params = new URLSearchParams(window.location.search);
  const subject = params.get('subject');
  const select = form.querySelector('select[name="enquiry_type"]');
  if (subject && select) {
    Array.prototype.forEach.call(select.options, function (opt) {
      if (opt.value.toLowerCase() === subject.toLowerCase()) select.value = opt.value;
    });
  }

  form.addEventListener('submit', function () {
    const btn = form.querySelector('button[type="submit"]');
    if (btn) {
      btn.disabled = true;
      btn.textContent = 'Sending...';
    }
  });
}

export function initFooterYear() {
  const yearEl = document.querySelector('[data-year]');
  if (yearEl) yearEl.textContent = String(new Date().getFullYear());
}
