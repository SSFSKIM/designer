#!/usr/bin/env python3.12
"""W41 G2 canonical light read through W40's declared stage (c9a §5.193; CLAUDE.md recipe).

  read.py declare <stage>            matrix stage: the four light profiles, both tiers,
                                     calibration,validation,holdout,recorded,probe, the
                                     sealed light document pair. No capture.
  read.py measure <stage> <tier>     calibration,validation,recorded,probe, one compare
                                     process per profile, a fresh X6 before each launch.
  read.py holdout <stage> <tier>     holdout, once per tier, only after the configuration
                                     log's last record names this exact configuration.

Every launch is logged (runs.jsonl beside this file). A pass writes an exclusive start
marker and never re-launches a started (profile, tier, pass) whose completion is absent:
that is a stop. --write-partial keeps successful rows in scratch and still exits 1;
missing cells are then re-measured by `measure ... --scene` under a new, logged launch.
Captures land in this worktree's packages/calibration/web-captures (gitignored), the tree
that is copied to the canonical path when the read lands.
"""
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[2]
G2 = HERE.parent
PROFILES = ['apple-macos-27.0-1x-light-standard-glass0.5',
            'apple-macos-27.0-2x-light-standard-glass0.5',
            'apple-macos-27.0-1x-light-reduced-transparency-glass0.5',
            'apple-macos-27.0-1x-light-increased-contrast-coupled-glass0.5']
ACTIVE = 'profiles/apple-macos-27.0-1x-light-standard-glass0.5.json'
RECEDED = 'profiles/apple-macos-27.0-1x-light-standard-glass0.5-receded.json'
MEASURED = 'calibration,validation,recorded,probe'

spec = importlib.util.spec_from_file_location(
    'w41_x6', CAL / 'results/2026-09-27-w41-g1-identification/x6/observe.py')
x6 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(x6)


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def log(row):
    with (HERE / 'runs.jsonl').open('a') as f:
        f.write(json.dumps(row, sort_keys=True) + '\n')


def sealed_documents():
    manifest = json.loads((G2 / 'sealed-manifest.json').read_text())
    entry = manifest['documents']['apple-macos-27.0-1x-light-standard-glass0.5-receded.json']
    assert hashlib.sha256((CAL / RECEDED).read_bytes()).hexdigest() == entry['fileSha256']
    return entry


def run(argv, label):
    observation = x6.observe()
    verdict = observation['verdict']
    log(dict(label=label, at=observation['recordedAt'], x6=verdict,
             foreign=[p[2][:160] for p in observation['foreignProcesses']]))
    if not verdict['passes']:
        print('X6 REFUSED', label, verdict['refusals'], flush=True)
        sys.exit(3)
    env = {k: v for k, v in os.environ.items() if not k.startswith('VITREA_')}
    env.update(VITREA_WEB_CAPTURES=str(CAL / 'web-captures'), VITREA_SCENE_SERVER_PORT='5197')
    started = now()
    with (HERE / 'logs').joinpath(label.replace('/', '__') + '.txt').open('x') as out:
        result = subprocess.run(argv, cwd=CAL, env=env, stdout=out, stderr=subprocess.STDOUT)
    log(dict(label=label, started=started, completed=now(), exitCode=result.returncode,
             argv=argv))
    print(label, 'exit', result.returncode, flush=True)
    return result.returncode


def main():
    mode, stage = sys.argv[1], Path(sys.argv[2]).resolve()
    sealed_documents()
    (HERE / 'logs').mkdir(exist_ok=True)
    if mode == 'declare':
        argv = ['pnpm', 'run', '-s', 'matrix', '--', 'stage', str(stage), '--profile',
                ','.join(PROFILES), '--renderer', 'webgpu,css',
                '--set', 'calibration,validation,holdout,recorded,probe',
                '--material-profile', ACTIVE, '--receded-profile', RECEDED]
        result = subprocess.run(argv, cwd=CAL)
        log(dict(label='declare', at=now(), argv=argv, exitCode=result.returncode))
        sys.exit(result.returncode)
    tier = sys.argv[3]
    extra = sys.argv[4:]
    if mode == 'holdout':
        configuration = importlib.util.spec_from_file_location(
            'w41_configuration', CAL / 'results/holdout-configuration/configuration.py')
        conf = importlib.util.module_from_spec(configuration)
        configuration.loader.exec_module(conf)
        last = conf.load_log()[-1]
        assert last['claims'] == 'c9a §5.193', last['claims']
        assert last['documents'] == conf.document_hashes()
        assert last['sourceSha256'] == conf.source_hash()[0]
        committed = subprocess.check_output(
            ['git', 'show', 'HEAD:packages/calibration/results/holdout-configuration/'
             'configuration-log.json'], cwd=CAL)
        assert json.loads(committed)['reads'][-1] == last, 'configuration record not committed'
        sets = 'holdout'
    elif mode == 'measure':
        sets = MEASURED
    else:
        raise SystemExit('mode: declare | measure | holdout')
    tag = '-'.join(x.replace(',', '+') for x in extra) if extra else 'all'
    for profile in PROFILES:
        label = f'{mode}/{tier}/{profile}/{tag}'
        marker = HERE / 'logs' / (label.replace('/', '__') + '.started')
        if marker.exists():
            done = [json.loads(l) for l in (HERE / 'runs.jsonl').read_text().splitlines()]
            if any(r.get('label') == label and 'exitCode' in r for r in done):
                continue
            raise SystemExit('started pass without completion is a stop: ' + label)
        argv = ['pnpm', 'run', '-s', 'compare', '--', '--stage', str(stage), '--profile', profile,
                '--renderer', tier, '--material-profile', ACTIVE, '--receded-profile', RECEDED,
                '--set', sets, '--alpha', '--write-partial', *extra]
        marker.write_text(now() + '\n')
        code = run(argv, label)
        if code not in (0, 1):
            raise SystemExit(f'{label}: exit {code}; stop')


if __name__ == '__main__':
    main()
