"""Prospective live-root admission. No fallback component or pre-fit PASS exists here."""
import os
from pathlib import Path
import re
import types
H=Path(__file__).resolve().parent
C=types.ModuleType('w50_live_authority_common');C.__file__=str(H/'common.py')
exec(compile((H/'common.py').read_bytes(),C.__file__,'exec'),C.__dict__)
D=C.D
ROLES={'capture','native','measurement','fit','judge','owner','initializer'}
OWN=('guard','common','authority','dispatch','lifecycle','quarantine','admission','prefit','native_evidence','owner_evidence')


def instrument_shape(roles):
    if not isinstance(roles,dict) or set(roles)!=ROLES:raise ValueError('Every real live component must be registered before seal')
    for role in roles.values():
        if not isinstance(role,dict) or set(role)!={'entrypoint','config'}:raise ValueError('Component needs source and config')
        for item in role.values():
            if not isinstance(item,dict) or set(item)!={'path','sha256'} or not isinstance(item['path'],str) or not re.fullmatch('[a-f0-9]{64}',item.get('sha256','')):
                raise ValueError('Component needs exact content pins, not a placeholder')


def instrument_interface(role,module):
    names={'capture':('capture','verify','recover'),'native':('admit','prepare','verify'),
        'owner':('admit','evaluate'),'fit':('evaluate','fit_record'),
        'initializer':('initialize','assemble','bind_arguments')}.get(role,('evaluate',))
    if any(not callable(getattr(module,name,None)) for name in names):
        raise ValueError('Registered component lacks its actual role interface')


def validate_body(path,doc):
    repo=Path(doc['repo']).resolve();path=Path(path).resolve()
    if (path.parent!=repo/'packages/calibration/results/2026-10-08-w50-g1-fit/live-execution' or
            path.name!='execution-root.json' or doc.get('schema')!='w50-g1-execution-root-1' or
            doc.get('lifecycle')!='logical-phase-attempts-1' or doc.get('quarantine')!='instrument-api-role-discipline-1' or
            any(k in doc for k in ('currentInstrument','currentResults'))):raise ValueError('Wrong live lifecycle root')
    instrument_shape(doc.get('instruments'))
    sources=doc['closure']['sources']
    for relative,digest in sources.items():D.checked(repo,{'path':relative,'sha256':digest})
    for name in OWN:
        target=path.parent/(name+'.py')
        if sources.get(str(target.relative_to(repo)))!=D.sha(target):raise ValueError('Unpinned live bootstrap source')
    for name in ('guard','admission','prefit','native_evidence','owner_evidence'):
        if D.sha(path.parent/(name+'.py'))!=D.sha(C.CURRENT3/'execution'/(name+'.py')):
            raise ValueError('Original pre-fit/admission algorithm changed')
    if D.checked(repo,doc['bootstrap'])!=path.parent/'dispatch.py':raise ValueError('Wrong actual dispatcher bootstrap')
    D.checked(repo,doc['probe'])
    if sources.get(doc['probe']['path'])!=doc['probe']['sha256']:raise ValueError('Probe is not source-bound')
    for name,role in doc['instruments'].items():
        for item in role.values():
            D.checked(repo,item)
            if item not in doc['inputs']:raise ValueError('Component source/config not prospectively registered')
        if sources.get(role['entrypoint']['path'])!=role['entrypoint']['sha256']:raise ValueError('Component absent from source closure')
        instrument_interface(name,C.source(D.checked(repo,role['entrypoint']),'w50_live_interface_'+name))
    for item in doc['inputs']:D.checked(repo,item)
    if doc.get('recoveryRuling') not in doc['inputs']:raise ValueError('DL5k ruling is not prospectively bound')
    D.checked(repo,doc['recoveryRuling'])
    one,two=(D.sealed(D.checked(repo,doc[name])) for name in ('partOne','partTwo'))
    if two['partOneSha256']!=doc['partOne']['sha256'] or two['candidateDomain']!=doc['candidateDomain'] or tuple(two['requiredEvidence'])!=D.PROOFS:
        raise ValueError('Original declaration/domain/proof population changed')
    for part in (one,two):
        for item in part['sources']:D.checked(repo,item)
    D.declared_inputs(repo,D.checked(repo,doc['partOne']),D.checked(repo,doc['partTwo']),D.checked(repo,doc['references']),D.checked(repo,doc['manifest']))
    original=D.load(D.checked(repo,doc['references']));D.verify_phase_dependencies(doc,original['cells'])
    composition=C.source(C.CANONICAL3/'execution/composition.py','w50_live_actual_current_composition')
    current=composition.validate_completed_current(repo,doc['currentComposition'])
    current_authority(doc,D.load(D.checked(repo,doc['currentEvidence'])),current)
    old=current['roots'][0]['document']
    if doc['repeatAdmission']!=old['repeatAdmission'] or doc['newBedHost']!=old['newBedHost']:
        raise ValueError('Live/current host or repeat policy differs')
    for item in [*doc['repeatAdmission'].values(),doc['newBedHost']]:
        if item not in doc['inputs']:raise ValueError('Original host/repeat input omitted')
    prefit=C.source(path.parent/'prefit.py','w50_live_prefit_validation')
    prefit.validate_exemptions(original,D.load(D.checked(repo,doc['manifest'])),doc['reportedKeys'])
    prefit.validate_empty_eligibility(original,D.load(D.checked(repo,doc['manifest'])),doc['reportedKeys'],doc['emptySupportKeys'])
    if doc['ownerBudgetKeys']!=D.owner_budget_keys(original['cells']):raise ValueError('Owner null-budget membership changed')
    if doc['ownerBudgetKeys']:
        if doc['ownerContracts'] not in doc['inputs']:raise ValueError('Owner snapshot omitted')
        owner=C.source(path.parent/'owner_evidence.py','w50_live_owner_reference')
        owner.OwnerEvidence(repo,doc['ownerContracts'],D.owner_source(doc)).finish()
    return doc


def current_authority(doc,evidence,current):
    """The completed-current evidence names the validated composition's chains exactly, in order."""
    if (evidence.get('schema')!='w50-completed-current-evidence-2' or evidence.get('status')!='EVIDENCE_ONLY' or
            'currentInstrument' in evidence or evidence.get('currentComposition')!=doc['currentComposition'] or
            evidence.get('currentInstruments')!=[r['pin'] for r in current['roots']] or
            evidence.get('currentResults')!=[r['pin'] for r in current['resultDocuments']] or
            evidence.get('chainPins')!=current['chainPins'] or
            evidence.get('originals',{}).get('references')!=doc['references'] or
            doc['baselineDocuments']!=current['candidates']):raise ValueError('Current evidence lacks genuine composed authority')
    for item in [doc['currentComposition'],doc['currentEvidence'],*current['chainPins']]:
        if item not in doc['inputs']:raise ValueError('Current composition/evidence chain omitted from root')


def root_doc(path):return validate_body(path,D.sealed(path))


def verify_prefit(path,doc):
    """current3's verify_prefit, then LIVE's lineage check on the same sealed evidence."""
    pinned=D.verify_prefit(path,doc)
    prefit_lineage(doc['repo'],D.sealed(Path(path).resolve().parent/'pre-fit-evidence.json'))
    return pinned


FIT_REL=Path('packages/calibration/results/2026-10-08-w50-g1-fit')
SUPERSESSIONS=('owner/r2/supersedes.json','completion/registered-2/supersedes.json')


def _pins(value,out):
    if isinstance(value,dict):
        if isinstance(value.get('path'),str) and isinstance(value.get('sha256'),str):out.append(value)
        for item in value.values():_pins(item,out)
    elif isinstance(value,list):
        for item in value:_pins(item,out)
    return out


def _lexical(repo,path):return os.path.normpath(os.path.join(str(repo),path))


def prefit_lineage(repo,evidence):
    """Tie the pre-fit evidence to the rebuilt proofs (second pre-seal review P2).

    current3's verify_prefit validates each proof alone, so a proof superseded by the DL5l-type
    reference recovery (DL5n) still validates beside the evidence that replaced it. Two
    supersession records name what that recovery replaced: owner/r2/supersedes.json and
    completion/registered-2/supersedes.json, each under its 'superseded' key. A superseded
    assembly archive also names, by content, the completed inventory it archived. Refused: any
    pin, anywhere in the evidence or in one of its proofs, that names a superseded file (by its
    lexically resolved path) or a superseded completed inventory (by content hash, so its live
    copy under any name). Required: referenceCompletion's sources contain the evidence's own
    completed inventory, exactly that pin."""
    repo=Path(repo);paths=set();inventories=set()
    for name in SUPERSESSIONS:
        record=D.load(repo/FIT_REL/name)
        if not isinstance(record.get('superseded'),dict):raise ValueError('Supersession record names nothing superseded')
        paths|={_lexical(repo,item['path']) for item in _pins(record['superseded'],[])}
        archive=record['superseded'].get('archive')
        if archive is not None:
            manifest=D.load(D.checked(repo,archive))
            if manifest.get('schema')!='w50-reference-assembly-archive-1':raise ValueError('Superseded archive is not an assembly archive')
            inventories.add(manifest['completedReferences']['original']['sha256'])
    documents=[('evidence',evidence)]+[(kind,D.load(D.checked(repo,item))) for kind,item in sorted(evidence['evidence'].items())]
    for kind,document in documents:
        for item in _pins(document,[]):
            if _lexical(repo,item['path']) in paths or item['sha256'] in inventories:
                raise ValueError('Pre-fit '+kind+' pins evidence a recorded recovery superseded')
    completion=dict(documents)['referenceCompletion']
    if evidence['references'] not in completion.get('sources',[]):
        raise ValueError('referenceCompletion does not complete the pre-fit evidence\'s own inventory')


def seal_root(path,document):
    """Seal only a fully assembled real registry; pre-fit evidence is a subsequent fixed seal."""
    validate_body(path,document)
    repo=Path(document['repo']);guard=C.source(C.CURRENT3/'execution/guard.py','w50_live_seal_guard')
    actual=guard.discover(repo,D.checked(repo,document['probe']),document['closure']['sources'])
    if actual!=document['closure']:raise ValueError('Unexercised live source closure/environment')
    return D.write_sealed(path,document)
