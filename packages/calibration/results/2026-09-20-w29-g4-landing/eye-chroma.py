#!/usr/bin/env python3
"""The chromatic half of `eye.md`, measured (W29 G4 review closure, claims §5.155).

`eye-measures.py` reads the residual as a LEVEL and as a STRUCTURE — interior mean and
standard deviation in linear luminance, plus the ring and the exterior. Both are
achromatic readings, and the sheets show something those two cannot: Apple's pane carries
the backdrop's own hue through it and vitrea's reads closer to neutral, which is why the
8x difference columns are coloured rather than grey. This file measures that, and the one
author tint whose pose behaviour `eye.md` described by eye rather than by number.

Two readings, and each names the strip it is a reading of:

**1. The harness bands** (`demo-and-harness-{light,dark}.png`, strips 2 and 3 — native |
vitrea | 8x difference). Over the same 200 x 100 device-pixel interior box
`eye-measures.py` uses, in OKLab: mean chroma, mean hue, and the spread of the two
opponent channels across the box — the spread is what "carries the backdrop's hue
through it" means, because a pane passing a coloured backdrop varies in a and b where a
neutral one does not. The per-channel mean absolute difference beside them is what makes
the difference column chromatic: three channels that differ by different amounts are a
coloured difference, and the sheets amplify it 8x.

**2. The demo band** (strip 1 — pinned active | pinned inactive | 8x difference), the
playground's orange `Publish` chip, in both the light-ground and the dark-ground rows.
The chip is an author tint composed through the material, so the pose moves it; `eye.md`
first said it recedes "at what reads as the same lightness", and this is the reading that
replaces that sentence. Measured on the SHEET rather than on the capture, because the
sheet is what was looked at and the demo captures were scratch: the band is the
playground at 2x scaled by 0.375, so the chip is a 54 x 28 block of sheet pixels.
White label glyphs are excluded by their own minimum channel; the chip's fill is what a
tint's lightness is a property of.

    python3 eye-chroma.py
"""
import math
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = HERE.split("/packages/")[0]
FIXTURES = os.path.join(REPO, "apps/reference-apple/fixtures")
CAPTURES = os.path.expanduser("~/vitrea-w29-g4-scratch/captures")
SHEETS = os.path.join(HERE, "sheets")

PROFILES = {
    "light": "apple-macos-27.0-2x-light-standard-glass0.5",
    "dark": "apple-macos-27.0-2x-dark-standard-glass0.5",
}
SCENES = ("photo__rrect-md__rest", "photo__rrect-md__inactive")

# The demo band of either sheet, in sheet pixels. The three columns are pasted at
# x = 40, 846 and 1652 (PAD, then the scaled image width plus sheet.py's 8 px gap), and
# the band's images start at y = 64 (PAD plus the 24 px caption strip).
COLUMN = {"active": 40, "inactive": 846, "difference": 1652}
# The two `Publish` chips, located by their own saturated fill in the active column and
# used as one box in all three columns — the page is the same page in each.
CHIPS = {"light ground row": (774, 520, 828, 548), "dark ground row": (774, 590, 828, 617)}
# The playground's registered-texture column, as offsets into the demo band's own width.
# It is the animated canvas of residual (d): at 8x its difference saturates over a third
# of the column, so a ranking that included it would be a ranking against an animation.
TEXTURE = (268, 544)


def linear(value):
    v = value / 255.0
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def oklab(rgb):
    r, g, b = (linear(c) for c in rgb)
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = (math.copysign(abs(v) ** (1 / 3), v) for v in (l, m, s))
    return (
        0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
        1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
        0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_,
    )


def stats(values):
    mean = sum(values) / len(values)
    sd = math.sqrt(sum((v - mean) ** 2 for v in values) / len(values))
    return mean, sd


def interior(image):
    """OKLab over the 200 x 100 device-pixel box at the centre — `eye-measures.py`'s."""
    width, height = image.size
    cx, cy = width // 2, height // 2
    px = image.load()
    return [
        oklab(px[x, y])
        for y in range(cy - 50, cy + 50)
        for x in range(cx - 100, cx + 100)
    ]


def harness():
    print("## 1. The harness bands — is the residual chromatic?")
    print("interior: the same 200x100 device px box at the pane's centre, in OKLab")
    print("C is chroma sqrt(a^2+b^2); spread is the sd of a and b ACROSS the box")
    print()
    for scheme, profile in PROFILES.items():
        for scene in SCENES:
            native = Image.open(os.path.join(FIXTURES, profile, f"{scene}.png")).convert("RGB")
            web = Image.open(
                os.path.join(CAPTURES, profile, scene, f"{scene}__webgpu.png")
            ).convert("RGB")
            rows = []
            for who, image in (("Apple", native), ("vitrea", web)):
                lab = interior(image)
                chroma = [math.hypot(a, b) for _, a, b in lab]
                _, sd_a = stats([a for _, a, _ in lab])
                _, sd_b = stats([b for _, _, b in lab])
                mean_a = sum(a for _, a, _ in lab) / len(lab)
                mean_b = sum(b for _, _, b in lab) / len(lab)
                rows.append(
                    (who, stats(chroma)[0], math.degrees(math.atan2(mean_b, mean_a)) % 360,
                     sd_a, sd_b)
                )
            print(f"{profile} {scene}")
            for who, c, hue, sd_a, sd_b in rows:
                print(
                    "  %-6s C %.5f   hue %6.1f deg   spread a %.5f  b %.5f"
                    % (who, c, hue, sd_a, sd_b)
                )
            print(
                "  ratios      C %.2fx   spread a %.2fx  b %.2fx"
                % (
                    rows[1][1] / rows[0][1],
                    rows[1][3] / rows[0][3],
                    rows[1][4] / rows[0][4],
                )
            )
            pn, pw = native.load(), web.load()
            width, height = native.size
            cx, cy = width // 2, height // 2
            channels = [[], [], []]
            for y in range(cy - 50, cy + 50):
                for x in range(cx - 100, cx + 100):
                    for k in range(3):
                        channels[k].append(abs(pn[x, y][k] - pw[x, y][k]))
            print(
                "  interior |delta| per channel, codes:  R %.2f  G %.2f  B %.2f"
                % tuple(sum(c) / len(c) for c in channels)
            )
            print()


def fill(image, x0, y0, x1, y1):
    """The chip's FILL: the modal pixel of its box.

    A mean over the box would be a blend of the fill with the white label glyphs and the
    antialiased corners, and a lightness claim about a tint has to be about the tint. The
    chip is 54 x 28 sheet pixels and its fill is the plurality of them by a wide margin,
    so the mode is the colour a reader sees rather than a robust approximation of it.
    """
    counts = {}
    px = image.load()
    for y in range(y0, y1):
        for x in range(x0, x1):
            counts[px[x, y]] = counts.get(px[x, y], 0) + 1
    rgb, n = max(counts.items(), key=lambda kv: kv[1])
    return rgb, n / ((x1 - x0) * (y1 - y0))


def demo():
    print("## 2. The demo band — the `Publish` chip through the pose")
    print("sheet pixels; the playground at 2x scaled 0.375 by sheet.py")
    print("the animated texture region (residual (d)) is excluded from the ranking:")
    print("it saturates the difference at 8x and is motion rather than material")
    print()
    for scheme in ("light", "dark"):
        sheet = Image.open(os.path.join(SHEETS, f"demo-and-harness-{scheme}.png")).convert("RGB")
        px = sheet.load()
        x0 = COLUMN["difference"]
        band = [
            max(px[x, y])
            for y in range(64, 625)
            for x in range(x0, x0 + 788)
            if not TEXTURE[0] <= x - x0 < TEXTURE[1]
        ]
        band.sort()
        print(f"demo-and-harness-{scheme}.png, band 1")
        for what, (bx0, by0, bx1, by1) in CHIPS.items():
            readings = {}
            for pose, offset in COLUMN.items():
                shift = offset - COLUMN["active"]
                rgb, share = fill(sheet, bx0 + shift, by0, bx1 + shift, by1)
                lightness, a, b = oklab(rgb)
                readings[pose] = (rgb, share, lightness, math.hypot(a, b))
            above = sum(1 for v in band if v < max(readings["difference"][0])) / len(band)
            print(f"  {what}")
            for pose in ("active", "inactive"):
                rgb, share, lightness, chroma = readings[pose]
                print(
                    "    %-8s fill rgb%-16s (%.0f%% of the box)  OKLab L %.4f  C %.4f"
                    % (pose, rgb, 100 * share, lightness, chroma)
                )
            print(
                "    the pose moves L by %+.4f and C by %+.4f"
                % (
                    readings["inactive"][2] - readings["active"][2],
                    readings["inactive"][3] - readings["active"][3],
                )
            )
            rgb, share, _, _ = readings["difference"]
            print(
                "    in the 8x difference column the chip reads rgb%s over %.0f%% of its box,"
                % (rgb, 100 * share)
            )
            print(
                "    brighter than %.2f%% of that column's pixels outside the texture region"
                % (100 * above)
            )
        print()


if __name__ == "__main__":
    harness()
    demo()
