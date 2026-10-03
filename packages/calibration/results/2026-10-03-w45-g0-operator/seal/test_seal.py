#!/usr/bin/env python3.12
"""W45 G0 (b): the seal port, tested on c05 before use (brief (b); charter clauses 2 and 8; Decision
Log 2; X44 as narrowed; X58).

Every case seals into a SCRATCH COPY of `packages/calibration/profiles/` (`--profiles`) with its
record beside it (`--manifest`), from candidates W45's builder writes into a scratch root, so no
shipped document is touched.

- **c05's own bytes reproduce its digests.** c05 itself built as a candidate (no override) and
  sealed: both light documents resolve to c05's recorded `resolvedMaterialSha256`
  (`50430fa62c1120bd` active, `5d8680980b7aeb55` receded) with c05's patch, nothing moved, and the
  dark documents and every other profile file byte-identical.
- **The operator's key is admitted where Decision Log 2 admits it**: W44's joint point with the
  operator in the active light document and, as a difference, in the receded light one.
- **Red cases**: a second seal over sealed bytes (not c05's), a receded leaf outside the narrowed set
  (the second tap's width), a moved leaf the candidate's spec does not declare, a moved leaf with no
  method, and a W44 candidate or profiles directory (X58).

    cd packages/calibration/results/2026-10-03-w45-g0-operator/seal
    python3.12 -B -m unittest test_seal -v
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "fit"))
import bindings as W  # noqa: E402

SEAL = HERE / "seal.ts"
PROFILES = W.CAL / "profiles"
C05_DIGESTS = {"apple-macos-27.0-1x-light-standard-glass0.25.json": "50430fa62c1120bd",
               "apple-macos-27.0-1x-light-standard-glass0.25-receded.json": "5d8680980b7aeb55"}
JOINT_OPERATOR = {"active.light": {"sizeScatterFloor2x": 1.0, "sizeHeavySecondShare": 0.5, "sizeHeavySecondSigma2x": 5,
                                   "sizeScatterRampStartThin2x": 0.8, "sizeHeavySecondShareFar2x": -0.5},
                  "receded.light": {"sizeScatterRampStartThin2x": 0.1, "sizeHeavySecondShareFar2x": -0.25}}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Seal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(tempfile.mkdtemp(prefix="w45-seal-"))
        cls.candidates = cls.root / "candidates"
        for label, overrides in (("c05-control", {}), ("joint-operator", JOINT_OPERATOR),
                                 ("undeclared", JOINT_OPERATOR),
                                 ("receded-width", {"receded.light": {"sizeHeavySecondSigma2x": 3}})):
            spec = cls.root / f"{label}.spec.json"
            spec.write_text(json.dumps(dict(label=label, note="test_seal", overrides=overrides)))
            got = subprocess.run(["pnpm", "exec", "tsx", str(W.BUILDER), str(spec)], cwd=W.CAL,
                                 env=dict(os.environ, W45_CANDIDATE_ROOT=str(cls.candidates)),
                                 capture_output=True, text=True)
            assert got.returncode == 0, got.stdout + got.stderr
        # The candidate's own spec, edited to drop a declared override: the seal must catch the move.
        spec = cls.candidates / "undeclared" / "spec.json"
        body = json.loads(spec.read_text())
        del body["overrides"]["receded.light"]
        spec.write_text(json.dumps(body))
        cls.method = cls.root / "method.json"
        cls.method.write_text(json.dumps({leaf: ["test_seal: a scratch rehearsal, no fit"]
                                          for slot in JOINT_OPERATOR.values() for leaf in slot}))
        cls.no_method = cls.root / "no-method.json"
        cls.no_method.write_text("{}")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.root)

    def seal(self, label, method=None, candidates=None, profiles=None):
        if profiles is None:
            profiles = Path(tempfile.mkdtemp(prefix="profiles-", dir=self.root))
            shutil.rmtree(profiles)
            shutil.copytree(PROFILES, profiles)
        manifest = profiles / "sealed-manifest.json"
        got = subprocess.run(["pnpm", "exec", "tsx", str(SEAL), label, str(method or self.method),
                              "--candidates", str(candidates or self.candidates), "--profiles", str(profiles),
                              "--manifest", str(manifest)], cwd=W.CAL, capture_output=True, text=True)
        return got.returncode, got.stdout + got.stderr, profiles, manifest

    def test_c05s_own_bytes_reproduce_its_digests(self):
        before = {p.name: sha(p) for p in PROFILES.glob("*.json")}
        code, out, profiles, manifest = self.seal("c05-control", method=self.no_method)
        self.assertEqual(code, 0, out)
        record = json.loads(manifest.read_text())
        for name, digest in C05_DIGESTS.items():
            sealed = json.loads((profiles / name).read_text())
            c05 = json.loads((PROFILES / name).read_text())
            self.assertEqual(sealed["resolvedMaterialSha256"], digest, name)
            self.assertEqual(record["documents"][name]["resolvedMaterialSha256"], digest)
            self.assertEqual(record["documents"][name]["movedFromC05"], [])
            self.assertEqual(record["documents"][name]["addedToTwinLeafSet"], [])
            self.assertEqual(sealed["patch"], c05["patch"], name)
            self.assertEqual(sealed["recordedBy"], "W45 G1")
            self.assertEqual(sealed["supersedes"]["sha256"], before[name])
        for p in profiles.glob("*.json"):
            if p.name not in C05_DIGESTS and p.name != "sealed-manifest.json":
                self.assertEqual(sha(p), before[p.name], p.name)
        # The shipped documents themselves never moved.
        self.assertEqual({p.name: sha(p) for p in PROFILES.glob("*.json")}, before)

    def test_the_operators_key_is_admitted_in_both_light_documents(self):
        code, out, profiles, manifest = self.seal("joint-operator")
        self.assertEqual(code, 0, out)
        record = json.loads(manifest.read_text())["documents"]
        active = record["apple-macos-27.0-1x-light-standard-glass0.25.json"]
        receded = record["apple-macos-27.0-1x-light-standard-glass0.25-receded.json"]
        self.assertEqual(active["addedToTwinLeafSet"], ["sizeHeavySecondShareFar2x"])
        self.assertEqual(receded["addedToTwinLeafSet"], ["sizeHeavySecondShareFar2x"])
        self.assertIn("sizeHeavySecondShareFar2x", active["movedFromC05"])
        for name in C05_DIGESTS:
            endpoint = json.loads((self.candidates / "joint-operator" /
                                   ("receded.light.json" if "receded" in name else "active.light.json")).read_text())
            self.assertEqual(json.loads((profiles / name).read_text())["resolvedMaterialSha256"],
                             endpoint["resolvedMaterialSha256"])

    def test_a_second_seal_over_sealed_bytes_refuses(self):
        code, out, profiles, _ = self.seal("c05-control", method=self.no_method)
        self.assertEqual(code, 0, out)
        code, out, _, _ = self.seal("c05-control", method=self.no_method, profiles=profiles)
        self.assertNotEqual(code, 0)
        self.assertIn("not the published c05 document", out)

    def test_a_receded_leaf_outside_the_narrowed_set_refuses(self):
        code, out, profiles, _ = self.seal("receded-width")
        self.assertNotEqual(code, 0)
        self.assertIn("X44", out)
        self.assertEqual(sha(profiles / "apple-macos-27.0-1x-light-standard-glass0.25.json"),
                         sha(PROFILES / "apple-macos-27.0-1x-light-standard-glass0.25.json"),
                         "a refused seal writes neither document")

    def test_an_undeclared_move_refuses(self):
        code, out, _, _ = self.seal("undeclared")
        self.assertNotEqual(code, 0)
        self.assertIn("moves undeclared leaves", out)

    def test_a_moved_leaf_with_no_method_refuses(self):
        code, out, _, _ = self.seal("joint-operator", method=self.no_method)
        self.assertNotEqual(code, 0)
        self.assertIn("no method recorded", out)

    def test_w44s_candidates_and_profiles_refuse(self):
        code, out, _, _ = self.seal("m3-t0.1", candidates=W.RESULTS / "2026-10-03-w44-g1-refit/fit/candidates")
        self.assertNotEqual(code, 0)
        self.assertIn("X58", out)
        w44_profiles = Path.home() / "vitrea-w44" / "w45-red-case-profiles"
        code, out, _, _ = self.seal("c05-control", method=self.no_method, profiles=w44_profiles)
        self.assertNotEqual(code, 0)
        self.assertIn("X58", out)
        self.assertFalse(w44_profiles.exists())


if __name__ == "__main__":
    unittest.main()
