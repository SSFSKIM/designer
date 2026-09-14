#!/usr/bin/env python3
"""Extract the eight predeclared holdout cells from the one resumed frozen read."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
read = json.load(open(os.path.join(HERE, "frozen-checking-matrix.json")))
partial = json.load(open(os.path.join(HERE, "frozen-read-partial.json")))
declared = json.load(open(os.path.join(HERE, "fitted-endpoint.json")))
partition = json.load(open(os.path.join(HERE, "partition.json")))
prior = json.load(open(os.path.join(HERE, "../2026-09-13-w27c-g1c-fit/frozen-checking-matrix.json")))
prior_rows = {f"{r['profile']}/{r['scene']}": r for r in prior["rows"]}
rows = {f"{r['profile']}/{r['scene']}": r for r in read["rows"]}
partial_cells = {f"{r['profile']}/{r['scene']}" for r in partial["rows"]}
out = {
    "gate": "W27c G1d / claims §5.143",
    "endpoint": declared["patchSha256"],
    "rule": partition["objective"]["holdout"],
    "logicalRead": {
        "startedAt": partial["machineAccessibility"]["readAt"],
        "resumedAt": read["machineAccessibility"]["readAt"],
        "reason": "The first segment stopped before its first H-group cell because the native resolver asked the new sitting plurality for a pre-existing fixture. frozen-read.ts resumed the same fixed endpoint, skipped every row already captured, and read each remaining cell once.",
    },
    "cells": [],
}
for cell in declared["holdout"]["cells"]:
    row = rows.get(cell)
    if row is None:
        raise SystemExit(f"missing holdout cell {cell}")
    before = prior_rows.get(cell)
    out["cells"].append({
        "cell": cell,
        "readSegment": "initial" if cell in partial_cells else "resume",
        "repeats": row["repeats"],
        "bodyDeltaE": row["body"]["deltaE"],
        "g1cBodyDeltaE": before["body"]["deltaE"] if before else None,
        "fullCanvasDeltaE": row["deltaE"]["mean"],
        "bodyYWeb": row["body"]["webY"],
        "bodyYNative": row["body"]["nativeY"],
        "captureSha256": row["captureSha256"],
    })
with open(os.path.join(HERE, "holdout.json"), "w") as handle:
    json.dump(out, handle, indent=1)
    handle.write("\n")
for row in out["cells"]:
    print(f"{row['cell']}: {row['readSegment']} body ΔE {row['bodyDeltaE']:.5f} "
          f"Y {row['bodyYWeb']:.5f}/{row['bodyYNative']:.5f}")
