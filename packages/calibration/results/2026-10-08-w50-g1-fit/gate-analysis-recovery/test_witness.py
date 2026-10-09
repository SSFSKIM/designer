"""Synthetic gates only: exact witness precedes judgment and burns its one attempt."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('recovery_witness', HERE/'witness.py')
W = importlib.util.module_from_spec(spec)
spec.loader.exec_module(W)


class WitnessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.old = self.home/'old'; self.old.mkdir()
        self.new = self.home/'new'
        self.keys = [['p', 'webgpu', 'a', 'level'], ['p', 'webgpu', 'b', 'level']]
        self.old_auth = {k: {'path': str(self.home/('old-'+k)), 'sha256': 'a'*64}
                         for k in W.AUTHORITY}
        self.new_auth = {k: {'path': str(self.home/('new-'+k)), 'sha256': 'b'*64}
                         for k in W.AUTHORITY}
        self.rows = [self.row(k, self.old_auth) for k in self.keys]
        name = W.filename(self.keys[0])
        p = self.old/name; p.write_bytes(W.encode(self.rows[0]))
        self.manifest = {'count': 1, 'files': [{**W.pin(p), 'bytes': p.stat().st_size}]}
        self.judged = 0
        self.measured = 0

    def row(self, key, authority):
        return {'schema': 'w50-keyed-measurement-evidence-1', 'phase': 'gate', **authority,
                'cohort': [{'sha256': 'c'*64}], 'config': {'sha256': 'd'*64},
                'row': dict(zip(W.KEY, key), readings={'value': 1.25, 'nested': {'contract': 7}})}

    def measure(self):
        self.measured += 1
        self.new.mkdir()
        for key in self.keys:
            (self.new/W.filename(key)).write_bytes(W.encode(self.row(key, self.new_auth)))
        (self.new/'phase.json').write_bytes(W.encode({'synthetic': True}))
        return {'status': 'EVIDENCE_ONLY'}

    def judge(self, measured):
        self.assertEqual(measured, {'status': 'EVIDENCE_ONLY'})
        self.assertEqual(self.measured, 1)
        self.judged += 1
        return {'status': 'PASS_EXPOSED_OWNER_PENDING'}

    def witness(self):
        return W.compare(self.manifest, self.old, self.new, self.keys, self.old_auth, self.new_auth)

    def run_gate(self, measure=None):
        return W.once(self.home/'analysis.started.json', {'analysis': 2},
                      measure or self.measure, self.witness, self.judge)

    def test_exact_witness_allows_judge_after_all_keys(self):
        result = self.run_gate()
        self.assertEqual(result['status'], 'PASS_EXPOSED_OWNER_PENDING')
        self.assertEqual(result['witness']['count'], 1)
        self.assertEqual(self.judged, 1)

    def test_only_top_level_authority_is_excluded(self):
        def changed():
            value = self.measure()
            p = self.new/W.filename(self.keys[0]); row = json.loads(p.read_bytes())
            row['row']['readings']['nested']['contract'] = 8
            p.write_bytes(W.encode(row)); return value
        self.assertEqual(self.run_gate(changed)['status'], 'NEITHER')
        self.assertEqual(self.judged, 0)

    def test_authority_only_changes_allowed_but_wrong_binding_refuses(self):
        self.measure()
        self.assertEqual(self.witness()['count'], 1)
        p = self.new/W.filename(self.keys[0]); row = json.loads(p.read_bytes())
        row['executionRoot'] = self.old_auth['executionRoot']
        p.write_bytes(W.encode(row))
        with self.assertRaises(ValueError): self.witness()

    def test_old_raw_bytes_checked_before_any_parse(self):
        self.measure()
        p = self.old/W.filename(self.keys[0]); p.write_bytes(b'NOT JSON')
        with self.assertRaisesRegex(ValueError, 'raw'):
            self.witness()

    def test_extra_missing_duplicate_population_refused(self):
        for kind in ('old-extra', 'new-extra', 'new-missing', 'duplicate-manifest', 'duplicate-keys'):
            with self.subTest(kind=kind):
                self.setUp(); self.measure()
                if kind == 'old-extra': (self.old/'extra').write_text('extra')
                if kind == 'new-extra': (self.new/'extra.json').write_text('{}')
                if kind == 'new-missing': (self.new/W.filename(self.keys[1])).unlink()
                if kind == 'duplicate-manifest':
                    self.manifest['files'] *= 2; self.manifest['count'] = 2
                if kind == 'duplicate-keys': self.keys.append(self.keys[0])
                with self.assertRaises(ValueError): self.witness()

    def test_incomplete_successor_never_reaches_judge(self):
        def incomplete():
            value = self.measure()
            (self.new/W.filename(self.keys[1])).unlink()
            return value
        self.assertEqual(self.run_gate(incomplete)['status'], 'NEITHER')
        self.assertEqual(self.judged, 0)

    def test_refusal_fault_and_restart_never_judge(self):
        def fault(): raise RuntimeError('synthetic numerical detail not public')
        result = self.run_gate(fault)
        self.assertEqual(result, {'status': 'NEITHER', 'measurementStatus': 'UNMEASURED'})
        self.assertEqual(self.judged, 0)
        with self.assertRaises(FileExistsError): self.run_gate()
        self.assertEqual(self.measured, 0)

    def test_crash_marker_bars_restart(self):
        W.write_once(self.home/'analysis.started.json', {'analysis': 2})
        with self.assertRaises(FileExistsError): self.run_gate()
        self.assertEqual(self.measured, 0)


if __name__ == '__main__': unittest.main()
