#!/usr/bin/env python3.12
"""W46 G0 (e): part 2 (`fit-declaration.json`) as the draft changed by exactly the decisions the ladders
support (charter clause 1: "part 2 after the ladders as a validated diff"). The changes are derived from
`ladders/results.json` by the protocol's rules, and `declare.py check-fit` re-validates every one:

- **narrow** each `tintAlpha` grid to the draft values among its arm's PASSING rungs (the shipped value
  and the rungs at which L1's clauses both pass): "the passing rungs are the transmission's domain in the
  fit" (clause 4 (i));
- **strike** every draft leaf whose lever read FLAT (no cell beyond its bar on any rung at the scale it
  acts at);
- **name-target** each target the ladders show no lever for, with the operator's shape given on the
  command line (X63; the parent rules an amendment or a deferral).
No scatter grid is narrowed: a narrowing must stay inside the lever's non-flat range, which spans only the
values its rungs read, so it would remove declared values no ladder read (W45 G0's part 2, the same call).

    python3.12 -B part2.py [--name-target 'TARGET=OPERATOR SHAPE' ...]   (writes ../fit-declaration.json;
                                                                          refuses once part 2 is hashed)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
sys.path.insert(0, str(EVIDENCE))
import bindings as W  # noqa: E402
import declare as D  # noqa: E402

R = EVIDENCE.relative_to(W.ROOT).as_posix()
TARGET_LADDER = {"P": "i", "C rest": "ii", "F inactive": "iii"}


def changes_from(draft: dict, results: dict, named: dict) -> list[dict]:
    out = []
    levers = {lev_id: e for lad in results["ladders"].values() for lev_id, e in lad.items()}
    for target, shape in named.items():
        if results["targets"][target]["lever"]:
            raise SystemExit(f"part2: the ladders read a lever for {target}; it is not named")
        out.append(dict(kind="name-target", target=target, ladder=TARGET_LADDER[target], operatorShape=shape))
    dropped = {t for t in named}
    for move in draft["moves"]:
        for family, body in move["families"].items():
            for key, spec in body["leaves"].items():
                lever = spec.get("ladder")
                if lever is None or spec["target"] in dropped:
                    continue
                e = levers[lever]
                if e["flat"]:
                    out.append(dict(kind="strike", move=move["id"], family=family, leaf=key, lever=lever,
                                    why=f"lever {lever} read flat on every rung (ladders/results.json)"))
                elif "passingRungs" in e:
                    grid = [x for x in spec["grid"] if x in set(e["passingRungs"])]
                    if grid != spec["grid"]:
                        out.append(dict(kind="narrow", move=move["id"], family=family, leaf=key, lever=lever, grid=grid,
                                        why=f"the transmission's domain is its passing rungs {sorted(e['passingRungs'])}"))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--name-target", action="append", default=[])
    args = ap.parse_args(argv)
    if W.PART2_DIGEST.exists():
        raise SystemExit("part2 REFUSES: part 2 is hashed")
    W.require_part(1)
    draft = json.loads(W.DRAFT.read_text())
    results = json.loads((HERE / "results.json").read_text())
    protocol = json.loads((HERE / "protocol.json").read_text())
    named = dict(x.split("=", 1) for x in args.name_target)
    changes = changes_from(draft, results, named)
    body = D.apply_changes(draft, changes, results, protocol)
    body.pop("status", None)
    sources = [f"{R}/ladders/results.json", f"{R}/ladders/results.txt", f"{R}/ladders/protocol.json",
               f"{R}/ladders/read.py", f"{R}/ladders/ladder.py", f"{R}/ladders/part2.py", f"{R}/ladders/runs.jsonl",
               f"{R}/ladders/x60-evidence.json"] + \
        [f"{R}/fit/{n}" for n in ("fit.py", "search.py", "joint.py", "finding.py", "recover.py", "labels.json",
                                  "build-candidate.ts")] + [f"{R}/seal/seal.ts", f"{R}/cuts/rule.py"]
    fit = dict(schema=draft["schema"],
               status="PART 2: the draft changed only by the ladders' permitted decisions (declare.py check-fit)",
               fromDraft=dict(partOneSha256=W.part_hash(1), draftSha256=D.sha(W.DRAFT.read_bytes())),
               changes=changes, **{k: v for k, v in body.items() if k != "schema"},
               sources={s: D.sha(D.source_bytes(s)) for s in sources})
    W.PART2.write_bytes(D.serialise(fit))
    print(f"fit-declaration.json: {len(changes)} change(s): " + "; ".join(
        f"{c['kind']} {c.get('leaf') or c.get('target')}" + (f" -> {c['grid']}" if c["kind"] == "narrow" else "")
        for c in changes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
