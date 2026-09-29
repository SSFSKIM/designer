"""W42 G0 rehearsal round 2, item (b): E2's shell bins read ABSOLUTELY against Apple.

E2 (W38 clause 1c) reads each shell bin's excess over the cell's own deep median (d <= -6 CSS
px) and compares web with native. Under a body law the deep median moves by design, so the
parent asked for the same bins read against Apple in absolute codes, with the deep-median
reference dropped:

    residual(bin) = mean over the bin's pixels of |web - native|, per channel (codes)
    bar           = residual(candidate) - residual(shipped) <= 1 code, every channel, every bin

The bins, the population and the measured/UNMEASURED rule are E2's own (e2.py's population,
reference, single_geometry and group_geometry, imported; a bin below four pixels is
UNMEASURED, never a pass). Natives through E2's role-guarded reader; the shipped captures are
the canonical tree; the candidate is a swapped tree.

It also reports, per bin, where the bin lies against the band the rehearsal holds (20 pt) and
against vitrea's lens (the optics pass's displacement at the bin's depth), which is the share
of E2 the held band hides from the law.

    python3.12 -B e2abs.py --tree /scratch/tree-c2 --out e2abs-c2.json
"""
from __future__ import annotations

import argparse
import io
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import body as B  # noqa: E402
from swap import CANONICAL, CAL, population  # noqa: E402

E2_DIR = CAL / 'results/2026-09-25-w38-g0-rim-axis-cut'
sys.path.insert(0, str(E2_DIR))
import e2  # noqa: E402

BAND_PT = 20.0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--tree', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    native = e2.CanonicalNativeReader()
    decl = e2.read('e2-declaration.json')
    declared = {c['cell'] for c in decl['cells']}
    rows = {f"{r['key']['profileKey']}/{r['key']['sceneId']}": r for r in population()}
    out_cells, bins_all = [], []
    for cell in sorted(declared):
        profile, sid = native.roles.admit(cell)
        row = rows.get(cell)
        if row is None:
            continue
        scale = 2 if '-2x-' in profile else 1
        shape = tuple(reversed(row['key']['web']['pixelSize']))
        comp_name = native.roles.scenes[sid]['component']
        component = native.roles.spec['components'][comp_name]
        n = np.asarray(Image.open(io.BytesIO(native.read(cell))).convert('RGB'), float)
        s = np.asarray(Image.open(CANONICAL / profile / sid / f'{sid}__webgpu.png').convert('RGB'), float)
        c = np.asarray(Image.open(args.tree / profile / sid / f'{sid}__webgpu.png').convert('RGB'), float)
        if component['kind'] == 'group':
            _, parts = e2.group_geometry(shape, component, scale)
        else:
            _, parts = e2.single_geometry(shape, component, scale)
        fl = B.field(comp_name, scale)
        fx, fy = fl.displacement(B.endpoint_of('light' if '-light-' in profile else 'dark', 'rest'))
        disp = np.hypot(fx, fy)
        verdicts = defaultdict(int)
        worst = None
        for info, mask in parts:
            if info['pixels'] < e2.MIN_PIXELS:
                verdicts['UNMEASURED'] += 1
                continue
            rs = np.abs(s[mask] - n[mask]).mean(axis=0)
            rc = np.abs(c[mask] - n[mask]).mean(axis=0)
            delta = rc - rs
            depth = float((-fl.d)[mask].mean())
            v = 'FAIL' if delta.max() > 1.0 else 'within'
            verdicts[v] += 1
            b = dict(cell=cell, **{k: info[k] for k in ('side', 'member', 'shell', 'angleBin') if k in info},
                     pixels=info['pixels'], depthCss=depth, inBand=depth <= BAND_PT,
                     lensDisplacementCss=float(disp[mask].mean()), shippedRGB=rs.tolist(),
                     candidateRGB=rc.tolist(), deltaRGB=delta.tolist(), verdict=v,
                     pixelsChanged=int(np.any(c[mask] != s[mask], axis=1).sum()))
            bins_all.append(b)
            if worst is None or delta.max() > worst['delta']:
                worst = dict(delta=float(delta.max()), bin=b)
        out_cells.append(dict(cell=cell, verdicts=dict(verdicts), worst=worst))
    measured = [b for b in bins_all]
    summary = dict(
        tree=str(args.tree), cells=len(out_cells), bins=len(measured),
        fail=sum(b['verdict'] == 'FAIL' for b in measured),
        failingCells=sorted({b['cell'] for b in measured if b['verdict'] == 'FAIL'}),
        binsWithAnyPixelChanged=sum(b['pixelsChanged'] > 0 for b in measured),
        binsInsideBand=sum(b['inBand'] for b in measured),
        binsUnderLens=sum(b['lensDisplacementCss'] > 0.5 for b in measured),
        lensDisplacementCss=dict(median=float(np.median([b['lensDisplacementCss'] for b in measured])),
                                 min=float(min(b['lensDisplacementCss'] for b in measured)),
                                 max=float(max(b['lensDisplacementCss'] for b in measured))),
        worstDelta=max((b['deltaRGB'] and max(b['deltaRGB'])) for b in measured),
        bestDelta=min(min(b['deltaRGB']) for b in measured))
    args.out.write_text(json.dumps(dict(summary=summary, cells=out_cells, bins=bins_all), indent=1) + '\n')
    print(json.dumps(summary, indent=1)[:3000])


if __name__ == '__main__':
    main()
