"""W49a G0: the declaration tool's own guarantees (`declare.py`).

    python3.12 -B -m unittest -v test_declare      (from this directory)
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import declare as D

sys.path.insert(0, str(D.PROBES))
import probe  # noqa: E402

RULINGS = Path("/Users/new/.claude/jobs/17c7ce02/tmp/w49-rulings.md")
COMMIT = subprocess.run(["git", "log", "-1", "--format=%H", "--", D.CHARTER], cwd=D.ROOT, capture_output=True,
                        text=True, check=True).stdout.strip()


class Declare(unittest.TestCase):
    def test_the_rulings_are_folded_verbatim(self):
        text = D.charter_at(COMMIT)
        for n in range(1, 9):
            body = D.ruling(text, n)
            self.assertTrue(body.startswith(f"DL{n}"), n)
        if RULINGS.exists():
            source = RULINGS.read_text()
            for n in range(1, 9):
                self.assertIn(D.ruling(text, n).split("\n\n*Later")[0], source, n)

    def test_both_parts_assemble_deterministically(self):
        a, b = D.part1(COMMIT), D.part1(COMMIT)
        self.assertEqual(D.canonical(a), D.canonical(b))
        self.assertEqual(sorted(a["probes"]["P2"]["far"]), [-0.1, 0, 0.05, 0.09, 0.1, 0.15])
        self.assertEqual({k: len(v) for k, v in a["probes"]["P2"]["cells"].items()}, {"1x": 21, "2x": 21})
        self.assertEqual({k: len(v) for k, v in a["probes"]["P1"]["cells"].items()}, {"1x": 45, "2x": 45})
        two = D.part2(COMMIT, "0" * 64)
        self.assertEqual(two["amendmentAfterGate"], "none")
        self.assertIn("NO post-gate amendment", two["rulings"]["DL4"])
        self.assertEqual(D.canonical(two), D.canonical(D.part2(COMMIT, "0" * 64)))

    def test_no_withheld_cell_is_rendered(self):
        one = D.part1(COMMIT)
        withheld = {key for key, c in probe.R.b2d074_cells().items() if c["partition"] != "gate"}
        self.assertEqual(len(withheld), 22)
        for name in ("P1", "P2"):
            for scale, scenes in one["probes"][name]["cells"].items():
                self.assertFalse({(int(scale[0]), s) for s in scenes} & withheld, name)

    def test_hash_and_amend_refuse_once_a_render_exists(self):
        saved = D.RUNS
        try:
            D.RUNS = Path(tempfile.mkdtemp()) / "runs.jsonl"
            D.RUNS.write_text("{}\n")
            with self.assertRaises(D.Refusal):
                D.hash_(COMMIT)
            with self.assertRaises(D.Refusal):
                D.amend(2, "a reason", None)
        finally:
            D.RUNS = saved


if __name__ == "__main__":
    unittest.main()
