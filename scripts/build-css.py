"""Split the monolithic stylesheet into a 7-1 layer structure, then rebuild style.css."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS_DIR = ROOT / "assets" / "css"
SOURCE = CSS_DIR / "style.css"
MANIFEST = CSS_DIR / "layers.json"

SECTION_FILES = {
    "reset & base": "base/reset.css",
    "buttons": "components/buttons.css",
    "header / nav": "layout/header.css",
    "hero (home)": "layout/hero.css",
    "section headers": "components/sections.css",
    "cards": "components/cards.css",
    "split feature sections": "components/split.css",
    "stats band": "components/stats.css",
    "quote / trust band": "components/quote.css",
    "faq accordion": "components/faq.css",
    "team": "components/team.css",
    "page hero": "layout/page-hero.css",
    "services page": "pages/services.css",
    "contact": "pages/contact.css",
    "cta band": "components/cta.css",
    "footer": "layout/footer.css",
    "scroll reveal": "utilities/reveal.css",
    "back to top": "components/back-to-top.css",
    "responsive": "utilities/responsive.css",
    "motion preferences": "utilities/motion.css",
    "high-tech chrome": "utilities/chrome.css",
    "home hero - two-column, no overlap": "layout/home-hero.css",
    "2026 cinematic layer": "layout/home-hero.css",
    "high-tech 3d layer (decorative only - never hides copy)": "utilities/fx-3d.css",
    "commercial finance site additions": "utilities/site-additions.css",
    "2026 layout system": "utilities/layout-system.css",
}

SECTION_RE = re.compile(
    r"^/\* (?:-+|=+) (?P<title>.+?) (?:-+|=+) \*/\s*$",
    re.MULTILINE,
)
BUNDLE_MARK = "generated bundle"


def normalize(title: str) -> str:
    return re.sub(r"\s+", " ", title.replace("—", "-").replace("–", "-")).strip().lower()


def slug(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", normalize(title)).strip("-")


def rewrite_urls(css: str) -> str:
    """Partials live one folder deeper than style.css."""
    return css.replace("url('../", "url('../../").replace('url("../', 'url("../../')


def restore_urls(css: str) -> str:
    return css.replace("url('../../", "url('../").replace('url("../../', 'url("../')


def split_preamble(block: str) -> tuple[str, str]:
    font_match = re.search(r"@font-face", block)
    root_match = re.search(r":root\s*\{", block)
    if not font_match or not root_match:
        return block, ""
    fonts = block[font_match.start() : root_match.start()].rstrip() + "\n"
    tokens = block[root_match.start() :].strip() + "\n"
    return fonts, tokens


def write_partial(rel: str, body: str) -> None:
    path = CSS_DIR / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    banner = f"/* {rel} */\n"
    path.write_text(banner + rewrite_urls(body.rstrip() + "\n"), encoding="utf-8")


def build_bundle(order: list[str]) -> None:
    chunks = [
        "/* ==========================================================================\n"
        "   Quantum Financial Advisers — generated bundle\n"
        "   Source layers live beside this file (7-1 / ITCSS).\n"
        "   Rebuild with: python scripts/build-css.py\n"
        "   ========================================================================== */\n"
    ]
    for rel in order:
        path = CSS_DIR / rel
        text = restore_urls(path.read_text(encoding="utf-8"))
        text = re.sub(r"^/\* .+? \*/\n", "", text, count=1)
        chunks.append(f"\n/* --- {rel} --- */\n{text.rstrip()}\n")
    SOURCE.write_text("".join(chunks), encoding="utf-8")
    MANIFEST.write_text(json.dumps(order, indent=2) + "\n", encoding="utf-8")


def split_monolith() -> list[str]:
    css = SOURCE.read_text(encoding="utf-8")
    if BUNDLE_MARK in css[:500]:
        raise SystemExit("style.css is already a generated bundle; split aborted.")
    matches = list(SECTION_RE.finditer(css))
    if not matches:
        raise SystemExit("No stylesheet sections found.")

    order: list[str] = []
    preamble = css[: matches[0].start()]
    fonts, tokens = split_preamble(preamble)
    write_partial("abstracts/fonts.css", fonts)
    write_partial("abstracts/tokens.css", tokens)
    order.extend(["abstracts/fonts.css", "abstracts/tokens.css"])

    for i, match in enumerate(matches):
        title = match.group("title").strip(" -=")
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(css)
        rel = SECTION_FILES.get(normalize(title)) or f"utilities/{slug(title)}.css"
        write_partial(rel, css[start:end])
        order.append(rel)
        print(f"  {title} -> {rel}")
    return order


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    if BUNDLE_MARK not in source[:500]:
        print("Splitting style.css into layers...")
        order = split_monolith()
    elif MANIFEST.exists():
        order = json.loads(MANIFEST.read_text(encoding="utf-8"))
    else:
        raise SystemExit("Missing assets/css/layers.json. Restore style.css and re-run.")
    build_bundle(order)
    print("CSS layers ready; assets/css/style.css rebuilt.")


if __name__ == "__main__":
    main()
