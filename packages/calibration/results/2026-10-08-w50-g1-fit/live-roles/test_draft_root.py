"""draft_root's registration and live-input checks on a synthetic git repository.

live_inputs() and role_inputs('owner') read only the module's REPO/FIT, so each test points them
at a temporary repository laid out like the real one; nothing in the real tree is read.
"""
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import types
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
REL = Path('packages/calibration/results/2026-10-08-w50-g1-fit')


def load():
    path = HERE/'draft_root.py'
    module = types.ModuleType('w50_draft_root_under_test'); module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


def sha(raw): return hashlib.sha256(raw).hexdigest()


class DraftRoot(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(); self.addCleanup(temp.cleanup)
        self.repo = Path(temp.name).resolve()/'repo'; self.fit = self.repo/REL
        (self.fit/'live-inputs').mkdir(parents=True)
        self.git('init', '-q')
        self.draft = load()
        for name, value in (('REPO', self.repo), ('FIT', self.fit)):
            patcher = patch.object(self.draft, name, value); patcher.start(); self.addCleanup(patcher.stop)
        self.raw = b'{"synthetic": "completed references"}\n'
        self.live = self.fit/'live-inputs/completed-references.json'; self.live.write_bytes(self.raw)
        self.archive = self.fit/'completion/registered/evidence/completed-references.json.gz'
        self.archive.parent.mkdir(parents=True)
        self.archive.write_bytes(gzip.compress(self.raw, mtime=0))
        self.manifest(self.raw)
        self.git('add', '-f', str(self.archive), str(self.archive.parent/'archive.json'))
        self.git('commit', '-q', '-m', 'synthetic archive')
        self.item = {'path': str(self.live.relative_to(self.repo)), 'sha256': sha(self.raw)}

    def git(self, *args):
        subprocess.run(['git', '-C', str(self.repo), '-c', 'user.name=synthetic', '-c', 'user.email=synthetic@invalid',
                        *args], check=True, capture_output=True)

    def manifest(self, decompressed):
        (self.archive.parent/'archive.json').write_text(json.dumps({'completedReferences': {
            'original': {'sha256': sha(decompressed)},
            'archive': {'path': str(self.archive.relative_to(self.repo)), 'sha256': sha(self.archive.read_bytes())}}}))

    def test_a_live_input_is_its_committed_archive_and_records_the_restore(self):
        [entry] = self.draft.live_inputs([self.item, {'path': 'elsewhere.json', 'sha256': '0'*64}])
        self.assertEqual(entry['archive'], {'path': str(self.archive.relative_to(self.repo)),
                                            'sha256': sha(self.archive.read_bytes())})
        self.assertTrue(entry['restore'].startswith(f'gunzip -c {entry["archive"]["path"]} > {self.item["path"]}'))

    def test_a_changed_absent_or_unarchived_live_input_refuses(self):
        self.live.write_bytes(self.raw+b' ')
        with self.assertRaisesRegex(ValueError, 'Changed or missing'): self.draft.live_inputs([self.item])
        self.live.unlink()
        with self.assertRaisesRegex(ValueError, 'Changed or missing'): self.draft.live_inputs([self.item])
        other = b'{"synthetic": "another input"}\n'; self.live.write_bytes(other)
        with self.assertRaisesRegex(ValueError, 'no unique committed archive'):
            self.draft.live_inputs([{**self.item, 'sha256': sha(other)}])

    def test_an_archive_that_does_not_decompress_to_the_live_bytes_or_is_uncommitted_refuses(self):
        # A manifest that claims the live hash for an archive of other bytes.
        self.archive.write_bytes(gzip.compress(b'{"other": true}\n', mtime=0)); self.manifest(self.raw)
        self.git('add', '-f', str(self.archive), str(self.archive.parent/'archive.json'))
        self.git('commit', '-q', '-m', 'mismatched archive')
        with self.assertRaisesRegex(ValueError, 'differs from its committed archive'): self.draft.live_inputs([self.item])
        # An archive the manifest names but git does not track.
        self.archive.write_bytes(gzip.compress(self.raw, mtime=0)); self.manifest(self.raw)
        self.git('add', '-f', str(self.archive.parent/'archive.json')); self.git('rm', '-q', '--cached', str(self.archive))
        self.git('commit', '-q', '-m', 'untracked archive')
        with self.assertRaisesRegex(ValueError, 'not committed'): self.draft.live_inputs([self.item])

    def test_an_owner_runtime_closure_outside_the_repository_refuses_registration(self):
        inside = self.fit/'live-roles/owner-runtime-closure.json'; inside.parent.mkdir(parents=True)
        inside.write_text('{}\n')
        outside = self.repo.parent/'owner-runtime-closure.json'; outside.write_text('{}\n')
        config = self.fit/'live-roles/owner-config.json'
        for runtime, expected in ((inside, [{'path': str(inside.relative_to(self.repo)), 'sha256': sha(b'{}\n')}]),
                                  (outside, None)):
            config.write_text(json.dumps({'runtimeClosure': {'path': str(runtime), 'sha256': sha(b'{}\n')}}))
            with self.subTest(runtime=runtime.name if expected else 'outside'):
                if expected is None:
                    with self.assertRaisesRegex(ValueError, 'outside the repository'):
                        self.draft.role_inputs('owner', config)
                else:
                    self.assertEqual(self.draft.role_inputs('owner', config), expected)


if __name__ == '__main__':
    unittest.main()
