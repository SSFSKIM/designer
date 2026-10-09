"""Current-material capture routing only, before the later live-candidate root exists.

The instrument's fixed batch remains whole: each adapter receives the same admitted context
and an original run, never a caller-built sub-context that could escape its content pin.
This file has no candidate, fitting, gate, exposure or judging entrypoint.
"""
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent


def source(path, name):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module


def adapters():
    # Actual execution has already installed the instrument's permanent source-only guard.
    return {'w50': source(HERE/'web/adapter.py', 'w50_current_web'),
            'canonical': source(HERE/'canonical/adapter.py', 'w50_current_canonical')}


def source_probe():
    """Exercise both source-only transport routes without a context, census or capture."""
    for adapter in adapters().values():
        result = adapter.source_probe()
        if result.get('status') != 'SOURCE_ONLY':
            raise ValueError('Unexpected source-only adapter probe result')
    return {'status': 'SOURCE_ONLY'}


def execute_current(context):
    dispatcher = sys.modules.get('w50_g1_dispatch')
    if dispatcher is None:
        raise ValueError('Current routing requires the live registered instrument')
    dispatcher.require_context(context)
    if context.get('phase') != 'current' or context.get('batch', {}).get('phase') != 'current':
        raise ValueError('This router cannot execute a live-candidate phase')
    runs = context['batch']['runs']
    if not runs or any(run.get('sceneSource') not in ('w50', 'canonical') for run in runs):
        raise ValueError('Unknown or empty current scene-source population')
    loaded = adapters()
    captures = []
    for run in runs:
        adapter = loaded[run['sceneSource']]
        capture = adapter._capture_run if run['sceneSource'] == 'w50' else adapter.capture_run
        captures.extend(capture(context, run, current=True))
    return {'schema': 'w50-current-captures-1', 'status': 'CAPTURED',
            'measurement': 'capture-completeness-only', 'phase': 'current',
            'candidateSha256s': sorted(pin['sha256'] for pin in context['batch']['cohort']),
            'captures': captures}
