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
AUTHORITY_PATH = HERE/'analysis-2-attempt-2.authority.json'
VIEW_PATH = HERE/'analysis-2-attempt-2.root-view.json'
CONTRACT_PATH = HERE/'analysis-2-attempt-2.contract.json'
NEW_MARKER = Path(str(CONTRACT_PATH)+'.phase/analysis.started.json')
PREFLIGHT = HERE/'analysis-2-attempt-2.preflight.json'
REVIEW = HERE/'attempt-2-review-clearance.json'
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
    return {'failedAttempt': {'analysis': 2, 'attempt': 1, 'tombstone': str(TOMBSTONE),
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
    value['analysisSuccessor'].update(attempt=2, ruling=RULING,
        failedAttemptAudit=W.pin(AUDIT), historicalProofCommit=HISTORICAL_COMMIT)
    return value


def successor_contract(old, view_pin):
    value = OLD.copy.deepcopy(old)
    value.update(schema='w50-dl5s-analysis-only-contract-1', analysis=2, attempt=2,
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


def review():
    value = W.parse(REVIEW.read_bytes())
    if (value.get('schema') != 'w50-dl5s-review-clearance-1' or value.get('reviewerType') !=
            'doperpowers:reviewer-high' or value.get('verdict') != 'CLEARED' or
            value.get('sources') != {name: W.sha(HERE/name) for name in TOOLS}):
        raise ValueError('Attempt 2 needs reviewer-high clearance of these exact sources')
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
