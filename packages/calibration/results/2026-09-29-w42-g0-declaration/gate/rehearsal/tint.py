"""W42 G0 rehearsal round 2, item (c): the tinted photo rrect-md inactive L1 growth, decomposed.

vitrea's author-tint composite, as the shipped code states it (material.ts
`tintedMaterialColour`, mirrored by wgsl/optics.ts): per pixel, with u the untinted material's
linear luminance,

    layer  = seed' * shade(u),  shade(u) = 1 + (clamp(dark + (light - dark) u) - 1) * grip
    seed'  = neutral + (seed - neutral) * chromaScale,   neutral = max(seed)
    tinted = lin((1 - s) enc(material) + s enc(layer))                  (per channel)

with the endpoint's constants from tint-resolved.json (this worktree's material code), seed the
tint's sRGB decoded, s its alpha (1 when the scene gives none), grip = tintShadeStrength (nominal
ambient tint, no tone collapse). In light RECEDED the constants are dark 0.0288, light 0.76,
chromaScale 0: the tint is a GREY layer at full strength whose level is 0.0288 + 0.7312 u, so a
tinted receded cell's luminance is an affine function of the untinted body's and nothing else.

Reads only calibration/validation natives (the role is checked before a path is formed) and
the canonical shipped captures, the swapped trees and the stages' rows.

    python3.12 -B tint.py --root /scratch/w42gate --variants c1,c2,c1p,c2p > tint.txt
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import body as B  # noqa: E402
from swap import CANONICAL, SPLIT, population, rgb, store, untinted  # noqa: E402

TINT = json.loads((HERE / 'tint-resolved.json').read_text())
L1_GROWTH = 0.005


def tint_code(ep: str, scene: str):
    """The shipped composite as a function of an untinted body in codes (H, W, 3) -> codes."""
    spec = B.SPEC['tints'][scene.split('__')[2].split('-tint-')[1]]
    k = TINT[ep]
    seed = B.dec(np.array(spec['srgb'], float) / 255)
    s = float(spec.get('alpha', 1.0))
    neutral = seed.max()
    seed2 = neutral + (seed - neutral) * k['tintChromaScale']
    grip = k['tintShadeStrength']

    def transfer(body255):
        lin = B.dec(body255 / 255)
        u = np.clip(lin @ B.W709, 0, 1)
        shade = 1 + (np.clip(k['tintShadeDark'] + (k['tintShadeLight'] - k['tintShadeDark']) * u, 0, 1) - 1) * grip
        layer = seed2 * shade[..., None]
        return ((1 - s) * B.enc(lin) + s * B.enc(np.clip(layer, 0, 1))) * 255
    return transfer


def native_mask(profile, scene):
    """The native silhouette L1 averages over, re-derived as memo A's port does (luminance delta
    0.02 or OKLab chroma 0.03 against the backdrop, inside the declared region)."""
    assert SPLIT.get(scene) in ('calibration', 'validation'), scene
    sys.path.insert(0, str(Path.home() / 'vitrea-w42/grounding/argument'))
    scale = 2 if '-2x-' in profile else 1
    n = rgb(B.FIX / profile / f'{scene}.png')
    bg = B.backdrop(scene.split('__')[0], scale) * 255
    region = B.field(scene.split('__')[1], scale).d <= 0
    own = B.dec(n / 255) @ B.W709
    base = B.dec(bg / 255) @ B.W709
    return region & (np.abs(own - base) >= 0.02), n


def mean_lum(img, mask):
    return float((B.dec(img / 255) @ B.W709)[mask].mean())


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', type=Path, required=True)
    ap.add_argument('--variants', default='c1,c2')
    args = ap.parse_args()
    print(__doc__.split('\n\n')[0])

    print('\n1. The code composite against the shipped tinted captures (body at depth >= 2 CSS px,'
          ' tint applied to the untinted twin\'s shipped capture), rms codes:')
    for r in population():
        p, sc = r['key']['profileKey'], r['key']['sceneId']
        twin = untinted(sc)
        if twin is None or SPLIT.get(sc) not in ('calibration', 'validation', 'probe'):
            continue
        ep = B.endpoint_of('light' if '-light-' in p else 'dark', B.pose_of(sc))
        fl = B.field(sc.split('__')[1], 2 if '-2x-' in p else 1)
        m = -fl.d >= 2
        pred = tint_code(ep, sc)(rgb(CANONICAL / p / twin / f'{twin}__webgpu.png'))
        real = rgb(CANONICAL / p / sc / f'{sc}__webgpu.png')
        print(f'   {p[17:]:28s} {sc:52s} {np.sqrt(((pred - real)[m] ** 2).mean()):5.2f}')

    l1 = {v: {c['cell']: c for c in json.loads((args.root / f'ref-{v}' / 'l1-cut.json').read_text())['cells']}
          for v in ['identity'] + args.variants.split(',')}
    print('\n2. photo__rrect-md__inactive-tint-orange, light receded: the growth decomposed.')
    print('   The tinted cell\'s web mean is 0.0288 + 0.7312 x (the untinted body\'s mean luminance over'
          ' the same pixels), exactly, so every change is the body\'s, scaled by 0.7312.')
    for scale in (1, 2):
        p = f'apple-macos-27.0-{scale}x-light-standard-glass0.5'
        t, u = 'photo__rrect-md__inactive-tint-orange', 'photo__rrect-md__inactive'
        mask_t, _ = native_mask(p, t)
        base = l1['identity'][f'{p}/{t}']
        allowed = base['baselineError'] + L1_GROWTH
        print(f'\n   {scale}x: native (tinted) {base["native"]:.4f}; shipped {base["web"]:.4f} '
              f'(error {base["error"]:.4f}, W33 baseline {base["baselineError"]:.4f}); passing needs '
              f'web <= {base["native"] + allowed:.4f}')
        ship_u = rgb(CANONICAL / p / u / f'{u}__webgpu.png')
        for v in args.variants.split(','):
            cand_u = rgb(args.root / f'tree-{v}' / p / u / f'{u}__webgpu.png')
            du = mean_lum(cand_u, mask_t) - mean_lum(ship_u, mask_t)
            code = tint_code('light-receded', t)
            dt_code = mean_lum(code(cand_u), mask_t) - mean_lum(code(ship_u), mask_t)
            row = l1[v][f'{p}/{t}']
            twin = l1[v][f'{p}/{u}']
            need = (base['native'] + allowed - base['web']) / 0.7312
            print(f'     {v:4s} untinted body mean over the tinted silhouette {du:+.4f}; the code composite '
                  f'moves the tinted mean {dt_code:+.4f} (the swap\'s fitted composite measured {row["web"] - base["web"]:+.4f}); '
                  f'growth {row["growth"]:+.4f}. The untinted twin: native {twin["native"]:.4f}, '
                  f'candidate {twin["web"]:.4f} (error {twin["error"]:.4f}). To pass, the untinted body may rise '
                  f'by at most {need:+.4f} here; the candidate raises it {du:+.4f}.')


if __name__ == '__main__':
    main()
