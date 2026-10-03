#!/usr/bin/env python3.12
"""W45 G0 (b): the fit driver's red cases (charter clause 2, X58; clause 5).

Each port refuses W44's bindings and the driver refuses what part 2 does not declare. The refusal
cases hand the driver a synthetic part 2 in a temporary directory (never W45's own declaration
files). The search cases run against the HASHED part 2 (`fit-declaration.json`) with a runner that
renders nothing: the first stage-1 sweep's labels from both starting points (the fixed 1x width
held in every point and never a label difference), a whole stage-1 search, and stage 2's two
components composed in order (`receded` swept from `thin`'s best, its relative grids read off the
active values, the composed point decided on the stage's union and recorded with both components)
(the review of W45 G0 (b)-(e), two P1 findings).

    cd packages/calibration/results/2026-10-03-w45-g0-operator/fit
    python3.12 -B -m unittest test_fit -v
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
import bindings as W  # noqa: E402
import finding  # noqa: E402
import fit  # noqa: E402
import joint  # noqa: E402
import search  # noqa: E402

SYNTHETIC_PART2 = {
    "schema": "w45-fit-declaration-1",
    "charter": W.CHARTER_PATH,
    "moves": [
        {"id": "stage1", "familyOrder": ["deep"], "families": {"deep": {"leaves": {
            "sizeScatterFloor2x": {"slot": "active.light", "domain": [0.5, 1.0], "grid": [0.5, 0.75, 1.0]},
            "sizeScatterSpanMax2x": {"slot": "active.light", "domain": [112, 256], "grid": [112, 128, 160, 192, 256]},
            "sizeHeavySecondShare": {"slot": "active.light", "domain": [0, 1], "grid": [0, 0.5, 1]},
            "sizeHeavySecondSigma2x": {"slot": "active.light", "domain": [1.5, 6], "grid": [2, 3]},
            "sizeHeavySecondShareFar2x": {"slot": "active.light", "domain": [-1, 0], "grid": [0, -0.5, -1]},
            "sizeScatterRampStartThick2x+sizeScatterRampStartFar2x": {
                "slot": "active.light", "tied": True, "domain": [0.05, 0.21], "grid": [0.05, 0.1, 0.21]}},
            "fixed": {"sizeHeavySecondSigma": {"slot": "active.light", "value": 0}}}}},
        {"id": "stage2", "families": {
            "start": {"scope": "stage2-thin", "leaves": {
                "sizeScatterRampStartThin2x": {"slot": "active.light", "domain": [0.46, 0.95], "grid": [0.46, 0.8]}}},
            "receded": {"scope": "stage2-receded", "leaves": {
                "sizeScatterRampStartThin2x": {"slot": "receded.light", "domain": [0.1, 0.7], "grid": [0.1, 0.4]},
                "sizeHeavySecondShare": {"slot": "receded.light", "domain": [0, 1], "domainRelativeTo": "active",
                                         "grid": [0, 0.5, 1]},
                "sizeHeavySecondShareFar2x": {"slot": "receded.light", "domain": [-1, 0], "grid": [0, -0.5]}}}}},
    ],
}


class Bindings(unittest.TestCase):
    def test_the_shared_inputs_hold_their_pins(self):
        self.assertEqual(W.verify_shared(), [])

    def test_a_moved_shared_input_refuses(self):
        moved = dict(W.SHARED)
        first = next(iter(moved))
        moved[first] = "0" * 64
        with mock.patch.object(W, "SHARED", moved), self.assertRaises(W.Refusal):
            W.require_shared()

    def test_w44_evidence_scratch_and_stage_refuse(self):
        for path in (W.RESULTS / "2026-10-03-w44-g1-refit/fit/candidates/m3-t0.1/candidate.json",
                     W.RESULTS / "2026-10-03-w44-g0-declaration",
                     Path.home() / "vitrea-w44/g1-scratch/fit/m3-t0.1/move3",
                     Path.home() / "vitrea-w44/g1-stage-light"):
            with self.assertRaises(W.Refusal, msg=str(path)):
                W.refuse_w44_path(path, "red case")
        self.assertEqual(W.refuse_w44_path(W.G1, "G1"), W.G1.resolve())
        self.assertEqual(W.refuse_w44_path(W.FIT_SCRATCH, "scratch"), W.FIT_SCRATCH.resolve())

    def test_w44_part_hashes_refuse(self):
        for digest in W.W44_PART_HASHES:
            with self.assertRaises(W.Refusal):
                W.refuse_w44_hash(digest, "red case")
        self.assertIsNone(W.refuse_w44_hash(None, "unhashed"))


class Part2(unittest.TestCase):
    """Run against a synthetic part 2 in a temporary directory, never W45's own files."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="w45-fit-part2-"))
        self.part2, self.digest = self.tmp / "fit-declaration.json", self.tmp / "fit-declaration.sha256"
        self.patches = [mock.patch.object(W, "PART2", self.part2), mock.patch.object(W, "PART2_DIGEST", self.digest)]
        for p in self.patches:
            p.start()
        fit._part2 = fit._declared = None

    def tearDown(self):
        for p in self.patches:
            p.stop()
        fit._part2 = fit._declared = None
        shutil.rmtree(self.tmp)

    def write(self, body: dict, digest: str | None = None):
        raw = (json.dumps(body, indent=2) + "\n").encode()
        self.part2.write_bytes(raw)
        self.digest.write_text(f"{digest or W.sha(raw)}  fit-declaration.json\n")

    def test_an_unhashed_part_2_refuses(self):
        self.part2.write_text(json.dumps(SYNTHETIC_PART2))
        with self.assertRaisesRegex(W.Refusal, "not hashed"):
            fit.part2()

    def test_a_w44_part_hash_refuses(self):
        self.write(SYNTHETIC_PART2, digest="c04227e9240a0f1e890aef5c6529db412783864305b7ddbc125a00923c771175")
        with self.assertRaisesRegex(W.Refusal, "W44 part hash"):
            fit.part2()

    def test_bytes_that_are_not_the_hash_refuse(self):
        self.write(SYNTHETIC_PART2)
        self.part2.write_text(self.part2.read_text() + " ")
        with self.assertRaisesRegex(W.Refusal, "not the hashed"):
            fit.part2()

    def test_a_part_2_naming_w44s_charter_refuses(self):
        self.write(dict(SYNTHETIC_PART2, charter=W.W44_CHARTER))
        with self.assertRaisesRegex(W.Refusal, "W44's charter"):
            fit.part2()

    def test_the_operator_and_the_span_top_are_admitted_where_declared(self):
        self.write(SYNTHETIC_PART2)
        fit.check_overrides({"active.light": {"sizeHeavySecondShareFar2x": -0.5, "sizeScatterSpanMax2x": 160,
                                              "sizeHeavySecondShare": 0.75, "sizeHeavySecondSigma2x": 3,
                                              "sizeScatterRampStartThick2x": 0.1, "sizeScatterRampStartFar2x": 0.1,
                                              "sizeHeavySecondSigma": 0},
                             "receded.light": {"sizeHeavySecondShareFar2x": -0.25}})
        # The receded share's domain is relative to the active share.
        fit.check_overrides({"active.light": {"sizeHeavySecondShare": 0.5},
                             "receded.light": {"sizeHeavySecondShare": 0.25}})

    def test_what_part_2_does_not_declare_refuses(self):
        self.write(SYNTHETIC_PART2)
        cases = [
            ({"active.dark": {"sizeScatterFloor2x": 1}}, "dark endpoints never move"),
            ({"receded.dark": {"sizeHeavySecondShareFar2x": -0.5}}, "dark endpoints never move"),
            ({"active.light": {"sizeScatterHeavyShareThick2x": 0.1}}, "not a leaf part 2 declares"),
            ({"receded.light": {"sizeScatterSpanMax2x": 160}}, "not a leaf part 2 declares"),
            ({"active.light": {"sizeHeavySecondShareFar2x": 0.5}}, "outside its declared domain"),
            ({"active.light": {"sizeScatterSpanMax2x": 96}}, "outside its declared domain"),
            ({"active.light": {"sizeHeavySecondSigma": 3}}, "held at 0"),
            ({"active.light": {"sizeHeavySecondShare": 0.5}, "receded.light": {"sizeHeavySecondShare": 0.75}},
             "outside its declared domain"),
        ]
        for overrides, needle in cases:
            with self.assertRaisesRegex(W.Refusal, needle, msg=json.dumps(overrides)):
                fit.check_overrides(overrides)

    def test_a_family_scope_must_be_a_charter_stage(self):
        self.write(SYNTHETIC_PART2)
        move = fit.part2()["moves"][1]
        self.assertEqual(fit.scope_of(move, "start"), "stage2-thin")
        self.assertEqual(fit.scope_of(fit.part2()["moves"][0], "deep"), "stage1")
        with self.assertRaisesRegex(W.Refusal, "is not one of"):
            fit.scope_of(dict(move, families={"x": {"leaves": {}}}), "x")

    def test_relative_grids_follow_the_active_value(self):
        self.write(SYNTHETIC_PART2)
        spec = fit.part2()["moves"][1]["families"]["receded"]["leaves"]["sizeHeavySecondShare"]
        self.assertEqual(search.grid_of(spec, {"active.light": {"sizeHeavySecondShare": 0.5}}, "sizeHeavySecondShare"),
                         [0, 0.25, 0.5])
        self.assertEqual(search.grid_of(spec, {}, "sizeHeavySecondShare"), [0])


class Cells(unittest.TestCase):
    def test_the_scopes_partition_the_fit_cells_and_hold_no_referee_or_holdout(self):
        B, t1 = W.load_cuts()
        plan = W.referee_plan()
        held = plan.referee_cells(plan.load_manifest())
        pregate = set(plan.lists()["pregateProbe"]["scenes"])
        scopes = {s: set(fit.scenes_for(s)) for s in fit.SCOPES}
        self.assertEqual(set().union(*scopes.values()), set(fit.scenes_for("fit")))
        self.assertEqual(sum(len(v) for v in scopes.values()), len(fit.scenes_for("fit")))
        for scale in (1, 2):
            for sid in fit.scenes_for("fit", scale):
                self.assertNotIn((fit.PROFILE[scale], sid), held)
                self.assertNotEqual(B.SCENES.role[sid], "holdout")
                if B.SCENES.role[sid] == "probe":
                    self.assertIn(sid, pregate)
        # The two inactive twins the charter names as referees are never fit cells.
        for sid in ("checkerboard-8__rrect-lg__inactive", "checkerboard-32__rrect-lg__inactive"):
            self.assertNotIn(sid, fit.scenes_for("fit"))

    def test_an_unknown_scope_refuses(self):
        with self.assertRaisesRegex(W.Refusal, "is not one of"):
            fit.scenes_for("move1")


class Render(unittest.TestCase):
    def test_every_fit_render_passes_alpha_and_never_a_holdout_set(self):
        argv = fit.compare_argv(W.G1 / "candidates" / "x" / "candidate.json", 2, ["a", "b"], Path("/tmp/out"))
        self.assertIn("--alpha", argv)
        self.assertIn("--write-partial", argv)
        self.assertEqual(argv[argv.index("--set") + 1], "calibration,validation,recorded,probe")
        self.assertEqual(argv[argv.index("--scene") + 1], "a,b")

    def test_a_w44_candidate_root_refuses(self):
        with self.assertRaises(W.Refusal):
            fit.builder_env(W.RESULTS / "2026-10-03-w44-g1-refit/fit/candidates")
        self.assertIn("W45_CANDIDATE_ROOT", fit.builder_env(W.G1 / "candidates"))

    def test_a_census_refusal_is_told_apart_from_a_partial_matrix(self):
        tmp = Path(tempfile.mkdtemp(prefix="w45-fit-log-"))
        try:
            refused, partial = tmp / "a.txt", tmp / "b.txt"
            refused.write_text("census w45-fit x/stage1: REFUSES (7 annotated, refusals ['captureProcessPresent'])\n")
            partial.write_text("census w45-fit x/stage1: passes (7 annotated, refusals [])\ncompare: 2 cells failed\n")
            self.assertTrue(fit.census_refused(refused))
            self.assertFalse(fit.census_refused(partial))
        finally:
            shutil.rmtree(tmp)


class StageRender(unittest.TestCase):
    """A stage's render after one of its parts draws the rest of its union, and nothing twice."""

    def test_the_rest_of_stage_2_after_its_receded_part(self):
        tmp = Path(tempfile.mkdtemp(prefix="w45-fit-render-")).resolve()
        try:
            (tmp / "g1" / "candidates" / "j-x").mkdir(parents=True)
            (tmp / "g1" / "candidates" / "j-x" / "candidate.json").write_text("{}")
            receded = set(fit.scenes_for("stage2-receded"))
            argvs = []

            def fake_run(argv, **kwargs):
                argvs.append(argv)
                return subprocess.CompletedProcess(argv, 0)

            with mock.patch.object(fit, "G1", tmp / "g1"), mock.patch.object(fit, "SCRATCH", tmp / "scratch"), \
                    mock.patch.object(fit, "rendered_scopes", lambda label: {"stage2-receded": receded}), \
                    mock.patch.object(fit, "CAL", tmp), mock.patch.object(fit.subprocess, "run", fake_run):
                self.assertEqual(fit.render("j-x", "stage2"), 0)
                self.assertEqual(fit.render("j-x", "stage2-receded"), 0)     # already rendered: no launch
            self.assertEqual(len(argvs), 1)
            scenes = argvs[0][argvs[0].index("--scene") + 1].split(",")
            self.assertEqual(sorted(scenes), fit.scenes_for("stage2-thin"))
            self.assertIn("--alpha", argvs[0])
            self.assertTrue(argvs[0][0].endswith("with-gpu.sh"))
        finally:
            shutil.rmtree(tmp)


class Starts(unittest.TestCase):
    def test_the_joint_point_is_admitted_by_its_declaration_hash(self):
        overrides = fit.joint_overrides()
        self.assertEqual(overrides["active.light"]["sizeHeavySecondShare"], 0.5)
        self.assertEqual(overrides["receded.light"]["sizeScatterRampStartThin2x"], 0.1)

    def test_another_declaration_hash_refuses(self):
        with mock.patch.dict(W.JOINT, declarationSha256="0" * 64), self.assertRaisesRegex(W.Refusal, "not the declared"):
            fit.joint_overrides()

    def test_an_undeclared_start_refuses(self):
        with self.assertRaisesRegex(W.Refusal, "not one of"):
            fit.start("w44-joint")


class Identity(unittest.TestCase):
    """The candidate identity on a real W45 build (the builder into a scratch root)."""

    @classmethod
    def setUpClass(cls):
        cls.root = Path(tempfile.mkdtemp(prefix="w45-fit-identity-"))
        cls.folders = {}
        for label, overrides in (("c05-control", {}),
                                 ("operator", {"active.light": {"sizeHeavySecondShare": 0.5,
                                                                "sizeHeavySecondSigma2x": 3,
                                                                "sizeHeavySecondShareFar2x": -0.5},
                                               "receded.light": {"sizeHeavySecondShareFar2x": -0.25}})):
            spec = cls.root / f"{label}.json"
            spec.write_text(json.dumps(dict(label=label, note="test_fit", overrides=overrides)))
            env = dict(os.environ, W45_CANDIDATE_ROOT=str(cls.root / "out"))
            got = subprocess.run(["pnpm", "exec", "tsx", str(W.BUILDER), str(spec)], cwd=W.CAL, env=env,
                                 capture_output=True, text=True)
            assert got.returncode == 0, got.stdout + got.stderr
            cls.folders[label] = (cls.root / "out" / label, overrides)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.root)

    def test_c05_itself_holds_with_no_override(self):
        folder, overrides = self.folders["c05-control"]
        got = fit.identity("c05-control", folder, dict(overrides=overrides))
        self.assertTrue(got["holds"])
        for slot, e in got["endpoints"].items():
            self.assertEqual(e["digest"], e["c05Digest"], slot)

    def test_the_operator_holds_where_declared_and_refuses_where_not(self):
        folder, overrides = self.folders["operator"]
        got = fit.identity("operator", folder, dict(overrides=overrides))
        self.assertEqual(got["endpoints"]["active.light"]["moved"],
                         ["sizeHeavySecondShare", "sizeHeavySecondShareFar2x", "sizeHeavySecondSigma2x"])
        self.assertEqual(got["endpoints"]["receded.light"]["moved"], ["sizeHeavySecondShareFar2x"])
        undeclared = json.loads(json.dumps(overrides))
        del undeclared["receded.light"]
        with self.assertRaisesRegex(W.Refusal, "identity operator"):
            fit.identity("operator", folder, dict(overrides=undeclared))


class Budget(unittest.TestCase):
    """finding.py reads W45's per-cell clause off a cut cell: growth past B, past 3B; a T cell's T1-low."""

    def cell(self, g, B=0.004, stratum="F", low=None):
        c = dict(stratum=stratum, growth=g, B=B)
        if low is not None:
            c["bands"] = {"low": dict(growth=low, B=B), "fine": dict(growth=-1, B=B)}
        return c

    def test_growth_alone(self):
        self.assertIsNone(finding.spend(self.cell(0.004)))
        self.assertEqual(finding.spend(self.cell(0.0041)), "past B")
        self.assertEqual(finding.spend(self.cell(0.012)), "past B")
        self.assertEqual(finding.spend(self.cell(0.0121)), "past 3B")
        self.assertIsNone(finding.spend(self.cell(-0.05)))

    def test_a_t_cell_reads_its_low_band(self):
        self.assertEqual(finding.spend(self.cell(-1, stratum="T", low=0.008)), "past B")
        self.assertIsNone(finding.spend(self.cell(1, stratum="T", low=0.001)))
        self.assertIsNone(finding.spend(dict(stratum="T", growth=1, B=0.004)))


class Decide(unittest.TestCase):
    """Part 2's selection within a stage, on synthetic summaries in a temporary G1 directory."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="w45-fit-decide-"))
        self.patches = [mock.patch.object(fit, "G1", self.tmp), mock.patch.object(search, "PATH", self.tmp / "path")]
        for p in self.patches:
            p.start()
        self.members = {sid: {} for sid in fit.scenes_for("stage1")}

    def tearDown(self):
        for p in self.patches:
            p.stop()
        shutil.rmtree(self.tmp)

    def point(self, label, objective, within, leaves, drop=None):
        cells = {k: v for k, v in self.members.items() if k != drop}
        folder = self.tmp / "candidates" / label
        folder.mkdir(parents=True)
        overrides = {"active.light": {f"leaf{i}": 0 for i in range(leaves)}}
        (folder / "summary.json").write_text(json.dumps(dict(
            overrides=overrides, cells=cells,
            stages={"stage1": dict(objective=objective, within=within, notWithin=[], tie=0.01)})))

    MOVE = {"id": "stage1", "families": {"deep": {"leaves": {}}}}

    def test_the_within_point_with_the_smallest_objective_lands(self):
        self.point("a1", 0.10, "NOT WITHIN", 1)
        self.point("b1", 0.20, "WITHIN", 2)
        self.point("b2", 0.15, "WITHIN", 3)
        self.assertEqual(search.decide(self.MOVE, "c05", ["a1", "b1", "b2"])["landed"], "b2")

    def test_with_nothing_within_the_tie_goes_to_the_fewer_moved_leaves(self):
        self.point("a1", 0.100, "NOT WITHIN", 3)
        self.point("b1", 0.105, "NOT WITHIN", 1)
        self.point("b2", 0.300, "NOT WITHIN", 0)
        got = search.decide(self.MOVE, "joint", ["a1", "b1", "b2"])
        self.assertEqual((got["landed"], got["within"]), ("b1", "NOT WITHIN"))

    def test_a_partial_objective_is_never_ranked(self):
        self.point("a1", 0.10, "NOT WITHIN", 1, drop=next(iter(self.members)))
        with self.assertRaisesRegex(W.Refusal, "UNMEASURED objective member"):
            search.decide(self.MOVE, "c05", ["a1"])


class FakeRunner:
    """Renders nothing: records every point the procedure asks for, refuses two points under one
    label, checks each against the committed part 2, and scores it with a synthetic objective."""

    def __init__(self, objective):
        self.store, self.calls, self.objective_fn = {}, [], objective

    def points(self, cands, labels, stage_id, family, start, scope):
        for ov, label in zip(cands, labels):
            fit.check_overrides(ov)
            if label in self.store and self.store[label] != ov:
                raise AssertionError(f"{label} names two points: {self.store[label]} and {ov}")
            self.store[label] = ov
        self.calls.append(dict(stage=stage_id, family=family, scope=scope, labels=list(labels),
                               cands=json.loads(json.dumps(cands))))
        return list(labels)

    def objective(self, label, scope):
        return self.objective_fn(self.store[label], scope)

    def overrides(self, label):
        return self.store[label]


def distance(target: dict):
    """A synthetic objective: how far a point's leaves are from `target` {(slot, leaf): value}."""
    def objective(ov, scope):
        return sum(abs(ov.get(slot, {}).get(leaf, 0) - value) for (slot, leaf), value in target.items())
    return objective


class CommittedPart2(unittest.TestCase):
    """The search against the HASHED part 2 (`fit-declaration.json`), with a runner that renders nothing."""

    def setUp(self):
        fit._part2 = fit._declared = None
        self.part2 = fit.part2()
        self.joint = fit.joint_overrides()

    def test_part_2_is_the_hashed_one_and_its_scopes_are_the_charters(self):
        self.assertEqual(W.sha(W.PART2.read_bytes()), W.part_hash(2))
        moves = {m["id"]: m for m in self.part2["moves"]}
        self.assertEqual(sorted(moves), ["stage1", "stage2"])
        self.assertEqual(fit.scope_of(moves["stage1"], "deep"), "stage1")
        self.assertEqual(moves["stage2"]["familyOrder"], ["thin", "receded"])
        self.assertEqual(fit.scope_of(moves["stage2"], "thin"), "stage2-thin")
        self.assertEqual(fit.scope_of(moves["stage2"], "receded"), "stage2-receded")
        self.assertEqual(set(fit.scenes_for("stage2")),
                         set(fit.scenes_for("stage2-thin")) | set(fit.scenes_for("stage2-receded")))

    def test_the_first_stage_1_sweep_from_both_starts(self):
        move = search.move_of("stage1")
        grid = move["families"]["deep"]["leaves"]["sizeScatterFloor2x"]["grid"]
        for start, base, prefix in (("c05", {}, "c-s1"), ("joint", self.joint, "j-s1")):
            runner = FakeRunner(distance({}))
            search.sweep_family(move, "deep", start, base, base, 1, runner)
            first = runner.calls[0]
            self.assertEqual(first["scope"], "stage1")
            expected = [f"{prefix}-base" if base.get("active.light", {}).get("sizeScatterFloor2x") == v
                        else f"{prefix}-fl{v:g}" for v in grid]
            self.assertEqual(first["labels"], expected, start)
            for ov in first["cands"]:
                # The fixed 1x width is held in every point and never a label difference.
                self.assertEqual(ov["active.light"]["sizeHeavySecondSigma"], 0)
            self.assertEqual(len(runner.calls), len(move["families"]["deep"]["leaves"]), start)

    def test_a_whole_stage_1_search_is_labelled_and_declared_from_both_starts(self):
        move = search.move_of("stage1")
        target = {("active.light", "sizeScatterFloor2x"): 0.9, ("active.light", "sizeScatterSpanMax2x"): 160,
                  ("active.light", "sizeHeavySecondShare"): 0.75, ("active.light", "sizeHeavySecondSigma2x"): 3,
                  ("active.light", "sizeHeavySecondShareFar2x"): -0.5,
                  ("active.light", "sizeScatterRampStartThick2x"): 0.1}
        for start, base in (("c05", {}), ("joint", self.joint)):
            runner = FakeRunner(distance(target))
            best, labels, _ = search.sweep_family(move, "deep", start, base, base, 2, runner)
            for (slot, leaf), value in target.items():
                self.assertEqual(best[slot][leaf], value, (start, leaf))
            self.assertEqual(best["active.light"]["sizeScatterRampStartFar2x"], 0.1)   # the tied pair
            self.assertTrue(all(label.startswith(f"{start[0]}-s1-") for label in labels))

    def test_stage_2_composes_its_components_in_order(self):
        stage1_point = search.merged(self.joint, {"active.light": {
            "sizeHeavySecondSigma": 0, "sizeHeavySecondShareFar2x": -0.5, "sizeScatterSpanMax2x": 160}})
        target = {("active.light", "sizeScatterRampStartThin2x"): 0.65,
                  ("receded.light", "sizeScatterRampStartThin2x"): 0.3,
                  ("receded.light", "sizeHeavySecondShare"): 0.25,
                  ("receded.light", "sizeHeavySecondShareFar2x"): -0.25}
        runner = FakeRunner(distance(target))
        path = search.compose("stage2", "joint", stage1_point, 2, runner)
        thin, receded = path["components"]
        self.assertEqual((thin["family"], thin["scope"]), ("thin", "stage2-thin"))
        self.assertEqual((receded["family"], receded["scope"]), ("receded", "stage2-receded"))
        self.assertEqual(thin["from_"], stage1_point)
        self.assertEqual(thin["bestOverrides"]["active.light"]["sizeScatterRampStartThin2x"], 0.65)
        # The receded sweep starts from the thin component's best, and every point it asks for keeps it.
        self.assertEqual(receded["from_"], thin["bestOverrides"])
        for call in runner.calls:
            if call["family"] == "receded":
                self.assertEqual(call["scope"], "stage2-receded")
                for ov in call["cands"]:
                    self.assertEqual(ov["active.light"]["sizeScatterRampStartThin2x"], 0.65)
        # The relative grids read the active values the stage-1 point carries.
        grids = {tuple(sorted({leaf for ov in c["cands"] for leaf in ov.get("receded.light", {})})): c
                 for c in runner.calls if c["family"] == "receded"}
        shares = sorted({ov["receded.light"].get("sizeHeavySecondShare") for c in runner.calls
                         if c["family"] == "receded" for ov in c["cands"]} - {None})
        self.assertEqual(shares, [0, 0.125, 0.25, 0.375, 0.5])
        deltas = sorted({ov["receded.light"].get("sizeHeavySecondShareFar2x") for c in runner.calls
                         if c["family"] == "receded" for ov in c["cands"]} - {None})
        self.assertEqual(deltas, [-0.5, -0.25, 0])
        self.assertTrue(grids)
        # The composed point carries both components.
        composed = path["composed"]
        self.assertEqual(composed["active.light"]["sizeScatterRampStartThin2x"], 0.65)
        for (slot, leaf), value in target.items():
            self.assertEqual(composed[slot][leaf], value, leaf)
        for leaf in ("sizeScatterFloor2x", "sizeHeavySecondShare", "sizeHeavySecondShareFar2x", "sizeScatterSpanMax2x"):
            self.assertEqual(composed["active.light"][leaf], stage1_point["active.light"][leaf], leaf)

    def test_stage_2_is_decided_on_its_union_and_records_both_components(self):
        tmp = Path(tempfile.mkdtemp(prefix="w45-fit-stage-"))
        try:
            base = search.merged(self.joint, {"active.light": {"sizeHeavySecondSigma": 0}})
            runner = FakeRunner(distance({("active.light", "sizeScatterRampStartThin2x"): 0.55,
                                          ("receded.light", "sizeScatterRampStartThin2x"): 0.2}))
            seen = {}

            def fake_decide(move, start, labels):
                seen.update(stage=move["id"], labels=list(labels))
                return dict(stage=move["id"], start=start, landed=labels[0], within="NOT WITHIN", how="test", points=[])

            with mock.patch.object(search, "PATH", tmp), \
                    mock.patch.object(search, "spec_of", lambda label: dict(start="joint", overrides=base)), \
                    mock.patch.object(search, "decide", fake_decide):
                record = search.stage("stage2", "joint", "j-s1-landed", 1, runner)
            last = runner.calls[-1]
            self.assertEqual((last["family"], last["scope"]), ("composed", "stage2"))
            self.assertEqual(last["cands"], [record["composed"]])
            self.assertEqual(seen, dict(stage="stage2", labels=last["labels"]))
            written = json.loads((tmp / "joint" / "stage2.json").read_text())
            self.assertEqual([c["family"] for c in written["components"]], ["thin", "receded"])
            self.assertEqual(written["components"][1]["from"], written["components"][0]["bestOverrides"])
            self.assertEqual(written["composed"]["active.light"]["sizeScatterRampStartThin2x"], 0.55)
            self.assertEqual(written["composed"]["receded.light"]["sizeScatterRampStartThin2x"], 0.2)
            self.assertEqual(written["base"], "j-s1-landed")
        finally:
            shutil.rmtree(tmp)


class Paths(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="w45-fit-path-"))

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_a_lineage_with_no_decision_refuses(self):
        with mock.patch.object(joint, "PATH", self.tmp), self.assertRaisesRegex(W.Refusal, "has no decision"):
            joint.path_of("c05", ["stage1", "stage2"])

    def test_stage_records_that_do_not_chain_refuse(self):
        (self.tmp / "c05").mkdir()
        (self.tmp / "c05" / "stage1.json").write_text(json.dumps(dict(stage="stage1", start="c05", base="start-c05",
                                                                     landed="c-s1-fl0.9")))
        (self.tmp / "c05" / "stage2.json").write_text(json.dumps(dict(stage="stage2", start="c05", base="c-s1-other",
                                                                     landed="c-s2-t0.65")))
        with mock.patch.object(joint, "PATH", self.tmp), self.assertRaisesRegex(W.Refusal, "not the previous"):
            joint.path_of("c05", ["stage1", "stage2"])

    def test_joint_reads_part_2s_two_stages_by_default(self):
        self.assertIn('"stage1,stage2"', (HERE / "joint.py").read_text())

    def test_labels_carry_the_lineage_and_the_stage(self):
        base = {"active.light": {"sizeScatterFloor2x": 1.0}}
        ov = {"active.light": {"sizeScatterFloor2x": 1.0, "sizeHeavySecondShareFar2x": -0.5},
              "receded.light": {"sizeHeavySecondShareFar2x": -0.25}}
        self.assertEqual(search.label_of("joint", "stage1", ov, base), "j-s1-d-0.5-Rd-0.25")
        self.assertEqual(search.label_of("c05", "stage2", base, base), "c-s2-base")


if __name__ == "__main__":
    unittest.main()
