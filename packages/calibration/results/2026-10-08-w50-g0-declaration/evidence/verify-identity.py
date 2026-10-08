"""Recheck the committed raster witnesses against retained scratch and canonical trees; no render."""
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[2]
CANONICAL = Path('/Users/new/Developer/GitHub/designer/packages/calibration/web-captures')


def raw(path):
    return np.asarray(Image.open(path).convert('RGBA'))


def controls(name, expected):
    matched, new = 0, 0
    for cell in json.loads((HERE / name).read_text())['cells']:
        capture = Path(cell['capture'])
        pixels = raw(capture)
        if hashlib.sha256(pixels.tobytes()).hexdigest() != cell['rawSha256']:
            raise ValueError(f'Retained scratch raster changed: {capture}')
        prior = CANONICAL / cell['profile'] / cell['scene'] / capture.name
        if cell['status'] == 'BYTE_IDENTICAL':
            if not np.array_equal(pixels, raw(prior)):
                raise ValueError(f'Canonical/scratch raster differs: {capture}')
            matched += 1
        elif cell['status'] == 'NO_PRIOR_CAPTURE':
            # A later publication may add this path; the G0 record remains an absence
            # at this read, never retroactively an identity comparison.
            new += 1
        else:
            raise ValueError('Unknown identity result')
    if (matched, new) != expected:
        raise ValueError(f'Wrong dark control population: {name}')
    return matched, new


def main():
    before = json.loads((CAL / 'results/2026-10-08-w49b-g0-declaration/evidence/identity-after.json').read_text())
    after = json.loads((HERE / 'raw-identity.json').read_text())
    if before != after or len(after) != 43:
        raise ValueError('Renderer raster identity witness differs')
    webgpu = controls('dark-controls-complete.json', (24, 4))
    css = controls('dark-controls-css.json', (21, 7))
    print(f'43 renderer witnesses exact; WebGPU {webgpu}, CSS {css} (prior exact, new intact)')


if __name__ == '__main__':
    main()
