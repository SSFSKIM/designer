#!/usr/bin/env python3.12
"""Exact W42 sitting membership: the dump step, the passes, their runs and sentinels (clause 4).

Derived from W39 G0's pass-spec.py (§5.184), which stays untouched. What W42 changes:

- The bed is ../scenes-w42-body.json with ../bed.json, and a pass is one (scale, scheme,
  pose): one profile per pass, so a run's quarantine loses one endpoint's run, not two.
- No preflight: W42 declares no phase actuator.
- The sitting's first step is `dump-layers` over the whole declared bed, one launch per
  pass, before any capture (clause 4's stop; the charter's G1, "First, dump-layers").
  dump-layers refuses non-rest ids in either pose, so a receded pass is dumped through the
  `__rest` twin of each of its cells under `--inactive` (bed.json dumpList).
- The no-glass references (`ref-<background>__<state>`, one per distinct backdrop of the
  pass) are captured in run 1 only, as W39's colour references were.
- The sentinels are bed.json's, re-captured under the long protocol, three runs a pass.

A derived scenes document keeps the file's backgrounds, components and ROLES for exactly
the scenes it names (SceneSpec.validate() refuses a split naming an absent scene).
"""
import argparse
import copy
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BED_DIR = HERE.parent
SCENES = BED_DIR / 'scenes-w42-body.json'
BED = BED_DIR / 'bed.json'
RUNS = {'dump': 1, 'bed': 7, 'sentinel': 3}
SPLIT_ROLES = ('calibration', 'validation', 'holdout', 'recorded', 'probe')
MODES = {1: '69', 2: '68'}           # displayplacer: 2560x1440 unscaled (1x) / HiDPI (2x)
DUMP_SETTLE = 8                       # memo D's --settle; settle 16 matched it byte for byte


def load(scenes=SCENES, bed=BED):
    return json.loads(Path(scenes).read_text()), json.loads(Path(bed).read_text())


def endpoint(key):
    """'2x-light-receded' -> (2, 'light', 'receded')."""
    scale, scheme, pose = key.split('-')
    return int(scale[:-1]), scheme, pose


def pass_order(bed):
    """Every pass of the sitting, in its one declared order, with its kind and run count.

    Dumps for the 2x endpoints then the 1x endpoints (mode 68, then 69), then mode 68: the
    four 2x bed passes and their sentinels; then mode 69: the four 1x passes and theirs.
    The display is restored to mode 68 after the last pass.
    """
    keys = list(bed['passes'])
    by_scale = {s: [k for k in keys if endpoint(k)[0] == s] for s in (2, 1)}
    order = []
    for s in (2, 1):
        order += [dict(name='dump-' + k, kind='dump', key=k, scale=s, runs=RUNS['dump']) for k in by_scale[s]]
    for s in (2, 1):
        order += [dict(name=k, kind='bed', key=k, scale=s, runs=RUNS['bed']) for k in by_scale[s]]
        order += [dict(name=k + '-sentinel', kind='sentinel', key=k, scale=s, runs=RUNS['sentinel'])
                  for k in by_scale[s]]
    for i, p in enumerate(order):
        p['rank'] = i
        p['mode'] = MODES[p['scale']]
    return order


def pass_of(name, bed):
    found = [p for p in pass_order(bed) if p['name'] == name]
    if not found:
        raise ValueError('undeclared pass ' + name)
    return found[0]


def subset(spec, ids, profile):
    """The scenes file restricted to `ids` under the one profile, roles preserved."""
    missing = sorted(set(ids) - {s['id'] for s in spec['scenes']})
    if missing:
        raise ValueError('derived document names undeclared scenes: ' + ', '.join(missing[:5]))
    doc = copy.deepcopy(spec)
    doc['scenes'] = [s for s in doc['scenes'] if s['id'] in set(ids)]
    used_bg = {s['background'] for s in doc['scenes']}
    used_c = {s['component'] for s in doc['scenes']}
    doc['backgrounds'] = {k: v for k, v in doc['backgrounds'].items() if k in used_bg}
    doc['components'] = {k: v for k, v in doc['components'].items() if k in used_c}
    doc['profiles'] = [dict(key=profile['key'], colorScheme=profile['colorScheme'], a11y=profile['a11y'],
                            scenes=sorted(ids))]
    doc['split'] = {role: sorted(s for s in doc['split'].get(role, []) if s in set(ids)) for role in SPLIT_ROLES}
    doc['$comment'] = ['W42 sitting: a derived pass document (bed/sitting/pass-spec.py) over',
                       'bed/scenes-w42-body.json; never edited by hand.']
    return doc


def capture_ids(bed, key, run, sentinel=False):
    p = bed['passes'][key]
    state = p['state']
    if sentinel:
        return sorted(f'{c}__{state}' for c in p['sentinels'])
    ids = [f'{c}__{state}' for c in p['cells']]
    if run == 1:
        ids += [f'ref-{b}__{state}' for b in p['references']]
    return sorted(ids)


def derive(key, run=1, sentinel=False, scenes=SCENES, bed_path=BED):
    """The scenes document the harness captures for run `run` of pass `key`, read from disk."""
    return derive_from(*load(scenes, bed_path), key, run, sentinel)


def derive_from(spec, bed, key, run=1, sentinel=False):
    """The same document from an in-memory declaration: the driver derives every run of a pass
    from the snapshot it validated, so the hash it records names the bytes it used."""
    if key not in bed['passes']:
        raise ValueError('undeclared pass ' + key)
    limit = RUNS['sentinel' if sentinel else 'bed']
    if run not in range(1, limit + 1):
        raise ValueError(f'run {run} outside 1..{limit}')
    p = bed['passes'][key]
    profile = next(x for x in spec['profiles'] if x['key'] == p['profile'])
    ids = capture_ids(bed, key, run, sentinel)
    unlisted = sorted(set(ids) - set(profile['scenes']))
    if unlisted:
        raise ValueError('pass names scenes its profile does not capture: ' + ', '.join(unlisted[:5]))
    return subset(spec, ids, profile)


def dump_ids(key, bed_path=BED):
    return dump_ids_from(json.loads(Path(bed_path).read_text()), key)


def dump_ids_from(bed, key):
    ids = bed['dumpList'][key]
    want = sorted(f'{c}__rest' for c in bed['passes'][key]['cells'])
    if ids != want:
        raise ValueError('bed.json dumpList disagrees with its pass cells: ' + key)
    return ids


def cells(doc):
    return [p['key'] + '/' + s for p in doc['profiles'] for s in p['scenes']]


def plan(scenes=SCENES, bed_path=BED):
    spec, bed = load(scenes, bed_path)
    passes, totals = [], dict(dumpScenes=0, glassCaptures=0, referenceCaptures=0, sentinelCaptures=0)
    for p in pass_order(bed):
        key = p['key']
        row = dict(p)
        if p['kind'] == 'dump':
            ids = dump_ids(key, bed_path)
            row.update(runsDetail=[dict(run=1, scenes=len(ids))])
            totals['dumpScenes'] += len(ids)
        else:
            sentinel = p['kind'] == 'sentinel'
            detail = []
            for n in range(1, p['runs'] + 1):
                doc = derive(key, n, sentinel, scenes, bed_path)
                ids = [s['id'] for s in doc['scenes']]
                refs = sum(1 for s in ids if s.startswith('ref-'))
                detail.append(dict(run=n, cells=len(ids), glass=len(ids) - refs, references=refs))
                if sentinel:
                    totals['sentinelCaptures'] += len(ids)
                else:
                    totals['glassCaptures'] += len(ids) - refs
                    totals['referenceCaptures'] += refs
            row.update(runsDetail=detail, captures=sum(d['cells'] for d in detail))
        passes.append(row)
    totals['captures'] = totals['glassCaptures'] + totals['referenceCaptures'] + totals['sentinelCaptures']
    return dict(schema='w42-pass-plan-1', scenes=str(Path(scenes).name), passes=passes, totals=totals,
                modeSwitches=['start at 68 (2x dumps)', '68 -> 69 (1x dumps)', '69 -> 68 (2x passes)',
                              '68 -> 69 (1x passes)', '69 -> 68 (restore)'])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('action', choices=['plan', 'spec', 'dump-ids', 'order'])
    ap.add_argument('--pass', dest='key')
    ap.add_argument('--run', type=int, default=1)
    ap.add_argument('--sentinel', action='store_true')
    args = ap.parse_args()
    if args.action == 'order':
        # One line per pass for the orchestrator: name kind key mode runs.
        for q in pass_order(load()[1]):
            print(q['name'], q['kind'], q['key'], q['mode'], q['runs'])
        return
    if args.action == 'plan':
        value = plan()
    elif args.action == 'dump-ids':
        value = dump_ids(args.key)
    else:
        value = derive(args.key, args.run, args.sentinel)
    print(json.dumps(value, indent=2))


if __name__ == '__main__':
    main()
