"""Build transparent 3D Q-globe favicons from the magenta-backed source render."""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "assets" / "images"
SOURCE_CANDIDATES = [
    ROOT / "scripts" / "favicon-3d-source.png",
    IMG / "favicon-3d-source.png",
]


def magenta_key(rgb: Image.Image) -> Image.Image:
    """Knock out magenta (#FF00FF) including the inner Q hole and fringing."""
    arr = np.asarray(rgb.convert("RGB"), dtype=np.float32)
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]

    # Magenta chroma: high red+blue, low green.
    mag = (r + b) * 0.5 - g
    dist = np.sqrt((r - 255.0) ** 2 + g**2 + (b - 255.0) ** 2)

    # Soft alpha: 1 = keep, 0 = drop.
    alpha = np.clip((dist - 55.0) / 70.0, 0.0, 1.0)
    alpha = np.minimum(alpha, np.clip((90.0 - mag) / 50.0, 0.0, 1.0))

    # Despill leftover magenta from edge pixels.
    spill = np.clip(mag / 255.0, 0.0, 1.0)
    r2 = r - spill * np.minimum(r, b) * 0.85
    b2 = b - spill * np.minimum(r, b) * 0.85
    g2 = g + spill * (np.minimum(r, b) - g) * 0.15

    out = np.dstack(
        [
            np.clip(r2, 0, 255),
            np.clip(g2, 0, 255),
            np.clip(b2, 0, 255),
            alpha * 255.0,
        ]
    ).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def tight_square(mark: Image.Image, inset: float = 0.04) -> Image.Image:
    alpha = np.asarray(mark.split()[-1])
    ys, xs = np.where(alpha > 12)
    if len(xs) == 0:
        return mark
    x0, x1 = int(xs.min()), int(xs.max()) + 1
    y0, y1 = int(ys.min()), int(ys.max()) + 1
    cropped = mark.crop((x0, y0, x1, y1))
    side = max(cropped.size)
    pad = int(side * inset)
    canvas = Image.new("RGBA", (side + pad * 2, side + pad * 2), (0, 0, 0, 0))
    canvas.paste(cropped, ((canvas.width - cropped.width) // 2, (canvas.height - cropped.height) // 2), cropped)
    return canvas


def fit_size(mark: Image.Image, size: int) -> Image.Image:
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    glyph = mark.copy()
    glyph.thumbnail((size, size), Image.Resampling.LANCZOS)
    x = (size - glyph.width) // 2
    y = (size - glyph.height) // 2
    canvas.alpha_composite(glyph, (x, y))
    if size <= 32:
        canvas = canvas.filter(ImageFilter.UnsharpMask(radius=0.6, percent=140, threshold=1))
    return canvas


def apple_touch(mark: Image.Image, size: int = 180) -> Image.Image:
    """iOS fills transparent apple-touch icons with black — use brand navy instead."""
    bg = Image.new("RGBA", (size, size), (11, 61, 154, 255))
    glyph = mark.copy()
    inner = int(size * 0.88)
    glyph.thumbnail((inner, inner), Image.Resampling.LANCZOS)
    x = (size - glyph.width) // 2
    y = (size - glyph.height) // 2
    bg.alpha_composite(glyph, (x, y))
    return bg.convert("RGB")


def main() -> None:
    src = next((p for p in SOURCE_CANDIDATES if p.exists()), None)
    if src is None:
        raise SystemExit("Missing 3D favicon source render")

    keyed = magenta_key(Image.open(src))
    master = tight_square(keyed, inset=0.03)
    IMG.mkdir(parents=True, exist_ok=True)

    sizes = {
        "favicon.png": 512,
        "favicon-192.png": 192,
        "favicon-32.png": 32,
        "favicon-16.png": 16,
    }
    for name, size in sizes.items():
        fit_size(master, size).save(IMG / name, "PNG", optimize=True)

    apple_touch(master, 180).save(IMG / "apple-touch-icon.png", "PNG", optimize=True)

    ico = fit_size(master, 256)
    ico.save(IMG / "favicon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48)])
    ico.save(ROOT / "favicon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48)])
    print("wrote transparent 3D favicons from", src.name, "master", master.size)


if __name__ == "__main__":
    main()
