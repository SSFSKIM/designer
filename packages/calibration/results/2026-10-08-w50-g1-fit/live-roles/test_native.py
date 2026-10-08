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
            with self.assertRaisesRegex(ValueError, 'ready'): self.role.verify(context, dict(payload, ready=False), self.config)
            fixture_root = Path(next(iter(payload['nativeExposure']['fixtures'].values()))['path'])
            (fixture_root/'manifest.json').write_text('{"changed": true}\n')
            with self.assertRaisesRegex(ValueError, 'changed'): self.role.verify(context, payload, self.config)

    def execute(self, wrap=None):
        """Register a synthetic capture member transport and count native role calls."""
        kit = self.kit
        capture = kit.repo/'synthetic-capture.py'; capture.write_text(CAPTURE)
        kit.register('capture', capture, kit.pin(capture))
        calls = {'prepare': 0, 'verify': []}
        prepare, verify = self.role.prepare, self.role.verify
        def counted_prepare(context, config):
            calls['prepare'] += 1; return prepare(context, config)
        def counted_verify(context, payload, config):
            calls['verify'].append(context['stage']); return verify(context, payload, config)
        self.role.prepare, self.role.verify = counted_prepare, counted_verify
        if wrap: wrap(self.role.P)
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
        def wrap(P):
            measure = P._measure_blind
            def noisy(*args):
                measure(*args); print(CANARY); raise ValueError({'native': CANARY})
            P._measure_blind = noisy
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

    def test_source_probe_is_source_only(self):
        role = K.module(HERE/'native.py', 'w50_native_role_probe')
        self.assertEqual(role.source_probe(), {'status': 'SOURCE_ONLY'})


if __name__ == '__main__':
    unittest.main()
