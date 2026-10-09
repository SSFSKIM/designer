"""DL5r's explicit historical-root/successor-view admission, never an old-root relabelling.

root3 remains sealed against its historical source map. The original root_doc still refuses
its changed phase_sources.py. This separate authority authenticates root3 against the ruling
commit, proves the EXACT three added carry lines, and validates a labelled successor view
through the original semantic authority validator. That validator's old pathname argument is
solely its lineage/location context, not a claim that the old root admitted the new bytes.
All non-source fields of the view, including every input/config/reference pin, are preserved.
The successor execution closure is separate again: the amended old closure plus THIS tooling.
"""
import copy
import hashlib
from pathlib import Path
import subprocess
import sys
import types

HERE = Path(__file__).resolve().parent
FIT = HERE.parent
REPO = FIT.parents[3]
REL = str(FIT.relative_to(REPO))
RULING = 'c36e52da1'
CARRY_COMMIT = '02c0e5694bf9b579d2c3125a2ab60bf3684d5ea3'
READ_RULING = 'cf07f1550'
ROOT = FIT/'live-execution/execution-root-3.json'
CONTRACT = FIT/'live-execution/execution-root-3.gate-contract.json'
MARKER = Path(str(CONTRACT)+'.phase/analysis.started.json')
UNION = MARKER.parent/'captures.complete.json'
MANIFEST = FIT/'evidence/gate-analysis-stop/unread-measurements-manifest.json'
REFUSAL = FIT/'fit/live-initializer/attempt-1-refusal.json'
OLD_OUTPUT = Path('/Users/new/vitrea-w50/g1-live/gate')
OUTPUT = Path('/Users/new/vitrea-w50/g1-live/gate-analysis-2')
AUTHORITY_PATH = HERE/'analysis-2.authority.json'
VIEW_PATH = HERE/'analysis-2.root-view.json'
CONTRACT_PATH = HERE/'analysis-2.contract.json'
NEW_MARKER = Path(str(CONTRACT_PATH)+'.phase/analysis.started.json')
SOURCE = REL+'/measurement/phase_sources.py'
TOOL_FILES = ('authority.py', 'witness.py', 'run.py', 'seal.py', 'probe.py', 'reads.py')
ROOT_SHA = 'd50cf0547b982d33b35b1c41e953b9c2b011ca0fde4999ba2d14a0d00215d882'
MARKER_SHA = '02c070dcb0d7d40dc6498309e5a1b911324db5436b3b2987e7aa089a87296c3b'
UNION_SHA = 'a3022525cc9111a98999eb3d1c8f1ab4dcb888ebf25495f0e2ede71974f5f0cf'
MANIFEST_SHA = '95295607703bfa30ee4adea63b0182897c74a3a5085ada19a6b9625333983d49'
BEFORE_ONE = b"                    statistics[name] = dict(copy.deepcopy(produced), measurementStatus=produced['status'],\n"
BEFORE_TWO = b"                    record_map[name] = item\n"


def source(path, name):
    module = types.ModuleType(name); module.__file__ = str(path); sys.modules[name] = module
    exec(compile(Path(path).read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


W = source(HERE/'witness.py', 'w50_analysis2_witness')
sha, pin, parse = W.sha, W.pin, W.parse


def digest(raw): return hashlib.sha256(raw).hexdigest()


def checked(repo, item):
    path = (Path(repo)/item['path']).resolve()
    if not path.is_file() or sha(path) != item['sha256']:
        raise ValueError('Pinned bytes differ')
    if 'bytes' in item and path.stat().st_size != item['bytes']:
        raise ValueError('Pinned size differs')
    return path


def git_bytes(path):
    relative = str(Path(path).resolve().relative_to(REPO))
    result = subprocess.run(['git', '-C', str(REPO), 'show', RULING+':'+relative],
                            capture_output=True, check=True)
    return result.stdout


def historical(path):
    raw = Path(path).read_bytes()
    if raw != git_bytes(path): raise ValueError('Historical authority changed')
    return parse(raw)


def carry(old):
    if old.count(BEFORE_ONE) != 1 or old.count(BEFORE_TWO) != 1:
        raise ValueError('Carry site is not the original unique source')
    return old.replace(BEFORE_ONE,
        b"                    production = statistics.get(name, {}).get('productionStatistic')\n"+BEFORE_ONE
        ).replace(BEFORE_TWO, BEFORE_TWO+
        b"                    if production is not None:\n"
        b"                        statistics[name]['productionStatistic'] = copy.deepcopy(production)\n")


def source_delta(original, actual, changed, old):
    if set(original) != set(actual) or original.get(changed) != digest(old):
        raise ValueError('Historical source population differs')
    for path, expected in original.items():
        if path == changed:
            if actual[path] != carry(old): raise ValueError('Not the sole ruled source carry')
        elif digest(actual[path]) != expected: raise ValueError('Another historical source changed')
    return {path: digest(raw) for path, raw in actual.items()}


def successor_view(original, sources, predecessor):
    view = copy.deepcopy(original)
    view['closure']['sources'] = dict(sources)
    view['analysisSuccessor'] = {'schema': 'w50-dl5r-labelled-root-view-1', 'analysis': 2,
        'historicalRoot': predecessor, 'ruling': RULING,
        'meaning': 'Successor analytical view; not a revalidation or reseal of historical root3'}
    return view


def check_view(original, view, sources, predecessor):
    if view != successor_view(original, sources, predecessor):
        raise ValueError('Successor view changed a non-source original field')


def metadata():
    """Source and authority metadata only. Never parses a gate measurement or capture payload."""
    for commit in (RULING, CARRY_COMMIT, READ_RULING):
        subprocess.run(['git', '-C', str(REPO), 'merge-base', '--is-ancestor', commit, 'HEAD'],
                       check=True, capture_output=True)
    for path, expected in ((ROOT, ROOT_SHA), (MARKER, MARKER_SHA),
                           (UNION, UNION_SHA), (MANIFEST, MANIFEST_SHA)):
        if sha(path) != expected: raise ValueError('DL5r fixed predecessor pin differs')
    root = historical(ROOT); contract = historical(CONTRACT)
    if contract['executionRootSha256'] != ROOT_SHA or contract['phase'] != 'gate':
        raise ValueError('Wrong original gate root')
    if Path(str(CONTRACT)+'.result.json').exists():
        raise ValueError('Original gate already has a result')
    batch_path = checked(REPO, contract['batch']); batch = historical(batch_path)
    fit_path = checked(REPO, contract['fitRecord']); fit = historical(fit_path)
    refusal = historical(REFUSAL)
    if len(refusal['files']) != 11 or len({p['path'] for p in refusal['files']}) != 11:
        raise ValueError('Candidate/initializer closure is not the preserved eleven files')
    for item in refusal['files']: checked(REPO, item)
    if (batch['cohort'] != contract['cohort'] or fit['selected'] != contract['cohort']
            or fit['executionRootSha256'] != ROOT_SHA or len(fit['completed']) != 1):
        raise ValueError('Original selected fit/cohort changed')
    for item in fit['completed']: checked(REPO, item)
    originals = root['closure']['sources']
    actual = {path: (REPO/path).read_bytes() for path in originals}
    sources = source_delta(originals, actual, SOURCE, git_bytes(REPO/SOURCE))
    committed_carry = subprocess.run(['git', '-C', str(REPO), 'show', CARRY_COMMIT+':'+SOURCE],
                                    check=True, capture_output=True).stdout
    if actual[SOURCE] != committed_carry: raise ValueError('Carry differs from reviewed commit')
    # Root inputs retain their old byte identities; no config/reference re-pinning is admitted.
    for item in root['inputs']: checked(REPO, item)
    manifest = parse(MANIFEST.read_bytes())
    if manifest['count'] != 634 or manifest['analysisMarker'] != {
            'path': str(MARKER.relative_to(REPO)), 'sha256': MARKER_SHA}:
        raise ValueError('Wrong unread manifest')
    W.old_bytes(manifest, OLD_OUTPUT/'measurement')
    held = [ROOT, Path(str(ROOT)+'.sha256'), CONTRACT, Path(str(CONTRACT)+'.sha256'),
            Path(str(CONTRACT)+'.started.json'), MARKER, UNION, MANIFEST, REFUSAL, batch_path, fit_path,
            *[checked(REPO, p) for p in fit['completed']],
            *[checked(REPO, p) for p in refusal['files']]]
    return root, contract, batch, manifest, sources, [pin(p) for p in held]


def closure_sources(amended):
    return {**amended, **{str((HERE/name).relative_to(REPO)): sha(HERE/name)
                         for name in TOOL_FILES}}


def successor_contract(old, view_pin):
    result = copy.deepcopy(old)
    result.update(schema='w50-dl5r-analysis-only-contract-1', executionRootSha256=view_pin['sha256'],
                  logicalOutput=str(OUTPUT), analysis=2, originalContract=pin(CONTRACT),
                  executionAuthority=pin(AUTHORITY_PATH))
    # This is not a capture contract: neither old capture admission nor create_phase accepts it.
    result.pop('outputMarker')
    return result


def verify_seal():
    root, contract, batch, manifest, sources, held = metadata()
    authority = parse(AUTHORITY_PATH.read_bytes())
    closure = authority['closure']
    if authority != authority_document(root, sources, held, closure):
        raise ValueError('Successor sealed authority differs')
    if closure['sources'] != closure_sources(sources):
        raise ValueError('Successor source closure differs')
    guard = source(FIT/'live-execution/guard.py', 'w50_analysis2_guard')
    if guard.environment() != closure['environment']:
        raise ValueError('Successor interpreter/environment changed')
    for path in (AUTHORITY_PATH, VIEW_PATH, CONTRACT_PATH):
        if Path(str(path)+'.sha256').read_text() != f'{sha(path)}  {path.name}\n':
            raise ValueError('Successor seal differs')
    view = parse(VIEW_PATH.read_bytes())
    check_view(root, view, sources, pin(ROOT))
    if parse(CONTRACT_PATH.read_bytes()) != successor_contract(contract, pin(VIEW_PATH)):
        raise ValueError('Successor analysis-only contract differs')
    return root, view, contract, batch, manifest, authority, guard


def authority_document(root, sources, held, closure):
    return {'schema': 'w50-dl5r-successor-analysis-authority-1', 'analysis': 2, 'ruling': RULING,
        'historicalRoot': pin(ROOT), 'spentMarker': pin(MARKER), 'captureUnion': pin(UNION),
        'unreadManifest': pin(MANIFEST), 'unchanged': held,
        'sourceDelta': {'path': SOURCE, 'before': root['closure']['sources'][SOURCE],
                        'after': sources[SOURCE], 'transform': 'exact-three-line-productionStatistic-carry',
                        'reviewedCommit': CARRY_COMMIT},
        'readAdapterRuling': READ_RULING,
        'closure': closure, 'output': str(OUTPUT), 'marker': str(NEW_MARKER),
        'witness': {'excludedTopLevelFields': list(W.AUTHORITY), 'exemptions': [], 'count': 634},
        'exposure': 'NOT_AUTHORISED_BY_THIS_INSTRUMENT'}
