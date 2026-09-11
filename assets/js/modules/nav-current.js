export function markCurrentNav() {
  const file = (window.location.pathname.split('/').pop() || 'index.html').toLowerCase();
  const current = file === '' || file === '/' ? 'index.html' : file;

  document.querySelectorAll('.nav-links a[href], .footer-links a[href], .footer-legal-links a[href]').forEach((link) => {
    const href = (link.getAttribute('href') || '').split('#')[0].toLowerCase();
    if (!href || href.startsWith('http') || href.startsWith('mailto') || href.startsWith('tel')) return;
    if (href === current || (current === 'index.html' && (href === '/' || href === './'))) {
      link.setAttribute('aria-current', 'page');
    } else {
      link.removeAttribute('aria-current');
    }
  });

  document.querySelectorAll('.nav-links .has-sub').forEach((item) => {
    const currentInMenu = Boolean(item.querySelector('a[aria-current="page"]'));
    item.classList.toggle('is-current', currentInMenu);
    const parentLink = item.querySelector(':scope > .nav-parent > a');
    if (parentLink && parentLink.getAttribute('aria-current') === 'page' && item.querySelector('.nav-sub a[aria-current="page"]')) {
      parentLink.removeAttribute('aria-current');
    }
  });
}
