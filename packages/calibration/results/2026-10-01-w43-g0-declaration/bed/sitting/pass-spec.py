#!/usr/bin/env python3.12
"""Exact W43 sitting membership, read from a DECLARED sitting plan (charter G0 (d), (e); clause 1).

Derived from W42 G0's pass-spec.py, which stays untouched. W42's membership was one wave-local
bed (bed.json over one scenes file, one profile per pass). W43's two sittings are not: G1a
captures the canonical `-glass0.25` bed from `apps/reference-apple/scenes.json` (a pass is one
scale and pose over BOTH schemes, as W29's were), brackets it with bridges at 0.5 over the
canonical file and W42's own scenes file, and opens every slider position with dump sentinels;
G1b adds the wave-local probe and ladder file. So the membership is a plan, declared and hashed
in G0 (e), and everything here derives from it.

The plan (`../sitting-<sitting>.json`, schema `w43-sitting-plan-1`):

    {"schema": "w43-sitting-plan-1", "sitting": "g1a",
     "sources": {"<name>": {"path": "<repo-relative scenes file>", "sha256": "<hex>"}, ...},
     "passes": [<pass>, ...]}                                   # the sitting's one order

    capture pass: {"name", "kind": "capture", "role": "<label>", "glass": x, "scale": 1|2,
                   "pose": "active"|"receded", "source": "<name>", "runs": n,
                   "protocol": "normal"|"long",
                   "profiles": {"<profile key>": [<scene id>, ...]},   # every run
                   "run1Only": {"<profile key>": [<scene id>, ...]},   # optional: run 1 only
                   "publish": true|false,                               # materialize's bed
                   "expect": {"<profile key>/<scene id>": [<frame sha256>, ...]}}  # optional
    dump pass:    {"name", "kind": "dump", "role": "<label>", "glass": x, "scale": 1|2,
                   "pose": "active"|"receded", "source": "<name>", "profile": "<profile key>",
                   "scenes": [<__rest scene id>, ...]}

A pass's display mode is its scale's (68 for 2x, 69 for 1x); its slider position is `glass`,
which every profile key it captures must name exactly (X6: the key names every axis that
moved a pixel). `validate_plan` refuses a plan that breaks any of that before anything runs.
"""
import argparse
import copy
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
BED_DIR = HERE.parent
REPO = HERE.parents[5]
SCHEMA = 'w43-sitting-plan-1'
SITTINGS = ('g1a', 'g1b')
KINDS = ('capture', 'dump')
POSES = ('active', 'receded')
PROTOCOLS = ('normal', 'long')
SPLIT_ROLES = ('calibration', 'validation', 'holdout', 'recorded', 'probe')
MODES = {1: '69', 2: '68'}           # displayplacer: 2560x1440 unscaled (1x) / HiDPI (2x)
DUMP_SETTLE = 8                       # memo D's --settle; settle 16 matched it byte for byte
KEY = re.compile(r'^apple-macos-27\.0-(?P<scale>[12])x-(?P<scheme>light|dark)-(?P<a11y>[a-z-]+?)'
                 r'-glass(?P<glass>\d+(?:\.\d+)?)$')
SHA = re.compile(r'^[0-9a-f]{64}$')
DUMP_FIELDS = {'name', 'kind', 'role', 'glass', 'scale', 'pose', 'source', 'profile', 'scenes'}


def plan_path(sitting):
    if sitting not in SITTINGS:
        raise ValueError(f'undeclared sitting {sitting!r}; W43 declares {", ".join(SITTINGS)}')
    return BED_DIR / f'sitting-{sitting}.json'


def parse_key(key):
    """'apple-macos-27.0-2x-light-standard-glass0.25' -> (2, 'light', 'standard', 0.25), or None."""
    found = KEY.match(key)
    if not found:
        return None
    return int(found['scale']), found['scheme'], found['a11y'], float(found['glass'])


def receded_id(sid):
    """A scene's pose is its state's: the receded states are `inactive` and its tinted and pressed forms."""
    return sid.rsplit('__', 1)[-1].startswith('inactive')


def load(path, repo=REPO):
    """(plan, {source name: scenes document}) from disk, validated. The driver reads the raw bytes
    itself so that the hashes it checks name the bytes it derives from (`sitting.pinned_snapshot`)."""
    plan = json.loads(Path(path).read_bytes())
    sources = {name: json.loads((Path(repo) / s['path']).read_bytes()) for name, s in plan.get('sources', {}).items()}
    validate_plan(plan, sources)
    return plan, sources


def validate_plan(plan, sources):
    """Every structural promise the sitting relies on, refused before anything runs."""
    problems = []
    if plan.get('schema') != SCHEMA:
        problems.append(f'plan schema is {plan.get("schema")!r}, not {SCHEMA}')
    if plan.get('sitting') not in SITTINGS:
        problems.append(f'plan names sitting {plan.get("sitting")!r}')
    for name, s in (plan.get('sources') or {}).items():
        if not isinstance(s, dict) or not SHA.match(str(s.get('sha256'))) or not s.get('path'):
            problems.append(f'source {name} needs a repo-relative path and a full sha256')
    passes = plan.get('passes') or []
    if not passes:
        problems.append('the plan declares no pass')
    names = [p.get('name') for p in passes]
    if len(set(names)) != len(names) or not all(isinstance(n, str) and re.match(r'^[\w.+-]+$', n) for n in names):
        problems.append('pass names must be unique words ([A-Za-z0-9_.+-])')
    for p in passes:
        problems += [f'{p.get("name")}: {m}' for m in pass_problems(p, sources)]
    if problems:
        raise ValueError('the sitting plan is refused: ' + '; '.join(problems))


def pass_problems(p, sources):
    out = []
    kind = p.get('kind')
    if kind not in KINDS:
        return [f'kind {kind!r} is neither {" nor ".join(KINDS)}']
    glass, scale, pose = p.get('glass'), p.get('scale'), p.get('pose')
    if not isinstance(glass, (int, float)) or isinstance(glass, bool) or not 0 <= glass <= 1:
        out.append(f'glass {glass!r} is not a slider position in [0, 1]')
    if scale not in MODES:
        out.append(f'scale {scale!r} is not 1 or 2')
    if pose not in POSES:
        out.append(f'pose {pose!r}')
    doc = sources.get(p.get('source'))
    if doc is None:
        return out + [f'source {p.get("source")!r} is not declared']
    declared = {q['key']: q for q in doc['profiles']}
    scene_ids = {s['id'] for s in doc['scenes']}
    if kind == 'dump':
        lists = {p.get('profile'): list(p.get('scenes') or [])}
        if set(p) - DUMP_FIELDS:
            out.append(f'a dump pass carries no {sorted(set(p) - DUMP_FIELDS)}')
        if any(not s.endswith('__rest') for s in lists[p.get('profile')]):
            out.append('dump-layers refuses non-rest ids in either pose; a receded pass dumps the __rest twin')
    else:
        lists = {k: list(v) for k, v in (p.get('profiles') or {}).items()}
        extra = p.get('run1Only') or {}
        for k, v in extra.items():
            if k not in lists:
                out.append(f'run1Only names profile {k}, which the pass does not capture')
            elif set(v) & set(lists[k]):
                out.append(f'run1Only repeats cells every run already captures in {k}')
        if not isinstance(p.get('runs'), int) or isinstance(p.get('runs'), bool) or p['runs'] < 1:
            out.append(f'runs {p.get("runs")!r}')
        if p.get('protocol') not in PROTOCOLS:
            out.append(f'protocol {p.get("protocol")!r}')
        if p.get('publish'):
            # materialize votes per cell across runs that must have read ONE declaration
            # (run-provenance rule 6), so a published pass captures the same cells every run.
            if extra:
                out.append('a published pass captures the same cells in every run (no run1Only)')
            if not isinstance(p.get('runs'), int) or p['runs'] < 2:
                out.append('a published pass needs at least two runs for materialize')
        for cell, shas in (p.get('expect') or {}).items():
            k, _, sid = cell.partition('/')
            if sid not in lists.get(k, []) + list(extra.get(k, [])):
                out.append(f'expect names {cell}, which the pass does not capture')
            if not shas or not all(SHA.match(str(s)) for s in shas):
                out.append(f'expect for {cell} needs full sha256 frame digests')
        for k, v in extra.items():
            if k in lists:
                lists[k] = lists[k] + list(v)
    if not lists or not any(lists.values()):
        out.append('the pass captures nothing')
    for key, ids in lists.items():
        parsed = parse_key(str(key))
        if parsed is None:
            out.append(f'{key} is not a macOS 27 profile key with a glass token')
            continue
        if key not in declared:
            out.append(f'{key} is not a profile of source {p.get("source")}')
            continue
        k_scale, k_scheme, _, k_glass = parsed
        if k_scale != scale:
            out.append(f'{key} states {k_scale}x and the pass is {scale}x')
        if isinstance(glass, (int, float)) and k_glass != glass:
            out.append(f'{key} names slider {k_glass} and the pass sets {glass} (X6)')
        if declared[key].get('colorScheme') != k_scheme:
            out.append(f'{key} declares colorScheme {declared[key].get("colorScheme")}')
        if len(set(ids)) != len(ids):
            out.append(f'{key} lists a scene twice')
        unknown = sorted(set(ids) - scene_ids)
        if unknown:
            out.append(f'{key} names undeclared scenes {unknown[:3]}')
        unlisted = sorted(set(ids) - set(declared[key]['scenes']))
        if unlisted:
            out.append(f'{key} does not list {unlisted[:3]}')
        if kind == 'capture':
            wrong = [s for s in ids if receded_id(s) != (pose == 'receded')]
            if wrong:
                out.append(f'{key}: {len(wrong)} scene(s) state the other pose, e.g. {wrong[0]}')
    return out


def pass_order(plan):
    """Every pass of the sitting in its one declared order, with rank and display mode."""
    order = []
    for i, p in enumerate(plan['passes']):
        q = dict(p)
        q['rank'] = i
        q['mode'] = MODES[p['scale']]
        q['runs'] = 1 if p['kind'] == 'dump' else p['runs']
        order.append(q)
    return order


def pass_of(name, plan):
    found = [p for p in pass_order(plan) if p['name'] == name]
    if not found:
        raise ValueError('undeclared pass ' + name)
    return found[0]


def scheme_of(key):
    return parse_key(key)[1]


def subset(spec, lists):
    """The scenes document restricted to `lists` ({profile key: ids}), roles preserved: one
    profile entry per key with exactly its ids, and only the backgrounds and components used."""
    wanted = {s for ids in lists.values() for s in ids}
    missing = sorted(wanted - {s['id'] for s in spec['scenes']})
    if missing:
        raise ValueError('derived document names undeclared scenes: ' + ', '.join(missing[:5]))
    doc = copy.deepcopy(spec)
    doc['scenes'] = [s for s in doc['scenes'] if s['id'] in wanted]
    used_bg = {s['background'] for s in doc['scenes']}
    used_c = {s['component'] for s in doc['scenes']}
    doc['backgrounds'] = {k: v for k, v in doc['backgrounds'].items() if k in used_bg}
    doc['components'] = {k: v for k, v in doc['components'].items() if k in used_c}
    declared = {p['key']: p for p in spec['profiles']}
    doc['profiles'] = [dict(key=k, colorScheme=declared[k]['colorScheme'], a11y=declared[k]['a11y'],
                            scenes=sorted(ids)) for k, ids in sorted(lists.items()) if ids]
    doc['split'] = {role: sorted(s for s in doc['split'].get(role, []) if s in wanted) for role in SPLIT_ROLES}
    doc['$comment'] = ['W43 sitting: a derived pass document (bed/sitting/pass-spec.py) over a declared',
                       'scenes file; never edited by hand.']
    return doc


def capture_lists(p, run):
    lists = {k: sorted(v) for k, v in p['profiles'].items()}
    if run == 1:
        for k, v in (p.get('run1Only') or {}).items():
            lists[k] = sorted(lists.get(k, []) + list(v))
    return lists


def derive_from(plan, sources, name, run=1):
    """The scenes document the harness captures for run `run` of capture pass `name`."""
    p = pass_of(name, plan)
    if p['kind'] != 'capture':
        raise ValueError(f'{name} is a {p["kind"]} pass')
    if run not in range(1, p['runs'] + 1):
        raise ValueError(f'run {run} outside 1..{p["runs"]}')
    return subset(sources[p['source']], capture_lists(p, run))


def dump_doc_from(plan, sources, name):
    p = pass_of(name, plan)
    if p['kind'] != 'dump':
        raise ValueError(f'{name} is a {p["kind"]} pass')
    return subset(sources[p['source']], {p['profile']: p['scenes']})


def capture_ids(doc):
    return sorted({s for q in doc['profiles'] for s in q['scenes']})


def cells(doc):
    return [p['key'] + '/' + s for p in doc['profiles'] for s in p['scenes']]


def plan_counts(plan, sources):
    """Per pass and in total: launches, captures (every run's cells), dump scenes, and the slider
    writes and display switches the order implies (counted between passes, from the first)."""
    passes, totals = [], dict(captureLaunches=0, captures=0, dumpLaunches=0, dumpScenes=0, sliderWrites=0,
                              modeSwitches=0, publishedCells=0)
    glass, mode = None, None
    for p in pass_order(plan):
        row = dict(name=p['name'], kind=p['kind'], role=p.get('role'), glass=p['glass'], scale=p['scale'],
                   pose=p['pose'], mode=p['mode'], runs=p['runs'])
        if glass is not None and p['glass'] != glass:
            totals['sliderWrites'] += 1
        if mode is not None and p['mode'] != mode:
            totals['modeSwitches'] += 1
        glass, mode = p['glass'], p['mode']
        if p['kind'] == 'dump':
            row['scenes'] = len(p['scenes'])
            totals['dumpLaunches'] += 1
            totals['dumpScenes'] += len(p['scenes'])
        else:
            per_run = [len(cells(derive_from(plan, sources, p['name'], n))) for n in range(1, p['runs'] + 1)]
            row.update(cellsPerRun=per_run, captures=sum(per_run), protocol=p['protocol'],
                       publish=bool(p.get('publish')))
            totals['captureLaunches'] += p['runs']
            totals['captures'] += sum(per_run)
            if p.get('publish'):
                totals['publishedCells'] += per_run[0]
        passes.append(row)
    return dict(schema='w43-pass-plan-1', sitting=plan['sitting'], passes=passes, totals=totals)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('action', choices=['plan', 'spec', 'order'])
    ap.add_argument('--sitting', required=True, choices=SITTINGS)
    ap.add_argument('--pass', dest='name')
    ap.add_argument('--run', type=int, default=1)
    args = ap.parse_args()
    plan, sources = load(plan_path(args.sitting))
    if args.action == 'order':
        # One line per pass for the orchestrator: name kind mode runs glass.
        for q in pass_order(plan):
            print(q['name'], q['kind'], q['mode'], q['runs'], repr(float(q['glass'])))
        return
    if args.action == 'plan':
        value = plan_counts(plan, sources)
    elif pass_of(args.name, plan)['kind'] == 'dump':
        value = dump_doc_from(plan, sources, args.name)
    else:
        value = derive_from(plan, sources, args.name, args.run)
    print(json.dumps(value, indent=2))


if __name__ == '__main__':
    main()
