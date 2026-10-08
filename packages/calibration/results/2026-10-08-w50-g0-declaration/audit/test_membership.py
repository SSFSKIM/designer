"""Capture-domain behavior: extra requests and withheld roles never reach compare."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


P = load('planner')
R = load('runner')


class Membership(unittest.TestCase):
    def setUp(self):
        self.run = {'id': 'one', 'profile': 'apple-macos-27.0-1x-dark-standard-glass0.5',
                    'renderer': 'webgpu', 'scenes': ['s'], 'sets': ['calibration'],
                    'candidate': {'path': 'candidate.json', 'sha256': 'a'*64}}

    def test_empty_and_duplicate_membership_refused(self):
        for scenes in ([], ['s', 's']):
            with self.assertRaises(ValueError):
                P.validate_run({**self.run, 'scenes': scenes}, 'gate')

    def test_current_baseline_is_not_a_live_chart_candidate_phase(self):
        with self.assertRaisesRegex(ValueError, 'phase'):
            P.plan({'schema': 'w50-render-batch-1', 'phase': 'baseline', 'runs': [self.run]})

    def test_holdout_and_wrong_material_refused(self):
        for fields in ({'sets': ['holdout']}, {'profile': self.run['profile'].replace('dark','light')}):
            with self.assertRaises(ValueError):
                P.validate_run({**self.run, **fields}, 'gate')

    def test_probe_label_cannot_hide_historical_prediction_check(self):
        plan = P.plan({'schema': 'w50-render-batch-1', 'phase': 'gate', 'runs': [self.run]})
        for role in ('blind', 'historical-prediction-check'):
            reference = {'profile': self.run['profile'], 'renderer': 'webgpu', 'scene': 's', 'role': role}
            with self.assertRaisesRegex(ValueError, 'Withheld'):
                R.validate_membership(plan, {'cells': [reference]})

    def test_extra_request_refused_even_when_batch_itself_is_valid(self):
        plan = P.plan({'schema': 'w50-render-batch-1', 'phase': 'gate', 'runs': [self.run]})
        with self.assertRaisesRegex(ValueError, 'outside'):
            R.validate_membership(plan, {'cells': []})

    def test_missing_or_clamped_numerical_referee_cannot_authorise_candidate(self):
        valid = {'schema': 'w50-candidate-numerical-referee-1', 'status': 'PASS',
                 'candidateSha256s': ['a'*64, 'b'*64], 'domain': {'inputCodeMin': 0, 'inputCodeMax': 64,
                 'stepCode': 1/64, 'spanMin': 32, 'spanMax': 224, 'scales': [1,2],
                 'positions': [0.25,0.5], 'poses': ['active','receded']},
                 'samples': 6325768, 'maxRunningDrawdownCode': 0,
                 'minimumRequestedNeutral': 0, 'fixedJoinPass': True, 'standDownPass': True,
                 'structuredArgumentPass': True,
                 'sources': [{'path': 'test_membership.py', 'sha256': R.sha(Path(__file__))}]}
        # Correct-looking numbers and one unchanged file still do not establish a measured cohort.
        with self.assertRaises(ValueError):
            R.validate_numerical_referee(valid, 'a'*64, HERE)
        for report in ({}, {'status': 'PASS'}, {**valid, 'minimumRequestedNeutral': -0.00001},
                       {**valid, 'maxRunningDrawdownCode': 0.00011},
                       {**valid, 'candidateSha256s': ['b'*64, 'c'*64]}, {**valid, 'samples': 100}):
            with self.subTest(report=report), self.assertRaises(ValueError):
                R.validate_numerical_referee(report, 'a'*64, HERE)

    def test_exposure_claim_is_irreversible_even_after_failed_capture(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            R.claim_exposure(directory, {'candidateId': 'frozen', 'batchSha256': 'a'*64})
            with self.assertRaises(FileExistsError):
                R.claim_exposure(directory, {'candidateId': 'second', 'batchSha256': 'b'*64})

    def test_exact_declared_request_survives(self):
        plan = P.plan({'schema': 'w50-render-batch-1', 'phase': 'gate', 'runs': [self.run]})
        R.validate_membership(plan, {'cells': [{'profile': self.run['profile'], 'renderer': 'webgpu',
                                               'scene': 's', 'role': 'gate'}]})
        self.assertEqual(plan['cells'], 1)


if __name__ == '__main__':
    unittest.main()
