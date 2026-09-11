"""Download HD stock and re-encode site photos as high-quality WebP."""
from __future__ import annotations

import io
import ssl
import sys
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "assets" / "images"
MAX_EDGE = 2560
WEBP_QUALITY = 88

# Free HD sources (Unsplash / Pexels). Same subject as each current asset.
SOURCES: dict[str, str] = {
    # Homepage + FAQs hero — aerial London / Tower Bridge
    "hero-skyline.webp": "https://images.unsplash.com/photo-1536000839277-85ebce30ea26?auto=format&fit=crop&w=3200&q=92",
    # Hero float handshake close-up
    "handshake.webp": "https://images.pexels.com/photos/7706928/pexels-photo-7706928.jpeg?auto=compress&cs=tinysrgb&dpr=2&w=2560",
    # Family signing documents
    "document-signing.webp": "https://images.pexels.com/photos/8293652/pexels-photo-8293652.jpeg?auto=compress&cs=tinysrgb&dpr=2&w=2560",
    # Couple reviewing papers with adviser
    "elderly-couple-advisor.webp": "https://images.pexels.com/photos/7579042/pexels-photo-7579042.jpeg?auto=compress&cs=tinysrgb&dpr=2&w=2560",
    # Looking-up commercial towers
    "commercial-property.webp": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=2560&q=90",
    # Modern residential development
    "development-site.webp": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=2560&q=90",
    # Adviser with older clients
    "advisor-clients.webp": "https://images.pexels.com/photos/8293778/pexels-photo-8293778.jpeg?auto=compress&cs=tinysrgb&dpr=2&w=2560",
    # About page office corridor / interior
    "about-hero.webp": "https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=2560&q=90",
    "about-office.webp": "https://images.unsplash.com/photo-1497366811353-6870744d04b2?auto=format&fit=crop&w=2560&q=90",
    # Handshake in a meeting room
    "handshake-office.webp": "https://images.pexels.com/photos/3184465/pexels-photo-3184465.jpeg?auto=compress&cs=tinysrgb&dpr=2&w=2560",
    # Two professionals in consultation
    "founder-meeting.webp": "https://images.pexels.com/photos/1181396/pexels-photo-1181396.jpeg?auto=compress&cs=tinysrgb&dpr=2&w=2560",
    # Pen / paperwork close-up (contact hero)
    "contact-hero.webp": "https://images.pexels.com/photos/5668858/pexels-photo-5668858.jpeg?auto=compress&cs=tinysrgb&dpr=2&w=2560",
    # Boardroom with large windows
    "contact-office.webp": "https://images.unsplash.com/photo-1431540013144-5d327ea9c0de?auto=format&fit=crop&w=2560&q=90",
    # Hands / notes / laptop (services banner)
    "services-hero.webp": "https://images.pexels.com/photos/3184292/pexels-photo-3184292.jpeg?auto=compress&cs=tinysrgb&dpr=2&w=2560",
    # City aerial at dusk
    "commercial-aerial.webp": "https://images.unsplash.com/photo-1449824913935-59a10b8d2000?auto=format&fit=crop&w=2560&q=90",
    # Housing construction from above
    "construction-aerial.webp": "https://images.pexels.com/photos/2219024/pexels-photo-2219024.jpeg?auto=compress&cs=tinysrgb&dpr=2&w=2560",
    "construction-workers.webp": "https://images.unsplash.com/photo-1504307651254-35680f356dfd?auto=format&fit=crop&w=2560&q=90",
    "faqs-hero.webp": "https://images.unsplash.com/photo-1529655683826-aba9b3e77383?auto=format&fit=crop&w=2560&q=90",
    "london-canary.webp": "https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?auto=format&fit=crop&w=2560&q=90",
    "london-gherkin.webp": "https://images.unsplash.com/photo-1486299267070-83823f5448dd?auto=format&fit=crop&w=2560&q=90",
    "stats-london.webp": "https://images.unsplash.com/photo-1505761671935-60b3a7427bad?auto=format&fit=crop&w=2560&q=90",
    "wills-feature.webp": "https://images.pexels.com/photos/8112199/pexels-photo-8112199.jpeg?auto=compress&cs=tinysrgb&dpr=2&w=2560",
    "commercial-feature.webp": "https://images.unsplash.com/photo-1470723710355-95404ed277a5?auto=format&fit=crop&w=2560&q=90",
    "development-feature.webp": "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=2560&q=90",
    "estate-feature.webp": "https://images.pexels.com/photos/7578930/pexels-photo-7578930.jpeg?auto=compress&cs=tinysrgb&dpr=2&w=2560",
    "btl-houses.jpg": "https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&w=2560&q=90",
}

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
)
CTX = ssl.create_default_context()


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "image/*,*/*"})
    with urllib.request.urlopen(req, context=CTX, timeout=60) as res:
        return res.read()


def fit_hd(im: Image.Image) -> Image.Image:
    im = im.convert("RGB")
    w, h = im.size
    longest = max(w, h)
    if longest > MAX_EDGE:
        scale = MAX_EDGE / longest
        im = im.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
    return im


def save_webp(im: Image.Image, dest: Path) -> None:
    im.save(dest, "WEBP", quality=WEBP_QUALITY, method=6)


def save_jpeg(im: Image.Image, dest: Path) -> None:
    im.save(dest, "JPEG", quality=90, optimize=True)


def main() -> int:
    failed = []
    for name, url in SOURCES.items():
        dest = IMG / name
        try:
            raw = fetch(url)
            im = Image.open(io.BytesIO(raw))
            im = fit_hd(im)
            if dest.suffix.lower() in {".jpg", ".jpeg"}:
                save_jpeg(im, dest)
            else:
                save_webp(im, dest)
            kb = dest.stat().st_size / 1024
            print(f"OK  {name:32} {im.size[0]}x{im.size[1]}  {kb:7.1f}KB")
        except Exception as exc:
            failed.append(name)
            print(f"FAIL {name}: {exc}", file=sys.stderr)
    if failed:
        print("Failed:", ", ".join(failed), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
