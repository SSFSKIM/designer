"""Canonical reference closure probe: synthetic numerical arrays only, no batch/source reads."""
from pathlib import Path
import types

path = Path(__file__).resolve().with_name('run.py')
entry = types.ModuleType('w50_reference_dry_entry'); entry.__file__ = str(path)
exec(compile(path.read_bytes(), str(path), 'exec', dont_inherit=True), entry.__dict__)
entry.dry_exercise()
