#!/usr/bin/env python3.12
"""W44 G0 (d): the referee manifest's four consumers, each with a red case (X49).

  planner   the pre-gate probe list excludes every referee, and `compare`'s selection under it
            (`--set probe`) is the probe cells less the referees exactly; the exposure list
            includes every referee and no other probe scene, and its selection (`--set
            holdout,probe`) is the canonical holdout plus the referees exactly; scenes.json's
            bytes and membership untouched; both lists move with the manifest, never typed.
  manifest  a manifest naming a non-probe scene, an undeclared scene or a scene twice is refused.
  loader    `cuts/bed.py` refuses a candidate bed carrying a referee row (the fit loader).
  gate      `bed.py` refuses a sealed stage bed carrying one before the exposure, admits it at the
            exposure (`with_holdout`), and `plan.py check-stage` refuses a stage matrix holding one.

    python3.12 -B -m unittest test_plan -v      (from this directory)
"""
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "cuts"))
import plan  # noqa: E402
import bed as B  # noqa: E402


def manifest_file(tmp: Path, **change) -> Path:
    body = json.loads(plan.MANIFEST.read_text())
    body.update(change)
    path = tmp / "referees.json"
    path.write_text(json.dumps(body))
    return path


class Planner(unittest.TestCase):
    def setUp(self):
        self.scenes_before = hashlib.sha256(plan.SCENES_PATH.read_bytes()).hexdigest()
        self.scenes = plan.load_scenes()
        self.m = plan.load_manifest(scenes=self.scenes)
        self.lists = plan.lists(self.m, self.scenes)

    def tearDown(self):
        self.assertEqual(hashlib.sha256(plan.SCENES_PATH.read_bytes()).hexdigest(), self.scenes_before,
                         "the planner moved scenes.json")

    def test_pregate_excludes_every_referee(self):
        pre = set(self.lists["pregateProbe"]["scenes"])
        self.assertFalse(pre & set(self.m["scenes"]))
        selected = plan.compare_selects(self.scenes, self.m["profiles"], ("probe",), pre)
        probe_cells = {(p, s) for p in self.m["profiles"] for s in self.scenes["declared"][p]
                       if self.scenes["role"][s] == "probe"}
        self.assertEqual(selected, probe_cells - plan.referee_cells(self.m))
        self.assertFalse(selected & plan.referee_cells(self.m))

    def test_exposure_is_the_holdout_and_the_referees_exactly(self):
        exp = set(self.lists["exposure"]["scenes"])
        self.assertTrue(set(self.m["scenes"]) <= exp)
        self.assertEqual({s for s in exp if self.scenes["role"][s] == "probe"}, set(self.m["scenes"]))
        selected = plan.compare_selects(self.scenes, self.m["profiles"], ("holdout", "probe"), exp)
        holdout_cells = {(p, s) for p in self.m["profiles"] for s in self.scenes["declared"][p]
                         if self.scenes["role"][s] == "holdout"}
        self.assertEqual(selected, holdout_cells | plan.referee_cells(self.m))
        # and the canonical holdout alone is NOT enough: a probe scene is unselectable under it
        self.assertFalse(plan.compare_selects(self.scenes, self.m["profiles"], ("holdout",), exp)
                         & plan.referee_cells(self.m))

    def test_canonical_membership_untouched(self):
        for sid in self.m["scenes"]:
            self.assertEqual(self.scenes["role"][sid], "probe")
        self.assertEqual(self.lists["scenesSha256"], self.scenes_before)

    def test_counts(self):
        self.assertEqual(len(self.m["scenes"]) * len(self.m["profiles"]), 12)
        self.assertEqual(self.lists["exposure"]["count"], 26)      # 20 holdout + 6 referees
        self.assertEqual(self.lists["pregateProbe"]["count"], 81)  # 87 probe - 6

    def test_lists_move_with_the_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            extra = sorted(set(self.lists["pregateProbe"]["scenes"]))[0]
            path = manifest_file(Path(tmp), scenes=self.m["scenes"] + [extra])
            m = plan.load_manifest(path, self.scenes)
            got = plan.lists(m, self.scenes)
            self.assertNotIn(extra, got["pregateProbe"]["scenes"])
            self.assertIn(extra, got["exposure"]["scenes"])


class ManifestRefusals(unittest.TestCase):
    def refused(self, **change):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(plan.Refused):
                plan.load_manifest(manifest_file(Path(tmp), **change))

    def test_a_holdout_scene(self):
        self.refused(scenes=["checkerboard__rrect-lg__rest"])

    def test_a_calibration_scene(self):
        self.refused(scenes=["checkerboard__rrect-md__rest"])

    def test_a_scene_twice(self):
        self.refused(scenes=["checkerboard-4__rrect-ml__rest", "checkerboard-4__rrect-ml__rest"])

    def test_a_scene_a_profile_does_not_declare(self):
        self.refused(scenes=["mid-light-solid__rrect-sm__inactive"])

    def test_a_dark_profile(self):
        self.refused(profiles=["apple-macos-27.0-2x-dark-standard-glass0.25"])


def row(profile, sid, renderer="webgpu", path="x"):
    return {"key": {"profileKey": profile, "sceneId": sid,
                    "web": {"engine": "chromium", "engineVersion": "0", "renderer": renderer,
                            "samplingBackend": "gpu-texture", "gpuAdapter": "test", "colorSpace": "srgb",
                            "capturePath": path}},
            "fixtureSet": B.SCENES.role[sid], "state": B.SCENES.by_id[sid]["state"]}


class Consumers(unittest.TestCase):
    """The loader and the gate, on synthetic schema-5 matrices: one admissible row, one referee row."""

    def matrix(self, tmp, rows):
        path = Path(tmp) / "matrix.json"
        path.write_text(json.dumps({"schemaVersion": 5, "cells": rows}))
        return str(path)

    def sealed_row(self, sid):
        sealed = B.sealed_025()
        path = ("materialProfile=packages/calibration/profiles/apple-macos-27.0-1x-light-standard-glass0.25.json "
                f"sha256:{sealed['packages/calibration/profiles/apple-macos-27.0-1x-light-standard-glass0.25.json']} "
                "sections=renderer+cssTierMapping, recededProfile=packages/calibration/profiles/"
                "apple-macos-27.0-1x-light-standard-glass0.25-receded.json "
                f"sha256:{sealed['packages/calibration/profiles/apple-macos-27.0-1x-light-standard-glass0.25-receded.json']}")
        return row("apple-macos-27.0-2x-light-standard-glass0.25", sid, path=path)

    def test_gate_refuses_a_referee_before_the_exposure_and_admits_it_at_it(self):
        referee = "checkerboard-4__rrect-ml__rest"
        with tempfile.TemporaryDirectory() as tmp:
            ok = self.matrix(tmp, [self.sealed_row("checkerboard-4__rrect-md__rest")])
            self.assertEqual(len(B.load([ok], "sealed").rows), 1)
        with tempfile.TemporaryDirectory() as tmp:
            bad = self.matrix(tmp, [self.sealed_row(referee)])
            with self.assertRaises(SystemExit) as caught:
                B.load([bad], "sealed")
            self.assertIn("a referee cell", str(caught.exception))
            self.assertEqual(len(B.load([bad], "sealed", with_holdout=True).rows), 1)

    def test_loader_refuses_a_candidate_bed_carrying_a_referee(self):
        referee = "checkerboard-8__rrect-sm__rest"
        cand = B.ROOT / "packages/calibration/results/2026-10-02-w43-g3-refit/fit/candidates/c05/candidate.json"
        sha = hashlib.sha256(cand.read_bytes()).hexdigest()[:12]
        path = (f"materialProfile=candidate candidateDocument={cand.relative_to(B.ROOT)} "
                f"declarationSha256={sha}")
        with tempfile.TemporaryDirectory() as tmp:
            bad = self.matrix(tmp, [row("apple-macos-27.0-2x-light-standard-glass0.25", referee, path=path)])
            with self.assertRaises(SystemExit) as caught:
                B.load([bad], "candidate", str(cand.relative_to(B.ROOT)))
            self.assertIn("a referee cell", str(caught.exception))
            # the candidate bed's refusal is not lifted by asking for the holdout
            with self.assertRaises(SystemExit):
                B.load([bad], "candidate", str(cand.relative_to(B.ROOT)), with_holdout=True)

    def test_check_stage(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = self.matrix(tmp, [row("apple-macos-27.0-1x-light-standard-glass0.25",
                                        "hc-text-7__rrect-md__inactive")])
            got = subprocess.run([sys.executable, "-B", str(HERE / "plan.py"), "check-stage", bad],
                                 capture_output=True, text=True)
            self.assertEqual(got.returncode, 1, got.stdout)
            self.assertIn("REFUSES", got.stdout)
        with tempfile.TemporaryDirectory() as tmp:
            ok = self.matrix(tmp, [row("apple-macos-27.0-1x-light-standard-glass0.25",
                                       "hc-text-7__rrect-md__rest"),
                                   row("apple-macos-27.0-2x-dark-standard-glass0.25",
                                       "hc-text-7__rrect-md__inactive")])
            got = subprocess.run([sys.executable, "-B", str(HERE / "plan.py"), "check-stage", ok],
                                 capture_output=True, text=True)
            self.assertEqual(got.returncode, 0, got.stdout)


if __name__ == "__main__":
    unittest.main()
