"""LIVE owner role: exposure-only owner evidence over the complete same-candidate union.

evaluate(context, captures, config) runs only in the dispatcher's analysis stage, under the
exclusive full-union analysis marker held by this process and lease (DL5k: no analytical read
before it). It admits the root-registered w50-owner-candidate-config-1 pin and delegates to
owner-candidate/live.py, which binds the logical exposure claim, the same-candidate gate,
the frozen intrinsic records and the separately exercised Node closure, and whose snapshot
carries the execution claim. The result is {report, snapshot}: metric evidence for the full
judge, never a PASS/NEITHER (DL4, DL5d-DL5e).

admit(context, config) is the same seam's metadata-only admission at LIVE's 'owner-admission'
stage (pre-seal review P1): at the exposure's creation, before the one-shot native marker and
before the analysis marker, so owner drift is an ordinary recoverable stop rather than an
analysis that ends with no result. It holds LIVE's require_owner_admission grant and runs
owner-candidate/live.preflight: every check evaluate makes before its snapshot, a hash of every
transitive owner evidence pin, the Node closure's source-only probe and the frozen engine's
reading of the batch's intrinsic records. No execution claim is required (at a creation none
exists) and nothing is written. The gate's creation admits it too (second pre-seal review P1):
the gate batch freezes the intrinsic records the exposure must reuse unchanged.
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


def admit(context, config):
    live = C.dispatcher(context, 'owner-admission')
    live.require_owner_admission(context)
    if context.get('phase') not in ('gate', 'exposure') or context['batch'].get('phase') != context['phase']:
        raise ValueError('Owner admission belongs to a gate or an exposure')
    C.registered(context, live, config, SCHEMA)
    result = C.source(OWNER, 'w50_live_role_owner_admission').preflight(context, config)
    live.require_context(context)
    if not isinstance(result, dict) or result.get('admitted') is not True:
        raise ValueError('Owner preflight did not admit')
    return {'admitted': True}


def source_probe():
    """Source-only: the role's in-process Python. The Node/edge closure is exercised separately."""
    C.source(HERE/'common.py', 'w50_live_owner_probe_common')
    C.source(OWNER, 'w50_live_owner_probe_candidate')
    return {'status': 'SOURCE_ONLY'}
