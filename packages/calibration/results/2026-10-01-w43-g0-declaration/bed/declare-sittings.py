#!/usr/bin/env python3.12
"""W43 G0 (e): both sittings' plans, declared (charter Design "The two sittings"; clauses 1, 3, 4; X47).

    python3.12 -B declare-sittings.py [--sitting-tools <dir>]          # writes sitting-g1a.json, sitting-g1b.json
    python3.12 -B declare-sittings.py check [--sitting-tools <dir>]    # re-derives both, byte for byte

The plans are G0 (d)'s schema, `w43-sitting-plan-1` (`bed/sitting/pass-spec.py` on its branch; its
README is the contract). Every pass is derived from a file this G0 declared, never typed:
- the canonical bed from `scenes.json` version 8's four `-glass0.25` keys;
- the probe and ladder from `probe-bed.json` over `scenes-w43-probe.json`;
- the bridges from `../bridges/bridge-cells.json`;
- the dump sentinels from memo F's six shapes (`../memo-f/plan.json`) in G1a, and from the probe
  file in G1b, whose keys alone name the ladder's positions.

`--sitting-tools` names G0 (d)'s `bed/sitting/` directory. When given, each plan is also validated
by its `validate_plan` and counted by its `plan_counts`, read in this process and never edited.

**G1a** (Design, steps 0–3). At 0.5 and mode 68, the side's pose check, then the opening bridges
at 2x. At 0.5 and mode 69, the opening bridges at 1x. At 0.25, the dump sentinels and then the
canonical passes: 2x at mode 68 first, then 1x at mode 69. At 0.5, the closing W42 sentinels, 1x
first because the display is already there, then 2x, which ends the sitting at mode 68. That is
two slider writes and four display switches.

**G1b** (Design, steps 0–3, at 2x and mode 68 throughout). At 0.5, the pose check and the opening
bridges. At each of 0.25, 1, 0 and 0.75, the position's dump sentinels and then its capture passes,
one per pose over both schemes. At 0.5, the closing sentinels. The restore of the original bundle
is the user's hand and the parent's check after the plan, not a pass.

One capture pass per pose and position carries both schemes, as the canonical passes do. Its run 1
also recaptures the one declared no-glass reference per profile, so the 16 references of
probe-bed.json's 16 endpoint-passes become `run1Only` cells of 8 launches' first runs.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
EVID = HERE.parent
ROOT = HERE.parents[4]
CANONICAL = 'apps/reference-apple/scenes.json'
W42_SCENES = 'packages/calibration/results/2026-09-29-w42-g0-declaration/bed/scenes-w42-body.json'
PROBE = f'{HERE.relative_to(ROOT).as_posix()}/scenes-w43-probe.json'
POSE_CHECK = ('checkerboard__capsule-button__rest',
              ('204f21f0362d3226f7e28690be7c61ece0848931c89062e8a888f1ade22d4033',
               '6c15311b06af50a17141c54d7a71645cf63518c844b61d113b9426e15bcbf1d0'))
G1B_DUMP = ('a-g000-capsule-button', 'a-g128-capsule-button', 'a-g255-capsule-button',
            'a-g000-rrect-md', 'a-g128-rrect-md', 'a-g255-rrect-md')
ENDPOINTS = (('light', 'active'), ('light', 'receded'), ('dark', 'active'), ('dark', 'receded'))
STATE = {'active': 'rest', 'receded': 'inactive'}
CANONICAL_RUNS, BRIDGE_RUNS = 7, 3


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def key(scale, scheme, glass):
    return f'apple-macos-27.0-{scale}x-{scheme}-standard-glass{glass:g}'


def receded(sid):
    return sid.rsplit('__', 1)[-1].startswith('inactive')


def sources():
    out = {}
    for name, path in (('canonical', CANONICAL), ('w42', W42_SCENES), ('probe', PROBE)):
        out[name] = dict(path=path, sha256=sha((ROOT / path).read_bytes()))
    return out


class Plan:
    def __init__(self, sitting):
        self.sitting, self.passes = sitting, []

    def capture(self, name, role, glass, scale, pose, source, profiles, runs, protocol='normal', **extra):
        self.passes.append(dict(name=name, kind='capture', role=role, glass=glass, scale=scale, pose=pose,
                                source=source, runs=runs, protocol=protocol,
                                profiles={k: sorted(v) for k, v in sorted(profiles.items())}, **extra))

    def dump(self, name, glass, scale, pose, source, profile, scenes):
        self.passes.append(dict(name=name, kind='dump', role='dump-sentinel', glass=glass, scale=scale, pose=pose,
                                source=source, profile=profile, scenes=list(scenes)))

    def doc(self, comment):
        return {'schema': 'w43-sitting-plan-1', 'sitting': self.sitting, '$comment': comment,
                'sources': sources(), 'passes': self.passes}


def bridges():
    return json.loads((EVID / 'bridges/bridge-cells.json').read_text())


def pose_check(plan):
    sid, frames = POSE_CHECK
    k = key(2, 'light', 0.5)
    plan.capture('pose-check', 'pose-check', 0.5, 2, 'active', 'canonical', {k: [sid]}, 1,
                 expect={f'{k}/{sid}': list(frames)})


def sentinels(plan, phase, scale):
    cells = bridges()['sentinels']
    for scheme, pose in ENDPOINTS:
        row = cells['byEndpoint'][f'{scale}x-{scheme}-{pose}']
        plan.capture(f'{phase}-w42-{scale}x-{scheme}-{pose}', 'bridge-w42-sentinel', 0.5, scale, pose, 'w42',
                     {row['profile']: row['scenes']}, BRIDGE_RUNS, 'long')


def canonical_bridges(plan, scale):
    by_pass = bridges()['canonical']['byPass']
    for pose in ('active', 'receded'):
        lists = {}
        for row in by_pass[f'{scale}x-{pose}']:
            lists.setdefault(row['profile'], []).append(row['scene'])
        plan.capture(f'open-canonical-{scale}x-{pose}', 'bridge-canonical', 0.5, scale, pose, 'canonical', lists,
                     BRIDGE_RUNS)


def g1a():
    spec = json.loads((ROOT / CANONICAL).read_text())
    prof = {p['key']: p['scenes'] for p in spec['profiles']}
    memo_f = json.loads((EVID / 'memo-f/plan.json').read_text())
    shapes = [s for s in memo_f['blocks'][0]['scenes']]          # memo F's six dark-solid shapes
    plan = Plan('g1a')
    pose_check(plan)
    sentinels(plan, 'open', 2)
    canonical_bridges(plan, 2)
    sentinels(plan, 'open', 1)
    canonical_bridges(plan, 1)
    for scale in (2, 1):
        for scheme, pose in ENDPOINTS:
            plan.dump(f'dump-0.25-{scale}x-{scheme}-{pose}', 0.25, scale, pose, 'canonical', key(scale, scheme, 0.25),
                      shapes)
        for pose in ('active', 'receded'):
            lists = {key(scale, sch, 0.25): [s for s in prof[key(scale, sch, 0.25)] if receded(s) == (pose == 'receded')]
                     for sch in ('light', 'dark')}
            plan.capture(f'bed-0.25-{scale}x-{pose}', 'bed', 0.25, scale, pose, 'canonical', lists, CANONICAL_RUNS,
                         publish=True)
    sentinels(plan, 'close', 1)
    sentinels(plan, 'close', 2)
    return plan.doc('W43 G0 (e): the G1a plan, generated by bed/declare-sittings.py; never edit by hand.')


def g1b():
    bed = json.loads((HERE / 'probe-bed.json').read_text())
    plan = Plan('g1b')
    pose_check(plan)
    sentinels(plan, 'open', 2)
    canonical_bridges(plan, 2)
    for step in bed['order']:
        x = step['x']
        for scheme, pose in ENDPOINTS:
            plan.dump(f'dump-{x:g}-2x-{scheme}-{pose}', x, 2, pose, 'probe', key(2, scheme, x),
                      [f'{c}__rest' for c in G1B_DUMP])
        for pose in ('active', 'receded'):
            lists, refs = {}, {}
            for p in bed['passes'].values():
                if p['x'] == x and p['pose'] == pose:
                    lists[p['profile']] = [f"{c}__{p['state']}" for c in p['cells']]
                    refs[p['profile']] = [f"ref-{p['recapturedReference']}__{p['state']}"]
            plan.capture(f"{step['kind']}-{x:g}-2x-{pose}", step['kind'], x, 2, pose, 'probe', lists, bed['runs'],
                         run1Only=refs)
    sentinels(plan, 'close', 2)
    return plan.doc('W43 G0 (e): the G1b plan, generated by bed/declare-sittings.py; never edit by hand.')


def tools(directory):
    spec = importlib.util.spec_from_file_location('w43_pass_spec_for_e', Path(directory) / 'pass-spec.py')
    P = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(P)
    return P


def encode(doc):
    return json.dumps(doc, indent=2) + '\n'


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('action', nargs='?', choices=('write', 'check'), default='write')
    ap.add_argument('--sitting-tools', type=Path)
    args = ap.parse_args()
    plans = {'g1a': g1a(), 'g1b': g1b()}
    ok = True
    for name, plan in plans.items():
        path = HERE / f'sitting-{name}.json'
        text = encode(plan)
        if args.action == 'check':
            same = path.exists() and path.read_text() == text
            ok &= same
            print(f'{path.name}: ' + ('this generator\'s output' if same else 'MISMATCH'))
        else:
            path.write_text(text)
            print(f'{path.name}: sha256 {sha(text.encode())}')
        if args.sitting_tools:
            P = tools(args.sitting_tools)
            docs = {n: json.loads((ROOT / s['path']).read_bytes()) for n, s in plan['sources'].items()}
            P.validate_plan(plan, docs)
            print(f'  validated by pass-spec.py; totals {json.dumps(P.plan_counts(plan, docs)["totals"])}')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
