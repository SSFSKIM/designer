"""Prospective LIVE capture transport, not a fitter, measurement instrument or referee.

execute(context) admits only fit/gate/exposure through the registered dispatcher singleton.
Canonical and W50 NEWBED runs use CURRENT3's paired transports under DL5h in every phase;
NEWBED keeps DL5f's border-box host. Every candidate call receives the ORIGINAL context
and run, and complete repeat evidence passes through unchanged. Exposure baselines are only
dispatcher.baseline_run derivatives admitted
inside that same invocation, never another current lane or another lease.

W50 exposure runs bind one shared nativeExposureConfig input pin and their complete fixtures
mapping before the batch is fixed. The existing native admission and metadata-only planner
verify those mappings before the one-shot preparation; returned fixture metadata must match
again. A run must contain one pose because its immutable fixtures field names one pose tree.
No run/context field is supplied, substituted or repaired after admission.
"""
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
G1 = HERE.parent
CURRENT3 = G1.parent/'2026-10-08-w50-g1-current3'


def source(path, name):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


def adapters():
    return {'canonical': source(CURRENT3/'canonical/adapter.py', 'w50_live_canonical'),
            'w50': source(CURRENT3/'web/adapter.py', 'w50_live_newbed')}


def native_adapter():
    return source(G1/'exposure/prepare.py', 'w50_live_native_exposure')


def source_probe():
    """Exercise all source import branches without an invocation or native data locator.

    CURRENT3's source-only helper exercises paired transports, native authority metadata and
    synthetic repeat statistics, never current execution/recovery or measured native data.
    The native exposure helper likewise uses synthetic arrays without locating an archive.
    """
    paired = source(CURRENT3/'current_router.py', 'w50_live_paired_probe')
    if paired.source_probe() != {'status': 'SOURCE_ONLY'}:
        raise ValueError('Unexpected paired capture source probe result')
    native_adapter().source_probe()
    return {'status': 'SOURCE_ONLY'}


def qualified_exposure(context):
    """Check the dispatcher's existing qualified receipt; this grants no new capability."""
    report = context.get('gateReport') or {}
    pending = context['phaseDependencies'].get('pendingOwnerKeys')
    if (context.get('gateResult') is None or not isinstance(pending, list) or
            report.get('status') != 'PASS_EXPOSED_OWNER_PENDING' or
            report.get('ownerChecks') != 'PENDING_FULL_UNION' or
            report.get('pendingOwnerKeys') != pending or
            report.get('candidateSha256s') != sorted(p['sha256'] for p in context['batch']['cohort'])):
        raise ValueError('Exposure needs the same-candidate qualified gate with exact pending owners')


def fixture_keys(runs, adapter):
    keys = []
    for run in runs:
        plan = adapter.scene_plan(run, 'exposure')
        poses = {scene['pose'] for scene in plan['scenes']}
        if len(poses) != 1:
            raise ValueError('An immutable fixture run must contain exactly one pose')
        keys.append(run['profile']+'|'+poses.pop())
    return keys


def verify_fixtures(runs, keys, fixtures):
    for run, key in zip(runs, keys):
        selected = fixtures.get(key)
        if not isinstance(selected, dict):
            raise ValueError('Missing admitted native fixture profile/pose mapping')
        expected = {field: selected[field] for field in ('path', 'manifestSha256', 'backgrounds')}
        if run.get('fixtures') != expected:
            raise ValueError('Immutable planned fixtures differ from native fixture metadata')


def prepare_exposure(context, runs, loaded):
    """Use the native module's original admission/planning/preparation API without pixel fallback."""
    newbed = [run for run in runs if run['sceneSource'] == 'w50']
    if not newbed:
        return None
    config_pin = newbed[0].get('nativeExposureConfig')
    if (not isinstance(config_pin, dict) or config_pin not in context['inputs'] or
            any(run.get('nativeExposureConfig') != config_pin for run in newbed)):
        raise ValueError('W50 exposure requires one shared registered nativeExposureConfig pin')
    keys = fixture_keys(newbed, loaded['w50'])
    native = native_adapter()
    # This original API proves root/config/claim/gate/membership before any archive frame read.
    _, _, config, manifest, scenes = native.admission(context, newbed[0], config_pin)
    plans = native.read_fixture_plan(Path(config['archiveRoot'])/'index.json',
        config['archiveIndexSha256'], manifest, scenes, Path(context['output'])/'native-blind')
    verify_fixtures(newbed, keys, plans)
    evidence = native.prepare_native_exposure(context, newbed[0], config_pin)
    verify_fixtures(newbed, keys, evidence['fixtures'])
    return evidence


def execute(context):
    dispatcher = sys.modules.get('w50_g1_dispatch')
    if dispatcher is None:
        raise ValueError('LIVE capture routing requires the registered dispatcher')
    dispatcher.require_context(context)
    phase = context.get('phase')
    if phase not in ('fit', 'gate', 'exposure') or context.get('batch', {}).get('phase') != phase:
        raise ValueError('LIVE router admits only a matching fit/gate/exposure batch')
    runs = context['batch']['runs']
    if not runs or any(run.get('sceneSource') not in ('canonical', 'w50') for run in runs):
        raise ValueError('Unknown or empty LIVE scene-source population')
    for run in runs:
        dispatcher.require_render_admission(context, run)
    baselines = []
    if phase == 'exposure':
        qualified_exposure(context)
        for run in runs:
            if run.get('baselineCandidate') not in context['baselineDocuments']:
                raise ValueError('Exposure needs a registered same-cell baseline candidate')
            baseline = dispatcher.baseline_run(run)
            dispatcher.require_render_admission(context, baseline, current=True)
            baselines.append(baseline)
    loaded = adapters()
    native = prepare_exposure(context, runs, loaded) if phase == 'exposure' else None
    captures = []
    for index, run in enumerate(runs):
        adapter = loaded[run['sceneSource']]
        capture = adapter.capture_run if run['sceneSource'] == 'canonical' else adapter._capture_run
        captures.extend(capture(context, run, current=False))
        if phase == 'exposure':
            captures.extend(capture(context, baselines[index], current=True))
    dispatcher.require_context(context)
    result = {'schema': 'w50-live-captures-1', 'status': 'CAPTURED',
              'measurement': 'capture-completeness-only', 'phase': phase,
              'candidateSha256s': sorted(p['sha256'] for p in context['batch']['cohort']),
              'captures': captures}
    if native is not None:
        result['nativeExposure'] = native
    return result
