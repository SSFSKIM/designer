"""W26 G0 — one ladder rung's material profile documents, written to SCRATCH.

W25 G3's `g3-candidate.py`, unchanged in behaviour and carried here because a rung is still the two
committed documents with this wave's constants overridden. The committed documents under
`packages/calibration/profiles/` are read and never written (X2), so an abandoned rung leaves
nothing behind and the declaration at G2 is the only thing that touches them.

    g0-candidate.py <outdir> light:sizeScatterGainMax=10.3 both:sizeHeavyTapSigma=20
"""

import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROFILES = os.path.abspath(os.path.join(HERE, "..", "..", "..", "profiles"))
DOCS = {
    "light": "apple-macos-26.5-1x-light-standard.json",
    "dark": "apple-macos-26.5-1x-dark-standard.json",
}


def assign(patch, dotted, value):
    node = patch
    parts = dotted.split(".")
    for part in parts[:-1]:
        node = node.setdefault(part, {})
    node[parts[-1]] = value


def main(argv):
    outdir = argv[0]
    os.makedirs(outdir, exist_ok=True)
    docs = {k: json.load(open(os.path.join(PROFILES, v))) for k, v in DOCS.items()}
    for spec in argv[1:]:
        scope, rest = spec.split(":", 1)
        dotted, raw = rest.split("=", 1)
        value = json.loads(raw)
        for key in (["light", "dark"] if scope == "both" else [scope]):
            assign(docs[key]["patch"], dotted, value)
    for key, name in DOCS.items():
        path = os.path.join(outdir, name)
        doc = copy.deepcopy(docs[key])
        doc.pop("resolvedMaterialSha256", None)
        doc["$comment-w26-g0-rung"] = (
            "SCRATCH. A W26 G0 ladder rung, not a profile: the committed document with this "
            "wave's constants overridden and the resolved fingerprint dropped. Never commit."
        )
        json.dump(doc, open(path, "w"), indent=2)
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
