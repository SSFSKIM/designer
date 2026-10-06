#!/usr/bin/env python3.12
"""W47 G0 (d): W45's landing rule as W46 bound it and W47 carries it verbatim (charter Design "The
landing rule"; clause 3: "plus W45's synthetic cases"), on synthetic maps, pinned before part 1 is
hashed. W46's test (`results/2026-10-05-w46-g0-declaration/cuts/test_rule.py`), ported by copy; W47
changes no case. W46's text follows.

W46 G0 (c): W45's landing rule as W46 binds it, on synthetic maps, pinned before part 1 is hashed
(charter clause 2: "W45's synthetic cases as tests"; Decision Log 3).

The synthetic map carries the REAL gate shape per dark profile (Design "The referees"): F rest 10,
F inactive 2, T rest 3, C rest 28, C inactive 14, P rest 4, P inactive 5. Its reference misses every
target (P ×0.4, C rest ×0.6, F inactive ×3), so each has something to halve.

W45's six clause-3 cases, each carried to W46's targets, per profile:
  (a) a map halving every target with three cells at 2B passes (improvement landing);
  (b) four cells at 2B fails (the count alone);
  (c) one cell at 3.1B fails (the ceiling);
  (d) a gated stratum aggregate worse by more than its tolerance fails;
  (e) every cell `unchanged` is neither;
  (f) a group of two gate cells is reported, not gated (W46's F inactive, the real shape).
Then the rule's boundaries (no crossing state; exactly three and exactly 3B pass; a crossing whose
error grew spends the budget; a T cell spends it on T1-low only; full close needs every target cell;
an absent member is UNMEASURED; the gate reads no referee or holdout; the exposure cannot gate a
reported group) and W46's own: the budget is per profile, the verdict is the weaker profile's, a
target halved at one scale only is neither, the scope is the dark WebGPU cells only, and the stage
clauses read their declared cells.

    cd packages/calibration/results/2026-10-06-w47-g0-operators/cuts
    python3.12 -B -m unittest test_rule -v
"""
import math
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import bed  # noqa: E402,F401  (W47's port first, so W44 G1's t1 binds to it)
sys.path.insert(1, str(bed.W44_G1 / "cuts"))
import rule  # noqa: E402

ONE, TWO = rule.SCOPE_PROFILES
CODE, BAR = 2 ** -8, 2 ** -9       # B = max(code, 2 bar) = 2^-8: dyadic, so "exactly 3B" is exact
B = max(CODE, 2 * BAR)
SHAPE = {("F", "rest"): 10, ("F", "inactive"): 2, ("T", "rest"): 3, ("C", "rest"): 28,
         ("C", "inactive"): 14, ("P", "rest"): 4, ("P", "inactive"): 5}
# (native, reference) per group: the targets miss, the others sit near Apple.
LEVELS = {("F", "rest"): (0.10, 0.08), ("F", "inactive"): (0.02, 0.03), ("T", "rest"): (0.10, 0.10),
          ("C", "rest"): (0.10, 0.06), ("C", "inactive"): (0.10, 0.12), ("P", "rest"): (0.08, 0.032),
          ("P", "inactive"): (0.08, 0.032)}


def cell(profile, scene, stratum, pose, n, c, k=None, span="mid", partition="gate", bands=None, tier="webgpu"):
    out = dict(profile=profile, tier=tier, scene=scene, partition=partition, stratum=stratum, pose=pose,
               spanClass=span, scale=2 if "-2x-" in profile else 1, scheme="dark", native=n, reference=c,
               candidate=c if k is None else k, bar=BAR, code=CODE,
               fidelity="miss")
    if bands is not None:
        out["bands"] = bands
    return out


def tband(n, c, k=None):
    return dict(native=n, reference=c, candidate=c if k is None else k)


def base_map(profiles=(ONE, TWO), shape=None):
    shape = shape or SHAPE
    cells = []
    for profile in profiles:
        for (s, p), count in shape.items():
            n, c = LEVELS[(s, p)]
            for i in range(count):
                bands = dict(fine=tband(0.05, 0.03), low=tband(0.07, 0.07)) if s == "T" else None
                cells.append(cell(profile, f"{s}-{p}-{i}", s, p, n, c, span="thin" if s == "T" else "mid",
                                  bands=bands))
    return cells


def halve(cells, groups=None, factor=0.49, profiles=(ONE, TWO)):
    """Move every target cell's candidate so its |log((k + ε)/(n + ε))| is `factor` of the reference's
    (0.49: clear of the half by more than float rounding)."""
    for c in cells:
        target = rule.is_target(c)
        if target is None or c["profile"] not in profiles or (groups and target not in groups):
            continue
        n, r, eps = c["native"], c["reference"], c["code"]
        c["candidate"] = (n + eps) * ((r + eps) / (n + eps)) ** factor - eps


def away_by(c, multiple):
    """Move one cell's candidate AWAY from native by `multiple` B beyond the reference's error."""
    n, r = c["native"], c["reference"]
    c["candidate"] = r + multiple * B if r >= n else r - multiple * B


def by_name(cells, name, profile=ONE):
    return next(c for c in cells if c["scene"] == name and c["profile"] == profile)


class ClauseThree(unittest.TestCase):
    """W45's six cases, carried to W46's targets."""

    def test_a_halving_every_target_with_three_cells_at_2b_passes(self):
        cells = base_map()
        halve(cells)
        for profile in (ONE, TWO):           # three per profile: the budget is per profile
            for i in range(3):
                away_by(by_name(cells, f"C-inactive-{i}", profile), 2.0)
        r = rule.evaluate(cells)
        for profile in (ONE, TWO):
            p = r["profiles"][profile]
            for t, a in p["targets"].items():
                self.assertTrue(math.isclose(a["A"], 0.49 * a["referenceA"], rel_tol=1e-9), t)
            self.assertEqual(len(p["awayBeyondB"]), 3)
            self.assertTrue(p["budgetHolds"])
            self.assertEqual(p["gatedAggregateFailures"], [])
        self.assertEqual(r["verdict"], "IMPROVEMENT LANDING")

    def test_b_four_cells_at_2b_fails(self):
        cells = base_map()
        halve(cells)
        for i in range(4):
            away_by(by_name(cells, f"C-inactive-{i}", TWO), 2.0)
        r = rule.evaluate(cells)
        p = r["profiles"][TWO]
        self.assertEqual(len(p["awayBeyondB"]), 4)
        self.assertFalse(p["budgetHolds"])
        self.assertEqual(p["gatedAggregateFailures"], [])
        self.assertTrue(any(w.startswith("budget count") for w in p["why"]))
        self.assertEqual(r["profiles"][ONE]["verdict"], "IMPROVEMENT LANDING")
        self.assertEqual(r["verdict"], "NEITHER: closes at the finding")

    def test_c_one_cell_at_3_1b_fails(self):
        cells = base_map()
        halve(cells)
        away_by(by_name(cells, "C-inactive-0"), 3.1)
        r = rule.evaluate(cells)
        p = r["profiles"][ONE]
        self.assertEqual(len(p["awayBeyondCeiling"]), 1)
        self.assertTrue(any(w.startswith("budget ceiling") for w in p["why"]))
        self.assertEqual(r["verdict"], "NEITHER: closes at the finding")

    def test_d_a_gated_aggregate_worse_beyond_its_tolerance_fails(self):
        cells = base_map()
        halve(cells)
        for c in cells:
            if (c["stratum"], c["pose"], c["profile"]) == ("F", "rest", ONE):
                away_by(c, 0.9)               # every cell under B: the budget is untouched
        r = rule.evaluate(cells)
        p = r["profiles"][ONE]
        self.assertEqual(p["awayBeyondB"], [])
        g = p["groups"]["F rest"]
        self.assertTrue(g["gated"])
        self.assertGreater(g["A"], g["referenceA"] + g["tau"])
        self.assertEqual(p["gatedAggregateFailures"], ["F rest"])
        self.assertEqual(r["verdict"], "NEITHER: closes at the finding")

    def test_e_every_cell_unchanged_is_neither(self):
        r = rule.evaluate(base_map())
        for p in r["profiles"].values():
            self.assertEqual(p["partition"]["unchanged"]["total"], p["read"])
            self.assertEqual(p["read"], sum(SHAPE.values()))
        self.assertEqual(r["verdict"], "NEITHER: closes at the finding")

    def test_f_a_group_of_two_gate_cells_is_reported_not_gated(self):
        cells = base_map()
        halve(cells)
        for c in cells:                       # F inactive's two cells pushed worse than the reference
            if (c["stratum"], c["pose"]) == ("F", "inactive"):
                c["candidate"] = c["reference"] + 0.9 * B
        r = rule.evaluate(cells)
        g = r["profiles"][ONE]["groups"]["F inactive"]
        self.assertEqual((g["cells"], g["gated"], g["holds"]), (2, False, False))
        self.assertEqual(r["profiles"][ONE]["reportedAggregateOver"], ["F inactive"])
        self.assertEqual(r["profiles"][ONE]["gatedAggregateFailures"], [])
        # ...but F inactive is a TARGET, so its aggregate failing to halve still denies the landing.
        self.assertFalse(r["profiles"][ONE]["targets"]["F inactive"]["halved"])
        self.assertEqual(r["verdict"], "NEITHER: closes at the finding")


class Boundaries(unittest.TestCase):
    def test_the_partition_has_no_crossing_state(self):
        self.assertEqual(rule.growth_change(0.10, 0.14, 0.075, BAR), "toward")
        self.assertEqual(rule.growth_change(0.10, 0.098, 0.13, BAR), "away")
        self.assertEqual(rule.growth_change(0.10, 0.14, 0.139, BAR), "unchanged")
        self.assertEqual(rule.growth_change(0.10, 0.12, 0.08, BAR), "toward")
        self.assertEqual(rule.growth_change(0.10, 0.12, 0.13, BAR), "away")

    def test_exactly_three_and_exactly_3b_pass(self):
        cells = base_map()
        halve(cells)
        away_by(by_name(cells, "C-inactive-0"), 3.0)
        away_by(by_name(cells, "C-inactive-1"), 2.0)
        away_by(by_name(cells, "F-rest-0"), 2.0)
        r = rule.evaluate(cells)
        self.assertEqual(len(r["profiles"][ONE]["awayBeyondB"]), 3)
        self.assertEqual(r["profiles"][ONE]["awayBeyondCeiling"], [])
        self.assertEqual(r["verdict"], "IMPROVEMENT LANDING")

    def test_a_crossing_whose_error_grew_spends_the_budget(self):
        cells = base_map()
        halve(cells)
        c = by_name(cells, "C-inactive-0")    # reference 0.1875 over native 0.125: cross below, error 2.5 B larger
        c["candidate"] = 0.125 - (0.0625 + 2.5 * B)
        r = rule.evaluate(cells)
        self.assertEqual([a["scene"] for a in r["profiles"][ONE]["awayBeyondB"]], ["C-inactive-0"])

    def test_a_t_cell_spends_the_budget_on_t1_low_only(self):
        cells = base_map()
        halve(cells)
        t = by_name(cells, "T-rest-0")
        t["bands"]["low"]["candidate"] = 0.07 + 2.0 * B
        t["candidate"] = 0.10 + 10 * B        # raw T1 is read by no clause
        r = rule.evaluate(cells)
        self.assertEqual([a["scene"] for a in r["profiles"][ONE]["awayBeyondB"]], ["T-rest-0"])
        self.assertEqual(r["verdict"], "IMPROVEMENT LANDING")
        cells = base_map()
        halve(cells)
        by_name(cells, "T-rest-0")["candidate"] = 0.10 + 10 * B
        self.assertEqual(rule.evaluate(cells)["profiles"][ONE]["awayBeyondB"], [])

    def test_full_close_needs_every_target_cell_within(self):
        cells = base_map()
        for c in cells:
            if rule.is_target(c):
                c["candidate"] = c["native"]
        self.assertEqual(rule.evaluate(cells)["verdict"], "FULL CLOSE")
        by_name(cells, "C-rest-5", TWO)["candidate"] = by_name(cells, "C-rest-5", TWO)["reference"]
        r = rule.evaluate(cells)
        self.assertEqual(r["profiles"][TWO]["targetNotWithin"]["C rest"], ["C-rest-5"])
        self.assertEqual(r["profiles"][TWO]["verdict"], "IMPROVEMENT LANDING")
        self.assertEqual(r["verdict"], "IMPROVEMENT LANDING")

    def test_an_absent_member_is_unmeasured_never_a_landing(self):
        cells = base_map()
        halve(cells)
        missing = [dict(profile=TWO, tier="webgpu", scene="F-rest-x", partition="gate", stratum="F",
                        pose="rest", reason="no row")]
        self.assertTrue(rule.evaluate(cells, missing)["verdict"].startswith("UNMEASURED"))
        cells = base_map()
        halve(cells)
        del by_name(cells, "T-rest-0")["bands"]
        self.assertTrue(rule.evaluate(cells)["verdict"].startswith("UNMEASURED"))

    def test_the_gate_scope_reads_no_referee_or_holdout_cell(self):
        cells = base_map()
        halve(cells)
        cells.append(cell(ONE, "C-referee", "C", "rest", 0.10, 0.105, k=0.30, partition="referee"))
        cells.append(cell(ONE, "C-holdout", "C", "rest", 0.10, 0.105, k=0.30, partition="holdout"))
        self.assertEqual(rule.evaluate(cells)["profiles"][ONE]["awayBeyondB"], [])
        exposed = rule.evaluate(cells, partitions=("gate", "referee", "holdout"))
        self.assertEqual(sorted(a["scene"] for a in exposed["profiles"][ONE]["awayBeyondB"]),
                         ["C-holdout", "C-referee"])

    def test_the_exposure_does_not_gate_a_group_the_gate_reports(self):
        # The real dark shape: F inactive holds two gate cells and one referee
        # (`checkerboard-4__rrect-md__inactive`). At the exposure it stays REPORTED.
        cells = base_map()
        halve(cells)
        cells.append(cell(ONE, "F-inactive-referee", "F", "inactive", 0.02, 0.03, k=0.20, partition="referee"))
        exposed = rule.evaluate(cells, partitions=("gate", "referee", "holdout"))
        g = exposed["profiles"][ONE]["groups"]["F inactive"]
        self.assertEqual((g["cells"], g["gateCells"], g["gated"]), (3, 2, False))

    def test_the_budget_and_the_verdict_are_per_profile(self):
        cells = base_map()
        halve(cells)
        for i in range(3):
            away_by(by_name(cells, f"C-inactive-{i}", ONE), 2.0)
            away_by(by_name(cells, f"C-inactive-{i}", TWO), 2.0)
        self.assertEqual(rule.evaluate(cells)["verdict"], "IMPROVEMENT LANDING")   # six in all, three per profile

    def test_a_target_halved_at_one_scale_only_is_neither(self):
        cells = base_map()
        halve(cells, profiles=(TWO,))
        r = rule.evaluate(cells)
        self.assertEqual(r["profiles"][TWO]["verdict"], "IMPROVEMENT LANDING")
        self.assertEqual(r["profiles"][ONE]["verdict"], "NEITHER: closes at the finding")
        self.assertEqual(r["verdict"], "NEITHER: closes at the finding")
        cells = base_map()
        halve(cells, groups=("P", "C rest"))
        self.assertEqual(rule.evaluate(cells)["verdict"], "NEITHER: closes at the finding")

    def test_the_scope_is_the_dark_webgpu_cells(self):
        cells = base_map()
        halve(cells)
        light = "apple-macos-27.0-2x-light-standard-glass0.25"
        cells.append(cell(light, "C-light", "C", "rest", 0.10, 0.105, k=0.30))
        cells.append(cell(ONE, "C-css", "C", "rest", 0.10, 0.105, k=0.30, tier="css"))
        r = rule.evaluate(cells)
        self.assertEqual(r["verdict"], "IMPROVEMENT LANDING")
        self.assertEqual(r["profiles"][ONE]["read"], sum(SHAPE.values()))

    def test_the_stage_clauses_read_their_declared_cells(self):
        cells = base_map()
        for c in cells:
            c["fidelity"] = "within" if rule.is_target(c) else "miss"
        self.assertEqual(rule.stage_within(cells, "stage1")["members"], 2 * (28 + 4))
        self.assertEqual(rule.stage_within(cells, "stage2")["members"], 2 * (5 + 2))
        self.assertEqual(rule.stage_within(cells, "stage1")["verdict"], "WITHIN")
        rest = [c for c in cells if c["pose"] == "rest" and c["stratum"] in ("F", "C", "P")]
        want = sorted(abs(math.log(c["candidate"] / c["native"])) for c in rest)
        got = rule.stage_objective(cells, "stage1")
        self.assertAlmostEqual(got, (want[len(want) // 2 - 1] + want[len(want) // 2]) / 2
                               if len(want) % 2 == 0 else want[len(want) // 2])

    def test_the_constants_are_the_charters(self):
        self.assertEqual((rule.BUDGET_COUNT, rule.BUDGET_CEILING_B, rule.GATING_MIN_CELLS), (3, 3.0, 3))
        self.assertEqual(rule.REFERENCE, "d0219cd684bf")
        self.assertEqual(rule.TARGETS, {"P": (("P", "rest"), ("P", "inactive")), "C rest": (("C", "rest"),),
                                        "F inactive": (("F", "inactive"),)})


if __name__ == "__main__":
    unittest.main()
