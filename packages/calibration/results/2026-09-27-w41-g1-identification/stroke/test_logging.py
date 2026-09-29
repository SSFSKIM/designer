"""Optimizer telemetry must not alter arguments, outcomes or the previous profiler."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import numpy as np
import replay
import run_logged


class LoggingTests(unittest.TestCase):
    def test_observer_records_real_solvers_without_changing_their_result(self):
        def solve():
            least = replay.f.least_squares(lambda x: np.array([x[0]-3]), [0.], max_nfev=30)
            mini = replay.f.minimize(lambda x: (x[0]-2)**2, [0.], method='SLSQP',
                                    options=dict(maxiter=30, ftol=1e-10))
            return least, mini
        baseline = solve()
        with tempfile.TemporaryDirectory(dir=replay.HERE, prefix='synthetic-observer-') as root:
            output = Path(root)/'attempt'
            def entry(*args, **kwargs):
                output.mkdir()
                actual = solve()
                for a, b in zip(actual, baseline):
                    np.testing.assert_array_equal(a.x, b.x)
                    self.assertEqual(a.nfev, b.nfev)
                    self.assertEqual(a.success, b.success)
            with patch.object(sys, 'argv', ['run_logged.py', '--out', str(output)]), \
                    patch.object(run_logged.runpy, 'run_path', entry):
                run_logged.main()
            rows = [json.loads(line) for line in (output/'optimizer-checkpoints.jsonl').read_text().splitlines()]
            self.assertEqual([row['kind'] for row in rows], ['least_squares', 'minimize'])
            self.assertIsNone(sys.getprofile())


if __name__ == '__main__':
    unittest.main()
