#!/usr/bin/env python3.12
"""The release asset's pack -> digest -> fetch -> verify -> extract path, with no network (§5.184, DL1).

A small synthetic archive stands in for the sitting's; the download is a fake
that copies (or corrupts) a local file, so every refusal is exercised on the
same code path `gh release download` feeds.
"""
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest

HERE = Path(__file__).resolve().parent


def module(name, file):
    spec = importlib.util.spec_from_file_location(name, HERE / file)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


release = module('w39_release_asset', 'release-asset.py')
fetcher = module('w39_fetch_archive', 'fetch-archive.py')


def sha(raw): return hashlib.sha256(raw).hexdigest()


class ReleaseAsset(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.archive = self.base / 'archive-dir'
        entries = []
        for role, n in [('calibration', 3), ('validation', 1), ('holdout', 2)]:
            for i in range(n):
                raw = os.urandom(2048) + bytes(4096)
                path = f'{role}/{sha(f"{role}{i}".encode())}.crop.bin.gz'
                (self.archive / role).mkdir(parents=True, exist_ok=True); (self.archive / path).write_bytes(raw)
                entries.append(dict(cell=f'p/{role}{i}', kind='crop', path=path, sha256=sha(raw)))
        (self.archive / 'inventory.json').write_text(json.dumps(dict(schema='w39-archive-1', entries=entries)))
        self.out = self.base / 'release'
        self.cache = self.base / 'cache'
        self.downloads = []

    def fake_download(self, source, corrupt=False):
        def download(tag, asset, repo, directory):
            self.downloads.append((tag, asset, repo))
            raw = Path(source).read_bytes()
            if corrupt: raw = raw[:-1] + bytes([raw[-1] ^ 1])
            (Path(directory) / asset).write_bytes(raw)
            return Path(directory) / asset
        return download

    def test_pack_names_the_asset_by_the_full_digest_and_is_deterministic(self):
        a = release.pack(self.archive, self.out)
        self.assertEqual(a['asset'], 'w39-archive-' + a['sha256'] + '.tar.zst')
        self.assertEqual(len(a['sha256']), 64)
        self.assertEqual(sha(Path(a['path']).read_bytes()), a['sha256'])
        self.assertEqual(Path(a['path']).stat().st_size, a['bytes'])
        self.assertLess(a['bytes'], release.LIMIT)
        self.assertEqual(a['entries'], 6); self.assertEqual(a['tarMembers'], 7)
        b = release.pack(self.archive, self.base / 'again')
        self.assertEqual(a['sha256'], b['sha256'])
        self.assertEqual([p.name for p in self.out.iterdir()], [a['asset']])
        commands = release.publish_commands(a)
        self.assertEqual(commands[0][:4], ['gh', 'release', 'create', 'w39-archive'])
        self.assertIn('--latest=false', commands[0])
        self.assertEqual(commands[1][:4], ['gh', 'release', 'upload', 'w39-archive'])
        # The tarball holds exactly archive/ + the inventory, with fixed metadata.
        listing = subprocess.run(['zstd', '-d', '-q', '-c', a['path']], capture_output=True, check=True).stdout
        with tarfile.open(fileobj=io.BytesIO(listing), mode='r:') as tar:
            members = tar.getmembers()
        self.assertTrue(all(m.name == 'archive' or m.name.startswith('archive/') for m in members))
        self.assertTrue(all(m.mtime == 0 and m.uid == 0 and m.gid == 0 for m in members))

    def test_pack_refuses_an_archive_that_is_not_its_inventory(self):
        (self.archive / 'calibration/stray.png').write_bytes(b'raw capture')
        with self.assertRaisesRegex(ValueError, 'unlisted'): release.pack(self.archive, self.out)
        (self.archive / 'calibration/stray.png').unlink()
        victim = next((self.archive / 'holdout').iterdir()); victim.write_bytes(b'altered')
        with self.assertRaisesRegex(ValueError, 'altered'): release.pack(self.archive, self.out)
        victim.unlink(); os.symlink('/etc/hosts', victim)
        with self.assertRaisesRegex(ValueError, 'missing|symlink'): release.pack(self.archive, self.out)
        with self.assertRaisesRegex(ValueError, 'outside the repository'):
            release.pack(self.archive, release.ROOT / 'packages/calibration/results/x')
        self.assertFalse(self.out.exists() and any(self.out.iterdir()))

    def test_pack_refuses_an_asset_at_or_over_the_limit_and_leaves_nothing(self):
        with self.assertRaisesRegex(ValueError, 'must be under'): release.pack(self.archive, self.out, limit=64)
        self.assertEqual(list(self.out.iterdir()), [])

    def test_fetch_verifies_then_extracts_then_reuses_a_verified_cache(self):
        a = release.pack(self.archive, self.out)
        root = fetcher.fetch('w39-archive', a['asset'], a['sha256'], cache=self.cache,
                             download=self.fake_download(a['path']))
        self.assertEqual(root, self.cache.resolve() / a['sha256'] / 'extracted' / 'archive')
        self.assertEqual((root / 'inventory.json').read_bytes(), (self.archive / 'inventory.json').read_bytes())
        self.assertEqual(release.verify_tree(root)['entries'], 6)
        marker = json.loads((self.cache / a['sha256'] / 'verified.json').read_text())
        self.assertEqual((marker['sha256'], marker['bytes']), (a['sha256'], a['bytes']))
        self.assertEqual(sha((self.cache / a['sha256'] / a['asset']).read_bytes()), a['sha256'])
        self.assertEqual(self.downloads, [('w39-archive', a['asset'], release.REPO)])
        # Second call: no download; the tree is re-checked, so an edited cache is refused.
        self.assertEqual(fetcher.fetch('w39-archive', a['asset'], a['sha256'], cache=self.cache,
                                       download=self.fake_download(a['path'])), root)
        self.assertEqual(len(self.downloads), 1)
        next((root / 'calibration').iterdir()).write_bytes(b'edited after extraction')
        with self.assertRaisesRegex(ValueError, 'altered'):
            fetcher.fetch('w39-archive', a['asset'], a['sha256'], cache=self.cache,
                          download=self.fake_download(a['path']))

    def test_fetch_refuses_a_digest_mismatch_before_extraction(self):
        a = release.pack(self.archive, self.out)
        with self.assertRaisesRegex(ValueError, 'digest mismatch'):
            fetcher.fetch('w39-archive', a['asset'], a['sha256'], cache=self.cache,
                          download=self.fake_download(a['path'], corrupt=True))
        home = self.cache / a['sha256']
        self.assertEqual(sorted(p.name for p in home.iterdir()), [])
        with self.assertRaisesRegex(ValueError, 'carry the expected digest'):
            fetcher.fetch('w39-archive', 'w39-archive-other.tar.zst', a['sha256'], cache=self.cache,
                          download=self.fake_download(a['path']))
        with self.assertRaisesRegex(ValueError, '64 hex'):
            fetcher.fetch('w39-archive', a['asset'], a['sha256'][:12], cache=self.cache)
        with self.assertRaisesRegex(ValueError, 'outside the repository'):
            fetcher.fetch('w39-archive', a['asset'], a['sha256'], cache=release.ROOT / '.cache')

    def test_fetch_verifies_a_local_second_copy_through_the_same_path(self):
        a = release.pack(self.archive, self.out)
        root = fetcher.fetch('w39-archive', a['asset'], a['sha256'], cache=self.cache, source=a['path'],
                             download=None)
        self.assertEqual(release.verify_tree(root)['inventorySha256'],
                         hashlib.sha256((self.archive / 'inventory.json').read_bytes()).hexdigest())

    def hostile(self, add):
        """A tarball whose digest is honest but whose members are not."""
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode='w', format=tarfile.PAX_FORMAT) as tar: add(tar)
        path = self.base / 'hostile.tar.zst'
        path.write_bytes(subprocess.run(['zstd', '-q', '-c'], input=buffer.getvalue(), capture_output=True,
                                        check=True).stdout)
        digest = sha(path.read_bytes())
        return path, digest, 'w39-archive-' + digest + '.tar.zst'

    def test_extraction_refuses_links_escapes_and_foreign_roots(self):
        def member(name, kind=tarfile.REGTYPE, data=b'x', link=''):
            def add(tar):
                t = tarfile.TarInfo(name); t.type = kind; t.size = len(data) if kind == tarfile.REGTYPE else 0
                t.linkname = link
                tar.addfile(t, io.BytesIO(data) if kind == tarfile.REGTYPE else None)
            return add
        cases = [('unsafe', member('archive/../../escape')), ('unsafe', member('/archive/abs')),
                 ('unsafe', member('elsewhere/file')),
                 ('not a regular', member('archive/link', tarfile.SYMTYPE, link='/etc/passwd')),
                 ('not a regular', member('archive/hard', tarfile.LNKTYPE, link='archive/x'))]
        for message, add in cases:
            path, digest, asset = self.hostile(add)
            with self.subTest(message), self.assertRaisesRegex(ValueError, message):
                fetcher.fetch('w39-archive', asset, digest, cache=self.cache, source=path, download=None)
            self.assertFalse((self.cache / digest / 'extracted').exists())
        self.assertFalse((self.base / 'escape').exists())


if __name__ == '__main__': unittest.main(verbosity=2)
