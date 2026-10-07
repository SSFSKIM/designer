#!/usr/bin/env python3.12
"""W48 G1 (the parent's request after the gate report): every stage-1 point's REST render composed with the
landed point's INACTIVE render, read under the landing rule's budget. Exact without a render: the landed
receded patch names every leaf any stage-1 point moves (asserted per point), so the resolved receded material,
and with it every inactive pixel, is the landed one whatever the active (one composite's receded digest built
in scratch, aa1a1b198ee72850, equals the landed's). Writes `path/d0219/budget-reading-composite.json`.

    python3.12 -B budget_composite.py
"""
import importlib.util, json
from pathlib import Path

H = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("br", H / "budget_reading.py"); m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
inact = [c for c in m.summary(m.LANDED)["t1Cells"] if c["pose"] == "inactive"]
landed_rec = json.loads((H / "specs" / f"{m.LANDED}.json").read_text())["overrides"]["receded.dark"]
rows = []
for f in sorted((H / "specs").glob("*.json")):
    sp = json.loads(f.read_text())
    if sp["stage"] not in ("stage1", "start") or not (H / "candidates" / sp["label"] / "summary.json").exists():
        continue
    assert set(sp["overrides"].get("active.dark", {})) <= set(landed_rec), sp["label"]
    s = m.summary(sp["label"]); r = m.read([c for c in s["t1Cells"] if c["pose"] == "rest"] + inact)
    p3 = [len(v["past3B"]) for v in r.values()]; aw = [len(v["away"]) for v in r.values()]
    rows.append(dict(outside=max(p3) > 0 or max(aw) > 3, past3B=sum(p3), away=sum(aw),
                     objective=s["stages"]["stage1"]["objective"], label=sp["label"], reading=r))
rows.sort(key=lambda x: (x["outside"], x["past3B"], x["away"], x["objective"]))
(H / "path/d0219/budget-reading-composite.json").write_text(json.dumps(dict(
    points=len(rows), insideBudget=sum(not x["outside"] for x in rows), nearest=rows[:10]), indent=1) + "\n")
print(len(rows), "composites;", sum(not x["outside"] for x in rows), "inside the budget")
