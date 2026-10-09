"""Authenticate one complete capture batch under its actual, already-validated root.

This helper never combines phase statistics. It preserves each member's real root,
contract and output. Optical/repeat semantics stay in the immutable source-owned
archival helper and both-report validators used by the analytical consumer.
"""
from pathlib import Path
import types

HERE=Path(__file__).resolve().parent
C=types.ModuleType('w50_canonical3_evidence_common');C.__file__=str(HERE/'common.py')
exec(compile((HERE/'common.py').read_bytes(),C.__file__,'exec'),C.__dict__)


def completed_batch(repo,root_pin,root,batch_pin,result_pin):
    repo=Path(repo).resolve();root_path=C.checked(repo,root_pin)
    if C.sealed(root_path)!=root or batch_pin not in root['currentBatches']:
        raise ValueError('Completed batch is outside its actual original root')
    batch=C.load(C.checked(repo,batch_pin))
    contract_path=root_path.parent/'current-instrument'/f'{batch_pin["sha256"]}.json'
    contract=C.sealed(contract_path)
    if (contract.get('schema')!='w50-g1-phase-contract-1' or contract.get('phase')!='current' or
            contract.get('executionRootSha256')!=root_pin['sha256'] or contract.get('batch')!=batch_pin or
            contract.get('cohort')!=batch['cohort'] or contract.get('preFitEvidence') is not None or
            C.checked(repo,result_pin)!=Path(str(contract_path)+'.result.json')):
        raise ValueError('Completed result differs from its actual fixed contract')
    result=C.D.result_for(contract_path);claim_path=Path(str(contract_path)+'.started.json');claim=C.load(claim_path)
    if (claim.get('phase')!='current' or claim.get('batchSha256')!=batch_pin['sha256'] or
            claim.get('numericalAdmission') is not None or result['report'].get('status')!='CAPTURED' or
            'analysis' in result['report'] or result['report'].get('captures')!=result.get('captures')):
        raise ValueError('Current chain is incomplete or contains phase analysis')
    admission=C.source(C.PRIOR/'execution/admission.py','w50_canonical3_capture_membership')
    if admission.validate_captures(batch,result['captures'],claim['output'])!=result['captureReceipt']:
        raise ValueError('Completed receipt changed complete original membership')
    if C.D.repeat_artifact_pins(repo,result['captures'])!=result.get('repeatReceipt'):
        raise ValueError('Completed result omitted paired artifacts or proof')
    if root.get('recovery',{}).get('schema')=='w50-current3-recovery-partition-1':
        C.D.verify_recovery_records({'batchPath':str(C.checked(repo,batch_pin))},result['captures'],doc=root)
    elif any(r.get('origin')!={'kind':'fresh-canonical-recovery'} for r in result['captures']['captures']):
        raise ValueError('Canonical recovery cannot carry retained/relabelled captures')
    chain=[root_pin,batch_pin,result_pin]
    for p in (Path(str(root_path)+'.sha256'),contract_path,Path(str(contract_path)+'.sha256'),claim_path,
              Path(str(contract_path)+'.result.json.sha256')):
        if not p.exists():raise ValueError('Completed chain sidecar missing')
        chain.append(C.pin(repo,p))
    members=[]
    for receipt in result['captures']['captures']:
        runs=[run for run in batch['runs'] if all(run[k]==receipt[k] for k in ('profile','renderer','candidate')) and receipt['scene'] in run['scenes']]
        if len(runs)!=1 or receipt.get('sceneSource')!=runs[0]['sceneSource'] or receipt.get('lane')!='current':
            raise ValueError('Capture differs from its actual run/lane/source')
        members.append(dict(instrument=root_pin,run=runs[0],receipt=receipt,output=claim['output'],batch=batch_pin,
            contract=C.pin(repo,contract_path),claim=C.pin(repo,claim_path),result=result_pin))
    return {'chainPins':chain,'members':members,'result':{'pin':result_pin,'document':result}}
