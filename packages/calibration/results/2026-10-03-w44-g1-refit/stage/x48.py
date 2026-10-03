#!/usr/bin/env python3.12
"""W44 G1 step 5: X48 on the stage — the 1x light rows are the published generation's, byte for byte.

Only 2x-anchored scatter leaves and the second tap at its inert 1x width moved (Decision Log 1;
X48), so every 1x light row the stage holds must equal the published c05 generation's row of the
same (profile, tier, scene) once the two fields that name HOW a row was drawn are set aside
(`key.web.capturePath`, whose document clauses name the new light documents, and `capturedAt`),
and every 1x capture (the PNG and its alpha PNG) must be byte-identical to the canonical tree's
c05 capture. The dark scheme is not staged: its documents are unchanged by byte (checked here
against the generation index) and its published generation stays current.

    python3.12 -B x48.py [--with-holdout]     writes x48.json (or x48-with-holdout.json) beside this file

Holdout and referee rows are compared only with `--with-holdout`, after the exposure. The verdict
is IDENTICAL only when nothing differs: no row or capture that differs, no 1x light row of c05's in
the read partitions the stage lacks, and both dark documents at their published hash.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
CAL = EVIDENCE.parents[1]
sys.path.insert(0, str(EVIDENCE / "cuts"))
import bed as B  # noqa: E402

STAGE = Path.home() / "vitrea-w44" / "g1-stage-light"
STAGE_CAPTURES = CAL / "web-captures"
CANONICAL = Path("/Users/new/Developer/GitHub/designer/packages/calibration/web-captures")
ONE_X = "apple-macos-27.0-1x-light-standard-glass0.25"
SET_ASIDE = ("capturedAt",)


def strip(row: dict) -> dict:
    out = json.loads(json.dumps(row))
    for field in SET_ASIDE:
        out.pop(field, None)
    out["key"]["web"].pop("capturePath")
    return out


def digest(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def main() -> int:
    with_holdout = "--with-holdout" in sys.argv
    held = B.referee_plan.referee_cells(B.referee_plan.load_manifest())
    excluded = lambda sid: (ONE_X, sid) in held or B.SCENES.role[sid] == "holdout"  # noqa: E731
    stage = [r for r in json.loads((STAGE / "matrix.json").read_bytes())["cells"]
             if r["key"]["profileKey"] == ONE_X]
    c05 = {(r["key"]["web"]["renderer"], r["key"]["sceneId"]): r for r in B.load_published("6d18c059eb42").rows
           if r["key"]["profileKey"] == ONE_X}
    same_rows = same_png = 0
    rows_differ, png_differ, no_twin, read_held = [], [], [], 0
    for row in stage:
        tier, sid = row["key"]["web"]["renderer"], row["key"]["sceneId"]
        if excluded(sid):
            read_held += 1
            if not with_holdout:
                raise SystemExit(f"{tier} {sid}: a holdout or referee row, compared only with --with-holdout")
        twin = c05.get((tier, sid))
        if twin is None:
            no_twin.append([tier, sid])
            continue
        if strip(row) == strip(twin):
            same_rows += 1
        else:
            fields = sorted(k for k in set(strip(row)) | set(strip(twin)) if strip(row).get(k) != strip(twin).get(k))
            rows_differ.append(dict(cell=[tier, sid], fields=fields))
        for suffix in ("", "__alpha"):
            name = f"{sid}__{tier}{suffix}.png"
            a = digest(STAGE_CAPTURES / ONE_X / sid / name)
            b = digest(CANONICAL / ONE_X / sid / name)
            if a is not None and a == b:
                same_png += 1
            else:
                png_differ.append(dict(cell=[tier, sid, suffix or "png"], stage=a, c05=b))
    have = {(r["key"]["web"]["renderer"], r["key"]["sceneId"]) for r in stage}
    missing = [list(k) for k in c05 if k not in have and (with_holdout or not excluded(k[1]))]
    index = json.loads((CAL / "results/generations/index.json").read_bytes())
    dark_docs = {d["path"]: d["sha256"] for d in index["files"]["d0219cd684bf.json"]["documents"]}
    dark = {p: dict(published=h, live=hashlib.sha256((B.ROOT / p).read_bytes()).hexdigest()[:12])
            for p, h in dark_docs.items()}
    dark_same = all(v["published"] == v["live"] for v in dark.values())
    result = dict(
        what="W44 G1 step 5, X48: the stage's 1x light rows and captures against the published c05 generation",
        stageOneXRows=len(stage), heldRowsRead=read_held, c05OneXRows=len(c05),
        identicalRowsExceptHowDrawn=same_rows, rowsThatDiffer=rows_differ,
        identicalCaptures=same_png, capturesThatDiffer=png_differ,
        stageRowsWithNoC05Twin=no_twin, c05RowsTheStageLacks=missing,
        darkDocuments=dark, setAside=["key.web.capturePath", *SET_ASIDE],
        verdict=("IDENTICAL" if not (rows_differ or png_differ or no_twin or missing) and dark_same
                 else "DIFFERS: STOP"))
    out = "x48-with-holdout.json" if with_holdout else "x48.json"
    (HERE / out).write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if not isinstance(v, list) or len(v) < 6}, indent=1))
    return 0 if result["verdict"] == "IDENTICAL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
