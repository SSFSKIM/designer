#!/usr/bin/env python3
"""W27c G2 read, step 1: the seven-run agreement per cell, read off the raw runs.

Reads only the banked sitting under the sitting root (default
`/Users/new/vitrea-w27-26.5-run`) and writes one JSON report beside this file. It
never writes into the sitting and never touches the fixture bundle: `materialize`
publishes, this counts. The two answers it owes claims §5.139 are how many of the
seven runs returned the plurality byte-state for each cell, and whether the cells
the sitting recorded under 45 s of input idle (claims §5.136 §10) agree any less
often than the rest.

Every run manifest's sha256 is checked against the sitting's committed
`provenance.json` first, because a report over runs that are not the banked ones
would describe nothing.
"""
import hashlib
import json
import os
import sys
from collections import Counter

SITTING = os.environ.get("VITREA_SITTING_ROOT", "/Users/new/vitrea-w27-26.5-run")
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = HERE.split("/packages/")[0]
RUN = os.path.join(REPO, "packages/calibration/results/2026-09-11-w27-26.5-run")

# The sitting's own pass names, and where each pass's seven run directories live.
# The two accessibility passes have their own roots because the sitting script
# names a pass by pose and scale only (claims §5.136 §10).
PASSES = {
    "inactive-2x": "inactive-2x",
    "active-2x": "active-2x",
    "inactive-1x": "inactive-1x",
    "active-1x": "active-1x",
    "inactive-1x-increase-contrast": "a11y-increase-contrast/inactive-1x",
    "inactive-1x-reduce-transparency": "a11y-reduce-transparency/inactive-1x",
}


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    prov = json.load(open(os.path.join(RUN, "provenance.json")))
    provruns = {}
    for p in prov["passes"]:
        for r in p["runs"]:
            provruns[(p["pass"], r["run"])] = r

    report = {
        "gate": "W27c G2 read / claims §5.139",
        "reads": "the banked sitting of claims §5.136 §10; the raw runs live outside the repository",
        "sittingRoot": SITTING,
        "provenanceChecked": [],
        "passes": [],
    }
    ok = True
    for name, rel in PASSES.items():
        root = os.path.join(SITTING, rel)
        runs = sorted(
            d for d in os.listdir(root)
            if d.startswith("run-") and os.path.isdir(os.path.join(root, d))
        )
        # 1. The banked manifests are the ones provenance.json names.
        for r in runs:
            got = sha(os.path.join(root, r, "manifest.json"))
            want = provruns.get((name, r), {}).get("manifestSha256")
            report["provenanceChecked"].append(
                {"pass": name, "run": r, "sha256": got, "matchesProvenance": got == want}
            )
            if got != want:
                ok = False
        # 2. Per cell, the byte-state tally over the runs, with the run's own
        #    per-cell idle reading beside it.
        idle = {}
        deterministic = {}
        for r in runs:
            man = json.load(open(os.path.join(root, r, "manifest.json")))
            for prof in man.get("profiles", []):
                for f in prof.get("fixtures", []):
                    cell = f"{prof['profileKey']}/{f['sceneId']}"
                    seconds = f.get("hidIdleSeconds")
                    if seconds is not None and seconds < 45:
                        idle.setdefault(cell, []).append(r)
                    deterministic.setdefault(cell, []).append(bool(f.get("deterministic")))
        profiles = sorted(
            d for d in os.listdir(os.path.join(root, runs[0]))
            if os.path.isdir(os.path.join(root, runs[0], d)) and d != "backgrounds"
        )
        tally = {}
        for prof in profiles:
            names = sorted(
                n for n in os.listdir(os.path.join(root, runs[0], prof)) if n.endswith(".png")
            )
            for png in names:
                cell = f"{prof}/{png[:-4]}"
                hashes = [sha(os.path.join(root, r, prof, png)) for r in runs]
                counts = Counter(hashes)
                top, n = counts.most_common(1)[0]
                tally[cell] = {
                    "runs": len(runs),
                    "distinctByteStates": len(counts),
                    "pluralityRuns": n,
                    "pluralityTied": sum(1 for _, k in counts.items() if k == n) > 1,
                    "pluralitySha256": top,
                    "perRunSha256": dict(zip(runs, hashes)),
                    "runsWithIdleUnder45s": idle.get(cell, []),
                    "deterministicInEveryRun": all(deterministic.get(cell, [])),
                }
        cells = sorted(tally)
        idlecells = [c for c in cells if tally[c]["runsWithIdleUnder45s"]]
        hist = Counter(tally[c]["pluralityRuns"] for c in cells)
        idlehist = Counter(tally[c]["pluralityRuns"] for c in idlecells)
        report["passes"].append({
            "pass": name,
            "dir": rel,
            "runs": len(runs),
            "cells": len(cells),
            "unanimousCells": sum(1 for c in cells if tally[c]["distinctByteStates"] == 1),
            "agreementHistogram": {str(k): hist[k] for k in sorted(hist, reverse=True)},
            "cellsBelowFiveOfSeven": [c for c in cells if tally[c]["pluralityRuns"] < 5],
            "tiedCells": [c for c in cells if tally[c]["pluralityTied"]],
            "idleGroup": {
                "$comment": "the cells claims §5.136 §10 lists as captured under 45 s of input "
                            "idle, reported apart because the idle gate is enforced once per run "
                            "and only recorded per cell",
                "cells": len(idlecells),
                "unanimous": sum(1 for c in idlecells if tally[c]["distinctByteStates"] == 1),
                "agreementHistogram": {str(k): idlehist[k] for k in sorted(idlehist, reverse=True)},
                "belowFiveOfSeven": [c for c in idlecells if tally[c]["pluralityRuns"] < 5],
                "cellList": idlecells,
            },
            "cellTally": tally,
        })
    report["provenanceHolds"] = ok
    with open(os.path.join(HERE, "plurality.json"), "w") as handle:
        json.dump(report, handle, indent=1)
        handle.write("\n")
    for p in report["passes"]:
        print(
            f"{p['pass']:34s} {p['cells']:4d} cells  {p['unanimousCells']:4d} unanimous  "
            f"hist {p['agreementHistogram']}  under-5 {len(p['cellsBelowFiveOfSeven'])}  "
            f"idle {p['idleGroup']['cells']} cells hist {p['idleGroup']['agreementHistogram']}"
        )
    print("provenance holds:", ok)
    return 0 if ok else 1


sys.exit(main())
