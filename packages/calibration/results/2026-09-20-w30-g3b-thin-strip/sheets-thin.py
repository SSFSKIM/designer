#!/usr/bin/env python3
"""W30 G3b — the 44 px capsule, native | before | after | difference.

    python3 sheets-thin.py

The cell the strip is on, at the three profiles charter Decision Log 5 asks to
see it at: the dark bed at 1x, where it is visible to the eye, and the light bed
at both scales.

**The "before" column is recovered from W30 G3's committed sheets rather than
re-rendered.** The web side of a read lives in `packages/calibration/web-captures/`,
which is gitignored and holds one generation — this gate's read overwrote G3's —
so the only committed pixels of the defective renderer are inside
`results/2026-09-20-w30-g3-operators/sheets/*.png`. Those were written at
`--scale 2` with `Image.NEAREST`, which is exactly invertible by taking every
second pixel, and the rows are laid out on a fixed pitch. This file finds the
right row by **matching its native column against the fixture** rather than by
counting rows, so a sheet whose cell list differs from the one assumed here
fails to find a row instead of cropping the wrong one.

Nothing under G3's directory is written.
"""
from __future__ import annotations

import os

from PIL import Image, ImageChops, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
PACKAGE = os.path.dirname(os.path.dirname(HERE))
REPO = os.path.dirname(os.path.dirname(PACKAGE))
FIXTURES = os.path.join(REPO, "apps", "reference-apple", "fixtures")
CAPTURES = os.path.join(PACKAGE, "web-captures")
BEFORE = os.path.join(os.path.dirname(HERE), "2026-09-20-w30-g3-operators", "sheets")
OUT = os.path.join(HERE, "sheets")

# `sheets.py`'s own layout constants, and the scale it was run at.
PAD, LABEL, SHEET_SCALE, AMPLIFY = 8, 18, 2, 8

CASES = [
    ("apple-macos-27.0-1x-dark-standard-glass0.5", "checkerboard__capsule-button__rest"),
    ("apple-macos-27.0-1x-light-standard-glass0.5", "checkerboard__capsule-button__rest"),
    ("apple-macos-27.0-2x-light-standard-glass0.5", "checkerboard__capsule-button__rest"),
]


def load(path: str) -> Image.Image | None:
    return Image.open(path).convert("RGB") if os.path.exists(path) else None


def unscale(image: Image.Image) -> Image.Image:
    """Undo `sheets.py`'s NEAREST upscale exactly."""
    return image.resize((image.width // SHEET_SCALE, image.height // SHEET_SCALE), Image.NEAREST)


def before_row(profile: str, native: Image.Image) -> Image.Image | None:
    """G3's WebGPU column for the row whose native column IS this fixture."""
    name = f"{profile.replace('apple-macos-27.0-', '')}__active.png"
    sheet = load(os.path.join(BEFORE, name))
    if sheet is None:
        return None
    flat = unscale(sheet)
    pitch = native.height + LABEL + PAD
    rows = (flat.height - PAD) // pitch
    for index in range(rows):
        top = PAD + index * pitch + LABEL
        box = (PAD, top, PAD + native.width, top + native.height)
        if flat.crop(box).tobytes() == native.tobytes():
            web = (PAD * 2 + native.width, top, PAD * 2 + native.width * 2, top + native.height)
            return flat.crop(web)
    return None


def compose(profile: str, cell: str) -> None:
    native = load(os.path.join(FIXTURES, profile, f"{cell}.png"))
    after = load(os.path.join(CAPTURES, profile, cell, f"{cell}__webgpu.png"))
    if native is None or after is None or native.size != after.size:
        print(f"skipped {profile} / {cell}: no native or no capture at this gate")
        return
    before = before_row(profile, native)
    if before is None:
        print(f"skipped {profile} / {cell}: no matching row in W30 G3's sheet")
        return

    columns = [
        ("native", native),
        ("before — W30 G3, the defective renderer", before),
        ("after — W30 G3b", after),
        (
            f"before vs after x{AMPLIFY}",
            ImageChops.difference(before, after).point(lambda v: min(255, v * AMPLIFY)),
        ),
        (
            f"native vs after x{AMPLIFY}",
            ImageChops.difference(native, after).point(lambda v: min(255, v * AMPLIFY)),
        ),
    ]
    width = sum(image.width for _, image in columns) + PAD * (len(columns) + 1)
    canvas = Image.new("RGB", (width, native.height + LABEL * 2 + PAD * 2), (24, 24, 26))
    draw = ImageDraw.Draw(canvas)
    draw.text((PAD, PAD), f"{profile}   {cell}", fill=(220, 220, 225))
    x = PAD
    for label, image in columns:
        draw.text((x, PAD + LABEL), label, fill=(200, 200, 208))
        canvas.paste(image, (x, PAD + LABEL * 2))
        x += image.width + PAD
    canvas = canvas.resize((canvas.width * 2, canvas.height * 2), Image.NEAREST)
    os.makedirs(OUT, exist_ok=True)
    name = f"{profile.replace('apple-macos-27.0-', '')}__{cell}.png"
    canvas.save(os.path.join(OUT, name))
    print(f"wrote sheets/{name}")


for profile, cell in CASES:
    compose(profile, cell)
