"""W21 G1 — the rows the landing must reproduce byte for byte (contract X6).

The dry run is the wave's one read of the canonical holdout, so G2's rebuild has to be the SAME
render and not merely a similar one. What makes that checkable is a digest per capture taken here,
at the frozen constants, and re-taken there: if a byte moves, either a constant moved or the
renderer did, and both are things the wave wants to hear about before it reads a fidelity number.

The manifest also records the profile document's own digest and its `resolvedMaterialSha256`, so a
G2 that reproduces the bytes can say WHICH document it reproduced them from.

    g1-digests.py <dry-run captures dir> <dry-run matrix.json> > g1-digests.txt
"""

import hashlib
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))
DOCUMENT = os.path.join(ROOT, "packages", "calibration", "profiles",
                        "apple-macos-26.5-1x-dark-standard.json")


def digest(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    captures, matrix_path = sys.argv[1:3]
    document = json.load(open(DOCUMENT))
    print("W21 G1 — the dry run's captures, at the frozen constants")
    print(f"profile document      packages/calibration/profiles/{os.path.basename(DOCUMENT)}")
    print(f"  file sha256         {digest(DOCUMENT)}")
    print(f"  resolvedMaterialSha256  {document['resolvedMaterialSha256']}")
    print(f"  patch               {json.dumps(document['patch'], sort_keys=True)}")
    print()
    keys = set()
    for cell in json.load(open(matrix_path))["cells"]:
        keys.add((cell["key"]["profileKey"], cell["key"]["web"]["renderer"],
                  cell["key"]["sceneId"]))
    print(f"{'sha256':64s}  capture")
    for profile, renderer, scene in sorted(keys):
        relative = os.path.join(profile, scene, f"{scene}__{renderer}.png")
        path = os.path.join(captures, relative)
        if not os.path.exists(path):
            print(f"{'MISSING':64s}  {relative}")
            continue
        print(f"{digest(path)}  {relative}")


if __name__ == "__main__":
    main()
