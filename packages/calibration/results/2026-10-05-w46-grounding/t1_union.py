#!/usr/bin/env python3.12
"""W46 grounding (a read; no capture, no holdout read, no runtime change): T1 over the WHOLE current
macOS 27 union, every generation, scale, tier, pose and set the published rows carry.

The arithmetic is W44 G1's `cuts/t1.py` (`population`, `stratum`, `classify`, `log_error`), imported
by path and not copied, with the candidate and the reference both set to the published row (so every
cell's change is `unchanged` and only fidelity and the aggregate are read). The bar is G0's
`bar/t1-bar.json` where it has the cell (the two 0.25 schemes: 0.5 code, separation 0); every other
cell is read at the floor bar 0.5 code, marked `barFloorAssumed` (no run-to-run bar was measured for
the 0.5 generation or the accessibility profiles), so B = 1 code there as well.

The text stratum T (`hc-text-7`, every member a probe scene) reads fidelity on T1-fine, as W44 G1
and W45's rule declare: its bands are read here on the canonical capture tree with W44 G1's
`readings.read` for every generation, and the light 0.25 readings are checked against W45's
committed band fixture. Raw T1 on a T cell is recorded beside it.

A holdout member is read from its published row only (its number is already recorded evidence;
no fixture pixel of a holdout scene is opened here) and aggregated in its own column.

    VITREA_WEB_CAPTURES=/Users/new/Developer/GitHub/designer/packages/calibration/web-captures \
        python3.12 -B t1_union.py
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import statistics
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[1]
CUTS = CAL / "results" / "2026-10-03-w44-g1-refit" / "cuts"
sys.path.insert(0, str(CUTS))
import bed as B  # noqa: E402
import t1 as T1  # noqa: E402
import matrix_store  # noqa: E402  (bed puts W40's adapter on the path)

GENERATIONS = {  # label -> active document hash (generation file name)
    "light 0.5": "85ad7f7e3e0d",
    "dark 0.5": "0eac5b294cc2",
    "light 0.25": "ebc3d9105a4a",
    "dark 0.25": "d0219cd684bf",
}
# The canonical holdout reads that spent each generation's holdout (the cross-gate ledger,
# results/holdout-configuration/configuration-log.json, read numbers 1-based).
HOLDOUT_READ = {"light 0.5": "read 5 (c9a §5.179, W36)", "dark 0.5": "read 5 (c9a §5.179, W36)",
                "light 0.25": "read 7 (c9a §5.206, W45 exposure)",
                "dark 0.25": "read 6 (c9a §5.201, W43 G3); its bytes also stand in read 7's set"}
CAPTURES = Path(os.environ.get("VITREA_WEB_CAPTURES",
                               "/Users/new/Developer/GitHub/designer/packages/calibration/web-captures"))
BAND_FIXTURE = CAL / "results" / "2026-10-03-w45-g1-refit" / "t1" / "t-bands-ebc3d9105a4a.json"


def load(label: str) -> list[dict]:
    active = GENERATIONS[label]
    index = json.loads((CAL / "results" / "generations" / "index.json").read_bytes())
    entry = index["files"][f"{active}.json"]
    raw = (CAL / "results" / "generations" / f"{active}.json").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == entry["sha256"], f"{active}: file hash"
    assert entry["status"] == "current", f"{active}: not current"
    rows = matrix_store.load_generation(active)
    assert len(rows) == entry["rowCount"], f"{active}: row count"
    return rows


def bands_for(rows: list[dict]) -> dict:
    """T1-fine / T1-low on every T-stratum row (all probe scenes), off the canonical tree."""
    import cuts as C  # W44 G1's capture reader: metadata must name the row's capturePath
    import readings as R
    out = {}
    for r in rows:
        profile, sid, tier = r["key"]["profileKey"], r["key"]["sceneId"], r["key"]["web"]["renderer"]
        if B.SCENES.by_id[sid]["background"] not in T1.STRATA["T"]:
            continue
        assert B.SCENES.role[sid] == "probe", sid
        web, _ = C.capture(CAPTURES, r, tier)
        fixture = C.rgb((C.FIXTURES / profile / f"{sid}.png").read_bytes())
        got = R.read(profile, sid, fixture, web)
        out[(profile, tier, sid)] = {k: dict(native=got["native"][k], web=got["web"][k]) for k in T1.BANDS}
    return out


def main() -> int:
    bars = T1.load_bars()
    held = B.referee_plan.referee_cells(B.referee_plan.load_manifest())
    fixture = {(e["profile"], e["renderer"], e["scene"]): e
               for e in json.loads(BAND_FIXTURE.read_text())["entries"]}
    cells, missing, band_check = [], [], []
    for label in GENERATIONS:
        rows = load(label)
        profiles = sorted({r["key"]["profileKey"] for r in rows})
        bands = bands_for(rows)
        for key, b in bands.items():
            if key in fixture:
                f = fixture[key]["bands"]
                band_check.append(max(abs(f[k][s] - b[k][s]) for k in T1.BANDS for s in ("native", "web")))
        got = T1.cut(rows, rows, profiles, bars, held, tiers=("webgpu", "css"),
                     partitions=("gate", "referee", "holdout"), bands=bands, reference_bands=bands)
        for c in got["cells"]:
            c["generation"] = label
            c["activeDocument"] = GENERATIONS[label]
            if c["stratum"] == "T" and "bands" in c:
                fine = c["bands"]["fine"]
                c["readMetric"], c["readNative"], c["readWeb"] = "t1FineStdDev", fine["native"], fine["candidate"]
                c["readFidelity"], c["readLogError"] = fine["fidelity"], fine["logError"]
                c["readB"] = fine["B"]
            else:
                c["readMetric"], c["readNative"], c["readWeb"] = "t1InteriorStdDev", c["native"], c["candidate"]
                c["readFidelity"], c["readLogError"], c["readB"] = c["fidelity"], c["logError"], c["B"]
            c["readRatio"] = c["readWeb"] / c["readNative"] if c["readNative"] else None
            c["readSignedCodes"] = (c["readWeb"] - c["readNative"]) / c["code"]
            cells.append(c)
        for m in got["missing"]:
            missing.append(dict(m, generation=label))
    assert band_check and max(band_check) < 1e-9, f"band fixture disagreement {max(band_check)}"

    # Cross-check the 0.25 cells against W45's landing cut (the cut the owner test pins).
    landing = json.loads((CAL / "results/2026-10-03-w45-g2-landing/cuts/cut-025-w45-landing.json").read_text())
    theirs = {(c["profile"], c["tier"], c["scene"]): c for c in landing["T1"]["cells"]}
    agree = 0
    for c in cells:
        t = theirs.get((c["profile"], c["tier"], c["scene"]))
        if t is None:
            continue
        assert abs(t["native"] - c["native"]) < 1e-12 and abs(t["candidate"] - c["candidate"]) < 1e-12, c["scene"]
        assert t["fidelity"] == c["fidelity"], (c["profile"], c["tier"], c["scene"])
        agree += 1

    def group_key(c):
        prof = c["profile"].replace("apple-macos-27.0-", "")
        return (c["generation"], prof, c["tier"], c["stratum"], c["pose"],
                "holdout" if c["partition"] == "holdout" else "non-holdout")

    groups = defaultdict(list)
    for c in cells:
        groups[group_key(c)].append(c)
    aggregates = []
    for key, g in sorted(groups.items()):
        ratios = [c["readRatio"] for c in g if c["readRatio"] is not None]
        miss = [c for c in g if c["readFidelity"] == "miss"]
        worst = max(g, key=lambda c: c["readLogError"])
        aggregates.append(dict(
            generation=key[0], profile=key[1], tier=key[2], stratum=key[3], pose=key[4], column=key[5],
            cells=len(g), within=len(g) - len(miss), miss=len(miss),
            medianRatio=statistics.median(ratios), minRatio=min(ratios), maxRatio=max(ratios),
            A=statistics.median(c["readLogError"] for c in g),
            tau=statistics.median(math.log(1 + c["bar"] / (c["readNative"] + c["code"])) for c in g),
            barFloorAssumed=all(c["barFloorAssumed"] for c in g),
            worst=f"{worst['scene']} " + (f"x{worst['readRatio']:.2f}" if worst["readRatio"] is not None
                                           else f"native 0, web {worst['readSignedCodes']:+.2f} codes")))

    scenes_by_stratum = defaultdict(set)
    for c in cells:
        scenes_by_stratum[c["stratum"]].add(B.SCENES.by_id[c["scene"]]["background"])
    out = dict(
        what="W46 grounding: T1 over the whole current macOS 27 union (W44 G1 t1.py arithmetic)",
        generations=GENERATIONS, holdoutSpentBy=HOLDOUT_READ,
        strata={k: list(v) for k, v in T1.STRATA.items()},
        bar=dict(path=str(T1.BAR_PATH.relative_to(B.ROOT)),
                 note="0.25 light and dark cells: measured, 0.5 code (seven pixel-identical G1a runs); "
                      "0.5 and accessibility cells: floor 0.5 code assumed (no bar measured)"),
        bandFixtureCheck=dict(cells=len(band_check), maxAbsDifference=max(band_check)),
        landingCutAgreement=dict(cells=agree, of=len(theirs)),
        missing=missing, aggregates=aggregates, cells=cells)
    (HERE / "t1-union.json").write_text(json.dumps(out, indent=1) + "\n")
    fields = ["generation", "profile", "tier", "scene", "set", "partition", "stratum", "pose", "spanClass",
              "readMetric", "readNative", "readWeb", "readRatio", "readSignedCodes", "readFidelity",
              "readLogError", "native", "candidate", "ratio", "code", "bar", "barFloorAssumed"]
    with (HERE / "t1-cells.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for c in sorted(cells, key=lambda c: (c["generation"], c["profile"], c["tier"], c["stratum"], c["scene"])):
            w.writerow({k: (f"{v:.6g}" if isinstance(v, float) else v) for k, v in c.items() if k in fields})
    with (HERE / "t1-aggregates.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(aggregates[0]))
        w.writeheader()
        for a in aggregates:
            w.writerow({k: (f"{v:.4f}" if isinstance(v, float) else v) for k, v in a.items()})
    print(len(cells), "cells;", len(missing), "declared members with no row/reading;",
          "band fixture", len(band_check), max(band_check), "; landing cut agrees on", agree, "of", len(theirs))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
