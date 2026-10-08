"""Exercise canonical recovery and immutable validators without reading evidence."""
from pathlib import Path
import sys
import types
HERE=Path(__file__).resolve().parent

def source(path,name):
    m=types.ModuleType(name);m.__file__=str(path);sys.modules[name]=m
    exec(compile(path.read_bytes(),str(path),'exec',dont_inherit=True),m.__dict__)
    return m

# Every old exercised Python source stays pinned; no old authority is executed.
source(HERE.parent/'2026-10-08-w50-g1-current3/current_probe.py','w50_canonical3_original_probe')
for name in ('common','dispatch','admission','recovery','evidence','composition'):
    source(HERE/'execution'/f'{name}.py',f'w50_canonical3_probe_{name}')
