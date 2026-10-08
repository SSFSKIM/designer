#!/Users/new/vitrea-w49/py/bin/python -I
"""Bound W50 candidate renderer with a stdlib-only, source-only bootstrap.

Planning has no side effects. Gate and exposure execution need the operational root plus
its authorised pre-fit web contract before any helper executes. Strict current reads belong
to a separate pre-fit instrument, not this live-chart candidate API.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
CONTRACT = HERE / 'execution-contract.json'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    # The caller checks source hashes first; never execute a stale repository .pyc.
    exec(compile(path.read_bytes(), str(path), 'exec'), result.__dict__)
    return result


def pinned(root, relative, digest):
    path = (root / relative).resolve()
    if not path.is_relative_to(root) or not path.is_file() or sha(path) != digest:
        raise ValueError(f'Changed closure source: {relative}')
    return path


def sealed_json(path):
    if Path(str(path) + '.sha256').is_file():
        sidecar = Path(str(path) + '.sha256')
    else:
        sidecar = path.with_suffix('.sha256')
    if sidecar.read_text() != f'{sha(path)}  {path.name}\n':
        raise ValueError(f'Changed prospective seal: {path.name}')
    return json.loads(path.read_text())


def bootstrap(root, execute):
    """Check trusted bytes without running any repository helper, including the guard."""
    doc = sealed_json(CONTRACT)
    if execute:
        parts = [sealed_json(HERE.parent / f'{part}.json')
                 for part in ('declaration', 'fit-declaration')]
        if parts[1].get('partOneSha256') != sha(HERE.parent / 'declaration.json'):
            raise ValueError('Root part two names another part one')
        for part in parts:
            for pin in part['sources']:
                pinned(root, pin['path'], pin['sha256'])
        evidence = sealed_json(HERE.parent / 'pre-fit-evidence.json')
        if evidence.get('partTwoSha256') != sha(HERE.parent / 'fit-declaration.json'):
            raise ValueError('Pre-fit evidence names another root')
        pins = {p['path']: p['sha256'] for p in evidence.get('sources', [])}
        for path in (CONTRACT, Path(str(CONTRACT) + '.sha256')):
            relative = str(path.relative_to(root))
            if relative not in pins:
                raise ValueError('Web contract is not authorised by the pre-fit source seal')
            pinned(root, relative, pins[relative])
    expected = dict(doc['closure']['sources'])
    for relative, digest in expected.items():
        pinned(root, relative, digest)
    for name in ('next_wave.py', 'closure.py'):
        relative = str((HERE / name).relative_to(root))
        pinned(root, relative, doc['guardSources'][name])
        expected[relative] = doc['guardSources'][name]
    # closure.py imports only stdlib. Its hash was just checked, and it installs a permanent
    # source-only gate before the first next_wave/planner/measurement import is executed.
    closure = module(HERE / 'closure.py', 'w50_bootstrap_closure')
    closure.enforce(root, expected)
    return module(HERE / 'next_wave.py', 'w50_registered_execution')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('batch', type=Path)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    root = Path(subprocess.check_output(['git', '-C', str(HERE), 'rev-parse', '--show-toplevel'],
                                       text=True).strip()).resolve()
    guard = bootstrap(root, args.execute)
    doc, registered, renderer = guard.verify(CONTRACT, root, args.batch)
    if renderer != Path(__file__).resolve():
        raise ValueError('Contract registers another renderer')
    batch = json.loads(registered.read_text())
    planner = module(HERE / 'planner.py', 'w50_planner')
    plan = planner.plan(batch)
    if not args.execute:
        print(json.dumps(plan, indent=2))
        return
    declaration = module(HERE.parent / 'declare.py', 'w50_declaration')
    declaration.verify(phase='fit')
    if not args.out:
        raise ValueError('Execution needs an explicit scratch output root')
    runner = module(HERE / 'runner.py', 'w50_runner')
    runner.execute(plan, args.out, root, registered)


if __name__ == '__main__':
    main()
