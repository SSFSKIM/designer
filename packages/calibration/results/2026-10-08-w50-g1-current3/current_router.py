"""DL5h mixed-origin current recovery with no rerender of retained members.

All original logical runs remain in the contract. Only the dispatcher's derived fresh
slice reaches a transport; original501 are source-revalidated and copied byte-for-byte
with explicit origin and legacy equality provenance. No second legacy image is invented.
"""
from pathlib import Path
import sys
import types

HERE=Path(__file__).resolve().parent


def source(path,name):
    module=types.ModuleType(name);module.__file__=str(path)
    exec(compile(path.read_bytes(),str(path),'exec',dont_inherit=True),module.__dict__)
    return module


def adapters():
    return {'w50':source(HERE/'web/adapter.py','w50_current3_web'),
            'canonical':source(HERE/'canonical/adapter.py','w50_current3_canonical')}


def source_probe():
    for adapter in adapters().values():
        if adapter.source_probe().get('status')!='SOURCE_ONLY':raise ValueError('Recovery transport probe is not source-only')
    retained=source(HERE/'execution/retained.py','w50_current3_retained_probe')
    if retained.source_probe(HERE.parents[3]).get('status')!='SOURCE_ONLY':raise ValueError('Original transport probe is not source-only')
    repeat=source(HERE/'repeat/admission.py','w50_current3_repeat_probe')
    if repeat.source_probe().get('status')!='SOURCE_ONLY':raise ValueError('Repeat reader probe is not source-only')
    return {'status':'SOURCE_ONLY'}


def execute_current(context):
    dispatcher=sys.modules.get('w50_g1_dispatch')
    if dispatcher is None:raise ValueError('Recovery router needs the actual admitted dispatcher')
    dispatcher.require_context(context)
    if context.get('phase')!='current' or context.get('batch',{}).get('phase')!='current':
        raise ValueError('Recovery router cannot execute a live candidate phase')
    runs=context['batch']['runs']
    if not runs or any(r.get('sceneSource') not in ('w50','canonical') for r in runs):
        raise ValueError('Unknown or empty current recovery population')
    restored=dispatcher.retained_current_records(context)
    loaded=adapters();fresh=[]
    for logical in runs:
        run=dispatcher.fresh_current_run(context,logical)
        if run is None:continue
        adapter=loaded[run['sceneSource']]
        capture=adapter._capture_run if run['sceneSource']=='w50' else adapter.capture_run
        for record in capture(context,run,current=True):
            if 'origin' in record:raise ValueError('Transport must not manufacture a retained origin')
            fresh.append({**record,'origin':{'kind':'fresh-attempt3'}})
    all_rows={}
    for record in restored+fresh:
        key=(record['profile'],record['renderer'],record['scene'])
        if key in all_rows:raise ValueError('Recovery duplicated a retained/fresh member')
        all_rows[key]=record
    ordered=[]
    for run in runs:
        for scene in run['scenes']:
            key=(run['profile'],run['renderer'],scene)
            if key not in all_rows:raise ValueError('Recovery omitted an original logical member')
            ordered.append(all_rows.pop(key))
    if all_rows:raise ValueError('Recovery reported extra members')
    return {'schema':'w50-current-recovery-captures-1','status':'CAPTURED',
        'measurement':'capture-completeness-only','phase':'current',
        'candidateSha256s':sorted(p['sha256'] for p in context['batch']['cohort']),
        'origins':{'retainedAttempt2':len(restored),'freshAttempt3':len(fresh)},'captures':ordered}
