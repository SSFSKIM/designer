"""One completed-current population assembled from two genuine instrument chains.

The document is a content-pinned reader input, not another execution root or a
replacement result. No member is returned until all799 original members are present
in their actual completed results. Analytical consumers retain per-member root and
repeat ownership and run the immutable both-report validators before measuring.
"""
from pathlib import Path
import types

HERE=Path(__file__).resolve().parent
C=types.ModuleType('w50_canonical3_composition_common');C.__file__=str(HERE/'common.py')
exec(compile((HERE/'common.py').read_bytes(),C.__file__,'exec'),C.__dict__)


def validate_manifest(doc,original,recovery):
    if (set(doc)!={'schema','originalInstrument','chains'} or
            doc.get('schema')!='w50-completed-current-composition-1' or len(doc.get('chains',[]))!=2 or
            any(set(c)!={'instrument','batch','contract','result'} for c in doc['chains'])):
        raise ValueError('Composition requires exactly two actual completed chains')
    old,new=doc['chains']
    if (old['instrument']!=doc['originalInstrument'] or new['instrument']==old['instrument'] or
            recovery.get('recoveryAuthority',{}).get('priorRoot')!=old['instrument'] or
            old['batch']!=original['currentBatches'][0] or new['batch']!=recovery['currentBatches'][0] or
            old['result']!=recovery['recoveryAuthority']['completedNewbed'] or
            recovery.get('recovery',{}).get('originalBatch')!=original['currentBatches'][1]):
        raise ValueError('Composition changed original completed/burned chain ownership')
    for key in ('baselineDocuments','repeatAdmission','newBedHost'):
        if recovery.get(key)!=original[key]:raise ValueError('Composition changes baseline/repeat policy/new-bed host')


def validate_completed_current(repo,composition_pin):
    repo=Path(repo).resolve();doc=C.load(C.checked(repo,composition_pin))
    if doc.get('schema')!='w50-completed-current-composition-1' or len(doc.get('chains',[]))!=2:
        raise ValueError('Missing genuine two-chain completed-current composition')
    original_path=C.checked(repo,doc['originalInstrument']);original=C.D.root_doc(original_path)
    dispatcher=C.source(HERE/'dispatch.py','w50_canonical3_composition_dispatch')
    recovery_pin=doc['chains'][1]['instrument'];recovery=dispatcher.root_doc(C.checked(repo,recovery_pin))
    validate_manifest(doc,original,recovery)
    E=C.source(HERE/'evidence.py','w50_canonical3_composition_evidence')
    roots=[{'pin':doc['originalInstrument'],'document':original},{'pin':recovery_pin,'document':recovery}]
    members=[];pins=[composition_pin];results=[]
    for chain,root in zip(doc['chains'],roots,strict=True):
        result=E.completed_batch(repo,root['pin'],root['document'],chain['batch'],chain['result'])
        if any(m['contract']!=chain['contract'] for m in result['members']):
            raise ValueError('Composition names another actual phase contract')
        members.extend(result['members']);pins.extend(result['chainPins']);results.append(result['result'])
        for item in root['document']['inputs']:
            if item not in pins:pins.append(item)
    batches=[C.load(C.checked(repo,p)) for p in original['currentBatches']]
    expected=[(run['profile'],run['renderer'],scene,run['candidate']['sha256'],run['sceneSource'])
        for batch in batches for run in batch['runs'] for scene in run['scenes']]
    actual=[(m['receipt']['profile'],m['receipt']['renderer'],m['receipt']['scene'],m['receipt']['candidate']['sha256'],m['receipt']['sceneSource']) for m in members]
    if (len(expected)!=799 or len(set(expected))!=799 or actual!=expected or
            sum(m['run']['sceneSource']=='w50' for m in members)!=672 or
            sum(m['run']['sceneSource']=='canonical' for m in members)!=127):
        raise ValueError('Composition does not exactly preserve original ordered672+127 membership')
    unique=[]
    for item in pins:
        if item not in unique:unique.append(item)
    return {'chainPins':unique,'roots':roots,'resultDocuments':results,
        'candidates':original['baselineDocuments'],'members':members}
