"""Read-only DL5 verification: derive exact members again from pinned static sources.

A self-consistent membership hash is insufficient: values, bands, epsilons and cost ceilings
must equal their original source records. This never opens a W50 gate payload, performs a
render, scores a non-fit candidate, or grants execution authority.
"""
import importlib.util
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('w51_dl5_declaration_build',HERE/'build.py')
B=importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)


def verify():
    B.verify_previous()
    witness=B.load(HERE/'membership-witness.json')
    B.require(witness['schema']=='w51-membership-witness-3' and witness['ruling']=='W51-DL5',
              'Declaration witness does not name DL5')
    names={'build.py','check.py','test_check.py','declared-costs.json','ruling.txt','clarifications.txt',
           'landing-policy.real.json','landing-policy.synthetic.json','amendment.json'}
    B.require(set(witness['files'])==names,'Declaration witness dropped or added an artifact')
    for name,item in witness['files'].items():
        B.require(B.checked(item)==HERE/name,'Witness names another declaration file')
    amendment=B.load(HERE/'amendment.json')
    real,synthetic,frozen=B.frozen_inputs()
    B.require(amendment['schema']=='w51-dl5-content-amendment-1' and
              amendment['ruling']==B.pin(HERE/'ruling.txt') and
              amendment['clarifications']==B.pin(HERE/'clarifications.txt') and
              amendment['declaredCosts']==B.pin(HERE/'declared-costs.json') and
              amendment['heldDeclaration']==B.pin(B.V2/'membership-witness.json'),
              'Amendment changed its ruling, cost or previous-declaration authority')
    B.require(amendment['heldScientificIdentities']=={
        k:frozen[k] for k in ('candidate','fitEvidence')},'Amendment changes the fixed candidate/fit')
    B.require(amendment['heldPopulations']=={phase:B.pin(B.V2/(phase+'-population.json'))
        for phase in ('gate','exposure','rehearsal')},'Amendment changes original populations')
    for item in amendment['retainedArtifacts']:B.checked(item)
    held={str(B.checked(p)) for p in amendment['retainedArtifacts']}
    B.require({str(p) for directory in (B.WAVE/'declaration',B.V2)
               for p in directory.iterdir() if p.is_file()}<=held,'Previous declaration artifact omitted')
    B.require(amendment['preGateAttestation']=={
        'actualGateSlotAbsent':True,'namespace':str(B.WAVE)},'Missing prospective pre-gate declaration')
    B.require(amendment['exceptionKeysSha256']==B.digest([e['key'] for e in real['exceptions']]),
              'Cost key declaration changed')
    for name,data in (('real',real),('synthetic',synthetic)):
        item=B.pin(HERE/('landing-policy.'+name+'.json'))
        B.require(amendment['landingPolicies'][name]==item,'Policy is not amendment-bound')
        policy=B.validate_policy(B.read(item),data)
        B.require(witness['counts'][name]=={'aggregates':len(policy['aggregates']),
                  'completeKeys':len(policy['completeKeys']),'exceptions':len(policy['exceptions'])},
                  'Policy witness counts differ')
    return witness


if __name__=='__main__':
    try:
        verify()
        print('W51 DL5 declaration intact: exact source-owned members, costs and epsilons; no execution seal.')
    except (ValueError,OSError,KeyError,TypeError) as error:
        print('W51 DL5 declaration refused: '+str(error),file=sys.stderr)
        raise SystemExit(1)
