"""W48 G0 (b): a W47 test module, by path, as part of a W48 test module (charter clause 2).

A W48 test file that REPLACES some of an inherited W47 module's cases (the ones that assert a W47
binding, a W47 count or a W47 scratch location) loads the W47 module here, under W48's bindings
(`inherit`), and runs every OTHER case of it unchanged beside its own:

    import inherited_suite as S
    W47_TESTS = S.module("fit/test_fit.py", patch={})
    REPLACED = {"test_fit.Part2.test_other_waves_part_hashes_refuse": "the W48 message names W47"}
    def load_tests(loader, tests, pattern):
        return S.suite(loader, tests, W47_TESTS, REPLACED)

`patch` sets module attributes of the W47 test module before it runs (a scratch location only; never an
assertion). The same write denial as `run_inherited.py` holds for W47's directory while it runs.
"""
from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
G0 = HERE.parent
sys.dont_write_bytecode = True
if str(G0) not in sys.path:
    sys.path.insert(0, str(G0))
import inherit  # noqa: E402

sys.path.insert(0, str(HERE))
import run_inherited  # noqa: E402

W = inherit.W
_HOOKED = False


def module(rel: str, patch: dict | None = None, importing=None):
    """W47's test module `rel` (under W47's root), loaded by path under W48's bindings. `importing` is an
    optional context manager held only while the module (and what it imports) executes."""
    global _HOOKED
    path = (W.W47_G0 / rel).resolve()
    if W.W47_G0.resolve() not in path.parents or not path.name.startswith("test_"):
        raise SystemExit(f"inherited_suite: {rel} is not a W47 test module")
    if not _HOOKED:
        sys.addaudithook(run_inherited._audit)
        _HOOKED = True
    if str(path.parent) not in sys.path:
        sys.path.insert(0, str(path.parent))
    name = f"w47_{path.parent.name}_{path.stem}"
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    if importing is None:
        spec.loader.exec_module(mod)
    else:
        with importing:
            spec.loader.exec_module(mod)
    for key, value in (patch or {}).items():
        if not hasattr(mod, key):
            raise SystemExit(f"inherited_suite: {rel} has no {key} to patch")
        setattr(mod, key, value)
    return mod


def _cases(suite):
    for t in suite:
        if isinstance(t, unittest.TestSuite):
            yield from _cases(t)
        else:
            yield t


def suite(loader, own: unittest.TestSuite, mod, replaced: dict[str, str], only=None) -> unittest.TestSuite:
    """Every case of W47's `mod` except the `replaced` ones (by `Class.method`), then this module's own;
    with `only` (a set of class names), only those classes' cases are carried."""
    out = unittest.TestSuite()
    seen = set()
    for case in _cases(loader.loadTestsFromModule(mod)):
        key = f"{type(case).__name__}.{case._testMethodName}"
        if only is not None and type(case).__name__ not in only:
            continue
        if key in replaced:
            seen.add(key)
            continue
        out.addTest(case)
    missing = set(replaced) - seen
    if missing:
        raise SystemExit(f"inherited_suite: replaced cases not in {mod.__name__}: {sorted(missing)}")
    out.addTests(own)
    return out
