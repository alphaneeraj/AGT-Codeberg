#!/usr/bin/env python3
"""
Regenerates favicon.ico/.svg, app icons and the Open Graph / Twitter card image.
Requires Pillow:  python3 -m pip install pillow   then   python3 scripts/make_images.py
"""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "assets" / "img"
IMG.mkdir(parents=True, exist_ok=True)

NAVY, NAVY_DARK, ACCENT, WHITE = (11, 61, 145), (7, 42, 102), (255, 180, 0), (255, 255, 255)
PHONE = "+1-888-609-1015"

# Plane outline on a 64x64 grid (same path as LOGO_SVG in build.py), rotated 45°.
PLANE = [(32, 6), (35, 11), (35, 26), (58, 40), (58, 45), (35, 38), (35, 52), (42, 58), (42, 62), (32, 59),
         (22, 62), (22, 58), (29, 52), (29, 38), (6, 45), (6, 40), (29, 26), (29, 11)]
PLANE_D = "M32 6l3 5v15l23 14v5l-23-7v14l7 6v4l-10-3-10 3v-4l7-6V38L6 45v-5l23-14V11z"


def plane(scale, ox=0, oy=0, deg=45):
    a = math.radians(deg)
    pts = []
    for x, y in PLANE:
        dx, dy = x - 32, y - 32
        rx, ry = dx * math.cos(a) - dy * math.sin(a), dx * math.sin(a) + dy * math.cos(a)
        pts.append((ox + (32 + rx) * scale, oy + (32 + ry) * scale))
    return pts


def icon(size, maskable=False):
    ss = 4  # supersample for smooth edges
    s = size * ss
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if maskable:
        d.rectangle([0, 0, s, s], fill=NAVY)
        k, off = s / 64 * 0.7, s * 0.15  # keep glyph inside the safe zone
    else:
        d.rounded_rectangle([0, 0, s - 1, s - 1], radius=s * 14 / 64, fill=NAVY)
        k, off = s / 64, 0
    d.polygon(plane(k, off, off), fill=WHITE)
    cx = off + 50 * k
    r = 5 * k
    d.ellipse([cx - r, cx - r, cx + r, cx + r], fill=ACCENT)
    return im.resize((size, size), Image.LANCZOS)


def font(size, bold=True):
    for path, idx in [("/System/Library/Fonts/HelveticaNeue.ttc", 1 if bold else 0),
                      ("/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf", 0),
                      ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", 0)]:
        try:
            return ImageFont.truetype(path, size, index=idx)
        except OSError:
            continue
    return ImageFont.load_default()


def og_image():
    W, H = 1200, 630
    im = Image.new("RGB", (W, H), NAVY_DARK)
    d = ImageDraw.Draw(im)
    for y in range(H):  # diagonal-ish gradient
        t = y / H
        c = tuple(int(NAVY_DARK[i] + (NAVY[i] - NAVY_DARK[i]) * t) for i in range(3))
        d.line([(0, y), (W, y)], fill=c)
    # large faint plane
    ghost = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(ghost).polygon(plane(9, 700, 20), fill=(255, 255, 255, 28))
    im.paste(ghost, (0, 0), ghost)
    d = ImageDraw.Draw(im)

    im.paste(icon(96), (70, 70), icon(96))
    d.text((186, 88), "Airlines Group Travel", font=font(46), fill=WHITE)
    d.text((70, 230), "Group flights for", font=font(72), fill=WHITE)
    d.text((70, 312), "10+ travelers", font=font(72), fill=ACCENT)
    d.text((70, 412), "Sports teams · Weddings · Corporate · Schools · Tours", font=font(30, bold=False), fill=(220, 230, 250))

    d.rounded_rectangle([70, 480, 560, 560], radius=40, fill=ACCENT)
    d.text((105, 500), "Call 24/7  " + PHONE, font=font(34), fill=(26, 19, 0))
    d.text((600, 506), "airlinesgrouptravel.codeberg.page", font=font(28, bold=False), fill=(200, 212, 235))
    im.save(IMG / "og-image.png", optimize=True)


def main():
    icon(512).save(IMG / "logo-512.png", optimize=True)
    icon(512).save(IMG / "icon-512.png", optimize=True)
    icon(192).save(IMG / "icon-192.png", optimize=True)
    icon(512, maskable=True).save(IMG / "icon-maskable-512.png", optimize=True)
    icon(180, maskable=True).convert("RGB").save(ROOT / "apple-touch-icon.png", optimize=True)
    icon(256).save(ROOT / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    (ROOT / "favicon.svg").write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#0b3d91"/>'
        f'<path fill="#fff" transform="rotate(45 32 32)" d="{PLANE_D}"/><circle cx="50" cy="50" r="5" fill="#ffb400"/></svg>\n')
    og_image()
    print("images written to", IMG)


if __name__ == "__main__":
    main()
