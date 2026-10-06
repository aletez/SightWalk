"""Draws the gutter icons into icons/ at 1x, 2x and 3x. Needs Pillow; run from the repository root:

    python3 tools/draw_icons.py path/to/InterVariable.ttf

Glyphs use Inter (SIL Open Font License, github.com/rsms/inter), which may be used in shipped images.

Coordinates are in a 16-unit square, as in the mockups. Each icon is drawn large and scaled down,
which gives smooth edges.
"""

import os
import string
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFont

FONT = sys.argv[1] if len(sys.argv) > 1 else "InterVariable.ttf"
OUT = "icons"
BIG = 64  # pixels per unit while drawing
SIZES = {"": 16, "@2x": 32, "@3x": 48}
MARGIN = 2  # units of 16 left clear on the right of each icon

GREEN, LIME = "#23894E", "#E4F7B5"
AMBER, PLUM = "#C77A0E", "#3A1838"
BLUE, BUTTER = "#2C6ED5", "#FFEFB0"
GRAPHITE = "#1E1F23"

# Polylines with one quadratic corner each: (start, control, end) of the bend, plus straight ends.
ARROWS = {
    "pass_up": ([(12.5, 10.5), (8.2, 10.5)], ((8.2, 10.5), (5.5, 10.5), (5.5, 7.8)),
                [(5.5, 7.8), (5.5, 3.6)], [(3, 6), (5.5, 3.4), (8, 6)]),
    "pass_down": ([(12.5, 5.5), (8.2, 5.5)], ((8.2, 5.5), (5.5, 5.5), (5.5, 8.2)),
                  [(5.5, 8.2), (5.5, 12.4)], [(3, 10), (5.5, 12.6), (8, 10)]),
    "take_above": ([(4.5, 3.2), (4.5, 7.6)], ((4.5, 7.6), (4.5, 10.4), (7.3, 10.4)),
                   [(7.3, 10.4), (12.4, 10.4)], [(10, 7.9), (12.6, 10.4), (10, 12.9)]),
    "take_below": ([(4.5, 12.8), (4.5, 8.4)], ((4.5, 8.4), (4.5, 5.6), (7.3, 5.6)),
                   [(7.3, 5.6), (12.4, 5.6)], [(10, 3.1), (12.6, 5.6), (10, 8.1)]),
}


def px(points):
    return [(x * BIG, y * BIG) for x, y in points]


def quad(p0, p1, p2, steps=24):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0],
             (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1])
            for t in (i / steps for i in range(steps + 1))]


def square(colour):
    image = Image.new("RGBA", (16 * BIG, 16 * BIG), (0, 0, 0, 0))
    ImageDraw.Draw(image).rounded_rectangle(
        [0.5 * BIG, 0.5 * BIG, 15.5 * BIG, 15.5 * BIG], radius=1 * BIG, fill=colour)
    return image


def stroke(draw, points, width, colour, closed=False):
    points = px(points + points[:1] if closed else points)
    w = int(width * BIG)
    draw.line(points, fill=colour, width=w, joint="curve")
    for x, y in (points[0], points[-1]):
        draw.ellipse([x - w / 2, y - w / 2, x + w / 2, y + w / 2], fill=colour)


def arrow(name):
    first, bend, last, head = ARROWS[name]
    image = square(GREEN)
    draw = ImageDraw.Draw(image)
    stroke(draw, first + quad(*bend) + last, 1.7, LIME)
    stroke(draw, head, 1.7, LIME)
    return image


def glyph(char, background, colour, size, weight):
    image = square(background)
    font = ImageFont.truetype(FONT, int(size * BIG))
    font.set_variation_by_axes([14, weight])  # optical size for small text, weight
    ImageDraw.Draw(image).text((8 * BIG, (8 + size * 0.36) * BIG), char, font=font,
                               fill=colour, anchor="ms")
    return image


def eye(direction, h=8.5):
    outline = quad((1.8, 8), (8, 8 - h), (14.2, 8))[:-1] + quad((14.2, 8), (8, 8 + h), (1.8, 8))[:-1]
    half = h / 2
    r = half * 0.68
    cy = 8 - (half - r) * 0.9 if direction == "up" else 8 + (half - r) * 0.9
    image = square(BUTTER)
    pupil = Image.new("L", image.size, 0)
    ImageDraw.Draw(pupil).ellipse(px([(8 - r, cy - r), (8 + r, cy + r)]), fill=255)
    inside = Image.new("L", image.size, 0)
    ImageDraw.Draw(inside).polygon(px(outline), fill=255)
    image.paste(GRAPHITE, (0, 0), ImageChops.multiply(pupil, inside))
    stroke(ImageDraw.Draw(image), outline, 1.45, GRAPHITE, closed=True)
    return image


def all_icons():
    icons = {name: arrow(name) for name in ARROWS}
    icons.update(("digit_%d" % n, glyph(str(n), AMBER, PLUM, 12.5, 600)) for n in range(1, 10))
    icons.update(("letter_%s" % c.lower(), glyph(c, BLUE, BUTTER, 11, 400))
                 for c in string.ascii_uppercase)
    icons.update(("eye_%s" % d, eye(d)) for d in ("up", "down"))
    return icons


def with_margin(image):
    """The icon a little smaller, at the left, with a clear strip on its right: Sublime draws a
    gutter icon right against the line number (Jakub)."""
    side = 16 * BIG
    small = int(side * (16 - MARGIN) / 16)
    out = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    out.paste(image.resize((small, small), Image.LANCZOS), (0, (side - small) // 2))
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    icons = {name: with_margin(image) for name, image in all_icons().items()}
    for name, image in icons.items():
        for suffix, size in SIZES.items():
            image.resize((size, size), Image.LANCZOS).save(os.path.join(OUT, name + suffix + ".png"))
    print("Wrote %d icons to %s/" % (len(icons), OUT), file=sys.stderr)


if __name__ == "__main__":
    main()
