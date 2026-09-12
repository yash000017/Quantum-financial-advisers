"""Restore alt text stripped during the first srcset rewrite."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ALTS = {
    "hero-skyline": "",
    "hero-funding-meeting": "Discussing a commercial funding requirement with company directors",
    "commercial-feature": "Commercial office buildings",
    "development-site": "A property development site",
    "handshake-office": "A commercial transaction meeting",
    "btl-terrace": "UK terraced houses for investment letting",
    "services-hero": "Preparing a commercial funding proposal",
    "founder-meeting": "Discussing a commercial funding requirement",
    "about-hero": "Quantum Financial Advisers Ltd office",
    "commercial-property": "Commercial property",
    "contact-hero": "Discussing a commercial finance requirement",
    "contact-office": "A meeting room for commercial finance discussions",
    "advisor-clients": "Business funding advisory meeting",
    "about-office": "Limited company property investment",
}

PAGE_ALTS = {
    "commercial-mortgages.html": {"commercial-property": "Commercial Mortgages"},
    "commercial-finance.html": {"commercial-property": "Commercial Finance"},
    "development-finance.html": {"development-site": "Development Finance"},
    "commercial-bridging-finance.html": {"handshake-office": "Commercial Bridging"},
    "limited-company-buy-to-let.html": {"about-office": "Limited Company Buy-to-Let"},
    "business-funding-advisory.html": {"advisor-clients": "Business Funding Advisory"},
    "privacy-policy.html": {"about-hero": "Privacy Policy"},
    "cookie-policy.html": {"about-hero": "Cookie Policy"},
    "terms-of-use.html": {"about-hero": "Terms of Use"},
    "regulatory-status.html": {"about-hero": "Regulatory Status"},
    "about.html": {"handshake-office": "A commercial finance meeting"},
}

RX = re.compile(r'src="assets/images/(?P<file>[a-z0-9-]+)\.webp[^"]*"([^>]*?)alt=""')


def main() -> None:
    for path in ROOT.glob("*.html"):
        html = path.read_text(encoding="utf-8")

        def repl(match: re.Match[str]) -> str:
            base = re.sub(r"-\d+$", "", match.group("file"))
            alt = PAGE_ALTS.get(path.name, {}).get(base, ALTS.get(base, ""))
            return match.group(0).replace('alt=""', f'alt="{alt}"')

        new = RX.sub(repl, html)
        if new != html:
            path.write_text(new, encoding="utf-8")
            print(f"fixed {path.name}")


if __name__ == "__main__":
    main()
