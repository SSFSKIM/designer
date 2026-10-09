"""Synthetic completed-current evidence only; never open an actual result or image."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import types
import unittest

HERE = Path(__file__).resolve().parent


def source(path, name):
    module = types.ModuleType(name); module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


class AnalysisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a = source(HERE/'analysis.py', 'synthetic_completed_current')

    def fixture(self):
        a = self.a; np = a.M.np
        canvas = {'width': 128, 'height': 128}
        component = {'kind': 'rrect', 'size': [112, 96], 'radius': 0}
        background = np.zeros((128, 128, 3), dtype=np.uint8)
        background[62:66, 62:66] = 255
        native = np.full_like(background, 70)
        mask = np.zeros((128, 128), dtype=bool); mask[20, 20:22] = True
        reading = a.M.R.S.read_frame(native, background, component, canvas, 1,
            impulse=True, include_structured=True, silhouette_mask=mask)
        runs = [dict(run=n, dependency='original/no-glass', evidence={'sha256': str(n)*64},
                     readings=copy.deepcopy(reading)) for n in (1, 2, 3)]
        cell = dict(id='p/s', profile='p', scene='s', family='structured', role='calibration',
                    pose='active', scale=1, reference='original/no-glass', runs=runs,
                    statistics=a.M.R.aggregate_runs(runs))
        web = np.full_like(background, 20); web[20, 20] = 0; web[20, 21] = 255
        return canvas, component, background, cell, web

    def test_current_uses_original_native_silhouette_and_preserves_run_aggregation(self):
        canvas, component, background, cell, web = self.fixture()
        result = self.a.measure_pixels(web, background, cell, component, canvas, impulse=True,
                                       renderer='webgpu')
        self.assertEqual(result['statistics']['T1-full-silhouette']['value'], .5)
        self.assertEqual(result['statistics']['deep8-channel-median']['value'], [20., 20., 20.])
        self.assertEqual(result['statistics']['T1-full-silhouette']['runValues'], [.5]*3)

    def test_two_x_supports_and_optional_empty_t1_never_use_a_web_silhouette(self):
        a = self.a; np = a.M.np
        canvas, component, background, cell, web = self.fixture()
        for scale in (1, 2):
            with self.subTest(scale=scale):
                bg = np.repeat(np.repeat(background, scale, axis=0), scale, axis=1)
                image = np.repeat(np.repeat(web, scale, axis=0), scale, axis=1)
                empty = np.zeros(image.shape[:2], dtype=bool)
                reading = a.M.R.S.read_frame(np.full_like(image, 70), bg, component, canvas,
                    scale, impulse=True, include_structured=True, silhouette_mask=empty)
                native = copy.deepcopy(cell); native.update(scale=scale, family='span')
                native['runs'] = [dict(run=n, dependency='original/no-glass',
                    evidence={'sha256': str(n)*64}, readings=copy.deepcopy(reading)) for n in (1, 2, 3)]
                native['statistics'] = a.M.R.aggregate_runs(native['runs'], reported=True)
                result = a.measure_pixels(image, bg, native, component, canvas, impulse=True,
                                          renderer='css')
                t1 = result['statistics']['T1-full-silhouette']
                self.assertEqual(t1['status'], 'UNMEASURED_EMPTY_SUPPORT')
                self.assertIsNone(t1['value']); self.assertIsNone(t1['B'])
                self.assertEqual(t1['runValues'], [None, None, None])
                self.assertEqual([w['pixels'] for w in t1['nativeSupportWitnesses']], [0, 0, 0])
                self.assertEqual([w['maskShape'] for w in t1['nativeSupportWitnesses']],
                                 [[128*scale, 128*scale]]*3)
                self.assertEqual(result['statistics']['deep8-channel-median']['value'], [20., 20., 20.])
                self.assertEqual(result['statistics']['deep8-far24-luma-mean']['status'], 'REPORTED')

    def test_changed_native_aggregate_rejected_not_silently_recomputed(self):
        canvas, component, background, cell, web = self.fixture()
        cell['statistics']['deep8-channel-median']['value'] = [1., 2., 3.]
        with self.assertRaisesRegex(ValueError, 'aggregation'):
            self.a.measure_pixels(web, background, cell, component, canvas, impulse=True,
                                  renderer='webgpu')

    def test_no_glass_dependency_controls_original_impulse_support(self):
        canvas, component, background, cell, web = self.fixture()
        with self.assertRaisesRegex(ValueError, 'support witness'):
            self.a.measure_pixels(web, background*0, cell, component, canvas, impulse=True,
                                  renderer='css')

    def test_additive_projection_keeps_original_pair_and_never_overrides_original_row(self):
        canvas, component, background, cell, web = self.fixture()
        read = self.a.measure_pixels(web, background, cell, component, canvas, impulse=True,
                                    renderer='css')
        rows = [dict(profile='p', renderer='css', scene='s', statistic=name, role='calibration',
                     currentDocumentPair={'active': 'original-a', 'receded': 'original-r'},
                     currentGeneration='original-generation', B={'held': 1})
                for name in read['statistics']]
        original = copy.deepcopy(rows)
        evidence = self.a.project_rows(rows, read, {'candidateDocument': {'sha256': 'a'*64}})
        self.assertEqual(rows, original)
        self.assertEqual([r['originalReference'] for r in evidence], original)
        self.assertEqual(evidence[0]['currentDocumentPair'], rows[0]['currentDocumentPair'])
        self.assertEqual(evidence[0]['evidenceKind'], 'completed-current-gate0')
        self.assertNotIn('B', evidence[0])
        with self.assertRaisesRegex(ValueError, 'exact original'):
            self.a.project_rows(rows[:-1], read, {})

    def test_required_arguments_exact_ids_not_future_candidate_evidence(self):
        required = {'p|css|s': {'profile': 'p', 'renderer': 'css', 'scene': 's'}}
        record = dict(id='p|css|s', profile='p', renderer='css', scene='s',
                      encodedLuminance=.1, linearLuminance=.2, rgb=[.2]*3,
                      candidateSha256='a'*64, provenance={'cell': 'original'})
        out = self.a.argument_population([record], required)
        self.assertEqual(out, [record])
        self.assertEqual(out[0]['candidateSha256'], 'a'*64)
        for bad in ([], [record, record], [{**record, 'id': 'other'}]):
            with self.assertRaises(ValueError): self.a.argument_population(bad, required)
        with self.assertRaises(ValueError):
            self.a.argument_population([{**record, 'linearLuminance': .3}], required)


class BootstrapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = source(HERE/'run.py', 'synthetic_current_bootstrap')

    def test_pin_refuses_changed_bytes_and_parent_symlink(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve(); (root/'data').mkdir(); p = root/'data/value.json'; p.write_text('{}')
            pin = {'path': 'data/value.json', 'sha256': hashlib.sha256(b'{}').hexdigest()}
            self.assertEqual(self.r.checked(root, pin), p)
            p.write_text('[]')
            with self.assertRaises(ValueError): self.r.checked(root, pin)
            (root/'alias').symlink_to(root/'data', target_is_directory=True)
            with self.assertRaises(ValueError):
                self.r.checked(root, {'path': 'alias/value.json', 'sha256': hashlib.sha256(b'[]').hexdigest()})

    def test_external_root_hash_admission_precedes_any_helper_or_data_read(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()/'instrument-root.json'; root.write_text('{}')
            with self.assertRaisesRegex(ValueError, 'external'):
                self.r.admit_root(root, '0'*64, repo=Path(td).resolve())

    def test_root_cannot_omit_guard_from_prospective_source_closure(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td).resolve()
            pins = {}
            for name in ('entry.py', 'probe.py', 'config.json'):
                p = repo/name; p.write_text('{}' if name.endswith('.json') else 'pass\n')
                pins[name] = {'path': name, 'sha256': self.r.sha(p)}
            root = dict(schema='w50-completed-current-root-1', config=pins['config.json'],
                entrypoint=pins['entry.py'], probe=pins['probe.py'],
                closure={'sources': {p['path']: p['sha256'] for p in (pins['entry.py'], pins['probe.py'])}})
            path = repo/'instrument-root.json'; self.r.write_once(path, root)
            Path(str(path)+'.sha256').write_text(f'{self.r.sha(path)}  {path.name}\n')
            with self.assertRaisesRegex(ValueError, 'guard'):
                self.r.admit_root(path, self.r.sha(path), repo=repo)

    def test_write_once_preserves_existing_bytes_and_rejects_nonfinite_before_creation(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td).resolve()/'result.json'
            self.r.write_once(p, {'status': 'EVIDENCE_ONLY'})
            before = p.read_bytes()
            with self.assertRaises(FileExistsError): self.r.write_once(p, {'status': 'PASS'})
            self.assertEqual(p.read_bytes(), before)
            other = Path(td).resolve()/'bad.json'
            with self.assertRaises(ValueError): self.r.write_once(other, {'x': float('nan')})
            self.assertFalse(other.exists())


if __name__ == '__main__': unittest.main()
