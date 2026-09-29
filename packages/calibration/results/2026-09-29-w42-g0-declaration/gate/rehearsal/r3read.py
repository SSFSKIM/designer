"""W42 G0 rehearsal round 3: every combination of candidate (1 | 2), knee (on-luma | per-channel),
chroma (none | face saturation | fitted g) and band (held | blended), per endpoint and referee,
and which endpoints could pass the gate as things stand.

A combination with chroma 'none' and the band held is a round-1 / round-2 variant (c1, c2, c1p,
c2p): the same pixels, read again here. Everything else is round 3's r3-* variants. The gate's
referees are the ones clause 10 names; E2 is read two ways, as adopted (its own deep-median
reference) and absolutely against Apple (round 2's reading, e2abs.py), because its reading is
the user's. Candidate 1 in light active is excluded by the parent's ruling (L1 reads as written).

    python3.12 -B r3read.py --root /scratch/w42gate --out round3/rehearsal-r3
"""
from __future__ import annotations

import argparse
import itertools
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EPS = ('light-active', 'light-receded', 'dark-active', 'dark-receded')
ALIAS = {'r3-1lnh': 'c1', 'r3-2lnh': 'c2', 'r3-1pnh': 'c1p', 'r3-2pnh': 'c2p'}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    combos = [f'r3-{c}{k}{h}{b}' for c, k, h, b in itertools.product('12', 'lp', 'nsg', 'hb')]
    names = [ALIAS.get(c, c) for c in combos]
    subprocess.run([sys.executable, '-B', str(HERE / 'read.py'), '--root', str(args.root),
                    '--variants', ','.join(names), '--out', str(args.out) + '-read'],
                   check=True, capture_output=True)
    read = json.loads(Path(str(args.out) + '-read.json').read_text())['variants']
    table = {}
    for combo, name in zip(combos, names):
        v = read.get(name)
        if v is None:
            table[combo] = dict(variant=name, missing=True)
            continue
        e2abs_path = args.root / f'e2abs-{name}.json'
        e2abs = json.loads(e2abs_path.read_text())['summary'] if e2abs_path.exists() else None
        per = {}
        for ep in EPS:
            fails = []
            l1 = v['l1'][ep]
            if l1['newAbsoluteMisses'] or l1['growthFailures']:
                fails.append(f"L1 {l1['growthFailures']} (max {l1['maxGrowth']:+.4f})")
            m1 = v['m1m2'][ep]['M1']
            if m1['verdict'] != 'pass':
                fails.append(f"M1 {m1['median']:.2f}/{len(m1['outOfCellWindow'])}")
            m2 = v['m1m2'][ep]['M2']
            if m2['failures']:
                fails.append(f"M2 {len(m2['failures'])}")
            if v['x1'][ep]['failing']:
                fails.append('X1')
            st = v['stops'].get(ep, {})
            for s in ('H', 'P'):
                if st.get(s, {}).get('failing'):
                    fails.append(f"Stop{s} {st[s]['failing']}/{st[s]['cells']}")
            e2rel = v['e2'][ep].get('failingBins')
            e2a = None
            if ep.endswith('active') and e2abs is not None:
                scheme = ep.split('-')[0]
                e2a = sum(1 for c in e2abs.get('failingCells', []) if f'-{scheme}-' in c)
            per[ep] = dict(fails=fails, e2Adopted=e2rel, e2AbsoluteFailingCells=e2a,
                           excludedByRuling=(combo[3] == '1' and ep == 'light-active'))
        table[combo] = dict(variant=name, endpoints=per)
    args.out.with_suffix('.json').write_text(json.dumps(table, indent=1) + '\n')
    lines = [f"{'combination':12s} " + ' | '.join(f'{ep:34s}' for ep in EPS)]
    for combo, row in table.items():
        if row.get('missing'):
            lines.append(f'{combo:12s} MISSING')
            continue
        cells = []
        for ep in EPS:
            e = row['endpoints'][ep]
            txt = 'PASS' if not e['fails'] else '; '.join(e['fails'])
            if ep.endswith('active'):
                txt += f" [E2 adopted {e['e2Adopted']} bins; abs {e['e2AbsoluteFailingCells']} cells]"
            if e['excludedByRuling']:
                txt = '(ruled out) ' + txt
            cells.append(f'{txt:34s}')
        lines.append(f'{combo:12s} ' + ' | '.join(cells))
    args.out.with_suffix('.txt').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))
    detail(args, combos, names, read)


def short(cell):
    p, s = cell.split('/')
    return f"{p.split('-')[3]} {s}"


def detail(args, combos, names, read):
    """Per combination and endpoint: M1's median always (item (a) asks for it whether or not it
    fails), and every failing cell of L1, M2, Stop H and Stop P with its reading; then, for the
    active pose, how much of the body the candidate reaches on each active component
    (the mean swap weight over the contour's coverage, from swap-<variant>.json): the answer to
    (c)'s "what the active pose then changes for spans <= 44"."""
    out = []
    for combo, name in zip(combos, names):
        v = read.get(name)
        if v is None:
            continue
        out.append(f'{combo} ({name})')
        for ep in EPS:
            m1 = v['m1m2'][ep]['M1']
            bits = [f"M1 median {m1['median']:.3f} [{m1['min']:.2f}, {m1['max']:.2f}]"]
            for f in v['l1'][ep].get('failures', []):
                bits.append(f"L1 {short(f['cell'])} web {f['web']:.4f} native {f['native']:.4f} "
                            f"growth {f['growth']:+.4f}")
            for f in v['m1m2'][ep]['M2']['failures']:
                bits.append(f"M2 {short(f['cell'])} {100 * f['delta']:+.1f} % (native "
                            f"{100 * (f['native'] / f['reference'] - 1):+.1f} %)")
            for sname in ('H', 'P'):
                for f in v['stops'].get(ep, {}).get(sname, {}).get('failures', []):
                    st = ', '.join(f"{k} {x['candidate']:.4g} vs native {x['native']:.4g} / shipped "
                                   f"{x['shipped']:.4g}" for k, x in f['stats'].items() if x['verdict'] == 'FAIL')
                    bits.append(f'Stop{sname} {short(f["cell"])}: {st}')
            out.append(f'  {ep:13s} ' + '\n                '.join(bits))
    out.append('')
    out.append('(c) the reach in the active pose, held band against blend: mean swap weight over the '
               'covered body, per component')
    for combo, name in zip(combos, names):
        sw = args.root / f'tree-{name}' / f'swap-{name}.json'
        if not sw.exists():
            continue
        by = {}
        for c in json.loads(sw.read_text())['cells']:
            if c['endpoint'].endswith('active'):
                comp = c['scene'].split('__')[1]
                by.setdefault(comp, []).append(c['swappedFraction'])
        out.append(f'  {combo}: ' + ', '.join(f'{k} {sum(x) / len(x):.3f} (n {len(x)})'
                                              for k, x in sorted(by.items())))
    Path(str(args.out) + '-detail.txt').write_text('\n'.join(out) + '\n')


if __name__ == '__main__':
    main()
