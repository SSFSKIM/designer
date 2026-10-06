"""W47 G0 (b): operator 2 after the merge with operator 1 at identity, read on the dark 0.25 bed itself, both tiers, both scales
(charter clause 1, Decision Log 3, X57, X66; claims §5.211).

All five operator leaves ship at 0, so the shipped dark 0.25 documents must render exactly what the published
generation `d0219cd684bf` measured: every capture byte-identical to the canonical capture tree and
every row's measured fields identical to the published row.

    python3.12 -B identity.py plan     the cells: the published calibration+validation rows of
                                       the two dark 0.25 profiles, checked against W47's withheld
                                       scenes (the referees and the holdout) before anything renders
    python3.12 -B identity.py render [tier]   strict-mode `compare` per scale and tier (webgpu
                                       first), every launch through with-gpu.sh, into scratch (never
                                       the repository's captures)
    python3.12 -B identity.py read     → identity.txt (exit 1 on any difference)

Scratch: ~/vitrea-w47/op2-identity/<scale>/<tier>/matrix.json and ONE capture tree per scale,
~/vitrea-w47/op2-identity/<scale>/captures/, shared by the two tiers as the canonical tree is: the
CSS row's coherence axis pairs it with the WebGPU capture of the same cell read off that tree, so a
CSS run against a tree without its WebGPU twin records no coherence (operator 1's first CSS read used per-tier trees and differed only in `coherence`; its PNGs
were byte-identical). This port keeps that correction from the outset. The canonical tree is read-only input.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[2]
GENERATION = CAL / "results/generations/d0219cd684bf.json"
CANONICAL = Path("/Users/new/Developer/GitHub/designer/packages/calibration/web-captures")
SCRATCH = Path.home() / "vitrea-w47/op2-identity"
WITH_GPU = HERE.parent / "with-gpu.sh"
PROFILES = {"1x": "apple-macos-27.0-1x-dark-standard-glass0.25", "2x": "apple-macos-27.0-2x-dark-standard-glass0.25"}
ACTIVE = "profiles/apple-macos-27.0-1x-dark-standard-glass0.25.json"
RECEDED = "profiles/apple-macos-27.0-1x-dark-standard-glass0.25-receded.json"
TIERS = ("webgpu", "css")
SETS = ("calibration", "validation")
# W47's withheld dark scenes (the standing rules): the six W46 referees and the seven holdout cells.
WITHHELD = {
    "checkerboard-8__rrect-sm__rest", "checkerboard-8__rrect-ml__rest", "checkerboard-4__rrect-md__inactive",
    "checkerboard-32__rrect-ml__rest", "checkerboard-32__rrect-lg__inactive", "hc-text-7__rrect-md__inactive",
    "checkerboard__glass-over-glass__rest", "checkerboard__glass-over-glass__inactive",
    "photo__glass-over-glass__inactive", "photo__rrect-lg__rest", "photo__rrect-lg__inactive",
    "mid-dark-solid__capsule-button__rest", "mid-dark-solid__capsule-button__inactive",
}
# Fields a re-render may legitimately differ in: when it ran, nothing it measured.
VOLATILE = {"capturedAt"}


def published() -> dict[tuple[str, str, str], dict]:
    cells = json.loads(GENERATION.read_text())["cells"]
    return {(c["key"]["profileKey"], c["key"]["web"]["renderer"], c["key"]["sceneId"]): c
            for c in cells if c["fixtureSet"] in SETS}


def plan() -> dict[str, dict[str, list[str]]]:
    rows = published()
    out: dict[str, dict[str, list[str]]] = {}
    for scale, profile in PROFILES.items():
        for tier in TIERS:
            scenes = sorted(s for (p, t, s) in rows if p == profile and t == tier)
            leaked = sorted(set(scenes) & WITHHELD)
            if leaked:
                raise SystemExit(f"refusing: {profile} {tier} calibration/validation names withheld {leaked}")
            out.setdefault(scale, {})[tier] = scenes
    return out


def render(only: str | None = None) -> int:
    cells = plan()
    for scale, profile in PROFILES.items():
        for tier in TIERS:
            if only is not None and tier != only:
                continue
            root = SCRATCH / scale / tier
            root.mkdir(parents=True, exist_ok=True)
            argv = ["python3.12", "-B", str(HERE / "proofs/census-retry.py"), str(WITH_GPU), f"w47-op2 identity {scale} {tier}", "pnpm", "run", "-s", "compare", "--",
                    "--profile", profile, "--renderer", tier, "--material-profile", ACTIVE,
                    "--receded-profile", RECEDED, "--set", ",".join(SETS), "--scene", ",".join(cells[scale][tier]),
                    "--alpha", "--write-partial", "--out-matrix", str(root / "matrix.json")]
            env = {**os.environ, "VITREA_WEB_CAPTURES": str(SCRATCH / scale / "captures"),
                   "VITREA_SCENE_SERVER_PORT": "5484"}
            env.pop("VITREA_MATRIX_PATH", None)
            if (root / "matrix.json").exists():
                raise SystemExit(f"{root} already holds a reading; refuse overwrite")
            with open(root / "compare.log", "x") as log:
                code = subprocess.run(argv, cwd=CAL, env=env, stdout=log, stderr=subprocess.STDOUT).returncode
            print(f"{scale} {tier}: exit {code}")
            if code != 0:
                return code
    return 0


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def strip(row: dict) -> dict:
    return {k: v for k, v in row.items() if k not in VOLATILE}


def read() -> int:
    cells, rows = plan(), published()
    lines, failures = [], []
    totals = {"png": 0, "png_identical": 0, "rows": 0, "rows_identical": 0}
    for scale, profile in PROFILES.items():
        for tier in TIERS:
            root = SCRATCH / scale / tier
            matrix = json.loads((root / "matrix.json").read_text())
            measured = {(c["key"]["profileKey"], c["key"]["web"]["renderer"], c["key"]["sceneId"]): c
                        for c in matrix["cells"]}
            for scene in cells[scale][tier]:
                key = (profile, tier, scene)
                row = measured.get(key)
                if row is None:
                    failures.append(f"{scale}/{tier}/{scene}: no row")
                    continue
                totals["rows"] += 1
                same_row = strip(row) == strip(rows[key])
                totals["rows_identical"] += same_row
                if not same_row:
                    diff = sorted(k for k in set(row) | set(rows[key])
                                  if k not in VOLATILE and row.get(k) != rows[key].get(k))
                    failures.append(f"{scale}/{tier}/{scene}: row fields differ {diff}")
                ours = sorted((SCRATCH / scale / "captures" / profile / scene).glob(f"*__{tier}*.png"))
                theirs = sorted((CANONICAL / profile / scene).glob(f"*__{tier}*.png"))
                if [p.name for p in ours] != [p.name for p in theirs] or not ours:
                    failures.append(f"{scale}/{tier}/{scene}: capture files differ "
                                    f"{[p.name for p in ours]} vs {[p.name for p in theirs]}")
                    continue
                same_png = 0
                for a, b in zip(ours, theirs):
                    totals["png"] += 1
                    if sha(a) == sha(b):
                        same_png += 1
                    else:
                        failures.append(f"{scale}/{tier}/{scene}: {a.name} differs")
                totals["png_identical"] += same_png
                lines.append(f"{'identical' if same_row and same_png == len(ours) else 'DIFFERENT'}  "
                             f"{scale} {tier:6s} {scene:52s} row {'=' if same_row else '≠'}  "
                             f"png {same_png}/{len(ours)}  {sha(ours[0])[:16]}")
    lines.append("")
    lines.append(f"rows whose measured fields equal the published d0219cd684bf row (all but {sorted(VOLATILE)}): "
                 f"{totals['rows_identical']} of {totals['rows']}")
    lines.append(f"captures byte-identical to the canonical tree: {totals['png_identical']} of {totals['png']}")
    lines.append(f"failures: {failures if failures else 'none'}")
    with (HERE / "identity.txt").open("x") as output:
        output.write("\n".join(lines) + "\n")
    print("\n".join(lines[-4:]))
    return 1 if failures else 0


if __name__ == "__main__":
    verb = sys.argv[1] if len(sys.argv) > 1 else ""
    if verb == "plan":
        print(json.dumps({s: {t: len(v) for t, v in d.items()} for s, d in plan().items()}))
        sys.exit(0)
    if verb == "render":
        sys.exit(render(sys.argv[2] if len(sys.argv) > 2 else None))
    if verb == "read":
        sys.exit(read())
    print(__doc__)
    sys.exit(64)
