#!/usr/bin/env python3.12
"""W45 G0 (b): declare.py's red cases (charter clause 2; X58).

W45's declaration tool refuses W44's bindings, refuses an amendment once render evidence exists,
and holds part 2 to the draft changed only by the protocol's decisions where the ladder results
support them; part 2's second and final amendment (the charter's Decision Log 7) carries exactly its
ruled items, values included, and a third is refused for ever. Each case runs against temporary
files or in memory; nothing here writes the real declaration.

    cd packages/calibration/results/2026-10-03-w45-g0-operator
    python3.12 -B -m unittest test_declare -v
"""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import declare as D  # noqa: E402

DRAFT = json.loads(D.DRAFT.read_text())
PROTOCOL = json.loads(D.PROTOCOL.read_text())
OP = D.OPERATOR


def results(**ladders):
    base = {"i": {"struck": [], "nonFlatRange": {OP: [-1, 0]}},
            "ii": {"met": ["ii-0.5-2--0.5"]},
            "iii": {"struck": [], "nonFlatRange": {"sizeScatterSpanMax2x": [112, 160]}},
            "iv": {"struck": [], "nonFlatRange": {"sizeScatterRampStartThick2x+sizeScatterRampStartFar2x": [0.05, 0.21]}},
            "x48": {"inert1x": True}}
    base.update(ladders)
    return {"ladders": base}


def fit_from(draft, changes):
    body = D.apply_changes(draft, changes, results(), PROTOCOL)
    body.pop("status", None)
    return dict(body, status="test", changes=changes, sources={}, fromDraft={})


class Bindings(unittest.TestCase):
    def temp_part(self, body: dict | None = None, digest: str | None = None):
        root = Path(tempfile.mkdtemp(prefix="w45-declare-"))
        part = dict(D.PARTS["protocol"], declaration=root / "declaration.json", digest=root / "declaration.sha256")
        if body is not None:
            part["declaration"].write_text(json.dumps(body))
        if digest is not None:
            part["digest"].write_text(f"{digest}  declaration.json\n")
        return {"protocol": part, "fit": dict(D.PARTS["fit"], declaration=root / "none.json", digest=root / "none.sha256")}

    def test_a_declaration_naming_w44s_charter(self):
        parts = self.temp_part({"schema": "w45-declaration-1",
                                "charter": "docs/doperpowers/specs/2026-10-03-w44-texture-at-0-25.md@0ee27ae2"})
        with mock.patch.object(D, "PARTS", parts), self.assertRaisesRegex(D.Refusal, "W44's charter"):
            D.bindings()

    def test_a_declaration_in_w44s_schema(self):
        parts = self.temp_part({"schema": "w44-declaration-1", "charter": D.CHARTER_PIN})
        with mock.patch.object(D, "PARTS", parts), self.assertRaisesRegex(D.Refusal, "W44's schema"):
            D.bindings()

    def test_a_digest_carrying_w44s_part_hash(self):
        w44 = sorted(D.W44_PART_HASHES)[0]
        parts = self.temp_part({"schema": "w45-declaration-1", "charter": D.CHARTER_PIN}, digest=w44)
        with mock.patch.object(D, "PARTS", parts), self.assertRaisesRegex(D.Refusal, "W44's part hash"):
            D.bindings()

    def test_w44s_scratch_as_the_ladder_scratch(self):
        with mock.patch.object(D, "LADDER_SCRATCH", Path.home() / "vitrea-w44" / "g0-ladders"), \
                self.assertRaisesRegex(D.Refusal, "X58"):
            D.bindings()

    def test_w44s_evidence_as_the_fit_directory(self):
        with mock.patch.object(D, "G1", D.W44_G1), self.assertRaisesRegex(D.Refusal, "X58"):
            D.bindings()

    def test_w45s_own_bindings_pass(self):
        D.bindings()


class Evidence(unittest.TestCase):
    def test_amend_refuses_before_the_hash(self):
        root = Path(tempfile.mkdtemp(prefix="w45-declare-"))
        parts = copy.deepcopy(D.PARTS)
        parts["protocol"]["digest"] = root / "absent.sha256"
        with mock.patch.object(D, "PARTS", parts):
            self.assertEqual(D.amend("protocol", ["--reason", "r", "--cause", "c", "x"]), 2)

    def test_amend_refuses_once_a_ladder_render_exists(self):
        root = Path(tempfile.mkdtemp(prefix="w45-declare-"))
        runs = root / "runs.jsonl"
        runs.write_text(json.dumps({"label": "c05-control/x", "started": "now"}) + "\n")
        digest = root / "declaration.sha256"
        digest.write_text("0" * 64 + "  declaration.json\n")
        parts = copy.deepcopy(D.PARTS)
        parts["protocol"]["digest"] = digest
        with mock.patch.object(D, "PARTS", parts), mock.patch.object(D, "LADDER_RUNS", runs):
            self.assertTrue(D.ladder_evidence())
            self.assertEqual(D.amend("protocol", ["--reason", "r", "--cause", "c", "x"]), 2)

    def test_amend_fit_refuses_once_a_fit_render_exists(self):
        root = Path(tempfile.mkdtemp(prefix="w45-declare-"))
        runs = root / "runs.jsonl"
        runs.write_text(json.dumps({"label": "s1/x", "started": "now"}) + "\n")
        digest = root / "fit-declaration.sha256"
        digest.write_text("0" * 64 + "  fit-declaration.json\n")
        parts = copy.deepcopy(D.PARTS)
        parts["fit"]["digest"] = digest
        with mock.patch.object(D, "PARTS", parts), mock.patch.object(D, "FIT_RUNS", runs):
            self.assertTrue(D.fit_evidence())
            self.assertEqual(D.amend("fit", ["--reason", "r", "--cause", "c", "x"]), 2)


class PartOneRecord(unittest.TestCase):
    """Part 2's one amendment may re-pin a few part-1 sources and read the light 0.25 documents at a
    commit; part 1's check accepts exactly what the record names (the review of G0 (b)-(e))."""
    KEY = f"{D.REL}/cuts/rule.py"

    def test_a_recorded_move_of_a_repinnable_source_is_accepted(self):
        with mock.patch.object(D, "part_one_record", return_value=({self.KEY: {"from": "a", "to": "b"}}, {})):
            self.assertTrue(D.accepted_repin(self.KEY, "a", "b"))
            self.assertFalse(D.accepted_repin(self.KEY, "a", "c"))      # moved again since the record
            self.assertFalse(D.accepted_repin(self.KEY, "z", "b"))      # not from the pinned bytes

    def test_a_source_outside_the_repinnable_set_is_never_accepted(self):
        other = f"{D.REL}/cuts/cuts.py"
        with mock.patch.object(D, "part_one_record", return_value=({other: {"from": "a", "to": "b"}}, {})):
            self.assertFalse(D.accepted_repin(other, "a", "b"))

    def test_a_read_at_source_is_read_at_its_commit(self):
        key = D.PART_ONE_READ_AT_ADMISSIBLE[0]
        with mock.patch.object(D, "part_one_record", return_value=({}, {key: "c152b89b"})), \
                mock.patch.object(D, "git_show", return_value=b"at-commit") as show:
            self.assertEqual(D.source_bytes(key), b"at-commit")
            show.assert_called_once_with(key, "c152b89b")
            self.assertNotEqual(D.source_bytes(key, live=True), b"at-commit")

    def record(self, entry: dict):
        root = Path(tempfile.mkdtemp(prefix="w45-declare-"))
        path = root / "fit-amendments.json"
        path.write_text(json.dumps({"amendments": [entry]}))
        parts = copy.deepcopy(D.PARTS)
        parts["fit"]["amendments"] = path
        return mock.patch.object(D, "PARTS", parts)

    def test_a_read_at_entry_for_any_other_source_is_refused_by_the_checker(self):
        bed = f"{D.REL}/cuts/bed.py"
        with self.record({"partOneReadAt": {bed: "f33d3e59"}}):
            self.assertEqual(D.part_one_record()[1], {})                 # never re-routes the read
            self.assertTrue(any("cuts/bed.py" in f for f in D.part_one_record_failures()))

    def test_a_repin_of_any_other_source_is_refused_by_the_checker(self):
        cuts = f"{D.REL}/cuts/cuts.py"
        with self.record({"partOnePins": {cuts: {"from": "a", "to": "b"}}}):
            self.assertEqual(D.part_one_record()[0], {})
            self.assertTrue(any("cuts/cuts.py" in f for f in D.part_one_record_failures()))

    def test_a_read_at_commit_whose_bytes_are_not_the_pin_is_refused(self):
        key = D.PART_ONE_READ_AT_ADMISSIBLE[0]
        with self.record({"partOneReadAt": {key: "c152b89b"}}), \
                mock.patch.object(D, "git_show", return_value=b"other bytes"):
            self.assertTrue(any("not part 1's pin" in f for f in D.part_one_record_failures()))

    def test_the_count_floor(self):
        self.assertTrue(D.ran_at_least("...\nRan 15 tests in 0.004s\n", 14))
        self.assertFalse(D.ran_at_least("...\nRan 13 tests in 0.004s\n", 14))
        self.assertFalse(D.ran_at_least("no summary", 1))


class SecondAmendment(unittest.TestCase):
    """Part 2's second and final amendment (G1 step 0; the charter's Decision Log 7): accepted once,
    under the ruling's commit, with exactly the ruled items, values included; never a third."""
    FIT = f"{D.REL}/fit/fit.py"
    SEAL = f"{D.REL}/seal/seal.ts"

    def before(self):
        """Part 2's body before the second amendment, whether or not it has been written."""
        fit = json.loads(D.PARTS["fit"]["declaration"].read_text())
        record = D.amendments("fit")
        return D.revert_ops(fit, record[1]["ops"]) if len(record) >= 2 else fit

    def entry(self):
        return {"cause": D.RULING_COMMIT, "ops": D.amendment_two(self.before()),
                "pins": {self.FIT: {"from": "a", "to": "b", "rulings": [1, 2]},
                         self.SEAL: {"from": "c", "to": "d", "rulings": [6]}},
                "partOnePins": {f"{D.REL}/declare.py": {"from": "e", "to": "f", "rulings": [1]}}}

    def refused(self, entry, needle):
        with self.assertRaisesRegex(D.Refusal, needle):
            D.validate_two(entry)

    def test_the_ruled_entry_validates(self):
        D.validate_two(self.entry())
        self.assertEqual(sorted({op["ruling"] for op in self.entry()["ops"]}), [2, 3, 6])

    def test_a_third_amendment_is_refused_for_ever(self):
        with mock.patch.object(D, "amendments", lambda part: [{"n": 1}, {"n": 2}]):
            self.assertEqual(D.amend_fit(["--reason", "r", "--cause", D.RULING_COMMIT]), 2)

    def test_the_second_amendment_only_under_the_ruling_commit(self):
        with mock.patch.object(D, "amendments", lambda part: [{"n": 1}]), \
                mock.patch.object(D, "fit_evidence", lambda: []), \
                mock.patch.object(D, "check_fit", side_effect=AssertionError("refused before any check")):
            self.assertEqual(D.amend_fit(["--reason", "r", "--cause", "c152b89b"]), 2)

    def test_the_second_amendment_refuses_once_a_fit_render_exists(self):
        with mock.patch.object(D, "amendments", lambda part: [{"n": 1}]), \
                mock.patch.object(D, "fit_evidence", lambda: ["fit/runs.jsonl"]):
            self.assertEqual(D.amend_fit(["--reason", "r", "--cause", D.RULING_COMMIT]), 2)

    def test_an_unknown_ruling(self):
        e = self.entry()
        e["ops"][0]["ruling"] = 4
        self.refused(e, "not one of Decision Log 7's")

    def test_an_op_at_a_path_its_ruling_does_not_change(self):
        e = self.entry()
        factorial = next(op for op in e["ops"] if op["ruling"] == 3)
        factorial["path"] = list(D.DELTA_ACTIVE)
        self.refused(e, "not a path ruling 3 changes")
        e = self.entry()
        e["ops"].append(dict(ruling=2, kind="replace", path=["moves", 0, "withinClause"], **{"from": "x"}, to="y"))
        self.refused(e, "not a path ruling 2 changes")

    def test_a_path_touched_twice_and_a_removal(self):
        e = self.entry()
        e["ops"].append(dict(e["ops"][0]))
        self.refused(e, "touched twice")
        e = self.entry()
        e["ops"][0]["kind"] = "remove"
        self.refused(e, "not an add or a replace")

    def test_a_ruling_with_nothing_executed(self):
        e = self.entry()
        e["ops"] = [op for op in e["ops"] if op["ruling"] != 3]
        self.refused(e, r"rulings \[3\] carry nothing")
        e = self.entry()
        e["pins"] = {}
        e["partOnePins"] = {}
        self.refused(e, r"rulings \[1\] carry nothing")

    def test_a_pin_no_ruling_moves(self):
        e = self.entry()
        e["pins"][f"{D.REL}/cuts/cuts.py"] = {"from": "a", "to": "b", "rulings": [1]}
        self.refused(e, "no ruling of Decision Log 7 among them moves it")
        e = self.entry()
        e["pins"][self.SEAL]["rulings"] = [2]
        self.refused(e, "no ruling of Decision Log 7 among them moves it")
        e = self.entry()
        e["partOnePins"][f"{D.REL}/cuts/rule.py"] = {"from": "a", "to": "b", "rulings": [1]}
        self.refused(e, "no ruling of Decision Log 7 among them moves it")

    def test_an_authorised_path_with_another_value_fails_the_value_check(self):
        fit = D.apply_ops(self.before(), self.entry()["ops"])
        failures, before = D.amendment_two_failures(fit, self.entry())
        self.assertEqual(failures, [])
        self.assertEqual(before, self.before())
        e = self.entry()
        factorial = next(op for op in e["ops"] if op["ruling"] == 3)
        factorial["to"] = [dict(factorial["to"][0], points=36)]
        failures, _ = D.amendment_two_failures(D.apply_ops(self.before(), e["ops"]), e)
        self.assertTrue(any("values included" in f for f in failures), failures)

    def test_another_cause_fails_the_check(self):
        e = dict(self.entry(), cause="c152b89b")
        failures, _ = D.amendment_two_failures(D.apply_ops(self.before(), e["ops"]), e)
        self.assertTrue(any("not the ruling's commit" in f for f in failures), failures)
        self.assertTrue(any("carries no Decision Log 7" in f for f in failures), failures)

    def test_a_part_one_pin_moved_twice_is_accepted_only_along_its_chain(self):
        key = f"{D.REL}/declare.py"
        root = Path(tempfile.mkdtemp(prefix="w45-declare-"))
        (root / "declaration.json").write_text(json.dumps({"sources": {}}))
        parts = copy.deepcopy(D.PARTS)
        parts["protocol"]["declaration"] = root / "declaration.json"
        two = [{"partOnePins": {key: {"from": "a", "to": "b"}}}, {"partOnePins": {key: {"from": "b", "to": "c"}}}]
        with mock.patch.object(D, "amendments", lambda part: two), mock.patch.object(D, "PARTS", parts):
            self.assertTrue(D.accepted_repin(key, "a", "c"))
            self.assertFalse(D.accepted_repin(key, "a", "b"))
            self.assertEqual(D.part_one_record_failures(), [])
        broken = [{"partOnePins": {key: {"from": "a", "to": "b"}}}, {"partOnePins": {key: {"from": "x", "to": "c"}}}]
        with mock.patch.object(D, "amendments", lambda part: broken), mock.patch.object(D, "PARTS", parts):
            self.assertFalse(D.accepted_repin(key, "a", "c"))
            self.assertFalse(D.accepted_repin(key, "x", "c"))
            self.assertTrue(any("chain that breaks" in f for f in D.part_one_record_failures()))


class ValidatedDiff(unittest.TestCase):
    def refused(self, fit, res=None, needle=""):
        with self.assertRaisesRegex(D.Refusal, needle):
            D.validate_fit(DRAFT, fit, res or results(), PROTOCOL)

    def test_the_draft_unchanged_validates(self):
        D.validate_fit(DRAFT, fit_from(DRAFT, []), results(), PROTOCOL)

    def test_a_supported_strike_validates(self):
        res = results(i={"struck": [OP], "nonFlatRange": {OP: None}})
        change = {"kind": "strike", "ladder": "i", "move": "stage1", "family": "deep", "leaf": OP}
        body = D.apply_changes(DRAFT, [change], res, PROTOCOL)
        body.pop("status", None)
        D.validate_fit(DRAFT, dict(body, changes=[change]), res, PROTOCOL)

    def test_a_strike_the_ladder_did_not_make(self):
        fit = fit_from(DRAFT, [])
        fit["changes"] = [{"kind": "strike", "ladder": "i", "move": "stage1", "family": "deep", "leaf": OP}]
        self.refused(fit, needle="did not strike")

    def test_a_strike_from_a_ladder_that_decides_no_strike(self):
        fit = fit_from(DRAFT, [])
        fit["changes"] = [{"kind": "strike", "ladder": "ii", "move": "stage1", "family": "deep", "leaf": "sizeHeavySecondShare"}]
        self.refused(fit, res=results(ii={"struck": ["sizeHeavySecondShare"]}), needle="does not let")

    def test_a_narrowing_outside_the_non_flat_range(self):
        fit = fit_from(DRAFT, [])
        fit["changes"] = [{"kind": "narrow", "ladder": "iii", "move": "stage1", "family": "deep", "leaf": "sizeScatterSpanMax2x",
                           "grid": [192, 256]}]
        self.refused(fit, needle="non-flat range")

    def test_a_widened_grid(self):
        fit = fit_from(DRAFT, [])
        fit["moves"][0]["families"]["deep"]["leaves"][OP]["grid"] = [0, -0.25, -0.5, -0.75, -1, -1.25]
        self.refused(fit, needle="beyond its permitted changes")

    def test_a_new_leaf(self):
        fit = fit_from(DRAFT, [])
        fit["moves"][0]["families"]["deep"]["leaves"]["sizeScatterHeavyShareThick2x"] = {"slot": "active.light", "unit": "x",
                                                                      "domain": [0, 1], "grid": [0, 0.1]}
        self.refused(fit, needle="beyond its permitted changes")

    def test_a_changed_prediction(self):
        fit = fit_from(DRAFT, [])
        fit["moves"][0]["families"]["deep"]["prediction"] = "anything else"
        self.refused(fit, needle="beyond its permitted changes")

    def test_an_inert_setting_without_x48(self):
        fit = fit_from(DRAFT, [])
        fit["changes"] = [{"kind": "inert", "ladder": "x48"}]
        self.refused(fit, res=results(x48={"inert1x": False}), needle="X48")

    def test_a_change_of_no_declared_kind(self):
        fit = fit_from(DRAFT, [])
        fit["changes"] = [{"kind": "replace", "ladder": "i", "move": "stage1", "family": "deep", "leaf": OP}]
        self.refused(fit, needle="does not let")


if __name__ == "__main__":
    unittest.main()
