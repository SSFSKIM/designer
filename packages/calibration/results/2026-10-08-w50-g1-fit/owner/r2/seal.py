#!/Users/new/vitrea-w49/py/bin/python -I -B
"""Seal the r2 owner reads: a DL5l reference-evidence recovery after the referee fix 7e621f344.

The superseded reads (owner/*-instrument.json, outputs in /Users/new/vitrea-w50/g1-owner-read)
ran owner/referee.ts before it read an absent L1 mean as the owner test does (DL5m 1). Their
bytes stay as recorded. r2 runs the same three reads through the unchanged owner/run.py: each
instrument is its superseded one with only `request`, `closure` and `output` replaced. The
closure is owner/discover.mjs's fresh output and differs from the superseded one in referee.ts
alone; the inputs, inventory, owner keys, byte witness, Node and Python environment are the
superseded instrument's own pins. Nothing here runs a read.

  seal.py reads DIR OUT
      contracts + prepare requests and instruments in DIR, outputs named under OUT; in the
      repository's owner/r2 it also writes supersedes.json, once.
  seal.py projection DIR OUT CONTRACTS PREPARE
      the project-current-batch request and instrument, pinning the two completed reads.

Every file is write-once. Stdout carries paths and hashes only.
"""
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
OWNER = HERE.parent
CLOSURE = HERE/'source-closure.json'
SUPERSEDED = {mode: OWNER/f'{mode}-instrument.json' for mode in ('contracts', 'prepare', 'projection')}
REPLACED = {'request', 'closure', 'output'}


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def pin(path): return {'path': str(Path(path).resolve()), 'sha256': sha(path)}
def load(path): return json.loads(Path(path).read_bytes())


def write_once(path, value):
    with Path(path).open('xb') as handle:
        handle.write((json.dumps(value, indent=2, allow_nan=False)+'\n').encode())
    return pin(path)


def directory(value):
    path = Path(value)
    if not path.is_absolute() or path.resolve() != path or not path.is_dir():
        raise ValueError('Expected an existing canonical absolute directory: '+value)
    return path


def instrument(mode, request, out, name):
    doc = load(SUPERSEDED[mode])
    doc.update(request=request, closure=pin(CLOSURE), output=str(out/name))
    if set(doc) != set(load(SUPERSEDED[mode])):
        raise ValueError('An r2 instrument keeps its superseded shape')
    return doc


def reads(target, out):
    written = {}
    for mode, name, request in (
            ('contracts', 'contracts.json', load(OWNER/'contracts-request.json')),
            ('prepare', 'prepare.json', load(OWNER/'prepare-request.json'))):
        request_pin = write_once(target/f'{mode}-request.json', request)
        written[mode] = write_once(target/f'{mode}-instrument.json', instrument(mode, request_pin, out, name))
    if target == HERE:
        old = load(OWNER/'source-closure.json')['sources']
        new = load(CLOSURE)['sources']
        moved = sorted(p['path'] for p in new if {'path': p['path'], 'sha256': p['sha256']} not in old)
        if [p['path'] for p in old] != [p['path'] for p in new]:
            raise ValueError('The r2 closure changes source membership')
        write_once(HERE/'supersedes.json', {
            'schema': 'w50-owner-read-supersession-1',
            'ruling': 'DL5l reference-evidence recovery; DL5m item 1 (owner context cells gate)',
            'cause': 'owner/referee.ts classifyCell read an absent L1 mean as undefined, so the eight '
                     'named dark inactive dark-solid WebGPU cells never carried namedExclusion; '
                     'fixed in 7e621f344 to the owner test\'s own reading (absent is null)',
            'superseded': {
                'instruments': {mode: pin(path) for mode, path in SUPERSEDED.items()},
                'requests': {mode: pin(OWNER/f'{mode}-request.json') for mode in SUPERSEDED},
                'closure': pin(OWNER/'source-closure.json'),
                'outputs': {name: pin(Path('/Users/new/vitrea-w50/g1-owner-read')/name)
                            for name in ('contracts.json', 'prepare.json', 'projection.json')},
                'evidence': {name: pin(OWNER/'evidence'/name) for name in
                             ('contracts.json', 'prepare.json', 'projection-index.json', 'projection.json.gz')},
                'status': 'retained unedited; recorded evidence of the pre-fix referee'},
            'closure': {'r2': pin(CLOSURE), 'movedSources': moved},
            'unchanged': 'config, inventory, ownerKeys, inputWitness, node and pythonEnvironment are the '
                         'superseded instruments\' own pins; owner/run.py and the bridge are unchanged',
        })
    print(json.dumps(written, indent=1))


def projection(target, out, contracts, prepare):
    request = load(OWNER/'projection-request.json')
    request.update(completedReferencesPin=pin(prepare), contractsPin=pin(contracts))
    request_pin = write_once(target/'projection-request.json', request)
    written = write_once(target/'projection-instrument.json',
                         instrument('projection', request_pin, out, 'projection.json'))
    print(json.dumps({'projection': written}, indent=1))


if __name__ == '__main__':
    verb, *args = sys.argv[1:]
    if verb == 'reads' and len(args) == 2:
        reads(directory(args[0]), directory(args[1]))
    elif verb == 'projection' and len(args) == 4:
        projection(directory(args[0]), directory(args[1]), Path(args[2]), Path(args[3]))
    else:
        raise SystemExit(__doc__)
