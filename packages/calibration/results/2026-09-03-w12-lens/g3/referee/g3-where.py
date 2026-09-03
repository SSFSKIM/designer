"""Where did the 2x GPU rows move? — the diagnostic the failed stop 3 needs.

§5.56 §3's prediction came from the dry run of claims §5.41 §4, which replaces vitrea's
capture INSIDE the §5.41 interior box only and leaves the rim band and the outside as they
are. The landing capture changes all three. This splits the same SSIM map the matrix scores
into the box, the band (0…24 CSS px inside the contour, outside the box) and the rest, on
the material on `main` and on the G3 candidate, so the two regions can be read apart.
"""
import os
import sys

import numpy as np

HERE = '/Users/new/Developer/GitHub/designer/.claude/worktrees/agent-a25a752a19656e6bc/packages/calibration/results/2026-09-03-w12-lens/g3'
sys.path.insert(0, HERE)
sys.path.insert(0, f'{HERE}/../g1')
os.environ.setdefault('VITREA_ROOT',
                      '/Users/new/Developer/GitHub/designer/.claude/worktrees/agent-a25a752a19656e6bc')

from g3lib import COMP, ROOT, box_mask, depth, load_rgb  # noqa: E402
from w11lib import luma_enc, ssim_map  # noqa: E402

T = '/Users/new/.claude/jobs/5c70e47f/tmp/w12'
PROF = 'apple-macos-26.5-2x-light-standard'
SCALE = 2
R = 5  # the SSIM map's 'valid' margin, so a mask must be cropped to match


def native(scene):
    return load_rgb(f'{ROOT}/apps/reference-apple/fixtures/{PROF}/{scene}.png')


def web(scene, caps):
    return load_rgb(f'{T}/{caps}/{PROF}/{scene}/{scene}__webgpu.png')


print(f'root: {ROOT}')
print(f'{"comp":16s} {"region":10s} {"n":>8s} {"main":>8s} {"G3":>8s} {"Δ":>8s}')
for comp in ('rrect-md', 'rrect-ml', 'rrect-lg', 'glass-over-glass'):
    scene = f'checkerboard__{comp}__rest'
    nat = native(scene)
    a = web(scene, 'web-captures-g2b')
    b = web(scene, 'web-captures-g3')
    ma = ssim_map(luma_enc(nat), luma_enc(a))
    mb = ssim_map(luma_enc(nat), luma_enc(b))
    if comp in COMP:
        u = depth(comp, SCALE)[R:-R, R:-R]
        box = box_mask(comp, SCALE)[R:-R, R:-R]
        regions = [
            ('whole', np.ones_like(box)),
            ('box', box),
            ('band<24', (u >= 0) & (u < 24) & ~box),
            ('outside', u < 0),
        ]
    else:
        # A composed scene with no single silhouette in COMP — whole crop only.
        regions = [('whole', np.ones(ma.shape, bool))]
    for name, mask in regions:
        if mask.sum() == 0:
            continue
        print(f'{comp:16s} {name:10s} {int(mask.sum()):8d} '
              f'{ma[mask].mean():8.4f} {mb[mask].mean():8.4f} {mb[mask].mean() - ma[mask].mean():+8.4f}')
