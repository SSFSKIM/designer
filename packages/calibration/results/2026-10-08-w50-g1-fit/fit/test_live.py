"""Synthetic LIVE fit-role tests over the judge's temporary World; no real data is opened."""
import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import sys
import types
import unittest

HERE = Path(__file__).resolve().parent


def source(path, name):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(Path(path).read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


H = source(HERE.parent/'judge/test_live.py', 'w50_fit_live_test_world')
P1 = H.P1
LEVEL = (P1, 'webgpu', 'cell-grey-004-s096__rest', 'deep8-channel-median')


def seal(path, value):
    raw = (json.dumps(value, sort_keys=True)+'\n').encode()
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_bytes(raw)
    Path(str(path)+'.sha256').write_text(f'{hashlib.sha256(raw).hexdigest()}  {Path(path).name}\n')


class FitTests(unittest.TestCase):
    def setUp(self):
        self.world = H.World(self)
        self.world.install(self)
        self.fit = source(HERE/'live.py', 'w50_fit_live_under_test')

    def analyse(self, overrides=None, rows=None):
        w = self.world
        context = w.context('fit', rows=rows)
        measured = w.measured(context, overrides)
        w.active = context
        try:
            return self.fit.evaluate(context, measured, w.fit_config)
        finally:
            w.active = None

    def test_one_rendered_point_records_selection_quantities_without_a_verdict(self):
        analysis = self.analyse({LEVEL: H.candidate('deep8-channel-median', [22, 20, 20])})
        self.assertEqual(analysis['status'], 'FIT_ANALYSIS_ONLY')
        self.assertNotIn(analysis['status'], ('PASS', 'NEITHER', 'PASS_EXPOSED_OWNER_PENDING'))
        flat = json.dumps(analysis)
        for verdict in ('"WITHIN"', '"EXCEEDS"', '"PASS"', '"NEITHER"', 'PASS_EXPOSED_OWNER_PENDING'):
            self.assertNotIn(verdict, flat)
        selection = analysis['selection']
        # Nine WebGPU absolute-level channels (uniform deep8 and centre8, the span control's
        # deep8); CSS, input64, T1 and reported rows are outside the clause 1-2 ranking.
        self.assertEqual(selection['levelComponents'], 9)
        self.assertEqual(selection['worstLowEndLevelErrorCodes'], 2)
        self.assertAlmostEqual(selection['meanAbsoluteLowEndLevelErrorCodes'], 2/9)
        # Four dark endpoints x three rows of [.1, .1, .2, .25] from the gate0 zero origin.
        self.assertAlmostEqual(selection['squaredNormalizedDistanceFromCurrent'], 12*(.01+.01+.04+.0625))
        self.assertEqual(selection['candidateId'], '+'.join(sorted(p['sha256'] for p in self.world.cohort)))
        self.assertEqual(selection['key'][:3], [2, 2/9, selection['squaredNormalizedDistanceFromCurrent']])
        self.assertEqual(selection['order'][0], 'Minimum worst exposed low-end level error')
        record = next(r for r in analysis['rows'] if tuple(r[k] for k in H.KEY) == LEVEL)
        self.assertEqual([c['error'] for c in record['levelErrors']], [2, 0, 0])
        self.assertEqual(analysis['charts']['receded.dark.0.5'], [[.1, .1, .2, .25]]*3)

    def test_verdict_statuses_are_refused_and_withheld_cells_never_enter(self):
        for verdict in ('PASS', 'NEITHER', 'PASS_EXPOSED_OWNER_PENDING'):
            with self.assertRaises(ValueError):
                self.fit._verdict_free({'status': verdict})
        blind = {tuple(k) for k in self.world.dependencies['gateKeys']}
        blind.add((P1, 'webgpu', 'cell-grey-007-s096__rest', 'deep8-channel-median'))
        with self.assertRaises(ValueError):
            self.analyse(rows=blind)

    def test_fit_record_names_exactly_one_completed_point_by_metadata(self):
        w = self.world
        analysis = self.analyse()
        root = w.root_path
        Path(str(root)+'.sha256').write_text(f'{H.sha_bytes(root.read_bytes())}  {root.name}\n')
        def completed(name, value):
            contract = root.parent/'fit'/f'{name}.json'
            seal(contract, {'phase': 'fit', 'executionRootSha256': H.sha_bytes(root.read_bytes()), 'cohort': w.cohort})
            result = Path(str(contract)+'.result.json')
            seal(result, {'contractSha256': H.sha_bytes(contract.read_bytes()),
                          'report': {'status': 'CAPTURED', 'analysis': value}})
            return {'path': str(result.relative_to(w.repo)), 'sha256': H.sha_bytes(result.read_bytes())}
        one = completed('one', analysis)
        record = self.fit.fit_record(root, [one])
        self.assertEqual(record['schema'], 'w50-g1-fit-record-1')
        self.assertEqual(record['selected'], w.cohort)
        self.assertEqual(record['completed'], [one])
        def numbers(value):
            if isinstance(value, dict): return [n for v in value.values() for n in numbers(v)]
            if isinstance(value, list): return [n for v in value for n in numbers(v)]
            return [value] if type(value) in (int, float) else []
        self.assertEqual(numbers(record), [], 'A fit record is metadata only')
        with self.assertRaises(ValueError):
            self.fit.fit_record(root, [one, completed('two', analysis)])
        with self.assertRaises(ValueError):
            self.fit.fit_record(root, [completed('verdict', {**analysis, 'status': 'PASS'})])

    def test_quarantine_canaries_hold(self):
        w = self.world
        log = w.base/'quarantine/fit.log'
        ok, analysis = H.Q.run_private(log, lambda: self.analyse(
            {LEVEL: H.candidate('deep8-channel-median', [H.CANARY, 20, 20])}))
        self.assertTrue(ok)
        self.assertIn(H.CANARY_TEXT, json.dumps(analysis))
        self.assertEqual(log.read_text(), '')
        loud = {LEVEL: H.candidate('deep8-channel-median', [H.CANARY*10, 20, 20])}
        public = io.StringIO()
        with contextlib.redirect_stdout(public), contextlib.redirect_stderr(public):
            with self.assertRaises(ValueError) as caught:
                self.analyse(loud)
        for text in (H.CANARY_TEXT, '876.54321'):
            self.assertNotIn(text, str(caught.exception)+public.getvalue())
        error_log = w.base/'quarantine/fit-error.log'
        ok, value = H.Q.run_private(error_log, lambda: self.analyse(loud))
        self.assertFalse(ok)
        self.assertNotIn('876.54321', error_log.read_text())


if __name__ == '__main__':
    unittest.main()
