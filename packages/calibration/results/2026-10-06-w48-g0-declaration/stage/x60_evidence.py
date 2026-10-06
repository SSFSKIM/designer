#!/usr/bin/env python3.12
"""W48 G0 (b): X60 by evidence, with no render: W47's `stage/x60.py evidence`, inherited by path, run as
`__main__` in a process that imported `inherit` first, so its `bindings` is W48's (charter X60, X71).
It checks the light 0.25 documents against W48's snapshots, the frozen 0.5 generations and 26.5 rows, every
candidate under W48's candidate roots (none exist at G0: W48 builds no candidate before G1), and that no
capture tree under `~/vitrea-w48` holds a withheld cell. The trees it finds at G0 are the archive's
producer output and second copy (`~/vitrea-w48/archive/producer-out`, `~/vitrea-w48/archive-copy`):
W47's ladder cells only, none withheld (X69).

    python3.12 -B x60_evidence.py      (writes x60/evidence-g0.json and x60/evidence-g0.txt)
"""
from __future__ import annotations

import contextlib
import io
import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import inherit  # noqa: E402

W = inherit.W
OUT = HERE / "x60" / "evidence-g0.json"

if __name__ == "__main__":
    sys.argv = [str(W.W47_G0 / "stage" / "x60.py"), "evidence", "--out", str(OUT)]
    buf = io.StringIO()
    code = 0
    with contextlib.redirect_stdout(buf):
        try:
            runpy.run_path(sys.argv[0], run_name="__main__")
        except SystemExit as stop:
            code = stop.code or 0
    (OUT.parent / "evidence-g0.txt").write_text(buf.getvalue())
    print(buf.getvalue(), end="")
    sys.exit(code)
