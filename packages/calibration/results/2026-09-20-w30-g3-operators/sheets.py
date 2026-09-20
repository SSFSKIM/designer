#!/usr/bin/env python3
"""W30 G3 — native | WebGPU | CSS | difference, per standard profile, both scales.

    python3 sheets.py [--scale 2]

W29 G3b's `sheets.py` with two changes, and both are this child's subject.

**Four columns rather than three.** The CSS tier sits between the native capture
and the difference, because the σ law is the first operator in the project's
history that mirrors FULLY onto that tier — one `box-shadow` blur radius per
surface, evaluated from the same law — while the scatter's five leaves are
deliberately not mirrored at all. A sheet that showed only the WebGPU tier could
not show which half of the wave the second tier carries. The difference column
is native against WebGPU, the fidelity target.

**The THIN spans lead.** W29 G3b led with the largest spans because the shadow's
one σ was fitted there; this child's σ law is graded by the caster and the place
it moves most is the thin end — 11.0 CSS px down to about 2.1, a factor of five
— so `capsule-button` (span 44) and `rrect-sm` (span 32) come first and the
span-160 cells come last. The eye reads the two ends of one law on one sheet.

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

# Thin spans first (the caster grading's own end), then the knee, then the two
# spans where the shipped σ was a third too narrow. The last two are the
# backdrops the scatter is read on rather than the shadow.
ACTIVE_CELLS = [
    "checkerboard__rrect-sm__rest",
    "checkerboard__capsule-button__rest",
    "light-solid__capsule-button__rest",
    "checkerboard__rrect-md__rest",
    "checkerboard__rrect-ml__rest",
    "checkerboard__rrect-lg__rest",
    "photo__rrect-lg__rest",
    "checkerboard-4__rrect-md__rest",
    "checkerboard-64__rrect-md__rest",
]
INACTIVE_CELLS = [
    "checkerboard__capsule-button__inactive",
    "checkerboard__rrect-md__inactive",
    "checkerboard__rrect-lg__inactive",
    "photo__rrect-md__inactive",
    "light-solid__capsule-button__inactive",
]
AMPLIFY = 8


def load(path: str) -> Image.Image | None:
    return Image.open(path).convert("RGB") if os.path.exists(path) else None


def sheet(profile: str, pose: str, cells: list[str], scale: int) -> None:
    rows = []
    for cell in cells:
        native = load(os.path.join(FIXTURES, profile, f"{cell}.png"))
        webgpu = load(os.path.join(CAPTURES, profile, cell, f"{cell}__webgpu.png"))
        css = load(os.path.join(CAPTURES, profile, cell, f"{cell}__css.png"))
        if native is None or webgpu is None or native.size != webgpu.size:
            continue
        if css is not None and css.size != native.size:
            css = None
        diff = ImageChops.difference(native, webgpu).point(lambda v: min(255, v * AMPLIFY))
        rows.append((cell, native, webgpu, css, diff))
    if not rows:
        return
    pad, label = 8, 18
    width = max(
        sum(image.width for image in (row[1], row[2], row[4])) + (row[3].width if row[3] else 0)
        + 5 * pad
        for row in rows
    )
    height = sum(row[1].height + label + pad for row in rows) + pad
    canvas = Image.new("RGB", (width, height), (24, 24, 26))
    draw = ImageDraw.Draw(canvas)
    y = pad
    for cell, native, webgpu, css, diff in rows:
        draw.text(
            (pad, y),
            f"{cell}   native | WebGPU | " + ("CSS | " if css else "(no CSS row) | ")
            + f"difference x{AMPLIFY} (native vs WebGPU)",
            fill=(220, 220, 225),
        )
        y += label
        x = pad
        for image in (native, webgpu, css, diff):
            if image is None:
                continue
            canvas.paste(image, (x, y))
            x += image.width + pad
        y += native.height + pad
    if scale != 1:
        canvas = canvas.resize((canvas.width * scale, canvas.height * scale), Image.NEAREST)
    os.makedirs(OUT, exist_ok=True)
    name = f"{profile.replace('apple-macos-27.0-', '')}__{pose}.png"
    canvas.save(os.path.join(OUT, name))
    print(f"wrote sheets/{name} ({len(rows)} cells)")


scale = int(sys.argv[sys.argv.index("--scale") + 1]) if "--scale" in sys.argv else 2
for profile in PROFILES:
    sheet(profile, "active", ACTIVE_CELLS, scale)
    sheet(profile, "inactive", INACTIVE_CELLS, scale)
