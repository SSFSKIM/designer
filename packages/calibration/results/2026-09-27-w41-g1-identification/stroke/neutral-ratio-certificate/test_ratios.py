"""Exact ratio-cut tests; no native evidence or optimization is needed."""
from fractions import Fraction as F
import unittest
import ratios


class RatioTests(unittest.TestCase):
    def test_negative_departures_reverse_both_bounds(self):
        # xA=-8..-6, xB=-4..-2 implies r=xA/xB in [3/2,4].
        result=ratios.ratio_interval(['-8','-6'],['-4','-2'])
        self.assertEqual(result['interval'],['3/2','4'])
        self.assertEqual(result['signs'],['negative','negative'])

    def test_positive_departures_and_zero_numerator(self):
        self.assertEqual(ratios.ratio_interval(['6','8'],['2','4'])['interval'],['3/2','4'])
        self.assertEqual(ratios.ratio_interval(['-1','1'],['2','4'])['interval'],['0','1/2'])
        self.assertEqual(ratios.ratio_interval(['0','0'],['2','4'])['interval'],['0','0'])

    def test_opposite_strict_signs_are_impossible(self):
        result=ratios.ratio_interval(['1','2'],['-4','-2'])
        self.assertEqual(result['status'],'EMPTY_SIGN_CONSTRAINT')
        self.assertIsNone(result['interval'])

    def test_denominator_zero_is_not_divided_away(self):
        for denominator in [['0','0'],['-1','1'],['0','3'],['-3','0']]:
            result=ratios.ratio_interval(['2','3'],denominator)
            self.assertEqual(result['status'],'OMITTED_DENOMINATOR_INCLUDES_ZERO')
            self.assertIsNone(result['interval'])

    def test_disjoint_closed_intervals_certify_but_touching_do_not(self):
        entries=[dict(level=40,numerator=['-8','-6'],denominator=['-4','-2']),
                 dict(level=255,numerator=['-20','-18'],denominator=['-3','-2'])]
        result=ratios.intersect_ratios(entries)
        self.assertEqual(result['status'],'EXACT_EMPTY_INTERSECTION')
        self.assertEqual(result['lower'],'6')
        self.assertEqual(result['upper'],'4')
        touching=[entries[0],dict(level=255,numerator=['-12','-8'],denominator=['-2','-1'])]
        result=ratios.intersect_ratios(touching)
        self.assertEqual(result['status'],'NOT_DETERMINING')
        self.assertEqual(result['lower'],result['upper'])

    def test_reversed_orientation_can_retain_a_zero_departure_constraint(self):
        entries=[dict(level=40,numerator=['-10','-8'],denominator=['-1','1']),
                 dict(level=255,numerator=['-10','-8'],denominator=['-10','-8'])]
        self.assertEqual(ratios.intersect_ratios(entries)['status'],'NOT_DETERMINING')
        reverse=[dict(level=r['level'],numerator=r['denominator'],denominator=r['numerator'])
                 for r in entries]
        self.assertEqual(ratios.intersect_ratios(reverse)['status'],'EXACT_EMPTY_INTERSECTION')

    def test_zero_denominator_only_is_not_a_rejection(self):
        result=ratios.intersect_ratios([dict(level=40,numerator=['1','2'],denominator=['-1','1'])])
        self.assertEqual(result['status'],'NOT_DETERMINING')

    def test_any_physical_nonnegative_coverage_ratio_is_contained(self):
        # Vary the arbitrary neutral material departure across zero and sign;
        # zero numerator coverage is legal, while denominator coverage is held.
        for ca in [F(0),F(1,4),F(1)]:
            cb=F(1,2)
            entries=[]
            for level,d in [(40,F(-20)),(72,F(0)),(104,F(20))]:
                entries.append(dict(level=level,
                    numerator=[str(ca*d-1),str(ca*d+1)],
                    denominator=[str(cb*d-1),str(cb*d+1)]))
            result=ratios.intersect_ratios(entries)
            self.assertEqual(result['status'],'NOT_DETERMINING')
            self.assertLessEqual(F(result['lower']),ca/cb)
            self.assertGreaterEqual(F(result['upper']),ca/cb)


if __name__=='__main__':unittest.main()
