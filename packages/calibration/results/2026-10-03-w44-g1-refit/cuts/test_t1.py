#!/usr/bin/env python3.12
"""W44 G1 step 0: G0's pinned examples (`results/2026-10-03-w44-g0-declaration/cuts/test_t1.py`),
copied unchanged, and extended to the text stratum's two bands (charter Decision Log 7 item 3):
the four change-state examples posed on a T cell's T1-fine and T1-low, the landing's reads of a T
cell, the selection metric without T, and the moves' within clauses. Part 2's one amendment pins
this file with `t1.py`, before any fit render.

G0's text follows, unchanged.

W44 G0 (d): T1's change-state examples, pinned before part 1 (charter Design "T1", output 2).

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


def cell(stratum, n, c, k, scene="s", bar=0.002, code=0.004, pose="rest", span="mid"):
    """A synthetic landing-scope cell: 2x light WebGPU, gate partition."""
    out = t1.classify(n, c, k, bar, code)
    return dict(out, profile=t1.GATED_PROFILES[1], tier="webgpu", scale=2, scheme="light",
                partition="gate", stratum=stratum, scene=scene, native=n, reference=c, candidate=k,
                bar=bar, code=code, logError=t1.log_error(k, n, code),
                referenceLogError=t1.log_error(c, n, code), pose=pose, spanClass=span)


class Landing(unittest.TestCase):
    """The review of W44 G0 (a)-(d): an absent reading in the landing scope is never a landing,
    and the selection metric is the charter's plain |log(web / native)|."""

    def test_full_close_when_every_f_cell_is_within(self):
        cells = [cell("F", 0.03, 0.06, 0.031), cell("C", 0.05, 0.05, 0.05), cell("P", 0.09, 0.06, 0.06)]
        self.assertEqual(t1.landing(cells)["verdict"], "FULL CLOSE (T1 clauses)")

    def test_an_unmeasured_scope_member_is_never_a_landing(self):
        cells = [cell("F", 0.03, 0.06, 0.031), cell("C", 0.05, 0.05, 0.05)]
        missing = [dict(profile=t1.GATED_PROFILES[1], tier="webgpu", scale=2, scheme="light",
                        partition="gate", stratum="F", scene="gone", reason="no reading")]
        got = t1.landing(cells, missing)
        self.assertFalse(got["fullCloseT1Clauses"])
        self.assertFalse(got["improvementT1Clauses"])
        self.assertTrue(got["verdict"].startswith("UNMEASURED"))
        # a member outside the scope (the referee partition, the 1x profile) does not hold it
        outside = [dict(missing[0], partition="referee"), dict(missing[0], scale=1)]
        self.assertEqual(t1.landing(cells, outside)["verdict"], "FULL CLOSE (T1 clauses)")

    def test_improvement_needs_half_the_f_aggregate_and_no_away_beyond_b(self):
        cells = [cell("F", 0.03, 0.09, 0.045, "a"), cell("F", 0.03, 0.09, 0.045, "b")]
        self.assertEqual(t1.landing(cells)["verdict"], "IMPROVEMENT LANDING (T1 clauses)")
        cells.append(cell("C", 0.05, 0.05, 0.08, "c"))      # away with g > B
        self.assertEqual(t1.landing(cells)["verdict"], "NEITHER: closes at the finding")

    def test_selection_metric_is_the_plain_log_ratio(self):
        cells = [cell("F", 0.02, 0.02, 0.04), cell("C", 0.05, 0.05, 0.05), cell("P", 0.10, 0.10, 0.05)]
        self.assertAlmostEqual(t1.selection_metric(cells), abs(__import__("math").log(2)), places=12)



# ---------------------------------------------------------------------------------------------
# W44 G1 step 0: the text stratum's two bands (Decision Log 7 item 3)
# ---------------------------------------------------------------------------------------------
KEY = ("p", "webgpu", "hc-text-7__rrect-md__rest")


def banded(fine, low, raw=(0.03, 0.025, 0.02), bar=0.002, code=0.004, scene="hc-text-7__rrect-md__rest"):
    """A T cell whose raw T1 reads `raw` (n, c, k) and whose bands read `fine` and `low`, each
    (n, c, k), through `band_outputs` as `cut` builds them."""
    bands = {KEY: {name: dict(native=v[0], web=v[2]) for name, v in (("fine", fine), ("low", low))}}
    refs = {KEY: {name: dict(native=v[0], web=v[1]) for name, v in (("fine", fine), ("low", low))}}
    got = cell("T", *raw, scene=scene, bar=bar, code=code)
    got["bands"] = t1.band_outputs(bands, refs, KEY, bar, code, "test")
    return got


class TextStratum(unittest.TestCase):
    """hc-text-7 is its own stratum, out of F; its outputs are its bands'."""

    def test_hc_text_7_is_T_and_not_F(self):
        self.assertEqual(t1.stratum("hc-text-7__rrect-md__rest"), "T")
        self.assertEqual(t1.stratum("checkerboard-4__rrect-md__rest"), "F")
        self.assertEqual(t1.stratum("checkerboard-8__rrect-md__rest"), "F")
        self.assertNotIn("hc-text-7", t1.STRATA["F"])
        self.assertEqual(sorted(t1.STRATA), ["C", "F", "P", "T"])

    def test_the_four_examples_on_the_fine_band(self):
        """G0's four pinned examples, posed on a T cell's T1-fine: its change IS T1-fine's."""
        for (n, c, k), (bar, code), want in (
                ((0.10, 0.14, 0.075), at(0.01), ("miss", "overshoot")),
                ((0.10, 0.14, 0.075), at(0.03, bar=0.005), ("within", "toward")),
                ((0.10, 0.12, 0.08), at(0.01), ("miss", "overshoot")),
                ((0.10, 0.14, 0.139), (0.002, 0.004), ("miss", "unchanged"))):
            got = banded(fine=(n, c, k), low=(0.05, 0.05, 0.05), bar=bar, code=code)
            fine = got["bands"]["fine"]
            self.assertEqual((fine["fidelity"], fine["change"]), want)
            reads = t1.landing_reads(got)
            self.assertEqual((reads["fidelity"], reads["change"]), want)

    def test_the_four_examples_on_the_low_band(self):
        """The same four on T1-low: its change is computed alike, and only its away is a veto."""
        for (n, c, k), (bar, code), want in (
                ((0.10, 0.14, 0.075), at(0.01), ("miss", "overshoot")),
                ((0.10, 0.14, 0.075), at(0.03, bar=0.005), ("within", "toward")),
                ((0.10, 0.12, 0.08), at(0.01), ("miss", "overshoot")),
                ((0.10, 0.14, 0.139), (0.002, 0.004), ("miss", "unchanged"))):
            got = banded(fine=(0.05, 0.05, 0.05), low=(n, c, k), bar=bar, code=code)
            low = got["bands"]["low"]
            self.assertEqual((low["fidelity"], low["change"]), want)
            # T1-low's overshoot is not the cell's change: the cell's change is T1-fine's
            self.assertEqual(t1.landing_reads(got)["change"], "unchanged")

    def test_low_band_away_beyond_B_is_the_veto(self):
        got = banded(fine=(0.05, 0.06, 0.055), low=(0.03, 0.025, 0.018))   # low away, g 0.007 > B 0.004
        self.assertEqual(got["bands"]["low"]["change"], "away")
        cells = [cell("F", 0.03, 0.06, 0.031), got]
        verdict = t1.landing(cells)
        self.assertEqual(verdict["awayBeyondB"], ["hc-text-7__rrect-md__rest 2x"])
        self.assertEqual(verdict["verdict"], "NEITHER: closes at the finding")

    def test_raw_t1_away_is_recorded_and_no_veto(self):
        """T1 itself away far beyond B on a T cell, both bands toward: no veto (T1 is recorded)."""
        got = banded(fine=(0.05, 0.10, 0.06), low=(0.03, 0.02, 0.025), raw=(0.03, 0.025, 0.015))
        self.assertEqual(got["change"], "away")
        self.assertGreater(got["growth"], got["B"])
        verdict = t1.landing([cell("F", 0.03, 0.06, 0.031), got])
        self.assertEqual(verdict["awayBeyondB"], [])
        self.assertEqual(verdict["verdict"], "FULL CLOSE (T1 clauses)")
        self.assertEqual(verdict["textCells"][0]["t1"]["change"], "away")

    def test_full_close_does_not_require_a_T_cell_within(self):
        got = banded(fine=(0.05, 0.12, 0.11), low=(0.03, 0.03, 0.03))       # fine miss, toward
        self.assertEqual(got["bands"]["fine"]["fidelity"], "miss")
        verdict = t1.landing([cell("F", 0.03, 0.06, 0.031), got])
        self.assertEqual(verdict["verdict"], "FULL CLOSE (T1 clauses)")

    def test_fine_band_overshoot_is_the_cells_overshoot(self):
        got = banded(fine=(0.10, 0.14, 0.075), low=(0.03, 0.03, 0.03), bar=0.005, code=0.01)
        verdict = t1.landing([cell("F", 0.03, 0.06, 0.031), got])
        self.assertEqual(verdict["overshoot"], ["hc-text-7__rrect-md__rest 2x"])

    def test_a_T_cell_without_bands_is_unmeasured(self):
        got = cell("T", 0.03, 0.025, 0.02, scene="hc-text-7__rrect-md__rest")
        verdict = t1.landing([cell("F", 0.03, 0.06, 0.031), got])
        self.assertTrue(verdict["verdict"].startswith("UNMEASURED"))
        self.assertIn("no band reading", verdict["unmeasuredInScope"][0])

    def test_a_band_native_disagreement_refuses(self):
        bands = {KEY: {"fine": dict(native=0.05, web=0.05), "low": dict(native=0.03, web=0.03)}}
        refs = {KEY: {"fine": dict(native=0.051, web=0.05), "low": dict(native=0.03, web=0.03)}}
        with self.assertRaises(SystemExit):
            t1.band_outputs(bands, refs, KEY, 0.002, 0.004, "test")

    def test_absent_band_readings_give_none(self):
        self.assertIsNone(t1.band_outputs(None, None, KEY, 0.002, 0.004, "test"))
        self.assertIsNone(t1.band_outputs({}, {KEY: {}}, KEY, 0.002, 0.004, "test"))


class SelectionAndMoves(unittest.TestCase):
    """The selection metric reads F u C u P; the moves' clauses as part 2 states them."""

    def test_selection_metric_leaves_T_out(self):
        cells = [cell("F", 0.02, 0.02, 0.04), cell("C", 0.05, 0.05, 0.05), cell("P", 0.10, 0.10, 0.05),
                 cell("T", 0.10, 0.10, 0.01), cell("T", 0.10, 0.10, 0.01)]
        self.assertAlmostEqual(t1.selection_metric(cells), abs(__import__("math").log(2)), places=12)

    def test_move_objective_reads_the_moves_cells(self):
        cells = [cell("F", 0.02, 0.02, 0.04, span="mid"), cell("C", 0.05, 0.05, 0.05, span="thin"),
                 cell("C", 0.05, 0.05, 0.10, pose="inactive", span="thin")]
        self.assertAlmostEqual(t1.move_objective(cells, "move1"), abs(__import__("math").log(2)), places=12)
        self.assertAlmostEqual(t1.move_objective(cells, "move2"), 0.0, places=12)
        self.assertAlmostEqual(t1.move_objective(cells, "move3"), abs(__import__("math").log(2)), places=12)

    def test_move1_clause_is_F_and_pitch_16_and_not_the_photo(self):
        f = cell("F", 0.03, 0.06, 0.031, scene="checkerboard-4__rrect-md__rest")
        p16 = cell("C", 0.03, 0.03, 0.0305, scene="checkerboard__rrect-md__rest")
        photo = cell("P", 0.09, 0.06, 0.06, scene="photo__rrect-md__rest")          # a miss
        cb64 = cell("C", 0.03, 0.03, 0.05, scene="checkerboard-64__rrect-md__rest")  # a miss, not in it
        text = banded(fine=(0.05, 0.12, 0.11), low=(0.03, 0.03, 0.03))
        got = t1.within_clause([f, p16, photo, cb64, text], "move1")
        self.assertEqual(got["verdict"], "WITHIN")
        self.assertEqual(got["members"], 2)
        p16_miss = cell("C", 0.03, 0.03, 0.05, scene="checkerboard__rrect-md__rest")
        self.assertEqual(t1.within_clause([f, p16_miss], "move1")["verdict"], "NOT WITHIN")

    def test_move2_clause_reads_every_F_C_P_cell_but_no_T(self):
        thin = dict(span="thin")
        c = cell("C", 0.03, 0.03, 0.05, scene="checkerboard-64__rrect-sm__rest", **thin)
        text = banded(fine=(0.05, 0.12, 0.11), low=(0.03, 0.03, 0.03))
        text["spanClass"] = "thin"
        self.assertEqual(t1.within_clause([c, text], "move2")["verdict"], "NOT WITHIN")
        ok = cell("C", 0.03, 0.03, 0.0305, scene="checkerboard-64__rrect-sm__rest", **thin)
        self.assertEqual(t1.within_clause([ok, text], "move2")["verdict"], "WITHIN")

    def test_a_missing_clause_member_is_unmeasured(self):
        f = cell("F", 0.03, 0.06, 0.031, scene="checkerboard-4__rrect-md__rest")
        gone = dict(profile=t1.GATED_PROFILES[1], tier="webgpu", scale=2, scheme="light",
                    partition="gate", stratum="F", scene="checkerboard-8__rrect-md__rest",
                    pose="rest", reason="no row")
        self.assertEqual(t1.within_clause([f], "move1", [gone])["verdict"], "UNMEASURED")


if __name__ == "__main__":
    unittest.main()
