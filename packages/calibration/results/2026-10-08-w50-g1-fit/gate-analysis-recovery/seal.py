"""Discover and seal DL5r successor sources BEFORE the one analytical invocation.

    /Users/new/vitrea-w49/py/bin/python -I -B <this-file> discover
    /Users/new/vitrea-w49/py/bin/python -I -B <this-file> seal

Both operations are source/authority-metadata only. They hash the 634 originals but never
parse their payloads. Discovery executes the original source-only composite probe plus this
adapter, with a permanent allowlisted import guard. `seal` writes the separate authority,
labelled successor root view and analysis-only contract exclusively. It never creates an
analysis marker, capture authority/batch, exposure authority/batch or numerical result.
"""
import argparse
import os
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent


def source(path, name):
    m = types.ModuleType(name); m.__file__ = str(path); sys.modules[name] = m
    exec(compile(Path(path).read_bytes(), str(path), 'exec', dont_inherit=True), m.__dict__)
    return m


A = source(HERE/'authority.py', 'w50_analysis2_seal_authority')
W = A.W


def write_sealed(path, value):
    item = W.write_once(path, value)
    side = Path(str(path)+'.sha256')
    with side.open('x') as stream:
        stream.write(f'{item["sha256"]}  {Path(path).name}\n'); stream.flush(); os.fsync(stream.fileno())
    fd = os.open(side.parent, os.O_RDONLY)
    try: os.fsync(fd)
    finally: os.close(fd)
    return item


def discover(root, amended):
    guard = source(A.FIT/'live-execution/guard.py', 'w50_analysis2_discovery_guard')
    expected = A.closure_sources(amended)
    closure = guard.discover(A.REPO, HERE/'probe.py', expected)
    if closure['environment'] != root['closure']['environment']:
        raise ValueError('Historical interpreter/environment changed')
    return closure


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('discover', 'seal'))
    args = parser.parse_args()
    root, contract, batch, manifest, amended, held = A.metadata()
    closure = discover(root, amended)
    if args.operation == 'seal':
        if A.NEW_MARKER.exists() or A.OUTPUT.exists(): raise ValueError('Successor already attempted')
        authority = A.authority_document(root, amended, held, closure)
        write_sealed(A.AUTHORITY_PATH, authority)
        view_pin = write_sealed(A.VIEW_PATH, A.successor_view(root, amended, W.pin(A.ROOT)))
        write_sealed(A.CONTRACT_PATH, A.successor_contract(contract, view_pin))
        A.verify_seal()
    print(W.encode({'status': 'SEALED' if args.operation == 'seal' else 'DISCOVERED',
                    'count': len(closure['sources']),
                    'sha256': A.digest(W.encode(closure))}).decode(), end='')


if __name__ == '__main__': main()
