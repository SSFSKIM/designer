#!/usr/bin/env python3
"""W32 G2 — the far-exterior halo, measured where W29 G3b's eye measured it (§5.169 §5).

    VITREA_WEB_CAPTURES=<a capture tree> python3 halo.py <label>

The tracker's far-halo entry and claims §5.154's review closure (a) both read one
number off a sheet: the mean of the ΔE × 8 difference panel over the FAR
EXTERIOR — every pixel more than 12 CSS px outside the component's declared box
— on `checkerboard__rrect-lg__inactive`, where it read **17.42** on the WebGPU
sheet and **15.89** on the CSS one against **≤ 5.92** on every active strip of
the same profile. That halo was vitrea drawing the full ACTIVE shadow in the
inactive pose, because both receded documents carried their active document's
anchors leaf for leaf.

W32 Decision Log 2 set the receded amplitude to zero, and W32 G1 reported the
halo gone by eye. This is the same number at the shipped bytes, computed from
the fixtures and the canonical capture tree rather than read back off a PNG, with
the active strip printed beside it as the same comparison W29 G3b made. The
definition — the band, the amplification and the 0–255 scale — is that gate's and
is not restated.

Run twice, once against the canonical tree and once against
`web-captures-superseded/49490eb9ff7a/`, which is the 0.21.0 generation's own
tree — so the before and the after are two readings of one function over two sets
of pixels, rather than one reading against a number somebody typed.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent.parent
REPO = PACKAGE.parent.parent
FIXTURES = REPO / "apps/reference-apple/fixtures"
CAPTURES = Path(os.environ.get("VITREA_WEB_CAPTURES", str(PACKAGE / "web-captures")))

FAR_CSS_PX = 12
GAIN = 8

CELLS = (
    ("apple-macos-27.0-1x-light-standard-glass0.5", "rrect-lg", "checkerboard__rrect-lg__inactive"),
    ("apple-macos-27.0-1x-light-standard-glass0.5", "rrect-lg", "checkerboard__rrect-lg__rest"),
    ("apple-macos-27.0-2x-light-standard-glass0.5", "rrect-lg", "checkerboard__rrect-lg__inactive"),
    ("apple-macos-27.0-2x-light-standard-glass0.5", "rrect-lg", "checkerboard__rrect-lg__rest"),
)


def srgb_to_linear(byte: int) -> float:
    c = byte / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def oklab(rgb):
    r, g, b = (srgb_to_linear(v) for v in rgb)
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)


def main() -> int:
    scenes = json.loads((REPO / "apps/reference-apple/scenes.json").read_text())
    canvas = scenes["canvas"]
    label = sys.argv[1] if len(sys.argv) > 1 else "at the tree named by the environment"
    print(f"W32 G2 — the far-exterior difference, W29 G3b's band and amplification — {label}")
    print("=" * 96)
    print(f"  every pixel more than {FAR_CSS_PX} CSS px outside the component's declared box;")
    print(f"  mean of ΔE(OKLab) × {GAIN} on 0–255, which is what the sheets draw.")
    print(f"  tree: {CAPTURES}")
    print()
    print(f"  {'profile':<46}{'scene':<38}{'tier':<8}{'far mean':>9}{'far max':>9}")
    for profile, component, scene in CELLS:
        native_path = FIXTURES / profile / f"{scene}.png"
        for tier in ("webgpu", "css"):
            web_path = CAPTURES / profile / scene / f"{scene}__{tier}.png"
            if not native_path.exists() or not web_path.exists():
                print(f"  {profile:<46}{scene:<38}{tier:<8}   (absent)")
                continue
            native = Image.open(native_path).convert("RGB")
            web = Image.open(web_path).convert("RGB")
            n = native.load()
            w = web.load()
            scale = native.width / canvas["width"]
            size = scenes["components"][component]["size"]
            x0 = ((canvas["width"] - size[0]) / 2 - FAR_CSS_PX) * scale
            y0 = ((canvas["height"] - size[1]) / 2 - FAR_CSS_PX) * scale
            x1 = x0 + (size[0] + 2 * FAR_CSS_PX) * scale
            y1 = y0 + (size[1] + 2 * FAR_CSS_PX) * scale
            total = 0.0
            count = 0
            worst = 0.0
            for y in range(native.height):
                inside_y = y0 <= y < y1
                for x in range(native.width):
                    if inside_y and x0 <= x < x1:
                        continue
                    a, b = oklab(n[x, y]), oklab(w[x, y])
                    d = sum((a[i] - b[i]) ** 2 for i in range(3)) ** 0.5
                    value = min(255.0, d * GAIN * 255)
                    total += value
                    worst = max(worst, value)
                    count += 1
            print(f"  {profile:<46}{scene:<38}{tier:<8}{total / count:>9.2f}{worst:>9.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
