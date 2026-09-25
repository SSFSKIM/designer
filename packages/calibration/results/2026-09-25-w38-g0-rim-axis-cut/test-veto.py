import unittest
from model import np
from score import constraints
class VetoBeforeAggregate(unittest.TestCase):
    def domain(self):
        return dict(oldError=np.array([[10.,10,10],[2,2,2],[0,0,0]]),labels=np.array(['greys-arc']*3),horizontal=np.array([False,False,True]),censored=np.zeros((3,3),bool))
    def test_improving_aggregate_cannot_hide_one_worse_channel(self):
        d=self.domain();result=constraints(d,np.array([[1.,1,1],[3.2,2,2],[0,0,0]]))
        self.assertLess(result['strata'][0]['maximum'],10)
        self.assertLess(result['strata'][0]['mean'],d['oldError'].mean())
        self.assertFalse(result['feasible']);self.assertAlmostEqual(result['maximumConstraintExcess'],.2)
    def test_horizontal_stop_independent_of_veto(self):
        d=self.domain();d['oldError'][2]=[10,10,10]
        result=constraints(d,np.array([[1.,1,1],[2,2,2],[3,3,3]]))
        self.assertLessEqual(result['maximumWorsening'],1)
        self.assertFalse(result['feasible']);self.assertEqual(result['maximumConstraintExcess'],1)
    def test_boundary_tolerance_and_censor_objective_are_separate(self):
        d=self.domain();d['censored'][0,0]=True
        a=np.array([[11.,1,1],[2,2,2],[0,0,0]])
        # Censoring excludes objective, NEVER removes a forward veto/stratum.
        result=constraints(d,a);self.assertEqual(result['minimax'],2)
        self.assertFalse(result['feasible']) # stratum maximum worsens1 >.5
        a[0,0]=10.5;self.assertTrue(constraints(d,a)['feasible'])
if __name__=='__main__':unittest.main()
