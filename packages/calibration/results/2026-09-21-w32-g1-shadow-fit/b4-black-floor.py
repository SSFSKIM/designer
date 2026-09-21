#!/usr/bin/env python3
"""The black floor under the shadow band — W32 G1 review closure, finding B-4.

`eye.md`'s span-160 paragraph said the ΔE panel was "black past the rim band on
every one of the four" `checkerboard-8__rrect-lg__rest` sheets. It is not: on
every black square of that checkerboard the panel carries a mid-grey, and this
script is the reading that says why.

**What it measures, and over what.** For one scene on one profile it takes the
native fixture and the WebGPU capture the gate's canonical read wrote, restricts
to the EXTERIOR — the canvas minus the component's declared rect, which for
`rrect-lg` is the 20 CSS px frame the whole shadow lives in — and splits that
exterior by what the BACKDROP is doing there:

  * the **black floor**: pixels whose native byte is exactly (0, 0, 0). Apple
    reads 0 on every one of them; the question is what vitrea reads.
  * the **lit** pixels: the checkerboard's white squares, where the shadow is a
    transmission and both sides have a falloff to compare byte for byte. These
    are reported at 3 CSS px and further from the declared rect, which is the
    admitted-band rule's own inner edge (W32 G0, claims §5.166 §1) — inside it
    lies the body's contour and Apple's rim, which are not the shadow.

The exterior rect is taken from `apps/reference-apple/scenes.json` — the single
source for the canvas and the components — and scaled by the capture's own pixel
size, so a 2x bed is read at 2x without a second constant.

**Why one LSB is visible at all.** The sheets amplify OKLab ΔE by eight. OKLab
takes a cube root of linear light, whose derivative diverges at zero, so the
distance from sRGB byte 0 to byte 1 is 0.067 — about the same as the distance
from 128 to 160 — and eight times that is a mid-grey. The script prints the
figure rather than asserting it, from the same OKLab the metric uses.

Run:

    python3 results/2026-09-21-w32-g1-shadow-fit/b4-black-floor.py

from `packages/calibration`, or with `--repo-root` from anywhere. Reads only;
writes nothing.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image

# One scene per span, all on `checkerboard-8` so the black floor and the lit
# falloff are both present in the same exterior at the same pitch.
SCENES = (
    ("capsule-button", 44, "checkerboard-8__capsule-button__rest"),
    ("rrect-ml", 128, "checkerboard-8__rrect-ml__rest"),
    ("rrect-lg", 160, "checkerboard-8__rrect-lg__rest"),
)

PROFILES = (
    "apple-macos-27.0-1x-light-standard-glass0.5",
    "apple-macos-27.0-2x-light-standard-glass0.5",
    "apple-macos-27.0-1x-dark-standard-glass0.5",
    "apple-macos-27.0-2x-dark-standard-glass0.5",
)


def srgb_to_linear(byte: int) -> float:
    c = byte / 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def oklab(rgb: tuple[int, int, int]) -> tuple[float, float, float]:
    r, g, b = (srgb_to_linear(v) for v in rgb)
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l_, m_, s_ = (v ** (1 / 3) if v >= 0 else -((-v) ** (1 / 3)) for v in (l, m, s))
    return (
        0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_,
        1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_,
        0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_,
    )


def delta_e(a: tuple[int, int, int], b: tuple[int, int, int]) -> float:
    la, aa, ba = oklab(a)
    lb, ab, bb = oklab(b)
    return ((la - lb) ** 2 + (aa - ab) ** 2 + (ba - bb) ** 2) ** 0.5


def exterior_rect(scenes: dict, component: str) -> tuple[float, float, float, float]:
    """The component's declared rect in CSS px, centred on the canvas."""
    width, height = scenes["canvas"]["width"], scenes["canvas"]["height"]
    size = scenes["components"][component]["size"]
    x0 = (width - size[0]) / 2
    y0 = (height - size[1]) / 2
    return (x0, y0, x0 + size[0], y0 + size[1])


def read(path: Path) -> tuple[Image.Image, object, int, int]:
    image = Image.open(path).convert("RGB")
    return image, image.load(), image.width, image.height


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=None)
    args = parser.parse_args()

    here = Path(__file__).resolve()
    root = Path(args.repo_root).resolve() if args.repo_root else here.parents[4]
    scenes = json.loads((root / "apps/reference-apple/scenes.json").read_text())
    canvas_w = scenes["canvas"]["width"]

    print("one LSB at the black floor, in the units the sheets amplify")
    print(f"  ΔE(OKLab) between sRGB (0,0,0) and (1,1,1)  {delta_e((0, 0, 0), (1, 1, 1)):.4f}")
    print(f"  the same, × 8 as the sheets draw it         "
          f"{min(1.0, delta_e((0, 0, 0), (1, 1, 1)) * 8):.4f} of full scale")
    print(f"  for scale, ΔE between (128,128,128) and (160,160,160)  "
          f"{delta_e((128, 128, 128), (160, 160, 160)):.4f}")
    print()

    header = (
        f"{'profile':52} {'span':>4} {'black ext':>9} {'web (1,1,1)':>11} "
        f"{'web >1':>6} | {'lit ≥3px':>8} {'Δ=0':>7} {'|Δ|≤1':>7} {'|Δ|max':>6}"
    )
    print(header)
    print("-" * len(header))

    for profile in PROFILES:
        for component, span, scene in SCENES:
            native_path = root / "apps/reference-apple/fixtures" / profile / f"{scene}.png"
            web_path = (
                root
                / "packages/calibration/web-captures"
                / profile
                / scene
                / f"{scene}__webgpu.png"
            )
            if not native_path.exists() or not web_path.exists():
                print(f"{profile:52} {span:>4}  (absent)")
                continue
            _, native, width, height = read(native_path)
            _, web, web_width, web_height = read(web_path)
            if (width, height) != (web_width, web_height):
                raise SystemExit(f"size mismatch on {scene} / {profile}")
            scale = width / canvas_w
            x0, y0, x1, y1 = (v * scale for v in exterior_rect(scenes, component))

            inner = 3 * scale  # the `0-3` band, excluded from the lit reading

            black = ones = above_one = lit = lit_equal = lit_within_one = 0
            lit_max = 0
            for y in range(height):
                inside_y = y0 <= y < y1
                for x in range(width):
                    if inside_y and x0 <= x < x1:
                        continue
                    n = native[x, y]
                    w = web[x, y]
                    if n == (0, 0, 0):
                        black += 1
                        if w == (1, 1, 1):
                            ones += 1
                        elif w != (0, 0, 0):
                            above_one += 1
                        continue
                    if min(n) < 200:
                        continue
                    # The checkerboard's white squares under the shadow: a
                    # transmission both sides can be compared through, read
                    # outside the `0-3` band where the contour and the rim live.
                    gap = max(x0 - x, x - (x1 - 1), y0 - y, y - (y1 - 1))
                    if gap < inner:
                        continue
                    lit += 1
                    d = max(abs(n[i] - w[i]) for i in range(3))
                    lit_equal += d == 0
                    lit_within_one += d <= 1
                    lit_max = max(lit_max, d)
            print(
                f"{profile:52} {span:>4} {black:>9} {ones:>11} {above_one:>6} | "
                f"{lit:>8} {lit_equal:>7} {lit_within_one:>7} {lit_max:>6}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
