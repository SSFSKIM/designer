"""Prospective DL5s sealing, only after exact-source reviewer-high clearance.

    python -I -B attempt2_seal.py discover
    python -I -B attempt2_seal.py seal
    python -I -B attempt2_run.py preflight

The preflight emits its canonical proof on stdout and makes NO file. Preserve that successful
stdout as analysis-2-attempt-2.preflight.json before run; run reruns the identical complete plan
and compares the entire proof. No command here re-seals any original instrument.
"""
import argparse
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent


def source(path, name):
    module = types.ModuleType(name); module.__file__ = str(path); sys.modules[name] = module
    exec(compile(Path(path).read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


A = source(HERE/'attempt2_authority.py', 'w50_attempt2_seal_authority')
S = source(HERE/'seal.py', 'w50_attempt2_original_seal')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('discover', 'seal'))
    args = parser.parse_args()
    A.review()
    root, contract, batch, manifest, amended, held = A.OLD.metadata()
    binding = A.preservation()
    guard = source(A.FIT/'live-execution/guard.py', 'w50_attempt2_seal_guard')
    closure = guard.discover(A.REPO, HERE/'attempt2_probe.py', A.closure_sources(amended))
    if closure['environment'] != root['closure']['environment']:
        raise ValueError('Historical interpreter/environment changed')
    if args.operation == 'seal':
        for path in (A.OUTPUT, A.NEW_MARKER.parent, A.PREFLIGHT,
                     HERE/'analysis-2-attempt-2.failed', Path(str(A.CONTRACT_PATH)+'.started.json')):
            if A.OLD.W.os.path.lexists(path): raise ValueError('Attempt 2 namespace already used')
        S.write_sealed(A.AUTHORITY_PATH,
                       A.authority_document(root, amended, held, closure, binding))
        view_pin = S.write_sealed(A.VIEW_PATH, A.successor_view(root, amended))
        S.write_sealed(A.CONTRACT_PATH, A.successor_contract(contract, view_pin))
        A.verify_seal()
    print(A.W.encode({'status': 'SEALED' if args.operation == 'seal' else 'DISCOVERED',
        'analysis': 2, 'attempt': 2, 'sources': len(closure['sources'])}).decode(), end='')


if __name__ == '__main__': main()
