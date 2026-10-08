"""Scratch-only unchanged-document controls, never candidate fitting or publication."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[2]
ROOT = CAL.parents[1]
SCENES = ['dark-solid__rrect-md__rest', 'dark-solid__rrect-md__inactive',
          'impulse__rrect-ml__rest', 'impulse__rrect-ml__inactive',
          'impulse__rrect-lg__rest', 'impulse__rrect-lg__inactive',
          'checkerboard-4__rrect-md__rest']


def main():
    out = Path(sys.argv[1]).resolve()
    renderer = sys.argv[2] if len(sys.argv) > 2 else 'webgpu'
    if renderer not in ('webgpu', 'css'):
        raise ValueError('Identity controls require an explicit supported renderer')
    if out.exists() or out == CAL or CAL in out.parents:
        raise ValueError('Require a fresh scratch root outside the calibration tree')
    out.mkdir(parents=True)
    spec = importlib.util.spec_from_file_location('w43_census',
        CAL / 'results/2026-10-02-w43-g3-refit/stage/census.py')
    census = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(census)
    for position in ('0.25', '0.5'):
        active = CAL / f'profiles/apple-macos-27.0-1x-dark-standard-glass{position}.json'
        receded = active.with_name(active.stem + '-receded.json')
        for scale in (1, 2):
            dest = out / f'{position}-{scale}x'
            dest.mkdir()
            observed = census.observe()
            (dest / 'census.json').write_text(json.dumps(observed, indent=2) + '\n')
            if not observed['passes']:
                raise ValueError(f'Census refuses: {observed["refusals"]}')
            argv = ['pnpm', 'run', '-s', 'compare', '--', '--profile',
                f'apple-macos-27.0-{scale}x-dark-standard-glass{position}',
                '--renderer', renderer, '--material-profile', str(active),
                '--receded-profile', str(receded), '--set', 'calibration,validation,recorded,probe',
                '--scene', ','.join(SCENES), '--write-partial', '--alpha',
                '--out-matrix', str(dest / 'matrix.json')]
            env = {k: v for k, v in os.environ.items() if not k.startswith('VITREA_')}
            env['VITREA_WEB_CAPTURES'] = str(dest / 'web-captures')
            (dest / 'request.json').write_text(json.dumps(argv, indent=2) + '\n')
            with (dest / 'render.log').open('w') as log:
                result = subprocess.run(argv, cwd=CAL, env=env, stdout=log, stderr=subprocess.STDOUT)
            (dest / 'exit.json').write_text(json.dumps({'exitCode': result.returncode}) + '\n')
            print(position, scale, 'exit', result.returncode, flush=True)
            if result.returncode:
                raise SystemExit(result.returncode)


if __name__ == '__main__':
    main()
