#!/usr/bin/env python3.12
"""W47 G0 (c): the candidate builder's guards (charter clause 2, G0 (c); X60, X62, X64, X67, X68),
each case built into a scratch root through the real builder. W46's test
(`results/2026-10-05-w46-g0-declaration/fit/test_build_candidate.py`), ported by copy and extended.

Admits: exactly X64's and X67's keys per dark slot (`bindings.ADMITTED`), each alone and all together,
the latter digest-neutral (`b074fc6913a91c66` / `280f0fddf014e0f6`, the light digests the light
snapshots' `3741b229…` / `c4ca0e1c…`); an existing leaf at its shape inside its domain (the dark
`tintAlpha`). The builder's mirrored tables equal the bindings' (`--tables`).

Refuses: every addition X64 and X67 do not list (in either dark slot), an operator-2 key on the active
(X66), the nested body width on the active, an admitted key of the OTHER dark slot, any light
override (X60), a nested unknown path, a non-finite value, a wrong shape, a value outside its declared
domain (X68; operator values included, which the builder checks before it asks the runtime
anything), an operator key while the runtime does not know its leaf (an unknown key would be dropped
from the resolved material silently), a label outside `labels.json`'s pattern, an output root in
W44's, W45's or W46's evidence or scratch or in `profiles/`, and no root.

WAITING (skipped with the reason, never passed silently) until the operators' runtime merges
(G0 (a): `tintAlphaFar1x`/`2x`; G0 (b): `sizeFineTapShare`, `sizeFineTapSigma`, `sizeFineTapSigma2x`):
every admitted key together, operator keys included, digest-neutral; and each operator key admitted
inside its domain and read back from the resolved material.

    cd packages/calibration/results/2026-10-06-w47-g0-operators/fit
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
OPERATORS = W.OPERATOR_1 + W.OPERATOR_2


def build(overrides: dict, label: str = "red-case", root: Path | None = None) -> tuple[int, str, Path]:
    scratch = Path(tempfile.mkdtemp(prefix="w47-builder-"))
    spec = scratch / "spec.json"
    spec.write_text(json.dumps(dict(label=label, note="test", overrides=overrides)))
    out_root = root if root is not None else scratch / "out"
    env = dict(os.environ, W47_CANDIDATE_ROOT=str(out_root))
    got = subprocess.run([str(TSX), str(W.BUILDER), str(spec)], cwd=W.CAL, env=env, capture_output=True, text=True)
    return got.returncode, got.stdout + got.stderr, out_root / label


def tables() -> dict:
    got = subprocess.run([str(TSX), str(W.BUILDER), "--tables"], cwd=W.CAL, capture_output=True, text=True,
                         env=dict(os.environ, W47_CANDIDATE_ROOT=tempfile.mkdtemp(prefix="w47-builder-")))
    assert got.returncode == 0, got.stdout + got.stderr
    return json.loads(got.stdout)


TABLES = tables()
KNOWS = set(TABLES["runtimeKnows"])
LACKS = [k for k in OPERATORS if k not in KNOWS]


def waiting(keys) -> str | None:
    missing = [k for k in keys if k not in KNOWS]
    if not missing:
        return None
    ops = sorted({1 if k in W.OPERATOR_1 else 2 for k in missing})
    return (f"WAITING for operator {' and '.join(map(str, ops))} runtime: DEFAULT_MATERIAL_PROFILE on this "
            f"branch has no {', '.join(missing)} (G0 (a), (b) not merged)")


def endpoint(folder: Path, slot: str) -> dict:
    return json.loads((folder / f"{slot}.json").read_text())


def get(patch: dict, path: str):
    for part in path.split("."):
        patch = patch[part]
    return patch


def known(slot: str) -> dict:
    return {k: v for k, v in W.ADMITTED[slot].items() if k not in OPERATORS}


class Tables(unittest.TestCase):
    def test_the_builders_tables_are_the_bindings(self):
        self.assertEqual(TABLES["ADMITTED"], W.ADMITTED)
        domains = {slot: {k: [[p[0], list(p[1])] if p[0] == "set" else list(p) for p in parts]
                          for k, parts in d.items()} for slot, d in W.DOMAINS.items()}
        self.assertEqual(TABLES["DOMAINS"], domains)


class Admits(unittest.TestCase):
    def assert_neutral(self, overrides: dict, label: str):
        code, out, folder = build(overrides, label=label)
        self.assertEqual(code, 0, out)
        for slot in W.SLOTS:
            doc = endpoint(folder, slot)
            self.assertEqual(doc["resolvedMaterialSha256"], W.DOCUMENT_DIGEST[slot], slot)
            if slot in overrides:
                self.assertEqual(doc["addedLeaves"], sorted(overrides[slot]))
                for key, value in overrides[slot].items():
                    self.assertEqual(get(doc["patch"], key), value)
            else:
                self.assertEqual(doc["patch"], W.document(slot)["patch"])
        return folder

    def test_every_x64_key_together_is_digest_neutral(self):
        folder = self.assert_neutral(W.X64, "x64")
        declaration = json.loads((folder / "candidate.json").read_text())
        self.assertEqual(declaration["name"], "apple-macos-27.0-glass0.25-w47-x64")

    def test_every_admitted_key_the_runtime_knows_together_is_digest_neutral(self):
        """X64 with X67's sizeOcclusionGain, the span tops and the receded body width: runs now."""
        overrides = {slot: known(slot) for slot in W.MOVING_SLOTS}
        self.assertIn("optics.regular.blurSigma", overrides["receded.dark"])
        self.assertIn("sizeScatterSpanMax2x", overrides["active.dark"])
        self.assert_neutral(overrides, "x67-known")

    def test_every_admitted_key_together_is_digest_neutral(self):
        why = waiting(OPERATORS)
        if why:
            self.skipTest(why)
        self.assert_neutral(W.ADMITTED, "x67")

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

    def test_each_known_x67_key_alone_inside_its_domain(self):
        moves = {"sizeOcclusionGain": 0.4, "sizeScatterSpanMax": 160, "sizeScatterSpanMax2x": 128,
                 "optics.regular.blurSigma": 3}
        for slot in W.MOVING_SLOTS:
            for key in known(slot):
                if key in W.X64[slot]:
                    continue
                code, out, folder = build({slot: {key: moves[key]}},
                                          label=f"one-{slot.split('.')[0]}-{key.lower()}")
                self.assertEqual(code, 0, f"{slot} {key}: {out}")
                doc = endpoint(folder, slot)
                self.assertEqual(doc["addedLeaves"], [key])
                self.assertEqual(get(doc["patch"], key), moves[key])
                self.assertNotEqual(doc["resolvedMaterialSha256"], W.DOCUMENT_DIGEST[slot], f"{slot} {key}")

    def test_each_operator_key_admitted_inside_its_domain(self):
        why = waiting(OPERATORS)
        if why:
            self.skipTest(why)
        moves = {"tintAlphaFar1x": 0.2, "tintAlphaFar2x": 0.45, "sizeFineTapShare": 0.5,
                 "sizeFineTapSigma": 3, "sizeFineTapSigma2x": 6}
        for slot in W.MOVING_SLOTS:
            for key in OPERATORS:
                if key not in W.ADMITTED[slot]:
                    continue
                code, out, folder = build({slot: {key: moves[key]}}, label=f"op-{slot.split('.')[0]}-{key.lower()}")
                self.assertEqual(code, 0, f"{slot} {key}: {out}")
                self.assertEqual(endpoint(folder, slot)["patch"][key], moves[key])

    def test_an_existing_leaf_moves_at_its_shape(self):
        code, out, folder = build({"active.dark": {"optics.regular.tintAlpha": 0.7},
                                   "receded.dark": {"optics.regular.tintAlpha": 0.8}}, label="ta")
        self.assertEqual(code, 0, out)
        self.assertEqual(endpoint(folder, "active.dark")["patch"]["optics"]["regular"]["tintAlpha"], 0.7)
        self.assertEqual(endpoint(folder, "receded.dark")["patch"]["optics"]["regular"]["tintAlpha"], 0.8)
        self.assertNotIn("addedLeaves", endpoint(folder, "active.dark"))
        for slot in ("active.light", "receded.light"):
            self.assertEqual(endpoint(folder, slot)["resolvedMaterialSha256"], W.DOCUMENT_DIGEST[slot])


class Refuses(unittest.TestCase):
    def refused(self, overrides, needle, root=None, label="red-case"):
        code, out, folder = build(overrides, root=root, label=label)
        self.assertNotEqual(code, 0, out)
        self.assertIn(needle, out)
        self.assertFalse(folder.exists(), "a refused build writes nothing")

    def test_additions_x64_and_x67_do_not_list(self):
        for slot in ("active.dark", "receded.dark"):
            for key in ("sizeScatterHeavyShareThick2x", "sizeScatterRampReach2xPx", "sizeHeavySecondShareFar",
                        "sizeSpanMax", "tintAlphaFar"):
                self.refused({slot: {key: 0.1}}, "X67")

    def test_an_operator_2_key_on_the_active(self):
        for key in W.OPERATOR_2:
            self.refused({"active.dark": {key: 0}}, "X67")

    def test_the_nested_body_width_on_the_active(self):
        self.refused({"active.dark": {"optics.regular.blurSigma": 1.25}}, "X67")

    def test_the_other_slots_admitted_keys(self):
        for key in set(W.ADMITTED["active.dark"]) - set(W.ADMITTED["receded.dark"]):
            if key not in W.document("receded.dark")["patch"]:
                self.refused({"receded.dark": {key: 0.3}}, "X67")
        for key in set(W.ADMITTED["receded.dark"]) - set(W.ADMITTED["active.dark"]):
            if W.document("active.dark")["patch"].get(key) is None and key != "optics.regular.blurSigma":
                self.refused({"active.dark": {key: 0.3}}, "X67")

    def test_values_outside_the_declared_domains(self):
        cases = [("active.dark", "optics.regular.tintAlpha", 0.6), ("active.dark", "optics.regular.tintAlpha", 0.95),
                 ("receded.dark", "optics.regular.tintAlpha", 0.7), ("receded.dark", "optics.regular.tintAlpha", 0.9),
                 ("active.dark", "sizeOcclusionGain", 0.04), ("receded.dark", "sizeOcclusionGain", 0.61),
                 ("active.dark", "sizeScatterSpanMax", 150), ("receded.dark", "sizeScatterSpanMax2x", 512),
                 ("receded.dark", "optics.regular.blurSigma", 1.0), ("receded.dark", "optics.regular.blurSigma", 5)]
        for slot, key, value in cases:
            self.refused({slot: {key: value}}, "X68")

    def test_operator_values_outside_their_domains_refuse_whatever_the_runtime_knows(self):
        cases = [("active.dark", "tintAlphaFar1x", -0.1), ("active.dark", "tintAlphaFar2x", 0.61),
                 ("receded.dark", "tintAlphaFar1x", 0.7), ("receded.dark", "sizeFineTapShare", 1.2),
                 ("receded.dark", "sizeFineTapShare", -0.1), ("receded.dark", "sizeFineTapSigma", 1.0),
                 ("receded.dark", "sizeFineTapSigma", 7), ("receded.dark", "sizeFineTapSigma2x", 0.5)]
        for slot, key, value in cases:
            self.refused({slot: {key: value}}, "X68")

    def test_an_operator_key_the_runtime_lacks_refuses(self):
        if not LACKS:
            self.skipTest("both operators' runtime has merged; the admitting cases read them")
        for key in LACKS:
            self.refused({"receded.dark": {key: 0}}, "the runtime does not know")
            if key in W.ADMITTED["active.dark"]:
                self.refused({"active.dark": {key: 0}}, "the runtime does not know")

    def test_a_light_override(self):
        for slot in ("active.light", "receded.light"):
            self.refused({slot: {"sizeScatterFloor2x": 1}}, "X60")
            self.refused({slot: {"optics.regular.tintAlpha": 0.6}}, "X60")

    def test_a_nested_unknown_path(self):
        self.refused({"active.dark": {"optics.regular.sizeScatterFloor2x": 1}}, "X67")

    def test_a_non_finite_or_misshapen_value(self):
        self.refused({"active.dark": {"sizeScatterFloor2x": "1"}}, "finite")
        self.refused({"active.dark": {"optics.regular.tintAlpha": [0.7]}}, "the spec gives")

    def test_a_label_outside_the_grammar(self):
        self.refused({}, "pattern", label="d-s2-Rta0.6")

    def test_roots_in_other_waves_or_profiles(self):
        for root in (W.RESULTS / "2026-10-03-w45-g1-refit" / "fit" / "candidates",
                     W.RESULTS / "2026-10-03-w44-g1-refit" / "fit" / "candidates",
                     W.RESULTS / "2026-10-05-w46-g1-refit" / "fit" / "candidates",
                     Path.home() / "vitrea-w45" / "g1-scratch" / "w47-red-case",
                     Path.home() / "vitrea-w46" / "g1-scratch" / "w47-red-case"):
            self.refused({}, "clause 2", root=root)
        self.refused({}, "X62", root=W.PROFILES_DIR)

    def test_no_root(self):
        scratch = Path(tempfile.mkdtemp(prefix="w47-builder-"))
        spec = scratch / "spec.json"
        spec.write_text(json.dumps(dict(label="no-root", overrides={})))
        env = {k: v for k, v in os.environ.items() if k != "W47_CANDIDATE_ROOT"}
        got = subprocess.run([str(TSX), str(W.BUILDER), str(spec)], cwd=W.CAL, env=env, capture_output=True, text=True)
        self.assertNotEqual(got.returncode, 0)
        self.assertIn("W47_CANDIDATE_ROOT", got.stdout + got.stderr)


if __name__ == "__main__":
    unittest.main()
