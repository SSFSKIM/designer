#!/Users/new/vitrea-w49/py/bin/python -I
"""CPU-only mutations of completed identity records; never render or read withheld pixels."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
SCRATCH = Path('/Users/new/vitrea-w49/b-g0-scratch')


def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


A = load('audit')
N = load('next_wave')


def edit_json(path, mutation):
    value = json.loads(path.read_text())
    mutation(value)
    path.write_text(json.dumps(value, indent=2) + '\n')


class Records(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = A.contract(ROOT)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name).resolve()
        self.candidates = self.base / 'candidates'
        shutil.copytree(SCRATCH / 'candidates', self.candidates)
        self.renders = self.base / 'renders'
        self.renders.mkdir()
        shutil.copy2(SCRATCH / 'renders/plan.json', self.renders / 'plan.json')
        shutil.copytree(SCRATCH / 'renders/identity', self.renders / 'identity')
        # Relocation changes path-bearing records, not the matrix's candidate content witness.
        old = str(SCRATCH / 'candidates')
        new = str(self.candidates)
        for folder in self.renders.glob('*/*'):
            for name in ('request.json', 'matrix.json'):
                path = folder / name
                path.write_text(path.read_text().replace(old, new).replace(
                    str(SCRATCH / 'renders'), str(self.renders)))
            for meta in folder.glob('web-captures/*/*/*.json'):
                meta.write_text(meta.read_text().replace(old, new))
            self.rewitness(folder)

    def tearDown(self):
        self.tmp.cleanup()

    def rewitness(self, folder):
        def mutate(value):
            value['matrixSha256'] = A.sha(folder / 'matrix.json')
            for path in value['captureEvidence']:
                value['captureEvidence'][path] = A.sha(folder / path)
        edit_json(folder / 'complete.json', mutate)

    def audit(self, partial=True):
        return A.audit_records(self.contract, self.candidates, self.renders, partial=partial)

    def test_completed_real_point_is_incomplete_not_pass_for_whole_batch(self):
        result = self.audit()
        self.assertEqual(result['status'], 'INCOMPLETE')
        self.assertEqual(result['completedRuns'], 2)
        self.assertEqual(result['measuredCells'], 132)
        self.assertEqual(len(result['missingRuns']), 52)
        self.assertEqual(len(result['runs']), 2)

    def test_final_audit_refuses_missing_runs(self):
        self.assertEqual(self.audit(partial=False)['status'], 'FAIL')

    def test_cli_partial_and_final_refuse_to_bless_completed_subset(self):
        for partial, status, exit_code in ((True, 'INCOMPLETE', 2), (False, 'FAIL', 1)):
            output = self.base / f'{status}.json'
            argv = [str(A.K.PYTHON), '-I', '-B', str(HERE / 'audit.py'),
                    '--candidates', str(self.candidates), '--renders', str(self.renders),
                    '--out', str(output)] + (['--partial'] if partial else [])
            result = subprocess.run(argv, capture_output=True, text=True)
            self.assertEqual(result.returncode, exit_code, result.stderr + result.stdout)
            report = json.loads(output.read_text())
            self.assertEqual(report['status'], status)
            self.assertEqual(report['completedRuns'], 2)
            self.assertEqual(report['ladderVerdict'], 'NOT_SELECTED')
            self.assertIn('node', report['runtimeCandidates']['environment'])
            self.assertEqual(report['measurementClosure']['pixels'], 'NONE: synthetic instrument exercise')

    def test_supplied_domain_cannot_replace_registered_batch(self):
        path = self.candidates / 'batch.json'
        edit_json(path, lambda v: v['points'][1]['overrides']['active.dark'].update(
            backdropCaptureScale=0.375))
        edit_json(self.candidates / 'build.json', lambda v: v.update(batchSha256=A.sha(path)))
        with self.assertRaisesRegex(ValueError, 'registered batch'):
            self.audit()

    def test_changed_candidate_rejected_even_with_updated_content_witness(self):
        folder = self.candidates / 'identity'
        path = folder / 'active.dark.json'
        edit_json(path, lambda v: v['patch'].update(tintAlpha=0.69))
        edit_json(folder / 'candidate.json', lambda v: v['endpoints']['active.dark'].update(
            sha256=A.sha(path)))
        edit_json(self.candidates / 'build.json', lambda v: v['points'][0].update(
            candidateSha256=A.sha(folder / 'candidate.json')))
        with self.assertRaisesRegex(ValueError, 'sealed point'):
            self.audit()

    def test_build_point_cannot_be_changed(self):
        edit_json(self.candidates / 'identity/point.json', lambda v: v.update(pose='rest'))
        with self.assertRaisesRegex(ValueError, 'point'):
            self.audit()

    def test_extra_root_plan_cannot_hide_behind_inclusion_check(self):
        edit_json(self.renders / 'plan.json', lambda v: v['plans'].append(v['plans'][0]))
        with self.assertRaisesRegex(ValueError, 'root plan'):
            self.audit()

    def test_extra_run_is_rejected(self):
        shutil.copytree(self.renders / 'identity/1x', self.renders / 'identity/3x')
        with self.assertRaisesRegex(ValueError, 'run membership'):
            self.audit()

    def test_missing_completed_cell_is_rejected_even_when_matrix_rewitnessed(self):
        folder = self.renders / 'identity/1x'
        edit_json(folder / 'matrix.json', lambda v: v['cells'].pop())
        self.rewitness(folder)
        with self.assertRaisesRegex(ValueError, 'membership'):
            self.audit()

    def test_extra_completed_cell_is_rejected_even_when_matrix_rewitnessed(self):
        folder = self.renders / 'identity/1x'
        edit_json(folder / 'matrix.json', lambda v: v['cells'].append(v['cells'][0]))
        self.rewitness(folder)
        with self.assertRaisesRegex(ValueError, 'membership'):
            self.audit()

    def test_withheld_scene_request_is_rejected_before_any_pixel_read(self):
        folder = self.renders / 'identity/1x'
        edit_json(folder / 'request.json', lambda v: v['scenes'].append('photo__rrect-lg__inactive'))
        with self.assertRaisesRegex(ValueError, 'request'):
            self.audit()

    def test_actual_launch_argv_cannot_request_a_different_scene(self):
        folder = self.renders / 'identity/1x'
        def change(value):
            at = value['argv'].index('--scene') + 1
            value['argv'][at] += ',photo__rrect-lg__inactive'
        edit_json(folder / 'request.json', change)
        with self.assertRaisesRegex(ValueError, 'argv'):
            self.audit()

    def test_extra_capture_witness_is_rejected_before_file_read(self):
        folder = self.renders / 'identity/1x'
        edit_json(folder / 'complete.json', lambda v: v['captureEvidence'].update(
            {'web-captures/withheld.png': '0' * 64}))
        with self.assertRaisesRegex(ValueError, 'capture membership'):
            self.audit()

    def test_changed_capture_is_rejected(self):
        path = next((self.renders / 'identity/1x').glob('web-captures/*/*/*__webgpu.png'))
        path.write_bytes(path.read_bytes() + b'changed')
        with self.assertRaisesRegex(ValueError, 'capture bytes'):
            self.audit()


class ImportClosure(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / 'instrument.py').write_text('def measure():\n    return 7\n')
        (self.root / 'probe.py').write_text(
            'import sys\nfrom pathlib import Path\n'
            'sys.path.insert(0, str(Path(__file__).parent))\n'
            'import instrument, renderer\nassert instrument.measure() == 7\n')
        (self.root / 'renderer.py').write_text(
            'import pathlib, sys\n'
            'if __name__ == "__main__":\n'
            '    pathlib.Path(sys.argv[2]).write_bytes(pathlib.Path(sys.argv[1]).read_bytes())\n')
        (self.root / 'batch.json').write_text('{"points":[{"label":"a"}]}\n')
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        subprocess.run(['git', '-C', str(self.root), 'add', '.'], check=True)
        subprocess.run(['git', '-C', str(self.root), '-c', 'user.name=Test', '-c',
                        'user.email=test@example.invalid', 'commit', '-qm', 'fixture'], check=True)
        self.commit = subprocess.check_output(['git', '-C', str(self.root), 'rev-parse', 'HEAD'], text=True).strip()

    def tearDown(self):
        self.tmp.cleanup()

    def test_changed_transitive_instrument_fails_against_git_seal_before_execution(self):
        before = A.discover(self.root, self.root / 'probe.py', commit=self.commit)
        self.assertIn('instrument.py', before['sources'])
        (self.root / 'instrument.py').write_text('def measure():\n    return 8\n')
        with self.assertRaisesRegex(ValueError, 'seal bytes'):
            A.discover(self.root, self.root / 'probe.py', commit=self.commit)

    def test_renderer_rejects_runtime_import_not_exercised_in_sealed_probe(self):
        tools = self.root / 'tools'
        tools.mkdir()
        for name in ('renderer_template.py', 'next_wave.py', 'closure.py'):
            shutil.copy2(HERE / name, tools / name)
        renderer = tools / 'renderer_template.py'
        renderer.write_text(renderer.read_text().replace(
            '    batch = json.loads(registered.read_text())',
            '    late = importlib.util.spec_from_file_location("later", HERE / "later.py")\n'
            '    late.loader.exec_module(importlib.util.module_from_spec(late))\n'
            '    batch = json.loads(registered.read_text())'))
        (tools / 'later.py').write_text('raise RuntimeError("UNSEALED CODE EXECUTED")\n')
        probe = self.root / 'probe-template.py'
        probe.write_text('import sys\nfrom pathlib import Path\n'
                         'sys.path.insert(0, str(Path(__file__).parent / "tools"))\n'
                         'import renderer_template\n')
        spec = importlib.util.spec_from_file_location('copied_next_wave', tools / 'next_wave.py')
        copied = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(copied)
        copied.seal(self.root, self.root / 'batch.json', probe, renderer, tools / 'execution-contract.json')
        result = subprocess.run([str(A.K.PYTHON), '-I', '-B', str(renderer), str(self.root / 'batch.json')],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('unsealed executed import', result.stderr)
        self.assertNotIn('RuntimeError: UNSEALED CODE EXECUTED', result.stderr)

    def test_renderer_template_binds_even_when_wrapper_is_bypassed(self):
        tools = self.root / 'tools'
        tools.mkdir()
        for name in ('renderer_template.py', 'next_wave.py', 'closure.py'):
            shutil.copy2(HERE / name, tools / name)
        probe = self.root / 'probe-template.py'
        probe.write_text('import sys\nfrom pathlib import Path\n'
                         'sys.path.insert(0, str(Path(__file__).parent / "tools"))\n'
                         'import renderer_template\n')
        spec = importlib.util.spec_from_file_location('copied_next_wave', tools / 'next_wave.py')
        copied = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(copied)
        copied.seal(self.root, self.root / 'batch.json', probe, tools / 'renderer_template.py',
                    tools / 'execution-contract.json')
        command = [str(A.K.PYTHON), '-I', '-B', str(tools / 'renderer_template.py')]
        good = subprocess.run(command + [str(self.root / 'batch.json')], capture_output=True, text=True)
        self.assertEqual(good.returncode, 0, good.stderr)
        self.assertEqual(json.loads(good.stdout)['points'], [{'label': 'a'}])
        (self.root / 'other.json').write_text('{"points":[{"label":"b"}]}\n')
        bad = subprocess.run(command + [str(self.root / 'other.json')], capture_output=True, text=True)
        self.assertNotEqual(bad.returncode, 0)
        self.assertIn('sealed batch', bad.stderr)

    def test_next_wave_cli_passes_bound_batch_to_renderer(self):
        contract = self.root / 'cli-contract.json'
        common = ['--root', str(self.root), '--batch', str(self.root / 'batch.json'),
                  '--contract', str(contract)]
        script = [str(A.K.PYTHON), '-I', '-B', str(HERE / 'next_wave.py')]
        sealed = subprocess.run(script + ['seal', *common, '--probe', str(self.root / 'probe.py'),
                                         '--renderer', str(self.root / 'renderer.py')],
                                capture_output=True, text=True)
        self.assertEqual(sealed.returncode, 0, sealed.stderr)
        observed = self.root / 'cli-observed.json'
        rendered = subprocess.run(script + ['render', *common, '--', str(observed)],
                                  capture_output=True, text=True)
        self.assertEqual(rendered.returncode, 0, rendered.stderr)
        self.assertEqual(observed.read_bytes(), (self.root / 'batch.json').read_bytes())

    def test_next_wave_seals_imports_and_renderer_binds_batch(self):
        path = self.root / 'next.json'
        N.seal(self.root, self.root / 'batch.json', self.root / 'probe.py',
               self.root / 'renderer.py', path)
        result = self.root / 'observed.json'
        N.render(path, self.root, self.root / 'batch.json', [str(result)])
        self.assertEqual(result.read_bytes(), (self.root / 'batch.json').read_bytes())
        (self.root / 'other.json').write_text('{"points":[{"label":"b"}]}\n')
        with self.assertRaisesRegex(ValueError, 'sealed batch'):
            N.render(path, self.root, self.root / 'other.json', [str(result)])
        (self.root / 'instrument.py').write_text('def measure():\n    return 8\n')
        with self.assertRaisesRegex(ValueError, 'closure'):
            N.render(path, self.root, self.root / 'batch.json', [str(result)])


if __name__ == '__main__':
    unittest.main()
