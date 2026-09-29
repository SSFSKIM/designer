"""Metadata-only conversion of a committed W39 candidate freeze to the sheet contract."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]


def convert(raw, frozen, seal, selected):
    captures = {}; roots = set(); documents = {}
    for cell in selected:
        profile, sid = cell.split('/', 1)
        row = raw['cells'][cell]
        primary = Path(row['primaryCapture'])
        if (not primary.is_absolute() or '..' in primary.parts or
            primary.name != sid + '__webgpu.png' or primary.parent.name != sid or
            primary.parent.parent.name != profile or primary.parents[2].name != 'calval'):
            raise ValueError('candidate primary capture is misfiled: ' + cell)
        roots.add(str(primary.parents[2]))
        for key in ('png', 'descriptor', 'report'):
            if frozen['files'].get(row[key]) != row[key + 'Sha256']:
                raise ValueError('candidate payload not bound by frozen envelope')
        captures[cell] = dict(png=str(primary), pngSha256=row['pngSha256'],
                             cellSha256=row['descriptorSha256'], reportSha256=row['reportSha256'])
        pair = seal['profiles'][profile]
        documents[profile] = [dict(kind=kind, path=pair[key], sha256=seal['inputs'][pair[key]][:12])
            for key, kind in [('material', 'materialProfile'), ('receded', 'recededProfile')]]
    if len(roots) != 1: raise ValueError('one actual candidate calval capture root required')
    return dict(captureRoot=roots.pop(), captures=captures, documents=documents,
                nativePayloadReads=0, capturePngReads=0,
                note='Metadata conversion only. PNG/descriptor/report bytes are checked by the sheet renderer.')


def committed(path):
    path = Path(path).resolve()
    if not path.is_relative_to(ROOT) or path.suffix != '.json': raise ValueError('committed JSON input required')
    name = str(path.relative_to(ROOT))
    data = path.read_bytes()
    prior = subprocess.check_output(['git', '-C', str(ROOT), 'show', 'HEAD:' + name])
    if data != prior: raise ValueError('input differs from committed bytes: ' + name)
    return json.loads(data), dict(path=name, sha256=hashlib.sha256(data).hexdigest())


def derive(attempt, output):
    if not re.fullmatch(r'[a-zA-Z0-9_-]+', attempt): raise ValueError('unsafe attempt name')
    directory = HERE.parent / 'candidate-capture' / attempt
    frozen, frozen_pin = committed(directory / 'frozen.json')
    raw, raw_pin = committed(directory / 'raw-inventory.json')
    seal, seal_pin = committed(directory / 'seal.json')
    preparation, scope_pin = committed(HERE.parent / 'baseline/preparation.json')
    if seal['inputs'].get(scope_pin['path']) != scope_pin['sha256']:
        raise ValueError('admission scope differs from candidate seal')
    if (frozen['files'].get(raw_pin['path']) != raw_pin['sha256'] or
        frozen['sealSha256'] != seal_pin['sha256'] or raw['sealSha256'] != seal_pin['sha256'] or
        frozen['files'].get(seal_pin['path']) != seal_pin['sha256']):
        raise ValueError('raw inventory/seal differs from original frozen envelope')
    selected = preparation['cells']
    if len(selected) != 536 or len(set(selected)) != 536: raise ValueError('536 admitted calval cells required')
    result = convert(raw, frozen, seal, selected)
    expected = Path('/Users/new/vitrea-w41/g1-captures/candidate-e3') / attempt / 'calval'
    if result['captureRoot'] != str(expected): raise ValueError('unexpected primary capture root')
    for pair in result['documents'].values():
        for doc in pair:
            _, pin = committed(ROOT / doc['path'])
            if pin['sha256'] != seal['inputs'][doc['path']]: raise ValueError('candidate document changed')
    result.update(sourceFrozen=frozen_pin, sourceRawInventory=raw_pin, sourceSeal=seal_pin,
                  admissionScope=scope_pin)
    output = Path(output).resolve()
    if not output.is_relative_to(HERE) or output.suffix != '.json': raise ValueError('new sheet JSON output required')
    with output.open('x') as stream:
        json.dump(result, stream, indent=2, sort_keys=True); stream.write('\n')
    print('Derived 536 calval metadata records; commit before rendering:', output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('attempt'); parser.add_argument('output')
    args = parser.parse_args()
    derive(args.attempt, args.output)
