#!/usr/bin/env python3
"""W30 G4's eye sheets: the demo's size sweep, and the harness's two spans beside it.

W29 G4's `sheet.py` (`results/2026-09-20-w29-g4-landing/sheet.py`) with the bands
re-chosen for this wave's operator, and the re-choice is the reading. That gate
photographed one scene in two POSES because it had moved the recede. This wave
moved the outer shadow's blur from one constant to a line in the CASTING SPAN, so
the thing a sheet has to hold side by side is two SPANS: a 44 CSS px control, where
the law draws σ 2.13 against 0.19.0's 11.0, and a 160 px panel, where it draws
17.37 against the same 11.0. A sheet at one span would show a tuning.

Three bands per sheet, one sheet per colour scheme:

**The demo band** is the site's material stage at 2x, in this scheme — three plates
at 40, 68 and 112 CSS px, one sampling group, one authored thickness of 8px, and
nothing differing but the size. Under 0.19.0 those three cast one width of shadow.
It is the operator on a real page, and it is what makes the harness bands beside it
evidence about what the demo draws rather than about what the harness does.

**The two harness bands** are `photo__capsule-button__rest` (span 44) and
`photo__rrect-lg__rest` (span 160), as native | vitrea WebGPU | 8x difference, at
2x. `photo` rather than `checkerboard` because it is the one backdrop family
carrying both spans in both schemes. The vitrea halves come from this gate's own
`harness-captures.sh` run rather than from the canonical `web-captures/` tree,
because that tree is the capture machine's record of the canonical reads and a
re-render is not one.

    python3 sheet.py <harness-capture-dir> <demo-capture-dir> [OUTDIR]
"""
import os
import sys

from PIL import Image, ImageChops, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = HERE.split("/packages/")[0]
FIXTURES = os.path.join(REPO, "apps/reference-apple/fixtures")
GAIN = 8
GAP = 8
PAD = 40
BACKGROUND = (20, 20, 20)
INK = (235, 235, 235)

# The two spans the law moved most, in the one backdrop family that carries both
# in both schemes. The span is in the label because the span is the argument.
CELLS = [
    ("photo__capsule-button__rest", 44, "sigma 11.00 -> 2.13"),
    ("photo__rrect-lg__rest", 160, "sigma 11.00 -> 17.37"),
]
PROFILES = {
    "light": "apple-macos-27.0-2x-light-standard-glass0.5",
    "dark": "apple-macos-27.0-2x-dark-standard-glass0.5",
}


def amplified(a, b):
    """|a - b| times GAIN, clipped — the difference as a shape rather than a hint."""
    diff = ImageChops.difference(a.convert("RGB"), b.convert("RGB"))
    return diff.point(lambda value: min(255, value * GAIN))


def label(draw, x, y, text):
    draw.text((x, y), text, fill=INK)


def band(images, captions, width):
    """One row of images with a caption line under each, on the sheet's background."""
    height = max(image.height for image in images)
    row = Image.new("RGB", (width, height + 22), BACKGROUND)
    draw = ImageDraw.Draw(row)
    x = 0
    for image, caption in zip(images, captions):
        row.paste(image, (x, 0))
        label(draw, x + 2, height + 6, caption)
        x += image.width + GAP
    return row


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    captures = sys.argv[1]
    demo = sys.argv[2]
    out = sys.argv[3] if len(sys.argv) > 3 else os.path.join(HERE, "sheets")
    os.makedirs(out, exist_ok=True)

    for scheme, profile in PROFILES.items():
        rows = []
        for scene, span, note in CELLS:
            native = Image.open(os.path.join(FIXTURES, profile, f"{scene}.png")).convert("RGB")
            web = Image.open(
                os.path.join(captures, profile, scene, f"{scene}__webgpu.png")
            ).convert("RGB")
            if web.size != native.size:
                web = web.resize(native.size)
            rows.append(
                (
                    [native, web, amplified(native, web)],
                    [
                        f"native  {scene}  span {span}",
                        f"vitrea webgpu  {note}",
                        f"difference x{GAIN}",
                    ],
                )
            )

        page = Image.open(os.path.join(demo, f"demo-{scheme}.png")).convert("RGB")
        # The demo shot is a 2x screenshot of a tall stage; scale it to the width
        # the harness band occupies so the two read at one scale on the page.
        harness_width = sum(image.width for image in rows[0][0]) + GAP * (len(rows[0][0]) - 1)
        page = page.resize(
            (harness_width, round(page.height * harness_width / page.width)),
            Image.LANCZOS,
        )
        rows.append(([page], ["the demo's size sweep, 40 / 68 / 112 px, one authored thickness"]))

        bands = [band(images, captions, harness_width) for images, captions in rows]
        height = sum(b.height for b in bands) + GAP * (len(bands) - 1) + PAD * 2 + 26
        sheet = Image.new("RGB", (harness_width + PAD * 2, height), BACKGROUND)
        draw = ImageDraw.Draw(sheet)
        label(
            draw,
            PAD,
            PAD - 26,
            f"W30 G4 — the span-graded shadow, {scheme} scheme, 2x  ({profile})",
        )
        y = PAD + 4
        for b in bands:
            sheet.paste(b, (PAD, y))
            y += b.height + GAP
        path = os.path.join(out, f"{profile}.png")
        sheet.save(path)
        print(f"wrote {path}  {sheet.size[0]}x{sheet.size[1]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
