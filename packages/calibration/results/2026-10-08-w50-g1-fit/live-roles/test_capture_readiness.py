"""The capture role's DL5h helper seams after a not-ready native read (second pre-seal review P3).

The bed, archive, real native role and LIVE checkpoint are live-roles/test_native.py's fixture,
reused unchanged; its own tests are not rerun here. The helper is the root-bound DL5h helper as
the W50 transport loads it, through the capture role's checkpointed loader or the sealed one.
"""
import importlib.util
from pathlib import Path
import sys
import unittest

import numpy as np

HERE = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); sys.modules[name] = module
    spec.loader.exec_module(module); return module


T = load('w50_capture_readiness_native_fixture', HERE/'test_native.py')


class CaptureReadiness(T.NativeRole):
    def pair(self, helper, cell, row, first, second):
        """newbed_pair's evaluation of an already-read blind cell: its original analytical masks,
        native_statistics on both images and the 0.1-bar comparison."""
        S = helper.S
        scene = next(s for s in self.scenes['scenes'] if s['id'] == row['scene'])
        export, dependency = cell['_export'], cell['_dependency']
        background = S.M.R.read_verified_frame(export, dependency, self.scenes['canvas'], cell['scale'])
        masks = S.M.R.S.analytical_masks(self.scenes['components'][scene['component']], self.scenes['canvas'],
            cell['scale'], first.shape[:2], background=background,
            impulse=self.scenes['backgrounds'][scene['background']]['kind'] == 'impulse')
        if cell['family'] == 'uniform': del masks['deep8_far24']
        native = {k: v for k, v in cell.items() if not k.startswith('_')}
        return helper.C.compare_statistics(*S.native_statistics(first, second, native, masks, renderer='webgpu',
                                                                 provenance={}))

    def test_an_unreadable_stop_needs_byte_identity_not_the_sealed_evaluators_refusal(self):
        """A required T1 the read could not measure (no native silhouette): the sealed evaluator
        refuses the not-ready read outright; through the capture role the stopped statistic is
        not computed and has no finite bar, so a non-identical pair is DL5h (ii)'s
        IdentityRequired, while a byte-identical pair never reaches the evaluator."""
        sealed, wired = self.capture_helper(False), self.capture_helper(True)
        row = self.blind_row('cell-impulse-sparse-s224__rest', 'T1-full-silhouette')
        first = np.full((384, 512, 3), 20, np.uint8)
        second = first.copy(); second[0, 0] = 21
        with self.checkpointed_capture(stops=True) as (context, payload):
            self.assertIn((row['profile']+'/'+row['scene'], 'T1-full-silhouette', 'UNMEASURED_UNAUTHORISED_POPULATION'),
                          [(s['cell'], s['statistic'], s['reason']) for s in payload['stops']])
            cell, dependency, export, _ = wired.S.blind_cell(context, self.runs[0], row, self.scenes)
            cell = dict(cell, _export=export, _dependency=dependency)
            with self.assertRaisesRegex(ValueError, 'empty required native support'):
                self.pair(sealed, cell, row, first, second)
            with self.assertRaises(wired.C.IdentityRequired) as refused:
                self.pair(wired, cell, row, first, second)
            self.assertIn('T1-full-silhouette', str(refused.exception))
            measured = {k for k, v in refused.exception.differences.items() if 'difference' in v}
            self.assertEqual(measured, set(cell['statistics'])-{'T1-full-silhouette'})

    def test_a_cell_the_checkpoint_does_not_stop_evaluates_as_the_sealed_one(self):
        sealed, wired = self.capture_helper(False), self.capture_helper(True)
        row = self.blind_row()
        first = np.full((384, 512, 3), 20, np.uint8); second = first.copy(); second[0, 0] = 21
        with self.checkpointed_capture() as (context, payload):
            self.assertTrue(payload['ready'])
            cell, dependency, export, _ = wired.S.blind_cell(context, self.runs[0], row, self.scenes)
            cell = dict(cell, _export=export, _dependency=dependency)
            self.assertEqual(self.pair(wired, cell, row, first, second), self.pair(sealed, cell, row, first, second))


for name in dir(T.NativeRole):
    if name.startswith('test'): setattr(CaptureReadiness, name, None)


if __name__ == '__main__':
    unittest.main()
