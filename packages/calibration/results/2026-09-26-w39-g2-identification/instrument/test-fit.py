"""Fit recovery must use a real optimizer, not the generating coefficients."""
import unittest
import numpy as np
import fitting

class FitTests(unittest.TestCase):
    def test_minimax_is_not_relabelled_least_squares(self):
        # 0, 0, 6: LS constant is 2, minimax is 3, worst errors 4 versus 3.
        fit=fitting.fit(lambda q:np.full((3,1),q[0]),np.array([[0.],[0.],[6.]]),[0.])
        self.assertAlmostEqual(fit['leastSquares']['coefficients'][0],2,places=5)
        self.assertAlmostEqual(fit['minimax']['coefficients'][0],3,places=5)
        self.assertAlmostEqual(fit['minimax']['maximum'],3,places=5)
    def test_bounds_and_rank_are_reported(self):
        fit=fitting.fit(lambda q:np.array([[q[0]+q[1]]]),np.array([[3.]]),[.2,.2],bounds=[(0,1)]*2)
        self.assertAlmostEqual(fit['leastSquares']['maximum'],1,places=5)
        self.assertEqual(fit['leastSquares']['rank'],1)
        self.assertEqual(len(fit['leastSquares']['singularValues']),1)

if __name__=='__main__':unittest.main()
