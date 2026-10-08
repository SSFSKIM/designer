"""Source-only phase measurement exercise; no context, config, role data or captures are read."""
from pathlib import Path
import types

HERE = Path(__file__).resolve().parent
phase = types.ModuleType('w50_phase_measurement_probe')
phase.__file__ = str(HERE/'phase.py')
exec(compile(Path(phase.__file__).read_bytes(), phase.__file__, 'exec', dont_inherit=True), phase.__dict__)
if phase.source_probe() != {'status': 'SOURCE_ONLY'}:
    raise ValueError('Phase measurement source exercise must remain evidence-free')
