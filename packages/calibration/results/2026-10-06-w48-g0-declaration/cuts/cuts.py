#!/usr/bin/env python3.12
"""W48 G0 (b): the launcher W48's bindings give as `CUTS / "cuts.py"` (charter clause 2; review P2).

W47's `fit/fit.py`, inherited unchanged, reads a scale's renders by running `W.CUTS / "cuts.py"` in a NEW
Python process. A new process does not carry `sys.modules["bindings"]`, so W47's `cuts.py` run there would
import W47's `bindings.py` and W47's refusals. This file installs W48's bindings first (`inherit`) and then
runs W47's `cuts/cuts.py` UNCHANGED as `__main__` (`bindings.CUTS_SOURCE`, pinned in `INHERITED`), so the
child process binds W48 exactly as the parent does. It adds no arithmetic.
"""
import runpy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import inherit  # noqa: E402

source = inherit.W.CUTS_SOURCE / "cuts.py"
inherit.W.require_inherited()
sys.argv[0] = str(source)
runpy.run_path(str(source), run_name="__main__")
