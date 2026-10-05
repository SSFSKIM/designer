#!/usr/bin/env python3.12
"""W47 G0 (c): W46's seal test (`results/2026-10-05-w46-g0-declaration/seal/test_seal.py`), ported by copy
and re-bound (charter clause 2, G0 (c); X60, X62, X64, X67). What W47 adds:

- **The pin with X67** (G0 (c): "a seal with every X67 key materialised at its resolved value
  reproduces `b074fc6913a91c66` / `280f0fddf014e0f6`"). It runs NOW for every admitted key the runtime
  knows (X64's, the occlusion gain, the span tops and the receded nested `optics.regular.blurSigma`),
  each recorded `materialised`; and it is WAITING (skipped with the reason, never passed) for the
  whole set with operator 1's and 2's leaves until their runtime merges (G0 (a), (b)).
- **The seal's list is the bindings'** (`seal.ts --may-add` equals `bindings.ADMITTED`'s keys).
- **A key the runtime does not know refuses** even when the endpoint's recorded digest matches (the
  runtime drops an unknown key, so the digest alone cannot tell): a red case writes an operator leaf
  into a built endpoint while the runtime lacks it.
- W46's evidence and scratch refused beside W44's and W45's; the receded `tintAlpha` move is 0.8
  (X68's receded domain {0.8, 0.89}).

W46's text follows, unchanged; where it says W46 it is W47.

W46 G0 (a): the seal port, tested on the snapshots before use (charter clauses 1 and 8; X60, X62,
X64). Every case seals into a SCRATCH COPY of `packages/calibration/profiles/` (`--profiles`) with its
record beside it, from candidates W46's builder writes into a scratch root, so no shipped document is
touched.

- **X64's digest neutrality, by test.** The snapshot candidate with EVERY X64 key materialised at its
  inherited value (`bindings.X64`) seals to `b074fc6913a91c66` / `280f0fddf014e0f6`, each key recorded
  `materialised`, with every other profile file byte-identical; the snapshot candidate with no
  override seals to the same digests with the snapshot's patch.
- **A real move seals** (the active `tintAlpha` and a receded X64 key moved), with its methods.
- **The record names the scale-separable reading** (W46 G1, Decision Log 8 item 4): a candidate with
  a composed `summary.json` records it and each scale renderer's `cuts-<s>x.json.gz` with their
  hashes; one without records null; a summary naming a renderer with no cut refuses.
- **Red cases**: a second seal over sealed bytes; a receded leaf outside X64 written into a built
  candidate's endpoint; an undeclared moved leaf; a moved leaf with no method; a W44 or W45 candidate
  or profiles directory; a candidate whose spec moves the light material.

    cd packages/calibration/results/2026-10-06-w47-g0-operators/seal
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
        "receded.dark": {"optics.regular.tintAlpha": 0.8, "sizeScatterRampStartFar1x": 0.04}}
OPERATORS = W.OPERATOR_1 + W.OPERATOR_2
TSX = W.CAL / "node_modules" / ".bin" / "tsx"


def runtime_knows() -> set:
    """The operator leaves the runtime the builder imports carries (`build-candidate.ts --tables`)."""
    got = subprocess.run([str(TSX), str(W.BUILDER), "--tables"], cwd=W.CAL, capture_output=True, text=True,
                         env=dict(os.environ, W47_CANDIDATE_ROOT=tempfile.mkdtemp(prefix="w47-seal-")))
    assert got.returncode == 0, got.stdout + got.stderr
    return set(json.loads(got.stdout)["runtimeKnows"])


KNOWS = runtime_knows()
LACKS = [k for k in OPERATORS if k not in KNOWS]
WAITING = (f"WAITING for operator {' and '.join(sorted({'1' if k in W.OPERATOR_1 else '2' for k in LACKS}))} "
           f"runtime: DEFAULT_MATERIAL_PROFILE on this branch has no {', '.join(LACKS)} (G0 (a), (b) not merged)"
           if LACKS else None)
X67_KNOWN = {slot: {k: v for k, v in W.ADMITTED[slot].items() if k not in OPERATORS} for slot in W.MOVING_SLOTS}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(root: Path, label: str, overrides: dict) -> subprocess.CompletedProcess:
    spec = root / f"{label}.spec.json"
    spec.write_text(json.dumps(dict(label=label, note="test_seal", overrides=overrides)))
    return subprocess.run(["pnpm", "exec", "tsx", str(W.BUILDER), str(spec)], cwd=W.CAL,
                          env=dict(os.environ, W47_CANDIDATE_ROOT=str(root / "candidates")),
                          capture_output=True, text=True)


class Seal(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(tempfile.mkdtemp(prefix="w47-seal-"))
        cls.candidates = cls.root / "candidates"
        labels = [("snapshot", {}), ("x64", W.X64), ("x67-known", X67_KNOWN), ("move", MOVE), ("undeclared", MOVE),
                  ("receded-extra", {}), ("light-spec", {}), ("read", MOVE), ("read-no-cut", MOVE),
                  ("unknown-leaf", {})]
        if not LACKS:
            labels.append(("x67", W.ADMITTED))
        for label, overrides in labels:
            got = build(cls.root, label, overrides)
            assert got.returncode == 0, got.stdout + got.stderr
        # An operator leaf the runtime does not know, written into a built receded endpoint at its
        # identity 0 with the declaration re-hashed: the digest still matches (the runtime drops the
        # key), so only the seal's read-back guard stands in the way.
        if LACKS:
            folder = cls.candidates / "unknown-leaf"
            endpoint = folder / "receded.dark.json"
            doc = json.loads(endpoint.read_text())
            doc["patch"][LACKS[0]] = 0
            endpoint.write_text(json.dumps(doc, indent=2) + "\n")
            declaration = json.loads((folder / "candidate.json").read_text())
            declaration["endpoints"]["receded.dark"]["sha256"] = sha(endpoint)
            (folder / "candidate.json").write_text(json.dumps(declaration, indent=2) + "\n")
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
        # Composed readings in the fit driver's layout: `read` names two scale renderers whose cuts
        # exist; `read-no-cut` names one whose 2x cut is absent.
        for label, renderers in (("read", ("twin-a", "twin-b")), ("read-no-cut", ("twin-a", "twin-c"))):
            (cls.candidates / label / "summary.json").write_text(json.dumps(dict(
                label=label, renderers={"1x": dict(label=renderers[0]), "2x": dict(label=renderers[1])})))
        for twin, scale in (("twin-a", "1x"), ("twin-b", "2x")):
            (cls.candidates / twin).mkdir()
            (cls.candidates / twin / f"cuts-{scale}.json.gz").write_bytes(f"{twin} {scale}".encode())
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

    def assert_reproduces(self, label, materialised, keys=None):
        before = {p.name: sha(p) for p in PROFILES.glob("*.json")}
        code, out, profiles, manifest = self.seal(label, method=self.no_method)
        self.assertEqual(code, 0, out)
        record = json.loads(manifest.read_text())
        keys = W.X64 if keys is None else keys
        for name, (slot, digest) in DARK.items():
            sealed = json.loads((profiles / name).read_text())
            self.assertEqual(sealed["resolvedMaterialSha256"], digest, name)
            self.assertEqual(record["documents"][name]["resolvedMaterialSha256"], digest)
            self.assertEqual(sorted(record["documents"][name]["materialised"]),
                             sorted(keys[slot]) if materialised else [])
            self.assertEqual(record["documents"][name]["movedFromSnapshot"],
                             sorted(keys[slot]) if materialised else [])
            self.assertEqual(sealed["recordedBy"], "W47 G1")
            self.assertEqual(sealed["supersedes"]["sha256"], W.DOCUMENT_SHA[slot])
            snapshot = W.document(slot)["patch"]
            if materialised:
                flat = {k: v for k, v in sealed["patch"].items() if k not in keys[slot]}
                if "optics.regular.blurSigma" in keys[slot]:
                    flat = json.loads(json.dumps(flat))
                    self.assertEqual(flat["optics"]["regular"].pop("blurSigma"), keys[slot]["optics.regular.blurSigma"])
                self.assertEqual(flat, snapshot)
                for key in keys[slot]:
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

    def test_x64_and_the_known_x67_keys_materialised_reproduce_both_digests(self):
        """Runs now: X64, sizeOcclusionGain, the span tops and the receded optics.regular.blurSigma."""
        self.assertIn("optics.regular.blurSigma", X67_KNOWN["receded.dark"])
        self.assert_reproduces("x67-known", materialised=True, keys=X67_KNOWN)

    def test_every_x64_and_x67_key_materialised_reproduces_both_digests(self):
        """G0 (c)'s pin with every admitted key named, the operators' leaves included."""
        if WAITING:
            self.skipTest(WAITING)
        self.assert_reproduces("x67", materialised=True, keys=W.ADMITTED)

    def test_the_seals_list_is_the_bindings(self):
        got = subprocess.run(["pnpm", "exec", "tsx", str(SEAL), "--may-add"], cwd=W.CAL, capture_output=True, text=True)
        self.assertEqual(got.returncode, 0, got.stdout + got.stderr)
        may = json.loads(got.stdout.strip().splitlines()[-1])
        self.assertEqual({p: sorted(v) for p, v in may.items()},
                         {"active": sorted(W.ADMITTED["active.dark"]), "receded": sorted(W.ADMITTED["receded.dark"])})

    def test_a_leaf_the_runtime_does_not_know_refuses(self):
        if not LACKS:
            self.skipTest("both operators' runtime has merged; the full X67 pin reads their leaves")
        code, out, profiles, _ = self.seal("unknown-leaf", method=self.no_method)
        self.assertNotEqual(code, 0)
        # The candidate reader refuses an unknown key first (`material-profile-file.ts`); the seal's
        # own read-back guard stands behind it.
        self.assertTrue(f"does not have: {LACKS[0]}" in out or "does not read back" in out, out[-600:])
        for name in DARK:
            self.assertEqual(sha(profiles / name), sha(W.document_path(DARK[name][0])))

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

    def test_the_record_names_the_scale_separable_reading(self):
        code, out, profiles, _ = self.seal("read")
        self.assertEqual(code, 0, out)
        for name in DARK:
            cuts = json.loads((profiles / name).read_text())["measurement"]["cuts"]
            self.assertEqual(cuts["summary"]["sha256"], sha(self.candidates / "read" / "summary.json"))
            for twin, scale in (("twin-a", "1x"), ("twin-b", "2x")):
                path = self.candidates / twin / f"cuts-{scale}.json.gz"
                self.assertEqual(cuts["perScale"][scale], dict(renderer=twin, path=os.path.relpath(path, W.ROOT),
                                                               sha256=sha(path)))
        code, out, profiles, _ = self.seal("move")
        self.assertEqual(code, 0, out)
        for name in DARK:
            self.assertIsNone(json.loads((profiles / name).read_text())["measurement"]["cuts"])

    def test_a_reading_whose_renderer_has_no_cut_refuses(self):
        code, out, profiles, _ = self.seal("read-no-cut")
        self.assertNotEqual(code, 0)
        self.assertIn("carries no cuts-2x.json.gz", out)
        for name in DARK:
            self.assertEqual(sha(profiles / name), sha(W.document_path(DARK[name][0])))

    def test_a_second_seal_over_sealed_bytes_refuses(self):
        code, out, profiles, _ = self.seal("move")
        self.assertEqual(code, 0, out)
        code, out, _, _ = self.seal("move", profiles=profiles)
        self.assertNotEqual(code, 0)
        self.assertIn("not the snapshot", out)

    def test_a_receded_leaf_outside_x64_refuses(self):
        code, out, profiles, _ = self.seal("receded-extra", method=self.no_method)
        self.assertNotEqual(code, 0)
        self.assertIn("X67", out)
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

    def test_w44s_w45s_and_w46s_candidates_and_profiles_refuse(self):
        for candidates in (W.RESULTS / "2026-10-03-w44-g1-refit/fit/candidates",
                           W.RESULTS / "2026-10-03-w45-g1-refit/fit/candidates",
                           W.RESULTS / "2026-10-05-w46-g1-refit/fit/candidates"):
            code, out, _, _ = self.seal("snapshot", candidates=candidates)
            self.assertNotEqual(code, 0)
            self.assertIn("clause 2", out)
        for theirs in (Path.home() / "vitrea-w45" / "w47-red-case-profiles",
                       Path.home() / "vitrea-w46" / "w47-red-case-profiles"):
            code, out, _, _ = self.seal("snapshot", method=self.no_method, profiles=theirs)
            self.assertNotEqual(code, 0)
            self.assertIn("clause 2", out)
            self.assertFalse(theirs.exists())


if __name__ == "__main__":
    unittest.main()
