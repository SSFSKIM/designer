"""Every pre-existing matrix cell, compared with itself across the landing (X11).

`merge-matrix.ts` refuses to write unless no existing cell moved, so this is the same
statement read a second way and from outside the merge: the committed matrix at a named
commit, against the file on disk, cell by cell, keyed on the cell's own key object. It
exists because the line-level diff of `results/matrix.json` is unreadable — 470 cells of
pretty-printed JSON interleaved into 637 make git rewrite most of the file's lines
without a single number changing — and "the active rows are byte-identical at the
landing" must be a reading rather than an impression of a diff.

    git show <ref>:packages/calibration/results/matrix.json > /tmp/old.json
    python3 matrix-identity.py /tmp/old.json <ref>
"""
import collections
import json
import pathlib
import sys

before = json.loads(pathlib.Path(sys.argv[1]).read_text())
ref = sys.argv[2]
here = pathlib.Path(__file__).resolve().parent
after = json.loads((here / "../matrix.json").resolve().read_text())


def key(cell):
    return json.dumps(cell["key"], sort_keys=True)


def body(cell):
    return json.dumps(cell, sort_keys=True)


old = {key(c): c for c in before["cells"]}
new = {key(c): c for c in after["cells"]}
missing = sorted(k for k in old if k not in new)
changed = sorted(k for k in old if k in new and body(old[k]) != body(new[k]))
added = [new[k] for k in new if k not in old]

report = {
    "gate": "W28 G4 — the canonical matrix at the landing",
    "claims": "§5.148",
    "contract": "X11 — the active material does not move",
    "before": {"ref": ref, "schemaVersion": before["schemaVersion"], "cells": len(old)},
    "after": {"schemaVersion": after["schemaVersion"], "cells": len(new)},
    "existingCellsMissing": missing,
    "existingCellsChanged": changed,
    "cellsAdded": len(added),
    "addedByProfileAndTier": {
        f"{p} / {t}": n
        for (p, t), n in sorted(
            collections.Counter((c["key"]["profileKey"], c["tier"]) for c in added).items()
        )
    },
    "addedByFixtureSet": dict(sorted(collections.Counter(c["fixtureSet"] for c in added).items())),
    "addedByState": dict(sorted(collections.Counter(c.get("state") for c in added).items())),
    "addedCellsCarryingCoherence": sum(1 for c in added if "coherence" in c),
    "statesPresentAfter": dict(
        sorted(collections.Counter(c.get("state", "(unlabelled)") for c in new.values()).items())
    ),
}
out = here / "matrix-identity.json"
if out.exists():
    raise SystemExit(f"{out} exists; refusing to overwrite evidence")
out.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: v for k, v in report.items() if k != "addedByProfileAndTier"}, indent=2))
if missing or changed:
    raise SystemExit(1)
