"""DL5f current attempt two: unchanged canonical transport, corrected new-bed host.

The dispatcher retains one original context. The forty-two first-run GPU results must
pass its byte comparator before any later run, particularly CSS, receives admission.
"""
from pathlib import Path
import sys
import types

HERE=Path(__file__).resolve().parent
PRIOR=HERE.parent/'2026-10-08-w50-g1-fit'


def source(path,name):
    module=types.ModuleType(name);module.__file__=str(path)
    exec(compile(path.read_bytes(),str(path),'exec',dont_inherit=True),module.__dict__)
    return module


def adapters():
    return {'w50':source(HERE/'web/adapter.py','w50_current2_web'),
            'canonical':source(PRIOR/'canonical/adapter.py','w50_current2_canonical')}


def source_probe():
    for adapter in adapters().values():
        if adapter.source_probe().get('status')!='SOURCE_ONLY':
            raise ValueError('Current2 source probe attempted a measured operation')
    return {'status':'SOURCE_ONLY'}


def execute_current(context):
    dispatcher=sys.modules.get('w50_g1_dispatch')
    if dispatcher is None:raise ValueError('Replacement routing requires actual dispatcher authority')
    dispatcher.require_context(context)
    if context.get('phase')!='current' or context.get('batch',{}).get('phase')!='current':
        raise ValueError('Current2 router cannot launch live candidate phases')
    runs=context['batch']['runs']
    if not runs or any(r.get('sceneSource') not in ('w50','canonical') for r in runs):
        raise ValueError('Unknown or empty current2 scene-source population')
    loaded=adapters();records=[]
    for run in runs:
        dispatcher.require_current_replay(context,run)
        adapter=loaded[run['sceneSource']]
        capture=adapter._capture_run if run['sceneSource']=='w50' else adapter.capture_run
        captured=capture(context,run,current=True)
        records.extend(captured)
        if dispatcher.is_replay_run(context,run):
            dispatcher.record_current_replay(context,captured)
    return {'schema':'w50-current-captures-1','status':'CAPTURED','measurement':'capture-completeness-only',
            'phase':'current','candidateSha256s':sorted(p['sha256'] for p in context['batch']['cohort']),
            'captures':records}
