#!/usr/bin/env python3.12
"""W42 G1: the repeat bar per cell, region statistic and channel, from the archive of record (c9a §5.195).

report-bars.py <archive root> --out <dir> [--deny <path> ...]

The declaration (`../../2026-09-29-w42-g0-declaration/declaration.md`, survivalBars; charter clause
5): seven runs; the bar per cell, region statistic and channel is 0.5 + half the largest pairwise
separation of the run medians, computed before plurality and published before G2. A zero observed
spread buys no tolerance: the bar is then exactly 0.5.

The region statistics are the instrument's own (`instrument/regions.py`, the populations clause 6
gates on), on the instrument's own cells (`forward.Cell`: the declared backdrop, shape, scale and
pose, and its deep evaluation mask). Every statistic is a per-channel median of output codes over
its population, so one run contributes one median per population and channel. An active cell is
read at both of ruling 3's masks (`n`, the narrow kernel's support; `w`, the wide one's), a
receded cell at its one mask. The seven-run bed (normal protocol) and the three-run sentinels
(long protocol) are separate strata and are never pooled (W39 G1's `report-bars.py`, the same rule).

Only the roles the wave Reader authorises without a receipt are read: calibration, validation and
probe (the F bridges). The holdout's bars are not computed here; its payload stays behind the
procedural boundary for G2's one exposure. No-glass references are captured in run 1 only and
carry no bar. Every read goes through the guarded Reader, so the archive is the only input, and
`--deny` forbids any open under a path (the raw run root, the producer's output) for the process.
"""
import argparse
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
DECL = HERE.parents[1] / '2026-09-29-w42-g0-declaration'
SITTING = DECL / 'bed/sitting'
sys.path.insert(0, str(DECL / 'instrument'))
import bed as IB  # noqa: E402  the instrument's bed (pinned scenes)
import forward as F  # noqa: E402
import regions as R  # noqa: E402

SCHEMA = 'w42-repeat-bar-1'
ROLES = ('calibration', 'validation', 'probe')


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def bar(values):
    """0.5 + half the largest pairwise separation of the runs' medians; and that separation."""
    a = np.asarray(values, float)
    spread = float(a.max() - a.min())
    return 0.5 + 0.5 * spread, spread


def decode(raw):
    with Image.open(io.BytesIO(raw)) as image:
        return np.asarray(image.convert('RGB'), dtype=np.float64)


def endpoint(profile, sid):
    scale = 1 if '-1x-' in profile else 2
    scheme = 'dark' if '-dark-' in profile else 'light'
    pose = 'rest' if sid.endswith('__rest') else 'inactive'
    return scale, scheme, pose


def cell_bars(wave, reader, cell, archive):
    profile, sid = cell.split('/', 1)
    role = wave.roles[sid]
    scene = wave.scenes[sid]
    component = wave.spec['components'][scene['component']]
    base = dict(cell=cell, role=role)
    if component.get('kind') == 'none':
        return [dict(base, status='no-glass reference: run 1 only, no bar')]
    scale, scheme, pose = endpoint(profile, sid)
    cid = sid.rsplit('__', 1)[0]
    family = wave.bed['cells'].get(cid, {}).get('family')
    header, blobs = archive.unbundle(reader.read(cell, 'states'))
    out = []
    kernels = ('n', 'w') if pose == 'rest' else ('n',)
    for kernel in kernels:
        c = F.Cell(f'{scale}x|{cid}', scene['background'], scene['component'], scale, scheme, pose,
                   rgb=True, kernel=kernel)
        if c.mask.sum() == 0:
            out.append(dict(base, family=family, kernel=kernel, status='empty deep mask'))
            continue
        pops = R.populations(c)
        if not pops:
            # regions.MIN_PX: a population under 12 px is not a statistic. A checker too fine for any
            # square's core to reach it (pitch 4 at 1x) has no region statistic at all, so no bar.
            out.append(dict(base, family=family, kernel=kernel,
                            status=f'no region statistic: every population under {R.MIN_PX} px'))
            continue
        stats_of = {}
        for protocol in ('normal', 'long'):
            rows = [r for r in header['runs'] if r['protocol'] == protocol]
            if not rows:
                continue
            row = dict(base, family=family, kernel=kernel, protocol=protocol, runs=len(rows),
                       passes=sorted({r['pass'] for r in rows}), distinctStates=len({r['frame'] for r in rows}))
            if len(rows) < 2:
                out.append(dict(row, status='insufficient admitted repeats'))
                continue
            per_run = []
            for r in rows:
                if r['frame'] not in stats_of:
                    stats_of[r['frame']] = R.statistics(c, decode(blobs[r['frame']]), pops)
                per_run.append(stats_of[r['frame']])
            names = sorted(per_run[0])
            if any(sorted(s) != names for s in per_run):
                raise ValueError('runs disagree on the statistic set: ' + cell)
            bars = {}
            for name in names:
                b, s = bar([p[name] for p in per_run])
                bars[name] = dict(bar=round(b, 6), spread=round(s, 6))
            out.append(dict(row, status='measured', statistics=bars))
    return out


def headlines(rows):
    measured = [r for r in rows if r.get('status') == 'measured']
    out = {}
    for protocol in ('normal', 'long'):
        for kernel in ('n', 'w'):
            sel = [r for r in measured if r['protocol'] == protocol and r['kernel'] == kernel]
            if not sel:
                continue
            flat = [(r['cell'], name, v['bar']) for r in sel for name, v in r['statistics'].items()]
            bars = np.array([b for _, _, b in flat])
            top = sorted(flat, key=lambda t: -t[2])[:12]
            by_role = {}
            for role in ROLES:
                rb = np.array([b for r in sel if r['role'] == role for b in (v['bar'] for v in r['statistics'].values())])
                if rb.size:
                    by_role[role] = dict(statistics=int(rb.size), atFloor=int((rb == 0.5).sum()),
                                         max=float(rb.max()), p99=float(np.quantile(rb, 0.99)))
            out[f'{protocol}/{kernel}'] = dict(
                cells=len(sel), statistics=int(bars.size), atFloor=int((bars == 0.5).sum()),
                above1=int((bars > 1.0).sum()), above2=int((bars > 2.0).sum()),
                max=float(bars.max()), p99=float(np.quantile(bars, 0.99)), median=float(np.median(bars)),
                cellsWithMoreThanOneState=sum(1 for r in sel if r['distinctStates'] > 1),
                byRole=by_role, largest=[dict(cell=c, statistic=n, bar=b) for c, n, b in top])
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('archive', type=Path)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--deny', type=Path, action='append', default=[])
    args = ap.parse_args(argv)
    archive = module('w42_archive_for_bars', SITTING / 'w42_archive.py')
    for path in args.deny:
        archive.deny(path)
    wave = archive.wave_module().default_wave()
    tree = archive.verify_tree(args.archive)
    reader = wave.reader(args.archive, roles=ROLES)
    cells = sorted({r['cell'] for r in reader.report_inventory()
                    if r['kind'] == 'states' and r['cell'].split('/', 1)[1] in reader.allowed})
    withheld = sorted({r['cell'] for r in reader.report_inventory() if r['cell'].split('/', 1)[1] not in reader.allowed})
    rows = [row for cell in cells for row in cell_bars(wave, reader, cell, archive)]
    value = dict(schema=SCHEMA, archiveGeneration=reader.generation, roles=list(ROLES),
                 rule='bar = 0.5 + 0.5 * (max - min) of the run medians, per cell, region statistic and channel; '
                      'normal (seven-run bed) and long (three-run sentinels) protocols never pooled',
                 instrument={name: hashlib.sha256((DECL / 'instrument' / name).read_bytes()).hexdigest()
                             for name in ('regions.py', 'forward.py', 'geometry.py', 'bed.py')},
                 tool=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                 deniedPaths=[str(p) for p in args.deny], cellsRead=len(cells),
                 cellsWithheld=dict(count=len(withheld), reason='holdout: behind the receipt'), rows=rows)
    args.out.mkdir(parents=True, exist_ok=True)
    raw = (json.dumps(value, sort_keys=True, separators=(',', ':')) + '\n').encode()
    (args.out / 'bar.json.gz').write_bytes(gzip.compress(raw, mtime=0))
    heads = dict(schema=SCHEMA, archiveGeneration=reader.generation, treeEntries=tree.get('entries'),
                 barJsonSha256=hashlib.sha256(raw).hexdigest(), cellsRead=len(cells),
                 cellsWithheld=len(withheld),
                 statuses={s: sum(1 for r in rows if r.get('status') == s) for s in sorted({r['status'] for r in rows})},
                 strata=headlines(rows))
    (args.out / 'bar-headlines.json').write_text(json.dumps(heads, indent=2) + '\n')
    print(json.dumps({k: v for k, v in heads.items() if k != 'strata'}, indent=2))
    for key, h in heads['strata'].items():
        print(key, {k: v for k, v in h.items() if k not in ('largest', 'byRole')})


if __name__ == '__main__':
    main()
