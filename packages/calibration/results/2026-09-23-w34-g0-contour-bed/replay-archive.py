#!/usr/bin/env python3.12
"""Replay through the wave reader, with an optional enforced ban on raw roots."""
import argparse
import json
from pathlib import Path
import sys
import archive
from wave import Wave,default_wave


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('root',type=Path)
    ap.add_argument('--declaration',type=Path);ap.add_argument('--deny-raw-root',type=Path)
    args=ap.parse_args()
    if args.deny_raw_root:
        forbidden=str(args.deny_raw_root.resolve())
        def audit(event,values):
            if event=='open' and isinstance(values[0],(str,bytes)):
                path=str(Path(values[0]).resolve())
                if path==forbidden or path.startswith(forbidden+'/'):
                    raise PermissionError('raw inputs forbidden in archive-only proof')
        sys.addaudithook(audit)
    d=args.declaration
    wave=Wave(d/'scenes.json',d/'split.json',d/'pins.json') if d else default_wave()
    reader=wave.reader(args.root)
    cells=sorted({r['cell'] for r in reader.report_inventory() if r['cell'].split('/',1)[1] in reader.allowed})
    print(json.dumps(dict(rawRootForbidden=str(args.deny_raw_root),
        outputs=[archive.replay(reader,cell) for cell in cells]),indent=2))


if __name__=='__main__':main()
