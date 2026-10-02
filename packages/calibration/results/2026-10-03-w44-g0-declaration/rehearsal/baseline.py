#!/usr/bin/env python3.12
"""W44 G0 (c): the PINNED c05 baseline the rehearsal must reproduce (charter clause 2).

Written and committed before T1 runs on anything. It reads the published light 0.25 generation
file (`results/generations/6d18c059eb42.json`, checked against `index.json`) directly with `json`,
not through `cuts/bed.py` or T1's code, so the rehearsal's reproduction is a check of T1 against
an independent reading of the same rows.

For every STRUCTURED row (the light scheme's T1 backdrops, both scales, both tiers, every set) it
records `interiorStdDevWeb / interiorStdDevNative` with the cell's grouping, and the structure
map's medians, with the grouping the charter states (Grounding, "the structure map"):

  span class   thin = spans 32-44 (rrect-sm, the capsules, toolbar-group by its 44 px members);
               mid = 96 (rrect-md); thick = 128-160 (rrect-ml, rrect-lg, glass-over-glass by its
               130 px base). A scene's span is its component's short side (a group's or a stack's
               by its members, as W43's bed.py reads it).
  pose         inactive* against everything else (the pressed states fold into rest).

And the three findings on their NAMED subsets, each with its exceptions named (clause 2):
  (i)   the thin rest median per structured backdrop, 2x WebGPU: every one below 0.9;
  (ii)  the F stratum's mid and thick rest cells, 2x WebGPU: median above 1.5, with the cells
        under 1 named (the charter names checkerboard-8__rrect-md__rest 0.85 and the hc-text-7
        cells);
  (iii) the inactive cells of checkerboard, checkerboard-lc16, checkerboard-32 and the F stratum,
        2x WebGPU: median above 2, with inactive checkerboard-64 and thick hc-text named.

    python3.12 -B baseline.py            writes c05-baseline.json beside it (refuses to overwrite)
"""
from __future__ import annotations

import hashlib
import json
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
GEN = ROOT / "packages/calibration/results/generations"
FILE = "6d18c059eb42.json"
SCENES = ROOT / "apps/reference-apple/scenes.json"
OUT = HERE / "c05-baseline.json"

STRATA = {"F": ("checkerboard-4", "checkerboard-8", "hc-text-7"),
          "C": ("checkerboard", "checkerboard-lc16", "checkerboard-32", "checkerboard-64", "hc-text",
                "hc-text-28", "impulse"),
          "P": ("photo",)}
BACKDROPS = [b for s in STRATA.values() for b in s]
ORDER = ["checkerboard-4", "checkerboard-8", "hc-text-7", "checkerboard-lc16", "checkerboard-32",
         "checkerboard-64", "hc-text-28", "checkerboard", "hc-text", "impulse", "photo"]


def span(component: dict) -> float:
    if component["kind"] in ("capsule", "rrect"):
        return min(component["size"])
    if component["kind"] == "stack":
        return min(component["base"]["size"])
    if component["kind"] == "group":
        return min(min(i["size"]) for i in component["items"])
    raise SystemExit(f"no span for {component['kind']}")


def span_class(s: float) -> str:
    return "thin" if s <= 44 else "mid" if s == 96 else "thick" if 128 <= s <= 160 else "other"


def main() -> int:
    index = json.loads((GEN / "index.json").read_bytes())
    raw = (GEN / FILE).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != index["files"][FILE]["sha256"]:
        raise SystemExit(f"{FILE} does not hash to its index entry")
    spec = json.loads(SCENES.read_bytes())
    by_id = {s["id"]: s for s in spec["scenes"]}
    cells = []
    for row in json.loads(raw)["cells"]:
        sid = row["key"]["sceneId"]
        scene = by_id[sid]
        if scene["background"] not in BACKDROPS:
            continue
        m = row.get("material") or {}
        n = (m.get("interiorStdDevNative") or {}).get("value")
        w = (m.get("interiorStdDevWeb") or {}).get("value")
        s = span(spec["components"][scene["component"]])
        cells.append(dict(
            profile=row["key"]["profileKey"], tier=row["key"]["web"]["renderer"], scene=sid,
            set=row["fixtureSet"], backdrop=scene["background"],
            stratum=next(k for k, v in STRATA.items() if scene["background"] in v),
            component=scene["component"], span=s, spanClass=span_class(s),
            pose="inactive" if scene["state"] == "inactive" else "rest", state=scene["state"],
            native=n, web=w, ratio=None if n in (None, 0) or w is None else w / n))
    cells.sort(key=lambda c: (c["profile"], c["tier"], c["scene"]))

    def med(sel):
        v = [c["ratio"] for c in sel if c["ratio"] is not None]
        return None if not v else dict(median=statistics.median(v), n=len(v), min=min(v), max=max(v))

    maps = {}
    for scale in ("1x", "2x"):
        for tier in ("webgpu", "css"):
            table = {}
            for b in ORDER:
                entry = {}
                for pose in ("rest", "inactive"):
                    for sc in ("thin", "mid", "thick"):
                        got = med([c for c in cells if f"-{scale}-" in c["profile"] and c["tier"] == tier
                                   and c["backdrop"] == b and c["pose"] == pose and c["spanClass"] == sc])
                        if got:
                            entry[f"{sc} {pose}"] = got
                table[b] = entry
            maps[f"{scale} light {tier}"] = table

    two = [c for c in cells if "-2x-" in c["profile"] and c["tier"] == "webgpu"]
    thin_rest = {b: maps["2x light webgpu"][b]["thin rest"]["median"] for b in ORDER}
    f_mt_rest = [c for c in two if c["stratum"] == "F" and c["pose"] == "rest"
                 and c["spanClass"] in ("mid", "thick")]
    inactive_over = [c for c in two if c["pose"] == "inactive" and (
        c["stratum"] == "F" or c["backdrop"] in ("checkerboard", "checkerboard-lc16", "checkerboard-32"))]
    named_iii = [c for c in two if c["pose"] == "inactive" and (
        c["backdrop"] == "checkerboard-64" or (c["backdrop"] == "hc-text" and c["spanClass"] == "thick"))]
    pick = lambda sel: [dict(scene=c["scene"], ratio=c["ratio"]) for c in sel]  # noqa: E731
    findings = {
        "i": dict(subset="2x WebGPU, rest, thin span, per structured backdrop: the median ratio",
                  bar="every backdrop's median below 0.9", perBackdrop=thin_rest,
                  range=[min(thin_rest.values()), max(thin_rest.values())],
                  holds=all(v < 0.9 for v in thin_rest.values())),
        "ii": dict(subset="2x WebGPU, F stratum, rest, mid and thick spans",
                   bar="median above 1.5; the cells under 1 named",
                   median=statistics.median(c["ratio"] for c in f_mt_rest), cells=pick(f_mt_rest),
                   namedUnder=pick(c for c in f_mt_rest if c["ratio"] < 1),
                   holds=statistics.median(c["ratio"] for c in f_mt_rest) > 1.5),
        "iii": dict(subset="2x WebGPU, inactive, checkerboard / checkerboard-lc16 / checkerboard-32 "
                           "and the F stratum",
                    bar="median above 2; inactive checkerboard-64 and thick hc-text named",
                    median=statistics.median(c["ratio"] for c in inactive_over),
                    cells=pick(inactive_over), named=pick(named_iii),
                    holds=statistics.median(c["ratio"] for c in inactive_over) > 2),
    }
    body = dict(
        schema="w44-c05-baseline-1",
        what="W44 G0 clause 2: every structured row's interiorStdDevWeb / interiorStdDevNative from "
             "the published c05 light generation, pinned before T1 runs; the structure map and the "
             "three findings on their named subsets",
        generation=dict(file=f"packages/calibration/results/generations/{FILE}", sha256=digest),
        scenesSha256=hashlib.sha256(SCENES.read_bytes()).hexdigest(),
        tool=dict(path=str(Path(__file__).relative_to(ROOT)),
                  sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),
        grouping=dict(strata=STRATA,
                      spanClass="thin = spans 32-44, mid = 96, thick = 128-160; a scene's span is "
                                "its component's short side (group and stack by their members)",
                      pose="inactive* against everything else; pressed folds into rest"),
        cells=cells, structureMap=maps, findings=findings)
    with OUT.open("x") as f:
        json.dump(body, f, indent=1)
        f.write("\n")
    for k, v in findings.items():
        print(k, "holds" if v["holds"] else "DOES NOT HOLD",
              {x: v[x] for x in ("range", "median") if x in v})
    print("named under (ii):", v := findings["ii"]["namedUnder"])
    print("named (iii):", findings["iii"]["named"])
    print(f"{len(cells)} structured rows; wrote {OUT.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
