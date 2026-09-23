#!/usr/bin/env python3
"""Run a declared handful of scratch cells, retaining every attempt (§5.174).

No retry on noisy pixels or a lost pose. The three-run construction is three
planned observations, not three successful observations selected from retries.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
SCRATCH = Path.home() / 'vitrea-w34/scratch'
SIDE = Path.home() / 'vitrea-w34/side'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--spec', type=Path, required=True)
    ap.add_argument('--name', required=True)
    ap.add_argument('--scale', type=int, choices=[1, 2], required=True)
    ap.add_argument('--pose', choices=['active', 'inactive'], default='active')
    ap.add_argument('--runs', type=int, default=3)
    ap.add_argument('--initial-settle', type=float, default=1.75)
    ap.add_argument('--seed', type=int)
    args = ap.parse_args()
    root = (SCRATCH / args.name).resolve()
    if SCRATCH.resolve() not in root.parents:
        raise SystemExit('Refused: capture root must be under ~/vitrea-w34/scratch/')
    spec = json.loads(args.spec.read_text())
    for profile in spec['profiles']:
        if not profile['key'].startswith('apple-macos-27.0-') or profile['a11y'] != 'standard':
            raise SystemExit('Refused: scratch declaration is not macOS 27 standard only')
    for n in range(1, args.runs + 1):
        run = root / f'run-{n}'
        if run.exists():
            print('RETAIN existing attempt', run, flush=True)
            continue
        session = json.loads(subprocess.check_output([str(SCRATCH / 'read-session')], text=True))
        print('preflight', session, flush=True)
        if session.get('idleSeconds', 0) < 60 or session.get('screenLocked') is not False:
            raise SystemExit('WAIT: no launch; sixty seconds idle and unlocked session required')
        run.mkdir(parents=True)
        (run / 'session-before.json').write_text(json.dumps(session, indent=2)+'\n')
        (run / 'scenes.json').write_bytes(args.spec.read_bytes())
        env = {**os.environ, 'VITREA_SCALE': str(args.scale),
               'VITREA_SCENES': str(run / 'scenes.json'), 'VITREA_FIXTURES': str(run)}
        def attest(phase):
            with (run / f'attest.{phase}.json').open('w') as f:
                subprocess.run(['python3', str(HERE / 'record-machine.py'),
                                f'{args.name}-run-{n}-{phase}'], stdout=f, check=True)
        attest('open')
        with (run / 'backgrounds.log').open('w') as f:
            subprocess.run([str(SIDE / 'harness'), 'backgrounds'], env=env,
                           stdout=f, stderr=subprocess.STDOUT, check=True)
        command = ['open', '-W']
        for key in ['VITREA_SCALE', 'VITREA_SCENES', 'VITREA_FIXTURES']:
            command += ['--env', key+'='+env[key]]
        command += ['--stdout', str(run/'capture.out'), '--stderr', str(run/'capture.err'),
                    str(SIDE/'VitreaReference.app'), '--args', 'capture',
                    '--run-label', f'w34-g0-{args.name}-{n}', '--reset-interstitial', '6',
                    '--min-idle-seconds', '60', '--initial-settle', str(args.initial_settle),
                    '--scenes', ','.join(s['id'] for s in spec['scenes'])]
        if args.pose == 'inactive': command += ['--inactive']
        if args.seed is not None: command += ['--order-seed', str(args.seed)]
        (run / 'command.json').write_text(json.dumps(command, indent=2)+'\n')
        subprocess.run(command, check=True)
        attest('close')
        if not (run / 'manifest.json').exists():
            print((run/'capture.err').read_text(), flush=True)
            raise SystemExit('REFUSED: no manifest; retained attempt is not retried')
        manifest = json.loads((run/'manifest.json').read_text())
        entries = [f for p in manifest['profiles'] for f in p['fixtures']]
        problems = []
        for f in entries:
            if not f['materialRendered'] or f.get('presentedActive') != (args.pose == 'active'):
                problems.append([f['sceneId'], 'material or pose attestation failed'])
            if f.get('deterministic') is not True:
                problems.append([f['sceneId'], 'immediate repeat did not settle'])
            if args.pose == 'inactive' and (f.get('presentation') or {}).get('observedPose') != 'inactive':
                problems.append([f['sceneId'], 'inactive attestation missing'])
        record = dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                      run=str(run), cells=len(entries), admitted=not problems, problems=problems,
                      manifestSha256=hashlib.sha256((run/'manifest.json').read_bytes()).hexdigest())
        (run/'admission.json').write_text(json.dumps(record, indent=2)+'\n')
        print(json.dumps(record), flush=True)
        dest = HERE / 'scratch-manifests' / args.name / f'run-{n}'
        dest.mkdir(parents=True, exist_ok=True)
        for file in ['manifest.json', 'attest.open.json', 'attest.close.json', 'session-before.json',
                     'command.json', 'admission.json', 'capture.out', 'capture.err']:
            (dest/file).write_bytes((run/file).read_bytes())


if __name__ == '__main__': main()
