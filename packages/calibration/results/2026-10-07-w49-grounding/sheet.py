#!/usr/bin/env python3
"""W49 G0 grounding: the eye sheet of the seventeen authorised cells (charter Grounding, "By eye").

Each row is Apple 0.25 | vitrea `d0219cd684bf` | vitrea `b2d074d2df24`, then the same three with a gain of
4 about the native image's median so a dark interior's structure is visible. 2x rows are decimated to 1x
size. Reads the native fixtures, the canonical capture tree and `web-captures-superseded/d0219cd684bf/`
of the checkout named by REPO (the capture machine's main checkout: captures are gitignored). Renders
nothing; the two withheld cells (`checkerboard-32__rrect-lg__inactive`, a W46 referee, and
`photo__rrect-lg__inactive`, holdout) were exposed at W48's read 8 and drawn on W48 G2's landing sheets.

    python3.12 -B sheet.py REPO OUT.png
"""
import sys
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from attribution import AUTHORISED  # noqa: E402


def main(repo, out):
    fix = f"{repo}/apps/reference-apple/fixtures"
    new = f"{repo}/packages/calibration/web-captures"
    old = f"{repo}/packages/calibration/web-captures-superseded/d0219cd684bf"
    load = lambda p: np.asarray(Image.open(p).convert("RGB")).astype(np.float32)  # noqa: E731
    rows = []
    for scale, scene in AUTHORISED:
        prof = f"apple-macos-27.0-{scale}x-dark-standard-glass0.25"
        ims = [load(f"{fix}/{prof}/{scene}.png"), load(f"{old}/{prof}/{scene}/{scene}__webgpu.png"),
               load(f"{new}/{prof}/{scene}/{scene}__webgpu.png")]
        if scale == 2:
            ims = [im[::2, ::2] for im in ims]
        m = float(np.median(ims[0]))
        ims += [np.clip((im - m) * 4 + 128, 0, 255) for im in ims[:3]]
        h, w = ims[0].shape[:2]
        row = Image.new("RGB", (w * 6 + 50, h + 14), (40, 40, 40))
        for i, im in enumerate(ims):
            row.paste(Image.fromarray(im.astype(np.uint8)), (i * (w + 10), 14))
        ImageDraw.Draw(row).text((2, 1), f"{scale}x {scene}   Apple | d0219cd684bf | b2d074d2df24 || "
                                 "the same, gain 4 about Apple's median", fill=(255, 255, 0))
        rows.append(row)
    sheet = Image.new("RGB", (max(r.width for r in rows), sum(r.height for r in rows)))
    y = 0
    for r in rows:
        sheet.paste(r, (0, y))
        y += r.height
    sheet.save(out, optimize=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
