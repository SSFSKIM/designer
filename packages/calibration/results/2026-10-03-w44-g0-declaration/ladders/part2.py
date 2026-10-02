#!/usr/bin/env python3.12
"""W44 G0 (g): write part 2, the fit declaration, from the draft and the ladder results (clause 1).

    python3.12 -B part2.py        writes ../fit-declaration.json (refuses to overwrite)

Part 2 is the draft's body with a `changes` list, and this script derives that list mechanically
from `results.json`, one change per enumerated decision and nothing else:
  - every draft leaf whose ladder the results strike: `strike`, the ladder cited (family C as a
    whole: `strikeFamily`, when L3 is struck for its 1x setting);
  - L3 proving C's inert 1x setting: `inert`;
  - every draft grid with a point outside its ladder's non-flat range: `narrow` to the points
    inside it (a grid is never narrowed to nothing; a ladder with no non-flat range strikes).
`declare.py check-fit` then re-applies the same changes to the draft through the validator and
refuses part 2 unless the bodies agree; `declare.py hash-fit` hashes it.
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
sys.path.insert(0, str(EVIDENCE))
import declare as D  # noqa: E402

ROOT = D.ROOT
REL = D.REL


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    out = EVIDENCE / "fit-declaration.json"
    if out.exists():
        raise SystemExit("fit-declaration.json exists; a declaration is never rewritten (amend-fit)")
    draft = json.loads(D.DRAFT.read_text())
    protocol = json.loads(D.PROTOCOL.read_text())
    results = json.loads(D.RESULTS.read_text())
    ladders = results["ladders"]
    changes = []
    l3 = ladders["L3"]
    if l3["struck"] and l3.get("moved1x"):
        changes.append({"kind": "strikeFamily", "move": "move1", "family": "C", "ladder": "L3",
                        "why": "L3 moved a 1x capture: C's 1x inert setting is not proven (X48)"})
    elif l3.get("inert1x"):
        changes.append({"kind": "inert", "ladder": "L3",
                        "why": "every 1x capture of every L3 rung pixel-identical to c05-control's"})
    struck_c = any(c["kind"] == "strikeFamily" for c in changes)
    for mid, fam, leaf, spec in D.draft_leaves(draft):
        if struck_c and fam == "C":
            continue
        lid = D.ladder_of(protocol, spec["slot"], leaf)
        lad = ladders[lid]
        if lad["struck"]:
            changes.append({"kind": "strike", "move": mid, "family": fam, "leaf": leaf, "ladder": lid,
                            "why": lad["why"]})
            continue
        rng = (lad.get("nonFlatRange") or {}).get(leaf)
        if rng is None:
            continue
        inside = [x for x in spec["grid"] if rng[0] <= x <= rng[1]]
        if inside and inside != spec["grid"]:
            changes.append({"kind": "narrow", "move": mid, "family": fam, "leaf": leaf, "ladder": lid,
                            "grid": inside, "why": f"{lid}'s non-flat range is {rng}"})
    body = D.apply_changes(draft, changes, results, protocol)
    body.pop("status", None)
    fit = {"schema": draft["schema"],
           "status": "PART 2, the fit declaration: the draft changed only by `changes`, each one of the "
                     "protocol's enumerated decisions cited to its ladder (declare.py check-fit validates it)",
           "fromDraft": sha(D.DRAFT.read_bytes()),
           "changes": changes,
           "sources": {f"{REL}/{p}": sha((EVIDENCE / p).read_bytes())
                       for p in ("fit-declaration-draft.json", "ladders/protocol.json", "ladders/results.json")},
           **{k: v for k, v in body.items() if k != "schema"}}
    out.write_bytes(D.serialise(fit))
    print(json.dumps(changes, indent=1))
    print(f"wrote {out.name}: {len(changes)} change(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
