#!/usr/bin/env python3.12
"""W44 G1 step 0: part 2's one amendment, red cases (charter v1.3, Decision Log 7; X50).

`declare.py amend-fit` writes Decision Log 7's five rulings into part 2 as a content diff. These
cases hold what that diff may be: the five rulings' operations are accepted, revert to the
superseded part 2 byte for byte (`443f494c…`), and leave a body that is still the draft's valid
diff; an operation outside its ruling's paths (a changed prediction, a widened grid), an unknown
ruling, a removal, a path touched twice and a missing ruling are refused; the verb refuses once a
fit render exists and a second time; part 1 accepts a moved pin of `declare.py` only when the
amendment records exactly that move. `declare.py check-fit` runs this file.

    python3.12 -B -m unittest test_amend_fit -v      (from this directory)
"""
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import declare as D  # noqa: E402

SUPERSEDED = "443f494c94fc66d8adf41932ca0d533600676e9295c7f9f69a9785fb565685d2"
FILE = D.PARTS["fit"]["declaration"].read_bytes()
FIT = json.loads(FILE)
RECORD = D.amendments("fit")
PRE = D.revert_ops(FIT, RECORD[0]["ops"]) if RECORD else FIT


def ops():
    return D.amendment_one(PRE)


def refused(test, operations):
    with test.assertRaises(D.Refusal):
        D.validate_ops(operations)


class Accepts(unittest.TestCase):
    def test_the_superseded_part_2_is_rebuilt(self):
        self.assertEqual(hashlib.sha256(D.serialise(PRE)).hexdigest(), SUPERSEDED)

    def test_the_five_rulings(self):
        got = ops()
        D.validate_ops(got)
        self.assertEqual(sorted({o["ruling"] for o in got}), [1, 2, 3, 4, 5])
        amended = D.apply_ops(PRE, got)
        self.assertEqual(D.revert_ops(amended, got), PRE)

    def test_the_recorded_amendment_is_the_file(self):
        if not RECORD:
            self.skipTest("part 2 is not amended yet")
        self.assertEqual(D.serialise(D.apply_ops(PRE, RECORD[0]["ops"])), FILE)
        D.validate_ops(RECORD[0]["ops"])

    def test_the_reverted_body_is_the_drafts_valid_diff(self):
        D.validate_fit(json.loads(D.DRAFT.read_text()), PRE, json.loads(D.RESULTS.read_text()),
                       json.loads(D.PROTOCOL.read_text()))

    def test_nothing_but_the_rulings_moves(self):
        amended = D.apply_ops(PRE, ops())
        for key in set(PRE) | set(amended):
            if PRE.get(key) != amended.get(key):
                self.assertIn(key, {"moves", "landingRule", "fitCells", "strata", "textStratum",
                                    "candidateIdentity", "sources"}, key)
        for name in ("searchProcedure", "selectionRule", "interactions", "notCandidates", "rehearsed",
                     "permittedChanges", "references", "changes"):
            self.assertEqual(PRE[name], amended[name], name)
        for i, move in enumerate(PRE["moves"]):
            for fam, body in move["families"].items():
                self.assertEqual(body.get("prediction"), amended["moves"][i]["families"][fam].get("prediction"))
                for leaf, spec in body.get("leaves", {}).items():
                    self.assertEqual(spec, amended["moves"][i]["families"][fam]["leaves"][leaf])
        self.assertEqual(sorted(PRE["sources"]), sorted(k for k in amended["sources"] if k in PRE["sources"]))


class Refuses(unittest.TestCase):
    def test_an_unknown_ruling(self):
        got = ops()
        got[0] = dict(got[0], ruling=6)
        refused(self, got)

    def test_a_changed_prediction(self):
        got = ops() + [dict(ruling=1, kind="replace", path=["moves", 0, "families", "A", "prediction"],
                            **{"from": PRE["moves"][0]["families"]["A"]["prediction"]}, to="A is within")]
        refused(self, got)

    def test_a_widened_grid(self):
        grid = PRE["moves"][0]["families"]["B"]["leaves"]["sizeHeavyTapSigma2x"]["grid"]
        got = ops() + [dict(ruling=3, kind="replace",
                            path=["moves", 0, "families", "B", "leaves", "sizeHeavyTapSigma2x", "grid"],
                            **{"from": grid}, to=[4] + grid)]
        refused(self, got)

    def test_a_path_under_another_ruling(self):
        got = ops()
        i = next(i for i, o in enumerate(got) if o["path"] == ["moves", 0, "withinClause"])
        got[i] = dict(got[i], ruling=4)
        refused(self, got)

    def test_a_removal(self):
        got = ops()
        got[0] = dict(got[0], kind="remove")
        refused(self, got)

    def test_a_missing_ruling(self):
        refused(self, [o for o in ops() if o["ruling"] != 4])

    def test_a_path_touched_twice(self):
        got = ops()
        refused(self, got + [got[-1]])

    def test_an_add_stating_a_from(self):
        got = ops()
        i = next(i for i, o in enumerate(got) if o["kind"] == "add")
        got[i] = dict(got[i], **{"from": None})
        refused(self, got)

    def test_a_replace_whose_from_is_not_in_place(self):
        got = ops()
        i = next(i for i, o in enumerate(got) if o["kind"] == "replace")
        got[i] = dict(got[i], **{"from": "something else"})
        with self.assertRaises(D.Refusal):
            D.apply_ops(PRE, got)

    def test_a_revert_whose_to_is_not_in_place(self):
        with self.assertRaises(D.Refusal):
            D.revert_ops(PRE, ops())


class TheVerb(unittest.TestCase):
    def test_fit_evidence_is_a_render_not_the_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            g1, scratch = Path(tmp) / "g1", Path(tmp) / "scratch"
            (g1 / "fit").mkdir(parents=True)
            scratch.mkdir()
            with mock.patch.object(D, "G1", g1), mock.patch.object(D, "G1_SCRATCH", scratch), \
                    mock.patch.object(D, "ROOT", Path(tmp)):
                self.assertEqual(D.fit_evidence(), [])
                (g1 / "fit" / "runs.jsonl").write_text('{"label": "x", "started": "now"}\n')
                self.assertEqual(len(D.fit_evidence()), 1)
                (g1 / "fit" / "runs.jsonl").unlink()
                (scratch / "c1").mkdir()
                (scratch / "c1" / "matrix.json").write_text("{}")
                self.assertEqual(len(D.fit_evidence()), 1)

    def test_refused_once_a_fit_render_exists(self):
        before = (D.PARTS["fit"]["declaration"].read_bytes(), D.PARTS["fit"]["digest"].read_bytes())
        with mock.patch.object(D, "fit_evidence", lambda: ["fit/runs.jsonl"]):
            self.assertEqual(D.amend_fit(["--reason", "r", "--cause", "ea487a17"]), 2)
        self.assertEqual(before, (D.PARTS["fit"]["declaration"].read_bytes(),
                                  D.PARTS["fit"]["digest"].read_bytes()))

    def test_refused_a_second_time(self):
        with mock.patch.object(D, "fit_evidence", lambda: []), \
                mock.patch.object(D, "amendments", lambda part: [{"n": 1}] if part == "fit" else []):
            self.assertEqual(D.amend_fit(["--reason", "r", "--cause", "ea487a17"]), 2)


class PartOneRepin(unittest.TestCase):
    KEY = D.PART_ONE_REPINNABLE[0]

    def test_this_file_exactly_as_recorded(self):
        self.assertTrue(D.accepted_repin(self.KEY, "a", "b", {self.KEY: {"from": "a", "to": "b"}}))

    def test_not_another_file_even_recorded(self):
        other = f"{D.REL}/cuts/t1.py"
        self.assertFalse(D.accepted_repin(other, "a", "b", {other: {"from": "a", "to": "b"}}))

    def test_not_from_another_hash_or_to_other_bytes(self):
        self.assertFalse(D.accepted_repin(self.KEY, "a", "b", {self.KEY: {"from": "x", "to": "b"}}))
        self.assertFalse(D.accepted_repin(self.KEY, "a", "b", {self.KEY: {"from": "a", "to": "x"}}))
        self.assertFalse(D.accepted_repin(self.KEY, "a", "b", {}))


if __name__ == "__main__":
    unittest.main()
