"""The static driver's own main() routes each sealed fit's solvers through SolverMemo.

main() runs unchanged on a temporary HERE with a synthetic declaration; only the
kernel-level probe, launch authority, native preparation and inactive load are
stubbed. The real fitter runs one original start per task on four synthetic
pixels. Spies at the solver boundary observe what the sealed fitter actually
called, rather than reading run.py's text.
"""
import functools
import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import numpy as np

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('static_run', HERE/'run.py')
run = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run)
from fixtures import observations  # noqa: E402  (memoization/ is on path via run.py)

r, f = run.r, run.r.f


def synthetic_inactive():
    """Both inactive endpoints, carrying the compact forward the driver's context reads."""
    rows = observations('M2', False, (1, 3))
    for i, o in enumerate(rows):
        fall = np.zeros_like(o['g']['d'])
        o.update(compact=r.CompoundComposite([r.CompactComposite(o['g'], o['backdrop'], fall)]),
                 amplitude=[0.], role='calibration', cell=f'synthetic/{i}', scale=1,
                 stateMembership=[])
    return rows


class StaticDriverMemoTests(unittest.TestCase):
    def test_main_fits_under_memo_with_scoped_observations_and_compact_forward(self):
        inactive = synthetic_inactive()
        tasks = [['M1', 'curvature', 3], ['M2', 'device', 5]]
        memos, fits, solves = [], [], []

        class RecordingMemo(run.SolverMemo):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                memos.append(self)

        real_partition = run.start_partition.partition

        def recording_partition(function, indices):
            fit, provenance = real_partition(function, indices)
            def recorded(*args):
                fits.append(args)
                return fit(*args)
            return recorded, provenance

        def spy(kind, real):
            @functools.wraps(real)  # SolverMemo binds the real solver's signature.
            def solver(*args, **kwargs):
                # Observed from inside the sealed fitter's own solver call.
                callback = kwargs.get('fun', args[0] if args else None)
                solves.append(dict(kind=kind, memo=memos[-1] if memos else None,
                    boundaryInstalled=getattr(getattr(f, kind), '__memo_solver__', False),
                    callbackWrapped=hasattr(callback, '__memo_label__'),
                    compactForward=f.predict is r.compact_predict))
                return real(*args, **kwargs)
            return solver

        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            (root/'declaration.json').write_text(json.dumps(dict(
                sourceSha256={}, partitions=dict(A=tasks))))
            with patch.object(run, 'HERE', root), \
                    patch.object(run, 'subprocess', SimpleNamespace(check_output=lambda *a: b'80\n')), \
                    patch.object(run.scope, 'verify_authority', lambda: dict(synthetic=True)), \
                    patch.object(run.r, 'Preparation', lambda: 'synthetic-preparation'), \
                    patch.object(run.prior, 'load_inactive',
                                 lambda prep, role: inactive if role == 'calibration' else None), \
                    patch.object(run.start_partition, 'partition', recording_partition), \
                    patch.object(run, 'SolverMemo', RecordingMemo), \
                    patch.object(f, 'least_squares', spy('least_squares', f.least_squares)), \
                    patch.object(f, 'minimize', spy('minimize', f.minimize)), \
                    patch('sys.argv', ['run.py', '--partition', 'A']):
                run.main()
            results = [json.loads((root/'A'/f'{g}-{fam}-start-{i:02d}.json').read_text())
                       for fam, g, i in tasks]
            self.assertTrue((root/'A'/'complete.json').exists())

        self.assertEqual(len(memos), 2)
        self.assertEqual(len(fits), 2)
        for (family, geometry, index), memo, fit, result in zip(tasks, memos, fits, results):
            curvature = geometry == 'curvature'
            expected = [inactive[0]] if family == 'M1' else inactive
            # The memo keys the very observations/family/curvature the fitter solves.
            self.assertIs(memo.fitter, f)
            self.assertIs(fit[0], memo.observations)
            self.assertEqual([id(o) for o in memo.observations], [id(o) for o in expected])
            self.assertEqual((memo.family, memo.curvature, memo.enabled), (family, curvature, True))
            self.assertEqual(fit[1:], (family, False, curvature))
            mine = [s for s in solves if s['memo'] is memo]
            self.assertTrue(mine)
            self.assertEqual(len(mine), len(memo.solvers))
            for s in mine:
                self.assertTrue(s['boundaryInstalled'] and s['callbackWrapped']
                                and s['compactForward'], s)
            summary = result['memoization']
            self.assertEqual(summary, json.loads(json.dumps(memo.summary())))
            self.assertTrue(summary['enabled'])
            self.assertGreater(summary['hits'], 0)
            self.assertEqual([s['startIndex'] for s in result['starts']], [index])
            self.assertEqual(result['staticPartition'], 'A')
        # Every solver the fitter called ran inside one of the two memo contexts.
        self.assertTrue(all(s['memo'] is not None for s in solves))
        self.assertEqual(len(solves), sum(len(m.solvers) for m in memos))
        # Context exit restored the spies, and compact_forward restored predict.
        self.assertFalse(getattr(f.least_squares, '__memo_solver__', False))
        self.assertIsNot(f.predict, r.compact_predict)


if __name__ == '__main__':
    unittest.main()
