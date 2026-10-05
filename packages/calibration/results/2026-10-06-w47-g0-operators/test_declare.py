#!/usr/bin/env python3.12
"""W47 G0 (g): declare.py's and assemble.py's red cases (charter clause 2; Decision Log 5; W46 Decision
Log 9's content-amendment form). W46's `test_declare.py`
(`results/2026-10-05-w46-g0-declaration/test_declare.py`), ported and re-bound. Nothing here writes a
part file: every case works on copies, temporary files or synthetic bodies, so it runs before part 1
exists. The synthetic draft and protocol have W47's shape (operator leaves, a multi-leaf rung, a rung
that depends on an earlier reading); the real ones are part 1's and are checked by `declare.py check`.

- **Bindings**: a declaration naming W46's (or W45's) charter or schema, and a digest file carrying a
  W46 part hash, refuse before anything is checked.
- **The amendment record, validated on read**: the pins-only form; a field outside both forms; a pin of
  a non-source; a second amendment; a wrong schema.
- **The content form** (W46 Decision Log 9's, general): the ruling must be, verbatim, the charter's
  Decision Log section at the named commit; another wave's charter, content without its ops, an op on
  the declaration's frame, `partOnePins` on part 1, a part-1 pin outside the re-pinnable list or not
  starting at part 1's pin — each refused; ops apply and revert byte for byte.
- **The chain**: a content amendment rebuilds the superseded hash; a tampered op breaks it; one
  amendment per part, final (a second `amend` refuses); partial content arguments refuse.
- **The validated diff and clause 5's outcomes**: W46's strike / narrow / name-target, and W47's
  name-operator (only an operator the ladders read as not separating, or whose body width met the bar;
  its leaves removed) and name-gap; required: an inert operator named, neither separating stops part 2.
- **Pins**: a moved source is a mismatch; a pending item and a ladder render stop the hash.
- **assemble.py**: refuses while `declaration-inputs.json` holds a TO FILL (the committed template
  does), and once part 1 is hashed.
- **The diagnostic's criterion**, the protocol's two rung forms, X67's admission and X68's domains.

    python3.12 -B -m unittest test_declare -v      (from this directory)
"""
import copy
import json
import shutil
import sys
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import declare as D  # noqa: E402

SCRATCH = HERE / ".test-scratch-declare"
CHARTER_AT = "c1f9bf84c"
W46_PART1 = "bc82562eaf1ab70a1a40ac55e00213cc4229aa3843e1659b7ad416e77f40a3aa"


def leaf(slot, grid, domain, target, ladder, unit="u"):
    return dict(slot=slot, grid=grid, domain=domain, unit=unit, target=target, ladder=ladder)


DRAFT = {
    "schema": "w47-fit-declaration-1", "references": {"dark": "d0219cd684bf", "light": "ebc3d9105a4a"},
    "landingRule": {"implementation": "cuts/rule.py (pinned by part 1)"}, "notFitted": [], "namedGaps": [],
    "moves": [
        {"id": "stage1", "slot": "active.dark", "familyOrder": ["span-law", "second-tap"], "families": {
            "span-law": {"why": "w", "leaves": {
                "optics.regular.tintAlpha": leaf("active.dark", [0.7, 0.8, 0.9], [0.7, 0.9], "P", "i-a"),
                "tintAlphaFar1x": leaf("active.dark", [0, 0.2, 0.45], [0, 0.6], "C rest", "i-f1"),
                "sizeOcclusionGain": leaf("active.dark", [0.05, 0.2, 0.4], [0.05, 0.6], "C rest", "i-g")},
                "factorialGroups": [{"keys": ["optics.regular.tintAlpha", "tintAlphaFar1x", "sizeOcclusionGain"]}]},
            "second-tap": {"why": "w", "leaves": {
                "sizeHeavySecondShareFar2x": leaf("active.dark", [0, 0.3, 0.6], [0, 1], "C rest", "ii-d")}}}},
        {"id": "stage2", "slot": "receded.dark", "familyOrder": ["fine", "transmission"], "families": {
            "fine": {"why": "w", "leaves": {
                "sizeFineTapSigma": leaf("receded.dark", [1.5, 2, 3], [0, 6], "F inactive", "iii-w"),
                "sizeFineTapShare": leaf("receded.dark", [0.5, 1], [0, 1], "F inactive", "iii-s")}},
            "transmission": {"why": "w", "leaves": {
                "optics.regular.tintAlpha": leaf("receded.dark", [0.8, 0.89], [0.8, 0.89], "P", None)}}}},
    ],
}
ALL = ["strike", "narrow", "name-target", "name-operator", "name-gap"]
PROTOCOL = {"ladders": [
    {"id": "i", "decides": ALL, "levers": [
        {"id": "i-a", "slot": "active.dark", "leaf": "optics.regular.tintAlpha", "values": [0.8, 0.7], "shipped": 0.9},
        {"id": "i-f1", "slot": "active.dark", "leaf": "tintAlphaFar1x", "values": [0.2, 0.45], "shipped": 0},
        {"id": "i-g", "slot": "active.dark", "leaf": "sizeOcclusionGain", "values": [0.2, 0.4, 0.6], "shipped": 0.05}]},
    {"id": "ii", "decides": ["strike", "narrow", "name-gap"], "levers": [
        {"id": "ii-d", "rungs": [{"id": "ii-d-1", "overrides": {"active.dark": {
            "sizeHeavySecondShare": 0.05, "sizeHeavySecondShareFar2x": 0.3}}}]}]},
    {"id": "iii", "decides": ["strike", "narrow", "name-target", "name-operator"], "levers": [
        {"id": "iii-w", "slot": "receded.dark", "leaf": "sizeFineTapSigma", "values": [1.5, 2, 3], "shipped": 0},
        {"id": "iii-s", "rungs": [{"id": "iii-s-0.5", "overrides": {"receded.dark": {
            "sizeFineTapShare": 0.5, "sizeFineTapSigma": {"dependsOn": "iii-w"}}}}]}]},
]}


def results(**over):
    ladders = {"i": {"i-a": dict(flat=False, nonFlatRange=[0.7, 0.9], passingRungs=[0.9, 0.8, 0.7]),
                     "i-f1": dict(flat=False, nonFlatRange=[0, 0.45]),
                     "i-g": dict(flat=False, nonFlatRange=[0.05, 0.6])},
               "ii": {"ii-d": dict(flat=False, nonFlatRange=[0, 0.6])},
               "iii": {"iii-w": dict(flat=False, nonFlatRange=[1.5, 3]),
                       "iii-s": dict(flat=False, nonFlatRange=[0.5, 1])}}
    out = dict(control=dict(verdict="IDENTICAL"), ladders=ladders,
               targets={"P": dict(lever=["i-a"]), "C rest": dict(lever=["i-f1"]), "F inactive": dict(lever=["iii-w"])},
               operators={"operator 1": dict(separates=True, ladder="i"),
                          "operator 2": dict(separates=True, ladder="iii")})
    for path, value in over.items():
        node = out
        keys = path.split("/")
        for k in keys[:-1]:
            node = node[k]
        node[keys[-1]] = value
    return out


def scratch_case(cls):
    cls.setUp = lambda self: SCRATCH.mkdir(exist_ok=True)
    cls.tearDown = lambda self: shutil.rmtree(SCRATCH, ignore_errors=True)
    return cls


@scratch_case
class Bindings(unittest.TestCase):
    def parts(self, declaration=None, digest=None):
        parts = copy.deepcopy(D.PARTS)
        decl, dig = SCRATCH / "declaration.json", SCRATCH / "declaration.sha256"
        if declaration is not None:
            decl.write_text(json.dumps(declaration))
        if digest is not None:
            dig.write_text(digest)
        parts["protocol"].update(declaration=decl, digest=dig)
        parts["fit"].update(declaration=SCRATCH / "none.json", digest=SCRATCH / "none.sha256")
        return parts

    def test_another_waves_charter_or_schema(self):
        for body in ({"schema": "w46-declaration-1"}, {"schema": "w45-declaration-1"},
                     {"schema": "w47-declaration-1", "charter": "docs/doperpowers/specs/2026-10-05-w46-dark-texture-at-0-25.md"}):
            with mock.patch.object(D, "PARTS", self.parts(declaration=body)), self.assertRaises(D.Refusal):
                D.bindings()
        with mock.patch.object(D, "PARTS", self.parts(declaration={"schema": "w47-declaration-1",
                                                                    "charter": D.W.CHARTER_PIN})):
            D.bindings()

    def test_a_w46_part_hash(self):
        with mock.patch.object(D, "PARTS", self.parts(digest=f"{W46_PART1}  declaration.json\n")), \
                self.assertRaisesRegex(D.Refusal, "W44, W45 or W46 part hash"):
            D.bindings()

    def test_the_schemas_and_pins_are_w47s(self):
        self.assertEqual((D.PARTS["protocol"]["schema"], D.PARTS["fit"]["schema"]),
                         ("w47-declaration-1", "w47-fit-declaration-1"))
        self.assertEqual(D.W.CHARTER_PIN.rsplit("@", 1)[1], CHARTER_AT)
        self.assertTrue(D.REL.endswith("2026-10-06-w47-g0-operators"))


@scratch_case
class AmendmentRecord(unittest.TestCase):
    def failures(self, body, part="protocol", d=None):
        path = SCRATCH / "amendments.json"
        path.write_text(json.dumps(body))
        parts = copy.deepcopy(D.PARTS)
        parts[part]["amendments"] = path
        with mock.patch.object(D, "PARTS", parts):
            return D.amendment_failures(part, d or {"sources": {"a/b.py": "0" * 64}})

    def entry(self, **extra):
        return dict(n=1, supersedes="x", declarationSha256="y", reason="r", cause="c",
                    pins={"a/b.py": {"from": "0" * 64, "to": "1" * 64}}, **extra)

    def test_a_clean_record_reads_clean(self):
        self.assertEqual(self.failures({"schema": "w47-protocol-amendments-1", "amendments": [self.entry()]}), [])

    def test_a_field_outside_both_forms(self):
        got = self.failures({"schema": "w47-protocol-amendments-1",
                             "amendments": [self.entry(partOneReadAt={"x": "abc"})]})
        self.assertTrue(any("outside the pins-only and content forms" in f for f in got))

    def test_a_pin_of_a_non_source_and_a_second_amendment_and_a_schema(self):
        e = self.entry()
        e["pins"]["c/d.py"] = {"from": "0", "to": "1"}
        got = self.failures({"schema": "w46-protocol-amendments-1", "amendments": [e, self.entry()]})
        self.assertTrue(any("not a working-tree source" in f for f in got))
        self.assertTrue(any("at most once" in f for f in got))
        self.assertTrue(any("schema" in f for f in got))


def charter_ruling(n=1):
    return D.decision_log(D.git_show(D.W.CHARTER_PATH, CHARTER_AT).decode(), f"Decision Log {n}")


@scratch_case
class ContentForm(unittest.TestCase):
    def content(self, **over):
        body = dict(n=1, supersedes="x", declarationSha256="y", reason="r", cause="c", pins={},
                    charter=f"{D.W.CHARTER_PATH}@{CHARTER_AT}", ruling=charter_ruling(1),
                    ops=[dict(op="replace", path=["moves", 0, "x"], **{"from": 1, "to": 2})])
        body.update(over)
        return body

    def failures(self, entry, part="protocol", part1_sources=None):
        path = SCRATCH / "amend.json"
        path.write_text(json.dumps({"schema": f"w47-{part}-amendments-1", "amendments": [entry]}))
        parts = copy.deepcopy(D.PARTS)
        parts[part]["amendments"] = path
        p1 = SCRATCH / "part1.json"
        p1.write_text(json.dumps({"sources": part1_sources or {}}))
        parts["protocol"]["declaration"] = p1
        with mock.patch.object(D, "PARTS", parts):
            return D.amendment_failures(part, {"sources": {}})

    def test_the_ruling_is_the_charters_section_verbatim(self):
        ruling = charter_ruling(1)
        self.assertTrue(ruling.startswith("### Decision Log 1 — RULED"))
        self.assertNotIn("### Decision Log 2", ruling)
        self.assertNotIn("## Surprises", charter_ruling(7))
        self.assertEqual(self.failures(self.content()), [])
        self.assertEqual(self.failures(self.content(), part="fit"), [])
        got = self.failures(self.content(ruling=ruling.replace("RULED", "ruled")))
        self.assertTrue(any("not, verbatim, the charter's `Decision Log 1`" in f for f in got))
        got = self.failures(self.content(ruling="### Decision Log 9 — RULED: a ruling no charter records\n"))
        self.assertTrue(any("lacks it" in f for f in got))

    def test_another_waves_charter_no_ops_and_the_frame(self):
        got = self.failures(self.content(charter="docs/doperpowers/specs/2026-10-05-w46-dark-texture-at-0-25.md@d00d9de6c"))
        self.assertTrue(any("charter other than W47's" in f for f in got))
        got = self.failures({k: v for k, v in self.content().items() if k != "ops"})
        self.assertTrue(any("without its ruling, charter and ops" in f for f in got))
        got = self.failures(self.content(ops=[dict(op="replace", path=["sources", "x"], **{"from": 1, "to": 2})]))
        self.assertTrue(any("frame" in f for f in got))
        got = self.failures(self.content(ops=[dict(op="remove", path=["moves"])]))
        self.assertTrue(any("not an add or a replace" in f for f in got))

    def test_part_one_pins_ride_part_2_only_and_only_the_repinnable(self):
        key = f"{D.REL}/fit/search.py"
        got = self.failures(self.content(partOnePins={key: {"from": "a", "to": "b"}}), part="protocol")
        self.assertTrue(any("outside the pins-only and content forms" in f for f in got))
        self.assertEqual(self.failures(self.content(partOnePins={key: {"from": "a", "to": "b"}}), part="fit",
                                       part1_sources={key: "a"}), [])
        got = self.failures(self.content(partOnePins={key: {"from": "z", "to": "b"}}), part="fit",
                            part1_sources={key: "a"})
        self.assertTrue(any("does not start at part 1's pin" in f for f in got))
        other = f"{D.REL}/cuts/rule.py"
        got = self.failures(self.content(partOnePins={other: {"from": "a", "to": "b"}}), part="fit",
                            part1_sources={other: "a"})
        self.assertTrue(any("which no amendment may" in f for f in got))

    def test_ops_apply_and_revert_byte_for_byte(self):
        ops = [dict(op="replace", path=["moves", 1, "families", "transmission", "leaves", "optics.regular.tintAlpha",
                                        "grid"], **{"from": [0.8, 0.89], "to": [0.8]}),
               dict(op="add", path=["moves", 1, "points"], to={"ruling": "Decision Log 8"})]
        amended = D.apply_ops(DRAFT, ops)
        self.assertEqual(D.serialise(D.revert_ops(amended, ops)), D.serialise(DRAFT))
        with self.assertRaisesRegex(D.Refusal, "does not hold its `from`"):
            D.apply_ops(amended, ops[:1])
        with self.assertRaisesRegex(D.Refusal, "the path exists"):
            D.apply_ops(amended, ops[1:])
        with self.assertRaisesRegex(D.Refusal, "frame"):
            D.apply_ops(DRAFT, [dict(op="replace", path=["schema"], **{"from": "a", "to": "b"})])


@scratch_case
class Chain(unittest.TestCase):
    def parts(self, body, lines, record):
        parts = copy.deepcopy(D.PARTS)
        decl, dig, rec = SCRATCH / "fit.json", SCRATCH / "fit.sha256", SCRATCH / "fit-amend.json"
        decl.write_bytes(D.serialise(body))
        dig.write_text("".join(f"{x}  fit.json\n" for x in lines))
        rec.write_text(json.dumps({"schema": "w47-fit-amendments-1", "amendments": record}))
        parts["fit"].update(declaration=decl, digest=dig, amendments=rec)
        return parts

    def test_a_content_amendment_rebuilds_the_superseded_hash_and_a_tampered_op_does_not(self):
        hashed = dict(copy.deepcopy(DRAFT), schema="w47-fit-declaration-1", changes=[], sources={})
        h0 = D.sha(D.serialise(hashed))
        ops = [dict(op="replace", path=["moves", 1, "familyOrder"], **{"from": ["fine", "transmission"],
                                                                       "to": ["transmission", "fine"]})]
        amended = D.apply_ops(hashed, ops)
        h1 = D.sha(D.serialise(amended))
        entry = dict(n=1, supersedes=h0, declarationSha256=h1, reason="r", cause="c", pins={},
                     charter=f"{D.W.CHARTER_PATH}@{CHARTER_AT}", ruling=charter_ruling(4), ops=ops)
        with mock.patch.object(D, "PARTS", self.parts(amended, [h0, h1], [entry])):
            c = D.Check()
            D.chain(c, "fit", amended)
            self.assertEqual(c.failures, [])
        bad = copy.deepcopy(entry)
        bad["ops"][0]["from"] = ["fine"]
        with mock.patch.object(D, "PARTS", self.parts(amended, [h0, h1], [bad])):
            c = D.Check()
            D.chain(c, "fit", amended)
            self.assertTrue(any("before amendment 1 rebuilt" in f for f in c.failures))

    def test_one_amendment_per_part_final(self):
        args = ["--reason", "r", "--cause", "c", "x"]
        with mock.patch.object(D, "digest_lines", lambda part: ["a" * 64]), \
                mock.patch.object(D, "ladder_evidence", lambda: []), mock.patch.object(D, "fit_evidence", lambda: []), \
                mock.patch.object(D, "amendments", lambda part: [{"n": 1}]):
            self.assertEqual(D.amend("protocol", args), 2)
            self.assertEqual(D.amend("fit", args), 2)

    def test_the_content_form_names_its_three_arguments_together(self):
        self.assertEqual(D.amend("fit", ["--reason", "r", "--cause", "c", "--ruling", "Decision Log 8", "x"]), 2)
        self.assertEqual(D.amend("protocol", ["--reason", "r", "--cause", "c"]), 2)

    def test_amend_refuses_after_a_render(self):
        with mock.patch.object(D, "digest_lines", lambda part: ["a" * 64]), \
                mock.patch.object(D, "ladder_evidence", lambda: ["ladders/runs.jsonl"]):
            self.assertEqual(D.amend("protocol", ["--reason", "r", "--cause", "c", "x"]), 2)


class ValidatedDiff(unittest.TestCase):
    def apply(self, changes, res=None):
        return D.apply_changes(DRAFT, changes, res or results(), PROTOCOL)

    def leaf(self, body, move, family, key):
        return D.find_leaf(body, move, family, key)[2]

    def fit(self, changes, res=None):
        body = D.apply_changes(DRAFT, changes, res or results(), PROTOCOL)
        body.pop("status", None)
        return dict(body, changes=changes)

    def test_no_change_is_the_draft(self):
        self.assertEqual(self.apply([]), DRAFT)
        D.validate_fit(DRAFT, self.fit([]), results(), PROTOCOL)

    def test_strike_only_a_flat_lever(self):
        ch = dict(kind="strike", move="stage1", family="span-law", leaf="sizeOcclusionGain", lever="i-g")
        with self.assertRaisesRegex(D.Refusal, "did not read flat"):
            self.apply([ch])
        body = self.apply([ch], results(**{"ladders/i/i-g/flat": True}))
        self.assertIsNone(self.leaf(body, "stage1", "span-law", "sizeOcclusionGain"))
        self.assertEqual(body["moves"][0]["families"]["span-law"]["factorialGroups"][0]["keys"],
                         ["optics.regular.tintAlpha", "tintAlphaFar1x"])

    def test_narrow_inside_the_range_and_the_passing_rungs(self):
        ch = dict(kind="narrow", move="stage1", family="span-law", leaf="tintAlphaFar1x", lever="i-f1", grid=[0, 0.2])
        self.assertEqual(self.leaf(self.apply([ch]), "stage1", "span-law", "tintAlphaFar1x")["grid"], [0, 0.2])
        with self.assertRaisesRegex(D.Refusal, "non-flat range"):
            self.apply([dict(ch, grid=[0.45])], results(**{"ladders/i/i-f1/nonFlatRange": [0, 0.3]}))
        with self.assertRaisesRegex(D.Refusal, "passing rungs"):
            self.apply([dict(kind="narrow", move="stage1", family="span-law", leaf="optics.regular.tintAlpha",
                             lever="i-a", grid=[0.7])], results(**{"ladders/i/i-a/passingRungs": [0.9, 0.8]}))

    def test_a_decision_its_ladder_may_not_make(self):
        with self.assertRaisesRegex(D.Refusal, "lets decide it"):
            self.apply([dict(kind="name-operator", operator="operator 1", ladder="ii", reading="flat")],
                       results(**{"operators/operator 1/separates": False}))

    def test_name_operator_only_without_separation(self):
        ch = dict(kind="name-operator", operator="operator 2", ladder="iii",
                  reading="ladder (iii): no rung lowered the fine inactive cells by 3 B")
        with self.assertRaisesRegex(D.Refusal, "as separating"):
            self.apply([ch])
        body = self.apply([ch], results(**{"operators/operator 2/separates": False}))
        self.assertNotIn("fine", body["moves"][1]["families"])
        self.assertEqual(body["notFitted"], [dict(operator="operator 2", ladder="iii", reading=ch["reading"])])
        body = self.apply([ch], results(**{"operators/operator 2/bodyWidthMeetsBar": True}))
        self.assertNotIn("fine", body["moves"][1]["families"])
        with self.assertRaisesRegex(D.Refusal, "reading"):
            self.apply([dict(ch, reading="")], results(**{"operators/operator 2/separates": False}))

    def test_name_gap_cites_its_ladder(self):
        ch = dict(kind="name-gap", gap="the 1x per-span width", ladder="ii",
                  shape="sizeHeavySecondShareFar1x, identity 0, a plain value drop")
        body = self.apply([ch])
        self.assertEqual(body["namedGaps"], [dict(gap=ch["gap"], ladder="ii", shape=ch["shape"])])
        self.assertEqual(body["moves"], DRAFT["moves"])
        with self.assertRaisesRegex(D.Refusal, "states the gap"):
            self.apply([dict(ch, shape="")])

    def test_name_target_only_without_a_lever(self):
        ch = dict(kind="name-target", target="F inactive", ladder="iii", operatorShape="a receded fine term")
        with self.assertRaisesRegex(D.Refusal, "read a lever"):
            self.apply([ch])
        body = self.apply([ch], results(**{"targets/F inactive/lever": []}))
        self.assertNotIn("fine", body["moves"][1]["families"])

    def test_nothing_without_an_identical_control_and_no_other_kind(self):
        with self.assertRaisesRegex(D.Refusal, "control"):
            self.apply([], results(**{"control/verdict": "DIFFERS"}))
        with self.assertRaisesRegex(D.Refusal, "decisions"):
            self.apply([dict(kind="inert", move="stage1")])

    def test_clause_5s_required_outcomes(self):
        res = results(**{"operators/operator 2/separates": False})
        with self.assertRaisesRegex(D.Refusal, "operator 2 shows no separation"):
            D.validate_fit(DRAFT, self.fit([]), res, PROTOCOL)
        named = [dict(kind="name-operator", operator="operator 2", ladder="iii", reading="flat")]
        D.validate_fit(DRAFT, self.fit(named, res), res, PROTOCOL)
        both = results(**{"operators/operator 1/separates": False, "operators/operator 2/separates": False})
        self.assertTrue(any("neither operator separates" in f for f in D.mandatory_failures(DRAFT, both)))
        self.assertTrue(any("closes at G0" in f for f in D.mandatory_failures(DRAFT, results(**{
            "targets/P/lever": [], "targets/C rest/lever": [], "targets/F inactive/lever": []}))))

    def test_validate_fit_refuses_a_body_beyond_its_changes_and_reads_the_reverted_body(self):
        fit = self.fit([])
        bad = copy.deepcopy(fit)
        bad["moves"][0]["families"]["span-law"]["leaves"]["tintAlphaFar1x"]["grid"] = [0.6]
        with self.assertRaisesRegex(D.Refusal, "beyond its permitted changes"):
            D.validate_fit(DRAFT, bad, results(), PROTOCOL)
        ops = [dict(op="add", path=["moves", 1, "points"], to={"ruling": "Decision Log 8"})]
        amended = D.apply_ops(fit, ops)
        D.validate_fit(DRAFT, amended, results(), PROTOCOL, [dict(ops=ops)])
        with self.assertRaisesRegex(D.Refusal, "beyond its permitted changes"):
            D.validate_fit(DRAFT, amended, results(), PROTOCOL, [])


@scratch_case
class Pins(unittest.TestCase):
    def test_a_moved_source_is_a_mismatch(self):
        f = SCRATCH / "x.txt"
        f.write_text("a")
        rel = f.relative_to(D.ROOT).as_posix()
        d = {"items": [{"id": "x", "title": "t", "clause": "c", "source": [rel], "declared": {}}],
             "sources": {rel: D.sha(b"a")}}
        c = D.Check()
        D.structure(c, d)
        self.assertEqual(c.failures, [])
        f.write_text("b")
        c = D.Check()
        D.structure(c, d)
        self.assertTrue(any(x.startswith(f"pin {rel}") for x in c.failures))

    def test_hash_refuses_after_a_ladder_render_and_while_pending(self):
        decl = SCRATCH / "declaration.json"
        decl.write_text("{}")
        parts = dict(D.PARTS, protocol=dict(D.PARTS["protocol"], digest=SCRATCH / "absent.sha256", declaration=decl))
        clean = (D.Check(), {"sources": {}}, {})
        with mock.patch.object(D, "PARTS", parts), mock.patch.object(D, "check_protocol", lambda: clean), \
                mock.patch.object(D, "ladder_evidence", lambda: ["ladders/runs.jsonl"]):
            self.assertEqual(D.main(["declare.py", "hash"]), 2)
        pending = (D.Check(), {"sources": {}}, {"x": {"id": "x", "pending": {"on": "a render"}}})
        with mock.patch.object(D, "PARTS", parts), mock.patch.object(D, "check_protocol", lambda: pending), \
                mock.patch.object(D, "ladder_evidence", lambda: []):
            self.assertEqual(D.main(["declare.py", "hash"]), 2)
        self.assertFalse((SCRATCH / "absent.sha256").exists())

    def test_a_part_one_pin_is_accepted_only_along_the_recorded_move(self):
        key = f"{D.REL}/fit/search.py"
        with mock.patch.object(D, "part_one_moves", lambda: {key: {"from": "a", "to": "b"}}), \
                mock.patch.object(D, "amended_sources", lambda: {key: "b"}):
            self.assertTrue(D.accepted_repin(key, "a", "b"))
            self.assertFalse(D.accepted_repin(key, "a", "c"))
            self.assertFalse(D.accepted_repin(f"{D.REL}/cuts/rule.py", "a", "b"))
        with mock.patch.object(D, "part_one_moves", lambda: {key: {"from": "a", "to": "c"}}), \
                mock.patch.object(D, "amended_sources", lambda: {key: "b"}):
            self.assertFalse(D.accepted_repin(key, "a", "c"))


@scratch_case
class Assemble(unittest.TestCase):
    def test_refuses_with_an_unfilled_placeholder(self):
        """On a template of the committed inputs' shape (the committed file is filled later by the parent,
        and this case must still hold when `declare.py check` re-runs it on the assembled tree)."""
        import assemble as A
        template = {k: v for k, v in json.loads(D.INPUTS.read_text()).items() if k in ("schema", "$comment")}
        template.update(targets=dict(predictions="TO FILL", statement="TO FILL", sources=[]),
                        s1=dict(predictedDirection="TO FILL", sentence="TO FILL", sources=[]),
                        diagnostic=dict(record="TO FILL", chosenForm="TO FILL", statement="TO FILL", sources=[]))
        path = SCRATCH / "inputs.json"
        path.write_text(json.dumps(template))
        before = D.W.PART1.read_bytes() if D.W.PART1.exists() else None
        with mock.patch.object(D, "INPUTS", path), mock.patch.object(A.W, "PART1_DIGEST", SCRATCH / "absent.sha256"), \
                mock.patch.object(A, "build", side_effect=AssertionError("build ran")):
            with self.assertRaisesRegex(SystemExit, "TO FILL at /targets/predictions"):
                A.main()
            filled = copy.deepcopy(template)
            for key in ("targets", "s1"):
                filled[key] = {k: ("given" if v == "TO FILL" else v) for k, v in filled[key].items()}
            filled["diagnostic"]["chosenForm"] = "body"
            path.write_text(json.dumps(filled))
            with self.assertRaisesRegex(SystemExit, "/diagnostic/record"):
                A.inputs()
        self.assertEqual(D.W.PART1.read_bytes() if D.W.PART1.exists() else None, before)

    def test_refuses_once_part_1_is_hashed(self):
        import assemble as A
        hashed = SCRATCH / "declaration.sha256"
        hashed.write_text("x\n")
        with mock.patch.object(A.W, "PART1_DIGEST", hashed), self.assertRaisesRegex(SystemExit, "hashed"):
            A.main()

    def test_placeholders_are_found_at_any_depth(self):
        self.assertEqual(D.placeholders({"a": [1, {"b": "TO FILL (x)"}], "c": "ok"}), ["/a/1/b"])
        self.assertEqual(D.placeholders({"a": 1}), [])


class Shapes(unittest.TestCase):
    def test_the_diagnostics_criterion(self):
        cell = lambda body, deep, scale=1: dict(cell="checkerboard-8__rrect-md__inactive", scale=scale,  # noqa: E731
                                                R=dict(body=body, deep=deep))
        self.assertEqual(D.diagnostic_choice([cell(0.6, 0.1), cell(0.7, 0.2, 2)]), "body")
        self.assertEqual(D.diagnostic_choice([cell(0.1, 0.6), cell(0.2, 0.9, 2)]), "deep")
        self.assertEqual(D.diagnostic_choice([cell(0.6, 0.1), cell(0.1, 0.7, 2)]), "parent")    # split by scale
        self.assertEqual(D.diagnostic_choice([cell(0.4, 0.1), cell(0.45, 0.2, 2)]), "parent")   # neither half

    def test_the_protocols_two_rung_forms(self):
        ids = [r["id"] for lad in PROTOCOL["ladders"] for r in D.protocol_rungs(lad)]
        self.assertEqual(ids, ["i-a-0.8", "i-a-0.7", "i-f1-0.2", "i-f1-0.45", "i-g-0.2", "i-g-0.4", "i-g-0.6",
                               "ii-d-1", "iii-w-1.5", "iii-w-2", "iii-w-3", "iii-s-0.5"])
        self.assertEqual(D.lever_ids(PROTOCOL), ["i-a", "i-f1", "i-g", "ii-d", "iii-w", "iii-s"])

    def test_x67_admission_and_x68_domains(self):
        self.assertTrue(D.admitted_leaf("receded.dark", "optics.regular.blurSigma"))
        self.assertFalse(D.admitted_leaf("active.dark", "optics.regular.blurSigma"))
        self.assertFalse(D.admitted_leaf("active.dark", "sizeFineTapShare"))
        self.assertTrue(D.admitted_leaf("receded.dark", "sizeFineTapShare"))
        self.assertTrue(D.admitted_leaf("active.dark", "optics.regular.tintAlpha"))          # the snapshot's own
        self.assertFalse(D.admitted_leaf("receded.dark", "sizeHeavyTapSigma2xx"))
        self.assertEqual(D.domains_json(D.W.DOMAINS["receded.dark"]["sizeFineTapSigma"]),
                         [["set", [0]], ["interval", 1.5, 6]])


if __name__ == "__main__":
    unittest.main()
