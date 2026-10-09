"""Synthetic routing/source checks; authority metadata only, no role/image reads or seal creation."""
import copy
import importlib.machinery
from pathlib import Path
import subprocess
import sys
import types
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
G1 = HERE.parent
CURRENT3 = G1.parent/'2026-10-08-w50-g1-current3'


def source(path, name):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


def pin(name, digit):
    return {'path': name, 'sha256': digit * 64}


# Load the real fault type before per-test sys.modules snapshots; NumPy's extension module
# cannot be unloaded by patch.dict cleanup and imported a second time in this process.
InstrumentFault = source(CURRENT3/'repeat/core.py', 'w50_live_test_repeat_fault').InstrumentFault


class RouterTests(unittest.TestCase):
    def setUp(self):
        self.router = source(HERE/'router.py', 'w50_live_test_router')
        self.load_adapters = self.router.adapters
        self.dispatcher = source(CURRENT3/'execution/dispatch.py', 'w50_live_test_dispatch')
        self.candidate = pin('candidate.json', 'a')
        self.baseline = pin('baseline.json', 'b')
        self.config = pin('native-inputs.json', 'c')
        self.calls = []
        self.prepare_calls = []
        self.runs = [self.make_run('w50', 'newbed-active', 'active'),
                     self.make_run('canonical', 'canonical')]
        pending = [['profile', 'webgpu', 'deferred', 'owner-contracts']]
        self.context = {'phase': 'fit', 'repo': str(G1.parents[3]),
            'executionRoot': '/synthetic/root.json', 'contract': '/synthetic/contract.json',
            'batchPath': '/synthetic/batch.json', 'output': '/synthetic/output',
            'batch': {'phase': 'fit', 'cohort': [self.candidate], 'runs': self.runs},
            'baselineDocuments': [self.baseline], 'inputs': [self.config],
            'repeatAdmission': {'entrypoint': pin('repeat/admission.py', '6'),
                                'config': pin('repeat-config.json', '7')},
            'phaseDependencies': {'pendingOwnerKeys': pending}, 'gateResult': None,
            'gateReport': None, 'gateCaptures': None, 'unionExpectedCells': []}
        self.adapters = {
            'canonical': types.SimpleNamespace(capture_run=self.capture),
            'w50': types.SimpleNamespace(_capture_run=self.capture, scene_plan=self.plan)}
        self.native = types.SimpleNamespace(prepare_native_exposure=self.prepare,
            admission=self.native_admission, read_fixture_plan=self.fixture_plan)
        self.install_active()
        self.addCleanup(lambda: setattr(self.dispatcher, '_ACTIVE', None))
        for mock in (patch.dict(sys.modules, {'w50_g1_dispatch': self.dispatcher}),
                     patch.object(self.dispatcher, 'lease_owned', return_value=True),
                     patch.object(self.dispatcher, 'sha', return_value='d'*64),
                     patch.object(self.dispatcher, 'checked', return_value=Path('/synthetic/pin')),
                     patch.object(self.dispatcher, 'admission_module', return_value=
                         types.SimpleNamespace(endpoints=lambda *a, **kw: .25)),
                     patch.object(self.router, 'adapters', return_value=self.adapters),
                     patch.object(self.router, 'native_adapter', return_value=self.native)):
            mock.start(); self.addCleanup(mock.stop)

    def make_run(self, source_name, identity, pose=None):
        run = {'id': identity, 'sceneSource': source_name,
               'profile': 'apple-macos-27.0-1x-dark-standard-glass0.25',
               'renderer': 'webgpu', 'candidate': self.candidate, 'sets': ['calibration'],
               'scenes': [identity+'__'+('inactive' if pose == 'receded' else 'rest')],
               'captureRoot': '/synthetic/output/'+identity,
               'matrixPath': '/synthetic/output/'+identity+'.json'}
        if source_name == 'w50':
            run['fixtures'] = self.fixture(run['profile'], pose or 'active')
        return run

    def fixture(self, profile, pose):
        return {'path': '/synthetic/output/native-blind/fixtures/'+profile+'/'+pose,
                'manifestSha256': 'e'*64,
                'backgrounds': {'grey-004@1x': pin('backgrounds/grey-004@1x.png', 'f')}}

    def install_active(self):
        self.dispatcher._ACTIVE = (self.context, copy.deepcopy(self.context), 'd'*64, 'd'*64,
                                   True, {'repo': self.context['repo']}, pin('numerical.json', '1'))

    def phase(self, phase):
        self.context['phase'] = phase
        self.context['batch']['phase'] = phase
        if phase == 'exposure':
            self.context['gateResult'] = pin('gate.result.json', '2')
            self.context['gateReport'] = {
                'status': 'PASS_EXPOSED_OWNER_PENDING', 'ownerChecks': 'PENDING_FULL_UNION',
                'pendingOwnerKeys': self.context['phaseDependencies']['pendingOwnerKeys'][:],
                'candidateSha256s': [self.candidate['sha256']]}
            for run in self.runs:
                run['baselineCandidate'] = self.baseline
                run['sets'] = ['holdout']
                if run['sceneSource'] == 'w50':
                    run['nativeExposureConfig'] = self.config
        self.install_active()

    def plan(self, run, phase):
        return {'scenes': [{'scene': scene, 'pose':
                           'receded' if scene.endswith('__inactive') else 'active'}
                          for scene in run['scenes']]}

    def capture(self, context, run, *, current):
        self.dispatcher.require_render_admission(context, run, current=current)
        self.calls.append((context, run, current))
        return [dict(profile=run['profile'], renderer=run['renderer'], scene=scene,
                     candidate=run['candidate'], lane='current' if current else 'candidate',
                     sceneSource=run['sceneSource'], artifacts={
                         name: pin('/synthetic/output/'+run['id']+'/'+name, '3')
                         for name in ('cell', 'report', 'png')}) for scene in run['scenes']]

    def native_admission(self, context, run, config):
        self.dispatcher.require_render_admission(context, run)
        self.assertIs(context, self.context); self.assertIs(run, self.runs[0])
        self.assertIs(config, self.config)
        return (self.dispatcher, {'inputs': [self.config]},
                {'archiveRoot': '/synthetic/archive', 'archiveIndexSha256': '7'*64}, {}, {})

    def fixture_plan(self, index, digest, manifest, scenes, destination):
        self.assertEqual(index, Path('/synthetic/archive/index.json'))
        self.assertEqual(digest, '7'*64)
        self.assertEqual(destination, Path('/synthetic/output/native-blind'))
        plans = {}
        for run in self.runs:
            if run['sceneSource'] == 'w50':
                pose = self.plan(run, 'exposure')['scenes'][0]['pose']
                plans[run['profile']+'|'+pose] = {
                    **self.fixture(run['profile'], pose), 'manifest': {'synthetic': True}}
        return plans

    def prepare(self, context, run, config):
        self.dispatcher.require_render_admission(context, run)
        self.prepare_calls.append((context, run, config))
        fixtures = {}
        for selected in self.runs:
            if selected['sceneSource'] == 'w50':
                pose = self.plan(selected, 'exposure')['scenes'][0]['pose']
                fixtures[selected['profile']+'|'+pose] = self.fixture(selected['profile'], pose)
        self.native_result = {'schema': 'w50-native-exposure-artifacts-1', 'role': 'blind',
            'ready': True, 'fixtures': fixtures, 'nativeRead': pin('/synthetic/native.json', '4'),
            'claim': pin('/synthetic/native.started.json', '5'), 'export': {
                'path': '/synthetic/role-export', 'indexSha256': '6'*64},
            'emptySupportWitnesses': [], 'originalArchive': {'indexSha256': '7'*64},
            'artifactManifest': pin('/synthetic/artifacts.json', '8')}
        return self.native_result

    def test_fit_and_gate_route_both_original_runs_without_native_preparation(self):
        for phase in ('fit', 'gate'):
            with self.subTest(phase=phase):
                self.phase(phase); self.calls.clear()
                before = copy.deepcopy(self.context)
                result = self.router.execute(self.context)
                self.assertEqual(result['status'], 'CAPTURED')
                self.assertEqual(result['measurement'], 'capture-completeness-only')
                self.assertEqual(result['phase'], phase)
                self.assertEqual(result['candidateSha256s'], [self.candidate['sha256']])
                self.assertEqual(len(result['captures']), 2)
                self.assertNotIn('nativeExposure', result)
                self.assertEqual(self.prepare_calls, [])
                self.router.native_adapter.assert_not_called()
                for actual, original in zip(self.calls, self.runs):
                    self.assertIs(actual[0], self.context)
                    self.assertIs(actual[1], original)
                    self.assertFalse(actual[2])
                self.assertEqual(self.context, before)

    def test_exposure_prepares_once_and_uses_registered_same_cell_baseline_derivatives(self):
        self.runs.append(self.make_run('w50', 'newbed-receded', 'receded'))
        self.phase('exposure')
        before = copy.deepcopy(self.context)
        with patch.object(self.dispatcher, 'baseline_run', wraps=self.dispatcher.baseline_run) as derivative:
            result = self.router.execute(self.context)
        self.assertEqual(len(self.prepare_calls), 1)
        context, admitted, config = self.prepare_calls[0]
        self.assertIs(context, self.context); self.assertIs(admitted, self.runs[0])
        self.assertIs(config, self.config)
        self.assertGreaterEqual(derivative.call_count, len(self.runs))
        self.assertEqual({id(call.args[0]) for call in derivative.call_args_list},
                         {id(run) for run in self.runs})
        self.assertEqual(len(result['captures']), 6)
        self.assertIs(result['nativeExposure'], self.native_result)
        self.assertEqual(self.context, before)
        for index, original in enumerate(self.runs):
            candidate_call, baseline_call = self.calls[index*2:index*2+2]
            self.assertIs(candidate_call[0], self.context); self.assertIs(candidate_call[1], original)
            self.assertFalse(candidate_call[2])
            self.assertIs(baseline_call[0], self.context); self.assertTrue(baseline_call[2])
            self.assertEqual(baseline_call[1], self.dispatcher.baseline_run(original))
            self.assertIs(baseline_call[1]['fixtures'] if 'fixtures' in original else original,
                          original['fixtures'] if 'fixtures' in original else original)

    def test_every_live_phase_routes_current3_and_keeps_paired_evidence_for_both_sources(self):
        original_source = self.router.source
        expected = {'canonical': CURRENT3/'canonical/adapter.py', 'w50': CURRENT3/'web/adapter.py'}
        loaded = []
        emitted = []
        repeat_binding = self.context['repeatAdmission']
        def paired_source(path, name):
            self.assertIn(path, expected.values(), 'LIVE selected an unpaired transport')
            adapter = original_source(path, name)
            loaded.append(path)
            def paired_capture(context, run, *, current):
                self.assertIs(context['repeatAdmission'], repeat_binding)
                self.assertEqual(path, expected[run['sceneSource']])
                rows = self.capture(context, run, current=current)
                for row in rows:
                    row['repeatPair'] = pin('/synthetic/output/repeat.json', '9')
                    row['repeatAdmission'] = {'status': 'ADMITTED', 'reading': 'first',
                        'artifacts': [pin('/synthetic/output/first.png', '4'),
                                      pin('/synthetic/output/second.png', '5')]}
                    emitted.append(row)
                return rows
            if path == expected['canonical']:
                adapter.capture_run = paired_capture
            else:
                adapter._capture_run = paired_capture
                adapter.scene_plan = self.plan
            return adapter
        with patch.object(self.router, 'adapters', self.load_adapters), \
             patch.object(self.router, 'source', side_effect=paired_source):
            for phase in ('fit', 'gate', 'exposure'):
                with self.subTest(phase=phase):
                    self.phase(phase); loaded.clear(); emitted.clear(); self.calls.clear()
                    before = copy.deepcopy(self.context)
                    result = self.router.execute(self.context)
                    self.assertEqual(set(loaded), set(expected.values()))
                    self.assertEqual(self.context, before)
                    self.assertEqual(len(result['captures']), 4 if phase == 'exposure' else 2)
                    for row, original in zip(result['captures'], emitted):
                        self.assertIs(row, original)
                        self.assertIs(row['repeatPair'], original['repeatPair'])
                        self.assertIs(row['repeatAdmission'], original['repeatAdmission'])
                    self.assertEqual([row['lane'] for row in result['captures']],
                                     ['candidate', 'current', 'candidate', 'current']
                                     if phase == 'exposure' else ['candidate', 'candidate'])

    def test_repeat_instrument_fault_propagates_once_without_retry_or_later_draw(self):
        fault = InstrumentFault('synthetic repeat disagreement')
        attempts = []
        def refuse(context, run, *, current):
            self.dispatcher.require_render_admission(context, run, current=current)
            attempts.append((context, run, current))
            raise fault
        self.adapters['w50']._capture_run = refuse
        for phase in ('fit', 'gate', 'exposure'):
            with self.subTest(phase=phase):
                self.phase(phase); attempts.clear(); self.prepare_calls.clear()
                before = copy.deepcopy(self.context)
                with self.assertRaises(type(fault)) as raised:
                    self.router.execute(self.context)
                self.assertIs(raised.exception, fault)
                self.assertEqual(len(attempts), 1)
                self.assertIs(attempts[0][0], self.context)
                self.assertIs(attempts[0][1], self.runs[0])
                self.assertFalse(attempts[0][2])
                self.assertEqual(self.calls, [])
                self.assertEqual(len(self.prepare_calls), 1 if phase == 'exposure' else 0)
                self.assertEqual(self.context, before)

    def test_current_direct_copied_or_mutated_context_is_refused_without_capture(self):
        for mode in ('current', 'copied', 'mutated', 'unregistered'):
            with self.subTest(mode=mode):
                self.phase('fit'); context = self.context
                if mode == 'current': self.phase('current')
                elif mode == 'copied': context = copy.deepcopy(context)
                elif mode == 'mutated': context['output'] = '/different-output'
                else: self.dispatcher._ACTIVE = None
                with self.assertRaises(ValueError): self.router.execute(context)
                self.assertEqual(self.calls, []); self.assertEqual(self.prepare_calls, [])

    def test_no_dispatcher_or_wrong_batch_phase_is_refused(self):
        with patch.dict(sys.modules):
            sys.modules.pop('w50_g1_dispatch')
            with self.assertRaises(ValueError): self.router.execute(self.context)
        self.context['batch']['phase'] = 'gate'; self.install_active()
        with self.assertRaises(ValueError): self.router.execute(self.context)
        self.assertEqual(self.calls, [])

    def test_all_run_sources_are_checked_before_any_capture(self):
        self.runs.append(dict(self.runs[0], id='foreign', sceneSource='alternate'))
        self.install_active()
        with self.assertRaises(ValueError): self.router.execute(self.context)
        self.assertEqual(self.calls, []); self.assertEqual(self.prepare_calls, [])

    def test_each_run_is_admitted_before_any_native_or_render_work(self):
        self.phase('exposure')
        original = self.dispatcher.require_render_admission
        def refuse_second(context, run, current=False):
            if run is self.runs[1]: raise ValueError('synthetic admission refusal')
            return original(context, run, current=current)
        with patch.object(self.dispatcher, 'require_render_admission', side_effect=refuse_second):
            with self.assertRaises(ValueError): self.router.execute(self.context)
        self.assertEqual(self.calls, []); self.assertEqual(self.prepare_calls, [])

    def test_exposure_requires_qualified_same_candidate_gate_and_exact_pending_owner_order(self):
        pending = self.context['phaseDependencies']['pendingOwnerKeys']
        pending.append(['profile', 'css', 'another', 'owner-contracts'])
        for change in ('bare-pass', 'neither', 'other-candidate', 'wrong-owner-scope',
                       'missing-pending', 'reordered-pending', 'missing-result'):
            with self.subTest(change=change):
                self.phase('exposure')
                report = self.context['gateReport']
                if change == 'bare-pass': report['status'] = 'PASS'
                elif change == 'neither': report['status'] = 'NEITHER'
                elif change == 'other-candidate': report['candidateSha256s'] = ['9'*64]
                elif change == 'wrong-owner-scope': report['ownerChecks'] = 'FULL_UNION'
                elif change == 'missing-pending': report.pop('pendingOwnerKeys')
                elif change == 'reordered-pending': report['pendingOwnerKeys'].reverse()
                else: self.context['gateResult'] = None
                self.install_active()
                with self.assertRaises(ValueError): self.router.execute(self.context)
                self.assertEqual(self.calls, []); self.assertEqual(self.prepare_calls, [])

    def test_missing_or_unregistered_baseline_is_refused_before_blind_preparation(self):
        for change in ('missing', 'unregistered'):
            with self.subTest(change=change):
                self.phase('exposure')
                if change == 'missing': self.runs[0].pop('baselineCandidate')
                else: self.runs[0]['baselineCandidate'] = pin('foreign.json', '9')
                self.install_active()
                with self.assertRaises(ValueError): self.router.execute(self.context)
                self.assertEqual(self.calls, []); self.assertEqual(self.prepare_calls, [])

    def test_exposure_config_must_be_shared_and_registered_without_run_rewrites(self):
        self.runs.append(self.make_run('w50', 'newbed-receded', 'receded'))
        for change in ('missing', 'unregistered', 'different'):
            with self.subTest(change=change):
                self.phase('exposure')
                if change == 'missing': self.runs[0].pop('nativeExposureConfig')
                elif change == 'unregistered': self.context['inputs'] = []
                else: self.runs[-1]['nativeExposureConfig'] = pin('other.json', '9')
                self.install_active()
                before = copy.deepcopy(self.context)
                with self.assertRaises(ValueError): self.router.execute(self.context)
                self.assertEqual(self.context, before)
                self.assertEqual(self.calls, []); self.assertEqual(self.prepare_calls, [])
                self.context['inputs'] = [self.config]

    def test_single_fixture_run_cannot_mix_poses(self):
        self.phase('exposure'); self.runs[0]['scenes'].append('mixed__inactive')
        self.install_active()
        with self.assertRaisesRegex(ValueError, 'pose'): self.router.execute(self.context)
        self.assertEqual(self.calls, []); self.assertEqual(self.prepare_calls, [])

    def test_planned_fixture_mismatch_is_refused_before_blind_preparation(self):
        for field in ('path', 'manifestSha256', 'backgrounds'):
            with self.subTest(field=field):
                self.phase('exposure'); self.prepare_calls.clear()
                fixture = copy.deepcopy(self.fixture(self.runs[0]['profile'], 'active'))
                fixture[field] = {} if field == 'backgrounds' else 'changed'
                self.runs[0]['fixtures'] = fixture; self.install_active()
                before = copy.deepcopy(self.context)
                with self.assertRaisesRegex(ValueError, 'fixture'): self.router.execute(self.context)
                self.assertEqual(self.prepare_calls, [])
                self.assertEqual(self.context, before); self.assertEqual(self.calls, [])

    def test_returned_fixture_mismatch_is_refused_not_repaired_or_rendered(self):
        self.phase('exposure')
        original = self.prepare
        def mismatch(*args):
            result = original(*args)
            result['fixtures'][self.runs[0]['profile']+'|active']['manifestSha256'] = '9'*64
            return result
        self.native.prepare_native_exposure = mismatch
        before = copy.deepcopy(self.context)
        with self.assertRaisesRegex(ValueError, 'fixture'): self.router.execute(self.context)
        self.assertEqual(len(self.prepare_calls), 1)
        self.assertEqual(self.context, before); self.assertEqual(self.calls, [])

    def test_unready_native_evidence_is_returned_without_router_issuing_a_statistical_verdict(self):
        self.phase('exposure')
        original = self.prepare
        def unready(*args):
            result = original(*args); result['ready'] = False; return result
        self.native.prepare_native_exposure = unready
        result = self.router.execute(self.context)
        self.assertEqual(result['status'], 'CAPTURED')
        self.assertFalse(result['nativeExposure']['ready'])
        self.assertNotIn('cells', result); self.assertNotIn('analysis', result)

    def test_canonical_only_exposure_does_not_open_native_blind_branch(self):
        self.runs[:] = [self.runs[1]]; self.phase('exposure')
        result = self.router.execute(self.context)
        self.assertEqual(len(result['captures']), 2)
        self.assertNotIn('nativeExposure', result)
        self.router.native_adapter.assert_not_called()


class SourceProbeTests(unittest.TestCase):
    def test_probe_imports_all_transport_branches_without_reading_data_or_executing_capture(self):
        router = source(HERE/'router.py', 'w50_live_source_probe_test')
        original, original_text = Path.read_bytes, Path.read_text
        g0 = G1.parent/'2026-10-08-w50-g0-declaration'
        metadata = {g0/name for name in ('bed/scenes-w50.json', 'bed/manifest.json',
            'declaration.json', 'declaration.sha256', 'fit-declaration.json', 'fit-declaration.sha256')}
        metadata.update(G1/'native'/name for name in ('instrument-root.json',
            'instrument-root.json.sha256', 'execution-contract.json',
            'execution-contract.json.sha256', 'read-batch.json'))
        metadata.update((CURRENT3/'inputs/repeat-config.json',
                         G1.parent/'2026-10-08-w50-g1-sitting/pack.json'))
        def source_only(path):
            if path.suffix != '.py' and path not in metadata:
                raise AssertionError('non-source file read: '+str(path))
            return original(path)
        def declaration_only(path, *args, **kwargs):
            if path.is_relative_to(G1.parents[3]) and path not in metadata:
                raise AssertionError('repository data read: '+str(path))
            return original_text(path, *args, **kwargs)
        original_run = subprocess.run
        def source_subprocess(argv, *args, **kwargs):
            self.assertEqual(argv[:4], [sys.executable, '-I', '-B', str(g0/'audit/closure.py')])
            self.assertEqual(argv[argv.index('--probe')+1], str(G1/'native/probe.py'))
            return original_run(argv, *args, **kwargs)
        original_source = router.source
        imports = []
        def exercised_source(path, name):
            imports.append(path)
            return original_source(path, name)
        original_code = importlib.machinery.SourceFileLoader.get_code
        def guarded_source(loader, name):
            path = Path(loader.get_filename(name)).resolve()
            if path.is_relative_to(G1.parents[3]):
                return compile(source_only(path), str(path), 'exec', dont_inherit=True)
            return original_code(loader, name)
        with patch.object(Path, 'read_bytes', source_only), \
             patch.object(Path, 'read_text', declaration_only), \
             patch.object(importlib.machinery.SourceFileLoader, 'get_code', guarded_source), \
             patch('subprocess.run', side_effect=source_subprocess), \
             patch.object(router, 'source', side_effect=exercised_source):
            self.assertEqual(router.source_probe(), {'status': 'SOURCE_ONLY'})
        self.assertIn(CURRENT3/'current_router.py', imports)

    def test_runtime_loader_routes_both_sources_to_current3_paired_adapters(self):
        router = source(HERE/'router.py', 'w50_live_source_routes_test')
        adapters = router.adapters()
        self.assertEqual(Path(adapters['w50'].__file__), CURRENT3/'web/adapter.py')
        self.assertEqual(Path(adapters['canonical'].__file__), CURRENT3/'canonical/adapter.py')
        self.assertEqual(Path(router.native_adapter().__file__), G1/'exposure/prepare.py')
        self.assertFalse(hasattr(router, 'execute_current'))


if __name__ == '__main__':
    unittest.main()
