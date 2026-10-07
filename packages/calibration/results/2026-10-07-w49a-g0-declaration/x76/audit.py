#!/usr/bin/env python3.12
"""W49a G0, X76: the audit of every receded document's inherited leaves (W49 charter Decision Log 3).

X76: a receded leaf inherited from the active is fitted or explicitly held in the document's method record,
never silently materialised. A receded document is a difference over its own scheme's active document, so
every leaf it does not name is the active's. That inheritance is how the defect X75 found shipped: W48's seal
wrote the receded dark 0.25 document's `tintAlphaFar1x` / `tintAlphaFar2x` as `materialised` at the active's
0.2 (no method, no reading), and at the receded `tintAlpha` 0.8 that value takes alphaBase to 1.0 at span 160.

For every receded profile document under `profiles/`, each leaf that matters to X76 is put in one class:

  measured      named in the receded patch with an `entries` record of status `measured` (it has a method);
  held          named or recorded under the document's `entries.held` families (an explicit hold);
  materialised  named in the receded patch at the value its active resolves it to, with an `entries` record of
                status `materialised` (no method): silent by X76;
  inherited     FITTED on the active (the active's patch names it with an `entries` record of status `measured`)
                and NOT named by the receded document: the receded draws the active's fit with no record of
                its own: silent by X76 unless a `held` family names it;
  unrecorded    named in the receded patch with no `entries` record at all (the pre-W43 document form, whose
                record lives in prose: `measurement`, the `$comment`s); reported, not classed silent here.

The macOS 26.5 receded material has no document (`receded-profile.ts`, W27c / W28 G1) and is frozen evidence;
it is listed as outside the document form. Reads committed files only.

    python3.12 -B audit.py > audit.txt              (also writes audit.json beside this file)
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROFILES = HERE.parents[2] / "profiles"


def leaves(node, prefix=""):
    if not isinstance(node, dict):
        return {prefix: node}
    out = {}
    for k, v in node.items():
        out.update(leaves(v, f"{prefix}.{k}" if prefix else k))
    return out


def status(entries: dict, leaf: str):
    e = entries.get(leaf)
    if e is None:
        # A nested leaf may be recorded under its family (`outerShadow`, `backdropToneResponse`, ...).
        head = leaf.split(".")[0]
        e = entries.get(head)
    return e.get("status") if isinstance(e, dict) else ("recorded" if e is not None else None)


def held_text(entries: dict) -> str:
    return json.dumps(entries.get("held") or {})


def main() -> None:
    report = []
    for path in sorted(PROFILES.glob("apple-macos-*-receded.json")):
        doc = json.loads(path.read_text())
        active_path = PROFILES / doc.get("resolvedOverActiveDocument", path.name.replace("-receded", ""))
        active = json.loads(active_path.read_text())
        mine, theirs = leaves(doc.get("patch", {})), leaves(active.get("patch", {}))
        entries, active_entries = doc.get("entries", {}) or {}, active.get("entries", {}) or {}
        held = held_text(entries)
        classes = {k: [] for k in ("measured", "held", "materialised", "inherited", "unrecorded")}
        for leaf, value in sorted(mine.items()):
            s = status(entries, leaf)
            if s == "measured":
                classes["measured"].append(leaf)
            elif s == "materialised":
                classes["materialised"].append(dict(leaf=leaf, value=value, activeValue=theirs.get(leaf)))
            elif s in ("held",) or (s is None and leaf in held):
                classes["held"].append(leaf)
            else:
                classes["unrecorded"].append(dict(leaf=leaf, value=value, record=s))
        for leaf, value in sorted(theirs.items()):
            if leaf in mine or status(active_entries, leaf) != "measured":
                continue
            row = dict(leaf=leaf, activeValue=value)
            if leaf in held or leaf.split(".")[0] in held:
                classes["held"].append(f"{leaf} (inherited, named by a held family)")
            else:
                classes["inherited"].append(row)
        silent = len(classes["materialised"]) + len(classes["inherited"])
        report.append(dict(document=path.name, sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                           active=active_path.name, recordedBy=doc.get("recordedBy"),
                           silentUnderX76=silent, **classes))
    out = dict(rule="X76 (W49 charter Decision Log 3)", documents=report,
               outsideTheForm=["macOS 26.5 receded light and dark: receded-profile.ts, no document (frozen)"])
    (HERE / "audit.json").write_text(json.dumps(out, indent=1) + "\n")
    print("X76 audit: every receded profile document's inherited leaves")
    for r in report:
        print(f"\n{r['document']} ({r['sha256'][:12]}, over {r['active']}; recorded by {r['recordedBy']})")
        print(f"  measured {len(r['measured'])}, held {len(r['held'])}, unrecorded {len(r['unrecorded'])}; "
              f"SILENT under X76: {r['silentUnderX76']}")
        for m in r["materialised"]:
            print(f"    materialised  {m['leaf']} = {m['value']} ("
                  + ("the active's patch names none: its resolved value" if m["activeValue"] is None
                     else f"the active's {m['activeValue']}") + ")")
        for m in r["inherited"]:
            print(f"    inherited     {m['leaf']} = {m['activeValue']} (fitted on the active, no receded record)")
        for m in r["unrecorded"]:
            print(f"    unrecorded    {m['leaf']} = {m['value']}")
    print("\noutside the document form:", "; ".join(out["outsideTheForm"]))


if __name__ == "__main__":
    main()
