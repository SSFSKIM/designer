#!/usr/bin/env python3.12
"""W45 G0 (b): the candidate builder's guards, red cases (charter Decision Log 2; X44 narrowed for
the operator's key; X58).

The builder admits the operator's key `sizeHeavySecondShareFar2x` in `active.light` and, as a
difference, in `receded.light`; W44's three second-tap keys in `receded.light` only where the active
document names them; and refuses every other leaf a slot's document does not name, in every slot,
and any output root inside W44's evidence or scratch. Each case builds into a scratch root, never
into a committed candidates directory.

    cd packages/calibration/results/2026-10-03-w45-g0-operator/fit
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
TSX = CAL / "node_modules" / ".bin" / "tsx"
OPERATOR = "sizeHeavySecondShareFar2x"


def build(overrides: dict, label: str = "red-case", root: Path | None = None) -> tuple[int, str, Path]:
    scratch = Path(tempfile.mkdtemp(prefix="w45-builder-"))
    spec = scratch / "spec.json"
    spec.write_text(json.dumps(dict(label=label, note="red case", overrides=overrides)))
    out_root = root if root is not None else scratch / "out"
    env = dict(os.environ, W45_CANDIDATE_ROOT=str(out_root))
    got = subprocess.run([str(TSX), str(BUILDER), str(spec)], cwd=CAL, env=env, capture_output=True, text=True)
    return got.returncode, got.stdout + got.stderr, out_root / label


def c05(slot: str) -> dict:
    pose, scheme = slot.split(".")
    return json.loads((CAL / "profiles" / f"apple-macos-27.0-1x-{scheme}-standard-glass0.25"
                       f"{'-receded' if pose == 'receded' else ''}.json").read_text())


class Admits(unittest.TestCase):
    def test_the_operator_in_both_light_slots(self):
        code, out, folder = build({
            "active.light": {"sizeHeavySecondShare": 0.5, "sizeHeavySecondSigma2x": 3, OPERATOR: -0.5},
            "receded.light": {OPERATOR: -0.25}})
        self.assertEqual(code, 0, out)
        active = json.loads((folder / "active.light.json").read_text())
        receded = json.loads((folder / "receded.light.json").read_text())
        self.assertEqual(active["patch"][OPERATOR], -0.5)
        self.assertEqual(active["addedLeaves"], [OPERATOR])
        self.assertEqual(receded["patch"][OPERATOR], -0.25)
        self.assertEqual(receded["addedLeaves"], [OPERATOR])
        self.assertNotEqual(active["resolvedMaterialSha256"], c05("active.light")["resolvedMaterialSha256"])

    def test_the_operator_at_its_identity_keeps_c05s_digest(self):
        # 0 is the leaf's identity: added at 0, the digest rule drops it and the digest is c05's.
        code, out, folder = build({"active.light": {OPERATOR: 0}}, label="identity")
        self.assertEqual(code, 0, out)
        active = json.loads((folder / "active.light.json").read_text())
        self.assertEqual(active["resolvedMaterialSha256"], c05("active.light")["resolvedMaterialSha256"])

    def test_the_operator_in_the_receded_document_alone(self):
        code, out, folder = build({"receded.light": {OPERATOR: -0.5}}, label="receded-only")
        self.assertEqual(code, 0, out)
        self.assertEqual(json.loads((folder / "receded.light.json").read_text())["addedLeaves"], [OPERATOR])
        self.assertNotIn(OPERATOR, json.loads((folder / "active.light.json").read_text())["patch"])

    def test_w44s_receded_second_tap_keys(self):
        for key, value in (("sizeHeavySecondShare", 0), ("sizeHeavySecondSigma2x", 3)):
            code, out, folder = build({"receded.light": {key: value}}, label=f"admit-{key.lower()}")
            self.assertEqual(code, 0, out)
            self.assertEqual(json.loads((folder / "receded.light.json").read_text())["addedLeaves"], [key])

    def test_the_span_top_it_already_names(self):
        code, out, folder = build({"active.light": {"sizeScatterSpanMax2x": 160}}, label="span-top")
        self.assertEqual(code, 0, out)
        active = json.loads((folder / "active.light.json").read_text())
        self.assertEqual(active["patch"]["sizeScatterSpanMax2x"], 160)
        self.assertNotIn("addedLeaves", active)


class Refuses(unittest.TestCase):
    def refused(self, overrides, needle="X44", root=None):
        code, out, folder = build(overrides, root=root)
        self.assertNotEqual(code, 0, out)
        self.assertIn(needle, out)
        self.assertFalse((folder / "candidate.json").exists())

    def test_the_operator_in_the_dark_active_document(self):
        self.refused({"active.dark": {OPERATOR: -0.5}})

    def test_the_operator_in_the_dark_receded_document(self):
        self.refused({"receded.dark": {OPERATOR: -0.5}})

    def test_a_nested_operator_path(self):
        self.refused({"active.light": {f"optics.{OPERATOR}": -0.5}})

    def test_the_struck_thick_share(self):
        # Decision Log 2: not in the document's leaf set, and saturated at 96.
        self.refused({"active.light": {"sizeScatterHeavyShareThick2x": 0.1}})

    def test_another_leaf_the_light_document_does_not_name(self):
        self.refused({"active.light": {"sizeHeavySecondShareFar": -0.5}})

    def test_the_floor_in_the_receded_document(self):
        self.refused({"receded.light": {"sizeScatterFloor2x": 1}})

    def test_a_non_finite_operator(self):
        self.refused({"active.light": {OPERATOR: "-0.5"}}, needle="finite")

    def test_a_root_in_w44s_evidence(self):
        root = CAL / "results" / "2026-10-03-w44-g1-refit" / "fit" / "candidates"
        self.refused({"active.light": {OPERATOR: -0.5}}, needle="X58", root=root)

    def test_a_root_in_w44s_scratch(self):
        root = Path.home() / "vitrea-w44" / "g1-scratch" / "w45-red-case"
        self.refused({"active.light": {OPERATOR: -0.5}}, needle="X58", root=root)

    def test_no_root(self):
        scratch = Path(tempfile.mkdtemp(prefix="w45-builder-"))
        spec = scratch / "spec.json"
        spec.write_text(json.dumps(dict(label="no-root", overrides={})))
        env = {k: v for k, v in os.environ.items() if k != "W45_CANDIDATE_ROOT"}
        got = subprocess.run([str(TSX), str(BUILDER), str(spec)], cwd=CAL, env=env, capture_output=True, text=True)
        self.assertNotEqual(got.returncode, 0)
        self.assertIn("W45_CANDIDATE_ROOT", got.stdout + got.stderr)


if __name__ == "__main__":
    unittest.main()
