#!/usr/bin/env python3.12
"""W47 G0 (c): X60 — the dark 0.25 material alone moves. W46 G0's `stage/x60.py`
(`results/2026-10-05-w46-g0-declaration/stage/x60.py`) ported by copy for W47 (charter clause 2, X60
carried); W46's committed copy is untouched.

What the port changes, and nothing else: W47's bindings (the candidate roots are W47's ladders, G1's
fit and the level check's candidates; the capture trees scanned are `~/vitrea-w47`'s and W47's
worktrees'), and the dark withheld cells read through W47's X69 loader (`w46-referees-1` by hash and
the seven dark holdout scenes per scale). X60's statement is W46's: every light 0.25 row, both 0.5
generations, the frozen 26.5 rows and the light and 0.5 documents unchanged.

W46 G0's text follows, unchanged; where it says W46 it is W47.

W46 G0 (a): X60 — the dark 0.25 material alone moves. W45 G0's `stage/x48.py`
(`results/2026-10-03-w45-g0-operator/stage/x48.py`) replaced, as the charter's X60 replaces X48; W45's
committed copy is untouched.

X48 read W45's 1x light rows against c05 because W45 moved only 2x-anchored light leaves. W46 moves
the DARK documents only, so what must not move is every light 0.25 row, both 0.5 generations, the
frozen 26.5 rows and the light and 0.5 documents. X60 reads that two ways (charter X60; Design "The
populations per phase"):

  render     a stage's LIGHT 0.25 rows — the light profiles' non-withheld cells, 138 scenes per scale
             per tier at the gate — against the published light generation `ebc3d9105a4a`: each row
             equal to its published twin but for `capturedAt` (the light documents are the snapshots'
             bytes, so `capturePath` names the same documents and must match too), and each capture
             (the PNG and its alpha PNG) byte-identical to the canonical tree's. A light WITHHELD row
             (the 20 holdout scenes and W44's six referees per scale, spent at read 7) refuses: the
             light holdout and W44's referees are never re-rendered.
  evidence   the light withheld cells and everything X60 holds without a render: the live light 0.25
             documents are the light snapshots' bytes (X62); both 0.5 generation files and their index
             entries are at their frozen hashes; the frozen 26.5 `results/matrix.json` is unchanged;
             every W46 candidate's light endpoints are patch- and digest-identical to the light
             snapshots (a candidate builds from the snapshots and the builder refuses a light override,
             so this is the per-rung form of X60); and NO capture of a light withheld cell, nor of a
             dark withheld cell before the exposure, exists in any W46 scratch tree under `~/vitrea-w46`
             or in a W46 worktree's `packages/calibration/web-captures`.

The verdict is IDENTICAL only when nothing differs.

    python3.12 -B x60.py render --stage DIR [--captures DIR] [--out FILE] [--only-stage-rows]
    python3.12 -B x60.py evidence [--candidate DIR ...] [--after-exposure] [--out FILE]

Defaults: `render` reads G1's light X60 stage's own `web-captures`, `evidence` scans the ladders' and
G1's candidate folders and the level check's; records go to G1's `stage/` (G0 passes `--out` into
`stage/x60/`). W44's and W45's stages, scratch and evidence are refused.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import bindings as W  # noqa: E402

CAL = W.CAL
SET_ASIDE = ("capturedAt",)
# The frozen 26.5 rows (`freeze.py verify`'s file), its bytes at W46's charter merge b711762ae and at
# W47's c1f9bf84c alike.
FROZEN_265_MATRIX = CAL / "results" / "matrix.json"
FROZEN_265_SHA = "a0b9720b079dc28980d097ddd47cd2d005e79dc011aa8c81f8bf887353d57843"
LIGHT_SLOTS = ("active.light", "receded.light")
SCRATCH_ROOT = W.SCRATCH
CANDIDATE_ROOTS = (W.LADDERS / "candidates", W.G1_FIT / "candidates", W.G0 / "level" / "candidates")


def digest(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def strip(row: dict) -> dict:
    out = json.loads(json.dumps(row))
    for field in SET_ASIDE:
        out.pop(field, None)
    return out


def withheld() -> dict:
    """{"light": {(profile, scene)}, "dark": {(profile, scene)}}: the cells nothing renders before the
    exposure (the dark ones) or ever again (the light ones)."""
    B, _, _ = W.load_cuts()
    plan = W.referees()
    scenes = plan.load_scenes()
    manifest = plan.load_manifest(scenes=scenes)
    dark = {(p, s) for p in W.DARK_025 for s in plan.withheld(manifest, scenes)}
    return dict(light=set(B.LIGHT_WITHHELD), dark=dark)


# ---------------------------------------------------------------------------------------------
# render
# ---------------------------------------------------------------------------------------------
def compare(stage_rows: list, captures: Path) -> dict:
    B, _, _ = W.load_cuts()
    held = withheld()["light"]
    stage = [r for r in stage_rows if r["key"]["profileKey"] in W.LIGHT_025]
    published = {(r["key"]["profileKey"], r["key"]["web"]["renderer"], r["key"]["sceneId"]): r
                 for r in B.load_published(W.REFERENCE["light"]).rows if r["key"]["profileKey"] in W.LIGHT_025}
    same_rows = same_png = 0
    rows_differ, png_differ, no_twin = [], [], []
    for row in stage:
        p, tier, sid = row["key"]["profileKey"], row["key"]["web"]["renderer"], row["key"]["sceneId"]
        if (p, sid) in held:
            raise W.Refusal(f"{p} {tier} {sid}: a light withheld cell (holdout or W44 referee), spent at read 7 "
                            "and never re-rendered (X60)")
        twin = published.get((p, tier, sid))
        if twin is None:
            no_twin.append([p, tier, sid])
            continue
        if strip(row) == strip(twin):
            same_rows += 1
        else:
            a, b = strip(row), strip(twin)
            rows_differ.append(dict(cell=[p, tier, sid], fields=sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))))
        for suffix in ("", "__alpha"):
            name = f"{sid}__{tier}{suffix}.png"
            mine = digest(captures / p / sid / name)
            theirs = digest(W.CANONICAL_CAPTURES / p / sid / name)
            if mine is not None and mine == theirs:
                same_png += 1
            else:
                png_differ.append(dict(cell=[p, tier, sid, suffix or "png"], stage=mine, published=theirs))
    have = {(r["key"]["profileKey"], r["key"]["web"]["renderer"], r["key"]["sceneId"]) for r in stage}
    tiers = {r["key"]["web"]["renderer"] for r in stage}
    lacks = [list(k) for k in published if k not in have and k[1] in tiers and (k[0], k[2]) not in held]
    return dict(stageLightRows=len(stage), publishedLightRows=len(published),
                identicalRowsButCapturedAt=same_rows, rowsThatDiffer=rows_differ,
                identicalCaptures=same_png, capturesThatDiffer=png_differ,
                stageRowsWithNoPublishedTwin=no_twin, publishedRowsTheStageLacks=lacks)


def render(args) -> dict:
    stage = W.refuse_other_wave_path(args.stage, "the stage")
    captures = W.refuse_other_wave_path(args.captures or (stage / "web-captures"), "the stage's captures")
    rows = json.loads((stage / "matrix.json").read_bytes())["cells"]
    result = compare(rows, captures)
    if args.only_stage_rows:
        result["publishedRowsNotStaged"] = len(result.pop("publishedRowsTheStageLacks"))
    differs = (result["rowsThatDiffer"] or result["capturesThatDiffer"] or result["stageRowsWithNoPublishedTwin"]
               or result.get("publishedRowsTheStageLacks") or not result["stageLightRows"])
    return dict(what="W47 X60 (render): a stage's light 0.25 rows and captures against the published "
                     f"{W.REFERENCE['light']} generation", stage=str(stage), **result,
                setAside=list(SET_ASIDE), verdict="DIFFERS: STOP" if differs else "IDENTICAL")


# ---------------------------------------------------------------------------------------------
# evidence
# ---------------------------------------------------------------------------------------------
def light_documents() -> list[str]:
    out = []
    for slot in LIGHT_SLOTS:
        path = CAL / "profiles" / f"{W.DOCUMENT_KEY[slot]}.json"
        if digest(path) != W.DOCUMENT_SHA[slot]:
            out.append(f"{path.relative_to(W.ROOT)} hashes to {digest(path)[:12]}, not the light snapshot "
                       f"{W.DOCUMENT_SHA[slot][:12]}")
    return out


def frozen_files() -> list[str]:
    out = []
    index = json.loads((CAL / "results/generations/index.json").read_bytes())
    for active, file_sha in W.FROZEN_05_GENERATIONS.items():
        entry = index["files"].get(f"{active}.json")
        got = digest(CAL / "results/generations" / f"{active}.json")
        if entry is None or not entry["sha256"].startswith(file_sha):
            out.append(f"generations/index.json's entry for {active}.json is not at {file_sha}")
        if got is None or not got.startswith(file_sha):
            out.append(f"generations/{active}.json hashes to {got and got[:12]}, not {file_sha}")
    for key in W.TWIN_05:
        try:
            W.twin_path(key)
        except W.Refusal as err:
            out.append(str(err))
    if digest(FROZEN_265_MATRIX) != FROZEN_265_SHA:
        out.append(f"results/matrix.json (the frozen 26.5 rows) moved from {FROZEN_265_SHA[:12]}")
    return out


def candidate_folders(given) -> list[Path]:
    folders = [W.refuse_other_wave_path(g, "--candidate") for g in given]
    for root in CANDIDATE_ROOTS:
        if root.exists():
            folders += sorted(p.parent for p in root.glob("*/candidate.json"))
    return list(dict.fromkeys(folders))


def light_endpoints(folders) -> tuple[int, list[str]]:
    snapshots = {slot: W.document(slot) for slot in LIGHT_SLOTS}
    out = []
    for folder in folders:
        body = json.loads((folder / "candidate.json").read_text())
        for slot in LIGHT_SLOTS:
            entry = body["endpoints"].get(slot)
            if entry is None:
                out.append(f"{folder}: no {slot} endpoint")
                continue
            doc = json.loads((folder / entry["path"]).read_text())
            if doc.get("patch") != snapshots[slot]["patch"]:
                out.append(f"{folder.name} {slot}: its patch is not the light snapshot's")
            if doc.get("resolvedMaterialSha256") != snapshots[slot]["resolvedMaterialSha256"]:
                out.append(f"{folder.name} {slot}: digest {doc.get('resolvedMaterialSha256')}, not the snapshot's "
                           f"{snapshots[slot]['resolvedMaterialSha256']}")
    return len(folders), out


def capture_trees(root: Path = SCRATCH_ROOT) -> list[Path]:
    """Every `web-captures` tree W47 can have written: under `~/vitrea-w47`'s scratch and stages (not
    descending into a worktree's checkout or `node_modules`), and each W47 worktree's own
    `packages/calibration/web-captures` (gitignored; where a G1 stage lands its captures)."""
    trees = []
    if not root.exists():
        return trees
    for top in sorted(root.iterdir()):
        if not top.is_dir():
            continue
        if (top / ".git").exists():          # a W46 worktree
            tree = top / "packages" / "calibration" / "web-captures"
            if tree.is_dir():
                trees.append(tree)
            continue
        for dirpath, dirnames, _ in os.walk(top):
            dirnames[:] = [d for d in dirnames if d not in ("node_modules", ".git")]
            if Path(dirpath).name == "web-captures":
                trees.append(Path(dirpath))
                dirnames[:] = []
    return trees


def withheld_captures(trees, after_exposure: bool) -> list[str]:
    held = withheld()
    out = []
    for tree in trees:
        for cell in (sorted(p for p in tree.glob("*/*") if p.is_dir())):
            key = (cell.parent.name, cell.name)
            if not any(cell.iterdir()):
                continue
            if key in held["light"]:
                out.append(f"{cell}: a light withheld cell (X60)")
            elif key in held["dark"] and not after_exposure:
                out.append(f"{cell}: a dark withheld cell before the exposure")
    return out


def evidence(args) -> dict:
    folders = candidate_folders(args.candidate or [])
    count, endpoint_failures = light_endpoints(folders)
    trees = capture_trees()
    failures = dict(lightDocuments=light_documents(), frozenFiles=frozen_files(),
                    candidateLightEndpoints=endpoint_failures,
                    withheldCaptures=withheld_captures(trees, args.after_exposure))
    differs = any(failures.values())
    return dict(what="W47 X60 (evidence): what X60 holds without a render", **failures,
                candidatesRead=count, captureTreesScanned=[str(t) for t in trees],
                afterExposure=bool(args.after_exposure), frozen265Sha256=FROZEN_265_SHA,
                frozen05Generations=W.FROZEN_05_GENERATIONS,
                verdict="DIFFERS: STOP" if differs else "IDENTICAL")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=("render", "evidence"))
    ap.add_argument("--stage", type=Path)
    ap.add_argument("--captures", type=Path)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--only-stage-rows", action="store_true",
                    help="a partial stage: compare the rows it holds; count, without failing, the published "
                         "light rows it never rendered")
    ap.add_argument("--candidate", action="append", type=Path, help="a candidate folder (repeatable)")
    ap.add_argument("--after-exposure", action="store_true",
                    help="the dark exposure has been read (read 8): dark withheld captures are admitted")
    args = ap.parse_args(argv)
    W.require_shared()
    if args.mode == "render":
        if args.stage is None:
            raise W.Refusal("x60 render names --stage")
        result = render(args)
    else:
        if args.after_exposure:
            stage = W.load_module("w47_stage", HERE / "stage.py")
            last = stage.committed_last_read() or {}
            if (last.get("refereeManifest") or {}).get("sha256") != W.referees().load_manifest()["sha256"]:
                raise W.Refusal("--after-exposure: the ledger's last committed read does not witness w46-referees-1")
        result = evidence(args)
    out = W.refuse_other_wave_path(args.out or (W.G1_STAGE / f"x60-{args.mode}.json"), "the X60 record")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if not isinstance(v, list) or len(v) < 6}, indent=1))
    return 0 if result["verdict"] == "IDENTICAL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
