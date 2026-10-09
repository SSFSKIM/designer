"""Re-admit original attempt2 receipts through its unchanged source before retaining bytes.

No browser is launched here. Existing run indices are checked where present; the partial
run is reconstructed by the exact same scene/candidate/fixture/report functions that
validated the original draw. Missing evidence or any divergence is an instrument fault.
"""
import copy
import hashlib
import json
from pathlib import Path
import types


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(path):return json.loads(Path(path).read_text())


def source(path,name):
    module=types.ModuleType(name);module.__file__=str(path)
    exec(compile(path.read_bytes(),str(path),'exec',dont_inherit=True),module.__dict__)
    return module


def source_probe(repo):
    path=Path(repo)/'packages/calibration/results/2026-10-08-w50-g1-current2/web/adapter.py'
    return source(path,'w50_retained_prior_adapter_probe').source_probe()


def checked(pin):
    if not isinstance(pin,dict) or not isinstance(pin.get('path'),str):raise ValueError('Missing original retained artifact')
    path=Path(pin['path'])
    if not path.is_file() or sha(path)!=pin.get('sha256'):raise ValueError('Retained original artifact changed')
    return path


def reconstruct(adapter,run,entry):
    """Pure source-owned admission plus hash/file reads; never trusts filenames alone."""
    for pin in [*entry['artifacts'].values(),*entry['originalEvidence'].values()]:checked(pin)
    plan=adapter.scene_plan(run,'current')
    specs=[s for s in plan['scenes'] if s['scene']==entry['scene']]
    if len(specs)!=1 or any(run[k]!=entry[k] for k in ('profile','renderer','sceneSource','candidate')):
        raise ValueError('Retained entry differs from original fixed run/scene')
    spec=specs[0]
    closure=adapter.read_json(adapter.pin_file(run['webSourceClosure']))
    for pin in closure['sources']:adapter.pin_file(pin)
    candidate=adapter.candidate_info(run['candidate'],plan['position'],current=True)
    fixture=adapter.fixture_info(run,plan)
    endpoint=candidate['endpoints'][f'{spec["pose"]}.dark']
    active=candidate['endpoints']['active.dark']['patch']
    mode={**active,**endpoint['patch']}.get('backdropToneAbscissa','source')
    abscissa='silhouette' if isinstance(mode,dict) else mode
    report=load(checked(entry['artifacts']['report']))
    arguments=adapter.validate_report(report,run,endpoint,abscissa=abscissa,phase='current')
    cell=load(checked(entry['artifacts']['cell']))
    if (cell.get('renderer')!=run['renderer'] or cell.get('colorSpace')!='srgb' or
            cell.get('deterministic') is not True or type(cell.get('repeatNoise')) not in (int,float) or cell['repeatNoise']!=0):
        raise ValueError('Retained capture lost its original byte-identical equality attestation')
    raw=checked(entry['artifacts']['png']).read_bytes()
    expected=(plan['canvas']['width']*plan['dpr'],plan['canvas']['height']*plan['dpr'])
    if raw[:8]!=b'\x89PNG\r\n\x1a\n' or tuple(int.from_bytes(raw[i:i+4],'big') for i in (16,20))!=expected:
        raise ValueError('Retained PNG violates original dimensions/source admission')
    original=entry['originalEvidence']
    for name in ('request','census','log'):
        if name not in original:raise ValueError('Retained draw lacks its original transport evidence')
    request=load(checked(original['request']));census=load(checked(original['census']))
    if (request.get('sceneSource')!=plan['source'] or request.get('scenesSha256')!=plan['scenesSha256'] or
            request.get('candidate')!=run['candidate'] or request.get('fixture')!=fixture or request.get('lane')!='current' or
            not request.get('argv') or request['argv'][-1]!=entry['scene'] or census.get('passes') is not True):
        raise ValueError('Retained draw does not reproduce its original request/census')
    argv=request['argv']
    for flag,wanted in [('--renderer',run['renderer']),('--scale',str(plan['dpr'])),
                         ('--candidate-document',candidate['path']),('--out',run['captureRoot'])]:
        if argv.count(flag)!=1 or argv[argv.index(flag)+1]!=wanted:
            raise ValueError('Retained launch argv differs from its fixed source/candidate')
    artifacts=entry['artifacts']
    for argument in arguments:
        argument['provenance'].update(report=artifacts['report'],capture=artifacts['png'],sceneSource=plan['source'],
            scenesSha256=plan['scenesSha256'],candidateDocument=run['candidate'],baseline=True,
            endpoint={k:v for k,v in endpoint.items() if k!='patch'})
    record=dict(profile=run['profile'],renderer=run['renderer'],scene=entry['scene'],candidate=run['candidate'],
        lane='current',sceneSource=plan['source'],canvas=plan['canvas'],dpr=plan['dpr'],artifacts=artifacts,
        arguments=arguments,background=next(b for b in fixture['backgrounds'] if b['key']==f'{spec["background"]}@{plan["dpr"]}x'))
    if 'record' in original and load(checked(original['record']))!=record:
        raise ValueError('Raw retained record differs from unchanged source reconstruction')
    if 'index' in original:
        index=load(checked(original['index']))
        if index.get('schema')!='w50-web-capture-index-1':raise ValueError('Unknown original run index')
        matches=[r for r in index.get('captures',[]) if all(r.get(k)==record[k] for k in ('profile','renderer','scene'))]
        if matches!=[record]:raise ValueError('Retained run index differs from source-reconstructed record')
    elif entry['runIndex']<11:
        raise ValueError('A completed original run cannot omit its sealed index')
    return record


def materialize(context,partition,entries):
    repo=Path(context['repo']);output=Path(context['output'])
    adapter=source(repo/'packages/calibration/results/2026-10-08-w50-g1-current2/web/adapter.py','w50_retained_prior_adapter')
    batches=[load(repo/p['path']) for p in partition['priorBatches']]
    result=[]
    for entry in entries:
        run=batches[entry['batchIndex']]['runs'][entry['runIndex']]
        original=reconstruct(adapter,run,entry)
        record=copy.deepcopy(original)
        folder=output/'retained-attempt2'/entry['profile']/entry['scene']/entry['renderer']
        folder.mkdir(parents=True,exist_ok=False)
        for name,pin in original['artifacts'].items():
            old=checked(pin);dest=folder/old.name
            with dest.open('xb') as handle:handle.write(old.read_bytes())
            if sha(dest)!=pin['sha256']:raise ValueError('Retained copy differs from original bytes')
            record['artifacts'][name]={'path':str(dest),'sha256':pin['sha256']}
        record['origin']={'kind':'retained-attempt2','ordinal':entry['ordinal'],
            'priorRoot':partition['authority']['priorRoot'],'priorClaim':partition['authority']['priorClaim'],
            'priorFailure':partition['authority']['priorFailure'],'originalArtifacts':original['artifacts'],
            'originalEvidence':entry['originalEvidence']}
        record['repeatAdmission']={'schema':'w50-legacy-byte-identical-1','mode':'legacy-byte-identical',
            'reading':'first','first':original['artifacts']['png'],'originalEqualityAttestation':original['artifacts']['cell'],
            'deterministic':True,'repeatNoise':0,'secondRetained':False}
        result.append(record)
    return result
