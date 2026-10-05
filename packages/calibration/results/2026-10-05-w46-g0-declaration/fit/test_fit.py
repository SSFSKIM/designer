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
  full       resolves the twin that measures a point before it renders (the tracker's entry)
  stage 2    `materialiseX64` starts the receded keys at the stage-1 active's resolved values, never a
             label difference; a partial objective is never ranked

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

    def test_an_alias_is_never_rendered(self):
        with tempfile.TemporaryDirectory() as tmp:
            g1 = Path(tmp)
            (g1 / "candidates" / "a").mkdir(parents=True)
            (g1 / "candidates" / "a" / "candidate.json").write_text("{}")
            (g1 / "aliases.json").write_text(json.dumps({"a": "b"}))
            with mock.patch.object(fit, "G1", g1), self.assertRaisesRegex(W.Refusal, "render the twin"):
                fit.render("a", "stage1")


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
    def test_full_renders_and_reads_the_twin(self):
        calls = []
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "aliases.json").write_text(json.dumps({"alias": "twin"}))
            with mock.patch.object(fit, "G1", Path(tmp)), \
                    mock.patch.object(fit, "render", lambda name, scope: calls.append(("render", name, scope)) or 0), \
                    mock.patch.object(fit, "read", lambda name: calls.append(("read", name)) or {}):
                search.full("alias")
        self.assertEqual(calls, [("render", "twin", "rest-of-fit"), ("read", "twin")])


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


if __name__ == "__main__":
    unittest.main()
