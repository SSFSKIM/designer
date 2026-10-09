"""Historical proof authentication uses real git objects, never synthetic hash exemptions."""
import gzip
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest

HERE = Path(__file__).resolve().parent
H = types.ModuleType('historical_tests_subject'); H.__file__ = str(HERE/'historical.py')
exec(compile((HERE/'historical.py').read_bytes(), H.__file__, 'exec'), H.__dict__)


def digest(raw): return hashlib.sha256(raw).hexdigest()


class HistoricalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name).resolve()
        self.git('init', '-q'); self.git('config', 'user.email', 'test@example.test')
        self.git('config', 'user.name', 'Test')
        (self.repo/'source.py').write_bytes(b'old source\n')
        (self.repo/'test.py').write_bytes(b'old test\n')
        self.git('add', '.'); self.git('commit', '-qm', 'historical proof')
        self.old = self.git('rev-parse', 'HEAD').decode().strip()
        (self.repo/'source.py').write_bytes(b'new source\n')
        (self.repo/'test.py').write_bytes(b'new test\n')
        self.git('add', '.'); self.git('commit', '-qm', 'reviewed carry and regression')
        self.new = self.git('rev-parse', 'HEAD').decode().strip()
        self.reader = H.Historical(self.repo, self.old, self.new, ('source.py', 'test.py'))

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.repo), *args], check=True,
                              capture_output=True).stdout

    def test_changed_test_pin_reproduces_live_failure_but_historical_admits(self):
        item = {'path': 'test.py', 'sha256': digest(b'old test\n')}
        self.assertNotEqual(digest((self.repo/'test.py').read_bytes()), item['sha256'])
        self.assertEqual(self.reader.checked(self.repo, item), self.repo/'test.py')
        self.assertEqual(self.reader.blob('test.py'), b'old test\n')

    def test_only_exact_committed_delta_is_admitted(self):
        (self.repo/'test.py').write_bytes(b'other test\n')
        with self.assertRaises(ValueError):
            self.reader.checked(self.repo, {'path': 'test.py', 'sha256': digest(b'old test\n')})

    def test_undeclared_live_change_refuses(self):
        reader = H.Historical(self.repo, self.old, self.new, ())
        with self.assertRaises(ValueError):
            reader.checked(self.repo, {'path': 'test.py', 'sha256': digest(b'old test\n')})

    def test_missing_blob_cannot_be_supplied_by_live_file(self):
        (self.repo/'missing').write_bytes(b'matches')
        with self.assertRaises(ValueError):
            self.reader.checked(self.repo, {'path': 'missing', 'sha256': digest(b'matches')})

    def test_wrong_commit_pin_and_path_refuse(self):
        for item in ({'path': '../escape', 'sha256': 'a'*64},
                     {'path': str(self.repo/'test.py'), 'sha256': digest(b'old test\n')},
                     {'path': 'test.py', 'sha256': digest(b'new test\n')}):
            with self.subTest(item=item), self.assertRaises(ValueError):
                self.reader.checked(self.repo, item)
        with self.assertRaises(ValueError):
            H.Historical(self.repo, 'not-a-commit', self.new, ())

    def test_exact_archive_exception_and_late_log_preservation(self):
        # The archive exists at the proof commit; neither decompressed input nor ignored log does.
        raw, log = b'{"metadata": "archive input"}\n', b'old test log\n'
        compressed = gzip.compress(raw, mtime=0)
        (self.repo/'input.json.gz').write_bytes(compressed)
        self.git('add', 'input.json.gz'); self.git('commit', '-qm', 'proof archive')
        proof_commit = self.git('rev-parse', 'HEAD').decode().strip()
        (self.repo/'input.json').write_bytes(raw); (self.repo/'test.log').write_bytes(log)
        self.git('add', 'test.log'); self.git('commit', '-qm', 'late log preservation')
        preservation = self.git('rev-parse', 'HEAD').decode().strip()
        exceptions = {
            'input.json': {'sha256': digest(raw), 'bytes': len(raw),
                'authentication': 'COMMITTED_GZIP_BLOB_DECOMPRESSION',
                'archiveCommit': proof_commit,
                'archive': {'path': 'input.json.gz', 'sha256': digest(compressed)}},
            'test.log': {'sha256': digest(log), 'bytes': len(log),
                'authentication': 'HISTORICAL_PROOF_SHA256_LATE_PRESERVATION'}}
        reader = H.Historical(self.repo, proof_commit, self.new, (), exceptions, preservation)
        for name, payload in (('input.json', raw), ('test.log', log)):
            self.assertEqual(reader.checked(self.repo, {'path': name, 'sha256': digest(payload)}),
                             self.repo/name)
        (self.repo/'test.log').write_bytes(b'regenerated')
        with self.assertRaises(ValueError):
            reader.checked(self.repo, {'path': 'test.log', 'sha256': digest(log)})
        exceptions['input.json']['archiveCommit'] = self.old
        with self.assertRaises(ValueError):
            H.Historical(self.repo, proof_commit, self.new, (), exceptions, preservation).checked(
                self.repo, {'path': 'input.json', 'sha256': digest(raw)})

    def test_wrong_historical_commit_cannot_authorize_matching_live_bytes(self):
        reader = H.Historical(self.repo, self.new, self.new, ('test.py',))
        with self.assertRaises(ValueError):
            reader.checked(self.repo, {'path': 'test.py', 'sha256': digest(b'old test\n')})

    def test_symlink_even_with_matching_bytes_refuses(self):
        (self.repo/'test.py').unlink(); (self.repo/'test.py').symlink_to('source.py')
        with self.assertRaises(ValueError):
            self.reader.checked(self.repo, {'path': 'test.py', 'sha256': digest(b'old test\n')})


if __name__ == '__main__': unittest.main()
