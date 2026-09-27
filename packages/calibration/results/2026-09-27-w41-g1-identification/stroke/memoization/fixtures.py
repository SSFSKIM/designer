"""Tiny synthetic data and held module imports; importing reads no native payload."""
from pathlib import Path
import sys
import numpy as np

HERE = Path(__file__).resolve().parent
PROOF = Path('/Users/new/vitrea-w41/pre-w41-proof')
STROKE = Path('packages/calibration/results/2026-09-27-w41-g1-identification/stroke')
sys.path.insert(0, str(PROOF/STROKE))
import replay as r
sys.path.remove(str(PROOF/STROKE))
sys.path.insert(0, str(HERE.parent))
import start_partition
f, m = r.f, r.m


def observations(family='M0', curvature=False, endpoints=(0, 1, 2, 3), rails=False,
                 scale=1, css=False):
    shape = m.readers.Shape('capsule-circular', (120., 44.), (20., 20.))
    xy = np.array([[80, 19], [80, 64], [140, 41], [138, 31]]) * scale
    g = m.samples(shape, xy, scale)
    _, _, q = f.domain(family, curvature)
    rows = []
    for endpoint in endpoints:
        b = np.broadcast_to(np.array([64., 128., 180.]), (*g['d'].shape, 3)).copy()
        if rails:
            b[0, :, :] = 0
            b[1, :, :] = 255
        o = dict(endpoint=endpoint, g=g, backdrop=b, shadow=b.copy(),
                 binids=np.arange(len(xy)), target=None)
        o['target'] = f.predict(q, o, family, css, curvature)
        rows.append(o)
    return rows
