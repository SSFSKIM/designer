"""W50 G1 pre-fit evidence: the executionClosure and independentReview proofs, then the sealed
per-root pre-fit evidence that LIVE's verify_prefit admits (charter DL5 (a), DL5o).

The root is the newest root of the LIVE chain (live-execution common.newest_root; DL5o's
successor) and its evidence lives in that root's own slot (common.slot(root, 'prefit')). Run
only after that root and its sidecar are sealed; nothing here seals or edits a root, and no
proof pins a superseded root. build(layout) does, in order:

1. Requires the sealed root. The completed reference inventory is the one the root's
   measurement config names (measurement/phase.py refuses a phase whose pre-fit references
   differ from its config). Each standing proof is the newest generation of its kind
   (prefit-proofs-r<n>/ before prefit-proofs/) and validates.
2. executionClosure: the root's seal; authority.validate_body on the sealed root; a fresh
   guard.discover of the root's probe equal to root.closure; each LIVE suite passing (unittest
   discovery per directory, and owner-candidate/live-test.py), with its log as an output.
3. independentReview: one check per round of review-records.json, each round's commit range,
   reviewers, findings by severity and dispositions with fixing commits, against git; then
   that the last round converged (no P0/P1) after every earlier fix, and that no root-bound
   byte changed after the last reviewed head. A TODO anywhere refuses.
4. The pre-fit evidence, written once with its sidecar: the root and its sidecar in sources,
   executionClosure equal to root.closure, references, partTwoSha256 and the twelve proofs.
5. verify(root): LIVE's own verify_prefit (default: a child process through the sealed
   dispatcher, since its import guard is permanent; run.Child).

A proof is written only when every check passes in this run; its logs are written once under
logs/<kind>/. An existing proof is reused only if it validates and pins this root. Logs carry
counts, hashes and pass/fail, never a measured value (DL5k).
"""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import types

HERE = Path(__file__).resolve().parent
FIT = HERE.parent
REPO = FIT.parents[3]
PY = '/Users/new/vitrea-w49/py/bin/python'
SCHEMA = 'w50-prefit-proof-1'
STANDING = ('identityDigestsGoldens', 'nativeArchive', 'negativeNeutralDiagnostic', 'newBedRendererAdapter',
            'numericalRehearsal', 'shaderCpuAgreement', 'referenceCompletion', 'repeatBar', 'dark05Bands',
            'active05ScratchBaselines')
DISCOVER = ('live-execution', 'live-roles', 'judge', 'fit', 'measurement', 'completion', 'references-r2')
SEVERITIES = ('P0', 'P1', 'P2', 'P3')
BLOCKING = ('P0', 'P1')
DISPOSITIONS = ('fixed', 'dismissed', 'deferred')


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(path): return json.loads(Path(path).read_text())


def source(path, name):
    module = types.ModuleType(name); module.__file__ = str(path)
    exec(compile(Path(path).read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


def require(condition, message):
    if not condition: raise AssertionError(message)


class Layout:
    """Where everything is. Defaults are the real tree; tests pass a synthetic repository."""

    def __init__(self, repo=REPO, *, fit=None, live=None, root=None, evidence=None, proofs=None, review=None,
                 standing=None, suites=None, python=PY, validate_body=None, discover=None, verify=None, builder=None):
        self.repo = Path(repo).resolve()
        self.fit = Path(fit or self.repo/FIT.relative_to(REPO)).resolve()
        self.live = Path(live or self.fit/'live-execution')
        chain = None
        if root is None or evidence is None: chain = source(self.live/'common.py', 'w50_live_run_chain')
        self.root = Path(root or chain.newest_root(self.live)).resolve()
        self.evidence = Path(evidence or chain.slot(self.root, 'prefit'))
        self.proofs = Path(proofs or self.fit/'live-run/prefit-proofs')
        self.review = Path(review or self.fit/'live-run/review-records.json')
        self.standing = standing or {kind: newest_proof(self.fit, kind) for kind in STANDING}
        self.python = python
        self.builder = Path(builder or __file__).resolve()
        self.suites = suites if suites is not None else (
            [(f'suite-{name}', self.fit/name, [python, '-I', '-B', '-m', 'unittest', 'discover', '-q', '-p', 'test_*.py'])
             for name in DISCOVER] +
            [('suite-owner-candidate-live-test', self.fit/'owner-candidate', [python, '-I', '-B', 'live-test.py'])])
        # The LIVE modules this run executes are pinned as the executionClosure proof's sources.
        self.used = []
        if validate_body is None:
            self.used.append(self.live/'authority.py')
            validate_body = source(self.live/'authority.py', 'w50_live_run_authority').validate_body
        if discover is None:
            self.used.append(self.live/'guard.py')
            discover = source(self.live/'guard.py', 'w50_live_run_guard').discover
        self.validate_body, self.discover, self.verify = validate_body, discover, verify
        self.mechanics = source(FIT.parent/'2026-10-08-w50-g1-current3/execution/dispatch.py', 'w50_live_run_mechanics')

    def pin(self, path):
        path = Path(path).resolve()
        return {'path': str(path.relative_to(self.repo)), 'sha256': sha(path)}

    def rel(self, path): return str(Path(path).resolve().relative_to(self.repo))


def newest_proof(fit, kind):
    """The newest generation of a standing proof: prefit-proofs-r<n> (highest n), else prefit-proofs."""
    folders = sorted(((int(p.name.rsplit('-r', 1)[1]), p) for p in Path(fit).glob('prefit-proofs-r*')
                      if re.fullmatch(r'prefit-proofs-r[0-9]+', p.name)), reverse=True)
    for _, folder in [*folders, (0, Path(fit)/'prefit-proofs')]:
        if (folder/f'{kind}.json').is_file(): return folder/f'{kind}.json'
    raise AssertionError(f'No standing {kind} proof')


def git(layout, *args, check=True):
    result = subprocess.run(['git', '-C', str(layout.repo), *args], capture_output=True, text=True)
    if check and result.returncode: raise AssertionError(f'git {args[0]} failed')
    return result


def commit(layout, value):
    require(isinstance(value, str) and re.fullmatch('[0-9a-f]{40}', value), 'A commit is a full 40-hex SHA')
    require(git(layout, 'cat-file', '-e', value+'^{commit}', check=False).returncode == 0, f'Unknown commit {value}')
    return value


def ancestor(layout, older, newer):
    return git(layout, 'merge-base', '--is-ancestor', older, newer, check=False).returncode == 0


class Proof:
    """One proof's checks, staged logs and write-once output (prefit-proofs/build.py's form)."""

    def __init__(self, layout, kind):
        self.layout, self.kind = layout, kind
        self.final = layout.proofs/'logs'/kind
        self.target = layout.proofs/f'{kind}.json'
        require(not self.final.exists(), f'Write-once: {layout.rel(self.final)} already exists')
        self.stage = layout.proofs/'logs'/f'.staging-{kind}-{os.getpid()}'
        self.stage.mkdir(parents=True)
        self.checks, self.failed = [], []

    def _log(self, name, raw):
        path = self.stage/name
        with path.open('xb') as handle: handle.write(raw)
        return path

    def function(self, cid, verifies, fn):
        try: summary, ok = fn(), True
        except Exception as error:
            summary, ok = {'error': f'{type(error).__name__}: {error}'}, False
        log = self._log(f'{cid}.json', (json.dumps(summary, indent=1, sort_keys=True, allow_nan=False)+'\n').encode())
        self._record(cid, verifies, ok, log, function=getattr(fn, '__name__', 'check'), summary=summary)

    def command(self, cid, verifies, argv, cwd):
        environment = {k: v for k, v in os.environ.items() if k not in ('FORCE_COLOR', 'VITREA_ALLOW_FALLBACK_ADAPTER')}
        environment['NO_COLOR'] = '1'
        result = subprocess.run(argv, cwd=cwd, env=environment, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        text = result.stdout.decode('utf-8', 'replace')
        ran = re.search(r'^Ran ([1-9][0-9]*) tests? in', text, re.M)
        ok = result.returncode == 0 and ran is not None and re.search(r'^OK( \(.*\))?$', text, re.M) is not None
        log = self._log(f'{cid}.log', result.stdout)
        self._record(cid, verifies, ok, log, command=[str(a) for a in argv], cwd=self.layout.rel(cwd),
                     exitCode=result.returncode, tests=int(ran[1]) if ran else 0)

    def _record(self, cid, verifies, ok, log, **fields):
        require(cid not in {c['id'] for c in self.checks}, f'Duplicate check id {cid}')
        self.checks.append({'id': cid, 'status': 'PASS' if ok else 'FAIL', 'verifies': verifies, **fields, 'log': str(log)})
        if not ok: self.failed.append(cid)

    def finish(self, establishes, boundary, sources):
        if self.failed:
            raise AssertionError(f'{self.kind} not written; failed checks {self.failed}; logs in {self.stage}')
        self.stage.rename(self.final)
        outputs = []
        for check in self.checks:
            check['log'] = self.layout.pin(self.final/Path(check['log']).name); outputs.append(check['log'])
        head = git(self.layout, 'rev-parse', 'HEAD').stdout.strip()
        pins, seen = [], set()
        for path in [self.layout.builder, *sources]:
            item = self.layout.pin(path)
            if item['path'] not in seen: seen.add(item['path']); pins.append(item)
        proof = {'schema': SCHEMA, 'kind': self.kind, 'status': 'PASS', 'establishes': establishes,
                 'boundary': boundary, 'builtFrom': {'gitHead': head, 'builder': self.layout.rel(self.layout.builder),
                 'python': sys.version.split()[0]}, 'checks': self.checks, 'sources': pins, 'outputs': outputs}
        with self.target.open('x') as handle: handle.write(json.dumps(proof, indent=1, allow_nan=False)+'\n')
        validate_proof(self.layout, self.kind)
        return self.layout.pin(self.target)


def validate_proof(layout, kind, path=None):
    """LIVE's own proof validator (live-execution/prefit.py, byte-identical to current3's)."""
    path = path or layout.proofs/f'{kind}.json'
    prefit = source(layout.live/'prefit.py', 'w50_live_run_prefit_'+kind)
    prefit.validate_proof(load(path), kind, str(layout.repo))
    return layout.pin(path)


def sealed_root(layout):
    require(Path(str(layout.root)+'.sha256').is_file(), 'The LIVE root is not sealed; run prefit only after the seal')
    doc = layout.mechanics.sealed(layout.root)
    return doc, [layout.pin(layout.root), layout.pin(str(layout.root)+'.sha256')]


def _existing(layout, kind, root_pins):
    """A proof from an earlier run is reused only if it validates and pins this root."""
    if not (layout.proofs/f'{kind}.json').exists(): return None
    pin = validate_proof(layout, kind)
    require(all(p in load(layout.proofs/f'{kind}.json')['sources'] for p in root_pins),
            f'An existing {kind} proof pins another root')
    return pin


def execution_closure(layout, doc, root_pins):
    found = _existing(layout, 'executionClosure', root_pins)
    if found: return found
    proof = Proof(layout, 'executionClosure')
    def root_seal():
        side = Path(str(layout.root)+'.sha256').read_text()
        require(side == f'{sha(layout.root)}  {layout.root.name}\n', 'Root sidecar differs from its bytes')
        return {'root': layout.rel(layout.root), 'sha256': sha(layout.root)}
    def validate_body():
        require(layout.validate_body(layout.root, doc) is not None, 'validate_body returned nothing')
        return {'status': 'PASS', 'inputs': len(doc['inputs']), 'closureSources': len(doc['closure']['sources']),
                'instruments': sorted(doc['instruments'])}
    def fresh_discovery():
        found = layout.discover(layout.repo, layout.repo/doc['probe']['path'], doc['closure']['sources'])
        require(found == doc['closure'], 'A fresh discovery differs from root.closure')
        return {'equal': True, 'sources': len(found['sources']), 'probeSha256': found.get('probeSha256')}
    proof.function('root-seal', 'The root is the newest sealed root of the LIVE chain (common.newest_root) and its '
                   'sidecar names its bytes.', root_seal)
    proof.function('validate-body', 'authority.validate_body admits the sealed root.', validate_body)
    proof.function('fresh-discovery', 'A fresh guard.discover of the root probe equals root.closure (sources and environment).',
                   fresh_discovery)
    suites = []
    for cid, cwd, argv in layout.suites:
        proof.command(cid, f'The {layout.rel(cwd)} suite passes on the tree the root seals.', argv, cwd)
        suites += sorted(Path(cwd).glob('test_*.py')) + [Path(cwd)/a for a in argv if str(a).endswith('.py') and (Path(cwd)/a).is_file()]
    return proof.finish(
        'The sealed LIVE root admits its body, its probe still exercises exactly root.closure, and every LIVE-related '
        'suite passes on the sealed tree (charter DL5 (a); DL5 review requirement before first use).',
        'Source and synthetic-suite checks only; no capture, candidate, native read or statistic.',
        [layout.root, Path(str(layout.root)+'.sha256'), *layout.used, layout.repo/doc['probe']['path'], *suites])


def _todo(value):
    if isinstance(value, str): return 'TODO' in value
    if isinstance(value, dict): return any(_todo(k) or _todo(v) for k, v in value.items())
    if isinstance(value, list): return any(_todo(v) for v in value)
    return False


def root_bound(layout, doc):
    """Every repository file the root binds: closure sources, instruments and tracked inputs.
    An untracked input is admitted only as a liveInputs copy bound to its committed archive."""
    paths = set(doc['closure']['sources'])
    for role in doc['instruments'].values(): paths |= {role['entrypoint']['path'], role['config']['path']}
    live_copies = {item['path'] for item in doc.get('liveInputs', [])}
    for item in doc['inputs']:
        if item['path'] in live_copies: continue
        paths.add(item['path'])
    return sorted(paths)


def independent_review(layout, doc, root_pins):
    found = _existing(layout, 'independentReview', root_pins)
    if found: return found
    record = load(layout.review)
    require(not _todo(record), f'{layout.rel(layout.review)} still has a TODO; fill in every round first')
    proof = Proof(layout, 'independentReview')
    rounds = record.get('rounds')
    def shape():
        require(record.get('schema') == 'w50-live-review-records-1', 'Unknown review record schema')
        require(isinstance(rounds, list) and rounds, 'No review round')
        require(len({r.get('id') for r in rounds}) == len(rounds), 'Duplicate round id')
        return {'rounds': len(rounds)}
    proof.function('record-shape', 'The review record is one complete, TODO-free document.', shape)
    for index, item in enumerate(rounds if isinstance(rounds, list) else []):
        def check(item=item, index=index):
            base, head = (commit(layout, item['range'][k]) for k in ('base', 'head'))
            require(ancestor(layout, base, head) and ancestor(layout, head, 'HEAD'), 'Round range is not on this history')
            if index: require(ancestor(layout, rounds[index-1]['range']['head'], head), 'Rounds are out of order')
            require(isinstance(item.get('reviewers'), list) and item['reviewers'] and
                    all(isinstance(r, str) and r for r in item['reviewers']), 'Round names no reviewer')
            findings = item.get('findings')
            require(isinstance(findings, list), 'Round lists no findings (an empty list is a clean round)')
            counts = {s: 0 for s in SEVERITIES}
            for finding in findings:
                require(finding.get('severity') in SEVERITIES and finding.get('disposition') in DISPOSITIONS and
                        isinstance(finding.get('summary'), str) and finding['summary'], 'Finding needs severity, summary, disposition')
                counts[finding['severity']] += 1
                if finding['disposition'] == 'fixed':
                    fixes = finding.get('fixedBy')
                    require(isinstance(fixes, list) and fixes, 'A fixed finding names its fixing commits')
                    for fix in fixes:
                        commit(layout, fix)
                        require(ancestor(layout, base, fix) and ancestor(layout, fix, 'HEAD'), 'A fix is not after its round on this history')
                else:
                    require(finding['severity'] not in BLOCKING or finding['disposition'] == 'dismissed',
                            'A P0/P1 is fixed or dismissed, never deferred')
                    require(isinstance(finding.get('reason'), str) and finding['reason'], 'A dismissed or deferred finding states why')
            if item.get('counts') is not None: require(item['counts'] == counts, 'Stated counts differ from the findings')
            return {'base': base, 'head': head, 'reviewers': len(item['reviewers']), 'findings': counts}
        proof.function(f'round-{item.get("id")}', f'Round {item.get("id")}: range, reviewers, findings and fixing commits verify.', check)
    def converged():
        last = rounds[-1]
        require(not any(f['severity'] in BLOCKING for f in last['findings']), 'The last round has a P0/P1: another round is due')
        head = last['range']['head']; fixes = 0
        for item in rounds[:-1]:
            for finding in item['findings']:
                for fix in finding.get('fixedBy', []):
                    require(ancestor(layout, fix, head), 'An earlier fix was never reviewed by the last round')
                    fixes += 1
        return {'lastRound': last['id'], 'lastHead': head, 'earlierFixesReviewed': fixes}
    proof.function('converged', 'The last round found no P0/P1, and it reviewed every earlier round\'s fixes.', converged)
    def covered():
        head = rounds[-1]['range']['head']; paths = root_bound(layout, doc)
        untracked = git(layout, 'ls-files', '--error-unmatch', '--', *paths, check=False)
        require(untracked.returncode == 0, 'A root-bound file is not tracked')
        changed = git(layout, 'diff', '--name-only', head, '--', *paths).stdout.split()
        require(not changed, f'{len(changed)} root-bound files changed after the last reviewed head')
        return {'rootBoundFiles': len(paths), 'changedAfterLastHead': 0, 'lastHead': head}
    proof.function('root-bound-reviewed', 'No closure source, instrument or tracked input changed after the last reviewed head '
                   '(worktree included).', covered)
    return proof.finish(
        'Every LIVE review round is recorded with its range, reviewers, findings by severity and dispositions with fixing '
        'commits; the last round converged and reviewed every byte the root binds (charter DL5: an independent review of '
        'the dispatcher before first use).',
        'Git history and the committed review record only; no capture, candidate, native read or statistic.',
        [layout.review, layout.root, Path(str(layout.root)+'.sha256')])


def write_sealed(path, value):
    path = Path(path)
    with path.open('x') as handle:
        json.dump(value, handle, indent=2, allow_nan=False); handle.write('\n'); handle.flush(); os.fsync(handle.fileno())
    with Path(str(path)+'.sha256').open('x') as handle:
        handle.write(f'{sha(path)}  {path.name}\n'); handle.flush(); os.fsync(handle.fileno())
    return path


def build(layout=None):
    layout = layout or Layout()
    require(not layout.evidence.exists() and not Path(str(layout.evidence)+'.sha256').exists(),
            'pre-fit-evidence.json already exists; it is written once')
    doc, root_pins = sealed_root(layout)
    measurement = load(layout.mechanics.checked(layout.repo, doc['instruments']['measurement']['config']))
    references = measurement.get('completedReferences')
    layout.mechanics.checked(layout.repo, references)
    require(references in doc['inputs'], 'The completed inventory is not a root input')
    proofs = {kind: validate_proof(layout, kind, path) for kind, path in layout.standing.items()}
    proofs['executionClosure'] = execution_closure(layout, doc, root_pins)
    proofs['independentReview'] = independent_review(layout, doc, root_pins)
    order = layout.mechanics.PROOFS
    require(set(proofs) == set(order), 'All twelve pre-fit proofs are required')
    evidence = {'schema': 'w50-g1-pre-fit-evidence-1', 'partTwoSha256': doc['partTwo']['sha256'],
                'sources': root_pins, 'executionClosure': doc['closure'], 'references': references,
                'evidence': {kind: proofs[kind] for kind in order}}
    write_sealed(layout.evidence, evidence)
    pinned = layout.verify(layout.root) if layout.verify else None
    return {'preFitEvidence': layout.pin(layout.evidence), 'verifyPrefit': pinned,
            'proofs': {k: v['sha256'] for k, v in evidence['evidence'].items()}}
