#!/usr/bin/env python3
"""W31 G3c — the two accessibility beds, before / at G3 / under the lift rule.

    python3 accessibility-read.py <label-or-matrix.json> [...]

`R = chromaStructureRatioWeb / chromaStructureRatioNative`, median over the
untinted `photo` cells of one profile, one tier and one pose — the statistic
claims §5.164 §4 declares and §8 (b) reports the accessibility beds on.
`oklabDeltaEP95` is the perceptual row beside it, the median over the same cells.

**Two beds, named rather than merged.** Decision Log 3 (d)'s "before" figures
(0.9096 / 0.8294 / 0.8147 / 0.1552) are the CALIBRATION+VALIDATION medians of
`pre-fit-matrix.json`, three cells a bed; §5.164 §8 (b)'s "after" figures
(3.0374 / 1.9923 / 2.9489 / 0.1381) are `verdict.py`'s, which include the
holdout cell and so run over FOUR. Both are printed here, at both bed
definitions, because a before and an after read over different cells is not a
movement.
"""
from __future__ import annotations

import json
import re
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent.parent

PROFILES = {
    "apple-macos-27.0-1x-light-reduced-transparency-glass0.5": "reduced transparency",
    "apple-macos-27.0-1x-light-increased-contrast-coupled-glass0.5": "increased contrast",
}
CALVAL = ("calibration", "validation")


def rows(path: Path) -> list[dict]:
    out = []
    for cell in json.loads(path.read_text())["cells"]:
        key = cell["key"]
        scene = key["sceneId"]
        if key["profileKey"] not in PROFILES:
            continue
        if not scene.startswith("photo__") or "-tint-" in scene:
            continue
        material = cell.get("material") or {}
        at = lambda k: material[k]["value"] if isinstance(material.get(k), dict) else None
        native = at("chromaStructureRatioNative")
        web = at("chromaStructureRatioWeb")
        documents = re.findall(r"sha256:([0-9a-f]{12})", key["web"]["capturePath"])
        out.append({
            "profile": key["profileKey"],
            "tier": key["web"]["renderer"],
            "pose": "inactive" if "__inactive" in scene else "active",
            "scene": scene,
            "set": cell.get("fixtureSet"),
            "documents": documents,
            "R": (web / native) if native else None,
            "deP95": ((cell.get("perceptual") or {}).get("oklabDeltaEP95") or {}).get("value"),
            "levelWeb": at("interiorMeanWeb"),
            "levelNative": at("interiorMeanNative"),
        })
    return out


def beds(rows: list[dict], sets: tuple[str, ...] | None) -> dict:
    out = {}
    for profile, label in PROFILES.items():
        for tier in ("webgpu", "css"):
            for pose in ("active", "inactive"):
                picked = [
                    r for r in rows
                    if r["profile"] == profile and r["tier"] == tier and r["pose"] == pose
                    and (sets is None or r["set"] in sets)
                ]
                if not picked:
                    continue
                out[(label, tier, pose)] = {
                    "n": len(picked),
                    "R": statistics.median([r["R"] for r in picked if r["R"] is not None]),
                    "deP95": statistics.median(
                        [r["deP95"] for r in picked if r["deP95"] is not None]
                    ),
                    "scenes": sorted(r["scene"] for r in picked),
                }
    return out


def table(name: str, source: Path, sets: tuple[str, ...] | None) -> dict:
    read = rows(source)
    documents = sorted({tuple(r["documents"]) for r in read})
    print(f"== {name} — {source} ==")
    print(f"   documents on the capturePath: {documents}")
    got = beds(read, sets)
    print(f"   {'bed':<24} {'tier':<7} {'pose':<9} {'n':>2} {'R':>9} {'ΔE P95':>9}")
    for (label, tier, pose), value in sorted(got.items()):
        print(
            f"   {label:<24} {tier:<7} {pose:<9} {value['n']:>2} "
            f"{value['R']:>9.4f} {value['deP95']:>9.5f}"
        )
    return got


def main() -> int:
    sources = [Path(a) for a in sys.argv[1:]]
    if not sources:
        raise SystemExit(__doc__)
    pre = PACKAGE / "results/2026-09-21-w31-g3-chroma-fit/pre-fit-matrix.json"
    canonical = PACKAGE / "results/matrix.json"
    for sets, name in ((CALVAL, "calibration+validation"), (None, "calibration+validation+holdout")):
        print(f"\n######## the bed: {name} ########\n")
        before = table("0.20.0, pre-fit (retention absent)", pre, sets)
        at_g3 = table("at G3, the retention applied unconditionally", canonical, sets)
        for source in sources:
            now = table(f"under the lift rule ({source.parent.name})", source, sets)
            print(f"\n   -- the movement, {name} --")
            print(f"   {'bed':<24} {'tier':<7} {'pose':<9} "
                  f"{'R 0.20.0':>9} {'R at G3':>9} {'R now':>9} | "
                  f"{'ΔE .20.0':>9} {'ΔE at G3':>9} {'ΔE now':>9}")
            for key in sorted(now):
                b, g, n = before.get(key), at_g3.get(key), now[key]
                fmt = lambda v, k, w: f"{v[k]:>{w}.5f}" if v else " " * w
                print(
                    f"   {key[0]:<24} {key[1]:<7} {key[2]:<9} "
                    f"{fmt(b,'R',9)} {fmt(g,'R',9)} {n['R']:>9.4f} | "
                    f"{fmt(b,'deP95',9)} {fmt(g,'deP95',9)} {n['deP95']:>9.5f}"
                )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
