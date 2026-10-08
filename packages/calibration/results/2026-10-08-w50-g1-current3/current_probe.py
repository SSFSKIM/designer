"""Source-only exercise for DL5h recovery and identical all-phase repeat policy."""
from pathlib import Path
import sys
import types

HERE=Path(__file__).resolve().parent


def source(path,name):
    module=types.ModuleType(name);module.__file__=str(path);sys.modules[name]=module
    exec(compile(path.read_bytes(),str(path),'exec',dont_inherit=True),module.__dict__)
    return module


for name in ('dispatch','guard','admission','recovery','retained'):
    source(HERE/'execution'/f'{name}.py',f'w50_current3_probe_{name}')
router=source(HERE/'current_router.py','w50_current3_probe_router')
if router.source_probe()!={'status':'SOURCE_ONLY'}:raise ValueError('Recovery probe read measured evidence')
