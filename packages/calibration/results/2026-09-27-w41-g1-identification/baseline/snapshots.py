"""Preserve byte-identical baseline evidence, while primary captures stay scratch.

This copies already-frozen web PNG/projection bytes. It neither renders nor opens
any native payload. A consumer may select its unclaimed cells from the map.
"""
import hashlib
from pathlib import Path


def copy_payloads(root, evidence, captures):
    root, evidence = Path(root), Path(evidence)
    directory = evidence / 'capture-payloads'
    payloads, cells = {}, {}
    for cell, capture in sorted(captures.items()):
        entry = {}
        for kind, suffix, path in [('png', '.png', Path(capture['png'])),
                                   ('projection', '.json', root / capture['projection'])]:
            raw = path.read_bytes()
            digest = hashlib.sha256(raw).hexdigest()
            if digest != capture[kind + 'Sha256']:
                raise ValueError('frozen source changed: ' + str(path))
            name = digest + suffix
            payloads[name] = raw
            entry[kind] = str((directory / name).relative_to(root))
        cells[cell] = entry
    directory.mkdir(exist_ok=False)
    for name, raw in payloads.items():
        with (directory / name).open('xb') as f: f.write(raw)
    return {'cells': cells}


def main():
    import baseline as b
    record = b.load(b.HERE / 'preparation.json')
    frozen = b.load(b.HERE / 'frozen-baseline.json')
    b.verify_preparation(record)
    b.verify_authority(record)
    b.verify_frozen(record, frozen)
    result = copy_payloads(b.ROOT, b.HERE, frozen['captures'])
    b.save(b.HERE / 'committed-payloads.json', result)
    artifacts = {path: b.sha(b.ROOT / path) for entry in result['cells'].values()
                 for path in entry.values()}
    b.save(b.HERE / 'snapshot-inventory.json', {'recordedAt': b.stamp(),
           'frozenBaselineSha256': b.sha(b.HERE / 'frozen-baseline.json'),
           'mapSha256': b.sha(b.HERE / 'committed-payloads.json'),
           'artifacts': artifacts, 'cells': len(result['cells']),
           'origin': 'Byte-identical copies of frozen web-only calibration/validation captures.'})
    print('Snapshotted', len(result['cells']), 'cells into', len(artifacts), 'unique payloads')


if __name__ == '__main__': main()
