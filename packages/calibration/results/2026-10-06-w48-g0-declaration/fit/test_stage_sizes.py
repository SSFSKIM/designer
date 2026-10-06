"""W48 G0 (b): the part-2 draft's stage sizes, computed through W47's search under W48's bindings
(charter Design "The moves", MARKED; Decision Log 4). Nothing renders: each family's steps are
`search.steps_of`, each step's points `search.step_candidates` from the snapshot start (`{}`), and a
step's renders per scale the distinct `fit.scale_overrides` of its points (scale-separable rendering).

What the tool computes, against the charter's figures (Decision Log 4):
- stage 1, span law: ONE factorial step of 432 grid points, plus the step's start (tintAlpha 0.9, far 0,
  top 256, gain 0.05 is not a grid point), so 433 candidates; 72 + 1 renders per scale. With the gain HELD
  at 0.05 (`hold`: the leaf leaves the search for the family's `fixed`), 108 + 1 and 18 + 1.
- stage 1, rest scatter: 26 points per pass (the charter's 26).
- stage 2, transmission x fine term x body width: ONE factorial step of 114 points (the share-0 points'
  widths collapse; the start IS a grid point), 42 renders per scale.
- stage 2, receded scatter: W47's family unchanged, 58 grid values per pass (the charter's figure), which
  the search offers as 78 candidates from the snapshot start, because W47's family sweeps the second
  tap's share and widths as ONE factorial step (3 x 4 x 4 = 48, 33 after the share-0 collapse) and the far
  share's joint domain [-share, 0] admits only 0 at share 0. Recorded beside the charter's 58.

    python3.12 -B -m unittest -v test_stage_sizes      (from this directory)
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
# W47's test_fit module supplies `fit`, `search` and its SyntheticPart2 (part 2 pointed at a hashed scratch
# copy of a body); its bare `import declare` is used only by a case W48 replaces, so a stub stands in.
T = S.module("fit/test_fit.py", importing=mock.patch.dict(sys.modules, {"declare": types.SimpleNamespace()}))
fit, search = T.fit, T.search
DRAFT = json.loads(W.DRAFT.read_text())


def family(body, move, fam):
    return next(m for m in body["moves"] if m["id"] == move)["families"][fam]


def sizes(body, move, fam):
    """[(step, points, [renders at 1x, at 2x])] of one family from the snapshot start."""
    f = family(body, move, fam)
    out = []
    with T.SyntheticPart2(body):
        for step in search.steps_of(f, "d0219"):
            cands = search.step_candidates(f, step, {})
            out.append((step, len(cands), [len({json.dumps(fit.scale_overrides(c, s), sort_keys=True) for c in cands})
                                           for s in (1, 2)]))
    return out


def held(body, move, fam, leaf, value):
    """`body` with `leaf` held at `value`: moved from the family's search to its `fixed` (part 2's `hold`)."""
    body = json.loads(json.dumps(body))
    f = family(body, move, fam)
    spec = f["leaves"].pop(leaf)
    f.setdefault("fixed", {})[leaf] = dict(slot=spec["slot"], value=value)
    for g in f.get("factorialGroups", []):
        g["keys"] = [k for k in g["keys"] if k != leaf]
    return body


class StageSizes(unittest.TestCase):
    def test_stage_1_span_law(self):
        [(step, points, renders)] = sizes(DRAFT, "stage1", "span-law")
        self.assertEqual(len(step), 6)
        self.assertEqual(points, 3 * 3 * 3 * 2 * 2 * 4 + 1)              # 432 and the start
        self.assertEqual(renders, [3 * 3 * 2 * 4 + 1] * 2)               # 72 per scale and the start

    def test_stage_1_span_law_with_the_gain_held(self):
        body = held(DRAFT, "stage1", "span-law", "sizeOcclusionGain", 0.05)
        [(step, points, renders)] = sizes(body, "stage1", "span-law")
        self.assertNotIn("sizeOcclusionGain", step)
        self.assertEqual(points, 108 + 1)
        self.assertEqual(renders, [18 + 1] * 2)

    def test_stage_1_rest_scatter(self):
        got = sizes(DRAFT, "stage1", "rest-scatter")
        self.assertEqual(len(got), 6)
        self.assertEqual(sum(p for _, p, _ in got), 26)

    def test_stage_2_transmission_fine_term(self):
        [(step, points, renders)] = sizes(DRAFT, "stage2", "transmission-fine-term")
        self.assertEqual(sorted(step), sorted(["optics.regular.tintAlpha", "sizeFineTapSigma", "sizeFineTapSigma2x",
                                               "sizeFineTapShare", "optics.regular.blurSigma"]))
        self.assertEqual(points, 2 * (3 * 3 * 2 + 1) * 3)                 # 114: the start is a grid point
        self.assertEqual(renders, [2 * (3 * 2 + 1) * 3] * 2)              # 42 per scale

    def test_stage_2_receded_scatter(self):
        f = family(DRAFT, "stage2", "receded-scatter")
        self.assertEqual(sum(len(s["grid"]) for s in f["leaves"].values()), 58)
        got = sizes(DRAFT, "stage2", "receded-scatter")
        self.assertEqual(sum(p for _, p, _ in got), 78)
        tap = next(p for s, p, _ in got if len(s) == 3)
        self.assertEqual(tap, 1 + 2 * 4 * 4)                              # share 0 collapses its widths

    def test_the_draft_records_these_sizes(self):
        sizes_ = DRAFT["stageSizes"]
        self.assertEqual(sizes_["stage1"]["spanLaw"]["points"], 432)
        self.assertEqual(sizes_["stage1"]["spanLaw"]["rendersPerScale"], {"1x": 72, "2x": 72})
        self.assertEqual(sizes_["stage1"]["spanLaw"]["gainHeld"]["points"], 108)
        self.assertEqual(sizes_["stage2"]["transmissionFineTerm"]["points"], 114)
        self.assertEqual(sizes_["stage2"]["transmissionFineTerm"]["rendersPerScale"], {"1x": 42, "2x": 42})
        self.assertEqual(sizes_["stage1"]["restScatter"]["gridPointsPerPass"], 26)
        self.assertEqual(sizes_["stage2"]["recededScatter"]["gridPointsPerPass"], 58)


if __name__ == "__main__":
    unittest.main()
