"""Synthetic phase capability/config/membership checks; no native or web data is used.

The dispatcher is the REAL LIVE dispatch module with an installed analysis-stage capability
(context, snapshot, hashes, members derived by the real lifecycle, checkpoint records), so
member binding meets LIVE's actual resolve_capture_run/require_read_admission semantics.
"""
import copy
import gzip
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
FIT = HERE.parent
CURRENT3 = FIT.parent/'2026-10-08-w50-g1-current3'
KEY = ('profile', 'renderer', 'scene', 'statistic')


def source(path, name):
    value = types.ModuleType(name); value.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec', dont_inherit=True), value.__dict__)
    return value


P = source(HERE/'phase.py', 'w50_test_phase')
RD = source(HERE/'readiness.py', 'w50_test_phase_readiness')
TR = source(HERE/'test_readiness.py', 'w50_test_phase_readiness_fixtures')
RULES = source(FIT/'judge/rules.py', 'w50_test_phase_judge_rules')
JUDGE = source(FIT/'judge/live.py', 'w50_test_phase_judge_live')
LIVE = FIT/'live-execution'
D = source(LIVE/'dispatch.py', 'w50_test_phase_live_dispatch')
CORE = source(LIVE/'common.py', 'w50_test_phase_live_common')
LIFECYCLE = source(LIVE/'lifecycle.py', 'w50_test_phase_live_lifecycle')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')
    return {'path': str(path), 'sha256': sha(path)}


class PhaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)/'repo'; self.repo.mkdir()
        self.output = Path(self.temp.name)/'output'; self.output.mkdir()
        self.candidate = write(self.repo/'candidate.json', {'synthetic': 'candidate'})
        self.baseline = write(self.repo/'baseline.json', {'synthetic': 'baseline'})
        self.profile = 'apple-macos-27.0-1x-dark-standard-glass0.25'
        self.row = {'profile': self.profile, 'renderer': 'webgpu', 'scene': 'cell',
            'statistic': 'deep8-channel-median', 'role': 'calibration', 'support': 'Original prose.',
            'nativeIdentity': self.profile+'/cell', 'referenceIdentity': self.profile+'/reference',
            'currentGeneration': 'old-generation', 'currentDocumentPair': {'active.dark': 'a'*64, 'receded.dark': 'b'*64},
            'native': None, 'current': None, 'B': None, 'historical': [{'generation': 'old',
                'value': [9, 19, 29], 'enforced': True, 'maxGrowthInB': 1, 'frozenCurrentGrowthInB': .25,
                'captureTree': '/synthetic/history',
                'documentPair': {'active.dark': 'a'*64, 'receded.dark': 'b'*64}}]}
        self.original = write(self.repo/'original.json', {'cells': [self.row]})
        self.completed_row = dict(self.row, native=[10, 20, 30], current=[12, 22, 32], B=1)
        self.completed = write(self.repo/'completed.json', {'cells': [self.completed_row]})
        self.current_report = write(self.repo/'current-report.json', {'synthetic': 'current'})
        self.canonical_report = write(self.repo/'canonical-report.json', {'synthetic': 'canonical'})
        self.native_batch = write(self.repo/'native-batch.json', {'synthetic': 'native batch'})
        self.scenes = write(self.repo/'scenes.json', {'synthetic': 'scenes'})
        self.calibration = write(self.repo/'calibration.json', {'synthetic': 'calibration'})
        self.validation = write(self.repo/'validation.json', {'synthetic': 'validation'})
        self.config_doc = {'schema': 'w50-phase-measurement-inputs-1',
            'completedReferences': self.completed, 'completedCurrentEvidence': self.current_report,
            'canonicalReferenceEvidence': self.canonical_report,
            'native': {'batch': self.native_batch, 'scenes': self.scenes,
                       'reports': {'calibration': self.calibration, 'validation': self.validation}}}
        self.config = write(self.repo/'config.json', self.config_doc)
        self.prefit = write(self.repo/'pre-fit.json', {'references': self.completed})
        self.run = {'id': 'first', 'profile': self.profile, 'renderer': 'webgpu',
            'sceneSource': 'w50', 'scenes': ['cell'], 'sets': ['calibration'], 'candidate': self.candidate,
            'captureRoot': str(self.output/'captures'), 'matrixPath': str(self.output/'matrix.json')}
        self.batch = {'phase': 'fit', 'cohort': [self.candidate], 'runs': [self.run]}
        self.batch_path = self.repo/'batch.json'; write(self.batch_path, self.batch)
        self.contract_path = self.repo/'contract.json'
        self.contract = {'phase': 'fit', 'cohort': [self.candidate], 'preFitEvidence': self.prefit}
        write(self.contract_path, self.contract)
        inputs = [self.config, self.completed, self.current_report, self.canonical_report,
                  self.native_batch, self.scenes, self.calibration, self.validation]
        self.root = {'references': self.original, 'inputs': inputs, 'manifest': self.scenes,
            'currentEvidence': self.current_report, 'currentComposition': self.current_report,
            'reportedKeys': [], 'emptySupportKeys': [], 'repeatAdmission': {'synthetic': True}}
        self.root_path = self.repo/'root.json'; write(self.root_path, self.root)
        self.context = {'repo': str(self.repo), 'executionRoot': str(self.root_path),
            'contract': str(self.contract_path), 'batchPath': str(self.batch_path), 'batch': self.batch,
            'phase': 'fit', 'stage': 'analysis', 'output': str(self.output), 'inputs': inputs, 'gateResult': None,
            'executionClaim': {'path': str(self.repo/'contract.json.phase/analysis.started.json'), 'sha256': 'f'*64},
            'baselineDocuments': [self.baseline], 'repeatAdmission': self.root['repeatAdmission'],
            'expectedCells': [{k: self.row[k] for k in KEY}]}
        self.receipt = {'profile': self.profile, 'renderer': 'webgpu', 'scene': 'cell',
            'sceneSource': 'w50', 'candidate': self.candidate, 'lane': 'candidate',
            'artifacts': {name: write(self.output/(name+'.json'), {'synthetic': name})
                          for name in ('png', 'report', 'cell')},
            'repeatPair': write(self.output/'pair.json', {'synthetic': 'pair'}),
            'repeatAdmission': write(self.output/'repeat-proof.json', {'synthetic': 'proof'})}
        self.captures = {'status': 'CAPTURED', 'candidateSha256s': [self.candidate['sha256']],
                         'phase': 'fit', 'captures': [self.receipt]}
        self.produced = []; self.blind_validated = []
        self.backend = types.SimpleNamespace(measure_member=self.measure_member,
            current_measurement=self.current_measurement, blind_envelope=self.blind_envelope,
            validate_blind_rows=lambda rows: self.blind_validated.extend(rows),
            authenticate=lambda *a: None)
        D._CORE = {'C': CORE, 'L': LIFECYCLE}
        self.install_active()
        self.addCleanup(lambda: setattr(D, '_ACTIVE', None))
        patches = [patch.dict(sys.modules, {'w50_g1_dispatch': D}),
            patch.object(CORE.D, 'lease_owned', return_value=True),
            patch.object(CORE.D, 'sealed', side_effect=lambda path:
                self.root if Path(path) == self.root_path else self.contract),
            patch.object(CORE.D, 'admission_module', return_value=types.SimpleNamespace(
                endpoints=lambda *a, **kw: .25, validate_captures=self.validate_captures)),
            patch.object(P.S, 'PhaseSources', return_value=self.backend)]
        for item in patches:
            item.start(); self.addCleanup(item.stop)

    def members(self):
        """The logical members exactly as the real lifecycle derives them (per-member runs)."""
        store = LIFECYCLE.Store(self.contract_path, self.batch, self.output)
        return [store._member(m, 1) for m in store.population]

    def member_run(self, lane):
        return next(m['run'] for m in self.members() if m['lane'] == lane)

    def install_active(self):
        """LIVE's analysis-stage capability: members and their immutable checkpoint records."""
        write(self.root_path, self.root)
        members = self.members(); records = {}
        for member in members:
            for receipt in self.captures['captures']:
                if all(receipt.get(k) == member['run'][k] for k in ('profile', 'renderer', 'candidate')) \
                        and receipt.get('scene') == member['scene'] and receipt.get('lane') == member['lane']:
                    records[member['id']] = copy.deepcopy(receipt)
        D._ACTIVE = {'context': self.context, 'snapshot': copy.deepcopy(self.context),
            'hashes': [(str(self.contract_path), sha(self.contract_path)), (str(self.batch_path), sha(self.batch_path))],
            'doc': self.root, 'store': None, 'numerical': None, 'members': members,
            'payloads': [], 'records': records}

    def phase(self, value):
        self.context['phase'] = value; self.batch['phase'] = value
        self.captures['phase'] = value; self.contract['phase'] = value
        if value == 'exposure':
            self.run['baselineCandidate'] = self.baseline
            baseline = dict(self.receipt, lane='current', candidate=self.baseline)
            baseline['artifacts'] = {k: write(self.output/('baseline-'+k+'.json'), {'synthetic': k})
                                     for k in ('png', 'report', 'cell')}
            self.captures['captures'] = [self.receipt, baseline]
        write(self.batch_path, self.batch); write(self.contract_path, self.contract)
        self.install_active()

    def validate_captures(self, batch, captures, output):
        self.assertIs(batch, self.batch); self.assertIs(captures, self.captures)
        self.assertEqual(Path(output), self.output)
        if captures.get('status') != 'CAPTURED': raise ValueError('synthetic incomplete capture')
        return {'members': [], 'artifacts': []}

    def statistic(self, value):
        return {'status': 'MEASURED', 'measurementStatus': 'MEASURED', 'value': value,
            'nativeValue': [10, 20, 30], 'required': True, 'support': 'deep8',
            'units': 'encoded-RGB-codes', 'nativeRepeat': {'barCodes': [.5, .5, .5], 'passes': True},
            'nativeSupportWitnesses': [{'run': n, 'maskShape': [64, 64], 'pixels': 100,
                                       'maskPackedBitsSha256': 'c'*64} for n in (1, 2, 3)],
            'nativeRuns': [{'run': n, 'sha256': str(n)*64} for n in (1, 2, 3)]}

    def measure_member(self, run, receipt, rows):
        D.require_read_admission(self.context, run, current=receipt['lane'] == 'current')
        self.produced.append((run, receipt, rows))
        value = [12, 22, 32] if receipt['lane'] == 'current' else [11, 21, 31]
        return {'statistics': {'deep8-channel-median': self.statistic(value)},
            'declaration': {'sceneSource': run['sceneSource'], 'family': 'uniform', 'inputCode': 4,
                'span': 44, 'pose': 'active', 'scale': 1, 'position': .25},
            'material': {'documentPair': {'activeSha256': 'd'*64, 'recededSha256': 'e'*64},
                         'samplingBackend': 'gpu-texture'},
            'evidence': {'capture': receipt['artifacts']['png'], 'repeatPair': receipt['repeatPair'],
                'repeatAdmission': receipt['repeatAdmission'], 'reading': 'first', 'material': {
                    'documentPair': {'activeSha256': 'd'*64, 'recededSha256': 'e'*64}}},
            'nativeCell': {'synthetic': True}}

    def current_measurement(self, row, *, name):
        return self.statistic([12, 22, 32]), {'snapshot': self.current_report,
            'capture': self.receipt['artifacts']['png'], 'material': {
                'documentPair': {'activeSha256': 'a'*64, 'recededSha256': 'b'*64}}}

    def blind_envelope(self, row, measured):
        return {'schema': 'w50-native-three-run-evidence-1', 'synthetic': True,
                **{k: row[k] for k in ('profile', 'scene', 'statistic', 'role', 'support')}}

    def rebind_documents(self):
        self.original = write(self.repo/'original.json', {'cells': [self.row]})
        self.root['references'] = self.original
        self.completed = write(self.repo/'completed.json', {'cells': [self.completed_row]})
        self.config_doc['completedReferences'] = self.completed
        self.config = write(self.repo/'config.json', self.config_doc)
        self.contract['preFitEvidence'] = write(self.repo/'pre-fit.json', {'references': self.completed})
        self.context['inputs'] = [self.config, self.completed, self.current_report, self.canonical_report,
            self.native_batch, self.scenes, self.calibration, self.validation]
        self.root['inputs'] = self.context['inputs']
        write(self.contract_path, self.contract); self.install_active()

    def test_gzip_role_report_pins_are_authenticated_without_json_parsing_at_config_boundary(self):
        path = self.repo/'calibration.json.gz'
        path.write_bytes(gzip.compress(json.dumps({'synthetic': 'calibration'}).encode()))
        self.calibration = {'path': str(path), 'sha256': sha(path)}
        self.config_doc['native']['reports']['calibration'] = self.calibration
        self.rebind_documents()
        result = P.measure_phase(self.context, self.captures, self.config)
        self.assertEqual(result['status'], 'EVIDENCE_ONLY')

    def test_blind_exposure_measures_both_original_lanes_and_pins_native_and_phase_evidence(self):
        self.row.update(role='blind', historical=[])
        self.completed_row = copy.deepcopy(self.row)
        self.rebind_documents(); self.phase('exposure')
        before = copy.deepcopy(self.context)
        result = P.measure_phase(self.context, self.captures, self.config)
        row = result['rows'][0]; reading = row['readings']['deep8-channel-median']
        self.assertEqual(self.context, before)
        self.assertEqual(row['originalReference'], self.row)
        self.assertEqual(row['reference'], self.row)
        self.assertEqual((reading['native'], reading['current'], reading['candidate']),
                         ([10, 20, 30], [12, 22, 32], [11, 21, 31]))
        self.assertEqual([receipt['lane'] for _, receipt, _ in self.produced], ['candidate', 'current'])
        self.assertEqual(self.produced[0][0], self.member_run('candidate'))
        self.assertEqual(self.produced[1][0], self.member_run('current'))
        self.assertEqual(self.produced[1][0]['candidate'], self.baseline)
        self.assertNotIn('baselineCandidate', self.produced[1][0])
        self.assertEqual(self.blind_validated, [row])
        self.assertEqual(row['candidateCapture'], self.receipt)
        self.assertEqual(row['currentCapture'], self.captures['captures'][1])
        self.assertEqual(sha(row['nativeEvidence']['path']), row['nativeEvidence']['sha256'])
        self.assertIsNone(self.row['native']); self.assertIsNone(self.row['current']); self.assertIsNone(self.row['B'])

    def test_fit_and_gate_return_exact_keyed_evidence_without_mutating_references(self):
        for phase in ('fit', 'gate'):
            with self.subTest(phase=phase):
                self.phase(phase)
                target = self.output/'measurement'
                if target.exists():
                    import shutil; shutil.rmtree(target)
                before = copy.deepcopy(self.context)
                result = P.measure_phase(self.context, self.captures, self.config)
                self.assertEqual(result['status'], 'EVIDENCE_ONLY')
                self.assertEqual(result['expectedKeys'], [[self.row[k] for k in KEY]])
                self.assertEqual(self.context, before)
                row = result['rows'][0]
                self.assertEqual(row['originalReference'], self.row)
                self.assertEqual(row['reference'], self.completed_row)
                read = row['readings']['deep8-channel-median']
                self.assertEqual((read['native'], read['current'], read['candidate']),
                                 ([10, 20, 30], [12, 22, 32], [11, 21, 31]))
                self.assertEqual((read['code'], read['bar'], read['B']),
                                 ([1, 1, 1], [.5, .5, .5], [1, 1, 1]))
                self.assertEqual(len(read['nativeSupportWitnesses']), 3)
                self.assertEqual(row['historical'], self.row['historical'])
                self.assertEqual(sha(result['snapshot']['path']), result['snapshot']['sha256'])
                saved = json.loads(Path(result['snapshot']['path']).read_bytes())
                self.assertEqual(saved['rows'], result['rows'])
                for name, path in (('executionRoot', self.root_path), ('contract', self.contract_path),
                                   ('batch', self.batch_path)):
                    self.assertEqual(saved[name]['sha256'], sha(path))
                self.assertEqual(saved['cohort'], self.batch['cohort'])
                self.assertEqual(sha(row['evidence']['path']), row['evidence']['sha256'])

    def test_actual_context_copied_mutated_wrong_phase_or_unregistered_calls_refuse(self):
        for change in ('copied', 'mutated', 'current', 'no-dispatcher'):
            with self.subTest(change=change):
                context = self.context
                if change == 'copied': context = copy.deepcopy(context)
                elif change == 'mutated': context['output'] = '/changed'
                elif change == 'current': self.phase('current')
                else: D._ACTIVE = None
                with self.assertRaises(ValueError): P.measure_phase(context, self.captures, self.config)
                self.assertEqual(self.produced, [])
                self.context['output'] = str(self.output); self.phase('fit')

    def test_config_completed_references_and_companion_pins_are_root_bound(self):
        for change in ('config', 'refs', 'companion', 'prefit'):
            with self.subTest(change=change):
                original_inputs = self.context['inputs'][:]
                original_root_inputs = self.root['inputs'][:]
                original_prefit = self.contract['preFitEvidence']
                if change == 'config': self.context['inputs'].remove(self.config)
                elif change == 'refs': self.root['inputs'] = [p for p in self.root['inputs'] if p != self.completed]
                elif change == 'companion': self.context['inputs'].remove(self.current_report)
                else: self.contract['preFitEvidence'] = write(self.repo/'foreign-prefit.json', {'references': self.original})
                write(self.contract_path, self.contract); self.install_active()
                with self.assertRaises(ValueError): P.measure_phase(self.context, self.captures, self.config)
                self.assertEqual(self.produced, [])
                self.context['inputs'][:] = original_inputs; self.root['inputs'] = original_root_inputs
                self.contract['preFitEvidence'] = original_prefit
                write(self.contract_path, self.contract); self.install_active()

    def test_blind_is_refused_outside_exposure_before_any_measurement(self):
        self.row['role'] = 'blind'
        self.original = write(self.repo/'original.json', {'cells': [self.row]})
        self.root['references'] = self.original
        self.completed_row['role'] = 'blind'
        self.completed = write(self.repo/'completed.json', {'cells': [self.completed_row]})
        self.config_doc['completedReferences'] = self.completed
        self.config = write(self.repo/'config.json', self.config_doc)
        self.contract['preFitEvidence'] = write(self.repo/'pre-fit.json', {'references': self.completed})
        self.context['inputs'] = [self.config, self.completed, self.current_report, self.canonical_report,
            self.native_batch, self.scenes, self.calibration, self.validation]
        self.root['inputs'] = self.context['inputs']; write(self.contract_path, self.contract)
        self.install_active()
        with self.assertRaises(ValueError): P.measure_phase(self.context, self.captures, self.config)
        self.assertEqual(self.produced, [])

    def test_missing_pair_or_proof_refuses_even_if_capture_summary_claims_completion(self):
        for field in ('repeatPair', 'repeatAdmission'):
            with self.subTest(field=field):
                pin = self.receipt.pop(field)
                with self.assertRaises(ValueError): P.measure_phase(self.context, self.captures, self.config)
                self.assertEqual(self.produced, [])
                self.receipt[field] = pin

    def test_duplicates_extras_and_missing_phase_keys_are_refused(self):
        for change in ('duplicate-receipt', 'missing-receipt', 'extra-key', 'missing-key'):
            with self.subTest(change=change):
                receipts = self.captures['captures'][:]
                expected = self.context['expectedCells'][:]
                if change == 'duplicate-receipt': self.captures['captures'].append(self.receipt)
                elif change == 'missing-receipt': self.captures['captures'] = []
                elif change == 'extra-key': self.context['expectedCells'].append(dict(expected[0], statistic='foreign'))
                else: self.context['expectedCells'] = []
                self.install_active()
                with self.assertRaises(ValueError): P.measure_phase(self.context, self.captures, self.config)
                self.assertEqual(self.produced, [])
                self.captures['captures'] = receipts; self.context['expectedCells'] = expected
                self.install_active()

    def test_owner_rows_remain_opaque_and_do_not_invent_numeric_measurements(self):
        owner = dict(self.row, statistic='owner-contracts', native=None, current=None, B=None)
        self.row = owner; self.completed_row = copy.deepcopy(owner)
        self.original = write(self.repo/'original.json', {'cells': [owner]}); self.root['references'] = self.original
        self.completed = write(self.repo/'completed.json', {'cells': [owner]})
        self.config_doc['completedReferences'] = self.completed
        self.config = write(self.repo/'config.json', self.config_doc)
        self.contract['preFitEvidence'] = write(self.repo/'pre-fit.json', {'references': self.completed})
        self.context['expectedCells'] = [{k: owner[k] for k in KEY}]
        self.context['inputs'] = [self.config, self.completed, self.current_report, self.canonical_report,
            self.native_batch, self.scenes, self.calibration, self.validation]
        self.root['inputs'] = self.context['inputs']; write(self.contract_path, self.contract)
        self.phase('gate')
        result = P.measure_phase(self.context, self.captures, self.config)
        row = result['rows'][0]
        self.assertEqual(row['readings'], {})
        self.assertEqual(row['originalReference'], owner)
        self.assertEqual(row['disposition'], 'PENDING_OWNER_UNION')
        self.assertEqual(row['measurementStatus'], 'POINTERS_ONLY')
        self.assertEqual(row['candidateCapture'], self.receipt)
        self.assertNotIn('native', row); self.assertNotIn('candidate', row)

    def test_second_measurement_call_cannot_create_a_second_snapshot_or_remeasure(self):
        P.measure_phase(self.context, self.captures, self.config)
        count = len(self.produced)
        with self.assertRaises(FileExistsError): P.measure_phase(self.context, self.captures, self.config)
        self.assertEqual(len(self.produced), count)

    def test_instrument_failure_keeps_claim_and_cannot_silently_retry(self):
        self.backend.measure_member = lambda *a: (_ for _ in ()).throw(ValueError('synthetic instrument fault'))
        with self.assertRaisesRegex(ValueError, 'instrument fault'):
            P.measure_phase(self.context, self.captures, self.config)
        self.assertTrue((self.output/'measurement').is_dir())
        with self.assertRaises(FileExistsError): P.measure_phase(self.context, self.captures, self.config)

    def test_only_the_analysis_stage_measures(self):
        for stage in ('capture', 'qualification', 'native'):
            with self.subTest(stage=stage):
                self.context['stage'] = stage; self.install_active()
                with self.assertRaisesRegex(ValueError, 'analysis marker'):
                    P.measure_phase(self.context, self.captures, self.config)
                self.assertEqual(self.produced, []); self.assertFalse((self.output/'measurement').exists())
        self.context['stage'] = 'analysis'; self.install_active()

    def test_each_receipt_is_bound_to_its_own_member_and_its_unchanged_checkpoint(self):
        result = P.measure_phase(self.context, self.captures, self.config)
        run = self.produced[0][0]
        self.assertEqual(run, self.member_run('candidate'))
        self.assertEqual(run['scenes'], ['cell']); self.assertNotEqual(run['captureRoot'], self.run['captureRoot'])
        self.assertEqual(result['rows'][0]['candidateCapture'], self.receipt)
        import shutil; shutil.rmtree(self.output/'measurement'); self.produced.clear()
        for change in ('relabelled', 'scene-source'):
            with self.subTest(change=change):
                saved = copy.deepcopy(self.receipt)
                if change == 'relabelled': self.receipt['artifacts']['png'] = {'path': '/foreign.png', 'sha256': 'f'*64}
                else: self.receipt['sceneSource'] = 'canonical'
                with self.assertRaises(ValueError): P.measure_phase(self.context, self.captures, self.config)
                self.assertEqual(self.produced, [])
                self.receipt.clear(); self.receipt.update(saved)
        self.install_active()
        self.receipt['sceneSource'] = 'canonical'; self.install_active()
        with self.assertRaisesRegex(ValueError, 'scene source'):
            P.measure_phase(self.context, self.captures, self.config)

    def test_phase_and_every_keyed_row_carry_the_analysis_claim(self):
        result = P.measure_phase(self.context, self.captures, self.config)
        self.assertEqual(result['executionClaim'], self.context['executionClaim'])
        saved = json.loads(Path(result['snapshot']['path']).read_bytes())
        self.assertEqual(saved['executionClaim'], self.context['executionClaim'])
        keyed = json.loads(Path(result['rows'][0]['evidence']['path']).read_bytes())
        self.assertEqual(keyed['executionClaim'], self.context['executionClaim'])

    def test_current_evidence_must_be_the_root_bound_composed_evidence(self):
        self.root['currentEvidence'] = self.canonical_report; self.install_active()
        with self.assertRaisesRegex(ValueError, 'composed current evidence'):
            P.measure_phase(self.context, self.captures, self.config)
        self.assertEqual(self.produced, [])

    def test_reported_key_defect_reaches_the_strict_snapshot_and_a_gated_key_still_refuses(self):
        """W50 DL5m (4)/DL5k: after the analysis marker a reported key's nonfinite or
        out-of-domain reading is recorded, never a stop; a gated key's still refuses."""
        canary = 987.654321
        producer = self.measure_member
        def defective(run, receipt, rows):
            measured = producer(run, receipt, rows)
            measured['statistics']['deep8-channel-median']['value'] = [11, float('nan'), 31]
            return measured
        self.backend.measure_member = defective
        self.backend.current_measurement = lambda row, *, name: (self.statistic([12, canary, 32]), {
            'snapshot': self.current_report, 'capture': self.receipt['artifacts']['png'],
            'material': {'documentPair': {'activeSha256': 'a'*64, 'recededSha256': 'b'*64}}})
        self.root['reportedKeys'] = [[self.row[k] for k in KEY]]; self.install_active()
        self.phase('gate')
        result = P.measure_phase(self.context, self.captures, self.config)
        read = result['rows'][0]['readings']['deep8-channel-median']
        self.assertEqual((read['native'], read['current'], read['candidate']), ([10, 20, 30], None, None))
        self.assertEqual(read['readingDefects'], [{'kind': 'OUT_OF_DOMAIN_READING', 'side': 'current'},
                                                  {'kind': 'NON_FINITE_READING', 'side': 'candidate'}])
        raw = Path(result['snapshot']['path']).read_text()
        self.assertEqual(json.loads(raw, parse_constant=lambda c: self.fail('nonfinite constant'))['rows'], result['rows'])
        self.assertNotIn('987.654321', raw)
        import shutil; shutil.rmtree(self.output/'measurement')
        self.root['reportedKeys'] = []; self.install_active()
        with self.assertRaisesRegex(ValueError, 'Nonfinite or out-of-domain producer reading') as caught:
            P.measure_phase(self.context, self.captures, self.config)
        self.assertNotIn('987.654321', str(caught.exception))
        self.assertFalse((self.output/'measurement/phase.json').exists())

    def test_blind_reported_native_defect_is_not_bound_as_the_native_aggregate(self):
        """A nulled native side on a blind reported key leaves row native unbound, so the blind
        envelope's native-aggregate comparison cannot refuse it after the marker (DL5m (4))."""
        self.row.update(role='blind', historical=[])
        self.completed_row = copy.deepcopy(self.row)
        self.rebind_documents(); self.phase('exposure')
        self.root['reportedKeys'] = [[self.row[k] for k in KEY]]; self.install_active()
        statistic = self.statistic
        def outside(value):
            produced = statistic(value); produced['nativeValue'] = [10, 300, 30]
            return produced
        self.statistic = outside
        result = P.measure_phase(self.context, self.captures, self.config)
        row = result['rows'][0]
        self.assertNotIn('native', row)
        self.assertEqual(row['readings']['deep8-channel-median']['readingDefects'],
                         [{'kind': 'OUT_OF_DOMAIN_READING', 'side': 'native'}])
        self.assertEqual(self.blind_validated, [row])

    # DL5n and DL5m (4) after the analysis marker: the readiness evaluator's two unread kinds
    # reach the strict snapshot as rows, never a raise, and route as the judge expects.
    def evaluated(self, name, empties, *, reported, stopped=()):
        cell, masks = TR.structured(empties, reported=reported)
        statistic = RD.evaluate_supports(TR.web(), cell, masks, renderer='webgpu',
                                         stopped=set(stopped))['statistics'][name]
        statistic['nativeRuns'] = [{'run': n, 'sha256': str(n)*64} for n in (1, 2, 3)]
        return statistic

    SCENES = {'uniform': 'cell-grey-004-s096__rest', 'structured': 'cell-impulse-sparse-s224__rest',
              'span': 'cell-grey-000-s224__inactive'}

    def blind(self, statistic, produced, *, family, reported=False, eligible=False):
        scene = self.SCENES[family]
        self.row.update(role='blind', historical=[], statistic=statistic, scene=scene,
                        nativeIdentity=self.profile+'/'+scene)
        self.run['scenes'] = [scene]; self.receipt['scene'] = scene
        self.completed_row = copy.deepcopy(self.row)
        self.context['expectedCells'] = [{k: self.row[k] for k in KEY}]
        self.rebind_documents(); self.phase('exposure')
        key = [self.row[k] for k in KEY]
        self.root.update(reportedKeys=[key] if reported else [], emptySupportKeys=[key] if eligible else [])
        self.install_active()
        producer = self.measure_member
        def measure(run, receipt, rows):
            measured = producer(run, receipt, rows)
            measured['statistics'] = {statistic: copy.deepcopy(produced)}
            measured['declaration'].update(family=family, inputCode=4 if family == 'uniform' else 0)
            return measured
        self.backend.measure_member = measure
        result = P.measure_phase(self.context, self.captures, self.config)
        raw = Path(result['snapshot']['path']).read_text()
        self.assertEqual(json.loads(raw, parse_constant=lambda c: self.fail('nonfinite constant'))['rows'],
                         result['rows'])
        self.assertNotIn(TR.CANARY_TEXT, raw)
        row = result['rows'][0]
        self.assertEqual(self.blind_validated, [row])
        routed = RULES.route_row(row, inventory_sha256=self.root['references']['sha256'],
            reported_keys=self.root['reportedKeys'], empty_support_keys=self.root['emptySupportKeys'])
        return row, row['readings'][statistic], routed

    def assert_unread(self, reading, reason):
        self.assertEqual((reading['measurementStatus'], reading['reason']), ('UNMEASURED', reason))
        for side in ('native', 'current', 'candidate'):
            self.assertIsNone(reading[side])
            self.assertEqual((reading[side+'MeasurementStatus'], reading[side+'Reason']), ('UNMEASURED', reason))

    def test_a_stopped_required_blind_level_reaches_the_judge_unmeasured_native_not_ready(self):
        cell, masks, _ = TR.TC.native_cell()
        cell['statistics']['deep8-channel-median'].update(value=[TR.CANARY]*3,
            repeat={'spreadCodes': [TR.CANARY]*3, 'passes': False})
        produced = RD.evaluate_supports(TR.web(), cell, masks, renderer='webgpu',
                                        stopped={'deep8-channel-median'})['statistics']['deep8-channel-median']
        produced['nativeRuns'] = [{'run': n, 'sha256': str(n)*64} for n in (1, 2, 3)]
        row, reading, routed = self.blind('deep8-channel-median', produced, family='uniform')
        self.assert_unread(reading, 'NATIVE_NOT_READY')
        self.assertEqual((reading['B'], reading['reported']), (None, False))
        self.assertNotIn('native', row)
        self.assertEqual(routed['status'], 'UNMEASURED')

    def test_a_stopped_required_blind_t1_with_no_native_silhouette_reaches_the_judge(self):
        produced = self.evaluated('T1-full-silhouette', [True]*3, reported=False, stopped={'T1-full-silhouette'})
        row, reading, routed = self.blind('T1-full-silhouette', produced, family='structured')
        self.assert_unread(reading, 'NATIVE_NOT_READY')
        self.assertNotIn('native', row)
        self.assertEqual(routed['status'], 'UNMEASURED')

    def test_an_incomplete_reported_blind_t1_is_unmeasured_reported_for_the_judge(self):
        cases = {'partly empty': ([True, True, False], True), 'empty, not eligible': ([True]*3, False)}
        for label, (empties, eligible) in cases.items():
            with self.subTest(label):
                import shutil; shutil.rmtree(self.output/'measurement', ignore_errors=True)
                self.blind_validated.clear()
                produced = self.evaluated('T1-full-silhouette', empties, reported=True)
                row, reading, routed = self.blind('T1-full-silhouette', produced, family='span',
                                                  reported=True, eligible=eligible)
                self.assert_unread(reading, 'INCOMPLETE_READING')
                self.assertEqual((reading['B'], reading['reported'], reading['eligibleEmptySupport']),
                                 (None, True, eligible))
                self.assertNotIn('native', row)
                self.assertEqual(routed['status'], 'UNMEASURED')
                gap = JUDGE.reported_gap(routed['status'], reading)
                self.assertEqual((gap['kind'], gap['sides']), ('INCOMPLETE_READING', ['native', 'current', 'candidate']))

    def test_an_eligible_empty_blind_t1_is_unchanged(self):
        produced = self.evaluated('T1-full-silhouette', [True]*3, reported=True)
        row, reading, routed = self.blind('T1-full-silhouette', produced, family='span', reported=True, eligible=True)
        self.assertEqual((reading['measurementStatus'], reading['nativeMeasurementStatus']), ('UNMEASURED_EMPTY_SUPPORT',)*2)
        self.assertNotIn('reason', reading)
        self.assertIn('native', row); self.assertIsNone(row['native'])
        self.assertEqual(routed['status'], 'UNMEASURED_EMPTY_SUPPORT')
        self.assertEqual([w['pixels'] for w in routed['emptySupportWitnesses']], [0]*3)


if __name__ == '__main__':
    unittest.main()
