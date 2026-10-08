"""Source-only guarded reference entrypoint tests in fresh synthetic repositories."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import py_compile
import shutil
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parents[1]
G0 = RESULTS/'2026-10-08-w50-g0-declaration'
PYTHON = '/Users/new/vitrea-w49/py/bin/python'
ONE = 'bb185d87d850d12fd3b0019cbe9d0db65c541b73c14690035192131e30a00b86'
TWO = 'bdd1050ed6ad9671676b0551c33a685e3093a5548652b04662fb81d4a29adb85'


def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n'); return p


def load(name, p):
    s = importlib.util.spec_from_file_location(name, p)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m


class RunTests(unittest.TestCase):
    def fixture(self, directory):
        repo = (Path(directory)/'repo').resolve()
        results = repo/'packages/calibration/results'
        home = results/'2026-10-08-w50-g1-fit/references-r2'; home.mkdir(parents=True)
        for name in ('run.py', 'probe.py', 'canonical.py', 'statistics.py', 'completion.py'):
            shutil.copyfile(HERE/name, home/name)
        for rel in ('2026-10-08-w50-g0-declaration/audit/next_wave.py',
                    '2026-10-08-w50-g0-declaration/audit/closure.py',
                    '2026-10-03-w44-g0-declaration/port/interior.py',
                    '2026-10-01-w43-g0-declaration/bed/sitting/w43_archive.py',
                    '2026-10-08-w50-g1-fit/native/statistics.py',
                    '2026-10-08-w50-g1-fit/execution/dispatch.py',
                    '2026-10-08-w50-g1-fit/execution/admission.py'):
            p = results/rel; p.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(RESULTS/rel, p)
        f = load('reference_tree_synth', HERE/'test_canonical.py')
        config, scenes, published, _ = f.trees(Path(directory)/'sources')
        profile = f.profile(1, '0.5'); scene = 'text__r__rest'
        native = Path(config['fixtureRoot'])/profile/(scene+'.png')
        row = {'profile': profile, 'renderer': 'webgpu', 'scene': scene, 'stratum': 'T',
            'statistic': 'T1-low', 'role': 'gate', 'nativeEvidence': f.pin(native),
            'currentEvidence': f.pin(native), 'native': None, 'current': None, 'B': None,
            'fidelity': None, 'historical': []}
        # The complete inventory includes an unsupported owner row and a NEW W50 blind row.
        inventory = {'schema': 'w50-reference-inventory-1', 'cells': [row,
            {**row, 'statistic': 'owner-contracts'}, {**row, 'role': 'blind', 'statistic': 'deep8-channel-median'}]}
        declaration = results/G0.name
        refs = write(declaration/'references.json', inventory)
        pin = lambda p: {'path': str(p.relative_to(repo)), 'sha256': sha(p)}
        common = [pin(refs), *[pin(declaration/'audit'/n) for n in ('next_wave.py', 'closure.py')]]
        one = write(declaration/'declaration.json', {'schema': 'w50-declaration-1',
            'references': 'references.json', 'sources': common})
        two = write(declaration/'fit-declaration.json', {'schema': 'w50-fit-declaration-1',
            'references': 'references.json', 'sources': common, 'partOneSha256': sha(one)})
        for p in (one, two): p.with_suffix('.sha256').write_text(f'{sha(p)}  {p.name}\n')
        entry = home/'run.py'; entry.write_text(entry.read_text().replace(ONE, sha(one)).replace(TWO, sha(two)))
        config_path = write(home/'read-config.json', {'schema': 'w50-canonical-reference-config-1', **config})
        batch = write(home/'read-batch.json', {'schema': 'w50-canonical-reference-batch-1',
            'inputs': {'partOne': pin(one), 'partTwo': pin(two), 'inventory': pin(refs), 'config': pin(config_path)},
            'selectedKeys': [[row[k] for k in ('profile', 'renderer', 'scene', 'statistic')]]})
        return repo, home, batch, config_path

    def command(self, home, *args):
        return subprocess.run([PYTHON, '-I', '-B', str(home/'run.py'), *map(str, args)],
                              capture_output=True, text=True)

    def seal(self, home, batch):
        result = self.command(home, 'seal', batch)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)['instrumentRootSha256']

    def test_guarded_fixed_subset_read_retains_original_rows_and_writes_once(self):
        with tempfile.TemporaryDirectory() as td:
            repo, home, batch, _ = self.fixture(td)
            root_hash = self.seal(home, batch)
            contract = json.loads((home/'execution-contract.json').read_bytes())
            for p in (home/'run.py', home/'probe.py', home/'canonical.py', home/'statistics.py',
                      home/'completion.py'):
                self.assertIn(str(p.relative_to(repo)), contract['closure']['sources'])
            self.assertNotIn(str((home.parent/'execution/dispatch.py').relative_to(repo)),
                             contract['closure']['sources'])
            output = Path(td)/'reference-evidence.json'
            result = self.command(home, batch, '--root-sha256', root_hash, '--out', output)
            self.assertEqual(result.returncode, 0, result.stderr)
            doc = json.loads(output.read_bytes())
            self.assertEqual(doc['purpose'], 'REFERENCE_EVIDENCE_ONLY_NOT_COEFFICIENT_INPUT')
            self.assertEqual(len(doc['partitions']['gate']), 1)
            self.assertEqual(doc['instrumentRootSha256'], root_hash)
            self.assertEqual(doc['inputs'], json.loads(batch.read_bytes())['inputs'])
            self.assertEqual(doc['partitions']['historical-prediction-check'], [])
            second = self.command(home, batch, '--root-sha256', root_hash, '--out', output)
            self.assertNotEqual(second.returncode, 0)
            self.assertIn('exists', second.stderr.lower())

    def test_prospective_seal_probe_never_reads_real_metadata_or_source_pixel_trees(self):
        with tempfile.TemporaryDirectory() as td:
            _, home, batch, config_path = self.fixture(td)
            config = json.loads(config_path.read_bytes())
            shutil.rmtree(config['w29']['root']); shutil.rmtree(config['w43']['root'])
            shutil.rmtree(config['fixtureRoot'])
            self.seal(home, batch)

    def test_no_caller_selected_row_config_or_blind_subset_can_be_sealed(self):
        for change in ('omit', 'blind', 'config'):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as td:
                _, home, batch, _ = self.fixture(td)
                doc = json.loads(batch.read_bytes())
                if change == 'omit': doc['selectedKeys'] = []
                elif change == 'blind': doc['selectedKeys'][0][-1] = 'deep8-channel-median'
                else: doc['inputs']['config']['path'] = str(Path(doc['inputs']['config']['path']).with_name('other.json'))
                write(batch, doc)
                result = self.command(home, 'seal', batch)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((home/'execution-contract.json').exists())

    def test_swapped_batch_or_changed_source_refuses_before_marker_executes(self):
        for change in ('batch', 'helper'):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as td:
                _, home, batch, _ = self.fixture(td); root_hash = self.seal(home, batch)
                marker = Path(td)/'executed'
                if change == 'batch': supplied = write(home/'other-batch.json', {})
                else:
                    supplied = batch
                    (home/'canonical.py').write_text(f'from pathlib import Path\nPath({str(marker)!r}).write_text("BAD")\n')
                result = self.command(home, supplied, '--root-sha256', root_hash, '--out', Path(td)/'never.json')
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(marker.exists()); self.assertFalse((Path(td)/'never.json').exists())

    def test_reference_seal_and_result_root_cannot_be_replaced_by_new_sidecar(self):
        with tempfile.TemporaryDirectory() as td:
            _, home, batch, _ = self.fixture(td); root_hash = self.seal(home, batch)
            second = self.command(home, 'seal', batch)
            self.assertNotEqual(second.returncode, 0)
            path = home/'instrument-root.json'; value = json.loads(path.read_bytes())
            value['replacement'] = True; write(path, value)
            Path(str(path)+'.sha256').write_text(f'{sha(path)}  {path.name}\n')
            result = self.command(home, batch, '--root-sha256', root_hash, '--out', Path(td)/'never.json')
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((Path(td)/'never.json').exists())

    def test_permanent_guard_refuses_new_actual_process_import_before_marker_execution(self):
        with tempfile.TemporaryDirectory() as td:
            _, home, batch, _ = self.fixture(td)
            marker = Path(td)/'late-executed'
            (home/'late.py').write_text(f'from pathlib import Path\nPath({str(marker)!r}).write_text("BAD")\n')
            path = home/'canonical.py'
            path.write_text(path.read_text()+'''
_original_reference_read = read_references

def read_references(*args, **kwargs):
    import importlib.util
    spec = importlib.util.spec_from_file_location('late_reference_source', HERE/'late.py')
    value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value)
    return _original_reference_read(*args, **kwargs)
''')
            root_hash = self.seal(home, batch)
            result = self.command(home, batch, '--root-sha256', root_hash, '--out', Path(td)/'never.json')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('unsealed', result.stderr.lower()); self.assertFalse(marker.exists())

    def test_metadata_command_never_opens_source_png_or_cell_record_statistics(self):
        with tempfile.TemporaryDirectory() as td:
            _, home, batch, config_path = self.fixture(td)
            config = json.loads(config_path.read_bytes())
            for base in (config['w29']['root'], config['w43']['root'], config['fixtureRoot']):
                for p in Path(base).rglob('*'):
                    if p.suffix == '.png' or p.name.endswith('.cell.json.gz'):
                        p.unlink()
            result = self.command(home, 'metadata', batch)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report['pixels'], 'NONE: metadata only, no PNG/cell statistic reads')
            self.assertEqual(report['issues'], [])
            self.assertFalse((home/'execution-contract.json').exists())

    def test_valid_stale_pyc_never_runs_in_probe_or_actual_reference_process(self):
        with tempfile.TemporaryDirectory() as td:
            _, home, batch, _ = self.fixture(td)
            path = home/'canonical.py'; safe = path.read_bytes(); stamp = path.stat().st_mtime
            marker = Path(td)/'bytecode'
            evil = f'from pathlib import Path\nPath({str(marker)!r}).write_text("BAD")\n'.encode()
            path.write_bytes(evil+b' '*(len(safe)-len(evil))); os.utime(path, (stamp, stamp))
            py_compile.compile(str(path), doraise=True); path.write_bytes(safe); os.utime(path, (stamp, stamp))
            load('unsafe_source_fixture', path); self.assertTrue(marker.exists()); marker.unlink()
            root_hash = self.seal(home, batch)
            result = self.command(home, batch, '--root-sha256', root_hash, '--out', Path(td)/'safe.json')
            self.assertEqual(result.returncode, 0, result.stderr); self.assertFalse(marker.exists())

    def test_unmeasured_reference_writes_honest_receipt_and_nonzero_exit(self):
        with tempfile.TemporaryDirectory() as td:
            _, home, batch, config_path = self.fixture(td)
            root_hash = self.seal(home, batch)
            config = json.loads(config_path.read_bytes())
            (Path(config['w29']['root'])/'standard-active-1x/run-1/attest.read').write_text('changed')
            out = Path(td)/'unmeasured.json'
            result = self.command(home, batch, '--root-sha256', root_hash, '--out', out)
            self.assertEqual(result.returncode, 1, result.stderr)
            report = json.loads(out.read_bytes())
            self.assertEqual(report['partitions']['gate'][0]['status'], 'UNMEASURED')


if __name__ == '__main__': unittest.main()
