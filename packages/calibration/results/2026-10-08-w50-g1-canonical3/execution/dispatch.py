"""DL5k canonical-only recovery; one new claim, unchanged127, actual old672 chain.

This bootstrap deliberately has no fit/gate/exposure interface. It reuses immutable
mechanical validators but owns its own real process capability; no old root, source,
claim or result is edited or impersonated. Both scientific phases must be complete
before the separate composition consumer grants analytical access.
"""
import copy
from pathlib import Path
import sys
import types

HERE=Path(__file__).resolve().parent
C=types.ModuleType('w50_canonical3_dispatch_common');C.__file__=str(HERE/'common.py')
exec(compile((HERE/'common.py').read_bytes(),C.__file__,'exec'),C.__dict__)
sha,load,pin,checked,sealed=C.sha,C.load,C.pin,C.checked,C.sealed
write_once,write_sealed=C.write_once,C.write_sealed
CURRENT_NAME=C.D.CURRENT_NAME
CURRENT_SCHEMA=C.D.CURRENT_SCHEMA
SLOTS=C.D.CURRENT_SLOTS
_ACTIVE=None
OWN=('dispatch.py','common.py','admission.py','recovery.py','evidence.py','composition.py')


def recovery_module():return C.source(HERE/'recovery.py','w50_canonical3_recovery')
def admission_module(doc):return C.D.admission_module(doc)
def result_for(contract):return C.D.result_for(contract)
def repeat_artifact_pins(repo,captures):return C.D.repeat_artifact_pins(repo,captures)


def validate_sources(repo,directory,sources,prior,adapter,probe):
    for relative,digest in sources.items():checked(repo,{'path':relative,'sha256':digest})
    for relative,digest in prior['closure']['sources'].items():
        if sources.get(relative)!=digest:raise ValueError('Recovery must preserve every old exercised Python source')
    for name in OWN:
        path=directory/name
        if sha(path)!=sha(HERE/name) or sources.get(str(path.relative_to(repo)))!=sha(path):
            raise ValueError('Recovery bootstrap not registered in source closure')
    if sha(directory/'admission.py')!=sha(C.PRIOR/'execution/admission.py'):
        raise ValueError('Original baseline/capture admission must remain unchanged')
    for item in (adapter,probe,prior['repeatAdmission']['entrypoint']):
        if sources.get(item['path'])!=item['sha256']:raise ValueError('Recovery entrypoint absent from source closure')
    if checked(repo,adapter)!=repo/recovery_module().PRIOR/'canonical/adapter.py':
        raise ValueError('Canonical recovery must use the immutable original canonical adapter')
    if checked(repo,probe)!=directory.parent/'current_probe.py':raise ValueError('Recovery probe is not its own entrypoint')


def preserve_environment(prior,closure):
    if closure.get('environment')!=prior['closure']['environment']:
        raise ValueError('Recovery interpreter/package environment differs from original current instrument')


def seal_current_root(repo,directory,authority,batch,probe,sources,inputs=()):
    repo,directory=Path(repo).resolve(),Path(directory).resolve();path=directory/CURRENT_NAME
    if path.exists() or Path(str(path)+'.sha256').exists():raise ValueError('Recovery already sealed; no amendment')
    batch_pin=pin(repo,batch);batch_doc=load(batch)
    R=recovery_module();recovery=R.derive(repo,directory,authority,batch_doc)
    prior=C.D.root_doc(checked(repo,authority['priorRoot']))
    adapter=pin(repo,repo/R.PRIOR/'canonical/adapter.py');probe_pin=pin(repo,probe)
    validate_sources(repo,directory,sources,prior,adapter,probe_pin)
    bound=list(prior['inputs'])
    for item in [*inputs,*authority.values(),prior['newBedHost'],*prior['repeatAdmission'].values()]:
        checked(repo,item)
        if item not in bound:bound.append(item)
    doc={k:copy.deepcopy(prior[k]) for k in ('partOne','partTwo','candidateDomain','references','manifest',
        'baselineDocuments','phaseDependencies','newBedHost','repeatAdmission')}
    doc.update(schema=CURRENT_SCHEMA,repo=str(repo),slots=SLOTS,bootstrap=pin(repo,directory/'dispatch.py'),
        adapter=adapter,probe=probe_pin,currentBatches=[batch_pin],inputs=bound,
        recoveryKind='DL5k-canonical-after-burned-attempt3',recoveryAuthority=authority,recovery=recovery)
    C.D.validate_batch(doc,batch,'current')
    guard=C.source(C.PRIOR/'execution/guard.py','w50_canonical3_seal_guard')
    doc['closure']=guard.discover(repo,probe,sources)
    preserve_environment(prior,doc['closure'])
    return write_sealed(path,doc)


def root_doc(path):
    path=Path(path).resolve();doc=sealed(path);repo=Path(doc['repo']).resolve()
    R=recovery_module()
    if (path!=repo/R.CURRENT/'execution'/CURRENT_NAME or doc.get('schema')!=CURRENT_SCHEMA or
            doc.get('slots')!=SLOTS or doc.get('recoveryKind')!='DL5k-canonical-after-burned-attempt3' or
            checked(repo,doc['bootstrap'])!=path.parent/'dispatch.py' or
            any(k in doc for k in ('judge','instruments','currentInstrument','currentResults')) or
            len(doc.get('currentBatches',[]))!=1):raise ValueError('Not the bounded canonical recovery root')
    prior=C.D.root_doc(checked(repo,doc['recoveryAuthority']['priorRoot']))
    validate_sources(repo,path.parent,doc['closure']['sources'],prior,doc['adapter'],doc['probe'])
    preserve_environment(prior,doc['closure'])
    for key in ('partOne','partTwo','candidateDomain','references','manifest','baselineDocuments',
                'phaseDependencies','newBedHost','repeatAdmission'):
        if doc.get(key)!=prior[key]:raise ValueError('Recovery changes original declaration/candidate/policy/host')
    for item in doc['inputs']:checked(repo,item)
    for item in [*prior['inputs'],*doc['recoveryAuthority'].values(),prior['newBedHost'],*prior['repeatAdmission'].values()]:
        if item not in doc['inputs']:raise ValueError('Recovery dropped original authority/source input')
    batch_path=checked(repo,doc['currentBatches'][0]);batch=load(batch_path)
    if R.derive(repo,path.parent,doc['recoveryAuthority'],batch)!=doc.get('recovery'):
        raise ValueError('Recovery partition or failed authority changed')
    C.D.validate_batch(doc,batch_path,'current')
    return doc


def current_contract(root,batch):
    root=Path(root).resolve();doc=root_doc(root)
    batch_doc,_=C.D.validate_batch(doc,batch,'current')
    target=root.parent/'current-instrument'/f'{sha(batch)}.json'
    return write_sealed(target,{'schema':'w50-g1-phase-contract-1','executionRootSha256':sha(root),
        'phase':'current','batch':pin(doc['repo'],batch),'cohort':batch_doc['cohort'],'preFitEvidence':None})


def require_context(context):
    if _ACTIVE is None or context is not _ACTIVE[0] or not C.D.lease_owned():
        raise ValueError('Canonical transport requires actual dispatcher capability and lease')
    if context!=_ACTIVE[1] or sha(context['contract'])!=_ACTIVE[2] or sha(context['batchPath'])!=_ACTIVE[3]:
        raise ValueError('Canonical recovery context/contract/batch mutated')
    return context


def require_render_admission(context,run,current=False):
    require_context(context)
    if current is not True or context['phase']!='current' or run not in context['batch']['runs'] or run.get('sceneSource')!='canonical':
        raise ValueError('Only unchanged declared canonical current runs are admitted')
    admission_module(_ACTIVE[4]).endpoints(_ACTIVE[4],run['candidate'],current=True)
    return run


def execute(root,contract,batch,output):
    global _ACTIVE
    root,contract,batch=map(lambda p:Path(p).resolve(),(root,contract,batch))
    doc=root_doc(root);repo=Path(doc['repo']);body=sealed(contract)
    expected_contract=root.parent/'current-instrument'/f'{sha(batch)}.json'
    batch_doc,expected=C.D.validate_batch(doc,batch,'current')
    if (contract!=expected_contract or body!={'schema':'w50-g1-phase-contract-1','executionRootSha256':sha(root),
            'phase':'current','batch':pin(repo,batch),'cohort':batch_doc['cohort'],'preFitEvidence':None}):
        raise ValueError('Invocation differs from its sealed recovery contract')
    output=Path(output).resolve()
    if output.exists() or output.is_relative_to(repo):raise ValueError('Recovery output must be fresh external scratch')
    for run in batch_doc['runs']:
        for key in ('captureRoot','matrixPath'):
            target=Path(run[key]).resolve()
            if not target.is_relative_to(output) or target==output:raise ValueError('Fresh run destination escaped its new invocation')
    guard=C.source(C.PRIOR/'execution/guard.py','w50_canonical3_guard')
    if guard.environment()!=doc['closure']['environment']:raise ValueError('Recovery interpreter/environment changed')
    guard.enforce(repo,doc['closure']['sources'])
    if guard.discover(repo,checked(repo,doc['probe']),doc['closure']['sources'])!=doc['closure']:
        raise ValueError('Recovery exercised source/import closure changed')
    with C.D.owned_gpu_lock():
        claim=Path(str(contract)+'.started.json')
        write_once(claim,{'phase':'current','contractSha256':sha(contract),'batchSha256':sha(batch),
            'output':str(output),'numericalAdmission':None,'gpuLease':C.D._LEASE['token']})
        output.mkdir(parents=True,exist_ok=False)
        context={'repo':str(repo),'executionRoot':str(root),'contract':str(contract),'batchPath':str(batch),
            'batch':batch_doc,'phase':'current','output':str(output),'expectedCells':expected,
            'baselineDocuments':doc['baselineDocuments'],'inputs':doc['inputs'],
            'phaseDependencies':doc['phaseDependencies'],'repeatAdmission':doc['repeatAdmission']}
        _ACTIVE=(context,copy.deepcopy(context),sha(contract),sha(batch),doc)
        sys.modules['w50_g1_dispatch']=sys.modules[__name__]
        try:
            adapter=C.source(checked(repo,doc['adapter']),'w50_canonical3_original_adapter')
            captures=adapter.execute_current(context);require_context(context)
            for record in captures.get('captures',[]):record['origin']={'kind':'fresh-canonical-recovery'}
            receipt=admission_module(doc).validate_captures(batch_doc,captures,output)
            repeat=C.source(checked(repo,doc['repeatAdmission']['entrypoint']),'w50_canonical3_original_repeat')
            for record in captures['captures']:
                runs=[run for run in batch_doc['runs'] if all(run[k]==record[k] for k in ('profile','renderer','candidate')) and record['scene'] in run['scenes']]
                if len(runs)!=1:raise ValueError('Repeat proof is outside its declared run')
                repeat.verify_receipt(context,runs[0],record)
            require_context(context)
            return write_sealed(Path(str(contract)+'.result.json'),{'contractSha256':sha(contract),'claimSha256':sha(claim),
                'report':{'status':'CAPTURED','captures':captures},'captures':captures,'captureReceipt':receipt,
                'repeatReceipt':repeat_artifact_pins(repo,captures)})
        finally:_ACTIVE=None


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('current','execute'))
    parser.add_argument('--root',required=True,type=Path)
    parser.add_argument('--batch',required=True,type=Path)
    parser.add_argument('--contract',type=Path)
    parser.add_argument('--out',type=Path)
    args=parser.parse_args()
    if args.command=='execute':
        if not args.contract or not args.out:parser.error('execute needs --contract and --out')
        print(execute(args.root,args.contract,args.batch,args.out))
    else:print(current_contract(args.root,args.batch))
