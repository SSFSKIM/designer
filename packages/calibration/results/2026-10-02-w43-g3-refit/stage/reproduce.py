#!/usr/bin/env python3.12
"""W43 G3 (ii): the stage reads reproduce candidate c05's scratch rows, byte for byte (a check;
a difference is a stop).

The sealed documents carry c05's patches leaf for leaf and the shipped 0.25 module carries the
sealed documents' (both pinned in `macos27-profile-export.test.ts`), and G0 (f) proved candidate
mode and strict mode draw byte-identical pixels for one content. So every stage capture must be
byte-identical to c05's capture of the same cell, and every stage row equal to c05's once the two
fields that name HOW it was drawn are set aside: `key.web.capturePath` (strict document clauses
against the candidate clause) and `capturedAt`.

    python3.12 -B reproduce.py [--with-holdout]   # writes reproduce.json beside this file

Holdout rows are compared only with `--with-holdout`, after the holdout read; c05 never read them,
so they have no twin and are counted apart.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[2]
STAGES = {s: Path.home() / "vitrea-w43" / f"g3-stage-{s}" for s in ("light", "dark")}
STAGE_CAPTURES = CAL / "web-captures"
C05 = Path.home() / "vitrea-w43" / "g3-scratch" / "fit" / "c05"
SET_ASIDE = ("capturedAt",)


def strip(row: dict) -> dict:
    out = json.loads(json.dumps(row))
    for field in SET_ASIDE:
        out.pop(field, None)
    out["key"]["web"].pop("capturePath")
    return out


def png(root: Path, row: dict) -> str | None:
    sid, renderer = row["key"]["sceneId"], row["key"]["web"]["renderer"]
    path = root / row["key"]["profileKey"] / sid / f"{sid}__{renderer}.png"
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def main() -> int:
    with_holdout = "--with-holdout" in sys.argv
    c05 = {(r["key"]["profileKey"], r["key"]["web"]["renderer"], r["key"]["sceneId"]): r
           for r in json.loads((C05 / "matrix.json").read_text())["cells"]}
    stage_rows = []
    for scheme, stage in STAGES.items():
        stage_rows += json.loads((stage / "matrix.json").read_text())["cells"]
    identical_rows = identical_png = 0
    differs_row, differs_png, no_twin, holdout = [], [], [], 0
    for row in stage_rows:
        key = (row["key"]["profileKey"], row["key"]["web"]["renderer"], row["key"]["sceneId"])
        if row["fixtureSet"] == "holdout":
            holdout += 1
            if not with_holdout:
                raise SystemExit(f"{key}: a holdout row, compared only with --with-holdout")
            continue
        twin = c05.get(key)
        if twin is None:
            no_twin.append(key)
            continue
        if strip(row) == strip(twin):
            identical_rows += 1
        else:
            differs_row.append(key)
        a, b = png(STAGE_CAPTURES, row), png(C05 / "web-captures", twin)
        if a is not None and a == b:
            identical_png += 1
        else:
            differs_png.append(dict(key=key, stage=a, c05=b))
    result = dict(
        what="W43 G3 (ii): stage rows and captures against candidate c05's scratch read",
        stageRows=len(stage_rows), holdoutRows=holdout, c05Rows=len(c05),
        identicalRowsExceptHowDrawn=identical_rows, rowsThatDiffer=[list(k) for k in differs_row],
        identicalCaptures=identical_png, capturesThatDiffer=differs_png,
        stageRowsWithNoC05Twin=[list(k) for k in no_twin],
        c05RowsWithNoStageRow=[list(k) for k in c05 if k not in
                               {(r["key"]["profileKey"], r["key"]["web"]["renderer"], r["key"]["sceneId"])
                                for r in stage_rows}],
        setAside=["key.web.capturePath", *SET_ASIDE],
        verdict=("REPRODUCED" if not differs_row and not differs_png and not no_twin else "DIFFERS: STOP"))
    (HERE / "reproduce.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if not isinstance(v, list) or len(v) < 8},
                     indent=1))
    return 0 if result["verdict"] == "REPRODUCED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
