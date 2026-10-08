"""DL5k canonical recovery after burned attempt3: zero retained canonical records.

Raw compare output is failed transport evidence, not a completed phase reading. The
new-bed result remains in its original chain; only the original127 canonical members
are admitted here. This is not a generic retry or partial scientific-reading interface.
"""
import copy
from pathlib import Path
import types

HERE=Path(__file__).resolve().parent
C=types.ModuleType('w50_canonical3_common');C.__file__=str(HERE/'common.py')
exec(compile((HERE/'common.py').read_bytes(),C.__file__,'exec'),C.__dict__)
PRIOR=Path('packages/calibration/results/2026-10-08-w50-g1-current3')
CURRENT=Path('packages/calibration/results/2026-10-08-w50-g1-canonical3')
FAILED=('apple-macos-27.0-1x-dark-standard-glass0.25','css','dark-solid__capsule-button__rest')
DL5K='''DL5k (parent, standing; after canonical attempt 3 stopped on a census refusal of a foreign
Playwright Chrome, since exited). An OPERATIONAL stop (census refusal, transport/admission fault,
lease loss) before a phase's result exists and before any statistic of that phase is computed is
recovered, in every W50 web phase including the one exposure, by: preserving the burned attempt
with its claim/log/artifact hashes; sealing a recovery naming it and this ruling, which keeps the
already-validated draws by content hash and captures only the remaining fixed members under the
unchanged admission (DL5h); launching only when the census reads clean, never by touching another
owner's process. A recovery never changes membership, candidate bytes, rule or reference, and
never computes a statistic on a partial phase. The worker applies this without a new ruling and
reports each use.
'''


def fixed_batch(original,fresh):
    if original.get('schema')!='w50-g1-batch-1' or original.get('phase')!='current':
        raise ValueError('Recovery requires original current batch')
    members=[]
    for run in original.get('runs',[]):
        if run.get('sceneSource')!='canonical':raise ValueError('Only canonical members may be recovered')
        members.extend((run['profile'],run['renderer'],s) for s in run['scenes'])
    if len(members)!=127 or len(set(members))!=127:raise ValueError('Recovery must cover original127 canonical members')
    def scientific(batch):
        result=copy.deepcopy(batch)
        for run in result.get('runs',[]):
            for key in ('captureRoot','matrixPath','webSourceClosure'):run.pop(key,None)
        return result
    if scientific(original)!=scientific(fresh):raise ValueError('Recovery changed original membership/candidate/run grouping')
    return members


def failed_inventory(repo,failure):
    if (failure.get('schema')!='w50-current-attempt-failure-1' or
            failure.get('status')!='STOPPED_INCOMPLETE_NO_RETRY' or failure.get('candidateVerdict')!='NOT_READ' or
            failure.get('successfulBatchResult') is not False or failure.get('validatedDrawCount')!=0 or
            failure.get('repeatAdmissionCount')!=0 or failure.get('reportCount')!=1 or failure.get('retainedPairCount')!=1 or
            failure.get('failure',{}).get('kind')!='CLASSIFYING_CENSUS_REFUSAL' or
            tuple(failure.get('failure',{}).get(k) for k in ('profile','renderer','scene'))!=FAILED):
        raise ValueError('Not the zero-validated canonical attempt3 census failure')
    tree=Path(failure['tree']).resolve();files=failure.get('files',[])
    if failure.get('fileCount')!=len(files) or len({f['path'] for f in files})!=len(files):
        raise ValueError('Failed file inventory count/uniqueness changed')
    actual={p.relative_to(tree).as_posix() for p in tree.rglob('*') if p.is_file()}
    if actual!={f['path'] for f in files}:raise ValueError('Failed tree changed after preservation')
    pins=[]
    for item in files:
        p=(tree/item['path']).resolve()
        if (not p.is_relative_to(tree) or p.stat().st_size!=item['size'] or C.sha(p)!=item['sha256'] or
                p.name=='complete.json' or p.name.startswith('repeat-admission__')):
            raise ValueError('Failed artifact changed or contains a validated canonical completion')
        pins.append({'path':str(p),'sha256':item['sha256']})
    census_pin=failure['failure']['census']
    if census_pin not in pins:raise ValueError('Census is outside preserved failed tree')
    census=C.load(census_pin['path'])
    if (census.get('passes') is not False or census.get('refusals')!=failure['failure'].get('refusals') or
            'captureProcessPresent' not in census.get('refusals',[])):
        raise ValueError('Failure lacks original census refusal')
    return pins


def failed_log(repo,failure):
    item=failure['log'];path=(Path(repo)/item['path']).resolve()
    if not path.is_file() or C.sha(path)!=item['sha256']:raise ValueError('Failed dispatcher log changed')
    return item


def derive(repo,directory,authority,fresh):
    repo,directory=Path(repo).resolve(),Path(directory).resolve()
    if directory!=repo/CURRENT/'execution' or not isinstance(authority,dict) or set(authority)!={
            'priorRoot','completedNewbed','priorContract','priorClaim','priorFailure','ruling'}:
        raise ValueError('Recovery authority must name exact original completed and burned chains')
    paths={k:C.checked(repo,v) for k,v in authority.items()}
    if (paths['priorRoot']!=repo/PRIOR/'execution/current-instrument-root.json' or
            paths['priorFailure']!=repo/PRIOR/'evidence/current-canonical-attempt3/failure.json' or
            paths['ruling'].read_text()!=DL5K):raise ValueError('Recovery does not name canonical attempt3 and DL5k')
    prior=C.D.root_doc(paths['priorRoot'])
    if len(prior['currentBatches'])!=2:raise ValueError('Original current instrument must have both fixed batches')
    original=C.load(C.checked(repo,prior['currentBatches'][1]));members=fixed_batch(original,fresh)
    contract=C.sealed(paths['priorContract']);claim=C.load(paths['priorClaim']);failure=C.load(paths['priorFailure'])
    if (paths['priorContract']!=paths['priorRoot'].parent/'current-instrument'/f'{prior["currentBatches"][1]["sha256"]}.json' or
            paths['priorClaim']!=Path(str(paths['priorContract'])+'.started.json') or
            Path(str(paths['priorContract'])+'.result.json').exists() or
            contract.get('executionRootSha256')!=authority['priorRoot']['sha256'] or contract.get('phase')!='current' or
            contract.get('batch')!=prior['currentBatches'][1] or contract.get('cohort')!=original['cohort'] or
            contract.get('preFitEvidence') is not None or claim.get('phase')!='current' or
            claim.get('contractSha256')!=authority['priorContract']['sha256'] or
            claim.get('batchSha256')!=prior['currentBatches'][1]['sha256'] or claim.get('numericalAdmission') is not None or
            failure.get('root')!=authority['priorRoot'] or failure.get('contract')!=authority['priorContract'] or
            failure.get('claim')!=authority['priorClaim'] or Path(claim['output']).resolve()!=Path(failure['tree']).resolve()):
        raise ValueError('Canonical attempt3 is not a preserved burned current claim')
    failed=failed_inventory(repo,failure)
    log=failed_log(repo,failure)
    failed_runs=[r for r in original['runs'] if (r['profile'],r['renderer'])==FAILED[:2] and FAILED[2] in r['scenes']]
    if len(failed_runs)!=1 or Path(failure['failure']['census']['path']).resolve()!=Path(failed_runs[0]['captureRoot'])/f'census-{FAILED[2]}.json':
        raise ValueError('Failure census is not the original failed run/scene')
    E=C.source(HERE/'evidence.py','w50_canonical3_original_evidence')
    chain=E.completed_batch(repo,authority['priorRoot'],prior,prior['currentBatches'][0],authority['completedNewbed'])
    if len(chain['members'])!=672 or any(m['run']['sceneSource']!='w50' for m in chain['members']):
        raise ValueError('Original new-bed result must contain exactly its completed672')
    return {'schema':'w50-canonical3-recovery-1','authority':authority,'originalBatch':prior['currentBatches'][1],
        'completedNewbed':authority['completedNewbed'],'retainedCanonical':[],
        'freshMembers':[list(m) for m in members],'failedArtifacts':failed,'failedLog':log}
