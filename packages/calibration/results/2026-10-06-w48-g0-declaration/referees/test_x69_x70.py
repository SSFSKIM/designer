"""W48 G0 (b): X69's and X70's red cases carried under W48's bindings (charter clause 2; X69, X70).

X70 (requested == planned before a render; measured == planned at read) lives in W47's
`ladders/ladder.py` (`x70_plan`, `admitted`) and `ladders/read.py` (`x70_read`, inherited by path). W48
renders no ladder, and W47's `fit/fit.py` carries no X70 check of its own (a finding recorded in §5.212).
The red cases are W47's `ladders/test_ladder.py` class `X70`, run unchanged under W48's bindings; while
that module imports, `bindings.LADDER_PROTOCOL` points at W47's ladder protocol (the rungs and sets the
cases read: W48's corrected protocol has W48's shape, not a runner's), so `ladder.py` and `read.py` bind
their protocol path to W47's committed file. The X69 manifest checks are W47's `referees/test_referees.py`,
which passes under W48's bindings unchanged (`tools/inherited/referees__test_referees.txt`).

    python3.12 -B -m unittest -v test_x69_x70      (from this directory)
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import inherited_suite as S  # noqa: E402

W = S.W
W47_TESTS = S.module("ladders/test_ladder.py",
                     importing=mock.patch.object(W, "LADDER_PROTOCOL", W.W47_G0 / "ladders" / "protocol.json"))


class Bound(unittest.TestCase):
    def test_the_x70_functions_read_w48s_bindings(self):
        ladder = sys.modules["ladder"]
        self.assertIs(ladder.W, W)
        self.assertEqual(ladder.PROTOCOL_PATH, W.W47_G0 / "ladders" / "protocol.json")
        self.assertEqual(W.LADDER_PROTOCOL, W.G0 / "ladders" / "protocol.json")   # restored after the import


def load_tests(loader, tests, pattern):
    return S.suite(loader, tests, W47_TESTS, {}, only={"X70"})


if __name__ == "__main__":
    unittest.main()
