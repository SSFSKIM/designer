#!/usr/bin/env python3
"""W15 G2: attribute every moved golden by measurement. Reads the renderer harness's readbacks
of each golden scene — declined (the isolation proof's named profile) and default — captured on
the pre-merge tree and on the landed tree by `e2e/golden/w15-attribution.spec.ts`, and prints per
scene: pixels differing, the largest channel delta, the bounding box of the change, and the
proof's hash (sha256 of the RGBA bytes, 32 hex chars) of the landed declined render — the value
`W15_HASHES` pins. Usage:

    python3 attribute-goldens.py <before dir> <after dir> [--check]

`--check` recomputes the pre-merge declined hashes and prints them beside the tables pinned in
isolation.spec.ts for the reader to compare (body-ramp-1x, placed-checkerboard).
"""
import sys, os, glob, hashlib
import numpy as np
from PIL import Image
before, after = sys.argv[1], sys.argv[2]
check = '--check' in sys.argv
def load(p): return np.asarray(Image.open(p).convert('RGBA'))
def h(a): return hashlib.sha256(a.tobytes()).hexdigest()[:32]
names = sorted({os.path.basename(p).split('__')[0] for p in glob.glob(f'{before}/*__declined.png')})
if check:
    print("pre-merge declined hashes (compare with the pinned tables):")
    for n in names: print(f"  {n:26s} {h(load(f'{before}/{n}__declined.png'))}")
    sys.exit(0)
print(f"{'scene':26s} {'render':9s} {'px differ':>10s} {'of':>7s} {'max|Δ| rgb':>11s} {'max|Δ| a':>9s} {'bbox (x0,y0,x1,y1)':>22s}  landed declined hash")
for n in names:
    for tag in ('declined', 'default'):
        a, b = load(f'{before}/{n}__{tag}.png'), load(f'{after}/{n}__{tag}.png')
        d = np.abs(a.astype(int) - b.astype(int)); m = d.max(axis=2) > 0
        ys, xs = np.nonzero(m)
        bbox = f"({xs.min()},{ys.min()},{xs.max()},{ys.max()})" if m.any() else "—"
        hh = h(b) if tag == 'declined' else ''
        print(f"{n:26s} {tag:9s} {int(m.sum()):>10d} {m.size:>7d} {int(d[..., :3].max()):>11d} {int(d[..., 3].max()):>9d} {bbox:>22s}  {hh}")
