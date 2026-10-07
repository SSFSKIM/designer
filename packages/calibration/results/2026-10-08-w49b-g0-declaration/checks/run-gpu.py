#!/usr/bin/env python3.12
"""Run one declared GPU check under the classifying census; never stop foreign processes."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[2]
ROOT = CAL.parents[1]
LOCK = Path('/tmp/w49-gpu.lock')
name, *command = sys.argv[1:]
if not command or not name.replace('-', '').isalnum():
    raise SystemExit('usage: run-gpu.py NAME COMMAND [ARG ...]')
out = Path('/Users/new/vitrea-w49/b-g0-scratch/checks') / name
out.mkdir(parents=True, exist_ok=False)
spec = importlib.util.spec_from_file_location('census',
    CAL / 'results/2026-10-02-w43-g3-refit/stage/census.py')
census = importlib.util.module_from_spec(spec)
spec.loader.exec_module(census)
LOCK.mkdir()
try:
    observation = census.observe()
    (out / 'census.json').write_text(json.dumps(observation, indent=2) + '\n')
    if not observation['passes']:
        raise SystemExit(f'Census refused: {observation["refusals"]}; see {out}')
    (out / 'request.json').write_text(json.dumps(dict(command=command, cwd=str(ROOT)), indent=2) + '\n')
    env = {k: v for k, v in os.environ.items() if not k.startswith('VITREA_')}
    with (out / 'output.txt').open('w') as log:
        result = subprocess.run(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
    (out / 'exit.json').write_text(json.dumps(dict(exitCode=result.returncode)) + '\n')
    print(f'{name}: exit {result.returncode}; {out}', flush=True)
    print((out / 'output.txt').read_text()[-8000:])
    raise SystemExit(result.returncode)
finally:
    LOCK.rmdir()
