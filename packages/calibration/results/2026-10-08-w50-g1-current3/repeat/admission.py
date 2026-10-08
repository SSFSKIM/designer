"""DL5h fresh-pair admission for current, fit, gate and exposure.

Both real images and both production page reports are retained and content-checked. The first
image is the reading even when its pair is admitted numerically. Legacy attempt-2 equality
attestations are deliberately not this format; their exact 501-member recovery is dispatcher-owned.
"""
import copy
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import sys
from PIL import Image

HERE=Path(__file__).resolve().parent


def source(path,name):
    import types
    module=types.ModuleType(name); module.__file__=str(path)
    exec(compile(path.read_bytes(),str(path),'exec',dont_inherit=True),module.__dict__)
    return module


S=source(HERE/'sources.py','w50_repeat_sources')
C=S.C


def sha(raw): return hashlib.sha256(raw).hexdigest()


def encoded(value): return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()


def load(raw):
    def invalid(value): raise C.InstrumentFault('Nonfinite repeat JSON: '+value)
    return json.loads(raw,parse_constant=invalid)


def read_pin(pin,root):
    return S.M._pin_bytes(pin,Path(root),external=True)


def identity(record):
    return {k:copy.deepcopy(record[k]) for k in
            ('profile','renderer','scene','candidate','lane','sceneSource')}


def read_pair(context,run,record,pair_pin):
    """Artifact validation only; this function cannot issue an admission receipt."""
    if any(record.get(k)!=run.get(k) for k in ('profile','renderer','candidate','sceneSource')) \
            or record.get('scene') not in run['scenes'] or record.get('lane') not in ('current','candidate'):
        raise C.InstrumentFault('Repeat receipt differs from the admitted run/member')
    scene,tier=record['scene'],record['renderer']
    folder=Path(run['captureRoot'])
    if run['sceneSource']=='canonical': folder/=run['profile']
    elif run['sceneSource']!='w50': raise C.InstrumentFault('Unknown repeat scene source')
    folder/=scene
    if pair_pin.get('path')!=str(folder/f'repeat__{tier}.json'):
        raise C.InstrumentFault('Pair manifest is not the exact retained source member')
    pair=load(read_pin(pair_pin,context['output']))
    if pair.get('schema')!=1 or pair.get('kind')!='w50-retained-repeat-pair' \
            or pair.get('reading')!='first' or pair.get('scene')!=scene or pair.get('renderer')!=tier:
        raise C.InstrumentFault('Fresh admission requires both retained captures, not legacy attestation')
    match=re.search(r'-([12])x-',record['profile'])
    if not match: raise C.InstrumentFault('Unknown repeat scale')
    dpr=int(match[1]); canvas=(320,200) if run['sceneSource']=='canonical' else (512,384)
    shape=(canvas[1]*dpr,canvas[0]*dpr,4)
    raw_images=[]; images=[]; pages=[]; pins=[]
    for side,suffix in (('first',''),('second','__repeat')):
        item=pair[side]
        for name,filename in (('image',f'{scene}__{tier}{suffix}.png'),
                              ('report',f'page__{tier}__{side}.json')):
            if item[name].get('path')!=str(folder/filename):
                raise C.InstrumentFault('Retained image/report aliases another capture')
            pins.append(item[name])
        raw=read_pin(item['image'],context['output']); raw_images.append(raw)
        with Image.open(io.BytesIO(raw)) as image:
            if image.format!='PNG': raise C.InstrumentFault('Retained image is not PNG')
            decoded=S.M.np.asarray(image.convert('RGBA'))
        if decoded.shape!=shape: raise C.InstrumentFault('Actual retained PNG geometry differs')
        images.append(decoded)
        pages.append(load(read_pin(item['report'],context['output'])))
    if len({os.stat(p['path']).st_ino for p in pins})!=4:
        raise C.InstrumentFault('Retained capture artifacts must be independent files')
    identical=raw_images[0]==raw_images[1]
    noise=float(S.M.np.abs(images[0].astype('int16')-images[1].astype('int16')).mean())
    if type(pair.get('deterministic')) is not bool or pair['deterministic']!=identical \
            or type(pair.get('repeatNoise')) not in (int,float) \
            or not math.isfinite(pair['repeatNoise']) or pair['repeatNoise']!=noise:
        raise C.InstrumentFault('Original equality/noise attestation differs from actual retained pair')
    artifacts=record['artifacts']
    if artifacts['png']!=pair['first']['image']:
        raise C.InstrumentFault('Reading capture must remain the original first image')
    for name,filename in (('report',f'report__{tier}.json'),('cell',f'cell__{tier}.json')):
        if artifacts[name].get('path')!=str(folder/filename):
            raise C.InstrumentFault('Original envelope/cell differs from exact capture member')
    envelope=load(read_pin(artifacts['report'],context['output']))
    cell=load(read_pin(artifacts['cell'],context['output']))
    if envelope.get('page')!=pages[0] or cell.get('deterministic')!=identical \
            or cell.get('repeatNoise')!=noise or cell.get('renderer')!=tier or cell.get('colorSpace')!='srgb':
        raise C.InstrumentFault('Original report/cell cannot be relabelled to admit a repeat')
    return dict(pair=pair,images=[im[:,:,:3] for im in images],pages=pages,envelope=envelope,
                identical=identical,noise=noise,folder=folder)


def authority(context,run,record):
    dispatcher=sys.modules.get('w50_g1_dispatch')
    if dispatcher is None: raise C.InstrumentFault('Repeat admission requires a live dispatcher')
    dispatcher.require_context(context)
    dispatcher.require_render_admission(context,run,current=record['lane']=='current')
    root=dispatcher.sealed(context['executionRoot'])
    binding=context.get('repeatAdmission')
    if not binding or binding!=root.get('repeatAdmission'):
        raise C.InstrumentFault('Repeat reader/config is not the execution-root binding')
    repo=Path(context['repo'])
    if dispatcher.checked(repo,binding['entrypoint'])!=Path(__file__).resolve() \
            or binding['config'] not in context['inputs']:
        raise C.InstrumentFault('Repeat admission entrypoint/config differs from sealed root')
    config=dispatcher.load(dispatcher.checked(repo,binding['config']))
    if config.get('schema')!='w50-repeat-config-1' or config.get('references')!=root['references']:
        raise C.InstrumentFault('Repeat membership is not the original declared reference set')
    inventory=dispatcher.load(dispatcher.checked(repo,config['references']))
    rows=[r for r in inventory['cells'] if all(r[k]==record[k] for k in ('profile','renderer','scene'))]
    if not rows or len({r['statistic'] for r in rows})!=len(rows):
        raise C.InstrumentFault('Repeat member lacks unique original declared statistics')
    if context['phase']!='exposure' and any(r['role'] in ('blind','historical-prediction-check') for r in rows):
        raise C.InstrumentFault('Withheld repeat sources are exposure-only')
    return dispatcher,config,rows,inventory


def validate_reports(context,run,record,retained,inventory):
    adapter=source(HERE.parent/('web' if run['sceneSource']=='w50' else 'canonical')/'adapter.py',
                   'w50_repeat_actual_report_validator')
    adapter.validate_pair_reports(context,run,record,retained['envelope'],*retained['pages'])
    if run['sceneSource']!='canonical': return
    required=S.M.N.required_arguments(inventory)
    key='|'.join(record[k] for k in ('profile','renderer','scene'))
    # required_arguments is keyed by the original three-field physical identity.
    if key not in required: return
    A=source(S.FIT/'current-analysis/analysis.py','w50_repeat_canonical_argument')
    plan=adapter.scene_plan(run,context['phase'])
    scene=next(s for s in plan['scenes'] if s['id']==record['scene'])
    pose='receded' if scene['state']=='inactive' else 'active'
    spec=dict(scene=scene['id'],pose=pose,role=scene['fixtureSet'],background=scene['background'],
              component=plan['components'][scene['component']])
    web=source(HERE.parent/'web/adapter.py','w50_repeat_actual_candidate')
    candidate=web.candidate_info(run['candidate'],plan['position'],current=record['lane']=='current')
    endpoint=candidate['endpoints'][pose+'.dark']
    resolved={**candidate['endpoints']['active.dark']['patch'],**endpoint['patch']}
    mode=resolved.get('backdropToneAbscissa','source')
    mode='silhouette' if isinstance(mode,dict) else mode
    for page in retained['pages']: A.canonical_argument(page,run,plan,spec,mode)


def proof_body(context,run,record,pair_pin,retained,config,rows):
    differences={}
    if not retained['identical']:
        if run['sceneSource']=='w50':
            first,second=S.newbed_pair(context,run,config,rows,*retained['images'])
        else:
            dispatcher=sys.modules['w50_g1_dispatch']
            canonical=dispatcher.load(dispatcher.checked(context['repo'],config['canonical']))
            first,second=S.canonical_pair(canonical,rows,*retained['images'])
        differences=C.compare_statistics(first,second)
    return dict(schema='w50-repeat-admission-1',kind='retained-repeat-pair',reading='first',
        **identity(record),mode='byte-identical' if retained['identical'] else 'native-repeat-band',
        manifest=copy.deepcopy(pair_pin),config=copy.deepcopy(context['repeatAdmission']['config']),
        pair=copy.deepcopy(retained['pair']),originalArtifacts={k:copy.deepcopy(record['artifacts'][k])
            for k in ('png','report','cell')},differences=differences,
        declaredStatistics=[r['statistic'] for r in rows],
        rule='every statistic/channel/cut <= 0.1 native repeat bar; never 0.1 B',
        executionRootSha256=sha(Path(context['executionRoot']).read_bytes()),
        contractSha256=sha(Path(context['contract']).read_bytes()),
        batchSha256=sha(Path(context['batchPath']).read_bytes()))


def write_once(path, body):
    raw=encoded(body)
    with path.open('xb') as handle:
        handle.write(raw);handle.flush();os.fsync(handle.fileno())
    return dict(path=str(path),sha256=sha(raw))


def write_fault(context,record,pair_pin,retained,error,rows):
    """Diagnose an instrument stop without creating any admitted reading or candidate verdict."""
    body=dict(schema='w50-repeat-fault-1',status='INSTRUMENT_FAULT',reading='first',
        **identity(record),reason=str(error),strictIdentityRequired=isinstance(error,C.IdentityRequired),
        differences=copy.deepcopy(getattr(error,'differences',{})),
        declaredStatistics=[r['statistic'] for r in rows],pair=copy.deepcopy(retained['pair']),
        manifest=copy.deepcopy(pair_pin),config=copy.deepcopy(context['repeatAdmission']['config']),
        originalArtifacts={k:copy.deepcopy(record['artifacts'][k]) for k in ('png','report','cell')})
    for name,path in (('executionRoot',context['executionRoot']),('contract',context['contract']),
                      ('batch',context['batchPath']),('claim',context['contract']+'.started.json')):
        body[name]=dict(path=str(path),sha256=sha(Path(path).read_bytes()))
    return write_once(retained['folder']/f'repeat-fault__{record["renderer"]}.json',body)


def admit_pair(context,run,record,pair_pin):
    """Write once; return a content pin, never a verdict or a replacement capture."""
    dispatcher,config,rows,inventory=authority(context,run,record)
    retained=read_pair(context,run,record,pair_pin)
    try:
        validate_reports(context,run,record,retained,inventory)
        body=proof_body(context,run,record,pair_pin,retained,config,rows)
    except (ValueError,OSError) as error:
        fault_pin=write_fault(context,record,pair_pin,retained,error,rows)
        fault=error if isinstance(error,C.InstrumentFault) else C.InstrumentFault(str(error))
        fault.receipt=fault_pin
        raise fault
    # Recheck retained pins after native source I/O, before writing the first-reading receipt.
    read_pair(context,run,record,pair_pin)
    dispatcher.require_context(context)
    path=retained['folder']/f'repeat-admission__{run["renderer"]}.json'
    return write_once(path,body)


def verify_receipt(context,run,record):
    """Recheck the pair and both source reports without reopening native statistical data."""
    dispatcher,config,rows,inventory=authority(context,run,record)
    retained=read_pair(context,run,record,record['repeatPair'])
    validate_reports(context,run,record,retained,inventory)
    pin=record['repeatAdmission']
    if pin.get('path')!=str(retained['folder']/f'repeat-admission__{run["renderer"]}.json'):
        raise C.InstrumentFault('Repeat proof is not the member-owned receipt')
    proof=load(read_pin(pin,context['output']))
    expected=proof_body(context,run,record,record['repeatPair'],
        {**retained,'identical':True},config,rows)
    if not retained['identical']:
        expected['mode']='native-repeat-band'
        differences=proof.get('differences',{})
        if run['sceneSource']=='w50':
            names={r['statistic'] for r in rows}
        else:
            canonical=dispatcher.load(dispatcher.checked(context['repo'],config['canonical']))
            scenes=S.R.json_pin(canonical['scenes'])
            scene=next(s for s in scenes['scenes'] if s['id']==record['scene'])
            kind=scenes['backgrounds'][scene['background']]['kind']
            names=set(S.canonical_membership(rows,impulse=kind=='impulse',solid=kind=='solid'))
        if set(differences)!=names:
            raise C.InstrumentFault('Repeat receipt omitted or invented a declared statistic/cut')
        first={};second={}
        for name,item in differences.items():
            common=dict(units=item['units'],support=item['support'],repeat=item['nativeRepeat'],
                        provenance=item['provenance'])
            first[name]=dict(common,value=item['first']);second[name]=dict(common,value=item['second'])
        expected['differences']=C.compare_statistics(first,second)
    if proof!=expected: raise C.InstrumentFault('Repeat receipt is not bound to this exact original pair')
    dispatcher.require_context(context)
    return proof


def source_probe():
    """Closure discovery and pure synthetic statistics, never actual captured/native data."""
    S.source_probe()
    source(HERE.parent/'web/adapter.py','w50_repeat_probe_web')
    source(HERE.parent/'canonical/adapter.py','w50_repeat_probe_canonical')
    return {'status':'SOURCE_ONLY'}
