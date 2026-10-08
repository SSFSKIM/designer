"""Source-only prospective probe; composition selection is metadata, never result admission."""
import json
import os
from pathlib import Path
import types

HERE=Path(__file__).resolve().parent
entry=types.ModuleType('w50_composed_probe_entry');entry.__file__=str(HERE/'run.py')
exec(compile((HERE/'run.py').read_bytes(),str(HERE/'run.py'),'exec',dont_inherit=True),entry.__dict__)
value=os.environ.get('W50_COMPOSED_CURRENT_COMPOSITION')
entry.source_probe(None if value is None else json.loads(value))
