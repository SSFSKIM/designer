#!/usr/bin/env python3
"""The coupled profile's caveat, and the pointer on its decoupled sibling.

W29 G1c Part B, Decision Log 4 (b), claims §5.152. The sibling of G1 Part B's
`add-a11y-caveat.py`, and it adds rather than edits for the same reason: a caveat
already on a profile is a statement somebody made about the bed in front of them,
and the honest shape for a fact that changed underneath it is a second sentence
beside the first.

There are two of those here.

The harness writes its own coupling note on any `increased-contrast` profile it
observes with reduce-transparency on (`main.swift`'s `couplingNote`), and it is
on all seven of this profile's runs — which is exactly the attestation this bed
needed. Its WORDING, though, is a statement about macOS 26.5: it says macOS
couples the toggles and that the coupled state is the only reachable one. That
was true when it was written and is false on 27, where this state took two
deliberate hands. The note stays as the capture recorded it; the caveat below
says what the state actually is and why the profile exists.

The decoupled profile of nearly the same name gets a pointer, also added rather
than edited. Its own caveat already says it is contrast alone and that a
difference between it and the 26.5 bed is confounded; what it could not say in
G1 is where the unconfounded reading lives.

    add-coupled-caveat.py <manifest.json> [--apply]
"""
import json
import sys

COUPLED = "apple-macos-27.0-1x-light-increased-contrast-coupled-glass0.5"
DECOUPLED = "apple-macos-27.0-1x-light-increased-contrast-glass0.5"

CAVEATS = {
    COUPLED: (
        "Captured with Increase Contrast ON and Reduce Transparency ON, and both are attested "
        "per run: all seven runs of both passes read increaseContrast=1 with "
        "reduceTransparency=1, ButtonShapesEnabled=0 and NSGlassTintAmount 0.5 (see this "
        "profile's `attestation` block). That state is why this profile exists. macOS 26.5 "
        "force-coupled the two toggles — contrast enabled transparency reduction and the "
        "transparency checkbox could not be uncleared while contrast was on — so the coupled "
        "state was the ONLY increased-contrast state a machine could be in, and "
        "apple-macos-26.5-1x-light-increased-contrast is it. macOS 27 made them independent, so "
        "the profile named apple-macos-27.0-1x-light-increased-contrast-glass0.5 is contrast "
        "ALONE and cannot be read against the 26.5 bed like for like; this profile can, and it "
        "is the only 27 profile that can (W29 Decision Log 4 (b); claims §5.151 §9, §5.152). "
        "NOTE on the harness's own coupling note beside this one: it is the attestation the "
        "capture wrote and it is kept verbatim, but its wording is a statement about macOS 26.5 "
        "— on 27 nothing couples the toggles and this state was reached by hand."
    ),
    DECOUPLED: (
        "Where the unconfounded reading lives: the same 32 cells captured with BOTH toggles on, "
        "the state the 26.5 profile of this name was captured in, are published under "
        "apple-macos-27.0-1x-light-increased-contrast-coupled-glass0.5 (W29 Decision Log 4 (b); "
        "claims §5.152). This profile is unchanged and its caveat above still holds of it."
    ),
}


def main() -> None:
    path = sys.argv[1]
    apply = "--apply" in sys.argv[2:]
    manifest = json.load(open(path, encoding="utf-8"))

    changed = []
    for profile in manifest["profiles"]:
        text = CAVEATS.get(profile["profileKey"])
        if text is None:
            continue
        existing = profile.get("caveats") or []
        if text in existing:
            print("already present: " + profile["profileKey"])
            continue
        # Appended, never inserted first: the order of a profile's caveats is the
        # order they became true of it, and the harness's own note came first.
        profile["caveats"] = [*existing, text]
        changed.append(profile["profileKey"])

    for key in changed:
        print("caveat added: " + key)
    if not changed:
        print("nothing to add")
        return
    if not apply:
        print("\nnothing written. Re-run with --apply.")
        return
    # Written with the manifest's own formatting, which `materialize` wrote and
    # `freeze.py` hashes per unit rather than whole-file.
    with open(path, "w", encoding="utf-8") as out:
        json.dump(manifest, out, indent=2, ensure_ascii=False)
        out.write("\n")
    print("\nwritten: " + path)


main()
