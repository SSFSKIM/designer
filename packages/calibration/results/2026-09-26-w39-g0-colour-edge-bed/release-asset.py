#!/usr/bin/env python3.12
"""Pack the W39 archive of record as one release asset named by its SHA-256 (§5.184, DL1).

Decision Log 1 (ruled 2026-09-26) puts the archive in a GitHub release asset,
out of ordinary Git. This packs an archive directory (what `archive-producer.py`
wrote) into `w39-archive-<sha256>.tar.zst`: a deterministic tar (sorted members
under `archive/`, mtime 0, uid/gid 0, fixed modes) compressed by the `zstd` CLI
at one thread, so packing the same directory with the same zstd twice gives the
same bytes. The digest is of the TARBALL, the name carries all 64 hex digits,
and the file must stay under GitHub's 2 GiB asset limit.

Before packing, the directory is checked as the reader will check it: every
inventory entry exists and hashes to its recorded digest, and nothing else is
in the tree (no stray PNG, no symlink), so the asset is exactly the inventory.

    python3.12 release-asset.py pack <archive-dir> --out-dir ~/vitrea-w39/release

prints the asset's path, digest, byte size, inventory digest and the commands G1
runs to publish it (tag `w39-archive`, never marked latest, so the npm releases'
"Latest" is untouched). `fetch-archive.py` is the reader's side.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TAG = 'w39-archive'
PREFIX = 'w39-archive-'
SUFFIX = '.tar.zst'
TOP = 'archive'
LIMIT = 2 * 1024 ** 3          # GitHub's per-asset ceiling; the asset must be strictly below it
REPO = 'SSFSKIM/designer'
ZSTD = ['zstd', '-19', '-T1', '-q', '-c']


def file_sha(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(chunk), b''): h.update(block)
    return h.hexdigest()


def asset_name(digest): return PREFIX + digest + SUFFIX


def check_digest(digest):
    if not (isinstance(digest, str) and len(digest) == 64 and all(c in '0123456789abcdef' for c in digest)):
        raise ValueError('an archive is named by a full lowercase SHA-256 (64 hex digits)')


def verify_tree(root):
    """Every inventory entry present and intact, and nothing else: the tree IS the inventory."""
    root = Path(root)
    inventory = json.loads((root / 'inventory.json').read_bytes())
    expected = {'inventory.json'}
    for row in inventory['entries']:
        rel = PurePosixPath(row['path'])
        if rel.is_absolute() or '..' in rel.parts: raise ValueError('inventory path escapes the archive')
        path = root / rel
        if path.is_symlink() or not path.is_file(): raise ValueError('inventory entry missing: ' + row['path'])
        if file_sha(path) != row['sha256']: raise ValueError('inventory entry altered: ' + row['path'])
        expected.add(str(rel))
    present = set()
    for dirpath, dirnames, filenames in os.walk(root):
        for name in dirnames + filenames:
            path = Path(dirpath) / name
            if path.is_symlink(): raise ValueError('symlink in archive tree: ' + str(path))
        for name in filenames: present.add((Path(dirpath) / name).relative_to(root).as_posix())
    if present != expected:
        raise ValueError('archive tree differs from its inventory: unlisted %s, missing %s' % (
            sorted(present - expected)[:5], sorted(expected - present)[:5]))
    return dict(entries=len(inventory['entries']), inventorySha256=file_sha(root / 'inventory.json'))


def tar_bytes_to(root, stream):
    root = Path(root)
    files = sorted(p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file())
    dirs = sorted({str(PurePosixPath(f).parent) for f in files} - {'.'})
    with tarfile.open(fileobj=stream, mode='w|', format=tarfile.PAX_FORMAT) as tar:
        def info(name, kind, size=0):
            t = tarfile.TarInfo(name); t.type = kind; t.size = size; t.mtime = 0
            t.uid = t.gid = 0; t.uname = t.gname = ''; t.mode = 0o755 if kind == tarfile.DIRTYPE else 0o644
            return t
        tar.addfile(info(TOP, tarfile.DIRTYPE))
        for d in dirs: tar.addfile(info(f'{TOP}/{d}', tarfile.DIRTYPE))
        for f in files:
            with open(root / f, 'rb') as handle:
                tar.addfile(info(f'{TOP}/{f}', tarfile.REGTYPE, (root / f).stat().st_size), handle)
    return len(files)


def zstd_version():
    return subprocess.run(['zstd', '--version'], capture_output=True, text=True, check=True).stdout.strip()


def pack(archive, out_dir, limit=None):
    limit = LIMIT if limit is None else limit
    archive, out_dir = Path(archive).resolve(), Path(out_dir).resolve()
    if out_dir == ROOT or ROOT in out_dir.parents:
        raise ValueError('the release asset is written outside the repository (DL1)')
    tree = verify_tree(archive)
    out_dir.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.packing-', dir=out_dir); os.close(fd)
    tmp = Path(tmp)
    try:
        with open(tmp, 'wb') as sink:
            zstd = subprocess.Popen(ZSTD, stdin=subprocess.PIPE, stdout=sink)
            try: members = tar_bytes_to(archive, zstd.stdin)
            finally: zstd.stdin.close()
            if zstd.wait() != 0: raise RuntimeError('zstd failed')
        size = tmp.stat().st_size
        if size >= limit:
            raise ValueError('asset is %d bytes; a release asset must be under %d' % (size, limit))
        digest = file_sha(tmp)
        final = out_dir / asset_name(digest)
        os.replace(tmp, final)
    finally:
        if tmp.exists(): tmp.unlink()
    return dict(asset=asset_name(digest), path=str(final), sha256=digest, bytes=size, tarMembers=members,
                zstd=zstd_version(), compression=' '.join(ZSTD[1:]), **tree)


def publish_commands(result, repo=REPO):
    notes = ('W39 archive of record (c9a §5.185). SHA-256 %s, %d bytes. Verify with '
             'fetch-archive.py before reading.' % (result['sha256'], result['bytes']))
    return [
        ['gh', 'release', 'create', TAG, '--repo', repo, '--title', 'W39 archive of record',
         '--notes', notes, '--latest=false', '--target', '<G1 merge commit>'],
        ['gh', 'release', 'upload', TAG, result['path'], '--repo', repo],
        ['gh', 'release', 'view', TAG, '--repo', repo, '--json', 'assets'],
    ]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='action', required=True)
    p = sub.add_parser('pack'); p.add_argument('archive', type=Path); p.add_argument('--out-dir', type=Path, required=True)
    v = sub.add_parser('verify-tree'); v.add_argument('archive', type=Path)
    args = ap.parse_args(argv)
    if args.action == 'verify-tree':
        print(json.dumps(verify_tree(args.archive), indent=2)); return
    result = pack(args.archive, args.out_dir)
    print(json.dumps(dict(**result, tag=TAG, publish=publish_commands(result)), indent=2))


if __name__ == '__main__': main()
