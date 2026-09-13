#!/usr/bin/env python3
"""W27c G1c: the sweep's residual tables and the declared selection, per term.

Reads every rung matrix a sweep wrote and applies `sweep-plan.json`'s rule as
declared: select on the equal-cell mean BODY ΔE over the term's calibration and
control cells jointly, and REFUSE a rung whose single worst control exceeds twice
its baseline reading at the frozen endpoint. The refusal is not a tie-break — a
term whose every improving rung is refused has its FORM refused, and that is the
result rather than a failure to produce one.

Nothing here decides which rung is "close enough". It prints the whole ladder,
names the rung the rule selects, and says on which control a refused rung was
refused.

    python3 fit-tables.py t1
    python3 fit-tables.py t2-s1
"""
import glob
import json
import os
import sys
from statistics import mean

HERE = os.path.dirname(os.path.abspath(__file__))
SWEEPS = os.environ.get("VITREA_G1C_SWEEPS", "/tmp/w27c-g1c")


def load(prefix):
    rungs = {}
    for path in sorted(glob.glob(os.path.join(SWEEPS, f"{prefix}*.json"))):
        doc = json.load(open(path))
        rungs[doc["label"]] = doc
    if not rungs:
        raise SystemExit(f"fit-tables: no rung matrix under {SWEEPS} matching {prefix}*")
    return rungs


def main():
    prefix = sys.argv[1] if len(sys.argv) > 1 else "t1"
    plan = json.load(open(os.path.join(HERE, "sweep-plan.json")))
    partition = json.load(open(os.path.join(HERE, "partition.json")))
    term = partition["terms"][0 if prefix.startswith("t1") else 1]
    calibration = set(term["calibration"]["cells"])

    rungs = load(prefix)
    baseline_label = sorted(rungs)[0] if prefix.startswith("t1") else None
    # The baseline is the rung that carries the frozen document, named by its own
    # matrix rather than assumed from an ordering.
    for label, doc in rungs.items():
        if doc["endpointUnderTest"]["isFrozenG1Endpoint"]:
            baseline_label = label
    if baseline_label is None or baseline_label not in rungs:
        raise SystemExit("fit-tables: no rung in this ladder carries the frozen endpoint, so "
                         "there is no baseline to refuse a control against")

    def cells(doc):
        return {f"{r['profile']}/{r['scene']}": r for r in doc["rows"]}

    base_cells = cells(rungs[baseline_label])
    table = {}
    for label in sorted(rungs, key=lambda l: (l != baseline_label, l)):
        rows = cells(rungs[label])
        cal = [r for k, r in rows.items() if k in calibration]
        ctl = [(k, r) for k, r in rows.items() if k not in calibration]
        worst = None
        for key, row in ctl:
            base = base_cells.get(key)
            if base is None:
                continue
            ratio = row["body"]["deltaE"] / max(base["body"]["deltaE"], 1e-9)
            if worst is None or ratio > worst["ratio"]:
                worst = {"cell": key, "ratio": ratio,
                         "bodyDeltaE": row["body"]["deltaE"],
                         "baselineBodyDeltaE": base["body"]["deltaE"]}
        table[label] = {
            "patchSha256": rungs[label]["patchSha256"],
            "isFrozen": rungs[label]["endpointUnderTest"]["isFrozenG1Endpoint"],
            "calibrationMeanBodyDeltaE": mean(r["body"]["deltaE"] for r in cal) if cal else None,
            "calibrationMeanFullCanvas": mean(r["deltaE"]["mean"] for r in cal) if cal else None,
            "controlMeanBodyDeltaE": mean(r["body"]["deltaE"] for _, r in ctl) if ctl else None,
            "jointMeanBodyDeltaE": mean(r["body"]["deltaE"] for r in list(rows.values())),
            "worstControl": worst,
            "refused": worst is not None and worst["ratio"] > 2.0,
            "rows": sorted(
                [{"cell": k, "role": "calibration" if k in calibration else "control",
                  "isControlOutsideBed": r.get("isControl", False),
                  "bodyDeltaE": r["body"]["deltaE"], "fullCanvasDeltaE": r["deltaE"]["mean"],
                  "webY": r["body"]["webY"], "nativeY": r["body"]["nativeY"],
                  "webSD": r["body"]["webSD"], "nativeSD": r["body"]["nativeSD"]}
                 for k, r in rows.items()],
                key=lambda r: (r["role"] != "calibration", r["cell"]),
            ),
        }

    baseline_cal = table[baseline_label]["calibrationMeanBodyDeltaE"]
    admissible = [
        l for l, t in table.items()
        if not t["refused"] and t["calibrationMeanBodyDeltaE"] < baseline_cal
    ]
    selected = (
        min(admissible, key=lambda l: table[l]["jointMeanBodyDeltaE"]) if admissible
        else baseline_label
    )
    out = {
        "gate": "W27c G1c / claims §5.141",
        "term": term["id"],
        "ladder": prefix,
        "rule": plan["objective"],
        "baseline": baseline_label,
        "admissible": sorted(admissible),
        "selected": selected,
        "formRefused": not admissible,
        "whyRefused": (
            None if admissible else
            "every rung that lowers the calibration cells raises a control above twice its "
            "baseline, so the one-parameter family cannot hold the calibration cells and the "
            "controls together and the FORM is refused (sweep-plan.json, objective.refusalRule)"
        ),
        "rungs": table,
    }
    with open(os.path.join(HERE, f"fit-{prefix}.json"), "w") as handle:
        json.dump(out, handle, indent=1)
        handle.write("\n")

    print(f"{term['id']} ladder {prefix} — baseline {baseline_label}")
    print(f"{'rung':28} {'cal body ΔE':>12} {'ctl body ΔE':>12} {'joint':>10} "
          f"{'worst control':>10}  verdict")
    for label in sorted(table, key=lambda l: (not table[l]["isFrozen"], l)):
        t = table[label]
        w = t["worstControl"]
        print(f"{label:28} {t['calibrationMeanBodyDeltaE']:12.5f} "
              f"{t['controlMeanBodyDeltaE']:12.5f} {t['jointMeanBodyDeltaE']:10.5f} "
              f"{(w['ratio'] if w else 1.0):9.2f}×  "
              f"{'REFUSED ' + w['cell'].split('/')[1] if t['refused'] else ''}")
    print(f"\nselected: {selected}"
          + ("   (THE FORM IS REFUSED — no rung both improves and clears the cap)"
             if out["formRefused"] else ""))


sys.exit(main())
