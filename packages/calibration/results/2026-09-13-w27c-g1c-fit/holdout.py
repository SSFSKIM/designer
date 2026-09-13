#!/usr/bin/env python3
"""W27c G1c: the four holdout cells, read once on the frozen endpoint.

They are declared in `partition.json` before the fit and captured by no sweep
rung: T1's ladder patterns exclude the span-44 pair by name and T2's exclude the
span-80 pair, so the first vitrea capture either of them sees under this child is
the frozen re-read. This script only lifts them out of that read and states what
each was a check OF — the fit selected on none of them, and no constant moves in
response to what is printed here.

    python3 holdout.py /tmp/w27c-g1c-frozen/checking.json
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    read = json.load(open(sys.argv[1] if len(sys.argv) > 1
                          else "/tmp/w27c-g1c-frozen/checking.json"))
    declared = json.load(open(os.path.join(HERE, "fitted-endpoint.json")))
    partition = json.load(open(os.path.join(HERE, "partition.json")))
    g2 = json.load(open(os.path.join(HERE, "../2026-09-13-w27c-g2-read/checking-matrix.json")))
    before = {(r["profile"], r["scene"]): r for r in g2["rows"]}
    rows = {f"{r['profile']}/{r['scene']}": r for r in read["rows"]}

    checks = {
        "apple-macos-26.5-1x-dark-standard/light-solid__capsule-button__inactive":
            "T1: does one far ordinate fitted where the thin row stands alone predict span 44? "
            "The term was REFUSED, so the endpoint here is the frozen one and this reads what a "
            "refused term leaves behind.",
        "apple-macos-26.5-2x-dark-standard/light-solid__capsule-button__inactive":
            "T1 at 2x, same question.",
        "apple-macos-26.5-1x-light-increased-contrast/dark-solid__rrect-80__inactive":
            "T2: is the fitted panel span-independent, or was the thin end bought at the thick "
            "end's expense?",
        "apple-macos-26.5-1x-light-reduced-transparency/dark-solid__rrect-80__inactive":
            "T2 under the other policy, same question.",
    }
    out = {
        "gate": "W27c G1c / claims §5.141",
        "endpoint": declared["patchSha256"],
        "spentAt": read["machineAccessibility"]["readAt"],
        "rule": partition["terms"][0]["holdout"]["readOnce"],
        "cells": [],
    }
    for cell, why in checks.items():
        row = rows.get(cell)
        if row is None:
            raise SystemExit(f"holdout: the frozen read does not carry {cell}")
        held = before.get((row["profile"], row["scene"]))
        out["cells"].append({
            "cell": cell,
            "checks": why,
            "scored": row["scored"],
            "bodyDeltaE": row["body"]["deltaE"],
            "frozenG1BodyDeltaE": held["body"]["deltaE"] if held else None,
            "fullCanvasDeltaE": row["deltaE"]["mean"],
            "bodyYWeb": row["body"]["webY"],
            "bodyYNative": row["body"]["nativeY"],
            "captureSha256": row["captureSha256"],
            "unchangedFromG2": held is not None and held["captureSha256"] == row["captureSha256"],
        })
    with open(os.path.join(HERE, "holdout.json"), "w") as handle:
        json.dump(out, handle, indent=1)
        handle.write("\n")

    for c in out["cells"]:
        print(f"{c['cell'].replace('apple-macos-26.5-', ''):64} body ΔE "
              f"{c['frozenG1BodyDeltaE']:.5f} -> {c['bodyDeltaE']:.5f}   "
              f"Y {c['bodyYWeb']:.5f}/{c['bodyYNative']:.5f}   "
              f"{'unchanged' if c['unchangedFromG2'] else 'MOVED'}")


sys.exit(main())
