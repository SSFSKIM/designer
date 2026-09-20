#!/usr/bin/env python3
"""W29 G4's eye sheets: the demo's two poses, and the macOS 27 harness captures beside them.

W28 G4's `sheet.py` (`results/2026-09-15-w28-g4-landing/sheet.py`) with one band added
and the profiles moved, and the addition is the point of this gate's reading. W28 put the
demo's two poses over ONE harness band — the inactive scene — because the active material
was the one it had already published. This gate moved the active material too, so both
poses get a harness band and the sheet carries three.

Three bands per sheet, one sheet per colour scheme:

**The demo band** is the playground at 2x, pinned `active` and pinned `inactive`, plus
their 8x amplified absolute difference. The difference is where the recede's structure
becomes a shape rather than an impression, on every surface of a real page at once — and
on macOS 27 what it does NOT show is the outer shadow leaving, because the 27 recede
keeps it (claims §5.154 §6).

**The two harness bands** are `photo__rrect-md` at rest and inactive, as
native | vitrea WebGPU | 8x difference, at the same scale. They are what make the demo
band evidence rather than a screenshot: the material the page shows has to be the
material the matrix measured against Apple. The vitrea halves come from this gate's own
`harness-captures.sh` run rather than from the canonical `web-captures/` tree, because
that tree holds the macOS 26.5 generation on this machine.

A fourth sheet, `real-focus.png`, is the same page under a real focus change rather than
a pin: `real-focus.ts`'s three captures, taken while the machine's frontmost application
was the browser, then the Finder, then the browser again, with the pin on `auto`
throughout. The pinned band shows the endpoint; this one shows the window server reaching
it. It is one sheet rather than two because the reading was taken once, in the scheme the
machine was in.

    python3 sheet.py <demo-capture-dir> <harness-capture-dir> [OUTDIR] [FOCUS-CAPTURE-DIR]
"""
import json
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

# The same scene W28 read, for the same reason and so the two gates' sheets can be put
# side by side: a mid-radius pane over the photo backdrop carries the rim, the outer
# shadow and a structured interior at once, and it is a calibration cell in both schemes
# at 2x. Both poses now, because both materials moved.
HARNESS_SCENES = ("photo__rrect-md__rest", "photo__rrect-md__inactive")
HARNESS_PROFILE = {
    "light": "apple-macos-27.0-2x-light-standard-glass0.5",
    "dark": "apple-macos-27.0-2x-dark-standard-glass0.5",
}


def difference(a, b):
    return ImageChops.difference(a, b).point(lambda v: min(255, v * GAIN))


def band(images, captions, width):
    """One row of equal-height images, scaled to fit `width`, with captions above."""
    total = sum(image.width for image in images) + GAP * (len(images) - 1)
    scale = min(1.0, width / total)
    scaled = [
        image.resize((max(1, int(image.width * scale)), max(1, int(image.height * scale))))
        for image in images
    ]
    height = max(image.height for image in scaled)
    strip = Image.new("RGB", (width, height + 24), BACKGROUND)
    draw = ImageDraw.Draw(strip)
    x = 0
    for image, caption in zip(scaled, captions):
        draw.text((x, 4), caption, fill=INK)
        strip.paste(image, (x, 24))
        x += image.width + GAP
    return strip


def main():
    demo_dir = sys.argv[1]
    harness_dir = sys.argv[2]
    outdir = sys.argv[3] if len(sys.argv) > 3 else os.path.join(HERE, "sheets")
    os.makedirs(outdir, exist_ok=True)
    written = {}

    for scheme in ("light", "dark"):
        active = Image.open(
            os.path.join(demo_dir, f"playground-2x-{scheme}-active.png")
        ).convert("RGB")
        inactive = Image.open(
            os.path.join(demo_dir, f"playground-2x-{scheme}-inactive.png")
        ).convert("RGB")
        bands = [
            band(
                [active, inactive, difference(active, inactive)],
                [
                    f"demo playground 2x {scheme} — windowActivation pinned active",
                    "pinned inactive",
                    f"{GAIN}x absolute difference",
                ],
                width=2400,
            )
        ]

        profile = HARNESS_PROFILE[scheme]
        for scene in HARNESS_SCENES:
            native = Image.open(os.path.join(FIXTURES, profile, f"{scene}.png")).convert("RGB")
            web = Image.open(
                os.path.join(harness_dir, profile, scene, f"{scene}__webgpu.png")
            ).convert("RGB")
            bands.append(
                band(
                    [native, web, difference(native, web)],
                    [
                        f"harness {profile} {scene} — Apple",
                        "vitrea WebGPU, the material this release ships",
                        f"{GAIN}x absolute difference",
                    ],
                    width=2400,
                )
            )

        sheet = Image.new(
            "RGB",
            (2400 + PAD * 2, sum(b.height for b in bands) + PAD * (len(bands) + 1)),
            BACKGROUND,
        )
        y = PAD
        for strip in bands:
            sheet.paste(strip, (PAD, y))
            y += strip.height + PAD
        path = os.path.join(outdir, f"demo-and-harness-{scheme}.png")
        sheet.save(path)
        written[scheme] = os.path.relpath(path, HERE)
        print(f"wrote {path} ({sheet.width}x{sheet.height})")

    focus_dir = sys.argv[4] if len(sys.argv) > 4 else None
    if focus_dir is not None:
        held = Image.open(os.path.join(focus_dir, "real-focus-held.png")).convert("RGB")
        lost = Image.open(os.path.join(focus_dir, "real-focus-lost.png")).convert("RGB")
        returned = Image.open(os.path.join(focus_dir, "real-focus-returned.png")).convert("RGB")
        strip = band(
            [held, lost, difference(held, lost), returned],
            [
                "pin auto, browser frontmost — resolved active",
                "Finder made frontmost — resolved inactive",
                f"{GAIN}x absolute difference",
                "browser frontmost again — resolved active",
            ],
            width=2400,
        )
        sheet = Image.new("RGB", (2400 + PAD * 2, strip.height + PAD * 2), BACKGROUND)
        sheet.paste(strip, (PAD, PAD))
        path = os.path.join(outdir, "real-focus.png")
        sheet.save(path)
        written["real-focus"] = os.path.relpath(path, HERE)
        print(f"wrote {path} ({sheet.width}x{sheet.height})")

    print(json.dumps(written, indent=2))


if __name__ == "__main__":
    main()
