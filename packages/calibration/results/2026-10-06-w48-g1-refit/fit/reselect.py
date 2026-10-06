#!/usr/bin/env python3.12
"""W48 G1 (Decision Log 9 §1-§2): the fit's selection re-run under part 2's amended selection rule, over the
EXISTING renders only. W47's `search.py` procedure is replayed unchanged (its steps, grids, passes, the step's
start as a candidate, the stage decision) with one change, the amendment's: wherever the hashed tie rule
chooses (`search.choose`: every coordinate or factorial step, and `decide`), the points inside the
objective's declared tie of the minimum are first narrowed to those with the FEWEST cells away beyond B
summed over both dark scales, then the fewest past 3 B, and only then the hashed tie rule.

The budget counts are the landing rule's (`rule.evaluate`) on a full-gate reading: a stage-1 point's own
rest cells with the landed point's inactive cells, a stage-2 point's own inactive cells with the selected
stage-1 point's rest cells. Both composites are exact: a rest cell is drawn by the active document alone,
and the landed receded patch names every leaf a stage-1 point moves, so the inactive pixels do not depend on
which stage-1 point is the active (`budget_composite.py`; a scratch build's receded digest is the landed
one's). A stage-2 point over a new active is read off the render of the same receded overrides over the
landed active, for the same reason; the replay checks the two resolve the same receded digest by building
the new pair in scratch (no render). A point no render measures refuses (`NeedsRender`): nothing renders.

    python3.12 -B reselect.py        writes path/d0219/reselect/{stage1,stage2,reselect}.json
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("w48_g1_fit", HERE / "fit.py")
X = importlib.util.module_from_spec(spec)
spec.loader.exec_module(X)
fit, W = X.fit, X.W
search = X.search()
R = fit.rule()
spec2 = importlib.util.spec_from_file_location("br", HERE / "budget_reading.py")
BR = importlib.util.module_from_spec(spec2)
spec2.loader.exec_module(BR)
LANDED = BR.LANDED
OUT = HERE / "path" / "d0219" / "reselect"
SCRATCH = W.SCRATCH / "g1-scratch" / "reselect"


class NeedsRender(W.Refusal):
    """A point the amended path offers that no existing render measures."""


def cells(label):
    return BR.summary(label)["t1Cells"]


STATE = {"rest": [c for c in cells(LANDED) if c["pose"] == "rest"],
         "inactive": [c for c in cells(LANDED) if c["pose"] == "inactive"], "measuredBy": {}}
_budget: dict = {}


def budget(label: str) -> tuple[int, int]:
    measured = STATE["measuredBy"].get(label, label)
    s = BR.summary(measured)
    own = s["t1Cells"]
    if s["stage"] in ("stage2",):
        full = STATE["rest"] + [c for c in own if c["pose"] == "inactive"]
    else:
        full = [c for c in own if c["pose"] == "rest"] + STATE["inactive"]
    key = (label, json.dumps(sorted(c["scene"] + c["profile"] for c in full)))
    if key not in _budget:
        r = BR.read(full)
        _budget[key] = (sum(len(v["away"]) for v in r.values()), sum(len(v["past3B"]) for v in r.values()))
    return _budget[key]


_hashed_choose = search.choose


def amended_choose(names, objective, tie, origin, keys, overrides):
    names = list(dict.fromkeys(names))
    values = {n: objective(n) for n in names}
    best = min(values.values())
    close = [n for n in names if values[n] - best <= tie]
    least = min(budget(n) for n in close)
    return _hashed_choose([n for n in close if budget(n) == least], objective, tie, origin, keys, overrides)


search.choose = amended_choose
search.PATH = OUT


def receded_digest(overrides: dict, tag: str) -> str:
    folder = SCRATCH / tag
    if not (folder / tag / "receded.dark.json").exists():
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "spec.json").write_text(json.dumps(dict(label=tag, note="reselect scratch", stage="scratch",
                                                          family="scratch", start="d0219", overrides=overrides)))
        env = dict(os.environ, W47_CANDIDATE_ROOT=str(folder))
        got = subprocess.run(["pnpm", "exec", "tsx", str(W.BUILDER), str(folder / "spec.json")], cwd=W.CAL,
                             capture_output=True, text=True, env=env)
        if got.returncode:
            raise W.Refusal(f"scratch build {tag}: {got.stdout[-400:]} {got.stderr[-400:]}")
    return json.loads((folder / tag / "receded.dark.json").read_text())["resolvedMaterialSha256"]


class NoRender(search.Runner):
    def points(self, cands, labels, stage_id, family, start, scope):
        named = []
        landed_active = search.base_overrides(LANDED)["active.dark"]
        for ov, label in zip(cands, labels):
            known = search.same_point(ov, start)
            if known is None and stage_id == "stage2":
                twin = json.loads(json.dumps(ov))
                twin["active.dark"] = landed_active
                known = search.same_point(twin, start)
                if known is not None:
                    tag = f"rs-{len(STATE['measuredBy'])}"
                    if receded_digest(ov, tag) != receded_digest(search.base_overrides(known), tag + "-t"):
                        raise W.Refusal(f"{label}: its receded material is not {known}'s; not measured")
                    STATE["measuredBy"][label] = known
                    known_label = label
                    fit.write_spec(label, ov, f"Decision Log 9 re-selection: measured by {known}", stage_id,
                                   family, start) if False else None
                    named.append(known)
                    continue
            if known is None:
                raise NeedsRender(f"{stage_id}/{family}: {label} ({json.dumps(ov, sort_keys=True)[:300]}) has no render")
            named.append(known)
        return named


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    runner = NoRender()
    s1 = search.stage("stage1", "start-d0219", 2, runner)
    sel1 = s1["landed"]
    STATE["rest"] = [c for c in cells(sel1) if c["pose"] == "rest"]
    s2 = search.stage("stage2", sel1, 2, runner)
    rec = dict(rule="Decision Log 9 §1: inside the objective's declared tie, fewest cells away beyond B (both "
                    "scales summed), then fewest past 3 B, then the hashed tie rule",
               stage1=dict(landed=sel1, budget=budget(sel1), objective=search.scope_objective(sel1, "stage1")),
               stage2=dict(landed=s2["landed"], measuredBy=STATE["measuredBy"].get(s2["landed"], s2["landed"]),
                           budget=budget(s2["landed"])),
               measuredBy=STATE["measuredBy"])
    (OUT / "reselect.json").write_text(json.dumps(rec, indent=1) + "\n")
    print(json.dumps(rec, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
