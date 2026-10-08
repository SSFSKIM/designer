"""Synthetic cut rehearsals; no held or native pixels."""
import importlib.util
from pathlib import Path
import unittest
import numpy as np

HERE=Path(__file__).resolve().parent

class CutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec=importlib.util.spec_from_file_location('w50_cuts_test', HERE/'cuts.py')
        cls.c=importlib.util.module_from_spec(spec); spec.loader.exec_module(cls.c)

    def test_uniforms_recover_every_channel_and_scale_over_both_declared_cuts(self):
        for scale in (1,2):
            rgb=np.broadcast_to(np.array([20,21,22], dtype=np.uint8), (384*scale,512*scale,3))
            row=self.c.read(rgb, {'kind':'rrect','size':[392,224],'radius':47.6}, scale)
            for name in ('deep8','center8'):
                self.assertEqual(row[name]['medianCodes'], [20,21,22])
                self.assertGreater(row[name]['pixels'],0)
            self.assertEqual(row['center8']['pixels'], 64*scale*scale)

    def test_noise_exceeding_one_code_stops_instead_of_growing_budget(self):
        row=lambda x: {'deep8':{'medianCodes':[x,x,x]}, 'center8':{'medianCodes':[x,x,x]}}
        self.assertTrue(self.c.repeat_verdict([row(20),row(21),row(20)])['passes'])
        self.assertFalse(self.c.repeat_verdict([row(20),row(22),row(20)])['passes'])
        with self.assertRaises(ValueError):
            self.c.repeat_verdict([row(20),row(20)])

if __name__=='__main__':unittest.main()
