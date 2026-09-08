"""W24 G0 (c) — the ladder's candidate profile documents.

Each candidate is the SHIPPED document for its scheme with one key added:
`patch.optics.regular.rimLitExponent`. Nothing else moves, so every difference a ladder capture
shows is attributable to the exponent alone, and the axis stays at the renderer default — the exact
diagonal — which is what makes the factor 1 on every straight side and the straight-span check a
statement about the mechanism rather than about a fitted angle.

The documents are written to SCRATCH and never committed: they are this gate's measurement
apparatus, not a declaration.

Usage: make-candidates.py <scratch-dir> [exponent ...]
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WORKTREE = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))
PROFILES = os.path.join(WORKTREE, "packages", "calibration", "profiles")

SCHEMES = {
    "light": "apple-macos-26.5-1x-light-standard.json",
    "dark": "apple-macos-26.5-1x-dark-standard.json",
}


def main() -> int:
    out_dir = sys.argv[1]
    exponents = [float(a) for a in sys.argv[2:]] or [1.0, 2.0]
    os.makedirs(out_dir, exist_ok=True)
    for scheme, name in SCHEMES.items():
        doc = json.load(open(os.path.join(PROFILES, name)))
        for exponent in exponents:
            candidate = json.loads(json.dumps(doc))
            optics = candidate["patch"].setdefault("optics", {}).setdefault("regular", {})
            optics["rimLitExponent"] = exponent
            # The recorded digest is the SHIPPED material's and this document is not it. It is
            # dropped rather than recomputed, so that nothing here can be mistaken for a profile
            # anybody declared; the cell key carries this file's own hash in any case.
            candidate.pop("resolvedMaterialSha256", None)
            candidate["$comment-w24"] = (
                f"W24 G0 ladder candidate: the shipped {scheme} document with "
                f"optics.regular.rimLitExponent = {exponent}. Scratch, never declared."
            )
            tag = f"{scheme}-lit{exponent:g}".replace(".", "p")
            path = os.path.join(out_dir, f"{tag}.json")
            with open(path, "w") as fh:
                json.dump(candidate, fh, indent=2)
            print(f"-> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
