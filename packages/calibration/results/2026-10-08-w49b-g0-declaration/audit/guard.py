#!/Users/new/vitrea-w49/py/bin/python -I
"""Bind future uses of the frozen G0 launcher to its one registered identification batch.

Default is plan-only. --execute delegates to the unchanged tool after provenance checks; it
adds no labels, points, rungs, fit domain, native capture, selection or publication pathway.
This wrapper does not retroactively prove that the already-running job used it.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('w49b_guard_audit', HERE / 'audit.py')
A = importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--batch', type=Path, default=HERE.parent / 'batches/identification.json')
    parser.add_argument('--candidates', type=Path, required=True)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    A.K.environment()
    c = A.contract()
    A.bound_batch(c, args.batch)
    A.discover(A.ROOT, HERE / 'instrument_probe.py', commit=A.SEAL)
    A.audit_candidates(c, args.candidates)
    A.verify_runtime_candidates(c, args.candidates)
    if not args.execute:
        print(json.dumps({'status': 'PRELAUNCH_BOUND', 'sealCommit': A.SEAL,
                          'plan': c['plan']}, indent=2))
        return
    if not args.out:
        parser.error('--execute requires --out')
    env = {**os.environ, 'PATH': f'{A.K.PYTHON.parent}{os.pathsep}{os.environ.get("PATH", "")}'}
    subprocess.run([str(A.K.PYTHON), '-I', '-B', str(c['directory'] / 'tools/render.py'),
                    str(c['batchPath']), '--candidates', str(args.candidates.resolve()),
                    '--out', str(args.out.resolve()), '--execute'],
                   cwd=c['L'].C.CAL, env=env, check=True)


if __name__ == '__main__':
    main()
