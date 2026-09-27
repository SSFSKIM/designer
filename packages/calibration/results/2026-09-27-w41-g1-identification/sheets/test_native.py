import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('native', Path(__file__).with_name('native.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class Selection(unittest.TestCase):
    def runs(self):
        return [dict(run=f'run-{i}', state=str(i), admitted=True, protocol='normal',
                     inputHashes={'source': str(i)}, attestation={'full': True}) for i in range(7)]

    def test_selection_is_actual_explicit_repeat_not_median(self):
        runs = self.runs()
        self.assertEqual(m.select_repeat(list(reversed(runs)), 2), runs[2])

    def test_incomplete_duplicate_non_normal_or_bad_ordinal_refused(self):
        for runs in [self.runs()[:6], self.runs() + [self.runs()[0]],
                     [dict(r, protocol='perturbed') for r in self.runs()]]:
            with self.assertRaises(ValueError): m.select_repeat(runs, 0)
        for index in [-1, 7]:
            with self.assertRaises(ValueError): m.select_repeat(self.runs(), index)

class GuardedBridge(unittest.TestCase):
    def test_real_reader_hash_guard_and_selected_pixels(self):
        import base64, hashlib, io, json, tempfile
        from types import SimpleNamespace
        from unittest.mock import patch
        import numpy as np
        from PIL import Image
        boundary = m.module('test_sheet_wave', m.W39 / 'wave.py')
        archive = m.module('test_sheet_archive', m.W39 / 'w39_archive.py')
        cell = 'p/open'
        fake = SimpleNamespace(cells={cell, 'p/closed'}, roles={'open': 'calibration', 'closed': 'holdout'},
                               scenes_sha='scenes', split_sha='split', select=lambda roles, auth: ['open'])
        fake.reader = lambda root, roles: boundary.Reader(fake, root, roles, None)
        runs, states = [], {}
        for i in range(7):
            raw = archive.pack({'rgb': np.full((2, 3, 3), 10 + i, dtype=np.uint8), 'scale': 1})
            state = archive.sha(raw); states[state] = raw
            runs.append(dict(run=f'run-{i}', state=state, admitted=True, protocol='normal',
                             sources={'exact': i}, attestation={'context': 'synthetic'}))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); (root / 'calibration').mkdir()
            payload = archive.bundle(runs, states)
            path = root / 'calibration/crop.bin.gz'; path.write_bytes(payload)
            inventory = dict(scenesSha256='scenes', splitSha256='split', entries=[dict(
                cell=cell, kind='crop', path='calibration/crop.bin.gz', admitted=True,
                sha256=archive.sha(payload))])
            inv = json.dumps(inventory).encode(); (root / 'inventory.json').write_bytes(inv)
            with patch.object(m, 'module', side_effect=lambda name, path:
                              SimpleNamespace(default_wave=lambda: fake) if name == 'sheet_wave' else archive):
                result = m.read_native(root, archive.sha(inv), cell, 4)
                image = Image.open(io.BytesIO(base64.b64decode(result['png'])))
                self.assertEqual(image.getpixel((1, 1)), (14, 14, 14))
                self.assertEqual(result['provenance']['selected'], runs[4])
                self.assertEqual(result['provenance']['allRuns'], runs)
                with self.assertRaises(PermissionError): m.read_native(root, archive.sha(inv), 'p/closed', 0)
                with self.assertRaises(ValueError): m.read_native(root, 'wrong', cell, 0)
                path.write_bytes(b'altered')
                with self.assertRaises(ValueError): m.read_native(root, archive.sha(inv), cell, 0)

if __name__ == '__main__': unittest.main()
