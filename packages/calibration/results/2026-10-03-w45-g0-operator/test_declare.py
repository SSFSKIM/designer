#!/usr/bin/env python3.12
"""W45 G0 (b): declare.py's red cases (charter clause 2; X58).

W45's declaration tool refuses W44's bindings, refuses an amendment once render evidence exists,
and holds part 2 to the draft changed only by the protocol's decisions where the ladder results
support them. Each case runs against temporary files; nothing here writes the real declaration.

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
