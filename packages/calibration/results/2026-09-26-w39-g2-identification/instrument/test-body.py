"""Synthetic-only checks; a wrong colour law must not pass its own referee."""
import unittest
import numpy as np
import body

class BodyTests(unittest.TestCase):
    def test_neutral_continuation_is_not_endpoint_clamping(self):
        knots=np.array([.2,.24,.28,.32,.36,.42,.475])
        np.testing.assert_allclose(body.curve(np.array([32,40,160])/255,body.KNOTS,knots),[.18,.2,.5],atol=1e-12)

    def test_matrix_preserves_neutral_and_couples_channels(self):
        q=np.array([1.2,-.2,.1,.8,-.2,.1])
        x=np.array([[88,88,88],[90,70,100],[90,100,70]])/255
        f=np.array([.2,.25,.3,.35,.4,.5,.6])
        y=body.h3(x,f,q)
        np.testing.assert_allclose(y[0],[.35]*3,atol=1e-12)
        self.assertGreater(abs(y[1,0]-y[2,0])*255,1)

    def test_retention_uses_composited_chroma_and_holds_luma(self):
        b=np.array([[.12,.04,.08]])
        c=.4*b+.6*.3
        got=body.retain(c,b,.35)
        np.testing.assert_allclose(got@body.W,c@body.W,atol=1e-14)
        qb=.4*(b@body.W)/(c@body.W)
        chroma=got/(got@body.W)[:,None]-1
        target=b/(b@body.W)[:,None]-1
        np.testing.assert_allclose(chroma,(qb+(1-qb)*.35)[:,None]*target,atol=1e-13)
        np.testing.assert_array_equal(body.retain(c,b,0),c)
        np.testing.assert_array_equal(body.retain(c,np.zeros_like(b),1),c)

    def test_oklab_inverse_and_neutral(self):
        x=np.array([[.05,.11,.18],[.4,.4,.4]])
        np.testing.assert_allclose(body.unlab(body.lab(x)),x,atol=1e-14)
        y=body.h3prime(np.array([[88,88,88]])/255,np.array([.2,.25,.3,.35,.4,.5,.6]),np.eye(2).ravel())
        np.testing.assert_allclose(y,[[.35]*3],atol=2e-7)

if __name__=='__main__':unittest.main()
