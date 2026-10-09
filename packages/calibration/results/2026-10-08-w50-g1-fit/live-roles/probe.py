"""Composite LIVE root probe: the dispatcher core and every registered component, source-only.

The sealed closure is exactly what this probe executes (live-execution/guard.py discover), and
the permanent guard refuses any later execution of a repository source outside it, so every
module a role executes at run time must be exercised here. Each component's own source_probe
covers its import graph with synthetic data; none reads a root, contract, batch, capture,
native read, owner or judge evidence, and none locates an archive.
"""
from pathlib import Path
import types

HERE = Path(__file__).resolve().parent
FIT = HERE.parent
COMPONENTS = (HERE/'capture.py', HERE/'native.py', HERE/'measurement.py', HERE/'owner.py',
              FIT/'judge/live.py', FIT/'judge/targets.py', FIT/'fit/live.py')
# The initializer is a separate pre-render entrypoint with no source_probe; it executes these.
INITIALIZER = (FIT/'fit/execution.py', FIT/'fit/inputs.py', FIT/'fit/uniform.py')
# Executed by the dispatcher itself at run time, not by a role: admission.validate_numerical
# loads G0's numerical referee (which loads numerical_guard.py) in every fit, gate and exposure
# attempt, and refuses unless both are in the closure.
DISPATCHER = (FIT.parent/'2026-10-08-w50-g0-declaration/audit/runner.py',)


def source(path, name):
    module = types.ModuleType(name); module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


def root_probe():
    source(FIT/'live-execution/probe.py', 'w50_live_root_probe_core')
    for index, path in enumerate(COMPONENTS):
        if source(path, f'w50_live_root_probe_{index}').source_probe() != {'status': 'SOURCE_ONLY'}:
            raise ValueError('A LIVE component probe did not remain source-only')
    for index, path in enumerate(INITIALIZER):
        source(path, f'w50_live_root_probe_initializer_{index}')
    for index, path in enumerate(DISPATCHER):
        source(path, f'w50_live_root_probe_dispatcher_{index}')
    return {'status': 'SOURCE_ONLY'}


root_probe()
