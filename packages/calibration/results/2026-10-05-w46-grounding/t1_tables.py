#!/usr/bin/env python3.12
"""Pivots of `t1-union.json` for the memo: per generation x scale x tier, each stratum's
within/count, median web/native and A (the median |log((web + code) / (native + code))|, W45's
aggregate), non-holdout members by pose and pooled; holdout members in their own table.

    python3.12 -B t1_tables.py > t1-tables.md
"""
import json
import statistics
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
d = json.loads((HERE / "t1-union.json").read_text())
cells = d["cells"]
ORDER = ["light 0.5", "dark 0.5", "light 0.25", "dark 0.25"]


def short(p):
    return p.replace("apple-macos-27.0-", "").replace("-standard", "").replace("-glass0.25", "").replace("-glass0.5", "")


def cell(group):
    if not group:
        return "—"
    within = sum(c["readFidelity"] == "within" for c in group)
    ratios = [c["readRatio"] for c in group if c["readRatio"] is not None]
    a = statistics.median(c["readLogError"] for c in group)
    return f"{within}/{len(group)} ×{statistics.median(ratios):.2f} A {a:.2f}"


def table(select, title, poses):
    print(f"\n#### {title}\n")
    print("| generation | profile | tier | pose | F | T | C | P | all |")
    print("|---|---|---|---|---|---|---|---|---|")
    keys = sorted({(c["generation"], c["profile"], c["tier"]) for c in cells if select(c)},
                  key=lambda k: (ORDER.index(k[0]), "-2x-" in k[1], "standard" not in k[1], k[1], k[2] != "webgpu"))
    for g, p, t in keys:
        for pose in poses:
            mine = [c for c in cells if select(c) and (c["generation"], c["profile"], c["tier"]) == (g, p, t)
                    and (pose == "both" or c["pose"] == pose)]
            if not mine:
                continue
            by = defaultdict(list)
            for c in mine:
                by[c["stratum"]].append(c)
            print(f"| {g} | {short(p)} | {t} | {pose} | " + " | ".join(cell(by[s]) for s in "FTCP")
                  + f" | {cell(mine)} |")


print("Cell format: within/count, median web/native ratio, A. T reads T1-fine; F, C, P read T1.")
table(lambda c: c["partition"] != "holdout", "Non-holdout members (calibration, validation, recorded, probe; "
      "light 0.25's twelve W44 referees included, spent at read 7)", ("rest", "inactive", "both"))
table(lambda c: c["partition"] == "holdout", "Holdout members (published rows; SPENT, never a fitting input)",
      ("both",))


def condensed(path):
    """The memo's table: standard profiles, WebGPU by pose and pooled, CSS pooled, non-holdout;
    accessibility profiles and the holdout column stay in the full tables above."""
    import contextlib
    import io
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        print("| generation | scale | tier | pose | F | T | C | P | all |")
        print("|---|---|---|---|---|---|---|---|---|")
        for g in ORDER:
            for scale in ("1x", "2x"):
                for tier, poses in (("webgpu", ("rest", "inactive", "both")), ("css", ("both",))):
                    for pose in poses:
                        mine = [c for c in cells if c["generation"] == g and f"-{scale}-" in c["profile"]
                                and "-standard-" in c["profile"] and c["tier"] == tier
                                and c["partition"] != "holdout" and (pose == "both" or c["pose"] == pose)]
                        if not mine:
                            continue
                        by = defaultdict(list)
                        for c in mine:
                            by[c["stratum"]].append(c)
                        print(f"| {g} | {scale} | {tier} | {pose} | " + " | ".join(cell(by[s]) for s in "FTCP")
                              + f" | {cell(mine)} |")
    (HERE / path).write_text(buf.getvalue())


condensed("t1-tables-memo.md")
