"""DL5h exact attempt-three recovery: retain501, draw only unfinished298.

No generic retry selector exists. Membership is derived from the prior ordered fixed
batches and original attested artifact inventory. Retained pixels are never passed off
as fresh repeated captures; their sole repeat evidence is the original equality record.
"""
import hashlib
import json
from pathlib import Path

PRIOR=Path('packages/calibration/results/2026-10-08-w50-g1-current2')
CURRENT=Path('packages/calibration/results/2026-10-08-w50-g1-current3')
FAILED=('apple-macos-27.0-2x-dark-standard-glass0.25','css','cell-grey-064-s160__inactive')
DL5H='''DL5h (parent, before any further current launch, candidate or exposure). Current attempt 2 (root
b775ce5f…) stopped at draw 502 (glass0.25/2x/receded/CSS cell-grey-064-s160__inactive):
deterministic:false, repeatNoise 1.9073e-6 (6 channel-code units over the frame); the second load
was not retained. Ruled, prospectively and for EVERY W50 web phase alike (current, fit, gate,
exposure, so a one-shot read cannot be lost to transport):
(a) attempt 2 is preserved as burned evidence; a separately sealed current recovery (attempt 3)
keeps attempt 2's 501 validated draws by content hash and recaptures the failed cell plus every
unfinished fixed member; no other draw is re-rendered or relabelled;
(b) every web draw retains BOTH repeat images;
(c) admission stays byte identity by default. A non-identical repeat is admitted only if both
images pass the unchanged geometry/source/numerical checks AND every declared statistic of that
cell (levels and T1 where it has them), computed on each image, agrees within 0.1 B (0.05 code at
the 0.5-code floor). The reading is the first image's; the pair difference is recorded per cell.
A repeat outside that band stops the run as an instrument fault, never a verdict.
DL5h clarifications (parent): (i) the band is 0.1 x the cell statistic's native repeat bar (0.05 code
at the 0.5-code floor), not 0.1 B; (ii) a cell with no finite source-bound repeat budget for every
declared statistic (e.g. owner-only, B null) keeps byte-identity admission, no new statistic is
invented; (iii) attempt 2's 501 draws stand as legacy byte-identical pairs: one preserved PNG plus
production's original equality attestation, never a manufactured second image; every new draw keeps
both PNGs and reports.
'''


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(path):return json.loads(Path(path).read_text())


def checked(repo,pin,external=False):
    if not isinstance(pin,dict) or not isinstance(pin.get('path'),str):raise ValueError('Missing recovery content pin')
    path=(Path(repo)/pin['path']).resolve()
    if (not external and not path.is_relative_to(Path(repo).resolve())) or not path.is_file() or sha(path)!=pin.get('sha256'):
        raise ValueError('Changed or missing recovery content pin')
    return path


def sealed(path):
    side=Path(str(path)+'.sha256')
    if not side.is_file() or side.read_text()!=f'{sha(path)}  {path.name}\n':raise ValueError('Prior recovery authority seal changed')
    return load(path)


def flatten(batches):
    result=[]
    for bi,batch in enumerate(batches):
        if batch.get('schema')!='w50-g1-batch-1' or batch.get('phase')!='current':raise ValueError('Recovery requires fixed current batches')
        for ri,run in enumerate(batch['runs']):
            for si,scene in enumerate(run['scenes']):
                result.append(dict(batchIndex=bi,runIndex=ri,sceneIndex=si,ordinal=len(result)+1,
                    profile=run['profile'],renderer=run['renderer'],scene=scene,sceneSource=run['sceneSource'],
                    candidate=run['candidate']))
    return result


def derive(repo,directory,authority,batches):
    repo,directory=Path(repo).resolve(),Path(directory).resolve()
    if directory!=repo/CURRENT/'execution' or not isinstance(authority,dict) or set(authority)!={
            'attempt','priorRoot','priorClaim','priorFailure','ruling','gpuReplayProof'} or authority['attempt']!=3:
        raise ValueError('Only the declared DL5h current attempt three is authorised')
    paths={k:checked(repo,authority[k]) for k in authority if k!='attempt'}
    if (paths['priorRoot']!=repo/PRIOR/'execution/current-instrument-root.json' or
            paths['priorFailure']!=repo/PRIOR/'evidence/current-attempt2/failure.json' or
            paths['gpuReplayProof']!=repo/PRIOR/'execution/gpu-replay-proof.json' or paths['ruling'].read_text()!=DL5H):
        raise ValueError('Recovery must name exact burned attempt2 and DL5h ruling')
    prior=sealed(paths['priorRoot']);failure=load(paths['priorFailure']);proof=sealed(paths['gpuReplayProof'])
    old_sources=prior.get('closure',{}).get('sources',{})
    if str(PRIOR/'web/adapter.py') not in old_sources:
        raise ValueError('Recovery lacks the original source-owned new-bed validation closure')
    for path,digest in old_sources.items():checked(repo,{'path':path,'sha256':digest})
    if (prior.get('schema')!='w50-g1-current-instrument-root-1' or
            failure.get('schema')!='w50-current-attempt-failure-1' or
            failure.get('status')!='STOPPED_INCOMPLETE_NO_RETRY' or failure.get('candidateVerdict')!='NOT_READ' or
            failure.get('successfulBatchResult') is not False or failure.get('root')!=authority['priorRoot'] or
            failure.get('claim')!=authority['priorClaim'] or failure.get('reportCount')!=502 or
            tuple(failure.get('failure',{}).get(k) for k in ('profile','renderer','scene'))!=FAILED):
        raise ValueError('Recovery is not the declared burned draw502 instrument fault')
    contract_path=checked(repo,failure['contract']);contract=sealed(contract_path);claim=load(paths['priorClaim'])
    if (contract.get('phase')!='current' or contract.get('executionRootSha256')!=authority['priorRoot']['sha256'] or
            paths['priorClaim']!=Path(str(contract_path)+'.started.json') or Path(str(contract_path)+'.result.json').exists() or
            claim.get('contractSha256')!=failure['contract']['sha256'] or
            claim.get('batchSha256')!=contract.get('batch',{}).get('sha256') or claim.get('phase')!='current'):
        raise ValueError('Prior claim/contract is not burned attempt2')
    prior_batches=[load(checked(repo,p)) for p in prior['currentBatches']]
    if contract.get('batch')!=prior['currentBatches'][0] or len(batches)!=len(prior_batches):
        raise ValueError('Recovery changed ordered fixed batch population')
    members=flatten(prior_batches)
    if (len(members)!=799 or sum(m['sceneSource']=='w50' for m in members)!=672 or
            sum(m['sceneSource']=='canonical' for m in members)!=127 or
            tuple(members[501][k] for k in ('profile','renderer','scene'))!=FAILED):
        raise ValueError('Prior declared membership is not the DL5h population')
    if flatten(batches)!=members:raise ValueError('Recovery may not add/drop/reorder/relabel any original member')
    for old,new in zip(prior_batches,batches):
        if old['cohort']!=new['cohort'] or len(old['runs'])!=len(new['runs']):raise ValueError('Recovery changed original cohort/run grouping')
        for before,after in zip(old['runs'],new['runs']):
            allowed={'captureRoot','matrixPath','webSourceClosure'}
            if {k:v for k,v in before.items() if k not in allowed}!={k:v for k,v in after.items() if k not in allowed}:
                raise ValueError('Recovery changes a held run/candidate/fixture field')
    tree=Path(failure['tree']).resolve()
    if Path(claim['output']).resolve()!=tree:raise ValueError('Failure manifest names another original capture tree')
    files=failure.get('files',[])
    if len({f['path'] for f in files})!=len(files):raise ValueError('Failure artifact index contains duplicates')
    index={f['path']:f for f in files}
    def artifact(path):
        path=Path(path).resolve()
        if not path.is_relative_to(tree):raise ValueError('Prior capture escapes failed tree')
        item=index.get(str(path.relative_to(tree)))
        if not item:raise ValueError('Original required artifact missing from pinned failure inventory')
        pin={'path':str(path),'sha256':item['sha256']}
        checked(repo,pin,external=True)
        return pin
    retained=[]
    for member in members[:502]:
        run=prior_batches[member['batchIndex']]['runs'][member['runIndex']]
        folder=Path(run['captureRoot'])/member['scene'];tier=member['renderer']
        artifacts={k:artifact(p) for k,p in (
            ('png',folder/f'{member["scene"]}__{tier}.png'),('cell',folder/f'cell__{tier}.json'),
            ('report',folder/f'report__{tier}.json'))}
        metadata=load(artifacts['cell']['path'])
        if member['ordinal']==502:
            if metadata.get('deterministic') is not False:raise ValueError('Failed502 has no original failed equality attestation')
            continue
        if metadata.get('renderer')!=tier or metadata.get('deterministic') is not True or \
                type(metadata.get('repeatNoise')) not in (int,float) or metadata['repeatNoise']!=0:
            raise ValueError('Retained member lacks original true/zero byte-equality attestation')
        extra={}
        for name,path in [('record',folder/'w50-capture.json'),('index',Path(run['matrixPath'])),
                          ('request',Path(run['captureRoot'])/f'request-{member["scene"]}.json'),
                          ('census',Path(run['captureRoot'])/f'census-{member["scene"]}.json'),
                          ('log',Path(run['captureRoot'])/f'capture-{member["scene"]}.log')]:
            if str(path.resolve().relative_to(tree)) in index:extra[name]=artifact(path)
        retained.append({**member,'artifacts':artifacts,'originalEvidence':extra})
    if (proof.get('schema')!='w50-current2-gpu-replay-proof-1' or proof.get('status')!='BYTE_IDENTICAL' or
            proof.get('executionRootSha256')!=authority['priorRoot']['sha256'] or
            proof.get('contractSha256')!=failure['contract']['sha256'] or
            proof.get('claimSha256')!=authority['priorClaim']['sha256'] or len(proof.get('cells',[]))!=42):
        raise ValueError('Recovery lacks the original passed GPU42 proof')
    for old,cell in zip(retained[:42],proof['cells']):
        if (any(old[k]!=cell.get(k) for k in ('profile','renderer','scene')) or
                Path(old['artifacts']['png']['path']).resolve()!=Path(cell.get('replacementPng',{}).get('path','')).resolve() or
                old['artifacts']['png']['sha256']!=cell.get('replacementPng',{}).get('sha256')):
            raise ValueError('Passed GPU42 proof differs from retained original membership/bytes')
    return {'schema':'w50-current3-recovery-partition-1','authority':authority,'priorBatches':prior['currentBatches'],
            'priorContract':failure['contract'],'priorHost':prior['newBedHost'],
            'retained':retained,'fresh':members[501:]}


def fresh_run(partition,batch_index,run_index,run):
    scenes=[m['scene'] for m in partition['fresh'] if (m['batchIndex'],m['runIndex'])==(batch_index,run_index)]
    return {**run,'scenes':scenes} if scenes else None
