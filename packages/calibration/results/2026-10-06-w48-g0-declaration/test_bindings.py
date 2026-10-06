#!/usr/bin/env python3.12
"""W48 G0 (b): the bindings every W48 tool and every inherited W47 tool reads first (charter clause 2;
X62, X64, X67-X73). W47's `test_bindings.py` ported by copy; its two cases that assert a W47 binding
(the charter pin and the refusal message naming three waves) are W48's here, and W48 adds: W47's
evidence directory, scratch, part hashes and charter refused; the snapshots at 78d0211e0 byte-identical to
W47's; the inherited tools pinned (`INHERITED`); `inherit.py` refusing a foreign `bindings` and a tool it
does not inherit, and re-binding exactly `REBIND`. The X67 case no longer skips: both operators are in
the runtime at this charter's merge.

    cd packages/calibration/results/2026-10-06-w48-g0-declaration
    python3.12 -B -m unittest test_bindings -v
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import bindings as W  # noqa: E402


class Snapshots(unittest.TestCase):
    def test_each_snapshot_is_its_hash_and_its_bytes_at_78d0211e0(self):
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
        W.refuse_other_wave_path(W.STAGE, "test")
        W.refuse_other_wave_path(W.FIT_SCRATCH, "test")

    def test_w47s_places_are_refused(self):
        for path in (W.W47_G0 / "ladders" / "x.json", W.W47_G0 / "fit" / "candidates" / "a",
                     W.RESULTS / "2026-10-06-w47-g1-refit" / "stage", Path.home() / "vitrea-w47" / "g0-ladders",
                     Path.home() / "vitrea-w47" / "g1-stage-dark"):
            with self.assertRaisesRegex(W.Refusal, "W44's, W45's, W46's or W47's evidence"):
                W.refuse_other_wave_path(path, "test")

    def test_other_waves_part_hashes(self):
        for digest in ("5630743b7416aedd1910394d4fe7c5eedbaf0ef611516edd1c90043718746e5d",
                       "e6874e02902755c8648e7fcce29568d326544398229c20d08ce7d24ddfdc5433",
                       "fdecebbfbc895005f1c3558397989b472e664d8e20a3e359ef3fda67d4664fdd",
                       "c04227e9240a0f1e890aef5c6529db412783864305b7ddbc125a00923c771175",
                       "bc82562eaf1ab70a1a40ac55e00213cc4229aa3843e1659b7ad416e77f40a3aa",
                       "5dca38e09a68f28ac7c016718a06553b9375e978b014191374cb0b5fa4c75301",
                       "ac642fea4637995c8901aa0f096769516b629273cca187b01b3754385043df55"):
            with self.assertRaisesRegex(W.Refusal, "W44, W45, W46 or W47 part hash"):
                W.refuse_other_wave_hash(digest, "part 1")
        for digest in ("2d6d49ad7af5dc9190227ba02f57e3eb9681a85f31890f127e6c08c621103579",      # W47 part 1
                       "2d4a2c7f73b5a0708c1e80ff06b64043657b0f7fafe3c05c3393da84d769c30e"):     # amended
            with self.assertRaisesRegex(W.Refusal, "W47 part hash"):
                W.refuse_other_wave_hash(digest, "part 1")

    def test_other_waves_charters(self):
        with self.assertRaisesRegex(W.Refusal, "charter"):
            W.refuse_other_wave_text('{"charter": "docs/doperpowers/specs/2026-10-03-w45-span-selective-texture.md"}', "x")
        with self.assertRaisesRegex(W.Refusal, "charter"):
            W.refuse_other_wave_text('{"charter": "docs/doperpowers/specs/2026-10-05-w46-dark-texture-at-0-25.md"}', "x")
        with self.assertRaisesRegex(W.Refusal, "charter"):
            W.refuse_other_wave_text('{"charter": "docs/doperpowers/specs/2026-10-06-w47-span-graded-dark-transmission.md"}', "x")
        W.refuse_other_wave_text(f'{{"charter": "{W.CHARTER_PIN}", "cites": "2026-10-06-w47-span-graded-dark-transmission.md"}}', "x")
        self.assertEqual(W.CHARTER_PIN, "docs/doperpowers/specs/2026-10-06-w48-dark-operators-fit.md@78d0211e0")

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
        self.assertEqual(waiting, [], "both operators are in the runtime at 78d0211e0 (W47 G0 (a), (b) merged)")


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


class W48(unittest.TestCase):
    def test_the_snapshots_are_w47s_bytes(self):
        for slot in W.SLOTS:
            self.assertEqual(W.document_path(slot).read_bytes(),
                             (W.W47_G0 / "documents" / W.document_path(slot).name).read_bytes(), slot)
        self.assertEqual(W.SNAPSHOT_COMMIT, "78d0211e0")

    def test_the_wave_bindings(self):
        self.assertEqual(W.G0.name, "2026-10-06-w48-g0-declaration")
        self.assertEqual(W.G1.name, "2026-10-06-w48-g1-refit")
        self.assertEqual(W.SCRATCH, Path.home() / "vitrea-w48")
        self.assertEqual(W.GPU_LOCK, Path("/tmp/w48-gpu.lock"))
        self.assertIn("LOCK=/tmp/w48-gpu.lock", (W.G0 / "with-gpu.sh").read_text())
        self.assertEqual(W.BUILDER, W.G0 / "fit" / "build-candidate.ts")
        self.assertEqual(W.SEAL, W.G0 / "seal" / "seal.ts")
        self.assertEqual(W.WITH_GPU, W.G0 / "with-gpu.sh")
        for inherited in (W.CUTS_SOURCE, W.FIT, W.REFEREES):
            self.assertEqual(inherited.parent, W.W47_G0)
        self.assertEqual(W.LADDER_CELLS, W.W47_G0 / "ladders" / "cells.json")
        self.assertEqual(W.LADDER_PROTOCOL, W.G0 / "ladders" / "protocol.json")
        self.assertFalse(W.LADDER_SCRATCH.exists(), "W48 renders no ladder (X71)")

    def test_the_inherited_tools_are_pinned(self):
        self.assertEqual(W.verify_inherited(), [])
        path = next(iter(W.INHERITED))
        with mock.patch.dict(W.INHERITED, {path: "0" * 64}):
            self.assertEqual(len(W.verify_inherited()), 1)
            with self.assertRaisesRegex(W.Refusal, "inherited W47 tool moved"):
                W.require_inherited()


class Inherit(unittest.TestCase):
    def run_py(self, code):
        import subprocess
        return subprocess.run([sys.executable, "-B", "-c", code], cwd=HERE, capture_output=True, text=True)

    def test_a_foreign_bindings_module_refuses(self):
        got = self.run_py("import sys, types; m = types.ModuleType('bindings'); m.__file__ = '/x/bindings.py'; "
                          "sys.modules['bindings'] = m; import inherit")
        self.assertNotEqual(got.returncode, 0)
        self.assertIn("another `bindings` is loaded", got.stdout + got.stderr)

    def test_an_inherited_tool_reads_w48s_bindings_and_rebinds(self):
        got = self.run_py("import inherit; s = inherit.tool('stage/stage.py'); import bindings; "
                          "assert s.W is bindings is inherit.W; assert s.SEALED_BY == 'W48 G1', s.SEALED_BY; "
                          "assert set(inherit.REBIND) == {'stage/stage.py'}; print('ok')")
        self.assertEqual(got.returncode, 0, got.stderr)
        self.assertIn("ok", got.stdout)

    def test_a_tool_w48_does_not_inherit_refuses(self):
        got = self.run_py("import inherit; inherit.tool('ladders/drive.py')")
        self.assertNotEqual(got.returncode, 0)
        self.assertIn("not a tool W48 inherits", got.stdout + got.stderr)

    def test_the_cuts_launcher_binds_w48_in_a_child_process(self):
        """W47's fit.py runs `W.CUTS / "cuts.py"` in a new process (review P2): it must bind W48, not W47."""
        launcher = W.CUTS / "cuts.py"
        self.assertEqual(launcher, W.G0 / "cuts" / "cuts.py")
        got = subprocess.run([sys.executable, "-B", "-c",
                              "import runpy, sys; sys.argv = ['x', '--help']\n"
                              f"try:\n    runpy.run_path({str(launcher)!r}, run_name='__main__')\n"
                              "except SystemExit:\n    pass\n"
                              "print(sys.modules['bindings'].__file__)"], capture_output=True, text=True,
                             cwd=W.CUTS)
        self.assertEqual(got.returncode, 0, got.stderr)
        self.assertEqual(Path(got.stdout.strip().splitlines()[-1]).resolve(), W.G0 / "bindings.py")


if __name__ == "__main__":
    unittest.main()
