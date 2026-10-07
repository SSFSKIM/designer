#!/usr/bin/env python3.12
"""W48 G1, after the gate report (the parent's request): the landing rule's budget over the EXISTING fit
renders only (no render). A rest cell is drawn by the active document alone, so every stage-2 point (all
share the stage-1 landed active) takes its rest cells from the landed point's full render; that composite
is exact. Stage-1 points have no inactive render, so they are read on their rest cells only. Writes
`path/d0219/budget-reading.json` and `.txt`.

    python3.12 -B budget_reading.py
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("w48_g1_fit", HERE / "fit.py")
X = importlib.util.module_from_spec(spec)
spec.loader.exec_module(X)
fit = X.fit
R = fit.rule()
LANDED = "d-s2-rta0.8-rs214-rfa0.5-rh10.25-re20.04-rk10.15-rk20.04-rn10.4-rn20.4-rg0"
SC = {p: p.split("-")[3] for p in R.SCOPE_PROFILES}


def summary(label):
    return json.loads((HERE / "candidates" / label / "summary.json").read_text())


def read(cells):
    ev = R.evaluate(cells, [])
    out = {}
    for p, v in ev["profiles"].items():
        away = [dict(scene=a["scene"], pose=a["pose"] if "pose" in a else ("inactive" if "inactive" in a["scene"] else "rest"),
                     B=round(a["growthInB"], 2)) for a in v["awayBeyondB"]]
        out[SC[p]] = dict(verdict=v["verdict"], away=away, past3B=[a["scene"] for a in v["awayBeyondCeiling"]],
                          targets={t: None if a is None else dict(A=round(a["A"], 4), ref=round(a["referenceA"], 4),
                                                                  halved=a["halved"]) for t, a in v["targets"].items()})
    return out


def inside(r):
    return all(len(v["away"]) <= 3 and not v["past3B"] for v in r.values())


def main() -> int:
    landed = summary(LANDED)
    rest = [c for c in landed["t1Cells"] if c["pose"] == "rest"]
    full, s1 = [], []
    for f in sorted((HERE / "specs").glob("*.json")):
        sp = json.loads(f.read_text())
        if sp["stage"] == "scale-twin" or not (HERE / "candidates" / sp["label"] / "summary.json").exists():
            continue
        s = summary(sp["label"])
        if sp["stage"] == "stage2":
            cells = rest + [c for c in s["t1Cells"] if c["pose"] == "inactive"]
            full.append(dict(label=sp["label"], objective=s["stages"]["stage2"]["objective"], reading=read(cells)))
        elif sp["stage"] in ("stage1", "start"):
            cells = [c for c in s["t1Cells"] if c["pose"] == "rest"]
            s1.append(dict(label=sp["label"], objective=s["stages"]["stage1"]["objective"], reading=read(cells)))
    count = lambda r: (sum(len(v["past3B"]) for v in r.values()), sum(len(v["away"]) for v in r.values()))  # noqa: E731
    full.sort(key=lambda x: (not inside(x["reading"]), count(x["reading"]), x["objective"]))
    s1.sort(key=lambda x: (not inside(x["reading"]), x["objective"]))
    body = dict(fullGate=dict(points=len(full), insideBudget=[x["label"] for x in full if inside(x["reading"])],
                              nearest=full[:5]),
                stage1RestOnly=dict(points=len(s1), insideBudgetOnRest=sum(inside(x["reading"]) for x in s1),
                                    best=[x for x in s1 if inside(x["reading"])][:5] or s1[:3]))
    (HERE / "path/d0219/budget-reading.json").write_text(json.dumps(body, indent=1) + "\n")
    lines = [f"full gate (stage-2 points, rest from the landed render): {len(full)} points, inside the budget at both "
             f"scales: {len(body['fullGate']['insideBudget'])}"]
    for x in full[:5]:
        lines.append(f"  {x['label']} obj {x['objective']:.4f} " + "; ".join(
            f"{s}: away {len(v['away'])} (rest {sum(a['pose'] == 'rest' for a in v['away'])}), past3B {len(v['past3B'])}, "
            + ", ".join(f"{t} {'H' if a and a['halved'] else '-'}{a and a['A']}/{a and a['ref']}" for t, a in v["targets"].items())
            for s, v in x["reading"].items()))
    lines.append(f"stage-1 points on their rest cells only: {len(s1)}, inside the budget on rest at both scales: "
                 f"{body['stage1RestOnly']['insideBudgetOnRest']}")
    for x in body["stage1RestOnly"]["best"]:
        lines.append(f"  {x['label']} obj {x['objective']:.4f} " + "; ".join(
            f"{s}: rest away {len(v['away'])} {[a['scene'] + ' ' + str(a['B']) for a in v['away']]} past3B {len(v['past3B'])}"
            for s, v in x["reading"].items()))
    (HERE / "path/d0219/budget-reading.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
