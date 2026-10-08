"""Source-only exercise for the immutable current-material instrument.

No capture batch, image, role export, census observation or measured reference is read.
The original G0 collector discovers this graph; the G1 guard then re-executes it under
that exact prospective allowlist before the current-only root can be sealed.
"""
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent


def source(path, name):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(path.read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


for name in ('dispatch', 'guard', 'admission'):
    source(HERE/'execution'/f'{name}.py', f'w50_current_probe_{name}')
router = source(HERE/'current_router.py', 'w50_current_probe_router')
if router.source_probe() != {'status': 'SOURCE_ONLY'}:
    raise ValueError('Current adapter probe did not remain source-only')
