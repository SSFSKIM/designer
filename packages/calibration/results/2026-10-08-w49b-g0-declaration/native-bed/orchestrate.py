#!/usr/bin/env python3.12
"""Run W43's tested restore/census/order machinery through the W49b adapters."""
import argparse
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reuse


def shell_source():
    source = (reuse.W43 / 'sitting-orchestrate.sh').read_text()
    old = 'HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"'
    if source.count(old) != 1:
        raise ValueError('W43 orchestrator binding point changed')
    python = os.environ.get('W49B_PYTHON', sys.executable)
    rebound = source.replace(old, 'HERE=' + shlex.quote(str(HERE))).replace('python3.12', shlex.quote(python))
    return rebound.replace('nothing away from 0.5 is captured, and the run stands admitted as evidence',
                           'the bridge stopped further passes; the run stands admitted as evidence')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--check-shell', action='store_true', help='syntax-check rebound shell, never execute it')
    args = ap.parse_args()
    if args.check_shell:
        subprocess.run(['/bin/bash', '-n'], input=shell_source(), text=True, check=True)
        print('Rebound W43 shell: syntax PASS; not executed')
        return
    reuse.require_capture_approval()
    if any(os.environ.get(k) for k in ('W43_EVIDENCE', 'W43_EVIDENCE_REPO')):
        raise ValueError('W49b collects/archive-releases separately: no automatic evidence commit')
    pin = json.loads((HERE / 'bundle-pin.json').read_bytes())
    if os.environ.get('VITREA_APP', pin['path']) != pin['path']:
        raise ValueError('the app override is not the pinned bundle')
    S = reuse.driver()
    S.pinned_declaration('native')
    # Raw blind captures never land in a world-readable default directory.
    os.umask(0o077)
    env = dict(os.environ, W43_SITTING='native', VITREA_APP=pin['path'])
    os.execve('/bin/bash', ['bash', '-c', shell_source()], env)


if __name__ == '__main__':
    try:
        main()
    except ValueError as error:
        print('W49b: ' + str(error), file=sys.stderr)
        raise SystemExit(2)
