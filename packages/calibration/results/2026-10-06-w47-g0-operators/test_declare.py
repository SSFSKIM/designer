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
- **Part 1 after the ladders (Decision Log 8)**: a pins-only amendment, an op that replaces a value,
  and part 2 after a fit render all refuse; an additive content amendment of part 1 is admitted, names
  the render evidence it was made over, chains to the superseded hash, and refuses a second time; on
  read, a post-render record that is pins-only, replaces a value or sits on part 2 is refused.
- **The validated diff and clause 5's outcomes**, in `ladders/protocol.json`'s words and on
  `ladders/read.py`'s results shape: name-unfitted (only an operator the ladders read as not separating;
  its leaves removed), body-width-first, name-target, name-1x-gap (only where ladder (ii) met its bar),
  strike (flat rungs, or a ladder-(ii)-conditional leaf when it did not meet its bar), narrow (the
  active transmission to its passing rungs); required: each of these where the ladders demand it, a
  one-scale separation ruled first, neither separating stops part 2; `ladders/part2.py` derives exactly
  the changes `validate_fit` accepts.
- **The committed protocol and draft** pass declare's ladders and draft checks.
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


def leaf(slot, grid, domain, target, ladder, rungs=(), unit="u", **extra):
    return dict(slot=slot, grid=grid, domain=domain, unit=unit, target=target, ladder=ladder, rungs=list(rungs),
                **extra)


DRAFT = {
    "schema": "w47-fit-declaration-1", "references": {"dark": "d0219cd684bf", "light": "ebc3d9105a4a"},
    "landingRule": {"implementation": "cuts/rule.py (pinned by part 1)"}, "notFitted": [], "namedGaps": [],
    "moves": [
        {"id": "stage1", "slot": "active.dark", "familyOrder": ["span-law", "second-tap"], "families": {
            "span-law": {"why": "w", "leaves": {
                "optics.regular.tintAlpha": leaf("active.dark", [0.7, 0.8, 0.9], [0.7, 0.9], "P", "i",
                                                 ["i-a0.7", "i-a0.8", "i-a0.7-f0.2"]),
                "tintAlphaFar1x": leaf("active.dark", [0, 0.2, 0.45], [0, 0.6], "P", "i", ["i-a0.7-f0.2"],
                                       operator="operator 1"),
                "sizeOcclusionGain": leaf("active.dark", [0.05, 0.2, 0.4], [0.05, 0.6], "P", "i", ["i-a0.7-g0.2"])},
                "factorialGroups": [{"keys": ["optics.regular.tintAlpha", "tintAlphaFar1x", "sizeOcclusionGain"]}]},
            "second-tap": {"why": "w", "leaves": {
                "sizeHeavySecondShareFar2x": leaf("active.dark", [0.3, 0.6], [0, 1], "C rest", "ii", ["ii-w6-d0.3"],
                                                  conditional="ii")}}}},
        {"id": "stage2", "slot": "receded.dark", "familyOrder": ["fine", "transmission"], "families": {
            "fine": {"why": "w", "leaves": {
                "sizeFineTapSigma": leaf("receded.dark", [1.5, 2, 3], [0, 6], "F inactive", "iii", ["iii-s2"],
                                         operator="operator 2"),
                "sizeFineTapShare": leaf("receded.dark", [0.5, 1], [0, 1], "F inactive", "iii", ["iii-s2", "iii-q0.5"],
                                         operator="operator 2"),
                "optics.regular.blurSigma": leaf("receded.dark", [1.25, 2], [1.25, 4], "F inactive", "iii", ["iii-b2"])}},
            "transmission": {"why": "w", "leaves": {
                "optics.regular.tintAlpha": leaf("receded.dark", [0.8, 0.89], [0.8, 0.89], "P", None)}}}},
    ],
}
PROTOCOL = {"decisions": {k: "text" for k in D.CHANGE_KINDS + D.OUTCOMES}, "ladders": [
    {"id": "i", "decides": ["name-unfitted", "name-target", "narrow", "strike"], "rungs": [
        {"label": "i-a0.7", "overrides": {"active.dark": {"optics.regular.tintAlpha": 0.7}}},
        {"label": "i-a0.8", "overrides": {"active.dark": {"optics.regular.tintAlpha": 0.8}}},
        {"label": "i-a0.7-f0.2", "overrides": {"active.dark": {"optics.regular.tintAlpha": 0.7, "tintAlphaFar1x": 0.2}}},
        {"label": "i-a0.7-g0.2", "overrides": {"active.dark": {"optics.regular.tintAlpha": 0.7,
                                                                "sizeOcclusionGain": 0.2}}}]},
    {"id": "ii", "decides": ["name-1x-gap", "strike"], "rungs": [
        {"label": "ii-w6-d0.3", "overrides": {"active.dark": {
            "sizeHeavySecondShare": 0.05, "sizeHeavySecondSigma2x": 6, "sizeHeavySecondShareFar2x": 0.3}}}]},
    {"id": "iii", "decides": ["name-unfitted", "body-width-first", "name-target", "strike"], "rungs": [
        {"label": "iii-b2", "overrides": {"receded.dark": {"optics.regular.blurSigma": 2}}},
        {"label": "iii-s2", "overrides": {"receded.dark": {"sizeFineTapShare": 1, "sizeFineTapSigma": 2,
                                                            "sizeFineTapSigma2x": 2}}},
        {"label": "iii-q0.5", "overrides": {"receded.dark": {"sizeFineTapShare": 0.5,
                                                              "sizeFineTapSigma": {"select": "iii-width-1x"}}}}]},
    {"id": "iv", "decides": ["name-target"], "rungs": []},
]}
RUNG_LADDER = {r["label"]: lad["id"] for lad in PROTOCOL["ladders"] for r in lad["rungs"]}


def results(moved=(), **over):
    """`ladders/read.py`'s results.json shape: every rung read, a cell moved on every rung unless the rung
    is listed flat by `moved` (a set of rungs whose cells read flat)."""
    rungs = {lab: dict(ladder=lad, cells={"1x/x": dict(moved=lab not in moved)}) for lab, lad in RUNG_LADDER.items()}
    ladders = {lad["id"]: dict(complete=True, read=[r["label"] for r in lad["rungs"]], notRead=[],
                               meets=[], meetsAtOneScaleOnly=[], passingL1=None) for lad in PROTOCOL["ladders"]}
    ladders["i"].update(meets=["i-a0.7-f0.2"], passingL1=["i-a0.7", "i-a0.8", "i-a0.7-f0.2"])
    out = dict(control=dict(verdict="IDENTICAL"), rungs=rungs, ladders=ladders,
               operators={"operator 1": dict(separates=True, complete=True, rungs=["i-a0.7-f0.2"], oneScaleOnly=[]),
                          "2x width": dict(meets=True, complete=True, rungs=["ii-w6-d0.3"]),
                          "operator 2": dict(separates=True, bodyWidthMeets=False, complete=True, rungs=["iii-s2"],
                                             bodyRungs=[], oneScaleOnly=[]),
                          "joint": dict(meets=True, complete=True)})
    for path, value in over.items():
        node = out
        keys = path.split("/")
        for k in keys[:-1]:
            node = node[k]
        node[keys[-1]] = value
    return out


GAP = dict(kind="name-1x-gap", ladder="ii", operatorShape="sizeHeavySecondShareFar1x, identity 0, a plain value drop")


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

    def test_a_post_render_record_is_part_1s_additive_content_form_only(self):
        post = D.POST_RENDER_EVIDENCE + "ladders/runs.jsonl"
        content = dict(charter=f"{D.W.CHARTER_PATH}@{CHARTER_AT}", ruling=charter_ruling(1))
        add = [dict(op="add", path=["items", 0, "declared", "x"], to=1)]
        clean = self.entry(renderEvidenceAtAmendment=post, ops=add, **content)
        self.assertEqual(self.failures({"schema": "w47-protocol-amendments-1", "amendments": [clean]}), [])
        got = self.failures({"schema": "w47-protocol-amendments-1",
                             "amendments": [self.entry(renderEvidenceAtAmendment=post)]})
        self.assertTrue(any("not part 1's content form" in f for f in got))
        replace = [dict(op="replace", path=["items", 0, "declared", "x"], **{"from": 1, "to": 2})]
        got = self.failures({"schema": "w47-protocol-amendments-1",
                             "amendments": [self.entry(renderEvidenceAtAmendment=post, ops=replace, **content)]})
        self.assertTrue(any("replaces a hashed value" in f for f in got))
        got = self.failures({"schema": "w47-fit-amendments-1", "amendments": [clean]}, part="fit")
        self.assertTrue(any("not part 1's content form" in f for f in got))

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

    def test_after_the_ladders_only_an_additive_content_amendment_of_part_1(self):
        body = {"schema": "w47-declaration-1", "items": [{"id": "x", "declared": {"bar": 3}}], "sources": {}}
        decl, dig, rec = SCRATCH / "part1.json", SCRATCH / "part1.sha256", SCRATCH / "part1-amend.json"
        decl.write_bytes(D.serialise(body))
        h0 = D.sha(decl.read_bytes())
        dig.write_text(f"{h0}  part1.json\n")
        parts = copy.deepcopy(D.PARTS)
        parts["protocol"].update(declaration=decl, digest=dig, amendments=rec)
        replace, add = SCRATCH / "replace.json", SCRATCH / "add.json"
        replace.write_text(json.dumps([dict(op="replace", path=["items", 0, "declared", "bar"], **{"from": 3, "to": 2})]))
        add.write_text(json.dumps([dict(op="add", path=["items", 0, "declared", "restated"], to={"bar": 2})]))
        args = ["--reason", "r", "--cause", "c", "--ruling", "Decision Log 1", "--charter-commit", CHARTER_AT, "--ops"]
        with mock.patch.object(D, "PARTS", parts), \
                mock.patch.object(D, "ladder_evidence", lambda: ["ladders/runs.jsonl"]), \
                mock.patch.object(D, "fit_evidence", lambda: ["fit/runs.jsonl"]), \
                mock.patch.object(D, "check_protocol", lambda: (D.Check(), None, None)):
            self.assertEqual(D.amend("protocol", args + [str(replace)]), 2)
            self.assertFalse(rec.exists())
            self.assertEqual(D.serialise(body), decl.read_bytes())
            self.assertEqual(D.amend("fit", args + [str(add)]), 2)
            self.assertEqual(D.amend("protocol", args + [str(add)]), 0)
            entry = json.loads(rec.read_text())["amendments"][0]
            self.assertEqual(entry["renderEvidenceAtAmendment"], D.POST_RENDER_EVIDENCE + "ladders/runs.jsonl")
            self.assertEqual(entry["supersedes"], h0)
            amended = json.loads(decl.read_text())
            self.assertEqual(amended["items"][0]["declared"], {"bar": 3, "restated": {"bar": 2}})
            c = D.Check()
            D.chain(c, "protocol", amended)
            self.assertEqual(c.failures, [])
            self.assertEqual(D.amend("protocol", args + [str(add)]), 2)


class ValidatedDiff(unittest.TestCase):
    """Clause 5's decisions in the protocol's words, on `ladders/read.py`'s results shape."""

    def apply(self, changes, res=None):
        return D.apply_changes(DRAFT, changes, res or results(), PROTOCOL)

    def leaf(self, body, move, family, key):
        return D.find_leaf(body, move, family, key)[2]

    def fit(self, changes, res=None):
        body = D.apply_changes(DRAFT, changes, res or results(), PROTOCOL)
        body.pop("status", None)
        return dict(body, changes=changes)

    def test_no_change_is_the_draft_and_the_gap_is_required(self):
        self.assertEqual(self.apply([]), DRAFT)
        with self.assertRaisesRegex(D.Refusal, "1x per-span width gap is not named"):
            D.validate_fit(DRAFT, self.fit([]), results(), PROTOCOL)
        D.validate_fit(DRAFT, self.fit([GAP]), results(), PROTOCOL)

    def test_strike_only_flat_rungs_or_ladder_ii_unmet(self):
        ch = dict(kind="strike", move="stage1", family="span-law", leaf="sizeOcclusionGain", ladder="i")
        with self.assertRaisesRegex(D.Refusal, "did not read flat"):
            self.apply([ch])
        body = self.apply([ch], results(moved={"i-a0.7-g0.2"}))
        self.assertIsNone(self.leaf(body, "stage1", "span-law", "sizeOcclusionGain"))
        self.assertEqual(body["moves"][0]["families"]["span-law"]["factorialGroups"][0]["keys"],
                         ["optics.regular.tintAlpha", "tintAlphaFar1x"])
        with self.assertRaisesRegex(D.Refusal, "read on ladder"):
            self.apply([dict(ch, ladder="iii")], results(moved={"i-a0.7-g0.2"}))
        cond = dict(kind="strike", move="stage1", family="second-tap", leaf="sizeHeavySecondShareFar2x", ladder="ii")
        with self.assertRaisesRegex(D.Refusal, "met its bar"):
            self.apply([cond])
        unmet = results(**{"operators/2x width/meets": False})
        self.assertNotIn("second-tap", self.apply([cond], unmet)["moves"][0]["families"])
        with self.assertRaisesRegex(D.Refusal, "crossed into stage 1 only"):
            D.validate_fit(DRAFT, self.fit([], unmet), unmet, PROTOCOL)
        D.validate_fit(DRAFT, self.fit([cond], unmet), unmet, PROTOCOL)

    def test_narrow_only_the_transmission_inside_its_passing_rungs(self):
        ch = dict(kind="narrow", move="stage1", family="span-law", leaf="optics.regular.tintAlpha", ladder="i",
                  grid=[0.8, 0.9])
        self.assertEqual(self.leaf(self.apply([ch]), "stage1", "span-law", "optics.regular.tintAlpha")["grid"],
                         [0.8, 0.9])
        res = results(**{"ladders/i/passingL1": ["i-a0.8"]})
        with self.assertRaisesRegex(D.Refusal, "passing rungs"):
            self.apply([dict(ch, grid=[0.7, 0.9])], res)
        with self.assertRaisesRegex(D.Refusal, "leaves the transmission's passing rungs"):
            D.validate_fit(DRAFT, self.fit([GAP], res), res, PROTOCOL)
        D.validate_fit(DRAFT, self.fit([GAP, ch], res), res, PROTOCOL)
        with self.assertRaisesRegex(D.Refusal, "narrows only the active transmission"):
            self.apply([dict(kind="narrow", move="stage1", family="span-law", leaf="tintAlphaFar1x", ladder="i",
                             grid=[0, 0.2])])

    def test_a_decision_its_ladder_may_not_make(self):
        with self.assertRaisesRegex(D.Refusal, "lets decide it"):
            self.apply([dict(kind="name-unfitted", operator="operator 1", ladder="ii", reading="flat")],
                       results(**{"operators/operator 1/separates": False}))
        with self.assertRaisesRegex(D.Refusal, "lets decide it"):
            self.apply([dict(GAP, ladder="i")])

    def test_name_unfitted_only_without_separation(self):
        ch = dict(kind="name-unfitted", operator="operator 2", ladder="iii",
                  reading="ladder (iii): no rung lowered the fine inactive cells by 3 B")
        with self.assertRaisesRegex(D.Refusal, "as separating"):
            self.apply([ch])
        res = results(**{"operators/operator 2/separates": False})
        body = self.apply([ch], res)
        fine = body["moves"][1]["families"]["fine"]["leaves"]
        self.assertEqual(list(fine), ["optics.regular.blurSigma"])
        self.assertEqual(body["notFitted"], [dict(operator="operator 2", ladder="iii", reading=ch["reading"])])
        with self.assertRaisesRegex(D.Refusal, "reading"):
            self.apply([dict(ch, reading="")], res)
        with self.assertRaisesRegex(D.Refusal, "incomplete"):
            self.apply([ch], results(**{"operators/operator 2/separates": False,
                                        "operators/operator 2/complete": False}))

    def test_body_width_first(self):
        ch = dict(kind="body-width-first", operator="operator 2", ladder="iii", reading="iii-b3 met the bar")
        with self.assertRaisesRegex(D.Refusal, "no receded optics.regular.blurSigma rung"):
            self.apply([ch])
        res = results(**{"operators/operator 2/bodyWidthMeets": True, "operators/operator 2/bodyRungs": ["iii-b2"]})
        body = self.apply([ch], res)
        self.assertEqual(list(body["moves"][1]["families"]["fine"]["leaves"]), ["optics.regular.blurSigma"])
        self.assertEqual(body["notFitted"][0]["decision"], "body-width-first")
        with self.assertRaisesRegex(D.Refusal, "body-width-first, not name-unfitted"):
            self.apply([dict(ch, kind="name-unfitted")], results(**{"operators/operator 2/bodyWidthMeets": True,
                                                                      "operators/operator 2/separates": False}))
        with self.assertRaisesRegex(D.Refusal, "is not named in notFitted"):
            D.validate_fit(DRAFT, self.fit([GAP], res), res, PROTOCOL)
        D.validate_fit(DRAFT, self.fit([GAP, ch], res), res, PROTOCOL)

    def test_name_1x_gap_only_where_ladder_ii_met_its_bar(self):
        body = self.apply([GAP])
        self.assertEqual(body["namedGaps"], [dict(gap="the 1x per-span width", ladder="ii", shape=GAP["operatorShape"],
                                                  rungs=["ii-w6-d0.3"])])
        self.assertEqual(body["moves"], DRAFT["moves"])
        with self.assertRaisesRegex(D.Refusal, "did not meet its bar"):
            self.apply([GAP], results(**{"operators/2x width/meets": False}))
        with self.assertRaisesRegex(D.Refusal, "operator's shape"):
            self.apply([dict(GAP, operatorShape="")])

    def test_name_target_only_without_a_lever(self):
        ch = dict(kind="name-target", target="F inactive", ladder="iii", operatorShape="a receded fine term")
        with self.assertRaisesRegex(D.Refusal, "read a lever"):
            self.apply([ch], results(**{"targets": {"F inactive": {"lever": True}}}))
        body = self.apply([ch])
        self.assertNotIn("fine", body["moves"][1]["families"])
        self.assertEqual(body["notFitted"], [dict(target="F inactive", ladder="iii", operatorShape=ch["operatorShape"])])

    def test_nothing_without_an_identical_control_and_no_other_kind(self):
        with self.assertRaisesRegex(D.Refusal, "control"):
            self.apply([], results(**{"control/verdict": "DIFFERS"}))
        with self.assertRaisesRegex(D.Refusal, "decisions"):
            self.apply([dict(kind="name-operator", move="stage1", ladder="i")])
        with self.assertRaisesRegex(D.Refusal, "decisions"):
            self.apply([dict(kind="fit", ladder="i")])

    def test_clause_5s_required_outcomes(self):
        res = results(**{"operators/operator 2/separates": False})
        with self.assertRaisesRegex(D.Refusal, "operator 2 shows no separation"):
            D.validate_fit(DRAFT, self.fit([GAP], res), res, PROTOCOL)
        named = [GAP, dict(kind="name-unfitted", operator="operator 2", ladder="iii", reading="flat")]
        D.validate_fit(DRAFT, self.fit(named, res), res, PROTOCOL)
        both = results(**{"operators/operator 1/separates": False, "operators/operator 2/separates": False})
        self.assertTrue(any("neither operator separates" in f and "closes at G0" in f
                            for f in D.mandatory_failures(DRAFT, both)))
        one = results(**{"operators/operator 1/oneScaleOnly": ["i-a0.7-f0.2"]})
        self.assertTrue(any("one scale only" in f for f in D.mandatory_failures(DRAFT, one)))
        incomplete = results(**{"ladders/iii/complete": False})
        self.assertTrue(any("ladder (iii) is incomplete" in f for f in D.mandatory_failures(DRAFT, incomplete)))
        flat = results(moved={"i-a0.7-g0.2"})
        self.assertTrue(any("read flat and the leaf is retained" in f for f in D.mandatory_failures(DRAFT, flat)))

    def test_validate_fit_refuses_a_body_beyond_its_changes_and_reads_the_reverted_body(self):
        fit = self.fit([GAP])
        bad = copy.deepcopy(fit)
        bad["moves"][0]["families"]["span-law"]["leaves"]["tintAlphaFar1x"]["grid"] = [0.6]
        with self.assertRaisesRegex(D.Refusal, "beyond its permitted changes"):
            D.validate_fit(DRAFT, bad, results(), PROTOCOL)
        ops = [dict(op="add", path=["moves", 1, "points"], to={"ruling": "Decision Log 8"})]
        amended = D.apply_ops(fit, ops)
        D.validate_fit(DRAFT, amended, results(), PROTOCOL, [dict(ops=ops)])
        with self.assertRaisesRegex(D.Refusal, "beyond its permitted changes"):
            D.validate_fit(DRAFT, amended, results(), PROTOCOL, [])

    def test_part2_derives_exactly_the_changes_declare_validates(self):
        """`ladders/part2.py`'s derivation, through `apply_changes` and `validate_fit`, on four synthetic
        readings: both separate (the gap named); operator 2 inert; the body width first; ladder (ii) unmet
        with the transmission narrowed. Neither separating stops it."""
        sys.path.insert(0, str(HERE / "ladders"))
        import part2 as P
        cases = [results(),
                 results(**{"operators/operator 2/separates": False}),
                 results(**{"operators/operator 2/bodyWidthMeets": True, "operators/operator 2/bodyRungs": ["iii-b2"]}),
                 results(**{"operators/2x width/meets": False, "ladders/i/passingL1": ["i-a0.8"]})]
        for res in cases:
            changes = P.changes_from(DRAFT, res, {})
            D.validate_fit(DRAFT, self.fit(changes, res), res, PROTOCOL)
        kinds = [sorted(c["kind"] for c in P.changes_from(DRAFT, r, {})) for r in cases]
        self.assertEqual(kinds, [["name-1x-gap"], ["name-1x-gap", "name-unfitted"], ["body-width-first", "name-1x-gap"],
                                 ["narrow", "strike"]])
        named = P.changes_from(DRAFT, results(), {"F inactive": "a receded fine term"})
        D.validate_fit(DRAFT, self.fit(named), results(), PROTOCOL)
        with self.assertRaisesRegex(SystemExit, "neither operator separates"):
            P.changes_from(DRAFT, results(**{"operators/operator 1/separates": False,
                                             "operators/operator 2/separates": False}), {})


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

    def test_clause_1_evidence_is_pinned_and_required(self):
        """The parent's ruling of 2026-10-06: part 1's `operators` item pins clause 1's evidence by name (both
        recorder specs, their scene fixture, each operator's seven proof records), assemble refuses while any
        is absent, and `check` refuses a declaration that drops one or pins other bytes. Holds whether or not
        operator 2's records have landed: the red cases use a path that never exists."""
        import assemble as A
        self.assertEqual(len(D.CLAUSE1_EVIDENCE), 3 + 2 * len(D.PROOF_RECORDS))
        self.assertTrue({f"{D.REL}/operator-2/{f}" for f in D.PROOF_RECORDS} <= set(D.CLAUSE1_EVIDENCE))
        absent = f"{D.REL}/operator-2/no-such-record.txt"
        self.assertEqual(D.clause1_missing(D.CLAUSE1_EVIDENCE[:3] + (absent,)), [absent])
        with mock.patch.object(D, "CLAUSE1_EVIDENCE", D.CLAUSE1_EVIDENCE + (absent,)), \
                self.assertRaisesRegex(SystemExit, "clause 1's evidence is absent.*no-such-record"):
            A.operators_declared()          # what `build` declares the `operators` item from
        present = tuple(p for p in D.CLAUSE1_EVIDENCE if (D.ROOT / p).is_file())
        with mock.patch.object(D, "CLAUSE1_EVIDENCE", present):
            item = dict(id="operators", declared=A.operators_declared())
            self.assertEqual(sorted(item["declared"]["clause1Evidence"]), sorted(present))
            c = D.Check()
            D.check_operators(c, item)
            self.assertFalse([f for f in c.failures if "clause 1" in f or "pinned bytes" in f], c.failures)
            dropped = copy.deepcopy(item)
            dropped["declared"]["clause1Evidence"].pop(present[0])
            c = D.Check()
            D.check_operators(c, dropped)
            self.assertTrue(any("clause 1's evidence pinned" in f for f in c.failures))
            other = copy.deepcopy(item)
            other["declared"]["clause1Evidence"][present[0]] = "0" * 64
            c = D.Check()
            D.check_operators(c, other)
            self.assertTrue(any(f"{present[0]} is the pinned bytes" in f for f in c.failures))

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

    def test_the_protocols_rung_forms(self):
        ids = [r["id"] for lad in PROTOCOL["ladders"] for r in D.protocol_rungs(lad)]
        self.assertEqual(ids, ["i-a0.7", "i-a0.8", "i-a0.7-f0.2", "i-a0.7-g0.2", "ii-w6-d0.3", "iii-b2", "iii-s2",
                               "iii-q0.5"])
        self.assertEqual(D.lever_ids(PROTOCOL), ids)
        w46 = {"id": "x", "levers": [{"id": "x-a", "slot": "active.dark", "leaf": "optics.regular.tintAlpha",
                                      "values": [0.8, 0.7]}]}
        self.assertEqual([r["id"] for r in D.protocol_rungs(w46)], ["x-a-0.8", "x-a-0.7"])
        self.assertEqual(D.rung_leaves(PROTOCOL)["iii-q0.5"],
                         {("sizeFineTapShare", "receded.dark"), ("sizeFineTapSigma", "receded.dark")})

    def test_x67_admission_and_x68_domains(self):
        self.assertTrue(D.admitted_leaf("receded.dark", "optics.regular.blurSigma"))
        self.assertFalse(D.admitted_leaf("active.dark", "optics.regular.blurSigma"))
        self.assertFalse(D.admitted_leaf("active.dark", "sizeFineTapShare"))
        self.assertTrue(D.admitted_leaf("receded.dark", "sizeFineTapShare"))
        self.assertTrue(D.admitted_leaf("active.dark", "optics.regular.tintAlpha"))          # the snapshot's own
        self.assertFalse(D.admitted_leaf("receded.dark", "sizeHeavyTapSigma2xx"))
        self.assertEqual(D.domains_json(D.W.DOMAINS["receded.dark"]["sizeFineTapSigma"]),
                         [["set", [0]], ["interval", 1.5, 6]])


class CommittedProtocolAndDraft(unittest.TestCase):
    """The committed `ladders/protocol.json` and `fit-declaration-draft.json` pass declare.py's own ladders
    and draft checks (the part-1 items' declared readings computed as `assemble.py` computes them), so the
    three ports agree on one vocabulary and one shape before part 1 is assembled."""

    def test_the_ladders_check_reads_the_committed_protocol_clean(self):
        protocol = json.loads(D.PROTOCOL.read_text())
        cells = json.loads(D.W.LADDER_CELLS.read_text())
        declared = dict(rungs=1 + sum(len(D.protocol_rungs(lad)) for lad in protocol["ladders"]),
                        levers=D.lever_ids(protocol),
                        cellsPerLadder={k: [len(v["rest"]), len(v["inactive"])] for k, v in cells["ladders"].items()})
        c = D.Check()
        D.check_ladders(c, dict(declared=declared))
        self.assertEqual(c.failures, [])
        self.assertEqual(declared["rungs"], 41)
        self.assertEqual({lad["id"]: lad["decides"] for lad in protocol["ladders"]},
                         {"i": ["name-unfitted", "name-target", "narrow", "strike"], "ii": ["name-1x-gap", "strike"],
                          "iii": ["name-unfitted", "body-width-first", "name-target", "strike"], "iv": ["name-target"]})

    def test_the_draft_check_reads_the_committed_draft_clean(self):
        draft = json.loads(D.DRAFT.read_text())
        c = D.Check()
        D.check_draft(c, dict(declared=dict(stages=["stage1", "stage2"], targets=["P", "C rest", "F inactive"],
                                            searchedLeaves=sum(len(f["leaves"]) for m in draft["moves"]
                                                               for f in m["families"].values()))))
        self.assertEqual(c.failures, [])
        operator = {k: s.get("operator") for m in draft["moves"] for f in m["families"].values()
                    for k, s in f["leaves"].items() if s.get("operator")}
        self.assertEqual(operator, {"tintAlphaFar1x": "operator 1", "tintAlphaFar2x": "operator 1",
                                    "sizeFineTapSigma": "operator 2", "sizeFineTapSigma2x": "operator 2",
                                    "sizeFineTapShare": "operator 2"})

    def test_a_draft_leaf_outside_its_x68_domain_or_citing_a_wrong_rung_refuses(self):
        draft = json.loads(D.DRAFT.read_text())
        protocol = json.loads(D.PROTOCOL.read_text())
        bad = copy.deepcopy(draft)
        span = bad["moves"][0]["families"]["span-law"]["leaves"]
        span["tintAlphaFar2x"]["grid"] = [0, 0.7]
        span["sizeOcclusionGain"]["rungs"] = ["iii-b2"]
        got = D.draft_failures(bad, protocol, ["P", "C rest", "F inactive"])
        self.assertTrue(any("tintAlphaFar2x grid [0, 0.7] outside" in f for f in got))
        self.assertTrue(any("cites rung iii-b2, which does not move it" in f for f in got))

    def test_the_second_tap_is_crossed_into_the_span_law(self):
        """Design "The moves": the 2x second tap is crossed WITH the span law's factorial (reviewer-medium,
        W47 G0); the tap as a family swept after it refuses."""
        draft = json.loads(D.DRAFT.read_text())
        protocol = json.loads(D.PROTOCOL.read_text())
        targets = ["P", "C rest", "F inactive"]
        self.assertEqual(D.draft_failures(draft, protocol, targets), [])
        bad = copy.deepcopy(draft)
        stage1 = bad["moves"][0]
        span = stage1["families"]["span-law"]
        tap = {k: span["leaves"].pop(k) for k in ("sizeHeavySecondShare", "sizeHeavySecondSigma2x",
                                                   "sizeHeavySecondShareFar2x")}
        span["factorialGroups"][0]["keys"] = [k for k in span["factorialGroups"][0]["keys"] if k not in tap]
        stage1["families"]["second-tap-2x"] = dict(leaves=tap, factorialGroups=[dict(keys=list(tap), starts=["d0219"])])
        stage1["familyOrder"].insert(1, "second-tap-2x")
        got = D.draft_failures(bad, protocol, targets)
        self.assertEqual(len([f for f in got if "not crossed into the span law's factorial" in f]), 3, got)

    def test_the_parents_rulings_are_stated_by_the_items_they_govern(self):
        """The parent's rulings of 2026-10-06 (protocol.json `rulings`): each stated, verbatim, by its item."""
        protocol = json.loads(D.PROTOCOL.read_text())
        r = {k: v for k, v in protocol["rulings"].items() if not k.startswith("$")}
        items = {"rule": dict(declared=dict(parentRulings={"target-p-pooled": r["target-p-pooled"]})),
                 "ladders": dict(declared=dict(parentRulings={"separation-both-scales": r["separation-both-scales"]})),
                 "draft": dict(declared=dict(parentRulings={k: r[k] for k in ("widened-second-tap-domains",
                                                                              "stage-1-crossed-factorial")}))}
        self.assertEqual(D.ruling_failures(items, protocol), [])
        bad = copy.deepcopy(items)
        bad["ladders"]["declared"]["parentRulings"]["separation-both-scales"] = "a separation at either scale"
        self.assertTrue(any("does not state the parent's ruling 'separation-both-scales'" in f
                            for f in D.ruling_failures(bad, protocol)))
        bad = copy.deepcopy(items)
        del bad["draft"]["declared"]["parentRulings"]["stage-1-crossed-factorial"]
        self.assertTrue(any("'stage-1-crossed-factorial'" in f for f in D.ruling_failures(bad, protocol)))

    def test_stage_2_materialises_the_receded_x64_and_x67_keys(self):
        """W46's `materialiseX64` check, generalised to X64 ∪ X67 (the parent's ruling on reading 10)."""
        draft = json.loads(D.DRAFT.read_text())
        protocol = json.loads(D.PROTOCOL.read_text())
        targets = ["P", "C rest", "F inactive"]
        self.assertEqual(D.draft_failures(draft, protocol, targets), [])
        for change in ({"materialise": None}, {"materialise": "active.dark"},
                       {"materialise": None, "materialiseX64": "receded.dark"},
                       {"materialise": "receded.dark", "materialiseX64": "receded.dark"}):
            bad = copy.deepcopy(draft)
            bad["moves"][1].update(change)
            bad["moves"][1] = {k: v for k, v in bad["moves"][1].items() if v is not None}
            got = D.draft_failures(bad, protocol, targets)
            self.assertTrue(any("stage 2 does not materialise the receded X64 ∪ X67 keys" in f for f in got), change)
        bad = copy.deepcopy(draft)
        bad["moves"][0]["materialise"] = "active.dark"
        self.assertTrue(any("stage 1 materialises a slot" in f
                            for f in D.draft_failures(bad, protocol, targets)))


if __name__ == "__main__":
    unittest.main()
