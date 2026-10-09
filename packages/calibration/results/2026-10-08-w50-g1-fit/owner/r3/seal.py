#!/Users/new/vitrea-w49/py/bin/python -I -B
"""Seal the r3 owner reads: the DL5o port moves two owner closure sources, so the chain moves again.

DL5o (a) changes owner/intrinsic.ts (historical family-keyed X76 entries admitted verbatim as
holds) and owner/witness.ts (the X76 contract names the functions and the exclusion that admit
them). Both are pinned in the owner contracts' readerSources and in the owner source closure, so
the r2 reads (owner/r2/*-instrument.json, outputs in /Users/new/vitrea-w50/g1-owner-read-r2) no
longer describe the closure the live owner runs. Their bytes stay as recorded. r3 runs the same
three reads through the unchanged owner/run.py, exactly as r2 did (DL5l's pattern): each r3
instrument is its r2 one with only `request`, `closure` and `output` replaced; the contracts and
prepare requests are r2's unchanged, the projection request moves only its two read pins. The
closure is owner/discover.mjs's fresh output and differs from r2's in intrinsic.ts and witness.ts
alone. Nothing here runs a read.

  seal.py reads DIR OUT
      contracts + prepare requests and instruments in DIR, outputs named under OUT; in the
      repository's owner/r3 it also writes supersedes.json, once.
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
R2 = OWNER/'r2'
CLOSURE = HERE/'source-closure.json'
SUPERSEDED = {mode: R2/f'{mode}-instrument.json' for mode in ('contracts', 'prepare', 'projection')}
R2_READ = Path('/Users/new/vitrea-w50/g1-owner-read-r2')


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
        raise ValueError('An r3 instrument keeps its superseded shape')
    return doc


def reads(target, out):
    written = {}
    for mode, name in (('contracts', 'contracts.json'), ('prepare', 'prepare.json')):
        request_pin = write_once(target/f'{mode}-request.json', load(R2/f'{mode}-request.json'))
        written[mode] = write_once(target/f'{mode}-instrument.json', instrument(mode, request_pin, out, name))
    if target == HERE:
        old = load(R2/'source-closure.json')['sources']
        new = load(CLOSURE)['sources']
        moved = sorted(p['path'] for p in new if {'path': p['path'], 'sha256': p['sha256']} not in old)
        if [p['path'] for p in old] != [p['path'] for p in new]:
            raise ValueError('The r3 closure changes source membership')
        write_once(HERE/'supersedes.json', {
            'schema': 'w50-owner-read-supersession-1',
            'ruling': 'DL5o (a), recovered in DL5l\'s pattern; DL5m item 5 (X75/X76 records at both positions)',
            'cause': 'owner/intrinsic.ts read the shipped glass-0.5 documents\' family-keyed provenance '
                     'entries as leaf records, so X76 could never read MEASURED at 0.5; DL5o (a) admits a '
                     'historical family-keyed entry verbatim as that family\'s hold when no moved leaf falls '
                     'under it, and owner/witness.ts\'s X76 contract names that admission',
            'superseded': {
                'instruments': {mode: pin(path) for mode, path in SUPERSEDED.items()},
                'requests': {mode: pin(R2/f'{mode}-request.json') for mode in SUPERSEDED},
                'closure': pin(R2/'source-closure.json'),
                'outputs': {name: pin(R2_READ/name) for name in ('contracts.json', 'prepare.json', 'projection.json')},
                'evidence': {name: pin(OWNER/'evidence-r2'/name) for name in
                             ('contracts.json', 'prepare.json', 'projection-index.json', 'projection.json.gz')},
                'status': 'retained unedited; recorded evidence of the pre-DL5o intrinsic port'},
            'closure': {'r3': pin(CLOSURE), 'movedSources': moved},
            'unchanged': 'config, inventory, ownerKeys, inputWitness, node and pythonEnvironment are the '
                         'superseded instruments\' own pins; owner/run.py is unchanged',
        })
    print(json.dumps(written, indent=1))


def projection(target, out, contracts, prepare):
    request = load(R2/'projection-request.json')
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
