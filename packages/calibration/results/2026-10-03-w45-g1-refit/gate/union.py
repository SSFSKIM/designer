#!/usr/bin/env python3.12
"""W45 G1 step 6: the scratch union the owner test's adapters read at the gate (charter clause 6;
claims §5.206). Writes one schema-5 matrix for `VITREA_MATRIX_PATH` (the single-file reader
override; never a publication input) and nothing else.

    python3.12 -B union.py --stage MATRIX --out FILE [--exposure]

The current union (W40's store: the frozen 26.5 rows and every current generation) with the two
light 0.25 profiles' rows replaced by the stage's: at the gate every stage row (calibration,
validation, recorded and the planner's pre-gate probe list), and the published c05 rows kept for
the cells the stage has not read yet — the referees and the canonical holdout, which are not
read before the exposure (each such row is named in the output's `keptFromC05`). With
`--exposure` the stage must hold every light 0.25 row the c05 generation does, and none is kept.
A stage row must be drawn with the sealed light documents (W45 G1), and the dark rows, the 0.5 rows
and the 26.5 rows are the store's, untouched.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[2]
sys.path.insert(0, str(CAL / "results" / "2026-09-26-w40-g0-generations"))
import matrix_store  # noqa: E402

LIGHT = ("apple-macos-27.0-1x-light-standard-glass0.25", "apple-macos-27.0-2x-light-standard-glass0.25")
ACTIVE = "packages/calibration/profiles/apple-macos-27.0-1x-light-standard-glass0.25.json"


def ident(r):
    return (r["key"]["profileKey"], r["key"]["web"]["renderer"], r["key"]["sceneId"])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--exposure", action="store_true")
    args = ap.parse_args()
    sealed = json.loads((CAL.parents[1] / ACTIVE).read_text())
    if sealed.get("recordedBy") != "W45 G1":
        raise SystemExit(f"{ACTIVE} is not sealed by W45 G1")
    current = matrix_store.load_current_rows(results_dir=CAL / "results")
    stage = json.loads(args.stage.read_bytes())["cells"]
    for r in stage:
        if r["key"]["profileKey"] not in LIGHT:
            raise SystemExit(f"{ident(r)}: the stage carries a row outside the two light 0.25 profiles")
    staged = {ident(r): r for r in stage}
    if len(staged) != len(stage):
        raise SystemExit("the stage carries two rows for one cell")
    c05_light = {ident(r): r for r in current if r["key"]["profileKey"] in LIGHT}
    kept = sorted(set(c05_light) - set(staged))
    extra = sorted(set(staged) - set(c05_light))
    if args.exposure and kept:
        raise SystemExit(f"--exposure: the stage lacks {len(kept)} rows the c05 generation has, e.g. {kept[:3]}")
    if extra:
        raise SystemExit(f"the stage holds {len(extra)} cells the c05 generation does not, e.g. {extra[:3]}")
    rows = [r for r in current if r["key"]["profileKey"] not in LIGHT] + stage + [c05_light[k] for k in kept]
    rows.sort(key=matrix_store.key)
    args.out.write_text(json.dumps(dict(schemaVersion=5, cells=rows)))
    record = dict(rows=len(rows), stageRows=len(stage), keptFromC05=[list(k) for k in kept],
                  replacedC05Rows=len(c05_light) - len(kept), currentUnionRows=len(current))
    args.out.with_suffix(".record.json").write_text(json.dumps(record, indent=1) + "\n")
    print(json.dumps({k: (v if k != "keptFromC05" else len(v)) for k, v in record.items()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
