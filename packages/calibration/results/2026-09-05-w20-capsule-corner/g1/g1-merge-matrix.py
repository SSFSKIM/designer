"""W20 G1: a whole matrix for the gate, from the dry run's GPU rows over the W19 bed.

`adopted-thresholds.test.ts` reads one matrix and asserts the WHOLE bed — every profile's cell
count, both tiers, the holdout included — so a partial dry run cannot be handed to it directly.
This writes a scratch matrix that is the canonical W19 bed with every cell the dry run re-measured
replaced by the dry run's row, keyed by (profile, scene, renderer).

What that matrix therefore is, said plainly so the gate's verdict can be read for what it is:

  - every GPU-tier calibration and validation cell is THIS WAVE'S measurement;
  - every CSS-tier cell is the W19 bed's, which this wave binds byte-identical and does not
    re-capture (contract X3, verified at G2);
  - every HOLDOUT cell is the W19 bed's, including four GPU capsule cells the fix does move —
    they are not read at this gate by the wave's own rule, so the gate's reading of them is
    W19's and is stale by exactly the fix.

    python3 g1-merge-matrix.py <dry-run.json> <canonical-matrix.json> <out.json>
"""
import json
import sys


def key(cell):
    return (cell["key"]["profileKey"], cell["key"]["sceneId"], cell["key"]["web"]["renderer"])


def main():
    dry_path, canonical_path, out_path = sys.argv[1:4]
    dry = json.load(open(dry_path))
    canonical = json.load(open(canonical_path))
    replacement = {key(cell): cell for cell in dry["cells"]}
    merged = []
    replaced = 0
    for cell in canonical["cells"]:
        candidate = replacement.get(key(cell))
        if candidate is None:
            merged.append(cell)
        else:
            merged.append(candidate)
            replaced += 1
    unseen = set(replacement) - {key(cell) for cell in canonical["cells"]}
    canonical["cells"] = merged
    json.dump(canonical, open(out_path, "w"))
    print(f"{len(merged)} cells, {replaced} replaced from the dry run, {len(unseen)} dry-run rows "
          f"with no canonical counterpart")
    for entry in sorted(unseen):
        print(f"  unmatched {entry}")


if __name__ == "__main__":
    main()
