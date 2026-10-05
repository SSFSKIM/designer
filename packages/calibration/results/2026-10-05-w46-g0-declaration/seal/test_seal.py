#!/usr/bin/env python3.12
"""W46 G0 (a): the seal port, tested on the snapshots before use (charter clauses 1 and 8; X60, X62,
X64). Every case seals into a SCRATCH COPY of `packages/calibration/profiles/` (`--profiles`) with its
record beside it, from candidates W46's builder writes into a scratch root, so no shipped document is
touched.

- **X64's digest neutrality, by test.** The snapshot candidate with EVERY X64 key materialised at its
  inherited value (`bindings.X64`) seals to `b074fc6913a91c66` / `280f0fddf014e0f6`, each key recorded
  `materialised`, with every other profile file byte-identical; the snapshot candidate with no
  override seals to the same digests with the snapshot's patch.
- **A real move seals** (the active `tintAlpha` and a receded X64 key moved), with its methods.
- **Red cases**: a second seal over sealed bytes; a receded leaf outside X64 written into a built
  candidate's endpoint; an undeclared moved leaf; a moved leaf with no method; a W44 or W45 candidate
  or profiles directory; a candidate whose spec moves the light material.

    cd packages/calibration/results/2026-10-05-w46-g0-declaration/seal
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
sys.path.insert(0, str(HERE.parent))
import bindings as W  # noqa: E402

SEAL = HERE / "seal.ts"
PROFILES = W.PROFILES_DIR
DARK = {"apple-macos-27.0-1x-dark-standard-glass0.25.json": ("active.dark", "b074fc6913a91c66"),
        "apple-macos-27.0-1x-dark-standard-glass0.25-receded.json": ("receded.dark", "280f0fddf014e0f6")}
MOVE = {"active.dark": {"optics.regular.tintAlpha": 0.7},
        "receded.dark": {"optics.regular.tintAlpha": 0.6, "sizeScatterRampStartFar1x": 0.04}}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(root: Path, label: str, overrides: dict) -> subprocess.CompletedProcess:
    spec = root / f"{label}.spec.json"
    spec.write_text(json.dumps(dict(label=label, note="test_seal", overrides=overrides)))
    return subprocess.run(["pnpm", "exec", "tsx", str(W.BUILDER), str(spec)], cwd=W.CAL,
                          env=dict(os.environ, W46_CANDIDATE_ROOT=str(root / "candidates")),
                          capture_output=True, text=True)


class Seal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(tempfile.mkdtemp(prefix="w46-seal-"))
        cls.candidates = cls.root / "candidates"
        for label, overrides in (("snapshot", {}), ("x64", W.X64), ("move", MOVE), ("undeclared", MOVE),
                                 ("receded-extra", {}), ("light-spec", {})):
            got = build(cls.root, label, overrides)
            assert got.returncode == 0, got.stdout + got.stderr
        # The candidate's own spec, edited to drop a declared override: the seal must catch the move.
        spec = cls.candidates / "undeclared" / "spec.json"
        body = json.loads(spec.read_text())
        del body["overrides"]["receded.dark"]
        spec.write_text(json.dumps(body))
        # A spec that claims a light override (the builder refuses one; a hand-edited spec must too).
        spec = cls.candidates / "light-spec" / "spec.json"
        spec.write_text(json.dumps(dict(label="light-spec", overrides={"active.light": {"sizeScatterFloor": 0.5}})))
        # A receded leaf outside X64 written into a built endpoint at its runtime default (so the endpoint
        # still resolves to its recorded digest) with the declaration re-hashed: only the seal's own
        # leaf-set guard stands in the way.
        folder = cls.candidates / "receded-extra"
        endpoint = folder / "receded.dark.json"
        doc = json.loads(endpoint.read_text())
        doc["patch"]["sizeScatterHeavyShareThick2x"] = 0
        endpoint.write_text(json.dumps(doc, indent=2) + "\n")
        declaration = json.loads((folder / "candidate.json").read_text())
        declaration["endpoints"]["receded.dark"]["sha256"] = sha(endpoint)
        (folder / "candidate.json").write_text(json.dumps(declaration, indent=2) + "\n")
        cls.method = cls.root / "method.json"
        cls.method.write_text(json.dumps({leaf: ["test_seal: a scratch rehearsal, no fit"]
                                          for slot in MOVE.values() for leaf in slot}))
        cls.no_method = cls.root / "no-method.json"
        cls.no_method.write_text("{}")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.root)

    def seal(self, label, method=None, candidates=None, profiles=None, live=None):
        """Seal into a scratch profiles directory: a copy of `live` (the live profiles by default) whose
        four 0.25 files are then the verified SNAPSHOTS' bytes (X62), so the rehearsal holds after G1's
        seal has moved the live dark pair (the review of G0's builder and seal, P1)."""
        if profiles is None:
            profiles = Path(tempfile.mkdtemp(prefix="profiles-", dir=self.root))
            shutil.rmtree(profiles)
            shutil.copytree(live or PROFILES, profiles)
            for slot in W.SLOTS:
                (profiles / f"{W.DOCUMENT_KEY[slot]}.json").write_bytes(W.document_path(slot).read_bytes())
        manifest = profiles / "sealed-manifest.json"
        got = subprocess.run(["pnpm", "exec", "tsx", str(SEAL), label, str(method or self.method),
                              "--candidates", str(candidates or self.candidates), "--profiles", str(profiles),
                              "--manifest", str(manifest)], cwd=W.CAL, capture_output=True, text=True)
        return got.returncode, got.stdout + got.stderr, profiles, manifest

    def assert_reproduces(self, label, materialised):
        before = {p.name: sha(p) for p in PROFILES.glob("*.json")}
        code, out, profiles, manifest = self.seal(label, method=self.no_method)
        self.assertEqual(code, 0, out)
        record = json.loads(manifest.read_text())
        for name, (slot, digest) in DARK.items():
            sealed = json.loads((profiles / name).read_text())
            self.assertEqual(sealed["resolvedMaterialSha256"], digest, name)
            self.assertEqual(record["documents"][name]["resolvedMaterialSha256"], digest)
            self.assertEqual(sorted(record["documents"][name]["materialised"]),
                             sorted(W.X64[slot]) if materialised else [])
            self.assertEqual(record["documents"][name]["movedFromSnapshot"],
                             sorted(W.X64[slot]) if materialised else [])
            self.assertEqual(sealed["recordedBy"], "W46 G1")
            self.assertEqual(sealed["supersedes"]["sha256"], W.DOCUMENT_SHA[slot])
            snapshot = W.document(slot)["patch"]
            if materialised:
                self.assertEqual({k: v for k, v in sealed["patch"].items() if k not in W.X64[slot]}, snapshot)
                for key in W.X64[slot]:
                    self.assertEqual(sealed["entries"][key]["status"], "materialised")
            else:
                self.assertEqual(sealed["patch"], snapshot)
        for p in profiles.glob("*.json"):
            if p.name not in DARK and p.name != "sealed-manifest.json":
                self.assertEqual(sha(p), before[p.name], p.name)
        self.assertEqual({p.name: sha(p) for p in PROFILES.glob("*.json")}, before)

    def test_the_rehearsal_holds_after_the_live_dark_pair_is_sealed(self):
        # The live dark pair as G1 leaves it: sealed bytes, not the snapshots'. The rehearsal seeds its
        # scratch from the snapshots, so the snapshot seal still reproduces both digests.
        code, out, sealed, _ = self.seal("move")
        self.assertEqual(code, 0, out)
        live = Path(tempfile.mkdtemp(prefix="live-", dir=self.root))
        shutil.rmtree(live)
        shutil.copytree(PROFILES, live)
        for name in DARK:
            (live / name).write_bytes((sealed / name).read_bytes())
            self.assertNotEqual(sha(live / name), W.DOCUMENT_SHA[DARK[name][0]])
        code, out, profiles, _ = self.seal("snapshot", method=self.no_method, live=live)
        self.assertEqual(code, 0, out)
        for name, (slot, digest) in DARK.items():
            self.assertEqual(json.loads((profiles / name).read_text())["resolvedMaterialSha256"], digest)

    def test_x64_materialised_reproduces_both_digests(self):
        self.assert_reproduces("x64", materialised=True)

    def test_the_snapshot_itself_reproduces_both_digests(self):
        self.assert_reproduces("snapshot", materialised=False)

    def test_a_real_move_seals_with_its_methods(self):
        code, out, profiles, manifest = self.seal("move")
        self.assertEqual(code, 0, out)
        record = json.loads(manifest.read_text())["documents"]
        receded = record["apple-macos-27.0-1x-dark-standard-glass0.25-receded.json"]
        self.assertEqual(receded["movedFromSnapshot"], ["optics.regular.tintAlpha", "sizeScatterRampStartFar1x"])
        self.assertEqual(receded["materialised"], [])
        for name, (slot, digest) in DARK.items():
            endpoint = json.loads((self.candidates / "move" / f"{slot}.json").read_text())
            self.assertNotEqual(endpoint["resolvedMaterialSha256"], digest)
            self.assertEqual(json.loads((profiles / name).read_text())["resolvedMaterialSha256"],
                             endpoint["resolvedMaterialSha256"])

    def test_a_second_seal_over_sealed_bytes_refuses(self):
        code, out, profiles, _ = self.seal("move")
        self.assertEqual(code, 0, out)
        code, out, _, _ = self.seal("move", profiles=profiles)
        self.assertNotEqual(code, 0)
        self.assertIn("not the snapshot", out)

    def test_a_receded_leaf_outside_x64_refuses(self):
        code, out, profiles, _ = self.seal("receded-extra", method=self.no_method)
        self.assertNotEqual(code, 0)
        self.assertIn("X64", out)
        self.assertIn("sizeScatterHeavyShareThick2x", out)
        for name in DARK:
            self.assertEqual(sha(profiles / name), sha(PROFILES / name), "a refused seal writes neither document")

    def test_an_undeclared_move_refuses(self):
        code, out, _, _ = self.seal("undeclared")
        self.assertNotEqual(code, 0)
        self.assertIn("moves undeclared leaves", out)

    def test_a_moved_leaf_with_no_method_refuses(self):
        code, out, _, _ = self.seal("move", method=self.no_method)
        self.assertNotEqual(code, 0)
        self.assertIn("no method recorded", out)

    def test_a_light_override_refuses(self):
        code, out, _, _ = self.seal("light-spec", method=self.no_method)
        self.assertNotEqual(code, 0)
        self.assertIn("X60", out)

    def test_w44s_and_w45s_candidates_and_profiles_refuse(self):
        for candidates in (W.RESULTS / "2026-10-03-w44-g1-refit/fit/candidates",
                           W.RESULTS / "2026-10-03-w45-g1-refit/fit/candidates"):
            code, out, _, _ = self.seal("snapshot", candidates=candidates)
            self.assertNotEqual(code, 0)
            self.assertIn("clause 1", out)
        theirs = Path.home() / "vitrea-w45" / "w46-red-case-profiles"
        code, out, _, _ = self.seal("snapshot", method=self.no_method, profiles=theirs)
        self.assertNotEqual(code, 0)
        self.assertIn("clause 1", out)
        self.assertFalse(theirs.exists())


if __name__ == "__main__":
    unittest.main()
