#!/usr/bin/env python3.12
"""W44 G1 step 0: the candidate builder's receded light guard, red cases (charter Decision Log 7
item 1; X44 narrowed by one difference).

The builder admits, in `receded.light` ONLY, exactly the three second-tap keys the active document
names (`sizeHeavySecondShare`, `sizeHeavySecondSigma`, `sizeHeavySecondSigma2x`) as leaves the
receded document adds, and refuses every other leaf a slot's document does not name, in every slot.
Each case builds into a scratch root (`W44_G1_CANDIDATE_ROOT`), never into `candidates/`.

    cd packages/calibration/results/2026-10-03-w44-g1-refit/fit
    python3.12 -B -m unittest test_build_candidate -v
"""
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[2]
BUILDER = HERE / "build-candidate.ts"


def build(overrides: dict, label: str = "red-case") -> tuple[int, str, Path]:
    root = Path(tempfile.mkdtemp(prefix="w44-g1-builder-"))
    spec = root / "spec.json"
    spec.write_text(json.dumps(dict(label=label, note="red case", overrides=overrides)))
    env = dict(os.environ, W44_G1_CANDIDATE_ROOT=str(root / "out"))
    got = subprocess.run(["npx", "tsx", str(BUILDER), str(spec)], cwd=CAL, env=env,
                         capture_output=True, text=True)
    return got.returncode, got.stdout + got.stderr, root / "out" / label


class Admits(unittest.TestCase):
    def test_the_receded_share_as_a_difference(self):
        code, out, folder = build({
            "active.light": {"sizeScatterFloor2x": 1, "sizeHeavySecondShare": 0.5,
                             "sizeHeavySecondSigma2x": 3},
            "receded.light": {"sizeHeavySecondShare": 0}})
        self.assertEqual(code, 0, out)
        receded = json.loads((folder / "receded.light.json").read_text())
        self.assertEqual(receded["patch"]["sizeHeavySecondShare"], 0)
        self.assertEqual(receded["addedLeaves"], ["sizeHeavySecondShare"])
        self.assertNotIn("sizeHeavySecondSigma2x", receded["patch"])   # the width stays inherited
        active = json.loads((folder / "active.light.json").read_text())
        self.assertNotIn("addedLeaves", active)

    def test_each_second_tap_key_and_no_other(self):
        for key, value in (("sizeHeavySecondSigma", 0), ("sizeHeavySecondSigma2x", 3)):
            code, out, folder = build({"receded.light": {key: value}}, label=f"admit-{key.lower()}")
            self.assertEqual(code, 0, out)
            self.assertEqual(json.loads((folder / "receded.light.json").read_text())["addedLeaves"], [key])


class Refuses(unittest.TestCase):
    def refused(self, overrides, needle="X44"):
        code, out, folder = build(overrides)
        self.assertNotEqual(code, 0, out)
        self.assertIn(needle, out)
        self.assertFalse((folder / "candidate.json").exists())

    def test_the_floor_in_the_receded_document(self):
        self.refused({"receded.light": {"sizeScatterFloor2x": 1}})

    def test_the_reach_in_the_receded_document(self):
        self.refused({"receded.light": {"sizeScatterRampReach2xPx": 150}})

    def test_another_leaf_the_active_document_names(self):
        self.refused({"receded.light": {"sizeScatterScaleGain": 0.1}})

    def test_the_second_tap_in_the_dark_receded_document(self):
        self.refused({"receded.dark": {"sizeHeavySecondShare": 0}})

    def test_a_nested_second_tap_path(self):
        self.refused({"receded.light": {"optics.sizeHeavySecondShare": 0}})

    def test_a_leaf_no_document_names(self):
        self.refused({"active.light": {"sizeHeavyThirdShare": 0.5}})


if __name__ == "__main__":
    unittest.main()
