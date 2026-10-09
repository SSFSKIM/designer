"""W50 G1 LIVE measurement role: measurement/phase.py's measure_phase, in the analysis stage only.

evaluate(context, captures, config) is called by the registered LIVE dispatcher once per
logical fit/gate/exposure phase, after its exclusive full-union analysis marker, with the
complete union's original member records. config is the root-pinned
w50-phase-measurement-inputs-1 document (live-roles/measurement-config.json). The result is
keyed measurement EVIDENCE that names the analysis claim it was read under; it is never a
verdict. The dispatcher quarantines it (DL5k); nothing here prints or formats a value.

Sources are compiled from their bytes so prospective import sealing sees every executed file.
"""
from pathlib import Path
import types

HERE = Path(__file__).resolve().parent


def source(path, name):
    module = types.ModuleType(name); module.__file__ = str(path)
    exec(compile(Path(path).read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


L = source(HERE/'common.py', 'w50_live_measurement_common')
P = source(HERE.parent/'measurement/phase.py', 'w50_live_measurement_phase')


def evaluate(context, captures, config):
    live = L.dispatcher(context, 'analysis')
    # The exclusive full-union marker, held by this process and lease, before any input is read.
    L.execution_claim(context, live)
    return P.measure_phase(context, captures, config)


def source_probe():
    """Every Python source the role executes, without a context, config, capture or role data."""
    if P.source_probe() != {'status': 'SOURCE_ONLY'}:
        raise ValueError('Measurement source exercise must remain evidence-free')
    return {'status': 'SOURCE_ONLY'}
