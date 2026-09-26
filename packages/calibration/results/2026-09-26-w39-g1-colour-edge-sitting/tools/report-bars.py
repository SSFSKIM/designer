#!/usr/bin/env python3.12
"""W39 G1: the repeat bar per cell/bin/channel, from the archive of record (c9a §5.185).

The declaration (G0 `bounds-declaration.txt`, "BODY STATISTIC"): the per-channel/bin bar is
0.5 + half the largest pairwise run-median separation, computed on all seven admitted runs
BEFORE plurality; the deep spatial min/max is kept separately and never used as repeat noise;
a zero observed spread buys no tolerance (the bar is then exactly 0.5).

What a run contributes, per glass member: the deep body's per-channel median (the declared
per-run deep statistic) and each measured edge bin's per-channel mean (`w39_readers.read_bins`,
the statistic the edge residual is scored on). An UNMEASURED bin in any run makes that bin's
bar UNMEASURED, never a bar over fewer runs. Protocols are separate strata: `--protocol normal`
reads the seven-run bed, `--protocol long` the three-run sentinels; they are never pooled.

Only the roles the wave reader authorises without a receipt are read (calibration and
validation). The holdout's bars are not computed here: its payload stays behind the
procedural boundary for G2's once-only exposure, which can derive them from the archive.
Reads go through the guarded reader, so this proves nothing about the raw root.
"""
import argparse
import json
from pathlib import Path
import sys

import numpy as np

G0 = Path(__file__).resolve().parents[2] / '2026-09-26-w39-g0-colour-edge-bed'
sys.path.insert(0, str(G0))
import w39_archive  # noqa: E402
from wave import default_wave  # noqa: E402


def bar(values):
    """0.5 + half the largest pairwise separation per channel over the runs' values."""
    a = np.asarray(values, float)
    widest = np.max(np.abs(a[:, None, :] - a[None, :, :]), axis=(0, 1))
    return (0.5 + 0.5 * widest).tolist(), widest.tolist()


def cell_bars(reader, cell, protocol):
    rows = [r for r in w39_archive.recorded_statistics(reader, cell)
            if r['admitted'] and r['protocol'] == protocol]
    out = dict(cell=cell, protocol=protocol, runs=len(rows), distinctStates=len({r['state'] for r in rows}))
    if not rows:
        return {**out, 'status': 'insufficient admitted repeats'}
    # What a cell IS is decided before how often it was captured: a `none` reference that
    # the declaration captures in run 1 only is a reference, not a glass cell short of runs.
    stats = [r['statistics'] for r in rows]
    if 'members' not in stats[0]:
        kind = 'reference' if 'reference' in stats[0] else 'other'
        return {**out, 'status': f'native-only {kind} cell: no glass bins'}
    if any(s.get('members') is None or all('deep' not in m for m in s['members']) for s in stats):
        return {**out, 'status': 'opaque control: coverage, not a repeat bar'}
    if len(rows) < 2:
        return {**out, 'status': 'insufficient admitted repeats'}
    members = []
    for m in range(len(stats[0]['members'])):
        runs = [s['members'][m] for s in stats]
        deeps = [r['deep'] for r in runs]
        if all(d['status'] == 'measured' for d in deeps):
            b, sep = bar([d['medianRGB'] for d in deeps])
            deep = dict(status='measured', barRGB=b, separationRGB=sep,
                        runMediansRGB=[d['medianRGB'] for d in deeps],
                        spatialMinimumRGB=np.min([d['minimumRGB'] for d in deeps], 0).tolist(),
                        spatialMaximumRGB=np.max([d['maximumRGB'] for d in deeps], 0).tolist(),
                        spatial='deep min/max over all runs: recorded, never repeat noise')
        else:
            deep = dict(status='UNMEASURED')
        bins = []
        for k, first in enumerate(runs[0]['bins']):
            if first['part'] == 'boundary':
                continue
            per = [r['bins'][k] for r in runs]
            key = dict(part=first['part'], side=first['side'], bin=first['bin'], shell=first['shell'],
                       depthCss=first['depthCss'], pixels=first['pixels'])
            if any((p['part'], p['side'], p['bin'], p['shell']) !=
                   (first['part'], first['side'], first['bin'], first['shell']) for p in per):
                raise ValueError(f'bin layout differs across runs: {cell}')
            if all(p['status'] == 'measured' for p in per):
                b, sep = bar([p['meanRGB'] for p in per])
                bins.append({**key, 'status': 'measured', 'barRGB': b, 'separationRGB': sep})
            else:
                bins.append({**key, 'status': 'UNMEASURED'})
        members.append(dict(member=m, deep=deep, bins=bins))
    return {**out, 'status': 'measured', 'members': members}


def headline(reports):
    """Max and median of the bar per stratum (scheme x pose x scale, from the profile key)."""
    strata = {}
    for r in reports:
        if r.get('status') != 'measured':
            continue
        profile = r['cell'].split('/', 1)[0]
        for m in r['members']:
            if m['deep']['status'] == 'measured':
                strata.setdefault(profile, {'deep': [], 'edge': []})['deep'] += m['deep']['barRGB']
            for b in m['bins']:
                if b['status'] == 'measured':
                    strata.setdefault(profile, {'deep': [], 'edge': []})['edge'] += b['barRGB']
    return {p: {k: (dict(max=float(np.max(v)), median=float(np.median(v)), values=len(v),
                         atFloor=int(np.sum(np.asarray(v) == 0.5))) if v else None)
                for k, v in d.items()} for p, d in sorted(strata.items())}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('archive', type=Path)
    ap.add_argument('--protocol', choices=['normal', 'long'], default='normal')
    ap.add_argument('--roles', default='calibration,validation')
    ap.add_argument('--deny-raw-root', type=Path)
    args = ap.parse_args(argv)
    if args.deny_raw_root:
        import importlib.util
        spec = importlib.util.spec_from_file_location('replay', G0 / 'replay-archive.py')
        replay = importlib.util.module_from_spec(spec); spec.loader.exec_module(replay)
        replay.deny(args.deny_raw_root)
    roles = args.roles.split(',')
    if 'holdout' in roles:
        ap.error('the holdout is behind the procedural boundary; no bar is read from it here')
    reader = default_wave().reader(args.archive, roles=roles)
    cells = sorted({r['cell'] for r in reader.report_inventory() if r['cell'].split('/', 1)[1] in reader.allowed})
    reports = [cell_bars(reader, c, args.protocol) for c in cells]
    print(json.dumps(dict(schema='w39-repeat-bar-1', protocol=args.protocol, roles=roles,
                          rawRootForbidden=None if args.deny_raw_root is None else str(args.deny_raw_root),
                          generation=reader.generation, cells=len(reports),
                          rule='0.5 + half the largest pairwise run-median separation, per channel',
                          headline=headline(reports), reports=reports), indent=2))


if __name__ == '__main__':
    main()
