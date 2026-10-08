#!/Users/new/vitrea-w49/py/bin/python -I
"""Next-wave renderer entrypoint pattern: bind before planning, even on direct invocation.

Copy with next_wave.py/closure.py into the next wave's tools. Its prospective ROOT declaration
pins execution-contract.json and execution-contract.json.sha256. The fixed contract pathname
is part of the renderer, not a caller option. This executable example is CPU plan-only; replace
only the final planning/output block with that wave's authorised launcher, keeping the binding.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
CONTRACT = HERE / 'execution-contract.json'
spec = importlib.util.spec_from_file_location('registered_execution', HERE / 'next_wave.py')
N = importlib.util.module_from_spec(spec)
spec.loader.exec_module(N)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('batch', type=Path)
    args = parser.parse_args()
    root = Path(subprocess.check_output(['git', '-C', str(HERE), 'rev-parse', '--show-toplevel'],
                                        text=True).strip())
    doc, registered, renderer = N.verify(CONTRACT, root, args.batch)
    if renderer != Path(__file__).resolve():
        raise ValueError('Contract registers another renderer')
    N.K.enforce(root, doc['closure']['sources'])
    # No caller-defined domain reaches the planner. Renderers use registered, never args.batch.
    batch = json.loads(registered.read_text())
    print(json.dumps({'status': 'BOUND_PLAN_ONLY', 'batchSha256': doc['batch']['sha256'],
                      'points': batch['points']}))


if __name__ == '__main__':
    main()
