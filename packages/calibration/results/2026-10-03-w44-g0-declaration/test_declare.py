#!/usr/bin/env python3.12
"""W44 G0 (g): the part-2 validator's red cases (charter clause 1; X50).

Part 2 is the draft changed only by the protocol's enumerated decisions, each supported by the
ladder results. These cases pose synthetic ladder results against the committed draft and
protocol and assert what `declare.validate_fit` accepts and refuses: a changed prediction and a
widened grid are refused (the brief's two red cases), and so are a narrowing outside the
ladder's non-flat range, a strike the ladder did not make, a new leaf, and C's inert setting
fixed without L3's proof; a strike, a narrowing and the inert fix that the results support pass.

    python3.12 -B -m unittest test_declare -v      (from this directory)
"""
import copy
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import declare as D  # noqa: E402

DRAFT = json.loads(D.DRAFT.read_text())
PROTOCOL = json.loads(D.PROTOCOL.read_text())


def results(**ladders):
    base = {lid: {"struck": False, "inert1x": lid == "L3", "nonFlatRange": {}} for lid in
            ("L1", "L2", "L3", "L4", "L5", "L6", "L7", "L8")}
    for lid, entry in ladders.items():
        base[lid].update(entry)
    return {"ladders": base}


def fit(changes, mutate=None):
    body = D.apply_changes(DRAFT, changes, RESULTS_FOR_BUILD, PROTOCOL)
    body.pop("status", None)
    if mutate:
        mutate(body)
    return dict(body, status="part 2", changes=changes)


RESULTS_FOR_BUILD = results(
    L2={"struck": True},
    L1={"nonFlatRange": {"sizeScatterFloor2x": [0.7, 1.0]}},
    L8={"nonFlatRange": {"sizeHeavyTapSigma2x": [14, 20]}})


class Accepts(unittest.TestCase):
    def test_the_draft_unchanged(self):
        D.validate_fit(DRAFT, fit([]), results(), PROTOCOL)

    def test_a_strike_the_ladder_made(self):
        ch = [{"kind": "strike", "move": "move1", "family": "B", "leaf": "sizeHeavyTapSigma2x", "ladder": "L2"}]
        got = fit(ch)
        self.assertNotIn("B", got["moves"][0]["families"])
        self.assertNotIn("B", got["moves"][0]["familyOrder"])
        D.validate_fit(DRAFT, got, RESULTS_FOR_BUILD, PROTOCOL)

    def test_a_narrowing_inside_the_non_flat_range(self):
        ch = [{"kind": "narrow", "move": "move1", "family": "A", "leaf": "sizeScatterFloor2x", "ladder": "L1",
               "grid": [0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]}]
        D.validate_fit(DRAFT, fit(ch), RESULTS_FOR_BUILD, PROTOCOL)

    def test_the_inert_setting_proven(self):
        ch = [{"kind": "inert", "ladder": "L3"}]
        got = fit(ch)
        self.assertTrue(got["moves"][0]["families"]["C"]["fixed"]["sizeHeavySecondSigma"]["inert"]
                        .startswith("proven by L3"))
        D.validate_fit(DRAFT, got, results(), PROTOCOL)


class Refuses(unittest.TestCase):
    def refused(self, body, res=RESULTS_FOR_BUILD):
        with self.assertRaises(D.Refusal):
            D.validate_fit(DRAFT, body, res, PROTOCOL)

    def test_a_changed_prediction(self):
        def mutate(b):
            b["moves"][0]["families"]["A"]["prediction"] = "A is within on both ends"
        self.refused(fit([], mutate))

    def test_a_widened_grid(self):
        def mutate(b):
            b["moves"][0]["families"]["B"]["leaves"]["sizeHeavyTapSigma2x"]["grid"] = [4, 6, 7, 8, 9, 10, 12, 14, 17, 20]
        self.refused(fit([], mutate))

    def test_a_widened_domain(self):
        def mutate(b):
            b["moves"][0]["families"]["A"]["leaves"]["sizeScatterFloor2x"]["domain"] = [0.5, 1.0]
        self.refused(fit([], mutate))

    def test_a_narrowing_outside_the_ladders_range(self):
        ch = [{"kind": "narrow", "move": "move1", "family": "A", "leaf": "sizeScatterFloor2x", "ladder": "L1",
               "grid": [0.6, 0.7]}]
        with self.assertRaises(D.Refusal):
            fit(ch)

    def test_a_narrowing_that_adds_a_point(self):
        ch = [{"kind": "narrow", "move": "move3", "family": "receded", "leaf": "sizeHeavyTapSigma2x",
               "ladder": "L8", "grid": [15, 18]}]
        with self.assertRaises(D.Refusal):
            fit(ch)

    def test_a_strike_the_ladder_did_not_make(self):
        ch = [{"kind": "strike", "move": "move1", "family": "A", "leaf": "sizeScatterFloor2x", "ladder": "L1"}]
        with self.assertRaises(D.Refusal):
            fit(ch)

    def test_a_strike_citing_another_leafs_ladder(self):
        ch = [{"kind": "strike", "move": "move1", "family": "A", "leaf": "sizeScatterFloor2x", "ladder": "L2"}]
        with self.assertRaises(D.Refusal):
            fit(ch)

    def test_a_new_leaf(self):
        def mutate(b):
            b["moves"][1]["families"]["start"]["leaves"]["sizeScatterSpanMax2x"] = {
                "slot": "active.light", "unit": "px", "domain": [128, 256], "grid": [128, 256]}
        self.refused(fit([], mutate))

    def test_the_inert_setting_without_the_proof(self):
        ch = [{"kind": "inert", "ladder": "L3"}]
        body = fit(ch)
        self.refused(body, results(L3={"inert1x": False}))

    def test_an_undeclared_change_kind(self):
        self.refused(dict(fit([]), changes=[{"kind": "retune", "ladder": "L1"}]))

    def test_a_missing_change_list(self):
        body = fit([])
        del body["changes"]
        self.refused(body)


if __name__ == "__main__":
    unittest.main()
