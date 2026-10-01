#!/usr/bin/env python3.12
"""The dry plan of a W43 sitting, distilled for the record (G0 (d); derived from W42's, untouched).

    dry-plan-summary.py --sitting g1a|g1b   # `sitting.py plan` (W43_SITTING) over the declared plan
    dry-plan-summary.py --stand-in          # sitting.dry_plan() in-process over stand_in.build()

Either way the dry mode runs into a fresh scratch directory outside the repository and executes
NOTHING (no machine read, no launcher, no harness, no slider write); its plan.json is then
distilled here: each launch argv is replaced by its SHA-256 (the full argv stays in the scratch
plan), and the plan's own SHA-256 is named. Writes dry-plan-<label>.json, dry-plan-<label>.txt and,
for a declared sitting, dry-plan-<label>-stdout.txt. The stand-in's record is a REHEARSAL: its
bridge cells and dump scenes are stand_in.py's picks, not the declaration's.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def distil(plan_walk, plan_sha, label, rehearsal):
    for p in plan_walk['passes']:
        for r in p['runs']:
            r['argvSha256'] = hashlib.sha256(json.dumps(r.pop('argv')).encode()).hexdigest()
    plan_walk['planSha256'] = plan_sha
    plan_walk['rehearsal'] = rehearsal
    lines = [f'W43 {label} dry plan (sitting.py plan): executed nothing; every document and argv was written',
             'under a scratch directory. Per pass: slider position, display mode, runs, cells per run.']
    if rehearsal:
        lines.append('REHEARSAL on the G1a-shaped STAND-IN (stand_in.py), not the declared plan.')
    lines += [f'plan {plan_sha[:12]}', '']
    for p in plan_walk['passes']:
        if p['kind'] == 'dump':
            r = p['runs'][0]
            lines.append(f'{p["name"]:32s} x={p["glass"]:<5g} mode {p["mode"]}  dump      {r["scenes"]:3d} scenes'
                         f'  (timeout {r["timeoutSeconds"]} s)')
        else:
            cells = ' '.join(str(r['cells']) for r in p['runs'])
            lines.append(f'{p["name"]:32s} x={p["glass"]:<5g} mode {p["mode"]}  {len(p["runs"])} runs  cells/run {cells}'
                         f'  {p["runs"][0]["protocol"]}{"  PUBLISHED" if p["publish"] else ""}')
    lines += ['', 'totals: ' + json.dumps(plan_walk['totals'])]
    return plan_walk, '\n'.join(lines) + '\n'


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    which = ap.add_mutually_exclusive_group(required=True)
    which.add_argument('--sitting', choices=('g1a', 'g1b'))
    which.add_argument('--stand-in', action='store_true')
    args = ap.parse_args(argv)
    scratch = Path(tempfile.mkdtemp(prefix='w43-dry-plan-')) / 'plan'
    if args.stand_in:
        S = module('w43_stand_in_dry', HERE / 'stand_in.py')
        D = module('w43_sitting_dry', HERE / 'sitting.py')
        canonical, w42, plan = S.build()
        sources = S.sources_of(plan, canonical, w42)
        D.pass_spec().validate_plan(plan, sources)
        D.dry_plan(plan, sources, out=scratch)
        label, plan_sha, stdout = 'stand-in', hashlib.sha256(S.encode(plan)).hexdigest(), None
    else:
        P = module('w43_pass_spec_dry', HERE / 'pass-spec.py')
        stdout = subprocess.run([sys.executable, str(HERE / 'sitting.py'), 'plan', '--out', str(scratch)],
                                env={**os.environ, 'W43_SITTING': args.sitting}, check=True, capture_output=True,
                                text=True).stdout
        label, plan_sha = args.sitting, hashlib.sha256(P.plan_path(args.sitting).read_bytes()).hexdigest()
    walk, text = distil(json.loads((scratch / 'plan.json').read_text()), plan_sha, label, args.stand_in)
    (HERE / f'dry-plan-{label}.json').write_text(json.dumps(walk, indent=1) + '\n')
    (HERE / f'dry-plan-{label}.txt').write_text(text)
    if stdout is not None:
        (HERE / f'dry-plan-{label}-stdout.txt').write_text(stdout)
    print(text, end='')


if __name__ == '__main__':
    main()
