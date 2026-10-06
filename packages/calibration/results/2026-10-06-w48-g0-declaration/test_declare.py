"""W48 G0 (b): W48's `declare.py`, what it changes from W47's (charter Decision Log 3 (c)-(g); X72, X73): the
`hold` decision beside `strike`, no precedence kind, `check-fit` reading `verdicts.json`, the off-grid values,
empty ops refused. Synthetic verdicts and change lists only; the draft and protocol are W48's own files.

    python3.12 -B -m unittest -v test_declare      (from this directory)
"""
from __future__ import annotations

import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import inherit  # noqa: E402

D = inherit.own("declare.py", "w48_declare")
W = inherit.W
DRAFT = json.loads(D.DRAFT.read_text())
PROTOCOL = json.loads(D.PROTOCOL.read_text())


def verdicts(op1=True, tap=True, width=True, unruled=(), passing=("i-a0.7", "i-a0.8")):
    """A synthetic verdicts.json body: which readings separate at both scales."""
    return dict(schema="w48-verdicts-1",
                operators={"operator 1": dict(separates=op1, rungs=["i-a0.7-f0.2-t128"] if op1 else []),
                           "operator 2": dict(separates=tap, rungs=["iii-s4"] if tap else [], bodyWidthMeets=width,
                                              bodyRungs=["iii-b4"] if width else []),
                           "2x width": dict(meets=False, rungs=[], complete=True),
                           "joint": dict(meets=True)},
                ladders={"i": dict(complete=True, passingL1=list(passing)), "iii": dict(complete=True)},
                oneScale=dict(rungs=["iii-s2", "iii-q0.5", *unruled], unruled=list(unruled)),
                flat={})


def fit_of(changes):
    body = D.apply_changes(DRAFT, changes, verdicts(), PROTOCOL)
    return dict(body, changes=changes)


class DecisionKinds(unittest.TestCase):
    def test_hold_is_a_kind_and_no_precedence_kind_exists(self):
        self.assertIn("hold", D.CHANGE_KINDS)
        self.assertNotIn("body-width-first", D.CHANGE_KINDS)
        self.assertNotIn("body-width-first", PROTOCOL["decisions"])
        self.assertEqual(PROTOCOL["decisionKinds"]["changes"], list(D.CHANGE_KINDS))

    def test_a_precedence_change_is_refused(self):
        with self.assertRaises(D.Refusal):
            D.apply_changes(DRAFT, [dict(kind="body-width-first", ladder="iii", operator="operator 2", reading="x")],
                            verdicts(), PROTOCOL)


GAIN = dict(kind="hold", ladder="i", move="stage1", family="span-law", leaf="sizeOcclusionGain", value=0.05,
            ruling="Decision Log 3", charterCommit=W.CHARTER_COMMIT)


class Hold(unittest.TestCase):
    def test_a_hold_moves_the_leaf_to_fixed_at_its_value(self):
        body = D.apply_changes(DRAFT, [GAIN], verdicts(), PROTOCOL)
        fam = next(m for m in body["moves"] if m["id"] == "stage1")["families"]["span-law"]
        self.assertNotIn("sizeOcclusionGain", fam["leaves"])
        self.assertEqual(fam["fixed"]["sizeOcclusionGain"]["value"], 0.05)
        self.assertEqual(fam["fixed"]["sizeOcclusionGain"]["slot"], "active.dark")
        self.assertNotIn("sizeOcclusionGain", fam["factorialGroups"][0]["keys"])
        self.assertEqual(D.mandatory_failures(body, verdicts(), PROTOCOL), [])

    def test_a_hold_off_its_declared_values_is_refused(self):
        with self.assertRaisesRegex(D.Refusal, "holdable"):
            D.apply_changes(DRAFT, [dict(GAIN, value=0.2)], verdicts(), PROTOCOL)

    def test_a_hold_without_a_ruling_or_with_one_not_naming_the_leaf_is_refused(self):
        with self.assertRaisesRegex(D.Refusal, "names the parent's ruling"):
            D.apply_changes(DRAFT, [{k: v for k, v in GAIN.items() if k != "ruling"}], verdicts(), PROTOCOL)
        with self.assertRaisesRegex(D.Refusal, "does not name"):
            D.apply_changes(DRAFT, [dict(GAIN, ruling="Decision Log 1")], verdicts(), PROTOCOL)

    def test_an_operator_leaf_is_never_held(self):
        with self.assertRaisesRegex(D.Refusal, "operator leaf"):
            D.apply_changes(DRAFT, [dict(GAIN, leaf="tintAlphaFar1x", value=0.2)], verdicts(), PROTOCOL)

    def test_a_leaf_the_draft_does_not_mark_holdable_is_refused(self):
        with self.assertRaisesRegex(D.Refusal, "holdable"):
            D.apply_changes(DRAFT, [dict(GAIN, family="rest-scatter", leaf="sizeScatterFloor", value=0.34)],
                            verdicts(), PROTOCOL)


class CheckFitReadsTheVerdicts(unittest.TestCase):
    def test_the_draft_unchanged_validates_when_everything_separates(self):
        D.validate_fit(DRAFT, fit_of([]), verdicts(), PROTOCOL)

    def test_both_levers_meeting_stay_members(self):
        body = D.apply_changes(DRAFT, [], verdicts(), PROTOCOL)
        self.assertTrue(D.body_width_leaves(body) and D.operator_leaves(body, "operator 2"))
        with self.assertRaisesRegex(D.Refusal, "a body-width rung meets"):
            D.apply_changes(DRAFT, [dict(kind="strike", ladder="iii", move="stage2", family="transmission-fine-term",
                                         leaf="optics.regular.blurSigma")], verdicts(), PROTOCOL)

    def test_the_body_width_must_leave_when_no_body_width_rung_meets(self):
        v = verdicts(width=False)
        fails = D.mandatory_failures(D.apply_changes(DRAFT, [], v, PROTOCOL), v, PROTOCOL)
        self.assertTrue(any("body width is searched" in f for f in fails))
        strike = dict(kind="strike", ladder="iii", move="stage2", family="transmission-fine-term",
                      leaf="optics.regular.blurSigma")
        self.assertEqual(D.mandatory_failures(D.apply_changes(DRAFT, [strike], v, PROTOCOL), v, PROTOCOL), [])

    def test_an_operator_not_separating_must_be_named_and_its_leaves_leave(self):
        v = verdicts(op1=False)
        fails = D.mandatory_failures(D.apply_changes(DRAFT, [], v, PROTOCOL), v, PROTOCOL)
        self.assertTrue(any("operator 1 does not separate" in f for f in fails))
        named = dict(kind="name-unfitted", ladder="i", operator="operator 1", reading="no rung at both scales")
        body = D.apply_changes(DRAFT, [named], v, PROTOCOL)
        self.assertEqual(D.mandatory_failures(body, v, PROTOCOL), [])
        with self.assertRaisesRegex(D.Refusal, "separating"):
            D.apply_changes(DRAFT, [named], verdicts(), PROTOCOL)

    def test_neither_operator_separating_stops(self):
        v = verdicts(op1=False, tap=False, width=False)
        fails = D.mandatory_failures(D.apply_changes(DRAFT, [], v, PROTOCOL), v, PROTOCOL)
        self.assertTrue(any("neither operator separates" in f for f in fails))

    def test_an_unruled_one_scale_rung_on_a_grid_stops_part_two(self):
        v = verdicts(unruled=("iii-s6",))
        v["rungs"] = {"iii-s6": dict(overrides={"receded.dark": {"sizeFineTapSigma": 6, "sizeFineTapSigma2x": 6,
                                                                 "sizeFineTapShare": 1}})}
        fails = D.mandatory_failures(D.apply_changes(DRAFT, [], v, PROTOCOL), v, PROTOCOL)
        self.assertTrue(any("one scale only" in f for f in fails))
        del v["rungs"]
        fails = D.mandatory_failures(D.apply_changes(DRAFT, [], v, PROTOCOL), v, PROTOCOL)
        self.assertTrue(any("one scale only" in f for f in fails), "a rung with no recorded point still stops")

    def test_an_unruled_one_scale_rung_on_no_grid_is_recorded(self):
        """W48 Decision Log 8: i-a0.8-g0.6's point (far 0, top 256) is on no W48 grid."""
        v = verdicts(unruled=("i-a0.8-g0.6",))
        v["rungs"] = {"i-a0.8-g0.6": dict(overrides={"active.dark": {"optics.regular.tintAlpha": 0.8,
                                                                     "sizeOcclusionGain": 0.6}})}
        body = D.apply_changes(DRAFT, [], v, PROTOCOL)
        self.assertEqual(D.mandatory_failures(body, v, PROTOCOL), [])
        self.assertEqual(D.one_scale_reading(body, v), ([], ["i-a0.8-g0.6"]))
        on = dict(v, rungs={"i-a0.8-g0.6": dict(overrides={"active.dark": {
            "optics.regular.tintAlpha": 0.8, "sizeOcclusionGain": 0.6, "tintAlphaFar1x": 0.2, "tintAlphaFar2x": 0.2,
            "sizeScatterSpanMax": 128, "sizeScatterSpanMax2x": 128}})})
        self.assertEqual(D.one_scale_reading(body, on), (["i-a0.8-g0.6"], []))

    def test_an_off_grid_value_on_a_grid_fails(self):
        body = json.loads(json.dumps(DRAFT))
        leaf = next(m for m in body["moves"] if m["id"] == "stage2")["families"]["transmission-fine-term"]["leaves"]
        leaf["sizeFineTapShare"]["grid"] = [0, 0.5, 0.75, 1]
        self.assertTrue(any("off the grid" in f for f in D.mandatory_failures(body, verdicts(), PROTOCOL)))
        self.assertTrue(any("off the grid" in f for f in D.draft_failures(body, PROTOCOL, ["P", "C rest", "F inactive"])))

    def test_part_two_beyond_its_changes_is_refused(self):
        fit = fit_of([])
        next(m for m in fit["moves"] if m["id"] == "stage1")["families"]["span-law"]["leaves"]["tintAlphaFar1x"]["grid"] = [0.2]
        with self.assertRaisesRegex(D.Refusal, "beyond its permitted changes"):
            D.validate_fit(DRAFT, fit, verdicts(), PROTOCOL)

    def test_the_verdicts_must_name_part_one_and_its_pins(self):
        part1 = dict(sources={})
        got = D.verdict_failures(dict(verdicts(), declarationSha256="a" * 64, inputs={}), part1, "b" * 64)
        self.assertTrue(any("current hash" in f for f in got))
        self.assertTrue(any("does not pin" in f for f in got))

    def test_check_fit_refuses_without_the_verdicts(self):
        c, _ = D.check_fit()
        if not D.VERDICTS.exists():
            self.assertTrue(any("verdicts" in f or "not hashed" in f for f in c.failures))


class EmptyOps(unittest.TestCase):
    def test_amend_and_amend_fit_refuse_an_empty_ops_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            ops = Path(tmp) / "ops.json"
            ops.write_text("[]")
            for part in ("protocol", "fit"):
                out = io.StringIO()
                with redirect_stdout(out):
                    rc = D.amend(part, ["--reason", "r", "--cause", "c", "--ruling", "Decision Log 3",
                                        "--charter-commit", W.CHARTER_COMMIT, "--ops", str(ops)])
                self.assertEqual(rc, 2)
                self.assertIn("empty", out.getvalue())

    def test_a_recorded_empty_ops_list_fails_on_read(self):
        a = dict(ruling="### Decision Log 3 x\n", charter=f"{W.CHARTER_PATH}@{W.CHARTER_COMMIT}", ops=[])
        self.assertTrue(any("empty ops" in f for f in D.content_failures("amendments.json", 1, a)))


class Draft(unittest.TestCase):
    def test_the_draft_is_well_formed(self):
        self.assertEqual(D.draft_failures(DRAFT, PROTOCOL, ["P", "C rest", "F inactive"]), [])

    def test_a_conditional_leaf_and_the_second_tap_fail(self):
        body = json.loads(json.dumps(DRAFT))
        law = next(m for m in body["moves"] if m["id"] == "stage1")["families"]["span-law"]
        law["leaves"]["tintAlphaFar1x"]["conditional"] = "ii"
        law.setdefault("fixed", {})["sizeHeavySecondSigma"] = dict(slot="active.dark", value=0)
        got = D.draft_failures(body, PROTOCOL, ["P", "C rest", "F inactive"])
        self.assertTrue(any("conditional" in f for f in got))
        self.assertTrue(any("second tap" in f for f in got))

    def test_holdable_only_where_decision_log_3_names_it(self):
        body = json.loads(json.dumps(DRAFT))
        rest = next(m for m in body["moves"] if m["id"] == "stage1")["families"]["rest-scatter"]
        rest["leaves"]["sizeScatterFloor"]["holdable"] = dict(values=[0.34])
        self.assertTrue(any("holdable" in f for f in D.draft_failures(body, PROTOCOL, ["P", "C rest", "F inactive"])))

    def test_the_stage_two_factorial_must_cross_the_body_width(self):
        body = json.loads(json.dumps(DRAFT))
        fam = next(m for m in body["moves"] if m["id"] == "stage2")["families"]["transmission-fine-term"]
        fam["factorialGroups"][0]["keys"].remove("optics.regular.blurSigma")
        self.assertTrue(any("ONE factorial" in f for f in D.draft_failures(body, PROTOCOL, ["P", "C rest", "F inactive"])))


class Refusals(unittest.TestCase):
    def test_w47s_part_hashes_and_paths_refuse(self):
        lines = (W.W47_G0 / "declaration.sha256").read_text().split()
        with self.assertRaises(W.Refusal):
            W.refuse_other_wave_hash(lines[0], "part 1")
        with self.assertRaises(W.Refusal):
            W.refuse_other_wave_path(W.W47_G0 / "ladders", "a ladder place")
        with self.assertRaises(W.Refusal):
            W.refuse_other_wave_path(Path.home() / "vitrea-w47" / "g0-ladders", "a scratch")
        self.assertIn("w47-", D.OTHER_SCHEMAS)


if __name__ == "__main__":
    unittest.main()
