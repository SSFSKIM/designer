"""Source-only core probe; a real root's composite probe also exercises ALL real roles.

This probe reads no root, checkpoint, capture, native report or material document. It
cannot substitute for the final assembled component closure or independent review.
"""
from pathlib import Path
import sys
import types
HERE=Path(__file__).resolve().parent

def source(path,name):
    m=types.ModuleType(name);m.__file__=str(path);sys.modules[name]=m
    exec(compile(path.read_bytes(),str(path),'exec',dont_inherit=True),m.__dict__)
    return m


def source_probe():
    source(HERE.parent.parent/'2026-10-08-w50-g1-canonical3/current_probe.py','w50_live_original_core_probe')
    for name in ('guard','common','authority','dispatch','lifecycle','quarantine',
                 'admission','prefit','native_evidence','owner_evidence'):
        source(HERE/(name+'.py'),'w50_live_probe_'+name)
    return {'status':'SOURCE_ONLY'}

source_probe()
