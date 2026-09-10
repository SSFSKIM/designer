"""W26 G2c — the diagnostic rungs' profile documents, written to scratch.

One rung changes one thing against the candidate, so that the edge→centre gradient the user's eye
found on the dark `checkerboard-64` rrects can be ATTRIBUTED rather than guessed at. The committed
documents are read-only inputs; every rung is a copy in scratch with a patch merged into `patch`.

The rungs, and what each one would prove:

  d9      the candidate itself, 9 / 9 — the column the eye objected to.
  t13     the candidate's MECHANISM at the old WIDTH (13.418 / 13.418). The 0.14.0 material drew
          13.418 through the chain tap; this draws it through the heavy texture. If the gradient is
          absent here it belongs to the width, and if it is present it belongs to the texture path.
  flat    the candidate with the body's depth RAMP switched off — the three 1x ramp starts and the
          three 2x ones set to the deep value's own anchor and the reach to 0, so `kScatter` is one
          number over the whole pane instead of growing from the contour inward. If the gradient
          goes, it is the ramp.
  nolens  the candidate with `lensRefractionGain` 0 — no refracted displacement of the sample near
          the edge. If the gradient goes, it is the lens.
  flat13  the ramp off AND the old width, the control for the pair.

`sizeScatterRampReach1xPx` 0 is what turns the ramp off: `scatterSharpShare` interpolates from the
ramp's start to the deep value over that reach in device px, so a reach of 0 leaves the deep value
everywhere. The starts are left where they are precisely so that the reach is the only lever moved.

    g2c-docs.py [--out DIR]
"""

import argparse
import copy
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PROFILES = os.path.abspath(os.path.join(HERE, "..", "..", "..", "profiles"))
LIGHT = "apple-macos-26.5-1x-light-standard.json"
DARK = "apple-macos-26.5-1x-dark-standard.json"

RAMP_OFF = {"sizeScatterRampReach1xPx": 0, "sizeScatterRampReach2xPx": 0}

RUNGS = {
    "d9": {},
    "t13": {"sizeHeavyTapSigma": 13.418, "sizeHeavyTapSigma2x": 13.418},
    "flat": dict(RAMP_OFF),
    "nolens": {"lensRefractionGain": 0},
    "flat13": {**RAMP_OFF, "sizeHeavyTapSigma": 13.418, "sizeHeavyTapSigma2x": 13.418},
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/Users/new/.claude/jobs/5c70e47f/tmp/w26/g2c/docs")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    for rung, overrides in RUNGS.items():
        for name in (LIGHT, DARK):
            document = json.load(open(os.path.join(PROFILES, name)))
            patch = copy.deepcopy(document.get("patch") or {})
            # BOTH documents take the patch, always (W26 Decision Log 4 (c)): the dark document is a
            # difference document resolved over the renderer's default, so a rung that wrote the
            # light one alone would render the dark scheme at the code defaults — which for a
            # diagnostic about the dark scheme would measure the wrong material entirely.
            patch.update(overrides)
            document["patch"] = patch
            document["$comment-g2c"] = [
                f"SCRATCH — W26 G2c diagnostic rung '{rung}'. Not a candidate and not committed.",
                f"Overrides against the landed material: {json.dumps(overrides, sort_keys=True)}",
            ]
            out = os.path.join(args.out, f"{rung}-{name}")
            json.dump(document, open(out, "w"), indent=2)
        print(f"{rung:8s} {json.dumps(overrides, sort_keys=True)}")
    print(f"-> {args.out}")


if __name__ == "__main__":
    main()
