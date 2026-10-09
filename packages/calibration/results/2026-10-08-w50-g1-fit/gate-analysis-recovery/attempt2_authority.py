"""DL5s analysis 2 attempt 2: additive authority, never a reseal of attempt 1 or root 3."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
import types
import sys


def source(path, name):
    module = types.ModuleType(name); module.__file__ = str(path); sys.modules[name] = module
    exec(compile(Path(path).read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


OLD = source(HERE/'authority.py', 'w50_dl5s_original_authority')
H = source(HERE/'historical.py', 'w50_dl5s_historical')
W = OLD.W
FIT, REPO, REL = OLD.FIT, OLD.REPO, OLD.REL
ROOT, CONTRACT, MARKER, UNION, MANIFEST = OLD.ROOT, OLD.CONTRACT, OLD.MARKER, OLD.UNION, OLD.MANIFEST
OLD_OUTPUT = OLD.OLD_OUTPUT
OUTPUT = OLD.OUTPUT.with_name('gate-analysis-2-attempt-2')
PREPARATION = 6
PREFIX = f'analysis-2-attempt-2.preparation-{PREPARATION}'
AUTHORITY_PATH = HERE/(PREFIX+'.authority.json')
VIEW_PATH = HERE/(PREFIX+'.root-view.json')
CONTRACT_PATH = HERE/(PREFIX+'.contract.json')
NEW_MARKER = Path(str(CONTRACT_PATH)+'.phase/analysis.started.json')
PREFLIGHT = HERE/(PREFIX+'.preflight.json')
REVIEW = HERE/(PREFIX+'.review-pending.json')
FINAL_REVIEW = HERE/(PREFIX+'.review-clearance.json')
INVOCATION = HERE/'analysis-2-attempt-2.invocation.json'
FIXED_LOGICAL = HERE/'analysis-2-attempt-2.contract.json.started.json'
PREPARATION_RULING = 'b36acb5c92b99fd708ba52bdd2135e0c06530b5c'
PREPARATION_ONE_COMMIT = 'd891fdcbbf65626dbd5c3027c1ea262a701b2a8e'
DIAGNOSTIC_ONE_COMMIT = '566ea52d23ce67d8c2d5be5d6222623e38f5aacb'
SEAMS = [
    {'id': 'registered-input-artifact-view', 'meaning': 'The full immutable union is verified first. A distinct Boundary-only copy omits only outside-capture artifacts exactly matching independently registered canonical repo input pins; original union/captures still feed measurement, judge and witness unchanged. Original capture-output paths and634 files remain payload-denied.'},
    {'id': 'static-config-provenance', 'meaning': 'An independently root-pinned noncapture input may share raw bytes with a copied capture artifact. JSON admission retains read-path provenance, allows only that original registered path/hash, and still denies every capture path and unprovenanced matching payload.'},
    {'id': 'stdlib-interpreter-alias', 'meaning': 'The stdlib file probe may spell the identical resolved current interpreter through Homebrew intermediate aliases; file identity remains exact, not an arbitrary file grant.'},
    {'id': 'stdlib-platform-file', 'meaning': 'Only platform._syscmd_file may invoke file -b on the resolved current interpreter with LC_ALL=C for the unchanged architecture fingerprint; every other target/command refuses.'},
    {'id': 'stdlib-platform-devnull', 'meaning': 'Only stdlib subprocess _get_devnull may open the existing /dev/null character device after exact device/inode/type checks; every other writable open remains denied.'},
    {'id': 'stdlib-platform-uname', 'meaning': 'Only platform.from_subprocess may invoke exact uname -p from /usr/bin/uname for the unchanged environment fingerprint; no arbitrary subprocess grant.'},
    {'id': 'additive-preparation', 'meaning': 'Distinct prospective seals preserve every earlier preparation; one fixed invocation/output/logical/terminal/failure fence bars every later preparation after execution starts. Final review remains pending until a clean diagnostic.'},
]


def preparation_paths(n):
    prefix = 'analysis-2-attempt-2' if n == 1 else f'analysis-2-attempt-2.preparation-{n}'
    return [HERE/(prefix+'.'+kind+suffix) for kind in ('authority', 'root-view', 'contract')
            for suffix in ('.json', '.json.sha256')]


def previous_execution_paths():
    return tuple(Path(str(preparation_paths(n)[4])+'.phase/analysis.started.json')
                 for n in range(1, PREPARATION))

RULING = '8adfc8fd90619e109a80edf0aa691fa43b59fbd9'
AUDIT_COMMIT = '36cfacf75b65dcd01433b466b2f957373fbdff54'
HISTORICAL_COMMIT = 'bdb0f3fef27c0dc6381a605ba58eb8f5b1703af0'
PRESERVATION_COMMIT = 'f2f88158e'
EXCEPTIONS = FIT/'evidence/dl5s-historical-pin-exceptions/exceptions.json'
EXCEPTIONS_SHA = '04d02bdfb8135e6dd3a3a94088b5d4d4f2447f288ed671584b1638dd772e9002'
CHARTER = 'docs/doperpowers/specs/2026-10-08-w50-dark-low-end-response.md'
AUDIT = FIT/'evidence/gate-analysis-2-terminal/audit.json'
TOMBSTONE = HERE/'analysis-2.failed'
DELTA_PATHS = (OLD.SOURCE, REL+'/measurement/test_phase_sources.py')
TOOLS = (*OLD.TOOL_FILES, 'historical.py', 'attempt2_authority.py', 'attempt2_run.py',
         'attempt2_preflight.py', 'attempt2_seal.py', 'attempt2_probe.py')


def git(*args):
    return OLD.subprocess.run(['git', '-C', str(REPO), *args], check=True,
                              capture_output=True).stdout


def committed(path, commit):
    raw = Path(path).read_bytes()
    if raw != git('cat-file', 'blob', commit+':'+str(Path(path).relative_to(REPO))):
        raise ValueError('Preserved authority or audit bytes changed')
    return W.pin(path)


def preservation():
    for commit in (RULING, AUDIT_COMMIT, HISTORICAL_COMMIT, PRESERVATION_COMMIT):
        git('merge-base', '--is-ancestor', commit, 'HEAD')
    if not TOMBSTONE.is_dir() or TOMBSTONE.is_symlink() or list(TOMBSTONE.iterdir()):
        raise ValueError('Attempt 1 empty failure tombstone must remain')
    audit_pin = committed(AUDIT, AUDIT_COMMIT)
    audit = W.parse(AUDIT.read_bytes())
    preserved = [audit_pin]
    for item in audit['writtenFiles']:
        path = Path(item['path'])
        if W.sha(path) != item['sha256'] or path.stat().st_size != item['bytes']:
            raise ValueError('Attempt 1 evidence changed')
        if path.is_relative_to(REPO): committed(path, AUDIT_COMMIT)
        preserved.append(W.pin(path))
    for name in ('analysis.log', 'public-event.txt'):
        preserved.append(committed(AUDIT.parent/name, AUDIT_COMMIT))
    for name in OLD.TOOL_FILES:
        preserved.append(committed(HERE/name, AUDIT_COMMIT))
    if any(p.exists() for p in (OLD.NEW_MARKER, Path(str(OLD.CONTRACT_PATH)+'.started.json'),
                               HERE/'analysis-2.terminal.json', HERE/'analysis-2.complete.json')):
        raise ValueError('Attempt 1 no longer represents its pre-marker failure')
    exception_pin = committed(EXCEPTIONS, PRESERVATION_COMMIT)
    if exception_pin['sha256'] != EXCEPTIONS_SHA: raise ValueError('Exception witness changed')
    witness = W.parse(EXCEPTIONS.read_bytes())
    if (witness['historicalCommit'] != HISTORICAL_COMMIT or witness['uniquePaths'] != 17
            or witness['occurrenceCount'] != 20 or len(witness['paths']) != 17):
        raise ValueError('Wrong exact exception witness')
    full_preservation = git('rev-parse', PRESERVATION_COMMIT+'^{commit}').decode().strip()
    previous = []
    for n in range(1, PREPARATION):
        for path in preparation_paths(n):
            previous.append(committed(path, PREPARATION_ONE_COMMIT) if n == 1 else W.pin(path))
        if n == 1:
            previous.append(committed(HERE/'attempt-2-review-clearance.json', PREPARATION_ONE_COMMIT))
        else:
            previous.append(W.pin(HERE/f'analysis-2-attempt-2.preparation-{n}.review-pending.json'))
    diagnostics = [committed(FIT/'evidence/dl5s-preflight-1'/name, DIAGNOSTIC_ONE_COMMIT)
                   for name in ('refusal.json', 'stderr.log')]
    for n in range(2, PREPARATION):
        diagnostics.extend(W.pin(HERE/f'diagnostic-preparation-{n}'/name)
                           for name in ('stdout.json', 'stderr.log'))
    return {'preparation': {'number': PREPARATION, 'predecessors': previous,
                'diagnosticEvidence': diagnostics, 'rulingCommit': PREPARATION_RULING,
                'rulingPath': CHARTER,
                'rulingSha256': OLD.digest(git('cat-file', 'blob', PREPARATION_RULING+':'+CHARTER)),
                'seams': SEAMS, 'reviewStatus': 'PENDING_FINAL_REVIEW',
                'invocationFence': str(INVOCATION), 'fixedLogicalClaim': str(FIXED_LOGICAL),
                'previousMarkers': [str(p) for p in previous_execution_paths()]},
            'failedAttempt': {'analysis': 2, 'attempt': 1, 'tombstone': str(TOMBSTONE),
                             'state': 'EMPTY_DIRECTORY', 'auditCommit': AUDIT_COMMIT,
                             'preserved': preserved},
            'ruling': {'commit': RULING, 'path': CHARTER,
                       'sha256': OLD.digest(git('cat-file', 'blob', RULING+':'+CHARTER))},
            'historicalProof': {'commit': HISTORICAL_COMMIT,
                'exceptions': exception_pin, 'preservationCommit': full_preservation,
                'exceptionPaths': witness['paths'], 'liveDeltaCommit': OLD.CARRY_COMMIT,
                'liveDeltaPaths': list(DELTA_PATHS)}}


def historical_reader(binding):
    proof = binding['historicalProof']
    return H.Historical(REPO, HISTORICAL_COMMIT, OLD.CARRY_COMMIT, DELTA_PATHS,
        {row['path']: row for row in proof['exceptionPaths']}, proof['preservationCommit'])


def closure_sources(sources):
    return {**sources, **{str((HERE/name).relative_to(REPO)): W.sha(HERE/name) for name in TOOLS}}


def successor_view(root, sources):
    value = OLD.successor_view(root, sources, W.pin(ROOT))
    value['analysisSuccessor'].update(attempt=2, preparation=PREPARATION, ruling=RULING,
        failedAttemptAudit=W.pin(AUDIT), historicalProofCommit=HISTORICAL_COMMIT)
    return value


def successor_contract(old, view_pin):
    value = OLD.copy.deepcopy(old)
    value.update(schema='w50-dl5s-analysis-only-contract-1', analysis=2, attempt=2, preparation=PREPARATION,
        executionRootSha256=view_pin['sha256'], logicalOutput=str(OUTPUT),
        originalContract=W.pin(CONTRACT), executionAuthority=W.pin(AUTHORITY_PATH))
    value.pop('outputMarker')
    return value


def authority_document(root, sources, held, closure, binding):
    return {'schema': 'w50-dl5s-attempt-2-authority-1', 'analysis': 2, 'attempt': 2,
        **binding, 'historicalRoot': W.pin(ROOT), 'spentMarker': W.pin(MARKER),
        'captureUnion': W.pin(UNION), 'unreadManifest': W.pin(MANIFEST), 'unchanged': held,
        'closure': closure, 'output': str(OUTPUT), 'marker': str(NEW_MARKER),
        'preflightRecord': str(PREFLIGHT), 'review': W.pin(REVIEW),
        'witness': {'excludedTopLevelFields': list(W.AUTHORITY), 'exemptions': [], 'count': 634},
        'exposure': 'NOT_AUTHORISED_BY_THIS_INSTRUMENT'}


def pending_review():
    return {'schema': 'w50-dl5s-preparation-review-1', 'preparation': PREPARATION,
            'status': 'PENDING_FINAL_REVIEW',
            'sources': {name: W.sha(HERE/name) for name in TOOLS}}


def review():
    value = W.parse(REVIEW.read_bytes())
    if value != pending_review(): raise ValueError('Prospective review-pending source pins differ')
    return value


def final_review():
    value = W.parse(FINAL_REVIEW.read_bytes())
    if (value.get('schema') != 'w50-dl5s-review-clearance-1' or value.get('reviewerType') !=
            'doperpowers:reviewer-high' or value.get('verdict') != 'CLEARED' or
            value.get('sources') != pending_review()['sources'] or
            value.get('preparation') != PREPARATION or value.get('authority') != W.pin(AUTHORITY_PATH)
            or value.get('preflight') != W.pin(PREFLIGHT)):
        raise ValueError('Actual execution needs final reviewer-high clearance after clean preflight')
    return value


def verify_seal():
    review()
    root, contract, batch, manifest, sources, held = OLD.metadata()
    binding = preservation()
    authority = W.parse(AUTHORITY_PATH.read_bytes()); closure = authority['closure']
    if authority != authority_document(root, sources, held, closure, binding):
        raise ValueError('Attempt 2 authority differs')
    if closure['sources'] != closure_sources(sources): raise ValueError('Attempt 2 closure differs')
    guard = source(FIT/'live-execution/guard.py', 'w50_dl5s_guard')
    if guard.environment() != closure['environment']: raise ValueError('Interpreter changed')
    for path in (AUTHORITY_PATH, VIEW_PATH, CONTRACT_PATH):
        if Path(str(path)+'.sha256').read_text() != f'{W.sha(path)}  {path.name}\n':
            raise ValueError('Attempt 2 seal differs')
    view = W.parse(VIEW_PATH.read_bytes())
    if view != successor_view(root, sources): raise ValueError('Attempt 2 root-view differs')
    if W.parse(CONTRACT_PATH.read_bytes()) != successor_contract(contract, W.pin(VIEW_PATH)):
        raise ValueError('Attempt 2 contract differs')
    return root, view, contract, batch, manifest, authority, guard
