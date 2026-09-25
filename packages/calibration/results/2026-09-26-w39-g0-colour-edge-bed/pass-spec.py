#!/usr/bin/env python3
"""Exact W39 pass membership, including references only in run one (§5.184)."""
import argparse
import copy
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SENTINELS = ('g128-c-c44', 'factor-y1-c12-h0-colour')


def derive(pose, scale, run=1, reachable_axes=(), sentinel=False):
    if pose not in ('active', 'inactive') or scale not in (1, 2) or run not in range(1, 8):
        raise ValueError('undeclared pose/scale/run')
    axes = set(reachable_axes)
    if not axes <= {'x', 'y'}:
        raise ValueError('undeclared phase axis')
    doc = json.loads((ROOT / 'apps/reference-apple/scenes-w39-colour-edge.json').read_text())
    state = 'rest' if pose == 'active' else 'inactive'
    def selected(s):
        if s['state'] != state or s.get('$scale', scale) != scale:
            return False
        if sentinel:
            return s['id'].rsplit('__', 1)[0] in SENTINELS
        if s['$class'] == 'colour-reference':
            return run == 1
        if s['$class'] == 'phase':
            return bool(axes) and (s['$phaseAxis'] == 'zero' or s['$phaseAxis'] in axes)
        return True
    doc['scenes'] = [s for s in doc['scenes'] if selected(s)]
    ids = {s['id'] for s in doc['scenes']}
    doc['profiles'] = [p for p in doc['profiles'] if f'-{scale}x-' in p['key']]
    for p in doc['profiles']:
        p['scenes'] = [s for s in p['scenes'] if s in ids]
    doc['split'] = dict(calibration=[], validation=[], holdout=[], probe=sorted(ids))
    return doc


def preflight(scale):
    if scale not in (1, 2):
        raise ValueError('undeclared scale')
    doc = json.loads((ROOT / 'apps/reference-apple/scenes-w39-preflight.json').read_text())
    doc['profiles'] = [p for p in doc['profiles'] if f'-{scale}x-' in p['key']]
    ids = set(doc['profiles'][0]['scenes'])
    doc['scenes'] = [s for s in doc['scenes'] if s['id'] in ids]
    doc['split'] = dict(calibration=[], validation=[], holdout=[], probe=sorted(ids))
    return doc


def cells(doc):
    return [p['key'] + '/' + s for p in doc['profiles'] for s in p['scenes']]


def plan():
    passes = []
    for pose, scale in [('active', 1), ('active', 2), ('inactive', 1), ('inactive', 2)]:
        runs = []
        for run in range(1, 8):
            base = cells(derive(pose, scale, run))
            full = cells(derive(pose, scale, run, ('x', 'y')))
            runs.append(dict(run=run, cells=base, count=len(base),
                conditionalCells=[c for c in full if c not in set(base)],
                conditionalCount=len(full) - len(base)))
        passes.append(dict(pose=pose, scale=scale, runs=runs,
            sentinel=dict(cells=cells(derive(pose, scale, sentinel=True)), runs=3,
                          initialSettleSeconds=8, orderSeed=3901)))
    base = sum(r['count'] for p in passes for r in p['runs'])
    conditional = sum(r['conditionalCount'] for p in passes for r in p['runs'])
    sentinel = sum(len(p['sentinel']['cells']) * 3 for p in passes)
    pre = []
    for scale in (1, 2):
        names = cells(preflight(scale))
        repeats = [c for c in names if '-zero' in c]
        pre.append(dict(scale=scale, pose='active', scheme='light', cells=names,
                        endRepeatCells=repeats, count=len(names) + len(repeats)))
    pre_count = sum(p['count'] for p in pre)
    total = base + sentinel + pre_count
    return dict(schema='w39-pass-plan-1', passOrder=['preflight-1x', 'preflight-2x',
        'active-1x', 'active-2x', 'inactive-1x', 'inactive-2x', 'long-sentinels-per-pass'],
        preflight=pre, passes=passes,
        counts=dict(normal=5768, run1ColourReferences=504, sentinels=sentinel,
                    preflight=pre_count, baseTotal=total, conditionalBothAxes=conditional,
                    conditionalOneAxis=448, totalBothAxes=total + conditional),
        timeModel=dict(secondsPerCapture=9.62, baseSeconds=total * 9.62,
                       bothAxesSeconds=(total + conditional) * 9.62,
                       excludes='machine changes, grant switches and independent idle preparation'),
        amendment='Charter v2 baseline6356 used36 preflight captures. G0 adds four phase-zero end repeats:6360 baseline,7144 with both axes. No ordinary bed cell dropped.')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('action', choices=['plan', 'spec', 'preflight'])
    ap.add_argument('--pose', choices=['active', 'inactive'])
    ap.add_argument('--scale', type=int, choices=[1, 2])
    ap.add_argument('--run', type=int, default=1)
    ap.add_argument('--reachable-axes', default='')
    ap.add_argument('--sentinel', action='store_true')
    ap.add_argument('--out', type=Path)
    args = ap.parse_args()
    if args.action == 'plan':
        value = plan()
    elif args.action == 'preflight':
        value = preflight(args.scale)
    else:
        value = derive(args.pose, args.scale, args.run, filter(None, args.reachable_axes.split(',')), args.sentinel)
    text = json.dumps(value, indent=2) + '\n'
    if args.out:
        if args.out.exists():
            raise ValueError('refuse overwrite: remove a generated plan explicitly only before captures')
        args.out.write_text(text)
    else:
        print(text, end='')


if __name__ == '__main__':
    main()
