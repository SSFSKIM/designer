"""Direct entrypoint and transitive-import refusal tests, with synthetic cells only."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
PYTHON = '/Users/new/vitrea-w49/py/bin/python'


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Execution(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve()
        self.audit = self.root / 'audit'
        self.audit.mkdir()
        for name in ('next_wave.py', 'closure.py', 'render.py', 'planner.py'):
            shutil.copy2(HERE / name, self.audit / name)
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        self.batch = self.root / 'batch.json'
        self.batch.write_text(json.dumps({'schema': 'w50-render-batch-1', 'phase': 'gate',
            'runs': [{'id': 'synthetic', 'profile': 'apple-macos-27.0-1x-dark-standard-glass0.5',
                      'renderer': 'webgpu', 'scenes': ['impulse__rrect-lg__rest'],
                      'sets': ['calibration'], 'candidate': {'path': 'candidate.json', 'sha256': 'a'*64}}]}))
        self.probe = self.root / 'probe.py'
        self.probe.write_text('import sys\nfrom pathlib import Path\n'
            'sys.path.insert(0, str(Path(__file__).parent / "audit"))\n'
            'import render, planner\n'
            'planner.validate_run({"id":"a", "profile":"apple-macos-27.0-1x-dark-standard-glass0.5",'
            '"renderer":"webgpu","scenes":["s"],"sets":["calibration"],'
            '"candidate":{"path":"c.json","sha256":"a"*64}}, "gate")\n')
        self.N = load(self.audit / 'next_wave.py', 'next_wave_test')

    def tearDown(self):
        self.tmp.cleanup()

    def seal(self):
        self.N.seal(self.root, self.batch, self.probe, self.audit / 'render.py',
                    self.audit / 'execution-contract.json')

    def run_renderer(self, batch=None, extra=()):
        return subprocess.run([PYTHON, '-I', '-B', str(self.audit / 'render.py'),
            str(batch or self.batch), *extra], capture_output=True, text=True)

    def test_direct_invocation_bound_before_planning(self):
        self.seal()
        good = self.run_renderer()
        self.assertEqual(good.returncode, 0, good.stderr)
        other = self.root / 'other.json'
        other.write_text(self.batch.read_text().replace('rrect-lg', 'rrect-sm'))
        bad = self.run_renderer(other)
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn('sealed batch', bad.stderr)

    def test_changed_registered_batch_refused_without_wrapper(self):
        self.seal()
        self.batch.write_text(self.batch.read_text().replace('rrect-lg', 'rrect-sm'))
        result = self.run_renderer()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('sealed batch', result.stderr)

    def test_requested_cell_outside_batch_refused(self):
        self.seal()
        result = self.run_renderer(extra=('--scene', 'photo__rrect-lg__rest'))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('unrecognized arguments', result.stderr)

    def test_changed_bootstrap_helpers_refused_before_their_code_executes(self):
        self.seal()
        for name in ('next_wave.py', 'closure.py'):
            path = self.audit / name
            original = path.read_bytes()
            marker = self.root / f'{name}.executed'
            path.write_bytes(original + f'\nPath({str(marker)!r}).write_text("executed")\n'.encode())
            result = self.run_renderer()
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(marker.exists(), result.stderr)
            path.write_bytes(original)

    def test_changed_transitive_planner_refused(self):
        self.seal()
        with (self.audit / 'planner.py').open('a') as f:
            f.write('\nraise RuntimeError("CHANGED CODE EXECUTED")\n')
        result = self.run_renderer()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Changed closure source', result.stderr)
        self.assertNotIn('RuntimeError: CHANGED CODE EXECUTED', result.stderr)

    def test_new_late_measurement_import_refused_in_process(self):
        renderer = self.audit / 'render.py'
        renderer.write_text(renderer.read_text().replace(
            '    batch = json.loads(registered.read_text())',
            '    late = importlib.util.spec_from_file_location("late", HERE / "late.py")\n'
            '    late.loader.exec_module(importlib.util.module_from_spec(late))\n'
            '    batch = json.loads(registered.read_text())'))
        (self.audit / 'late.py').write_text('raise RuntimeError("UNSEALED CODE EXECUTED")\n')
        self.seal()
        result = self.run_renderer()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('unsealed executed import', result.stderr)
        self.assertNotIn('RuntimeError: UNSEALED CODE EXECUTED', result.stderr)

    def test_execute_requires_root_seal_and_prefit_evidence(self):
        self.seal()
        result = self.run_renderer(extra=('--execute', '--out', str(self.root / 'out')))
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root / 'out').exists())


if __name__ == '__main__':
    unittest.main()
