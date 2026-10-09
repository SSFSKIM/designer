"""Source-only closure exercise for DL5s. No metadata, gate payload or output opens."""
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent


def source(path, name):
    module = types.ModuleType(name); module.__file__ = str(path); sys.modules[name] = module
    exec(compile(Path(path).read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


def exercise():
    source(HERE/'probe.py', 'w50_attempt2_original_probe')
    for name in ('historical', 'attempt2_authority', 'attempt2_preflight', 'attempt2_run', 'attempt2_seal'):
        source(HERE/(name+'.py'), 'w50_attempt2_probe_'+name)
    return {'status': 'SOURCE_ONLY'}


exercise()
