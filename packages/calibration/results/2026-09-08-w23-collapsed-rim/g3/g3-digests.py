"""W23 G3 — the rows the landing must reproduce byte for byte (contract X3).

W21 G1's script, moved to this wave's document. The dry run is the wave's one read of the canonical
holdout, so G2's rebuild has to be the SAME render and not merely a similar one: a digest per
capture taken here, at the frozen configuration, and re-taken there. If a byte moves, either a
constant moved or the renderer did, and both are things the wave wants to hear about before it reads
a fidelity number.

BOTH profile documents move in this wave and both are recorded: the light one carries the rim law's
intercept and gain, the band's second anchor and the two collapsed rims, and the dark one carries
its own intercept and gain. Their digests are printed beside the captures so a G2 that reproduces
these bytes can say WHICH documents it reproduced them from, out of this file rather than out of a
commit message.

    g3-digests.py <dry-run captures dir> <dry-run matrix.json> > g1-digests.txt
"""

import hashlib
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", ".."))
PROFILES = os.path.join(ROOT, "packages", "calibration", "profiles")
DOCUMENTS = (
    "apple-macos-26.5-1x-light-standard.json",
    "apple-macos-26.5-1x-dark-standard.json",
)


def digest(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def main():
    captures, matrix_path = sys.argv[1:3]
    print("W23 G3 — the dry run's captures, at the frozen configuration")
    for name in DOCUMENTS:
        path = os.path.join(PROFILES, name)
        document = json.load(open(path))
        print(f"profile document      packages/calibration/profiles/{name}")
        print(f"  file sha256         {digest(path)}")
        print(f"  resolvedMaterialSha256  {document['resolvedMaterialSha256']}")
        print(f"  patch               {json.dumps(document['patch'], sort_keys=True)}")
    print()
    keys = set()
    for cell in json.load(open(matrix_path))["cells"]:
        keys.add(
            (cell["key"]["profileKey"], cell["key"]["web"]["renderer"], cell["key"]["sceneId"])
        )
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
