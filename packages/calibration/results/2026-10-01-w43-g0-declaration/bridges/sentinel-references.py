#!/usr/bin/env python3.12
"""W43 G0 (e): the reference frames of W42's two sentinel cells, read from w42-archive (clause 3).

    python3.12 -B sentinel-references.py <w42 archive root> [--deny <path> ...]   # writes sentinel-references.json

Each sitting's sentinel bridge compares its long-protocol captures at 0.5 with W42 G1's long-protocol
sentinel rows of the same cell and endpoint. The protocol matters: in the active pose the long and
normal protocols settle on different frames (five of the eight active cell-endpoints differ), so a
sentinel is never compared with the normal-protocol bed rows. Read through the guarded Reader with the
probe role only; H is never requested. Records each row's run, frame SHA-256 and admitted state counts.
"""
import argparse
import collections
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SITTING = HERE.parents[1] / '2026-09-29-w42-g0-declaration/bed/sitting'
INVENTORY = '5481795e0a77ef246f6743d2b6bbe2111a79d858ff9b7a2a4571255595940ed7'


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('archive', type=Path)
    ap.add_argument('--deny', type=Path, action='append', default=[])
    args = ap.parse_args()
    spec = importlib.util.spec_from_file_location('w42_archive_for_sentinels', SITTING / 'w42_archive.py')
    archive = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(archive)
    for path in args.deny:
        archive.deny(path)
    if archive.verify_tree(args.archive)['inventorySha256'] != INVENTORY:
        raise SystemExit('not w42-archive')
    cells = json.loads((HERE / 'bridge-cells.json').read_text())['sentinels']['byEndpoint']
    reader = archive.wave_module().default_wave().reader(args.archive, roles=('probe',))
    out = {}
    for endpoint, row in cells.items():
        for sid in row['scenes']:
            header, _ = archive.unbundle(reader.read(f"{row['profile']}/{sid}", 'states'))
            for protocol in ('long', 'normal'):
                runs = [r for r in header['runs'] if r['protocol'] == protocol]
                out.setdefault(endpoint, {}).setdefault(sid, {})[protocol] = dict(
                    runs=len(runs), states=dict(collections.Counter(r['frame'] for r in runs).most_common()))
    differ = sorted(f'{e} {s}' for e, v in out.items() for s, p in v.items()
                    if set(p['long']['states']) != set(p['normal']['states']))
    value = dict(schema='w43-sentinel-references-1', archiveInventorySha256=INVENTORY, roles=['probe'],
                 deniedPaths=[str(p) for p in args.deny], referenceProtocol='long', byEndpoint=out,
                 longDiffersFromNormal=differ)
    (HERE / 'sentinel-references.json').write_text(json.dumps(value, indent=1, sort_keys=True) + '\n')
    print(f'{sum(len(v) for v in out.values())} sentinel cell-endpoints; long and normal protocols settle on '
          f'different frames in {len(differ)}: {differ}')


if __name__ == '__main__':
    main()
