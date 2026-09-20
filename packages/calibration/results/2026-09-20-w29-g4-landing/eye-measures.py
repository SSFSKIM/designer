#!/usr/bin/env python3
"""The arithmetic behind `eye.md`'s residual table (W29 G4, claims §5.155).

Three readings over the four harness pairs on the sheets — interior mean and standard
deviation in linear luminance, the ring immediately outside the component's box, and the
exterior beyond it. None of them is a gated metric and none is compared against a
threshold: they exist so that a sentence in `eye.md` that says "the dark body passes
almost nothing of the photo through" can be checked by someone who did not look at the
sheet.

The interior box is 200 x 100 device pixels at the pane's centre, inside the rim and the
lens band of a 160 x 100 CSS px component at 2x. The ring is every pixel within 12 CSS px
outside that component's own box and the exterior is everything beyond it — the same
12 CSS px split the tracker's exterior-halo entry uses, so the two readings are
comparable.

    python3 eye-measures.py <harness-capture-dir>
"""
import math
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = HERE.split("/packages/")[0]
FIXTURES = os.path.join(REPO, "apps/reference-apple/fixtures")

PROFILES = (
    "apple-macos-27.0-2x-light-standard-glass0.5",
    "apple-macos-27.0-2x-dark-standard-glass0.5",
)
SCENES = ("photo__rrect-md__rest", "photo__rrect-md__inactive")
# The component's own box in DEVICE pixels at 2x: scenes.json's 160 x 100, centred.
BOX = (320, 200)
RING_CSS_PX = 12


def linear(value):
    v = value / 255.0
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def main():
    captures = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser(
        "~/vitrea-w29-g4-scratch/captures"
    )
    print("interior: 200x100 device px at centre, linear luminance")
    print("ring: within %d CSS px outside the component box; exterior: beyond it" % RING_CSS_PX)
    print("values are max-channel differences in encoded codes for ring/exterior")
    print()
    for profile in PROFILES:
        for scene in SCENES:
            native = Image.open(os.path.join(FIXTURES, profile, f"{scene}.png")).convert("RGB")
            web = Image.open(
                os.path.join(captures, profile, scene, f"{scene}__webgpu.png")
            ).convert("RGB")
            if native.size != web.size:
                raise SystemExit(f"{scene}: {native.size} against {web.size}")
            width, height = native.size
            cx, cy = width // 2, height // 2
            pad = RING_CSS_PX * 2
            bx0, by0 = cx - BOX[0] // 2, cy - BOX[1] // 2
            bx1, by1 = cx + BOX[0] // 2, cy + BOX[1] // 2
            pn, pw = native.load(), web.load()

            interior_n, interior_w, ring, exterior = [], [], [], []
            for y in range(height):
                for x in range(width):
                    a, b = pn[x, y], pw[x, y]
                    if abs(x - cx) < 100 and abs(y - cy) < 50:
                        interior_n.append(
                            0.2126 * linear(a[0]) + 0.7152 * linear(a[1]) + 0.0722 * linear(a[2])
                        )
                        interior_w.append(
                            0.2126 * linear(b[0]) + 0.7152 * linear(b[1]) + 0.0722 * linear(b[2])
                        )
                        continue
                    if bx0 <= x < bx1 and by0 <= y < by1:
                        continue
                    delta = max(abs(a[k] - b[k]) for k in range(3))
                    distance = max(bx0 - x, x - (bx1 - 1), by0 - y, y - (by1 - 1), 0)
                    (exterior if distance > pad else ring).append(delta)

            def stats(values):
                mean = sum(values) / len(values)
                sd = math.sqrt(sum((v - mean) ** 2 for v in values) / len(values))
                return mean, sd

            nm, ns = stats(interior_n)
            wm, ws = stats(interior_w)
            print(f"{profile} {scene}")
            print(
                "  interior  native %.4f / sd %.4f   vitrea %.4f / sd %.4f"
                "   sd ratio %.2f   mean %+.4f"
                % (nm, ns, wm, ws, ws / max(ns, 1e-9), wm - nm)
            )
            print(
                "  ring      mean %.2f  max %d        exterior  mean %.2f  max %d"
                % (
                    sum(ring) / len(ring),
                    max(ring),
                    sum(exterior) / len(exterior),
                    max(exterior),
                )
            )


if __name__ == "__main__":
    main()
