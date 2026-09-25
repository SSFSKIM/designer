#!/usr/bin/env python3.12
"""Replay the W39 archive through the wave reader, with an enforced ban on raw roots (§5.184).

Derived from W34 G0's `replay-archive.py`. `root` is the extracted archive
(what `fetch-archive.py` prints); only the roles the reader authorises are
replayed (calibration and validation by default; holdout needs the receipt,
which this command never holds). `--deny-raw-root` installs an audit hook that
refuses any open under the raw capture root, so a pass proves the statistics
come from the archive alone.
"""
import argparse
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import w39_archive  # noqa: E402
from wave import Wave, default_wave  # noqa: E402


def deny(root):
    forbidden = str(Path(root).resolve())

    def audit(event, values):
        if event == 'open' and isinstance(values[0], (str, bytes)):
            path = str(Path(values[0].decode() if isinstance(values[0], bytes) else values[0]).resolve())
            if path == forbidden or path.startswith(forbidden + '/'):
                raise PermissionError('raw inputs forbidden in archive-only proof')
    sys.addaudithook(audit)


def main(argv=None, analyse=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('root', type=Path)
    ap.add_argument('--declaration', type=Path,
                    help='directory holding scenes.json, split.json, pins.json (tests); default the pinned W39 bed')
    ap.add_argument('--roles', default='calibration,validation')
    ap.add_argument('--deny-raw-root', type=Path)
    args = ap.parse_args(argv)
    d = args.declaration
    wave = Wave(d / 'scenes.json', d / 'split.json', d / 'pins.json') if d else default_wave()
    analyse = analyse or w39_archive.default_analyse()
    if args.deny_raw_root: deny(args.deny_raw_root)
    reader = wave.reader(args.root, roles=args.roles.split(','))
    cells = sorted({r['cell'] for r in reader.report_inventory() if r['cell'].split('/', 1)[1] in reader.allowed})
    outputs = [w39_archive.replay(reader, cell, analyse) for cell in cells]
    print(json.dumps(dict(rawRootForbidden=str(args.deny_raw_root), roles=args.roles.split(','),
                          generation=reader.generation, cells=len(outputs),
                          identical=all(o['identical'] for o in outputs), outputs=outputs), indent=2))


if __name__ == '__main__': main()
