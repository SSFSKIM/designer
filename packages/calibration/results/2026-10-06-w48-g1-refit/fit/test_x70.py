"""W48 G1: X70's three-way check on a fit render, green and red (`fit.py` beside this file; X70; the
tracker's "X70 covers no fit render"). Nothing renders: W47's launch (`render_scale`'s original) is
replaced by a fake that writes a matrix, and G1's fit directory and scratch are pointed at a temporary
root for each case, so no committed file and no scratch tree is touched.

    python3.12 -B -m unittest -v test_x70      (from this directory)
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("w48_g1_fit", HERE / "fit.py")
X = importlib.util.module_from_spec(spec)
sys.modules["w48_g1_fit"] = X
spec.loader.exec_module(X)
fit, W = X.fit, X.W

SCOPE, SCALE = "stage1", 2
WANTED = fit.wanted(SCOPE, SCALE)            # the real stage-1 cells at 2x (X69's withholding applied)
UNDECLARED = "no-such-scene__rrect-md__rest"


def rows(scenes, scale=SCALE):
    return [dict(key=dict(profileKey=W.PROFILE[scale], sceneId=s)) for s in scenes]


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="w48-g1-x70-"))
        self.patches = [mock.patch.object(fit, "SCRATCH", self.tmp / "scratch"),
                        mock.patch.object(fit, "G1", self.tmp / "g1")]
        for p in self.patches:
            p.start()
        self.launched = []

    def tearDown(self):
        for p in self.patches:
            p.stop()
        shutil.rmtree(self.tmp)

    def fake_launch(self, measured, code=0, write=True):
        """W47's render_scale stood in for: records the launch, writes `measured` as the scope's matrix."""
        def launch(renderer, scope, scale):
            self.launched.append((renderer, scope, scale))
            out = fit.SCRATCH / renderer / f"{scope}-{scale}x"
            out.mkdir(parents=True, exist_ok=True)
            if write:
                (out / "matrix.json").write_text(json.dumps(dict(cells=measured)))
            return code
        return mock.patch.object(X, "_render_scale", launch)

    def x70_rows(self):
        path = fit.G1 / "runs.jsonl"
        return [json.loads(l)["x70"] for l in path.read_text().splitlines() if "x70" in l] if path.exists() else []


class RenderGreen(Base):
    def test_requested_planned_measured_equal_pass(self):
        with self.fake_launch(rows(WANTED)):
            self.assertEqual(X.render_scale("r", SCOPE, SCALE), 0)
        self.assertEqual(len(self.launched), 1)
        got = self.x70_rows()
        self.assertEqual([r["equal"] for r in got], [True, True])
        self.assertEqual(got[1]["measured"], len(WANTED))

    def test_census_refusal_before_launch_is_not_a_measurement(self):
        with self.fake_launch([], code=3, write=False):
            self.assertEqual(X.render_scale("r", SCOPE, SCALE), 3)
        self.assertEqual([r["where"].endswith("before the launch") for r in self.x70_rows()], [True])

    def test_nothing_requested_launches_through_unchecked(self):
        (fit.SCRATCH / "r" / f"{SCOPE}-{SCALE}x").mkdir(parents=True)
        (fit.SCRATCH / "r" / f"{SCOPE}-{SCALE}x" / "matrix.json").write_text(json.dumps(dict(cells=rows(WANTED))))
        with mock.patch.object(X, "_render_scale", lambda *a: 0):
            self.assertEqual(X.render_scale("r", SCOPE, SCALE), 0)
        self.assertEqual(self.x70_rows(), [])


class RenderRed(Base):
    def test_planned_differs_from_requested_refuses_before_launch(self):
        # A requested scene the dark 2x profile does not declare: compare would silently skip it.
        with mock.patch.object(fit, "wanted", lambda scope, scale: WANTED + [UNDECLARED]), \
                self.fake_launch(rows(WANTED)):
            with self.assertRaisesRegex(X.X70Refusal, "before the launch: X70 REFUSES: compare would plan"):
                X.render_scale("r", SCOPE, SCALE)
        self.assertEqual(self.launched, [])
        self.assertEqual([r["equal"] for r in self.x70_rows()], [False])

    def test_the_real_plan_drops_a_scene_of_another_profile(self):
        # The transcription itself: a 1x-only scene is not planned on the 2x profile.
        scenes = W.referees().load_scenes()
        only_1x = sorted(set(scenes["declared"][W.PROFILE[1]]) - set(scenes["declared"][W.PROFILE[2]]))
        probe = only_1x[0] if only_1x else UNDECLARED
        self.assertNotIn((W.PROFILE[2], probe), X.planned([probe], 2))
        self.assertEqual(X.planned(WANTED, 2), {(W.PROFILE[2], s) for s in WANTED})

    def test_a_partial_matrix_refuses_after_launch(self):
        with self.fake_launch(rows(WANTED[:-1]), code=1):
            with self.assertRaisesRegex(X.X70Refusal, r"after the launch \(exit 1\): X70 REFUSES: the rows measured"):
                X.render_scale("r", SCOPE, SCALE)
        self.assertEqual(self.x70_rows()[-1]["measured"], len(WANTED) - 1)

    def test_an_extra_row_refuses_after_launch(self):
        with self.fake_launch(rows(WANTED + ["checkerboard-8__rrect-md__inactive"])):
            with self.assertRaisesRegex(X.X70Refusal, "1 extra"):
                X.render_scale("r", SCOPE, SCALE)

    def test_a_row_twice_refuses_after_launch(self):
        with self.fake_launch(rows(WANTED + WANTED[:1])):
            with self.assertRaisesRegex(X.X70Refusal, "measured twice"):
                X.render_scale("r", SCOPE, SCALE)

    def test_no_matrix_after_a_launch_refuses(self):
        with self.fake_launch([], code=0, write=False):
            with self.assertRaisesRegex(X.X70Refusal, "no matrix"):
                X.render_scale("r", SCOPE, SCALE)


class Read(Base):
    def write(self, name, scenes):
        out = fit.SCRATCH / "r" / name
        out.mkdir(parents=True, exist_ok=True)
        (out / "matrix.json").write_text(json.dumps(dict(cells=rows(scenes))))

    def test_green_reads_through(self):
        self.write(f"{SCOPE}-{SCALE}x", WANTED)
        with mock.patch.object(X, "_read_scale", lambda r, s: "read"):
            self.assertEqual(X.read_scale("r", SCALE), "read")
        self.assertTrue(self.x70_rows()[-1]["equal"])

    def test_a_missing_cell_refuses_the_reading(self):
        self.write(f"{SCOPE}-{SCALE}x", WANTED[1:])
        with mock.patch.object(X, "_read_scale", lambda r, s: self.fail("read past X70")):
            with self.assertRaisesRegex(X.X70Refusal, "at read: X70 REFUSES: the rows measured"):
                X.read_scale("r", SCALE)

    def test_a_cell_in_two_scope_directories_refuses_the_reading(self):
        fit_cells = fit.wanted("rest-of-fit", SCALE)
        self.write(f"{SCOPE}-{SCALE}x", WANTED)
        self.write(f"rest-of-fit-{SCALE}x", [s for s in fit_cells if s not in WANTED] + WANTED[:1])
        with mock.patch.object(X, "_read_scale", lambda r, s: self.fail("read past X70")):
            with self.assertRaisesRegex(X.X70Refusal, "measured twice"):
                X.read_scale("r", SCALE)

    def test_two_scopes_that_cover_the_fit_read_through(self):
        fit_cells = fit.wanted("rest-of-fit", SCALE)
        self.write(f"{SCOPE}-{SCALE}x", WANTED)
        self.write(f"rest-of-fit-{SCALE}x", [s for s in fit_cells if s not in WANTED])
        with mock.patch.object(X, "_read_scale", lambda r, s: "read"):
            self.assertEqual(X.read_scale("r", SCALE), "read")


class Installed(unittest.TestCase):
    def test_the_inherited_module_calls_the_checked_functions(self):
        self.assertIs(fit.render_scale, X.render_scale)
        self.assertIs(fit.read_scale, X.read_scale)
        self.assertIs(sys.modules["fit"], fit)
        self.assertEqual(Path(fit.__file__), W.W47_G0 / "fit" / "fit.py")
        self.assertEqual(W.verify_inherited(), [])

    def test_search_and_joint_see_the_checked_module(self):
        self.assertIs(X.search().fit, fit)
        self.assertIs(X.joint().fit, fit)


if __name__ == "__main__":
    unittest.main()
