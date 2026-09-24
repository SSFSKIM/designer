"""A reader that opens a held or path-named payload must fail before filesystem access."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / '2026-09-23-w34-g0-contour-bed'))

class Boundary(unittest.TestCase):
    def test_web_refuses_holdout_and_bare_paths_before_open(self):
        from w35_readers import WebReader
        reader = WebReader.w34()
        for key in ['apple-macos-27.0-1x-light-standard-glass0.5/grey-208__circular-120__rest',
                    '/tmp/anything.png', '../outside.png']:
            with patch.object(Path, 'read_bytes', side_effect=AssertionError('payload opened')):
                with self.assertRaises((ValueError, PermissionError)):
                    reader.read(key)

    def test_canonical_refuses_holdout_recorded_and_paths(self):
        from w35_readers import CanonicalNativeReader
        reader = CanonicalNativeReader()
        for sid in ['hc-text__capsule-button__rest', 'checkerboard__capsule-button__pressed']:
            with patch.object(Path, 'read_bytes', side_effect=AssertionError('payload opened')):
                with self.assertRaises(PermissionError):
                    reader.read('apple-macos-27.0-1x-light-standard-glass0.5/' + sid)
        with self.assertRaises(ValueError): reader.read('/tmp/pixel.png')

    def test_canonical_web_has_the_same_role_boundary(self):
        from w35_readers import WebReader
        reader = WebReader.canonical(Path('/unavailable'))
        with self.assertRaises(PermissionError):
            reader.read('apple-macos-27.0-1x-light-standard-glass0.5/hc-text__capsule-button__rest')

if __name__ == '__main__': unittest.main()
