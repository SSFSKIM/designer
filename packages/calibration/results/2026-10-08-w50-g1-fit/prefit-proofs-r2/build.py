#!/Users/new/vitrea-w49/py/bin/python -I -B
"""Build one W50 G1 pre-fit proof (`w50-prefit-proof-1`) by re-executing its checks.

r2: prefit-proofs/build.py with only its paths changed, for the DL5l recovery after the owner
referee fix 7e621f344 (DL5m 1). It reads the r2 completed inventory
(live-inputs/completed-references-r2.json) and the r2 assembly (completion/registered-2), and
writes proofs and logs here, beside the superseded proofs it never touches. Prose that named
the superseded inventory's hash names no hash. Only the kinds whose pins moved are rebuilt
(active05ScratchBaselines, dark05Bands, referenceCompletion, repeatBar); the other proofs in
prefit-proofs/ stand. The original description follows.

Usage, from anywhere:  /Users/new/vitrea-w49/py/bin/python -I -B build.py <kind> [--dry]

--dry runs the same checks with logs in a temporary directory outside the repository and
writes nothing; it exists so the builder can be exercised before its bytes are frozen.

Each kind re-executes cheap checks over evidence that already exists (unit suites, recorded
hash chains, deterministic replays with recorded expected outputs) and writes a proof only if
every check returns PASS in this run. Logs go to logs/<kind>/ and are pinned as outputs; the
evidence each check rests on is pinned as sources. Both the proof and its logs are write-once:
an existing proof or log directory refuses, and a failing run leaves its staging directory for
inspection and writes no proof. Missing evidence is reported, never substituted.

DL5k: nothing here opens a blind export, the plaintext blind archive or a native exposure
checkpoint. Archive assets are checked only by SHA-256 of their compressed bytes; native
readings are read only from the committed exposed (calibration/validation) reader outputs; blind
reference rows are checked for being identity-only without reading or printing any value. No
capture, candidate render or sealed one-shot read is rerun. Logs carry counts, hashes and
pass/fail facts, never a held statistic.

executionClosure and independentReview are not built here: they depend on the LIVE root.
"""
from __future__ import annotations

import gzip
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import types

HERE = Path(__file__).resolve().parent
FIT = HERE.parent
RES = FIT.parent
CAL = RES.parent
REPO = CAL.parents[1]
G0 = RES/'2026-10-08-w50-g0-declaration'
SIT = RES/'2026-10-08-w50-g1-sitting'
CUR3 = RES/'2026-10-08-w50-g1-current3'
CAN3 = RES/'2026-10-08-w50-g1-canonical3'
GROUND = RES/'2026-10-08-w50-grounding'
PY = '/Users/new/vitrea-w49/py/bin/python'
LIVE_REFS = FIT/'live-inputs/completed-references-r2.json'
REGISTERED = FIT/'completion/registered-2'
LIVE_CURRENT = FIT/'live-inputs/completed-current.json'
G0_MERGE = 'f608255abc7182dd3f69b0fe7e4d8fcd7e72f057'
# DL5k: these external roots hold raw/blind native data; nothing here reads inside them.
GUARDED = ('/Users/new/vitrea-w50/g1a-', '/Users/new/vitrea-w50/native-')
SCHEMA = 'w50-prefit-proof-1'
CHARTER = 'docs/doperpowers/specs/2026-10-08-w50-dark-low-end-response.md'
CLAIMS = 'docs/doperpowers/specs/c9a-fidelity-claims.md'


def sha_bytes(raw): return hashlib.sha256(raw).hexdigest()
def sha(path): return sha_bytes(Path(path).read_bytes())
def rel(path): return str(Path(path).resolve().relative_to(REPO))
def pin(path): return {'path': rel(path), 'sha256': sha(path)}
def load(path): return json.loads(Path(path).read_bytes())
def gunzip(path): return gzip.decompress(Path(path).read_bytes())


def module(path, name):
    m = types.ModuleType(name); m.__file__ = str(path); sys.modules[name] = m
    exec(compile(Path(path).read_bytes(), str(path), 'exec', dont_inherit=True), m.__dict__)
    return m


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def guarded(path):
    return str(path).startswith(GUARDED)


def verify_file(path, digest, repo=REPO):
    path = Path(path) if Path(path).is_absolute() else Path(repo)/path
    require(not guarded(path), f'DL5k-guarded path is not opened here: {path}')
    require(path.is_file() and sha(path) == digest, f'Changed or missing pinned bytes: {path}')


def pins_in(value):
    """Every {'path','sha256'} pin and every {path: sha} closure map inside a root document."""
    out = []
    if isinstance(value, dict):
        if isinstance(value.get('path'), str) and isinstance(value.get('sha256'), str):
            out.append((value['path'], value['sha256']))
        for k, v in value.items():
            if k in ('sources',) and isinstance(v, dict) and all(isinstance(x, str) for x in v.values()):
                out.extend(v.items())
            else:
                out.extend(pins_in(v))
    elif isinstance(value, list):
        for v in value: out.extend(pins_in(v))
    return out


def verify_root(path, label):
    """A sealed root: its sidecar names its bytes, and every pin inside still matches."""
    side = Path(str(path)+'.sha256').read_text().split()
    require(side[0] == sha(path), f'{label}: sidecar differs from root bytes')
    doc = load(path)
    pins = pins_in(doc)
    repo_pins = external = skipped = 0
    for p, digest in pins:
        if guarded(p):
            skipped += 1; continue
        verify_file(p, digest)
        if Path(p).is_absolute(): external += 1
        else: repo_pins += 1
    return {'root': label, 'sha256': side[0], 'repoPinsVerified': repo_pins,
            'externalPinsVerified': external, 'guardedPinsNotOpened': skipped}


# ------------------------------------------------------------------------------------------
class Run:
    def __init__(self, kind, dry=False):
        self.kind, self.dry = kind, dry
        self.final = HERE/'logs'/kind
        require(not self.final.exists(), f'Write-once: {rel(self.final)} already exists')
        require(not (HERE/f'{kind}.json').exists(), f'Write-once: {kind}.json already exists')
        if dry:
            self.stage = Path(tempfile.mkdtemp(prefix=f'w50-prefit-dry-{kind}-'))
        else:
            self.stage = HERE/'logs'/f'.staging-{kind}-{os.getpid()}'
            self.stage.mkdir(parents=True)
        self.checks, self.failed = [], []

    def _log(self, name, raw):
        path = self.stage/name
        with path.open('xb') as handle: handle.write(raw)
        return path

    def command(self, cid, verifies, argv, cwd, expect=(), env=None):
        environment = {k: v for k, v in os.environ.items()
                       if k not in ('FORCE_COLOR', 'VITREA_ALLOW_FALLBACK_ADAPTER')}
        environment.update(NO_COLOR='1', **(env or {}))
        result = subprocess.run(argv, cwd=cwd, env=environment, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        text = result.stdout.decode('utf-8', 'replace')
        log = self._log(f'{cid}.log', result.stdout)
        matched = [m.group(0) for e in expect for m in [re.search(e, text, re.M)] if m]
        ok = result.returncode == 0 and len(matched) == len(expect)
        self._record(cid, verifies, ok, log, command=[str(a) for a in argv],
                     cwd=rel(cwd) if Path(cwd).resolve().is_relative_to(REPO) else str(cwd),
                     exitCode=result.returncode, matched=matched)

    def function(self, cid, verifies, fn):
        try:
            summary, ok = fn(), True
        except Exception as error:  # recorded as FAIL, never swallowed into a PASS
            summary, ok = {'error': f'{type(error).__name__}: {error}'}, False
        raw = (json.dumps(summary, indent=1, sort_keys=True, allow_nan=False)+'\n').encode()
        log = self._log(f'{cid}.json', raw)
        self._record(cid, verifies, ok, log, function=fn.__name__, summary=summary)

    def _record(self, cid, verifies, ok, log, **fields):
        require(cid not in {c['id'] for c in self.checks}, f'Duplicate check id {cid}')
        status = 'PASS' if ok else 'FAIL'
        print(f'[{self.kind}] {cid}: {status}', flush=True)
        self.checks.append({'id': cid, 'status': status, 'verifies': verifies, **fields,
                            'log': str(log)})
        if not ok: self.failed.append(cid)

    def finish(self, establishes, sources, boundary):
        if self.failed or self.dry:
            print(json.dumps({'kind': self.kind, 'status': 'NOT_WRITTEN', 'dry': self.dry,
                              'failed': self.failed, 'logs': str(self.stage)}, indent=1))
            return 1 if self.failed else 0
        self.stage.rename(self.final)
        outputs = []
        for check in self.checks:
            path = self.final/Path(check['log']).name
            check['log'] = pin(path); outputs.append(check['log'])
        head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=REPO, capture_output=True,
                              text=True, check=True).stdout.strip()
        source_pins, seen = [], set()
        for path in [Path(__file__), *sources]:
            item = pin(path)
            if item['path'] not in seen: seen.add(item['path']); source_pins.append(item)
        proof = {'schema': SCHEMA, 'kind': self.kind, 'status': 'PASS',
                 'establishes': establishes, 'boundary': boundary,
                 'builtFrom': {'gitHead': head, 'builder': rel(__file__),
                               'python': sys.version.split()[0]},
                 'checks': self.checks, 'sources': source_pins, 'outputs': outputs}
        raw = (json.dumps(proof, indent=1, allow_nan=False)+'\n').encode()
        target = HERE/f'{self.kind}.json'
        with target.open('xb') as handle: handle.write(raw)
        prefit = module(CUR3/'execution/prefit.py', 'w50_current3_prefit_validator')
        prefit.validate_proof(load(target), self.kind, str(REPO))
        print(json.dumps({'kind': self.kind, 'status': 'PASS', 'proof': rel(target),
                          'sha256': sha(target), 'checks': len(self.checks),
                          'validateProof': 'current3 prefit.validate_proof PASS'}, indent=1))
        return 0


def py_test(run, cid, verifies, path, tests):
    run.command(cid, verifies, [PY, '-I', '-B', str(path)], cwd=Path(path).parent,
                expect=[rf'^Ran {tests} tests? in', r'^OK$'])


def node_test(run, cid, verifies, path, tests, extra=()):
    run.command(cid, verifies, ['pnpm', 'exec', 'tsx', '--test', *extra, str(path)], cwd=CAL,
                expect=[rf'^ℹ pass {tests}$', r'^ℹ fail 0$'])


def vitest(run, cid, verifies, package_dir, files, tests, extra=()):
    run.command(cid, verifies, ['pnpm', 'exec', 'vitest', 'run', *files, *extra], cwd=package_dir,
                expect=[rf'Tests\s+{tests} passed', r'Test Files\s+\d+ passed'])


_COMPLETED = []


def completed():
    """The 284 MB completed inventory, loaded once per run; checks never mutate it."""
    if not _COMPLETED: _COMPLETED.append(load(LIVE_REFS))
    return _COMPLETED[0]


def key(cell):
    return tuple(cell[k] for k in ('profile', 'renderer', 'scene', 'statistic'))


# ------------------------------------------------------------------------------------------
def native_archive(run):
    attempt, pack = load(SIT/'attempt-02-complete.json'), load(SIT/'pack.json')
    local, remote = load(SIT/'local-verification.json'), load(SIT/'release-verification.json')
    sums = dict(reversed(line.split()) for line in (SIT/'SHA256SUMS').read_text().splitlines())

    py_test(run, 'archive-wrapper-synthetic-tests',
            'The G1a archive wrapper refuses incomplete admission, changed bridge reports and '
            'unbridged closes on synthetic inputs (§5.217 §8: 11 tests).',
            SIT/'test_archive_finished.py', 11)

    def sitting_records_agree():
        archive = attempt['archive']
        require(attempt['driverExitCode'] == 0 and attempt['ownedWakeAssertionExitCode'] == 0,
                'driver/wake assertion exit')
        require(len(attempt['admissions']) == 40 and attempt['frames'] == 1600 and
                sum(a['frames'] for a in attempt['admissions']) == 1600, '40 admitted runs/1600 frames')
        require(len(attempt['bridges']) == 16 and all(b['agrees'] for b in attempt['bridges']),
                '16 bridge reports agree')
        require(attempt['bridgeStatus'] == 'bridged' and attempt['restore']['restored'] is True,
                'bridged and restored')
        require(attempt['partOneSha256'] == sha(G0/'declaration.json') == pack['declarationSha256'],
                'part 1 bound')
        require(attempt['partTwoSha256'] == sha(G0/'fit-declaration.json'), 'part 2 bound')
        digest = pack['sha256']
        require(archive['sha256'] == digest == local['sha256'] and sums[pack['asset']] == digest,
                'archive SHA agrees across records')
        require(pack['indexSha256'] == local['indexSha256'] and pack['frames'] == local['frames'] == 1600
                and pack['files'] == local['files'] == 2624, 'index/frames/files agree')
        require(local['verified'] is True and local['bridgeStatus'] == pack['bridgeStatus'] == 'bridged'
                and local['unbridgedClosingPasses'] == pack['unbridgedClosingPasses'] == [],
                'local replay bridged with no unbridged close')
        failed = attempt['failedAttemptArchive']
        require(sums[failed['asset']] == failed['sha256'], 'failed attempt asset retained by hash')
        assets = {a['name']: a for a in remote['release']['assets']}
        require(assets[pack['asset']]['digest'] == 'sha256:'+digest and
                assets[pack['asset']]['size'] == pack['bytes'], 'release record names the asset')
        require(remote['release']['targetCommitish'] == G0_MERGE, 'release targets sealed G0 merge')
        return {'admittedRuns': 40, 'frames': 1600, 'bridgesAgree': 16, 'archiveSha256': digest,
                'indexSha256': pack['indexSha256'], 'files': pack['files'],
                'failedAttemptSha256': failed['sha256']}
    run.function('sitting-records-agree', 'attempt-02-complete, pack, local and release '
                 'verification records name one admitted 1,600-frame bridged archive (§5.217 §8-9).',
                 sitting_records_agree)

    def release_assets_local_sha256():
        out = {}
        for directory in ('/Users/new/vitrea-w50/w50-release', '/Users/new/vitrea-w50/w50-release-fetched'):
            d = Path(directory)
            require((d/'SHA256SUMS').read_bytes() == (SIT/'SHA256SUMS').read_bytes(), 'SHA256SUMS bytes')
            for name, digest in sums.items():
                require(sha(d/name) == digest, f'{directory}/{name}')  # compressed bytes only
            out[directory] = sorted(sums.values())
        return {'assetsVerifiedByCompressedSha256': out, 'decoded': False}
    run.function('release-assets-local-sha256', 'Both local copies of the release assets hash to '
                 'SHA256SUMS; compressed bytes only, nothing decoded (DL5k).', release_assets_local_sha256)

    def release_remote_redownload():
        view = subprocess.run(['gh', 'release', 'view', 'w50-archive', '--repo', 'SSFSKIM/designer',
                               '--json', 'assets,tagName,targetCommitish'],
                              capture_output=True, text=True, check=True)
        listed = {a['name']: a['digest'] for a in json.loads(view.stdout)['assets']}
        for name, digest in sums.items():
            require(listed[name] == 'sha256:'+digest, f'remote digest {name}')
        scratch = Path(tempfile.mkdtemp(prefix='w50-prefit-release-'))
        try:
            subprocess.run(['gh', 'release', 'download', 'w50-archive', '--repo', 'SSFSKIM/designer',
                            '--dir', str(scratch)], check=True, capture_output=True)
            got = {p.name: sha(p) for p in scratch.iterdir()}
        finally:
            shutil.rmtree(scratch)
        for name, digest in sums.items():
            require(got[name] == digest, f'downloaded {name}')
        require(got['SHA256SUMS'] == sha(SIT/'SHA256SUMS'), 'downloaded SHA256SUMS bytes')
        return {'remoteDigests': listed, 'downloadedSha256': got, 'decoded': False}
    run.function('release-remote-redownload', 'A fresh download of release w50-archive matches '
                 'SHA256SUMS and the committed record (compressed bytes only).', release_remote_redownload)

    def identification_binds_archive():
        root = verify_root(FIT/'native/instrument-root.json', 'native identification root')
        doc = load(FIT/'native/instrument-root.json')
        require(doc['inputs']['pack']['sha256'] == sha(SIT/'pack.json'), 'root pins pack.json')
        exposed = load(FIT/'identification/native-exposed.json')
        src = exposed['source']
        require(sha(FIT/'identification/native-read.json.gz') == src['sha256'], 'native-read gz')
        read = json.loads(gunzip(FIT/'identification/native-read.json.gz'))
        require(sha_bytes(gzip.decompress((FIT/'identification/native-read.json.gz').read_bytes()))
                == src['decodedSha256'], 'native-read decoded')
        require(read['instrumentRootSha256'] == root['sha256'] == exposed['instrumentRootSha256'],
                'one identification root')
        require(sorted(r['role'] for r in read['roles']) == ['calibration', 'validation'],
                'only exposed roles were read')
        for r in read['exports']:
            require(pack['exportIndexSha256'][r['role']] == r['indexSha256'], 'export index bound')
        return {**root, 'rolesRead': ['calibration', 'validation'], 'blindRoleRead': False,
                'exportIndexSha256': pack['exportIndexSha256']}
    run.function('identification-binds-archive', 'The sealed identification root pins the archive '
                 'pack record, and its read opened only the calibration/validation exports.',
                 identification_binds_archive)

    return run.finish(
        'The G1a native sitting is archived by hash before fitting (charter "Archive by hash before '
        'fitting"; §5.217 §8-9): 40 admitted runs, 1,600 frames, all 16 bridges agree, published '
        'as release w50-archive and re-verified here by compressed-asset SHA-256, with the '
        'identification read bound to the same archive record.',
        [SIT/n for n in ('archive_finished.py', 'test_archive_finished.py', 'attempt-02-complete.json',
                         'pack.json', 'local-verification.json', 'release-verification.json',
                         'SHA256SUMS', 'release-notes.txt')] +
        [G0/'declaration.json', G0/'fit-declaration.json', FIT/'native/instrument-root.json',
         FIT/'native/instrument-root.json.sha256', FIT/'identification/native-read.json.gz',
         FIT/'identification/native-exposed.json'],
        'Hash verification only: no archive was decompressed or extracted and no blind frame, '
        'thumbnail or statistic was opened (DL5k).')


# ------------------------------------------------------------------------------------------
def repeat_bar(run):
    exposed = load(FIT/'identification/native-exposed.json')
    for name, tests in (('test_statistics.py', 10), ('test_reader.py', 10), ('test_bootstrap.py', 11)):
        py_test(run, 'native-'+name[5:-3]+'-tests', f'Native reader {name} (synthetic inputs).',
                FIT/'native'/name, tests)

    def native_read_bytes():
        read = json.loads(gunzip(FIT/'identification/native-read.json.gz'))
        for role in ('calibration', 'validation'):
            projection = json.loads(gunzip(FIT/f'identification/native-{role}.json.gz'))
            require([r for r in read['roles'] if r['role'] == role] == [projection],
                    f'{role} projection equals the read')
        require(read['status'] == 'READY' and read['ready'] is True, 'read READY')
        return {'status': read['status'], 'roleProjectionsExact': ['calibration', 'validation']}
    run.function('native-read-bytes', 'The archived identification read is READY and its per-role '
                 'projections are exact.', native_read_bytes)

    def new_bed_bar_recomputed():
        np = __import__('numpy')
        counts = {'statistics': 0, 'required': 0, 'emptySupport': 0}
        max_required_spread, bars = 0.0, set()
        for role in exposed['roles']:
            require(role['ready'] is True and role['stops'] == [], f'{role["role"]} ready, no stop')
            for cell in role['cells']:
                for name, stat in cell['statistics'].items():
                    counts['statistics'] += 1
                    values, rep = stat.get('runValues'), stat.get('repeat')
                    if stat.get('measurementStatus') == 'UNMEASURED_EMPTY_SUPPORT':
                        require(not stat['required'] and rep is None, 'empty support is optional (DL5b)')
                        counts['emptySupport'] += 1; continue
                    if rep is not None and 'spreadLinear' in rep:
                        spread, step = float(np.ptp(np.asarray(values, float))), rep['codeStepLinear']
                        want = {'spreadLinear': spread, 'spreadCodes': spread/step,
                                'barLinear': max(.5*step, .5*spread), 'barCodes': max(.5, .5*spread/step),
                                'passes': bool(spread/step <= 1)}
                        spread_codes, bar_codes = [spread/step], [want['barCodes']]
                    else:
                        spread = np.ptp(np.asarray(values, float), axis=0)
                        want = {'spreadCodes': spread.tolist(), 'barCodes': np.maximum(.5, spread/2).tolist(),
                                'passes': bool(np.all(spread <= 1))}
                        spread_codes, bar_codes = np.ravel(spread).tolist(), np.ravel(want['barCodes']).tolist()
                    for k, v in want.items():
                        require(rep[k] == v, f'{cell["id"]}/{name}/{k} recomputes')
                    if stat['required']:
                        counts['required'] += 1
                        require(rep['passes'], f'required repeat stop {cell["id"]}/{name}')
                        max_required_spread = max(max_required_spread, *spread_codes)
                        bars.update(bar_codes)
        require(bars == {0.5}, 'every required bar is the 0.5-code floor')
        require(max_required_spread < 1, 'no required spread reaches the 1-code stop')
        return {**counts, 'requiredBarsCodes': sorted(bars),
                'maxRequiredSpreadBelowOneCode': True, 'maxRequiredSpreadCodes': max_required_spread}
    run.function('new-bed-bar-recomputed', 'Every exposed new-bed statistic\'s spread, bar '
                 '(max(0.5, half spread)) and 1-code stop recompute from its three run values; all '
                 'required bars are 0.5 code (charter landing rule 1; §5.217 §10).', new_bed_bar_recomputed)

    def new_bed_budgets_from_bar():
        native = {(c['profile'], c['scene'], n): s['repeat']
                  for r in exposed['roles'] for c in r['cells'] for n, s in c['statistics'].items()}
        counts = {}
        for row in completed()['cells']:
            if not row['scene'].startswith('cell-') or row['role'] == 'blind': continue
            counts[row['status']] = counts.get(row['status'], 0)+1
            if row['status'] != 'MEASURED': continue
            rep = native[(row['profile'], row['scene'], row['statistic'])]
            require(row['nativeRepeat'] == rep, f'{key(row)} carries its native repeat')
            if row['statistic'] == 'T1-full-silhouette':
                want = max(rep['codeStepLinear'], 2*rep['barLinear'])
            else:
                bars = rep['barCodes'] if isinstance(rep['barCodes'], list) else [rep['barCodes']]
                want = max(max(1, 2*b) for b in bars)
                require(len({max(1, 2*b) for b in bars}) == 1, 'equal per-channel budget')
            require(row['B'] == want, f'{key(row)} B follows its own bar')
        return {'newBedExposedRowsByStatus': counts}
    run.function('new-bed-budgets-from-bar', 'Every exposed new-bed reference row carries its own '
                 'native repeat and B = max(1 code, 2*bar) (T1: max(code step, 2*bar)).',
                 new_bed_budgets_from_bar)

    py_test(run, 'canonical-statistics-tests', 'Canonical seven-run repeat-bar rules (synthetic).',
            FIT/'references-r2/test_statistics.py', 6)

    def canonical_bars_recomputed():
        stats = module(FIT/'references-r2/statistics.py', 'w50_prefit_r2_statistics')
        rows = checked = 0
        for row in completed()['cells']:
            readings = row.get('canonicalReadings')
            if row['role'] == 'blind' or not readings: continue
            rows += 1
            for name, item in readings.items():
                if item['status'] != 'MEASURED': continue
                rep = item['repeat']
                again = stats.repeat_bar(item['repeatValues'], units=item['units'],
                                         published_mean=rep['publishedNativeInteriorMean'])
                require(again == rep and item['B'] == rep['B'], f'{key(row)}/{name} bar recomputes')
                checked += 1
            if 'perFieldBudgets' in row:
                for field in row['perFieldBudgets'].values():
                    require(field['B'] == readings[field['statistic']]['B'], f'{key(row)} field budget')
            elif row['statistic'] in readings and row['status'] == 'MEASURED':
                require(row['B'] == readings[row['statistic']]['B'], f'{key(row)} B is its own bar')
        return {'canonicalRowsWithReadings': rows, 'readingsRecomputed': checked}
    run.function('canonical-bars-recomputed', 'Every canonical reference reading\'s seven-run bar '
                 'and B recompute from its own repeat values (references-r2 rule).', canonical_bars_recomputed)

    return run.finish(
        'Bar = half the largest admitted run-to-run separation, floored at 0.5 code; a spread over '
        '1 code in a required population stops the fit (charter landing rule 1 and the sitting '
        'section). Recomputed here from the exposed identification read: no required stop, every '
        'required bar 0.5 code; each reference row\'s B follows its own bar.',
        [FIT/'native/statistics.py', FIT/'native/reader.py', FIT/'native/test_statistics.py',
         FIT/'native/test_reader.py', FIT/'native/test_bootstrap.py',
         FIT/'identification/native-read.json.gz', FIT/'identification/native-calibration.json.gz',
         FIT/'identification/native-validation.json.gz', FIT/'identification/native-exposed.json',
         FIT/'references-r2/statistics.py', FIT/'references-r2/test_statistics.py',
         FIT/'completion/assembler.py', LIVE_REFS],
        'Exposed calibration/validation readings only; the 112 blind cells were not opened.')


# ------------------------------------------------------------------------------------------
def reference_completion(run):
    archive = load(REGISTERED/'evidence/archive.json')
    binding_path = REGISTERED/'binding.json'

    def archive_bytes():
        target = archive['completedReferences']
        raw = gunzip(REGISTERED/'evidence/completed-references.json.gz')
        require(sha(REGISTERED/'evidence/completed-references.json.gz') ==
                target['archive']['sha256'], 'archive gz')
        require(sha_bytes(raw) == target['original']['sha256'] == sha(LIVE_REFS) ==
                sha(target['original']['path']), 'archive, live copy and original are one inventory')
        require(len(raw) == target['original']['bytes'], 'byte length')
        require(sha(binding_path) == archive['binding']['sha256'], 'binding bytes')
        require(sha(REGISTERED/'evidence/artifacts.tar.gz') ==
                archive['artifacts']['archive']['sha256'], 'artifact archive')
        return {'completedReferencesSha256': sha(LIVE_REFS), 'bytes': len(raw),
                'bindingSha256': archive['binding']['sha256']}
    run.function('archive-bytes', 'The archived completed inventory, its gitignored live copy '
                 'and the external original are byte-identical.', archive_bytes)

    def registered_revalidation():
        binding = load(binding_path)
        for path, digest in binding['sourcePins'].items(): verify_file(path, digest)
        bound = module(FIT/'completion/bound.py', 'w50_prefit_bound')
        bundle_path = Path(archive['bundle']['path'])
        require(sha(bundle_path) == archive['bundle']['sha256'], 'bundle bytes')
        bundle = load(bundle_path)
        require(sha_bytes((json.dumps(bundle['completed'], indent=2, allow_nan=False)+'\n').encode())
                == sha(LIVE_REFS), 'bundle carries the completed inventory')
        result = bound.validate_registered(REPO, binding, bundle)
        require(result['status'] == 'REFERENCE_VALIDATION_ONLY', 'validator ran')
        return {'result': result['status'], 'validator': result['validator'],
                'deterministicReassembly': 'EQUAL', 'counts': bundle['counts']}
    run.function('registered-revalidation', 'bound.validate_registered re-derives the bundle '
                 'deterministically from the registered evidence and passes the strict pre-fit '
                 'completion validator (exemptions, DL5b/c empty support, owner budgets, DL5g blind).',
                 registered_revalidation)

    def declared_identity_preserved():
        declared, done = load(G0/'references.json'), completed()
        require([key(c) for c in declared['cells']] == [key(c) for c in done['cells']], 'membership/order')
        for name, value in declared.items():
            if name != 'cells': require(done.get(name) == value, f'metadata {name}')
        for before, after in zip(declared['cells'], done['cells']):
            for field in ('profile', 'renderer', 'scene', 'statistic', 'support', 'role',
                          'currentGeneration', 'currentDocumentPair', 'historical'):
                require(before.get(field) == after.get(field), f'fixed {field} {key(before)}')
            for field in ('B', 'native', 'current', 'fidelity', 'nativeEvidence',
                          'currentEvidence', 'currentMetadata'):
                if before.get(field) is not None:
                    require(before[field] == after.get(field), f'known {field} {key(before)}')
        return {'rows': len(done['cells']), 'declaredSha256': sha(G0/'references.json')}
    run.function('declared-identity-preserved', 'G0 declare.verify(phase=fit)\'s reference '
                 'clauses: membership/order, fixed fields and every already-known value unchanged.',
                 declared_identity_preserved)

    def status_census():
        counts, blind = {}, 0
        for c in completed()['cells']:
            k = f'{c["role"]} {c["status"]}'; counts[k] = counts.get(k, 0)+1
            if c['role'] == 'blind':
                blind += 1
                require(c['status'] == 'SEALED_BLIND' and all(c.get(n) is None for n in
                        ('native', 'current', 'fidelity', 'B', 'nativeEvidence', 'currentEvidence',
                         'currentMetadata')), 'blind row identity-only')
            elif c['status'] not in ('MEASURED', 'REPORTED', 'UNMEASURED_EMPTY_SUPPORT'):
                raise AssertionError(f'exposed row not completed: {key(c)} {c["status"]}')
        require(counts == archive['summary']['statuses'], 'census equals the archive record')
        require(blind == 832, '832 blind rows')
        return {'statuses': counts, 'blindIdentityOnly': blind}
    run.function('status-census', 'Every exposed row is MEASURED, REPORTED (DL5a) or '
                 'UNMEASURED_EMPTY_SUPPORT (DL5b); 832 blind rows are SEALED_BLIND with null values '
                 'and evidence (DL5g); census equals the archive record.', status_census)

    for name, tests in (('test_assembler.py', 11), ('test_bound.py', 4), ('test_bound_composed.py', 6),
                        ('test_validator.py', 2)):
        py_test(run, 'completion-'+name[5:-3]+'-tests', f'Completion {name} (synthetic).',
                FIT/'completion'/name, tests)

    return run.finish(
        'The completed reference inventory (3,527 rows) is the one assembly executed '
        'from the committed binding and archived exactly; it keeps every declared identity, role, '
        'support, historical cap and known value; every exposed row is measured or carries its '
        'ruled status; blind rows stay identity-only (README pre-fit clause; DL5a-DL5g, DL5l).',
        [binding_path, REGISTERED/'run.py', REGISTERED/'evidence/archive.json',
         REGISTERED/'evidence/completed-references.json.gz',
         REGISTERED/'evidence/artifacts.tar.gz', FIT/'completion/bound.py',
         FIT/'completion/assembler.py', CUR3/'execution/prefit.py', G0/'references.json',
         G0/'bed/manifest.json', LIVE_REFS] +
        [FIT/'completion'/n for n in ('test_assembler.py', 'test_bound.py', 'test_bound_composed.py',
                                      'test_validator.py')],
        'Reference validation only; no candidate, fit, gate or exposure value; blind rows were '
        'checked for nullity without reading or printing a value.')


# ------------------------------------------------------------------------------------------
def dark05_bands(run):
    r2 = load(FIT/'references-r2/evidence/archive.json')

    def r2_archive_and_root():
        root = verify_root(FIT/'references-r2/instrument-root.json', 'references-r2 root')
        side = (FIT/'references-r2/execution-contract.json.sha256').read_text().split()[0]
        require(side == sha(FIT/'references-r2/execution-contract.json'), 'contract sidecar')
        binding = load(REGISTERED/'binding.json')
        target = binding['canonicalReferences']
        raw = gunzip(FIT/'references-r2/evidence/canonical-references.json.gz')
        require(sha_bytes(raw) == target['sha256'] == sha(target['path']), 'r2 output archived exactly')
        require(json.dumps(r2).count(target['sha256']) >= 1, 'archive record names the output')
        out = json.loads(raw)
        require(out['instrumentRootSha256'] == root['sha256'], 'output names its root')
        return {**root, 'outputSha256': target['sha256']}
    run.function('r2-archive-and-root', 'The canonical reference read (root 604041d2..., DL5l) is '
                 'sealed, its pins hold and its output is archived byte-exactly.', r2_archive_and_root)

    for name, tests in (('test_statistics.py', 6), ('test_canonical.py', 11), ('test_completion.py', 7),
                        ('test_composed_completion.py', 8), ('test_run.py', 9), ('test_run_composed.py', 4)):
        py_test(run, 'r2-'+name[5:-3]+'-tests', f'references-r2 {name} (synthetic).',
                FIT/'references-r2'/name, tests)

    def dark05_t1_population():
        stats = module(FIT/'references-r2/statistics.py', 'w50_prefit_r2_statistics_b')
        rows = [c for c in completed()['cells'] if c['profile'].endswith('-glass0.5')
                and c['statistic'] in ('T1-full-silhouette', 'T1-low') and not c['scene'].startswith('cell-')
                and c['role'] != 'blind']
        counts = {}
        for c in rows:
            k = f'{c["profile"][17:19]} {c["statistic"]} {c["role"]}'; counts[k] = counts.get(k, 0)+1
            require(c['status'] == 'MEASURED' and type(c['B']) is float and math.isfinite(c['B'])
                    and c['B'] > 0, f'{key(c)} measured with positive B')
            require(c['currentGeneration'] == '0eac5b294cc2' and c['currentDocumentPair'] == {
                'active.dark': '0eac5b294cc235e2ba03841472211e63f85d36258a20951bef6f974931cda445',
                'receded.dark': '5cec8c9612012a8988e37ee51a80bcc8de35b306f6f8464d596dfdbbdbcef0d2'},
                f'{key(c)} against its own frozen current')
            reading = c['canonicalReadings'][c['statistic']]
            again = stats.repeat_bar(reading['repeatValues'], units=reading['units'],
                                     published_mean=reading['repeat']['publishedNativeInteriorMean'])
            require(again['B'] == c['B'] == reading['B'] and reading['repeat']['runs'] == 7,
                    f'{key(c)} B is its own seven-run bar')
            if c['statistic'] == 'T1-low':
                f = c['fidelity']
                require(set(f) == {'statistic', 'native', 'current', 'reference'} and
                        f['statistic'] == 'T1-fine' and 'T1-fine' in c['canonicalReadings'],
                        f'{key(c)} T band carries its own T1-fine fidelity (DL5g)')
            for name in ('nativeEvidence', 'currentEvidence', 'currentMetadata'):
                verify_file(c[name]['path'], c[name]['sha256'])
        require(len(rows) == 154 and all(v in (63, 10, 3, 1) for v in counts.values()), 'population')
        return {'rows': len(rows), 'byScaleStatisticRole': counts, 'evidencePinsVerified': 3*len(rows)}
    run.function('dark05-t1-population', 'All 154 exposed dark 0.5 canonical T1 rows (63+10 '
                 'full-silhouette, 3+1 T-band per scale) are MEASURED against frozen current '
                 '0eac5b294cc2, each B recomputes from its own seven native repeats, T-band rows carry '
                 'typed T1-fine fidelity, and every native/current pin hashes.', dark05_t1_population)

    def dark05_missing_baselines():
        declared = {key(c): c for c in load(G0/'references.json')['cells']}
        found = []
        for c in completed()['cells']:
            before = declared[key(c)]
            if c['profile'].endswith('-glass0.5') and c['statistic'].startswith('T1') and \
                    not c['scene'].startswith('cell-') and c['role'] != 'blind' and \
                    before.get('currentEvidence') is None:
                require(c['status'] == 'MEASURED' and c['currentEvidence']['path'].startswith(
                        '/Users/new/vitrea-w50/g1-baselines/'), f'{key(c)} own pre-fit current')
                found.append('|'.join(key(c)))
        summary = load(FIT/'current-analysis-composed/evidence/archive.json')['summary']
        require(len(found) == 12 == summary['canonicalMissingT1Routes'], 'twelve missing baselines')
        return {'previouslyMissingDefaultT1Baselines': sorted(found)}
    run.function('dark05-missing-baselines', 'The 12 dark 0.5 T1 rows with no prior current capture '
                 'now read their own pre-fit current render (canonical3 recovery).', dark05_missing_baselines)

    return run.finish(
        'Dark 0.5 T1 is priced against its own frozen current 0eac5b294cc2 with its own pre-fit '
        'bands and per-cell B, generated and sealed before fitting (landing rule 4; part 2 '
        'dark05T1). The bands and B come from the sealed references-r2 read, archived exactly.',
        [FIT/'references-r2/instrument-root.json', FIT/'references-r2/instrument-root.json.sha256',
         FIT/'references-r2/execution-contract.json', FIT/'references-r2/execution-contract.json.sha256',
         FIT/'references-r2/read-batch.json', FIT/'references-r2/statistics.py',
         FIT/'references-r2/canonical.py', FIT/'references-r2/evidence/archive.json',
         FIT/'references-r2/evidence/canonical-references.json.gz',
         FIT/'current-analysis-composed/evidence/archive.json', REGISTERED/'binding.json',
         G0/'references.json', LIVE_REFS],
        'No canonical read was rerun; B recomputation uses recorded repeat values only.')


# ------------------------------------------------------------------------------------------
def verify_identity_command(run, cid):
    run.command(cid, 'verify-identity.py: the 43 renderer raster witnesses equal W49b\'s and the '
                'retained scratch controls hash to their records; prior-capture cells are raw-RGBA '
                'identical to the canonical tree (read-only).',
                [PY, '-I', '-B', str(G0/'evidence/verify-identity.py')], cwd=G0/'evidence',
                expect=[r'^43 renderer witnesses exact; WebGPU \(24, 4\), CSS \(21, 7\)'])


def active05_scratch(run):
    verify_identity_command(run, 'scratch-raster-identity')
    declared = {key(c): c for c in load(G0/'references.json')['cells']}

    def scratch_bound_rows():
        roots = ('/Users/new/vitrea-w50/identity-controls-complete/', '/Users/new/vitrea-w50/identity-controls-css/')
        rows = [c for c in completed()['cells'] if (c.get('currentEvidence') or {}).get('path', '').startswith(roots)]
        for c in rows:
            # DL5e: owner-contract rows on the same captures are MEASURED with B null by ruling.
            require(c['status'] == 'MEASURED' and (c['B'] is None if c['statistic'] == 'owner-contracts'
                    else math.isfinite(c['B']) and c['B'] > 0), f'{key(c)} measured')
            require(declared[key(c)]['currentEvidence'] == c['currentEvidence'], f'{key(c)} G0 pin kept')
            verify_file(c['currentEvidence']['path'], c['currentEvidence']['sha256'])
        want = [(p, r, s) for p in ('apple-macos-27.0-1x-dark-standard-glass0.5',
                                    'apple-macos-27.0-2x-dark-standard-glass0.5')
                for r in ('webgpu', 'css') for s in ('impulse__rrect-ml__rest', 'impulse__rrect-lg__rest')]
        want += [('apple-macos-27.0-2x-dark-standard-glass0.5', 'css', s)
                 for s in ('impulse__rrect-ml__inactive', 'impulse__rrect-lg__inactive')]
        have = {(c['profile'], c['renderer'], c['scene']) for c in rows if c['statistic'] == 'low-end-path-level'}
        require(set(want) <= have, 'active 0.5 impulse ml/lg rest both scales/tiers and 2x receded CSS')
        return {'rowsOnScratchControls': len(rows), 'lowEndPathRequired': len(want),
                'statuses': sorted({c['status'] for c in rows})}
    run.function('scratch-bound-rows', 'The active 0.5 impulse ml/lg current rows (both scales and '
                 'tiers) and the two default 2x receded CSS ml/lg references are MEASURED on the '
                 'G0-bound scratch captures, whose pins are unchanged and hash.', scratch_bound_rows)

    return run.finish(
        'Active 0.5\'s missing current web rows are read in scratch before fitting (landing rule 2; '
        'README "missing active0.5 ml/lg current captures"; §5.217 §2 and §5), and the retained '
        'scratch rasters still verify.',
        [G0/'evidence/verify-identity.py', G0/'evidence/dark-controls-complete.json',
         G0/'evidence/dark-controls-css.json', G0/'evidence/raw-identity.json',
         RES/'2026-10-08-w49b-g0-declaration/evidence/identity-after.json', G0/'references.json', LIVE_REFS],
        'Reads retained scratch captures and the canonical capture tree read-only; renders nothing.')


# ------------------------------------------------------------------------------------------
def identity_digests_goldens(run):
    runtime = ['packages/core', 'packages/platform-web', 'packages/renderer-webgpu', 'packages/react',
               'packages/policy', 'packages/geometry', 'packages/motion', 'packages/calibration/src',
               'packages/calibration/test', 'packages/calibration/profiles', 'packages/calibration/scripts',
               'packages/calibration/results/generations', 'apps/reference-apple/scenes.json',
               'apps/reference-apple/fixtures', 'pnpm-lock.yaml']

    def runtime_unchanged_since_g0():
        diff = subprocess.run(['git', 'diff', '--name-only', G0_MERGE, '--', *runtime], cwd=REPO,
                              capture_output=True, text=True, check=True).stdout.split()
        require(diff == [], f'runtime changed since G0: {diff[:5]}')
        return {'since': G0_MERGE, 'paths': runtime, 'changedFiles': 0, 'worktreeIncluded': True}
    run.function('runtime-unchanged-since-g0', 'No runtime, profile, generation, fixture or owner '
                 'test byte changed since the sealed G0 merge (working tree included), so G0\'s '
                 'identity witnesses describe the current bytes.', runtime_unchanged_since_g0)

    def digest_records():
        records = load(G0/'evidence/digests.json')
        for r in records:
            doc = CAL/'profiles'/r['name']
            require(sha(doc) == r['documentSha256'] and r['recorded'] == r['actual'] and
                    load(doc)['resolvedMaterialSha256'].startswith(r['recorded']), r['name'])
        require(len(records) == 10, 'ten documents')
        return {'documents': len(records), 'recordedEqualsActual': True}
    run.function('digest-records', 'All ten shipped profile documents are byte-identical to G0\'s '
                 'digest record, whose recorded and recomputed fingerprints agree.', digest_records)

    vitest(run, 'calibration-identity-suite', 'Digest pins and identity proofs recomputed from the '
           'live documents (tuned-profiles, W30/W31 identity, gate groups, macOS27 export, tier '
           'coherence, material selection).', CAL,
           ['test/tuned-profiles.test.ts', 'test/w30-operator-identity.test.ts',
            'test/w31-identity-table.test.ts', 'test/macos27-profile-export.test.ts',
            'test/tier-coherence.test.ts', 'test/material-selection.test.ts'], r'\d+')
    vitest(run, 'renderer-gate-groups', 'Each identity-table gate-group drops as one unit, the W50 '
           'chart included.', REPO/'packages/renderer-webgpu', ['test/w31-gate-groups.test.ts'], r'\d+')
    run.command('renderer-goldens', 'All renderer goldens pass on a hardware adapter at the new '
                'gate\'s identity (G0 recorded 34).', ['pnpm', 'run', 'test:golden'],
                cwd=REPO/'packages/renderer-webgpu', expect=[r'^\s+34 passed'])
    verify_identity_command(run, 'raster-witnesses')
    run.command('freeze-1818', 'The macOS 26.5 freeze witness is intact.',
                ['python3.12', 'results/2026-09-16-w29-freeze/freeze.py', 'verify'], cwd=CAL,
                expect=[r'^26\.5 freeze intact: 1818 entries'])
    run.command('x41-911', 'The X41 0.5-generation witness is intact.',
                ['pnpm', 'exec', 'tsx', 'results/2026-10-01-w43-g0-declaration/x41/x41.ts', 'verify'],
                cwd=CAL, expect=[r'intact: 911 entries'])

    return run.finish(
        'Light endpoints and the frozen 26.5 pair remain identical; all ten digests and all '
        'goldens are identical at the new gate\'s identity (landing rule 5; §5.217 §2).',
        [G0/'evidence/digests.json', G0/'evidence/identity-proof.json', G0/'evidence/raw-identity.json',
         G0/'evidence/verify-identity.py', G0/'evidence/dark-controls-complete.json',
         G0/'evidence/dark-controls-css.json',
         RES/'2026-10-08-w49b-g0-declaration/evidence/identity-after.json',
         *sorted((CAL/'profiles').glob('apple-macos-2*-standard*.json')),
         CAL/'test/tuned-profiles.test.ts', CAL/'test/w30-operator-identity.test.ts',
         CAL/'test/w31-identity-table.test.ts', REPO/'packages/renderer-webgpu/test/w31-gate-groups.test.ts',
         CAL/'test/macos27-profile-export.test.ts',
         CAL/'test/tier-coherence.test.ts', CAL/'test/material-selection.test.ts',
         REPO/'packages/renderer-webgpu/src/material.ts', REPO/'packages/renderer-webgpu/src/wgsl/optics.ts',
         REPO/'packages/platform-web/src/optics.ts'],
        'GPU goldens render the shipped material at identity only; no candidate was rendered.')


# ------------------------------------------------------------------------------------------
def numerical_rehearsal(run):
    node_test(run, 'numerical-standalone-tests', 'audit/numerical.test.ts: the ten standalone '
              'producer tests in authorised (post-seal) runtime mode.', G0/'audit/numerical.test.ts', 10)
    py_test(run, 'numerical-guard-tests', 'audit/numerical_guard.py consumer pins (synthetic).',
            G0/'audit/test_numerical_guard.py', r'\d+')

    def full_synthetic_sweep():
        result = subprocess.run(['pnpm', 'exec', 'tsx', str(FIT/'prefit-proofs/synthetic-sweep.ts')], cwd=CAL,
                                capture_output=True, text=True, env={**os.environ, 'NO_COLOR': '1'})
        require(result.returncode == 0, result.stderr[-2000:])
        report = json.loads(result.stdout[result.stdout.index('{'):])
        record = load(G0/'evidence/synthetic-rehearsal.json')
        require(report['status'] == 'UNMEASURED' and report['structuredArgumentPass'] is False,
                'a synthetic rehearsal without measured arguments is UNMEASURED, never a PASS')
        require(report['samples'] == record['samples'] == 6325768, 'full domain sample count')
        require(report['maxRunningDrawdownCode'] == record['runningDrawdownCode'] == 0, 'zero drawdown')
        require(report['minimumRequestedNeutral'] == record['minimumRequestedNeutral'], 'min neutral')
        require(report['fixedJoinPass'] and report['standDownPass'] and report['negativeRequests'] == [],
                'join, stand-downs, no negative request')
        report.pop('domain'); return report
    run.function('full-synthetic-sweep', 'The full declared domain (0-64 at 1/64 code, spans '
                 '32-224, both scales/positions/poses) through the sealed producer reproduces G0\'s '
                 'record exactly: 6,325,768 samples, zero running drawdown, minimum neutral '
                 '0.008744262734081729, fixed join and stand-downs intact; UNMEASURED without '
                 'measured arguments.', full_synthetic_sweep)

    vitest(run, 'css-low-end-unit', 'CSS low-end law: interpolation, fixed64 join, authority, '
           'drawdown referee, stand-downs.', REPO/'packages/platform-web', ['test/w50-low-end.test.ts'], 10)
    vitest(run, 'renderer-low-end-unit', 'Renderer chart: identity drop, actual-span join, validation.',
           REPO/'packages/renderer-webgpu', ['test/w50-low-end.test.ts'], 4)
    vitest(run, 'candidate-reader-unit', 'Candidate chart reader across the real document reader.',
           CAL, ['test/w50-candidate-reader.test.ts'], r'\d+')

    return run.finish(
        'G0\'s numerical rehearsal: the composed pre-quantised CPU uniform response meets the '
        'running-drawdown bound <=1e-4 code over the full declared domain with the fixed64 join '
        'and every stand-down intact (landing rule 1; part 2 monotonicity; §5.217 §1 and §6). '
        'Synthetic on-state proofs, not a fitted candidate\'s numericalReferee.',
        [G0/'audit/numerical.ts', G0/'audit/numerical.test.ts', G0/'audit/numerical_guard.py',
         G0/'audit/test_numerical_guard.py', G0/'audit/runtime-closure.json',
         G0/'evidence/synthetic-rehearsal.json', FIT/'prefit-proofs/synthetic-sweep.ts',
         REPO/'packages/platform-web/src/optics.ts', REPO/'packages/platform-web/test/w50-low-end.test.ts',
         REPO/'packages/renderer-webgpu/src/material.ts', REPO/'packages/renderer-webgpu/test/w50-low-end.test.ts',
         CAL/'test/w50-candidate-reader.test.ts', CAL/'scripts/candidate-document.ts'],
        'Synthetic profile only; no candidate, measured argument or native value.')


# ------------------------------------------------------------------------------------------
def shader_cpu(run):
    run.command('gpu-w50-low-end', 'On a hardware adapter: the production WGSL chart agrees with '
                'the CPU within 0.001 encoded code, and the uniform block reaches the body while '
                'every old solve gate holds.',
                ['pnpm', 'exec', 'playwright', 'test', 'e2e/gpu/w50-low-end.spec.ts', '--project=chromium-gpu'],
                cwd=REPO/'packages/renderer-webgpu', expect=[r'^\s+2 passed'])
    return run.finish(
        'Shader/CPU agreement has its own <=1e-3 encoded output code precision bound (landing rule 1; '
        'part 2 shaderCpuMaxErrorCode 0.001; §5.217 §1).',
        [REPO/'packages/renderer-webgpu/e2e/gpu/w50-low-end.spec.ts', REPO/'packages/renderer-webgpu/e2e/support.ts',
         REPO/'packages/renderer-webgpu/src/material.ts', REPO/'packages/renderer-webgpu/src/wgsl/optics.ts',
         REPO/'packages/renderer-webgpu/src/renderer.ts', REPO/'packages/renderer-webgpu/playwright.config.ts',
         G0/'fit-declaration.json'],
        'A synthetic chart on the production functions; no candidate document was rendered.')


# ------------------------------------------------------------------------------------------
def negative_neutral(run):
    vitest(run, 'css-pre-clamp-request', 'lowEndNeutralRequest reports the actual pre-clamp neutral '
           'request and keeps the independent linear mean.', REPO/'packages/platform-web',
           ['test/w50-low-end.test.ts'], 1, extra=['-t', 'pre-clamp neutral request'])
    node_test(run, 'numerical-negative-referee', 'The structured referee keeps the measured linear '
              'mean and rejects a negative request.', G0/'audit/numerical.test.ts', 1,
              extra=['--test-name-pattern', 'rejects a negative request'])
    py_test(run, 'numerical-guard-tests', 'Consumer refusal of reports without the negative-request '
            'clause (synthetic).', G0/'audit/test_numerical_guard.py', r'\d+')

    def attribution_rederived():
        rows = load(GROUND/'attribution.json')['rows']
        negatives = []
        for r in rows:
            n, t = r['tone']['neutralClampContext'], r['tone']
            a, mu = n['sizedAlpha'], n['toneLinearMean']
            require(abs(n['minimumTransmittedAggregateLinear'] - (1-a)*mu) <= 1e-15, 'floor (1-a)mu')
            if n['fullAuthorityUnclampedNeutralAtZeroCollapse'] is not None:
                require(t['toneAuthority'] == 1 and n['collapseWeight'] == 0, 'full authority, k=0')
                again = n['responseMinusTransmissionFloor']/a
                require(abs(again - n['fullAuthorityUnclampedNeutralAtZeroCollapse']) <= 1e-15,
                        'unclamped neutral (R-(1-a)mu)/a')
                if again < 0: negatives.append((r['profile'], r['scene'], round(again, 9)))
        want = {('glass0.25', -0.000337849), ('glass0.5', -0.000399516)}
        got = {(p.rsplit('-', 1)[1], round(v, 9)) for p, s, v in negatives}
        require(len(negatives) == 4 and all(s == 'impulse__rrect-lg__inactive' for _, s, _ in negatives)
                and want <= got, 'the receded lg impulse requests are negative as the charter tabulates')
        return {'rows': len(rows), 'negativeRequests': negatives}
    run.function('attribution-rederived', 'The grounding attribution\'s negative-neutral mechanism '
                 're-derives from its recorded inputs: (R-(1-a)mu)/a is negative on both positions\' '
                 'receded lg impulse (charter table -.000337849 / -.000399516), positive elsewhere.',
                 attribution_rederived)

    return run.finish(
        'A low-end target requesting negative neutral is reported, not hidden by the gamut clamp '
        '(charter "report every low-end target that requests negative neutral"; Attribution; '
        '§5.217 §1, §6); the current failure\'s negative request is reproduced from recorded inputs.',
        [GROUND/'attribution.json', GROUND/'attribute.py', REPO/'packages/platform-web/src/optics.ts',
         REPO/'packages/platform-web/test/w50-low-end.test.ts', G0/'audit/numerical.ts',
         G0/'audit/numerical.test.ts', G0/'audit/numerical_guard.py', G0/'audit/test_numerical_guard.py'],
        'Recorded grounding inputs and synthetic tests only; attribute.py was not rerun (it reads '
        'the main checkout and rewrites its output in place).')


# ------------------------------------------------------------------------------------------
def new_bed_adapter(run):
    web = CUR3/'web'
    for name, tests in (('current.test.ts', 2), ('pair.test.ts', 1), ('host.test.mjs', 2),
                        ('guard.test.mjs', 46), ('discovery.test.mjs', 4)):
        node_test(run, 'web-'+name.split('.')[0]+'-tests', f'New-bed web adapter {name}.', web/name, tests)
    for path, tests in ((web/'test_adapter.py', 13), (CUR3/'canonical/test_adapter.py', 13),
                        *[(CUR3/'repeat'/f'test_{n}.py', t) for n, t in (('admission', 6), ('archived', 3),
                          ('blind', 4), ('core', 7), ('source_probe', 1), ('sources', 7))],
                        *[(CUR3/'execution'/f'test_{n}.py', t) for n, t in (('recovery', 6), ('retained', 5),
                          ('root_recovery', 4), ('router_recovery', 6))],
                        *[(CAN3/'execution'/f'test_{n}.py', t) for n, t in (('composition', 3), ('dispatch', 6),
                          ('evidence', 6), ('invocation', 2), ('recovery', 7))],
                        *[(FIT/'current-analysis-composed'/f'test_{n}.py', t) for n, t in
                          (('analysis', 5), ('archived', 3), ('run', 5))]):
        label = {CUR3: 'current3', CAN3: 'canonical3', FIT: 'g1fit'}[Path(path).parents[1]]
        py_test(run, f'{label}-{Path(path).parent.name}-{Path(path).stem}', f'{rel(path)} (synthetic).',
                path, tests)

    def instrument_roots():
        out = [verify_root(CUR3/'execution/current-instrument-root.json', 'current3 root'),
               verify_root(CAN3/'execution/current-instrument-root.json', 'canonical3 root'),
               verify_root(FIT/'current-analysis-composed/instrument-root.json', 'composed analysis root')]
        require(out[0]['sha256'].startswith('dbe20abc') and out[1]['sha256'].startswith('849e137f') and
                out[2]['sha256'].startswith('0b140dfd'), 'the three recorded roots')
        return {'roots': out}
    run.function('instrument-roots', 'The current3 (new-bed 512x384), canonical3 and composed-analysis '
                 'roots are sealed and every source/closure/capture pin inside still hashes.', instrument_roots)

    def new_bed_result_chain():
        base = CUR3/'execution/current-instrument/d25a355d0944bccdefffb1c1829fa8dd0cf26cf1e7d9009a5174ae02e52bd698.json'
        result = Path(str(base)+'.result.json')
        require(Path(str(result)+'.sha256').read_text().split()[0] == sha(result) and
                sha(result).startswith('20b7422c'), 'result sidecar 20b7422c')
        require(Path(str(base)+'.sha256').read_text().split()[0] == sha(base), 'contract sidecar')
        doc = load(result)
        cap = doc['captures']
        require(doc['report']['status'] == cap['status'] == 'CAPTURED' and len(cap['captures']) == 672 and
                cap['origins'] == {'retainedAttempt2': 501, 'freshAttempt3': 171}, '672 = 501 + 171')
        verified = 0
        for p, digest in pins_in(doc['captureReceipt']) + pins_in(doc['repeatReceipt']):
            if guarded(p): continue
            verify_file(p, digest); verified += 1
        return {'resultSha256': sha(result), 'captures': 672, 'origins': cap['origins'],
                'receiptPinsVerified': verified}
    run.function('new-bed-result-chain', 'The new-bed current batch result (20b7422c...) is '
                 'CAPTURED with 672 logical captures (501 retained + 171 fresh, DL5h) and every '
                 'capture/repeat receipt pin hashes.', new_bed_result_chain)

    def composed_analysis_archive():
        record = load(FIT/'current-analysis-composed/evidence/archive.json')
        raw = gunzip(FIT/'current-analysis-composed/evidence/completed-current.json.gz')
        require(sha(FIT/'current-analysis-composed/evidence/completed-current.json.gz') ==
                record['archive']['sha256'], 'archive gz')
        require(sha_bytes(raw) == record['original']['sha256'] == sha(LIVE_CURRENT) ==
                sha(record['original']['path']), 'archive, live copy and original agree')
        doc = json.loads(raw)
        require(doc['instrumentRootSha256'] == record['instrumentRootSha256'] ==
                sha(FIT/'current-analysis-composed/instrument-root.json'), 'output names its root')
        require(record['summary']['referenceEvidenceRows'] == 1632 and record['summary']['actualRoots'] == 2,
                'new-bed reference evidence rows and both actual roots')
        return {'completedCurrentSha256': record['original']['sha256'], 'summary': record['summary']}
    run.function('composed-analysis-archive', 'The composed current analysis (the adapter\'s '
                 'exercised measurement over both real chains) is archived exactly and names its root.',
                 composed_analysis_archive)

    return run.finish(
        'The custom 512x384 new-bed compare/measurement adapter (DL5f border-box host, DL5h repeat '
        'admission) exists, is sealed with its exercised source closure, and has produced the '
        'completed current chain the references were assembled from (README pre-fit clause; '
        '§5.217 §4; Revision Notes G1 attempt3).',
        [CUR3/'execution/current-instrument-root.json', CUR3/'execution/current-instrument-root.json.sha256',
         CAN3/'execution/current-instrument-root.json', CAN3/'execution/current-instrument-root.json.sha256',
         FIT/'current-analysis-composed/instrument-root.json',
         FIT/'current-analysis-composed/instrument-root.json.sha256',
         CUR3/'execution/current-instrument/d25a355d0944bccdefffb1c1829fa8dd0cf26cf1e7d9009a5174ae02e52bd698.json',
         CUR3/'execution/current-instrument/d25a355d0944bccdefffb1c1829fa8dd0cf26cf1e7d9009a5174ae02e52bd698.json.result.json',
         CUR3/'execution/current-instrument/d25a355d0944bccdefffb1c1829fa8dd0cf26cf1e7d9009a5174ae02e52bd698.json.result.json.sha256',
         web/'adapter.py', web/'capture-web.ts', web/'current.ts', web/'host.mjs', web/'pair.ts',
         CUR3/'canonical/adapter.py', CUR3/'repeat/admission.py', CUR3/'repeat/core.py',
         CUR3/'inputs/web-source-closure.json', CUR3/'inputs/current-python-closure.json',
         FIT/'current-analysis-composed/analysis.py', FIT/'current-analysis-composed/run.py',
         FIT/'current-analysis-composed/evidence/archive.json',
         FIT/'current-analysis-composed/evidence/completed-current.json.gz', LIVE_CURRENT],
        'No capture or current read was rerun; tests use synthetic inputs and roots are '
        'hash-verified only.')


KINDS = {'nativeArchive': native_archive, 'repeatBar': repeat_bar,
         'referenceCompletion': reference_completion, 'dark05Bands': dark05_bands,
         'active05ScratchBaselines': active05_scratch, 'identityDigestsGoldens': identity_digests_goldens,
         'numericalRehearsal': numerical_rehearsal, 'shaderCpuAgreement': shader_cpu,
         'negativeNeutralDiagnostic': negative_neutral, 'newBedRendererAdapter': new_bed_adapter}

if __name__ == '__main__':
    args = sys.argv[1:]
    dry = '--dry' in args
    args = [a for a in args if a != '--dry']
    if len(args) != 1 or args[0] not in KINDS:
        sys.exit(f'usage: build.py {{{",".join(KINDS)}}} [--dry]')
    sys.exit(KINDS[args[0]](Run(args[0], dry)))
