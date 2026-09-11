"""Build square navy favicons from the Q mark in logo.webp."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "assets" / "images"
logo = Image.open(IMG / "logo.webp").convert("RGBA")
w, h = logo.size
mark = logo.crop((0, 0, min(160, w), h))

pixels = mark.load()
min_x, min_y, max_x, max_y = mark.width, mark.height, 0, 0
for y in range(mark.height):
    for x in range(mark.width):
        r, g, b, a = pixels[x, y]
        if a < 20:
            continue
        if r > 245 and g > 245 and b > 245:
            continue
        min_x, min_y = min(min_x, x), min(min_y, y)
        max_x, max_y = max(max_x, x), max(max_y, y)

pad = 4
q = mark.crop((max(0, min_x - pad), max(0, min_y - pad), min(mark.width, max_x + 1 + pad), min(mark.height, max_y + 1 + pad)))
qp = q.load()
for y in range(q.height):
    for x in range(q.width):
        r, g, b, a = qp[x, y]
        brightness = (r + g + b) / 3
        if brightness > 232:
            qp[x, y] = (r, g, b, 0)
        elif brightness > 210:
            qp[x, y] = (r, g, b, int(a * 0.25))

NAVY = (38, 68, 131, 255)


def rounded_square(size: int, radius: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((0, 0, size - 1, size - 1), radius=radius, fill=NAVY)
    return img


def make_icon(size: int, radius: int, inset: float = 0.16) -> Image.Image:
    canvas = rounded_square(size, radius)
    inner = int(size * (1 - inset * 2))
    glyph = q.copy()
    glyph.thumbnail((inner, inner), Image.Resampling.LANCZOS)
    x = (size - glyph.width) // 2
    y = (size - glyph.height) // 2
    canvas.alpha_composite(glyph, (x, y))
    return canvas


png512 = make_icon(512, 96)
png180 = make_icon(180, 40)
png164 = make_icon(164, 36)
png32 = make_icon(32, 7, inset=0.14)
png16 = make_icon(16, 4, inset=0.12)

png164.save(IMG / "favicon.png", "PNG")
png32.save(IMG / "favicon-32.png", "PNG")
png180.save(IMG / "apple-touch-icon.png", "PNG")
png16.save(IMG / "favicon-16.png", "PNG")

ico16 = make_icon(16, 3, inset=0.1)
ico32 = png32
ico48 = make_icon(48, 10, inset=0.14)
ico16.save(
    IMG / "favicon.ico",
    format="ICO",
    sizes=[(16, 16), (32, 32), (48, 48)],
    append_images=[ico32, ico48],
)

svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="Quantum Financial Advisers Ltd">
  <rect width="64" height="64" rx="14" fill="#264483"/>
  <circle cx="32" cy="30" r="15.5" fill="none" stroke="#ffffff" stroke-width="3.2"/>
  <ellipse cx="32" cy="30" rx="6.2" ry="15.2" fill="none" stroke="#7eb3d9" stroke-width="1.6"/>
  <path d="M16.8 30h30.4" fill="none" stroke="#7eb3d9" stroke-width="1.6"/>
  <path d="M18 42c6.5 8.5 21.5 8.5 28 0" fill="none" stroke="#4f8fbf" stroke-width="3.2" stroke-linecap="round"/>
</svg>
"""
(IMG / "favicon.svg").write_text(svg, encoding="utf-8")
print("wrote favicons", png164.size, png32.size, png180.size)
