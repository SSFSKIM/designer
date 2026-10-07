"""Exercise real candidate composition and X75 without a browser or GPU."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[2]
TSX = CAL / "node_modules/.bin/tsx"


class BuilderTests(unittest.TestCase):
    def run_builder(self, batch, parent):
        path = parent / "supplied.json"; path.write_text(json.dumps(batch))
        out = parent / "new-candidates"
        run = subprocess.run([str(TSX), str(HERE / "build.ts"), str(path), str(out)],
                             cwd=CAL, capture_output=True, text=True)
        return run, out

    def test_candidate_roundtrip_and_no_overwrite(self):
        batch = {"schema": "w49b-g0-batch-1", "base": "b2d074d2df24-940384c06f73", "points": [
            {"label": "identity", "scales": [1, 2], "pose": "both", "overrides": {}}]}
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp); run, out = self.run_builder(batch, parent)
            self.assertEqual(run.returncode, 0, run.stderr)
            verify = subprocess.run([str(TSX), str(HERE / "verify-candidate.ts"),
                                     str(out / "identity/candidate.json")], cwd=CAL,
                                    capture_output=True, text=True)
            self.assertEqual(verify.returncode, 0, verify.stderr)
            before = (out / "identity/candidate.json").read_bytes()
            second, _ = self.run_builder(batch, parent)
            self.assertNotEqual(second.returncode, 0)
            self.assertEqual(before, (out / "identity/candidate.json").read_bytes())

    def test_every_point_passes_x75_before_any_output_is_created(self):
        batch = {"schema": "w49b-g0-batch-1", "base": "b2d074d2df24-940384c06f73", "points": [
            {"label": "identity", "scales": [1, 2], "pose": "both", "overrides": {}},
            {"label": "opaque", "scales": [1, 2], "pose": "inactive", "overrides": {
                "receded.dark": {"tintAlphaFar1x": 0.2, "tintAlphaFar2x": 0.2}}}]}
        with tempfile.TemporaryDirectory() as tmp:
            run, out = self.run_builder(batch, Path(tmp))
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("violates X75", run.stderr)
            self.assertFalse(out.exists())

    def test_self_consistent_candidate_change_cannot_escape_supplied_batch(self):
        import importlib.util
        s = importlib.util.spec_from_file_location("w49b_render", HERE / "render.py")
        r = importlib.util.module_from_spec(s); s.loader.exec_module(r)
        batch = {"schema": "w49b-g0-batch-1", "base": "b2d074d2df24-940384c06f73", "points": [
            {"label": "identity", "scales": [1, 2], "pose": "both", "overrides": {}}]}
        with tempfile.TemporaryDirectory() as tmp:
            parent = Path(tmp); run, out = self.run_builder(batch, parent)
            self.assertEqual(run.returncode, 0, run.stderr)
            candidate = out / "identity/candidate.json"
            changed = json.loads(candidate.read_text()); changed["name"] += "-changed"
            candidate.write_text(json.dumps(changed))
            with self.assertRaises(ValueError):
                r.verify_candidate(out, "identity", parent / "supplied.json", HERE.parent / "references.json")

    def test_candidate_endpoint_mutation_is_rejected(self):
        batch = {"schema": "w49b-g0-batch-1", "base": "b2d074d2df24-940384c06f73", "points": [
            {"label": "identity", "scales": [1], "pose": "both", "overrides": {}}]}
        with tempfile.TemporaryDirectory() as tmp:
            run, out = self.run_builder(batch, Path(tmp))
            self.assertEqual(run.returncode, 0, run.stderr)
            endpoint = out / "identity/receded.dark.json"; endpoint.write_text('{}')
            verify = subprocess.run([str(TSX), str(HERE / "verify-candidate.ts"),
                                     str(out / "identity/candidate.json")], cwd=CAL,
                                    capture_output=True, text=True)
            self.assertNotEqual(verify.returncode, 0)
            self.assertIn("sha256", verify.stderr)


if __name__ == "__main__": unittest.main()
