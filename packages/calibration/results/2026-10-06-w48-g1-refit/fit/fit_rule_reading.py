#!/usr/bin/env python3.12
"""W48 G1: the hashed landing rule (W47's `cuts/rule.py`) read on a fit point's composed T1 cells, per
dark profile (reads only; the gate's reading is the strict-mode stage's cut). Prints the verdict, the
targets' halving, every group with tau, and the cells away beyond B and past 3 B.

    python3.12 -B fit_rule_reading.py LABEL [LABEL ...] [--out FILE]
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


def reading(label: str) -> dict:
    s = json.loads((HERE / "candidates" / label / "summary.json").read_text())
    ev = R.evaluate(s["t1Cells"], s["t1Missing"])
    out = {}
    for p, v in ev["profiles"].items():
        out[p] = dict(verdict=v["verdict"], why=v.get("why"),
                      targets={t: None if a is None else dict(A=round(a["A"], 4), ref=round(a["referenceA"], 4),
                                                              halved=a["halved"]) for t, a in v["targets"].items()},
                      groups={k: dict(A=round(g["A"], 4), ref=round(g["referenceA"], 4), tau=round(g["tau"], 4),
                                      gated=g["gated"], holds=g["holds"], cells=g["cells"]) for k, g in v["groups"].items()},
                      awayBeyondB=[(a["scene"], round(a["growthInB"], 2)) for a in v["awayBeyondB"]],
                      pastCeiling=[a["scene"] for a in v["awayBeyondCeiling"]], budgetHolds=v["budgetHolds"],
                      partition={k: x["total"] for k, x in v["partition"].items()})
    return dict(label=label, verdict=ev["verdict"], profiles=out)


def main(argv) -> int:
    labels = [a for a in argv[1:] if not a.startswith("--") and (argv.index(a) == 0 or argv[argv.index(a) - 1] != "--out")]
    got = [reading(l) for l in labels]
    text = json.dumps(got, indent=1)
    if "--out" in argv:
        Path(argv[argv.index("--out") + 1]).write_text(text + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
