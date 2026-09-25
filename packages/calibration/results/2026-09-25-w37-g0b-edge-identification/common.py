"""Load unchanged G0 siblings without confusing identically named modules."""
import importlib.util
import sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
G0=HERE.parent/'2026-09-25-w37-g0-edge-identification'
ROOT=HERE.parents[3]
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module
oldlaw=load('g0_law',G0/'law.py')
previous=sys.modules.get('law');sys.modules['law']=oldlaw
try:
    oldidentify=load('g0_identify',G0/'identify.py')
    oldcanonical=load('g0_canonical',G0/'canonical.py')
finally:
    if previous is None:sys.modules.pop('law',None)
    else:sys.modules['law']=previous
edge=oldlaw.edge
