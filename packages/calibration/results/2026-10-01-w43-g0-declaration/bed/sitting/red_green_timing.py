#!/usr/bin/env python3.12
"""Item 9's red/green: the dry plan and the timing are derived from the DECLARED membership.

RED, on W42's committed timing.py and dry-plan-summary.py (results/2026-09-29-w42-g0-declaration/
bed/sitting/, run unedited in a throwaway tree that holds them at their real relative paths with
W42's bed, W39's pin and W39 G1's attestations): they price W42's own bed (pass-spec.py over
bed.json), so placing a W43 plan at its declared path beside them, with the canonical scenes file
it reads, moves neither total.
GREEN, on W43's timing.py: its totals are the stand-in plan's membership, and they move by
exactly one run's modelled cost when the plan gains a run.

`scenario()` returns dict(name, red, green, red_ok, green_ok); red-green.py calls it. Nothing is
launched, read from the machine or written outside a temporary directory.
"""
import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[5]
W42_SITTING = REPO / 'packages/calibration/results/2026-09-29-w42-g0-declaration/bed/sitting'
W42_BED = W42_SITTING.parent
W39_PIN = REPO / 'packages/calibration/results/2026-09-26-w39-g0-colour-edge-bed/bundle-pin.json'
W39_G1 = REPO / 'packages/calibration/results/2026-09-26-w39-g1-colour-edge-sitting'
W43_BED = REPO / 'packages/calibration/results/2026-10-01-w43-g0-declaration/bed'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def w42_tree(root):
    """W42's sitting tools and what they read, at their real relative paths under `root`."""
    def put(src, link=False):
        dst = root / Path(src).relative_to(REPO)
        dst.parent.mkdir(parents=True, exist_ok=True)
        if link:
            dst.symlink_to(src)
        else:
            shutil.copyfile(src, dst)
    for name in ('timing.py', 'dry-plan-summary.py', 'pass-spec.py', 'sitting.py'):
        put(W42_SITTING / name)
    for name in ('scenes-w42-body.json', 'bed.json', 'pins.json'):
        put(W42_BED / name)
    put(W39_PIN)
    put(W39_G1 / 'attest', link=True)
    return root / W42_SITTING.relative_to(REPO)


def w42_totals(sitting):
    """Run W42's two derivers unedited; read their recorded totals."""
    for script in ('timing.py', 'dry-plan-summary.py'):
        subprocess.run([sys.executable, '-B', str(sitting / script)], check=True, capture_output=True, text=True,
                       env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
    timing = json.loads((sitting / 'timing.json').read_text())['w42']
    walk = json.loads((sitting / 'dry-plan.json').read_text())['totals']
    return dict(timingCaptures=sum(p.get('captures', 0) for p in timing['passes'] if p['kind'] != 'dump'),
                timingHours=timing['totalHours'], dryPlanCaptures=walk['captures'], dumpScenes=walk['dumpScenes'])


def scenario():
    name = '9. the dry plan and the timing derived from the declared membership (the G1a stand-in)'
    S = load('w43_stand_in_rg_timing', HERE / 'stand_in.py')
    canonical, w42, plan = S.build()
    sources = S.sources_of(plan, canonical, w42)
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        sitting = w42_tree(root)
        if not Path('/Users/new/vitrea-w42/grounding/dumps/runs').is_dir():
            return dict(name=name, red='SKIPPED: memo D\'s dump scratch, which W42\'s timing.py reads, is absent',
                        green='not run', red_ok=False, green_ok=False)
        before = w42_totals(sitting)
        plan_path = root / W43_BED.relative_to(REPO) / 'sitting-g1a.json'
        plan_path.parent.mkdir(parents=True, exist_ok=True)
        plan_path.write_bytes(S.encode(plan))
        (root / S.CANONICAL).parent.mkdir(parents=True, exist_ok=True)
        (root / S.CANONICAL).write_bytes(canonical)
        after = w42_totals(sitting)
    red_ok = before == after and before['dryPlanCaptures'] != 4103 and before['timingCaptures'] == 3441
    red = (f'W42 tools price {before["dryPlanCaptures"]:,} captures, {before["dumpScenes"]} dump scenes, '
           f'{before["timingHours"]} h without a W43 plan and {after["dryPlanCaptures"]:,} / {after["dumpScenes"]} / '
           f'{after["timingHours"]} h with the stand-in at its declared path: blind to it')
    T = load('w43_timing_rg', HERE / 'timing.py')
    rates = T.measure()
    T.pass_spec().validate_plan(plan, sources)
    base = T.price(plan, sources, rates)
    moved = copy.deepcopy(plan)
    p = next(q for q in moved['passes'] if q['name'] == 'bed-0.25-2x-active')
    p['runs'] += 1
    cells = sum(len(v) for v in p['profiles'].values())
    grown = T.price(moved, sources, rates)
    delta = grown['exactTotalSeconds'] - base['exactTotalSeconds']
    run = T.run_seconds(rates, 'normal', 2, cells) + rates['gapWithinPassSeconds']
    green_ok = (base['totals']['captures'] == 4103 and base['totals']['dumpScenes'] == 48
                and grown['totals']['captures'] == 4103 + cells and abs(delta - run) < 1e-6)
    green = (f'W43 timing prices the stand-in at {base["totals"]["captures"]:,} captures and '
             f'{base["totals"]["dumpScenes"]} dump scenes, {base["totalHours"]} h; one more 2x active bed run '
             f'gives {grown["totals"]["captures"]:,} captures and +{delta:.1f} s, that run\'s modelled {run:.1f} s')
    return dict(name=name, red=red, green=green, red_ok=red_ok, green_ok=green_ok)


if __name__ == '__main__':
    r = scenario()
    print(f'{r["name"]}\n  RED   (W42 committed tools): {r["red"]}  [{"defect shown" if r["red_ok"] else "NOT SHOWN"}]\n'
          f'  GREEN (W43): {r["green"]}  [{"fixed" if r["green_ok"] else "NOT FIXED"}]')
    raise SystemExit(0 if r['red_ok'] and r['green_ok'] else 1)
