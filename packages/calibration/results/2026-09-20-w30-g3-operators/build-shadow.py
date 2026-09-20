#!/usr/bin/env python3
"""W30 G3 — merge a set of fitted shadow constants into the four macOS 27 documents.

    python3 build-shadow.py <constants.json> <out-dir>      # a fit candidate
    python3 build-shadow.py <constants.json> --in-place     # the seal

W29 G3b's `build-shadow.py` with two differences, both forced by what this child
fits. The σ law's three leaves live on the ACTIVE documents only — a receded
document is a difference over the active document of its own scheme and
`withMaterialOverrides` merges `outerShadow` leaf by leaf, so a leaf the recede
does not name is the active document's own and the law needs no second copy.
The seven amplitude leaves the recede DOES name are written into it leaf for
leaf from its own scheme's active document, which is what "the receded documents
inherit the block" means and what W29 G3b's pair already does (claims §5.154
§5): on macOS 27 the recede keeps the shadow rather than removing it.

`reducedTransparencyOcclusion` is NOT written. It is outside this child's fit
(contract X3 names the σ, the six occlusion anchors and `liftAmplitude`), and it
is the one amplitude the reduced-transparency fold writes into all six anchors,
so the accessibility beds' shadow moves in this child through σ alone. That is
deliberate and §5.159 records what it costs.

Every other key of every document is copied through unchanged, byte for byte in
value if not in formatting, and the two frozen macOS 26.5 documents are never
opened (X1).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent.parent
PROFILES = PACKAGE / "profiles"

ACTIVE = {
    "light": "apple-macos-27.0-1x-light-standard-glass0.5",
    "dark": "apple-macos-27.0-1x-dark-standard-glass0.5",
}

# The leaves a receded document carries in its own `outerShadow` block and
# therefore inherits leaf for leaf from its scheme's active document. Read from
# the committed receded documents rather than listed by hand where possible;
# this tuple is the order they are written in.
INHERITED = (
    "thinOcclusionDark", "thinOcclusionMid", "thinOcclusionBright",
    "thickOcclusionAt96", "thickOcclusionAt128", "thickOcclusionAt160",
    "liftAmplitude",
)

# The σ law's three leaves plus the width they pivot about. Active documents only.
SIGMA = ("sigmaPx", "sigmaSlopePerSpan", "sigmaSpanRefPx", "sigmaThinOffsetPx")

# The scatter's five leaves (W30 Decision Log 2 (d)), on `MaterialProfile`'s top
# level rather than inside the shadow's block. Written into the two ACTIVE
# documents only: a receded document is a difference over the active document of
# its own scheme and `withMaterialOverrides` merges leaf by leaf, so a leaf the
# recede does not name is the active document's own. Two of the five are
# scheme-conditioned (`sizeHeavySecondShare`, `sizeScatterScaleGain`) and three
# are not — a spatial scale is a property of the source raster, which is the same
# raster in both schemes — but all five are written into both documents, because
# each is a patch over the renderer's default and neither inherits from the other.
SCATTER = (
    "sizeHeavySecondSigma", "sizeHeavySecondSigma2x", "sizeHeavySecondShare",
    "sizeScatterScaleGain", "sizeScatterScaleRef",
)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        raise SystemExit(__doc__)
    constants = json.loads(Path(argv[0]).read_text())
    in_place = argv[1] == "--in-place"
    out = PROFILES if in_place else Path(argv[1])
    out.mkdir(parents=True, exist_ok=True)

    for scheme, name in ACTIVE.items():
        block = constants[scheme]
        document = json.loads((PROFILES / f"{name}.json").read_text())
        shadow = dict(document["patch"]["outerShadow"])
        for leaf in SIGMA + INHERITED:
            if leaf in block:
                shadow[leaf] = block[leaf]
        document["patch"]["outerShadow"] = shadow
        scatter = block.get("scatter") or {}
        for leaf in SCATTER:
            if leaf in scatter:
                document["patch"][leaf] = scatter[leaf]
        (out / f"{name}.json").write_text(json.dumps(document, indent=2) + "\n")
        print(f"{'sealed ' if in_place else 'candidate '}{name}")
        for leaf in SIGMA + INHERITED:
            print(f"    {leaf:<24}{shadow[leaf]}")
        for leaf in SCATTER:
            if leaf in scatter:
                print(f"    {leaf:<24}{scatter[leaf]}")

        receded_name = f"{name}-receded"
        receded = json.loads((PROFILES / f"{receded_name}.json").read_text())
        receded_shadow = dict(receded["patch"]["outerShadow"])
        for leaf in INHERITED:
            if leaf in receded_shadow and leaf in block:
                receded_shadow[leaf] = block[leaf]
        receded["patch"]["outerShadow"] = receded_shadow
        (out / f"{receded_name}.json").write_text(json.dumps(receded, indent=2) + "\n")
        print(f"{'sealed ' if in_place else 'candidate '}{receded_name}"
              f"  (the σ law inherited from {name}, not copied)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
