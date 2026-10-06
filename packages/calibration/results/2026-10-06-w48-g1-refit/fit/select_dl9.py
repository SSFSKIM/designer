#!/usr/bin/env python3.12
"""W48 G1: the selection part 2's amendment declares (W48 Decision Log 9 and its addendum), over the fit's
RENDERED points, no render: "Inside the objective's declared tie of a stage's minimum, over every rendered
point of that stage, the point with the fewest cells away beyond B summed over both scales is selected, then
the fewest past 3 B, then the hashed tie rule. The budget of a rendered point is read by its exact composite
(its own rest cells with the landed inactive cells, the receded document unchanged)." A stage-2 point's
composite is its own inactive cells with the selected stage-1 point's rest cells. The budget arithmetic is
`reselect.py`'s (the landing rule's `rule.evaluate`); the hashed tie rule is W47's `search.choose`, measured
from the stage's base. Writes `path/d0219/dl9-selection.json`.

    python3.12 -B select_dl9.py
"""
import importlib.util, json
from pathlib import Path

H = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("rs", H / "reselect.py"); m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
search, fit = m.search, m.fit
search.choose = m._hashed_choose                      # the dry run's procedural patch is not used here


def rendered(stage):
    return [f.stem for f in sorted((H / "specs").glob("*.json"))
            if json.loads(f.read_text())["stage"] == stage and (H / "candidates" / f.stem / "summary.json").exists()]


def select(stage, base):
    pts = rendered(stage)
    obj = {l: search.scope_objective(l, stage) for l in pts}
    best, tie = min(obj.values()), fit.stage_tie_of(stage)
    close = [l for l in pts if obj[l] - best <= tie]
    least = min(m.budget(l) for l in close)
    few = [l for l in close if m.budget(l) == least]
    origin = search.base_overrides(base)
    pick = m._hashed_choose(few, lambda n: obj[n], tie, origin, search.declared_keys(origin), search.base_overrides)
    return dict(stage=stage, rendered=len(pts), minimum=best, tie=tie, insideTie=len(close),
                fewest=dict(away=least[0], past3B=least[1], points=few), selected=pick, objective=obj[pick],
                budget=dict(away=m.budget(pick)[0], past3B=m.budget(pick)[1]))


s1 = select("stage1", "start-d0219")
m.STATE["rest"] = [c for c in m.cells(s1["selected"]) if c["pose"] == "rest"]
s2 = select("stage2", s1["selected"])
rec = dict(rule="W48 Decision Log 9 and its addendum (part 2's amendment)", stage1=s1, stage2=s2)
(H / "path/d0219/dl9-selection.json").write_text(json.dumps(rec, indent=1) + "\n")
print(json.dumps({k: (v["selected"], round(v["objective"], 4), v["budget"]) for k, v in rec.items() if k != "rule"}))
