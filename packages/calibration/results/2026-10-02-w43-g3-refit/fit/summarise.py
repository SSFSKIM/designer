#!/usr/bin/env python3.12
"""W43 G3 (i): one cuts.py output as a per-profile, per-tier table (markdown), for the record.

    python3.12 -B summarise.py CUTS.json [--label NAME]
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path

PROFILES = ["1x-light", "2x-light", "1x-dark", "2x-dark"]


def short(cell: str) -> str:
    return cell.replace("apple-macos-27.0-", "").replace("-standard-glass0.25", "")


def profile_of(cell: str) -> str:
    return short(cell).split("/")[0]


def main() -> int:
    r = json.loads(Path(sys.argv[1]).read_text())
    label = sys.argv[sys.argv.index("--label") + 1] if "--label" in sys.argv else Path(sys.argv[1]).stem
    out = [f"### {label}", "", "| cut | tier | " + " | ".join(PROFILES) + " | verdict |",
           "| --- | --- | " + " | ".join("---" for _ in PROFILES) + " | --- |"]
    for renderer in ("webgpu", "css"):
        row = []
        for p in PROFILES:
            t = r["tables"].get(f"apple-macos-27.0-{p}-standard-glass0.25 {renderer}")
            row.append("—" if t is None else f"{len(t['misses'])} miss / {t['cells']} cells")
        verdicts = {t["verdict"] for k, t in r["tables"].items() if k.endswith(renderer)}
        out.append(f"| tables | {renderer} | " + " | ".join(row) + f" | {'/'.join(sorted(verdicts)) or '—'} |")
    for renderer in ("webgpu", "css"):
        m1 = r["M1"][renderer]
        beds = m1["beds"]
        cell = {p: [] for p in PROFILES}
        for c in r["M1M2cells"][renderer]:
            cell[short(c["profile"])].append(c["R"])
        row = [("—" if not v else f"R {min(v):.2f}–{max(v):.2f}") for p, v in cell.items()]
        med = ", ".join(f"{k} {v['median']:.3f}" for k, v in beds.items())
        out.append(f"| M1 | {renderer} | " + " | ".join(row) + f" | {m1['verdict']} (medians {med}) |")
    for renderer in ("webgpu", "css"):
        m2 = r["M2"][renderer]
        count = defaultdict(lambda: [0, 0])
        for m in m2["misses"]:
            count[profile_of(m["cell"])][0 if m["verdict"] == "named" else 1] += 1
        row = [f"{count[p][0]} named, {count[p][1]} fail" for p in PROFILES]
        out.append(f"| M2 | {renderer} | " + " | ".join(row) + f" | {m2['verdict']} |")
    for renderer in ("webgpu", "css"):
        c1 = r["C1"][renderer]["perBedSpan"]
        row = []
        for p in PROFILES:
            bed = p.replace("-", " ")
            vals = [f"{e['statistic']:.4f}" if e["statistic"] is not None else "—"
                    for k, e in c1.items() if k.startswith(bed)]
            row.append(" / ".join(vals))
        out.append(f"| C1 (96/128/160) | {renderer} | " + " | ".join(row) + f" | {r['C1'][renderer]['verdict']} |")
    if not isinstance(r["X1"], str):
        for renderer in ("webgpu", "css"):
            x = r["X1"][renderer]
            fail = defaultdict(int)
            for c in x["failing"]:
                fail[profile_of(c["cell"])] += 1
            tot = defaultdict(int)
            for c in x["perCell"]:
                tot[profile_of(c["cell"])] += 1
            row = [f"{fail[p]} fail / {tot[p]}" for p in PROFILES]
            out.append(f"| X1 | {renderer} | " + " | ".join(row) + f" | {x['verdict']} |")
    for renderer in ("webgpu", "css"):
        l1 = r["L1"][renderer]
        mx = defaultdict(float)
        gr = defaultdict(lambda: -1.0)
        miss = defaultdict(int)
        for c in l1["cells"]:
            p = profile_of(c["cell"])
            if c["error"] is not None:
                mx[p] = max(mx[p], c["error"])
            if c["growth"] is not None:
                gr[p] = max(gr[p], c["growth"])
        for c in l1["absoluteMisses"] + l1["growthMisses"]:
            miss[profile_of(c["cell"])] += 1
        row = [f"max {mx[p]:.4f}, growth {gr[p]:+.4f}, {miss[p]} miss" if p in mx else "—" for p in PROFILES]
        out.append(f"| L1 | {renderer} | " + " | ".join(row) + f" | {l1['verdict']} |")
    if not isinstance(r["E2"], str):
        for renderer in ("webgpu", "css"):
            e = r["E2"][renderer]
            fail = defaultdict(int)
            tot = defaultdict(int)
            for c in e["perCell"]:
                tot[profile_of(c["cell"])] += 1
            for c in e["failing"]:
                fail[profile_of(c["cell"])] += 1
            row = [f"{fail[p]} fail / {tot[p]}" for p in PROFILES]
            mean = e["meanChange"]
            out.append(f"| E2 | {renderer} | " + " | ".join(row) +
                       f" | {e['verdict']} (mean change {'—' if mean is None else format(mean, '+.3f')} codes; {len(e['namedMissBins'])} named bins) |")
    for renderer in ("webgpu", "css"):
        s = r["S1"][renderer]
        wrong = defaultdict(int)
        for w in s["wrongSign"]:
            wrong[profile_of(w["cell"])] += 1
        row = []
        for p in PROFILES:
            e = s["perProfileMedian"][f"apple-macos-27.0-{p}-standard-glass0.25"]
            row.append(f"n {e['cells']}, median {e['median']:.3f}, {wrong[p]} wrong sign" if e["cells"] else "—")
        pooled = s["pooledMedianRatio"]
        pooled = "—" if pooled is None else format(pooled, ".3f")
        out.append(f"| S1 (R2) | {renderer} | " + " | ".join(row) +
                   f" | {s['verdict']} (pooled median {pooled}, {len(s['wrongSign'])} wrong sign) |")
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
