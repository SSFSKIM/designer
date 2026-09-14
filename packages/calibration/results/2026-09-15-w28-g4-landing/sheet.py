#!/usr/bin/env python3
"""W28 G4's eye sheets: the demo's two poses, and the harness capture beside them.

Two sheets, one per colour scheme, each in two bands.

**The demo band** is the playground at 2×, pinned `active` and pinned `inactive`, plus
their 8× amplified absolute difference. The difference is the point of the band: it is
where the outer shadow and the bright rim leaving become visible as shapes rather than
as an impression, on every surface of a real page at once.

**The harness band** is one inactive scene from the canonical `web-captures/` — the
same tree the matrix's rows were measured from — as native | WebGPU | 8× difference, at
the same scale. It is what makes the demo band evidence rather than a screenshot: the
recede the page shows has to be the material the matrix measured against Apple, and the
only way to see that is to put them on one sheet.

A third sheet, `real-focus.png`, is the same page under a real focus change rather than a
pin: `real-focus.ts`'s three captures, taken while the machine's frontmost application was
the browser, then the Finder, then the browser again, with the pin on `auto` throughout.
The pinned band shows the endpoint; this one shows the window server reaching it. It is
one sheet rather than two because the reading was taken once, in the scheme the machine
was in.

    python3 sheet.py <demo-capture-dir> [OUTDIR] [FOCUS-CAPTURE-DIR]
"""
import json
import os
import sys

from PIL import Image, ImageChops, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = HERE.split("/packages/")[0]
FIXTURES = os.path.join(REPO, "apps/reference-apple/fixtures")
CANONICAL_CAPTURES = "/Users/new/developer/github/designer/packages/calibration/web-captures"
GAIN = 8
GAP = 8
PAD = 40
BACKGROUND = (20, 20, 20)
INK = (235, 235, 235)

# One scene per scheme, chosen for what it shows rather than for its number: a
# mid-radius pane over the photo backdrop carries the rim, the outer shadow and a
# structured interior at once, and it is a calibration cell in both schemes at 2×.
HARNESS_SCENE = "photo__rrect-md__inactive"
HARNESS_PROFILE = {
    "light": "apple-macos-26.5-2x-light-standard",
    "dark": "apple-macos-26.5-2x-dark-standard",
}


def difference(a, b):
    return ImageChops.difference(a, b).point(lambda v: min(255, v * GAIN))


def band(images, captions, width):
    """One row of equal-height images, scaled to fit `width`, with captions above."""
    height = max(image.height for image in images)
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
    outdir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "sheets")
    os.makedirs(outdir, exist_ok=True)
    written = {}

    for scheme in ("light", "dark"):
        active = Image.open(os.path.join(demo_dir, f"playground-2x-{scheme}-active.png")).convert("RGB")
        inactive = Image.open(os.path.join(demo_dir, f"playground-2x-{scheme}-inactive.png")).convert("RGB")
        demo = band(
            [active, inactive, difference(active, inactive)],
            [
                f"demo playground 2x {scheme} — windowActivation pinned active",
                "pinned inactive",
                f"{GAIN}x absolute difference",
            ],
            width=2400,
        )

        profile = HARNESS_PROFILE[scheme]
        native = Image.open(os.path.join(FIXTURES, profile, f"{HARNESS_SCENE}.png")).convert("RGB")
        web = Image.open(
            os.path.join(CANONICAL_CAPTURES, profile, HARNESS_SCENE, f"{HARNESS_SCENE}__webgpu.png")
        ).convert("RGB")
        harness = band(
            [native, web, difference(native, web)],
            [
                f"harness {profile} {HARNESS_SCENE} — Apple",
                "vitrea WebGPU, the row this wave published",
                f"{GAIN}x absolute difference",
            ],
            width=2400,
        )

        sheet = Image.new(
            "RGB",
            (2400 + PAD * 2, demo.height + harness.height + PAD * 3),
            BACKGROUND,
        )
        sheet.paste(demo, (PAD, PAD))
        sheet.paste(harness, (PAD, PAD * 2 + demo.height))
        path = os.path.join(outdir, f"demo-and-harness-{scheme}.png")
        sheet.save(path)
        written[scheme] = os.path.relpath(path, HERE)
        print(f"wrote {path} ({sheet.width}x{sheet.height})")

    focus_dir = sys.argv[3] if len(sys.argv) > 3 else None
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
