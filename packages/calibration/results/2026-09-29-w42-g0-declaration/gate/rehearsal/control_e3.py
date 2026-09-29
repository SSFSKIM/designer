"""The swap's own error, measured (rehearsal control): the sealed W41 E3 body swapped onto the
canonical shipped capture (swap.py --variant e3ctl) against W41 G2's REAL stage capture of that
same body (/Users/new/vitrea-w41/g2-captures/canonical-stage, receded 003940b4c7da), light
receded cells, calibration/validation/probe roles only (a holdout cell is dropped by role before
any path is formed). Reported per cell: rms codes by depth band, and the interior mean linear
luminance over the shape (depth > 0) of the swap minus the real capture, the quantity L1 reads.

    python3.12 -B control_e3.py /tmp/tree-e3ctl > control-e3.txt
"""
import json, sys
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, str(Path(__file__).resolve().parent))
import body as B
from swap import SPLIT, rgb
STAGE = Path('/Users/new/vitrea-w41/g2-captures/canonical-stage')
tree = Path(sys.argv[1])
bands = [('0-2', 0, 2), ('2-8', 2, 8), ('8-18', 8, 18), ('18+', 18, 1e9)]
print(__doc__.split('\n\n')[0])
print(f"{'cell':70s} " + ' '.join(f'{b[0]:>6s}' for b in bands) + '   dMeanLin  max|d|')
worst = []
for prof in ('apple-macos-27.0-1x-light-standard-glass0.5', 'apple-macos-27.0-2x-light-standard-glass0.5'):
    scale = 2 if '-2x-' in prof else 1
    for d in sorted((tree / prof).iterdir()):
        scene = d.name
        if SPLIT.get(scene) not in ('calibration', 'validation', 'probe') or B.pose_of(scene) != 'inactive':
            continue
        st = STAGE / prof / scene / f'{scene}__webgpu.png'
        meta = json.loads((STAGE / prof / scene / 'cell__webgpu.json').read_text())
        assert 'sha256:003940b4c7da' in meta['capturePath'], scene
        a, b = rgb(d / f'{scene}__webgpu.png'), rgb(st)
        fl = B.field(scene.split('__')[1], scale)
        dep = -fl.d
        r = a - b
        out = []
        for _, lo, hi in bands:
            m = (dep > lo) & (dep <= hi)
            out.append(f'{np.sqrt((r[m] ** 2).mean()):6.2f}' if m.any() else '     -')
        m = dep > 0
        dmean = float((B.dec(a / 255) @ B.W709)[m].mean() - (B.dec(b / 255) @ B.W709)[m].mean())
        worst.append((abs(dmean), f'{prof}/{scene}'))
        print(f'{prof[17:]:>26s}/{scene:43s} ' + ' '.join(out) + f'   {dmean:+.5f}  {np.abs(r[m]).max():5.0f}')
worst.sort(reverse=True)
print('\nlargest |interior mean| error (linear luminance; L1 bounds 0.055, growth 0.005):', worst[:5])
