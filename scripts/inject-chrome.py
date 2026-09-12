"""Sync shared header, footer and head assets into live HTML pages."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INCLUDES = ROOT / "src" / "includes"

LIVE_PAGES = [
    "index.html",
    "about.html",
    "contact.html",
    "404.html",
    "410.html",
    "commercial-finance.html",
    "commercial-mortgages.html",
    "development-finance.html",
    "commercial-bridging-finance.html",
    "limited-company-buy-to-let.html",
    "business-funding-advisory.html",
    "regulatory-status.html",
    "privacy-policy.html",
    "cookie-policy.html",
    "terms-of-use.html",
]

ASSET_VERSION = "20260914c"

HEADER_START = "<!-- include:header -->"
HEADER_END = "<!-- /include:header -->"
FOOTER_START = "<!-- include:footer -->"
FOOTER_END = "<!-- /include:footer -->"

SKIP_RE = re.compile(
    r'<a class="skip-link".*?(?=<main\b)',
    re.DOTALL,
)
FOOTER_RE = re.compile(
    r'<footer class="site-footer">.*?</button>\s*',
    re.DOTALL,
)
HEAD_ASSETS_RE = re.compile(
    r'<link rel="icon".*?<link rel="stylesheet" href="assets/css/style\.css[^"]*">',
    re.DOTALL,
)
IMAGE_PRELOAD_RE = re.compile(
    r'<link rel="preload" as="image"[^>]*>\s*',
)
SCRIPT_RE = re.compile(
    r'<script(?:\s+type="module")?\s+src="assets/js/main\.js[^"]*"></script>'
)


def indent_block(html: str, spaces: int = 2) -> str:
    pad = " " * spaces
    lines = html.strip("\n").splitlines()
    return "\n".join(pad + line if line.strip() else line for line in lines)


def wrap(start: str, end: str, inner: str) -> str:
    return f"{start}\n{indent_block(inner)}\n  {end}"


def sync_page(path: Path, header: str, footer: str, head_assets: str) -> None:
    html = path.read_text(encoding="utf-8")

    if HEADER_START in html and HEADER_END in html:
        html = re.sub(
            re.escape(HEADER_START) + r".*?" + re.escape(HEADER_END),
            wrap(HEADER_START, HEADER_END, header),
            html,
            count=1,
            flags=re.DOTALL,
        )
    else:
        html, n = SKIP_RE.subn(wrap(HEADER_START, HEADER_END, header) + "\n  ", html, count=1)
        if n != 1:
            raise SystemExit(f"Could not find header region in {path.name}")

    if FOOTER_START in html and FOOTER_END in html:
        html = re.sub(
            re.escape(FOOTER_START) + r".*?" + re.escape(FOOTER_END),
            wrap(FOOTER_START, FOOTER_END, footer),
            html,
            count=1,
            flags=re.DOTALL,
        )
    else:
        html, n = FOOTER_RE.subn(wrap(FOOTER_START, FOOTER_END, footer) + "\n  ", html, count=1)
        if n != 1:
            raise SystemExit(f"Could not find footer region in {path.name}")

    match = HEAD_ASSETS_RE.search(html)
    if not match:
        raise SystemExit(f"Could not find head assets in {path.name}")
    image_preloads = IMAGE_PRELOAD_RE.findall(match.group(0))
    replacement = head_assets.strip()
    if image_preloads:
        lines = replacement.splitlines()
        # Keep page-specific hero preloads immediately before the stylesheet.
        replacement = "\n  ".join(lines[:-1] + [p.strip() for p in image_preloads] + [lines[-1]])
    html = html[: match.start()] + replacement + html[match.end() :]

    html, n = SCRIPT_RE.subn(
        f'<script type="module" src="assets/js/main.js?v={ASSET_VERSION}"></script>',
        html,
        count=1,
    )
    if n != 1:
        raise SystemExit(f"Could not find main.js script in {path.name}")

    html = html.replace("theme-color\" content=\"#07111F\"", "theme-color\" content=\"#122033\"")
    html = html.replace(
        'content="width=device-width, initial-scale=1"',
        'content="width=device-width, initial-scale=1, viewport-fit=cover"',
    )
    path.write_text(html, encoding="utf-8")


def main() -> None:
    header = (INCLUDES / "header.html").read_text(encoding="utf-8")
    footer = (INCLUDES / "footer.html").read_text(encoding="utf-8")
    head_assets = (INCLUDES / "head-assets.html").read_text(encoding="utf-8")
    for name in LIVE_PAGES:
        sync_page(ROOT / name, header, footer, head_assets)
        print(f"synced {name}")


if __name__ == "__main__":
    main()
