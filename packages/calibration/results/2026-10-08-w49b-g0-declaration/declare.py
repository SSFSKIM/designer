#!/usr/bin/env python3.12
"""Seal W49b's two prospective parts on the assembled tree; no amendment verb.

Unlike the W48 template's amendment machinery, this wave deliberately has none. Hash refuses
existing seals or any ladder render. Both parts pin relative source bytes; check never rewrites.
The living charter may grow after sealing: its approval is captured as a literal ruling payload,
while the tested laws, references, tools and native bed remain content-addressed by this seal.
"""
import argparse
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SCRATCH = Path('/Users/new/vitrea-w49/b-g0-scratch')
PARTS = ('declaration', 'fit-declaration')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def checked(part, directory=HERE, root=ROOT):
    path = directory / f'{part}.json'
    doc = load(path)
    if doc.get('schema') != f'w49b-{part}-1':
        raise ValueError('Wrong wave/part schema')
    if not doc.get('sources') or len({p['path'] for p in doc['sources']}) != len(doc['sources']):
        raise ValueError('Empty or duplicate source pins')
    for item in doc['sources']:
        target = (root / item['path']).resolve()
        if not target.is_relative_to(root.resolve()) or sha(target) != item['sha256']:
            raise ValueError(f'Changed or escaped source: {item["path"]}')
    if part == 'fit-declaration':
        if doc.get('noPostGateAmendment') is not True or doc.get('onFailure') != 'NEITHER: no seal, no publication, no re-selection':
            raise ValueError('Missing DL4 stop')
        if doc.get('partOneSha256') != sha(directory / 'declaration.json'):
            raise ValueError('Part two names another part one')
    return path


def seal(directory=HERE, root=ROOT, scratch=SCRATCH):
    if any((directory / f'{part}.sha256').exists() for part in PARTS):
        raise ValueError('Existing declaration: no rehash or amendment is admitted')
    if (scratch / 'renders').exists() and any((scratch / 'renders').iterdir()):
        raise ValueError('Ladder render exists: declaration must precede it')
    paths = [checked(part, directory, root) for part in PARTS]
    for path in paths:
        path.with_suffix('.sha256').write_text(f'{sha(path)}  {path.name}\n')


def verify(directory=HERE, root=ROOT):
    for part in PARTS:
        path = checked(part, directory, root)
        seal_file = path.with_suffix('.sha256')
        if seal_file.read_text() != f'{sha(path)}  {path.name}\n':
            raise ValueError(f'{part} bytes differ from seal')
        print(f'{part}: {sha(path)}; {len(load(path)["sources"])} source pins intact')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['hash', 'check'])
    args = parser.parse_args()
    if args.command == 'hash':
        seal()
    verify()
