#!/usr/bin/env python3.12
"""W47 G0 (c): the referee manifest under X69 — W46's `w46-referees-1`, loaded by its SHA-256 and never
re-derived from W47's ladders (charter `2026-10-06-w47-span-graded-dark-transmission.md`, clause 4,
Decision Log 1 as amended v1.1, X69).

W46's planner adapter (`results/2026-10-05-w46-g0-declaration/referees/plan.py`, pinned in
`bindings.SHARED`) DERIVES a manifest from the ladder list it is given: its rule takes, per slot, the
first eligible probe scene after excluding that list. Given W47's ladders it would pick
`checkerboard-32__rrect-sm__rest` for the coarse-rest slot and refuse the frozen file (the charter's
v1.1 P1). So W47 never gives it W47's ladders. This loader:

  load        reads `w46-referees-1` at the pinned path and refuses it unless its bytes hash to the
              pinned `0eb8ef77…`, its schema is W46's and its profiles are the two dark 0.25 profiles
  pin         re-runs W46's adapter against W46's FROZEN ladder list (`bindings.W46_LADDER_CELLS`,
              pinned in W46's declaration), as a pin that W46's tools still reproduce the file; it is
              the only list the adapter is ever given
  membership  every referee scene is declared by both dark 0.25 profiles in `scenes.json`
  disjoint    no W47 ladder cell (`ladders/cells.json`) is a referee; a ladder that names one has that
              cell replaced in the ladder list, never the manifest, and the refusal names which
  withhold    a read before the exposure holds no referee row and no holdout row (`assert_absent`,
              `check-stage`); the exposure's sealed stage alone reads them, once

Its interface is W46's adapter's (`load_manifest`, `referee_cells`, `withheld`, `pregate_probe`,
`exposure`, `compare_selects`, `lists`, `assert_absent`, `check-stage`), so W47's ports of W46's
consumers (the bed, the cuts, the ladders, the stage) read it unchanged; the lists are W46's own
functions applied to the frozen manifest.

    python3.12 -B referees.py check                 load, pin, membership, disjointness
    python3.12 -B referees.py lists [--json]        the pre-gate and exposure whitelists
    python3.12 -B referees.py check-stage M.json    exit 0 when the matrix holds no referee or
                                                     holdout row, 1 when it does
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import bindings as W  # noqa: E402

MANIFEST = W.W46_REFEREES
MANIFEST_SHA = W.SHARED[W.W46_REFEREES]
LADDER_CELLS = W.LADDER_CELLS
LADDER_SCHEMA = "w47-ladder-cells-1"
SCHEMA = W.REFEREE_SCHEMA
DARK_025 = W.DARK_025
Refused = W.Refusal

_plan = W.referee_plan()                    # W46's adapter, by path, pinned (X69)
load_scenes = _plan.load_scenes
referee_cells = _plan.referee_cells
pregate_probe = _plan.pregate_probe
exposure = _plan.exposure
withheld = _plan.withheld
compare_selects = _plan.compare_selects
span = _plan.span
pose = _plan.pose
SCENES_PATH = _plan.SCENES_PATH


def load_ladder_cells(path: Path = LADDER_CELLS) -> dict[str, list[str]]:
    """W47's ladder list: `{ladder: [scene, ...]}` over both poses, its `union` checked."""
    body = json.loads(Path(path).read_bytes())
    if body.get("schema") != LADDER_SCHEMA:
        raise Refused(f"{path}: schema {body.get('schema')!r}, not {LADDER_SCHEMA}")
    out = {name: list(lad["rest"]) + list(lad["inactive"]) for name, lad in body["ladders"].items()}
    if {s for cells in out.values() for s in cells} != set(body["union"]):
        raise Refused(f"{path}: `union` is not the ladders' cells")
    return out


def pin_derivation(path: Path = MANIFEST, scenes: dict | None = None) -> dict:
    """W46's adapter against W46's frozen ladder list, and nothing else: the pin that W46's tools
    still reproduce `w46-referees-1` (X69). Never given W47's ladders."""
    frozen = _plan.load_ladder_cells(W.W46_LADDER_CELLS)
    return _plan.load_manifest(path, scenes, frozen)


def check_membership(manifest: dict, scenes: dict) -> None:
    """Every referee scene declared by both dark 0.25 profiles (X69)."""
    for profile in DARK_025:
        missing = [s for s in manifest["scenes"] if s not in set(scenes["declared"][profile])]
        if missing:
            raise Refused(f"{manifest['path']}: {missing} not declared by {profile}; every referee scene "
                          "is declared by both dark 0.25 profiles (X69 membership)")


def check_disjoint(manifest: dict, ladders: dict[str, list[str]], where: str = "ladders/cells.json") -> None:
    """No W47 ladder cell is a referee (X69). The refusal names the ladder and the cell, which the
    LADDER list replaces; the manifest never moves."""
    held = set(manifest["scenes"])
    hits = [f"ladder ({name}) {sid}" for name, cells in ladders.items() for sid in cells if sid in held]
    if hits:
        raise Refused(f"{where}: names referee scene(s) of w46-referees-1: {', '.join(hits)}; replace the "
                      "cell in the ladder list, never the manifest (X69 disjointness)")


def load_manifest(path: Path = MANIFEST, scenes: dict | None = None,
                  ladders: dict[str, list[str]] | None = None) -> dict:
    """The frozen manifest, by hash, with the derivation pin and W47's membership and disjointness
    checks. `ladders` defaults to W47's committed `ladders/cells.json` (when it exists)."""
    scenes = scenes or load_scenes()
    raw = Path(path).read_bytes()
    got = W.sha(raw)
    if got != MANIFEST_SHA:
        raise Refused(f"{path}: sha256 {got[:12]}…, not w46-referees-1's pinned {MANIFEST_SHA[:12]}… (X69: "
                      "loaded by hash, never re-derived)")
    body = json.loads(raw)
    if body.get("schema") != SCHEMA or list(body.get("profiles") or ()) != list(DARK_025):
        raise Refused(f"{path}: not {SCHEMA} over the two dark 0.25 profiles")
    manifest = dict(path=str(path), sha256=got, profiles=list(body["profiles"]), scenes=list(body["scenes"]))
    pinned = pin_derivation(path, scenes)
    if pinned["scenes"] != manifest["scenes"]:
        raise Refused(f"{path}: W46's adapter no longer reproduces it from W46's frozen ladder list")
    check_membership(manifest, scenes)
    if ladders is None and LADDER_CELLS.exists():
        ladders = load_ladder_cells()
    if ladders is not None:
        check_disjoint(manifest, ladders)
    return manifest


def holdout_scenes(scenes: dict) -> set[str]:
    return {s for p in DARK_025 for s in scenes["declared"][p] if scenes["role"][s] == "holdout"}


def assert_absent(rows, manifest: dict, where: str, scenes: dict | None = None) -> None:
    """X69 withholding: a read before the exposure holds no referee row and no holdout row of a dark
    0.25 profile (Design "The populations per phase"; clause 4: such a row voids the read)."""
    scenes = scenes or load_scenes()
    held = referee_cells(manifest)
    hold = holdout_scenes(scenes)
    cells = {(r["key"]["profileKey"], r["key"]["sceneId"]) for r in rows}
    found = sorted(cells & held)
    found += sorted((p, s) for p, s in cells if p in DARK_025 and s in hold)
    if found:
        raise Refused(f"{where}: holds {len(found)} withheld cell(s) before the exposure "
                      f"(w46-referees-1 sha256 {manifest['sha256'][:12]}, and the dark holdout): "
                      + ", ".join(f"{p}/{s}" for p, s in found))


def lists(manifest: dict | None = None, scenes: dict | None = None) -> dict:
    scenes = scenes or load_scenes()
    manifest = manifest or load_manifest(scenes=scenes)
    return _plan.lists(manifest, scenes)


def check_stage(matrix_path: str) -> int:
    rows = json.loads(Path(matrix_path).read_bytes())["cells"]
    manifest = load_manifest()
    try:
        assert_absent(rows, manifest, matrix_path)
    except Refused as refusal:
        print(f"check-stage REFUSES: {refusal}")
        return 1
    print(f"check-stage: {len(rows)} rows, no referee or holdout cell (w46-referees-1 sha256 "
          f"{manifest['sha256'][:12]})")
    return 0


def main(argv: list[str]) -> int:
    verb = argv[1] if len(argv) > 1 else ""
    if verb == "check":
        m = load_manifest()
        print(f"w46-referees-1 sha256 {m['sha256']}: loaded by hash; W46's adapter reproduces it from W46's "
              f"frozen ladder list; every scene declared by both dark profiles; no W47 ladder cell among "
              f"{m['scenes']}")
        return 0
    if verb == "lists":
        out = lists()
        if "--json" in argv:
            print(json.dumps(out, indent=2))
        else:
            for name in ("pregateProbe", "exposure"):
                print(f"{name}: {out[name]['count']} scenes")
                for sid in out[name]["scenes"]:
                    print(f"  {sid}")
        return 0
    if len(argv) == 3 and verb == "check-stage":
        return check_stage(argv[2])
    print(__doc__)
    return 64


if __name__ == "__main__":
    sys.exit(main(sys.argv))
