from pathlib import Path
import io
import ssl
import urllib.request

from PIL import Image

IMG = Path(r"d:\Quantum Financial Advisers\Quantum-financial-advisers\assets\images")
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
)
CTX = ssl.create_default_context()


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "image/*,*/*"})
    with urllib.request.urlopen(req, context=CTX, timeout=60) as res:
        return res.read()


def fit_save(im: Image.Image, dest: Path, max_edge: int = 2560) -> None:
    im = im.convert("RGB")
    w, h = im.size
    longest = max(w, h)
    if longest > max_edge:
        scale = max_edge / longest
        im = im.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
    im.save(dest, "WEBP", quality=88, method=6)
    kb = dest.stat().st_size / 1024
    print(f"{dest.name:32} {im.size[0]}x{im.size[1]} {kb:.1f}KB")


src = Path(
    r"C:\Users\Admin\.cursor\projects\d-Quantum-Financial-Advisers-Quantum-financial-advisers\assets\about-office-4k.png"
)
office = Image.open(src).convert("RGB").resize((2560, 1440), Image.Resampling.LANCZOS)
office.save(IMG / "about-office.webp", "WEBP", quality=90, method=6)
print(
    "about-office.webp",
    office.size,
    f"{(IMG / 'about-office.webp').stat().st_size / 1024:.1f}KB",
)

redown = {
    "handshake-office.webp": "https://images.pexels.com/photos/3184465/pexels-photo-3184465.jpeg",
    "development-feature.webp": "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=2560&h=1700&q=90",
    "about-hero.webp": "https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=2560&h=1700&q=90",
}
for name, url in redown.items():
    fit_save(Image.open(io.BytesIO(fetch(url))), IMG / name)
