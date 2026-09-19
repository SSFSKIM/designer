#!/usr/bin/env python3
"""W29 G3 — native | vitrea | difference, per 27 profile, per tier.

    python3 sheets.py [--scale 3]

Acceptance clause 4's seventh line and the wave's "look at it" rule: metrics are
not the whole verdict, so the refitted material goes beside the fixture it was
fitted to and the difference goes beside both, amplified so the eye can see what
SSIM is scoring.

The native side is the committed fixture. The web side is the canonical
`web-captures/` tree the sealed read wrote — which is gitignored and lives on the
capture machine, so this script runs there and only its OUTPUT is committed.

The cells are chosen for what they show rather than for how they score: the two
near-tone backdrops where claims §5.151 §4's finding lives, a structured backdrop
at the pitch the diffusion residual is worst on, the photograph, a tinted cell,
and the largest span — which is where every row this child missed sits.
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
CELLS = [
    "dark-solid__capsule-button__rest",
    "impulse__capsule-button__rest",
    "checkerboard__rrect-md__rest",
    "photo__rrect-md__rest",
    "photo__capsule-button__rest-tint-orange",
    "checkerboard__rrect-lg__rest",
    "photo__rrect-lg__rest",
]
AMPLIFY = 8


def load(path: str) -> Image.Image | None:
    return Image.open(path).convert("RGB") if os.path.exists(path) else None


def sheet(profile: str, tier: str, scale: int) -> None:
    rows = []
    for cell in CELLS:
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
    name = f"{profile.replace('apple-macos-27.0-', '')}__{tier}.png"
    canvas.save(os.path.join(OUT, name))
    print(f"wrote sheets/{name} ({len(rows)} cells)")


scale = int(sys.argv[sys.argv.index("--scale") + 1]) if "--scale" in sys.argv else 2
for profile in PROFILES:
    for tier in ("webgpu", "css"):
        sheet(profile, tier, scale)
