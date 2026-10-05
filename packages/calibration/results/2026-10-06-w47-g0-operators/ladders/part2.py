#!/usr/bin/env python3.12
"""W47 G0 (g): part 2 (`fit-declaration.json`) as the draft changed by exactly the decisions the ladders
support (charter clause 2: "part 2 after the ladders as a validated diff"; clause 5; `protocol.json`
`decisions`). W46 G0's `ladders/part2.py`, ported by copy and re-bound to W47's clause 5; W46's copy is
untouched. The changes are derived from `ladders/results.json` (`operators`, `ladders`) by the protocol's
rules, and `declare.py check-fit` re-validates every one:

- **name-unfitted** each operator whose ladder shows no separation (no rung meets its clause 5 bar at
  both scales): it is NOT fitted, part 2 names it with the reading (X63), and its leaves
  (`bindings.OPERATOR_1` / `OPERATOR_2`) leave the draft; the wave continues on the other;
- **name-target** a target the parent rules has no lever (`--name-target`; X63), on its ladder;
- **body-width-first** when a receded `optics.regular.blurSigma` rung of ladder (iii) meets its bar on its
  own: the body width is fitted, the tap is named unfitted and its leaves leave the draft (Decision Log 3);
- **name-1x-gap** when ladder (ii) meets its bar: the 1x per-span width gap is named with
  `sizeHeavySecondShareFar1x`'s shape (X63; Decision Log 2's declined item); nothing is added;
- **narrow** each `tintAlpha` grid the draft ties to ladder (i) to the draft values among the shipped
  value and the base rungs at which L1 passes;
- **strike** a draft leaf whose protocol rungs (`rungs`) read flat (no cell beyond its bar), and each
  stage-1 leaf `conditional` on ladder (ii) when ladder (ii) did not meet its bar (Design "The moves");
- **stop**: neither operator separates, so the wave closes at G0 with the finding and part 2 is not
  written. A separation at one scale only is not decided here: it goes to the parent.
Rungs that were not read (an operator not yet in the runtime, a selection not recorded) decide nothing:
part 2 refuses while a ladder it would decide from is incomplete.

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

R = EVIDENCE.relative_to(W.ROOT).as_posix()
GAP_1X = ("a 1x twin of W45's far-graded second-tap share, sizeHeavySecondShareFar1x (identity 0, a plain value "
          "drop), giving the 1x thick spans the width ladder (ii) found at 2x (Decision Log 2, declined for W47)")


def _draft_leaves(draft: dict):
    for move in draft["moves"]:
        for family, body in move["families"].items():
            for key, spec in body["leaves"].items():
                yield move["id"], family, key, spec


# The ladder a named target is decided on (Design "The targets"): P and C rest on ladder (i), F inactive on
# ladder (iii). A target is named only on the parent's ruling (`--name-target`), never inferred here.
TARGET_LADDER = {"P": "i", "C rest": "i", "F inactive": "iii"}
OPERATOR_LEAVES = {"operator 1": set(W.OPERATOR_1), "operator 2": set(W.OPERATOR_2)}


def _flat(results: dict, rungs) -> bool:
    got = results.get("rungs") or {}
    return bool(rungs) and all(r in got for r in rungs) and not any(
        c.get("moved") for r in rungs for c in got[r]["cells"].values())


def changes_from(draft: dict, results: dict, named: dict) -> list[dict]:
    """The changes clause 5 requires of the draft, in `protocol.json`'s words; `declare.py`'s
    `apply_changes` and `mandatory_failures` re-validate every one."""
    ops, lads = results["operators"], results["ladders"]
    for lad in ("i", "iii"):
        if not lads[lad]["complete"]:
            raise SystemExit(f"part2 REFUSES: ladder ({lad}) is incomplete (not read: {lads[lad]['notRead']}); "
                             "an unread rung decides nothing")
    one = [f"{k}: {v['oneScaleOnly']}" for k, v in ops.items() if v.get("oneScaleOnly")]
    if one:
        raise SystemExit(f"part2 REFUSES: a separation at one scale only goes to the parent first ({'; '.join(one)}); "
                         "the operator is neither struck nor admitted until ruled (the parent's ruling of 2026-10-06, "
                         "protocol.json `rulings` separation-both-scales)")
    op1, op2 = ops["operator 1"]["separates"], ops["operator 2"]["separates"] or ops["operator 2"]["bodyWidthMeets"]
    if not op1 and not op2:
        raise SystemExit("part2 STOPS: neither operator separates; the wave closes at G0 with the finding (clause 5)")
    out, dropped = [], set()
    for target, shape in named.items():
        out.append(dict(kind="name-target", target=target, ladder=TARGET_LADDER[target], operatorShape=shape))
    if not op1:
        dropped |= OPERATOR_LEAVES["operator 1"]
        out.append(dict(kind="name-unfitted", operator="operator 1", ladder="i",
                        reading=f"no ladder (i) rung meets clause 5 (i)'s bar at both scales (read {lads['i']['read']})"))
    if ops["operator 2"]["bodyWidthMeets"]:
        dropped |= OPERATOR_LEAVES["operator 2"]
        out.append(dict(kind="body-width-first", operator="operator 2", ladder="iii",
                        reading="a receded optics.regular.blurSigma rung meets clause 5 (iii)'s bar on its own: the body "
                                "width is fitted and the tap is named unfitted (Decision Log 3); it stays landed inert"))
    elif not ops["operator 2"]["separates"]:
        dropped |= OPERATOR_LEAVES["operator 2"]
        out.append(dict(kind="name-unfitted", operator="operator 2", ladder="iii",
                        reading=f"no ladder (iii) rung meets clause 5 (iii)'s bar at both scales (read {lads['iii']['read']})"))
    width = ops["2x width"]
    if width["meets"]:
        out.append(dict(kind="name-1x-gap", ladder="ii", operatorShape=GAP_1X))
    passing = set(lads["i"]["passingL1"] or [])
    shipped = W.document("active.dark")["patch"]["optics"]["regular"]["tintAlpha"]
    base = {shipped} | {float(lab[3:]) for lab in passing if lab.startswith("i-a") and lab.count("-") == 1}
    for move, family, key, spec in _draft_leaves(draft):
        if key in dropped or spec.get("target") in named:
            continue                       # the name-unfitted / name-target change removes it
        if spec.get("conditional") == "ii" and not width["meets"]:
            out.append(dict(kind="strike", move=move, family=family, leaf=key, ladder="ii",
                            why="crossed into stage 1 only where ladder (ii) meets its bar, which it did not"))
            continue
        if key == "optics.regular.tintAlpha" and spec.get("ladder") == "i":
            grid = [x for x in spec["grid"] if x in base]
            if grid != spec["grid"]:
                out.append(dict(kind="narrow", move=move, family=family, leaf=key, ladder="i", grid=grid,
                                why=f"the transmission's domain is the shipped value and the base rungs at which L1 "
                                    f"passes {sorted(base)}"))
        if spec.get("ladder") is not None and _flat(results, spec.get("rungs")):
            out.append(dict(kind="strike", move=move, family=family, leaf=key, ladder=spec["ladder"],
                            why=f"its rungs {spec['rungs']} read flat (no cell beyond its bar)"))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--name-target", action="append", default=[])
    args = ap.parse_args(argv)
    if W.PART2_DIGEST.exists():
        raise SystemExit("part2 REFUSES: part 2 is hashed")
    W.require_part(1)
    import declare as D  # noqa: PLC0415
    draft = json.loads(W.DRAFT.read_text())
    results = json.loads((HERE / "results.json").read_text())
    protocol = json.loads((HERE / "protocol.json").read_text())
    named = dict(x.split("=", 1) for x in args.name_target)
    changes = changes_from(draft, results, named)
    body = D.apply_changes(draft, changes, results, protocol)
    body.pop("status", None)
    sources = [f"{R}/ladders/results.json", f"{R}/ladders/results.txt", f"{R}/ladders/protocol.json",
               f"{R}/ladders/selections.json", f"{R}/ladders/read.py", f"{R}/ladders/ladder.py",
               f"{R}/ladders/part2.py", f"{R}/ladders/runs.jsonl", f"{R}/ladders/x60-evidence.json"] + \
        [f"{R}/fit/{n}" for n in ("fit.py", "search.py", "joint.py", "finding.py", "recover.py", "labels.json",
                                  "build-candidate.ts")] + [f"{R}/seal/seal.ts", f"{R}/cuts/rule.py"]
    fit = dict(schema=draft["schema"],
               status="PART 2: the draft changed only by the ladders' permitted decisions (declare.py check-fit)",
               fromDraft=dict(partOneSha256=W.part_hash(1), draftSha256=D.sha(W.DRAFT.read_bytes())),
               changes=changes, **{k: v for k, v in body.items() if k != "schema"},
               sources={s: D.sha(D.source_bytes(s)) for s in sources})
    W.PART2.write_bytes(D.serialise(fit))
    print(f"fit-declaration.json: {len(changes)} change(s): " + "; ".join(
        f"{c['kind']} {c.get('leaf') or c.get('operator') or c.get('target') or ''}"
        + (f" -> {c['grid']}" if c["kind"] == "narrow" else "") for c in changes))
    return 0


if __name__ == "__main__":
    sys.exit(main())
