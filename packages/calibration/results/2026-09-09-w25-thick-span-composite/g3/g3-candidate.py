"""W25 G3 — one ladder rung's material profile documents, written to SCRATCH.

A rung is a material, and a material is the two committed profile documents with this wave's
constants overridden. This writes the pair into the rung's own scratch directory and prints the
paths; the committed documents under `packages/calibration/profiles/` are read and never written
(X2), so a rung that is abandoned leaves nothing behind and the declaration is the only thing that
touches them.

The overrides are given as dotted paths so the optics leaf can be reached:

    g3-candidate.py <outdir> light:sizeScatterHeavyShareThick1x=0.455 \
                             both:optics.regular.rimAlongSideSlope=0.45 \
                             dark:sizeToneLevelFar=-0.02

`light:` writes the light document's patch only, `dark:` the dark difference document's only, and
`both:` writes each into its own document — which is what a material constant that is not a
colour-scheme difference needs, because the dark document is a DIFFERENCE document over the light
material's defaults and does not inherit the light document's patch (X7). A constant the dark
scheme does not separate is therefore written `light:` and left absent from the dark document,
where the renderer default (0) applies — so `both:` is used only where a value must reach both
schemes and the dark document would otherwise fall back to the default.
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
    parts = dotted.split(".")
    node = patch
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
        # The fingerprint a scratch document carries would be the committed one's and would be a
        # lie about the material below it; `compare` does not read it, and no test opens a scratch
        # document, so it is dropped rather than recomputed under a name it does not deserve.
        doc = copy.deepcopy(docs[key])
        doc.pop("resolvedMaterialSha256", None)
        doc["$comment-w25-g3-rung"] = (
            "SCRATCH. A W25 G3 ladder rung, not a profile: the committed document with this "
            "wave's constants overridden and the resolved fingerprint dropped. Never commit."
        )
        json.dump(doc, open(path, "w"), indent=2)
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
