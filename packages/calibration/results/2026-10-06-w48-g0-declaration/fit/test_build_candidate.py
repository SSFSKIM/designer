"""W48 G0 (b): W47's builder tests, run under W48's bindings against W48's COPY of the builder
(`bindings.BUILDER` = `fit/build-candidate.ts` here, whose diff from W47's is `tools/ts_copies.py`; W47's
module reads `W.BUILDER`, so every case drives W48's copy). One W47 case asserts the candidate's name
carries "w47"; it is W48's here (the name and the snapshot path a candidate records are W48's). Among the
carried cases: every X64 and X67 key together at its resolved value is digest-neutral on all four slots
(`b074fc6913a91c66` / `280f0fddf014e0f6` dark, `3741b22934f17f4d` / `c4ca0e1cd6791bde` light), the builder's
tables equal `bindings.ADMITTED` and `DOMAINS`, and X68's domains refuse. W48 adds W47's places refused.

    python3.12 -B -m unittest -v test_build_candidate      (from this directory)
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import inherited_suite as S  # noqa: E402

W = S.W
W47_TESTS = S.module("fit/test_build_candidate.py")


class W48Builder(W47_TESTS.Admits):
    def test_every_x64_key_together_is_digest_neutral(self):
        folder = self.assert_neutral(W.X64, "x64")
        declaration = json.loads((folder / "candidate.json").read_text())
        self.assertEqual(declaration["name"], "apple-macos-27.0-glass0.25-w48-x64")
        for slot in W.SLOTS:
            doc = W47_TESTS.endpoint(folder, slot)
            self.assertEqual(doc["derivedFrom"]["path"],
                             f"packages/calibration/results/2026-10-06-w48-g0-declaration/documents/"
                             f"{W.DOCUMENT_SHA[slot][:12]}.json")
            self.assertTrue(doc["recordedBy"].startswith("W48, scratch candidate"))

    def test_the_four_digests_with_every_admitted_key(self):
        self.assertEqual(W.DOCUMENT_DIGEST, {"active.dark": "b074fc6913a91c66", "receded.dark": "280f0fddf014e0f6",
                                             "active.light": "3741b22934f17f4d", "receded.light": "c4ca0e1cd6791bde"})
        self.assertIsNone(W47_TESTS.waiting(W47_TESTS.OPERATORS))
        self.assert_neutral(W.ADMITTED, "x67-w48")

    def test_a_w47_root_refuses(self):
        for root in (W.W47_G0 / "fit" / "candidates", Path.home() / "vitrea-w47" / "g1-scratch"):
            code, out, _ = W47_TESTS.build({}, label="w47-root", root=root)
            self.assertNotEqual(code, 0)
            self.assertIn("W47's evidence or scratch; W48 builds into its own", out)

    def test_the_builder_driven_is_w48s_copy(self):
        self.assertEqual(W.BUILDER, W.G0 / "fit" / "build-candidate.ts")


# W48Builder subclasses W47's `Admits` for its fixtures; W47's other Admits cases run once, in W47's class.
for _name in [n for n in dir(W47_TESTS.Admits) if n.startswith("test_") and n not in W48Builder.__dict__]:
    setattr(W48Builder, _name, None)


def load_tests(loader, tests, pattern):
    return S.suite(loader, tests, W47_TESTS, {
        "Admits.test_every_x64_key_together_is_digest_neutral": "the name is w48: W48Builder's case"})


if __name__ == "__main__":
    unittest.main()
