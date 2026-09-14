"""Exercise the scorer's own admission boundary, not just the browser driver."""
import importlib.util
from pathlib import Path
import unittest

here = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("fit_tables", here / "fit-tables.py")
scorer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scorer)


class Admission(unittest.TestCase):
    def test_every_checking_name_is_refused_in_every_role(self):
        scenes = next(g for g in scorer.bed["groups"] if g["id"] == "D")["scenes"]
        for scene in scenes + ["checkerboard__rrect-ml__inactive"]:
            for role in ["fit", "control", None]:
                with self.subTest(scene=scene, role=role):
                    with self.assertRaisesRegex(ValueError, "checking set"):
                        scorer.admit([{"profile": "p", "scene": scene, "role": role}])

    def test_holdout_is_not_a_control(self):
        for cell in scorer.holdout:
            profile, scene = cell.split("/")
            with self.assertRaisesRegex(ValueError, "holdout"):
                scorer.admit([{"profile": profile, "scene": scene, "role": "control"}])


class Selection(unittest.TestCase):
    def test_measured_middle_changes_only_when_controls_refuse_it(self):
        table = {
            "dark-four-x0.7-m0.04092": {"refused": False, "fitMeanBodyDeltaE": 0.02},
            "dark-four-x0.7-m0.06496": {"refused": False, "fitMeanBodyDeltaE": 0.01},
            "dark-four-x0.7-m0.089": {"refused": False, "fitMeanBodyDeltaE": 0.005},
            "dark-baseline-silhouette": {"refused": False, "fitMeanBodyDeltaE": 0.001},
        }
        self.assertEqual(scorer.choose("dark", table), "dark-four-x0.7-m0.04092")
        table["dark-four-x0.7-m0.04092"]["refused"] = True
        self.assertEqual(scorer.choose("dark", table), "dark-four-x0.7-m0.06496")
        table["dark-four-x0.7-m0.06496"]["refused"] = True
        table["dark-four-x0.7-m0.089"]["refused"] = True
        self.assertIsNone(scorer.choose("dark", table))


if __name__ == "__main__":
    unittest.main()
