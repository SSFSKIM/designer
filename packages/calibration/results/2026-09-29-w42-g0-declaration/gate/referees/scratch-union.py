"""Write a stage's scratch union as one schema-5 file, for `VITREA_MATRIX_PATH` (W41 G2, §5.193).

`adopted-thresholds.test.ts` reads a scratch matrix as ONE file. This writes the union
`referee_source.py` builds from `--stage DIR` in the legacy envelope over each row's raw
bytes, so the file's SHA-256 is the legacy-envelope digest the ported L1 cut records and
the owner test can run every bound against the stage before anything is published. The
destination must lie outside the calibration package's results tree.

    python3.12 -B scratch-union.py --stage DIR --out /tmp/union.json
"""
import argparse
import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import referee_source  # noqa: E402
from referee_source import store  # noqa: E402

parser = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
referee_source.add_source_arguments(parser)
parser.add_argument('--out', type=Path, required=True)
args = parser.parse_args()
if args.stage is None:
    raise SystemExit('scratch-union: --stage is required; the current union is already canonical')
out = args.out.resolve()
if referee_source.RESULTS.resolve() in out.parents:
    raise SystemExit(f'scratch-union: {out} is inside the results tree; write scratch elsewhere')
source = referee_source.load(args)
raw = (b'{\n  "schemaVersion": 5,\n  "cells": [\n    ' +
       b',\n    '.join(store._RAW[id(row)] for row in source.rows) + b'\n  ]\n}\n')
if hashlib.sha256(raw).hexdigest() != source.legacy_sha256:
    raise SystemExit('scratch-union: envelope bytes differ from the legacy digest')
with out.open('xb') as f:
    f.write(raw)
print(f'{out}: {len(source.rows)} rows, sha256 {source.legacy_sha256}')
