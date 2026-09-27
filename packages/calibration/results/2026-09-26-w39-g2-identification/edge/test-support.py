"""A tail outside every basis support must stay fixed under arbitrary coefficients."""
import sys
from pathlib import Path
import unittest
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'instrument'))
import edge_law

class SupportTests(unittest.TestCase):
    def test_every_grid_and_quadrature_is_zero_for_entire_deep_pixels(self):
        # Positive margins beyond the half-pixel diagonal prove the entire
        # pixel is deeper than12 even for the diagonal normal, not just its centre.
        ny=np.array([-1,-.7071067811865476,0,.7071067811865476,1])
        for scale in [1,2]:
          d=np.full(len(ny),-12-np.sqrt(.5)/scale-.01)
          for width in [.8,1,1.2,1.4,1.6,1.8,2,2.2,2.4]:
            for exponent in [1,2,3,4,6]:
              for order in [8,16]:
                radial=edge_law.radial(d,ny,np.full(len(ny),scale),width,exponent,order)
                np.testing.assert_array_equal(radial,np.zeros((len(ny),11)))
                b=np.tile([.4,.5,.6],(len(ny),1))
                np.testing.assert_array_equal(edge_law.forward(b,radial,np.tile([-4096,4096],22)),b)

if __name__=='__main__':unittest.main()
