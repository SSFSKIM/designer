"""Run the unchanged W29 verifier against a scratch copy of its matrix input.

W39 G2 forbids CLI reads of authoritative matrix destinations. The verifier is
imported unchanged; only its MATRIX variable points at the byte-identical copy.
"""
import importlib.util
from pathlib import Path
import shutil
import tempfile

HERE = Path(__file__).resolve().parent
OLD = HERE.parent / '2026-09-16-w29-freeze' / 'freeze.py'
spec = importlib.util.spec_from_file_location('w29_freeze', OLD)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
with tempfile.TemporaryDirectory(prefix='w39-freeze-') as temp:
    copied = Path(temp) / 'matrix.json'
    shutil.copyfile(module.MATRIX, copied)
    module.MATRIX = copied
    raise SystemExit(module.main())
