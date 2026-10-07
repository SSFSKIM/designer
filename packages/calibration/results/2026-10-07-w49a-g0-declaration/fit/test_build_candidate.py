"""W49a G0: the builder's refusals and its two bases (`fit/build-candidate.ts`; charter Decision Logs 1, 3).

    python3.12 -B -m unittest -v test_build_candidate      (from this directory; ~1 min, one tsx per case)
"""
from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[2]
BUILDER = HERE / "build-candidate.ts"
SPECS = HERE.parent / "probes" / "specs"


def build(spec: dict, root: Path | None = None):
    root = root or Path(tempfile.mkdtemp(prefix="w49a-builder-"))
    path = Path(tempfile.mkdtemp(prefix="w49a-spec-")) / "spec.json"
    path.write_text(json.dumps(spec))
    got = subprocess.run(["pnpm", "exec", "tsx", str(BUILDER), str(path)], cwd=CAL, capture_output=True,
                         text=True, env={**__import__("os").environ, "W49A_CANDIDATE_ROOT": str(root)})
    out = got.stdout + got.stderr
    return got.returncode, out, (json.loads(got.stdout) if got.returncode == 0 else None)


def far(v, label=None, **extra):
    return dict(label=label or f"t-far{v}", base="b2d074",
                overrides={"receded.dark": {"tintAlphaFar1x": v, "tintAlphaFar2x": v}, **extra})


class Builder(unittest.TestCase):
    def test_every_declared_probe_builds_with_the_light_and_b2d074_active_untouched(self):
        root = Path(tempfile.mkdtemp(prefix="w49a-probes-"))
        for spec in sorted(SPECS.glob("*.json")):
            code, out, got = build(json.loads(spec.read_text()), root)
            self.assertEqual(code, 0, out)
            self.assertEqual(got["digests"]["active.light"], "3741b22934f17f4d")
            self.assertEqual(got["digests"]["receded.light"], "c4ca0e1cd6791bde")
            if got["base"] == "b2d074":
                self.assertEqual(got["digests"]["active.dark"], "791cde91d97acbc7")
                self.assertEqual(got["moved"]["receded.dark"], ["tintAlphaFar1x", "tintAlphaFar2x"])

    def test_the_shipped_pair_itself_refuses_x75(self):
        code, out, _ = build(dict(label="t-shipped", base="b2d074"))
        self.assertNotEqual(code, 0)
        self.assertIn("receded.dark: draws opaque glass, alphaBase above 0.95 (X75)", out)
        self.assertIn("max alphaBase 1.0000", out)

    def test_x75_refuses_above_the_bound_and_admits_it(self):
        for v in (0.2, 0.16):
            code, out, _ = build(far(v))
            self.assertNotEqual(code, 0, v)
            self.assertIn("(X75)", out)
        code, out, _ = build(far(0.15))
        self.assertEqual(code, 0, out)

    def test_the_signed_domain(self):
        for v in (-0.31, 0.21):
            code, out, _ = build(far(v))
            self.assertNotEqual(code, 0, v)
            self.assertIn("outside its declared domain", out)
        for v in (-0.3, 0):
            code, out, got = build(far(v))
            self.assertEqual(code, 0, out)
        # The anchors are separate members; one moved alone leaves the other at the shipped 0.2, which
        # X75 refuses at its own scale only.
        code, out, _ = build(dict(label="t-far1x-only", base="b2d074",
                                  overrides={"receded.dark": {"tintAlphaFar1x": -0.2}}))
        self.assertNotEqual(code, 0)
        self.assertIn("webgpu regular dpr 2", out)
        self.assertNotIn("dpr 1", out)
        code, out, _ = build(dict(label="t-far-split", base="b2d074",
                                  overrides={"receded.dark": {"tintAlphaFar1x": -0.2, "tintAlphaFar2x": 0.1}}))
        self.assertEqual(code, 0, out)

    def test_nothing_but_the_members_moves(self):
        for slot, leaf, value in (("active.dark", "tintAlphaFar1x", 0.1),
                                  ("receded.dark", "optics.regular.tintAlpha", 0.89),
                                  ("receded.light", "tintAlphaFar1x", 0.0),
                                  ("active.light", "sizeScatterSpanMax", 160)):
            code, out, _ = build(dict(label="t-nonmember", base="b2d074", overrides={slot: {leaf: value}}))
            self.assertNotEqual(code, 0, (slot, leaf))
            self.assertIn("is not a W49a member on base b2d074", out)

    def test_the_d0219_base_reproduces_its_digests_and_takes_only_p1(self):
        code, out, got = build(dict(label="t-d0219", base="d0219"))
        self.assertEqual(code, 0, out)
        self.assertEqual(got["digests"]["active.dark"], "b074fc6913a91c66")
        self.assertEqual(got["digests"]["receded.dark"], "280f0fddf014e0f6")
        code, out, _ = build(dict(label="t-d0219-192", base="d0219",
                                  overrides={"active.dark": {"sizeScatterSpanMax": 192}}))
        self.assertNotEqual(code, 0)
        self.assertIn("outside its declared domain", out)
        code, out, _ = build(dict(label="t-d0219-far", base="d0219",
                                  overrides={"receded.dark": {"tintAlphaFar1x": 0.1}}))
        self.assertNotEqual(code, 0)
        self.assertIn("is not a W49a member on base d0219", out)

    def test_other_waves_roots_and_labels_refuse(self):
        for root in (CAL / "results" / "2026-10-06-w48-g1-refit" / "x", Path.home() / "vitrea-w48" / "x"):
            code, out, _ = build(far(0.1), root=root)
            self.assertNotEqual(code, 0)
            self.assertIn("W44's-W48's evidence or scratch", out)
        code, out, _ = build(far(0.1, label="d-s2-x"))
        self.assertNotEqual(code, 0)
        self.assertIn("does not match labels.json", out)


if __name__ == "__main__":
    unittest.main()
