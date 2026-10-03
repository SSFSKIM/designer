#!/usr/bin/env python3.12
"""W45 G0 (b): the sheets port's red cases (charter clause 10; X58). Nothing is drawn.

    cd packages/calibration/results/2026-10-03-w45-g0-operator/sheets
    python3.12 -B -m unittest test_sheets -v
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import sheets  # noqa: E402

W = sheets.W
W44_STAGE = Path.home() / "vitrea-w44" / "g1-stage-light"


class Sheets(unittest.TestCase):
    def test_a_w44_stage_refuses(self):
        with self.assertRaisesRegex(W.Refusal, "X58"):
            sheets.main(["--stage", str(W44_STAGE / "matrix.json"), "--stage-captures", "/tmp", "--out", "/tmp/x"])

    def test_a_referee_row_refuses_before_the_exposure(self):
        B, t1 = W.load_cuts()
        plan = W.referee_plan()
        held = plan.referee_cells(plan.load_manifest())
        p, sid = sorted(held)[0]
        row = {"key": {"profileKey": p, "sceneId": sid, "web": {"renderer": "webgpu"}}}
        with self.assertRaisesRegex(W.Refusal, "before --whole"):
            sheets.select([row], B, t1, held, whole=False)
        self.assertEqual(len(sheets.select([row], B, t1, held, whole=True)), 1)

    def test_a_capture_that_names_other_documents_refuses(self):
        tmp = Path(tempfile.mkdtemp(prefix="w45-sheets-"))
        try:
            folder = tmp / W.PROFILE[2] / "photo__rrect-md__rest"
            folder.mkdir(parents=True)
            (folder / "cell__webgpu.json").write_text(json.dumps(dict(
                capturePath="materialProfile=other", sceneId="photo__rrect-md__rest", renderer="webgpu")))
            row = {"key": {"profileKey": W.PROFILE[2], "sceneId": "photo__rrect-md__rest",
                           "web": {"renderer": "webgpu", "capturePath": "materialProfile=mine", "sceneId":
                                   "photo__rrect-md__rest"}}}
            with self.assertRaisesRegex(W.Refusal, "capturePath"):
                sheets.checked_png(tmp, row)
        finally:
            shutil.rmtree(tmp)


if __name__ == "__main__":
    unittest.main()
