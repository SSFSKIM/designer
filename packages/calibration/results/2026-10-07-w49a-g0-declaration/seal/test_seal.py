"""W49a G0: the seal's X75 and X76 refusals and its one-file write (`seal/seal.ts`; charter Decision Logs 1, 3).

Every case seals into a scratch COPY of `profiles/` with its record beside it; nothing under the package's
`profiles/` is written.

    python3.12 -B -m unittest -v test_seal      (from this directory)
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
G0 = HERE.parent
CAL = G0.parents[1]
SEAL = HERE / "seal.ts"
BUILDER = G0 / "fit" / "build-candidate.ts"
RECEDED = "apple-macos-27.0-1x-dark-standard-glass0.25-receded.json"
# The eleven receded leaves W48's seal recorded as materialised, other than the two far deltas.
MATERIALISED = ["optics.regular.blurSigma", "sizeFineTapShare", "sizeFineTapSigma", "sizeFineTapSigma2x",
                "sizeHeavySecondShareFar2x", "sizeHeavyTapSigma", "sizeOcclusionGain", "sizeScatterFloor2x",
                "sizeScatterRampStartFar1x", "sizeScatterSpanMax", "sizeScatterSpanMax2x"]
FAR_METHOD = {"tintAlphaFar1x": ["test: the receded far delta, family R"],
              "tintAlphaFar2x": ["test: the receded far delta, family R"]}
HOLDS = {leaf: {"held": [f"test: {leaf} held at the active's value"]} for leaf in MATERIALISED}
TSX = ["pnpm", "exec", "tsx"]


def run(argv, **env):
    got = subprocess.run(argv, cwd=CAL, capture_output=True, text=True, env={**os.environ, **env})
    return got.returncode, got.stdout + got.stderr


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Seal(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="w49a-seal-"))
        self.candidates = self.tmp / "candidates"
        self.profiles = self.tmp / "profiles"
        shutil.copytree(CAL / "profiles", self.profiles)

    def build(self, v, label):
        spec = self.tmp / f"{label}.json"
        spec.write_text(json.dumps(dict(label=label, base="b2d074", overrides={
            "receded.dark": {"tintAlphaFar1x": v, "tintAlphaFar2x": v}})))
        code, out = run([*TSX, str(BUILDER), str(spec)], W49A_CANDIDATE_ROOT=str(self.candidates))
        self.assertEqual(code, 0, out)

    def seal(self, label, method, manifest="manifest.json"):
        path = self.tmp / f"method-{label}-{manifest}"
        path.write_text(json.dumps(method))
        return run([*TSX, str(SEAL), label, str(path), "--candidates", str(self.candidates),
                    "--profiles", str(self.profiles), "--manifest", str(self.tmp / manifest)])

    def test_x76_refuses_a_silent_inheritance_then_seals_with_explicit_holds(self):
        self.build(0.09, "t-seal-009")
        code, out = self.seal("t-seal-009", FAR_METHOD)
        self.assertNotEqual(code, 0)
        self.assertIn("11 leaf/leaves would be inherited from the active silently", out)
        self.assertIn("(X76)", out)
        for leaf in MATERIALISED:
            self.assertIn(leaf, out)
        untouched = {f.name: sha(f) for f in self.profiles.iterdir() if f.name != RECEDED}
        code, out = self.seal("t-seal-009", {**FAR_METHOD, **HOLDS})
        self.assertEqual(code, 0, out)
        doc = json.loads((self.profiles / RECEDED).read_text())
        self.assertEqual(doc["recordedBy"], "W49a G1")
        self.assertEqual(doc["patch"]["tintAlphaFar1x"], 0.09)
        statuses = {k: v.get("status") for k, v in doc["entries"].items() if isinstance(v, dict)}
        self.assertNotIn("materialised", statuses.values())
        for leaf in MATERIALISED:
            self.assertEqual(statuses[leaf], "held", leaf)
        self.assertEqual(statuses["tintAlphaFar1x"], "measured")
        candidate = json.loads((self.candidates / "t-seal-009" / "receded.dark.json").read_text())
        self.assertEqual(doc["resolvedMaterialSha256"], candidate["resolvedMaterialSha256"])
        self.assertEqual({f.name: sha(f) for f in self.profiles.iterdir() if f.name != RECEDED}, untouched)
        # It runs once: the receded file is no longer the snapshot's bytes.
        code, out = self.seal("t-seal-009", {**FAR_METHOD, **HOLDS}, manifest="again.json")
        self.assertNotEqual(code, 0)
        self.assertIn("the seal runs once", out)

    def test_a_moved_leaf_needs_its_method(self):
        self.build(0.1, "t-seal-01")
        code, out = self.seal("t-seal-01", HOLDS)
        self.assertNotEqual(code, 0)
        self.assertIn("no method recorded for the moved leaf tintAlphaFar1x", out)

    def test_x75_refuses_an_opaque_candidate_before_the_digest(self):
        # The builder never makes one (X75 refuses there too), so a built far-0.15 candidate is tampered
        # to far 0.2 with its digest and hash re-stated, which only the seal's own X75 can refuse.
        self.build(0.15, "t-seal-opaque")
        folder = self.candidates / "t-seal-opaque"
        tamper = self.tmp / "tamper.ts"
        tamper.write_text(f"""
import {{ readFileSync, writeFileSync }} from "node:fs";
import {{ createHash }} from "node:crypto";
import {{ DEFAULT_MATERIAL_PROFILE, withMaterialOverrides }} from "@vitrea/renderer-webgpu";
import {{ resolvedDigest }} from "{CAL}/scripts/candidate-document";
const dir = {json.dumps(str(folder))};
const active = JSON.parse(readFileSync(dir + "/active.dark.json", "utf8"));
const receded = JSON.parse(readFileSync(dir + "/receded.dark.json", "utf8"));
receded.patch.tintAlphaFar1x = 0.2; receded.patch.tintAlphaFar2x = 0.2;
receded.resolvedMaterialSha256 = resolvedDigest(withMaterialOverrides(
  withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, active.patch), receded.patch));
const text = JSON.stringify(receded, null, 2) + "\\n";
writeFileSync(dir + "/receded.dark.json", text);
const c = JSON.parse(readFileSync(dir + "/candidate.json", "utf8"));
c.endpoints["receded.dark"].sha256 = createHash("sha256").update(text).digest("hex");
writeFileSync(dir + "/candidate.json", JSON.stringify(c, null, 2) + "\\n");
const s = JSON.parse(readFileSync(dir + "/spec.json", "utf8"));
s.overrides["receded.dark"] = {{ tintAlphaFar1x: 0.2, tintAlphaFar2x: 0.2 }};
writeFileSync(dir + "/spec.json", JSON.stringify(s));
""")
        code, out = run([*TSX, str(tamper)])
        self.assertEqual(code, 0, out)
        code, out = self.seal("t-seal-opaque", {**FAR_METHOD, **HOLDS})
        self.assertNotEqual(code, 0)
        self.assertIn("receded.dark: draws opaque glass, alphaBase above 0.95 (X75)", out)
        self.assertEqual(sha(self.profiles / RECEDED), sha(CAL / "profiles" / RECEDED))

    def test_other_waves_paths_refuse(self):
        code, out = run([*TSX, str(SEAL), "x", "m.json", "--candidates",
                         str(CAL / "results" / "2026-10-06-w48-g1-refit" / "fit" / "candidates"),
                         "--manifest", str(self.tmp / "m.json")])
        self.assertNotEqual(code, 0)
        self.assertIn("W44's-W48's evidence or scratch", out)


if __name__ == "__main__":
    unittest.main()
