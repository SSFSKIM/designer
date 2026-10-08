"""Synthetic closure probe; the prospective bootstrap path is selected explicitly by discover."""
import os
from pathlib import Path
import types

HERE = Path(__file__).resolve().parent
entry = types.ModuleType('w50_completed_current_probe_entry')
entry.__file__ = str(HERE/'run.py')
exec(compile((HERE/'run.py').read_bytes(), str(HERE/'run.py'), 'exec', dont_inherit=True), entry.__dict__)
entry.source_probe(Path(os.environ['W50_CURRENT_ANALYSIS_BOOTSTRAP']),
                   Path(os.environ['W50_CURRENT_ANALYSIS_PROBE']))
