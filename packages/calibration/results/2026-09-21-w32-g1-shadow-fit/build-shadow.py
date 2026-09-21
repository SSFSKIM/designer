#!/usr/bin/env python3
"""W32 G1 — merge a fitted shadow triple into the four macOS 27 documents.

    python3 build-shadow.py <constants.json> <out-dir>      # a fit candidate
    python3 build-shadow.py <constants.json> --in-place     # the seal

`results/2026-09-20-w30-g3-operators/build-shadow.py` copied and changed in
exactly three places, each of which this wave's rulings force. Everything else —
the leaf-by-leaf copy, the pass-through of every other key, the rule that a
receded document never carries the σ law because `withMaterialOverrides` merges
`outerShadow` leaf by leaf, and the rule that the two frozen macOS 26.5
documents are never opened (X1) — is W30 G3's, byte for byte in behaviour.

**Change 1 — the two LENGTHS are writable.** W30's copy wrote the σ law and the
seven amplitudes; `spreadPx` and `offsetPx` were inherited from the macOS 26.5
default in every document that carries them and had never been fitted on the
macOS 27 bed (claims §5.162 §2). They are this wave's subject, so `LENGTHS` is
written into the two ACTIVE documents.

  The dark active document carries NEITHER leaf today, so "the dark document
  inherits the light one's value" cannot be expressed by leaving the leaf out:
  an absent leaf inherits `DEFAULT_MATERIAL_PROFILE`'s 3.10 / 7.95, not the
  light document's fitted value. A document is a patch over the DEFAULT and not
  over its sibling. So when the fit says the dark bed wants what the light bed
  wants, the value is WRITTEN into the dark document and the inheritance is
  recorded in the ledger as a reading — which is the only form of it that draws
  what it says.

**Change 2 — the receded documents' AMPLITUDE stands down to zero**
(W32 Decision Log 2, RULED). Apple's receded window removes no light from 3 CSS
px outward on 121 of 121 non-holdout inactive cells, 153 of 153 with the
holdout, and 235 of 235 on the frozen macOS 26.5 bed (claims §5.166 §7 and its
review closure). So the receded documents' six occlusion anchors, `liftAmplitude`
and their own `reducedTransparencyOcclusion` are written as **0** — a declared
reading, the way `sigmaThinOffsetPx` was declared at W30 Decision Log 2 (b) —
rather than inherited from the active document leaf for leaf, which is what W30's
copy did and what made vitrea draw the ACTIVE shadow in the inactive pose.

  `reducedTransparencyOcclusion` is the one leaf W30's copy deliberately did not
  write, because it is outside that child's contract. It is inside this one's:
  Decision Log 2 names it, and it is the amplitude the reduced-transparency fold
  writes into all six anchors — so a recede that stands down and leaves it at
  0.087 would draw the full receded shadow on exactly the bed where the recede
  is hardest to see. It is written on the RECEDED documents only; the active
  documents' fold amplitude does not move (X3).

**Change 3 — the σ law's leaves are bounded by B1 here rather than by a
convention elsewhere.** `--in-place` refuses to write a σ law outside the joint
windows `bounds-declaration.md` §4 prints, so the seal cannot land a material the
adopted bound would refuse. A candidate build prints the position and does not
refuse, because a round that breaks a stop is a round this wave records.

The scatter's five leaves are pass-through: W30 wrote them and X3 forbids this
wave to move them, so they are neither read nor written here and stay whatever
the document on disk says.
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

# The σ law's three leaves plus the width they pivot about. Active documents only.
SIGMA = ("sigmaPx", "sigmaSlopePerSpan", "sigmaSpanRefPx", "sigmaThinOffsetPx")

# W32's two: the outset and the displacement. Active documents only, for the
# same reason the σ law is — a receded document that named one would be stating
# a difference this wave has no inactive reading to support (Decision Log 2
# leaves the receded LENGTHS unread, because nothing draws at zero amplitude).
LENGTHS = ("spreadPx", "offsetPx")

# The amplitude leaves a receded document carries in its own `outerShadow`
# block. W30's copy inherited each from its scheme's active document; W32
# Decision Log 2 sets every one of them to zero.
RECEDED_ZERO = (
    "thinOcclusionDark", "thinOcclusionMid", "thinOcclusionBright",
    "thickOcclusionAt96", "thickOcclusionAt128", "thickOcclusionAt160",
    "liftAmplitude", "reducedTransparencyOcclusion",
)

# The seven amplitude leaves the ACTIVE documents carry and this wave re-solves.
ACTIVE_AMPLITUDE = (
    "thinOcclusionDark", "thinOcclusionMid", "thinOcclusionBright",
    "thickOcclusionAt96", "thickOcclusionAt128", "thickOcclusionAt160",
    "liftAmplitude",
)

# B1's joint windows at the shipped bytes, `bounds-declaration.md` §4 —
# `shadow-law.py --at-shipped`'s output, transcribed with its source named so a
# reader can re-derive rather than trust. The σ law's closed form must land
# inside all three on the document's own scheme.
B1_WINDOWS = {
    "light": {96: (8.8966, 9.0193), 128: (12.6397, 13.7947), 160: (16.7033, 17.8198)},
    "dark": {96: (8.9084, 9.3180), 128: (12.7458, 13.8499), 160: (16.7931, 18.3237)},
}


def law_sigma(block: dict, span: float) -> float:
    """`outerShadowSigmaPx`'s closed form, in the units the document states it in."""
    return block["sigmaPx"] + max(
        block["sigmaThinOffsetPx"],
        block["sigmaSlopePerSpan"] * (span - block["sigmaSpanRefPx"]),
    )


def b1_position(scheme: str, block: dict) -> list[tuple[int, float, tuple[float, float], bool]]:
    out = []
    for span, window in B1_WINDOWS[scheme].items():
        sigma = law_sigma(block, span)
        out.append((span, sigma, window, window[0] <= sigma <= window[1]))
    return out


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        raise SystemExit(__doc__)
    constants = json.loads(Path(argv[0]).read_text())
    in_place = argv[1] == "--in-place"
    out = PROFILES if in_place else Path(argv[1])
    out.mkdir(parents=True, exist_ok=True)

    # Built first, written second: `--in-place` refuses a σ law outside B1 and a
    # refusal that fired after the first document was written would leave the
    # four on disk half sealed.
    refusals: list[str] = []
    planned: list[tuple[Path, dict]] = []
    for scheme, name in ACTIVE.items():
        block = constants[scheme]
        document = json.loads((PROFILES / f"{name}.json").read_text())
        shadow = dict(document["patch"]["outerShadow"])
        for leaf in SIGMA + LENGTHS + ACTIVE_AMPLITUDE:
            if leaf in block:
                shadow[leaf] = block[leaf]
        document["patch"]["outerShadow"] = shadow
        planned.append((out / f"{name}.json", document))
        print(f"{'sealed ' if in_place else 'candidate '}{name}")
        for leaf in SIGMA + LENGTHS + ACTIVE_AMPLITUDE:
            print(f"    {leaf:<28}{shadow[leaf]}")
        print("    B1 at this σ law:")
        for span, sigma, window, inside in b1_position(scheme, shadow):
            print(f"      span {span:>3}  σ {sigma:>9.4f}  window [{window[0]:.4f}, {window[1]:.4f}]"
                  f"  {'INSIDE' if inside else 'OUTSIDE'}")
            if not inside:
                refusals.append(f"{name}: σ({span}) = {sigma:.4f} outside [{window[0]}, {window[1]}]")

        receded_name = f"{name}-receded"
        receded = json.loads((PROFILES / f"{receded_name}.json").read_text())
        receded_shadow = dict(receded["patch"]["outerShadow"])
        for leaf in RECEDED_ZERO:
            if leaf in receded_shadow:
                receded_shadow[leaf] = 0
        receded["patch"]["outerShadow"] = receded_shadow
        planned.append((out / f"{receded_name}.json", receded))
        print(f"{'sealed ' if in_place else 'candidate '}{receded_name}"
              f"  (the σ law and the two lengths inherited from {name}, not copied;"
              f" every amplitude 0 — W32 Decision Log 2)")
        for leaf in RECEDED_ZERO:
            if leaf in receded_shadow:
                print(f"    {leaf:<28}{receded_shadow[leaf]}")

    if refusals and in_place:
        for line in refusals:
            print(f"REFUSED  {line}")
        print("\nB1 is adopted and this wave does not fit it off (Decision Log 1 (a)). "
              "Nothing was sealed.")
        return 1
    for path, document in planned:
        path.write_text(json.dumps(document, indent=2) + "\n")
    if refusals:
        print("\n  (candidate build: the σ law is outside B1 on the line(s) above. A round that "
              "breaks a stop is recorded and not shipped.)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
