#!/usr/bin/env python3.12
"""W45 G0 (b): X48 on a stage — the 1x light rows are the published c05 generation's, byte for byte.
W44 G1's `stage/x48.py` ported for W45 (charter clause 6, X48, X58); W44's committed copy is untouched.

Only 2x-anchored leaves moved (the scatter's, the second tap at its inert 1x width, and the
operator, which `rampAtScale(0, delta, dpr)` holds at 0 at dpr 1), so every 1x light row a stage
holds must equal the published c05 generation's row of the same (profile, tier, scene) once the two
fields that name HOW a row was drawn are set aside (`key.web.capturePath`, whose document clauses
name the new light documents, and `capturedAt`), and every 1x capture (the PNG and its alpha PNG)
must be byte-identical to the canonical tree's c05 capture. The dark documents are checked at their
published hashes against the generation index.

    python3.12 -B x48.py [--stage DIR] [--captures DIR] [--out FILE] [--with-holdout] [--only-stage-rows]

Defaults: G1's stage (`~/vitrea-w45/g1-stage-light`), this worktree's `web-captures`, `x48.json`
(or `x48-with-holdout.json`) in G1's `stage/`. G0's rehearsal runs it on the rehearsal stage
(`--stage ~/vitrea-w45/g0-stage-rehearsal --captures …/web-captures --out rehearsal/x48.json
--only-stage-rows`: that stage renders only the T1 gate cells, so the rest of c05's 1x rows are
counted as not staged rather than as missing).
A W44 stage, scratch or evidence path is refused (X58). Holdout and referee rows are compared only
with `--with-holdout`, after the exposure. The verdict is IDENTICAL only when nothing differs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "fit"))
import bindings as W  # noqa: E402

CAL = W.CAL
ONE_X = W.PROFILE[1]
SET_ASIDE = ("capturedAt",)


def strip(row: dict) -> dict:
    out = json.loads(json.dumps(row))
    for field in SET_ASIDE:
        out.pop(field, None)
    out["key"]["web"].pop("capturePath")
    return out


def digest(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def compare(stage_rows: list, captures: Path, with_holdout: bool) -> dict:
    B, _ = W.load_cuts()
    plan = W.referee_plan()
    held = plan.referee_cells(plan.load_manifest())
    excluded = lambda sid: (ONE_X, sid) in held or B.SCENES.role[sid] == "holdout"  # noqa: E731
    stage = [r for r in stage_rows if r["key"]["profileKey"] == ONE_X]
    c05 = {(r["key"]["web"]["renderer"], r["key"]["sceneId"]): r for r in B.load_published(W.C05["light"]).rows
           if r["key"]["profileKey"] == ONE_X}
    same_rows = same_png = 0
    rows_differ, png_differ, no_twin, read_held = [], [], [], 0
    for row in stage:
        tier, sid = row["key"]["web"]["renderer"], row["key"]["sceneId"]
        if excluded(sid):
            read_held += 1
            if not with_holdout:
                raise W.Refusal(f"{tier} {sid}: a holdout or referee row, compared only with --with-holdout")
        twin = c05.get((tier, sid))
        if twin is None:
            no_twin.append([tier, sid])
            continue
        if strip(row) == strip(twin):
            same_rows += 1
        else:
            a, b = strip(row), strip(twin)
            rows_differ.append(dict(cell=[tier, sid], fields=sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))))
        for suffix in ("", "__alpha"):
            name = f"{sid}__{tier}{suffix}.png"
            mine = digest(captures / ONE_X / sid / name)
            theirs = digest(W.CANONICAL_CAPTURES / ONE_X / sid / name)
            if mine is not None and mine == theirs:
                same_png += 1
            else:
                png_differ.append(dict(cell=[tier, sid, suffix or "png"], stage=mine, c05=theirs))
    have = {(r["key"]["web"]["renderer"], r["key"]["sceneId"]) for r in stage}
    stage_tiers = {r["key"]["web"]["renderer"] for r in stage}
    missing = [list(k) for k in c05 if k not in have and k[0] in stage_tiers
               and (with_holdout or not excluded(k[1]))]
    return dict(stageOneXRows=len(stage), heldRowsRead=read_held, c05OneXRows=len(c05),
                identicalRowsExceptHowDrawn=same_rows, rowsThatDiffer=rows_differ,
                identicalCaptures=same_png, capturesThatDiffer=png_differ,
                stageRowsWithNoC05Twin=no_twin, c05RowsTheStageLacks=missing)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--stage", type=Path, default=W.STAGE)
    ap.add_argument("--captures", type=Path, default=CAL / "web-captures")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--with-holdout", action="store_true")
    ap.add_argument("--only-stage-rows", action="store_true",
                    help="a partial stage (G0's rehearsal): compare the rows it holds and record, without "
                         "counting as a difference, the c05 rows it never declared to render")
    args = ap.parse_args(argv)
    W.require_shared()
    stage = W.refuse_w44_path(args.stage, "the stage")
    captures = W.refuse_w44_path(args.captures, "the stage's captures")
    out = W.refuse_w44_path(args.out or (W.G1_STAGE / ("x48-with-holdout.json" if args.with_holdout else "x48.json")),
                            "the X48 record")
    rows = json.loads((stage / "matrix.json").read_bytes())["cells"]
    result = compare(rows, captures, args.with_holdout)
    index = json.loads((CAL / "results/generations/index.json").read_bytes())
    dark_docs = {d["path"]: d["sha256"] for d in index["files"][f"{W.C05['dark']}.json"]["documents"]}
    dark = {p: dict(published=h, live=hashlib.sha256((W.ROOT / p).read_bytes()).hexdigest()[:12])
            for p, h in dark_docs.items()}
    dark_same = all(v["published"] == v["live"] for v in dark.values())
    if args.only_stage_rows:
        result["c05RowsNotStaged"] = len(result.pop("c05RowsTheStageLacks"))
    differs = (result["rowsThatDiffer"] or result["capturesThatDiffer"] or result["stageRowsWithNoC05Twin"]
               or result.get("c05RowsTheStageLacks") or not result["stageOneXRows"])
    result = dict(what="W45 X48: a stage's 1x light rows and captures against the published c05 generation",
                  stage=str(stage), **result, darkDocuments=dark, setAside=["key.web.capturePath", *SET_ASIDE],
                  verdict="IDENTICAL" if not differs and dark_same else "DIFFERS: STOP")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if not isinstance(v, list) or len(v) < 6}, indent=1))
    return 0 if result["verdict"] == "IDENTICAL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
