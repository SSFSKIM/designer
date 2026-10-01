#!/usr/bin/env python3.12
"""W42 G2 step 4: E2 read per cell in absolute codes (Decision Log 5e; declaration `activeBandAndE2`).

Reduces `gate/rehearsal/e2abs.py`'s per-bin residuals, exactly as the declaration states:
- per cell, the mean over its MEASURED bins and channels of the bin residual mean |web - native|
  (codes), for the shipped render and the candidate; the cell FAILS iff the candidate's mean
  exceeds the shipped render's (tolerance zero, kept by the parent, A2); a cell with no measured
  bin is UNMEASURED and never a pass;
- every measured bin whose residual worsens by more than 1 code on any channel is a named miss
  (cell, bin, channel, shipped and candidate residuals): recorded, never a gate.

    python3.12 -B e2cell.py <e2abs.json> <out.json>
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np


def main():
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    data = json.loads(src.read_text())
    bins = defaultdict(list)
    for b in data['bins']:
        bins[b['cell']].append(b)
    cells, misses = [], []
    for cell in sorted({c['cell'] for c in data['cells']}):
        measured = bins.get(cell, [])
        if not measured:
            cells.append(dict(cell=cell, verdict='UNMEASURED'))
            continue
        s = float(np.mean([v for b in measured for v in b['shippedRGB']]))
        c = float(np.mean([v for b in measured for v in b['candidateRGB']]))
        cells.append(dict(cell=cell, bins=len(measured), shippedMean=s, candidateMean=c, delta=c - s,
                          verdict='FAIL' if c > s else 'pass'))
        for b in measured:
            for ch, (rs, rc) in enumerate(zip(b['shippedRGB'], b['candidateRGB'])):
                if rc - rs > 1.0:
                    misses.append(dict(cell=cell, bin={k: b[k] for k in ('side', 'member', 'shell', 'angleBin')
                                                       if k in b},
                                       channel='RGB'[ch], shipped=rs, candidate=rc, worseBy=rc - rs,
                                       depthCss=b['depthCss'], lensDisplacementCss=b['lensDisplacementCss']))
    fails = [c for c in cells if c['verdict'] == 'FAIL']
    unmeasured = [c for c in cells if c['verdict'] == 'UNMEASURED']
    value = dict(source=str(src), reading='Decision Log 5e: per cell, absolute codes; worse bins listed',
                 cells=len(cells), failing=len(fails), unmeasured=len(unmeasured),
                 passes=not fails and not unmeasured, failingCells=fails,
                 namedMisses=dict(count=len(misses), cells=len({m['cell'] for m in misses}),
                                  worst=max((m['worseBy'] for m in misses), default=0.0), bins=misses),
                 perCell=cells)
    out.write_text(json.dumps(value, indent=1) + '\n')
    print(json.dumps({k: value[k] for k in ('cells', 'failing', 'unmeasured', 'passes')}),
          'named misses', value['namedMisses']['count'], 'on', value['namedMisses']['cells'], 'cells, worst',
          round(value['namedMisses']['worst'], 2))
    for f in fails:
        print('  FAIL', f['cell'], round(f['shippedMean'], 3), '->', round(f['candidateMean'], 3))


if __name__ == '__main__':
    main()
