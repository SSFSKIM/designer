"""Synthetic proof of forward, population, repeat, censor and native boundaries."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import scorer as s


class ForwardTests(unittest.TestCase):
    def test_end_segment_continuation_and_neutral_chroma(self):
        x = np.repeat(np.array([0., 32., 40., 150., 192., 255.])[:, None], 3, axis=1)
        y = s.e3(x, [150,157,164,171,178,188,197], [.9,.95,1.])
        np.testing.assert_allclose(y[:, 0], [132.5,146.5,150,197,214.1818181818,239.9545454545])
        np.testing.assert_array_equal(y[:, 0], y[:, 1])
        np.testing.assert_array_equal(y[:, 1], y[:, 2])

    def test_radial_gain_held_endpoints_and_interpolation(self):
        x = np.array([[10,40,70], [90,90,130], [200,230,250]], float)
        y = x @ s.colour.W
        expected = s.colour.curve(y, s.KNOTS, np.arange(7)/10)*255
        gain = np.interp(y, [63,93,118], [.4,.7,1.2])
        np.testing.assert_allclose(s.e3(x, np.arange(7)*25.5, [.4,.7,1.2]),
                                   np.clip(expected[:, None] + gain[:, None]*(x-y[:, None]),0,255))

    def test_all_members_and_native_only_holdout_in_public_prediction_scope(self):
        cells, _ = s.runner.admitted_scope(s.ROOT, s.wave)
        predictions = s.predictions()
        self.assertEqual(set(predictions['cells']), set(cells['numerical']))
        self.assertEqual(len(predictions['cells']), 648)
        held = [c for c in predictions['cells'] if s.wave.roles[c.split('/',1)[1]] == 'holdout']
        self.assertEqual(len(held), 72)
        self.assertEqual(len(set(held)-set(cells['rendered'])), 8)
        for cell, row in predictions['cells'].items():
            shapes = s.m.readers.shapes_of(s.base.component(cell)[0])
            self.assertEqual([r['member'] for r in row['members']],
                             [i for i, shape in enumerate(shapes) if not shape.opaque])
            self.assertTrue(all(np.all(np.isfinite(m['predictedRGB'])) for m in row['members']))

    def test_s0_applies_before_median(self):
        rgb = np.array([[0,0,0],[10,10,10],[220,220,220],[250,250,250]], float)
        prediction = s.local_prediction(rgb, 'light-inactive', 44)
        expected = np.median(s.e3(rgb, s.parameters()['neutral'], s.parameters()['coefficients']), axis=0)
        np.testing.assert_array_equal(prediction, expected)
        self.assertFalse(np.allclose(prediction, s.local_prediction(np.median(rgb,axis=0)[None], 'light-inactive',44)))

    def test_import_and_project_need_no_scipy_or_native_reader(self):
        code = '''import sys, importlib.abc
class Deny(importlib.abc.MetaPathFinder):
 def find_spec(self, fullname, path=None, target=None):
  if fullname == 'scipy' or fullname.startswith('scipy.'): raise RuntimeError('SciPy forbidden')
sys.meta_path.insert(0,Deny())
import scorer
scorer.wave.reader=lambda *a,**k: (_ for _ in ()).throw(RuntimeError('native Reader forbidden'))
from PIL import Image
from pathlib import Path
import tempfile
cell=next(c for c in scorer.runner.admitted_scope(scorer.ROOT,scorer.wave)[0]['rendered'] if 'light' in c)
with tempfile.TemporaryDirectory() as t:
 p=Path(t)/'web.png'; Image.new('RGB',scorer.runner.dimension(scorer.wave,cell),(80,90,100)).save(p)
 result=scorer.project(cell,p)
 assert result['members']
'''
        result = subprocess.run([sys.executable, '-c', code], cwd=HERE, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


class ScoreTests(unittest.TestCase):
    def test_each_repeat_is_binding_and_bar_not_fitted(self):
        target = np.repeat([[100.,100.,100.]],7,axis=0); target[6,1] = 103
        row = s.score_deep([100,100,100], target, [4]*7)
        self.assertEqual(row['barRGB'], [.5,2.,.5])
        self.assertFalse(row['survives'])
        self.assertFalse(row['median']['failed'][1])
        self.assertTrue(row['runs'][6]['failed'][1])

    def test_censor_rail_never_hides_other_channel_failure(self):
        runs = np.repeat([[255.,100.,0.]],7,axis=0)
        row = s.score_deep([249,102,5],runs,[4]*7)
        self.assertEqual(row['median']['status'],['UNMEASURED','measured','censored-bound-satisfied'])
        self.assertEqual(row['median']['boundFailure'],[True,False,False])
        self.assertEqual(row['median']['failed'],[True,True,False])
        summary = s.deep_summary([row])
        self.assertEqual(summary['status'],'UNMEASURED')
        self.assertFalse(summary['constraintsPass'])
        okay = s.deep_summary([s.score_deep([250,100,5],runs,[4]*7)])
        self.assertIsNone(okay['passes']); self.assertTrue(okay['constraintsPass'])

    def test_population_deficiency_excluded_and_counted_not_zero_error(self):
        deficient = s.score_deep([100,100,100], np.repeat([[100,100,100]],7,axis=0), [3]*7)
        self.assertEqual(deficient['status'],'UNMEASURED')
        summary = s.deep_summary([deficient])
        self.assertFalse(summary['passes'])
        self.assertEqual(summary['populationDeficientMembers'],1)
        self.assertEqual(summary['admittedMembers'],0)

    def test_veto_absolute_before_mean_and_all_repeats(self):
        native = np.repeat(np.array([[[100.,100,100],[100,100,100],[100,100,100],[100,100,100]]]),7,axis=0)
        baseline = np.full((4,3),100.)
        candidate = baseline.copy(); candidate[:,0] = [98,102,98,102]
        row = s.veto_bin(candidate, baseline, native)
        self.assertFalse(row['passes'])
        self.assertEqual(row['median']['candidateResidualRGB'][0],2)
        self.assertEqual(len(row['runs']),7)
        native[6,:,1]=104; candidate=baseline.copy(); candidate[:,1]=99
        # Exact one-code worsening is admitted; no floating fuzzy width beyond 1e-10.
        self.assertTrue(s.veto_bin(candidate,baseline,native)['passes'])
        candidate[:,1]=98.9
        self.assertFalse(s.veto_bin(candidate,baseline,native)['passes'])

    def test_veto_population_below_four_is_explicit_exclusion(self):
        row=s.veto_bin(np.zeros((3,3)),np.zeros((3,3)),np.zeros((7,3,3)))
        self.assertEqual(row['status'],'UNMEASURED')
        self.assertIsNone(row['passes'])

    def test_prediction_input_rejects_nonfinite_and_bounds(self):
        for rgb in ([[float('nan'),1,2]], [[256,1,2]]):
            with self.assertRaises(ValueError):s.e3(rgb,[1]*7,[1]*3)


if __name__ == '__main__': unittest.main()
