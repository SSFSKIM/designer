#!/usr/bin/env python3.12
"""W46 G0 (a): the fit driver's and the search's cases (charter clause 1; Design "The moves"; X60,
X62, X64). Nothing here renders: the refusal cases hand the driver a synthetic part 2 in a temporary
directory (never W46's own declaration files, which do not exist yet), and the search cases run with
a runner that renders nothing.

  part 2     an unhashed part 2, a W44/W45 part hash, bytes that are not the hash and a W45 charter
             refuse; `check_overrides` refuses a light slot (X60), an undeclared leaf and an
             out-of-domain value, and admits an X64 key stated at its inherited value
  cells      the scopes per scale (the dark T1 gate cells of the pose plus L1's population of it), no
             referee or holdout, every probe inside the pre-gate whitelist; the objective members
  render     every fit launch passes `--alpha`, one profile per launch, never a holdout set; a census
             refusal is told apart from a partial matrix; an alias is never rendered
  identity   the snapshot start holds; a light move or an undeclared move refuses
  tie rule   a plateau goes to the point nearest the step's start, never to grid order (red case: the
             grid's first point, which W45's `min` kept), then the fewer moved leaves; `decide` the same
             from the stage base; the tie is computed once from the reference rows
  labels     one grammar: every slot and leaf labels inside the builder's pattern, reads back to one
             (slot, leaf), and builds through the real builder (the tracker's upper-case R entry)
  full       renders a point on the renderers that measure it, then reads it (the tracker's entry)
  scales     scale-separable rendering: a 1x lever × 2x lever factorial renders (#1x) + (#2x) scale
             contents, not their product; a `both` leaf splits both scales; a point reads, per scale,
             exactly its renderer's cells; a leaf with no scale refuses
  stage 2    `materialiseX64` starts the receded keys at the stage-1 active's resolved values, never a
             label difference; a partial objective is never ranked
  two points part 2's amendment (Decision Log 9): each branch fixes the receded tintAlpha, sweeps the
             receded scatter and admits only points with no L1 excess (its exception excepted); a step
             with no admissible point is steered to the least excess; A is the better no-exception
             branch, B the exception branch with its cell's numbers; branches off the grid refuse;
             an L1 excess sums both clauses over the pose's measured cells, the exempt left out

    cd packages/calibration/results/2026-10-05-w46-g0-declaration/fit
    python3.12 -B -m unittest test_fit -v
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
import fit  # noqa: E402
import search  # noqa: E402

W = fit.W
TA = "optics.regular.tintAlpha"

SYNTHETIC_PART2 = {
    "schema": "w46-fit-declaration-1",
    "charter": W.CHARTER_PIN,
    "moves": [
        {"id": "stage1", "familyOrder": ["transmission-scatter", "starts"], "families": {
            "transmission-scatter": {"factorial": True, "leaves": {
                TA: {"slot": "active.dark", "domain": [0.5, 0.9], "grid": [0.9, 0.8, 0.7]},
                "sizeScatterFloor": {"slot": "active.dark", "domain": [0.2, 1], "grid": [0.34, 0.6]}}},
            "starts": {"leaves": {
                "sizeScatterRampStartThin2x": {"slot": "active.dark", "domain": [0.3, 1], "grid": [0.46, 0.7]},
                "sizeScatterScaleGain": {"slot": "active.dark", "domain": [-2, 0], "grid": [-2, -1, 0]}}}}},
        {"id": "stage2", "materialiseX64": "receded.dark", "familyOrder": ["transmission", "scatter"], "families": {
            "transmission": {"leaves": {TA: {"slot": "receded.dark", "domain": [0.5, 0.89], "grid": [0.89, 0.7, 0.5]}}},
            "scatter": {"leaves": {
                "sizeScatterRampStartThin2x": {"slot": "receded.dark", "domain": [0.1, 1], "grid": [1, 0.5, 0.1]},
                "sizeHeavySecondShare": {"slot": "receded.dark", "domain": [0, 1], "grid": [0, 0.5]},
                "sizeHeavySecondShareFar2x": {"slot": "receded.dark", "domain": [-1, 0], "grid": [0, -0.25],
                                              "domainLowerIsMinus": "sizeHeavySecondShare"}}}}},
    ],
}


class SyntheticPart2:
    """Point `bindings.PART2` at a temporary hashed copy of `body`."""

    def __init__(self, body=SYNTHETIC_PART2, digest=None):
        self.body, self.digest = body, digest

    def __enter__(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="w46-fit-part2-"))
        part2, digest = self.tmp / "fit-declaration.json", self.tmp / "fit-declaration.sha256"
        raw = (json.dumps(self.body, indent=2) + "\n").encode()
        part2.write_bytes(raw)
        digest.write_text(f"{self.digest or W.sha(raw)}  fit-declaration.json\n")
        self.patches = [mock.patch.object(W, "PART2", part2), mock.patch.object(W, "PART2_DIGEST", digest)]
        for p in self.patches:
            p.start()
        fit._part2 = fit._declared = None
        return self

    def __exit__(self, *exc):
        for p in self.patches:
            p.stop()
        fit._part2 = fit._declared = None
        shutil.rmtree(self.tmp)


class Part2(unittest.TestCase):
    def test_an_unhashed_part_2_refuses(self):
        with SyntheticPart2():
            W.PART2_DIGEST.unlink()
            with self.assertRaisesRegex(W.Refusal, "not hashed"):
                fit.part2()

    def test_other_waves_part_hashes_refuse(self):
        with SyntheticPart2(digest="e6874e02902755c8648e7fcce29568d326544398229c20d08ce7d24ddfdc5433"):
            with self.assertRaisesRegex(W.Refusal, "W44 or W45 part hash"):
                fit.part2()

    def test_bytes_that_are_not_the_hash_refuse(self):
        with SyntheticPart2():
            W.PART2.write_text(W.PART2.read_text() + " ")
            with self.assertRaisesRegex(W.Refusal, "not the hashed"):
                fit.part2()

    def test_a_part_2_naming_w45s_charter_refuses(self):
        body = dict(SYNTHETIC_PART2, charter="docs/doperpowers/specs/2026-10-03-w45-span-selective-texture.md")
        with SyntheticPart2(body):
            with self.assertRaisesRegex(W.Refusal, "charter"):
                fit.part2()

    def test_check_overrides(self):
        with SyntheticPart2():
            fit.check_overrides({"active.dark": {TA: 0.7, "sizeScatterFloor": 0.6}})
            fit.check_overrides({"receded.dark": {"sizeHeavySecondShare": 0.5, "sizeHeavySecondShareFar2x": -0.25}})
            for bad, needle in (({"active.light": {TA: 0.7}}, "X60"),
                                ({"receded.light": {"sizeScatterFloor": 0.5}}, "X60"),
                                ({"active.dark": {"sizeScatterFloor2x": 0.7}}, "not a leaf part 2 declares"),
                                ({"active.dark": {"sizeScatterSpanMax2x": 160}}, "not a leaf part 2 declares"),
                                ({"active.dark": {TA: 0.95}}, "outside its declared domain"),
                                ({"receded.dark": {TA: 0.9}}, "outside its declared domain"),
                                ({"receded.dark": {"sizeHeavySecondShareFar2x": -0.25}}, "joint domain")):
                with self.assertRaisesRegex(W.Refusal, needle, msg=str(bad)):
                    fit.check_overrides(bad)

    def test_an_x64_key_at_its_inherited_value_is_not_a_move(self):
        with SyntheticPart2():
            fit.check_overrides({"active.dark": dict(W.X64["active.dark"])})
            fit.check_overrides({"receded.dark": dict(W.X64["receded.dark"])})
            # After the active floor moved, the receded inherits the moved value: that is its start.
            moved = {"active.dark": {"sizeScatterFloor": 0.6}, "receded.dark": {"sizeScatterFloor": 0.6}}
            fit.check_overrides(moved)
            with self.assertRaisesRegex(W.Refusal, "not a leaf part 2 declares"):
                fit.check_overrides({"active.dark": {"sizeScatterFloor": 0.6}, "receded.dark": {"sizeScatterFloor": 0.34}})

    def test_preflight_refuses_without_part_2(self):
        with mock.patch.object(W, "PART2_DIGEST", W.G0 / "no-such-digest"), self.assertRaises(W.Refusal):
            fit.preflight()


class Cells(unittest.TestCase):
    def test_the_scopes_per_scale(self):
        B, t1, r = fit.cuts()
        plan = W.referee_plan()
        held = plan.referee_cells(plan.load_manifest())
        pregate = set(plan.lists()["pregateProbe"]["scenes"])
        for scale in fit.SCALES:
            rest, inactive = fit.scenes_for("stage1", scale), fit.scenes_for("stage2", scale)
            self.assertEqual((len(rest), len(inactive)), (48, 25))
            self.assertEqual(sorted(rest + inactive), fit.scenes_for("fit", scale))
            for sid in rest + inactive:
                self.assertNotIn((fit.PROFILE[scale], sid), held)
                self.assertNotEqual(B.SCENES.role[sid], "holdout")
                if B.SCENES.role[sid] == "probe":
                    self.assertIn(sid, pregate)
            self.assertTrue(set(fit.l1_population("rest")) <= set(rest))
            self.assertTrue(set(fit.l1_population("inactive")) <= set(inactive))
        self.assertEqual((len(fit.selection_members("stage1")), len(fit.selection_members("stage2"))), (84, 42))

    def test_an_unknown_scope_refuses(self):
        with self.assertRaises(W.Refusal):
            fit.scenes_for("x48")

    def test_the_stage_tie_is_the_reference_rows_once(self):
        fit._ties.clear()
        first = fit.stage_tie_of("stage1")
        self.assertAlmostEqual(first, 0.0365, places=4)
        self.assertAlmostEqual(fit.stage_tie_of("stage2"), 0.0544, places=4)
        with mock.patch.object(W, "REFERENCE", {"dark": "no-such"}):
            self.assertEqual(fit.stage_tie_of("stage1"), first)     # cached: computed once


class Render(unittest.TestCase):
    def test_every_fit_launch_passes_alpha_one_profile_and_no_holdout_set(self):
        for scale in fit.SCALES:
            argv = fit.compare_argv(W.G1_FIT / "candidates" / "x" / "candidate.json", scale, ["a"], Path("/tmp/o"))
            self.assertIn("--alpha", argv)
            self.assertEqual(argv[argv.index("--profile") + 1], fit.PROFILE[scale])
            self.assertNotIn("holdout", argv[argv.index("--set") + 1])

    def test_a_census_refusal_is_told_apart(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "l.txt"
            log.write_text("census w46-fit x: REFUSES (0 annotated, refusals ['browserNotPinned'])\n")
            self.assertTrue(fit.census_refused(log))
            log.write_text("census w46-fit x: passes (0 annotated, refusals [])\nwrote a partial matrix\n")
            self.assertFalse(fit.census_refused(log))

    def test_a_point_renders_only_through_its_scale_twins(self):
        with tempfile.TemporaryDirectory() as tmp:
            g1 = Path(tmp)
            (g1 / "candidates" / "a").mkdir(parents=True)
            (g1 / "candidates" / "a" / "candidate.json").write_text("{}")
            (g1 / "specs").mkdir()
            (g1 / "specs" / "a.json").write_text(json.dumps(dict(label="a", stage="stage1", start="d0219", overrides={})))
            with mock.patch.object(fit, "G1", g1), self.assertRaisesRegex(W.Refusal, "scale twin"):
                fit.render_scale("a", "stage1", 1)


class Identity(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="w46-fit-identity-"))

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def built(self, label, overrides):
        spec = self.tmp / f"{label}.json"
        spec.write_text(json.dumps(dict(label=label, overrides=overrides)))
        got = subprocess.run(["pnpm", "exec", "tsx", str(W.BUILDER), str(spec)], cwd=W.CAL, capture_output=True,
                             text=True, env=dict(os.environ, W46_CANDIDATE_ROOT=str(self.tmp / "c")))
        self.assertEqual(got.returncode, 0, got.stdout + got.stderr)
        return self.tmp / "c" / label

    def test_the_snapshot_start_holds(self):
        folder = self.built("d-start", {})
        got = fit.identity("d-start", folder, dict(overrides={}))
        self.assertTrue(got["holds"])
        for slot in ("active.light", "receded.light"):
            self.assertTrue(got["endpoints"][slot]["patchIdentical"] and got["endpoints"][slot]["digestIdentical"])

    def test_an_undeclared_or_light_move_refuses(self):
        folder = self.built("d-ta", {"active.dark": {TA: 0.7}})
        self.assertTrue(fit.identity("d-ta", folder, dict(overrides={"active.dark": {TA: 0.7}}))["holds"])
        with self.assertRaisesRegex(W.Refusal, "identity"):
            fit.identity("d-ta", folder, dict(overrides={}))
        doc = json.loads((folder / "active.light.json").read_text())
        doc["resolvedMaterialSha256"] = "0" * 16
        (folder / "active.light.json").write_text(json.dumps(doc))
        with self.assertRaisesRegex(W.Refusal, "identity"):
            fit.identity("d-ta", folder, dict(overrides={"active.dark": {TA: 0.7}}))


class TieRule(unittest.TestCase):
    """The declared tie rule (Design "The moves"; the tracker's plateau-by-grid-order entry)."""

    KEYS = [("active.dark", TA, (0.5, 0.9))]

    def test_a_plateau_goes_to_the_point_nearest_the_start_not_to_grid_order(self):
        points = {"g0.9": {"active.dark": {TA: 0.9}}, "g0.8": {"active.dark": {TA: 0.8}},
                  "g0.7": {"active.dark": {TA: 0.7}}, "g0.5": {"active.dark": {TA: 0.5}}}
        objective = {"g0.9": 0.300, "g0.8": 0.301, "g0.7": 0.300, "g0.5": 0.500}.get
        start = {"active.dark": {TA: 0.7}}
        # W45's rule (`min` in grid order) keeps the grid's first indistinguishable point, 0.9 ...
        self.assertEqual(min(points, key=objective), "g0.9")
        # ... the declared rule keeps the one nearest the step's start.
        self.assertEqual(search.choose(list(points), objective, 0.01, start, self.KEYS, points.get), "g0.7")
        # From another start the same plateau resolves the other way: the start decides, not the grid.
        self.assertEqual(search.choose(list(points), objective, 0.01, {"active.dark": {TA: 0.85}},
                                       self.KEYS, points.get), "g0.8")

    def test_a_distinguishable_minimum_wins_whatever_its_distance(self):
        points = {"near": {"active.dark": {TA: 0.9}}, "far": {"active.dark": {TA: 0.5}}}
        objective = {"near": 0.30, "far": 0.20}.get
        self.assertEqual(search.choose(list(points), objective, 0.05, {"active.dark": {TA: 0.9}}, self.KEYS,
                                       points.get), "far")

    def test_then_the_fewer_moved_leaves_then_grid_order(self):
        points = {"two": {"active.dark": {TA: 0.9, "sizeScatterFloor": 0.34}},
                  "one": {"active.dark": {TA: 0.9}}}
        objective = {"two": 0.3, "one": 0.3}.get
        start = {"active.dark": {TA: 0.8}}
        # sizeScatterFloor 0.34 IS the snapshot's value: stating it moves nothing, so the two tie on
        # leaves too, and grid order decides last.
        self.assertEqual(search.choose(list(points), objective, 0.0, start, self.KEYS, points.get), "two")
        points["two"]["active.dark"]["sizeScatterFloor"] = 0.6
        self.assertEqual(search.choose(list(points), objective, 0.0, start, self.KEYS, points.get), "one")


class Labels(unittest.TestCase):
    def test_every_slot_and_leaf_reads_back_to_one(self):
        grammar = fit.LABELS
        seen = {}
        for slot, mark in grammar["slotMark"].items():
            for leaf, short in grammar["short"].items():
                label = search.label_of("d0219", "stage2", {slot: {leaf: -0.25}}, {})
                self.assertRegex(label, grammar["pattern"])
                part = label.split("-", 2)[2]
                self.assertNotIn(part, seen, f"{slot} {leaf} and {seen.get(part)} share a label part")
                seen[part] = (slot, leaf)
                self.assertTrue(part.startswith(f"{mark}{short}"))
        self.assertEqual(search.label_of("d0219", "stage1", {}, {}), "d-s1-base")

    def test_a_leaf_with_no_short_name_refuses(self):
        with self.assertRaisesRegex(W.Refusal, "no short name"):
            search.label_of("d0219", "stage1", {"active.dark": {"sizeScatterSpanMax2x": 160}}, {})

    def test_every_slots_label_builds_through_the_real_builder(self):
        with tempfile.TemporaryDirectory() as tmp:
            for slot in fit.LABELS["slotMark"]:
                every = {slot: {leaf: 0.5 for leaf in fit.LABELS["short"]}}
                label = search.label_of("d0219", "stage2", every, {})
                spec = Path(tmp) / f"{slot}.json"
                spec.write_text(json.dumps(dict(label=label, overrides={})))
                got = subprocess.run(["pnpm", "exec", "tsx", str(W.BUILDER), str(spec)], cwd=W.CAL,
                                     capture_output=True, text=True,
                                     env=dict(os.environ, W46_CANDIDATE_ROOT=str(Path(tmp) / "c")))
                self.assertEqual(got.returncode, 0, f"{label}: {got.stdout + got.stderr}")


class Full(unittest.TestCase):
    def test_full_renders_the_point_through_its_renderers_and_reads_it(self):
        calls = []
        with mock.patch.object(fit, "render", lambda name, scope: calls.append(("render", name, scope)) or 0), \
                mock.patch.object(fit, "read", lambda name: calls.append(("read", name)) or {}):
            search.full("point")
        self.assertEqual(calls, [("render", "point", "rest-of-fit"), ("read", "point")])


class FakeRunner:
    def __init__(self, objective):
        self.store, self.calls, self.objective_fn = {}, [], objective

    def points(self, cands, labels, stage_id, family, start, scope):
        for ov, label in zip(cands, labels):
            fit.check_overrides(ov)
            if label in self.store and self.store[label] != ov:
                raise AssertionError(f"{label} names two points")
            self.store[label] = ov
        self.calls.append(dict(stage=stage_id, family=family, scope=scope, labels=list(labels),
                               cands=json.loads(json.dumps(cands))))
        return list(labels)

    def objective(self, label, scope):
        return self.objective_fn(self.store[label], scope)

    def overrides(self, label):
        return self.store[label]

    def tie(self, scope):
        return 0.0


class Stages(unittest.TestCase):
    def test_stage_1_is_a_factorial_then_coordinate_sweeps(self):
        with SyntheticPart2():
            runner = FakeRunner(lambda ov, scope: abs(fit.resolved_value(ov, "active.dark", TA) - 0.7)
                                + abs(fit.resolved_value(ov, "active.dark", "sizeScatterFloor") - 0.6))
            path = search.compose("stage1", "d0219", {}, 2, runner)
            first = runner.calls[0]
            self.assertEqual((first["family"], len(first["labels"])), ("transmission-scatter", 6))
            self.assertEqual(path["components"][0]["bestOverrides"]["active.dark"], {TA: 0.7, "sizeScatterFloor": 0.6})
            self.assertTrue(all(re.fullmatch(fit.LABELS["pattern"], lab) for c in runner.calls for lab in c["labels"]))

    def test_stage_2_materialises_x64_at_the_stage_1_active_values(self):
        with SyntheticPart2():
            base = {"active.dark": {TA: 0.7, "sizeScatterFloor": 0.6}}
            runner = FakeRunner(lambda ov, scope: abs(fit.resolved_value(ov, "receded.dark", TA) - 0.5))
            path = search.compose("stage2", "d0219", base, 1, runner)
            start = path["base"]["receded.dark"]
            self.assertEqual(start["sizeScatterFloor"], 0.6)                 # the stage-1 active's value
            self.assertEqual(start["sizeScatterFloor2x"], 1)                  # the runtime default it inherits
            self.assertEqual(start["sizeScatterScaleGain"], -2)               # the active snapshot's
            self.assertEqual(set(start), set(W.X64["receded.dark"]))
            first = runner.calls[0]
            self.assertEqual(first["labels"], ["d-s2-rta0.89", "d-s2-rta0.7", "d-s2-rta0.5"])
            for cand in first["cands"]:
                for key, value in start.items():
                    self.assertEqual(cand["receded.dark"][key], value)
            self.assertEqual(path["composed"]["receded.dark"][TA], 0.5)

    def test_decide_applies_the_tie_rule_from_the_stage_base(self):
        with SyntheticPart2(), tempfile.TemporaryDirectory() as tmp:
            g1 = Path(tmp)
            members = {k: {} for k in fit.selection_members("stage1")}
            with mock.patch.object(fit, "G1", g1):
                for label, ta, objective, within in (("a", 0.9, 0.300, "NOT WITHIN"), ("b", 0.7, 0.301, "NOT WITHIN"),
                                                     ("c", 0.5, 0.500, "NOT WITHIN")):
                    ov = {"active.dark": {TA: ta}}
                    (g1 / "specs").mkdir(exist_ok=True)
                    (g1 / "specs" / f"{label}.json").write_text(json.dumps(dict(label=label, start="d0219", overrides=ov)))
                    (g1 / "candidates" / label).mkdir(parents=True)
                    (g1 / "candidates" / label / "summary.json").write_text(json.dumps(dict(
                        overrides=ov, cells=members,
                        stages={"stage1": dict(objective=objective, within=within, notWithin=[])})))
                move = search.move_of("stage1")
                runner = FakeRunner(None)
                runner.tie = lambda scope: 0.01
                got = search.decide(move, "d0219", ["a", "b", "c"], {"active.dark": {TA: 0.7}}, runner)
                self.assertEqual(got["landed"], "b")
                got = search.decide(move, "d0219", ["a", "b", "c"], {}, runner)        # from the snapshot's 0.9
                self.assertEqual(got["landed"], "a")
                # A partial objective is never ranked.
                (g1 / "candidates" / "c" / "summary.json").write_text(json.dumps(dict(
                    overrides={}, cells={}, stages={"stage1": dict(objective=0.1, within="NOT WITHIN", notWithin=[])})))
                with self.assertRaisesRegex(W.Refusal, "UNMEASURED stage1 objective member"):
                    search.decide(move, "d0219", ["a", "b", "c"], {}, runner)


IMPULSE = "impulse__capsule-button__inactive"


def two_point_part2(grid=(0.8, 0.89)) -> dict:
    body = json.loads(json.dumps(SYNTHETIC_PART2))
    stage2 = body["moves"][1]
    stage2["families"]["transmission"]["leaves"][TA]["grid"] = list(grid)
    stage2["families"]["scatter"]["leaves"] = {
        "sizeScatterRampStartThin1x": {"slot": "receded.dark", "domain": [0, 1], "grid": [1, 0.4, 0.1]},
        "sizeScatterFloor": {"slot": "receded.dark", "domain": [0, 1], "grid": [0.34, 0.1]}}
    stage2["points"] = {"ruling": "Decision Log 9", "branchesOf": TA, "family": "scatter", "branches": [
        {"id": "A89", "point": "A", "value": 0.89}, {"id": "A80", "point": "A", "value": 0.8},
        {"id": "B", "point": "B", "value": 0.8, "exempt": [IMPULSE]}]}
    return body


class TwoPointRunner(FakeRunner):
    """A runner that writes each point's spec and summary (so `decide` reads them) and reads an L1
    excess from a function of the point's overrides."""

    def __init__(self, g1, objective, excess):
        super().__init__(objective)
        self.g1, self.excess_fn = g1, excess
        self.members = {k: {} for k in fit.selection_members("stage2")}

    def points(self, cands, labels, stage_id, family, start, scope):
        named = super().points(cands, labels, stage_id, family, start, scope)
        for ov, label in zip(cands, labels):
            (self.g1 / "specs").mkdir(parents=True, exist_ok=True)
            (self.g1 / "specs" / f"{label}.json").write_text(json.dumps(dict(label=label, start=start, overrides=ov)))
            (self.g1 / "candidates" / label).mkdir(parents=True, exist_ok=True)
            (self.g1 / "candidates" / label / "summary.json").write_text(json.dumps(dict(
                overrides=ov, cells=self.members,
                stages={"stage2": dict(objective=self.objective_fn(ov, scope), within="NOT WITHIN", notWithin=[])})))
        return named

    def excess(self, label, pose, exempt=()):
        return 0.0 if IMPULSE in exempt else self.excess_fn(self.store[label])

    def exception(self, label, exempt):
        return [dict(cell=f"x/{IMPULSE}", error=0.074, growth=0.033, absoluteMiss=True, growthMiss=True)]


class TwoPoints(unittest.TestCase):
    def run_stage(self, objective, excess, grid=(0.8, 0.89)):
        with SyntheticPart2(two_point_part2(grid)), tempfile.TemporaryDirectory() as tmp:
            g1 = Path(tmp)
            with mock.patch.object(fit, "G1", g1), mock.patch.object(search, "PATH", g1 / "path"):
                runner = TwoPointRunner(g1, objective, excess)
                base = {"active.dark": {TA: 0.8}}
                (g1 / "specs").mkdir()
                (g1 / "specs" / "s1.json").write_text(json.dumps(dict(label="s1", start="d0219", overrides=base)))
                record = search.stage("stage2", "s1", 2, runner)
                return record, runner, json.loads((g1 / "path" / "d0219" / "stage2.json").read_text())

    @staticmethod
    def ta(ov):
        return fit.resolved_value(ov, "receded.dark", TA)

    @staticmethod
    def thin(ov):
        return fit.resolved_value(ov, "receded.dark", "sizeScatterRampStartThin1x")

    def test_a_dilution_that_passes_at_0_8_is_point_a(self):
        # The objective prefers 0.8 and a thin start of 0.4; L1 passes at 0.8 only at a thin start of 0.1,
        # which still beats every 0.89 point (0.3 against 0.5).
        objective = lambda ov, scope: (0.0 if self.ta(ov) == 0.8 else 0.5) + abs(self.thin(ov) - 0.4)  # noqa: E731
        excess = lambda ov: 0.0 if self.ta(ov) == 0.89 or self.thin(ov) == 0.1 else 0.03  # noqa: E731
        record, runner, written = self.run_stage(objective, excess)
        a80 = record["branches"]["A80"]["landed"]
        self.assertEqual((self.ta(runner.store[a80]), self.thin(runner.store[a80])), (0.8, 0.1))
        self.assertEqual(record["points"]["A"]["landed"], a80)
        self.assertEqual(record["landed"], a80)
        b = record["points"]["B"]["landed"]
        self.assertEqual((self.ta(runner.store[b]), self.thin(runner.store[b])), (0.8, 0.4))
        self.assertEqual(record["points"]["B"]["exception"][0]["growth"], 0.033)
        self.assertEqual(written, record)

    def test_no_admissible_point_at_0_8_leaves_point_a_at_0_89(self):
        objective = lambda ov, scope: (0.1 if self.ta(ov) == 0.8 else 0.3) + abs(self.thin(ov) - 0.4)  # noqa: E731
        excess = lambda ov: 0.0 if self.ta(ov) == 0.89 else 0.01 + self.thin(ov) / 10  # noqa: E731
        record, runner, _ = self.run_stage(objective, excess)
        self.assertIsNone(record["branches"]["A80"]["landed"])
        a = record["points"]["A"]["landed"]
        self.assertEqual((self.ta(runner.store[a]), self.thin(runner.store[a])), (0.89, 0.4))
        # Steered: A80's sweep moved to the least excess (thin 0.1) against the objective's 0.4.
        self.assertEqual(self.thin(record["branches"]["A80"]["swept"]), 0.1)
        b = record["points"]["B"]["landed"]
        self.assertEqual(self.ta(runner.store[b]), 0.8)

    def test_branches_off_the_grid_refuse(self):
        with self.assertRaisesRegex(W.Refusal, "not .*grid"):
            self.run_stage(lambda ov, scope: 0, lambda ov: 0, grid=(0.7, 0.89))

    def test_l1_excess_sums_both_clauses_over_the_poses_measured_cells(self):
        cells = {"1x": [dict(cell=f"p1/{IMPULSE}", error=0.074, growth=0.033, status="MEASURED"),
                        dict(cell="p1/photo__capsule-button__inactive", error=0.05, growth=0.006, status="MEASURED"),
                        dict(cell="p1/photo__capsule-button__rest", error=0.09, growth=0.0, status="MEASURED"),
                        dict(cell="p1/dark-solid__capsule-button__inactive", error=None, growth=None,
                             status="UNMEASURED")],
                 "2x": [dict(cell=f"p2/{IMPULSE}", error=0.05, growth=0.004, status="MEASURED")]}
        with mock.patch.object(search, "summary_of", lambda label: dict(L1cells=cells)):
            self.assertAlmostEqual(search.l1_excess("x", "inactive"), 0.019 + 0.028 + 0.001)
            self.assertAlmostEqual(search.l1_excess("x", "inactive", (IMPULSE,)), 0.001)
            self.assertAlmostEqual(search.l1_excess("x", "rest"), 0.035)
            got = search.exception_reading("x", (IMPULSE,))
            self.assertEqual([(g["absoluteMiss"], g["growthMiss"]) for g in got], [(True, True), (False, False)])


def separable_part2(with_tint: bool) -> dict:
    leaves = {"sizeScatterFloor": {"slot": "active.dark", "domain": [0.2, 1], "grid": [0.34, 0.5, 0.6]},
              "sizeScatterFloor2x": {"slot": "active.dark", "domain": [0.4, 1], "grid": [1, 0.8, 0.6]}}
    if with_tint:
        leaves = {TA: {"slot": "active.dark", "domain": [0.5, 0.9], "grid": [0.9, 0.7]}, **leaves}
    return dict(SYNTHETIC_PART2, moves=[{"id": "stage1", "families": {"f": {"factorial": True, "leaves": leaves}}},
                                        SYNTHETIC_PART2["moves"][1]])


class ScaleSeparable(unittest.TestCase):
    """The real Runner and `compose`, with build, the per-scale render and the per-scale read replaced
    in memory: content is each candidate's moves (non-moves dropped), a render marks its scale's
    cells rendered, and a read writes synthetic T1 cells whose web SD follows the renderer's leaves."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="w46-fit-scales-")).resolve()
        self.g1, self.scratch = self.tmp / "g1", self.tmp / "scratch"
        self.renders, self.inert = [], set()
        B, t1, r = fit.cuts()
        self.B, self.t1 = B, t1
        self.patches = [mock.patch.object(fit, "G1", self.g1), mock.patch.object(fit, "SCRATCH", self.scratch),
                        mock.patch.object(search, "PATH", self.g1 / "path"),
                        mock.patch.object(fit, "build", self.build),
                        mock.patch.object(fit, "render_scale", self.render_scale),
                        mock.patch.object(fit, "read_scale", self.read_scale)]
        for patch in self.patches:
            patch.start()

    def tearDown(self):
        for patch in self.patches:
            patch.stop()
        shutil.rmtree(self.tmp)

    def spec(self, label):
        return json.loads((self.g1 / "specs" / f"{label}.json").read_text())

    def build(self, label):
        folder = self.g1 / "candidates" / label
        if (folder / "candidate.json").exists():
            return
        folder.mkdir(parents=True, exist_ok=True)
        moves = {slot: {k: v for k, v in leaves.items() if fit.resolved_value({}, slot, k) != v
                        and k not in self.inert}
                 for slot, leaves in self.spec(label)["overrides"].items()}
        digest = W.sha(json.dumps({k: v for k, v in moves.items() if v}, sort_keys=True).encode())[:16]
        for slot in W.SLOTS:
            (folder / f"{slot}.json").write_text(json.dumps(dict(resolvedMaterialSha256=digest)))
        (folder / "candidate.json").write_text("{}")

    def render_scale(self, renderer, scope, scale):
        if set(fit.wanted(scope, scale)) <= fit.rendered(renderer)[scale]:
            return 0
        self.assertEqual(self.spec(renderer)["stage"], "scale-twin")
        self.renders.append((renderer, scale))
        out = self.scratch / renderer / f"{scope}-{scale}x"
        out.mkdir(parents=True)
        (out / "matrix.json").write_text(json.dumps(dict(cells=[{"key": {"sceneId": s}} for s in fit.wanted(scope, scale)])))
        return 0

    def read_scale(self, renderer, scale):
        ov = self.spec(renderer)["overrides"]
        f = (1 + abs(fit.resolved_value(ov, "active.dark", "sizeScatterFloor") - 0.6) if scale == 1 else
             1 + abs(fit.resolved_value(ov, "active.dark", "sizeScatterFloor2x") - 0.8))
        f *= 1 + abs(fit.resolved_value(ov, "active.dark", TA) - 0.7)
        cells = []
        for key in fit.selection_members("stage1"):
            sc, sid = key.split("x ", 1)
            if int(sc) != scale:
                continue
            cells.append(dict(profile=fit.PROFILE[scale], tier="webgpu", scene=sid, partition="gate",
                              stratum=self.t1.stratum(sid), pose="rest", spanClass=self.t1.span_class(sid), scale=scale,
                              scheme="dark", native=0.1, reference=0.1, candidate=0.1 * f, bar=0.001, code=0.002,
                              fidelity="miss", change="away", growth=0.0, B=0.002))
        body = dict(renderer=renderer, scale=scale, scopes={k: len(v) for k, v in fit.rendered_scopes(renderer, scale).items()},
                    cells=cells, missing=[], L1=dict(absoluteMisses=[], growthMisses=[], unmeasured=[]), verdicts={})
        fit.scale_summary_path(renderer, scale).write_text(json.dumps(body))
        return body

    def run_stage1(self, with_tint):
        with SyntheticPart2(separable_part2(with_tint)):
            path = search.compose("stage1", "d0219", {}, 1, search.Runner())
        return path

    def test_a_1x_lever_by_a_2x_lever_renders_their_sum_not_their_product(self):
        path = self.run_stage1(with_tint=False)
        points = path["components"][0]["points"]
        self.assertEqual(len(points), 9)
        self.assertEqual(sorted(s for _, s in self.renders), [1, 1, 1, 2, 2, 2])
        self.assertEqual(len(set(self.renders)), 6)
        self.assertEqual(path["composed"]["active.dark"], {"sizeScatterFloor": 0.6, "sizeScatterFloor2x": 0.8})

    def test_a_both_leaf_splits_both_scales(self):
        path = self.run_stage1(with_tint=True)
        self.assertEqual(len(path["components"][0]["points"]), 18)
        self.assertEqual(sum(1 for _, s in self.renders if s == 1), 6)     # tintAlpha 2 × floor 3
        self.assertEqual(sum(1 for _, s in self.renders if s == 2), 6)     # tintAlpha 2 × floor2x 3
        self.assertEqual(path["composed"]["active.dark"][TA], 0.7)

    def test_a_point_reads_its_renderers_cells_per_scale(self):
        path = self.run_stage1(with_tint=False)
        aliases = fit.scale_aliases()
        for label in path["components"][0]["points"]:
            summary = json.loads((self.g1 / "candidates" / label / "summary.json").read_text())
            for scale in fit.SCALES:
                renderer = summary["renderers"][f"{scale}x"]["label"]
                twin = fit.twin_label("d0219", scale, fit.scale_overrides(self.spec(label)["overrides"], scale))
                self.assertEqual(renderer, aliases.get(f"{twin} {scale}x", twin))
                theirs = json.loads(fit.scale_summary_path(renderer, scale).read_text())["cells"]
                mine = [c for c in summary["t1Cells"] if c["scale"] == scale]
                self.assertEqual(mine, theirs)
                self.assertEqual({k for k in summary["cells"] if k.startswith(f"{scale}x ")},
                                 {f"{scale}x {c['scene']}" for c in theirs})

    def test_twins_of_one_content_render_once(self):
        # A leaf the digest drops (as the identity table drops the second tap's widths at share 0)
        # makes every 2x twin one content: the 2x scale renders once and every other twin is measured.
        self.inert = {"sizeScatterFloor2x"}
        self.run_stage1(with_tint=False)
        self.assertEqual(sum(1 for _, s in self.renders if s == 1), 3)
        self.assertEqual(sum(1 for _, s in self.renders if s == 2), 1)
        aliases = fit.scale_aliases()
        self.assertEqual(len([k for k in aliases if k.endswith(" 2x")]), 2)
        self.assertTrue(all(v == self.renders[[s for _, s in self.renders].index(2)][0]
                            for k, v in aliases.items() if k.endswith(" 2x")))

    def test_a_leaf_with_no_scale_refuses(self):
        with self.assertRaisesRegex(W.Refusal, "no scale"):
            fit.leaf_scale("sizeScatterSpanMax2x")
        with self.assertRaisesRegex(W.Refusal, "no scale"):
            fit.scale_overrides({"active.dark": {"sizeScatterSpanMax2x": 160}}, 2)
        self.assertEqual(set(fit.LABELS["scales"]), set(fit.LABELS["short"]))

    def test_the_scale_twins_drop_non_moves_and_the_other_scales_leaves(self):
        ov = {"active.dark": {TA: 0.7, "sizeScatterFloor": 0.6, "sizeScatterFloor2x": 1},
              "receded.dark": dict(W.X64["receded.dark"])}
        one, two = fit.scale_overrides(ov, 1), fit.scale_overrides(ov, 2)
        self.assertEqual(one["active.dark"], {TA: 0.7, "sizeScatterFloor": 0.6})
        self.assertEqual(two, {"active.dark": {TA: 0.7}})                 # floor2x 1 is the inherited default
        self.assertNotIn("receded.dark", two)                              # every receded X64 key at its default


class StartIsACandidate(unittest.TestCase):
    """Every step offers its start, on the grid or off it (the parent's ruling under the tie rule)."""

    def sweep(self, start_ta, objective, tie):
        with SyntheticPart2():
            runner = FakeRunner(objective)
            runner.tie = lambda scope: tie
            move = search.move_of("stage2")
            base = {"receded.dark": {TA: start_ta}}
            best, labels, _ = search.sweep_family(move, "transmission", "d0219", base, base, 1, runner)
        return best, runner.calls[0]

    def test_an_off_grid_start_is_kept_when_it_is_best(self):
        best, call = self.sweep(0.8, lambda ov, scope: abs(fit.resolved_value(ov, "receded.dark", TA) - 0.8), 0.0)
        self.assertEqual(len(call["cands"]), 4)                       # the grid's three and the start
        self.assertEqual(call["cands"][0], {"receded.dark": {TA: 0.8}})
        self.assertEqual(best["receded.dark"][TA], 0.8)

    def test_an_off_grid_start_wins_a_plateau_within_the_tie(self):
        objective = lambda ov, scope: {0.8: 0.305, 0.89: 0.300, 0.7: 0.301, 0.5: 0.500}[  # noqa: E731
            fit.resolved_value(ov, "receded.dark", TA)]
        best, _ = self.sweep(0.8, objective, 0.01)
        self.assertEqual(best["receded.dark"][TA], 0.8)
        best, _ = self.sweep(0.8, objective, 0.001)                    # distinguishable: the minimum moves it
        self.assertEqual(best["receded.dark"][TA], 0.89)

    def test_an_on_grid_start_is_not_duplicated(self):
        _, call = self.sweep(0.7, lambda ov, scope: 0.3, 0.0)
        self.assertEqual(len(call["cands"]), 3)

    def test_a_factorial_step_includes_its_start(self):
        with SyntheticPart2():
            fbody = search.move_of("stage1")["families"]["transmission-scatter"]
            start = {"active.dark": {TA: 0.75}}
            cands = search.step_candidates(fbody, list(fbody["leaves"]), start)
            self.assertEqual(cands[0], start)
            self.assertEqual(len(cands), 1 + 3 * 2)
            on_grid = search.step_candidates(fbody, list(fbody["leaves"]), {"active.dark": {TA: 0.8}})
            self.assertEqual(len(on_grid), 6)                          # floor 0.34 is the snapshot's: on the grid


if __name__ == "__main__":
    unittest.main()
