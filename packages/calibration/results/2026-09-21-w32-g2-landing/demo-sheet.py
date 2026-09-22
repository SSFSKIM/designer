#!/usr/bin/env python3
"""W32 G2 — the demo beside the harness, at the two thick spans (claims §5.169 §5).

    python3 demo-sheet.py --laws <dir of laws-shot.mjs's output> \
                          --demo <dir of demo-shot.mjs's output>

`CLAUDE.md`'s own instruction: *when you change the material, put the capture
next to the native fixture (and the demo next to the harness capture) and look.*
W31 G4's `sheet.py` is the file this replaces for one wave; it is not copied,
because what it composed was the site's material stage under the harness's two
spans and this wave has a THIRD thing to put in the row — a page whose whole
subject is the operator that moved.

Each sheet is one row, all panels scaled to a common height and nothing
resampled beyond that:

    harness native | harness WebGPU | the /laws/ shadow stage | the site's material stage

The two harness panels are the calibration bed at that span, from the canonical
capture tree, so they are the same pixels the committed rows were measured off.
The third is the page a reader can drag the span on, at the same span. The
fourth is the site's own stage, where three spans of one authored thickness sit
side by side — the demo's material, unchanged by this wave except in what its
exterior draws.

**The grounds are not the same and that is stated rather than hidden.** The
harness's `photo` and `checkerboard` beds are what Apple was captured over; the
`/laws/` stage paints a 16 px checkerboard of its own and the site's stage a dark
multi-lobe bloom. A sheet like this is a juxtaposition and never a metric: what
it can show is whether the exterior vitrea draws on a page LOOKS like the
exterior it draws on the bed, and the span-160 row is composed against the
harness's 16 px `checkerboard` cell precisely so the two checkerboards are at the
same pitch there.

The receded row is the third sheet and is the one worth the most: Apple's
inactive capture beside vitrea's beside the page's receded stage, which is the
whole of Decision Log 2 in one line.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent.parent
REPO = PACKAGE.parent.parent
FIXTURES = REPO / "apps/reference-apple/fixtures"
CAPTURES = Path(
    __import__("os").environ.get("VITREA_WEB_CAPTURES", str(PACKAGE / "web-captures"))
)

PROFILE = "apple-macos-27.0-2x-light-standard-glass0.5"
GUTTER = 8

#: The row's height in device px, and the corner of a stage shot that carries the
#: caster. A stage is a whole page column and the harness canvas is 320 x 200 CSS;
#: putting the two in one row without a crop would either shrink the harness to a
#: stamp or blow the stage up past its own resolution. The crop is the stage's
#: top-left corner, where `DESIGN.md` §9 puts the stack, taken at the shot's own
#: pixels and never resampled up; the harness panels are the ones scaled, by
#: exactly 2 from their 2x capture, so nothing in the row is invented detail.
ROW_HEIGHT = 800
STAGE_CROP = (0, 0, 920, 800)

#: Which harness cell stands beside which stage shot. At span 160 the harness's
#: own 16 px `checkerboard` cell is used rather than `photo`, so the two
#: checkerboards in the row are at the same pitch; at 96 the bed declares no
#: checkerboard cell for `rrect-md` and the row is against `photo`, which the
#: caption says.
ROWS = (
    ("96", "photo__rrect-md__rest", "laws-shadow-active-96.png", "demo-light.png"),
    ("160", "checkerboard__rrect-lg__rest", "laws-shadow-active-160.png", "demo-light.png"),
    ("160-receded", "checkerboard__rrect-lg__inactive", "laws-shadow-receded-160.png",
     "demo-light.png"),
)


def scaled(image: Image.Image, height: int) -> Image.Image:
    if image.height == height:
        return image
    width = max(1, round(image.width * height / image.height))
    return image.resize((width, height), Image.LANCZOS)


def row(panels: list[Image.Image]) -> Image.Image:
    height = ROW_HEIGHT
    panels = [scaled(p, height) for p in panels]
    width = sum(p.width for p in panels) + GUTTER * (len(panels) - 1)
    sheet = Image.new("RGB", (width, height), (0, 0, 0))
    x = 0
    for panel in panels:
        sheet.paste(panel, (x, 0))
        x += panel.width + GUTTER
    return sheet


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--laws", required=True)
    parser.add_argument("--demo", required=True)
    args = parser.parse_args()
    laws = Path(args.laws)
    demo = Path(args.demo)

    for label, scene, laws_shot, demo_shot in ROWS:
        native = FIXTURES / PROFILE / f"{scene}.png"
        web = CAPTURES / PROFILE / scene / f"{scene}__webgpu.png"
        for path in (native, web, laws / laws_shot, demo / demo_shot):
            if not path.exists():
                raise SystemExit(f"demo-sheet: {path} is not there")
        panels = [Image.open(native).convert("RGB"), Image.open(web).convert("RGB")]
        panels += [
            Image.open(path).convert("RGB").crop(STAGE_CROP)
            for path in (laws / laws_shot, demo / demo_shot)
        ]
        out = HERE / f"demo-beside-harness-{label}.png"
        sheet = row(panels)
        sheet.save(out)
        print(f"{out.name}  {sheet.width}x{sheet.height}")
        print(f"  harness native | harness WebGPU   {PROFILE} / {scene}")
        print(f"  /laws/ shadow stage               {laws_shot}")
        print(f"  the site's material stage         {demo_shot}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
