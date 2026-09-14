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


if __name__ == "__main__":
    unittest.main()
