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

# The inherited tool draws "W47" in its column names, page headers and per-row lines (its bytes are W47's,
# pinned); the column it labels is W48's. Every string the tool draws goes through ImageDraw.Draw(...).text,
# so the label is corrected there, at draw time, and nothing else about the sheets changes (§5.213 Surprises).
_Draw = sheets.ImageDraw.Draw


class _W48Draw:
    def __init__(self, image, *a, **k):
        self._d = _Draw(image, *a, **k)

    def text(self, xy, text, *a, **k):
        return self._d.text(xy, text.replace("W47", "W48"), *a, **k)

    def __getattr__(self, name):
        return getattr(self._d, name)


sheets.ImageDraw.Draw = _W48Draw
import os  # noqa: E402
if os.environ.get("W48_G1_ROUND", "first") == "dl9":
    W.STAGE = W.SCRATCH / "g1-stage-dark-dl9"
    captures = W.STAGE / "web-captures"
else:
    captures = W.SCRATCH / "g1-stage-dark" / "web-captures"     # moved there from the worktree's tree
args = ["--stage", str(W.STAGE / "matrix.json"), "--stage-captures", str(captures),
        "--out", sys.argv[1]]
if "--cut" in sys.argv:
    args += ["--cut", sys.argv[sys.argv.index("--cut") + 1]]
if "--whole" in sys.argv:
    args.append("--whole")
sys.exit(sheets.main(args))
