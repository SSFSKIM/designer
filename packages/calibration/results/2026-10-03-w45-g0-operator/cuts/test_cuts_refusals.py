#!/usr/bin/env python3.12
"""W45 G0 (b): the cuts port refuses W44's bindings and reads its shared inputs pinned (X58).

    cd packages/calibration/results/2026-10-03-w45-g0-operator/cuts
    python3.12 -B -m unittest test_cuts_refusals -v
"""
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import bed as B  # noqa: E402
import cuts  # noqa: E402

W44_G1 = B.RESULTS / "2026-10-03-w44-g1-refit"


class Refuses(unittest.TestCase):
    def refused(self, fn, needle="X58"):
        with self.assertRaises(SystemExit) as raised:
            fn()
        self.assertIn(needle, str(raised.exception))

    def test_an_output_in_w44s_evidence(self):
        out = W44_G1 / "references" / "w45-red-case.json"
        self.refused(lambda: cuts.main(["--published", "6d18c059eb42", "--captures", "/nonexistent",
                                        "--out", str(out)]))
        self.assertFalse(out.exists())

    def test_a_text_report_in_w44s_scratch(self):
        out = Path.home() / "vitrea-w44" / "g1-scratch" / "w45-red-case.txt"
        self.refused(lambda: cuts.main(["--published", "6d18c059eb42", "--captures", "/nonexistent",
                                        "--out", str(Path(tempfile.mkdtemp()) / "o.json"),
                                        "--text", str(out)]))
        self.assertFalse(out.exists())

    def test_a_bed_matrix_in_w44s_scratch(self):
        self.refused(lambda: B.load([str(Path.home() / "vitrea-w44" / "g1-scratch" / "fit" / "matrix.json")],
                                    "candidate", str(W44_G1 / "fit/candidates/m3-t0.1/candidate.json")))

    def test_a_w44_candidate_document(self):
        self.refused(lambda: B.Candidate.read(str(W44_G1 / "fit/candidates/m3-t0.1/candidate.json")))


class SharedInputs(unittest.TestCase):
    def test_pinned_byte_for_byte(self):
        names = sorted(p.relative_to(B.RESULTS).as_posix() for p in B.SHARED_PINS)
        self.assertEqual(names, ["2026-10-03-w44-g0-declaration/bar/t1-bar.json",
                                 "2026-10-03-w44-g0-declaration/referees/plan.py",
                                 "2026-10-03-w44-g0-declaration/referees/referees.json",
                                 "2026-10-03-w44-g1-refit/cuts/readings.py",
                                 "2026-10-03-w44-g1-refit/cuts/t1.py"])
        for path, want in B.SHARED_PINS.items():
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), want, path.name)

    def test_t1_and_readings_are_w44_g1s_and_bed_is_w45s(self):
        import readings
        self.assertEqual(Path(cuts.T1.__file__).resolve(), (W44_G1 / "cuts" / "t1.py").resolve())
        self.assertEqual(Path(readings.__file__).resolve(), (W44_G1 / "cuts" / "readings.py").resolve())
        self.assertEqual(Path(cuts.T1.B.__file__).resolve(), (HERE / "bed.py").resolve())
        self.assertFalse((HERE / "t1.py").exists() or (HERE / "readings.py").exists())


if __name__ == "__main__":
    unittest.main()
