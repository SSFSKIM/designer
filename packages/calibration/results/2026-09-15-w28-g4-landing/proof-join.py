"""The strongest link in the seam proof, which the proof itself does not draw (§5.148 §1).

`seam-identity.ts` re-captures every inactive cell of G2's frozen matrices through the new
seam and compares each capture's SHA-256 with the `captureSha256` G2 recorded. That is a
statement about a bespoke harness. What the landing needs is the same statement about the
PUBLISHING driver, and it is already on disk: `capture-tree-after.json` hashes every file in
the canonical `web-captures/` after `compare` wrote the 470 published rows into it, so joining
the two artifacts on (profile, scene, renderer) asks whether the capture `compare` published
is the same bytes as both the seam's observation and G2's record.

It opens nothing, re-captures nothing and computes no fidelity number; it is two committed
JSON files joined on a path. A cell is `absent` when the canonical tree holds no capture for
it, which is not a failure of identity but a statement about which cells the publishing run
reached: the run passed only the inactive scenes `scenes.json` declares `calibration`,
`validation` or `probe`, and among those a scene with no committed native fixture at a profile
plans no cell and so writes no capture.

    python3 proof-join.py
"""
import collections
import json
import pathlib

here = pathlib.Path(__file__).resolve().parent
seam = json.loads((here / "seam-identity.json").read_text())
tree = json.loads((here / "capture-tree-after.json").read_text())["files"]

joined = []
for outcome in seam["outcomes"]:
    path = f"{outcome['profile']}/{outcome['scene']}/{outcome['scene']}__{outcome['renderer']}.png"
    published = tree.get(path)
    joined.append({
        "profile": outcome["profile"],
        "scene": outcome["scene"],
        "renderer": outcome["renderer"],
        "isHoldout": outcome["isHoldout"],
        "path": path,
        "published": published,
        "recordedByG2": outcome["expected"],
        "observedBySeam": outcome["observed"],
        "state": (
            "absent" if published is None
            else "agrees" if published == outcome["expected"] and published in outcome["observed"]
            else "differs"
        ),
    })

by_state = collections.Counter(row["state"] for row in joined)
report = {
    "gate": "W28 G4 — the publishing driver reproduces G2's bytes",
    "claims": "§5.148 §1",
    "joins": ["seam-identity.json", "capture-tree-after.json"],
    "cells": len(joined),
    "agrees": by_state["agrees"],
    "absent": by_state["absent"],
    "differs": by_state["differs"],
    "absentCells": [
        {k: row[k] for k in ("profile", "scene", "renderer", "isHoldout")}
        for row in joined if row["state"] == "absent"
    ],
    "differingCells": [row for row in joined if row["state"] == "differs"],
    "rows": joined,
}
(here / "proof-join.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: v for k, v in report.items() if k != "rows"}, indent=2))
if report["differs"]:
    raise SystemExit(1)
