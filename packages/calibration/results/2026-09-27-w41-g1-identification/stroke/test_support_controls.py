"""A bin is outside every rival only when all samples clear CSS-scaled reach."""
import unittest
import numpy as np
import support_controls as s


class SupportTests(unittest.TestCase):
    def test_css_width_and_every_subpixel_not_centres_control_admission(self):
        g = dict(scale=2, d=np.array([[4., 4.1], [3.999, 5.]]))
        self.assertTrue(s.outside_every_rival(g, np.array([True, False])))
        self.assertFalse(s.outside_every_rival(g, np.array([True, True])))
        self.assertFalse(s.outside_every_rival(g, np.array([False, False])))
        g['scale'] = 1
        self.assertTrue(s.outside_every_rival(g, np.array([True, True])))


if __name__ == '__main__':
    unittest.main()
