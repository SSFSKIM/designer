"""LIVE owner role: exposure-only owner evidence over the complete same-candidate union.

evaluate(context, captures, config) runs only in the dispatcher's analysis stage, under the
exclusive full-union analysis marker held by this process and lease (DL5k: no analytical read
before it). It admits the root-registered w50-owner-candidate-config-1 pin and delegates to
owner-candidate/live.py, which binds the logical exposure claim, the same-candidate gate,
the frozen intrinsic records and the separately exercised Node closure, and whose snapshot
carries the execution claim. The result is {report, snapshot}: metric evidence for the full
judge, never a PASS/NEITHER (DL4, DL5d-DL5e).
"""
from pathlib import Path
import types

HERE = Path(__file__).resolve().parent
OWNER = HERE.parent/'owner-candidate/live.py'
SCHEMA = 'w50-owner-candidate-config-1'


def _source(path, name):
    module = types.ModuleType(name); module.__file__ = str(path)
    exec(compile(Path(path).read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


C = _source(HERE/'common.py', 'w50_live_owner_common')


def evaluate(context, captures, config):
    live = C.dispatcher(context, 'analysis')
    C.execution_claim(context, live)
    if context.get('phase') != 'exposure' or context['batch'].get('phase') != 'exposure':
        raise ValueError('Candidate owner evidence is exposure-only; the gate keeps owners pending')
    C.registered(context, live, config, SCHEMA)
    result = C.source(OWNER, 'w50_live_role_owner_candidate').evaluate(context, captures, config)
    live.require_context(context)
    if not isinstance(result, dict) or set(result) != {'report', 'snapshot'}:
        raise ValueError('Owner seam did not return {report, snapshot}')
    return result


def source_probe():
    """Source-only: the role's in-process Python. The Node/edge closure is exercised separately."""
    C.source(HERE/'common.py', 'w50_live_owner_probe_common')
    C.source(OWNER, 'w50_live_owner_probe_candidate')
    return {'status': 'SOURCE_ONLY'}
