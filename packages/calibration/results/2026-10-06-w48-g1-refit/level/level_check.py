#!/usr/bin/env python3.12
"""W48 G1: the level check (W47's `level/level.py check`, inherited by path under W48's bindings) on a fit
point's renders, per scale on the renderer that measures the point there (charter Design "The targets and
the predictions": the level check's excesses read beside L1 at every stage and in the gate report,
ungated; Decision Log 5).

    python3.12 -B level_check.py LABEL     writes <LABEL>-<s>x.json per scale beside this file
"""
from __future__ import annotations

import json
import runpy
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
G1 = HERE.parent
G0 = G1.parent / "2026-10-06-w48-g0-declaration"
sys.path.insert(0, str(G0))
import inherit  # noqa: E402

W = inherit.W
SCRATCH = W.FIT_SCRATCH

if __name__ == "__main__" and len(sys.argv) == 2:
    label = sys.argv[1]
    summary = json.loads((W.G1_FIT / "candidates" / label / "summary.json").read_text())
    for scale in (1, 2):
        renderer = summary["renderers"][f"{scale}x"]["label"]
        mats = sorted((SCRATCH / renderer).glob(f"*-{scale}x/matrix.json"))
        out = HERE / f"{label}-{scale}x.json"
        argv = [sys.executable, "-B", "-c",
                f"import sys; sys.path.insert(0, {str(G0)!r}); import inherit, runpy; "
                f"sys.argv = [{str(W.W47_G0 / 'level' / 'level.py')!r}] + sys.argv[1:]; "
                f"runpy.run_path(sys.argv[0], run_name='__main__')",
                "check", "--candidate", str(W.G1_FIT / "candidates" / renderer),
                *[a for m in mats for a in ("--matrix", str(m))],
                "--captures", str(SCRATCH / renderer / f"merged-captures-{scale}x"), "--out", str(out)]
        got = subprocess.run(argv, cwd=W.W47_G0 / "level", capture_output=True, text=True)
        print(scale, "exit", got.returncode, got.stdout[-600:], got.stderr[-800:])
