#!/usr/bin/env python3.12
"""Red cases for `verify_amendment.py` (the review of W44 G1 steps 0-2, P2): an authorized path
carrying an unauthorized value is refused; the recorded amendment is accepted.

    python3.12 -B -m unittest test_verify_amendment -v      (from this directory)
"""
import copy
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import declare as D  # noqa: E402
import verify_amendment as V  # noqa: E402

FIT = json.loads(D.PARTS["fit"]["declaration"].read_text())
OPS = D.amendments("fit")[0]["ops"]
PRE = D.revert_ops(FIT, OPS)


def tampered(path, value):
    """The amendment with one authorized path's value replaced, and part 2 as it would then read."""
    ops = copy.deepcopy(OPS)
    i = next(i for i, o in enumerate(ops) if o["path"] == path)
    ops[i]["to"] = value
    return D.apply_ops(PRE, ops), ops


class Verify(unittest.TestCase):
    def test_the_recorded_amendment(self):
        self.assertEqual(V.differences(FIT, OPS), [])

    def test_an_unauthorized_value_at_an_authorized_path(self):
        fit, ops = tampered(["landingRule", "fullClose"], "every F cell within; all regressions permitted")
        D.validate_ops(ops)                      # the path check alone admits it
        self.assertTrue(V.differences(fit, ops))  # the value check refuses it

    def test_a_changed_grid_in_the_added_leaf(self):
        leaf = ["moves", 2, "families", "receded", "leaves", "sizeHeavySecondShare"]
        value = dict(next(o for o in OPS if o["path"] == leaf)["to"], grid=[0, 1])
        fit, ops = tampered(leaf, value)
        self.assertTrue(V.differences(fit, ops))

    def test_a_dropped_operation(self):
        ops = [o for o in OPS if o["path"] != ["fitCells"]]
        fit = D.apply_ops(PRE, ops)
        self.assertTrue(V.differences(fit, ops))


if __name__ == "__main__":
    unittest.main()
