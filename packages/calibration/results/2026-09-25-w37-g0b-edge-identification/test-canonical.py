"""Absent sides and deficient shells must not disappear from the E1 population."""
import unittest
import numpy as np
from common import oldcanonical
try:
    import canonical
except ModuleNotFoundError:
    canonical=oldcanonical

class Canonical(unittest.TestCase):
    def test_capsule_absent_sides_are_explicit(self):
        _,bins=canonical.geometry((100,180),{'size':[120,44],'radius':22},1)
        self.assertEqual(len(bins),24)
        by_side={s:[(i,m) for i,m in bins if i['side']==s] for s in ['top','bottom','left','right']}
        for side in ['left','right']:
            self.assertEqual(len(by_side[side]),6)
            for info,mask in by_side[side]:
                self.assertEqual(info['status'],'UNMEASURED')
                self.assertFalse(mask.any())
        self.assertEqual(canonical.cell_status([i for i,m in bins]),'UNMEASURED')

    def test_all_shells_and_small_populations_remain(self):
        _,bins=canonical.geometry((50,50),{'size':[10,10],'radius':2},2)
        self.assertEqual(len(bins),48)
        self.assertTrue(any(i['pixels']==0 for i,m in bins))
        self.assertEqual(canonical.cell_status([i for i,m in bins]),'UNMEASURED')
        self.assertEqual(canonical.cell_status([{'status':'measured'}]),'measured')
        self.assertEqual(canonical.cell_status([{'status':'measured'},{'status':'UNMEASURED'}]),'UNMEASURED')

if __name__=='__main__':unittest.main()
