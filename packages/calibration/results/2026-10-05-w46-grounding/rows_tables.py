#!/usr/bin/env python3.12
"""Markdown pivots of `rows-union.json` for the memo (deliverable 2).

    python3.12 -B rows_tables.py > rows-tables.md
"""
import json
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
d = json.loads((HERE / "rows-union.json").read_text())["perGeneration"]
GATED = {"tables": "gated both tiers", "M1": "gated WebGPU standard", "C1": "gated WebGPU",
         "X1": "gated WebGPU", "L1": "gated WebGPU (cal/val)", "E2": "gated WebGPU at 0.25 only"}


def sp(p):
    return p.replace("apple-macos-27.0-", "").replace("-standard", "").replace("-glass0.25", "").replace("-glass0.5", "")


def worst_table(ms):
    measured = [m for m in ms if m["measured"] is not None]
    absent = len(ms) - len(measured)
    note = f" ({absent} UNMEASURED: metric absent)" if absent else ""
    if not measured:
        return note.strip()
    m = min(measured, key=lambda m: m["margin"])
    return f"{m['scene']} {m['metric']} {m['measured']:.4f} vs {m['bound']}{note}"


print("#### The tables (ssim / ΔE / edge / silhouette / contour; the owner test's bounds)\n")
print("Gated = the owner test's bed (no probe, no recorded, rest pose; holdout INCLUDED and counted apart); "
      "not gated = the same table on the probe, recorded and inactive rows.\n")
print("| generation | profile | tier | gated cells | gated misses (non-holdout / holdout) | worst gated | "
      "not-gated cells | not-gated misses | worst not gated |")
print("|---|---|---|---|---|---|---|---|---|")
for g, v in d.items():
    for key, t in v["tables"].items():
        prof, tier = key.rsplit(" ", 1)
        gm = t["gatedMisses"] + t["gatedHoldoutMisses"]
        print(f"| {g} | {sp(prof)} | {tier} | {t['gatedCells']} | {len(t['gatedMisses'])} / {len(t['gatedHoldoutMisses'])} | "
              f"{worst_table(gm)} | {t['notGatedCells']} | {len(t['notGatedMisses'])} | {worst_table(t['notGatedMisses'])} |")
print("\nEvery gated miss count above equals `MISSED_27_ROWS`'s entries for that profile, tier and table metric "
      "(`tablesVsMissed27` in rows-union.json: all agree).\n")

print("#### M1, C1, X1, L1 (absolute), E2 (absolute), per generation and tier\n")
print("| generation | tier | M1 (median active / inactive; cells outside [0.6, 1.4]) | C1 worst bed x span (≤ 0.0042) | "
      "X1 failing / cells | L1 abs misses / measured (max error) | E2 median / max mean-abs codes | gated? |")
print("|---|---|---|---|---|---|---|---|")
for g, v in d.items():
    for tier in ("webgpu", "css"):
        m = v["M1"][tier]
        mb = m["beds"]
        m1 = (f"{mb['active']['median']:.3f} / {mb['inactive']['median']:.3f}; "
              f"{len(m['cellMisses'])} of {m['cells']}"
              + (f" (worst {max(m['cellMisses'], key=lambda c: abs(c['R'] - 1))['cell']} {max(m['cellMisses'], key=lambda c: abs(c['R'] - 1))['R']:.3f})" if m["cellMisses"] else ""))
        c1 = [(k, e) for k, e in v["C1"][tier]["perBedSpan"].items() if e["cells"]]
        k, e = max(c1, key=lambda kv: kv[1]["statistic"])
        c1s = f"{k} {e['statistic']:.4f} ({sum(x['statistic'] > 0.0042 for _, x in c1)} of {len(c1)} bed-spans over)"
        x = v["X1"][tier]
        x1 = f"{len(x['failing'])} / {x['cells']}" + (f" ({len(x['noRow'])} no row)" if x["noRow"] else "")
        l = v["L1absolute"][tier]
        l1 = f"{len(l['misses'])} / {l['measured']} ({l['maxError']:.4f})"
        e2v = [c["meanAbsCodes"] for c in v["E2"][tier]["perCell"] if c.get("meanAbsCodes") is not None]
        e2 = f"{statistics.median(e2v):.2f} / {max(e2v):.2f} ({len(e2v)} cells)"
        gated = "yes" if tier == "webgpu" else "no (CSS read only)"
        print(f"| {g} | {tier} | {m1} | {c1s} | {x1} | {l1} | {e2} | {gated} |")

print("\n#### Regression rows read off the pinned cuts (reference generations differ per gate)\n")
print("| generation | tier | M2 misses (named / failure) | L1 growth misses | E2 failing / named-miss cells | source |")
print("|---|---|---|---|---|---|")
for g, v in d.items():
    for tier in ("webgpu", "css"):
        m2 = v["M2"].get(tier)
        lg = v["L1growth"].get(tier)
        e2 = v["E2"][tier]
        if m2 is None and lg is None:
            continue
        m2s = "—" if m2 is None else (
            f"{len(m2['misses'])} ({sum(x.get('verdict') == 'named' for x in m2['misses'])} / "
            f"{sum(x.get('verdict') == 'failure' for x in m2['misses'])})")
        lgs = "—" if lg is None else str(len(lg["growthMisses"]))
        e2s = (f"{len(e2['failing'])} / {len(e2['namedMissCells'])}" if "failing" in e2 else "not gated (no reference)")
        src = (m2 or lg)["source"]
        print(f"| {g} | {tier} | {m2s} | {lgs} | {e2s} | {src} |")
