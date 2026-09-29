import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from PIL import Image
import snapshots


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


class SnapshotTests(unittest.TestCase):
    def fixture(self, root):
        image = root / 'scratch/image.png'
        image.parent.mkdir()
        Image.new('RGB', (2, 2), (30, 40, 50)).save(image)
        projection = root / 'evidence/projection.json'
        projection.parent.mkdir()
        projection.write_text('{"deep": [30, 40, 50]}\n')
        capture = {'png': str(image), 'pngSha256': sha(image),
                   'projection': str(projection.relative_to(root)),
                   'projectionSha256': sha(projection)}
        return {'profile/a': capture, 'profile/b': dict(capture)}

    def test_copies_exact_bytes_deduplicates_and_keeps_scratch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            captures = self.fixture(root)
            result = snapshots.copy_payloads(root, root / 'evidence', captures)
            self.assertEqual(result['cells']['profile/a'], result['cells']['profile/b'])
            self.assertEqual(len(list((root / 'evidence/capture-payloads').iterdir())), 2)
            for cell, payload in result['cells'].items():
                self.assertEqual((root / payload['png']).read_bytes(), Path(captures[cell]['png']).read_bytes())
                self.assertEqual((root / payload['projection']).read_bytes(),
                                 (root / captures[cell]['projection']).read_bytes())
            with self.assertRaises(FileExistsError):
                snapshots.copy_payloads(root, root / 'evidence', captures)

    def test_changed_source_refuses_before_copying(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            captures = self.fixture(root)
            Path(captures['profile/a']['png']).write_bytes(b'changed')
            with self.assertRaises(ValueError):
                snapshots.copy_payloads(root, root / 'evidence', captures)
            self.assertFalse((root / 'evidence/capture-payloads').exists())


if __name__ == '__main__': unittest.main()
