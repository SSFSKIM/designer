#!/usr/bin/env python3.12
"""W47 G0 (c): the bindings every W47 tool reads first — the four document snapshots (X62) at the
charter's merge `c1f9bf84c`, the shared pins (X69's frozen referee inputs among them), X64's and X67's
admitted keys, the refusals of W44's, W45's and W46's bindings, and of the live `profiles/` as a start.
W46's test (`results/2026-10-05-w46-g0-declaration/test_bindings.py`), ported by copy.

The X67 case reads the runtime default of each X67 key in `material.ts`; the operators' leaves
(`tintAlphaFar1x`/`2x`, `sizeFineTap*`) are not in this branch's runtime until G0 (a) and (b) merge,
so that case reports each missing operator leaf as a SKIP with its reason and checks the rest.

    cd packages/calibration/results/2026-10-06-w47-g0-operators
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
    def test_each_snapshot_is_its_hash_and_its_bytes_at_c1f9bf84c(self):
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
                     Path.home() / "vitrea-w44" / "g1-scratch", W.W46_G0 / "ladders" / "x.json",
                     W.W46_G1 / "gate" / "x.json", Path.home() / "vitrea-w46" / "g1-scratch"):
            with self.assertRaisesRegex(W.Refusal, "clause 2"):
                W.refuse_other_wave_path(path, "test")
        W.refuse_other_wave_path(W.LADDER_SCRATCH, "test")
        W.refuse_other_wave_path(W.G1_FIT, "test")

    def test_other_waves_part_hashes(self):
        for digest in ("5630743b7416aedd1910394d4fe7c5eedbaf0ef611516edd1c90043718746e5d",
                       "e6874e02902755c8648e7fcce29568d326544398229c20d08ce7d24ddfdc5433",
                       "fdecebbfbc895005f1c3558397989b472e664d8e20a3e359ef3fda67d4664fdd",
                       "c04227e9240a0f1e890aef5c6529db412783864305b7ddbc125a00923c771175",
                       "bc82562eaf1ab70a1a40ac55e00213cc4229aa3843e1659b7ad416e77f40a3aa",
                       "5dca38e09a68f28ac7c016718a06553b9375e978b014191374cb0b5fa4c75301",
                       "ac642fea4637995c8901aa0f096769516b629273cca187b01b3754385043df55"):
            with self.assertRaisesRegex(W.Refusal, "W44, W45 or W46 part hash"):
                W.refuse_other_wave_hash(digest, "part 1")

    def test_other_waves_charters(self):
        with self.assertRaisesRegex(W.Refusal, "charter"):
            W.refuse_other_wave_text('{"charter": "docs/doperpowers/specs/2026-10-03-w45-span-selective-texture.md"}', "x")
        with self.assertRaisesRegex(W.Refusal, "charter"):
            W.refuse_other_wave_text('{"charter": "docs/doperpowers/specs/2026-10-05-w46-dark-texture-at-0-25.md"}', "x")
        W.refuse_other_wave_text(f'{{"charter": "{W.CHARTER_PIN}", "cites": "2026-10-03-w45-span-selective-texture.md"}}', "x")
        self.assertEqual(W.CHARTER_PIN,
                         "docs/doperpowers/specs/2026-10-06-w47-span-graded-dark-transmission.md@c1f9bf84c")

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


class X67(unittest.TestCase):
    """X67's keys, absent from their snapshot and stated at the value the material resolves to; ADMITTED
    is exactly X64 ∪ X67 per dark slot; operator 2 is receded-only (X66)."""

    def test_admitted_is_x64_and_x67_and_nothing_else(self):
        self.assertEqual(set(W.ADMITTED), {"active.dark", "receded.dark"})
        for slot in W.MOVING_SLOTS:
            self.assertEqual(W.ADMITTED[slot], {**W.X64[slot], **W.X67[slot]})
        self.assertFalse(set(W.OPERATOR_2) & set(W.ADMITTED["active.dark"]))
        self.assertTrue(set(W.OPERATOR_2) <= set(W.ADMITTED["receded.dark"]))
        self.assertTrue(set(W.OPERATOR_1) <= set(W.ADMITTED["active.dark"]) & set(W.ADMITTED["receded.dark"]))

    def test_the_x67_values_are_the_resolved_ones(self):
        material = (W.ROOT / "packages/renderer-webgpu/src/material.ts").read_text()
        active = W.document("active.dark")["patch"]
        receded = W.document("receded.dark")["patch"]
        waiting = []
        for slot, patch in (("active.dark", active), ("receded.dark", receded)):
            for key, value in W.X67[slot].items():
                if key == "optics.regular.blurSigma":
                    self.assertNotIn("blurSigma", patch.get("optics", {}).get("regular", {}))
                    self.assertNotIn("blurSigma", active.get("optics", {}).get("regular", {}))
                    self.assertIn("\n      blurSigma: 1.25,\n", material)
                    self.assertEqual(value, 1.25)
                    continue
                self.assertNotIn(key, patch, key)
                if key in W.OPERATOR_1 + W.OPERATOR_2 and f"\n  {key}:" not in material:
                    waiting.append(key)
                    self.assertEqual(value, 0, key)      # every operator leaf's identity is 0
                    continue
                if slot == "receded.dark" and key in active:
                    self.assertEqual(active[key], value, key)
                else:
                    self.assertIn(f"\n  {key}: {value},\n", material, key)
        if waiting:
            self.skipTest("WAITING for the operators' runtime (G0 (a), (b)): material.ts has no default for "
                          + ", ".join(sorted(set(waiting))) + "; every other X67 value checked")


class X68(unittest.TestCase):
    """X68: every declared domain names an admitted or a snapshot leaf of its slot, the starting point
    (the snapshot or its resolved value) is inside it, and the boundaries are the charter's."""

    def test_the_domains_hold_the_start_and_their_bounds(self):
        for slot, domains in W.DOMAINS.items():
            snapshot = W.document(slot)["patch"]
            for key, parts in domains.items():
                if key in W.ADMITTED[slot]:
                    start = W.ADMITTED[slot][key]
                else:
                    node = snapshot
                    for part in key.split("."):
                        node = node[part]
                    start = node
                self.assertTrue(W.in_domain(slot, key, start), (slot, key, start))
        self.assertFalse(set(W.OPERATOR_2) & set(W.DOMAINS["active.dark"]))
        cases = [("active.dark", "tintAlphaFar2x", 0.6, True), ("active.dark", "tintAlphaFar2x", 0.61, False),
                 ("active.dark", "tintAlphaFar1x", -0.1, False), ("active.dark", "sizeOcclusionGain", 0.04, False),
                 ("active.dark", "sizeScatterSpanMax2x", 128, True), ("active.dark", "sizeScatterSpanMax2x", 130, False),
                 ("active.dark", "optics.regular.tintAlpha", 0.6, False),
                 ("receded.dark", "optics.regular.tintAlpha", 0.8, True),
                 ("receded.dark", "optics.regular.tintAlpha", 0.7, False),
                 ("receded.dark", "optics.regular.blurSigma", 4, True),
                 ("receded.dark", "optics.regular.blurSigma", 5, False),
                 ("receded.dark", "optics.regular.blurSigma", 1.75, False),   # interior non-member: a set
                 ("receded.dark", "optics.regular.blurSigma", 2.5, False),
                 ("receded.dark", "sizeFineTapShare", 1, True), ("receded.dark", "sizeFineTapShare", 1.1, False),
                 ("receded.dark", "sizeFineTapSigma2x", 0, True), ("receded.dark", "sizeFineTapSigma2x", 1, False),
                 ("receded.dark", "sizeFineTapSigma", 6, True), ("receded.dark", "sizeFineTapSigma", 7, False),
                 ("active.dark", "sizeScatterFloor", 0.1, True)]          # no declared domain: W46's admission
        for slot, key, value, inside in cases:
            self.assertEqual(W.in_domain(slot, key, value), inside, (slot, key, value))


if __name__ == "__main__":
    unittest.main()
