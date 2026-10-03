#!/usr/bin/env python3.12
"""W45 G0 (e): write part 2, the fit declaration, from the draft and the ladder results (clause 2).
W44 G0's `ladders/part2.py`, ported for W45's protocol.

    python3.12 -B part2.py        writes ../fit-declaration.json (refuses to overwrite)

Part 2 is the draft's body with a `changes` list, derived from `results.json`, one change per
decision the protocol lets the cited ladder make and nothing else:
  - ladder (ii) with no rung meeting its bar is the STOP: the wave closes at G0 and no part 2 is
    written;
  - every draft leaf whose ladder the results strike: `strike`, the ladder cited;
  - X48 holding on every render: `inert`, the 1x second width's PENDING setting replaced by the
    citation (the value stays 0).
No grid is narrowed here. The ladders render a leaf only inside part of its draft grid (the span top
at 112-192 where the draft also holds c05's 256, the starting point's own value), and a narrowing
must stay inside the ladder's non-flat range, so narrowing would remove values the ladder never
read. `declare.py check-fit` re-applies the same changes through the validator and refuses part 2
unless the bodies agree; `declare.py hash-fit` hashes it.
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
sys.path.insert(0, str(EVIDENCE))
import declare as D  # noqa: E402

REL = D.REL
G1_TOOLS = ("fit/bindings.py", "fit/fit.py", "fit/search.py", "fit/joint.py", "fit/finding.py",
            "fit/recover.py", "fit/test_fit.py", "fit/build-candidate.ts", "fit/test_build_candidate.py",
            "stage/stage.py", "stage/x48.py", "stage/test_stage.py", "seal/seal.ts", "seal/test_seal.py",
            "sheets/sheets.py", "sheets/test_sheets.py", "cuts/cuts.py", "cuts/bed.py", "cuts/rule.py")


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
    if ladders["ii"]["stop"]:
        raise SystemExit("ladder (ii) met its bar on no rung: the wave closes at G0 and part 2 is not written")
    changes = []
    for mid, fam, key, spec in D.draft_leaves(draft):
        lid = spec.get("ladder")
        if lid is None or "strike" not in next(x for x in protocol["ladders"] if x["id"] == lid)["decides"]:
            continue
        if key in (ladders[lid].get("struck") or []):
            changes.append({"kind": "strike", "move": mid, "family": fam, "leaf": key, "ladder": lid,
                            "why": f"ladder ({lid}) read it flat on its cells"})
    if ladders["x48"]["inert1x"]:
        changes.append({"kind": "inert", "ladder": "x48",
                        "why": "every render's 1x captures pixel-identical to c05-control's (X48)"})
    body = D.apply_changes(draft, changes, results, protocol)
    body.pop("status", None)
    paths = ("fit-declaration-draft.json", "ladders/protocol.json", "ladders/results.json", *G1_TOOLS)
    fit = {"schema": draft["schema"],
           "status": ("PART 2, the fit declaration: the draft changed only by `changes`, each a decision the "
                      "protocol lets its ladder make, cited (declare.py check-fit validates it)"),
           "fromDraft": {"partOneSha256": D.digest_lines("protocol")[0], "draftSha256": sha(D.DRAFT.read_bytes())},
           "changes": changes,
           "sources": {f"{REL}/{p}": sha((EVIDENCE / p).read_bytes()) for p in paths},
           **{k: v for k, v in body.items() if k != "schema"}}
    out.write_bytes(D.serialise(fit))
    print(json.dumps(changes, indent=1))
    print(f"wrote {out.name}: {len(changes)} change(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
