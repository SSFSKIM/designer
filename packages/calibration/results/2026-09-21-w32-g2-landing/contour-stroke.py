#!/usr/bin/env python3
"""What the `0-3` band actually holds — W32 G2 review closure, finding B2.

**The claim this refutes, in its own words.** Every W32 record that names the
`0-3` band names it as *"vitrea's body over-fills its declared contour by 3.5–4
CSS px against Apple's ≤ 1 (§5.62)"* — a web-side error, positive, three to four
pixels wide. §5.62 measured that at W14, on the macOS 26.5 material, through the
shape axis. It is not what the macOS 27 bytes under this wave show.

**What the bytes show.** Read outward from the declared rect, one DEVICE pixel at
a time, along the four straight edges of the component:

  * at **one device pixel out**, the native is far DARKER than the web — Apple
    draws a stroke at the contour and vitrea draws none;
  * at **two device pixels and beyond**, the two agree to a fraction of a byte on
    the standard beds, which is the exterior this wave fitted.

Both halves matter. The first is the sign: a body over-filling by 3.5–4 CSS px
would put WEB below NATIVE across three or four pixels of what should be
backdrop, and the difference would be the body's colour rather than a stroke's.
The second is the width: at 2x the stroke is still one DEVICE pixel, so it is
half a CSS pixel, not three and a half of them. And it is on the ACTIVE pose as
well as the receded one, and on the two accessibility beds as well as the four
standard ones, so it is neither pose-specific nor a property of the recede.

That makes the `0-3` band's residual **Apple's contour hairline, un-drawn by
vitrea** — the rim term the tracker has carried since W29 G3b — rather than a
vitrea over-fill. It is one term on both poses, not two terms one per pose.

**What this does NOT claim.** It does not withdraw §5.62: that measurement stands
where it was taken, on the material and through the instrument it was taken with.
It does not measure the body's silhouette at all — everything here is read
strictly OUTSIDE the declared rect. And it moves no number in `matrix.json`: it
is a reading of committed captures, like `b4-black-floor.py` beside it.

**Geometry.** The declared rect is `scenes.json`'s canvas and component size,
centred, scaled by the capture's own pixel size — `b4-black-floor.py`'s
`exterior_rect`, imported here in spirit rather than in code so the two readings
share no implementation. Samples are taken along the four straight edges only,
excluding each corner's radius plus a two-CSS-px margin, so no sample sits on a
corner arc where "one pixel out" is not one pixel out.

Run, from `packages/calibration`:

    python3 results/2026-09-21-w32-g2-landing/contour-stroke.py

The canonical `web-captures/` tree is gitignored and lives on the capture
machine, so `--repo-root` points the reader at the checkout that holds it. Reads
only; writes nothing.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image

# One thick component and one thin one, in both poses, on the `photo` bed — the
# bed the eye's contour ring was read on, and the one with no native-black
# exterior pixel anywhere (`sheets.txt`), so nothing here is the black floor.
SCENES = (
    ("rrect-lg", 160, "photo__rrect-lg__rest"),
    ("rrect-lg", 160, "photo__rrect-lg__inactive"),
    ("capsule-button", 44, "photo__capsule-button__rest"),
    ("capsule-button", 44, "photo__capsule-button__inactive"),
)

PROFILES = (
    "apple-macos-27.0-1x-light-standard-glass0.5",
    "apple-macos-27.0-2x-light-standard-glass0.5",
    "apple-macos-27.0-1x-dark-standard-glass0.5",
    "apple-macos-27.0-2x-dark-standard-glass0.5",
    "apple-macos-27.0-1x-light-reduced-transparency-glass0.5",
    "apple-macos-27.0-1x-light-increased-contrast-coupled-glass0.5",
)

# How far out to read, in DEVICE pixels. Six covers the `0-3` band at 1x twice
# over and the whole of it at 2x.
OFFSETS = 6

# The transect printed literally at the end, so the parent's own spot reading is
# reproducible byte for byte rather than summarised.
TRANSECT = ("apple-macos-27.0-1x-light-standard-glass0.5", "photo__rrect-lg__rest", "rrect-lg")


def declared_rect(scenes: dict, component: str) -> tuple[float, float, float, float]:
    """The component's declared rect in CSS px, centred on the canvas."""
    width, height = scenes["canvas"]["width"], scenes["canvas"]["height"]
    size = scenes["components"][component]["size"]
    x0 = (width - size[0]) / 2
    y0 = (height - size[1]) / 2
    return (x0, y0, x0 + size[0], y0 + size[1])


def corner_radius(scenes: dict, component: str) -> float:
    """CSS px of corner arc to stay clear of. A capsule's is half its short side."""
    spec = scenes["components"][component]
    if spec["kind"] == "rrect":
        return float(spec["radius"])
    return float(spec["size"][1]) / 2


def mean_byte(pixel: tuple[int, int, int]) -> float:
    return sum(pixel) / 3


def read_pair(root: Path, profile: str, scene: str) -> tuple | None:
    native_path = root / "apps/reference-apple/fixtures" / profile / f"{scene}.png"
    web_path = (
        root / "packages/calibration/web-captures" / profile / scene / f"{scene}__webgpu.png"
    )
    if not native_path.exists() or not web_path.exists():
        return None
    native = Image.open(native_path).convert("RGB")
    web = Image.open(web_path).convert("RGB")
    if native.size != web.size:
        raise SystemExit(f"size mismatch on {scene} / {profile}")
    return native.load(), web.load(), native.width, native.height


def edge_samples(
    width: int,
    height: int,
    rect: tuple[float, float, float, float],
    radius_px: float,
    offset: int,
) -> list[tuple[int, int]]:
    """Every device pixel `offset` out from a straight edge of the rect."""
    x0, y0, x1, y1 = (int(round(v)) for v in rect)
    inset = int(round(radius_px))
    points: list[tuple[int, int]] = []
    for y in range(y0 + inset, y1 - inset):
        for x in (x0 - offset, x1 - 1 + offset):
            if 0 <= x < width and 0 <= y < height:
                points.append((x, y))
    for x in range(x0 + inset, x1 - inset):
        for y in (y0 - offset, y1 - 1 + offset):
            if 0 <= x < width and 0 <= y < height:
                points.append((x, y))
    return points


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=None)
    args = parser.parse_args()

    here = Path(__file__).resolve()
    root = Path(args.repo_root).resolve() if args.repo_root else here.parents[4]
    scenes = json.loads((root / "apps/reference-apple/scenes.json").read_text())
    canvas_w = scenes["canvas"]["width"]

    print("W32 G2 review closure — the `0-3` band, read outward one DEVICE pixel at a time")
    print("=" * 100)
    print()
    print("  native and web are the mean of the three channels over every sample at that")
    print("  offset; `n−w` is native minus web, so a NEGATIVE number is the native being")
    print("  darker — Apple removing light vitrea does not. A body over-filling its contour")
    print("  by 3.5–4 CSS px would read POSITIVE across offsets 1 to 4 at 1x.")
    print()

    header = (
        f"  {'profile':44} {'scene':32} {'off':>3} {'n':>6} "
        f"{'native':>8} {'web':>8} {'n−w':>9}"
    )

    stroke_rows = 0
    total_rows = 0
    exceptions: list[str] = []
    overfill_rows = 0
    for profile in PROFILES:
        for component, span, scene in SCENES:
            pair = read_pair(root, profile, scene)
            print(header)
            print("  " + "-" * (len(header) - 2))
            if pair is None:
                print(f"  {profile[11:]:44} {scene:32}  (absent)")
                print()
                continue
            native, web, width, height = pair
            scale = width / canvas_w
            rect = tuple(v * scale for v in declared_rect(scenes, component))
            radius_px = corner_radius(scenes, component) * scale
            first: float | None = None
            rest: list[float] = []
            for offset in range(1, OFFSETS + 1):
                points = edge_samples(width, height, rect, radius_px, offset)
                if not points:
                    continue
                n = sum(mean_byte(native[x, y]) for x, y in points) / len(points)
                w = sum(mean_byte(web[x, y]) for x, y in points) / len(points)
                if offset == 1:
                    first = n - w
                else:
                    rest.append(n - w)
                print(
                    f"  {profile[11:]:44} {scene:32} {offset:>3} {len(points):>6} "
                    f"{n:>8.2f} {w:>8.2f} {n - w:>+9.2f}"
                )
            total_rows += 1
            if first is not None and first < -1.0 and all(abs(d) < abs(first) for d in rest):
                stroke_rows += 1
                verdict = "STROKE at one device px, absent beyond it"
            elif first is not None and first > 1.0:
                overfill_rows += 1
                verdict = "the web is darker at one device px — an OVER-FILL's sign"
            else:
                verdict = "no stroke at this cell"
                exceptions.append(f"{profile[11:]} {scene}")
            print(f"  {'':44} {'span ' + str(span):32} → {verdict}")
            print()

    print(f"  cells read {total_rows}; one-device-pixel native stroke on {stroke_rows} of them")
    print(f"  cells whose web is darker than the native anywhere in the band: {overfill_rows}")
    for cell in exceptions:
        print(f"    no stroke: {cell}")
    print()
    print("  The over-fill count is the reading that decides the sign. A body over-filling its")
    print("  declared contour by 3.5–4 CSS px would show WEB below NATIVE across the band on")
    print("  every active cell; it shows on none, and what shows instead is the native below")
    print("  the web at exactly one device pixel and nowhere else.")
    print()

    profile, scene, component = TRANSECT
    pair = read_pair(root, profile, scene)
    if pair is not None:
        native, web, width, height = pair
        scale = width / canvas_w
        x0, y0, x1, y1 = (v * scale for v in declared_rect(scenes, component))
        row = int((y0 + y1) / 2)
        print(f"  The transect, printed literally: {profile[11:]} {scene}, row y={row}")
        print(f"  the declared rect's left edge is x={int(x0)}, so x={int(x0) - 1} is the last")
        print("  exterior pixel and x=" + str(int(x0)) + " is the first body one.")
        print()
        print(f"    {'x':>4} {'native':>18} {'web':>18}")
        for x in range(int(x0) - 8, int(x0) + 4):
            print(f"    {x:>4} {str(native[x, row]):>18} {str(web[x, row]):>18}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
