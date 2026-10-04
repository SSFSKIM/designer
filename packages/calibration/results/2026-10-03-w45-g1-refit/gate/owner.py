#!/usr/bin/env python3.12
"""W45 G1 step 6: the owner test's adapters on the stage's scratch union, against the new cut
(charter clause 6; claims §5.206). Writes nothing outside --out except one scratch test file,
created and removed here.

    python3.12 -B owner.py --union FILE --cut FILE --bands FILE --out DIR

`adopted-thresholds.test.ts` reads three things the gate replaces, and nothing else changes:
- **the rows**, through W40's store, which `VITREA_MATRIX_PATH` redirects to the scratch union
  (`union.py`: the current union, the light 0.25 rows the stage's);
- **the 0.25 cut**, `GLASS025_CUT`, which names W43's `cut-025.json` by path: the scratch copy
  names the new cut instead;
- **the T-band fixture**, `T1_BANDS_FILE`: the scratch copy names a merged scratch fixture, the
  reference's entries (W44 G2's, unchanged) plus the candidate's gate entries (`t1/bands.py gate`).
  Clause (b) looks up both the candidate's and the reference's T cells through it (G2's five-part
  order, part (iii) read early, as the gate's witness; nothing moves).

The copy is `test/zz-w45-g1-gate-owner.test.ts`, run by vitest from the package and removed in a
`finally`. Everything else in the owner test is the committed file's, byte for byte, so each
failure is the committed test's verdict on the stage. A failure is recorded as a failure; the
expected ones are named in the ledger (pins re-derived at G2, the T1 clause (b) witness).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[2]
OWNER = CAL / "test" / "adopted-thresholds.test.ts"
SCRATCH_TEST = CAL / "test" / "zz-w45-g1-gate-owner.test.ts"
W43_CUT = 'resolve(PACKAGE_ROOT, "results", "2026-10-02-w43-g3-landing", "cuts", "cut-025.json")'
BANDS = re.compile(r'const T1_BANDS_FILE = \{\n  path: "[^"]+",\n  sha256: "[0-9a-f]+",\n\} as const;')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--union", type=Path, required=True)
    ap.add_argument("--cut", type=Path, required=True)
    ap.add_argument("--bands", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    text = OWNER.read_text()
    if text.count(W43_CUT) != 1 or len(BANDS.findall(text)) != 1:
        raise SystemExit("the owner test no longer names the cut or the band fixture where this adapter expects")
    bands_sha = hashlib.sha256(args.bands.read_bytes()).hexdigest()
    copy = text.replace(W43_CUT, f'resolve(PACKAGE_ROOT, {json.dumps(str(args.cut.resolve()))})')
    copy = BANDS.sub(f'const T1_BANDS_FILE = {{\n  path: {json.dumps(str(args.bands.resolve()))},\n'
                     f'  sha256: "{bands_sha}",\n}} as const;', copy)
    args.out.mkdir(parents=True, exist_ok=True)
    if SCRATCH_TEST.exists():
        raise SystemExit(f"{SCRATCH_TEST} exists; remove it first")
    SCRATCH_TEST.write_text(copy)
    try:
        env = dict(os.environ, VITREA_MATRIX_PATH=str(args.union.resolve()))
        with (args.out / "owner.txt").open("w") as log:
            got = subprocess.run(["pnpm", "exec", "vitest", "run", str(SCRATCH_TEST.relative_to(CAL)),
                                  "--reporter=verbose", "--reporter=json",
                                  f"--outputFile.json={args.out / 'owner.json'}"],
                                 cwd=CAL, env=env, stdout=log, stderr=subprocess.STDOUT)
    finally:
        SCRATCH_TEST.unlink()
    record = dict(owner=str(OWNER.relative_to(CAL)), ownerSha256=hashlib.sha256(OWNER.read_bytes()).hexdigest(),
                  union=str(args.union), unionSha256=hashlib.sha256(args.union.read_bytes()).hexdigest(),
                  cut=str(args.cut), cutSha256=hashlib.sha256(args.cut.read_bytes()).hexdigest(),
                  bands=str(args.bands), bandsSha256=bands_sha, vitestExit=got.returncode)
    (args.out / "owner-record.json").write_text(json.dumps(record, indent=1) + "\n")
    print(json.dumps(record, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
