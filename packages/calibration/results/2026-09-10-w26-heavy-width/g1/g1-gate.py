"""W26 G1 — the gate's matrix at the candidate, assembled so the floors can be re-read.

`adopted-thresholds.test.ts` is the ONLY copy of the adopted bounds, the fourteen thick regression
floors and the conditioning predicate, and it reads whichever matrix `VITREA_MATRIX_PATH` names
(contract X6). It asserts over the WHOLE frozen bed — counts, partitions and a "every floor is
reached by a gated row" guard — so a matrix carrying only this child's re-captured rows fails on
absence rather than on any measurement.

**X3 says the holdout is read once, at the declaring child's dry run.** So this child captures
`calibration,validation` at the candidate and nothing else, and this script assembles the gate's
input as:

  * every calibration and validation cell from the CANDIDATE capture, and
  * every holdout cell from the canonical committed matrix, unchanged.

The holdout rows in the assembled matrix are therefore the 0.14.0 bed's own. Any holdout assertion
the gate makes over them is a statement about the frozen bed and NOT about the candidate, and that
is stated here rather than discovered later: only the calibration and validation rows in this run
are evidence about the candidate. G2 reads the holdout once, properly.

    g1-gate.py [--bed DIR] [--out FILE]
"""

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PACKAGE = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CANONICAL = os.path.join(PACKAGE, "results", "matrix.json")


def key_of(cell):
    k = cell["key"]
    return (cell["tier"], k["profileKey"], k["sceneId"])


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--bed", default="/Users/new/.claude/jobs/5c70e47f/tmp/w26/g1/bedc/bed.json")
    ap.add_argument("--out", default="/Users/new/.claude/jobs/5c70e47f/tmp/w26/g1/bedc/gate.json")
    args = ap.parse_args(argv)

    canonical = json.load(open(CANONICAL))
    candidate = json.load(open(args.bed))

    # The candidate's newest row per key — a `--write-partial` run appends beside older rows.
    newest = {}
    for cell in candidate["cells"]:
        newest[key_of(cell)] = cell
    kept = [c for c in newest.values() if c["fixtureSet"] in ("calibration", "validation")]
    holdout = [c for c in canonical["cells"] if c["fixtureSet"] == "holdout"]

    out = {**canonical, "cells": kept + holdout}
    json.dump(out, open(args.out, "w"))
    print(f"{len(kept)} candidate calibration/validation cells "
          f"+ {len(holdout)} canonical holdout cells -> {args.out}")
    canon_bed = [c for c in canonical["cells"]
                 if c["fixtureSet"] in ("calibration", "validation")]
    missing = {key_of(c) for c in canon_bed} - {key_of(c) for c in kept}
    if missing:
        print(f"MISSING {len(missing)} bed rows the candidate did not capture:", file=sys.stderr)
        for k in sorted(missing):
            print(f"  {k}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
