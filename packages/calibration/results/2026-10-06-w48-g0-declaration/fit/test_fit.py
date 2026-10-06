"""W48 G0 (b): W47's fit-driver and search tests, run under W48's bindings (charter clause 2; Design
"The moves"; X60, X64, X67, X68). W47's `fit/test_fit.py` is loaded by path and every case of it runs
unchanged but four, which assert W47's draft or W47's message and are W48's here:

- `Part2.test_other_waves_part_hashes_refuse`: the refusal names four waves and W47's part hashes refuse;
- `Part2.test_stage_2_admits_the_receded_start_a_stage_1_point_leaves`: W47's case moves the active 2x
  second tap, which W48's stage 1 does not search (ladder (ii) met no rung); W48's case takes a stage-1
  span-law point (far deltas, span tops, the gain) and admits the receded start it leaves, a receded move
  still held to the declared domain;
- `CrossedFactorial.test_the_tap_is_crossed_into_the_span_law`: W48's span law is ONE factorial of its six
  keys with no tap and nothing fixed;
- `CrossedFactorial.test_points_and_renders_per_scale`: the full counts are `test_stage_sizes.py`'s.

W47's module imports `declare` by its bare name only for `drop_leaf` in the replaced count case; a stub
stands in while it imports, so neither W47's nor W48's declaration tool is loaded here.

    python3.12 -B -m unittest -v test_fit      (from this directory)
"""
from __future__ import annotations

import json
import sys
import types
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import inherited_suite as S  # noqa: E402

W = S.W
T = S.module("fit/test_fit.py", importing=mock.patch.dict(sys.modules, {"declare": types.SimpleNamespace()}))
fit, search = T.fit, T.search
REPLACED = {
    "Part2.test_other_waves_part_hashes_refuse": "the W48 refusal names four waves; W47's part hashes added",
    "Part2.test_stage_2_admits_the_receded_start_a_stage_1_point_leaves": "W48's stage 1 has no second tap",
    "CrossedFactorial.test_the_tap_is_crossed_into_the_span_law": "W48's span law has no tap",
    "CrossedFactorial.test_points_and_renders_per_scale": "test_stage_sizes.py counts W48's draft in full",
}
SPAN = ["optics.regular.tintAlpha", "tintAlphaFar1x", "tintAlphaFar2x", "sizeScatterSpanMax", "sizeScatterSpanMax2x",
        "sizeOcclusionGain"]


class W48Part2(unittest.TestCase):
    def test_other_waves_part_hashes_refuse(self):
        for digest in ("e6874e02902755c8648e7fcce29568d326544398229c20d08ce7d24ddfdc5433",
                       "ac642fea4637995c8901aa0f096769516b629273cca187b01b3754385043df55",
                       "2d6d49ad7af5dc9190227ba02f57e3eb9681a85f31890f127e6c08c621103579",     # W47 part 1
                       "2d4a2c7f73b5a0708c1e80ff06b64043657b0f7fafe3c05c3393da84d769c30e"):    # W47, amended
            with T.SyntheticPart2(digest=digest):
                with self.assertRaisesRegex(W.Refusal, "W44, W45, W46 or W47 part hash"):
                    fit.part2()

    def test_stage_2_admits_the_receded_start_a_stage_1_point_leaves(self):
        draft = json.loads(W.DRAFT.read_text())
        with T.SyntheticPart2(draft):
            stage1 = {"active.dark": {"optics.regular.tintAlpha": 0.7, "tintAlphaFar1x": 0.3, "tintAlphaFar2x": 0.45,
                                      "sizeScatterSpanMax": 128, "sizeScatterSpanMax2x": 160, "sizeOcclusionGain": 0.6}}
            fit.check_overrides(stage1)
            start = fit.materialise(stage1, "receded.dark")
            for leaf in ("tintAlphaFar1x", "tintAlphaFar2x", "sizeScatterSpanMax", "sizeScatterSpanMax2x",
                         "sizeOcclusionGain"):
                self.assertEqual(start["receded.dark"][leaf], stage1["active.dark"][leaf], leaf)
            fit.check_overrides(start)
            moved = json.loads(json.dumps(start))
            moved["receded.dark"].update(sizeFineTapShare=0.75, sizeFineTapSigma=4, sizeFineTapSigma2x=6)
            moved["receded.dark"]["optics.regular.blurSigma"] = 3
            fit.check_overrides(moved)                                  # a move inside the declared domains
            for leaf, value in (("sizeFineTapShare", 1.1), ("sizeFineTapSigma", 7), ("optics.regular.blurSigma", 1.75)):
                bad = json.loads(json.dumps(moved))
                bad["receded.dark"][leaf] = value
                with self.assertRaisesRegex(W.Refusal, "outside", msg=leaf):
                    fit.check_overrides(bad)


class W48SpanLaw(unittest.TestCase):
    def test_the_span_law_is_one_factorial_with_no_tap(self):
        draft = json.loads(W.DRAFT.read_text())
        stage1 = draft["moves"][0]
        self.assertEqual(stage1["familyOrder"], ["span-law", "rest-scatter"])
        span = stage1["families"]["span-law"]
        self.assertEqual(list(span["leaves"]), SPAN)
        self.assertEqual([g["keys"] for g in span["factorialGroups"]], [SPAN])
        self.assertNotIn("fixed", span)
        self.assertFalse(any(s.get("conditional") for s in span["leaves"].values()))
        self.assertEqual(search.steps_of(span, "d0219"), [SPAN])


def load_tests(loader, tests, pattern):
    return S.suite(loader, tests, T, REPLACED)


if __name__ == "__main__":
    unittest.main()
