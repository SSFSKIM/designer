#!/usr/bin/env python3.12
"""W46 G0 (a): the bindings every W46 tool reads first — the four document snapshots (X62), the shared
pins, the refusals of W44's and W45's bindings, and of the live `profiles/` as a start.

    cd packages/calibration/results/2026-10-05-w46-g0-declaration
    python3.12 -B -m unittest test_bindings -v
"""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import bindings as W  # noqa: E402


class Snapshots(unittest.TestCase):
    def test_each_snapshot_is_its_hash_and_its_bytes_at_b36c9990(self):
        self.assertEqual(W.verify_documents(), [])
        self.assertEqual({s: W.document_path(s).name[:12] for s in W.SLOTS},
                         {"active.dark": "d0219cd684bf", "receded.dark": "f0b36a71772a",
                          "active.light": "ebc3d9105a4a", "receded.light": "12712d534b78"})

    def test_a_tampered_snapshot_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            for slot in W.SLOTS:
                shutil.copy(W.document_path(slot), Path(tmp) / W.document_path(slot).name)
            path = Path(tmp) / W.document_path("active.dark").name
            body = json.loads(path.read_text())
            body["patch"]["optics"]["regular"]["tintAlpha"] = 0.8
            path.write_text(json.dumps(body, indent=2) + "\n")
            with mock.patch.object(W, "DOCUMENTS", Path(tmp)):
                self.assertTrue(any("hashes to" in f for f in W.verify_documents(at_commit=False)))
                with self.assertRaises(W.Refusal):
                    W.document("active.dark")

    def test_the_live_profiles_are_never_a_start(self):
        with self.assertRaisesRegex(W.Refusal, "X62"):
            W.refuse_live_profile(W.PROFILES_DIR / "apple-macos-27.0-1x-dark-standard-glass0.25.json", "start")
        W.refuse_live_profile(W.document_path("active.dark"), "start")

    def test_the_twins_are_checked_frozen(self):
        for key in W.TWIN_05:
            W.twin_path(key)
        with mock.patch.dict(W.TWIN_05, {"apple-macos-27.0-1x-dark-standard-glass0.5": "000000000000"}):
            with self.assertRaisesRegex(W.Refusal, "X41"):
                W.twin_path("apple-macos-27.0-1x-dark-standard-glass0.5")


class Refusals(unittest.TestCase):
    def test_other_waves_paths(self):
        for path in (W.W44_G0 / "x.json", W.W45_G0 / "fit" / "x.json", Path.home() / "vitrea-w45" / "g1-stage-light",
                     Path.home() / "vitrea-w44" / "g1-scratch"):
            with self.assertRaisesRegex(W.Refusal, "clause 1"):
                W.refuse_other_wave_path(path, "test")
        W.refuse_other_wave_path(W.LADDER_SCRATCH, "test")
        W.refuse_other_wave_path(W.G1_FIT, "test")

    def test_other_waves_part_hashes(self):
        for digest in ("5630743b7416aedd1910394d4fe7c5eedbaf0ef611516edd1c90043718746e5d",
                       "e6874e02902755c8648e7fcce29568d326544398229c20d08ce7d24ddfdc5433",
                       "fdecebbfbc895005f1c3558397989b472e664d8e20a3e359ef3fda67d4664fdd",
                       "c04227e9240a0f1e890aef5c6529db412783864305b7ddbc125a00923c771175"):
            with self.assertRaisesRegex(W.Refusal, "W44 or W45 part hash"):
                W.refuse_other_wave_hash(digest, "part 1")

    def test_other_waves_charters(self):
        with self.assertRaisesRegex(W.Refusal, "charter"):
            W.refuse_other_wave_text('{"charter": "docs/doperpowers/specs/2026-10-03-w45-span-selective-texture.md"}', "x")
        W.refuse_other_wave_text(f'{{"charter": "{W.CHARTER_PIN}", "cites": "2026-10-03-w45-span-selective-texture.md"}}', "x")

    def test_the_shared_inputs_hold(self):
        self.assertEqual(W.verify_shared(), [])


class X64(unittest.TestCase):
    def test_the_inherited_values_are_the_resolved_ones(self):
        """Every X64 key is absent from its snapshot and stated at the value the material resolves to:
        the runtime default for the active (checked against material.ts) and the shipped active's for
        the receded, which the active either names or inherits from the default."""
        material = (W.ROOT / "packages/renderer-webgpu/src/material.ts").read_text()
        active = W.document("active.dark")["patch"]
        receded = W.document("receded.dark")["patch"]
        for key, value in W.X64["active.dark"].items():
            self.assertNotIn(key, active)
            self.assertIn(f"\n  {key}: {value},\n", material, key)
        for key, value in W.X64["receded.dark"].items():
            self.assertNotIn(key, receded)
            if key in active:
                self.assertEqual(active[key], value, key)
            else:
                self.assertIn(f"\n  {key}: {value},\n", material, key)


if __name__ == "__main__":
    unittest.main()
