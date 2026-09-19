#!/usr/bin/env python3
"""The 27 accessibility profiles' caveat: macOS 27 does not couple the two toggles.

W29 G1 Part B, claims §5.150. On macOS 26.5 turning on Increase Contrast
force-enabled Reduce Transparency and the transparency checkbox could not be
uncleared while contrast was on (user-verified 2026-08-29), so the coupled state
was the ONLY reachable increased-contrast state and the 26.5 profile carries a
caveat saying its fixtures were captured with both on. The harness records that
coupling itself, as a profile caveat, whenever it sees it
(`main.swift`'s `couplingNote`).

On macOS 27 it is gone. Every one of the seven increased-contrast runs attested
`increaseContrast=1` with `reduceTransparency=0`, the harness wrote no coupling
note in any of the 56 run manifests, and the reduced-transparency passes attested
the mirror image. So the 27 increased-contrast bed is a DIFFERENT state from the
26.5 one — contrast without transparency reduction — and a reader comparing the
two profiles cell by cell has to know that before attributing any difference to
the material.

The 26.5 caveat is not touched. It is a true statement about the bed it describes
and about the operating system that bed was captured on; this is added beside it,
which is the only honest shape for a fact that changed underneath two beds.

    add-a11y-caveat.py <manifest.json> [--apply]
"""
import json
import sys

CAVEATS = {
    "apple-macos-27.0-1x-light-increased-contrast-glass0.5": (
        "Captured with Increase Contrast ON and Reduce Transparency OFF. macOS 27 does not "
        "couple them: all seven runs attested increaseContrast=1 with reduceTransparency=0, "
        "and the harness wrote no coupling note (it records one whenever it observes the "
        "coupling). This is a DIFFERENT state from the 26.5 profile of the same name, whose "
        "own caveat records that on macOS 26.5 the coupled state was the only reachable "
        "increased-contrast state — that caveat is true of that bed and is unchanged. A "
        "difference between the two beds on this profile is therefore confounded with the "
        "decoupling and must not be attributed to the material without separating them "
        "(W29 Surprises; claims §5.150)."
    ),
    "apple-macos-27.0-1x-light-reduced-transparency-glass0.5": (
        "Captured with Reduce Transparency ON and Increase Contrast OFF, which is the same "
        "state the 26.5 profile of this name was captured in. Recorded here only because its "
        "sibling profile changed: macOS 27 no longer couples the two toggles, so on 27 this "
        "state and the increased-contrast state are independent where on 26.5 one implied "
        "the other (W29 Surprises; claims §5.150)."
    ),
}

path = sys.argv[1]
apply = "--apply" in sys.argv[2:]
m = json.load(open(path))

changed = []
for profile in m["profiles"]:
    text = CAVEATS.get(profile["profileKey"])
    if text is None:
        continue
    existing = profile.get("caveats") or []
    if text in existing:
        print("already present: %s" % profile["profileKey"])
        continue
    profile["caveats"] = [*existing, text]
    changed.append(profile["profileKey"])

for key in changed:
    print("caveat added: %s" % key)
if not apply:
    print("\nnothing written. Re-run with --apply.")
    raise SystemExit(0)
open(path, "w").write(json.dumps(m, indent=2) + "\n")
print("\nwritten to %s" % path)
