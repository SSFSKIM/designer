#!/usr/bin/env python3.12
"""W46 G0 (a): X60's red cases (charter X60). Nothing here launches a browser.

A clean input reads IDENTICAL; a moved light row, a moved light capture, a moved light document, a
candidate whose light endpoint moved, a moved frozen file and a withheld capture each fail.

    cd packages/calibration/results/2026-10-05-w46-g0-declaration/stage
    python3.12 -B -m unittest test_x60 -v
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import x60  # noqa: E402

W = x60.W
LIGHT2 = W.LIGHT_025[1]
SID = "photo__rrect-md__rest"


def published_row(profile=LIGHT2, sid=SID, tier="webgpu"):
    B, _, _ = W.load_cuts()
    return next(r for r in B.load_published(W.REFERENCE["light"]).rows
                if (r["key"]["profileKey"], r["key"]["sceneId"], r["key"]["web"]["renderer"]) == (profile, sid, tier))


class Render(unittest.TestCase):
    def test_a_clean_row_and_its_captures_are_identical(self):
        got = x60.compare([published_row()], W.CANONICAL_CAPTURES)
        self.assertEqual((got["identicalRowsButCapturedAt"], got["identicalCaptures"]), (1, 2))
        self.assertEqual(got["rowsThatDiffer"] + got["capturesThatDiffer"], [])

    def test_a_moved_row_is_found(self):
        moved = json.loads(json.dumps(published_row()))
        moved["material"]["interiorStdDevWeb"]["value"] += 1e-9
        self.assertEqual(len(x60.compare([moved], W.CANONICAL_CAPTURES)["rowsThatDiffer"]), 1)
        named = json.loads(json.dumps(published_row()))
        named["key"]["web"]["capturePath"] += " (another document)"
        self.assertEqual(len(x60.compare([named], W.CANONICAL_CAPTURES)["rowsThatDiffer"]), 1)

    def test_a_moved_capture_is_found(self):
        tmp = Path(tempfile.mkdtemp(prefix="w46-x60-"))
        try:
            folder = tmp / LIGHT2 / SID
            folder.mkdir(parents=True)
            for suffix in ("", "__alpha"):
                shutil.copy(W.CANONICAL_CAPTURES / LIGHT2 / SID / f"{SID}__webgpu{suffix}.png", folder)
            self.assertEqual(x60.compare([published_row()], tmp)["capturesThatDiffer"], [])
            with (folder / f"{SID}__webgpu.png").open("ab") as f:
                f.write(b"\0")
            self.assertEqual(len(x60.compare([published_row()], tmp)["capturesThatDiffer"]), 1)
        finally:
            shutil.rmtree(tmp)

    def test_a_light_withheld_row_refuses(self):
        for sid in ("photo__rrect-lg__rest", "checkerboard-4__rrect-ml__rest"):    # holdout; W44 referee
            row = {"key": {"profileKey": LIGHT2, "sceneId": sid, "web": {"renderer": "webgpu"}}}
            with self.assertRaisesRegex(W.Refusal, "X60"):
                x60.compare([row], W.CANONICAL_CAPTURES)

    def test_the_light_non_withheld_population_is_138_per_scale(self):
        B, _, _ = W.load_cuts()
        for p in W.LIGHT_025:
            free = [s for s in B.SCENES.declared(p) if (p, s) not in B.LIGHT_WITHHELD]
            self.assertEqual(len(free), 138, p)


class Evidence(unittest.TestCase):
    def args(self, **kw):
        return Namespace(candidate=kw.get("candidate", []), after_exposure=kw.get("after_exposure", False))

    def test_the_clean_tree_reads_identical(self):
        with mock.patch.object(x60, "CANDIDATE_ROOTS", ()), mock.patch.object(x60, "capture_trees", lambda: []):
            self.assertEqual(x60.evidence(self.args())["verdict"], "IDENTICAL")

    def test_a_moved_light_document_fails(self):
        with mock.patch.dict(W.DOCUMENT_SHA, {"active.light": "0" * 64}):
            self.assertTrue(x60.light_documents())

    def test_a_moved_frozen_file_fails(self):
        with mock.patch.object(x60, "FROZEN_265_SHA", "0" * 64):
            self.assertTrue(any("26.5" in f for f in x60.frozen_files()))
        with mock.patch.dict(W.FROZEN_05_GENERATIONS, {"0eac5b294cc2": "000000000000"}):
            self.assertTrue(x60.frozen_files())

    def candidate(self, tmp: Path, move: bool) -> Path:
        folder = tmp / "cand"
        folder.mkdir()
        endpoints = {}
        for slot in W.SLOTS:
            doc = W.document(slot)
            if move and slot == "receded.light":
                doc["patch"]["sizeHeavySecondShare"] = 0.3
            (folder / f"{slot}.json").write_text(json.dumps(doc))
            endpoints[slot] = {"path": f"{slot}.json", "sha256": "x"}
        (folder / "candidate.json").write_text(json.dumps({"endpoints": endpoints}))
        return folder

    def test_a_candidate_whose_light_endpoint_moved_fails(self):
        tmp = Path(tempfile.mkdtemp(prefix="w46-x60-"))
        try:
            self.assertEqual(x60.light_endpoints([self.candidate(tmp, move=False)])[1], [])
            shutil.rmtree(tmp / "cand")
            failures = x60.light_endpoints([self.candidate(tmp, move=True)])[1]
            self.assertTrue(any("receded.light" in f for f in failures))
        finally:
            shutil.rmtree(tmp)

    def test_a_withheld_capture_fails(self):
        tmp = Path(tempfile.mkdtemp(prefix="w46-x60-"))
        try:
            tree = tmp / "web-captures"
            (tree / W.DARK_025[0] / "photo__rrect-md__rest").mkdir(parents=True)
            (tree / W.DARK_025[0] / "photo__rrect-md__rest" / "x.png").write_bytes(b"x")
            self.assertEqual(x60.withheld_captures([tree], after_exposure=False), [])
            for p, sid, needle in ((W.LIGHT_025[0], "checkerboard-4__rrect-ml__rest", "light withheld"),
                                   (W.DARK_025[1], "checkerboard-8__rrect-sm__rest", "dark withheld")):
                (tree / p / sid).mkdir(parents=True)
                (tree / p / sid / "x.png").write_bytes(b"x")
                self.assertTrue(any(needle in f for f in x60.withheld_captures([tree], after_exposure=False)))
            after = x60.withheld_captures([tree], after_exposure=True)
            self.assertEqual(len(after), 1)
            self.assertIn("light withheld", after[0])
        finally:
            shutil.rmtree(tmp)

    def test_the_scratch_scan_finds_trees_and_skips_a_worktree_checkout(self):
        tmp = Path(tempfile.mkdtemp(prefix="w46-x60-"))
        try:
            (tmp / "g0-ladders" / "a" / "web-captures").mkdir(parents=True)
            (tmp / "g9").mkdir()
            (tmp / "g9" / ".git").write_text("gitdir: x")
            (tmp / "g9" / "node_modules" / "web-captures").mkdir(parents=True)
            (tmp / "g9" / "packages" / "calibration" / "web-captures").mkdir(parents=True)
            trees = sorted(str(t.relative_to(tmp)) for t in x60.capture_trees(tmp))
            self.assertEqual(trees, ["g0-ladders/a/web-captures", "g9/packages/calibration/web-captures"])
        finally:
            shutil.rmtree(tmp)


if __name__ == "__main__":
    unittest.main()
