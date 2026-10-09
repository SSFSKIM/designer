#!/Users/new/vitrea-w49/py/bin/python -I -B
"""Byte-level witness of the r2 owner-evidence recovery (DL5l; DL5m 1).

Compares every superseded artefact of the owner chain with its r2 successor and classifies
each difference. The recovery is admitted only if nothing moved beyond:
  * the owner reader pin: referee.ts in the source closure and the contracts' readerSources,
    each naming the fixed referee.ts's actual hash;
  * the eight named dark inactive dark-solid WebGPU cells' L1 namedExclusion (false -> true);
  * pins that name those files: a projection's reportPin/contractsPin, the index's source
    and each row's evidence pin, a completed owner row's ownerEvidence, the binding's
    ownerIndex, ownerContracts and run.py source pin, the bundle's inputs. A moved pin's
    path is its predecessor's r2 successor and both of its hashes are the actual hashes of
    the files they name, so no moved pin can carry any other hash;
  * the assembly's fresh artifact root: an artifact pin's directory, with its file name and
    content hash unchanged, that hash its file's, and every artifact byte-identical.
And the chain is closed at both ends of each read:
  * each r2 instrument is its superseded one with only request, closure and output replaced,
    each replacement naming its r2 file at its actual hash; the contracts and prepare requests
    are unchanged and the projection request moves only its two read pins;
  * each r2 dispatch log names its instrument's output, that output's actual hash, the
    instrument's own hash as the root and the request's mode; the committed r2 contracts and
    prepare evidence are those outputs' bytes, and the committed r2 projection evidence is
    owner/r2/index.py's archive of the logged projection output, every byte, no extra row.
Anything else is listed under `unexpected` and the status says so; nothing is hidden. It also
grades both prepared reports as the candidate (judge/owner_selfcheck.py: the superseded one
fails on exactly the eight cells, r2 passes everything) and records which pre-fit proofs were
rebuilt in prefit-proofs-r2 and which stand, each validated, none pinning a superseded file.
Counts, paths, identities and hashes only; no statistic is printed or written (DL5k).

Schema 2 is the second pre-seal review's strictness (P3). The first witness,
recovery-witness.json, stays as recorded beside this one's output, recovery-witness-2.json, and
must reproduce: every section it recorded reads the same here and every count it admitted is
admitted again. completion/test_witness.py mutates a synthetic tree one link at a time.

  witness.py [--write PATH]
"""
import collections
import gzip
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
FIT = HERE.parents[1]
REPO = FIT.parents[3]
OWNER = FIT/'owner'
OLD_READ, NEW_READ = Path('/Users/new/vitrea-w50/g1-owner-read'), Path('/Users/new/vitrea-w50/g1-owner-read-r2')
OLD_OUT, NEW_OUT = Path('/Users/new/vitrea-w50/g1-completion'), Path('/Users/new/vitrea-w50/g1-completion-r2')
KEY = ('profile', 'renderer', 'scene', 'statistic')
READS = {'contracts': 'contracts.json', 'prepare': 'prepare.json', 'projection': 'projection.json'}
NAMED = sorted(f'apple-macos-27.0-{s}x-dark-standard-glass{g}/webgpu/dark-solid__{c}__inactive'
               for s in (1, 2) for g in ('0.25', '0.5') for c in ('capsule-button', 'rrect-md'))


def sha(raw): return hashlib.sha256(raw).hexdigest()
def rel(path): return str(Path(path).resolve().relative_to(REPO))
def pin(path): return {'path': rel(path) if Path(path).resolve().is_relative_to(REPO) else str(path),
                       'sha256': sha(Path(path).read_bytes())}
def load(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if raw[:2] == b'\x1f\x8b' else raw)


def leaves(a, b, path=()):
    """Every differing leaf as (path, old, new); a missing side is the sentinel 'ABSENT'."""
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            yield from leaves(a.get(k, 'ABSENT'), b.get(k, 'ABSENT'), path+(k,))
    elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        for i, (x, y) in enumerate(zip(a, b)):
            yield from leaves(x, y, path+(i,))
    elif type(a) is not type(b) or a != b:
        yield path, a, b


def fmt(path): return '/'.join(str(p) for p in path)


class Ledger:
    def __init__(self): self.expected, self.unexpected = collections.Counter(), []
    def admit(self, what, ok, where):
        if ok: self.expected[what] += 1
        else: self.unexpected.append(where)


_ACTUAL = {}


def actual(path):
    """The sha256 of the file a pin names (a relative path resolves under REPO), or None when
    there is none. Cached by size and modification time: each row file is named twice."""
    if not isinstance(path, (str, Path)) or not str(path):
        return None
    path = Path(path)
    path = path if path.is_absolute() else REPO/path
    if not path.is_file():
        return None
    stat = path.stat()
    key = (str(path), stat.st_size, stat.st_mtime_ns)
    if key not in _ACTUAL:
        _ACTUAL[key] = sha(path.read_bytes())
    return _ACTUAL[key]


def at(doc, path):
    """The value at a leaves() path, or None where either side lacks it."""
    for part in path:
        try:
            doc = doc[part]
        except (KeyError, IndexError, TypeError):
            return None
    return doc


def names_its_file(pin):
    """A {path, sha256} pin whose hash is the actual hash of the existing file it names."""
    return isinstance(pin, dict) and set(pin) == {'path', 'sha256'} and isinstance(pin['sha256'], str) \
        and pin['sha256'] == actual(pin['path'])


def moved_pin(old, new, rename):
    """A pin that now names the r2 successor of the file it named: the new path is `rename` of
    the old one, and each side's hash is the actual hash of its own file."""
    return names_its_file(old) and names_its_file(new) and rename(old['path']) == new['path']


def to_r2(path):
    """The r2 evidence directory's name for a superseded owner evidence path."""
    return path.replace('/owner/evidence/', '/owner/evidence-r2/', 1) \
        if isinstance(path, str) and '/owner/evidence/' in path else None


def evidence_files():
    """The superseded owner evidence a projection read pins, by its r2 successor."""
    return {str(OWNER/'evidence'/n): str(OWNER/'evidence-r2'/n) for n in ('prepare.json', 'contracts.json')}


def reads():
    """The superseded read outputs, by their r2 successors."""
    return {str(OLD_READ/n): str(NEW_READ/n) for n in READS.values()}


def module(path, name):
    import types
    loaded = types.ModuleType(name); loaded.__file__ = str(path); sys.modules[name] = loaded
    exec(compile(Path(path).read_bytes(), str(path), 'exec', dont_inherit=True), loaded.__dict__)
    return loaded


def owner_files(L):
    out = {}
    closure_old, closure_new = load(OWNER/'source-closure.json'), load(OWNER/'r2/source-closure.json')
    moved = [fmt(p) for p, _, _ in leaves(closure_old, closure_new)]
    referee = closure_old['sources'].index(next(s for s in closure_old['sources'] if s['path'].endswith('owner/referee.ts')))
    fixed = actual(OWNER/'referee.ts')
    L.admit('closure referee.ts', moved == [f'sources/{referee}/sha256'] and
            closure_new['sources'][referee]['sha256'] == fixed, ['closure', moved])
    out['closure'] = {'sources': len(closure_new['sources']), 'differing': moved}

    r2_contracts = load(OWNER/'evidence-r2/contracts.json')
    contracts = list(leaves(load(OWNER/'evidence/contracts.json'), r2_contracts))
    L.admit('contracts readerSources referee.ts', [fmt(p) for p, _, _ in contracts] == ['readerSources/referee.ts/sha256']
            and r2_contracts['readerSources']['referee.ts']['sha256'] == fixed,
            ['contracts', [fmt(p) for p, _, _ in contracts]])
    out['contracts'] = {'differing': [fmt(p) for p, _, _ in contracts]}

    prepared = list(leaves(load(OWNER/'evidence/prepare.json'), load(OWNER/'evidence-r2/prepare.json')))
    cells = sorted(p[1] for p, _, _ in prepared)
    ok = cells == NAMED and all(p[0] == 'cells' and p[2:] == ('L1', 'namedExclusion') and o is False and n is True
                                for p, o, n in prepared)
    L.admit('prepare L1 namedExclusion false->true', ok, ['prepare', [fmt(p) for p, _, _ in prepared]])
    out['prepare'] = {'cells': len(load(OWNER/'evidence-r2/prepare.json')['cells']), 'differingCells': cells,
                      'differingField': 'L1.namedExclusion', 'change': 'false -> true'}
    return out


def projections(L):
    old_batch, new_batch = load(OLD_READ/'projection.json'), load(NEW_READ/'projection.json')
    def pins_only(old, new, where):
        for path, o, n in leaves(old, new):
            field = path[-2] if len(path) >= 2 else None
            ok = path[-1] in ('path', 'sha256') and field in ('reportPin', 'contractsPin') and \
                moved_pin(at(old, path[:-1]), at(new, path[:-1]), evidence_files().get)
            L.admit(f'projection {field}', ok, [where, fmt(path)])
    pins_only({k: v for k, v in old_batch.items() if k != 'rows'}, {k: v for k, v in new_batch.items() if k != 'rows'}, 'batch')
    keys = [[r['row'][k] for k in KEY] for r in old_batch['rows']]
    L.admit('projection membership/order', keys == [[r['row'][k] for k in KEY] for r in new_batch['rows']], ['rows order'])
    for old, new in zip(old_batch['rows'], new_batch['rows']):
        pins_only(old, new, old['cellId'])
    old_index, new_index = load(OWNER/'evidence/projection-index.json'), load(OWNER/'evidence-r2/projection-index.json')
    L.admit('index membership/order', [r['key'] for r in old_index['rows']] == [r['key'] for r in new_index['rows']] == keys,
            ['index order'])
    L.admit('index schema and source pin', set(old_index) == set(new_index) == {'schema', 'source', 'rows'} and
            old_index['schema'] == new_index['schema'] and
            moved_pin(old_index['source'], new_index['source'], reads().get), ['index source'])
    for old, new in zip(old_index['rows'], new_index['rows']):
        ok = set(old) == set(new) == {'key', 'evidence'} and moved_pin(old['evidence'], new['evidence'], to_r2)
        L.admit('index row evidence pin (directory and content pins)', ok, ['index', old['key']])
    return {'rows': len(new_batch['rows']), 'rowValuesIdentical': 'every row differs only in reportPin/contractsPin',
            'indexRows': len(new_index['rows'])}


def instruments(L):
    """Each r2 read against its superseded one: the instrument, the request and the dispatch log."""
    out = {}
    closures = {str(OWNER/'source-closure.json'): str(OWNER/'r2/source-closure.json')}.get
    for mode, name in READS.items():
        instrument = OWNER/f'r2/{mode}-instrument.json'
        old, new = load(OWNER/f'{mode}-instrument.json'), load(instrument)
        moved = sorted({p[0] for p, _, _ in leaves(old, new)})
        requests = {str(OWNER/f'{mode}-request.json'): str(OWNER/f'r2/{mode}-request.json')}.get
        L.admit('instrument: only request, closure and output replaced, each its r2 file',
                set(old) == set(new) and moved == ['closure', 'output', 'request'] and
                moved_pin(old['request'], new['request'], requests) and
                moved_pin(old['closure'], new['closure'], closures) and
                old['output'] == str(OLD_READ/name) and new['output'] == str(NEW_READ/name), [mode, 'instrument', moved])
        old_request, new_request = load(OWNER/f'{mode}-request.json'), load(OWNER/f'r2/{mode}-request.json')
        request_moved = sorted({p[0] for p, _, _ in leaves(old_request, new_request)})
        pins = ['completedReferencesPin', 'contractsPin'] if mode == 'projection' else []
        L.admit("request: unchanged but the projection's two read pins", request_moved == pins and
                all(moved_pin(old_request[k], new_request[k], evidence_files().get) for k in pins),
                [mode, 'request', request_moved])
        log_path = NEW_READ/f'{mode}-dispatch.log'
        output = actual(new['output'])
        L.admit("dispatch log: the r2 instrument's output at its actual hash", output is not None and
                log_path.is_file() and load(log_path) == {'output': new['output'], 'sha256': output,
                                                          'rootSha256': actual(instrument), 'mode': new_request.get('mode')},
                [mode, 'dispatch log'])
        out[mode] = {'instrument': pin(instrument), 'fieldsMoved': moved, 'requestFieldsMoved': request_moved,
                     'dispatchLog': pin(log_path) if log_path.is_file() else None,
                     'output': pin(new['output']) if output is not None else None}
    return out


def evidence_archive(L):
    """The committed r2 evidence is the logged reads' bytes: contracts and prepare as copies, the
    projection as owner/r2/index.py's archive of its output, every file and no other."""
    different = [n for n in ('contracts.json', 'prepare.json')
                 if (OWNER/'evidence-r2'/n).read_bytes() != (NEW_READ/n).read_bytes()]
    L.admit('r2 evidence: the logged contracts and prepare outputs', not different, ['evidence copies', different])
    archive = module(OWNER/'r2/index.py', 'w50_recovery_index').build(NEW_READ/'projection.json', OWNER/'evidence-r2')
    differing = sorted(p for p, raw in archive.items() if not (REPO/p).is_file() or (REPO/p).read_bytes() != raw)
    extra = sorted({rel(p) for p in (OWNER/'evidence-r2/rows').iterdir()} - set(archive))
    top = sorted(p.name for p in (OWNER/'evidence-r2').iterdir())
    L.admit("r2 evidence: index.py's archive of the logged projection output", not differing and not extra and
            top == ['contracts.json', 'prepare.json', 'projection-index.json', 'projection.json.gz', 'rows'],
            ['evidence archive', differing, extra, top])
    return {'copies': ['contracts.json', 'prepare.json'], 'archiveFiles': len(archive),
            'archiver': pin(OWNER/'r2/index.py')}


def binding_and_bundle(L):
    old, new = load(FIT/'completion/registered/binding.json'), load(HERE/'binding.json')
    moved = sorted({p[0] for p, _, _ in leaves(old, new)})
    source_moves = [fmt(p) for p, _, _ in leaves(old['sourcePins'], new['sourcePins'])]
    old_run, new_run = rel(FIT/'completion/registered/run.py'), rel(HERE/'run.py')
    L.admit('binding ownerIndex/ownerContracts/run.py source pin',
            moved == ['ownerContracts', 'ownerIndex', 'sourcePins'] and sorted(source_moves) == sorted([new_run, old_run])
            and old['sourcePins'].get(old_run) == actual(old_run) and new['sourcePins'].get(new_run) == actual(new_run)
            and all(moved_pin(old[k], new[k], to_r2) for k in ('ownerContracts', 'ownerIndex')),
            ['binding', moved, source_moves])
    old_bundle, new_bundle = load(OLD_OUT/'bundle.json'), load(NEW_OUT/'bundle.json')
    fields = sorted({p[0] for p, _, _ in leaves({k: v for k, v in old_bundle.items() if k != 'completed'},
                                                  {k: v for k, v in new_bundle.items() if k != 'completed'})})
    L.admit('bundle fields', fields == ['artifactRoot', 'artifacts', 'binding', 'inputs', 'sourcePins'], ['bundle', fields])
    L.admit('bundle binding and sources are the r2 binding\'s', new_bundle['binding'] == new and
            new_bundle['sourcePins'] == new['sourcePins'] and old_bundle['binding'] == old, ['bundle binding'])
    inputs = sorted({p[0] for p, _, _ in leaves(old_bundle['inputs'], new_bundle['inputs'])})
    L.admit('bundle inputs: owner index, contracts and batch', inputs == ['ownerBatch', 'ownerContracts', 'ownerIndex'] and
            moved_pin(old_bundle['inputs']['ownerBatch'], new_bundle['inputs']['ownerBatch'], reads().get) and
            all(moved_pin(old_bundle['inputs'][k], new_bundle['inputs'][k], to_r2) for k in ('ownerContracts', 'ownerIndex')),
            ['bundle inputs', inputs])
    prefix = lambda name, root: name[len(str(root/'artifacts')):]
    L.admit('bundle artifacts: same names and documents under the fresh root',
            {prefix(k, OLD_OUT): v for k, v in old_bundle['artifacts'].items()} ==
            {prefix(k, NEW_OUT): v for k, v in new_bundle['artifacts'].items()} and
            all(k.startswith(str(OLD_OUT/'artifacts')+'/') for k in old_bundle['artifacts']) and
            all(k.startswith(str(NEW_OUT/'artifacts')+'/') for k in new_bundle['artifacts']), ['bundle artifacts'])
    return {'bindingFieldsMoved': moved, 'bindingSourcePinsMoved': source_moves, 'bundleFieldsMoved': fields,
            'bundleNote': 'artifacts and artifactRoot move with the fresh root; inputs with the owner pins; '
                          'binding and sourcePins with the binding; the completed inventory is witnessed below'}


def inventory(L):
    old, new = load(FIT/'live-inputs/completed-references.json'), load(FIT/'live-inputs/completed-references-r2.json')
    L.admit('inventory metadata', all(old[k] == new.get(k) for k in old if k != 'cells') and set(old) == set(new),
            ['inventory metadata'])
    L.admit('inventory membership/order', [[c[k] for k in KEY] for c in old['cells']] ==
            [[c[k] for k in KEY] for c in new['cells']], ['inventory order'])
    by_kind, identical = collections.Counter(), 0
    for a, b in zip(old['cells'], new['cells']):
        diffs = list(leaves(a, b))
        if not diffs:
            identical += 1; continue
        where = '|'.join(a[k] for k in KEY)
        for path, o, n in diffs:
            if a['statistic'] == 'owner-contracts' and path[0] == 'ownerEvidence':
                ok = len(path) == 2 and path[-1] in ('path', 'sha256') and \
                    moved_pin(a['ownerEvidence'], b['ownerEvidence'], to_r2)
                L.admit('owner row ownerEvidence pin', ok, [where, fmt(path)]); by_kind['owner ownerEvidence'] += 1
            elif path[-1] == 'path' and isinstance(o, str) and o.startswith(str(OLD_OUT/'artifacts')+'/'):
                held = at(b, path[:-1])
                L.admit('artifact pin directory', n == str(NEW_OUT/'artifacts')+o[len(str(OLD_OUT/'artifacts')):] and
                        isinstance(held, dict) and held.get('sha256') == actual(n),
                        [where, fmt(path)]); by_kind['artifact directory '+str(path[0])] += 1
            else:
                L.admit('unclassified', False, [where, fmt(path)])
    owners = sum(c['statistic'] == 'owner-contracts' for c in new['cells'])
    return {'rows': len(new['cells']), 'byteIdenticalRows': identical, 'ownerRows': owners,
            'differingLeavesByKind': dict(sorted(by_kind.items()))}


def artifacts(L):
    old = {p.name: p.read_bytes() for p in (OLD_OUT/'artifacts').iterdir()}
    new = {p.name: p.read_bytes() for p in (NEW_OUT/'artifacts').iterdir()}
    L.admit('artifacts byte-identical', old == new, ['artifacts', len(old), len(new)])
    return {'files': len(new), 'namesAndBytesIdentical': old == new}


def selfcheck(L):
    """Both prepared reports graded as the candidate through the judge's grade_owner_report."""
    S = module(FIT/'judge/owner_selfcheck.py', 'w50_recovery_owner_selfcheck')
    keys = S.owner_keys(load(FIT.parent/'2026-10-08-w50-g0-declaration/references.json'))
    out = {}
    for name, directory in (('superseded', 'evidence'), ('r2', 'evidence-r2')):
        report = load(OWNER/directory/'prepare.json')
        result = S.grade(report, load(OWNER/directory/'contracts.json'), keys, S.membership_of(report))
        out[name] = {k: result[k] for k in ('status', 'counts', 'statuses')}
        out[name]['notPassing'] = [c['id'] for c in result['notPassing']]
    L.admit('self-check: superseded fails on exactly the eight, r2 passes', out['superseded']['notPassing'] == NAMED
            and out['r2']['status'] == 'PASS' and out['r2']['notPassing'] == [], ['selfcheck'])
    return out


REBUILT = ('active05ScratchBaselines', 'dark05Bands', 'referenceCompletion', 'repeatBar')
STANDING = ('identityDigestsGoldens', 'nativeArchive', 'negativeNeutralDiagnostic', 'newBedRendererAdapter',
            'numericalRehearsal', 'shaderCpuAgreement')


def proofs(L):
    """Which pre-fit proofs moved with the recovery, and that each current one validates."""
    V = module(FIT.parent/'2026-10-08-w50-g1-current3/execution/prefit.py', 'w50_recovery_prefit')
    fit = rel(FIT)+'/'
    moved = lambda p: p.startswith((fit+'owner/evidence/', fit+'completion/registered/')) or p in (
        fit+'live-inputs/completed-references.json', fit+'owner/referee.ts', fit+'owner/source-closure.json')
    out = {'rebuilt': {}, 'standing': {}}
    for kind in REBUILT + STANDING:
        group, directory = ('rebuilt', 'prefit-proofs-r2') if kind in REBUILT else ('standing', 'prefit-proofs')
        proof_path = FIT/directory/f'{kind}.json'
        proof = load(proof_path)
        V.validate_proof(proof, kind, str(REPO))
        hits = sorted({p['path'] for p in proof['sources'] + proof['outputs'] if moved(p['path'])})
        L.admit(f'{group} proof pins no superseded artefact', not hits, [kind, hits])
        entry = {'proof': pin(proof_path), 'validateProof': 'PASS', 'movedPins': hits}
        if group == 'rebuilt':
            old_path = FIT/'prefit-proofs'/f'{kind}.json'
            entry['superseded'] = pin(old_path)
            entry['supersededMovedPins'] = sorted({p['path'] for p in load(old_path)['sources'] if moved(p['path'])})
            L.admit('rebuilt proof replaces a moved pin', bool(entry['supersededMovedPins']), [kind])
        out[group][kind] = entry
    return out


def build():
    L = Ledger()
    record = {'schema': 'w50-owner-recovery-witness-2', 'ruling': 'DL5l reference-evidence recovery; DL5m item 1',
              'fix': '7e621f344 owner/referee.ts reads an absent L1 mean as the owner test does (null)',
              'strictness': 'second pre-seal review P3: moved pins name their files\' actual hashes; the '
                            'instruments and dispatch logs close each read',
              'priorWitness': pin(HERE/'recovery-witness.json')}
    record['owner'] = owner_files(L)
    record['projection'] = projections(L)
    record['reads'] = instruments(L)
    record['evidenceArchive'] = evidence_archive(L)
    record['assembly'] = binding_and_bundle(L)
    record['inventory'] = inventory(L)
    record['artifacts'] = artifacts(L)
    record['ownerSelfcheck'] = selfcheck(L)
    record['prefitProofs'] = proofs(L)
    record['pins'] = pins()
    prior(L, record)
    record['admitted'] = dict(sorted(L.expected.items()))
    record['unexpected'] = L.unexpected
    record['status'] = 'ONLY_RULED_DIFFERENCES' if not L.unexpected else 'UNEXPECTED_DIFFERENCES'
    record['builder'] = pin(Path(__file__))
    return record


def prior(L, record):
    """The first witness reproduces: every section it recorded reads the same here, and every
    count it admitted is admitted again; only its schema, builder and status words differ."""
    first = load(HERE/'recovery-witness.json')
    shared = sorted(set(first) - {'schema', 'admitted', 'unexpected', 'status', 'builder'})
    moved = [k for k in shared if record.get(k) != first[k]]
    L.admit('prior witness: every recorded section and admitted count reproduced', not moved and
            first['unexpected'] == [] and all(L.expected.get(k) == v for k, v in first['admitted'].items()),
            ['prior witness', moved])


def pins():
    return {
        'superseded': {name: pin(path) for name, path in (
            ('closure', OWNER/'source-closure.json'), ('contracts', OWNER/'evidence/contracts.json'),
            ('prepare', OWNER/'evidence/prepare.json'), ('projection', OLD_READ/'projection.json'),
            ('projectionIndex', OWNER/'evidence/projection-index.json'),
            ('binding', FIT/'completion/registered/binding.json'), ('bundle', OLD_OUT/'bundle.json'),
            ('completedReferences', FIT/'live-inputs/completed-references.json'))},
        'r2': {name: pin(path) for name, path in (
            ('closure', OWNER/'r2/source-closure.json'), ('contracts', OWNER/'evidence-r2/contracts.json'),
            ('prepare', OWNER/'evidence-r2/prepare.json'), ('projection', NEW_READ/'projection.json'),
            ('projectionIndex', OWNER/'evidence-r2/projection-index.json'),
            ('binding', HERE/'binding.json'), ('bundle', NEW_OUT/'bundle.json'),
            ('completedReferences', FIT/'live-inputs/completed-references-r2.json'))}}


if __name__ == '__main__':
    result = build()
    raw = (json.dumps(result, indent=1, allow_nan=False)+'\n').encode()
    if '--write' in sys.argv:
        with Path(sys.argv[sys.argv.index('--write')+1]).open('xb') as handle: handle.write(raw)
    sys.stdout.write(raw.decode())
    sys.exit(0 if result['status'] == 'ONLY_RULED_DIFFERENCES' else 1)
