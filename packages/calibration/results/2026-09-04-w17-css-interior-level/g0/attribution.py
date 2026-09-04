#!/usr/bin/env python3
"""W17 G0 (a) — the attribution table, read out of the six scratch matrices.

The instrument is six GPU-tier renders of the same bed under six profile documents: the committed
default, the four single-term declines, and all four declined together. What each cell contributes
is `material.interiorMeanWeb` — the mean linear-light luminance of the capture over the NATIVE
silhouette, the same statistic the bed's own level rows are read from and the one contract X4
validates.

Two things this script does not do. It does not read the CSS tier: the declines are a property of
the renderer, and the cross-tier comparison belongs to (d). And it does not average over cells: the
sum test is per cell, because a term that is large on a thin span and small on a large one would
pass on a mean and fail where the conversion has to work.

The residual reported is `default − all-declined` minus the sum of the four `default − declined`
differences. It is zero exactly when the four terms superpose; anything else is the interaction
between them, which is a real property of the shader (the rim's light is clamped into an alpha, the
lens moves the pixels the rim then lights) and is what the 0.005 clause is a bound on.

Usage: `python3 attribution.py <matrixDir> [outJson]`.
"""

import json
import sys
from pathlib import Path

CONFIGS = ["default", "no-lens", "no-rim", "no-highlight", "no-lift", "all-declined"]
TERMS = ["no-lens", "no-rim", "no-highlight", "no-lift"]


def read(path):
    """The texture-tier cells of one matrix, keyed by profile and scene."""
    cells = json.loads(Path(path).read_text())["cells"]
    out = {}
    for cell in cells:
        if cell["tier"] != "texture":
            continue
        material = cell.get("material")
        key = (cell["key"]["profileKey"], cell["key"]["sceneId"])
        out[key] = None if material is None else material["interiorMeanWeb"]["value"]
    return out


def main():
    matrix_dir = Path(sys.argv[1])
    tables = {config: read(matrix_dir / f"{config}.json") for config in CONFIGS}

    keys = sorted(tables["default"])
    rows = []
    absent = []
    for key in keys:
        values = {config: tables[config].get(key) for config in CONFIGS}
        if any(value is None for value in values.values()):
            absent.append(key)
            continue
        default = values["default"]
        terms = {config: default - values[config] for config in TERMS}
        whole = default - values["all-declined"]
        rows.append(
            {
                "profileKey": key[0],
                "sceneId": key[1],
                "default": default,
                "allDeclined": values["all-declined"],
                "whole": whole,
                "terms": terms,
                "sumOfTerms": sum(terms.values()),
                "residual": whole - sum(terms.values()),
            }
        )

    worst = max(rows, key=lambda row: abs(row["residual"]))
    over = [row for row in rows if abs(row["residual"]) > 0.005]
    report = {
        "cells": len(rows),
        "absentMaterialAxis": [list(key) for key in absent],
        "worstResidual": {
            "profileKey": worst["profileKey"],
            "sceneId": worst["sceneId"],
            "residual": worst["residual"],
        },
        "cellsOver0.005": [
            {"profileKey": row["profileKey"], "sceneId": row["sceneId"], "residual": row["residual"]}
            for row in over
        ],
        "rows": rows,
    }
    if len(sys.argv) > 2:
        Path(sys.argv[2]).write_text(json.dumps(report, indent=1) + "\n")

    print(f"cells {len(rows)}   absent material axis {len(absent)}")
    print(
        f"worst residual {worst['residual']:+.6f} on {worst['profileKey']} {worst['sceneId']}; "
        f"cells over 0.005: {len(over)}"
    )
    header = f"{'profile':>4} {'scene':<40} {'default':>8} {'whole':>8} " + " ".join(
        f"{term.replace('no-', ''):>8}" for term in TERMS
    ) + f" {'sum':>8} {'resid':>8}"
    print(header)
    for row in rows:
        short = row["profileKey"].removeprefix("apple-macos-26.5-").removesuffix("-standard")
        print(
            f"{short:>4} {row['sceneId']:<40} {row['default']:8.4f} {row['whole']:+8.4f} "
            + " ".join(f"{row['terms'][term]:+8.4f}" for term in TERMS)
            + f" {row['sumOfTerms']:+8.4f} {row['residual']:+8.4f}"
        )


if __name__ == "__main__":
    main()
