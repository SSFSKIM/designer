"""W42 G0 rehearsal (charter clause 3): the per-endpoint, per-referee reading of every variant.

Reads, for each variant, the referee outputs the gate's candidate-admission referees wrote
(`ref.sh` below: l1-cut, chroma-cut, exterior-cut, black-cut, e2-regression), the directional
stops (`gate/stops/stops.py`), the owner-test summary (`gate/owner/run-owner.py`) and the swap
log (the fraction of each cell's body the swap replaced), and writes one table: per endpoint
and referee, pass / FAIL / band-dominated / unmoved-by-construction, with the numbers, beside
the identity variant (the shipped render re-measured), which is the base every bar is read
against.

    python3.12 -B read.py --root /scratch/w42gate --variants c1,c1s,c2,c1m --out rehearsal
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import sys
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from swap import CAL  # noqa: E402

sys.path.insert(0, str(CAL / 'results/2026-09-26-w40-g0-generations'))
import matrix_store as store  # noqa: E402

EPS = ('light-active', 'light-receded', 'dark-active', 'dark-receded')
#: Clause 10's bars, as they stand when G2 opens.
L1_ABS, L1_GROWTH = 0.055, 0.005
M1_MED, M1_CELL = (0.8, 1.2), (0.6, 1.4)
M2_TOL = 0.02
#: MISSED_27_ROWS' three M1 cells (adopted-thresholds.test.ts), excused as recorded.
M1_NAMED = {('apple-macos-27.0-1x-light-standard-glass0.5', 'photo__rrect-sm__inactive'),
            ('apple-macos-27.0-2x-light-standard-glass0.5', 'photo__rrect-sm__inactive'),
            ('apple-macos-27.0-2x-light-standard-glass0.5', 'photo__rrect-sm__rest')}
#: A cell is BAND-DOMINATED when the swap replaced less than half its body: in the active pose
#: only beyond the 20 pt refraction band is swapped (swap.ACTIVE_BAND_PT).
BAND = 0.5


def ep_of(profile, scene):
    scheme = 'light' if '-light-' in profile else 'dark'
    pose = 'receded' if scene.split('__')[2].startswith('inactive') else 'active'
    return f'{scheme}-{pose}'


def load(root: Path, variant: str):
    d = root / f'ref-{variant}'
    out = {k: json.loads((d / f'{k}.json').read_text()) for k in
           ('l1-cut', 'chroma-cut', 'black-cut', 'e2-regression', 'exterior-cut')
           if (d / f'{k}.json').exists()}
    if (d / 'stops.json').exists():
        out['stops'] = json.loads((d / 'stops.json').read_text())
    o = root / f'owner-{variant}' / 'summary.json'
    if o.exists():
        out['owner'] = json.loads(o.read_text())
    swaps = {}
    for tree in [root / f'tree-{variant}']:
        s = tree / f'swap-{variant}.json'
        if s.exists():
            for c in json.loads(s.read_text())['cells']:
                swaps[(c['profile'], c['scene'])] = c
    out['swap'] = swaps
    rows = {}
    for st in sorted(root.glob(f'stage-{variant}/stage-*')):
        for r in store.load_current_rows(matrix_path=str(st / 'matrix.json')):
            rows[(r['key']['profileKey'], r['key']['sceneId'])] = r
    out['rows'] = rows
    return out


def swapped(v, profile, scene):
    c = v['swap'].get((profile, scene))
    return None if c is None else c.get('swappedFraction', 0.0 if c.get('moved') == 0 else None)


def read_l1(v, base):
    cells = defaultdict(list)
    base_miss = {c['cell'] for c in base['l1-cut']['cells'] if c['error'] is not None and c['error'] > L1_ABS}
    for c in v['l1-cut']['cells']:
        p, s = c['cell'].split('/', 1)
        cells[ep_of(p, s)].append(c)
    out = {}
    for ep in EPS:
        cs = [c for c in cells[ep] if c['error'] is not None]
        new_abs = [c for c in cs if c['error'] > L1_ABS and c['cell'] not in base_miss]
        grow = [c for c in cs if c['growth'] > L1_GROWTH]
        fails = new_abs + [c for c in grow if c not in new_abs]
        bd = [c for c in fails if (swapped(v, *c['cell'].split('/', 1)) or 0) < BAND]
        out[ep] = dict(
            cells=len(cells[ep]), measured=len(cs), newAbsoluteMisses=len(new_abs),
            growthFailures=len(grow), maxError=max(c['error'] for c in cs),
            maxGrowth=max(c['growth'] for c in cs if c['growth'] is not None),
            failures=[dict(cell=c['cell'], native=c['native'], web=c['web'], error=c['error'],
                           growth=c['growth'], swappedFraction=swapped(v, *c['cell'].split('/', 1)))
                      for c in sorted(fails, key=lambda c: -(c['growth'] or 0))],
            bandDominatedFailures=len(bd),
            verdict='pass' if not fails else ('FAIL (band-dominated)' if len(bd) == len(fails) else 'FAIL'))
    return out


def read_m1m2(v, base):
    beds = defaultdict(list)
    for c in v['chroma-cut']['cells']:
        beds[f"{c['scheme']}-{'receded' if c['pose'] == 'inactive' else 'active'}"].append(c)
    out = {}
    for ep in EPS:
        cs = beds[ep]
        Rs = sorted(c['R'] for c in cs)
        med = (Rs[len(Rs) // 2] + Rs[(len(Rs) - 1) // 2]) / 2
        out_cells = [c for c in cs if not (M1_CELL[0] <= c['R'] <= M1_CELL[1])
                     and (c['profile'], c['scene']) not in M1_NAMED]
        m2 = []
        for c in cs:
            # Apple's reading is the native side, the same in every variant (the identity stage's).
            n = base['rows'][(c['profile'], c['scene'])]['material']['interiorStdDevNative']['value']
            r, w = c['interiorStdDevWebReference'], c['interiorStdDevWeb']
            d = (w - r) / r
            if abs(d) <= M2_TOL:
                verdict = 'within'
            else:
                toward = (w - r) * (n - r) > 0
                beyond = (w - n) * (n - r) > 0
                verdict = 'named' if toward and (not beyond or abs(w - n) / n <= M2_TOL) else 'FAIL'
            m2.append(dict(cell=f"{c['profile']}/{c['scene']}", reference=r, web=w, native=n,
                           delta=d, verdict=verdict,
                           swappedFraction=swapped(v, c['profile'], c['scene'])))
        m2_fail = [c for c in m2 if c['verdict'] == 'FAIL']
        bd = [c for c in m2_fail if (c['swappedFraction'] or 0) < BAND]
        out[ep] = dict(
            M1=dict(cells=len(cs), median=med, min=Rs[0], max=Rs[-1],
                    outOfCellWindow=[dict(cell=f"{c['profile']}/{c['scene']}", R=c['R']) for c in out_cells],
                    verdict='pass' if M1_MED[0] <= med <= M1_MED[1] and not out_cells else 'FAIL'),
            M2=dict(cells=len(cs), named=sum(c['verdict'] == 'named' for c in m2),
                    within=sum(c['verdict'] == 'within' for c in m2), failures=m2_fail,
                    all=m2, bandDominatedFailures=len(bd),
                    verdict='pass' if not m2_fail else ('FAIL (band-dominated)' if len(bd) == len(m2_fail) else 'FAIL')))
    return out


def read_x1(v):
    per = defaultdict(lambda: [0, 0])
    for c in v['black-cut']['cells']:
        ep = ep_of(c['profile'], c['scene'])
        per[ep][0] += 1
        per[ep][1] += int(any(c[m]['aboveZero'] or c[m]['aboveOne'] for m in ('integer', 'analytic')))
    return {ep: dict(cells=per[ep][0], failing=per[ep][1],
                     verdict='pass (exterior: the swap does not reach it)' if per[ep][1] == 0 else 'FAIL')
            for ep in EPS}


def read_e2(v):
    e = v['e2-regression']
    per = defaultdict(lambda: dict(cells=set(), fail=0))
    for f in e['failures']:
        p, s = f['cell'].split('/', 1)
        per[ep_of(p, s)]['cells'].add(f['cell'])
        per[ep_of(p, s)]['fail'] += 1
    out = {}
    for ep in EPS:
        if ep.endswith('receded'):
            out[ep] = dict(verdict='n/a (E2 reads the active pose only)')
            continue
        cells = sorted(per[ep]['cells'])
        out[ep] = dict(failingBins=per[ep]['fail'], failingCells=len(cells), cells=cells,
                       verdict='pass' if not cells else 'FAIL (band-dominated: every shell is inside '
                       'the 20 pt band, held at the shipped render; the bins move only through the '
                       "cell's own deep median, d <= -6 CSS px)")
    return out


def read_stops(v):
    s = v.get('stops')
    if s is None:
        return {}
    out = {}
    for stop, key in (('H', 'halo'), ('P', 'chroma')):
        per = defaultdict(list)
        for c in s['stops'][key]['cells']:
            per[ep_of(c['profile'], c['scene'])].append(c)
        for ep in EPS:
            cs = per[ep]
            fails = [c for c in cs if c['verdict'] != 'pass']
            bd = [c for c in fails if (swapped(v, c['profile'], c['scene']) or 0) < BAND]
            out.setdefault(ep, {})[stop] = dict(
                cells=len(cs), failing=len(fails), bandDominatedFailures=len(bd),
                failures=[dict(cell=f"{c['profile']}/{c['scene']}", stats={
                    k: {kk: st.get(kk) for kk in ('native', 'shipped', 'candidate', 'dShip', 'dCand', 'res', 'verdict')}
                    for k, st in c['statistics'].items()}) for c in fails],
                verdict='pass' if not fails else ('FAIL (band-dominated)' if len(bd) == len(fails) else 'FAIL'))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--root', type=Path, required=True)
    ap.add_argument('--variants', required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    base = load(args.root, 'identity')
    result = dict(base=dict(
        l1=read_l1(base, base), m1m2=read_m1m2(base, base), x1=read_x1(base), e2=read_e2(base),
        stops=read_stops(base)), variants={})
    for name in args.variants.split(','):
        v = load(args.root, name)
        if 'l1-cut' not in v:
            continue
        exterior_same = None
        if 'exterior-cut' in v and 'exterior-cut' in base:
            exterior_same = [r.get('statistic') for r in v['exterior-cut'].get('rows', [])] == \
                [r.get('statistic') for r in base['exterior-cut'].get('rows', [])]
        result['variants'][name] = dict(
            l1=read_l1(v, base), m1m2=read_m1m2(v, base), x1=read_x1(v), e2=read_e2(v),
            stops=read_stops(v), owner=v.get('owner'), c1ActiveStatisticsUnchanged=exterior_same)
    args.out.with_suffix('.json').write_text(json.dumps(result, indent=1, default=list) + '\n')
    print(json.dumps({n: {ep: {
        'L1': r['l1'][ep]['verdict'], 'M1': r['m1m2'][ep]['M1']['verdict'],
        'M2': r['m1m2'][ep]['M2']['verdict'], 'X1': r['x1'][ep]['verdict'][:4],
        'E2': r['e2'][ep]['verdict'][:22], 'H': r['stops'].get(ep, {}).get('H', {}).get('verdict'),
        'P': r['stops'].get(ep, {}).get('P', {}).get('verdict')} for ep in EPS}
        for n, r in result['variants'].items()}, indent=1))


if __name__ == '__main__':
    main()
