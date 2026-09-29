"""Scratch-only checks: never a production receipt, scorer, browser or native payload."""
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'exposure'))
import test_runner
import runner
import preflight


class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.fixture = test_runner.ExposureTests(methodName='runTest')
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        f = self.fixture
        self.put = f.put
        self.put(preflight.RUNTIME, preflight.REQUIRED)
        # Bind the executable entry points just as a production freeze does.
        for name in (preflight.RUNNER, preflight.BOUNDARY, preflight.SELF):
            self.put(name, (preflight.ROOT / name).read_text())
        f.commit()
        f.manifest = runner.freeze(f.root, f.wave, f.candidates, config='config.json',
                                  scorer='scorer.py', declaration='declaration.txt',
                                  closure='closure.json', instruments=[preflight.RUNTIME],
                                  dry_cells=f.cells)
        self.put('frozen.json', f.manifest)
        f.commit()
        self.evidence = Path(f.tmp.name) / 'preflight.json'
        # Exercise the real verifier on its existing synthetic fixture. Production
        # CLI has no synthetic-mode switch, backend injection or alternate receipt.
        adapter = SimpleNamespace(ROOT=f.root, boundary=SimpleNamespace(default_wave=lambda: f.wave),
                                  verify=lambda root, wave, path, mode:
                                  runner.verify(root, wave, path, 'synthetic'))
        self.loader = patch.object(preflight, 'load_runner', return_value=adapter).start()
        self.addCleanup(patch.stopall)
        patch.object(preflight, 'probe_versions', return_value=dict(preflight.REQUIRED)).start()
        self.guards = [patch.object(runner.boundary, 'Receipt', side_effect=AssertionError('receipt')),
                       patch.object(runner, 'run_production', side_effect=AssertionError('production'))]
        for guard in self.guards:
            guard.start()

    def run_check(self):
        return preflight.run(self.fixture.root, self.fixture.root / 'frozen.json', self.evidence)

    def report(self):
        return json.loads(self.evidence.read_text())

    def test_verified_synthetic_bytes_record_digests_without_exposure(self):
        self.assertEqual(self.run_check(), 0)
        report = self.report()
        self.assertEqual(report['status'], 'success')
        self.assertEqual(report['manifestSha256'], runner.sha(self.fixture.root / 'frozen.json'))
        self.assertEqual(report['runtimeSha256'], runner.sha(self.fixture.root / preflight.RUNTIME))
        self.assertIn('runner.verify:production', report['checks'])
        self.assertEqual(report['liveRuntime'], preflight.REQUIRED)

    def test_stale_instrument_stops_before_runner_or_scorer_import(self):
        self.put('scorer.py', "raise AssertionError('SCORER IMPORTED')\n")
        self.assertEqual(self.run_check(), 1)
        self.loader.assert_not_called()
        self.assertEqual(self.report()['status'], 'refusal')
        self.assertIn('uncommitted', self.report()['error'])

    def test_committed_instrument_drift_stops_before_import(self):
        self.put('scorer.py', "raise AssertionError('SCORER IMPORTED')\n")
        self.fixture.commit()
        self.assertEqual(self.run_check(), 1)
        self.loader.assert_not_called()
        self.assertIn('frozen hash mismatch', self.report()['error'])

    def test_each_live_runtime_mismatch_stops_before_runner_import(self):
        for key, bad in [('python', [3, 13]), ('numpy', '0.0'), ('pillow', '0.0')]:
            with self.subTest(key=key):
                self.evidence = self.evidence.with_name(key + '.json')
                live = dict(preflight.REQUIRED, **{key: bad})
                with patch.object(preflight, 'probe_versions', return_value=live):
                    self.assertEqual(self.run_check(), 1)
                self.loader.assert_not_called()
                self.assertIn('live runtime mismatch', self.report()['error'])

    def test_runtime_document_drift_stops_before_import(self):
        self.put(preflight.RUNTIME, dict(preflight.REQUIRED, numpy='0.0'))
        self.assertEqual(self.run_check(), 1)
        self.loader.assert_not_called()

    def test_absent_manifest_records_refusal_not_success(self):
        (self.fixture.root / 'frozen.json').unlink()
        self.assertEqual(self.run_check(), 1)
        self.assertEqual(self.report()['status'], 'refusal')
        self.loader.assert_not_called()

    def test_existing_evidence_is_never_overwritten(self):
        self.evidence.write_text('prior evidence')
        with self.assertRaises(FileExistsError):
            self.run_check()
        self.assertEqual(self.evidence.read_text(), 'prior evidence')
        self.loader.assert_not_called()

    def test_full_verifier_rejects_added_source_inventory(self):
        self.put('packages/renderer-webgpu/src/extra.ts', 'export const extra = 1;')
        self.assertEqual(self.run_check(), 1)
        self.assertIn('source inventory changed', self.report()['error'])
        self.assertEqual(self.loader.call_count, 1)


if __name__ == '__main__':
    unittest.main()
