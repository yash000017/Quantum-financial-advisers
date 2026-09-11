"""Fix landscape heroes and the two failed HD downloads."""
from __future__ import annotations

import io
import ssl
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "assets" / "images"
GEN = Path(r"C:\Users\Admin\.cursor\projects\d-Quantum-Financial-Advisers-Quantum-financial-advisers\assets\about-office-hd.png")
MAX_EDGE = 2560
Q = 88
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
)
CTX = ssl.create_default_context()

SOURCES = {
    # Force 16:9 landscape London aerial / Tower Bridge
    "hero-skyline.webp": "https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?auto=format&fit=crop&w=3840&h=2160&q=92",
    "faqs-hero.webp": "https://images.unsplash.com/photo-1529655683826-aba9b3e77383?auto=format&fit=crop&w=3840&h=2160&q=92",
    "contact-office.webp": "https://images.unsplash.com/photo-1462826303086-329426d1aef5?auto=format&fit=crop&w=2560&h=1600&q=90",
    "commercial-feature.webp": "https://images.unsplash.com/photo-1486325212027-8081e485255e?auto=format&fit=crop&w=2560&h=1600&q=90",
}


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "image/*,*/*"})
    with urllib.request.urlopen(req, context=CTX, timeout=60) as res:
        return res.read()


def fit(im: Image.Image) -> Image.Image:
    im = im.convert("RGB")
    w, h = im.size
    longest = max(w, h)
    if longest > MAX_EDGE:
        scale = MAX_EDGE / longest
        im = im.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
    return im


def save(im: Image.Image, dest: Path) -> None:
    im.save(dest, "WEBP", quality=Q, method=6)
    kb = dest.stat().st_size / 1024
    print(f"OK  {dest.name:32} {im.size[0]}x{im.size[1]}  {kb:7.1f}KB")


def main() -> None:
    for name, url in SOURCES.items():
        im = fit(Image.open(io.BytesIO(fetch(url))))
        save(im, IMG / name)

    if GEN.exists():
        im = fit(Image.open(GEN))
        save(im, IMG / "about-office.webp")
        print(f"Used generated office: {GEN}")
    else:
        print("Generated office PNG not found")


if __name__ == "__main__":
    main()
