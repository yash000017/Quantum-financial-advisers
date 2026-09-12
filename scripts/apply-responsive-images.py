"""Rewrite <img> tags to use generated srcset variants."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "assets" / "images"
VERSION = "20260914c"

PAGES = [
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

SIZES = {
    "hero-skyline": "100vw",
    "page-hero": "100vw",
    "hero-funding-meeting": "(max-width: 1020px) 92vw, 420px",
    "card": "(max-width: 720px) 92vw, (max-width: 1020px) 46vw, 280px",
    "split": "(max-width: 1020px) 92vw, 540px",
}

CARD_NAMES = {
    "commercial-feature",
    "development-site",
    "handshake-office",
    "btl-terrace",
    "services-hero",
}
SPLIT_NAMES = {"founder-meeting", "handshake-office", "contact-office"}
HERO_BG = {"hero-skyline"}
PAGE_HERO = {
    "about-hero",
    "commercial-property",
    "development-site",
    "handshake-office",
    "about-office",
    "advisor-clients",
    "contact-hero",
}


def variant_widths(stem: str) -> list[int]:
    found = []
    for path in IMG.glob(f"{stem}-*.webp"):
        try:
            found.append(int(path.stem.rsplit("-", 1)[1]))
        except ValueError:
            continue
    return sorted(set(found))


def srcset(stem: str) -> str:
    return ", ".join(
        f"assets/images/{stem}-{width}.webp?v={VERSION} {width}w"
        for width in variant_widths(stem)
    )


def default_src(stem: str) -> str:
    widths = variant_widths(stem)
    pick = 768 if 768 in widths else (widths[min(len(widths) - 1, 1)] if widths else None)
    if pick:
        return f"assets/images/{stem}-{pick}.webp?v={VERSION}"
    return f"assets/images/{stem}.webp?v={VERSION}"


def sizes_for(stem: str, class_name: str) -> str:
    if stem in HERO_BG:
        return SIZES["hero-skyline"]
    if "page-hero-photo" in class_name:
        return SIZES["page-hero"]
    if stem == "hero-funding-meeting":
        return SIZES["hero-funding-meeting"]
    if stem in CARD_NAMES:
        return SIZES["card"]
    if stem in SPLIT_NAMES:
        return SIZES["split"]
    return "(max-width: 720px) 92vw, 800px"


IMG_RE = re.compile(
    r'<img(?P<before>[^>]*?)src="assets/images/(?P<name>[a-z0-9-]+)\.(?P<ext>webp|jpg|png)(?:\?v=[^"]*)?"(?P<after>[^>]*)>',
    re.I,
)


def rebuild_img(match: re.Match[str]) -> str:
    before = match.group("before")
    name = match.group("name")
    ext = match.group("ext")
    after = match.group("after")
    attrs = f"{before} {after}"
    class_name = ""
    class_match = re.search(r'class="([^"]*)"', attrs)
    if class_match:
        class_name = class_match.group(1)

    if name == "logo" or ext == "png" and name.startswith("favicon"):
        return match.group(0)

    if not variant_widths(name):
        return match.group(0)

    eager = "fetchpriority" in attrs or "page-hero-photo" in class_name or name == "hero-skyline"
    loading = "eager" if eager else "lazy"
    priority = ' fetchpriority="high"' if (name == "hero-skyline" or "page-hero-photo" in class_name) else ""
    if name == "hero-funding-meeting":
        loading = "eager"
        priority = ' fetchpriority="low"'

    alt_match = re.search(r'alt="([^"]*)"', attrs)
    alt = alt_match.group(1) if alt_match else ""
    width_match = re.search(r'width="(\d+)"', attrs)
    height_match = re.search(r'height="(\d+)"', attrs)
    extra_class = f' class="{class_name}"' if class_name else ""
    dims = ""
    if width_match and height_match:
        dims = f' width="{width_match.group(1)}" height="{height_match.group(1)}"'

    return (
        f'<img{extra_class} src="{default_src(name)}" srcset="{srcset(name)}" '
        f'sizes="{sizes_for(name, class_name)}" alt="{alt}"{dims} '
        f'loading="{loading}" decoding="async"{priority}>'
    )


PRELOAD_RE = re.compile(
    r'<link rel="preload" as="image" href="assets/images/([a-z0-9-]+)\.webp(?:\?v=[^"]*)?" fetchpriority="high">',
    re.I,
)


def rebuild_preload(match: re.Match[str]) -> str:
    stem = match.group(1)
    widths = variant_widths(stem)
    if not widths:
        return match.group(0)
    href = default_src(stem)
    srcset_val = srcset(stem)
    return (
        f'<link rel="preload" as="image" href="{href}" imagesrcset="{srcset_val}" '
        f'imagesizes="100vw" fetchpriority="high">'
    )


def patch_file(path: Path) -> None:
    html = path.read_text(encoding="utf-8")
    html = IMG_RE.sub(rebuild_img, html)
    html = PRELOAD_RE.sub(rebuild_preload, html)
    html = html.replace(
        'src="assets/images/logo.png"',
        f'src="assets/images/logo.webp?v={VERSION}" srcset="assets/images/logo-210.webp?v={VERSION} 210w, assets/images/logo-420.webp?v={VERSION} 420w, assets/images/logo.webp?v={VERSION} 698w" sizes="(max-width: 480px) 160px, 210px"',
    )
    path.write_text(html, encoding="utf-8")
    print(f"patched {path.name}")


def main() -> None:
    for name in PAGES:
        patch_file(ROOT / name)
    for rel in ("src/includes/header.html", "src/includes/footer.html"):
        patch_file(ROOT / rel)


if __name__ == "__main__":
    main()
