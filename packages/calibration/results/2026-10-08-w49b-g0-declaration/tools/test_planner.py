"""Gate planning exercises the real pinned fixture manifest, never the browser."""
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
s = importlib.util.spec_from_file_location("w49b_render", HERE / "render.py")
R = importlib.util.module_from_spec(s); s.loader.exec_module(R)


class PlannerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.registry = R.C.load_registry()

    def test_active_population_retains_pressed_cells_and_omits_referees(self):
        point = {"label": "active", "pose": "rest"}
        plan = R.plan_run(self.registry, point, 1)
        self.assertEqual(plan["cells"], 45)
        self.assertIn("photo__capsule-button__pressed", plan["scenes"])
        self.assertNotIn("checkerboard-32__rrect-lg__inactive", plan["scenes"])
        self.assertEqual(plan["requested"], plan["planned"])

    def test_supplied_batch_has_exact_population_and_no_withheld_cells(self):
        batch = R.C.validate_batch(json.loads((HERE.parent / "batches/identification.json").read_text()))
        plans = [R.plan_run(self.registry, p, scale) for p in batch["points"] for scale in p["scales"]]
        self.assertEqual(len(plans), 54)
        # 4 both-pose points, 4 active-only points, 19 inactive-only points, at both scales.
        self.assertEqual(sum(p["cells"] for p in plans), 4 * 2 * 66 + 4 * 2 * 45 + 19 * 2 * 21)
        withheld = {(c["profile"], c["renderer"], c["scene"]) for c in self.registry["cells"]
                    if c["partition"] != "gate"}
        self.assertTrue(all(not set(map(tuple, p["planned"])) & withheld for p in plans))


if __name__ == "__main__": unittest.main()
