"""W48 G0 (b): W47's tools inherited BY PATH under W48's bindings (charter clause 2).

    import inherit                 # installs W48's bindings as the module `bindings`
    fit = inherit.tool("fit/fit.py")

W47's tools bind everything through `import bindings as W` after putting W47's evidence root first on
`sys.path`. Python resolves that import from `sys.modules` when a module named `bindings` is already
loaded, so importing THIS file first (it imports W48's `bindings.py` under that name) makes every
`W.*` an inherited tool reads W48's: its charter pin, parts, draft, protocol, G1, scratch, stages,
lock and refusals. The tools' own files are W47's bytes, pinned in `bindings.INHERITED`, and
`tool()` refuses a moved one before it loads.

Two consequences, stated so a caller does not trip on them:
- `inherit` must be imported before any W47 tool and before anything else named `bindings`; it refuses
  if another `bindings` module is already loaded.
- An inherited tool inserts W47's root on `sys.path`, so a later bare `import declare` (or `assemble`)
  would find W47's file. W48's own modules are therefore loaded by path (`own()`), never by a bare name
  after a W47 tool has been imported.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
_loaded = sys.modules.get("bindings")
if _loaded is not None and Path(getattr(_loaded, "__file__", "")).resolve() != HERE / "bindings.py":
    raise SystemExit(f"inherit: another `bindings` is loaded ({_loaded.__file__}); W48's must be first")
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
import bindings as W  # noqa: E402

W.require_inherited()


def _load(name: str, path: Path):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# A module-level constant an inherited tool compares W48's bytes against by its W47 value, re-bound after the
# tool loads (each is read at call time, so the rebinding holds for every call). `stage/stage.py` refuses a sealed
# document whose `recordedBy` is not its SEALED_BY; W48's seal (`seal/seal.ts`, W48's copy) records "W48 G1".
# Only these names are re-bound; everything else in the tool is W47's bytes (`bindings.INHERITED`).
REBIND = {"stage/stage.py": {"SEALED_BY": "W48 G1"}}


def tool(rel: str, name: str | None = None):
    """A W47 tool by its path under W47's root, loaded under W48's bindings (pinned, `INHERITED`). A tool
    whose siblings import it by its bare name (`import fit`, `import rule`) is registered under that name,
    so the sibling gets this very module."""
    path = W.W47_G0 / rel
    if path not in W.INHERITED:
        raise W.Refusal(f"inherit: {rel} is not a tool W48 inherits (bindings.INHERITED)")
    W.require_inherited()
    if str(path.parent) not in sys.path:
        sys.path.insert(0, str(path.parent))
    module = _load(name or path.stem, path)
    for key, value in REBIND.get(rel, {}).items():
        if not hasattr(module, key):
            raise W.Refusal(f"inherit: {rel} has no {key} to re-bind")
        setattr(module, key, value)
    return module


def own(rel: str, name: str | None = None):
    """A W48 module by its path under this root (never by a bare name, which W47's root may shadow)."""
    path = HERE / rel
    return _load(name or f"w48_{path.stem.replace('-', '_')}", path)
