#!/usr/bin/env python3
"""W29 G3b — merge this child's outer-shadow constants into the two 27 active documents.

    python3 build-shadow.py

G3's `build-documents.py` rebuilds a 27 document from its 26.5 base plus that
child's whole fitted set. This does the other thing, and deliberately: it PATCHES
the committed 27 documents in place with the one block Decision Log 6 (a) rules,
so that the proof "no other constant moved" is a property of the script and not
of a diff nobody ran. Re-running G3's builder instead would mean holding a second
copy of its eighty fitted keys here, which is how a copy goes stale.

Everything else about each document — every other patch key, its `$comment`, its
`measurement` and G3's six `entries` — is read from disk and written back
untouched. `seal.ts` then re-resolves `resolvedMaterialSha256`; nothing here
computes a digest.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROFILES = HERE.parent.parent / "profiles"

spec = json.loads((HERE / "fitted-shadow.json").read_text())

NOTE = [
    "",
    "W29 G3b (claims §5.154; Decision Log 6 (a)) refits the `outerShadow` block and",
    "nothing else. The shadow is the one law G2 never read and G3 was therefore",
    "forbidden to follow (§5.153 §5); it is read native-against-native in",
    "`results/2026-09-19-w29-g3b-shadow-recede/` and the constants are fitted on the",
    "departure the shadow axis measures. Every other key below is G3's, unchanged.",
]

for entry in spec["documents"]:
    path = PROFILES / f"{entry['profileKey']}.json"
    document = json.loads(path.read_text())

    before = dict(document["patch"]["outerShadow"])
    document["patch"]["outerShadow"] = {**before, **entry["outerShadow"]}
    moved = {
        key: (before.get(key, "(inherited from the default)"), value)
        for key, value in entry["outerShadow"].items()
        if before.get(key) != value
    }

    document["$comment"] = [*document["$comment"], *NOTE]
    document["entries"] = {**document["entries"], **entry["entry"]}
    document["entries"]["outerShadow"]["value"] = entry["outerShadow"]
    document["entries"]["outerShadow"]["previous"] = {k: v[0] for k, v in moved.items()}
    document["measurement"] = {
        **document["measurement"],
        "outerShadow": {
            "gate": "W29 G3b, claims §5.154",
            "bar": "results/2026-09-19-w29-g3b-shadow-recede/noise-bar.json, declared before the first 26.5 pair",
            "objective": spec["objective"]["metric"],
            "objectiveBefore": spec["objective"]["beforeLight"],
            "objectiveAfter": spec["objective"]["afterLight"],
            "reproduce": spec["objective"]["reproduce"],
        },
    }

    path.write_text(json.dumps(document, indent=2) + "\n")
    print(f"patched {entry['profileKey']}.json — {len(moved)} leaf/leaves moved")
    for key, (was, now) in sorted(moved.items()):
        print(f"    outerShadow.{key:<34} {json.dumps(was):>12}  ->  {json.dumps(now)}")
