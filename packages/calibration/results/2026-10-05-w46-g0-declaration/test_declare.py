#!/usr/bin/env python3.12
"""W46 G0 (e): declare.py's red cases (charter clause 1; the brief's item 2: "the amendment record
validated on read"). Nothing here writes a part file: every case works on copies or synthetic bodies.

- **Bindings**: a declaration naming W45's charter or schema, and a digest file carrying a W45 part hash,
  refuse before anything is checked.
- **The amendment record, validated on read**: a field outside the pins-only form (W45's `partOneReadAt`
  among them), a pin of a non-source, a second amendment, a wrong schema — each a failure `check` reports.
- **The validated diff**: `strike` only a lever read flat; `narrow` only to a subset inside the lever's
  non-flat range (for tintAlpha: inside the passing rungs); `name-target` only a target with no lever, with
  its ladder and the operator's shape, removing every draft leaf of that target; nothing when the control
  is not IDENTICAL; no other kind.
- **Pins**: a moved source is a mismatch; a pending item stops the hash; a ladder render stops the hash.

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
DRAFT = json.loads(D.DRAFT.read_text())
PROTOCOL = json.loads(D.PROTOCOL.read_text())


def results(**over):
    """Synthetic ladder results: every lever non-flat on its whole grid, i's passing rungs 0.9/0.8/0.7."""
    ladders = {}
    for lad in PROTOCOL["ladders"]:
        ladders[lad["id"]] = {}
        for lv in lad.get("arms", []) + lad.get("levers", []):
            vals = [lv["shipped"]] + lv["values"]
            entry = dict(flat=False, nonFlatRange=[min(vals), max(vals)])
            if lad["id"] == "i":
                entry["passingRungs"] = [lv["shipped"], 0.8, 0.7]
            ladders[lad["id"]][lv["id"]] = entry
    out = dict(control=dict(verdict="IDENTICAL"), ladders=ladders,
               targets={"P": dict(lever=["i-a"]), "C rest": dict(lever=["ii-fa"]), "F inactive": dict(lever=[])})
    for path, value in over.items():
        node = out
        keys = path.split("/")
        for k in keys[:-1]:
            node = node[k]
        node[keys[-1]] = value
    return out


class Bindings(unittest.TestCase):
    def setUp(self):
        SCRATCH.mkdir(exist_ok=True)

    def tearDown(self):
        shutil.rmtree(SCRATCH, ignore_errors=True)

    def parts(self, declaration=None, digest=None):
        parts = copy.deepcopy(D.PARTS)
        decl = SCRATCH / "declaration.json"
        dig = SCRATCH / "declaration.sha256"
        if declaration is not None:
            decl.write_text(json.dumps(declaration))
        if digest is not None:
            dig.write_text(digest)
        parts["protocol"].update(declaration=decl, digest=dig)
        parts["fit"].update(declaration=SCRATCH / "none.json", digest=SCRATCH / "none.sha256")
        return parts

    def test_another_waves_charter_or_schema(self):
        for body in ({"schema": "w45-declaration-1"},
                     {"schema": "w46-declaration-1", "charter": "docs/doperpowers/specs/2026-10-03-w45-span-selective-texture.md"}):
            with mock.patch.object(D, "PARTS", self.parts(declaration=body)), self.assertRaises(D.Refusal):
                D.bindings()

    def test_another_waves_part_hash(self):
        line = "5630743b7416aedd1910394d4fe7c5eedbaf0ef611516edd1c90043718746e5d  declaration.json\n"
        with mock.patch.object(D, "PARTS", self.parts(digest=line)), self.assertRaisesRegex(D.Refusal, "W45 part hash"):
            D.bindings()


class AmendmentRecord(unittest.TestCase):
    def setUp(self):
        SCRATCH.mkdir(exist_ok=True)
        self.d = {"sources": {"a/b.py": "0" * 64}}

    def tearDown(self):
        shutil.rmtree(SCRATCH, ignore_errors=True)

    def failures(self, body):
        path = SCRATCH / "amendments.json"
        path.write_text(json.dumps(body))
        parts = copy.deepcopy(D.PARTS)
        parts["protocol"]["amendments"] = path
        with mock.patch.object(D, "PARTS", parts):
            return D.amendment_failures("protocol", self.d)

    def entry(self, **extra):
        return dict(n=1, supersedes="x", declarationSha256="y", reason="r", cause="c",
                    pins={"a/b.py": {"from": "0" * 64, "to": "1" * 64}}, **extra)

    def test_a_clean_record_reads_clean(self):
        self.assertEqual(self.failures({"schema": "w46-protocol-amendments-1", "amendments": [self.entry()]}), [])

    def test_a_field_outside_the_pins_only_form(self):
        got = self.failures({"schema": "w46-protocol-amendments-1",
                             "amendments": [self.entry(partOneReadAt={"x": "abc"})]})
        self.assertTrue(any("outside the pins-only form" in f for f in got))

    def test_a_pin_of_a_non_source_and_a_second_amendment_and_a_schema(self):
        e = self.entry()
        e["pins"]["c/d.py"] = {"from": "0", "to": "1"}
        got = self.failures({"schema": "w45-protocol-amendments-1", "amendments": [e, self.entry()]})
        self.assertTrue(any("not a working-tree source" in f for f in got))
        self.assertTrue(any("at most once" in f for f in got))
        self.assertTrue(any("schema" in f for f in got))


class ValidatedDiff(unittest.TestCase):
    def apply(self, changes, res=None):
        return D.apply_changes(DRAFT, changes, res or results(), PROTOCOL)

    def leaf(self, body, move, family, key):
        return D.find_leaf(body, move, family, key)[2]

    def test_no_change_is_the_draft(self):
        self.assertEqual(self.apply([]), DRAFT)

    def test_strike_only_a_flat_lever(self):
        ch = dict(kind="strike", move="stage1", family="thin-and-conditioning", leaf="sizeScatterRampStartThin1x",
                  lever="ii-n1")
        with self.assertRaisesRegex(D.Refusal, "did not read flat"):
            self.apply([ch])
        body = self.apply([ch], results(**{"ladders/ii/ii-n1/flat": True}))
        self.assertIsNone(self.leaf(body, "stage1", "thin-and-conditioning", "sizeScatterRampStartThin1x"))

    def test_strike_prunes_a_factorial_group(self):
        ch = dict(kind="strike", move="stage1", family="transmission-scatter", leaf="sizeHeavyTapSigma", lever="ii-s1")
        body = self.apply([ch], results(**{"ladders/ii/ii-s1/flat": True}))
        group = body["moves"][0]["families"]["transmission-scatter"]["factorialGroups"][0]["keys"]
        self.assertNotIn("sizeHeavyTapSigma", group)
        self.assertEqual(len(group), 4)

    def test_narrow_inside_the_range_only(self):
        ch = dict(kind="narrow", move="stage1", family="transmission-scatter", leaf="sizeScatterFloor", lever="ii-fa",
                  grid=[0.1, 0.2, 0.34])
        body = self.apply([ch], results(**{"ladders/ii/ii-fa/nonFlatRange": [0.1, 0.34]}))
        self.assertEqual(self.leaf(body, "stage1", "transmission-scatter", "sizeScatterFloor")["grid"], [0.1, 0.2, 0.34])
        with self.assertRaisesRegex(D.Refusal, "non-flat range"):
            self.apply([dict(ch, grid=[0.2, 0.5])], results(**{"ladders/ii/ii-fa/nonFlatRange": [0.1, 0.34]}))
        with self.assertRaisesRegex(D.Refusal, "subset"):
            self.apply([dict(ch, grid=[0.15])])

    def test_narrow_the_transmission_to_its_passing_rungs(self):
        ch = dict(kind="narrow", move="stage1", family="transmission-scatter", leaf="optics.regular.tintAlpha",
                  lever="i-a", grid=[0.7, 0.8, 0.9])
        body = self.apply([ch])
        self.assertEqual(self.leaf(body, "stage1", "transmission-scatter", "optics.regular.tintAlpha")["grid"],
                         [0.7, 0.8, 0.9])
        with self.assertRaisesRegex(D.Refusal, "passing rungs"):
            self.apply([dict(ch, grid=[0.6, 0.7])])

    def test_a_lever_that_is_not_the_leafs(self):
        with self.assertRaisesRegex(D.Refusal, "is read by lever"):
            self.apply([dict(kind="strike", move="stage1", family="transmission-scatter", leaf="sizeScatterFloor",
                             lever="ii-fb")])

    def test_name_target_only_without_a_lever(self):
        ch = dict(kind="name-target", target="F inactive", ladder="iii",
                  operatorShape="a receded-only fine term: lowers checkerboard-4/-8 structure without the coarse pitches")
        body = self.apply([ch])
        self.assertEqual(body["notFitted"], [dict(target="F inactive", ladder="iii", operatorShape=ch["operatorShape"])])
        self.assertNotIn("scatter", body["moves"][1]["families"])
        self.assertIn("transmission", body["moves"][1]["families"])
        with self.assertRaisesRegex(D.Refusal, "read a lever"):
            self.apply([dict(ch, target="P", ladder="i")])
        with self.assertRaisesRegex(D.Refusal, "operator's shape"):
            self.apply([dict(ch, operatorShape="")])

    def test_nothing_without_an_identical_control(self):
        with self.assertRaisesRegex(D.Refusal, "control"):
            self.apply([], results(**{"control/verdict": "DIFFERS"}))

    def test_no_other_kind(self):
        with self.assertRaisesRegex(D.Refusal, "decisions"):
            self.apply([dict(kind="inert", move="stage1")])

    def required(self):
        """The changes the synthetic results REQUIRE: both tintAlpha grids to the passing rungs and
        F inactive (no lever) named."""
        return [dict(kind="narrow", move="stage1", family="transmission-scatter", leaf="optics.regular.tintAlpha",
                     lever="i-a", grid=[0.7, 0.8, 0.9]),
                dict(kind="narrow", move="stage2", family="transmission", leaf="optics.regular.tintAlpha",
                     lever="i-r", grid=[0.7, 0.8, 0.89]),
                dict(kind="name-target", target="F inactive", ladder="iii", operatorShape="a receded-only fine term")]

    def fit(self, changes):
        body = D.apply_changes(DRAFT, changes, results(), PROTOCOL)
        body.pop("status", None)
        return dict(body, changes=changes)

    def test_omitting_a_required_change_is_refused(self):
        D.validate_fit(DRAFT, self.fit(self.required()), results(), PROTOCOL)
        for drop, needle in ((0, "passing rungs"), (1, "passing rungs"), (2, "no lever")):
            changes = [c for i, c in enumerate(self.required()) if i != drop]
            with self.assertRaisesRegex(D.Refusal, needle):
                D.validate_fit(DRAFT, self.fit(changes), results(), PROTOCOL)
        with self.assertRaisesRegex(D.Refusal, "read flat"):
            D.validate_fit(DRAFT, self.fit(self.required()), results(**{"ladders/ii/ii-fa/flat": True}), PROTOCOL)

    def test_no_target_with_a_lever_stops_part_2(self):
        res = results(**{"targets/P/lever": [], "targets/C rest/lever": []})
        self.assertTrue(any("closes at G0" in f for f in D.mandatory_failures(DRAFT, res)))

    def test_validate_fit_refuses_a_body_beyond_its_changes(self):
        fit = self.fit(self.required())
        D.validate_fit(DRAFT, fit, results(), PROTOCOL)
        fit = copy.deepcopy(fit)
        fit["moves"][0]["families"]["transmission-scatter"]["leaves"]["sizeScatterFloor"]["grid"] = [0.1]
        with self.assertRaisesRegex(D.Refusal, "beyond its permitted changes"):
            D.validate_fit(DRAFT, fit, results(), PROTOCOL)


class Pins(unittest.TestCase):
    def setUp(self):
        SCRATCH.mkdir(exist_ok=True)

    def tearDown(self):
        shutil.rmtree(SCRATCH, ignore_errors=True)

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
        parts = dict(D.PARTS, protocol=dict(D.PARTS["protocol"], digest=SCRATCH / "absent.sha256"))
        clean = (D.Check(), {"sources": {}}, {})
        with mock.patch.object(D, "PARTS", parts), mock.patch.object(D, "check_protocol", lambda: clean), \
                mock.patch.object(D, "ladder_evidence", lambda: ["ladders/runs.jsonl"]):
            self.assertEqual(D.main(["declare.py", "hash"]), 2)
        pending = (D.Check(), {"sources": {}}, {"x": {"id": "x", "pending": {"on": "a render"}}})
        with mock.patch.object(D, "PARTS", parts), mock.patch.object(D, "check_protocol", lambda: pending), \
                mock.patch.object(D, "ladder_evidence", lambda: []):
            self.assertEqual(D.main(["declare.py", "hash"]), 2)
        self.assertFalse((SCRATCH / "absent.sha256").exists())


if __name__ == "__main__":
    unittest.main()
