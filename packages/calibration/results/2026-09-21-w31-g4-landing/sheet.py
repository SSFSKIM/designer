#!/usr/bin/env python3
"""W31 G4 — the demo's material stage, with the harness's two spans beside it.

W30 G4's `sheet.py` (`results/2026-09-20-w30-g4-landing/sheet.py`) with the bands
re-chosen for this wave's operator and one thing corrected.

**The re-choice.** That gate photographed two SPANS because its operator was the
shadow's blur as a function of the casting span. This one's operator is the
body's chroma, and the axis a sheet has to hold side by side is the SCHEME: the
retention is fitted per colour scheme and per window pose, at 0.282 light and
0.336 dark on the active endpoint, and the dark scheme is where the residual was
(ratio (i) 0.333 against the light's 0.551 before the fit). So one sheet per
scheme, with two harness cells on each — `photo__rrect-md__rest` at span 96 and
`photo__rrect-lg__rest` at span 160, the brief's two cells per scheme — as
native | vitrea WebGPU | ×8 difference, at 2x.

**The correction.** W30 G4's sheet took its vitrea halves from a re-render of its
own rather than from the canonical `web-captures/` tree, because at that gate
that tree was a DIFFERENT GENERATION from the rows beside it (charter Surprises;
claims §5.161 §2) and a re-render was the honest substitute. It is not any more:
the parent copied W31 G3c's read tree to the canonical path at merge, so the
panels here are the pixels the committed rows were measured off, and no
re-render happens at this gate at all. `sheets.ts` beside this file asserts the
document bytes per cell.

    python3 sheet.py <demo-capture-dir> [OUTDIR]

The demo band is `demo-shot.mjs`'s screenshot of `#material` at 2x in the same
scheme — the site's one stage whose backdrop has hues in it to restore.
"""
import os
import sys

from PIL import Image, ImageChops, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = HERE.split("/packages/")[0]
FIXTURES = os.path.join(REPO, "apps/reference-apple/fixtures")
CAPTURES = os.environ.get(
    "VITREA_WEB_CAPTURES", os.path.join(REPO, "packages/calibration/web-captures")
)
GAIN = 8
GAP = 8
PAD = 40
BACKGROUND = (20, 20, 20)
INK = (235, 235, 235)

# The two cells per scheme, and the retention each was drawn at. The value is in
# the label because the value is the whole of the operator on that document.
CELLS = [
    ("photo__rrect-md__rest", 96),
    ("photo__rrect-lg__rest", 160),
]
PROFILES = {
    "light": ("apple-macos-27.0-2x-light-standard-glass0.5", "bodyChromaRetention 0.282"),
    "dark": ("apple-macos-27.0-2x-dark-standard-glass0.5", "bodyChromaRetention 0.336"),
}

# What the demo band is, per scheme, said on the sheet rather than in a file
# nobody opens beside it. `StageBackdrop.tsx`'s DARK_GROUND carries `field: 0`.
DEMO_NOTE = {
    "light": "the demo's material stage: three plates over a multi-lobe oklch bloom",
    "dark": "the demo's material stage: DARK_GROUND is field 0 — no lobes, so the retention is the identity here",
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
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    demo = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "sheets")
    os.makedirs(out, exist_ok=True)

    for scheme, (profile, retention) in PROFILES.items():
        rows = []
        for scene, span in CELLS:
            native = Image.open(os.path.join(FIXTURES, profile, f"{scene}.png")).convert("RGB")
            web = Image.open(
                os.path.join(CAPTURES, profile, scene, f"{scene}__webgpu.png")
            ).convert("RGB")
            if web.size != native.size:
                web = web.resize(native.size)
            rows.append(
                (
                    [native, web, amplified(native, web)],
                    [
                        f"native  {scene}  span {span}",
                        f"vitrea webgpu  {retention}",
                        f"difference x{GAIN}",
                    ],
                )
            )

        page = Image.open(os.path.join(demo, f"demo-{scheme}.png")).convert("RGB")
        harness_width = sum(image.width for image in rows[0][0]) + GAP * (len(rows[0][0]) - 1)
        page = page.resize(
            (harness_width, round(page.height * harness_width / page.width)),
            Image.LANCZOS,
        )
        rows.append(([page], [DEMO_NOTE[scheme]]))

        bands = [band(images, captions, harness_width) for images, captions in rows]
        height = sum(b.height for b in bands) + GAP * (len(bands) - 1) + PAD * 2 + 26
        sheet = Image.new("RGB", (harness_width + PAD * 2, height), BACKGROUND)
        draw = ImageDraw.Draw(sheet)
        label(
            draw,
            PAD,
            PAD - 26,
            f"W31 G4 — the body carries the backdrop's hue, {scheme} scheme, 2x  ({profile})",
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
