"""W48 G0 (b): W47's seal tests, run unchanged under W48's bindings against W48's COPY of the seal
(charter clause 2; X62, X64, X67). W47's `seal/test_seal.py` names its seal as the file beside it; here
its module attribute `SEAL` is pointed at `bindings.SEAL` (`seal/seal.ts`, W48's copy, whose diff from
W47's is `tools/ts_copies.py`), so every case drives the tool G1 will run. Among them, the pin: the
snapshots sealed with every X64 and X67 key materialised at its resolved value reproduce
`b074fc6913a91c66` / `280f0fddf014e0f6`; the list the seal admits equals `bindings.ADMITTED`; a seal into
W44-W46's places refuses. W48 adds the record's wave and W47's places refused.

    python3.12 -B -m unittest -v test_seal      (from this directory)
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import inherited_suite as S  # noqa: E402

W = S.W
W47_TESTS = S.module("seal/test_seal.py", patch={"SEAL": W.SEAL})


# W47's four digest pins assert the sealed record's `recordedBy` is "W47 G1"; W48's seal records "W48 G1"
# (`tools/ts_copies.py`). They run here on a subclass of W47's `Seal` (same fixtures, same cases) whose
# `assert_reproduces` is W47's, copied, with that one expectation W48's.
PINS = ("test_x64_materialised_reproduces_both_digests",
        "test_x64_and_the_known_x67_keys_materialised_reproduce_both_digests",
        "test_every_x64_and_x67_key_materialised_reproduces_both_digests",
        "test_the_snapshot_itself_reproduces_both_digests")
json_, sha, DARK, PROFILES = json, W47_TESTS.sha, W47_TESTS.DARK, W47_TESTS.PROFILES


class W48Pins(W47_TESTS.Seal):
    def assert_reproduces(self, label, materialised, keys=None):
        before = {p.name: sha(p) for p in PROFILES.glob("*.json")}
        code, out, profiles, manifest = self.seal(label, method=self.no_method)
        self.assertEqual(code, 0, out)
        record = json_.loads(manifest.read_text())
        keys = W.X64 if keys is None else keys
        for name, (slot, digest) in DARK.items():
            sealed = json_.loads((profiles / name).read_text())
            self.assertEqual(sealed["resolvedMaterialSha256"], digest, name)
            self.assertEqual(record["documents"][name]["resolvedMaterialSha256"], digest)
            self.assertEqual(sorted(record["documents"][name]["materialised"]),
                             sorted(keys[slot]) if materialised else [])
            self.assertEqual(record["documents"][name]["movedFromSnapshot"],
                             sorted(keys[slot]) if materialised else [])
            self.assertEqual(sealed["recordedBy"], "W48 G1")   # W48: the only change
            self.assertEqual(sealed["supersedes"]["sha256"], W.DOCUMENT_SHA[slot])
            snapshot = W.document(slot)["patch"]
            if materialised:
                flat = {k: v for k, v in sealed["patch"].items() if k not in keys[slot]}
                if "optics.regular.blurSigma" in keys[slot]:
                    flat = json_.loads(json.dumps(flat))
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



for _name in [n for n in dir(W47_TESTS.Seal) if n.startswith("test_") and n not in PINS]:
    setattr(W48Pins, _name, None)


class W48Seal(unittest.TestCase):
    def test_the_seal_driven_is_w48s_copy(self):
        self.assertEqual(W47_TESTS.SEAL, W.G0 / "seal" / "seal.ts")
        text = W.SEAL.read_text()
        self.assertIn('const G1 = join(PACKAGE, "results", "2026-10-06-w48-g1-refit");', text)
        self.assertIn('recordedBy: "W48 G1"', text)

    def test_a_w47_place_refuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            method = Path(tmp) / "m.json"
            method.write_text("{}")
            for where in (W.W47_G0 / "fit" / "candidates", Path.home() / "vitrea-w47" / "g1-scratch"):
                got = subprocess.run(["pnpm", "exec", "tsx", str(W.SEAL), "x", str(method), "--candidates", str(where)],
                                     cwd=W.CAL, capture_output=True, text=True)
                self.assertNotEqual(got.returncode, 0)
                self.assertIn("W47's evidence or scratch; W48 seals its own", got.stderr)


def load_tests(loader, tests, pattern):
    return S.suite(loader, tests, W47_TESTS, {f"Seal.{n}": "recordedBy is W48 G1: run on W48Pins" for n in PINS})


if __name__ == "__main__":
    unittest.main()
