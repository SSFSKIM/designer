#!/usr/bin/env python3.12
"""W47 G0, Decision Log 8: `reread.py`'s bars on synthetic readings, built through the landing rule's own
reader (`cuts/rule.py` `reads`) so the partition is the rule's, not a copy of it.

- Operator 1's partition: a cell over Apple that does not move beyond its bar fails the toward clause; a
  cell under Apple drawn further under reads `away`; three cells away beyond B fail the count where two
  pass; one away beyond 3 B fails the ceiling; a T cell is partitioned on T1-fine and priced on T1-low.
- Operator 2's fine halving: R exactly at the minimum passes, below it fails, a cell with no excess fails;
  the guards' floor is inclusive.
- The outcome: a rung meeting at both scales separates; one scale only is named, never separating.

    python3.12 -B -m unittest test_reread -v      (from this directory)
"""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reread as RR  # noqa: E402

BAR, CODE = 0.5, 1.0   # B = 1


def cell(n, c, k, stratum="F", bands=None):
    out = dict(scene="x", stratum=stratum, native=n, reference=c, candidate=k, bar=BAR, code=CODE)
    if bands:
        out["bands"] = {b: dict(native=v[0], reference=v[1], candidate=v[2]) for b, v in bands.items()}
    return RR.RULE.reads(out)


class Partition(unittest.TestCase):
    def test_over_apple_must_move_toward(self):
        got = RR.partition({"a": cell(10, 14, 13.6)}, 3, 2)      # moved 0.4 <= bar: unchanged
        self.assertEqual(got["overAppleNotToward"], ["a"])
        self.assertFalse(got["holds"])
        self.assertTrue(RR.partition({"a": cell(10, 14, 12)}, 3, 2)["holds"])

    def test_under_apple_drawn_further_under_is_away(self):
        got = RR.partition({"a": cell(10, 6, 4.5)}, 3, 2)
        self.assertEqual(got["awayBeyondB"], ["a"])
        self.assertTrue(got["holds"])                              # one beyond B, none beyond 3 B

    def test_the_count_and_the_ceiling(self):
        two = {s: cell(10, 6, 4.5) for s in "ab"}
        self.assertTrue(RR.partition(two, 3, 2)["holds"])
        self.assertFalse(RR.partition(dict(two, c=cell(10, 6, 4.5)), 3, 2)["countHolds"])
        got = RR.partition({"a": cell(10, 6, 2.5)}, 3, 2)          # growth 3.5 B
        self.assertEqual(got["awayBeyondCeiling"], ["a"])
        self.assertFalse(got["holds"])

    def test_a_t_cell_reads_fine_and_is_priced_on_low(self):
        r = cell(10, 14, 12, stratum="T", bands={"fine": (1, 3, 2.9), "low": (5, 5, 9)})
        got = RR.partition({"t": r}, 3, 2)
        self.assertEqual(got["overAppleNotToward"], ["t"])         # fine moved 0.1: unchanged
        self.assertEqual(got["awayBeyondCeiling"], ["t"])          # low grew 4 B


class FineAndGuards(unittest.TestCase):
    def test_the_halving(self):
        self.assertTrue(RR.fine_halving({"a": dict(native=1, reference=3, rung=2)}, 0.5)["holds"])
        self.assertFalse(RR.fine_halving({"a": dict(native=1, reference=3, rung=2.01)}, 0.5)["holds"])
        got = RR.fine_halving({"a": dict(native=3, reference=3, rung=2)}, 0.5)
        self.assertIsNone(got["cells"]["a"]["R"])
        self.assertFalse(got["holds"])

    def test_the_guard_floor_is_inclusive(self):
        self.assertTrue(RR.guards_hold({"g": dict(web=9, control=10, B=1)}, 1)["holds"])
        self.assertFalse(RR.guards_hold({"g": dict(web=8.99, control=10, B=1)}, 1)["holds"])


class Outcome(unittest.TestCase):
    def test_both_scales_or_named(self):
        got = RR.outcome({"r1": {1: True, 2: True}, "r2": {1: True, 2: False}, "r3": {1: False, 2: False}})
        self.assertEqual(got, dict(meetsBoth=["r1"], meetsOneScaleOnly=["r2"]))


if __name__ == "__main__":
    unittest.main()
