"""The LIVE measurement role against the REAL LIVE dispatcher/journal (livekit).

The science backend (measurement/phase_sources.PhaseSources) is a synthetic stand-in here; its
own suites cover it. These tests cover the role boundary: stage, the analysis claim, member
binding to the immutable checkpoints, and the quarantine of every value (DL5k).
"""
import contextlib
import copy
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('w50_measurement_role_kit', HERE/'livekit.py')
K = importlib.util.module_from_spec(spec); spec.loader.exec_module(K)
SECRET = 'NATIVE_SECRET_12345.875'
PROFILE = 'apple-macos-27.0-1x-dark-standard-glass0.25'
STATISTIC = 'deep8-channel-median'


class MeasurementRole(unittest.TestCase):
    def setUp(self):
        self.candidate = {'path': 'candidate.json', 'sha256': 'a'*64}
        run = {'id': 'r', 'profile': PROFILE, 'renderer': 'webgpu', 'sceneSource': 'w50', 'scenes': ['one', 'two'],
               'sets': ['calibration'], 'candidate': self.candidate, 'captureRoot': 'unused', 'matrixPath': 'unused'}
        self.kit = kit = K.Kit(self, phase='fit', runs=[run], cohort=[self.candidate], statistics=(STATISTIC,))
        kit.put('candidate.json', {'synthetic': 'candidate'})
        cells = json.loads((kit.repo/'references.json').read_text())['cells']
        completed = kit.pin(kit.put('completed.json', {'cells': cells}))
        companions = {name: kit.pin(kit.put(name+'.json', {'synthetic': name}))
                      for name in ('current', 'canonical', 'native-batch', 'scenes', 'calibration', 'validation')}
        self.config = kit.pin(kit.put('measurement-config.json', {'schema': 'w50-phase-measurement-inputs-1',
            'completedReferences': completed, 'completedCurrentEvidence': companions['current'],
            'canonicalReferenceEvidence': companions['canonical'],
            'native': {'batch': companions['native-batch'], 'scenes': companions['scenes'],
                       'reports': {'calibration': companions['calibration'], 'validation': companions['validation']}}}))
        kit.doc['inputs'][:] = [self.config, completed, *companions.values()]
        kit.doc.update(currentEvidence=companions['current'], currentComposition=companions['current'])
        kit.reseal()
        kit.body['preFitEvidence'] = kit.pin(kit.put('pre-fit-evidence.json', {'references': completed}))
        kit.write(kit.contract, kit.body)
        Path(str(kit.contract)+'.sha256').write_text(f'{K.sha(kit.contract)}  {kit.contract.name}\n')
        self.role = kit.register('measurement', HERE/'measurement.py', self.config)
        self.produced = []
        self.backend = types.SimpleNamespace(measure_member=self.measure_member,
            current_measurement=self.current_measurement, blind_envelope=None, validate_blind_rows=None)
        patcher = patch.object(self.role.P.S, 'PhaseSources', return_value=self.backend)
        patcher.start(); self.addCleanup(patcher.stop)

    def statistic(self, value):
        return {'status': 'MEASURED', 'measurementStatus': 'MEASURED', 'value': value, 'nativeValue': [10, 20, 30],
            'required': True, 'support': 'deep8', 'units': 'encoded-RGB-codes',
            'nativeRepeat': {'barCodes': [.5, .5, .5], 'passes': True},
            'nativeSupportWitnesses': [{'run': n, 'maskShape': [64, 64], 'pixels': 100,
                                       'maskPackedBitsSha256': 'c'*64} for n in (1, 2, 3)],
            'nativeRuns': [{'run': n, 'sha256': str(n)*64} for n in (1, 2, 3)]}

    def measure_member(self, run, receipt, rows):
        self.produced.append((run, receipt))
        return {'statistics': {STATISTIC: self.statistic([11, 21, 31])},
            'declaration': {'sceneSource': 'w50', 'family': 'uniform', 'inputCode': 4, 'span': 44,
                            'pose': 'active', 'scale': 1, 'position': .25},
            'material': {'documentPair': {'activeSha256': 'd'*64, 'recededSha256': 'e'*64}},
            'evidence': {'capture': receipt['artifacts']['png'], 'material': {
                'documentPair': {'activeSha256': 'd'*64, 'recededSha256': 'e'*64}}}}

    def current_measurement(self, row, *, name):
        return self.statistic([12, 22, 32]), {'capture': self.kit.pin(self.kit.repo/'current.json'),
            'material': {'documentPair': {'activeSha256': 'a'*64, 'recededSha256': 'b'*64}}}

    def captured(self):
        """Every member captured, checkpointed and finished under one real attempt claim."""
        kit = self.kit; records = []
        with kit.lease():
            attempt, claim = kit.attempt_claim()
            for member in attempt['members']:
                base = Path(member['run']['captureRoot'])/member['scene']
                pins = {}
                for name, value in (('png', b'png'), ('report', b'{}'), ('cell', b'{}')):
                    path = base/(name+'.bin'); path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes(value)
                    pins[name] = kit.L.pin(path)
                pair = base/'pair.json'; pair.write_text(json.dumps({'first': pins['png']}))
                proof = base/'repeat-admission__webgpu.json'
                proof.write_text(json.dumps({'manifest': kit.L.pin(pair), 'pair': {'first': pins['png']}, 'originalArtifacts': pins}))
                record = {'profile': PROFILE, 'renderer': 'webgpu', 'scene': member['scene'], 'lane': member['lane'],
                    'candidate': member['candidate'], 'sceneSource': 'w50', 'artifacts': pins,
                    'repeatPair': kit.L.pin(pair), 'repeatAdmission': kit.L.pin(proof), 'secret': SECRET}
                kit.store.checkpoint(attempt, member, record, list(pins.values()))
                records.append(record)
            kit.store.finish(attempt)
        return attempt, claim, records

    def captures(self, records):
        return {'schema': 'w50-live-composed-captures-1', 'status': 'CAPTURED',
                'candidateSha256s': [self.candidate['sha256']], 'captures': copy.deepcopy(records)}

    @contextlib.contextmanager
    def analysis(self, claim=None):
        kit = self.kit; attempt, attempt_claim, records = self.captured()
        rows = kit.store.checkpoints()
        with kit.lease():
            marker = claim(kit, attempt_claim) if claim else kit.analysis_claim()
            with kit.stage('analysis', marker, [r['member'] for r in rows], [r['payload'] for r in rows]) as context:
                yield context, records, marker

    def test_measures_the_union_bound_to_each_member_and_carries_the_analysis_claim(self):
        with self.analysis() as (context, records, marker):
            result = self.role.evaluate(context, self.captures(records), self.config)
        self.assertEqual(result['executionClaim'], marker)
        self.assertEqual(json.loads(Path(result['snapshot']['path']).read_text())['executionClaim'], marker)
        for row in result['rows']:
            self.assertEqual(json.loads(Path(row['evidence']['path']).read_text())['executionClaim'], marker)
        members = {r['member']['scene']: r['member']['run'] for r in self.kit.store.checkpoints()}
        self.assertEqual([run for run, _ in self.produced], [members['one'], members['two']])
        self.assertTrue(all('/attempts/000001/quarantine/' in run['captureRoot'] for run, _ in self.produced))

    def test_refuses_outside_the_analysis_stage_before_reading_any_input(self):
        kit = self.kit
        with kit.lease():
            attempt, claim = kit.attempt_claim()
            for stage, members in (('capture', attempt['members'][:1]), ('qualification', attempt['members'])):
                with self.subTest(stage=stage), kit.stage(stage, claim, members) as context, \
                        patch.object(self.role.P, 'inputs', side_effect=AssertionError('input read')):
                    with self.assertRaisesRegex(ValueError, 'outside its LIVE stage'):
                        self.role.evaluate(context, {'captures': []}, self.config)
        self.assertFalse((kit.output/'measurement').exists())

    def test_refuses_an_analysis_context_without_this_process_full_union_marker(self):
        def elsewhere(kit, claim):
            return kit.L.write_once(kit.store.home/'elsewhere.started.json', {'schema': 'w50-live-analysis-claim-1',
                'logicalContract': kit.L.pin(kit.contract), 'captures': kit.L.pin(kit.batch_path),
                'pid': os.getpid(), 'gpuLease': kit.D._LEASE['token'], 'output': str(kit.output)})
        with self.analysis(elsewhere) as (context, records, _):
            with self.assertRaisesRegex(ValueError, 'full-union analysis marker'):
                self.role.evaluate(context, self.captures(records), self.config)
        self.assertEqual(self.produced, [])

    def test_refuses_a_marker_held_by_another_process(self):
        def foreign(kit, claim):
            return kit.L.write_once(kit.store.analysis_marker, {'schema': 'w50-live-analysis-claim-1',
                'logicalContract': kit.L.pin(kit.contract), 'captures': kit.L.pin(kit.batch_path),
                'pid': os.getpid()+1, 'gpuLease': kit.D._LEASE['token'], 'output': str(kit.output)})
        with self.analysis(foreign) as (context, records, _):
            with self.assertRaisesRegex(ValueError, 'this process and lease'):
                self.role.evaluate(context, self.captures(records), self.config)
        self.assertFalse((self.kit.output/'measurement').exists())

    def test_a_receipt_differing_from_its_checkpoint_refuses(self):
        with self.analysis() as (context, records, _):
            captures = self.captures(records)
            captures['captures'][1]['artifacts']['png'] = captures['captures'][0]['artifacts']['png']
            with self.assertRaisesRegex(ValueError, 'original checkpoint'):
                self.role.evaluate(context, captures, self.config)
        self.assertEqual(self.produced, [])

    def run_analysis(self, backend_failure):
        """The real execute_analysis; returns (public event, everything printed, public status)."""
        kit = self.kit; self.captured()
        def noisy(run, receipt, rows):
            print(SECRET); print(SECRET, file=sys.stderr); os.write(1, SECRET.encode()); os.write(2, SECRET.encode())
            if backend_failure: raise ValueError({'nativeRead': SECRET})
            return self.measure_member(run, receipt, rows)
        self.backend.measure_member = noisy
        fit = kit.repo/'fit-role.py'
        fit.write_text("def evaluate(context, measured, config):\n print('NATIVE_SECRET_12345.875')\n return {'synthetic': 'analysis'}\n")
        kit.register('fit', fit, self.config)
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            event = kit.D.execute_analysis(kit.root, kit.contract)
            status = kit.D.public_status(kit.root, kit.contract)
        return event, out.getvalue(), status

    def test_a_stopped_analysis_publishes_only_its_code(self):
        event, printed, status = self.run_analysis(True)
        self.assertEqual(event, {'schema': 'w50-live-public-event-1', 'code': 'ANALYSIS_STOPPED', 'phase': 'fit'})
        self.assertNotIn('NATIVE_SECRET', printed+json.dumps(event)+json.dumps(status))
        self.assertTrue(status['analysisStarted'])
        log = self.kit.output/'quarantine/analysis.log'
        self.assertIn(SECRET, log.read_text())
        self.assertFalse(Path(str(self.kit.contract)+'.result.json').exists())

    def test_a_completed_analysis_publishes_only_its_code(self):
        event, printed, status = self.run_analysis(False)
        self.assertEqual(event, {'schema': 'w50-live-public-event-1', 'code': 'ANALYSIS_COMPLETE', 'phase': 'fit'})
        self.assertNotIn('NATIVE_SECRET', printed+json.dumps(event)+json.dumps(status))
        result = json.loads(Path(str(self.kit.contract)+'.result.json').read_text())
        self.assertEqual(result['analysisClaim'], self.kit.L.pin(self.kit.store.analysis_marker))
        self.assertEqual(result['report']['analysis'], {'synthetic': 'analysis'})


if __name__ == '__main__':
    unittest.main()
