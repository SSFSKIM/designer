#!/usr/bin/env python3.12
"""W43 G1b: replay the archive of record with every raw input denied (charter clause 5; X24).

replay-denied.py <fetched archive root> --out <dir>

The sitting's worktree is itself under ~/vitrea-w43, so the whole directory cannot be denied as
W42 G1 denied ~/vitrea-w42: the tool would refuse its own imports. Every other path under it that
holds a sitting input or a product of one is denied instead, through w43_archive.deny (the same
audit hook `replay --deny-raw-root` installs): the raw root, the producer's output, the packed
asset's directory, the second copy, the stop evidence and the pre-launch reads. A control first
proves the hook refuses an open under the raw root and the producer's output, and that the
fetched cache stays readable; then the replay recomputes every statistic from the archived bytes.
"""
import argparse
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE.parents[1] / '2026-10-01-w43-g0-declaration/bed/sitting/w43_archive.py'
W43 = Path.home() / 'vitrea-w43'
DENIED = [W43 / 'g1b-run', W43 / 'g1b-archive', W43 / 'g1b-release', W43 / 'archive-copy-g1b',
          W43 / 'g1b-stops', W43 / 'g1b-prelaunch', W43 / 'g1b-restore']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('root', type=Path)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    spec = importlib.util.spec_from_file_location('w43_archive', TOOL)
    A = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(A)
    for d in DENIED:
        A.deny(d)
    control = []
    for probe in (W43 / 'g1b-run/pose-check/run-1/admission.json', W43 / 'g1b-archive/inventory.json'):
        try:
            probe.read_bytes()
            control.append(f'NOT REFUSED: {probe}')
        except PermissionError as err:
            control.append(f'refused as designed: {err}')
    control.append(f'cache readable: {(args.root / "inventory.json").is_file() and bool((args.root / "inventory.json").read_bytes())}')
    result = A.replay(args.root)
    summary = {k: v for k, v in result.items() if k != 'outputs'}
    summary['denied'] = [str(d) for d in DENIED]
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / 'deny-control.txt').write_text('\n'.join(control) + '\n')
    (args.out / 'replay-archive.json').write_text(json.dumps(summary, indent=2) + '\n')
    print('\n'.join(control))
    print(json.dumps(summary, indent=2))
    if not result['identical'] or any(not line.startswith(('refused', 'cache readable: True')) for line in control):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
