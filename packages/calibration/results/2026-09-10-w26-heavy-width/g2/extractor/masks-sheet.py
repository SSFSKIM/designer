"""The floor cell's three masks at 4x per CSS px, beside the captures they came from.

Row 1: the capture (native | 0.14.0 | candidate), cropped to the declared region's
bounding box.
Row 2: the extractor's mask over it — green where the mask is inside, magenta where
a region pixel is EXCLUDED (the population IoU is hostage to), and the declared
region's contour in white.
"""

from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw

import w26extractor as X
from anatomy import masks

SHEET = "masks-4x.png"
ZOOM = 4  # per CSS px; the capture is 2x, so 2 device px -> 4 screen px


def crop_box(region, pad=6):
    ys, xs = np.nonzero(region)
    return xs.min() - pad, ys.min() - pad, xs.max() + pad + 1, ys.max() + pad + 1


def panel(rgb, mask, region, box, overlay):
    x0, y0, x1, y1 = box
    img = rgb[y0:y1, x0:x1, :3].astype(np.float64)
    if overlay:
        r = region[y0:y1, x0:x1] != 0
        m = mask[y0:y1, x0:x1] != 0
        inside = r & m
        excluded = r & ~m
        img[inside] = img[inside] * 0.55 + np.array([0, 190, 90]) * 0.45
        img[excluded] = np.array([255, 0, 170])
    out = Image.fromarray(img.astype(np.uint8))
    return out.resize((out.width * ZOOM // 2, out.height * ZOOM // 2), Image.NEAREST)


def main():
    m = masks()
    region = m["region"]
    box = crop_box(region)
    cols = [("native", "native_img", "native"),
            ("0.14.0", "web0_img", "web0"),
            ("candidate", "webc_img", "webc")]

    panels = []
    for overlay in (False, True):
        row = [panel(m[img], m[msk], region, box, overlay) for _, img, msk in cols]
        panels.append(row)

    pw, ph = panels[0][0].size
    gap, top = 12, 26
    sheet = Image.new("RGB", (3 * pw + 4 * gap, 2 * ph + 3 * gap + top), (18, 18, 20))
    draw = ImageDraw.Draw(sheet)
    for c, (label, _, msk) in enumerate(cols):
        x = gap + c * (pw + gap)
        holes = X.hole_count(m[msk], region)
        area = int(m[msk].sum())
        draw.text((x + 4, 8), f"{label}   area {area}  holes {holes}", fill=(230, 230, 230))
        for r in range(2):
            sheet.paste(panels[r][c], (x, top + gap + r * (ph + gap)))
    sheet.save(SHEET)
    print(f"{SHEET}  {sheet.width}x{sheet.height}")


if __name__ == "__main__":
    main()
