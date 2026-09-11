# Quantum Financial Advisers Ltd

Static marketing site for [quantum-fa.co.uk](https://quantum-fa.co.uk). Public page URLs stay at the site root so existing links and search listings keep working.

## Local preview

Serve the project root over HTTP (ES modules will not load from `file://`):

- VS Code / Cursor Live Server (port `5501`), or
- `python -m http.server 5501`

Then open `http://127.0.0.1:5501/`.

## Folder structure

```text
├── index.html                 Live pages (stable public URLs)
├── about.html
├── contact.html
├── …service and legal pages
├── 404.html / 410.html
├── assets/
│   ├── css/                   7-1 layers + generated style.css
│   ├── js/                    Entry + feature modules
│   ├── images/
│   ├── fonts/
│   └── documents/             Policy PDFs and other downloads
├── src/includes/              Shared header, footer, head assets
├── scripts/                   Maintainer tools (not part of the product UI)
├── _redirects / _headers      Netlify
├── .htaccess                  Apache
├── robots.txt / sitemap.xml
└── site.webmanifest
```

## Editing shared chrome

1. Change `src/includes/header.html`, `footer.html`, or `head-assets.html`.
2. Run `python scripts/inject-chrome.py`.

Current page highlighting is applied in `assets/js/modules/nav-current.js`.

## Editing CSS

Edit the layer files under `assets/css/` (abstracts, base, layout, components, pages, utilities), then:

```bash
python scripts/build-css.py
```

That rebuilds `assets/css/style.css`, which is what the pages load.
