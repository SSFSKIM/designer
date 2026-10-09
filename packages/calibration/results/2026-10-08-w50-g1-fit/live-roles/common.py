"""Shared mechanics of the LIVE role components; no capability is granted here.

Every entry first requires the registered dispatcher's genuine context for the stage the role
is called in, so a caller-built or copied context refuses before any file is read. LIVE issues
render admission only to a remaining capture member (capture stage); qualification and analysis
read already-written members through require_read_admission/resolve_capture_run. The immutable
DL5h helpers were written for the whole-batch dispatcher and authenticate through render
admission, so a non-capture stage replays a retained pair through the root-bound helper's own
archived replay and the transports' pure report validators instead (the current-analysis
precedent), never through a widened render capability.

Sources are compiled from their bytes, as the surrounding modules do, so the prospective import
guard sees every executed file.
"""
import hashlib
import json
import os
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
FIT = HERE.parent
CURRENT3 = FIT.parent/'2026-10-08-w50-g1-current3'
KEY = ('profile', 'renderer', 'scene', 'statistic')


def source(path, name):
    module = types.ModuleType(name); module.__file__ = str(path)
    exec(compile(Path(path).read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pin(path):
    """The journal's absolute content pin (lifecycle.pin)."""
    path = Path(path).resolve()
    return {'path': str(path), 'sha256': sha(path)}


def read(path):
    def invalid(value): raise ValueError('Nonfinite JSON: '+value)
    return json.loads(Path(path).read_text(), parse_constant=invalid)


def dispatcher(context, *stages):
    """The registered LIVE dispatcher, after it authenticates this exact context and lease."""
    live = sys.modules.get('w50_g1_dispatch')
    if live is None: raise ValueError('No registered LIVE dispatcher capability')
    live.require_context(context)
    if context.get('stage') not in stages: raise ValueError('Role called outside its LIVE stage')
    return live


def registered(context, live, item, schema):
    """A role config: a root input and a context input, read through the dispatcher's own pin check."""
    root = live.sealed(context['executionRoot'])
    if item not in root['inputs'] or item not in context['inputs']:
        raise ValueError('Role config is not a prospective root input')
    document = live.load(live.checked(context['repo'], item))
    if document.get('schema') != schema: raise ValueError('Unknown role config schema')
    return root, document


def execution_claim(context, live):
    """The attempt, reconciliation or analysis claim this context names, held by THIS process/lease.

    require_context already rechecked the claim bytes; this binds its content to the logical
    phase and to the process that is calling, so evidence a role writes names a genuine claim.
    """
    item = context['executionClaim']; path = Path(item['path'])
    home = Path(context['contract']+'.phase')
    claim = read(path)
    if (claim.get('logicalContract') != pin(context['contract']) or claim.get('pid') != os.getpid()
            or claim.get('gpuLease') != live._LEASE['token'] or not path.is_relative_to(home)):
        raise ValueError('Execution claim is not this process and lease on this logical phase')
    stage = context['stage']
    if stage == 'analysis':
        if (path != home/'analysis.started.json' or claim.get('schema') != 'w50-live-analysis-claim-1'
                or claim.get('output') != context['output']):
            raise ValueError('Analysis requires the exclusive full-union analysis marker')
    elif claim.get('schema') == 'w50-live-reconciliation-claim-1':
        if stage != 'qualification' or path.name != 'started.json':
            raise ValueError('A reconciliation claim admits only qualification')
    elif (path.name != 'started.json' or path.parent.parent != home/'attempts'
            or claim.get('output') != context['output']):
        raise ValueError('Capture stages require their own attempt claim')
    return claim


def admit_run(context, live, member):
    """Stage-appropriate authority over one member's own derived run."""
    current = member['lane'] == 'current'
    if context['stage'] == 'capture': live.require_render_admission(context, member['run'], current=current)
    else: live.require_read_admission(context, member['run'], current=current)
    return member['run']


_REPEAT = {}


def _repeat_binding(context, live):
    """Helper, config and inventory, verified once per dispatcher context (one stage of one
    invocation): an analysis or reconciliation reads every member under one context."""
    if _REPEAT.get('context') is context: return _REPEAT['value']
    root = live.sealed(context['executionRoot'])
    binding = root.get('repeatAdmission')
    if not binding or binding != context.get('repeatAdmission') or binding['config'] not in context['inputs']:
        raise ValueError('Repeat helper/config is not the execution-root binding')
    helper = source(live.checked(context['repo'], binding['entrypoint']), 'w50_live_role_repeat')
    config = live.load(live.checked(context['repo'], binding['config']))
    if config.get('schema') != 'w50-repeat-config-1' or config.get('references') != root['references']:
        raise ValueError('Repeat membership is not the original declared reference set')
    inventory = live.load(live.checked(context['repo'], config['references']))
    _REPEAT.clear(); _REPEAT.update(context=context, value=(helper, config, inventory))
    return helper, config, inventory


def repeat_authority(context, live, record):
    """The root-bound DL5h helper/config and the record's original declared rows (helper.authority
    without its render admission)."""
    helper, config, inventory = _repeat_binding(context, live)
    rows = [r for r in inventory['cells'] if all(r[k] == record[k] for k in KEY[:3])]
    if not rows or len({r['statistic'] for r in rows}) != len(rows):
        raise ValueError('Repeat member lacks unique original declared statistics')
    if context['phase'] != 'exposure' and any(r['role'] in ('blind', 'historical-prediction-check') for r in rows):
        raise ValueError('Withheld repeat sources are exposure-only')
    return helper, config, rows, inventory


def validate_pages(context, helper, transports, run, record, retained, inventory):
    """Both retained pages through the transports' pure source validators: the exact checks of
    the transports' validate_pair_reports and helper.validate_reports, minus their render admission."""
    envelope, pages = retained['envelope'], retained['pages']
    if envelope.get('page') != pages[0]: raise ValueError('First page differs from reading envelope')
    current = record['lane'] == 'current'; web = transports['w50']
    if run['sceneSource'] == 'w50':
        plan = web.scene_plan(run, context['phase'])
        spec = next(s for s in plan['scenes'] if s['scene'] == record['scene'])
        candidate = web.candidate_info(run['candidate'], plan['position'], current=current)
        endpoint = candidate['endpoints'][f'{spec["pose"]}.dark']
        mode = {**candidate['endpoints']['active.dark']['patch'], **endpoint['patch']}.get('backdropToneAbscissa', 'source')
        mode = 'silhouette' if isinstance(mode, dict) else mode
        guard = source(web.G0/'audit/numerical_guard.py', 'w50_live_role_pair_numerical')
        for page in pages:
            for argument in web.validate_report({**envelope, 'page': page}, run, endpoint,
                                                abscissa=mode, phase=context['phase']):
                guard.validate_tone_values(argument)
        return
    if run['sceneSource'] != 'canonical': raise ValueError('Unknown repeat scene source')
    canonical = transports['canonical']
    plan = canonical.scene_plan(run, context['phase'])
    scene = next(s for s in plan['scenes'] if s['id'] == record['scene'])
    candidate = web.candidate_info(run['candidate'], plan['position'], current=current)
    pose = 'receded' if scene['state'] == 'inactive' else 'active'
    endpoint = candidate['endpoints'][f'{pose}.{plan["scheme"]}']
    for page in pages: canonical.validate_report({**envelope, 'page': page}, run, plan, scene, endpoint)
    if '|'.join(record[k] for k in KEY[:3]) not in helper.S.M.N.required_arguments(inventory): return
    analysis = source(helper.S.FIT/'current-analysis/analysis.py', 'w50_live_role_canonical_argument')
    spec = dict(scene=scene['id'], pose=pose, role=scene['fixtureSet'], background=scene['background'],
                component=plan['components'][scene['component']])
    dark = candidate['endpoints'][pose+'.dark']
    mode = {**candidate['endpoints']['active.dark']['patch'], **dark['patch']}.get('backdropToneAbscissa', 'source')
    mode = 'silhouette' if isinstance(mode, dict) else mode
    for page in pages: analysis.canonical_argument(page, run, plan, spec, mode)


def archived_pair(context, live, run, record, transports):
    """helper.verify_receipt with validate_reports replaced by validate_pages: the retained pair,
    both reports, the member-owned proof and its exact original statistic band, never a new draw."""
    helper, config, rows, inventory = repeat_authority(context, live, record)
    if not record.get('repeatPair') or not record.get('repeatAdmission'):
        raise ValueError('A live member needs both content-pinned repeat witnesses')
    retained = helper.read_pair(context, run, record, record['repeatPair'])
    validate_pages(context, helper, transports, run, record, retained, inventory)
    proof = helper.retained_proof(context['output'], run, record, retained)
    binding = helper.receipt_binding(context, run, record, config, rows, needs_statistics=not retained['identical'])
    helper.verify_pair_semantics(binding, run, record, retained, proof)
    live.require_context(context)
    return proof
