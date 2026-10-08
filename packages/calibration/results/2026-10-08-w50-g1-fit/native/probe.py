"""Source-closure dry probe. It cannot read a batch, native export or measured statistic.

The unchanged G0 closure collector audits these dynamic source compilations, including
ModuleType modules absent from sys.modules. All pixels below are produced by dry_exercise.
"""
from pathlib import Path
import types

HERE = Path(__file__).resolve().parent
ENTRY = HERE/'run.py'
reader_entry = types.ModuleType('w50_native_probe_entry')
reader_entry.__file__ = str(ENTRY)
exec(compile(ENTRY.read_bytes(), str(ENTRY), 'exec', dont_inherit=True), reader_entry.__dict__)
reader_entry.dry_exercise()
