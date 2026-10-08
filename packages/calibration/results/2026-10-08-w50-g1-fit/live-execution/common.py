"""Source-only access to the immutable original numerical/admission machinery."""
from pathlib import Path
import sys
import types
HERE=Path(__file__).resolve().parent
FIT=HERE.parent
CURRENT3=FIT.parent/'2026-10-08-w50-g1-current3'
CANONICAL3=FIT.parent/'2026-10-08-w50-g1-canonical3'

def source(path,name):
    m=types.ModuleType(name);m.__file__=str(path);sys.modules[name]=m
    exec(compile(Path(path).read_bytes(),str(path),'exec',dont_inherit=True),m.__dict__)
    return m

D=source(CURRENT3/'execution/dispatch.py','w50_live_immutable_mechanics')
