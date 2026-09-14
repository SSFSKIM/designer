#!/usr/bin/env python3
"""Apply the predeclared fit objective and 9x control refusal to each ladder."""
import glob
import json
import os
from statistics import mean

HERE = os.path.dirname(os.path.abspath(__file__))
SWEEPS = os.environ.get("VITREA_G1D_SWEEPS", "/tmp/w27c-g1d-sweeps")
PARTITION = json.load(open(os.path.join(HERE, "partition.json")))


def read(label):
    return json.load(open(os.path.join(SWEEPS, f"{label}.json")))


def score(prefix, baseline_label, calibration, out_name):
    docs = {os.path.basename(path)[:-5]: json.load(open(path))
            for path in sorted(glob.glob(os.path.join(SWEEPS, f"{prefix}*.json")))}
    baseline = read(baseline_label)
    base = {f"{r['profile']}/{r['scene']}": r for r in baseline["rows"]}
    table = {}
    for label, doc in docs.items():
        rows = {f"{r['profile']}/{r['scene']}": r for r in doc["rows"]}
        fit = [row for cell, row in rows.items() if cell in calibration]
        controls = [(cell, row) for cell, row in rows.items() if cell not in calibration]
        worst = max(({
            "cell": cell,
            "ratio": row["body"]["deltaE"] / max(base[cell]["body"]["deltaE"], 1e-9),
            "bodyDeltaE": row["body"]["deltaE"],
            "baselineBodyDeltaE": base[cell]["body"]["deltaE"],
        } for cell, row in controls), key=lambda item: item["ratio"], default=None)
        table[label] = {
            "patchSha256": doc["patchSha256"],
            "fitMeanBodyDeltaE": mean(row["body"]["deltaE"] for row in fit),
            "controlMeanBodyDeltaE": mean(row["body"]["deltaE"] for _, row in controls),
            "worstControl": worst,
            "refused": worst is not None and worst["ratio"] > 9,
            "rows": [{
                "cell": cell,
                "role": "fit" if cell in calibration else "control",
                "bodyDeltaE": row["body"]["deltaE"],
                "fullCanvasDeltaE": row["deltaE"]["mean"],
                "webY": row["body"]["webY"],
                "nativeY": row["body"]["nativeY"],
                "webSD": row["body"]["webSD"],
                "nativeSD": row["body"]["nativeSD"],
            } for cell, row in sorted(rows.items())],
        }
    baseline_mean = mean(
        row["body"]["deltaE"] for row in baseline["rows"]
        if f"{row['profile']}/{row['scene']}" in calibration
    )
    admissible = [label for label, item in table.items()
                  if not item["refused"] and item["fitMeanBodyDeltaE"] < baseline_mean]
    selected = min(admissible, key=lambda label: table[label]["fitMeanBodyDeltaE"])
    result = {
        "gate": "W27c G1d / claims §5.143",
        "rule": PARTITION["objective"],
        "baseline": baseline_label,
        "baselineFitMeanBodyDeltaE": baseline_mean,
        "admissible": sorted(admissible),
        "selected": selected,
        "rungs": table,
    }
    with open(os.path.join(HERE, out_name), "w") as handle:
        json.dump(result, handle, indent=1)
        handle.write("\n")
    print(out_name, "selected", selected, "fit", table[selected]["fitMeanBodyDeltaE"],
          "worst control", table[selected]["worstControl"])


def main():
    t1 = set(PARTITION["terms"][0]["calibration"]["cells"])
    score("t1-", "t1-baseline", t1, "fit-t1.json")
    rt = {
        f"apple-macos-26.5-1x-light-reduced-transparency/{scene}"
        for scene in ("checkerboard__rrect-md__inactive", "photo__rrect-md__inactive")
    }
    score("t2-rt-", "t2-rt-baseline", rt, "fit-t2-reduced-transparency.json")
    ic = {
        f"apple-macos-26.5-1x-light-increased-contrast/{scene}"
        for scene in ("checkerboard__rrect-md__inactive", "photo__rrect-md__inactive")
    }
    score("t2-ic-", "t2-ic-baseline", ic, "fit-t2-increased-contrast.json")


main()
