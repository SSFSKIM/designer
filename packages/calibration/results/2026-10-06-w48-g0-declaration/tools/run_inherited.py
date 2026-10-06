#!/usr/bin/env python3.12
"""W48 G0 (b): run one of W47's tool test modules, by its path, UNDER W48's bindings (charter clause 2).

    python3.12 -B tools/run_inherited.py <path under W47's root, e.g. cuts/test_rule.py> [--out FILE]

`inherit` is imported first, so the module named `bindings` every W47 tool and test imports is W48's
(`inherit.py`); the test module is then loaded from W47's directory with its own directory first on
`sys.path`, exactly as `python -m unittest` from that directory would, and run verbosely. An audit hook
refuses any write, create, rename or remove under W47's evidence directory for the whole run, so an
inherited test that would write beside itself fails loudly instead of touching W47's committed files.
Each module runs in its own process (`run_all`), so module caches (`fit`, `bed`, `rule`) never cross.
The transcript is what `unittest` prints; a module's failures under W48's bindings are triaged in
`tools/inherited.json` (which W48 test replaces each W47 assertion of a W47 binding).
"""
from __future__ import annotations

import fcntl
import importlib.util
import io
import os
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
G0 = HERE.parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(G0))
import inherit  # noqa: E402  (W48's bindings installed as `bindings` before any W47 module)

W = inherit.W
_DENIED = os.path.realpath(str(W.W47_G0))
_FLAGS = os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND


def _under(path, dir_fd=None) -> bool:
    """`path` (relative to `dir_fd` when one is given, as `shutil.rmtree` passes it) inside W47's root."""
    if not isinstance(path, (str, bytes, os.PathLike)):
        return False
    raw = os.fsdecode(path)
    if isinstance(dir_fd, int) and not os.path.isabs(raw):
        raw = os.path.join(fcntl.fcntl(dir_fd, fcntl.F_GETPATH, b"\0" * 1024).rstrip(b"\0").decode(), raw)
    p = os.path.realpath(raw)
    return p == _DENIED or p.startswith(_DENIED + "/")


def _audit(event, args):
    if event == "open":
        path, mode, flags = args
        writes = (isinstance(mode, str) and any(c in mode for c in "wax+")) or (
            isinstance(flags, int) and flags & _FLAGS)
        if writes and _under(path):
            raise PermissionError(f"run_inherited: a write into W47's directory refused: {path}")
    elif event in ("os.mkdir", "os.remove", "os.rmdir", "os.truncate"):
        if args and _under(args[0], args[-1] if event != "os.truncate" else None):
            raise PermissionError(f"run_inherited: {event} in W47's directory refused: {args[0]}")
    elif event in ("os.rename", "os.link", "os.symlink"):
        if _under(args[0], args[2] if len(args) > 2 else None) or _under(args[1], args[3] if len(args) > 3 else None):
            raise PermissionError(f"run_inherited: {event} in W47's directory refused: {args[:2]}")


def run(rel: str) -> tuple[int, str]:
    path = (W.W47_G0 / rel).resolve()
    if W.W47_G0.resolve() not in path.parents or not path.name.startswith("test_"):
        raise SystemExit(f"run_inherited: {rel} is not a W47 test module")
    sys.addaudithook(_audit)
    sys.path.insert(0, str(path.parent))
    os.chdir(path.parent)
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[path.stem] = module
    spec.loader.exec_module(module)
    buf = io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromModule(module)
    result = unittest.TextTestRunner(stream=buf, verbosity=2).run(suite)
    head = (f"W48 G0 (b): W47's {rel} run under W48's bindings ({W.CHARTER_PIN}); "
            f"bindings module {sys.modules['bindings'].__file__}\n")
    return (0 if result.wasSuccessful() else 1), head + buf.getvalue()


if __name__ == "__main__":
    args = sys.argv[1:]
    out = None
    if "--out" in args:
        i = args.index("--out")
        out = Path(args[i + 1]).resolve()
        del args[i:i + 2]
    code, text = run(args[0])
    if out is not None:
        out.write_text(text)
    print(text)
    sys.exit(code)
