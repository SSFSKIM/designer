"""G0 refuses holdout/path payloads before a file can be opened."""
import sys,unittest
from pathlib import Path
from unittest.mock import patch
from law import HERE,edge
from w35_readers import CanonicalNativeReader,WebReader
class Readers(unittest.TestCase):
    def test_native_archive_refuses_spent_payloads(self):
        wave=edge.W.default_wave();reader=wave.reader(edge.G1/'probe')
        held=next(c for c in sorted(wave.cells) if wave.roles[c.split('/')[1]]=='holdout')
        with patch.object(Path,'read_bytes',side_effect=AssertionError('opened payload')):
            with self.assertRaises(PermissionError):reader.read(held,'png')
            with self.assertRaises(ValueError):reader.read('/tmp/arbitrary.png','png')
        with self.assertRaises(PermissionError):wave.reader(edge.G1/'probe',roles=('holdout',))
    def test_web_and_canonical_roles_are_not_interchangeable(self):
        w=WebReader.w34();native=CanonicalNativeReader();web=WebReader.canonical('/unavailable')
        held='apple-macos-27.0-1x-light-standard-glass0.5/grey-208__circular-120__rest'
        with patch.object(Path,'read_bytes',side_effect=AssertionError('opened payload')):
            with self.assertRaises(PermissionError):w.read(held)
            for reader in [native,web]:
                for sid in ['hc-text__capsule-button__rest','checkerboard__capsule-button__pressed']:
                    with self.assertRaises(PermissionError):reader.read('apple-macos-27.0-1x-light-standard-glass0.5/'+sid)
                with self.assertRaises(ValueError):reader.read('/tmp/arbitrary.png')
if __name__=='__main__':unittest.main()
