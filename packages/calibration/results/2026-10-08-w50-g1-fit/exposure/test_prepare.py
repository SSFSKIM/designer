"""Synthetic archive pixels and dispatcher claims only; sealed native sources remain untouched."""
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parents[1]
G0 = RESULTS/'2026-10-08-w50-g0-declaration'
G1 = HERE.parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, doc):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2, allow_nan=False)+'\n')
    return path


def sidecar(path):
    Path(str(path)+'.sha256').write_text(f'{sha(path)}  {path.name}\n')


class ExposureTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.repo = self.base/'repo'; self.repo.mkdir()
        results = self.repo/'packages/calibration/results'
        self.home = results/'2026-10-08-w50-g1-fit'
        for name in ('native', 'execution', 'exposure'):
            (self.home/name).mkdir(parents=True)
        for name in ('reader.py', 'statistics.py'):
            shutil.copyfile(G1/'native'/name, self.home/'native'/name)
        for name in ('dispatch.py', 'admission.py'):
            shutil.copyfile(G1/'execution'/name, self.home/'execution'/name)
        shutil.copyfile(HERE/'prepare.py', self.home/'exposure/prepare.py')
        port = results/'2026-10-03-w44-g0-declaration/port/interior.py'
        port.parent.mkdir(parents=True)
        shutil.copyfile(RESULTS/'2026-10-03-w44-g0-declaration/port/interior.py', port)
        archive = results/G0.name/'bed/sitting/archive.py'
        archive.parent.mkdir(parents=True); shutil.copyfile(G0/'bed/sitting/archive.py', archive)
        self.D = load('w50_g1_dispatch', self.home/'execution/dispatch.py')
        self.P = load('w50_blind_prepare', self.home/'exposure/prepare.py')
        fixture = load('w50_blind_tree_fixture', G1/'native/test_reader.py')
        F = load('w50_candidate_fixture', G1/'execution/test_support.py')
        built = F.build(self.repo, G0, self.D.PROOFS)
        self.manifest, self.scenes = fixture.bed()
        for cell in self.manifest['cells']:
            if cell['background'].startswith('grey-'):
                cell['level'] = int(cell['background'][5:])
        profile = fixture.PROFILE
        calibration = next(c for c in self.manifest['cells'] if c['family'] == 'structured')
        structured = dict(calibration, span=224, role='blind',
                          scene='cell-impulse-sparse-s224__rest',
                          id=profile+'/cell-impulse-sparse-s224__rest')
        self.manifest['cells'].append(structured)
        ref = next(r for r in self.manifest['references'] if r['id'] == structured['reference'])
        ref['roles'].append('blind'); ref['roles'].sort()
        self.scenes['scenes'].append(dict(id=structured['scene'], background='impulse-sparse',
                                          component='span-224', state='rest'))
        self.scenes['split']['holdout'].append(structured['scene'])
        self.scenes['profiles'][0]['scenes'].append(structured['scene'])
        control = dict(next(c for c in self.manifest['cells'] if c['family'] == 'span' and c['span'] == 224),
                       background='grey-000', level=0, pose='receded',
                       scene='cell-grey-000-s224__inactive',
                       id=profile+'/cell-grey-000-s224__inactive',
                       reference=profile+'/ref-grey-000__inactive', passName='bed-receded')
        self.manifest['cells'].append(control)
        self.manifest['references'].append(dict(id=control['reference'], scene='ref-grey-000__inactive',
            profile=profile, background='grey-000', roles=['blind'], passName='bed-receded', run=1))
        for scene, component in ((control['scene'], 'span-224'), ('ref-grey-000__inactive', 'none')):
            self.scenes['scenes'].append(dict(id=scene, background='grey-000', component=component, state='inactive'))
            self.scenes['profiles'][0]['scenes'].append(scene)
        self.scenes['split']['holdout'].append(control['scene'])
        self.scenes['split']['recorded'].append('ref-grey-000__inactive')
        self.manifest_path = built['manifest']; write(self.manifest_path, self.manifest)
        self.scenes_path = self.manifest_path.with_name('scenes-w50.json'); write(self.scenes_path, self.scenes)
        self.pin = lambda path: {'path': str(path.relative_to(self.repo)), 'sha256': sha(path)}
        one, two = built['one'], built['two']
        for path in (one, two):
            doc = json.loads(path.read_bytes())
            doc['sources'] = [p for p in doc['sources'] if p['path'] != self.pin(self.manifest_path)['path']]
            doc['sources'] += [self.pin(self.manifest_path), self.pin(self.scenes_path)]
            if path == two: doc['partOneSha256'] = sha(one)
            write(path, doc); sidecar(path)
        self.archive = self.base/'synthetic-archive'; self.archive.mkdir()
        rows = []
        for spec in self.manifest['cells']+self.manifest['references']:
            is_ref = 'roles' in spec
            for run in ([1] if is_ref else [1, 2, 3]):
                role = 'blind' if is_ref and 'blind' in spec['roles'] else spec.get('role', 'calibration')
                level = -30 if spec.get('pose') == 'receded' else 20
                row, raw = fixture.fixture_row(spec, run, self.scenes, role, level=level)
                row['roles'] = spec['roles'] if is_ref else [spec['role']]
                row['declarationSha256'] = sha(one)
                if spec['scene'].endswith('inactive'):
                    row['native']['presentedActive'] = False
                    row['native']['presentation'] = dict(observedPose='inactive', isKeyWindow=False,
                                                          appIsActive=False)
                file = self.archive/row['path']; file.parent.mkdir(parents=True, exist_ok=True)
                file.write_bytes(raw); rows.append(row)
        self.rows = rows
        self.index = fixture.reseal(self.archive, rows)
        self.asset = self.base/'synthetic-archive.tar.zst'; self.asset.write_bytes(b'synthetic archive asset')
        self.pack_path = results/'2026-10-08-w50-g1-sitting/pack.json'
        write(self.pack_path, dict(indexSha256=self.index, sha256=sha(self.asset),
                                   declarationSha256=sha(one)))
        self.config = self.home/'exposure/native-inputs.json'
        write(self.config, dict(schema='w50-native-exposure-inputs-1', archiveRoot=str(self.archive),
            archiveIndexSha256=self.index, archiveAsset={'path': str(self.asset), 'sha256': sha(self.asset)},
            pack=self.pin(self.pack_path), manifest=self.pin(self.manifest_path), scenes=self.pin(self.scenes_path),
            partOne=self.pin(one), partTwo=self.pin(two)))
        self.output = self.base/'dispatcher-output'; self.output.mkdir()
        candidate = next(p for p in built['cohort'] if json.loads((self.repo/p['path']).read_bytes())['glassTintAmount'] == .5)
        self.run = dict(id='blind-run', profile=profile, renderer='webgpu',
            scenes=[c['scene'] for c in self.manifest['cells'] if c['role'] == 'blind'],
            sets=['holdout'], candidate=candidate)
        self.batch_path = write(self.home/'execution/exposure-batch.json',
            dict(phase='exposure', cohort=built['cohort'], runs=[self.run]))
        gate = write(self.home/'execution/gate-contract.json', dict(phase='gate', cohort=built['cohort']))
        sidecar(gate)
        gate_claim = write(Path(str(gate)+'.started.json'), {'contractSha256': sha(gate)})
        self.pending_owner_keys = [[profile, 'webgpu', 'history-1', 'owner-contracts'],
                                   [profile, 'css', 'history-2', 'owner-contracts']]
        gate_result = write(Path(str(gate)+'.result.json'), dict(contractSha256=sha(gate),
            claimSha256=sha(gate_claim), report={'status': 'PASS_EXPOSED_OWNER_PENDING',
              'ownerChecks': 'PENDING_FULL_UNION', 'pendingOwnerKeys': self.pending_owner_keys,
              'candidateSha256s': sorted(p['sha256'] for p in built['cohort'])},
            captureReceipt={'members': ['synthetic-gate-cell'], 'artifacts': []}))
        sidecar(gate_result)
        self.contract = write(self.home/'execution/exposure-contract.json', dict(phase='exposure',
            batch=self.pin(self.batch_path), cohort=built['cohort'], gateContract=self.pin(gate),
            gateResult=self.pin(gate_result)))
        sidecar(self.contract)
        self.gate_result = gate_result
        self.lock = self.base/'gpu.lock'; self.lock.write_text('synthetic-owned-lease\n')
        stat = self.lock.stat(); self.D.GPU_LOCK = self.lock
        self.D._LEASE = {'identity': (stat.st_dev, stat.st_ino), 'token': self.lock.read_text()}
        self.claim = write(Path(str(self.contract)+'.started.json'), dict(phase='exposure', pid=os.getpid(),
            contractSha256=sha(self.contract), batchSha256=sha(self.batch_path), output=str(self.output),
            gpuLease=self.lock.read_text(), numericalAdmission=built['numerical']))
        root_doc = {'repo': str(self.repo), 'bootstrap': self.pin(self.home/'execution/dispatch.py'),
                    'partOne': self.pin(one), 'partTwo': self.pin(two),
                    'manifest': self.pin(self.manifest_path), 'inputs': [self.pin(self.config)],
                    'phaseDependencies': {'pendingOwnerKeys': self.pending_owner_keys},
                    'reportedKeys': self.P.R.reported_reference_keys(self.manifest, self.scenes),
                    'emptySupportKeys': self.P.empty_support_keys(self.manifest, self.scenes),
                    'closure': {'sources': {str(p.relative_to(self.repo)): sha(p) for p in self.repo.rglob('*.py')}}}
        self.root = write(self.home/'execution/execution-root.json', root_doc); sidecar(self.root)
        self.context = {'repo': str(self.repo), 'executionRoot': str(self.root), 'contract': str(self.contract),
            'batchPath': str(self.batch_path), 'batch': json.loads(self.batch_path.read_bytes()),
            'phase': 'exposure', 'output': str(self.output), 'inputs': [self.pin(self.config)],
            'expectedCells': [], 'baselineDocuments': built['baselines']}
        self.D._ACTIVE = (self.context, copy.deepcopy(self.context), sha(self.contract), sha(self.batch_path),
                          True, root_doc, built['numerical'])
        self.addCleanup(lambda: setattr(self.D, '_ACTIVE', None))
        self.addCleanup(lambda: setattr(self.D, '_LEASE', None))

    def prepare(self, context=None, run=None):
        return self.P.prepare_native_exposure(self.context if context is None else context,
            self.run if run is None else run, self.pin(self.config))

    def set_gate_report(self, report):
        # Keep every surrounding synthetic content pin/claim coherent so a protocol rejection
        # cannot pass merely because a changed gate file failed its unrelated hash check.
        result = json.loads(self.gate_result.read_bytes()); result['report'] = report
        write(self.gate_result, result); sidecar(self.gate_result)
        contract = json.loads(self.contract.read_bytes()); contract['gateResult'] = self.pin(self.gate_result)
        write(self.contract, contract); sidecar(self.contract)
        claim = json.loads(self.claim.read_bytes()); claim['contractSha256'] = sha(self.contract)
        write(self.claim, claim)
        active = self.D._ACTIVE
        self.D._ACTIVE = (self.context, copy.deepcopy(self.context), sha(self.contract), active[3],
                          active[4], active[5], active[6])

    def test_one_shot_blind_read_keeps_original_roles_real_supports_and_hash_pinned_fixtures(self):
        result = self.prepare()
        report = json.loads(Path(result['nativeRead']['path']).read_bytes())
        self.assertEqual(report['schema'], 'w50-native-role-read-1')
        self.assertEqual(report['role'], 'blind')
        self.assertTrue(report['ready'])
        self.assertEqual({c['id'] for c in report['cells']},
                         {c['id'] for c in self.manifest['cells'] if c['role'] == 'blind'})
        archive_index = json.loads((Path(result['export']['path'])/'index.json').read_bytes())
        shared = next(r for r in archive_index['files'] if r['cell'].endswith('ref-grey-028__rest'))
        self.assertEqual(shared['roles'], ['blind', 'validation'])
        cell = next(c for c in report['cells'] if c['family'] == 'structured')
        self.assertGreater(cell['runs'][0]['readings']['supports']['deep8_far24']['pixels'], 0)
        self.assertEqual(cell['runs'][0]['evidence']['declarationSha256'], report['declarationSha256'])
        self.assertNotIn('statistics', report['dependencies'][0])
        for fixture in result['fixtures'].values():
            manifest = Path(fixture['path'])/'manifest.json'
            self.assertEqual(sha(manifest), fixture['manifestSha256'])
            for pin in fixture['backgrounds'].values():
                self.assertEqual(sha(Path(fixture['path'])/pin['path']), pin['sha256'])
        self.assertEqual(sha(Path(result['nativeRead']['path'])), result['nativeRead']['sha256'])
        self.assertTrue(result['emptySupportWitnesses'])
        witness = json.loads(Path(result['emptySupportWitnesses'][0]['pin']['path']).read_bytes())
        self.assertEqual(witness['nativeRead'], result['nativeRead'])
        self.assertEqual(witness['role'], 'blind')

    def test_direct_foreign_or_pre_pass_calls_refuse_before_archive_decode_or_artifacts(self):
        for change in ('direct', 'foreign', 'not-pass', 'bare-pass', 'no-claim'):
            with self.subTest(change=change):
                context, run = self.context, self.run
                before = None
                if change == 'direct': context = copy.deepcopy(context)
                elif change == 'foreign': run = dict(run, scenes=['foreign-blind-cell'])
                elif change in ('not-pass', 'bare-pass'):
                    before = self.gate_result.read_bytes()
                    doc = json.loads(before)
                    doc['report']['status'] = 'NEITHER' if change == 'not-pass' else 'PASS'
                    self.set_gate_report(doc['report'])
                else:
                    before = self.claim.read_bytes(); self.claim.unlink()
                with patch.object(self.P.R.S, 'decode_png', side_effect=AssertionError('pixel decode')):
                    with self.assertRaises(ValueError): self.prepare(context, run)
                self.assertFalse((self.output/'native-blind').exists())
                if change in ('not-pass', 'bare-pass'): self.set_gate_report(json.loads(before)['report'])
                elif change == 'no-claim': self.claim.write_bytes(before)

    def test_pending_owner_protocol_requires_exact_ordered_root_keys_and_pending_full_union(self):
        original = json.loads(self.gate_result.read_bytes())['report']
        for change in ('missing-keys', 'missing-row', 'reordered', 'full-union', 'missing-owner-state'):
            with self.subTest(change=change):
                report = copy.deepcopy(original)
                if change == 'missing-keys': del report['pendingOwnerKeys']
                elif change == 'missing-row': report['pendingOwnerKeys'] = report['pendingOwnerKeys'][:1]
                elif change == 'reordered': report['pendingOwnerKeys'].reverse()
                elif change == 'full-union': report['ownerChecks'] = 'FULL_UNION'
                else: del report['ownerChecks']
                self.set_gate_report(report)
                with patch.object(self.P.R.S, 'decode_png', side_effect=AssertionError('pixel decode')):
                    with self.assertRaises(ValueError): self.prepare()
                self.assertFalse((self.output/'native-blind.started.json').exists())
                self.set_gate_report(original)

    def test_second_attempt_and_failed_attempt_cannot_read_again(self):
        self.prepare()
        with self.assertRaises((ValueError, FileExistsError)): self.prepare()
        self.assertTrue((self.output/'native-blind.started.json').is_file())

    def rebind_synthetic_index(self):
        fixture = load('w50_rebound_archive_fixture', G1/'native/test_reader.py')
        index = fixture.reseal(self.archive, self.rows)
        pack = json.loads(self.pack_path.read_bytes()); pack['indexSha256'] = index
        write(self.pack_path, pack)
        config = json.loads(self.config.read_bytes())
        config.update(archiveIndexSha256=index, pack=self.pin(self.pack_path)); write(self.config, config)
        root = json.loads(self.root.read_bytes()); root['inputs'] = [self.pin(self.config)]
        write(self.root, root); sidecar(self.root)
        self.context['inputs'] = root['inputs']
        active = self.D._ACTIVE
        self.D._ACTIVE = (self.context, copy.deepcopy(self.context), active[2], active[3], active[4],
                          root, active[6])

    def test_foreign_blind_membership_is_refused_even_with_self_consistent_registered_hashes(self):
        # Give an exposed frame a foreign blind identity, leaving all PNG/path hashes valid.
        self.rows[0]['roles'] = ['blind']; self.rows[0]['cell'] = 'foreign/cell'
        self.rebind_synthetic_index()
        with self.assertRaisesRegex(ValueError, 'Foreign'):
            self.prepare()
        self.assertTrue((self.output/'native-blind.started.json').exists())
        with self.assertRaises((ValueError, FileExistsError)): self.prepare()

    def test_original_index_hash_failure_burns_the_native_attempt(self):
        fixture = load('w50_changed_archive_fixture', G1/'native/test_reader.py')
        self.rows[0]['native']['extraAttestation'] = {'changed': True}
        fixture.reseal(self.archive, self.rows)
        with self.assertRaises(ValueError): self.prepare()
        self.assertTrue((self.output/'native-blind.started.json').exists())
        with self.assertRaises((ValueError, FileExistsError)): self.prepare()

    def test_original_asset_hash_failure_burns_the_native_attempt(self):
        self.asset.write_bytes(b'changed archive asset')
        with self.assertRaises(ValueError): self.prepare()
        self.assertTrue((self.output/'native-blind.started.json').exists())

    def test_empty_t1_is_permitted_only_for_exact_eligible_keys_with_three_zero_masks(self):
        result = self.prepare()
        report = json.loads(Path(result['nativeRead']['path']).read_bytes())
        control = next(c for c in report['cells'] if c['pose'] == 'receded')
        t1 = control['statistics']['T1-full-silhouette']
        self.assertEqual(t1['status'], 'UNMEASURED_EMPTY_SUPPORT')
        self.assertIsNone(t1['value']); self.assertIsNone(t1['B']); self.assertFalse(t1['required'])
        self.assertEqual(control['statistics']['deep8-channel-median']['status'], 'MEASURED')
        self.assertTrue(control['statistics']['deep8-channel-median']['required'])
        for run in control['runs']:
            support = run['readings']['supports']['full-silhouette']
            self.assertEqual(support['pixels'], 0)
            self.assertFalse(self.P.R.S.decode_support(support).any())

    def test_empty_support_outside_dl5c_remains_a_stop_not_a_reported_success(self):
        from PIL import Image
        import io
        for row in self.rows:
            if row['cell'].endswith('cell-grey-028-s224__rest'):
                stream = io.BytesIO(); Image.new('RGB', (512, 384), (20, 20, 20)).save(stream, format='PNG')
                (self.archive/row['path']).write_bytes(stream.getvalue())
                row['sha256'] = hashlib.sha256(stream.getvalue()).hexdigest()
        self.rebind_synthetic_index()
        result = self.prepare()
        report = json.loads(Path(result['nativeRead']['path']).read_bytes())
        self.assertFalse(report['ready'])
        self.assertTrue(any(s['statistic'] == 'T1-full-silhouette' and
                            s['reason'] == 'UNMEASURED_UNAUTHORISED_POPULATION' for s in report['stops']))
        witnesses = {(w['profile'], w['scene']) for w in result['emptySupportWitnesses']}
        self.assertNotIn((self.run['profile'], 'cell-grey-028-s224__rest'), witnesses)

    def test_required_structured_empty_support_blocks_without_an_exception_witness(self):
        from PIL import Image
        import io
        scene = 'cell-impulse-sparse-s224__rest'
        for row in self.rows:
            if row['cell'].endswith(scene):
                stream = io.BytesIO(); Image.new('RGB', (512, 384), (20, 20, 20)).save(stream, format='PNG')
                (self.archive/row['path']).write_bytes(stream.getvalue())
                row['sha256'] = hashlib.sha256(stream.getvalue()).hexdigest()
        self.rebind_synthetic_index()
        result = self.prepare()
        report = json.loads(Path(result['nativeRead']['path']).read_bytes())
        self.assertFalse(report['ready'])
        self.assertTrue(any(s['cell'].endswith(scene) and s['statistic'] == 'T1-full-silhouette'
                            for s in report['stops']))
        self.assertNotIn((self.run['profile'], scene),
                         {(w['profile'], w['scene']) for w in result['emptySupportWitnesses']})

    def test_metadata_fixture_plan_never_opens_pngs_and_matches_actual_preparation(self):
        index = json.loads((self.archive/'index.json').read_bytes())
        future = self.output/'native-blind'
        with patch.object(self.P.R.S, 'decode_png', side_effect=AssertionError('pixel decode')):
            plans = self.P.plan_fixture_metadata(index, self.manifest, self.scenes, future)
            from_file = self.P.read_fixture_plan(self.archive/'index.json', self.index,
                                                 self.manifest, self.scenes, future)
        self.assertEqual(plans, from_file)
        self.assertFalse(future.exists())
        result = self.prepare()
        self.assertEqual({k: {n: p[n] for n in ('path', 'manifestSha256', 'backgrounds')}
                          for k, p in plans.items()}, result['fixtures'])
        self.assertEqual({key.split('|')[1] for key in plans}, {'active', 'receded'})

    def test_partial_or_changed_zero_masks_cannot_certify_dl5c(self):
        result = self.prepare()
        report = json.loads(Path(result['nativeRead']['path']).read_bytes())
        runs = copy.deepcopy(next(c for c in report['cells'] if c['pose'] == 'receded')['runs'])
        with self.assertRaises(ValueError): self.P.zero_support_witness(runs[:2])
        runs[1]['readings']['supports']['full-silhouette']['maskPackedBitsSha256'] = '0'*64
        with self.assertRaises(ValueError): self.P.zero_support_witness(runs)

    def test_direct_internal_file_read_helpers_require_the_same_live_exposure(self):
        copied = copy.deepcopy(self.context)
        with patch.object(self.P.R.S, 'decode_png', side_effect=AssertionError('pixel decode')):
            with self.assertRaises(ValueError):
                self.P._measure_blind(copied, self.run, self.archive, self.index, {},
                                      self.manifest, self.scenes, '0'*64)
            with self.assertRaises(ValueError): self.P._copy_fixtures(copied, self.run, self.archive, {})

    def test_source_probe_uses_synthetic_pixels_and_never_locates_an_archive(self):
        self.P.source_probe()


if __name__ == '__main__':
    unittest.main()
