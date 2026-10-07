"""W49a G0: the landing rule, the selection and X74 (`probes/rule.py`) rehearsed on committed readings.

The rehearsal reads two existing generations AS IF they were probe points, from W48's exposure cut alone:
`b2d074d2df24` itself (the shipped point: it must fail (a) and nothing else at the gate) and `d0219cd684bf`
(the pre-W48 point: it repairs (a) and (b) by definition and must fail (c) and (d), because W48's gains are
what it lacks). Synthetic cases hold X74's control and DL4's tie rule.

    python3.12 -B -m unittest -v test_rule      (from this directory)
"""
from __future__ import annotations

import copy
import unittest

import rule as R

B = R.b2d074_cells()


def as_point(column: str, scale: int, pose: str = "inactive") -> list[dict]:
    """The gate cells of one pose at `scale` with `candidate` set to the cut's `column`."""
    out = []
    for (sc, scene), c in B.items():
        if sc == scale and c["pose"] == pose and c["partition"] == "gate":
            cell = copy.deepcopy(c)
            cell["candidate"] = c[column]
            if "bands" in cell:
                for band in cell["bands"].values():
                    band["candidate"] = band[column]
            out.append(cell)
    return out


class Rule(unittest.TestCase):
    def test_moved_by_r(self):
        self.assertTrue(R.moved_by_r("checkerboard-64__rrect-lg__inactive"))
        self.assertTrue(R.moved_by_r("impulse__rrect-ml__inactive"))
        self.assertTrue(R.moved_by_r("photo__glass-over-glass__inactive"))
        self.assertFalse(R.moved_by_r("checkerboard-64__rrect-lg__rest"))
        self.assertFalse(R.moved_by_r("checkerboard__capsule-button__inactive-tint-orange"))
        self.assertFalse(R.moved_by_r("checkerboard-8__rrect-md__inactive"))

    def test_the_shipped_point_fails_the_repair_and_nothing_else(self):
        for scale in (1, 2):
            ev = R.evaluate_profile(as_point("candidate", scale), scale, B)
            self.assertFalse(ev["meets"])
            self.assertEqual(len(ev["failures"]), 1, ev["failures"])
            self.assertTrue(ev["failures"][0].startswith(f"(a) {R.REPAIR_GATE}"))
            self.assertEqual(ev["unread"], [])
            self.assertTrue(all(h["halved"] for h in ev["halvings"].values()), ev["halvings"])
        g = R.evaluate_profile(as_point("candidate", 1), 1, B)["failures"][0]
        self.assertIn("+8.94 B", g)

    def test_the_pre_w48_point_repairs_but_trades(self):
        for scale in (1, 2):
            cells = as_point("reference", scale) + as_point("reference", scale, "rest")
            ev = R.evaluate_profile(cells, scale, B)
            self.assertFalse(any(f.startswith("(a)") or f.startswith("(b)") for f in ev["failures"]))
            self.assertTrue(any(f.startswith("(c)") for f in ev["failures"]), ev["failures"])
            self.assertTrue(any(f.startswith("(d)") for f in ev["failures"]), ev["failures"])

    def test_x74_names_unmoved_cells_and_voids_on_a_control_drift(self):
        a = as_point("candidate", 1)
        b = copy.deepcopy(a)
        for c in b:
            if R.moved_by_r(c["scene"]):
                c["candidate"] += c["bar"]
        auth = R.authority({"x": a, "y": b}, 1, B)
        self.assertEqual(sorted(auth["reach"]), sorted(c["scene"] for c in a if R.moved_by_r(c["scene"])))
        self.assertTrue(all("predicted" in o["reason"] for o in auth["outside"]))
        self.assertEqual(auth["verdict"], "control holds")
        for c in b + a:
            if c["scene"] == "checkerboard-8__rrect-md__inactive":
                c["candidate"] += 0.2 * c["bar"]
        self.assertTrue(R.authority({"x": a, "y": b}, 1, B)["verdict"].startswith("VOID"))

    def test_selection_ties_go_to_the_largest_far_and_none_passing_is_neither(self):
        def point(repaired: bool):
            cells = []
            for scale in (1, 2):
                for c in as_point("candidate", scale):
                    c = copy.deepcopy(c)
                    if c["scene"] == R.REPAIR_GATE and repaired:
                        c["candidate"] = c["native"]                   # the repair cell at Apple's value
                    cells.append(c)
            return cells
        # Two points identical in every reading are tied, so the larger far wins; the unrepaired one fails (a).
        got = R.select({"p-a": (0.05, point(True)), "p-b": (0.09, point(True)), "p-c": (0.15, point(False))}, B)
        for scale in ("1x", "2x"):
            self.assertEqual(got["scales"][scale]["selected"], "p-b", got["scales"][scale]["why"])
        self.assertEqual(got["landing"], dict(tintAlphaFar1x=0.09, tintAlphaFar2x=0.09))
        none = R.select({"p-c": (0.15, point(False)), "p-d": (0.1, point(False))}, B)
        self.assertTrue(none["verdict"].startswith("NEITHER"))
        self.assertIsNone(none["landing"])

if __name__ == "__main__":
    unittest.main()
