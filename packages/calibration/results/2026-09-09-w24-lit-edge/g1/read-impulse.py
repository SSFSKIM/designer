"""The impulse instrument (W24 G1) — what a collapsed surface transmits, read dot by dot.

The `impulse` background is fifteen 4 CSS px white dots on black (240 lit device px at 1x, 960 at
2x — the dots are 4 CSS px at BOTH scales, so in device px they are 4 across at 1x and 8 across at
2x, which is why a width quoted in CSS px does not double with the scale). Through a surface the
dot is the cleanest probe the bed has for transmission: the body around it is the level, and the
dot above it is the structure the material passes.

For a cell this reads, per dot that lies fully under the declared shape:

- **peak** — the excess of the profile's maximum over the LOCAL body, in linear luma;
- **fwhm** — the full width at half that excess, in CSS px, along both axes;
- **integral** — the excess summed along the profile, in CSS px units (the parent's "integral per
  CSS px" in `finding/eye-finding.txt`).

The local body is the profile's own mean over an annulus 10-16 CSS px from the dot's centre,
clipped to the declared shape eroded by 6 CSS px, so a dot near an edge is read against the body
beside it and never against the rim. Dots whose window leaves the eroded shape on an axis are
reported with that axis blank rather than silently read against the rim.

The centre dot is the headline row; the others are the check — a transmission that is real reads
the same way on every dot the shape covers, and an artefact of one position does not.

Validation (`--validate`): run on the background itself, where the answer is known by
construction — a 4 CSS px square profile against a black body reads peak 1.0, FWHM 4.0 and
integral 4.0 exactly, at both scales.

Usage:
    read-impulse.py --bg <impulse@Nx.png> --scale N --component capsule-button
                    --src native=<png> --src landed=<png>
    read-impulse.py --validate
"""

import argparse
import math
import sys

import numpy as np
from PIL import Image

CANVAS = (320.0, 200.0)
# From apps/reference-apple/scenes.json; kind, size in CSS px, corner radius (capsules clamp to
# half the height, which is what the reference draws and what the shape axis certifies).
COMPONENTS = {
    "capsule-button": ("capsule", 120.0, 44.0, 22.0),
    "rrect-md": ("rrect", 160.0, 96.0, 20.0),
    "rrect-sm": ("rrect", 64.0, 32.0, 8.0),
    "rrect-lg": ("rrect", 224.0, 128.0, 27.0),
}


def linearise(a):
    a = a / 255.0
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)


def luma_of(path):
    rgb = np.asarray(Image.open(path).convert("RGB"), dtype=np.float64)
    c = linearise(rgb)
    return 0.2126 * c[..., 0] + 0.7152 * c[..., 1] + 0.0722 * c[..., 2]


def find_dots(bg):
    """The dots' centres in device px, from the background's own lit pixels.

    Labelling rather than a hard-coded grid: the fixture is the evidence, and a scene that moved a
    dot would move this read with it.
    """
    from scipy import ndimage

    lab, n = ndimage.label(bg > 0.5)
    out = []
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        out.append((xs.mean() + 0.5, ys.mean() + 0.5,
                    int(xs.max() - xs.min() + 1), int(ys.max() - ys.min() + 1)))
    out.sort(key=lambda p: (round(p[1]), round(p[0])))
    return out


def shape_mask(kind, w, h, radius, scale, shape, erode):
    """The declared shape, eroded by `erode` CSS px, as a boolean mask in device px."""
    cx, cy = CANVAS[0] / 2.0, CANVAS[1] / 2.0
    hw, hh = w / 2.0 - erode, h / 2.0 - erode
    r = max((h / 2.0 if kind == "capsule" else radius) - erode, 0.0)
    yy, xx = np.mgrid[0 : shape[0], 0 : shape[1]]
    x = (xx + 0.5) / scale - cx
    y = (yy + 0.5) / scale - cy
    dx = np.maximum(np.abs(x) - (hw - r), 0.0)
    dy = np.maximum(np.abs(y) - (hh - r), 0.0)
    return (np.abs(x) <= hw) & (np.abs(y) <= hh) & (np.hypot(dx, dy) <= r + 1e-9)


def profile_along(lum, cx, cy, axis, half_dev, band_dev):
    """One profile through the dot, averaged over the `band_dev` lines at its centre.

    Averaging the two central lines rather than picking one: a 4 device px square's centre falls
    between device pixels at 1x, so a single line under-reads the peak by the sampling phase alone.
    """
    h, w = lum.shape
    offs = np.arange(int(math.floor(-half_dev)), int(math.ceil(half_dev)) + 1)
    b = max(int(round(band_dev)), 1)
    b0 = -(b // 2)
    vals = []
    for o in offs:
        acc = []
        for k in range(b0, b0 + b):
            if axis == "x":
                xi, yi = int(round(cx - 0.5)) + int(o), int(round(cy - 0.5)) + k
            else:
                xi, yi = int(round(cx - 0.5)) + k, int(round(cy - 0.5)) + int(o)
            if 0 <= yi < h and 0 <= xi < w:
                acc.append(lum[yi, xi])
        vals.append(np.mean(acc) if acc else np.nan)
    return offs.astype(float), np.array(vals, dtype=float)


def in_mask(mask, cx, cy, axis, offs, band_dev):
    h, w = mask.shape
    b = max(int(round(band_dev)), 1)
    b0 = -(b // 2)
    ok = []
    for o in offs:
        good = True
        for k in range(b0, b0 + b):
            if axis == "x":
                xi, yi = int(round(cx - 0.5)) + int(o), int(round(cy - 0.5)) + k
            else:
                xi, yi = int(round(cx - 0.5)) + k, int(round(cy - 0.5)) + int(o)
            good = good and 0 <= yi < h and 0 <= xi < w and bool(mask[yi, xi])
        ok.append(good)
    return np.array(ok)


def fwhm_of(offs, excess, scale):
    """Full width at half the peak excess, in CSS px, by linear interpolation on both flanks."""
    if not np.isfinite(excess).any():
        return float("nan")
    i = int(np.nanargmax(excess))
    peak = excess[i]
    if not np.isfinite(peak) or peak <= 0:
        return float("nan")
    half = peak / 2.0
    left = right = None
    for j in range(i, 0, -1):
        if excess[j - 1] < half <= excess[j]:
            t = (half - excess[j - 1]) / (excess[j] - excess[j - 1])
            left = offs[j - 1] + t * (offs[j] - offs[j - 1])
            break
    for j in range(i, len(offs) - 1):
        if excess[j + 1] < half <= excess[j]:
            t = (half - excess[j + 1]) / (excess[j] - excess[j + 1])
            right = offs[j + 1] - t * (offs[j + 1] - offs[j])
            break
    if left is None or right is None:
        return float("nan")
    return (right - left) / scale


def read_dot(lum, mask, cx, cy, scale, inner_css=10.0, outer_css=16.0, band_css=1.0):
    """The dot's peak, FWHM and integral on both axes, against the body beside it."""
    out = {}
    for axis in ("x", "y"):
        offs, vals = profile_along(lum, cx, cy, axis, outer_css * scale, band_css * scale)
        ok = in_mask(mask, cx, cy, axis, offs, band_css * scale)
        r = np.abs(offs) / scale
        base = ok & (r >= inner_css) & (r <= outer_css)
        core = ok & (r <= inner_css)
        if base.sum() < 4 or core.sum() < 3:
            out[axis] = {"body": float("nan"), "peak": float("nan"), "fwhm": float("nan"),
                         "integral": float("nan"), "n": int(base.sum())}
            continue
        body = float(np.nanmean(vals[base]))
        excess = np.where(ok, vals - body, np.nan)
        out[axis] = {
            "body": body,
            "peak": float(np.nanmax(excess[core])),
            "fwhm": fwhm_of(offs[ok], excess[ok], scale),
            "integral": float(np.nansum(np.clip(excess[ok], 0.0, None)) / scale),
            "n": int(base.sum()),
        }
    return out


def read_cell(path, bg, component, scale, erode=6.0):
    lum = luma_of(path)
    kind, w, h, radius = COMPONENTS[component]
    mask = shape_mask(kind, w, h, radius, scale, lum.shape, erode)
    cxc, cyc = CANVAS[0] / 2.0 * scale, CANVAS[1] / 2.0 * scale
    rows = []
    for (dx, dy, sw, sh) in find_dots(bg):
        yi, xi = int(round(dy - 0.5)), int(round(dx - 0.5))
        if not (0 <= yi < mask.shape[0] and 0 <= xi < mask.shape[1] and mask[yi, xi]):
            continue
        r = read_dot(lum, mask, dx, dy, scale)
        # The headline dot is the one the grid puts nearest the canvas centre — at CSS (160, 104),
        # four px below the shapes' own centre, which is where the grid's middle row falls.
        r["centre"] = math.hypot(dx - cxc, dy - cyc) < 8.0 * scale
        r["pos"] = (dx / scale, dy / scale)
        rows.append(r)
    return {"body": float(lum[mask].mean()) if mask.any() else float("nan"), "dots": rows}


def fmt(v, w=7, p=4):
    return f"{'-':>{w}}" if v is None or not np.isfinite(v) else f"{v:{w}.{p}f}"


def validate():
    ok = True
    for scale in (1, 2):
        p = f"apps/reference-apple/fixtures/backgrounds/impulse@{scale}x.png"
        bg = luma_of(p)
        dots = find_dots(bg)
        sizes = sorted({(d[2], d[3]) for d in dots})
        print(f"validate {scale}x: {len(dots)} dots, {sizes} device px "
              f"= {sorted({(d[2] / scale, d[3] / scale) for d in dots})} CSS px")
        mask = np.ones_like(bg, dtype=bool)
        for (dx, dy, _sw, _sh) in [dots[0], dots[7]]:
            r = read_dot(bg, mask, dx, dy, float(scale))
            for axis in ("x", "y"):
                a = r[axis]
                print(f"  dot ({dx / scale:6.1f},{dy / scale:6.1f}) {axis}: body {fmt(a['body'])} "
                      f"peak {fmt(a['peak'])} fwhm {fmt(a['fwhm'], 6, 2)} "
                      f"integral {fmt(a['integral'], 6, 3)}")
                ok = ok and abs(a["peak"] - 1.0) < 1e-9 and abs(a["fwhm"] - 4.0) < 1e-9 \
                    and abs(a["integral"] - 4.0) < 1e-9
    print("VALIDATION " + ("PASS — a dot reads its own size (peak 1.0, FWHM 4.0, integral 4.0)"
                           if ok else "FAIL"))
    return 0 if ok else 1


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--bg")
    ap.add_argument("--scale", type=float)
    ap.add_argument("--component")
    ap.add_argument("--title", default="")
    ap.add_argument("--src", action="append", default=[])
    args = ap.parse_args(argv)
    if args.validate:
        return validate()
    bg = luma_of(args.bg)
    print(f"\n== {args.title}  ({args.component}, {args.scale:g}x)")
    print(f"{'src':9}{'dot (CSS)':>16} {'axis':>5} {'body':>8} {'peak':>9} {'fwhm':>7} "
          f"{'integral':>9}")
    for spec in args.src:
        tag, path = spec.split("=", 1)
        cell = read_cell(path, bg, args.component, args.scale)
        for r in cell["dots"]:
            mark = "*" if r["centre"] else " "
            for axis in ("x", "y"):
                a = r[axis]
                print(f"{tag:9}{mark}({r['pos'][0]:6.1f},{r['pos'][1]:6.1f}) {axis:>5} "
                      f"{fmt(a['body'], 8)} {fmt(a['peak'], 9)} {fmt(a['fwhm'], 7, 2)} "
                      f"{fmt(a['integral'], 9, 4)}")
        print(f"{tag:9} body over the shape eroded 6 CSS px: {cell['body']:.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
