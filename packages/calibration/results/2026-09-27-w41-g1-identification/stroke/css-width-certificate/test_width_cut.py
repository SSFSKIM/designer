"""Synthetic tests of complete strict-support partition and necessary intervals."""
from fractions import Fraction as F
import unittest
import width_cut as c


def geometry():
    return {'1x-s0':[F(2*i+1,32) for i in range(16)],
            '2x-s0':[F(2*i+1,64) for i in range(16)],
            '2x-s1':[F(2*i+33,64) for i in range(16)]}


def row(key, lo, hi):
    return dict(geometry=key, lower=None if lo is None else str(lo),
                upper=None if hi is None else str(hi))


class WidthTests(unittest.TestCase):
    def test_complete_partition_and_strict_boundaries(self):
        g = geometry()
        states = c.states(g)
        self.assertEqual(len(states), 99)
        self.assertEqual(sum(s['kind']=='point' for s in states), 50)
        points = [F(s['representative']) for s in states if s['kind']=='point']
        self.assertEqual(points, sorted({F(0),F(2),*(x for v in g.values() for x in v)}))
        for i,s in enumerate(states):
            if s['kind']=='open':
                a,b=F(s['lower']),F(s['upper'])
                self.assertEqual(a,F(states[i-1]['representative']))
                self.assertEqual(b,F(states[i+1]['representative']))
                for ts in g.values():
                    for ratio in (F(1,100),F(1,3),F(1,2),F(99,100)):
                        self.assertEqual(c.fraction(ts,a+(b-a)*ratio),c.fraction(ts,s['representative']))
        self.assertEqual(c.fraction(g['1x-s0'],F(1,32)),0)
        self.assertEqual(c.fraction(g['1x-s0'],F(1,32)+F(1,10000)),F(1,16))

    def test_zero_and_max_width_and_duplicate_samples(self):
        g=geometry()
        for ts in g.values():
            self.assertEqual(c.fraction(ts,0),0)
            self.assertEqual(c.fraction(ts,2),1)
            self.assertEqual(c.fraction(ts*16,F(13,32)),c.fraction(ts,F(13,32)))
        self.assertEqual(c.fraction([0,-1,3,F(1,2)],1),F(1,4))

    def test_subpixel_alias_must_remain_feasible(self):
        rows=[row('1x-s0',-21,-19),row('2x-s0',-21,-19),row('2x-s1',-1,1)]
        result=c.solve(geometry(),{'input128-channel0':rows})
        self.assertEqual(result['status'],'NOT_REJECTED_BY_RELAXATION')
        match=next(s for s in result['states'] if s['kind']=='open' and s['lower']=='1/32')
        self.assertTrue(match['feasible'])
        self.assertEqual(match['fractions'],{'1x-s0':'1/16','2x-s0':'1/16','2x-s1':'0'})
        self.assertEqual(match['groups']['input128-channel0']['witnessZ'],'-304')

    def test_disjoint_intervals_exact_witness(self):
        out=c.intersect([row('a',-21,-19),row('b',-1,1)],{'a':'1','b':'1'})
        self.assertFalse(out['feasible'])
        self.assertEqual(out['separation'],'18')

    def test_zero_fraction_and_touching_intervals(self):
        self.assertFalse(c.intersect([row('a',-21,-19)],{'a':'0'})['feasible'])
        self.assertTrue(c.intersect([row('a',-1,1)],{'a':'0'})['feasible'])
        self.assertTrue(c.intersect([row('a',0,1),row('b',1,2)],{'a':'1','b':'1'})['feasible'])

    def test_one_sided_rails(self):
        self.assertFalse(c.intersect([row('a',None,-20)],{'a':'0'})['feasible'])
        self.assertTrue(c.intersect([row('a',-5,None)],{'a':'0'})['feasible'])
        self.assertFalse(c.intersect([row('a',None,-20),row('b',-5,None)],{'a':'1','b':'1'})['feasible'])

    def test_every_width_state_can_be_rejected(self):
        groups={'x':[row('1x-s0',-2,-1),row('1x-s0',1,2)]}
        result=c.solve(geometry(),groups)
        self.assertEqual(result['status'],'CERTIFIED_INFEASIBLE_RELAXATION')
        self.assertEqual(result['feasibleStateIndices'],[])

    def test_width_shared_across_independent_z_groups(self):
        # The same width must satisfy both; each group is allowed its own z.
        g={'a':[F(1,4)],'b':[F(3,4)]}
        early=[row('a',1,2),row('b',0,0)]
        late=[row('a',0,0),row('b',1,2)]
        self.assertEqual(c.solve(g,{'early':early})['status'],'NOT_REJECTED_BY_RELAXATION')
        self.assertEqual(c.solve(g,{'early':early,'late':late})['status'],'CERTIFIED_INFEASIBLE_RELAXATION')


if __name__=='__main__':
    unittest.main()
