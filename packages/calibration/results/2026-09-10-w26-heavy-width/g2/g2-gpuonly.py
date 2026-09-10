"""W26 G2 — the counterfactual the floors' verdict asks for: the two constants WITHOUT clause 7.

Thirteen of the fourteen thick regression floors go under at the candidate and twelve of the
thirteen are `dom` rows. That points at a question the parent will have to rule on, and it can be
ANSWERED rather than argued, because the two tiers render independently: a CSS capture does not read
the GPU tier's material, it reads the profile document, and the two constants this wave lands are
named in the document but reach the CSS tier only through the code change of clause 7. So the bed a
landing WITHOUT clause 7 would produce is not a hypothesis — it is the candidate's texture rows
beside the 0.14.0 bed's own dom rows, and it can be gated.

What the assembled matrix is and is not:

  * every `texture` cell is the candidate's, from this child's dry run;
  * every `dom` cell is the canonical committed bed's, unchanged — which is exactly what the CSS
    tier would draw at these documents with `cssTierHeavySigmaCssPx` left on the gain path, since
    neither `sizeScatterGainMax` nor `blurSigma` nor the ramp moves this wave;
  * the `coherence` axis on the dom cells is STALE by construction — it was measured against the
    0.14.0 GPU capture and the candidate's is different. Nothing in `REGRESSION_FLOORS` or in the
    adopted bounds reads that axis, so the gate's verdict stands; a cross-tier coherence number read
    off this matrix would not.

    g2-gpuonly.py [--candidate-dir DIR] [--out FILE]
"""

import argparse
import json
import os


def newest(paths):
    out = {}
    for path in paths:
        for cell in json.load(open(path))["cells"]:
            key = (cell["tier"], cell["fixtureSet"], cell["key"]["sceneId"],
                   cell["key"]["profileKey"])
            if key not in out or cell["capturedAt"] >= out[key]["capturedAt"]:
                out[key] = cell
    return out


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate-dir", default="/Users/new/.claude/jobs/5c70e47f/tmp/w26/g2/cand")
    ap.add_argument("--canonical", default=os.path.abspath(
        os.path.join(here, "..", "..", "matrix.json")))
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    out = args.out or os.path.join(args.candidate_dir, "gate-gpuonly.json")

    bed = os.path.join(args.candidate_dir, "bed.json")
    holdout = os.path.join(args.candidate_dir, "holdout.json")
    candidate = newest([bed, holdout])
    canonical = newest([args.canonical])

    mixed = {}
    borrowed = 0
    for key, cell in candidate.items():
        if key[0] == "texture" or key not in canonical:
            mixed[key] = cell
        else:
            mixed[key] = canonical[key]
            borrowed += 1
    schema = json.load(open(bed)).get("schemaVersion")
    json.dump({"schemaVersion": schema, "cells": list(mixed.values())}, open(out, "w"))
    print(f"{len(mixed)} cells: {len(mixed) - borrowed} from the candidate (every texture row), "
          f"{borrowed} dom rows from the 0.14.0 bed -> {out}")


if __name__ == "__main__":
    main()
