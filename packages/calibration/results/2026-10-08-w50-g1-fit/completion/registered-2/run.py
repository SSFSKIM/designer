#!/Users/new/vitrea-w49/py/bin/python -I
"""Register and execute the r2 reference assembly over the composed current analysis.

r2 is completion/registered/run.py with only its own paths changed: the owner projection
index and contracts are owner/evidence-r2's (the DL5l recovery after the referee fix
7e621f344, DL5m 1), the output is /Users/new/vitrea-w50/g1-completion-r2, and `register`
also names the superseded binding in supersedes.json. The validator, assembler and every
other registered input are the superseded binding's. Its original description follows.

`register` writes binding.json once from fixed upstream identities: the G0 inventory and bed
manifest, the composed current analysis and its root, the references-r2 read and its root,
the owner projection index and contracts, the corrected current2 validator, and the exact
DL5b/DL5c key lists derived with the validator's own expressions. `execute` (after the
binding is committed) assembles into a fresh external directory, materializes the planned
content-addressed artifacts once, re-validates the bundle against a deterministic re-assembly
and the strict validator, then writes the completed inventory and the bundle write-once.
Its stdout is metadata only: counts, statuses and hashes, never a statistic.
"""
import collections
import hashlib
import json
import os
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
FIT = HERE.parents[1]
RESULTS = FIT.parent
REPO = RESULTS.parents[2]
G0 = RESULTS/'2026-10-08-w50-g0-declaration'
CURRENT2 = RESULTS/'2026-10-08-w50-g1-current2/execution'
BINDING = HERE/'binding.json'
OUT = Path('/Users/new/vitrea-w50/g1-completion-r2')
SUPERSEDED = FIT/'completion/registered'


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def rel(path): return str(Path(path).resolve().relative_to(REPO))
def pin(path, absolute=False):
    return {'path': str(Path(path).resolve()) if absolute else rel(path), 'sha256': sha(path)}
def load(path): return json.loads(Path(path).read_bytes())
def module(path, name):
    m = types.ModuleType(name); m.__file__ = str(path); sys.modules[name] = m
    exec(compile(Path(path).read_bytes(), str(path), 'exec', dont_inherit=True), m.__dict__); return m


def write_once(path, raw):
    with Path(path).open('xb') as handle:
        handle.write(raw); handle.flush(); os.fsync(handle.fileno())


def register():
    if BINDING.exists(): raise ValueError('Binding already registered')
    original = load(G0/'references.json'); manifest = load(G0/'bed/manifest.json')
    prefit = module(CURRENT2/'prefit.py', 'w50_registration_prefit')
    key = prefit.key
    controls = {(c['profile'], c['scene']) for c in manifest['cells']
                if c.get('family') == 'span' and c.get('span') in (128, 224)
                and c.get('level') in (0, 4, 28, 64) and c.get('background') == f'grey-{c.get("level"):03d}'}
    reported = [list(key(c)) for c in original['cells']
                if (c['profile'], c['scene']) in controls and c['statistic'] in prefit.EXTRA]
    empty_controls = {(c['profile'], c['scene']) for c in manifest['cells']
                      if c.get('family') == 'span' and c.get('pose') == 'receded'
                      and c.get('level') in (0, 4, 28) and c.get('background') == f'grey-{c.get("level"):03d}'
                      and ((c.get('span') == 128 and c.get('role') != 'blind') or
                           (c.get('span') == 224 and c.get('role') == 'blind'))}
    empty = [list(key(c)) for c in original['cells']
             if (c['profile'], c['scene']) in empty_controls and c['statistic'] == 'T1-full-silhouette']
    prefit.validate_exemptions(original, manifest, reported)
    prefit.validate_empty_eligibility(original, manifest, reported, empty)
    contracts = load(FIT/'owner/evidence-r2/contracts.json')
    sources = [FIT/'completion/bound.py', FIT/'completion/assembler.py', CURRENT2/'prefit.py',
               CURRENT2/'native_evidence.py', CURRENT2/'owner_evidence.py', Path(__file__)]
    binding = {
        'original': pin(G0/'references.json'), 'manifest': pin(G0/'bed/manifest.json'),
        'currentAnalysis': pin('/Users/new/vitrea-w50/g1-current-analysis/completed-current.json', True),
        'currentAnalysisRoot': pin(FIT/'current-analysis-composed/instrument-root.json'),
        'canonicalReferences': pin('/Users/new/vitrea-w50/g1-canonical-references-r2/canonical-references.json', True),
        'canonicalReferencesRoot': pin(FIT/'references-r2/instrument-root.json'),
        'ownerIndex': pin(FIT/'owner/evidence-r2/projection-index.json'),
        'ownerContracts': pin(FIT/'owner/evidence-r2/contracts.json'),
        'ownerSource': contracts['ownerSource'], 'validator': pin(CURRENT2/'prefit.py'),
        'sourcePins': {rel(p): sha(p) for p in sources},
        'reportedKeys': reported, 'emptySupportKeys': empty}
    write_once(BINDING, (json.dumps(binding, indent=2, allow_nan=False)+'\n').encode())
    old = load(SUPERSEDED/'binding.json')
    write_once(HERE/'supersedes.json', (json.dumps({
        'schema': 'w50-reference-assembly-supersession-1',
        'ruling': 'DL5l reference-evidence recovery; DL5m item 1 (owner context cells gate)',
        'superseded': {'binding': pin(SUPERSEDED/'binding.json'), 'run': pin(SUPERSEDED/'run.py'),
                       'archive': pin(SUPERSEDED/'evidence/archive.json'),
                       'status': 'retained unedited; its completed inventory is recorded evidence'},
        'changedFields': sorted(k for k in binding if binding[k] != old[k]),
        'owner': 'owner/r2/supersedes.json names the superseded owner reads and evidence',
    }, indent=2, allow_nan=False)+'\n').encode())
    print(json.dumps({'binding': pin(BINDING), 'reportedKeys': len(reported), 'emptySupportKeys': len(empty)}))


def execute():
    binding = load(BINDING)
    bound = module(FIT/'completion/bound.py', 'w50_registered_bound')
    if OUT.exists(): raise ValueError('Completion output must be a fresh external directory')
    OUT.mkdir()
    bundle = bound.assemble_registered(REPO, binding, artifact_root=OUT/'artifacts')
    pins = bound.materialize_artifacts(bundle)
    bound.validate_registered(REPO, binding, bundle)
    encode = lambda value: (json.dumps(value, indent=2, allow_nan=False)+'\n').encode()
    write_once(OUT/'completed-references.json', encode(bundle['completed']))
    write_once(OUT/'bundle.json', encode(bundle))
    statuses = collections.Counter((c['role'], c['status']) for c in bundle['completed']['cells'])
    print(json.dumps({'binding': pin(BINDING), 'counts': bundle['counts'],
        'statuses': sorted([list(k)+[n] for k, n in statuses.items()]), 'artifacts': len(pins),
        'completedReferences': pin(OUT/'completed-references.json', True),
        'bundle': pin(OUT/'bundle.json', True)}, indent=1))


if __name__ == '__main__':
    {'register': register, 'execute': execute}[sys.argv[1]]()
