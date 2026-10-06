"""W48 G0 (b): the verdict reader's tests (charter clause 3: "the reader's test, committed at (b), shows each
bar tripping on a synthetic reading"). Synthetic records only, and W47's committed CONTROL values (a rung
whose reading equals its reference); no ladder rung's reading is read here.

    python3.12 -B -m unittest -v test_verdicts      (from this directory)
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))
import bindings as W  # noqa: E402
import verdicts as V  # noqa: E402

PROTOCOL = json.loads((HERE / "protocol.json").read_text())
BARS = PROTOCOL["bars"]
THICK = BARS["operator 1"]["cells"]
FINE = BARS["operator 2"]["fine"]
GUARDS = BARS["operator 2"]["guards"]


def band(n, c, k, B=1.0, bar=0.5):
    """A rule.reads() band: growth |k - n| - |c - n|; the state by growth_change's partition."""
    growth = abs(k - n) - abs(c - n)
    change = "unchanged" if abs(k - c) <= bar else ("toward" if growth <= 0 else "away")
    return dict(n=n, c=c, k=k, B=B, growth=growth, change=change, growthInB=growth / B)


def thick(states, thin=True, l1=True):
    """A ladder (i) perScale record: `states` maps cell -> (n, c, k)."""
    return dict(thick={sid: dict(changeBand=band(*v), awayBand=band(*v)) for sid, v in states.items()},
                thinGain=0.10 if thin else 0.01, pointAThinGain=0.10, thinKeepsHalf=thin, L1passes=l1)


def closest_rung_like():
    """Two over-Apple cells toward, one over-Apple unchanged (hc-text-7's case), two under-Apple away beyond
    B but not past 3 B: Decision Log 3 (a)'s closure."""
    return {THICK[0]: (10, 12, 10.6), THICK[1]: (10, 12, 11), THICK[2]: (10, 12, 11.8),
            THICK[3]: (10, 9, 6.5), THICK[4]: (10, 9, 7)}


def fine_record(R1, R2, g1=0.0, g2=0.0):
    def cell(R):
        native, reference = 1.0, 3.0
        rung = reference - R * (reference - native)
        return dict(native=native, reference=reference, rung=rung, R=(reference - rung) / (reference - native),
                    wholeFallInB=2.5)
    return dict(fine=dict(cells={FINE[0]: cell(R1), FINE[1]: cell(R2)}),
                guards=dict(deltaInB={GUARDS[0]: g1, GUARDS[1]: g2}))


class Operator1(unittest.TestCase):
    bar = BARS["operator 1"]

    def test_unchanged_over_apple_is_admitted(self):
        got = V.operator1_scale(thick(closest_rung_like()), self.bar)
        self.assertEqual(got["changeState"][THICK[2]], "unchanged")
        self.assertTrue(got["overApple"][THICK[2]])
        self.assertTrue(got["meets"])

    def test_an_over_apple_cell_reading_away_trips(self):
        s = closest_rung_like()
        s[THICK[2]] = (10, 12, 12.6)
        got = V.operator1_scale(thick(s), self.bar)
        self.assertEqual(got["partition"]["overAppleNotAdmitted"], [THICK[2]])
        self.assertFalse(got["meets"])

    def test_three_cells_away_beyond_b_trip_the_count(self):
        s = closest_rung_like()
        s[THICK[1]] = (10, 9.5, 11.6)            # under Apple at the reference? no: c < n, drawn past it, away
        got = V.operator1_scale(thick(s), self.bar)
        self.assertEqual(len(got["partition"]["awayBeyondB"]), 3)
        self.assertFalse(got["partition"]["countHolds"])
        self.assertFalse(got["meets"])

    def test_a_cell_past_three_b_trips_the_ceiling(self):
        s = closest_rung_like()
        s[THICK[4]] = (10, 9, 5.5)
        got = V.operator1_scale(thick(s), self.bar)
        self.assertEqual(got["partition"]["awayBeyondCeiling"], [THICK[4]])
        self.assertFalse(got["meets"])

    def test_the_thin_clause_and_l1_each_trip(self):
        self.assertFalse(V.operator1_scale(thick(closest_rung_like(), thin=False), self.bar)["meets"])
        self.assertFalse(V.operator1_scale(thick(closest_rung_like(), l1=False), self.bar)["meets"])


class Operator2(unittest.TestCase):
    bar = BARS["operator 2"]

    def test_half_the_excess_meets(self):
        self.assertTrue(V.operator2_scale(fine_record(0.5, 0.9), self.bar)["meets"])

    def test_just_under_half_trips(self):
        got = V.operator2_scale(fine_record(0.499, 0.9), self.bar)
        self.assertFalse(got["fine"]["cells"][FINE[0]]["meets"])
        self.assertFalse(got["meets"])

    def test_no_excess_trips(self):
        rec = fine_record(0.9, 0.9)
        rec["fine"]["cells"][FINE[1]].update(reference=1.0, rung=1.0)
        rec["fine"]["cells"][FINE[1]].pop("R")
        self.assertIsNone(V.operator2_scale(rec, self.bar)["fine"]["cells"][FINE[1]]["R"])
        self.assertFalse(V.operator2_scale(rec, self.bar)["meets"])

    def test_a_guard_beyond_one_b_trips_and_one_b_holds(self):
        self.assertFalse(V.operator2_scale(fine_record(0.9, 0.9, g1=-1.01), self.bar)["meets"])
        self.assertTrue(V.operator2_scale(fine_record(0.9, 0.9, g2=-1.0), self.bar)["meets"])

    def test_a_recorded_r_the_inputs_do_not_give_refuses(self):
        rec = fine_record(0.6, 0.6)
        rec["fine"]["cells"][FINE[0]]["R"] = 0.61
        with self.assertRaises(V.Refusal):
            V.operator2_scale(rec, self.bar)


def joint_entry(R=0.8, photo_ratio=0.41, point_a=0.42, away=None):
    per = {}
    for s in (1, 2):
        reads = {sid: dict(changeBand=band(1, 3, 1.4), awayBand=band(1, 3, 1.4)) for sid in FINE}
        if away and s in away:
            reads[FINE[0]] = dict(changeBand=band(1, 3, 3.9), awayBand=band(1, 3, 3.9))
        per[str(s)] = dict(partitionReads=reads, fine=fine_record(R, R)["fine"],
                           photo=dict(ratio=photo_ratio, pointA=point_a, deltaFromPointAInBars=-0.02))
    return dict(overrides={}, perScale=per)


class Joint(unittest.TestCase):
    bar = BARS["joint"]

    def test_partition_and_halving_hold_and_the_photo_decides_nothing(self):
        got = V.joint(joint_entry(), self.bar)
        self.assertTrue(got["holds"])
        self.assertFalse(got["photo"][1]["atOrAbovePointA"])

    def test_an_over_apple_cell_away_trips_the_joint(self):
        self.assertFalse(V.joint(joint_entry(away={2}), self.bar)["holds"])

    def test_the_halving_trips_the_joint(self):
        self.assertFalse(V.joint(joint_entry(R=0.3), self.bar)["holds"])


def synthetic(meets: dict):
    """(protocol, reread, results) where each listed rung meets at the listed scales and nothing else does."""
    protocol = json.loads(json.dumps(PROTOCOL))
    rungs = {}
    for lid in ("i", "iii"):
        for lab in protocol["ladders"][lid]["rungs"]:
            ok = meets.get(lab, set())
            if lid == "i":
                per = {str(s): thick(closest_rung_like(), thin=s in ok) for s in (1, 2)}
            else:
                per = {str(s): fine_record(0.8 if s in ok else 0.2, 0.8) for s in (1, 2)}
            rungs[lab] = dict(ladder=lid, overrides={}, perScale=per)
    rungs["iv-joint"] = dict(ladder="iv", **joint_entry())
    results = dict(rungs={lab: dict(cells={"1x/x": dict(moved=True)}) for lab in rungs},
                   operators={"2x width": dict(meets=False, rungs=[], complete=True)},
                   ladders={"i": dict(passingL1=["i-a0.7"]), "ii": dict(complete=True, meets=[])})
    return protocol, dict(rungs=rungs), results


class Outcome(unittest.TestCase):
    def test_both_levers_meeting_are_both_members(self):
        p, rr, res = synthetic({"i-a0.7-f0.2-t128": {1, 2}, "iii-s4": {1, 2}, "iii-b4": {1, 2}})
        v = V.read(p, rr, res)
        self.assertEqual(v["operators"]["operator 2"]["members"], ["the tap", "the body width"])
        self.assertEqual(v["operators"]["operator 1"]["rungs"], ["i-a0.7-f0.2-t128"])
        self.assertTrue(v["outcome"].startswith("BOTH"))

    def test_a_ruled_one_scale_rung_is_recorded_and_an_unruled_one_stops(self):
        p, rr, res = synthetic({"i-a0.7-f0.2-t128": {1, 2}, "iii-s4": {1, 2}, "iii-s2": {2}})
        v = V.read(p, rr, res)
        self.assertEqual(v["oneScale"]["ruledOffGrid"], ["iii-s2"])
        self.assertTrue(v["outcome"].startswith("BOTH"))
        p, rr, res = synthetic({"i-a0.7-f0.2-t128": {1, 2}, "iii-s4": {1, 2}, "iii-s6": {1}})
        v = V.read(p, rr, res)
        self.assertEqual(v["oneScale"]["unruled"], ["iii-s6"])
        self.assertTrue(v["outcome"].startswith("STOP"))

    def test_one_operator_and_neither_stop(self):
        p, rr, res = synthetic({"iii-s4": {1, 2}})
        self.assertTrue(V.read(p, rr, res)["outcome"].startswith("ONE"))
        p, rr, res = synthetic({})
        self.assertTrue(V.read(p, rr, res)["outcome"].startswith("NEITHER"))

    def test_a_rung_w47_did_not_read_stops(self):
        p, rr, res = synthetic({})
        del rr["rungs"]["iii-s4"]
        with self.assertRaises(V.Refusal):
            V.read(p, rr, res)

    def test_a_difference_from_the_charter_is_said(self):
        p, rr, res = synthetic({"i-a0.7-f0.2-t128": {1, 2}, "iii-s4": {1, 2}})
        diffs = V.against_expected(V.read(p, rr, res), p["expected"])
        self.assertTrue(any(d.startswith("operator 1:") for d in diffs))
        self.assertTrue(any(d.startswith("body width:") for d in diffs))


class W47ControlRows(unittest.TestCase):
    """A rung whose reading IS the reference, built from W47's committed control values (results.json's
    `control` and `native`, `B`; reread.json's fine `reference` and `native`): every thick cell reads
    unchanged, R is 0, and neither bar is met (the thin clause has no gain)."""

    def setUp(self):
        ev = PROTOCOL["evidence"]
        self.results = json.loads((W.ROOT / ev["results"]["path"]).read_text())
        self.reread = json.loads((W.ROOT / ev["reread"]["path"]).read_text())

    def test_the_control_meets_no_bar(self):
        any_i = PROTOCOL["ladders"]["i"]["rungs"][0]
        any_iii = PROTOCOL["ladders"]["iii"]["rungs"][0]
        for s in (1, 2):
            cells = self.results["rungs"][any_i]["cells"]
            states = {sid: (cells[f"{s}x/{sid}"]["native"], cells[f"{s}x/{sid}"]["control"],
                            cells[f"{s}x/{sid}"]["control"]) for sid in THICK}
            rec = thick(states, thin=False)
            for sid in THICK:
                for b in ("changeBand", "awayBand"):
                    rec["thick"][sid][b]["B"] = cells[f"{s}x/{sid}"]["B"]
            got = V.operator1_scale(rec, BARS["operator 1"])
            self.assertTrue(all(st == "unchanged" for st in got["changeState"].values()))
            self.assertTrue(got["partition"]["holds"])
            self.assertFalse(got["meets"])
            fine = V.at_scale(self.reread["rungs"][any_iii]["perScale"], s)["fine"]["cells"]
            rec2 = dict(fine=dict(cells={sid: dict(native=fine[sid]["native"], reference=fine[sid]["reference"],
                                                   rung=fine[sid]["reference"]) for sid in FINE}),
                        guards=dict(deltaInB={sid: 0.0 for sid in GUARDS}))
            got2 = V.operator2_scale(rec2, BARS["operator 2"])
            self.assertTrue(all(c["R"] == 0 for c in got2["fine"]["cells"].values()))
            self.assertFalse(got2["meets"])


class Pinning(unittest.TestCase):
    def test_the_reader_refuses_before_part_one_is_hashed(self):
        def unhashed(part):
            raise W.Refusal("W48 part 1 is not hashed")
        with mock.patch.object(W, "require_part", unhashed), self.assertRaises(SystemExit):
            V.pinned_inputs()

    def test_the_reader_refuses_a_part_one_that_does_not_pin_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake = Path(tmp) / "declaration.json"
            fake.write_text(json.dumps(dict(sources={})))
            with mock.patch.object(W, "require_part", lambda part: "0" * 64), \
                    mock.patch.object(W, "PART1", fake), self.assertRaises(V.Refusal):
                V.pinned_inputs()


if __name__ == "__main__":
    unittest.main()
