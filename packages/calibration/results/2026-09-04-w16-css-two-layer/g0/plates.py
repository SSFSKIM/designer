"""W16 G0 — the probe backdrops as PNGs the Chromium page can lay down.

The native probe bed's checkerboards are generated analytically by
`2026-09-03-w12-lens/g3/g3lib.py:checker_plate` (bottom-left anchored, AppKit's
flipped y) and that generator is proved equal to the committed rasters at both
scales by `g3lib.verify_plates`. This writes the same plate at device resolution
so the page's `<img>` maps one image pixel to one device pixel, which is what
makes the analytic plate the instrument uses the plate the capture was taken over.
"""
import os
import sys

import numpy as np
from PIL import Image

G3 = '/Users/new/Developer/GitHub/designer/packages/calibration/results/2026-09-03-w12-lens/g3'
if G3 not in sys.path:
    sys.path.insert(0, G3)
import g3lib  # noqa: E402

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__)) + '/pages/plates'


def encode(lin):
    c = np.clip(lin, 0, 1)
    return np.where(c <= 0.0031308, c * 12.92, 1.055 * c ** (1 / 2.4) - 0.055)


def main():
    os.makedirs(OUT, exist_ok=True)
    for name, pitch in g3lib.PITCH.items():
        if name == 'checkerboard-lc16':
            continue
        for scale in (1, 2):
            P = g3lib.plate(name, scale)
            img = (encode(P) * 255).round().astype(np.uint8)
            Image.fromarray(np.stack([img] * 3, -1)).save(f'{OUT}/{name}@{scale}x.png')
            print(f'[wrote] {name}@{scale}x.png  {img.shape}  levels {sorted(set(img.ravel().tolist()))}')
    # the photo backdrop, copied at both scales for the lift's reading
    for scale in (1, 2):
        P = g3lib.plate('photo', scale)
        img = (encode(P) * 255).round().astype(np.uint8)
        Image.fromarray(np.stack([img] * 3, -1)).save(f'{OUT}/photo-luma@{scale}x.png')
        print(f'[wrote] photo-luma@{scale}x.png {img.shape}')


if __name__ == '__main__':
    main()
