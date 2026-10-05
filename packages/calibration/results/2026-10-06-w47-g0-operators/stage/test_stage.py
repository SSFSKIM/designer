#!/usr/bin/env python3.12
"""W47 G0 (c): the stage port's red cases (charter clauses 2, 7 and 8; Design "The populations per
phase"; X62, X69). Nothing here launches a browser or declares a stage. W46's test, ported by copy:
the stages are W47's, W46's stages and recorded documents are refused beside W44's and W45's.

    cd packages/calibration/results/2026-10-06-w47-g0-operators/stage
    python3.12 -B -m unittest test_stage -v
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import stage  # noqa: E402

W = stage.W


class Stage(unittest.TestCase):
    def test_the_stages_are_w47s_and_dark(self):
        for mode in stage.MODES.values():
            W.refuse_other_wave_path(mode["stage"], "stage")
            W.refuse_other_wave_path(mode["out"], "evidence")
            self.assertIn("vitrea-w47", str(mode["stage"]))
        self.assertEqual(stage.PROFILES, list(W.DARK_025))
        self.assertIn("-dark-", stage.ACTIVE)
        self.assertIn("-dark-", stage.RECEDED)

    def test_a_w44_w45_or_w46_stage_refuses(self):
        for other in (Path.home() / "vitrea-w45" / "g1-stage-light", Path.home() / "vitrea-w44" / "g1-stage-light",
                      Path.home() / "vitrea-w46" / "g1-stage-x60-light", Path.home() / "vitrea-w46" / "g0-stage-rehearsal"):
            with mock.patch.dict(stage.MODES["g1"], stage=other), self.assertRaisesRegex(W.Refusal, "clause 2"):
                stage.declare("g1")

    def test_g1_refuses_the_shipped_documents_and_unhashed_parts(self):
        # The shipped state (the dark documents the snapshots' bytes), stated rather than read off the
        # live files, so the case holds after G1's seal moves them (the review of G0's tools: X62).
        shipped = {k: dict(v, snapshot=True, recordedBy="W43 G3") for k, v in stage.documents_state().items()}

        def unhashed(part):
            raise W.Refusal("unhashed")
        with mock.patch.object(W, "require_part", unhashed), self.assertRaises(W.Refusal):
            stage.require_sealed()
        with mock.patch.object(W, "require_part", lambda part: "x"), \
                mock.patch.object(stage, "documents_state", lambda: shipped), \
                self.assertRaisesRegex(W.Refusal, "not sealed by W47 G1"):
            stage.require_sealed()
        sealed = {k: dict(v, snapshot=False, recordedBy="W47 G1") for k, v in stage.documents_state().items()}
        with mock.patch.object(W, "require_part", lambda part: "x"), \
                mock.patch.object(stage, "documents_state", lambda: sealed):
            stage.require_sealed()
        for other in ("W45 G1", "W46 G1"):
            wrong = {k: dict(v, snapshot=False, recordedBy=other) for k, v in stage.documents_state().items()}
            with mock.patch.object(W, "require_part", lambda part: "x"), \
                    mock.patch.object(stage, "documents_state", lambda: wrong), \
                    self.assertRaisesRegex(W.Refusal, "not sealed by W47 G1"):
                stage.require_sealed()

    def test_the_rehearsal_stages_only_the_snapshot_bytes(self):
        shipped = {k: dict(v, snapshot=True) for k, v in stage.documents_state().items()}
        with mock.patch.object(stage, "documents_state", lambda: shipped):
            stage.require_snapshot()
        state = {k: dict(v, snapshot=False) for k, v in stage.documents_state().items()}
        with mock.patch.object(stage, "documents_state", lambda: state), \
                self.assertRaisesRegex(W.Refusal, "not the snapshot"):
            stage.require_snapshot()

    def test_the_rehearsal_renders_dark_t1_gate_cells_only(self):
        B, t1, _ = W.load_cuts()
        plan = W.referees()
        held = plan.referee_cells(plan.load_manifest())
        pregate = set(plan.lists()["pregateProbe"]["scenes"])
        for profile in W.DARK_025:
            lists = stage.gate_t1_scenes(profile)
            self.assertEqual(len(lists["cvr"]) + len(lists["probe"]), 66, profile)
            for sid in lists["cvr"] + lists["probe"]:
                self.assertNotIn((profile, sid), held)
                self.assertNotEqual(B.SCENES.role[sid], "holdout")
                self.assertIn(B.SCENES.by_id[sid]["background"], t1.T1_BACKDROPS)
            self.assertTrue(set(lists["probe"]) <= pregate)
            for sid in plan.load_manifest()["scenes"]:
                self.assertNotIn(sid, lists["cvr"] + lists["probe"])
            passes = stage.passes("rehearse-measure", profile)
            self.assertEqual([p[1] for p in passes], ["calibration,validation,recorded", "probe"])

    def test_measure_never_names_the_withheld_and_the_exposure_is_the_thirteen(self):
        plan = W.referees()
        held = set(plan.load_manifest()["scenes"])
        for profile in W.DARK_025:
            for _, sets, scenes in stage.passes("measure", profile):
                self.assertNotIn("holdout", sets)
                self.assertFalse(set(scenes or ()) & held)
            [(_, sets, scenes)] = stage.passes("exposure", profile)
            self.assertEqual(sets, "holdout,probe")
            self.assertEqual(len(scenes), 13)
            self.assertTrue(held <= set(scenes))

    def test_a_census_refusal_is_not_a_completion(self):
        import json
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            stage.log(out, dict(label="p", started="t", argv=[]))
            stage.log(out, dict(label="p", started="t", completed="t", exitCode=3))
            self.assertFalse(stage.done(out, "p")[0])
            stage.log(out, dict(label="p/relaunch-1", started="t", completed="t", exitCode=0))
            self.assertTrue(stage.done(out, "p/relaunch-1")[0])
            self.assertEqual(len([json.loads(x) for x in (out / "runs.jsonl").read_text().splitlines()]), 3)

    def test_the_exposure_waits_on_the_ledger(self):
        refusals = stage.exposure_refusals(stage.holdout_configuration(), stage.committed_last_read())
        self.assertTrue(any("w46-referees-1" in r for r in refusals), refusals)


if __name__ == "__main__":
    unittest.main()
