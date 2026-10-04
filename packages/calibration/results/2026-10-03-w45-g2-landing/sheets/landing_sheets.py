#!/usr/bin/env python3.12
"""W45 G2: the landing's eye sheets over the whole light bed (charter clause 10; claims §5.207),
drawn from the trees as the landing left them.

W45 G0's `sheets/sheets.py` unchanged (native | vitrea c05 | vitrea W45 | |W45 - Apple| x4 |
|c05 - Apple| x4 | |W45 - c05| x4, `--whole`), with two inputs the landing moved:
  - W45's rows are the published generation `ebc3d9105a4a` read through the store (written to one
    scratch matrix, since the tool reads a matrix file), and its captures are the CANONICAL tree
    the landing copied them into;
  - c05's captures are read from `web-captures-superseded/6d18c059eb42/`, where the landing moved
    them: the tool's c05 root (`bindings.CANONICAL_CAPTURES`) is rebound to it for this run.
The tool's per-cell assertion still runs on every capture before any pixel is read, so a sheet is
drawn only if both trees hold exactly the captures their rows name.

    python3.12 -B landing_sheets.py --out DIR
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[2]
SHEETS = CAL / "results" / "2026-10-03-w45-g0-operator" / "sheets"
sys.path.insert(0, str(SHEETS))
import sheets as S  # noqa: E402

CANONICAL = Path("/Users/new/Developer/GitHub/designer/packages/calibration/web-captures")
SUPERSEDED_C05 = CANONICAL.parent / "web-captures-superseded" / "6d18c059eb42"
CUT = CAL / "results" / "2026-10-03-w45-g2-landing" / "cuts" / "cut-025-w45-landing.json"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    B, _ = S.W.load_cuts()
    rows = B.load_published("ebc3d9105a4a").rows
    args.out.mkdir(parents=True, exist_ok=False)
    matrix = args.out.parent / f"{args.out.name}-published-ebc3d9105a4a.json"
    matrix.write_text(json.dumps(dict(schemaVersion=5, cells=rows)))
    S.W.CANONICAL_CAPTURES = SUPERSEDED_C05
    return S.main(["--stage", str(matrix), "--stage-captures", str(CANONICAL), "--out", str(args.out),
                   "--cut", str(CUT), "--whole"])


if __name__ == "__main__":
    raise SystemExit(main())
