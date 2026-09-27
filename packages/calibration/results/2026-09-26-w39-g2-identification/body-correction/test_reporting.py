"""Integration checks against recorded evidence and the actual certificate inputs."""
import copy
import gzip
import json
from pathlib import Path
import sys
import unittest
sys.dont_write_bytecode = True
import numpy as np
from replay import summarize, projections, checked_inputs, score, PROJECTION
from solver import channel_constraints, farkas_valid
import body

HERE = Path(__file__).resolve().parent


class ReportingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = json.loads(gzip.decompress((HERE.parent /
            'body/identification-attempt-1.json.gz').read_bytes()))
        cls.correction = json.loads(gzip.decompress((HERE / 'correction-attempt-1.json.gz').read_bytes()))
        cls.evidence = json.loads((HERE.parent / 'body/evidence-complete.json').read_bytes())

    def test_signed_factorial_projection_matches_existing_evidence(self):
        self.assertEqual(PROJECTION, self.evidence['projectionDefinition'])
        key = lambda row: tuple(row[k] for k in ('family', 'endpoint', 'method', 'factorYLevel', 'hueDegrees'))
        expected = {key(r): r for r in self.evidence['diagnostic']}
        for actual in projections(self.original['scores']):
            old = expected.pop(key(actual))
            self.assertEqual(actual['cells'], old['cells'])
            for field in ('signedMeanRGB', 'encodedLumaProjection', 'parallelToLumaVectorRGB',
                          'perpendicularToLumaVectorRGB'):
                np.testing.assert_allclose(actual[field], old[field], atol=1e-12, rtol=0)
        self.assertFalse(expected)

    def test_all_channel_and_repeat_reports_match_recorded_evidence(self):
        key = lambda row: tuple(row[k] for k in ('family', 'endpoint', 'scale', 'method'))
        expected = {key(r): r for r in self.evidence['summary']}
        for actual in summarize(self.original['scores']):
            if actual['population'] != 'colour':
                continue
            old = expected.pop(key(actual))
            for field in old:
                if field == 'maximumRGBMean':
                    self.assertEqual(actual[field]['cell'], old[field]['cell'])
                    self.assertEqual(actual[field]['residualRGB'], old[field]['residualRGB'])
                    # NumPy and Python's three-term mean differ at one float64 ulp.
                    self.assertAlmostEqual(actual[field]['meanCodes'], old[field]['meanCodes'], places=12)
                else:
                    self.assertEqual(actual[field], old[field], (key(actual), field))
        self.assertFalse(expected)

    def test_censored_required_cell_never_survives_even_if_bounds_pass(self):
        row = copy.deepcopy(self.original['rows'][0])
        row['members'][0].update(medianRGB=[255., 100., 100.], barRGB=[.5, .5, .5],
                                 runMediansRGB=[[255., 100., 100.]]*7, censoredChannels=[0])
        s = score(row, 'dark-inactive', 'H3', 'globalMinimax', dict(converged=True),
                  np.array([255., 100., 100.]))
        self.assertEqual(s['failedChannels'], [])
        self.assertEqual(summarize([s])[0]['status'], 'UNMEASURED')

    def test_repeat_state_failure_prevents_a_median_only_pass(self):
        row = copy.deepcopy(self.original['rows'][0])
        row['members'][0].update(medianRGB=[100., 100., 100.], barRGB=[.5, .5, .5],
            runMediansRGB=[[102., 100., 100.]] + [[100., 100., 100.]]*6, censoredChannels=[])
        s = score(row, 'dark-inactive', 'H3', 'globalMinimax', dict(converged=True),
                  np.array([100., 100., 100.]))
        self.assertEqual(s['failedChannels'], [])
        self.assertEqual(summarize([s])[0]['status'], 'failed')

    def test_certificates_bind_to_actual_calibration_arrays_and_forward_upper(self):
        rows = {r['cell']: r for r in self.original['rows']}
        for fit in self.correction['fits']:
            if fit['family'] != 'H3':
                continue
            cells = [rows[c] for c in fit['fitCells']]
            self.assertTrue(all(r['role'] == 'calibration' for r in cells))
            x = np.array([r['inputCodes'] for r in cells])/255
            y = np.array([r['members'][0]['medianRGB'] for r in cells])
            f = np.array(fit['neutralOrdinatesCodes'])/255
            cert = fit['lowerCertificate']; self.assertTrue(farkas_valid(cert))
            a, b, labels = channel_constraints(body.decode(body.h1(x, f)), y[:, cert['channel']],
                                               fit['lowerCodes'])
            for index, label in enumerate(cert['constraints']):
                i = labels.index(tuple(label))
                np.testing.assert_array_equal(a[i], cert['a'][index])
                self.assertEqual(b[i], cert['b'][index])
            actual = np.max(abs(body.h3(x, f, fit['coefficients'])*255-y))
            self.assertEqual(actual, fit['upperCodes'])
            bad = copy.deepcopy(cert); bad['weights'][0] = '-1'
            self.assertFalse(farkas_valid(bad))

    def test_replay_rejects_changed_provenance(self):
        with self.assertRaisesRegex(RuntimeError, 'Input hash mismatch'):
            checked_inputs('0'*64)

    def test_exact_original_least_squares_fits_are_retained(self):
        self.assertEqual(self.correction['originalFits'], self.original['fits'])
        expected = [r for r in self.original['scores'] if r['method'] == 'leastSquares']
        actual = [r for r in self.correction['scores'] if r['method'] == 'leastSquares']
        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
