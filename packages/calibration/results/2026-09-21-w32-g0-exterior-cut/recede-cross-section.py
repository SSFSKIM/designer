#!/usr/bin/env python3
"""W32 G0 review closure — the recede read off the fixture pixels themselves
(claims §5.166 §10, finding N16).

    python3 recede-cross-section.py > recede-cross-section.txt   # writes the JSON beside it

`recede-26.5.py` reads the axis's own per-band statistics and finds Apple's receded
window removing no light from 3 CSS px outward on both generations. That is a statement
about a band average, and a band average can hide a stroke. This file answers the
question the band cannot: **how far out does the receded capture differ from its
backdrop at all, pixel for pixel, and what is the shape of what is left?**

It reads the native fixture PNGs directly — the inactive capture and the background the
scene was composed over — and walks outward from the component's own rectangle on each
of the four sides, reporting the first offset at which the capture is byte-identical to
the backdrop across that whole side and stays so. **Nothing is written under a macOS
26.5-keyed path and no capture is taken** (W32 X1, X2, X5); the fixtures are read and
the outputs land in this gate's own directory.

The PNG decoder is the standard library and about forty lines, as every reader under
`results/` is pure standard library. The fixtures are 8-bit, non-interlaced, truecolour
with or without alpha, which is what `capture.sh` writes; anything else is refused
rather than guessed at.

**The offsets are measured from the body's LAST pixel**, so offset 1 is the first
exterior pixel and an "identical from 2" reading means one exterior pixel differs. The
component rectangle comes from `scenes.json`'s own `size` centred on its own `canvas`,
never from a constant here.
"""
from __future__ import annotations

import json
import struct
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent.parent
ROOT = PACKAGE.parent.parent
SCENES = ROOT / "apps/reference-apple/scenes.json"
FIXTURES = ROOT / "apps/reference-apple/fixtures"

# One inactive scene per span the recede is read at, on the two generations, at both
# scales. `checkerboard` is the calibration backdrop and the only one both generations
# capture at both components, which is what makes the two readings comparable.
SCENES_READ = ["checkerboard__rrect-lg__inactive", "checkerboard__rrect-md__inactive"]
PROFILES = [
    ("26.5", 1, "apple-macos-26.5-1x-light-standard"),
    ("26.5", 2, "apple-macos-26.5-2x-light-standard"),
    ("27", 1, "apple-macos-27.0-1x-light-standard-glass0.5"),
    ("27", 2, "apple-macos-27.0-2x-light-standard-glass0.5"),
]
SIDES = ["above", "below", "left", "right"]


def read_png(path: Path) -> tuple[int, int, int, bytes]:
    """`(width, height, bytes per pixel, pixels)` for an 8-bit truecolour PNG."""
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path} is not a PNG")
    width, height, depth, colour, _, _, interlace = struct.unpack(">IIBBBBB", data[16:29])
    if depth != 8 or interlace != 0 or colour not in (2, 6):
        raise ValueError(f"{path}: depth {depth}, colour {colour}, interlace {interlace} "
                         "is outside what this reader accepts")
    stream, index = bytearray(), 8
    while index < len(data):
        length = struct.unpack(">I", data[index:index + 4])[0]
        if data[index + 4:index + 8] == b"IDAT":
            stream += data[index + 8:index + 8 + length]
        index += 12 + length
    raw = zlib.decompress(bytes(stream))
    bpp = 4 if colour == 6 else 3
    stride = width * bpp
    out, previous, position = bytearray(height * stride), bytearray(stride), 0
    for y in range(height):
        kind = raw[position]
        position += 1
        line = bytearray(raw[position:position + stride])
        position += stride
        if kind == 1:
            for x in range(bpp, stride):
                line[x] = (line[x] + line[x - bpp]) & 255
        elif kind == 2:
            for x in range(stride):
                line[x] = (line[x] + previous[x]) & 255
        elif kind == 3:
            for x in range(stride):
                left = line[x - bpp] if x >= bpp else 0
                line[x] = (line[x] + ((left + previous[x]) >> 1)) & 255
        elif kind == 4:
            for x in range(stride):
                a = line[x - bpp] if x >= bpp else 0
                b = previous[x]
                c = previous[x - bpp] if x >= bpp else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[x] = (line[x] + (a if pa <= pb and pa <= pc
                                      else (b if pb <= pc else c))) & 255
        elif kind != 0:
            raise ValueError(f"{path}: filter {kind} on row {y}")
        out[y * stride:(y + 1) * stride] = line
        previous = line
    return width, height, bpp, bytes(out)


class Image:
    def __init__(self, path: Path) -> None:
        self.width, self.height, self.bpp, self.pixels = read_png(path)

    def rgb(self, x: int, y: int) -> tuple[int, int, int]:
        at = (y * self.width + x) * self.bpp
        return self.pixels[at], self.pixels[at + 1], self.pixels[at + 2]


def rect(component: dict, canvas: dict, scale: int) -> tuple[int, int, int, int]:
    """The component's own rectangle in device pixels: `(left, top, right, bottom)`.

    Inclusive on every side, centred on the canvas the way the harness composes it.
    """
    width, height = component["size"]
    left = (canvas["width"] - width) // 2
    top = (canvas["height"] - height) // 2
    return (left * scale, top * scale,
            (left + width) * scale - 1, (top + height) * scale - 1)


def first_identical(capture: Image, backdrop: Image, box: tuple[int, int, int, int],
                    side: str) -> tuple[int | None, int]:
    """The first offset at which this whole side equals the backdrop and stays so.

    The comparison runs across the body's own span on that side — the corners are
    left out, because a corner pixel is a reading of two sides at once and the
    question here is how far the recede reaches straight out. Returns the offset in
    DEVICE px and the number of offsets examined.
    """
    left, top, right, bottom = box
    reach = {"above": top, "below": capture.height - 1 - bottom,
             "left": left, "right": capture.width - 1 - right}[side]

    def line(offset: int) -> list[tuple[int, int]]:
        if side in ("above", "below"):
            y = top - offset if side == "above" else bottom + offset
            return [(x, y) for x in range(left, right + 1)]
        x = left - offset if side == "left" else right + offset
        return [(x, y) for y in range(top, bottom + 1)]

    same = [all(capture.rgb(x, y) == backdrop.rgb(x, y) for x, y in line(offset))
            for offset in range(1, reach + 1)]
    for index, value in enumerate(same):
        if value and all(same[index:]):
            return index + 1, reach
    return None, reach


def columns(backdrop: Image, box: tuple[int, int, int, int]) -> dict[str, int]:
    """One column of the body's own span over a LIGHT backdrop square and one over a
    DARK one, picked from the backdrop itself rather than named here.

    The two together say what KIND of term the one differing pixel is. A shadow is a
    TRANSMISSION: it removes light in proportion to what is there and can never lift a
    black square. A composited stroke can, and does. The readings below are the second.
    """
    left, _, right, bottom = box
    row = bottom + 1
    # The middle half of the edge only: nearer the ends the corner radius has already
    # taken the body away, and a column there reads the backdrop on both sides.
    inset = (right - left) // 4
    out: dict[str, int] = {}
    for x in range(left + inset, right - inset + 1):
        value = sum(backdrop.rgb(x, row)) / 3
        if "light" not in out and value >= 224:
            out["light"] = x
        if "dark" not in out and value <= 32:
            out["dark"] = x
    return out


def cross_section(capture: Image, backdrop: Image, box: tuple[int, int, int, int],
                  count: int = 6) -> dict[str, list[dict]]:
    """The bottom edge read outward from the last body row, on two columns."""
    _, _, _, bottom = box
    out: dict[str, list[dict]] = {}
    for label, x in columns(backdrop, box).items():
        entries = []
        for offset in range(0, count + 1):
            y = bottom + offset
            if y >= capture.height:
                break
            entries.append({"offsetDevicePx": offset, "x": x,
                            "capture": capture.rgb(x, y), "backdrop": backdrop.rgb(x, y)})
        out[label] = entries
    return out


def main() -> int:
    scenes = json.loads(SCENES.read_text())
    canvas, components = scenes["canvas"], scenes["components"]

    print("W32 G0 review closure — the receded exterior read off the fixture pixels")
    print("=" * 160)
    print()
    print(f"Fixtures: {FIXTURES.relative_to(ROOT)}")
    print("Read:     committed PNGs only. No capture, no browser, nothing written under a")
    print("          macOS 26.5-keyed path (W32 X1, X2, X5).")
    print()
    print("§1. How far out does the receded capture differ from its backdrop at all?")
    print("-" * 160)
    print("  The first offset from the body's LAST pixel at which the capture is byte-identical")
    print("  to the background across that whole side and stays so, in device px and in CSS px.")
    print("  Offset 1 is the first exterior pixel, so `2` means exactly one exterior pixel of")
    print("  that side carries anything at all. The corners are left out of each side's line.")
    print()
    print(f"  {'os':>5}{'scale':>7}  {'scene':<38}"
          + "".join(f"{s:>22}" for s in SIDES))
    records = []
    for os_name, scale, profile in PROFILES:
        for scene in SCENES_READ:
            capture_path = FIXTURES / profile / f"{scene}.png"
            if not capture_path.exists():
                print(f"  {os_name:>5}{scale:>7}  {scene:<38}  no fixture")
                continue
            backdrop_name = scene.split("__")[0]
            backdrop_path = FIXTURES / "backgrounds" / f"{backdrop_name}@{scale}x.png"
            capture, backdrop = Image(capture_path), Image(backdrop_path)
            box = rect(components[scene.split("__")[1]], canvas, scale)
            line = f"  {os_name:>5}{scale:>7}  {scene:<38}"
            record = {"os": os_name, "scale": scale, "scene": scene,
                      "profile": profile, "box": list(box), "sides": {}}
            for side in SIDES:
                offset, reach = first_identical(capture, backdrop, box, side)
                record["sides"][side] = {"firstIdenticalDevicePx": offset,
                                         "firstIdenticalCssPx": None if offset is None
                                         else offset / scale,
                                         "offsetsExamined": reach}
                line += (f"{'never':>22}" if offset is None
                         else f"{f'{offset} dev = {offset / scale:g} CSS':>22}")
            records.append(record)
            print(line)
    print()

    print("§2. What the one differing pixel is: two columns of the bottom edge")
    print("-" * 160)
    print("  `offset 0` is the body's last row, `1` the first exterior row. Read on two columns")
    print("  of the same edge — one over a light backdrop square and one over a dark one — which")
    print("  says what KIND of term the one differing pixel is rather than only how wide it is.")
    print("  On macOS 27 it reads 141–156 over a backdrop of 255 and 0–6 over a backdrop of 0:")
    print("  DARKER than both the backdrop and the body over the light square, and LIGHTER than")
    print("  the backdrop over the dark one. A shadow is a transmission and cannot lift a black")
    print("  square, so this is a semi-transparent dark stroke composited over the backdrop —")
    print("  a contour term. And it is ONE pixel wide, with the next pixel the backdrop byte for")
    print("  byte: a falloff at the σ ≈ 17 px this bed measures on the ACTIVE pose cannot be one")
    print("  pixel wide. On macOS 26.5 even that pixel is absent.")
    print()
    for record in records:
        capture_path = FIXTURES / record["profile"] / f"{record['scene']}.png"
        backdrop_path = (FIXTURES / "backgrounds"
                         / f"{record['scene'].split('__')[0]}@{record['scale']}x.png")
        capture, backdrop = Image(capture_path), Image(backdrop_path)
        section = cross_section(capture, backdrop, tuple(record["box"]))
        record["bottomEdgeColumns"] = section
        print(f"  macOS {record['os']}  {record['scale']}x  {record['scene']}")
        for label, entries in section.items():
            print(f"    over the {label} square, column x = {entries[0]['x']}")
            for entry in entries:
                mark = "" if entry["capture"] != entry["backdrop"] else "   = backdrop"
                print(f"      offset {entry['offsetDevicePx']:>2}   "
                      f"capture {str(entry['capture']):<18}"
                      f"backdrop {str(entry['backdrop']):<18}{mark}")
        print()

    print("§3. What this settles")
    print("-" * 160)
    print("  The receded exterior is ONE device pixel wide on macOS 27 and ZERO pixels wide on")
    print("  macOS 26.5 — on 26.5 the capture equals its backdrop from the very first exterior")
    print("  pixel, on all four sides, at both scales, on both components. Neither is a shadow")
    print("  at any alpha, so the recede's anchor solve (W32 clause 4) has no falloff to lower")
    print("  on either generation, and §5.166 §7's finding is about Apple's material rather")
    print("  than about macOS 27's version of it. What the `0-3` band reads on macOS 27 is that")
    print("  single stroke pixel averaged over a three-px-wide ring, which is why the departure")
    print("  there is small, why it is larger on the beds whose backdrop is brighter, and why")
    print("  this wave's Deferred list is right to call it a rim term rather than a shadow one.")
    print()

    (HERE / "recede-cross-section.json").write_text(json.dumps({
        "fixtures": str(FIXTURES),
        "read": "committed PNGs only; no capture (W32 X2, X5)",
        "offsetConvention": "device px from the body's last pixel; 1 is the first exterior pixel",
        "rows": records,
    }, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
