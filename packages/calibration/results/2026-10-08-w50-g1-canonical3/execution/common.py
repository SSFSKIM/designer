"""Source-only reuse of immutable dispatcher mechanics, never its phase authority."""
from pathlib import Path
import sys
import types

HERE=Path(__file__).resolve().parent
PRIOR=HERE.parents[1]/'2026-10-08-w50-g1-current3'

def source(path,name):
    module=types.ModuleType(name);module.__file__=str(path)
    sys.modules[name]=module
    exec(compile(path.read_bytes(),str(path),'exec',dont_inherit=True),module.__dict__)
    return module

D=source(PRIOR/'execution/dispatch.py','w50_canonical3_immutable_mechanics')
sha,load,pin,checked,sealed=D.sha,D.load,D.pin,D.checked,D.sealed
write_once,write_sealed=D.write_once,D.write_sealed
