"""The capsule's corner on the GPU tier (claims §5.83): the shoulder measurement.

Reads the canonical fixtures and captures for the cells listed below and builds two masks per
capsule from the geometry `scenes.json` declares: the declared stadium (radius half the short
side) and the shape the renderer actually drew — the same box with the radius clamped to
`min(halfW, halfH) / 1.52866495`, which is the Apple corner reference's saturation clamp
(`packages/geometry/src/shape.ts`, `resolveCorner`; `apple.ts`, `buildAppleContour`). A smaller
radius in the same box is a FULLER shape, so the drawn shape is a superset of the stadium and the
difference is four shoulders at the ends.

For each cell and tier it reports the mean absolute linear-luminance difference against Apple's
capture in the shoulders (drawn shape minus stadium), in the body (the stadium eroded 4 CSS px,
inside the rim) and in a control ring 2 CSS px outside the drawn shape. A material that stops at
the clamped contour reads high in the shoulders and clean in the ring; a material that stops at
the stadium reads the shoulders as the contour line only. Two controls: a rounded rectangle whose
ratio is under the clamp (no shoulders by construction) and the capsule over `dark-solid` in the
light scheme, where the material is nearly invisible on both sides.

Also writes the by-eye evidence beside this file: `corners.png` (native | CSS | GPU crops of the
left end), `shoulders.png` (the GPU tier's |ΔL| heat map with both contours drawn) and
`css-vs-gpu.png` (the same crop on both tiers with their heat maps).

    python3 shoulders.py > shoulders.txt
"""
import os

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
FIXTURES = os.path.join(ROOT, "apps", "reference-apple", "fixtures")
CAPTURES = os.path.join(ROOT, "packages", "calibration", "web-captures")
APPLE_REACH = 1.52866495

# (profile, scale, scene, capsule centres in CSS px, box size in CSS px, declared radius or None)
CELLS = [
    ("apple-macos-26.5-1x-light-standard", 1, "photo__capsule-button__rest", [160], (120, 44), None),
    ("apple-macos-26.5-1x-light-standard", 1, "checkerboard__capsule-button__rest", [160], (120, 44), None),
    ("apple-macos-26.5-1x-light-standard", 1, "light-solid__capsule-button__rest", [160], (120, 44), None),
    ("apple-macos-26.5-1x-light-standard", 1, "dark-solid__capsule-button__rest", [160], (120, 44), None),
    ("apple-macos-26.5-2x-light-standard", 2, "photo__capsule-button__rest", [160], (120, 44), None),
    ("apple-macos-26.5-2x-light-standard", 2, "checkerboard__capsule-button__rest", [160], (120, 44), None),
    ("apple-macos-26.5-1x-light-standard", 1, "photo__toolbar-group__rest", [104, 160, 216], (44, 44), None),
    ("apple-macos-26.5-1x-dark-standard", 1, "photo__capsule-button__rest", [160], (120, 44), None),
    ("apple-macos-26.5-1x-light-standard", 1, "photo__rrect-md__rest", [160], (160, 96), 20),
]


def linear(a):
    a = a / 255.0
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)


def luma(img):
    c = linear(np.asarray(img.convert("RGB"), dtype=np.float64))
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]


def rrect_mask(size, radius, cx, cy, shape, scale, inset=0.0):
    """Pixels whose centres lie inside a rounded rect of `size` at (`cx`, `cy`), all in CSS px."""
    h_px, w_px = shape
    yy, xx = np.mgrid[0:h_px, 0:w_px]
    x = (xx + 0.5) / scale
    y = (yy + 0.5) / scale
    hw, hh, r = size[0] / 2 - inset, size[1] / 2 - inset, max(radius - inset, 0.0)
    dx = np.maximum(np.abs(x - cx) - (hw - r), 0.0)
    dy = np.maximum(np.abs(y - cy) - (hh - r), 0.0)
    return (dx * dx + dy * dy) <= r * r


def native_path(profile, scene):
    return os.path.join(FIXTURES, profile, f"{scene}.png")


def capture_path(profile, scene, tier):
    return os.path.join(CAPTURES, profile, scene, f"{scene}__{tier}.png")


def main():
    print("mean |dL| against Apple's capture, linear luminance: shoulders (drawn shape minus the")
    print("declared stadium) / body (stadium eroded 4 CSS px) / ring (2 CSS px outside the drawn shape)")
    print()
    heat = []
    corners = []
    for profile, scale, scene, centres, size, declared in CELLS:
        nat_img = Image.open(native_path(profile, scene))
        nat = luma(nat_img)
        radius = declared if declared is not None else min(size) / 2
        drawn = min(radius, (min(size) / 2) / APPLE_REACH)
        S = np.zeros(nat.shape, bool)
        Q = np.zeros(nat.shape, bool)
        B = np.zeros(nat.shape, bool)
        O = np.zeros(nat.shape, bool)
        for cx in centres:
            S |= rrect_mask(size, radius, cx, 100, nat.shape, scale)
            Q |= rrect_mask(size, drawn, cx, 100, nat.shape, scale)
            B |= rrect_mask(size, radius, cx, 100, nat.shape, scale, inset=4)
            O |= rrect_mask(size, drawn, cx, 100, nat.shape, scale, inset=-2)
        shoulders = Q & ~S
        ring = O & ~Q
        line = f"{scene} @{scale}x ({profile[16:]}): drawn r {drawn:.2f} of {radius:.0f} CSS px, shoulders {int(shoulders.sum())} px"
        tiers = {}
        for tier in ("webgpu", "css"):
            web_img = Image.open(capture_path(profile, scene, tier))
            d = np.abs(luma(web_img) - nat)
            sh = d[shoulders].mean() if shoulders.any() else float("nan")
            tiers[tier] = (sh, d[B].mean(), d[ring].mean())
            line += f" | {tier}: shoulders {sh:.4f} body {d[B].mean():.4f} ring {d[ring].mean():.4f}"
            if tier == "webgpu":
                gpu_img, gpu_d = web_img, d
            else:
                css_img, css_d = web_img, d
        print(line)

        if scale == 1 and len(centres) == 1 and declared is None and "dark" not in profile:
            # The left end, zoomed six times: the heat map with both contours, and the crops.
            x0, y0, x1, y1 = 94, 72, 166, 128
            z = 6
            hm = np.clip(gpu_d[y0:y1, x0:x1] / 0.25 * 255, 0, 255).astype(np.uint8)
            im = Image.fromarray(np.stack([hm, hm, hm], -1)).resize(((x1 - x0) * z, (y1 - y0) * z), Image.NEAREST)
            dr = ImageDraw.Draw(im)
            for mask, colour in ((S, (0, 255, 0)), (Q, (255, 0, 0))):
                e = mask[y0:y1, x0:x1]
                edge = (e & ~np.roll(e, 1, 0)) | (e & ~np.roll(e, -1, 0)) | (e & ~np.roll(e, 1, 1)) | (e & ~np.roll(e, -1, 1))
                for yy, xx in zip(*np.nonzero(edge)):
                    dr.rectangle([(xx * z, yy * z), (xx * z + z - 1, yy * z + z - 1)], outline=colour)
            dr.text((4, 4), f"{scene}: |L gpu - L native| (white = 0.25); green = declared stadium, red = drawn r {drawn:.1f}", fill=(255, 255, 0))
            heat.append(im)
            row = []
            for img in (nat_img, css_img, gpu_img):
                row.append(img.convert("RGB").crop((x0, y0, x1, y1)).resize(((x1 - x0) * z, (y1 - y0) * z), Image.NEAREST))
            for d in (css_d, gpu_d):
                hm = np.clip(d[y0:y1, x0:x1] / 0.25 * 255, 0, 255).astype(np.uint8)
                row.append(Image.fromarray(np.stack([hm, hm, hm], -1)).resize(((x1 - x0) * z, (y1 - y0) * z), Image.NEAREST))
            corners.append((scene, row))

    def stack(panels, out):
        w = max(p.width for p in panels)
        h = sum(p.height + 4 for p in panels)
        sheet = Image.new("RGB", (w, h), (24, 24, 24))
        y = 0
        for p in panels:
            sheet.paste(p, (0, y))
            y += p.height + 4
        sheet.save(os.path.join(HERE, out))

    stack(heat, "shoulders.png")
    rows = []
    for scene, panels in corners:
        w = sum(p.width + 4 for p in panels)
        row = Image.new("RGB", (w, panels[0].height + 16), (24, 24, 24))
        x = 0
        for p in panels:
            row.paste(p, (x, 16))
            x += p.width + 4
        ImageDraw.Draw(row).text((4, 2), f"{scene}: native | css | gpu | |css - native| | |gpu - native| (white = 0.25)", fill=(255, 255, 0))
        rows.append(row)
    stack(rows, "css-vs-gpu.png")
    stack([r.crop((0, 0, sum(p.width + 4 for p in panels[:3]), r.height)) for r, (_, panels) in zip(rows, corners)], "corners.png")
    print()
    print("wrote shoulders.png, css-vs-gpu.png, corners.png beside this script")


if __name__ == "__main__":
    main()
