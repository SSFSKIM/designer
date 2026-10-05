#!/usr/bin/env python3.12
"""W47 G0 (c): the sheets port's red cases (charter clause 10; Design "The populations per phase"), W46's
test ported by copy with W46's stages added to the refused inputs. Nothing is drawn.

    cd packages/calibration/results/2026-10-06-w47-g0-operators/sheets
    python3.12 -B -m unittest test_sheets -v
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import sheets  # noqa: E402

W = sheets.W


def row(p, sid):
    return {"key": {"profileKey": p, "sceneId": sid, "web": {"renderer": "webgpu"}}}


class Sheets(unittest.TestCase):
    def setUp(self):
        self.B, self.t1, _ = W.load_cuts()
        plan = W.referees()
        self.held = plan.referee_cells(plan.load_manifest())

    def select(self, rows, whole=False):
        return sheets.select(rows, self.B, self.t1, self.held, self.B.LIGHT_WITHHELD, whole)

    def test_a_w45_or_w46_stage_refuses(self):
        for other in ("vitrea-w45/g1-stage-light", "vitrea-w46/g1-stage-x60-light"):
            with self.assertRaisesRegex(W.Refusal, "clause 2"):
                sheets.main(["--stage", str(Path.home() / other / "matrix.json"),
                             "--stage-captures", "/tmp", "--out", "/tmp/x"])

    def test_a_dark_referee_or_holdout_row_refuses_before_the_exposure(self):
        for sid in ("checkerboard-8__rrect-sm__rest", "mid-dark-solid__capsule-button__inactive"):
            with self.assertRaisesRegex(W.Refusal, "before --whole"):
                self.select([row(W.DARK_025[0], sid)])
            self.assertEqual(len(self.select([row(W.DARK_025[0], sid)], whole=True)), 1)

    def test_a_light_withheld_row_refuses_always(self):
        for whole in (False, True):
            with self.assertRaisesRegex(W.Refusal, "X60"):
                self.select([row(W.LIGHT_025[0], "checkerboard-4__rrect-ml__rest")], whole)

    def test_light_rows_are_not_drawn_and_dark_non_t1_rows_are(self):
        got = self.select([row(W.LIGHT_025[0], "photo__rrect-md__rest"),
                           row(W.DARK_025[0], "dark-solid__rrect-md__rest")])
        self.assertEqual([(g[4], g[0]) for g in got], [("dark-solid__rrect-md__rest", "-")])

    def test_whole_refuses_without_the_exposure_read(self):
        with self.assertRaisesRegex(W.Refusal, "read 8"):
            sheets.main(["--stage", "/tmp/m.json", "--stage-captures", "/tmp", "--out", "/tmp/x", "--whole"])
        with mock.patch.object(sheets, "exposure_read", lambda: True):
            self.assertTrue(sheets.exposure_read())

    def test_the_dark_gain_is_printed(self):
        self.assertEqual(sheets.GAIN["dark"], 16)
        self.assertIn("x16", " | ".join(sheets.columns(16)))

    def test_a_capture_that_names_other_documents_refuses(self):
        tmp = Path(tempfile.mkdtemp(prefix="w47-sheets-"))
        try:
            folder = tmp / W.DARK_025[1] / "photo__rrect-md__rest"
            folder.mkdir(parents=True)
            (folder / "cell__webgpu.json").write_text(json.dumps(dict(
                capturePath="materialProfile=other", sceneId="photo__rrect-md__rest", renderer="webgpu")))
            r = {"key": {"profileKey": W.DARK_025[1], "sceneId": "photo__rrect-md__rest",
                         "web": {"renderer": "webgpu", "capturePath": "materialProfile=mine",
                                 "sceneId": "photo__rrect-md__rest"}}}
            with self.assertRaisesRegex(W.Refusal, "capturePath"):
                sheets.checked_png(tmp, r)
        finally:
            shutil.rmtree(tmp)


if __name__ == "__main__":
    unittest.main()
