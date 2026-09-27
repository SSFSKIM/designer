"""A censored channel cannot silently reduce its cell's least-squares mass."""
import unittest
import numpy as np
import stroke_fit as f
class MassTests(unittest.TestCase):
    def test_equal_cell_mass_with_partial_censoring(self):
        a=dict(target=np.array([[255,100,100],[255,100,100]],float),binids=np.array([0,0]))
        b=dict(target=np.array([[100,100,100]],float),binids=np.array([0]))
        target,mass,groups=f.objective_layout([a,b])
        # Unit error on the first cell, two-code error on the second: (1+4)/2.
        delta=np.array([0,1,1,0,1,1,2,2,2],float)
        self.assertAlmostEqual(float(np.sum(mass*delta*delta)),2.5)
        self.assertAlmostEqual(float(mass[:6].sum()),.5)
        self.assertAlmostEqual(float(mass[6:].sum()),.5)
        self.assertEqual(len(groups),5)
if __name__=='__main__':unittest.main()
