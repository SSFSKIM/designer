#!/usr/bin/env python3.12
"""Body texture beside the eye (W41 G2 sheets; c9a §5.193, G1's mottling hypothesis §5.192 §20).

G1 saw E3 turn the backdrop's texture-period luma into chroma mottling on the light-inactive
photo. The ΔE panels cannot separate "E3 added texture" from "E3 removed a broad offset and
revealed texture that was already there", so this reads the BODY ITSELF in each column.

For every RENDERED canonical light-inactive cell in a G2 sheet run inventory it re-reads the three
source PNGs (each checked against the inventory's hash), takes the body as the pixels the seal
moved (pre-W41 RGBA != now RGBA) eroded by `erode` px so the rim and contour stay out, converts
to OKLab, and removes each channel's local mean over a (2*radius+1)^2 box. What is left is the
body's own fine structure. It reports, per column, the RMS of that residual in L and in chroma
(a, b together), and the RMS of each web column's LOW-pass difference from native (the broad
level/hue miss E3 was fitted to close), and each column's mean sRGB code over the body. A diagnostic for the eye, not a referee or a bound.
usage: texture.py <inventory.json> [radius_px_at_1x=6] [erode_px_at_1x=4]
"""
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[5]


def load(path, digest):
    data = Path(path).read_bytes()
    if hashlib.sha256(data).hexdigest() != digest:
        raise SystemExit(f'{path}: bytes differ from the inventory')
    with Image.open(Path(path)) as image:
        return np.asarray(image.convert('RGB'), dtype=np.float64) / 255.0


def oklab(rgb):
    linear = np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)
    m1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929],
                   [0.2119034982, 0.6806995451, 0.1073969566],
                   [0.0883024619, 0.2817188376, 0.6299787005]])
    m2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468],
                   [1.9779984951, -2.4285922050, 0.4505937099],
                   [0.0259040371, 0.7827717662, -0.8086757660]])
    return np.cbrt(linear @ m1.T) @ m2.T


def box(field, radius):
    """Mean over a (2r+1)^2 window, edge-clamped, per channel (integral image)."""
    padded = np.pad(field, ((radius, radius), (radius, radius), (0, 0)), mode='edge')
    s = padded.cumsum(0).cumsum(1)
    s = np.pad(s, ((1, 0), (1, 0), (0, 0)))
    k = 2 * radius + 1
    h, w = field.shape[:2]
    return (s[k:k + h, k:k + w] - s[:h, k:k + w] - s[k:k + h, :w] + s[:h, :w]) / (k * k)


def erode(mask, r):
    out = mask.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            out &= np.roll(np.roll(mask, dy, 0), dx, 1)
    return out


def main():
    inventory_path = Path(sys.argv[1])
    radius1 = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    erode1 = int(sys.argv[3]) if len(sys.argv) > 3 else 4
    inventory = json.loads(inventory_path.read_text())
    out = {}
    for r in inventory['records']:
        if r['status'] != 'RENDERED' or '__inactive' not in r['sceneId']:
            continue
        scale = 2 if '-2x-' in r['profileKey'] else 1
        native = load(ROOT / r['native']['path'], r['native']['pngSha256'])
        pre = load(r['pre']['png'], r['pre']['pngSha256'])
        now = load(r['now']['png'], r['now']['pngSha256'])
        body = erode(np.any(pre != now, axis=2), erode1 * scale)
        if body.sum() < 50:
            continue
        radius = radius1 * scale
        row = {'bodyPixels': int(body.sum())}
        low = {}
        for name, image in (('native', native), ('pre', pre), ('now', now)):
            lab = oklab(image)
            smooth = box(lab, radius)
            fine = (lab - smooth)[body]
            low[name] = smooth[body]
            row[name] = {'fineL': float(np.sqrt((fine[:, 0] ** 2).mean())),
                         'fineChroma': float(np.sqrt((fine[:, 1] ** 2 + fine[:, 2] ** 2).mean()))}
            row[name + 'BodyMeanCodes'] = [round(float(c), 1) for c in (image[body] * 255).mean(0)]
        for name in ('pre', 'now'):
            d = low[name] - low['native']
            row[name]['broadMissL'] = float(np.sqrt((d[:, 0] ** 2).mean()))
            row[name]['broadMissChroma'] = float(np.sqrt((d[:, 1] ** 2 + d[:, 2] ** 2).mean()))
        out[f"{r['profileKey']}/{r['sceneId']}"] = {
            k: ({kk: round(vv, 5) for kk, vv in v.items()} if isinstance(v, dict) else v) for k, v in row.items()}
    json.dump({'schema': 'w41-g2-body-texture-1', 'inventory': str(inventory_path),
               'inventorySha256': hashlib.sha256(inventory_path.read_bytes()).hexdigest(),
               'radiusPxAt1x': radius1, 'erodePxAt1x': erode1, 'cells': out}, sys.stdout, indent=1)
    sys.stdout.write('\n')


if __name__ == '__main__':
    main()
