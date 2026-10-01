#!/usr/bin/env python3.12
"""The probe's 0.5 counterparts, read from w42-archive through W42's guarded Reader (X46).

    python3.12 -B w42frames.py      # caches the plurality frame of every counterpart outside the repository

Only the roles calibration and validation are opened; H is never requested, and W42's raw sitting root is
denied for the process by the archive module's audit hook. The archive is the second owner-controlled copy
(`~/vitrea-w42/archive-copy/`), its tree verified entry by entry against the inventory W42 G1 published
(§5.195 §5). The observed image of a cell is the plurality frame of its seven normal runs, the earliest run's
frame on a tie (W42 G2's reading plan, item 1). Frames are cached as .npy under SCRATCH with their SHA-256 in
an index; a cached frame that no longer hashes as indexed is refused.
"""
import hashlib
import importlib.util
import io
import json
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
SITTING = ROOT / 'packages/calibration/results/2026-09-29-w42-g0-declaration/bed/sitting'
ARCHIVE_ROOT = (Path.home() / 'vitrea-w42/archive-copy/1e3d6e65fa3b9a621f1d0f80fb03cc79ee76c29d9b001174983689a7aed31014'
                '/extracted/archive')
INVENTORY = '5481795e0a77ef246f6743d2b6bbe2111a79d858ff9b7a2a4571255595940ed7'
DENY = (Path.home() / 'vitrea-w42/g1',)
SCRATCH = Path.home() / 'vitrea-w43/wtest-scratch/observed-0.5'
ROLES = ('calibration', 'validation')


def _archive():
    spec = importlib.util.spec_from_file_location('w42_archive_for_w43_wtest', SITTING / 'w42_archive.py')
    a = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(a)
    for p in DENY:
        a.deny(p)
    return a


def profile(scheme):
    return f'apple-macos-27.0-2x-{scheme}-standard-glass0.5'


def extract(cells):
    """cells: [(scheme, state, cid)]. Writes SCRATCH/<profile>/<cid>__<state>.npy and index.json."""
    a = _archive()
    tree = a.verify_tree(ARCHIVE_ROOT)
    if tree['inventorySha256'] != INVENTORY:
        raise SystemExit('not w42-archive')
    wave = a.wave_module().default_wave()
    reader = wave.reader(ARCHIVE_ROOT, roles=ROLES)
    from PIL import Image
    index = {}
    for scheme, state, cid in sorted(set(cells)):
        name = f'{profile(scheme)}/{cid}__{state}'
        header, blobs = a.unbundle(reader.read(name, 'states'))
        runs = sorted((r for r in header['runs'] if r['protocol'] == 'normal'), key=lambda r: r['run'])
        count = Counter(r['frame'] for r in runs)
        top = max(count.values())
        frame = next(r['frame'] for r in runs if count[r['frame']] == top)
        with Image.open(io.BytesIO(blobs[frame])) as im:
            img = np.asarray(im.convert('RGB'), dtype=np.uint8)
        out = SCRATCH / profile(scheme) / f'{cid}__{state}.npy'
        out.parent.mkdir(parents=True, exist_ok=True)
        np.save(out, img)
        index[name] = dict(frame=frame, plurality=top, runs=len(runs), states=len(count),
                           npySha256=hashlib.sha256(out.read_bytes()).hexdigest())
    (SCRATCH / 'index.json').write_text(json.dumps(dict(inventory=INVENTORY, cells=index), indent=1, sort_keys=True))
    return index


def observed(scheme, state, cid):
    index = json.loads((SCRATCH / 'index.json').read_text())
    name = f'{profile(scheme)}/{cid}__{state}'
    row = index['cells'][name]
    path = SCRATCH / profile(scheme) / f'{cid}__{state}.npy'
    if hashlib.sha256(path.read_bytes()).hexdigest() != row['npySha256']:
        raise SystemExit('cached frame altered: ' + name)
    return np.load(path).astype(np.float64), row


def probe_counterparts():
    bed = json.loads((HERE.parent / 'bed' / 'probe-bed.json').read_text())
    return [(p['scheme'], p['state'], c) for p in bed['passes'].values() for c in p['cells']]


if __name__ == '__main__':
    idx = extract(probe_counterparts())
    print(f'{len(idx)} counterparts cached under {SCRATCH}; states > 1: '
          f'{sum(1 for v in idx.values() if v["states"] > 1)}')
