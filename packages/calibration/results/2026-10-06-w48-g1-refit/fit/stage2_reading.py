#!/usr/bin/env python3.12
"""W48 G1: a reading of stage 2's points beside the stage objective the search decides by (reads only).

Per point and dark profile: the stage objective (W47's rule, both scales pooled), the inactive groups'
aggregates against d0219cd684bf (F, C, P inactive: A / reference A, the halving of the F inactive target),
R on T1-fine for the two fine inactive cells (W48 Design (b): the share of the reference's fine-band excess
removed, (|c-n| - |k-n|) / |c-n| on the fine band, as W47's re-read), and every L1 miss. Writes
`path/d0219/stage2-reading.json` and `.txt`.

    python3.12 -B stage2_reading.py
"""
from __future__ import annotations

import importlib.util
import json
import math
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("w48_g1_fit", HERE / "fit.py")
X = importlib.util.module_from_spec(spec)
spec.loader.exec_module(X)
fit, W = X.fit, X.W
R = fit.rule()
FINE = ("checkerboard-8__rrect-md__inactive", "checkerboard-8__rrect-lg__inactive")


def le(x, n, eps):
    return abs(math.log((x + eps) / (n + eps)))


def groups(cells, profile):
    out = {}
    for s in ("F", "C", "P"):
        rs = [c for c in cells if c["profile"] == profile and R.in_scope(c) and c["stratum"] == s
              and c["pose"] == "inactive"]
        if rs:
            a = statistics.median(le(c["candidate"], c["native"], c["code"]) for c in rs)
            ar = statistics.median(le(c["reference"], c["native"], c["code"]) for c in rs)
            out[f"{s} inactive"] = dict(cells=len(rs), A=round(a, 4), ref=round(ar, 4), ratio=round(a / ar, 3))
    return out


def r_fine(cells, profile):
    out = {}
    for c in cells:
        if c["profile"] == profile and c["scene"] in FINE and "bands" in c:
            f = c["bands"]["fine"]
            ex = abs(f["reference"] - f["native"])
            out[c["scene"].split("__")[1]] = round((ex - abs(f["candidate"] - f["native"])) / ex, 3) if ex else None
        elif c["profile"] == profile and c["scene"] in FINE:
            ex = abs(c["reference"] - c["native"])
            out[c["scene"].split("__")[1] + " (whole)"] = round((ex - abs(c["candidate"] - c["native"])) / ex, 3)
    return out


def l1_misses(s):
    return [f"{k} {c['cell'].split('/')[1]} e{c['error']:.4f} g{(c['growth'] or 0):+.4f}"
            for k, v in s["L1cells"].items() for c in v
            if c["error"] is not None and (c["error"] > fit.L1_ABSOLUTE or (c["growth"] or 0) > fit.L1_GROWTH)]


def main() -> int:
    rec = json.loads((HERE / "path/d0219/stage2.json").read_text())
    rows = []
    for comp in rec["components"]:
        for label in comp["points"]:
            s = json.loads((HERE / "candidates" / label / "summary.json").read_text())
            cells = s["t1Cells"]
            rows.append(dict(family=comp["family"], label=label, objective=s["stages"]["stage2"]["objective"],
                             overrides=s["overrides"].get("receded.dark", {}),
                             profiles={p: dict(groups=groups(cells, p), Rfine=r_fine(cells, p)) for p in W.DARK_025},
                             L1misses=l1_misses(s)))
    rows.sort(key=lambda r: (r["family"], r["objective"]))
    (HERE / "path/d0219/stage2-reading.json").write_text(json.dumps(rows, indent=1) + "\n")
    lines = []
    for r in rows:
        g = "  ".join(f"{p.split('-')[3]} F{v['groups'].get('F inactive', {}).get('ratio')} "
                      f"C{v['groups'].get('C inactive', {}).get('ratio')} P{v['groups'].get('P inactive', {}).get('ratio')} "
                      f"R{list(v['Rfine'].values())}" for p, v in r["profiles"].items())
        lines.append(f"{r['family'][:12]:<12} {r['objective']:.4f} {r['label']:<70} {g}  L1 {r['L1misses'] or '-'}")
    (HERE / "path/d0219/stage2-reading.txt").write_text("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
