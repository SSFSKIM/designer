#!/Users/new/vitrea-w49/py/bin/python -I -B
"""Byte-level witness of the r3 owner-evidence chain (DL5o, in DL5l's pattern; DL5m 5).

DL5o (a) changes owner/intrinsic.ts (historical family-keyed X76 entries admitted verbatim as a
family's hold) and owner/witness.ts (the X76 contract names the functions and the exclusion that
admit them). Both are owner closure sources and contract readerSources, so the owner reads and
the reference assembly were rerun exactly as r2 was. This compares every r2 artefact of the
chain with its r3 successor and classifies each difference. The chain is admitted only if
nothing moved beyond:
  * the two moved sources: intrinsic.ts and witness.ts in the source closure and the contracts'
    readerSources, each naming the file's actual hash;
  * the contracts' X76 contract: its sourceSelectors gaining exactly the four DL5o functions and
    its exclusions gaining exactly `familyKeyedHistory`; every projection row's copy of that
    contract equal to the r3 contracts' own;
  * nothing in the prepared current report (byte-identical: X75/X76 there are placeholders);
  * pins that name moved files: a projection's reportPin/contractsPin, the index's source and
    each row's evidence pin, a completed owner row's ownerEvidence, the binding's ownerIndex,
    ownerContracts and run.py source pin, the bundle's inputs. A moved pin's path is its
    predecessor's r3 successor and both of its hashes are the actual hashes of the files they
    name;
  * the assembly's fresh artifact root, every artifact byte-identical.
And each read is closed at both ends: each r3 instrument is its r2 one with only request,
closure and output replaced, each naming its r3 file at its actual hash; the contracts and
prepare requests are unchanged and the projection request moves only its two read pins; each
dispatch log names its instrument's output at its actual hash, the instrument as root and the
request's mode; the committed r3 evidence is those outputs' bytes and owner/r2/index.py's
archive of the logged projection output, every byte, no extra row.
Anything else is listed under `unexpected` and the status says so. It also grades both prepared
reports as the candidate without intrinsic evidence (both pass), grades the r3 one WITH X75/X76
on the hypothetical identity candidate through the frozen owner engine (judge/owner_selfcheck.py;
DL5o requires that before the successor root seals), and records which pre-fit proofs were
rebuilt in prefit-proofs-r3 and which stand, each validated, none pinning a superseded file.
Counts, paths, identities and hashes only; no statistic is printed or written (DL5k).

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
OLD_READ, NEW_READ = Path('/Users/new/vitrea-w50/g1-owner-read-r2'), Path('/Users/new/vitrea-w50/g1-owner-read-r3')
OLD_OUT, NEW_OUT = Path('/Users/new/vitrea-w50/g1-completion-r2'), Path('/Users/new/vitrea-w50/g1-completion-r3')
OLD_TAG, NEW_TAG = 'r2', 'r3'
OLD_REGISTERED = 'completion/registered-2'
KEY = ('profile', 'renderer', 'scene', 'statistic')
READS = {'contracts': 'contracts.json', 'prepare': 'prepare.json', 'projection': 'projection.json'}
MOVED_SOURCES = ('owner/intrinsic.ts', 'owner/witness.ts')
DL5O_SELECTORS = ['partitionEntries', 'fallsUnder', 'admitFamilies', 'checkFamilyInheritance']


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
    """The sha256 of the file a pin names (a relative path resolves under REPO), or None."""
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
    for part in path:
        try:
            doc = doc[part]
        except (KeyError, IndexError, TypeError):
            return None
    return doc


def names_its_file(pin):
    return isinstance(pin, dict) and set(pin) == {'path', 'sha256'} and isinstance(pin['sha256'], str) \
        and pin['sha256'] == actual(pin['path'])


def moved_pin(old, new, rename):
    return names_its_file(old) and names_its_file(new) and rename(old['path']) == new['path']


def to_new(path):
    """The r3 evidence directory's name for an r2 owner evidence path."""
    old, new = f'/owner/evidence-{OLD_TAG}/', f'/owner/evidence-{NEW_TAG}/'
    return path.replace(old, new, 1) if isinstance(path, str) and old in path else None


def evidence_files():
    return {str(OWNER/f'evidence-{OLD_TAG}'/n): str(OWNER/f'evidence-{NEW_TAG}'/n)
            for n in ('prepare.json', 'contracts.json')}


def reads():
    return {str(OLD_READ/n): str(NEW_READ/n) for n in READS.values()}


def module(path, name):
    import types
    loaded = types.ModuleType(name); loaded.__file__ = str(path); sys.modules[name] = loaded
    exec(compile(Path(path).read_bytes(), str(path), 'exec', dont_inherit=True), loaded.__dict__)
    return loaded


def x76_contract(old, new):
    """The DL5o change to the X76 contract, and nothing else in it."""
    expected = dict(old, sourceSelectors=old['sourceSelectors'][:3]+DL5O_SELECTORS[:3]
                    + old['sourceSelectors'][3:4]+DL5O_SELECTORS[3:]+old['sourceSelectors'][4:],
                    exclusions=dict(old['exclusions'], familyKeyedHistory=new['exclusions'].get('familyKeyedHistory')))
    return new == expected and isinstance(new['exclusions'].get('familyKeyedHistory'), str) \
        and new['exclusions']['familyKeyedHistory'].startswith('DL5o (a)')


def owner_files(L):
    out = {}
    closure_old = load(OWNER/f'{OLD_TAG}/source-closure.json')
    closure_new = load(OWNER/f'{NEW_TAG}/source-closure.json')
    moved = [fmt(p) for p, _, _ in leaves(closure_old, closure_new)]
    index = {s['path']: i for i, s in enumerate(closure_old['sources'])}
    prefix = rel(FIT)+'/'
    expected = sorted(f'sources/{index[prefix+name]}/sha256' for name in MOVED_SOURCES)
    L.admit('closure intrinsic.ts and witness.ts', sorted(moved) == expected and all(
        closure_new['sources'][index[prefix+name]]['sha256'] == actual(FIT/name) for name in MOVED_SOURCES),
        ['closure', moved])
    out['closure'] = {'sources': len(closure_new['sources']), 'differing': moved}

    old_contracts = load(OWNER/f'evidence-{OLD_TAG}/contracts.json')
    new_contracts = load(OWNER/f'evidence-{NEW_TAG}/contracts.json')
    contracts = [fmt(p) for p, _, _ in leaves(old_contracts, new_contracts)]
    readers = sorted(f'readerSources/{Path(n).name}/sha256' for n in MOVED_SOURCES)
    L.admit('contracts readerSources intrinsic.ts and witness.ts',
            sorted(c for c in contracts if c.startswith('readerSources/')) == readers and
            all(new_contracts['readerSources'][Path(n).name]['sha256'] == actual(FIT/n) for n in MOVED_SOURCES),
            ['contracts readerSources', contracts])
    rest = sorted(c for c in contracts if not c.startswith('readerSources/'))
    L.admit('contracts X76: the four DL5o selectors and familyKeyedHistory',
            rest == ['intrinsic/X76/exclusions/familyKeyedHistory', 'intrinsic/X76/sourceSelectors'] and
            x76_contract(old_contracts['intrinsic']['X76'], new_contracts['intrinsic']['X76']) and
            {k: v for k, v in old_contracts.items() if k not in ('readerSources', 'intrinsic')} ==
            {k: v for k, v in new_contracts.items() if k not in ('readerSources', 'intrinsic')} and
            old_contracts['intrinsic']['X75'] == new_contracts['intrinsic']['X75'],
            ['contracts X76', rest])
    out['contracts'] = {'differing': contracts}

    same = (OWNER/f'evidence-{OLD_TAG}/prepare.json').read_bytes() == (OWNER/f'evidence-{NEW_TAG}/prepare.json').read_bytes()
    L.admit('prepare byte-identical', same, ['prepare'])
    out['prepare'] = {'cells': len(load(OWNER/f'evidence-{NEW_TAG}/prepare.json')['cells']), 'byteIdentical': same}
    return out


def projections(L):
    old_batch, new_batch = load(OLD_READ/'projection.json'), load(NEW_READ/'projection.json')
    new_x76 = load(OWNER/f'evidence-{NEW_TAG}/contracts.json')['intrinsic']['X76'] \
        if (OWNER/f'evidence-{NEW_TAG}/contracts.json').is_file() else None
    def pins_only(old, new, where):
        for path, o, n in leaves(old, new):
            if path[:3] == ('intrinsic', 'X76', 'contract'):
                L.admit('projection row X76 contract: the r3 contracts\' own', at(new, path[:3]) == new_x76, [where, fmt(path)])
                continue
            field = path[-2] if len(path) >= 2 else None
            ok = path[-1] in ('path', 'sha256') and field in ('reportPin', 'contractsPin') and \
                moved_pin(at(old, path[:-1]), at(new, path[:-1]), evidence_files().get)
            L.admit(f'projection {field}', ok, [where, fmt(path)])
    pins_only({k: v for k, v in old_batch.items() if k != 'rows'}, {k: v for k, v in new_batch.items() if k != 'rows'}, 'batch')
    keys = [[r['row'][k] for k in KEY] for r in old_batch['rows']]
    L.admit('projection membership/order', keys == [[r['row'][k] for k in KEY] for r in new_batch['rows']], ['rows order'])
    for old, new in zip(old_batch['rows'], new_batch['rows']):
        pins_only(old, new, old['cellId'])
    old_index = load(OWNER/f'evidence-{OLD_TAG}/projection-index.json')
    new_index = load(OWNER/f'evidence-{NEW_TAG}/projection-index.json')
    L.admit('index membership/order', [r['key'] for r in old_index['rows']] == [r['key'] for r in new_index['rows']] == keys,
            ['index order'])
    L.admit('index schema and source pin', set(old_index) == set(new_index) == {'schema', 'source', 'rows'} and
            old_index['schema'] == new_index['schema'] and
            moved_pin(old_index['source'], new_index['source'], reads().get), ['index source'])
    for old, new in zip(old_index['rows'], new_index['rows']):
        ok = set(old) == set(new) == {'key', 'evidence'} and moved_pin(old['evidence'], new['evidence'], to_new)
        L.admit('index row evidence pin (directory and content pins)', ok, ['index', old['key']])
    return {'rows': len(new_batch['rows']),
            'rowValuesIdentical': 'every row differs only in reportPin/contractsPin and its copy of the X76 contract',
            'indexRows': len(new_index['rows'])}


def instruments(L):
    out = {}
    closures = {str(OWNER/f'{OLD_TAG}/source-closure.json'): str(OWNER/f'{NEW_TAG}/source-closure.json')}.get
    for mode, name in READS.items():
        instrument = OWNER/f'{NEW_TAG}/{mode}-instrument.json'
        old, new = load(OWNER/f'{OLD_TAG}/{mode}-instrument.json'), load(instrument)
        moved = sorted({p[0] for p, _, _ in leaves(old, new)})
        requests = {str(OWNER/f'{OLD_TAG}/{mode}-request.json'): str(OWNER/f'{NEW_TAG}/{mode}-request.json')}.get
        L.admit(f'instrument: only request, closure and output replaced, each its {NEW_TAG} file',
                set(old) == set(new) and moved == ['closure', 'output', 'request'] and
                moved_pin(old['request'], new['request'], requests) and
                moved_pin(old['closure'], new['closure'], closures) and
                old['output'] == str(OLD_READ/name) and new['output'] == str(NEW_READ/name), [mode, 'instrument', moved])
        old_request = load(OWNER/f'{OLD_TAG}/{mode}-request.json')
        new_request = load(OWNER/f'{NEW_TAG}/{mode}-request.json')
        request_moved = sorted({p[0] for p, _, _ in leaves(old_request, new_request)})
        pins = ['completedReferencesPin', 'contractsPin'] if mode == 'projection' else []
        L.admit("request: unchanged but the projection's two read pins", request_moved == pins and
                all(moved_pin(old_request[k], new_request[k], evidence_files().get) for k in pins),
                [mode, 'request', request_moved])
        log_path = NEW_READ/f'{mode}-dispatch.log'
        output = actual(new['output'])
        L.admit(f"dispatch log: the {NEW_TAG} instrument's output at its actual hash", output is not None and
                log_path.is_file() and load(log_path) == {'output': new['output'], 'sha256': output,
                                                          'rootSha256': actual(instrument), 'mode': new_request.get('mode')},
                [mode, 'dispatch log'])
        out[mode] = {'instrument': pin(instrument), 'fieldsMoved': moved, 'requestFieldsMoved': request_moved,
                     'dispatchLog': pin(log_path) if log_path.is_file() else None,
                     'output': pin(new['output']) if output is not None else None}
    return out


def evidence_archive(L):
    evidence = OWNER/f'evidence-{NEW_TAG}'
    different = [n for n in ('contracts.json', 'prepare.json') if (evidence/n).read_bytes() != (NEW_READ/n).read_bytes()]
    L.admit(f'{NEW_TAG} evidence: the logged contracts and prepare outputs', not different, ['evidence copies', different])
    archive = module(OWNER/'r2/index.py', 'w50_recovery_index').build(NEW_READ/'projection.json', evidence)
    differing = sorted(p for p, raw in archive.items() if not (REPO/p).is_file() or (REPO/p).read_bytes() != raw)
    extra = sorted({rel(p) for p in (evidence/'rows').iterdir()} - set(archive))
    top = sorted(p.name for p in evidence.iterdir())
    L.admit(f"{NEW_TAG} evidence: index.py's archive of the logged projection output", not differing and not extra and
            top == ['contracts.json', 'prepare.json', 'projection-index.json', 'projection.json.gz', 'rows'],
            ['evidence archive', differing, extra, top])
    return {'copies': ['contracts.json', 'prepare.json'], 'archiveFiles': len(archive),
            'archiver': pin(OWNER/'r2/index.py')}


def binding_and_bundle(L):
    old, new = load(FIT/OLD_REGISTERED/'binding.json'), load(HERE/'binding.json')
    moved = sorted({p[0] for p, _, _ in leaves(old, new)})
    source_moves = [fmt(p) for p, _, _ in leaves(old['sourcePins'], new['sourcePins'])]
    old_run, new_run = rel(FIT/OLD_REGISTERED/'run.py'), rel(HERE/'run.py')
    L.admit('binding ownerIndex/ownerContracts/run.py source pin',
            moved == ['ownerContracts', 'ownerIndex', 'sourcePins'] and sorted(source_moves) == sorted([new_run, old_run])
            and old['sourcePins'].get(old_run) == actual(old_run) and new['sourcePins'].get(new_run) == actual(new_run)
            and all(moved_pin(old[k], new[k], to_new) for k in ('ownerContracts', 'ownerIndex')),
            ['binding', moved, source_moves])
    old_bundle, new_bundle = load(OLD_OUT/'bundle.json'), load(NEW_OUT/'bundle.json')
    fields = sorted({p[0] for p, _, _ in leaves({k: v for k, v in old_bundle.items() if k != 'completed'},
                                                  {k: v for k, v in new_bundle.items() if k != 'completed'})})
    L.admit('bundle fields', fields == ['artifactRoot', 'artifacts', 'binding', 'inputs', 'sourcePins'], ['bundle', fields])
    L.admit(f"bundle binding and sources are the {NEW_TAG} binding's", new_bundle['binding'] == new and
            new_bundle['sourcePins'] == new['sourcePins'] and old_bundle['binding'] == old, ['bundle binding'])
    inputs = sorted({p[0] for p, _, _ in leaves(old_bundle['inputs'], new_bundle['inputs'])})
    L.admit('bundle inputs: owner index, contracts and batch', inputs == ['ownerBatch', 'ownerContracts', 'ownerIndex'] and
            moved_pin(old_bundle['inputs']['ownerBatch'], new_bundle['inputs']['ownerBatch'], reads().get) and
            all(moved_pin(old_bundle['inputs'][k], new_bundle['inputs'][k], to_new) for k in ('ownerContracts', 'ownerIndex')),
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
    old = load(FIT/f'live-inputs/completed-references-{OLD_TAG}.json')
    new = load(FIT/f'live-inputs/completed-references-{NEW_TAG}.json')
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
                    moved_pin(a['ownerEvidence'], b['ownerEvidence'], to_new)
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
    """Both prepared reports graded without intrinsic evidence, and the r3 one WITH X75/X76 on
    the identity candidate through the frozen owner engine (DL5o)."""
    S = module(FIT/'judge/owner_selfcheck.py', 'w50_recovery_owner_selfcheck')
    keys = S.owner_keys(load(FIT.parent/'2026-10-08-w50-g0-declaration/references.json'))
    out = {}
    for name in (OLD_TAG, NEW_TAG):
        report = load(OWNER/f'evidence-{name}/prepare.json')
        result = S.grade(report, load(OWNER/f'evidence-{name}/contracts.json'), keys, S.membership_of(report))
        out[name] = {k: result[k] for k in ('status', 'counts', 'statuses', 'intrinsicNotGraded')}
        out[name]['notPassing'] = [c['id'] for c in result['notPassing']]
    graded = S.selfcheck(FIT/'judge/config.json')
    out['graded'] = {k: graded[k] for k in ('status', 'counts', 'statuses', 'familyHolds', 'identityCandidate')}
    out['graded']['notPassing'] = [c['id'] for c in graded['notPassing']]
    out['graded']['intrinsic'] = graded['intrinsic']
    out['graded']['ownerConfig'] = graded['engine']['ownerConfig']
    L.admit('self-check: r2 and r3 pass ungraded; r3 passes with X75 (12) and X76 (0.25, 0.5) graded',
            out[OLD_TAG]['status'] == out[NEW_TAG]['status'] == 'PASS' and graded['status'] == 'PASS'
            and graded['config']['sha256'] == actual(FIT/'judge/config.json')
            and graded['preparedReport']['path'].endswith(f'/owner/evidence-{NEW_TAG}/prepare.json')
            and sorted((i['name'], i['member']) for i in graded['intrinsic'] if i['name'] == 'X76')
            == [('X76', '0.25'), ('X76', '0.5')]
            and sum(i['name'] == 'X75' and i['member'] != '*' for i in graded['intrinsic']) == 12
            and all(i['status'] == 'PASS' for i in graded['intrinsic']), ['selfcheck'])
    return out


REBUILT = ('active05ScratchBaselines', 'dark05Bands', 'referenceCompletion', 'repeatBar')
STANDING = ('identityDigestsGoldens', 'nativeArchive', 'negativeNeutralDiagnostic', 'newBedRendererAdapter',
            'numericalRehearsal', 'shaderCpuAgreement')


def proofs(L):
    """Which pre-fit proofs moved with the chain, and that each current one validates."""
    V = module(FIT.parent/'2026-10-08-w50-g1-current3/execution/prefit.py', 'w50_recovery_prefit')
    fit = rel(FIT)+'/'
    superseded = lambda p: p.startswith((fit+f'owner/evidence-{OLD_TAG}/', fit+f'owner/{OLD_TAG}/',
                                         fit+OLD_REGISTERED+'/', fit+'owner/evidence/', fit+'completion/registered/')) \
        or p in (fit+f'live-inputs/completed-references-{OLD_TAG}.json', fit+'live-inputs/completed-references.json',
                 fit+'owner/source-closure.json')
    out = {'rebuilt': {}, 'standing': {}}
    for kind in REBUILT + STANDING:
        group, directory = ('rebuilt', f'prefit-proofs-{NEW_TAG}') if kind in REBUILT else ('standing', 'prefit-proofs')
        proof_path = FIT/directory/f'{kind}.json'
        proof = load(proof_path)
        V.validate_proof(proof, kind, str(REPO))
        hits = sorted({p['path'] for p in proof['sources'] + proof['outputs'] if superseded(p['path'])})
        L.admit(f'{group} proof pins no superseded artefact', not hits, [kind, hits])
        entry = {'proof': pin(proof_path), 'validateProof': 'PASS', 'movedPins': hits}
        if group == 'rebuilt':
            old_path = FIT/f'prefit-proofs-{OLD_TAG}'/f'{kind}.json'
            entry['superseded'] = pin(old_path)
            entry['supersededMovedPins'] = sorted({p['path'] for p in load(old_path)['sources'] if superseded(p['path'])})
            L.admit('rebuilt proof replaces a moved pin', bool(entry['supersededMovedPins']), [kind])
        out[group][kind] = entry
    return out


def prior(L, record):
    """The r2 witness stands as recorded: its own status and an empty unexpected list."""
    first = load(FIT/OLD_REGISTERED/'recovery-witness-2.json')
    L.admit('prior witness: r2 recorded only ruled differences', first.get('status') == 'ONLY_RULED_DIFFERENCES'
            and first.get('unexpected') == [], ['prior witness'])
    record['priorWitness'] = pin(FIT/OLD_REGISTERED/'recovery-witness-2.json')


def pins():
    side = lambda tag, read, out, registered: {name: pin(path) for name, path in (
        ('closure', OWNER/f'{tag}/source-closure.json'), ('contracts', OWNER/f'evidence-{tag}/contracts.json'),
        ('prepare', OWNER/f'evidence-{tag}/prepare.json'), ('projection', read/'projection.json'),
        ('projectionIndex', OWNER/f'evidence-{tag}/projection-index.json'),
        ('binding', registered/'binding.json'), ('bundle', out/'bundle.json'),
        ('completedReferences', FIT/f'live-inputs/completed-references-{tag}.json'))}
    return {'superseded': side(OLD_TAG, OLD_READ, OLD_OUT, FIT/OLD_REGISTERED), NEW_TAG: side(NEW_TAG, NEW_READ, NEW_OUT, HERE)}


def build():
    L = Ledger()
    record = {'schema': 'w50-owner-recovery-witness-3',
              'ruling': 'DL5o (a), recovered in DL5l\'s pattern; DL5m item 5',
              'fix': 'owner/intrinsic.ts admits a historical family-keyed X76 entry verbatim as that family\'s hold '
                     'when no moved leaf falls under it; owner/witness.ts\'s X76 contract names that admission'}
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


if __name__ == '__main__':
    result = build()
    raw = (json.dumps(result, indent=1, allow_nan=False)+'\n').encode()
    if '--write' in sys.argv:
        with Path(sys.argv[sys.argv.index('--write')+1]).open('xb') as handle: handle.write(raw)
    sys.stdout.write(raw.decode())
    sys.exit(0 if result['status'] == 'ONLY_RULED_DIFFERENCES' else 1)
