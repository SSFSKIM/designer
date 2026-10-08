"""DL5f's one declared replacement, not a general retry facility.

The prior run remains burned. Its failed manifest, contract and claim identify precisely
42 successful GPU PNGs. This module compares compressed PNG bytes, never decodes pixels
or measures a statistic. It cannot replace a missing prior artifact or widen admission.
"""
import hashlib
import json
from pathlib import Path

PRIOR=Path('packages/calibration/results/2026-10-08-w50-g1-fit')
CURRENT=Path('packages/calibration/results/2026-10-08-w50-g1-current2')
DL5F='''DL5f (parent, before any candidate). The first current-only batch (f28a2dc42 root 9f7e413c…) stopped
at exact geometry admission: the shipped source-abscissa CSS host is content-box (scene.ts 848-862),
so CSS draws 122x46 for a declared 120x44. This is the tracked harness debt "The source-profile CSS
harness retains its historical content-box sizing" (tracker, §5.145), whose stated correction is
border-box geometry for the source-profile bed. Ruled: an additive W50 NEW-BED-only border-box host
setup (wave-local entry; canonical scene.ts semantics and all G0 pins untouched); admission is NOT
relaxed. The burned attempt and its 43 artefacts are retained as failed evidence. A replacement
current-only instrument is sealed as attempt 2 naming attempt 1 and this ruling, and must prove
the 42 GPU cells already captured re-render byte-identical under the new host before its CSS cells
count. Canonical draws keep canonical semantics. Candidate and current read the same new-bed host.
'''


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(path):return json.loads(Path(path).read_text())


def checked(repo,pin):
    if not isinstance(pin,dict) or not isinstance(pin.get('path'),str):
        raise ValueError('Missing replacement evidence pin')
    path=(Path(repo)/pin['path']).resolve()
    if not path.is_relative_to(Path(repo).resolve()) or not path.is_file() or sha(path)!=pin.get('sha256'):
        raise ValueError('Changed or escaped replacement evidence pin')
    return path


def sealed(path):
    if Path(str(path)+'.sha256').read_text()!=f'{sha(path)}  {path.name}\n':
        raise ValueError('Prior current instrument/contract seal changed')
    return load(path)


def validate(repo,directory,declaration,batches):
    repo,directory=Path(repo).resolve(),Path(directory).resolve()
    if directory!=repo/CURRENT/'execution' or not isinstance(declaration,dict) or set(declaration)!={
            'attempt','priorRoot','priorClaim','priorFailure','ruling'} or declaration.get('attempt')!=2:
        raise ValueError('Only DL5f attempt two at its declared sibling is authorised')
    paths={k:checked(repo,declaration[k]) for k in ('priorRoot','priorClaim','priorFailure','ruling')}
    if paths['priorRoot']!=repo/PRIOR/'execution/current-instrument-root.json' or \
            paths['priorFailure']!=repo/PRIOR/'evidence/current-attempt1/failure.json' or \
            paths['ruling'].read_text()!=DL5F:
        raise ValueError('Replacement must name the declared first attempt and exact DL5f ruling')
    prior=sealed(paths['priorRoot']);failure=load(paths['priorFailure'])
    if (prior.get('schema')!='w50-g1-current-instrument-root-1' or 'replacementAttempt' in prior or
            failure.get('schema')!='w50-current-attempt-failure-1' or
            failure.get('status')!='STOPPED_INCOMPLETE_NO_RETRY' or failure.get('candidateVerdict')!='NOT_READ' or
            failure.get('successfulBatchResult') is not False or failure.get('reportCount')!=43 or
            failure.get('root')!=declaration['priorRoot'] or failure.get('claim')!=declaration['priorClaim']):
        raise ValueError('Replacement cannot promote an unrelated or successful prior attempt')
    contract_path=checked(repo,failure['contract']);contract=sealed(contract_path)
    if (contract.get('phase')!='current' or contract.get('executionRootSha256')!=declaration['priorRoot']['sha256'] or
            contract.get('batch') not in prior.get('currentBatches',[]) or
            paths['priorClaim']!=Path(str(contract_path)+'.started.json') or
            Path(str(contract_path)+'.result.json').exists()):
        raise ValueError('Prior current attempt was not this burned claimed contract')
    claim=load(paths['priorClaim']);batch_path=checked(repo,contract['batch']);prior_batch=load(batch_path)
    if claim.get('contractSha256')!=failure['contract']['sha256'] or claim.get('batchSha256')!=contract['batch']['sha256'] or \
            claim.get('phase')!='current' or Path(claim.get('output','')).resolve()!=Path(failure['tree']).resolve():
        raise ValueError('Prior claim is not bound to the failed capture tree')
    if not prior_batch.get('runs'):raise ValueError('Prior contract has no registered GPU run')
    first=prior_batch['runs'][0]
    if first.get('renderer')!='webgpu' or first.get('sceneSource')!='w50' or len(first.get('scenes',[]))!=42 or \
            len(set(first['scenes']))!=42:
        raise ValueError('Prior first run is not the forty-two declared GPU cells')
    if not batches or not batches[0].get('runs'):raise ValueError('Replacement has no fixed first GPU run')
    new=batches[0]['runs'][0]
    for key in ('profile','renderer','sceneSource','scenes','sets','candidate','fixtures'):
        if new.get(key)!=first.get(key):
            raise ValueError(f'Replacement first GPU run changes original {key}')
    tree=Path(failure['tree']).resolve();capture_root=Path(first['captureRoot']).resolve()
    files=failure.get('files',[])
    if len({p['path'] for p in files})!=len(files):raise ValueError('Duplicate failed artifact identity')
    index={p['path']:p for p in files};wanted=[]
    for scene in first['scenes']:
        path=capture_root/scene/f'{scene}__webgpu.png'
        if not path.is_relative_to(tree):raise ValueError('Prior capture escapes failed tree')
        relative=str(path.relative_to(tree));item=index.get(relative)
        if not item or not isinstance(item.get('sha256'),str):raise ValueError('Missing exact prior GPU PNG witness')
        wanted.append({'profile':first['profile'],'renderer':'webgpu','scene':scene,
                       'candidate':first['candidate'],'png':{'path':str(path),'sha256':item['sha256']}})
    all_gpu={p['path'] for p in files if p['path'].endswith('__webgpu.png')}
    if all_gpu!={str(Path(p['png']['path']).relative_to(tree)) for p in wanted}:
        raise ValueError('Prior GPU population differs from exactly forty-two declared cells')
    # Hashes are rechecked at compare time; sealing reads metadata, never capture statistics.
    return {**declaration,'priorGpu':wanted,'priorContract':failure['contract'],
            'priorBatch':contract['batch'],'firstRunId':new['id']}


def compare(replacement,records,output):
    expected=replacement['priorGpu']
    key=lambda r:(r.get('profile'),r.get('renderer'),r.get('scene'))
    if len(records)!=42 or [key(r) for r in records]!=[key(r) for r in expected]:
        raise ValueError('Replacement GPU replay membership/order is not the exact prior forty-two')
    compared=[]
    for before,after in zip(expected,records):
        if after.get('candidate')!=before['candidate'] or after.get('lane')!='current':
            raise ValueError('Replacement GPU replay changes current material/lane')
        old=Path(before['png']['path']);new_pin=after.get('artifacts',{}).get('png',{})
        new=Path(new_pin.get('path','')).resolve()
        if not new.is_relative_to(Path(output).resolve()) or new==old.resolve() or not old.is_file() or not new.is_file() or \
                sha(old)!=before['png']['sha256'] or sha(new)!=new_pin.get('sha256') or \
                new_pin['sha256']!=before['png']['sha256'] or new.read_bytes()!=old.read_bytes():
            raise ValueError('Replacement GPU PNG bytes differ from the retained first attempt')
        compared.append({**{k:before[k] for k in ('profile','renderer','scene')},
                         'priorPng':before['png'],'replacementPng':new_pin})
    return compared
