"""Source-only successor closure exercise. No authority, config, capture or reading opens."""
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent


def source(path, name):
    module = types.ModuleType(name); module.__file__ = str(path); sys.modules[name] = module
    exec(compile(Path(path).read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


def exercise():
    source(HERE.parent/'live-roles/probe.py', 'w50_analysis2_original_source_probe')
    for name in ('authority', 'witness', 'run', 'seal', 'reads'):
        source(HERE/(name+'.py'), 'w50_analysis2_probe_'+name)
    return {'status': 'SOURCE_ONLY'}


exercise()
