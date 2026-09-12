"""Generate compact responsive WebP variants for PageSpeed / LCP."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "assets" / "images"
WIDTHS = (480, 768, 1080, 1440, 1920)

PHOTOS = [
    "hero-skyline.webp",
    "hero-funding-meeting.webp",
    "commercial-feature.webp",
    "development-site.webp",
    "handshake-office.webp",
    "btl-terrace.webp",
    "services-hero.webp",
    "founder-meeting.webp",
    "about-hero.webp",
    "commercial-property.webp",
    "contact-hero.webp",
    "contact-office.webp",
    "advisor-clients.webp",
    "about-office.webp",
    "stats-london.webp",
]


def as_rgb(im: Image.Image) -> Image.Image:
    im = ImageOps.exif_transpose(im)
    if im.mode in {"RGBA", "LA"}:
        bg = Image.new("RGB", im.size, (18, 32, 51))
        bg.paste(im, mask=im.getchannel("A"))
        return bg
    if im.mode != "RGB":
        return im.convert("RGB")
    return im


def save_webp(im: Image.Image, dest: Path, quality: int) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    im.save(dest, "WEBP", quality=quality, method=6)


def variants_for(src_name: str) -> None:
    src = IMG / src_name
    if not src.exists():
        print(f"skip missing {src_name}")
        return
    stem = src.stem
    original = as_rgb(Image.open(src))
    quality = 62 if stem == "hero-skyline" else 68
    print(f"{src_name} {original.size[0]}x{original.size[1]}")
    for width in WIDTHS:
        if width > original.size[0] + 8:
            continue
        ratio = width / original.size[0]
        size = (width, max(1, int(original.size[1] * ratio)))
        resized = original.resize(size, Image.Resampling.LANCZOS)
        dest = IMG / f"{stem}-{width}.webp"
        save_webp(resized, dest, quality)
        print(f"  {dest.name:28} {dest.stat().st_size / 1024:6.1f} KB")


def compress_logo() -> None:
    src = IMG / "logo.png"
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGBA")
    save_webp(im, IMG / "logo.webp", 88)
    for width in (210, 420):
        ratio = width / im.size[0]
        size = (width, max(1, int(im.size[1] * ratio)))
        save_webp(im.resize(size, Image.Resampling.LANCZOS), IMG / f"logo-{width}.webp", 88)
    print(f"logo.webp { (IMG / 'logo.webp').stat().st_size / 1024:.1f} KB")


def compress_favicon() -> None:
    src = IMG / "favicon.png"
    if not src.exists():
        return
    im = ImageOps.exif_transpose(Image.open(src)).convert("RGBA")
    im = im.resize((512, 512), Image.Resampling.LANCZOS)
    im.save(src, "PNG", optimize=True)
    print(f"favicon.png {src.stat().st_size / 1024:.1f} KB")


def main() -> None:
    for name in PHOTOS:
        variants_for(name)
    compress_logo()
    compress_favicon()
    print("responsive images ready")


if __name__ == "__main__":
    main()
