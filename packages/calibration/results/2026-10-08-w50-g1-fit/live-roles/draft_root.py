"""Assemble the LIVE root body as a DRAFT (live-execution/execution-root.draft.json); never seal.

Every field is derived from repository bytes and checked by the original source validators the
seal will run again (authority.validate_body): G0 declaration selection, the DL5d dependency
table, the composed-current authority, the DL5a/b/c key enumerations, the DL5e owner budget and
evidence, each registered role's interface and its config/input registration. A component that
is not yet landed keeps a named TODO slot, which instrument_shape refuses, so the draft cannot be
sealed by accident. The closure is what the composite probe executes now; it must be rediscovered
when any source changes, which the seal (authority.seal_root) does and compares.

Run: /Users/new/vitrea-w49/py/bin/python -I -B live-roles/draft_root.py   (from the fit directory or anywhere)
"""
import json
from pathlib import Path
import subprocess
import sys
import types

HERE = Path(__file__).resolve().parent
FIT = HERE.parent
REPO = FIT.parents[3]
LIVE = FIT/'live-execution'
CANONICAL3 = FIT.parent/'2026-10-08-w50-g1-canonical3'


def source(path, name):
    module = types.ModuleType(name); module.__file__ = str(path)
    exec(compile(Path(path).read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


A = source(LIVE/'authority.py', 'w50_draft_authority')
D = A.D


def pin(path): return D.pin(REPO, path)


def todo(role, field, path, why):
    return {'TODO': f'{role}.{field}: {path} ({why})'}


INSTRUMENTS = {
    'capture': (HERE/'capture.py', HERE/'capture-config.json'),
    'native': (HERE/'native.py', HERE/'native-exposure-inputs.json'),
    'measurement': (HERE/'measurement.py', HERE/'measurement-config.json'),
    'owner': (HERE/'owner.py', HERE/'owner-config.json'),
}
PENDING = {
    'judge': (todo('judge', 'entrypoint', 'judge/live.py', 'concurrent judge worker'),
              todo('judge', 'config', 'judge/config.json', 'concurrent judge worker')),
    'fit': (todo('fit', 'entrypoint', 'fit/live.py', 'concurrent fit worker'),
            todo('fit', 'config', 'fit/analysis-config.json', 'concurrent fit worker')),
    'initializer': ({'path': str((FIT/'fit/execution.py').relative_to(REPO)), 'sha256': None},
                    todo('initializer', 'config', 'w50-fit-initializer-inputs-1 document',
                         'completedCurrent=currentEvidence, runtime closure/node, fit-scratch output; not yet written')),
}


def role_inputs(name, config):
    """Pins a role config names that its role requires to be root inputs (repo files only)."""
    doc = D.load(config)
    if name == 'measurement':
        native = doc['native']
        return [doc['completedReferences'], doc['completedCurrentEvidence'], doc['canonicalReferenceEvidence'],
                native['batch'], native['scenes'], *native['reports'].values()]
    if name == 'native':
        return [doc[k] for k in ('scenes', 'pack')]
    if name == 'owner':
        runtime = Path(doc['runtimeClosure']['path'])
        return [pin(runtime)] if runtime.is_relative_to(REPO) else []
    if name == 'capture':
        return list(doc['transports'].values())
    return []


def closure(probe, sources=None):
    """Record what the probe executes in an isolated child, then let the real guard confirm it."""
    recorder = r'''
import hashlib, importlib.machinery, json, runpy, sys
from pathlib import Path
repo, probe, guard = (Path(p).resolve() for p in sys.argv[1:4]); seen = {}
def note(name):
    path = Path(name).resolve()
    if path.is_relative_to(repo): seen[str(path.relative_to(repo))] = hashlib.sha256(path.read_bytes()).hexdigest()
note(guard)
old = importlib.machinery.SourceFileLoader.get_code
def get_code(loader, name): note(loader.get_filename(name)); return old(loader, name)
importlib.machinery.SourceFileLoader.get_code = get_code
sys.addaudithook(lambda e, a: note(a[0].co_filename) if e == 'exec' and not a[0].co_filename.startswith('<') else None)
prefix = str(repo)+'/'
sys.setprofile(lambda f, e, a: note(f.f_code.co_filename) if e == 'call' and f.f_code.co_filename.startswith(prefix) else None)
runpy.run_path(str(probe), run_name='w50_synthetic_probe'); sys.setprofile(None)
print(json.dumps(dict(sorted(seen.items()))))
'''
    if sources is None:
        result = subprocess.run([sys.executable, '-I', '-B', '-c', recorder, str(REPO), str(probe), str(LIVE/'guard.py')],
                                capture_output=True, text=True)
        if result.returncode: raise ValueError(result.stderr.strip()[-2000:])
        sources = json.loads(result.stdout.strip().splitlines()[-1])
    guard = source(LIVE/'guard.py', 'w50_draft_guard')
    return guard.discover(REPO, probe, sources)


def assemble():
    current3 = D.sealed(FIT.parent/'2026-10-08-w50-g1-current3/execution/current-instrument-root.json')
    binding = D.load(FIT/'completion/registered/binding.json')
    doc = {'schema': 'w50-g1-execution-root-1', 'repo': str(REPO), 'lifecycle': 'logical-phase-attempts-1',
           'quarantine': 'instrument-api-role-discipline-1', 'bootstrap': pin(LIVE/'dispatch.py'),
           'probe': pin(HERE/'probe.py'), 'recoveryRuling': pin(CANONICAL3/'inputs/dl5k-ruling.txt')}
    for name in ('partOne', 'partTwo', 'references', 'manifest'): doc[name] = current3[name]
    two = D.sealed(D.checked(REPO, doc['partTwo']))
    doc['candidateDomain'] = two['candidateDomain']
    D.declared_inputs(REPO, *(D.checked(REPO, doc[k]) for k in ('partOne', 'partTwo', 'references', 'manifest')))
    original = D.load(D.checked(REPO, doc['references'])); manifest = D.load(D.checked(REPO, doc['manifest']))
    doc['phaseDependencies'] = D.derive_phase_dependencies(original['cells'])
    if binding['original'] != doc['references'] or binding['manifest'] != doc['manifest']:
        raise ValueError('Registered completion binding names another declaration')
    doc['reportedKeys'], doc['emptySupportKeys'] = binding['reportedKeys'], binding['emptySupportKeys']
    prefit = source(LIVE/'prefit.py', 'w50_draft_prefit')
    prefit.validate_exemptions(original, manifest, doc['reportedKeys'])
    prefit.validate_empty_eligibility(original, manifest, doc['reportedKeys'], doc['emptySupportKeys'])
    doc['ownerBudgetKeys'] = D.owner_budget_keys(original['cells'])
    doc['ownerContracts'] = binding['ownerContracts']
    doc['currentComposition'] = pin(CANONICAL3/'composition/completed-current.json')
    doc['currentEvidence'] = pin(FIT/'live-inputs/completed-current.json')
    composition = source(CANONICAL3/'execution/composition.py', 'w50_draft_composition')
    current = composition.validate_completed_current(REPO, doc['currentComposition'])
    doc['baselineDocuments'] = current['candidates']
    old = current['roots'][0]['document']
    doc['repeatAdmission'], doc['newBedHost'] = old['repeatAdmission'], old['newBedHost']

    instruments, inputs, pending = {}, [], []
    def add(item):
        if item not in inputs: inputs.append(item)
    for name, (entrypoint, config) in INSTRUMENTS.items():
        if not entrypoint.is_file() or not config.is_file():
            instruments[name] = {'entrypoint': todo(name, 'entrypoint', entrypoint.name, 'absent'),
                                 'config': todo(name, 'config', config.name, 'absent')}
            pending.append(name); continue
        instruments[name] = {'entrypoint': pin(entrypoint), 'config': pin(config)}
        A.instrument_interface(name, source(entrypoint, 'w50_draft_interface_'+name))
        for item in (*instruments[name].values(), *role_inputs(name, config)): add(item)
    for name, (entrypoint, config) in PENDING.items():
        if entrypoint.get('sha256', '') is None: entrypoint = pin(REPO/entrypoint['path'])
        instruments[name] = {'entrypoint': entrypoint, 'config': config}; pending.append(name)
        if 'TODO' not in entrypoint: add(entrypoint)
    doc['instruments'] = instruments
    for item in (doc['recoveryRuling'], *doc['repeatAdmission'].values(), doc['newBedHost'],
                 doc['currentComposition'], doc['currentEvidence'], *current['chainPins'], doc['ownerContracts']):
        add(item)
    doc['inputs'] = inputs
    A.current_authority(doc, D.load(D.checked(REPO, doc['currentEvidence'])), current)
    if doc['ownerBudgetKeys']:
        source(LIVE/'owner_evidence.py', 'w50_draft_owner').OwnerEvidence(REPO, doc['ownerContracts'], D.owner_source(doc)).finish()
    for item in inputs: D.checked(REPO, item)
    doc['closure'] = closure(HERE/'probe.py')
    for name, role in instruments.items():
        for item in role.values():
            if 'TODO' not in item and doc['closure']['sources'].get(item['path']) not in (None, item['sha256']):
                raise ValueError('Component bytes differ from the exercised closure')
    return doc, pending


def main():
    doc, pending = assemble()
    target = LIVE/'execution-root.draft.json'
    target.write_text(json.dumps(doc, indent=2, allow_nan=False)+'\n')
    print(json.dumps({'draft': str(target.relative_to(REPO)), 'pending': pending,
                      'inputs': len(doc['inputs']), 'closureSources': len(doc['closure']['sources'])}))


if __name__ == '__main__':
    main()
