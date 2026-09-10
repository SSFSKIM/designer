"""W26 G2b — the configuration the parent ruled for, assembled from captures that were actually run.

Configuration (2) of `g2-dryrun.md` §10: the two constants land on the GPU tier and clause 7's CSS
derivation is declined. Every cell of it exists on disk and none of it is a counterfactual any more:

  * the `texture` rows are W26 G2's own dry run — the same GPU material, proved unmoved by the G2b
    revert on a 72-capture sample (`g2b-gpu-identity.txt`, byte for byte);
  * the `dom` rows are G2b's own re-capture at the LANDED profile documents, which is the column
    that had to be run rather than assumed: the documents now name two constants the CSS tier no
    longer mirrors, and 640 of 644 of its captures come back byte-identical to the 0.14.0 bed with
    the four movers measured as run-to-run noise (`g2b-css-identity.txt`).

That is the difference from `g2-gpuonly.py`, which borrowed the 0.14.0 bed's dom rows to answer a
question before the ruling. This matrix borrows nothing: its cross-tier `coherence` axis is measured
against the GPU capture that actually sits beside each dom cell, so unlike the counterfactual's it
is a reading and not a stale number.

`--holdout` folds the holdout columns in. X3 is respected by construction: the GPU holdout rows are
W26 G2's ONE read, reused rather than re-taken, and the CSS holdout rows are byte-identical to the
0.14.0 bed, so nothing that moved is read twice.

    g2b-matrix.py --gpu <dir with bed.json,holdout.json> --css <dir with bed.json,holdout.json>
                  [--holdout] --out FILE
"""

import argparse
import json
import os


def newest(paths):
    out = {}
    for path in paths:
        if not os.path.exists(path):
            continue
        for cell in json.load(open(path))["cells"]:
            key = (cell["tier"], cell["fixtureSet"], cell["key"]["sceneId"],
                   cell["key"]["profileKey"])
            if key not in out or cell["capturedAt"] >= out[key]["capturedAt"]:
                out[key] = cell
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gpu", required=True)
    ap.add_argument("--css", required=True)
    ap.add_argument("--holdout", action="store_true")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    columns = ["bed.json"] + (["holdout.json"] if args.holdout else [])
    gpu = newest([os.path.join(args.gpu, name) for name in columns])
    css = newest([os.path.join(args.css, name) for name in columns])

    cells = {}
    for key, cell in gpu.items():
        if key[0] == "texture":
            cells[key] = cell
    for key, cell in css.items():
        if key[0] == "dom":
            cells[key] = cell

    schema = json.load(open(os.path.join(args.gpu, "bed.json"))).get("schemaVersion")
    json.dump({"schemaVersion": schema, "cells": list(cells.values())}, open(args.out, "w"))
    texture = sum(1 for key in cells if key[0] == "texture")
    print(f"{len(cells)} cells: {texture} texture rows from W26 G2's dry run, "
          f"{len(cells) - texture} dom rows from G2b's re-capture -> {args.out}")


if __name__ == "__main__":
    main()
