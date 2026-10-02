#!/usr/bin/env python3.12
"""W44 G0 (d): the referee planner, the manifest's first consumer (charter Design "The referees"; X49).

`compare` has no exclusion flag, and it selects a cell when its profile is named, its scene is in
the `--scene` whitelist AND the scene's canonical split role is in `--set` (`cli/compare.ts`,
`plan()`: the `options.scenes.includes` test, then `options.sets.includes(declared)`). So a probe
scene cannot be selected under `--set holdout`, and an ordinary probe pass would render the
referees. Rather than add a flag, this planner derives two POSITIVE whitelists from
`referees.json` and `scenes.json` and nothing else (never typed by hand):

  pre-gate probe   every probe scene the manifest's profiles declare, less the manifest;
                   run as  `compare --set probe --scene <list>`
  exposure         every canonical holdout scene the manifest's profiles declare, plus the
                   manifest; run as  `compare --set holdout,probe --scene <list>`, once per tier

Canonical membership is untouched: no list moves a scene between splits, and every referee stays
a probe scene in scenes.json (the planner refuses a manifest naming any other kind). `matrix
status` on a declared stage already reports the referees as expected-missing cells until the
exposure fills them, and `matrix publish` refuses the holes; nothing here relaxes either.

The other consumers import `load_manifest` and `referee_cells` from here: `cuts/bed.py` refuses a
fit bed carrying a referee row and a stage bed carrying one before the exposure, and
`check-stage` below is the gate's absence check on a stage's own matrix.

    python3.12 -B plan.py lists [--json]          the two whitelists and their compare flags
    python3.12 -B plan.py check-stage MATRIX.json exit 0 when the stage holds no referee row, 1 when it does
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
MANIFEST = HERE / "referees.json"
SCENES_PATH = ROOT / "apps/reference-apple/scenes.json"
SCHEMA = "w44-referees-1"
LIGHT_025 = ("apple-macos-27.0-1x-light-standard-glass0.25",
             "apple-macos-27.0-2x-light-standard-glass0.25")
ROLES = ("calibration", "validation", "holdout", "recorded", "probe")


class Refused(SystemExit):
    """A refusal: the planner's red cases assert on these."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_scenes(path: Path = SCENES_PATH) -> dict:
    spec = json.loads(path.read_bytes())
    role = {}
    for r in ROLES:
        for sid in spec["split"].get(r, []):
            if sid in role:
                raise Refused(f"scenes.json: {sid} is in two splits ({role[sid]}, {r})")
            role[sid] = r
    declared = {}
    for p in spec["profiles"]:
        declared[p["key"]] = [s["id"] for s in spec["scenes"]] if p["scenes"] == "all" else list(p["scenes"])
    return dict(spec=spec, role=role, declared=declared)


def load_manifest(path: Path = MANIFEST, scenes: dict | None = None) -> dict:
    """The manifest, validated against scenes.json: a refusal for anything but probe scenes every
    named light 0.25 profile declares, each named once."""
    scenes = scenes or load_scenes()
    raw = Path(path).read_bytes()
    m = json.loads(raw)
    if m.get("schema") != SCHEMA:
        raise Refused(f"{path}: schema {m.get('schema')!r}, not {SCHEMA}")
    profiles, ids = m.get("profiles"), m.get("scenes")
    if not profiles or not ids:
        raise Refused(f"{path}: names no profile or no scene")
    if len(set(ids)) != len(ids) or len(set(profiles)) != len(profiles):
        raise Refused(f"{path}: a scene or profile is named twice")
    for p in profiles:
        if p not in LIGHT_025:
            raise Refused(f"{path}: {p} is not a light -glass0.25 standard profile")
    for sid in ids:
        role = scenes["role"].get(sid)
        if role != "probe":
            raise Refused(f"{path}: {sid} is {role or 'in no split'} in scenes.json; a referee is a "
                          "probe scene (the canonical holdout is read by its own rule)")
        for p in profiles:
            if sid not in scenes["declared"][p]:
                raise Refused(f"{path}: {p} does not declare {sid}")
    return dict(path=str(path), sha256=sha256(raw), profiles=list(profiles), scenes=list(ids))


def referee_cells(manifest: dict) -> set[tuple[str, str]]:
    return {(p, s) for p in manifest["profiles"] for s in manifest["scenes"]}


def _declared_union(scenes: dict, profiles) -> set[str]:
    return {s for p in profiles for s in scenes["declared"][p]}


def pregate_probe(manifest: dict, scenes: dict) -> list[str]:
    held = set(manifest["scenes"])
    return sorted(s for s in _declared_union(scenes, manifest["profiles"])
                  if scenes["role"][s] == "probe" and s not in held)


def exposure(manifest: dict, scenes: dict) -> list[str]:
    holdout = {s for s in _declared_union(scenes, manifest["profiles"]) if scenes["role"][s] == "holdout"}
    return sorted(holdout | set(manifest["scenes"]))


def compare_selects(scenes: dict, profiles, sets, whitelist) -> set[tuple[str, str]]:
    """`compare`'s cell selection, transcribed from `plan()` in cli/compare.ts: a named profile, a
    whitelisted scene, a canonical role inside `--set`. The red cases read the lists through it."""
    return {(p, s) for p in profiles for s in scenes["declared"][p]
            if s in whitelist and scenes["role"][s] in sets}


def lists(manifest: dict | None = None, scenes: dict | None = None) -> dict:
    scenes = scenes or load_scenes()
    manifest = manifest or load_manifest(scenes=scenes)
    pre, exp = pregate_probe(manifest, scenes), exposure(manifest, scenes)
    return {
        "manifest": {"path": (str(Path(manifest["path"]).relative_to(ROOT))
                              if Path(manifest["path"]).is_relative_to(ROOT) else manifest["path"]),
                     "sha256": manifest["sha256"]},
        "scenesSha256": sha256(SCENES_PATH.read_bytes()),
        "profiles": manifest["profiles"],
        "pregateProbe": {"set": "probe", "scenes": pre, "count": len(pre),
                         "compare": ["--set", "probe", "--scene", ",".join(pre)]},
        "exposure": {"set": "holdout,probe", "scenes": exp, "count": len(exp),
                     "compare": ["--set", "holdout,probe", "--scene", ",".join(exp)]},
    }


def assert_absent(rows, manifest: dict, where: str) -> None:
    """The gate's absence check and the fit loader's refusal: no row of a referee cell."""
    held = referee_cells(manifest)
    found = sorted({(r["key"]["profileKey"], r["key"]["sceneId"]) for r in rows} & held)
    if found:
        raise Refused(f"{where}: holds {len(found)} referee cell(s) before the exposure "
                      f"(referees.json sha256 {manifest['sha256'][:12]}): "
                      + ", ".join(f"{p}/{s}" for p, s in found))


def check_stage(matrix_path: str) -> int:
    rows = json.loads(Path(matrix_path).read_bytes())["cells"]
    manifest = load_manifest()
    try:
        assert_absent(rows, manifest, matrix_path)
    except Refused as refusal:
        print(f"check-stage REFUSES: {refusal}")
        return 1
    print(f"check-stage: {len(rows)} rows, no referee cell (referees.json sha256 {manifest['sha256'][:12]})")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) >= 2 and argv[1] == "lists":
        out = lists()
        if "--json" in argv:
            print(json.dumps(out, indent=2))
        else:
            print(f"referees.json sha256 {out['manifest']['sha256']}; scenes.json sha256 {out['scenesSha256']}")
            for name in ("pregateProbe", "exposure"):
                entry = out[name]
                print(f"\n{name}: {entry['count']} scenes, compare {' '.join(entry['compare'][:3])} <list>")
                for sid in entry["scenes"]:
                    print(f"  {sid}")
        return 0
    if len(argv) == 3 and argv[1] == "check-stage":
        return check_stage(argv[2])
    print(__doc__)
    return 64


if __name__ == "__main__":
    sys.exit(main(sys.argv))
