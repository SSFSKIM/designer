"""Record each close check's own exit code, with a census and free-port check for browsers.

Usage: run.py LABEL [--browser PORT] -- COMMAND ...
The command runs from the repository root. Existing logs are never overwritten; a failed
attempt is evidence. There is no retry and no process termination.
"""
from pathlib import Path
import json
import os
import subprocess
import sys

HERE = Path(__file__).resolve().parent
LANDING = HERE.parent
CAL = LANDING.parents[1]
ROOT = CAL.parents[1]
sys.path.insert(0, str(LANDING.parent / '2026-10-07-w49a-g0-declaration/probes'))
import probe
probe.HERE = HERE


def main():
    args = sys.argv[1:]
    label = args[0]
    split = args.index('--')
    command = args[split+1:]
    options = args[1:split]
    browser = '--browser' in options
    log = HERE / (label + '.txt')
    if log.exists():
        raise SystemExit(f'{log} exists; preserve the previous attempt and use another label')
    lock = Path('/tmp/w49-gpu.lock')
    if browser:
        port = options[options.index('--browser')+1]
        held = subprocess.run(['lsof','-nP',f'-iTCP:{port}','-sTCP:LISTEN'], capture_output=True,text=True)
        if held.returncode == 0:
            raise SystemExit(f'port {port} is held; no browser launched\n{held.stdout}')
        lock.mkdir()
    try:
        if browser and not probe.census(label):
            raise SystemExit('classifying census refused; no browser launched')
        load = subprocess.run(['sysctl','-n','vm.loadavg'],capture_output=True,text=True).stdout.strip()
        env = dict(os.environ, VITREA_WEB_CAPTURES='/Users/new/Developer/GitHub/designer/packages/calibration/web-captures')
        with log.open('w') as out:
            out.write(f'command: {command!r}\nload before: {load}\n')
            out.flush()
            got = subprocess.run(command,cwd=ROOT,env=env,stdout=out,stderr=subprocess.STDOUT)
            out.write(f'\nexit code: {got.returncode}\n')
        with (HERE/'close-checks.txt').open('a') as out:
            out.write(f'{label}: {command!r}; exit {got.returncode}; load {load}\n')
        print(f'{label}: exit {got.returncode}',flush=True)
        return got.returncode
    finally:
        if browser:
            lock.rmdir()

if __name__ == '__main__':
    sys.exit(main())
