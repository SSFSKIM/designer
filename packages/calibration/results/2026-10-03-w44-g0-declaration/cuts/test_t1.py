#!/usr/bin/env python3.12
"""W44 G0 (d): T1's change-state examples, pinned before part 1 (charter Design "T1", output 2).

The four examples the charter fixes the precedence with, verbatim, then the cases the
precedence implies around them. Each example gives B (or the bar) and leaves the other free, so
each is posed at a `code` and `bar` whose `max(code, 2 bar)` is the stated B.

    python3.12 -B -m unittest test_t1 -v      (from this directory)
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import t1  # noqa: E402


def at(B, bar=None):
    """(bar, code) with max(code, 2 bar) = B: the bar at half of B unless the example names it."""
    bar = B / 2 if bar is None else bar
    return bar, B


class PinnedExamples(unittest.TestCase):
    """The charter's four, verbatim (Design "T1", output 2)."""

    def test_1_overshoot_at_B_0_01(self):
        bar, code = at(0.01)
        got = t1.classify(n=0.10, c=0.14, k=0.075, bar=bar, code=code)
        self.assertEqual(got["fidelity"], "miss")
        self.assertEqual(got["change"], "overshoot")

    def test_2_toward_at_B_0_03(self):
        bar, code = at(0.03, bar=0.005)
        got = t1.classify(n=0.10, c=0.14, k=0.075, bar=bar, code=code)
        self.assertEqual(got["B"], 0.03)
        self.assertEqual(got["fidelity"], "within")
        self.assertEqual(got["change"], "toward")

    def test_3_overshoot_equal_error_crossing_that_misses(self):
        bar, code = at(0.01)
        got = t1.classify(n=0.10, c=0.12, k=0.08, bar=bar, code=code)
        self.assertAlmostEqual(got["growth"], 0.0, places=15)
        self.assertEqual(got["fidelity"], "miss")
        self.assertEqual(got["change"], "overshoot")

    def test_4_unchanged_within_the_bar(self):
        got = t1.classify(n=0.10, c=0.14, k=0.139, bar=0.002, code=0.004)
        self.assertEqual(got["change"], "unchanged")
        self.assertEqual(got["fidelity"], "miss")   # an unchanged miss, never a failure


class Precedence(unittest.TestCase):
    """What the precedence implies around the four, so a reordering of the branches fails here."""

    def test_away_on_one_side(self):
        got = t1.classify(n=0.10, c=0.12, k=0.13, bar=0.002, code=0.004)
        self.assertEqual(got["change"], "away")
        self.assertGreater(got["growth"], 0)

    def test_toward_on_one_side(self):
        self.assertEqual(t1.classify(n=0.10, c=0.14, k=0.12, bar=0.002, code=0.004)["change"], "toward")

    def test_equal_error_crossing_that_lands_within_is_toward(self):
        got = t1.classify(n=0.10, c=0.103, k=0.097, bar=0.002, code=0.004)
        self.assertEqual(got["fidelity"], "within")
        self.assertEqual(got["change"], "toward")

    def test_unchanged_precedes_overshoot(self):
        # crossed and a miss, but displaced by no more than the bar
        got = t1.classify(n=0.10, c=0.1004, k=0.0996, bar=0.001, code=0.0001)
        self.assertTrue(got["crossed"])
        self.assertEqual(got["change"], "unchanged")

    def test_ratio_clause_guarded_at_one_code(self):
        # n below one code: 10 % of n is no licence; only B decides
        got = t1.classify(n=0.002, c=0.002, k=0.0021, bar=0.0001, code=0.003)
        self.assertEqual(got["fidelity"], "within")          # by B = 0.003
        got = t1.classify(n=0.002, c=0.002, k=0.0061, bar=0.0001, code=0.003)
        self.assertEqual(got["fidelity"], "miss")
        # n at or above one code: the 10 % clause admits what B alone would not
        got = t1.classify(n=0.20, c=0.20, k=0.215, bar=0.001, code=0.004)
        self.assertEqual(got["fidelity"], "within")

    def test_states_partition(self):
        for n, c, k in ((0.1, 0.14, 0.075), (0.1, 0.12, 0.13), (0.1, 0.14, 0.12), (0.1, 0.1, 0.1)):
            got = t1.classify(n, c, k, 0.002, 0.004)
            self.assertIn(got["change"], t1.CHANGE)
            self.assertIn(got["fidelity"], t1.FIDELITY)


if __name__ == "__main__":
    unittest.main()
