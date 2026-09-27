import unittest
from fractions import Fraction as F
import numpy as np
import bounded_cut
import run
from test_width_cut import geometry,row


class BoundedTests(unittest.TestCase):
    def test_sealed_range_removes_unbounded_alias(self):
        rows=[dict(**r,b=255) for r in [row('1x-s0',-56,-54),row('2x-s0',-56,-54),row('2x-s1',-5,None)]]
        result=bounded_cut.solve(geometry(),{'input255-channel0':rows})
        self.assertEqual(result['status'],'CERTIFIED_INFEASIBLE_RELAXATION')
        self.assertEqual(result['independentlyRejectingInputLevels'],['255'])
        self.assertEqual(result['stateCount'],99)

    def test_zero_departure_includes_zero_width_and_angular_zero(self):
        rows=[dict(**r,b=128) for r in [row('1x-s0',-1,1),row('2x-s0',-1,1),row('2x-s1',-1,1)]]
        result=bounded_cut.solve(geometry(),{'x':rows})
        self.assertTrue(all(s['feasible'] for s in result['states']))
        self.assertEqual(result['bounds']['x']['lower'],'-128')
        self.assertEqual(result['bounds']['x']['upper'],'127')

    def test_mixed_censor_retains_exact_subset_jensen_and_hard_rails(self):
        pixels=np.tile(np.array([[3,20,255],[20,20,255],[22,20,255],[24,20,255]]),(7,1,1))
        rows,bars=run.allowances(pixels,32,'1x-s0')
        ch0=[r for r in rows if r['state']==1 and r['channel']==0]
        self.assertEqual(len(ch0),2)
        self.assertEqual(ch0[0]['kind'],'Jensen-uncensored-mean')
        self.assertEqual(ch0[0]['uncensoredPixels'],3)
        self.assertEqual((ch0[0]['lower'],ch0[0]['upper']),('-11','-9'))
        self.assertEqual(ch0[1]['upper'],'-27')
        ch2=[r for r in rows if r['state']==1 and r['channel']==2]
        self.assertEqual(len(ch2),1)
        self.assertEqual(ch2[0]['lower'],'218')
        self.assertIsNone(ch2[0]['upper'])
        self.assertEqual(bars,[F(1,2)]*3)

    def test_all_repeat_bar_uses_whole_bin(self):
        p=np.full((7,4,3),20);p[-1]=26
        rows,bars=run.allowances(p,32,'1x-s0')
        self.assertEqual(bars,[F(7,2)]*3)
        self.assertEqual(rows[0]['bound'],'7/2')
        self.assertEqual(len(rows),24)

    def test_product_bounds_hold_for_parameter_endpoints(self):
        for b in (0,40,128,255):
            for alpha in (F(0),F(1,16),F(1,2),F(1)):
                for s in (F(0),F(255,2),F(255)):
                    self.assertLessEqual(-b,alpha*(s-b))
                    self.assertLessEqual(alpha*(s-b),255-b)


if __name__=='__main__':unittest.main()
