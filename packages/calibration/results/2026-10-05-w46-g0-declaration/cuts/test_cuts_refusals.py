#!/usr/bin/env python3.12
"""W46 G0 (a): the cuts port refuses W44's and W45's bindings, reads its shared inputs pinned, and
never admits a withheld cell (charter clause 1; Design "The populations per phase"; X60).

    cd packages/calibration/results/2026-10-05-w46-g0-declaration/cuts
    python3.12 -B -m unittest test_cuts_refusals -v
"""
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import bed as B  # noqa: E402
import cuts  # noqa: E402

W = B.W
W44_G1 = W.W44_G1
W45_G0 = W.W45_G0


def row(profile, sid, path, renderer="webgpu"):
    return {"key": {"profileKey": profile, "sceneId": sid,
                    "web": {"engine": "chromium", "engineVersion": "151.0.7922.34", "renderer": renderer,
                            "samplingBackend": "gpu-texture", "gpuAdapter": "test", "colorSpace": "srgb",
                            "capturePath": path}},
            "fixtureSet": B.SCENES.role[sid], "state": B.SCENES.by_id[sid]["state"]}


def sealed_path(scheme):
    live = B.sealed_025()
    a = f"packages/calibration/profiles/apple-macos-27.0-1x-{scheme}-standard-glass0.25.json"
    r = f"packages/calibration/profiles/apple-macos-27.0-1x-{scheme}-standard-glass0.25-receded.json"
    return (f"materialProfile={a} sha256:{live[a]} sections=renderer+cssTierMapping, "
            f"recededProfile={r} sha256:{live[r]}")


def matrix(tmp, rows):
    path = Path(tmp) / "matrix.json"
    path.write_text(json.dumps({"schemaVersion": 5, "cells": rows}))
    return str(path)


class Refuses(unittest.TestCase):
    def refused(self, fn, needle):
        with self.assertRaises(SystemExit) as raised:
            fn()
        self.assertIn(needle, str(raised.exception))

    def test_an_output_in_w44s_or_w45s_evidence(self):
        for out in (W44_G1 / "references" / "w46-red-case.json", W45_G0 / "rehearsal" / "w46-red-case.json"):
            self.refused(lambda: cuts.main(["--published", "d0219cd684bf", "--captures", "/nonexistent",
                                            "--out", str(out)]), "clause 1")
            self.assertFalse(out.exists())

    def test_a_text_report_in_w45s_scratch(self):
        out = Path.home() / "vitrea-w45" / "g1-scratch" / "w46-red-case.txt"
        self.refused(lambda: cuts.main(["--published", "d0219cd684bf", "--captures", "/nonexistent",
                                        "--out", str(Path(tempfile.mkdtemp()) / "o.json"),
                                        "--text", str(out)]), "clause 1")
        self.assertFalse(out.exists())

    def test_a_bed_matrix_in_w45s_scratch(self):
        self.refused(lambda: B.load([str(Path.home() / "vitrea-w45" / "g1-scratch" / "fit" / "matrix.json")],
                                    "sealed"), "clause 1")

    def test_a_w44_or_w45_candidate_document(self):
        self.refused(lambda: B.Candidate.read(str(W44_G1 / "fit/candidates/m3-t0.1/candidate.json")), "clause 1")
        self.refused(lambda: B.Candidate.read(
            str(W45_G0 / "ladders/candidates/c05-control/candidate.json")), "clause 1")

    def test_a_dark_referee_row_before_the_exposure(self):
        sid = "checkerboard-8__rrect-sm__rest"
        with tempfile.TemporaryDirectory() as tmp:
            bad = matrix(tmp, [row(W.DARK_025[1], sid, sealed_path("dark"))])
            self.refused(lambda: B.load([bad], "sealed"), "a referee cell")
            self.assertEqual(len(B.load([bad], "sealed", with_holdout=True).rows), 1)

    def test_a_dark_holdout_row_before_the_exposure(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = matrix(tmp, [row(W.DARK_025[0], "mid-dark-solid__capsule-button__rest", sealed_path("dark"))])
            self.refused(lambda: B.load([bad], "sealed"), "a holdout row")

    def test_a_light_withheld_row_is_refused_even_at_the_exposure(self):
        for sid in ("checkerboard-4__rrect-ml__rest", "photo__rrect-lg__rest"):   # W44 referee; light holdout
            with tempfile.TemporaryDirectory() as tmp:
                bad = matrix(tmp, [row(W.LIGHT_025[1], sid, sealed_path("light"))])
                self.refused(lambda: B.load([bad], "sealed"), "X60")
                self.refused(lambda: B.load([bad], "sealed", with_holdout=True), "X60")

    def test_the_withheld_counts(self):
        light = {s for p, s in B.LIGHT_WITHHELD if p == W.LIGHT_025[0]}
        self.assertEqual(len(light), 26)                  # 20 holdout + W44's six referees
        dark = B.referee_plan.lists()["exposure"]["scenes"]
        self.assertEqual(len(dark), 13)                   # 7 holdout + W46's six referees


class SharedInputs(unittest.TestCase):
    def test_pinned_byte_for_byte(self):
        self.assertEqual(W.verify_shared(), [])

    def test_t1_and_readings_are_w44_g1s_and_bed_and_rule_are_w46s(self):
        import readings
        self.assertEqual(Path(cuts.T1.__file__).resolve(), (W44_G1 / "cuts" / "t1.py").resolve())
        self.assertEqual(Path(readings.__file__).resolve(), (W44_G1 / "cuts" / "readings.py").resolve())
        self.assertEqual(Path(cuts.T1.B.__file__).resolve(), (HERE / "bed.py").resolve())
        self.assertEqual(Path(cuts.W46_RULE.__file__).resolve(), (HERE / "rule.py").resolve())
        self.assertFalse((HERE / "t1.py").exists() or (HERE / "readings.py").exists())

    def test_the_references_are_w46s(self):
        self.assertEqual(cuts.T1_REFERENCE, ("ebc3d9105a4a", "d0219cd684bf"))
        self.assertEqual(cuts.BAND_PROFILES, W.DARK_025)


if __name__ == "__main__":
    unittest.main()
