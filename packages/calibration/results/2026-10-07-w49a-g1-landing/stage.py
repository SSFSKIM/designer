"""W49a strict-mode stage and read 9, a prediction check under Decision Logs 6 and 9.

Run declare, measure, then exposure once. Every browser launch uses G0's classifying
census and browser pin, with a new landing log. Referees are withheld with holdout.
A started pass without a successful completion is a stop, never an automatic retry.
"""
from pathlib import Path
import datetime
import gzip
import importlib.util
import json
import os
import subprocess
import sys

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[1]
ROOT = CAL.parents[1]
G0 = HERE.parent / '2026-10-07-w49a-g0-declaration'
sys.path.insert(0, str(G0 / 'probes'))
import probe
probe.HERE = HERE
STAGE = Path.home() / 'vitrea-w49/w49a-stage-dark'
PROFILES = list(probe.R.PROFILES.values())
ACTIVE = 'profiles/apple-macos-27.0-1x-dark-standard-glass0.25.json'
RECEDED = 'profiles/apple-macos-27.0-1x-dark-standard-glass0.25-receded.json'
SETS = 'calibration,validation,holdout,recorded,probe'
LOGS = HERE / 'stage'
LOGS.mkdir(exist_ok=True)


def run(label, args, browser=False):
    marker = LOGS / (label + '.started')
    if marker.exists():
        raise SystemExit(f'{label}: already started; inspect the recorded outcome before any retry')
    lock = Path('/tmp/w49-gpu.lock')
    if browser:
        lock.mkdir()
    try:
        if browser and not probe.census(label):
            raise SystemExit('classifying census refused; no render launched')
        marker.write_text(datetime.datetime.now(datetime.timezone.utc).isoformat()+'\n')
        env = {k:v for k,v in os.environ.items() if not k.startswith('VITREA_')}
        env['VITREA_WEB_CAPTURES'] = str(STAGE / 'web-captures')
        with (LOGS / (label+'.txt')).open('w') as out:
            got = subprocess.run(['pnpm','run','-s',*args], cwd=CAL, env=env, stdout=out, stderr=subprocess.STDOUT)
        with (LOGS/'runs.jsonl').open('a') as out:
            out.write(json.dumps(dict(label=label, args=args, exitCode=got.returncode))+'\n')
        print(label, 'exit', got.returncode, flush=True)
        if got.returncode:
            raise SystemExit(got.returncode)
    finally:
        if browser:
            lock.rmdir()


def main():
    verb = sys.argv[1]
    docs = ['--material-profile', ACTIVE, '--receded-profile', RECEDED]
    if verb == 'declare':
        run('declare', ['matrix','--','stage',str(STAGE),'--profile',','.join(PROFILES),
                       '--renderer','webgpu,css','--set',SETS,*docs])
        return
    if verb not in ('measure','exposure'):
        raise SystemExit('declare | measure | exposure')
    manifest = json.loads((ROOT/'apps/reference-apple/scenes.json').read_text())
    holdout = set(manifest['split']['holdout'])
    cells = probe.R.b2d074_cells()
    for tier in ('webgpu','css'):
        for scale, profile in probe.R.PROFILES.items():
            declared = next(p['scenes'] for p in manifest['profiles'] if p['key']==profile)
            referees = {s for (sc,s),c in cells.items() if sc==scale and c['partition']=='referee'}
            withheld = holdout | referees
            scenes = sorted(s for s in declared if (s in withheld)==(verb=='exposure'))
            sets = SETS if verb=='exposure' else 'calibration,validation,recorded,probe'
            run(f'{verb}-{tier}-{scale}x', ['compare','--','--stage',str(STAGE),'--profile',profile,
                '--renderer',tier,'--set',sets,'--scene',','.join(scenes),*docs,'--alpha','--write-partial'], True)

if __name__ == '__main__':
    main()
