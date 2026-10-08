"""Synthetic archive pixels under the REAL LIVE dispatcher; sealed native sources stay untouched.

The bed/archive fixtures are exposure/test_prepare.py's and native/test_reader.py's. The
original prepare_native_exposure runs under a permissive fake dispatcher only as the
equivalence referee for the role's bytes.
"""
import contextlib
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

import numpy as np

HERE = Path(__file__).resolve().parent
FIT = HERE.parent
G0 = FIT.parent/'2026-10-08-w50-g0-declaration'
CANARY = 'NATIVE_SECRET_12345.875'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); sys.modules[name] = module
    spec.loader.exec_module(module); return module


K = load('w50_native_role_livekit', HERE/'livekit.py')
fixture = load('w50_native_role_tree_fixture', FIT/'native/test_reader.py')
F = load('w50_native_role_candidate_fixture', FIT/'execution/test_support.py')


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, doc):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2, allow_nan=False)+'\n'); return path


def sidecar(path): Path(str(path)+'.sha256').write_text(f'{sha(path)}  {Path(path).name}\n')


def fresh_prepare(name):
    module = types.ModuleType(name); path = FIT/'exposure/prepare.py'; module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


def bed():
    """exposure/test_prepare.py's bed: active and receded blind cells, DL5c control included."""
    manifest, scenes = fixture.bed()
    for cell in manifest['cells']:
        if cell['background'].startswith('grey-'): cell['level'] = int(cell['background'][5:])
    profile = fixture.PROFILE
    calibration = next(c for c in manifest['cells'] if c['family'] == 'structured')
    structured = dict(calibration, span=224, role='blind', scene='cell-impulse-sparse-s224__rest',
                      id=profile+'/cell-impulse-sparse-s224__rest')
    manifest['cells'].append(structured)
    ref = next(r for r in manifest['references'] if r['id'] == structured['reference'])
    ref['roles'].append('blind'); ref['roles'].sort()
    scenes['scenes'].append(dict(id=structured['scene'], background='impulse-sparse', component='span-224', state='rest'))
    scenes['split']['holdout'].append(structured['scene']); scenes['profiles'][0]['scenes'].append(structured['scene'])
    control = dict(next(c for c in manifest['cells'] if c['family'] == 'span' and c['span'] == 224),
                   background='grey-000', level=0, pose='receded', scene='cell-grey-000-s224__inactive',
                   id=profile+'/cell-grey-000-s224__inactive', reference=profile+'/ref-grey-000__inactive',
                   passName='bed-receded')
    manifest['cells'].append(control)
    manifest['references'].append(dict(id=control['reference'], scene='ref-grey-000__inactive', profile=profile,
        background='grey-000', roles=['blind'], passName='bed-receded', run=1))
    for scene, component in ((control['scene'], 'span-224'), ('ref-grey-000__inactive', 'none')):
        scenes['scenes'].append(dict(id=scene, background='grey-000', component=component, state='inactive'))
        scenes['profiles'][0]['scenes'].append(scene)
    scenes['split']['holdout'].append(control['scene']); scenes['split']['recorded'].append('ref-grey-000__inactive')
    return manifest, scenes


class Planner:
    """The new-bed transport's pose plan for the synthetic bed (router.fixture_keys reads only poses)."""
    def __init__(self, scenes): self.states = {s['id']: s['state'] for s in scenes['scenes']}
    def scene_plan(self, run, phase):
        return {'scenes': [{'scene': s, 'pose': 'receded' if self.states[s] == 'inactive' else 'active'}
                           for s in run['scenes']]}


CAPTURE = '''from pathlib import Path
import hashlib,json,sys
def put(path,value):
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value))
 return {'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
def capture(context,member,config):
 d=sys.modules['w50_g1_dispatch'];d.require_render_admission(context,member['run'],current=member['lane']=='current')
 if '000001' in context['executionClaim']['path'] and member['lane']=='current':raise ValueError('synthetic transport stop')
 run=member['run'];base=Path(run['captureRoot'])
 artifacts={k:put(base/(k+'.json'),{'synthetic':k}) for k in ('png','cell','report')}
 record={'profile':run['profile'],'renderer':run['renderer'],'scene':member['scene'],'lane':member['lane'],
  'candidate':run['candidate'],'artifacts':artifacts}
 pair=put(base/'pair.json',{'first':artifacts['png']})
 record.update(repeatPair=pair,repeatAdmission=put(base/'repeat-admission__webgpu.json',
  {'manifest':pair,'pair':{'first':artifacts['png']},'originalArtifacts':artifacts}))
 return {'record':record,'artifacts':list(artifacts.values())}
def recover(context,member,config):return None
def verify(context,member,record,config):pass
'''

# LIVE runs the owner's metadata-only admission before the native marker (pre-seal review P1);
# the owner role itself is exercised in test_owner.py.
OWNER = '''import sys
def admit(context,config):
 sys.modules['w50_g1_dispatch'].require_owner_admission(context);return {'admitted':True}
def evaluate(context,captures,config):raise ValueError('synthetic owner is admission-only')
'''


class NativeRole(unittest.TestCase):
    def setUp(self):
        self.manifest, self.scenes = bed()
        profile = fixture.PROFILE
        blind = [c for c in self.manifest['cells'] if c['role'] == 'blind']
        self.candidate = {'path': 'candidate.json', 'sha256': hashlib.sha256(b'candidate').hexdigest()}
        baseline = {'path': 'baseline.json', 'sha256': hashlib.sha256(b'baseline').hexdigest()}
        common = dict(profile=profile, renderer='webgpu', sceneSource='w50', candidate=self.candidate,
                      baselineCandidate=baseline, sets=['holdout'], captureRoot='unused', matrixPath='unused')
        self.runs = [dict(common, id='blind-active', scenes=[c['scene'] for c in blind if c['pose'] == 'active']),
                     dict(common, id='blind-receded', scenes=[c['scene'] for c in blind if c['pose'] == 'receded'])]
        self.pending = [[profile, 'webgpu', 'history-1', 'owner-contracts'],
                        [profile, 'css', 'history-2', 'owner-contracts']]
        self.gate = {'captures': {'captures': []}, 'report': {'status': 'PASS_EXPOSED_OWNER_PENDING',
            'ownerChecks': 'PENDING_FULL_UNION', 'pendingOwnerKeys': self.pending,
            'candidateSha256s': [self.candidate['sha256']]}}
        self.kit = kit = K.Kit(self, phase='exposure', runs=self.runs, cohort=[self.candidate], gate=self.gate)
        repo = kit.repo
        built = F.build(repo, G0, kit.C.D.PROOFS)
        manifest_path = write(built['manifest'], self.manifest)
        scenes_path = write(Path(built['manifest']).with_name('scenes-w50.json'), self.scenes)
        one, two = built['one'], built['two']
        for path in (one, two):
            doc = json.loads(path.read_bytes())
            doc['sources'] = [p for p in doc['sources'] if p['path'] != kit.pin(manifest_path)['path']]
            doc['sources'] += [kit.pin(manifest_path), kit.pin(scenes_path)]
            if path == two: doc['partOneSha256'] = sha(one)
            write(path, doc); sidecar(path)
        self.archive = kit.base/'synthetic-archive'; self.archive.mkdir()
        self.rows = []
        for spec in self.manifest['cells']+self.manifest['references']:
            is_ref = 'roles' in spec
            for run in ([1] if is_ref else [1, 2, 3]):
                role = 'blind' if is_ref and 'blind' in spec['roles'] else spec.get('role', 'calibration')
                row, raw = fixture.fixture_row(spec, run, self.scenes, role, level=-30 if spec.get('pose') == 'receded' else 20)
                row['roles'] = spec['roles'] if is_ref else [spec['role']]
                row['declarationSha256'] = sha(one)
                if spec['scene'].endswith('inactive'):
                    row['native']['presentedActive'] = False
                    row['native']['presentation'] = dict(observedPose='inactive', isKeyWindow=False, appIsActive=False)
                file = self.archive/row['path']; file.parent.mkdir(parents=True, exist_ok=True)
                file.write_bytes(raw); self.rows.append(row)
        index = fixture.reseal(self.archive, self.rows)
        self.asset = kit.base/'synthetic-archive.tar.zst'; self.asset.write_bytes(b'synthetic archive asset')
        pack = write(repo/'packages/calibration/results/2026-10-08-w50-g1-sitting/pack.json',
                     dict(indexSha256=index, sha256=sha(self.asset), declarationSha256=sha(one)))
        config = write(repo/'native-exposure-inputs.json', dict(schema='w50-native-exposure-inputs-1',
            archiveRoot=str(self.archive), archiveIndexSha256=index,
            archiveAsset={'path': str(self.asset), 'sha256': sha(self.asset)}, pack=kit.pin(pack),
            manifest=kit.pin(manifest_path), scenes=kit.pin(scenes_path), partOne=kit.pin(one), partTwo=kit.pin(two)))
        self.config = kit.pin(config)
        reference = fresh_prepare('w50_native_role_plan_referee')
        plans = reference.read_fixture_plan(self.archive/'index.json', index, self.manifest, self.scenes,
                                            kit.output/'native-blind')
        for run in self.runs:
            pose = 'receded' if run['id'].endswith('receded') else 'active'
            run.update(nativeExposureConfig=self.config,
                       fixtures={k: plans[profile+'|'+pose][k] for k in ('path', 'manifestSha256', 'backgrounds')})
        bootstrap = write(repo/'original-bootstrap-dispatch.py', {'synthetic': 'original bootstrap identity'})
        self.rebind({'partOne': kit.pin(one), 'partTwo': kit.pin(two), 'manifest': kit.pin(manifest_path),
            'inputs': [self.config], 'bootstrap': kit.pin(bootstrap),
            'phaseDependencies': {'ownerUnionKeys': [], 'pendingOwnerKeys': self.pending},
            'reportedKeys': [list(k) for k in reference.R.reported_reference_keys(self.manifest, self.scenes)],
            'emptySupportKeys': [list(k) for k in reference.empty_support_keys(self.manifest, self.scenes)]})
        self.role = kit.register('native', HERE/'native.py', self.config)
        self.role.ROUTER.adapters = lambda: {'w50': Planner(self.scenes), 'canonical': None}

    def rebind(self, extras):
        """Write the final batch/root/contract (with seals) before any attempt names them."""
        kit = self.kit
        kit.batch_path.write_text(json.dumps(kit.batch, indent=2)+'\n')
        kit.doc.update(extras); write(kit.root, kit.doc); sidecar(kit.root)
        kit.body.update(executionRootSha256=sha(kit.root), batch=kit.pin(kit.batch_path))
        kit.write(kit.contract, kit.body); sidecar(kit.contract); sidecar(kit.gate_contract)
        kit.store = kit.L.Store(kit.contract, kit.batch, kit.output)
        kit.data = (kit.doc, kit.body, kit.batch_path, kit.batch, kit.expected, kit.store)

    def tree(self, root):
        return {str(p.relative_to(root)): p.read_bytes() for p in sorted(root.rglob('*')) if p.is_file()}

    @contextlib.contextmanager
    def native_stage(self):
        with self.kit.lease():
            attempt, claim = self.kit.attempt_claim(); self.kit.store.start_native(attempt)
            with self.kit.stage('native', claim) as context:
                yield context

    def original_preparation(self):
        """The sealed prepare_native_exposure under a permissive old-style dispatcher (referee only)."""
        kit = self.kit; original = fresh_prepare('w50_native_role_original_prepare')
        fake = types.ModuleType('w50_native_role_permissive_dispatch')
        fake.__file__ = str(kit.repo/'original-bootstrap-dispatch.py')
        fake.require_render_admission = lambda *a, **k: None
        fake.sealed, fake.checked, fake.load, fake.sha = kit.C.D.sealed, kit.C.D.checked, kit.C.D.load, kit.C.D.sha
        fake.result_for = lambda path: self.gate; fake._LEASE = kit.D._LEASE
        context = {'repo': str(kit.repo), 'executionRoot': str(kit.root), 'contract': str(kit.contract),
                   'batchPath': str(kit.batch_path), 'batch': copy.deepcopy(kit.batch), 'phase': 'exposure',
                   'output': str(kit.output), 'inputs': kit.doc['inputs']}
        with patch.dict(sys.modules, {'w50_g1_dispatch': fake}):
            return original.prepare_native_exposure(context, self.runs[0], self.config)

    def test_role_reproduces_the_sealed_preparation_byte_for_byte_and_verifies(self):
        kit = self.kit
        with kit.lease():
            kit.logical_claim()
            expected = self.original_preparation()
        aside = kit.base/'original-preparation'; aside.mkdir()
        for name in ('native-blind', 'native-blind.started.json'): (kit.output/name).rename(aside/name)
        with self.native_stage() as context:
            payload = self.role.prepare(context, self.config)
            self.role.verify(context, payload, self.config)
        self.assertTrue(payload['ready'])
        self.assertEqual(payload['nativeExposure'], expected)
        produced = {k: v for k, v in self.tree(kit.output).items() if k.startswith('native-blind')}
        self.assertEqual(produced, self.tree(aside))
        self.assertTrue(payload['nativeExposure']['emptySupportWitnesses'])
        self.assertEqual(payload['artifacts'][0], expected['artifactManifest'])

    def test_refuses_outside_the_native_stage_or_with_a_copied_context_before_any_archive_read(self):
        with self.kit.lease():
            attempt, claim = self.kit.attempt_claim(); self.kit.store.start_native(attempt)
            with patch.object(self.role.P.A, 'verify_archive', side_effect=AssertionError('archive read')):
                for stage in ('capture', 'qualification'):
                    with self.kit.stage(stage, claim, attempt['members'][:1]) as context:
                        with self.subTest(stage=stage), self.assertRaisesRegex(ValueError, 'outside its LIVE stage'):
                            self.role.prepare(context, self.config)
                with self.kit.stage('native', claim) as context:
                    with self.assertRaisesRegex(ValueError, 'genuine live context'):
                        self.role.prepare(copy.deepcopy(context), self.config)
                    foreign = dict(self.config, sha256='0'*64)
                    with self.assertRaisesRegex(ValueError, 'not pinned'):
                        self.role.prepare(context, foreign)
        self.assertFalse((self.kit.output/'native-blind.started.json').exists())
        self.assertFalse((self.kit.output/'native-blind').exists())

    def test_refuses_a_gate_without_exposed_pass_and_pending_owners_before_any_archive_read(self):
        with self.kit.lease():
            attempt, claim = self.kit.attempt_claim(); self.kit.store.start_native(attempt)
            for change in ('NEITHER', 'reordered', 'full-union'):
                report = copy.deepcopy(self.gate['report'])
                if change == 'NEITHER': report['status'] = 'NEITHER'
                elif change == 'reordered': report['pendingOwnerKeys'].reverse()
                else: report['ownerChecks'] = 'FULL_UNION'
                with self.subTest(change=change), patch.dict(self.gate, report=report), \
                        patch.object(self.role.P.A, 'verify_archive', side_effect=AssertionError('archive read')), \
                        self.kit.stage('native', claim) as context:
                    with self.assertRaisesRegex(ValueError, 'gate PASS'):
                        self.role.prepare(context, self.config)
        self.assertFalse((self.kit.output/'native-blind.started.json').exists())

    def test_outside_exposure_the_native_capability_refuses(self):
        run = dict(self.runs[0]); run.pop('baselineCandidate')
        fit = K.Kit(self, phase='fit', runs=[run], cohort=[self.candidate])
        role = fit.register('native', HERE/'native.py', self.config)
        with fit.lease():
            attempt, claim = fit.attempt_claim()
            with self.assertRaisesRegex(ValueError, 'exposure-only'): fit.store.start_native(attempt)
            with fit.stage('native', claim) as context:
                with self.assertRaisesRegex(ValueError, 'native preparation capability'):
                    role.prepare(context, self.config)
        self.assertFalse((fit.output/'native-blind.started.json').exists())

    def test_a_second_preparation_is_refused_by_the_role_and_by_the_live_marker(self):
        with self.native_stage() as context:
            self.role.prepare(context, self.config)
            before = self.tree(self.kit.output)
            with self.assertRaises((ValueError, FileExistsError)): self.role.prepare(context, self.config)
        self.assertEqual(self.tree(self.kit.output), before)
        with self.assertRaises(FileExistsError):
            self.kit.store.start_native(self.kit.L.read(self.kit.store._contracts()[0]))
        with self.assertRaisesRegex(ValueError, 'cannot be replayed'):
            self.kit.D.prepare_attempt(self.kit.root, self.kit.contract)
        with self.assertRaisesRegex(ValueError, 'no replay'): self.kit.store.plan()

    def test_an_existing_destination_refuses_before_the_one_shot_claim(self):
        (self.kit.output/'native-blind').mkdir()
        with self.native_stage() as context:
            with self.assertRaisesRegex(ValueError, 'destination exists'): self.role.prepare(context, self.config)
        self.assertFalse((self.kit.output/'native-blind.started.json').exists())

    def test_verify_refuses_a_changed_artifact_or_payload(self):
        with self.native_stage() as context:
            payload = self.role.prepare(context, self.config)
            forged = copy.deepcopy(payload); forged['artifacts'].pop()
            with self.assertRaisesRegex(ValueError, 'pins differ'): self.role.verify(context, forged, self.config)
            with self.assertRaisesRegex(ValueError, 'readiness differs'):
                self.role.verify(context, dict(payload, ready=False), self.config)
            with self.assertRaisesRegex(ValueError, 'one complete preparation'):
                self.role.verify(context, dict(payload, complete=False), self.config)
            stop = {'cell': fixture.PROFILE+'/cell-grey-007-s044__rest', 'statistic': 'deep8-channel-median',
                    'reason': 'NATIVE_SPREAD_EXCEEDS_ONE_CODE'}
            with self.assertRaisesRegex(ValueError, 'readiness differs'):
                self.role.verify(context, dict(payload, stops=[stop]), self.config)
            # A stop the read does not carry, even with a consistent readiness, is refused.
            forged = copy.deepcopy(payload); forged.update(ready=False, stops=[stop])
            forged['nativeExposure']['ready'] = False
            with self.assertRaisesRegex(ValueError, 'another preparation layout|differs'):
                self.role.verify(context, forged, self.config)
            fixture_root = Path(next(iter(payload['nativeExposure']['fixtures'].values()))['path'])
            (fixture_root/'manifest.json').write_text('{"changed": true}\n')
            with self.assertRaisesRegex(ValueError, 'changed'): self.role.verify(context, payload, self.config)

    def execute(self, wrap=None):
        """Register a synthetic capture member transport and count native role calls."""
        kit = self.kit
        capture = kit.repo/'synthetic-capture.py'; capture.write_text(CAPTURE)
        kit.register('capture', capture, kit.pin(capture))
        owner = kit.repo/'synthetic-owner.py'; owner.write_text(OWNER)
        kit.register('owner', owner, kit.pin(owner))
        calls = {'prepare': 0, 'verify': []}
        prepare, verify = self.role.prepare, self.role.verify
        def counted_prepare(context, config):
            calls['prepare'] += 1; return prepare(context, config)
        def counted_verify(context, payload, config):
            calls['verify'].append(context['stage']); return verify(context, payload, config)
        self.role.prepare, self.role.verify = counted_prepare, counted_verify
        if wrap: wrap(self.role)
        return calls

    def test_execute_attempt_prepares_once_and_a_later_attempt_only_verifies_without_public_values(self):
        kit = self.kit; calls = self.execute()
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            first = kit.D.execute_attempt(kit.root, kit.contract, kit.store.plan())
            status = kit.store.status()
            second = kit.D.execute_attempt(kit.root, kit.contract, kit.D.prepare_attempt(kit.root, kit.contract))
        self.assertEqual(first['code'], 'INSTRUMENT_FAULT'); self.assertTrue(status['nativeComplete'])
        self.assertEqual(second['code'], 'ATTEMPT_COMPLETE')
        self.assertEqual(calls, {'prepare': 1, 'verify': ['native', 'qualification']})
        self.assertEqual(kit.store.status()['remaining'], 0)
        report = json.loads((kit.output/'native-blind/native-read.json').read_text())
        values = {repr(v) for c in report['cells'] for s in c['statistics'].values()
                  for v in (s.get('value') if isinstance(s.get('value'), list) else [s.get('value')])
                  if isinstance(v, float) and len(repr(v)) > 6}
        self.assertTrue(values)
        checkpoint = (kit.output/'native-blind/quarantine/checkpoint.json').read_text()
        public = out.getvalue()+str(first)+str(second)+str(status)+str(kit.store.status())+checkpoint
        self.assertFalse([v for v in values if v in public])

    def test_a_noisy_failing_native_read_is_quarantined_and_never_replayed(self):
        kit = self.kit
        def wrap(role):
            measure = role._measure_blind
            def noisy(*args):
                measure(*args); print(CANARY); raise ValueError({'native': CANARY})
            role._measure_blind = noisy
        calls = self.execute(wrap)
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            event = kit.D.execute_attempt(kit.root, kit.contract, kit.store.plan())
            status = kit.D.public_status(kit.root, kit.contract)
        self.assertEqual(event, {'schema': 'w50-live-public-event-1', 'code': 'INSTRUMENT_FAULT',
                                 'phase': 'exposure', 'attempt': 1})
        self.assertNotIn(CANARY, out.getvalue()+str(event)+str(status)+str(kit.store.status()))
        self.assertIn(CANARY, (kit.output/'attempts/000001/quarantine/worker.log').read_text())
        self.assertFalse(kit.store.status()['nativeComplete'])
        with self.assertRaisesRegex(ValueError, 'cannot be replayed'):
            kit.D.prepare_attempt(kit.root, kit.contract)
        self.assertEqual(calls['prepare'], 1)

    def log(self, ordinal):
        return (self.kit.output/f'attempts/{ordinal:06d}/quarantine/worker.log').read_text()

    def test_admission_refusals_burn_nothing_and_a_fixed_environment_then_prepares(self):
        """DL5k: a refusable environment stops before native.started.json, as an ordinary
        recoverable stop, however many times; once fixed, the next attempt prepares once."""
        kit = self.kit; calls = self.execute(); admits = []
        admit = self.role.admit
        def counted_admit(context, config):
            admits.append(context['stage']); return admit(context, config)
        self.role.admit = counted_admit
        asset_aside = kit.base/'asset-aside'; index = self.archive/'index.json'; raw = index.read_bytes()
        native, config = kit.components['native']
        def missing_asset(): self.asset.rename(asset_aside); return lambda: asset_aside.rename(self.asset)
        def changed_index(): index.write_bytes(raw+b' '); return lambda: index.write_bytes(raw)
        def stray_file():
            stray = self.archive/'stray.txt'; stray.write_text('stray'); return stray.unlink
        def foreign_config():
            kit.components['native'] = (native, dict(config, sha256='0'*64))
            return lambda: kit.components.__setitem__('native', (native, config))
        blind = next(self.archive/r['path'] for r in self.rows if r['roles'] == ['blind'])
        frame = blind.read_bytes()
        def corrupt_frame(): blind.write_bytes(frame[:-1]+bytes([frame[-1] ^ 1])); return lambda: blind.write_bytes(frame)
        def partial_extraction():
            aside = kit.base/'frame-aside'; blind.rename(aside); return lambda: aside.rename(blind)
        cases = [(missing_asset, 'archive asset hash mismatch'), (changed_index, 'Archive root hash differs'),
                 (stray_file, 'Archive membership mismatch'), (foreign_config, 'not pinned'),
                 (corrupt_frame, 'Archive hash mismatch'), (partial_extraction, 'Archive hash mismatch')]
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            for ordinal, (break_environment, message) in enumerate(cases, 1):
                restore = break_environment()
                attempt = kit.store.plan() if ordinal == 1 else kit.D.prepare_attempt(kit.root, kit.contract)
                event = kit.D.execute_attempt(kit.root, kit.contract, attempt)
                restore()
                with self.subTest(case=break_environment.__name__):
                    self.assertEqual(event['code'], 'INSTRUMENT_FAULT')
                    self.assertIn(message, self.log(ordinal))
                    self.assertFalse((kit.store.home/'native.started.json').exists())
                    self.assertFalse((kit.output/'native-blind.started.json').exists())
                    self.assertFalse((kit.output/'native-blind').exists())
                    self.assertTrue((kit.store.attempts/f'{ordinal:06d}/failure.json').is_file())
            attempt = kit.D.prepare_attempt(kit.root, kit.contract)
            event = kit.D.execute_attempt(kit.root, kit.contract, attempt)
        self.assertEqual((attempt['ordinal'], event['code']), (len(cases)+1, 'ATTEMPT_COMPLETE'))
        self.assertEqual(admits, ['native-admission']*(len(cases)+1))
        self.assertEqual(calls, {'prepare': 1, 'verify': ['native']})
        self.assertTrue(kit.store.status()['nativeComplete']); self.assertEqual(kit.store.status()['remaining'], 0)

    def test_admit_hashes_every_member_decodes_no_frame_and_writes_nothing(self):
        """The pre-marker admission reads the bytes prepare will read, through the archive's own
        verify_archive (pre-seal review P2), and stops there: no decode, statistic or write."""
        kit = self.kit; opened = []
        real = io.open
        def recording(file, *args, **kwargs):
            if isinstance(file, (str, Path)): opened.append(Path(file).resolve())
            return real(file, *args, **kwargs)
        forbidden = AssertionError('frame decoded or payload read')
        with kit.lease():
            attempt, claim = kit.attempt_claim()
            with kit.stage('native-admission', claim) as context:
                before = self.tree(kit.base)
                with patch('builtins.open', recording), patch('io.open', recording), \
                        patch.object(self.role.P.R, 'read_verified_frame', side_effect=forbidden), \
                        patch.object(self.role.P.R.S, 'read_frame', side_effect=forbidden), \
                        patch.object(self.role.P.R.S, 'decode_png', side_effect=forbidden), \
                        patch.object(self.role.P, '_copy_fixtures', side_effect=forbidden), \
                        patch.object(self.role, '_measure_blind', side_effect=forbidden):
                    self.assertEqual(self.role.admit(context, self.config), {'admitted': True})
                self.assertEqual(self.tree(kit.base), before)
                archive = self.archive.resolve()
                self.assertEqual({p for p in opened if p.is_relative_to(archive)},
                                 {archive/'index.json', archive/'index.sha256'} |
                                 {(archive/r['path']).resolve() for r in self.rows})
                self.assertIn(self.asset.resolve(), opened)
                member = attempt['members'][0]
                for name, call in (('payload', lambda: kit.D.require_payload(context, {'path': str(self.asset)})),
                                   ('native payload', lambda: kit.D.qualification_native(context)),
                                   ('render', lambda: kit.D.require_render_admission(context, member['run'])),
                                   ('read', lambda: kit.D.require_read_admission(context, member['run'])),
                                   ('preparation', lambda: kit.D.require_native_preparation(context)),
                                   ('prepare', lambda: self.role.prepare(context, self.config))):
                    with self.subTest(capability=name), self.assertRaises(ValueError): call()
        self.assertFalse((kit.store.home/'native.started.json').exists())

    def test_admit_refuses_outside_its_stage_after_the_marker_and_outside_exposure(self):
        with self.kit.lease():
            attempt, claim = self.kit.attempt_claim(); self.kit.store.start_native(attempt)
            with self.kit.stage('native', claim) as context:
                with self.assertRaisesRegex(ValueError, 'outside its LIVE stage'): self.role.admit(context, self.config)
            with self.kit.stage('native-admission', claim) as context:
                with self.assertRaisesRegex(ValueError, 'before the one-shot native marker'):
                    self.role.admit(context, self.config)
        run = dict(self.runs[0]); run.pop('baselineCandidate')
        fit = K.Kit(self, phase='fit', runs=[run], cohort=[self.candidate])
        role = fit.register('native', HERE/'native.py', self.config)
        with fit.lease():
            attempt, claim = fit.attempt_claim()
            with fit.stage('native-admission', claim) as context:
                with self.assertRaisesRegex(ValueError, 'native admission capability'):
                    role.admit(context, self.config)
        self.assertFalse((fit.output/'native-blind.started.json').exists())

    # DL5m item 4 and DL5n: what may and may not stop a started read --------------------------
    @contextlib.contextmanager
    def readings(self, frames=(), silhouettes=()):
        """Synthetic blind data properties at the role's own reading seam. `frames` maps
        (cell, run) to a change of the decoded frame; `silhouettes` maps (cell, run) to the
        detected-silhouette mask that run reads instead (its real read_support on that frame)."""
        R = self.role.P.R; frames, silhouettes = dict(frames), dict(silhouettes); last = {}
        verified, read_frame = R.read_verified_frame, R.S.read_frame
        def changed_frame(root, row, canvas, scale):
            rgb = verified(root, row, canvas, scale); last['key'] = (row['cell'], row['run'])
            return frames[last['key']](rgb) if last['key'] in frames else rgb
        def changed_reading(rgb, *args, **kwargs):
            out = read_frame(rgb, *args, **kwargs)
            if last['key'] in silhouettes:
                support = R.S.read_support(rgb, silhouettes[last['key']](rgb.shape[:2]), retain_mask=True)
                out['supports']['full-silhouette'] = support
                out['statistics']['T1-full-silhouette'] = {'status': support['status'], 'support': 'full-silhouette',
                    'units': 'linear-luma', 'value': support.get('linearLumaStdDev')}
            return out
        with patch.object(R, 'read_verified_frame', changed_frame), patch.object(R.S, 'read_frame', changed_reading):
            yield

    def sealed_policy(self, context, artifacts):
        """The sealed prepare._measure_blind over the same export (the pre-seal finding's referee)."""
        P = self.role.P; settings = json.loads((self.kit.repo/self.config['path']).read_text())
        export = Path(artifacts['export']['path'])
        index = P.A.verify_archive(export, artifacts['export']['indexSha256'])
        _, _, rows = P.selected_rows(index, self.manifest, self.scenes, settings['partOne']['sha256'])
        return P._measure_blind(context, self.runs[0], export, artifacts['export']['indexSha256'], rows,
                                self.manifest, self.scenes, settings['partOne']['sha256'])

    def test_incomplete_reported_keys_are_recorded_with_a_metadata_cause_never_a_stop(self):
        """DL5m item 4: a REPORTED blind T1 that reads nothing (a non-eligible key with an empty
        silhouette) or an eligible key empty in only some runs is UNMEASURED_REPORTED with its
        cause; the read stays ready. The sealed policy stopped or raised on both."""
        profile = fixture.PROFILE
        reported = profile+'/cell-grey-028-s224__rest'   # DL5a, active: not DL5c-eligible
        control = profile+'/cell-grey-000-s224__inactive'  # DL5c-eligible, empty in runs 1-2 only
        def block(shape): mask = np.zeros(shape, bool); mask[180:200, 240:270] = True; return mask
        flat = {(reported, n): (lambda rgb: np.full_like(rgb, 28)) for n in (1, 2, 3)}
        with self.native_stage() as context, self.readings(flat, {(control, 3): block}):
            payload = self.role.prepare(context, self.config)
            self.role.verify(context, payload, self.config)
            with self.assertRaisesRegex(ValueError, 'three real zero native silhouettes'):
                self.sealed_policy(context, payload['nativeExposure'])
        self.assertEqual((payload['ready'], payload['complete'], payload['stops']), (True, True, []))
        report = json.loads(Path(payload['nativeExposure']['nativeRead']['path']).read_text())
        self.assertEqual((report['ready'], report['stops']), (True, []))
        cells = {c['id']: c for c in report['cells']}
        for identity, unread, eligible in ((reported, [1, 2, 3], False), (control, [1, 2], True)):
            t1 = cells[identity]['statistics']['T1-full-silhouette']
            self.assertEqual((t1['status'], t1['value'], t1['B'], t1['required']), ('UNMEASURED_REPORTED', None, None, False))
            self.assertEqual(t1['cause'], {'kind': 'INCOMPLETE_READING', 'side': 'native',
                                           'unmeasuredRuns': unread, 'eligibleEmptySupport': eligible})
        self.assertEqual(payload['nativeExposure']['emptySupportWitnesses'], [])
        self.assertEqual({s['status'] for c in report['cells'] for n, s in c['statistics'].items()
                          if c['id'] not in (reported, control) or n != 'T1-full-silhouette'}, {'MEASURED', 'REPORTED'})

    def test_the_sealed_policy_stops_a_non_eligible_empty_reported_key(self):
        """The finding reproduced alone: the sealed policy turns a REPORTED key into a stop."""
        reported = fixture.PROFILE+'/cell-grey-028-s224__rest'
        flat = {(reported, n): (lambda rgb: np.full_like(rgb, 28)) for n in (1, 2, 3)}
        with self.native_stage() as context, self.readings(flat):
            payload = self.role.prepare(context, self.config)
            sealed = self.sealed_policy(context, payload['nativeExposure'])
        self.assertEqual(payload['stops'], [])
        self.assertEqual([(s['cell'], s['statistic'], s['reason']) for s in sealed['stops']],
                         [(reported, 'T1-full-silhouette', 'UNMEASURED_UNAUTHORISED_POPULATION')])

    REQUIRED = [(fixture.PROFILE+'/cell-grey-007-s044__rest', 'central8-channel-median', 'NATIVE_SPREAD_EXCEEDS_ONE_CODE'),
                (fixture.PROFILE+'/cell-grey-007-s044__rest', 'deep8-channel-median', 'NATIVE_SPREAD_EXCEEDS_ONE_CODE'),
                (fixture.PROFILE+'/cell-impulse-sparse-s224__rest', 'T1-full-silhouette', 'UNMEASURED_UNAUTHORISED_POPULATION')]

    def required_stops(self):
        """A required spread past one code (uniform, run 3 three codes up) and a required T1 with
        no silhouette (structured, body drawn at its own black backdrop)."""
        uniform, structured = self.REQUIRED[0][0], self.REQUIRED[2][0]
        up = lambda rgb: (rgb.astype(np.int16)+3).clip(0, 255).astype(np.uint8)
        return self.readings({(uniform, 3): up, **{(structured, n): np.zeros_like for n in (1, 2, 3)}})

    def test_a_required_stop_completes_the_read_not_ready_with_metadata_stops(self):
        """DL5n: the read completes and is returned not ready; its stops are cell, statistic and
        reason only, equal to the read's own stops without their repeat values."""
        with self.native_stage() as context, self.required_stops():
            payload = self.role.prepare(context, self.config)
            self.role.verify(context, payload, self.config)
            for forged, message in ((dict(payload, stops=payload['stops'][1:]), 'stops differ'),
                                    (dict(payload, stops=[dict(s, repeat=None) for s in payload['stops']]), 'metadata'),
                                    (dict(payload, stops=payload['stops'][:1]*2), 'metadata'),
                                    (dict(payload, ready=True), 'readiness differs')):
                with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                    self.role.verify(context, forged, self.config)
        self.assertEqual((payload['ready'], payload['complete'], payload['nativeExposure']['ready']), (False, True, False))
        self.assertEqual([(s['cell'], s['statistic'], s['reason']) for s in payload['stops']], self.REQUIRED)
        report = json.loads(Path(payload['nativeExposure']['nativeRead']['path']).read_text())
        self.assertFalse(report['ready'])
        self.assertEqual([{k: s[k] for k in ('cell', 'statistic', 'reason')} for s in report['stops']], payload['stops'])
        self.assertTrue(report['stops'][0]['repeat']['spreadCodes'])
        self.assertTrue(all(set(s) == {'cell', 'statistic', 'reason'} for s in payload['stops']))

    def test_a_not_ready_read_is_checkpointed_once_and_later_verified_without_public_values(self):
        """Through LIVE: the not-ready payload is the native checkpoint (DL5n), never a stop, and a
        later attempt verifies it at qualification; stdout, events and status carry no value."""
        kit = self.kit; calls = self.execute()
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            with self.required_stops():
                first = kit.D.execute_attempt(kit.root, kit.contract, kit.store.plan())
            status = kit.store.status()
            second = kit.D.execute_attempt(kit.root, kit.contract, kit.D.prepare_attempt(kit.root, kit.contract))
        self.assertEqual((first['code'], second['code']), ('INSTRUMENT_FAULT', 'ATTEMPT_COMPLETE'))
        self.assertTrue(status['nativeComplete'])
        self.assertEqual(calls, {'prepare': 1, 'verify': ['native', 'qualification']})
        checkpoint = json.loads((kit.output/'native-blind/quarantine/checkpoint.json').read_text())
        self.assertEqual((checkpoint['ready'], checkpoint['complete']), (False, True))
        self.assertEqual([(s['cell'], s['statistic'], s['reason']) for s in checkpoint['stops']], self.REQUIRED)
        report = json.loads((kit.output/'native-blind/native-read.json').read_text())
        spreads = {repr(v) for s in report['stops'] if s['repeat'] for v in s['repeat']['spreadCodes']}
        self.assertTrue(spreads)
        public = out.getvalue()+str(first)+str(second)+str(status)+str(kit.store.status())+json.dumps(checkpoint)
        self.assertFalse([v for v in spreads if v in public])

    def test_source_probe_is_source_only(self):
        role = K.module(HERE/'native.py', 'w50_native_role_probe')
        self.assertEqual(role.source_probe(), {'status': 'SOURCE_ONLY'})


if __name__ == '__main__':
    unittest.main()
