"""Synthetic-only proofs; no archive, reader, capture or native payload dependency."""
import argparse
import json
from fractions import Fraction
from pathlib import Path
import unittest
import numpy as np
import body41 as b

HERE = Path(__file__).resolve().parent
NEUTRAL = np.array([69, 83, 96, 108, 119, 134, 146.])
RESULTS = {}


def cloud():
    # Fixed laboratory colours at three levels, not W39 scene inputs.
    rng = np.random.default_rng(991)
    return np.vstack([level + rng.uniform(-22, 22, (14, 3)) for level in (52, 87, 132)])


def planted_e3(x, q):
    luma = x @ np.array([.2126, .7152, .0722])
    f = np.interp(luma, [40, 56, 72, 88, 104, 128, 150], NEUTRAL)
    # The declared neutral curve CONTINUES, unlike the gain's held endpoints.
    f = np.where(luma < 40, 69+(luma-40)*14/16, f)
    f = np.where(luma > 150, 146+(luma-150)*12/22, f)
    f = np.clip(f, 0, 255)
    gain = np.interp(luma, [63, 93, 118], q)
    return np.clip(f[:, None] + gain[:, None] * (x-luma[:, None]), 0, 255)


def independent_certificate(cert, a, rhs):
    # Deliberately does not call implementation's verifier. Bind the proof to
    # regenerated constraints as well as checking exact rational cancellation.
    indices = cert['indices']
    weights = list(map(Fraction, cert['weights']))
    assert len(weights) == len(indices) and all(w >= 0 for w in weights)
    assert sum(weights) == 1
    for j in range(a.shape[1]):
        assert sum(w * Fraction(float(a[i, j])) for w, i in zip(weights, indices)) == 0
    assert sum(w * Fraction(float(rhs[i])) for w, i in zip(weights, indices)) < 0


class BodyProofs(unittest.TestCase):
    def test_e3_planted_gains_and_global_zero(self):
        x = cloud(); q = np.array([1.31, 1.12, .93]); y = planted_e3(x, q)
        np.testing.assert_allclose(b.forward('E3', x, NEUTRAL, q), y, atol=1e-12)
        fit = b.solve_linear('E3', x, NEUTRAL, y)
        self.assertLess(fit['upperCodes'], 1e-7)
        np.testing.assert_allclose(fit['coefficients'], q, atol=1e-7)
        RESULTS['E3'] = fit

    def test_eh6_planted_gains_and_periodic_hue(self):
        # Analytic OKLab hues expose all six gain nodes and wraparound.
        hue = np.deg2rad(np.arange(0, 360, 15))
        lab = np.column_stack((np.full(len(hue), .52), .025*np.cos(hue), .025*np.sin(hue)))
        x = b.colour.encode(b.colour.unlab(lab))*255
        q = np.array([.71, 1.2, .86, 1.4, 1.05, .9])
        actual_hue = np.mod(np.rad2deg(np.arctan2(
            b.colour.lab(b.colour.decode(x/255))[:, 2],
            b.colour.lab(b.colour.decode(x/255))[:, 1])), 360)
        g = np.interp(actual_hue, np.arange(0, 361, 60), np.r_[q, q[0]])
        luma = x @ np.array([.2126, .7152, .0722])
        f = np.interp(luma, [40,56,72,88,104,128,150], NEUTRAL)
        y = f[:, None]+g[:, None]*(x-luma[:, None])
        np.testing.assert_allclose(b.forward('EH6', x, NEUTRAL, q), y, atol=1e-11)
        fit = b.solve_linear('EH6', x, NEUTRAL, y)
        self.assertLess(fit['upperCodes'], 1e-7)
        np.testing.assert_allclose(fit['coefficients'], q, atol=1e-7)
        RESULTS['EH6'] = fit

    def test_wrong_family_fails_one_code_with_independent_certificate(self):
        x = cloud(); y = planted_e3(x, [1.9, 1.1, .35])
        fit = b.solve_linear('EH6', x, NEUTRAL, y)
        self.assertGreater(fit['lowerCodes'], 1)
        self.assertLessEqual(fit['bracketWidthCodes'], 1e-5)
        a, rhs, _ = b.constraints('EH6', x, NEUTRAL, y, fit['lowerCodes'])
        independent_certificate(fit['lowerCertificate'], a, rhs)
        cert = dict(fit['lowerCertificate']); cert['weights'] = ['1']*len(cert['weights'])
        self.assertFalse(b.verify_certificate(cert, a, rhs))
        survival = b.survival_linear('EH6', x, NEUTRAL, y, np.full_like(y, .5))
        self.assertEqual(survival['status'], 'certified-infeasible')
        RESULTS['wrongFamily'] = fit

    def test_censors_are_hard_and_uncensored_channels_remain(self):
        x = np.array([[192,32,32], [32,192,32], [70,80,90.]])
        y = b.forward('E3', x, NEUTRAL, [2,2,2]); y[0,0] = 255
        fit = b.solve_linear('E3', x, NEUTRAL, y)
        prediction = b.forward('E3', x, NEUTRAL, fit['coefficients'])
        self.assertGreaterEqual(prediction[0,0], 250)
        a, rhs, labels = b.constraints('E3', x, NEUTRAL, y, 100)
        rail = labels.index([0, 0, 'high-rail'])
        _, rhs0, labels0 = b.constraints('E3', x, NEUTRAL, y, 0)
        self.assertEqual(rhs[rail], rhs0[labels0.index([0, 0, 'high-rail'])])
        score = b.score(prediction, y)
        self.assertEqual(score['statuses'][0][0], 'censored-bound-satisfied')
        broken = prediction.copy(); broken[0,0] = 249; broken[0,1] += 10
        bad = b.score(broken, y)
        self.assertEqual(bad['statuses'][0][0], 'UNMEASURED')
        self.assertGreater(bad['boundDeficitCodes'][0][0], 0)
        self.assertGreater(bad['uncensoredFailures'], 0)
        # Neutral input cannot meet a high rail at this fixed neutral curve.
        impossible = b.solve_linear('E3', [[80,80,80]], NEUTRAL, [[255,100,100]])
        self.assertEqual(impossible['status'], 'certified-hard-rail-infeasible')
        self.assertNotIn('upperCodes', impossible)
        RESULTS['censor'] = score
        RESULTS['impossibleRail'] = impossible

    def test_neutral_continuation_bounds_and_reject_nonfinite(self):
        x = np.array([[0,0,0], [255,255,255.]])
        expected = np.array([[34,34,34], [203.2727272727]*3])
        np.testing.assert_allclose(b.forward('E3', x, NEUTRAL, [3,0,3]), expected, atol=1e-9)
        for family, q in [('E3', [0,0,4]), ('EH6', [0]*5+[-1]), ('O12',[9]*12)]:
            with self.assertRaises(ValueError): b.forward(family, x, NEUTRAL, q)
        with self.assertRaises(ValueError): b.forward('E3', [[np.nan,0,0]], NEUTRAL, [1]*3)
        with self.assertRaises(ValueError): b.solve_linear('E3', [], NEUTRAL, [])

    def test_o12_planted_recovery_local_rank_and_all_starts(self):
        x = cloud()
        q = np.array([[[1.05,.04],[-.03,.91]], [[.97,-.04],[.03,1.08]],
                      [[.91,.02],[-.05,1.03]]]).ravel()
        z = b.colour.lab(b.colour.decode(x/255)); transformed = z.copy()
        knots = np.array([40,56,72,88,104,128,150.])
        nl = b.colour.lab(b.colour.decode(np.repeat(knots[:,None]/255,3,axis=1)))[:,0]
        ny = b.colour.lab(b.colour.decode(np.repeat(NEUTRAL[:,None]/255,3,axis=1)))[:,0]
        transformed[:,0] = b.colour.curve(z[:,0], nl, ny)
        nodes = np.cbrt([.05,.11,.18])
        for i in range(len(x)):
            matrix = np.array([np.interp(z[i,0], nodes, q.reshape(3,4)[:,j]) for j in range(4)]).reshape(2,2)
            transformed[i,1:] = matrix @ z[i,1:]
        y = b.colour.encode(b.colour.unlab(transformed))*255
        np.testing.assert_allclose(b.forward('O12', x, NEUTRAL, q), y, atol=1e-10)
        fit = b.fit_local('O12', x, NEUTRAL, y)
        self.assertEqual(fit['classification'], 'LOCAL; not a global family negative')
        self.assertEqual(len(fit['starts']), 16)
        self.assertEqual(fit['leastSquares']['rank'], 12)
        self.assertLess(fit['leastSquares']['maximumCodes'], 1e-5)
        self.assertLess(fit['minimax']['maximumCodes'], 1e-5)
        np.testing.assert_allclose(fit['leastSquares']['coefficients'], q, atol=1e-5)
        np.testing.assert_array_equal(fit['starts'][0]['initial'], np.tile([1,0,0,1], 3))
        np.testing.assert_array_equal(fit['starts'][1]['initial'], np.random.default_rng(4100).uniform(-8,8,12))
        RESULTS['O12'] = fit


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results', type=Path, help='Optional write-once synthetic result artifact')
    args = parser.parse_args()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(BodyProofs)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if result.wasSuccessful() and args.results is not None:
        destination = args.results
        # Test results are evidence; refuse overwriting a previous reading.
        with destination.open('x') as out:
            json.dump(RESULTS, out, indent=2, allow_nan=False); out.write('\n')
    raise SystemExit(not result.wasSuccessful())
