#!/usr/bin/env python3
"""The scene specification one pass of the 27 bed runs against, and its cell list.

    pass-spec.py spec <canonical-scenes.json> <out.json> [decoupled|coupled]
    pass-spec.py ids  <spec.json> <active|inactive> <a11y-mode> <1|2>

**Why a derived specification exists at all.** `scenes.json` declares both beds —
the six frozen `apple-macos-26.5-…` profiles and W29's `apple-macos-27.0-…-glass0.5`
ones — because the charter's clause 2 puts the 27
keys "beside the six 26.5 keys" and because the two beds must be read from one
declaration to be comparable. The harness, though, selects profiles by
accessibility mode and display scale and by **nothing else**: it has no profile
filter, and `--scenes` narrows cells rather than profiles (`main.swift`'s a11y
gate and scale gate; `CaptureOptions.onlyScenes`). So a 2x standard pass against
the canonical file would select four profiles, not two, and would spend the
sitting capturing 27 pixels a second time into `apple-macos-26.5-…` directories
inside the run snapshot — twice the machine hours the pass plan is priced at, and
a run snapshot that invites exactly the mistake contract X1 forbids.

Narrowing the profile list in the file the pass reads is the fix that needs no
rebuild of the granted bundle (X4). It is **derived, never kept**: this script
writes it from the canonical declaration at the opening of every pass, and
refuses unless what it finds there is the six expected keys, each at the ruled
slider position, each declaring its 26.5 counterpart's scenes exactly. Everything
else in the document — the canvas, the backgrounds, the components, the tints,
the 168 scenes, the split and `version` — passes through untouched, so the
manifest a pass writes records the canonical file's own `sceneSpecVersion` and
split, which is true of it.

**Why one of the two increased-contrast profiles is left out of every pass.**
macOS 27 decoupled Reduce transparency from Increase Contrast, so the bed holds
two contrast profiles: `…-increased-contrast-glass0.5`, captured with contrast
alone, and `…-increased-contrast-coupled-glass0.5`, captured with both toggles
on — the state macOS 26.5 forced, and the only one comparable with the 26.5 bed
like for like (W29 Decision Log 4 (b); claims §5.151 §9, §5.152). The harness
cannot tell them apart: it selects on the profile's declared `a11y` field, both
declare `increased-contrast` because that is what `SystemAccessibility.current`
returns in either state, and teaching it the difference would be a rebuild (X4).
So the derived specification carries exactly ONE of them, named by the pass —
`decoupled` by default, which is what the six passes of the first sitting ran
against and what they still derive today. Structural rather than advisory: the
list is built by filling one contrast slot, so there is no arrangement of
arguments under which both reach the bundle.

**Why the cell list is derived too.** A pass presents one pose for its whole
length and the harness refuses the run outright if any cell the selected
profiles declare states the other pose, so `--scenes` is not an optimisation
here, it is required. The list is computed from the same document the pass reads,
per pose and per accessibility mode, rather than committed as a text file: the
W27 sitting needed a hand-derived `bed-inactive-a11y.txt` because the two
accessibility profiles declare a subset, and a list that is derived cannot
disagree with the declaration it was derived from.
"""
import hashlib
import json
import sys

OS_27_PREFIX = "apple-macos-27.0-"
GLASS_TOKEN = "-glass0.5"

# The six keys W29 acceptance clause 2 declares, plus Decision Log 4 (b)'s
# coupled contrast profile. Spelled out rather than pattern-matched: the whole
# purpose of the refusal below is that a pass cannot run against a declaration
# somebody widened, narrowed or re-slidered without this file moving with it.
EXPECTED = [
    "apple-macos-27.0-1x-dark-standard-glass0.5",
    "apple-macos-27.0-1x-light-increased-contrast-coupled-glass0.5",
    "apple-macos-27.0-1x-light-increased-contrast-glass0.5",
    "apple-macos-27.0-1x-light-reduced-transparency-glass0.5",
    "apple-macos-27.0-1x-light-standard-glass0.5",
    "apple-macos-27.0-2x-dark-standard-glass0.5",
    "apple-macos-27.0-2x-light-standard-glass0.5",
]

# The two contrast profiles, and which of them each variant puts in the pass.
CONTRAST = {
    "decoupled": "apple-macos-27.0-1x-light-increased-contrast-glass0.5",
    "coupled": "apple-macos-27.0-1x-light-increased-contrast-coupled-glass0.5",
}

# The 26.5 profile each 27 profile is the counterpart of. Derived by dropping the
# OS token and the slider — an axis 26.5 could not carry — except for the coupled
# key, which drops `-coupled` as well for the same reason: 26.5 could not carry
# that axis either, because contrast force-enabled transparency reduction there,
# so the 26.5 profile of the plain name IS the coupled state.
def counterpart_of(key):
    source = key[: -len(GLASS_TOKEN)].replace(OS_27_PREFIX, "apple-macos-26.5-")
    return source.replace("-increased-contrast-coupled", "-increased-contrast")

# Which `state` values a fresh run can put on screen, per pose. The same two sets
# `SceneSpecFile.freshlyCapturableStates` returns; mirrored rather than imported
# because this is a shell-side pre-flight and the harness is the authority that
# enforces it. The mirror is checked every pass: a list this file derives that the
# harness then refuses is a disagreement the pass reports before it captures.
REACHABLE = {"active": {"rest", "pressed"}, "inactive": {"inactive"}}


def die(message: str) -> None:
    sys.stderr.write("pass-spec: " + message + "\n")
    raise SystemExit(2)


def derive(canonical_path: str, out_path: str, variant: str) -> None:
    if variant not in CONTRAST:
        die("the contrast variant must be one of " + ", ".join(sorted(CONTRAST))
            + ", not '" + variant + "'")
    raw = open(canonical_path, "rb").read()
    doc = json.loads(raw)
    profiles = doc.get("profiles") or []
    keys27 = sorted(p["key"] for p in profiles if p["key"].startswith(OS_27_PREFIX))
    if keys27 != EXPECTED:
        die("the canonical declaration's 27 profiles are\n  "
            + "\n  ".join(keys27 or ["(none)"])
            + "\nand this pass expects\n  " + "\n  ".join(EXPECTED)
            + "\nA pass does not run against a bed whose declaration moved under it.")
    by_key = {p["key"]: p for p in profiles}
    for key in EXPECTED:
        if not key.endswith(GLASS_TOKEN):
            die(key + " does not state the ruled slider position " + GLASS_TOKEN
                + ". Decision Log 3 (a) captures this bed at NSGlassTintAmount 0.5 and X6"
                " puts the position in the key.")
        source = counterpart_of(key)
        counterpart = by_key.get(source)
        if counterpart is None:
            die(key + " has no 26.5 counterpart " + source
                + ". Clause 2 captures the 27 bed over the 26.5 bed's scenes, so every 27"
                " profile must have one.")
        if counterpart["scenes"] != by_key[key]["scenes"]:
            die(key + " declares scenes its counterpart " + source + " does not."
                " G2 reads 27 against 26.5 cell by cell; a drifted list turns a"
                " declaration bug into a missing cell.")
    # One contrast slot, filled by the pass's variant. Built this way rather than
    # by removing the other key so that a third contrast state added to EXPECTED
    # without a decision here fails loudly at CONTRAST rather than silently
    # joining every pass.
    selected = sorted([key for key in EXPECTED if key not in CONTRAST.values()]
                      + [CONTRAST[variant]])
    doc["profiles"] = [by_key[key] for key in selected]
    text = json.dumps(doc, indent=2, ensure_ascii=False) + "\n"
    open(out_path, "w").write(text)
    print("canonicalSha256=" + hashlib.sha256(raw).hexdigest())
    print("passSpecSha256=" + hashlib.sha256(text.encode()).hexdigest())
    print("contrastVariant=" + variant)
    print("profiles=" + ",".join(selected))


def ids(spec_path: str, pose: str, a11y: str, scale: str) -> None:
    if pose not in REACHABLE:
        die("pose must be active or inactive, not '" + pose + "'")
    doc = json.loads(open(spec_path, "rb").read())
    state = {s["id"]: s["state"] for s in doc["scenes"]}
    labelled = {s["id"] for s in doc["scenes"] if s.get("label") is not None}
    # Selected by BOTH axes the harness selects by, because the list should be the
    # cells this pass will actually present. Two profiles at one scale can declare
    # the same ids as the pair at the other and the list would look right anyway —
    # which is how a pass that no profile can serve, like accessibility at 2x
    # (W29 Deferred), reaches the harness and fails there instead of here.
    selected = [p for p in doc["profiles"]
                if p["a11y"] == a11y and ("-%sx-" % scale) in p["key"]]
    if not selected:
        die("no profile in " + spec_path + " is both a11y mode '" + a11y + "' and " + scale
            + "x. The two accessibility profiles are 1x light only, as on 26.5; dark and 2x"
            " accessibility are W29 Deferred.")
    declared = set()
    for p in selected:
        if p["scenes"] == "all":
            declared.update(state)
        else:
            declared.update(p["scenes"])
    wanted = sorted(i for i in declared
                    if state.get(i) in REACHABLE[pose] and i not in labelled)
    if not wanted:
        die("no cell of a11y mode '" + a11y + "' is reachable in the " + pose + " pose."
            " A pass that presents nothing is not a pass.")
    print(",".join(wanted))


def main() -> None:
    if len(sys.argv) >= 2 and sys.argv[1] == "spec" and len(sys.argv) in (4, 5):
        derive(sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) == 5 else "decoupled")
    elif len(sys.argv) >= 2 and sys.argv[1] == "ids" and len(sys.argv) == 6:
        ids(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    else:
        die(__doc__ or "")


main()
