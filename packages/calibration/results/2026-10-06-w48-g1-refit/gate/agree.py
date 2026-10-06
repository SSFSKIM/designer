#!/usr/bin/env python3.12
"""W48 G1 (Decision Log 9 addendum): the selected pair's gate reading against the composite it was selected
on. The composite is the stage-1 selection's rest cells with the stage-2 selection's inactive cells, from
their fit renders (candidate mode); the gate is the re-freeze's strict-mode stage cut. Per dark WebGPU gate
cell, the candidate's T1 reading (and a T cell's fine and low bands) must agree within the cell's bar (W44's
run-to-run bar, 0.5 code); the rule's verdict, targets and away lists are set beside each other.

    python3.12 -B agree.py CUT_NAME        writes agree-<CUT_NAME>.json beside this file; exit 1 on a disagreement
"""
import gzip, importlib.util, json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIT = HERE.parent / "fit"
spec = importlib.util.spec_from_file_location("br", FIT / "budget_reading.py"); BR = importlib.util.module_from_spec(spec)
spec.loader.exec_module(BR)
S1 = "d-s1-ta0.7-s10-o0.05-fa0.34-fb1-n10.72-n20.46-g-0.5-m1160-m2160-t10.2-t20.2"
S2 = "d-s2-rta0.8-rq0.25-rw15-rw25-rs214-rfa0.5-rh10.25-re20.04-rk10.15-rk20.04-rn10.4-rn20.4-rg0"
name = sys.argv[1]
comp = [c for c in BR.summary(S1)["t1Cells"] if c["pose"] == "rest"] + \
       [c for c in BR.summary(S2)["t1Cells"] if c["pose"] == "inactive"]
cut = json.load(gzip.open(HERE.parent / "cuts" / f"{name}.json.gz"))
gate = [c for c in cut["T1"]["cells"] if BR.R.in_scope(c)]
key = lambda c: (c["profile"], c["scene"])  # noqa: E731
ck, gk = {key(c): c for c in comp if BR.R.in_scope(c)}, {key(c): c for c in gate}
out, worst = [], 0.0
for k in sorted(set(ck) | set(gk)):
    a, b = ck.get(k), gk.get(k)
    if a is None or b is None:
        out.append(dict(cell="/".join(k), missing="composite" if a is None else "gate"))
        continue
    d = abs(a["candidate"] - b["candidate"]) / max(b["code"], 1e-12)
    bands = {bd: abs(a["bands"][bd]["candidate"] - b["bands"][bd]["candidate"]) / max(b["code"], 1e-12)
             for bd in ("fine", "low")} if "bands" in a and "bands" in b else {}
    worst = max([worst, d, *bands.values()])
    if d > 0.5 or any(v > 0.5 for v in bands.values()):
        out.append(dict(cell="/".join(k), codes=d, bands=bands))
rc, rg = BR.read(comp), BR.read(gate)
same = {s: dict(composite=dict(away=len(rc[s]["away"]), past3B=len(rc[s]["past3B"])),
                gate=dict(away=len(rg[s]["away"]), past3B=len(rg[s]["past3B"])),
                awaySame=sorted(a["scene"] for a in rc[s]["away"]) == sorted(a["scene"] for a in rg[s]["away"]),
                targets=dict(composite=rc[s]["targets"], gate=rg[s]["targets"])) for s in rc}
body = dict(cells=len(gk), compositeCells=len(ck), worstCodes=worst, disagreements=out, budget=same,
            agrees=not out and all(v["awaySame"] for v in same.values()))
(HERE / f"agree-{name}.json").write_text(json.dumps(body, indent=1) + "\n")
print(json.dumps({k: v for k, v in body.items() if k != "budget"}, indent=1)[:1500])
print({s: (v["composite"], v["gate"], v["awaySame"]) for s, v in same.items()})
sys.exit(0 if body["agrees"] else 1)
