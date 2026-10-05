#!/usr/bin/env python3.12
"""W46 G0 (a): the candidate builder's guards (charter clause 1; X60, X62, X64), each case built into a
scratch root through the real builder.

Admits: exactly X64's keys per dark slot, each alone and all together, the latter digest-neutral
(`b074fc6913a91c66` / `280f0fddf014e0f6`, the light digests the light snapshots'); an existing leaf at
its shape (the dark `tintAlpha`). Refuses: every addition X64 does not list (in either dark slot,
including `sizeScatterSpanMax2x` and `sizeScatterHeavyShareThick2x`, and an X64 key of the OTHER dark
slot), any light override (X60), a nested unknown path, a non-finite value, a wrong shape, a label
outside `labels.json`'s pattern, an output root in W44's or W45's evidence or scratch or in
`profiles/`, and no root.

    cd packages/calibration/results/2026-10-05-w46-g0-declaration/fit
    python3.12 -B -m unittest test_build_candidate -v
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import bindings as W  # noqa: E402

TSX = W.CAL / "node_modules" / ".bin" / "tsx"


def build(overrides: dict, label: str = "red-case", root: Path | None = None) -> tuple[int, str, Path]:
    scratch = Path(tempfile.mkdtemp(prefix="w46-builder-"))
    spec = scratch / "spec.json"
    spec.write_text(json.dumps(dict(label=label, note="test", overrides=overrides)))
    out_root = root if root is not None else scratch / "out"
    env = dict(os.environ, W46_CANDIDATE_ROOT=str(out_root))
    got = subprocess.run([str(TSX), str(W.BUILDER), str(spec)], cwd=W.CAL, env=env, capture_output=True, text=True)
    return got.returncode, got.stdout + got.stderr, out_root / label


def endpoint(folder: Path, slot: str) -> dict:
    return json.loads((folder / f"{slot}.json").read_text())


class Admits(unittest.TestCase):
    def test_every_x64_key_together_is_digest_neutral(self):
        code, out, folder = build(W.X64, label="x64")
        self.assertEqual(code, 0, out)
        for slot in W.SLOTS:
            doc = endpoint(folder, slot)
            self.assertEqual(doc["resolvedMaterialSha256"], W.DOCUMENT_DIGEST[slot], slot)
            if slot in W.X64:
                self.assertEqual(doc["addedLeaves"], sorted(W.X64[slot]))
                for key, value in W.X64[slot].items():
                    self.assertEqual(doc["patch"][key], value)
            else:
                self.assertEqual(doc["patch"], W.document(slot)["patch"])
        declaration = json.loads((folder / "candidate.json").read_text())
        self.assertEqual(declaration["name"], "apple-macos-27.0-glass0.25-w46-x64")

    def test_each_x64_key_alone(self):
        for slot, keys in W.X64.items():
            for key, value in keys.items():
                moved = value + 0.1
                code, out, folder = build({slot: {key: moved}}, label=f"one-{slot.split('.')[0]}-{key.lower()}")
                self.assertEqual(code, 0, f"{slot} {key}: {out}")
                doc = endpoint(folder, slot)
                self.assertEqual(doc["addedLeaves"], [key])
                # The second tap's widths are a W30 gate-group under its share, which is 0 in both
                # dark documents, so moving a width alone is dropped from the digest (W31 Rule 2).
                if key not in ("sizeHeavySecondSigma", "sizeHeavySecondSigma2x"):
                    self.assertNotEqual(doc["resolvedMaterialSha256"], W.DOCUMENT_DIGEST[slot], f"{slot} {key}")
                else:
                    self.assertEqual(doc["resolvedMaterialSha256"], W.DOCUMENT_DIGEST[slot], f"{slot} {key}")

    def test_an_existing_leaf_moves_at_its_shape(self):
        code, out, folder = build({"active.dark": {"optics.regular.tintAlpha": 0.7},
                                   "receded.dark": {"optics.regular.tintAlpha": 0.6}}, label="ta")
        self.assertEqual(code, 0, out)
        self.assertEqual(endpoint(folder, "active.dark")["patch"]["optics"]["regular"]["tintAlpha"], 0.7)
        self.assertEqual(endpoint(folder, "receded.dark")["patch"]["optics"]["regular"]["tintAlpha"], 0.6)
        self.assertNotIn("addedLeaves", endpoint(folder, "active.dark"))
        for slot in ("active.light", "receded.light"):
            self.assertEqual(endpoint(folder, slot)["resolvedMaterialSha256"], W.DOCUMENT_DIGEST[slot])


class Refuses(unittest.TestCase):
    def refused(self, overrides, needle, root=None, label="red-case"):
        code, out, folder = build(overrides, root=root, label=label)
        self.assertNotEqual(code, 0, out)
        self.assertIn(needle, out)
        self.assertFalse(folder.exists(), "a refused build writes nothing")

    def test_additions_x64_does_not_list(self):
        for slot in ("active.dark", "receded.dark"):
            for key in ("sizeScatterSpanMax2x", "sizeScatterHeavyShareThick2x", "sizeScatterRampReach2xPx",
                        "sizeHeavySecondShareFar"):
                self.refused({slot: {key: 0.1}}, "X64")

    def test_the_other_slots_x64_keys(self):
        # active X64 keys the receded list omits, and receded X64 keys the active list omits (and the
        # active snapshot does not name)
        for key in set(W.X64["active.dark"]) - set(W.X64["receded.dark"]):
            if key not in W.document("receded.dark")["patch"]:
                self.refused({"receded.dark": {key: 0.3}}, "X64")
        for key in set(W.X64["receded.dark"]) - set(W.X64["active.dark"]):
            if key not in W.document("active.dark")["patch"]:
                self.refused({"active.dark": {key: 0.3}}, "X64")

    def test_a_light_override(self):
        for slot in ("active.light", "receded.light"):
            self.refused({slot: {"sizeScatterFloor2x": 1}}, "X60")
            self.refused({slot: {"optics.regular.tintAlpha": 0.6}}, "X60")

    def test_a_nested_unknown_path(self):
        self.refused({"active.dark": {"optics.regular.sizeScatterFloor2x": 1}}, "X64")

    def test_a_non_finite_or_misshapen_value(self):
        self.refused({"active.dark": {"sizeScatterFloor2x": "1"}}, "finite")
        self.refused({"active.dark": {"optics.regular.tintAlpha": [0.7]}}, "the spec gives")

    def test_a_label_outside_the_grammar(self):
        self.refused({}, "pattern", label="d-s2-Rta0.6")

    def test_roots_in_other_waves_or_profiles(self):
        for root in (W.RESULTS / "2026-10-03-w45-g1-refit" / "fit" / "candidates",
                     W.RESULTS / "2026-10-03-w44-g1-refit" / "fit" / "candidates",
                     Path.home() / "vitrea-w45" / "g1-scratch" / "w46-red-case",
                     Path.home() / "vitrea-w44" / "g1-scratch" / "w46-red-case"):
            self.refused({}, "clause 1", root=root)
        self.refused({}, "X62", root=W.PROFILES_DIR)

    def test_no_root(self):
        scratch = Path(tempfile.mkdtemp(prefix="w46-builder-"))
        spec = scratch / "spec.json"
        spec.write_text(json.dumps(dict(label="no-root", overrides={})))
        env = {k: v for k, v in os.environ.items() if k != "W46_CANDIDATE_ROOT"}
        got = subprocess.run([str(TSX), str(W.BUILDER), str(spec)], cwd=W.CAL, env=env, capture_output=True, text=True)
        self.assertNotEqual(got.returncode, 0)
        self.assertIn("W46_CANDIDATE_ROOT", got.stdout + got.stderr)


if __name__ == "__main__":
    unittest.main()
