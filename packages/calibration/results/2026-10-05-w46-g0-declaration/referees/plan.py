#!/usr/bin/env python3.12
"""W46 G0 (b): the referee planner ADAPTER for the two dark 0.25 profiles (charter Design "The
referees", MARKED; Decision Log 2 as amended v1.1; clause 3).

W44's planner (`results/2026-10-03-w44-g0-declaration/referees/plan.py`) accepts only its own schema
and the two light profiles, and validates a manifest rather than selecting one; it stays
byte-identical (pinned in `bindings.SHARED`) and is not imported here. This adapter keeps W44's
consumers' interface (`load_manifest`, `referee_cells`, `lists`, `assert_absent`, `check-stage`) and
adds what W46's charter makes binding: the manifest is the OUTPUT of a deterministic rule, and a
manifest the rule does not produce is refused.

**The rule** (Design "The referees"). For each slot below, the candidates are the probe scenes of
the slot's stratum, pose, span class and backdrop that both dark profiles declare, that carry no
tint and that no ladder lists (`ladders/cells.json`'s `union`); the referee is the first under
(span ascending, pitch descending, scene id). Spans are the component's shorter side (CSS px), as
T1 reads them; the pitch is the backdrop's number (`checkerboard-8` → 8).

  slot              stratum, pose     span, backdrop
  thin fine rest    F rest            <= 44, checkerboard-4/-8
  thick fine rest   F rest            128-160, checkerboard-4/-8
  fine inactive     F inactive        any, checkerboard-4/-8
  coarse rest       C rest            any, checkerboard-32
  coarse inactive   C inactive        any, checkerboard-32
  text              T inactive        any, hc-text-7

**The two whitelists**, derived from the manifest and scenes.json and never typed (W44's form):
  pre-gate probe   every probe scene the two dark profiles declare, less the manifest; run as
                   `compare --set probe --scene <list>`
  exposure         every canonical holdout scene the two dark profiles declare, plus the manifest;
                   run as `compare --set holdout,probe --scene <list>`, once per tier (clause 7)

    python3.12 -B plan.py derive              the rule's six scenes, with every slot's candidates
    python3.12 -B plan.py write               write referees.json from the rule (refuses if present)
    python3.12 -B plan.py lists [--json]      the two whitelists and their compare flags
    python3.12 -B plan.py check-stage M.json  exit 0 when the stage holds no referee row, 1 when it does
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
MANIFEST = HERE / "referees.json"
LADDER_CELLS = HERE.parent / "ladders" / "cells.json"
SCENES_PATH = ROOT / "apps/reference-apple/scenes.json"
SCHEMA = "w46-referees-1"
LADDER_SCHEMA = "w46-ladder-cells-1"
DARK_025 = ("apple-macos-27.0-1x-dark-standard-glass0.25",
            "apple-macos-27.0-2x-dark-standard-glass0.25")
ROLES = ("calibration", "validation", "holdout", "recorded", "probe")
FINE = ("checkerboard-4", "checkerboard-8")
SLOTS = (
    dict(slot="thin fine rest", stratum="F", pose="rest", span=(0, 44), backdrops=FINE),
    dict(slot="thick fine rest", stratum="F", pose="rest", span=(128, 160), backdrops=FINE),
    dict(slot="fine inactive", stratum="F", pose="inactive", span=None, backdrops=FINE),
    dict(slot="coarse rest", stratum="C", pose="rest", span=None, backdrops=("checkerboard-32",)),
    dict(slot="coarse inactive", stratum="C", pose="inactive", span=None, backdrops=("checkerboard-32",)),
    dict(slot="text", stratum="T", pose="inactive", span=None, backdrops=("hc-text-7",)),
)


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
    return dict(spec=spec, role=role, declared=declared, by_id={s["id"]: s for s in spec["scenes"]})


def load_ladder_cells(path: Path = LADDER_CELLS) -> set[str]:
    body = json.loads(Path(path).read_bytes())
    if body.get("schema") != LADDER_SCHEMA:
        raise Refused(f"{path}: schema {body.get('schema')!r}, not {LADDER_SCHEMA}")
    union = {sid for lad in body["ladders"].values() for pose in ("rest", "inactive") for sid in lad[pose]}
    if union != set(body["union"]):
        raise Refused(f"{path}: `union` is not the ladders' cells")
    return union


def span(scenes: dict, sid: str) -> float:
    comp = scenes["spec"]["components"][scenes["by_id"][sid]["component"]]
    if comp["kind"] in ("capsule", "rrect"):
        return min(comp["size"])
    if comp["kind"] == "stack":
        return min(comp["base"]["size"])
    return min(min(i["size"]) for i in comp["items"])


def pitch(background: str) -> int:
    m = re.search(r"-(\d+)$", background)
    return int(m.group(1)) if m else 0


def pose(scenes: dict, sid: str) -> str:
    return "inactive" if scenes["by_id"][sid]["state"] == "inactive" else "rest"


def candidates(scenes: dict, slot: dict, ladder: set[str]) -> list[str]:
    """A slot's candidates in the rule's order: (span ascending, pitch descending, scene id)."""
    both = set(scenes["declared"][DARK_025[0]]) & set(scenes["declared"][DARK_025[1]])
    out = []
    for sid in both:
        s = scenes["by_id"][sid]
        if scenes["role"][sid] != "probe" or s["background"] not in slot["backdrops"] or "tint" in s:
            continue
        if pose(scenes, sid) != slot["pose"] or sid in ladder:
            continue
        if slot["span"] is not None and not slot["span"][0] <= span(scenes, sid) <= slot["span"][1]:
            continue
        out.append(sid)
    return sorted(out, key=lambda sid: (span(scenes, sid), -pitch(scenes["by_id"][sid]["background"]), sid))


def derive(scenes: dict | None = None, ladder: set[str] | None = None) -> list[dict]:
    """The rule: per slot, its candidates and its referee. A slot with no candidate refuses."""
    scenes = scenes or load_scenes()
    ladder = load_ladder_cells() if ladder is None else ladder
    out = []
    for slot in SLOTS:
        got = candidates(scenes, slot, ladder)
        if not got:
            raise Refused(f"the rule offers no candidate for the slot {slot['slot']!r}")
        out.append(dict(slot=slot["slot"], stratum=slot["stratum"], pose=slot["pose"],
                        referee=got[0], span=span(scenes, got[0]), candidates=got))
    return out


def load_manifest(path: Path = MANIFEST, scenes: dict | None = None, ladder: set[str] | None = None) -> dict:
    """The manifest, refused unless it is exactly what the rule produces: W46's schema, the two dark
    0.25 profiles in order, the six slots' referees in slot order, no ladder cell."""
    scenes = scenes or load_scenes()
    ladder = load_ladder_cells() if ladder is None else ladder
    raw = Path(path).read_bytes()
    m = json.loads(raw)
    if m.get("schema") != SCHEMA:
        raise Refused(f"{path}: schema {m.get('schema')!r}, not {SCHEMA}")
    profiles, ids = m.get("profiles"), m.get("scenes")
    if list(profiles or ()) != list(DARK_025):
        raise Refused(f"{path}: profiles {profiles}, not the two dark -glass0.25 standard profiles {list(DARK_025)}")
    if not ids or len(set(ids)) != len(ids):
        raise Refused(f"{path}: names no scene, or a scene twice")
    on_ladder = sorted(set(ids) & ladder)
    if on_ladder:
        raise Refused(f"{path}: names ladder cells {on_ladder}; no ladder cell is eligible (Decision Log 2)")
    for sid in ids:
        if scenes["role"].get(sid) != "probe":
            raise Refused(f"{path}: {sid} is {scenes['role'].get(sid) or 'in no split'} in scenes.json; a "
                          "referee is a probe scene")
    want = [d["referee"] for d in derive(scenes, ladder)]
    if list(ids) != want:
        raise Refused(f"{path}: {list(ids)} is not what the rule produces ({want})")
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


def withheld(manifest: dict, scenes: dict) -> list[str]:
    """Design "The populations per phase": per dark scale the seven canonical holdout scenes and the
    six referees — the exposure list, which nothing renders before the exposure."""
    return exposure(manifest, scenes)


def compare_selects(scenes: dict, profiles, sets, whitelist) -> set[tuple[str, str]]:
    """`compare`'s cell selection, transcribed from `plan()` in cli/compare.ts (W44's)."""
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


def manifest_body(scenes: dict | None = None) -> dict:
    derived = derive(scenes)
    return {
        "schema": SCHEMA,
        "$comment": [
            "W46's referee manifest (charter 2026-10-05-w46-dark-texture-at-0-25.md, Design \"The",
            "referees\", Decision Log 2 as amended v1.1): the ONLY statement of the held-out dark texture",
            "cells, each scene held out on both dark 0.25 profiles, six per scale, twelve in all. It is",
            "the output of the rule in referees/plan.py over scenes.json and ladders/cells.json, written",
            "by `plan.py write`; the adapter refuses any other content. Consumers: the planner's two",
            "whitelists, the fit loader and the gate (cuts/bed.py), `plan.py check-stage`, and the",
            "exposure (read 8). Canonical membership in scenes.json is untouched: every scene below",
            "stays a probe scene there.",
        ],
        "charter": "docs/doperpowers/specs/2026-10-05-w46-dark-texture-at-0-25.md",
        "rule": "per slot: the probe scenes of its stratum, pose, span class and backdrop that both dark "
                "profiles declare, untinted and on no ladder; the first under (span ascending, pitch "
                "descending, scene id)",
        "slots": [dict(slot=d["slot"], referee=d["referee"], span=d["span"], candidates=d["candidates"])
                  for d in derived],
        "profiles": list(DARK_025),
        "scenes": [d["referee"] for d in derived],
    }


def main(argv: list[str]) -> int:
    verb = argv[1] if len(argv) > 1 else ""
    if verb == "derive":
        for d in derive():
            print(f"{d['slot']:<16} {d['referee']:<40} span {d['span']:g}   candidates {d['candidates']}")
        return 0
    if verb == "write":
        if MANIFEST.exists():
            print("write REFUSES: referees.json exists; the manifest is written once")
            return 2
        with MANIFEST.open("x") as f:
            f.write(json.dumps(manifest_body(), indent=1) + "\n")
        m = load_manifest()
        print(f"referees.json sha256 {m['sha256']}: {m['scenes']}")
        return 0
    if verb == "lists":
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
    if len(argv) == 3 and verb == "check-stage":
        return check_stage(argv[2])
    print(__doc__)
    return 64


if __name__ == "__main__":
    sys.exit(main(sys.argv))
