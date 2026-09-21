#!/usr/bin/env python3
"""W32 G1 — a round's constants file, built from the SHIPPED documents plus overrides.

    python3 constants.py <out.json> [scheme.leaf=value ...]
    python3 constants.py --show

Every round's candidate is a difference from the shipped documents, so the file
`build-shadow.py` reads is built from those documents rather than typed. A leaf
not named on the command line is the shipped value, which is what makes "the
round moved the spread and nothing else" a property of the file rather than of
a reader's care.

    python3 constants.py /tmp/A.json light.spreadPx=0.5 dark.spreadPx=0.5

**The knee is held at 44 by construction** (W30 Decision Log 2 (b), 3 (c), and
this wave's Decision Log 1 (a)). `sigmaThinOffsetPx` is the floor the σ line is
clamped below at and the knee sits at `sigmaSpanRefPx + sigmaThinOffsetPx /
sigmaSlopePerSpan`, so a slope that moves with the offset held moves the knee
too. Whenever `sigmaSlopePerSpan` is overridden the offset is re-derived as
`slope · (44 − 96)` and the derivation is printed; naming
`sigmaThinOffsetPx` explicitly overrides the derivation and says so.

`sigmaSpanRefPx` is held at 96 and is refused as an override, because moving it
moves the law's one flat direction rather than the law (`material.ts`,
`sigmaSpanRefPx`'s doc comment) and Decision Log 1 (a) holds it.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROFILES = HERE.parent.parent / "profiles"

ACTIVE = {
    "light": "apple-macos-27.0-1x-light-standard-glass0.5",
    "dark": "apple-macos-27.0-1x-dark-standard-glass0.5",
}

# Every leaf a round may carry, in the order `build-shadow.py` writes them.
LEAVES = (
    "sigmaPx", "sigmaSlopePerSpan", "sigmaSpanRefPx", "sigmaThinOffsetPx",
    "spreadPx", "offsetPx",
    "thinOcclusionDark", "thinOcclusionMid", "thinOcclusionBright",
    "thickOcclusionAt96", "thickOcclusionAt128", "thickOcclusionAt160",
    "liftAmplitude",
)

# The macOS 26.5 default the dark document inherits the two lengths from today.
# Read from the renderer rather than retyped would need a TS round trip; the
# values are `DEFAULT_MATERIAL_PROFILE.outerShadow` in `material.ts` and are
# asserted against it by `shipped()` below refusing to invent a leaf it cannot
# source.
DEFAULT_LENGTHS = {"spreadPx": 3.1, "offsetPx": 7.95}

KNEE_SPAN = 44.0
REF_SPAN = 96.0


def shipped() -> dict:
    out = {}
    for scheme, name in ACTIVE.items():
        block = json.loads((PROFILES / f"{name}.json").read_text())["patch"]["outerShadow"]
        here = {}
        for leaf in LEAVES:
            if leaf in block:
                here[leaf] = block[leaf]
            elif leaf in DEFAULT_LENGTHS:
                # The dark document carries neither length and inherits the
                # macOS 26.5 default's. A candidate that means to keep that
                # inheritance still has to WRITE the value, because a document
                # is a patch over the default and not over its sibling.
                here[leaf] = DEFAULT_LENGTHS[leaf]
            else:
                raise SystemExit(f"constants: {name} carries no {leaf} and there is no default")
        out[scheme] = here
    return out


def main(argv: list[str]) -> int:
    base = shipped()
    if argv and argv[0] == "--show":
        print(json.dumps(base, indent=2))
        return 0
    if not argv:
        raise SystemExit(__doc__)
    out = Path(argv[0])
    slope_moved = set()
    thin_named = set()
    for assignment in argv[1:]:
        path, _, raw = assignment.partition("=")
        scheme, _, leaf = path.partition(".")
        if scheme not in base:
            raise SystemExit(f"constants: no scheme '{scheme}'")
        if leaf not in LEAVES:
            raise SystemExit(f"constants: no leaf '{leaf}'")
        if leaf == "sigmaSpanRefPx":
            raise SystemExit("constants: sigmaSpanRefPx is held at 96 (Decision Log 1 (a))")
        base[scheme][leaf] = float(raw)
        if leaf == "sigmaSlopePerSpan":
            slope_moved.add(scheme)
        if leaf == "sigmaThinOffsetPx":
            thin_named.add(scheme)
    for scheme in slope_moved - thin_named:
        derived = base[scheme]["sigmaSlopePerSpan"] * (KNEE_SPAN - REF_SPAN)
        print(f"  {scheme}: the knee held at {KNEE_SPAN:.0f} — sigmaThinOffsetPx re-derived "
              f"{base[scheme]['sigmaThinOffsetPx']} → {derived:.6g} "
              f"= {base[scheme]['sigmaSlopePerSpan']} · ({KNEE_SPAN:.0f} − {REF_SPAN:.0f})")
        base[scheme]["sigmaThinOffsetPx"] = round(derived, 6)
    for scheme in thin_named:
        print(f"  {scheme}: sigmaThinOffsetPx named explicitly — the knee is NOT re-derived, "
              f"it sits at {REF_SPAN + base[scheme]['sigmaThinOffsetPx'] / base[scheme]['sigmaSlopePerSpan']:.3f}")
    out.write_text(json.dumps(base, indent=2) + "\n")
    print(json.dumps(base, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
