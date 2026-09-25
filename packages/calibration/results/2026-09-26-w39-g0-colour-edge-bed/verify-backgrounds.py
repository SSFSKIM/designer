#!/usr/bin/env python3
"""Verify non-capturing side-bundle rasters against the declared sRGB arithmetic."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def verify(directory):
    doc = json.loads((ROOT / 'apps/reference-apple/scenes-w39-colour-edge.json').read_text())
    rows = []
    for scale in (1, 2):
        height, width = 280 * scale, 320 * scale
        y, x = np.mgrid[:height, :width]
        for name, bg in doc['backgrounds'].items():
            path = directory / f'{name}@{scale}x.png'
            rgb = np.asarray(Image.open(path).convert('RGB'))
            if rgb.shape != (height, width, 3):
                raise ValueError('wrong dimensions: ' + str(path))
            if bg['kind'] == 'solid':
                expected = np.broadcast_to(bg['srgb'], rgb.shape)
            else:
                angle = np.deg2rad(bg['angle']); nx, ny = np.cos(angle), np.sin(angle)
                t = np.clip(.5 + (((x + .5) / scale - 160) * nx +
                                  ((y + .5) / scale - 140) * ny) / (abs(nx) * 320 + abs(ny) * 280), 0, 1)
                expected = np.floor(np.asarray(bg['from'])[None, None, :] * (1 - t[..., None]) +
                                    np.asarray(bg['to'])[None, None, :] * t[..., None] + .5)
            error = int(np.abs(rgb.astype(float) - expected).max())
            if error:
                raise ValueError(f'{name}@{scale}x differs by {error}')
            rows.append(dict(background=name, scale=scale, size=[width, height],
                sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                medianRGB=np.median(rgb, axis=(0, 1)).tolist(), maxAbsoluteCodeError=error))
    return dict(kind='generated background rasters, NOT native evidence captures', rows=rows, allMatch=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__); p.add_argument('directory', type=Path)
    args = p.parse_args(); print(json.dumps(verify(args.directory), indent=2))
