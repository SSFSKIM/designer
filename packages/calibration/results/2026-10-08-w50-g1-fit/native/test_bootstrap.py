"""Prospective native bootstrap tests in disposable synthetic repositories/role exports only."""
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
PART_ONE = 'bb185d87d850d12fd3b0019cbe9d0db65c541b73c14690035192131e30a00b86'
PART_TWO = 'bdd1050ed6ad9671676b0551c33a685e3093a5548652b04662fb81d4a29adb85'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def encoded(doc):
    return (json.dumps(doc, indent=2, allow_nan=False)+'\n').encode()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class BootstrapTests(unittest.TestCase):
    def fixture(self, directory):
        """Copy authored code, never data/captures, into a fresh fake repository."""
        root = (Path(directory)/'repo').resolve()
        results = root/'packages/calibration/results'
        native = results/'2026-10-08-w50-g1-fit/native'; native.mkdir(parents=True)
        declaration = results/G0.name
        (declaration/'audit').mkdir(parents=True); (declaration/'bed').mkdir()
        for name in ('next_wave.py', 'closure.py'):
            shutil.copyfile(G0/'audit'/name, declaration/'audit'/name)
        for name in ('run.py', 'probe.py', 'reader.py', 'statistics.py'):
            shutil.copyfile(HERE/name, native/name)
        port = results/'2026-10-03-w44-g0-declaration/port/interior.py'
        port.parent.mkdir(parents=True); shutil.copyfile(RESULTS/port.relative_to(results), port)
        fixture = load('w50_synthetic_role_tree', HERE/'test_reader.py')
        manifest, scenes = fixture.bed()
        (declaration/'bed/manifest.json').write_bytes(encoded(manifest))
        (declaration/'bed/scenes-w50.json').write_bytes(encoded(scenes))
        rel = lambda path: str(path.relative_to(root))
        pin = lambda path: {'path': rel(path), 'sha256': sha(path)}
        pins = [pin(p) for p in (declaration/'audit/next_wave.py', declaration/'audit/closure.py',
                                declaration/'bed/manifest.json', declaration/'bed/scenes-w50.json')]
        part1 = declaration/'declaration.json'
        part1.write_bytes(encoded({'schema': 'w50-declaration-1', 'sources': pins}))
        part2 = declaration/'fit-declaration.json'
        part2.write_bytes(encoded({'schema': 'w50-fit-declaration-1', 'sources': pins,
                                  'partOneSha256': sha(part1)}))
        for p in (part1, part2):
            p.with_suffix('.sha256').write_text(f'{sha(p)}  {p.name}\n')
        # Synthetic reviewed entrypoint binds synthetic declarations, without changing live code.
        entry = native/'run.py'
        entry.write_text(entry.read_text().replace(PART_ONE, sha(part1)).replace(PART_TWO, sha(part2)))
        exports = []
        for role in ('calibration', 'validation'):
            export = Path(directory)/('synthetic-'+role); export.mkdir()
            index, rows = fixture.tree(export, role, manifest, scenes)
            for row in rows:
                row['declarationSha256'] = sha(part1)
            index = fixture.reseal(export, rows)
            exports.append({'role': role, 'root': str(export), 'indexSha256': index})
        pack = results/'2026-10-08-w50-g1-sitting/pack.json'
        pack.parent.mkdir()
        pack.write_bytes(encoded({'declarationSha256': sha(part1),
                                 'exportIndexSha256': {e['role']: e['indexSha256'] for e in exports}}))
        inputs = {'pack': pin(pack),
                  'declaration': pin(part1), 'declarationSidecar': pin(part1.with_suffix('.sha256')),
                  'fitDeclaration': pin(part2), 'fitDeclarationSidecar': pin(part2.with_suffix('.sha256')),
                  'manifest': pin(declaration/'bed/manifest.json'),
                  'scenes': pin(declaration/'bed/scenes-w50.json')}
        batch = native/'read-batch.json'
        batch.write_bytes(encoded({'schema': 'w50-native-read-batch-1', 'inputs': inputs, 'exports': exports}))
        return root, native, batch

    def command(self, native, *arguments):
        return subprocess.run([PYTHON, '-I', '-B', str(native/'run.py'), *map(str, arguments)],
                              capture_output=True, text=True)

    def seal(self, native, batch):
        result = self.command(native, 'seal', batch)
        self.assertEqual(result.returncode, 0, result.stderr)
        doc = json.loads(result.stdout)
        return doc['instrumentRootSha256']

    def test_synthetic_probe_collects_dynamic_modules_and_role_read_writes_fresh_provenance(self):
        with tempfile.TemporaryDirectory() as td:
            root, native, batch = self.fixture(td)
            instrument = self.seal(native, batch)
            contract = json.loads((native/'execution-contract.json').read_bytes())
            sources = contract['closure']['sources']
            for path in (native/'run.py', native/'probe.py', native/'reader.py', native/'statistics.py',
                         root/'packages/calibration/results/2026-10-03-w44-g0-declaration/port/interior.py'):
                self.assertIn(str(path.relative_to(root)), sources)
            out = Path(td)/'report.json'
            result = self.command(native, batch, '--root-sha256', instrument, '--out', out)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(out.read_bytes())
            self.assertTrue(report['ready'])
            self.assertEqual([r['role'] for r in report['roles']], ['calibration', 'validation'])
            self.assertEqual(report['instrumentRootSha256'], instrument)
            self.assertEqual(report['batch']['sha256'], sha(batch))
            self.assertEqual(report['inputs'], json.loads(batch.read_bytes())['inputs'])
            self.assertTrue(all(r['cells'] for r in report['roles']))
            repeat = self.command(native, batch, '--root-sha256', instrument, '--out', out)
            self.assertNotEqual(repeat.returncode, 0)
            self.assertIn('exists', repeat.stderr.lower())

    def test_source_sealing_and_probe_do_not_open_registered_exports(self):
        with tempfile.TemporaryDirectory() as td:
            _, native, batch = self.fixture(td)
            for export in json.loads(batch.read_bytes())['exports']:
                shutil.rmtree(export['root'])
            self.seal(native, batch)
            self.assertTrue((native/'execution-contract.json').is_file())

    def test_repeat_stop_is_written_with_full_readings_and_nonzero_exit(self):
        with tempfile.TemporaryDirectory() as td:
            _, native, batch = self.fixture(td)
            fixture = load('w50_synthetic_stop_tree', HERE/'test_reader.py')
            manifest, scenes = fixture.bed()
            batch_doc = json.loads(batch.read_bytes())
            for export in batch_doc['exports']:
                if export['role'] == 'calibration':
                    _, rows = fixture.tree(Path(export['root']), export['role'], manifest, scenes,
                                           levels=(20, 22, 20))
                    for row in rows:
                        row['declarationSha256'] = batch_doc['inputs']['declaration']['sha256']
                    export['indexSha256'] = fixture.reseal(Path(export['root']), rows)
            pack = native.parents[1]/'2026-10-08-w50-g1-sitting/pack.json'
            pack_doc = json.loads(pack.read_bytes())
            pack_doc['exportIndexSha256'] = {e['role']: e['indexSha256'] for e in batch_doc['exports']}
            pack.write_bytes(encoded(pack_doc)); batch_doc['inputs']['pack']['sha256'] = sha(pack)
            batch.write_bytes(encoded(batch_doc))
            instrument = self.seal(native, batch)
            out = Path(td)/'stop-report.json'
            result = self.command(native, batch, '--root-sha256', instrument, '--out', out)
            self.assertEqual(result.returncode, 1, result.stderr)
            report = json.loads(out.read_bytes())
            self.assertFalse(report['ready'])
            self.assertEqual(report['status'], 'STOP_NATIVE_READINESS')
            self.assertTrue(report['roles'][0]['stops'])
            self.assertEqual(len(report['roles'][0]['cells'][0]['runs']), 3)
            self.assertTrue(report['roles'][1]['ready'])

    def test_contract_and_native_root_are_write_once(self):
        with tempfile.TemporaryDirectory() as td:
            _, native, batch = self.fixture(td)
            self.seal(native, batch)
            before = {p.name: p.read_bytes() for p in (native/'execution-contract.json',
                native/'execution-contract.json.sha256', native/'instrument-root.json',
                native/'instrument-root.json.sha256')}
            second = self.command(native, 'seal', batch)
            self.assertNotEqual(second.returncode, 0)
            for name, raw in before.items():
                self.assertEqual((native/name).read_bytes(), raw)

    def test_swapped_batch_or_resealed_native_root_refuses_before_pixel_decode(self):
        with tempfile.TemporaryDirectory() as td:
            _, native, batch = self.fixture(td)
            instrument = self.seal(native, batch)
            other = native/'swapped.json'; other.write_text('{}')
            for supplied in (other, batch):
                if supplied == batch:
                    path = native/'instrument-root.json'
                    doc = json.loads(path.read_bytes()); doc['extra'] = 'changed'
                    path.write_bytes(encoded(doc))
                    Path(str(path)+'.sha256').write_text(f'{sha(path)}  {path.name}\n')
                result = self.command(native, supplied, '--root-sha256', instrument,
                                      '--out', Path(td)/'never.json')
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((Path(td)/'never.json').exists())

    def test_changed_early_helper_is_rejected_before_its_marker_executes(self):
        for name in ('reader.py', 'statistics.py'):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as td:
                _, native, batch = self.fixture(td)
                instrument = self.seal(native, batch)
                marker = Path(td)/'executed'
                (native/name).write_text(f'from pathlib import Path\nPath({str(marker)!r}).write_text("BAD")\n')
                result = self.command(native, batch, '--root-sha256', instrument,
                                      '--out', Path(td)/'never.json')
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('source', result.stderr.lower())
                self.assertFalse(marker.exists())

    def test_changed_g0_manifest_or_guard_is_rejected_before_helper_execution(self):
        for relative in ('bed/manifest.json', 'audit/next_wave.py', 'audit/closure.py'):
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as td:
                root, native, batch = self.fixture(td)
                instrument = self.seal(native, batch)
                target = root/'packages/calibration/results'/G0.name/relative
                target.write_text('CHANGED')
                result = self.command(native, batch, '--root-sha256', instrument,
                                      '--out', Path(td)/'never.json')
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((Path(td)/'never.json').exists())

    def test_new_late_import_is_refused_in_actual_reader_process_before_marker_executes(self):
        with tempfile.TemporaryDirectory() as td:
            _, native, batch = self.fixture(td)
            marker = Path(td)/'late-executed'
            (native/'late.py').write_text(f'from pathlib import Path\nPath({str(marker)!r}).write_text("BAD")\n')
            reader = native/'reader.py'
            reader.write_text(reader.read_text()+'''
_original_role_read = read_role_export

def read_role_export(*args, **kwargs):
    import importlib.util
    spec = importlib.util.spec_from_file_location('late_unsealed_module', HERE/'late.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return _original_role_read(*args, **kwargs)
''')
            instrument = self.seal(native, batch)
            result = self.command(native, batch, '--root-sha256', instrument,
                                  '--out', Path(td)/'never.json')
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('unsealed', result.stderr.lower())
            self.assertFalse(marker.exists())

    def test_source_only_actual_reader_ignores_timestamp_valid_stale_pyc(self):
        with tempfile.TemporaryDirectory() as td:
            _, native, batch = self.fixture(td)
            instrument = self.seal(native, batch)
            path = native/'reader.py'; safe = path.read_bytes(); stamp = path.stat().st_mtime
            marker = Path(td)/'bytecode-executed'
            evil = f'from pathlib import Path\nPath({str(marker)!r}).write_text("BAD")\n'.encode()
            path.write_bytes(evil+b' '*(len(safe)-len(evil)))
            os.utime(path, (stamp, stamp)); py_compile.compile(str(path), doraise=True)
            path.write_bytes(safe); os.utime(path, (stamp, stamp))
            # Prove the cache is genuinely accepted by an ordinary SourceFileLoader.
            ordinary = load('unsafe_pyc_fixture', path)
            self.assertTrue(marker.exists()); marker.unlink()
            out = Path(td)/'source-report.json'
            result = self.command(native, batch, '--root-sha256', instrument, '--out', out)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(marker.exists())

    def test_sealing_also_ignores_timestamp_valid_stale_guard_bytecode(self):
        with tempfile.TemporaryDirectory() as td:
            root, native, batch = self.fixture(td)
            guard = root/'packages/calibration/results'/G0.name/'audit/closure.py'
            safe = guard.read_bytes(); stamp = guard.stat().st_mtime
            marker = Path(td)/'guard-bytecode-executed'
            evil = f'from pathlib import Path\nPath({str(marker)!r}).write_text("BAD")\n'.encode()
            guard.write_bytes(evil+b' '*(len(safe)-len(evil)))
            os.utime(guard, (stamp, stamp)); py_compile.compile(str(guard), doraise=True)
            guard.write_bytes(safe); os.utime(guard, (stamp, stamp))
            load('unsafe_guard_pyc_fixture', guard)
            self.assertTrue(marker.exists()); marker.unlink()
            self.seal(native, batch)
            self.assertFalse(marker.exists())

    def test_blind_role_or_unregistered_g0_input_cannot_be_sealed(self):
        for change in ('blind', 'manifest', 'export-index'):
            with self.subTest(change=change), tempfile.TemporaryDirectory() as td:
                _, native, batch = self.fixture(td)
                doc = json.loads(batch.read_bytes())
                if change == 'blind':
                    doc['exports'][0]['role'] = 'blind'
                elif change == 'export-index':
                    doc['exports'][0]['indexSha256'] = 'f'*64
                else:
                    doc['inputs']['manifest']['sha256'] = '0'*64
                batch.write_bytes(encoded(doc))
                result = self.command(native, 'seal', batch)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((native/'execution-contract.json').exists())
                self.assertFalse((native/'instrument-root.json').exists())


if __name__ == '__main__':
    unittest.main()
