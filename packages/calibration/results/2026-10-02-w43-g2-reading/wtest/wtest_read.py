#!/usr/bin/env python3.12
"""W43 G2 stage two (c): the w-test, read ONCE against the prediction hashed in G0 (charter clause 8).

    python3.12 -B wtest_read.py check   # everything but the 0.25 statistic: pins, archives, support, plumbing
    python3.12 -B wtest_read.py read    # the read, once; refuses if reading.json exists

`read-plan.md` beside this file states, before the read and in a commit of its own, what is computed and
from which frames. Every function that turns pixels into a ratio is the declaration's own, imported unchanged
from `results/2026-10-01-w43-g0-declaration/wtest/` (wtest.py, rehearse.py, w42frames.py) and checked against
the SHA-256 the declaration (4f90f910..., the chain's last line) pins for it. Nothing here chooses a region, a
statistic, a resolution or a verdict rule: those are `support.json`, `wtest.ratio`, `wtest.verdict` and
`prediction.json` as hashed.

The frames:
- 0.5: the plurality of W42's seven normal runs per counterpart, read from `w42-archive` (asset 1e3d6e65...,
  inventory 5481795e...) through W42's guarded Reader, roles calibration and validation only, H never
  requested, W42's raw root denied (`w42frames.extract`), into a scratch directory outside the repository; each
  frame's SHA-256 must equal the one G0's rehearsal 3 read.
- 0.25: the plurality of G1b's three normal runs per probe cell (`probe-0.25-2x-*`), read from the
  owner-controlled copy of `w43-archive-g1b` (asset e17f7efa..., inventory 9c7fbd86...), its tree verified entry
  by entry; G1b's raw root and stop evidence are denied for the process.
"""

from __future__ import annotations

import collections
import gzip
import hashlib
import importlib.util
import io
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
EVID = HERE.parent
RESULTS = EVID.parent
REPO = RESULTS.parents[2]
G0 = RESULTS / '2026-10-01-w43-g0-declaration'
WT = G0 / 'wtest'
sys.path.insert(0, str(WT))
import wtest as W  # noqa: E402
import rehearse as RH  # noqa: E402
import w42frames as O  # noqa: E402

HOME = Path.home()
G1B_ASSET = 'e17f7efaec0d5389953689a073e3540abe50d8deb0d3b91b0dfe225ef5f12e1d'
G1B_INVENTORY = '9c7fbd86576b77eb8153e07b671129f622ef3192bc2b37d294bbc57db4603038'
G1B_ROOT = HOME / 'vitrea-w43/archive-copy-g1b' / G1B_ASSET / 'extracted/archive'
G1B_DENY = [HOME / 'vitrea-w43' / d for d in ('g1b-run', 'g1b-stops', 'g1b-prelaunch', 'g1b-restore', 'g1b-release')]
SCRATCH = HOME / 'vitrea-w43/g2b-scratch'
DECLARATION_IN_FORCE = '4f90f91015f3c82cdb9c73951d887a7a7a9b02e72963922c7ef72d8e6dbb79bb'
PINNED = ('wtest/wtest.py', 'wtest/rehearse.py', 'wtest/w42frames.py', 'wtest/support.json', 'wtest/prediction.json',
          'bed/probe-bed.json', 'bed/scenes-w43-probe.json')
OUT_JSON = HERE / 'reading.json'
OUT_TXT = HERE / 'reading.txt'


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def archive_tool():
    spec = importlib.util.spec_from_file_location('w43_archive_g2', G0 / 'bed/sitting/w43_archive.py')
    a = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(a)
    return a


def check_pins() -> list[str]:
    lines = []
    chain = [line.split()[0] for line in (G0 / 'declaration.sha256').read_text().splitlines() if line.strip()]
    if chain[-1] != DECLARATION_IN_FORCE or sha_file(G0 / 'declaration.json') != DECLARATION_IN_FORCE:
        raise SystemExit('the declaration in force is not 4f90f910...')
    sources = json.loads((G0 / 'declaration.json').read_text())['sources']
    for rel in PINNED:
        key = f'packages/calibration/results/2026-10-01-w43-g0-declaration/{rel}'
        want = sources[key] if isinstance(sources[key], str) else sources[key]['sha256']
        got = sha_file(G0 / rel)
        if got != want:
            raise SystemExit(f'{rel} is not the declared bytes')
        lines.append(f'  {rel:<26} {got[:16]}... as declared')
    return lines


# --------------------------------------------------------------------------------------- the 0.25 frames

class G1bArchive:
    """The probe's frames at any position, from the archive's own records; plurality of the normal runs."""

    def __init__(self):
        a = archive_tool()
        for d in G1B_DENY:
            a.deny(d)
        tree = a.verify_tree(G1B_ROOT)
        if tree['inventorySha256'] != G1B_INVENTORY:
            raise SystemExit('not w43-archive-g1b')
        self.tree = tree
        self.records = {}
        for path in sorted(G1B_ROOT.glob('*/*.cell.json.gz')):
            rec = json.loads(gzip.decompress(path.read_bytes()))
            self.records[rec['cell']] = rec

    def plurality(self, glass: str, scheme: str, cid: str, state: str, pass_prefix: str):
        name = f'apple-macos-27.0-2x-{scheme}-standard-glass{glass}/{cid}__{state}'
        rec = self.records[name]
        runs = sorted((r for r in rec['runs'] if r['protocol'] == 'normal' and r['pass'].startswith(pass_prefix)),
                      key=lambda r: r['run'])
        count = collections.Counter(r['frame'] for r in runs)
        top = max(count.values())
        frame = next(r['frame'] for r in runs if count[r['frame']] == top)
        return dict(name=name, frame=frame, runs=len(runs), states=len(count), plurality=top, counts=dict(count))

    def image(self, frame: str) -> np.ndarray:
        raw = (G1B_ROOT / 'frames' / f'{frame}.png').read_bytes()
        if hashlib.sha256(raw).hexdigest() != frame:
            raise SystemExit(f'frame {frame} is not its name')
        with Image.open(io.BytesIO(raw)) as im:
            return np.asarray(im.convert('RGB'), dtype=np.uint8).astype(np.float64)


# ---------------------------------------------------------------------------------------- the 0.5 frames

def w42_counterparts() -> dict:
    """Re-extract every counterpart into this child's scratch and require G0's frames, by SHA-256."""
    g0_index = {}
    for d in ('observed-0.5',):
        g0_index.update(json.loads((HOME / 'vitrea-w43/wtest-scratch' / d / 'index.json').read_text())['cells'])
    O.SCRATCH = SCRATCH / 'observed-0.5'
    index = O.extract(O.probe_counterparts())
    for name, row in index.items():
        if g0_index.get(name, {}).get('frame') != row['frame']:
            raise SystemExit(f'{name}: not the frame G0 read')
    return index


def endpoint_frames(ep: str, archive: G1bArchive, x: str, pass_prefix: str):
    scheme, pose = ep.split('-')
    key = f'x{x}/2x-{scheme}-{W.POSE_OF[pose]}'
    cells = W.probe()['passes'][key]['cells']
    return {cid: archive.plurality(x, scheme, cid, pose, pass_prefix) for cid in cells}


# ------------------------------------------------------------------------------------------------- read

def read_endpoint(ep, support, archive, img25_of, T25, frames25):
    scheme, pose = ep.split('-')
    greys50, _ = RH.endpoint_cells(ep)
    T50 = RH.grey_tables(ep, {cid: O.observed(scheme, pose, cid)[0] for cid in greys50})
    img50 = lambda cid: O.observed(scheme, pose, cid)[0]  # noqa: E731
    free = RH.evaluate(ep, support, img25_of, img50, T25, T50, 'median', 'free')
    lifted = RH.evaluate(ep, support, img25_of, img50, T25, T50, 'median', 'lifted')
    return free, lifted, T50


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else 'check'
    if mode not in ('check', 'read'):
        raise SystemExit('wtest_read.py check | read')
    if mode == 'read' and OUT_JSON.exists():
        raise SystemExit('the w-test has been read: reading.json exists, and it is read once')
    lines = ['# W43 G2 stage two (c): the w-test, ' + ('read once' if mode == 'read' else 'checked, not read'), '']
    lines.append(f'Declaration in force {DECLARATION_IN_FORCE[:16]}... (the chain\'s last line); its pins:')
    lines += check_pins()
    support = RH.load_support('median', 'declared')   # regenerated from the declared rule, refused unless as hashed
    prediction = json.loads((WT / 'prediction.json').read_text())['prediction']
    archive = G1bArchive()
    lines.append(f'w43-archive-g1b tree verified: {archive.tree["entries"]} entries, inventory '
                 f'{archive.tree["inventorySha256"][:16]}...')
    index50 = w42_counterparts()
    lines.append(f'w42-archive counterparts re-extracted: {len(index50)}, every frame the one G0 read; '
                 f'{sum(1 for v in index50.values() if v["states"] > 1)} with more than one state (its plurality read)')
    lines.append('')
    record = dict(schema='w43-g2-wtest-reading-1', mode=mode, declaration=DECLARATION_IN_FORCE, endpoints={})
    for ep in W.ENDPOINTS:
        scheme, pose = ep.split('-')
        frames25 = endpoint_frames(ep, archive, '0.25', 'probe-0.25-')
        bad = {cid: f for cid, f in frames25.items() if f['runs'] != 3}
        if bad:
            raise SystemExit(f'{ep}: probe cells without three normal runs: {sorted(bad)}')
        greys25, _ = RH.endpoint_cells(ep)
        sup = support.get(ep, {})
        free_regions = [cid for cid, reg in sup.items() if 'free' in reg]
        lifted_regions = [cid for cid, reg in sup.items() if 'lifted' in reg]
        lines.append(f'== {ep}: {len(frames25)} probe cells at 0.25, three runs each, '
                     f'{sum(1 for f in frames25.values() if f["states"] > 1)} with two states; '
                     f'{len(free_regions)} supported free-side regions, {len(lifted_regions)} lifted (never gated); '
                     f'prediction {"stated" if prediction[ep]["stated"] else "NOT stated"}, r_pred {prediction[ep]["rPred"]}')
        if mode == 'check':
            # The plumbing, on 0.5 pixels only: the 0.25 slot is given the 0.5 frame and T, so every region must
            # read r = 1 exactly (a FAIL against 0.5 by construction). No 0.25 pixel is decoded.
            img50 = lambda cid, s=scheme, p=pose: O.observed(s, p, cid)[0]  # noqa: E731
            T50 = RH.grey_tables(ep, {cid: img50(cid) for cid in greys25})
            rows = RH.evaluate(ep, sup, img50, img50, T50, T50, 'median', 'free')
            rs = [r['r'] for r in rows if r['status'] == 'measured']
            lines.append(f'  plumbing on 0.5 in both slots: {len(rs)} regions, r = '
                         f'{", ".join(f"{v:.12f}" for v in rs)}; verdict {W.verdict(rows, 0.5)["verdict"]} (by construction)')
            record['endpoints'][ep] = dict(plumbingR=rs)
            continue
        cache = {}

        def img25_of(cid, s=scheme, f=frames25):
            if cid not in cache:
                cache[cid] = archive.image(f[cid]['frame'])
            return cache[cid]

        T25 = RH.grey_tables(ep, {cid: img25_of(cid) for cid in greys25})
        free, lifted, _ = read_endpoint(ep, sup, archive, img25_of, T25, frames25)
        v = W.verdict(free, prediction[ep]['rPred'])
        lines.append(f'  VERDICT {v["verdict"]}: {v.get("measured", 0)} measured, {v.get("failing", 0)} failing, '
                     f'median r {v.get("rMedian", float("nan")):.4f}')
        for row in free:
            if row['status'] != 'measured':
                lines.append(f'    free   {row["region"]:<34} {row["status"]}: {row.get("reason")}')
                continue
            ok = abs(row['r'] - prediction[ep]['rPred']) <= row['dr']
            lines.append(f'    free   {row["region"]:<34} r {row["r"]:.4f}  dr {row["dr"]:.4f}  |r - 0.5|/dr '
                         f'{abs(row["r"] - prediction[ep]["rPred"]) / row["dr"]:.2f}  D {row["D"]:+.1f}  '
                         f'channels {", ".join(f"{c:.3f}" for c in row["rChannels"])}  {"within" if ok else "OUTSIDE"}')
        lifted_out = []
        for row in lifted:
            if row['status'] != 'measured':
                lines.append(f'    lifted {row["region"]:<34} {row["status"]}: {row.get("reason")}')
                continue
            lr = W.lifted_reading(ep, row['r'])
            lifted_out.append(dict(row, **lr))
            lines.append(f'    lifted {row["region"]:<34} r_lift {row["r"]:.4f}  dr {row["dr"]:.4f}  D {row["D"]:+.1f}  '
                         f'lam25 {lr["lam25"]:.4f} (lam50 {lr["lam50"]}; declared ramp: ratio {lr.get("byRatio", float("nan")):.4f}, '
                         f'difference {lr.get("byDifference", float("nan")):.4f})')
        record['endpoints'][ep] = dict(verdict=v, free=free, lifted=lifted_out,
                                       frames25={cid: {k: f[k] for k in ('frame', 'runs', 'states', 'plurality')}
                                                 for cid, f in frames25.items()})
    lines.append('')
    text = '\n'.join(lines) + '\n'
    if mode == 'read':
        OUT_JSON.write_text(json.dumps(record, indent=1, default=float) + '\n')
        OUT_TXT.write_text(text)
    else:
        (HERE / 'check.txt').write_text(text)
    print(text)


if __name__ == '__main__':
    main()
