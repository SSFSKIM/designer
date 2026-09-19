#!/usr/bin/env python3
"""W29 G3b — native | vitrea | difference, per 27 profile, per tier, both poses.

    python3 sheets.py [--scale 2]

G3's `sheets.py` with two changes, and both are this child's subject. The cell
list leads with the LARGEST SPANS, because the shadow is what moved and the
shadow is what the eye reads outside a big surface; and every profile gets an
INACTIVE sheet beside its active one, because the recede is the other half of
the ruling and a pose nobody looked at is a pose nobody checked.

The native side is the committed fixture. The web side is the canonical
`web-captures/` tree the sealed read wrote — gitignored, on the capture machine —
so this script runs there and only its output is committed.
"""
from __future__ import annotations

import os
import sys

from PIL import Image, ImageChops, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
PACKAGE = os.path.dirname(os.path.dirname(HERE))
REPO = os.path.dirname(os.path.dirname(PACKAGE))
FIXTURES = os.path.join(REPO, "apps", "reference-apple", "fixtures")
CAPTURES = os.path.join(PACKAGE, "web-captures")
OUT = os.path.join(HERE, "sheets")

PROFILES = [
    "apple-macos-27.0-1x-light-standard-glass0.5",
    "apple-macos-27.0-2x-light-standard-glass0.5",
    "apple-macos-27.0-1x-dark-standard-glass0.5",
    "apple-macos-27.0-2x-dark-standard-glass0.5",
    "apple-macos-27.0-1x-light-reduced-transparency-glass0.5",
    "apple-macos-27.0-1x-light-increased-contrast-coupled-glass0.5",
]

# The shadow's own cells first — the two largest spans and the stack, which is
# where the seven rows §5.153 §5 named sit and where the exterior is most of what
# the eye sees — then the near-tone and photographic bodies G3's sheet carried.
ACTIVE_CELLS = [
    "checkerboard__rrect-lg__rest",
    "checkerboard__rrect-ml__rest",
    "checkerboard__glass-over-glass__rest",
    "checkerboard__rrect-md__rest",
    "checkerboard__capsule-button__rest",
    "photo__rrect-lg__rest",
    "light-solid__rrect-md__rest",
]
INACTIVE_CELLS = [
    "checkerboard__rrect-lg__inactive",
    "checkerboard__rrect-md__inactive",
    "checkerboard__capsule-button__inactive",
    "photo__rrect-md__inactive",
    "photo__capsule-button__inactive",
    "impulse__capsule-button__inactive",
    "light-solid__capsule-button__inactive",
]
AMPLIFY = 8


def load(path: str) -> Image.Image | None:
    return Image.open(path).convert("RGB") if os.path.exists(path) else None


def sheet(profile: str, tier: str, pose: str, cells: list[str], scale: int) -> None:
    rows = []
    for cell in cells:
        native = load(os.path.join(FIXTURES, profile, f"{cell}.png"))
        web = load(os.path.join(CAPTURES, profile, cell, f"{cell}__{tier}.png"))
        if native is None or web is None or native.size != web.size:
            continue
        diff = ImageChops.difference(native, web).point(lambda v: min(255, v * AMPLIFY))
        rows.append((cell, native, web, diff))
    if not rows:
        return
    pad, label = 8, 18
    width = max(sum(i.width for i in row[1:]) + 4 * pad for row in rows)
    height = sum(row[1].height + label + pad for row in rows) + pad
    canvas = Image.new("RGB", (width, height), (24, 24, 26))
    draw = ImageDraw.Draw(canvas)
    y = pad
    for cell, native, web, diff in rows:
        draw.text((pad, y), f"{cell}   native | vitrea | difference x{AMPLIFY}", fill=(220, 220, 225))
        y += label
        x = pad
        for image in (native, web, diff):
            canvas.paste(image, (x, y))
            x += image.width + pad
        y += native.height + pad
    if scale != 1:
        canvas = canvas.resize((canvas.width * scale, canvas.height * scale), Image.NEAREST)
    os.makedirs(OUT, exist_ok=True)
    name = f"{profile.replace('apple-macos-27.0-', '')}__{tier}__{pose}.png"
    canvas.save(os.path.join(OUT, name))
    print(f"wrote sheets/{name} ({len(rows)} cells)")


scale = int(sys.argv[sys.argv.index("--scale") + 1]) if "--scale" in sys.argv else 2
for profile in PROFILES:
    for tier in ("webgpu", "css"):
        sheet(profile, tier, "active", ACTIVE_CELLS, scale)
        sheet(profile, tier, "inactive", INACTIVE_CELLS, scale)
