#!/usr/bin/env python3.12
"""W48 G1: W47's eye sheets (`sheets/sheets.py`, inherited by path under W48's bindings): Apple 0.25 |
vitrea d0219cd684bf | vitrea W48 | the three gain-lifted differences, over the dark stage's rows (both
tiers), with the gate cut's T1 states. Before the exposure the non-withheld rows only (the tool refuses a
withheld row); `--whole` after read 8.

    python3.12 -B run.py OUT_DIR [--whole] [--cut CUT.json]
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "2026-10-06-w48-g0-declaration"))
import inherit  # noqa: E402

W = inherit.W
sheets = inherit.tool("sheets/sheets.py", "sheets")
args = ["--stage", str(W.STAGE / "matrix.json"), "--stage-captures", str(W.CAL / "web-captures"),
        "--out", sys.argv[1]]
if "--cut" in sys.argv:
    args += ["--cut", sys.argv[sys.argv.index("--cut") + 1]]
if "--whole" in sys.argv:
    args.append("--whole")
sys.exit(sheets.main(args))
