#!/usr/bin/env python3.12
"""Fetch the W39 archive of record by the name the ledger records, verify it, extract it (§5.184, DL1).

    python3.12 fetch-archive.py --tag w39-archive --asset w39-archive-<sha256>.tar.zst --sha256 <sha256>

downloads the release asset with `gh release download` into
`~/.cache/vitrea-archives/<sha256>/`, verifies the FULL SHA-256 of the
tarball before anything is decompressed, refuses a mismatch (the download is
deleted and nothing is extracted), extracts through a member check (regular
files and directories under `archive/` only: no link, device, absolute path or
`..`; then Python's `data` filter), checks the extracted tree against its own
inventory (every entry intact, nothing unlisted), and prints the root that the
guarded reader takes:

    python3.12 replay-archive.py "$(python3.12 fetch-archive.py ...)" --deny-raw-root ~/vitrea-w39/run

A verified cache is reused, but its tree is re-checked against the inventory
on every call, so a cache edited after extraction is refused rather than
trusted. The digest detects replacement, not loss: a second owner-controlled
copy of the asset is G1's obligation (DL1), and `--source` verifies and
extracts that local copy through exactly the same path.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location('release_asset', HERE / 'release-asset.py')
release = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(release)
CACHE = Path.home() / '.cache' / 'vitrea-archives'


def gh_download(tag, asset, repo, directory):
    subprocess.run(['gh', 'release', 'download', tag, '--repo', repo, '--pattern', asset,
                    '--dir', str(directory)], check=True)
    return Path(directory) / asset


def safe_members(tar):
    seen = set()
    for member in tar:
        name = PurePosixPath(member.name)
        if name.is_absolute() or '..' in name.parts or not name.parts or name.parts[0] != release.TOP:
            raise ValueError('unsafe archive member path: ' + member.name)
        if not (member.isreg() or member.isdir()):
            raise ValueError('archive member is not a regular file or directory: ' + member.name)
        if str(name) in seen: raise ValueError('duplicate archive member: ' + member.name)
        seen.add(str(name))
        yield member


def extract(tarball, destination):
    """zstd-decompress to a temporary tar beside the destination, check every member, extract."""
    destination = Path(destination)
    with tempfile.NamedTemporaryFile(dir=destination.parent, suffix='.tar') as plain:
        subprocess.run(['zstd', '-d', '-q', '-c', str(tarball)], stdout=plain, check=True)
        plain.flush()
        with tarfile.open(plain.name, mode='r:') as tar:
            members = list(safe_members(tar))
            destination.mkdir()
            tar.extractall(destination, members=members, filter='data')
    return destination / release.TOP


def fetch(tag, asset, digest, repo=release.REPO, cache=CACHE, download=gh_download, source=None):
    release.check_digest(digest)
    if asset != release.asset_name(digest):
        raise ValueError('asset name does not carry the expected digest: ' + asset)
    cache = Path(cache).expanduser().resolve()
    if cache == release.ROOT or release.ROOT in cache.parents:
        raise ValueError('the archive cache lives outside the repository')
    home = cache / digest
    root = home / 'extracted' / release.TOP
    marker = home / 'verified.json'
    if root.is_dir() and marker.is_file() and json.loads(marker.read_text()).get('sha256') == digest:
        release.verify_tree(root)
        return root
    home.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=home, prefix='.download-') as scratch:
        if source is not None:
            fetched = Path(scratch) / asset; shutil.copyfile(source, fetched)
        else:
            fetched = Path(download(tag, asset, repo, scratch))
        actual = release.file_sha(fetched)
        if actual != digest:
            raise ValueError('digest mismatch: expected %s, fetched %s; nothing extracted' % (digest, actual))
        partial = Path(scratch) / 'extracted'
        extracted = extract(fetched, partial)
        tree = release.verify_tree(extracted)
        if (home / 'extracted').exists(): shutil.rmtree(home / 'extracted')
        os.replace(partial, home / 'extracted')
        os.replace(fetched, home / asset)
    marker.write_text(json.dumps(dict(sha256=digest, asset=asset, tag=tag, repo=repo,
                                      bytes=(home / asset).stat().st_size, **tree), indent=2) + '\n')
    return root


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--tag', default=release.TAG)
    ap.add_argument('--asset', required=True)
    ap.add_argument('--sha256', required=True)
    ap.add_argument('--repo', default=release.REPO)
    ap.add_argument('--cache', type=Path, default=CACHE)
    ap.add_argument('--source', type=Path, help='a local copy of the asset, verified the same way')
    args = ap.parse_args(argv)
    try:
        root = fetch(args.tag, args.asset, args.sha256, args.repo, args.cache, source=args.source)
    except ValueError as error:
        sys.exit('fetch-archive: refused: ' + str(error))
    print(root)


if __name__ == '__main__': main()
