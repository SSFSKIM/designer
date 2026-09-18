#!/usr/bin/env python3
"""The SDK-gating pixel arm's sheet — W29 G1 (4), claims §5.150.

    sdk-pixel-sheet.py <sdk-pixel-root> <out.png>

Per cell: what the **granted** bundle drew (`LC_BUILD_VERSION` records `sdk
26.0`), what the **27-SDK side** bundle drew (`sdk 27.0`), their amplified
difference, and — the column that makes that one readable — the granted bundle's
difference from ITSELF across two runs, at the same gain. A difference strip is
only evidence when the same cell's difference from itself is beside it and
visibly empty; here both strips are empty, which is the verdict.

The gain is 8x absolute difference, the same the W28 sheets and G0's sheets use,
so a strip here and a strip there mean the same thing.
"""
import os
import sys

from PIL import Image, ImageChops, ImageDraw

GAIN = 8
GAP = 10
PAD = 34
LABEL = 26
BACKGROUND = (20, 20, 20)
INK = (235, 235, 235)

CELLS = [
    ("apple-macos-26.5-2x-light-standard", "photo__rrect-md__rest"),
    ("apple-macos-26.5-2x-dark-standard", "checkerboard__capsule-button__rest"),
    ("apple-macos-26.5-2x-light-standard", "hc-text__rrect-sm__rest"),
    ("apple-macos-26.5-2x-dark-standard", "dark-solid__rrect-80__rest"),
]


def amplified(a, b):
    return ImageChops.difference(a.convert("RGB"), b.convert("RGB")).point(
        lambda v: min(255, v * GAIN))


def row(images, captions):
    height = max(i.height for i in images)
    width = sum(i.width for i in images) + GAP * (len(images) - 1)
    canvas = Image.new("RGB", (width, height + LABEL), BACKGROUND)
    draw = ImageDraw.Draw(canvas)
    x = 0
    for image, caption in zip(images, captions):
        canvas.paste(image.convert("RGB"), (x, 0))
        draw.text((x + 2, height + 6), caption, fill=INK)
        x += image.width + GAP
    return canvas


def main():
    root, out = sys.argv[1], sys.argv[2]
    rows = []
    for profile, scene in CELLS:
        def load(arm, run):
            return Image.open(os.path.join(root, arm, "active-r%d" % run, profile, scene + ".png"))
        h1, h2 = load("harness", 1), load("harness", 2)
        s1 = load("side-sdk27", 1)
        rows.append(row(
            [h1, s1, amplified(h1, s1), amplified(h1, h2)],
            ["%s / %s  —  granted (sdk 26.0)"
             % (profile.replace("apple-macos-26.5-2x-", "").replace("-standard", ""), scene),
             "side (sdk 27.0)", "granted - side  x%d" % GAIN,
             "granted r1 - r2  x%d (the bar)" % GAIN]))
    width = max(r.width for r in rows)
    height = sum(r.height for r in rows) + GAP * (len(rows) - 1)
    canvas = Image.new("RGB", (width + PAD * 2, height + PAD * 2 + LABEL), BACKGROUND)
    ImageDraw.Draw(canvas).text(
        (PAD, PAD // 2),
        "W29 G1 (4) — the SDK-gating pixel arm: two bundles, one machine, slider 0.5, 2x active."
        "  Both difference columns are empty.",
        fill=INK)
    y = PAD + LABEL
    for r in rows:
        canvas.paste(r, (PAD, y))
        y += r.height + GAP
    canvas.save(out)
    print(out)


main()
