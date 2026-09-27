"""Off-seed recovery: finite differences alone cannot cross coverage plateaus."""
import json
import time
import unittest
import numpy as np
import instrument as m
import stroke_fit as f

class WidthTests(unittest.TestCase):
    def test_two_shell_off_seed_recovery(self):
        # Four top-straight pixels per shell. Unit angular coverage, 128 backdrop,
        # 64 stroke: shell0 is64, shell1 is128-64*(device width-1).
        for scale,css_width,width,second in [(1,False,1.75,80.),(2,True,.84375,84.)]:
            with self.subTest(scale=scale,cssWidth=css_width,width=width):
                sh=m.readers.Shape('capsule-circular',(120.,44.),(20.,20.))
                xy=np.array([[x*scale,20*scale-1-shell] for shell in range(2)
                             for x in (78,79,80,81)])
                g=m.samples(sh,xy,scale)
                b=np.full((*g['d'].shape,3),128.)
                o=dict(endpoint=1,g=g,backdrop=b,shadow=b,binids=np.repeat([0,1],4),
                       target=np.repeat([[64.]*3,[second]*3],4,axis=0))
                planted=f.domain('M0')[2];planted[0]=width;planted[2]=0
                planted[9:11]=[0,64]
                np.testing.assert_array_equal(f.predict(planted,o,'M0',css_width),o['target'])
                before=time.perf_counter();result=f.fit_local([o],'M0',css_width)
                summary=dict(scale=scale,cssWidth=css_width,plantedWidth=width,
                             seconds=time.perf_counter()-before)
                for key in ('leastSquares','minimax'):
                    fit=result[key]
                    self.assertIsNotNone(fit)
                    summary[key]={k:fit[k] for k in ('maximumCodes','optimizerSuccess','converged','zeroFloorBracketCodes')}
                    summary[key]['width']=fit['coefficients'][0]
                print(json.dumps(summary,allow_nan=False),flush=True)
                for key in ('leastSquares','minimax'):
                    self.assertLess(result[key]['maximumCodes'],1e-6)
                    self.assertEqual(result[key]['railDeficitCodes'],0)
                self.assertTrue(any(r['leastSquares']['coefficients'][0]!=r['initial'][0]
                                    for r in result['starts']))

    def test_off_seed_fit_retains_censored_channel_as_hard_rail(self):
        sh=m.readers.Shape('capsule-circular',(120.,44.),(20.,20.))
        xy=np.array([[x,19-shell] for shell in range(2) for x in (78,79,80,81)])
        g=m.samples(sh,xy,1)
        b=np.broadcast_to([255.,128.,128.],(*g['d'].shape,3)).copy()
        o=dict(endpoint=1,g=g,backdrop=b,shadow=b,binids=np.repeat([0,1],4),
               target=np.repeat([[255.,64.,64.],[255.,80.,80.]],4,axis=0))
        result=f.fit_local([o],'M0')
        for key in ('leastSquares','minimax'):
            row=result[key];self.assertIsNotNone(row)
            pred=f.predict(row['coefficients'],o,'M0')
            self.assertTrue(np.all(pred[:,0]>=250))
            self.assertLess(np.max(abs(pred[:,1:]-o['target'][:,1:])),1e-6)
            self.assertEqual(row['railDeficitCodes'],0)

    def test_width_sweep_refines_beyond_grid_without_moving_other_coefficients(self):
        q=np.array([.2,7.,-3.])
        # A staircase with a narrow bottom not containing any coarse grid point.
        def objective(v):return np.floor(abs(v[0]-1.413)/.002)
        result,trace=f.search_width(q,objective,lambda v:True)
        self.assertEqual(objective(result),0)
        np.testing.assert_array_equal(result[1:],q[1:])
        self.assertTrue(0<=result[0]<=2)
        self.assertLessEqual(trace['evaluations'],102)

    def test_width_search_keeps_hard_rails_and_boundaries(self):
        for optimum in (0.,2.):
            q=np.array([1.,9.])
            result,_=f.search_width(q,lambda v:(v[0]-optimum)**2,lambda v:True)
            self.assertEqual(result[0],optimum)
        result,_=f.search_width(np.array([.5]),lambda v:-v[0],lambda v:v[0]<=1.25)
        self.assertEqual(result[0],1.25)

if __name__=='__main__':unittest.main()
