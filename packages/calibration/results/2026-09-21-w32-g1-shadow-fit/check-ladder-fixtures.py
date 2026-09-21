#!/usr/bin/env python3
"""W32 G1 — the widened ladder's fixtures, checked per profile directory.

    python3 check-ladder-fixtures.py

Decision Log 1 (b) widens the read set to ten probe inactive scenes whose native
captures are already on disk. The brief's condition on that widening is that
**a missing fixture is a red, not a short population**: a scene a profile
DECLARES and has no fixture for would make `compare` plan a cell it cannot
measure, and a scene a profile does not declare is simply not its bed.

So the check is per profile directory and against the declaration, not against
the ten names: for every macOS 27 profile, every scene in the widened ladder
that the profile declares must have a native fixture beside it. The two
accessibility profiles declare three of the ten and the four standard profiles
declare all ten; both are printed, so a short population is visible as a
declaration rather than discovered as an absence.

Exit 1 on any declared scene with no fixture. No capture, nothing written.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent.parent
ROOT = PACKAGE.parent.parent
SCENES = ROOT / "apps/reference-apple/scenes.json"
FIXTURES = ROOT / "apps/reference-apple/fixtures"

GENERATION = "apple-macos-27.0-"


def ladder() -> tuple[list[str], list[str]]:
    """The two halves of `ladder.sh`, read out of that file rather than retyped."""
    text = (HERE / "ladder.sh").read_text()
    out = []
    for name in ("LADDER_45", "LADDER_W32"):
        line = next(l for l in text.splitlines() if l.startswith(f"{name}="))
        out.append(line.split("=", 1)[1].strip().strip('"').split(","))
    return out[0], out[1]


def main() -> int:
    spec = json.loads(SCENES.read_text())
    forty_five, widened = ladder()
    full = forty_five + widened

    print("W32 G1 — the widened ladder's fixtures, per profile directory")
    print("=" * 100)
    print(f"  the ladder is {len(forty_five)} + {len(widened)} = {len(full)} scenes "
          f"(`ladder.sh`, Decision Log 1 (b))")
    print()

    bad = 0
    for profile in spec["profiles"]:
        key = profile["key"]
        if not key.startswith(GENERATION):
            continue
        declared = set(profile["scenes"])
        directory = FIXTURES / key
        here_45 = [s for s in forty_five if s in declared]
        here_w32 = [s for s in widened if s in declared]
        missing = [s for s in here_45 + here_w32
                   if not any(directory.glob(f"{s}.*")) and not (directory / s).is_dir()]
        bad += len(missing)
        print(f"  {key}")
        print(f"      declares {len(here_45):>2} of the 45 and {len(here_w32):>2} of the ten; "
              f"{len(missing)} declared with no fixture")
        for name in missing:
            print(f"      MISSING  {name}")
        for name in widened:
            mark = "declared" if name in declared else "not this profile's bed"
            print(f"        {name:<40}{mark}")
    print()
    print("  a declared scene with no fixture is a red; a scene the profile does not declare")
    print("  is not its bed and is not a short population.")
    print(f"  verdict: {'RED — ' + str(bad) + ' declared scene(s) with no fixture' if bad else 'GREEN — every declared scene has its fixture'}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
