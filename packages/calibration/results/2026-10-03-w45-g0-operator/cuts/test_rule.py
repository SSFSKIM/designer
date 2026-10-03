#!/usr/bin/env python3.12
"""W45 G0 (c): the landing rule's synthetic boundary cases, pinned before part 1 is hashed (charter
clause 3; Decision Log 3; X55).

The six cases clause 3 lists, exactly as it lists them, on one synthetic 2x light WebGPU map whose
c05 F stratum misses (so F has something to halve), then the rule's own boundaries:

  (a) a map halving F with three cells at 2B passes;
  (b) four cells at 2B fails;
  (c) one cell at 3.1B fails;
  (d) a stratum aggregate worse by more than its tolerance fails;
  (e) every cell `unchanged` is neither;
  (f) a T stratum of two cells is reported, not gated.

A case the implementation decides against its declared text stops the hash (clause 3's stop).

    cd packages/calibration/results/2026-10-03-w45-g0-operator/cuts
    python3.12 -B -m unittest test_rule -v
"""
import math
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import bed  # noqa: E402,F401  (W45's port first, so W44 G1's t1 binds to it)
sys.path.insert(1, str(bed.W44_G1 / "cuts"))
import rule  # noqa: E402

PROFILE = rule.SCOPE_PROFILE
CODE, BAR = 0.004, 0.002          # B = max(code, 2 bar) = 0.004
B = max(CODE, 2 * BAR)


def cell(scene, stratum, pose, n, c, k=None, span="mid", partition="gate", bands=None):
    out = dict(profile=PROFILE, tier="webgpu", scene=scene, partition=partition, stratum=stratum,
               pose=pose, spanClass=span, scale=2, scheme="light", native=n, reference=c,
               candidate=c if k is None else k, bar=BAR, code=CODE)
    if bands is not None:
        out["bands"] = bands
    return out


def tband(n, c, k=None):
    return dict(native=n, reference=c, candidate=c if k is None else k)


def base_map(t_cells=3):
    """c05 against itself, by construction: F misses (×0.6), C rest within, C inactive and P near."""
    cells = []
    for i in range(8):
        cells.append(cell(f"F-rest-{i}", "F", "rest", 0.10, 0.06))
    for i in range(7):
        cells.append(cell(f"F-inactive-{i}", "F", "inactive", 0.10, 0.06))
    for i in range(t_cells):
        cells.append(cell(f"T-rest-{i}", "T", "rest", 0.10, 0.10, span="thin",
                          bands=dict(fine=tband(0.05, 0.03), low=tband(0.07, 0.07))))
    for i in range(10):
        cells.append(cell(f"C-rest-{i}", "C", "rest", 0.10, 0.105))
    for i in range(10):
        cells.append(cell(f"C-inactive-{i}", "C", "inactive", 0.10, 0.12))
    for i in range(8):
        cells.append(cell(f"P-rest-{i}", "P", "rest", 0.08, 0.075))
    for i in range(8):
        cells.append(cell(f"P-inactive-{i}", "P", "inactive", 0.08, 0.075))
    return cells


def halve_f(cells, factor=0.5):
    """Move every F cell's candidate so its |log((k + ε) / (n + ε))| is `factor` of c05's."""
    for c in cells:
        if c["stratum"] == "F":
            n, r, eps = c["native"], c["reference"], c["code"]
            c["candidate"] = (n + eps) * ((r + eps) / (n + eps)) ** factor - eps


def away_by(c, multiple):
    """Move one cell's candidate AWAY from native by `multiple` B beyond c05's error (g = multiple·B)."""
    n, r = c["native"], c["reference"]
    c["candidate"] = r + multiple * B if r >= n else r - multiple * B


def by_name(cells, name):
    return next(c for c in cells if c["scene"] == name)


class ClauseThree(unittest.TestCase):
    """The six cases, as clause 3 states them."""

    def test_a_halving_f_with_three_cells_at_2b_passes(self):
        cells = base_map()
        halve_f(cells)
        for i in range(3):
            away_by(by_name(cells, f"C-rest-{i}"), 2.0)
        r = rule.evaluate(cells)
        self.assertTrue(math.isclose(r["fAggregate"], 0.5 * r["fAggregateReference"], rel_tol=1e-12))
        self.assertEqual(len(r["awayBeyondB"]), 3)
        self.assertTrue(all(abs(a["growthInB"] - 2.0) < 1e-9 for a in r["awayBeyondB"]))
        self.assertTrue(r["budgetHolds"])
        self.assertEqual(r["gatedAggregateFailures"], [])
        self.assertEqual(r["verdict"], "IMPROVEMENT LANDING")

    def test_b_four_cells_at_2b_fails(self):
        cells = base_map()
        halve_f(cells)
        for i in range(4):
            away_by(by_name(cells, f"C-rest-{i}"), 2.0)
        r = rule.evaluate(cells)
        self.assertEqual(len(r["awayBeyondB"]), 4)
        self.assertFalse(r["budgetHolds"])
        self.assertEqual(r["gatedAggregateFailures"], [])     # the count alone decides it
        self.assertEqual(r["verdict"], "NEITHER: closes at the finding")
        self.assertTrue(any(w.startswith("budget count") for w in r["why"]))

    def test_c_one_cell_at_3_1b_fails(self):
        cells = base_map()
        halve_f(cells)
        away_by(by_name(cells, "C-rest-0"), 3.1)
        r = rule.evaluate(cells)
        self.assertEqual(len(r["awayBeyondB"]), 1)
        self.assertEqual(len(r["awayBeyondCeiling"]), 1)
        self.assertEqual(r["gatedAggregateFailures"], [])
        self.assertEqual(r["verdict"], "NEITHER: closes at the finding")
        self.assertTrue(any(w.startswith("budget ceiling") for w in r["why"]))

    def test_d_a_stratum_aggregate_worse_beyond_its_tolerance_fails(self):
        cells = base_map()
        halve_f(cells)
        for c in cells:
            if c["stratum"] == "P" and c["pose"] == "rest":
                away_by(c, 0.9)               # every cell under B: the budget is untouched
        r = rule.evaluate(cells)
        self.assertEqual(r["awayBeyondB"], [])
        g = r["groups"]["P rest"]
        self.assertTrue(g["gated"])
        self.assertGreater(g["A"], g["referenceA"] + g["tau"])
        self.assertEqual(r["gatedAggregateFailures"], ["P rest"])
        self.assertEqual(r["verdict"], "NEITHER: closes at the finding")

    def test_e_every_cell_unchanged_is_neither(self):
        r = rule.evaluate(base_map())
        self.assertEqual(r["partition"]["unchanged"]["total"], r["read"])
        self.assertEqual(r["partition"]["away"]["total"], 0)
        self.assertEqual(r["verdict"], "NEITHER: closes at the finding")

    def test_f_a_t_stratum_of_two_cells_is_reported_not_gated(self):
        cells = base_map(t_cells=2)
        halve_f(cells)
        for c in cells:
            if c["stratum"] == "T":           # T1-fine pushed away under B on both: A worse beyond τ
                c["bands"]["fine"]["candidate"] = 0.03 - 0.9 * B
        r = rule.evaluate(cells)
        g = r["groups"]["T rest"]
        self.assertEqual(g["cells"], 2)
        self.assertFalse(g["gated"])
        self.assertFalse(g["holds"])
        self.assertEqual(r["reportedAggregateOver"], ["T rest"])
        self.assertEqual(r["gatedAggregateFailures"], [])
        self.assertEqual(r["verdict"], "IMPROVEMENT LANDING")
        # ... and the same push on THREE T cells is gated, and fails.
        cells = base_map(t_cells=3)
        halve_f(cells)
        for c in cells:
            if c["stratum"] == "T":
                c["bands"]["fine"]["candidate"] = 0.03 - 0.9 * B
        r = rule.evaluate(cells)
        self.assertTrue(r["groups"]["T rest"]["gated"])
        self.assertEqual(r["gatedAggregateFailures"], ["T rest"])
        self.assertEqual(r["verdict"], "NEITHER: closes at the finding")


class Boundaries(unittest.TestCase):
    """The rule's own edges, beside the six."""

    def test_the_partition_has_no_crossing_state(self):
        # Crossed Apple with a smaller error: toward. Crossed with a larger error: away.
        self.assertEqual(rule.growth_change(0.10, 0.14, 0.075, BAR), "toward")
        self.assertEqual(rule.growth_change(0.10, 0.098, 0.13, BAR), "away")
        self.assertEqual(rule.growth_change(0.10, 0.14, 0.139, BAR), "unchanged")
        self.assertEqual(rule.growth_change(0.10, 0.12, 0.08, BAR), "toward")   # an equal-error crossing
        self.assertEqual(rule.growth_change(0.10, 0.12, 0.13, BAR), "away")

    def test_exactly_three_and_exactly_3b_pass(self):
        cells = base_map()
        halve_f(cells)
        away_by(by_name(cells, "C-rest-0"), 3.0)
        away_by(by_name(cells, "C-rest-1"), 2.0)
        away_by(by_name(cells, "C-inactive-0"), 2.0)
        r = rule.evaluate(cells)
        self.assertEqual(len(r["awayBeyondB"]), 3)
        self.assertEqual(r["awayBeyondCeiling"], [])
        self.assertEqual(r["verdict"], "IMPROVEMENT LANDING")

    def test_a_crossing_whose_error_grew_spends_the_budget(self):
        cells = base_map()
        halve_f(cells)
        c = by_name(cells, "C-rest-0")      # c05 0.105 over native 0.10: cross below, error 2.5 B larger
        c["candidate"] = 0.10 - (0.005 + 2.5 * B)
        r = rule.evaluate(cells)
        self.assertEqual([a["scene"] for a in r["awayBeyondB"]], ["C-rest-0"])

    def test_a_t_cell_spends_the_budget_on_t1_low_only(self):
        cells = base_map()
        halve_f(cells)
        t = by_name(cells, "T-rest-0")
        t["bands"]["low"]["candidate"] = 0.07 + 2.0 * B      # T1-low away at 2 B
        t["candidate"] = 0.10 + 10 * B                        # raw T1 is read by no clause
        r = rule.evaluate(cells)
        self.assertEqual([a["scene"] for a in r["awayBeyondB"]], ["T-rest-0"])
        self.assertEqual(r["verdict"], "IMPROVEMENT LANDING")
        cells = base_map()
        halve_f(cells)
        by_name(cells, "T-rest-0")["candidate"] = 0.10 + 10 * B
        self.assertEqual(rule.evaluate(cells)["awayBeyondB"], [])

    def test_full_close(self):
        cells = base_map()
        for c in cells:
            if c["stratum"] == "F":
                c["candidate"] = c["native"]
        r = rule.evaluate(cells)
        self.assertEqual(r["fNotWithin"], [])
        self.assertEqual(r["verdict"], "FULL CLOSE")

    def test_an_absent_member_is_unmeasured_never_a_landing(self):
        cells = base_map()
        halve_f(cells)
        missing = [dict(profile=PROFILE, tier="webgpu", scene="F-rest-x", partition="gate", stratum="F",
                        pose="rest", reason="no row")]
        self.assertTrue(rule.evaluate(cells, missing)["verdict"].startswith("UNMEASURED"))
        cells = base_map()
        halve_f(cells)
        del by_name(cells, "T-rest-0")["bands"]
        self.assertTrue(rule.evaluate(cells)["verdict"].startswith("UNMEASURED"))

    def test_the_gate_scope_reads_no_referee_or_holdout_cell(self):
        cells = base_map()
        halve_f(cells)
        cells.append(cell("C-referee", "C", "rest", 0.10, 0.105, k=0.30, partition="referee"))
        cells.append(cell("C-holdout", "C", "rest", 0.10, 0.105, k=0.30, partition="holdout"))
        self.assertEqual(rule.evaluate(cells)["awayBeyondB"], [])
        exposed = rule.evaluate(cells, partitions=("gate", "referee", "holdout"))
        self.assertEqual(sorted(a["scene"] for a in exposed["awayBeyondB"]), ["C-holdout", "C-referee"])

    def test_the_constants_are_the_charters(self):
        self.assertEqual((rule.BUDGET_COUNT, rule.BUDGET_CEILING_B, rule.GATING_MIN_CELLS), (3, 3.0, 3))


if __name__ == "__main__":
    unittest.main()
