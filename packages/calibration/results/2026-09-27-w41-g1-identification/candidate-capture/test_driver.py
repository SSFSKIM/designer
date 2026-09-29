"""No browser/native reads: test the real orchestration with controlled process argv."""
import importlib.util
from pathlib import Path
import tempfile
import sys
from types import ModuleType
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('candidate_driver', HERE / 'driver.py')
d = importlib.util.module_from_spec(spec)


class DriverTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec.loader.exec_module(d)

    def test_x6_refusal_is_resumable_but_launched_failure_never_reexecutes(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            with patch.object(d.base.x6, 'observe', return_value={'verdict': {'passes': False}}):
                with self.assertRaises(PermissionError):
                    d.launch(out, ['never-run'], {}, lambda: None)
            self.assertFalse((out / 'started.json').exists())
            with patch.object(d.base.x6, 'observe', return_value={'verdict': {'passes': True}}):
                with self.assertRaises(d.subprocess.CalledProcessError):
                    d.launch(out, ['/usr/bin/false'], {}, lambda: None)
                with self.assertRaisesRegex(ValueError, 'launched'):
                    d.launch(out, ['/usr/bin/true'], {}, lambda: None)
            self.assertTrue((out / 'failure.json').is_file())

    def test_pins_reject_changed_file_and_added_runtime_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / 'a').write_text('one')
            pins = {'a': d.runner.sha(root / 'a')}
            d.check_hashes(root, pins)
            (root / 'a').write_text('two')
            with self.assertRaisesRegex(ValueError, 'changed'):
                d.check_hashes(root, pins)

    def test_source_frontier_tracks_imports_not_unrelated_instruments(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            instrument = d.runner.INSTRUMENT_ROOTS[-1]
            driver = root / instrument / 'candidate-capture/driver.py'
            helper = root / instrument / 'helper.py'
            unrelated = root / instrument / 'stroke/fit.py'
            runtime = root / d.runner.SOURCE_ROOTS[0] / 'runtime.ts'
            config = root / 'packages/calibration/vite.config.mjs'
            for path in (driver, helper, unrelated, runtime, config):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('# initial')
            module = ModuleType('unregistered_helper')
            module.__file__ = str(helper)
            namespace = {'__file__': str(driver), 'helper': module}
            sources = d.source_inventory(root, namespace)
            self.assertEqual(set(sources), {str(p.relative_to(root))
                                           for p in (driver, helper, runtime, config)})
            pins = {name: d.runner.sha(root / name) for name in sources}
            unrelated.write_text('# concurrently edited')
            (unrelated.parent / 'new.py').write_text('# unrelated addition')
            self.assertEqual(d.source_inventory(root, namespace), sources)
            d.check_hashes(root, pins)
            helper.write_text('# changed imported helper')
            with self.assertRaisesRegex(ValueError, 'changed'):
                d.check_hashes(root, pins)
            added = root / instrument / 'new_helper.py'
            added.write_text('VALUE = 1')
            imported = ModuleType('new_helper'); imported.__file__ = str(added)
            module.imported = imported
            with self.assertRaisesRegex(ValueError, 'coverage mismatch'):
                d.runner.coverage(d.source_inventory(root, namespace), sources, 'sources')
            del module.imported
            (runtime.parent / 'new.ts').write_text('// new runtime source')
            with self.assertRaisesRegex(ValueError, 'coverage mismatch'):
                d.runner.coverage(d.source_inventory(root, namespace), sources, 'sources')

    def test_real_import_frontier_includes_unregistered_boundary_not_scorer(self):
        sources = d.source_inventory(d.ROOT)
        for module in (d.base, d.runner, d.base.runner, d.runner.boundary,
                       d.base.m, d.base.rendered, d.base.x6, d.base.m.readers):
            self.assertIn(str(Path(module.__file__).relative_to(d.ROOT)), sources)
        self.assertIn(str((HERE / 'driver.py').relative_to(d.ROOT)), sources)
        self.assertNotIn(str((HERE / 'test_driver.py').relative_to(d.ROOT)), sources)
        self.assertNotIn(str((d.G1 / 'candidate-e3/prepare.py').relative_to(d.ROOT)), sources)

    def test_full_verification_precedes_fresh_x6_and_controlled_argv(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            order = out / 'order.txt'
            def mark(text):
                with order.open('a') as f: f.write(text + '\n')
            def verify(): mark('verify')
            def observe():
                mark('x6')
                return {'verdict': {'passes': True}}
            command = [sys.executable, '-c',
                       "import pathlib; p=pathlib.Path(__import__('sys').argv[1]); "
                       "assert (p.parent/'started.json').exists(); "
                       "p.open('a').write('launch\\n')", str(order)]
            with patch.object(d.base.x6, 'observe', side_effect=observe):
                d.launch(out, command, {}, verify)
            self.assertEqual(order.read_text().splitlines(), ['verify', 'x6', 'launch'])
            self.assertEqual(d.runner.load(out / 'started.json')['argv'], command)

    def test_identity_checks_every_unclaimed_png_and_projection(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, text in [('a.png', 'one'), ('b.png', 'one'), ('a.json', '{}'), ('b.json', '{}')]:
                (root / name).write_text(text)
            a = {'png': 'a.png', 'projection': 'a.json'}
            b = {'png': 'b.png', 'projection': 'b.json'}
            self.assertEqual(d.compare_identity(root, {'x': a}, {'x': b}, ['x'])['failures'], [])
            (root / 'b.json').write_text('{"different":1}')
            result = d.compare_identity(root, {'x': a}, {'x': b}, ['x'])
            self.assertEqual(result['failures'], ['x'])
            self.assertTrue(result['cells']['x']['pngEqual'])
            self.assertFalse(result['cells']['x']['projectionEqual'])

    def test_batches_preserve_all_cells_calval_before_blind(self):
        cells = ['p/a', 'q/b', 'p/h', 'q/h']
        roles = {'a': 'calibration', 'b': 'validation', 'h': 'holdout'}
        batches = d.batches(cells, roles)
        self.assertEqual([(kind, profile, ids) for kind, profile, ids in batches], [
            ('calval', 'p', ['a']), ('calval', 'q', ['b']),
            ('blind', 'p', ['h']), ('blind', 'q', ['h'])])

    def test_snapshots_are_content_addressed_and_collision_refuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); source = root / 'raw.json'; source.write_text('{}')
            path = d.snapshot(source, root / 'payloads')
            self.assertEqual(path.stem, d.runner.sha(source))
            path.write_text('corrupt')
            with self.assertRaisesRegex(ValueError, 'collision'):
                d.snapshot(source, root / 'payloads')


if __name__ == '__main__': unittest.main()
