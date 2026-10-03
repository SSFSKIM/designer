#!/usr/bin/env python3.12
"""W45 G0 (b): the stage and X48 ports' red cases (charter clauses 2, 6 and 7; X48, X49, X58).
Nothing here launches a browser or declares a stage.

    cd packages/calibration/results/2026-10-03-w45-g0-operator/stage
    python3.12 -B -m unittest test_stage -v
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import stage  # noqa: E402
import x48  # noqa: E402

W = stage.W
W44_STAGE = Path.home() / "vitrea-w44" / "g1-stage-light"


class Stage(unittest.TestCase):
    def test_the_stages_are_w45s(self):
        for mode in stage.MODES.values():
            W.refuse_w44_path(mode["stage"], "stage")
            W.refuse_w44_path(mode["out"], "evidence")
            self.assertIn("vitrea-w45", str(mode["stage"]))

    def test_a_w44_stage_refuses(self):
        with mock.patch.dict(stage.MODES["g1"], stage=W44_STAGE), self.assertRaisesRegex(W.Refusal, "X58"):
            stage.declare("g1")

    def test_g1_refuses_c05s_own_documents(self):
        # Today the light documents on disk ARE c05 and W45's parts are unhashed: G1's stage refuses.
        with self.assertRaises(W.Refusal):
            stage.require_sealed()
        with mock.patch.object(W, "require_part", lambda part: "x"), self.assertRaisesRegex(W.Refusal, "not sealed by W45"):
            stage.require_sealed()

    def test_the_rehearsal_stages_only_c05(self):
        stage.require_c05()
        state = {k: dict(v, c05=False) for k, v in stage.documents_state().items()}
        with mock.patch.object(stage, "documents_state", lambda: state), self.assertRaisesRegex(W.Refusal, "not c05"):
            stage.require_c05()

    def test_the_rehearsal_renders_t1_gate_cells_only(self):
        B, t1 = W.load_cuts()
        plan = W.referee_plan()
        held = plan.referee_cells(plan.load_manifest())
        pregate = set(plan.lists()["pregateProbe"]["scenes"])
        for profile in W.LIGHT_025:
            lists = stage.gate_t1_scenes(profile)
            self.assertEqual(len(lists["cvr"]) + len(lists["probe"]), 94, profile)
            for sid in lists["cvr"] + lists["probe"]:
                self.assertNotIn((profile, sid), held)
                self.assertNotEqual(B.SCENES.role[sid], "holdout")
                self.assertIn(B.SCENES.by_id[sid]["background"], t1.T1_BACKDROPS)
            self.assertTrue(set(lists["probe"]) <= pregate)
            for sid in ("checkerboard-8__rrect-lg__inactive", "checkerboard-32__rrect-lg__inactive"):
                self.assertNotIn(sid, lists["cvr"] + lists["probe"])
            passes = stage.passes("rehearse-measure", profile)
            self.assertEqual([p[1] for p in passes], ["calibration,validation,recorded", "probe"])

    def test_measure_never_names_the_holdout_and_the_exposure_waits_on_the_ledger(self):
        for profile in W.LIGHT_025:
            for _, sets, scenes in stage.passes("measure", profile):
                self.assertNotIn("holdout", sets)
        refusals = stage.exposure_refusals(stage.holdout_configuration(), stage.committed_last_read())
        self.assertTrue(any("referee manifest" in r for r in refusals), refusals)


class X48(unittest.TestCase):
    def row(self, sid, tier="webgpu"):
        return {"key": {"profileKey": W.PROFILE[1], "sceneId": sid, "web": {"renderer": tier, "capturePath": "x"}}}

    def test_a_w44_stage_refuses(self):
        with self.assertRaisesRegex(W.Refusal, "X58"):
            x48.main(["--stage", str(W44_STAGE), "--out", "/tmp/w45-x48-red.json"])

    def test_a_holdout_row_refuses_before_the_exposure(self):
        with self.assertRaisesRegex(W.Refusal, "holdout or referee"):
            x48.compare([self.row("checkerboard__rrect-lg__rest")], Path("/tmp"), with_holdout=False)

    def test_a_referee_row_refuses_before_the_exposure(self):
        plan = W.referee_plan()
        held = sorted(s for p, s in plan.referee_cells(plan.load_manifest()) if p == W.PROFILE[1])
        with self.assertRaisesRegex(W.Refusal, "holdout or referee"):
            x48.compare([self.row(held[0])], Path("/tmp"), with_holdout=False)

    def test_a_row_that_differs_is_found(self):
        B, _ = W.load_cuts()
        twin = next(r for r in B.load_published(W.C05["light"]).rows
                    if r["key"]["profileKey"] == W.PROFILE[1] and r["key"]["sceneId"] == "photo__rrect-md__rest"
                    and r["key"]["web"]["renderer"] == "webgpu")
        moved = json.loads(json.dumps(twin))
        moved["material"]["interiorStdDevWeb"]["value"] += 1e-9
        got = x48.compare([moved], W.CANONICAL_CAPTURES, with_holdout=False)
        self.assertEqual(len(got["rowsThatDiffer"]), 1)
        same = x48.compare([twin], W.CANONICAL_CAPTURES, with_holdout=False)
        self.assertEqual(same["identicalRowsExceptHowDrawn"], 1)


if __name__ == "__main__":
    unittest.main()
