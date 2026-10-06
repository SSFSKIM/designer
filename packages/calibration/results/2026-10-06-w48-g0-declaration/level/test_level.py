"""W48 G0 (b): W47's level-check tests, run unchanged under W48's bindings (charter clause 2; X61, X65).
W47's `level/test_level.py` writes its fixtures to `.test-scratch` beside ITSELF, inside W47's evidence
directory, which W48 may not write; its module attribute `SCRATCH` (read at call time by every case) is
pointed at `.test-scratch` beside THIS file (inside the repository, as `Candidate.read` requires; W47's
cases remove it), and nothing else changes. Every case is W47's: the projection,
identity on the published `d0219cd684bf` rows under candidate provenance (and each red case reading
DIFFERS), the arithmetic, operator 1's `alphaBase` at identity and graded, the attribution.

    python3.12 -B -m unittest -v test_level      (from this directory)
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import inherited_suite as S  # noqa: E402

W = S.W
SCRATCH = Path(__file__).resolve().parent / ".test-scratch"
T = S.module("level/test_level.py", patch={"SCRATCH": SCRATCH})


class W48Level(unittest.TestCase):
    def test_the_level_check_is_w47s_under_w48s_bindings(self):
        self.assertIs(T.L.W, W)
        self.assertEqual(Path(T.L.__file__), W.W47_G0 / "level" / "level.py")
        self.assertNotIn(W.W47_G0, T.SCRATCH.parents)


def load_tests(loader, tests, pattern):
    return S.suite(loader, tests, T, {})


if __name__ == "__main__":
    unittest.main()
