#!/usr/bin/env python3.12
"""W43 G3 (i): the light tone rows, solved on the calibration set against L1's own clauses.

Decision Log 7 item 1 as RULED: `backdropToneResponseThin` / `…Thick` (anchors held) and the black
branch `backdropToneBlackThin` / `…Thick`, in both light documents. The level of every light
calibration cell is linear in those ordinates to the precision a 0.02 step resolves, so the
Jacobian is MEASURED, one rendered probe per ordinate (`specs/j-*.json`, each the base candidate
with one ordinate +0.02 in both light documents; a rest cell reads the active document's
ordinate and an inactive cell the receded one's, so one probe gives both columns):

    err(cell) = err_base(cell) + Σ_j J[cell, j] · Δ_j

The solve minimises Σ err² over the light calibration cells (tinted included: L1 reads them)
subject to L1 as ruled, on every cell, with a margin: |err| ≤ 0.055 − m, and
|err| − |err_prefit| ≤ 0.005 − m (growth against the pre-fit render). A cell the constraints
cannot hold (its pre-fit error is already past both) enters the objective only, and is named.
The rows stay monotone in the anchor (each ordinate at least the previous one's + 1e-4).
Validation is not read: it is the transfer.

    python3.12 -B solve_tone.py --base c01 --spec-in specs/c01.json --label c02 [--margin 0.003]
        [--keep-structure-from specs/X.json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fit as F  # noqa: E402
import bed as B  # noqa: E402

STEP = 0.02
PARAMS = [f"thin{k}" for k in range(4)] + [f"thick{k}" for k in range(4)] + ["black"]
SLOTS = ("active.light", "receded.light")


def levels(label: str) -> dict:
    out = {}
    for r in F.load_bed(label, "webgpu", {"calibration"}):
        if B.scheme_of(r["key"]["profileKey"]) != "light":
            continue
        n, w = B.value(r, "material", "interiorMeanNative"), B.value(r, "material", "interiorMeanWeb")
        if n is not None and w is not None:
            out[(r["key"]["profileKey"], r["key"]["sceneId"])] = w - n
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", required=True)
    ap.add_argument("--spec-in", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--margin", type=float, default=0.003)
    ap.add_argument("--note", default="")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--min-norm", type=float, default=1.5,
                    help="hold a column whose summed |J| over the calibration cells is below this")
    args = ap.parse_args()
    base = levels(args.base)
    pre = levels("prefit")
    probes = {p: levels(f"j-{p}") for p in PARAMS}
    cells = sorted(k for k in base if k in pre and all(k in probes[p] for p in PARAMS))
    slot_of = lambda k: "receded.light" if "__inactive" in k[1] else "active.light"  # noqa: E731
    cols = [(slot, p) for slot in SLOTS for p in PARAMS]
    J = np.zeros((len(cells), len(cols)))
    for i, k in enumerate(cells):
        for j, (slot, p) in enumerate(cols):
            if slot == slot_of(k):
                J[i, j] = (probes[p][k] - base[k]) / STEP
    # A column the calibration set barely reads (the impulse anchor and the black branch: the
    # bed's untinted impulse cells are VALIDATION cells) is not identified by this solve; it keeps
    # the base candidate's value, which for c01 is Apple's own measured change at that knot.
    norms = np.abs(J).sum(axis=0)
    free = norms >= args.min_norm
    J = J[:, free]
    cols = [c for c, f in zip(cols, free) if f]
    held = [f"{slot} {p} (column norm {n:.2f})" for (slot, p), n, f in
            zip([(slot, p) for slot in SLOTS for p in PARAMS], norms, free) if not f]
    e0 = np.array([base[k] for k in cells])
    ep = np.array([pre[k] for k in cells])
    m = args.margin
    cap = np.minimum(0.055, np.abs(ep) + 0.005) - m
    reachable = np.abs(e0) <= cap + 0.08  # every cell; the cap itself decides feasibility below
    spec = json.loads(Path(args.spec_in).read_text())

    def cur(slot, p):
        o = spec["overrides"][slot]
        if p == "black":
            return o["backdropToneBlackThin"]
        row = "Thin" if p.startswith("thin") else "Thick"
        return o[f"backdropToneResponse{row}"][int(p[-1])]

    x0 = np.zeros(len(cols))
    cons = []
    # A cell no free column reaches (summed |J| < 0.3) cannot be held by this solve: it is left
    # out of the constraints, kept in the objective, and named below as a solve the rows cannot do.
    reach = np.abs(J).sum(axis=1)
    soft = [cells[i] for i in range(len(cells)) if reach[i] < 0.3 and abs(e0[i]) > cap[i]]
    for i in range(len(cells)):
        if reach[i] < 0.3 and abs(e0[i]) > cap[i]:
            continue
        cons.append({"type": "ineq", "fun": lambda d, i=i: cap[i] - (e0[i] + J[i] @ d)})
        cons.append({"type": "ineq", "fun": lambda d, i=i: cap[i] + (e0[i] + J[i] @ d)})
    for s, slot in enumerate(SLOTS):
        for row in ("thin", "thick"):
            for k in range(1, 4):
                lo, hi = (slot, f"{row}{k - 1}"), (slot, f"{row}{k}")
                a = cols.index(lo) if lo in cols else None
                b = cols.index(hi) if hi in cols else None
                va, vb = cur(*lo), cur(*hi)
                cons.append({"type": "ineq", "fun": lambda d, a=a, b=b, va=va, vb=vb:
                             (vb + (d[b] if b is not None else 0)) - (va + (d[a] if a is not None else 0)) - 1e-4})
    obj = lambda d: float(np.sum((e0 + J @ d) ** 2)) + 1e-3 * float(np.sum(d ** 2))  # noqa: E731
    res = minimize(obj, x0, constraints=cons, method="SLSQP", options=dict(maxiter=500, ftol=1e-12))
    d = res.x
    err = e0 + J @ d
    violated = [(cells[i], round(float(err[i]), 4), round(float(cap[i] + m), 4)) for i in range(len(cells))
                if abs(err[i]) > cap[i] + m + 1e-9]
    report = dict(success=bool(res.success), message=str(res.message), cells=len(cells),
                  objectiveBase=float(np.sum(e0 ** 2)), objective=float(np.sum(err ** 2)),
                  maxAbsBase=float(np.max(np.abs(e0))), maxAbs=float(np.max(np.abs(err))),
                  violatedWithoutMargin=violated, heldColumns=held,
                  unreachableCells=[f"{p}/{c}" for p, c in soft],
                  delta={f"{slot} {p}": round(float(d[j]), 5) for j, (slot, p) in enumerate(cols)})
    print(json.dumps(report, indent=1))
    worst = sorted(range(len(cells)), key=lambda i: -abs(err[i]))[:12]
    for i in worst:
        print(f"  {cells[i][0][17:-17]:<12} {cells[i][1]:<48} base {e0[i]:+.4f} prefit {ep[i]:+.4f} "
              f"-> {err[i]:+.4f} (cap {cap[i] + m:.4f})")
    if args.dry:
        return 0
    new = json.loads(json.dumps(spec))
    new["label"] = args.label
    for j, (slot, p) in enumerate(cols):
        o = new["overrides"][slot]
        if p == "black":
            for leaf in ("backdropToneBlackThin", "backdropToneBlackThick"):
                o[leaf] = round(o[leaf] + float(d[j]), 6)
        else:
            row = "Thin" if p.startswith("thin") else "Thick"
            v = list(o[f"backdropToneResponse{row}"])
            v[int(p[-1])] = round(v[int(p[-1])] + float(d[j]), 4)
            o[f"backdropToneResponse{row}"] = v
    new["note"] = args.note or f"light tone rows solved on the calibration set over {args.base} (solve_tone.py)"
    new["toneSolve"] = report
    with (HERE / "specs" / f"{args.label}.json").open("x") as f:
        f.write(json.dumps(new, indent=1) + "\n")
    print("wrote", HERE / "specs" / f"{args.label}.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
