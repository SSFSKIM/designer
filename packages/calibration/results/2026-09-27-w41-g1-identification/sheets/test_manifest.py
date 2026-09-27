import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from unittest import mock
import unittest

spec = importlib.util.spec_from_file_location('sheet_manifest', Path(__file__).with_name('manifest.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class Conversion(unittest.TestCase):
    def fixture(self):
        cell = 'profile/open'
        row = dict(primaryCapture='/scratch/attempt/calval/profile/open/open__webgpu.png',
            png='payload/p.png', pngSha256='p', descriptor='payload/c.json', descriptorSha256='c',
            report='payload/r.json', reportSha256='r')
        raw = {'cells': {cell: row, 'profile/closed': {'DO_NOT_READ': 'blind sentinel'}}}
        frozen = {'files': {'payload/p.png': 'p', 'payload/c.json': 'c', 'payload/r.json': 'r'}}
        seal = {'profiles': {'profile': {'material': 'candidate/active.json', 'receded': 'candidate/receded.json'}},
                'inputs': {'candidate/active.json': 'a'*64, 'candidate/receded.json': 'b'*64}}
        return cell, row, raw, frozen, seal

    def test_only_selected_metadata_converted_and_candidate_paths_retained(self):
        cell, _, raw, frozen, seal = self.fixture()
        result = m.convert(raw, frozen, seal, [cell])
        self.assertEqual(set(result['captures']), {cell})
        self.assertEqual(result['captureRoot'], '/scratch/attempt/calval')
        self.assertEqual(result['captures'][cell]['cellSha256'], 'c')
        self.assertEqual(result['documents']['profile'][0]['path'], 'candidate/active.json')
        self.assertEqual(result['documents']['profile'][1]['sha256'], 'b'*12)

    def test_misfiled_cell_and_unbound_payload_refused(self):
        cell, row, raw, frozen, seal = self.fixture()
        row['primaryCapture'] = '/scratch/attempt/calval/profile/other/open__webgpu.png'
        with self.assertRaises(ValueError): m.convert(raw, frozen, seal, [cell])
        cell, row, raw, frozen, seal = self.fixture()
        row['descriptorSha256'] = 'changed'
        with self.assertRaises(ValueError): m.convert(raw, frozen, seal, [cell])

class Derivation(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = (Path(self.tmp.name) / 'repo').resolve()
        self.root.mkdir()
        self.sheet = self.root / 'work/sheets'
        self.sheet.mkdir(parents=True)
        self.attempt = 'attempt-1'
        self.prefix = Path('work/candidate-capture') / self.attempt
        subprocess.run(['git', '-C', str(self.root), 'init', '-q'], check=True)
        self.cells = [f'profile/cell{i:03}' for i in range(536)]
        self.preparation = {'cells': self.cells.copy()}
        self.documents = {'candidate/active.json': {'material': 'active'},
                          'candidate/receded.json': {'material': 'receded'}}
        for path, document in self.documents.items(): self.save(path, document)
        scope = self.save('work/baseline/preparation.json', self.preparation)
        self.seal = {'profiles': {'profile': {'material': 'candidate/active.json',
                                             'receded': 'candidate/receded.json'}},
                     'inputs': {path: self.digest(path) for path in self.documents}}
        self.seal['inputs']['work/baseline/preparation.json'] = scope
        seal_path = self.prefix / 'seal.json'
        seal_sha = self.save(seal_path, self.seal)
        capture_root = Path('/Users/new/vitrea-w41/g1-captures/candidate-e3') / self.attempt / 'calval'
        self.raw = {'sealSha256': seal_sha, 'cells': {}}
        self.frozen = {'sealSha256': seal_sha, 'files': {str(seal_path): seal_sha}}
        for cell in [*self.cells, 'profile/blind']:
            profile, sid = cell.split('/')
            row = {'primaryCapture': str(capture_root / profile / sid / (sid + '__webgpu.png'))}
            for key in ('png', 'descriptor', 'report'):
                path = f'payload/{sid}-{key}'
                row[key] = path
                row[key + 'Sha256'] = sid + '-' + key
                self.frozen['files'][path] = row[key + 'Sha256']
            self.raw['cells'][cell] = row
        raw_path = self.prefix / 'raw-inventory.json'
        self.frozen['files'][str(raw_path)] = self.save(raw_path, self.raw)
        self.save(self.prefix / 'frozen.json', self.frozen)
        self.commit()
        self.patch = mock.patch.multiple(m, ROOT=self.root, HERE=self.sheet)
        self.patch.start()
        self.addCleanup(self.patch.stop)
        self.output = self.sheet / 'derived.json'

    def digest(self, path):
        return hashlib.sha256((self.root / path).read_bytes()).hexdigest()

    def save(self, path, data):
        path = self.root / path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, sort_keys=True) + '\n')
        return self.digest(path.relative_to(self.root))

    def commit(self):
        subprocess.run(['git', '-C', str(self.root), 'add', '.'], check=True)
        subprocess.run(['git', '-C', str(self.root), '-c', 'user.name=Fixture',
                        '-c', 'user.email=fixture@example.test', 'commit', '-qm', 'metadata fixture'], check=True)

    def refresh_chain(self):
        scope_path = 'work/baseline/preparation.json'
        self.seal['inputs'][scope_path] = self.save(scope_path, self.preparation)
        seal_path = self.prefix / 'seal.json'
        seal_sha = self.save(seal_path, self.seal)
        self.raw['sealSha256'] = seal_sha
        raw_path = self.prefix / 'raw-inventory.json'
        self.frozen['files'][str(raw_path)] = self.save(raw_path, self.raw)
        self.frozen['sealSha256'] = seal_sha
        self.frozen['files'][str(seal_path)] = seal_sha
        self.save(self.prefix / 'frozen.json', self.frozen)
        self.commit()

    def assert_refused(self, message=None):
        with self.assertRaisesRegex(ValueError, message or ''):
            m.derive(self.attempt, self.output)
        self.assertFalse(self.output.exists())

    def test_derived_metadata_binds_chain_and_ignores_unselected_blind(self):
        m.derive(self.attempt, self.output)
        result = json.loads(self.output.read_text())
        self.assertEqual(len(result['captures']), 536)
        self.assertNotIn('profile/blind', result['captures'])
        self.assertEqual(result['admissionScope']['sha256'],
                         self.seal['inputs']['work/baseline/preparation.json'])
        self.assertEqual(result['sourceRawInventory']['sha256'],
                         self.frozen['files'][str(self.prefix / 'raw-inventory.json')])
        self.assertEqual(result['sourceSeal']['sha256'], self.raw['sealSha256'])
        self.assertEqual(result['documents']['profile'][0]['path'], 'candidate/active.json')
        self.assertEqual(result['nativePayloadReads'], 0)
        self.assertEqual(result['capturePngReads'], 0)

    def test_broken_raw_or_seal_links_refused(self):
        cases = [('frozen raw', lambda: self.frozen['files'].__setitem__(
                     str(self.prefix / 'raw-inventory.json'), 'incorrect')),
                 ('frozen seal', lambda: self.frozen.__setitem__('sealSha256', 'incorrect')),
                 ('raw seal', lambda: self.raw.__setitem__('sealSha256', 'incorrect')),
                 ('seal file', lambda: self.frozen['files'].__setitem__(
                     str(self.prefix / 'seal.json'), 'incorrect'))]
        for name, change in cases:
            with self.subTest(name=name):
                change()
                if name == 'raw seal': self.save(self.prefix / 'raw-inventory.json', self.raw)
                else: self.save(self.prefix / 'frozen.json', self.frozen)
                self.commit()
                self.assert_refused('raw inventory/seal differs')
                self.raw['sealSha256'] = self.frozen['sealSha256'] = self.digest(self.prefix / 'seal.json')
                self.frozen['files'][str(self.prefix / 'seal.json')] = self.frozen['sealSha256']
                self.frozen['files'][str(self.prefix / 'raw-inventory.json')] = self.save(
                    self.prefix / 'raw-inventory.json', self.raw)
                self.save(self.prefix / 'frozen.json', self.frozen)
                self.commit()

    def test_changed_committed_candidate_document_refused(self):
        self.save('candidate/active.json', {'material': 'changed'})
        self.commit()
        self.assert_refused('candidate document changed')

    def test_scope_count_and_duplicate_refused(self):
        self.preparation['cells'].pop()
        self.refresh_chain()
        self.assert_refused('536 admitted calval cells required')
        self.preparation['cells'].append(self.preparation['cells'][0])
        self.refresh_chain()
        self.assert_refused('536 admitted calval cells required')

    def test_selected_blind_primary_capture_refused(self):
        self.preparation['cells'][0] = 'profile/blind'
        self.raw['cells']['profile/blind']['primaryCapture'] = (
            '/Users/new/vitrea-w41/g1-captures/candidate-e3/attempt-1/blind/profile/blind/'
            'blind__webgpu.png')
        self.refresh_chain()
        self.assert_refused('candidate primary capture is misfiled: profile/blind')

    def test_output_must_be_new_json_inside_sheets(self):
        self.output.write_text('do not replace')
        with self.assertRaises(FileExistsError): m.derive(self.attempt, self.output)
        self.assertEqual(self.output.read_text(), 'do not replace')
        outside = self.root / 'outside.json'
        self.assert_refused_output(outside)
        self.assert_refused_output(self.sheet / 'derived.txt')

    def assert_refused_output(self, path):
        with self.assertRaisesRegex(ValueError, 'new sheet JSON output required'):
            m.derive(self.attempt, path)
        self.assertFalse(path.exists())

    def test_post_seal_committed_scope_change_is_refused(self):
        self.preparation['cells'][:2] = reversed(self.preparation['cells'][:2])
        self.save('work/baseline/preparation.json', self.preparation)
        self.commit()
        with self.assertRaisesRegex(ValueError, 'admission scope.*seal'):
            m.derive(self.attempt, self.output)
        self.assertFalse(self.output.exists())

if __name__ == '__main__': unittest.main()

