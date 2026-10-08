"""Prospective live-root admission. No fallback component or pre-fit PASS exists here.

A LIVE root is admitted only as the newest generation of its directory's chain (DL5o; common.py
names the chain and its per-root slots). A successor's 'supersedes' record names the root before
it exactly: its content pin, the commit that sealed it, the ruling that authorises the
succession (a text pinned among the successor's inputs that names that commit), and the
statement that nothing executed under it, with the slot area that statement covers. Every link
is re-checked at every admission, so a superseded root can never execute again and a successor
is never sealed, or admitted, over a predecessor whose slot area holds anything. That area
includes the predecessor's pre-fit evidence: every phase entry passes verify_prefit before it
claims an external output, so an empty area is the proof that no output was claimed either.
"""
import os
from pathlib import Path
import re
import subprocess
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


FIT_REL=Path('packages/calibration/results/2026-10-08-w50-g1-fit')
SUPERSESSION='w50-live-root-supersession-1'
LINK=('schema','root','sealingCommit','ruling','unexecuted')
UNEXECUTED=('No pre-fit evidence, phase contract, output claim, marker or attempt exists under the superseded '
    'root: every name in its slot area is absent, and every LIVE phase entry passes verify_prefit on that '
    'root\'s own pre-fit evidence before it claims an external output.')


def _git(repo,*args):return subprocess.run(['git','-C',str(repo),*args],capture_output=True)


def sealing_commit(repo,root,commit):
    """`commit` introduced this root and its sidecar, with exactly their present bytes."""
    repo=Path(repo).resolve();relative=str(Path(root).resolve().relative_to(repo))
    if not isinstance(commit,str) or not re.fullmatch('[0-9a-f]{40}',commit) or \
            _git(repo,'cat-file','-t',commit).stdout!=b'commit\n':
        raise ValueError('Sealing commit is not a commit of this repository')
    for name in (relative,relative+'.sha256'):
        blob=_git(repo,'cat-file','blob',f'{commit}:{name}')
        if blob.returncode or blob.stdout!=(repo/name).read_bytes():
            raise ValueError('Sealing commit does not hold the superseded root and its seal')
        if _git(repo,'cat-file','-e',f'{commit}^:{name}').returncode==0:
            raise ValueError('Sealing commit did not introduce the superseded root')


def unexecuted(repo,root):
    """The supersedes record's statement and the slot area it covers, as the record states it."""
    repo=Path(repo).resolve()
    return {'statement':UNEXECUTED,'slots':[{'directory':str(Path(folder).relative_to(repo)),'pattern':pattern}
                                           for folder,pattern in C.slot_area(root)]}


def ruling(repo,doc,record):
    """The ruling a link names is a text pinned among the successor's own inputs, opening with its
    id and naming the superseded root's sealing commit by an abbreviation of at least 7 digits."""
    item=record['ruling']
    if not isinstance(item,dict) or set(item)!={'id','text'} or not isinstance(item['id'],str) or \
            not re.fullmatch('DL[0-9]+[a-z]*',item['id']) or item['text'] not in doc['inputs']:
        raise ValueError('Supersession ruling is not prospectively bound')
    text=D.checked(repo,item['text']).read_text()
    if not text.startswith(item['id']+' ') or \
            not any(record['sealingCommit'].startswith(t) for t in re.findall(r'\b[0-9a-f]{7,40}\b',text)):
        raise ValueError('Supersession ruling does not name the root it supersedes')


def _link(repo,folder,n,doc):
    """Generation n's supersedes record against generation n-1; returns n-1's path and document."""
    record=doc.get('supersedes');prior=folder/C.root_name(n-1)
    if not isinstance(record,dict) or set(record)!=set(LINK) or record['schema']!=SUPERSESSION:
        raise ValueError('A successor LIVE root needs its exact supersedes record')
    if not prior.is_file() or record['root']!=D.pin(repo,prior):
        raise ValueError('Supersedes record does not pin the generation before it')
    prior_doc=D.sealed(prior)
    if prior_doc.get('repo')!=doc['repo']:raise ValueError('Superseded root names another repository')
    sealing_commit(repo,prior,record['sealingCommit'])
    ruling(repo,doc,record)
    if record['unexecuted']!=unexecuted(repo,prior):raise ValueError('Supersedes record misstates the superseded slot area')
    if C.slot_entries(prior):raise ValueError('Superseded root has executed history; no successor is sealed over it')
    return prior,prior_doc


def predecessors(path,doc):
    """The superseded roots below this LIVE root, nearest first, each as its pin and its seal's.

    Refuses a root off the chain's names or not the newest of its directory, a first root that
    supersedes anything, and every link below it (_link)."""
    path=Path(path).resolve();repo=Path(doc['repo']).resolve();n=C.generation(path.name)
    if n is None or path.name.endswith('.sha256'):raise ValueError('Wrong live lifecycle root')
    if C.superseded(path):raise ValueError('Superseded LIVE root: a later generation exists beside it')
    out=[]
    while n>1:
        prior,prior_doc=_link(repo,path.parent,n,doc)
        out+=[D.pin(repo,prior),D.pin(repo,Path(str(prior)+'.sha256'))]
        doc,n=prior_doc,n-1
    if 'supersedes' in doc:raise ValueError('The first LIVE root supersedes nothing')
    return out


def validate_body(path,doc):
    repo=Path(doc['repo']).resolve();path=Path(path).resolve()
    if (path.parent!=repo/FIT_REL/'live-execution' or doc.get('schema')!='w50-g1-execution-root-1' or
            doc.get('lifecycle')!='logical-phase-attempts-1' or doc.get('quarantine')!='instrument-api-role-discipline-1' or
            any(k in doc for k in ('currentInstrument','currentResults'))):raise ValueError('Wrong live lifecycle root')
    predecessors(path,doc)
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
    """current3's verify_prefit on this root's own evidence slot, then LIVE's lineage check on the
    same sealed evidence, with the chain's superseded roots among what it refuses (DL5o)."""
    roots=predecessors(path,doc)
    pinned=_verify_prefit(path,doc)
    prefit_lineage(doc['repo'],D.sealed(C.slot(path,'prefit')),roots)
    return pinned


def _verify_prefit(path, doc):
    """current3's verify_prefit with one change: the evidence is read from, and pinned at, this
    root's own slot (C.slot(path, 'prefit')) rather than the pre-fit-evidence.json every root of
    the directory would share. test_authority proves the copy by syntax tree."""
    repo = Path(doc['repo']); directory = Path(path).resolve().parent
    evidence = D.sealed(C.slot(path, 'prefit'))
    if evidence.get('partTwoSha256') != doc['partTwo']['sha256']:
        raise ValueError('Pre-fit evidence names another part two')
    pins = evidence.get('sources', [])
    for item in pins: D.checked(repo, item)
    for target in (Path(path), Path(str(path)+'.sha256')):
        if D.pin(repo, target) not in pins:
            raise ValueError('Pre-fit evidence did not prospectively pin execution root')
    if evidence.get('executionClosure') != doc['closure']:
        raise ValueError('Pre-fit evidence lacks exact exercised closure')
    prefit = D.module(directory / 'prefit.py', 'w50_g1_prefit')
    original = D.load(D.checked(repo, doc['references']))
    prefit.validate_exemptions(original, D.load(D.checked(repo, doc['manifest'])), doc['reportedKeys'])
    prefit.validate_completion(original, D.load(D.checked(repo, evidence['references'])),
                               doc['reportedKeys'], repo, empty_support_keys=doc['emptySupportKeys'],
                               owner_budget_keys=doc['ownerBudgetKeys'], owner_contracts=doc['ownerContracts'],
                               owner_source=D.owner_source(doc) if doc['ownerBudgetKeys'] else None)
    if set(evidence.get('evidence', {})) != set(D.PROOFS):
        raise ValueError('All twelve pre-fit proofs are required')
    for kind in D.PROOFS:
        prefit.validate_proof(D.load(D.checked(repo, evidence['evidence'][kind])), kind, repo)
    return D.pin(repo, C.slot(path, 'prefit'))


# Each supersession series holds one record per evidence generation from 2 up. The r2 pair (the
# DL5l-type recovery of DL5n) is the committed base and must always be read.
SERIES=('owner/r{}/supersedes.json','completion/registered-{}/supersedes.json','prefit-proofs-r{}/supersedes.json')
BASE=('owner/r2/supersedes.json','completion/registered-2/supersedes.json')


def supersession_records(repo):
    """Every supersession record of the pre-fit lineage, by series and generation. A series runs
    without a gap from its lowest record to its highest, and the r2 base records are present, so
    deleting a record from inside a series, or an r2 base record, refuses. Deleting a series'
    NEWEST record is not detectable from the tree: the generations left are still contiguous and
    nothing here records how many there should be, so this check alone does not keep what that
    record superseded from being readmitted. A series with no record at all is likewise accepted
    unless its r2 record is among BASE."""
    fit=Path(repo)/FIT_REL;found=[]
    for series in SERIES:
        head,tail=series.split('{}')
        pattern=re.compile(re.escape(head)+'([2-9]|[1-9][0-9]+)'+re.escape(tail))
        generations=sorted(int(m.group(1)) for p in fit.glob(series.format('*'))
                           if (m:=pattern.fullmatch(str(p.relative_to(fit)))) and p.is_file())
        if generations!=list(range(generations[0],generations[-1]+1) if generations else []):
            raise ValueError('A supersession record is missing from its series')
        found+=[series.format(n) for n in generations]
    if any(name not in found for name in BASE):raise ValueError('The r2 supersession records are required')
    return found


def _pins(value,out):
    if isinstance(value,dict):
        if isinstance(value.get('path'),str) and isinstance(value.get('sha256'),str):out.append(value)
        for item in value.values():_pins(item,out)
    elif isinstance(value,list):
        for item in value:_pins(item,out)
    return out


def _lexical(repo,path):return os.path.normpath(os.path.join(str(repo),path))


def prefit_lineage(repo,evidence,roots=()):
    """Tie the pre-fit evidence to the rebuilt proofs (second pre-seal review P2) and to its root.

    current3's verify_prefit validates each proof alone, so a proof superseded by a DL5l-type
    reference recovery (DL5n; the DL5o owner cascade) still validates beside the evidence that
    replaced it. Supersession records name what each recovery replaced, under their 'superseded'
    key; every record of every generation is read (supersession_records). A superseded assembly
    archive also names, by content, the completed inventory it archived. Refused: any pin,
    anywhere in the evidence or in one of its proofs, that names a superseded file (by its
    lexically resolved path) or a superseded completed inventory (by content hash, so its live
    copy under any name). `roots` are the chain's superseded LIVE roots and their seals
    (predecessors), refused by path and by content, so evidence written for one root never
    stands for another. Required: referenceCompletion's sources contain the evidence's own
    completed inventory, exactly that pin."""
    repo=Path(repo);paths=set();inventories=set()
    for name in supersession_records(repo):
        record=D.load(repo/FIT_REL/name)
        if not isinstance(record.get('superseded'),dict):raise ValueError('Supersession record names nothing superseded')
        paths|={_lexical(repo,item['path']) for item in _pins(record['superseded'],[])}
        archive=record['superseded'].get('archive')
        if archive is not None:
            manifest=D.load(D.checked(repo,archive))
            if manifest.get('schema')!='w50-reference-assembly-archive-1':raise ValueError('Superseded archive is not an assembly archive')
            inventories.add(manifest['completedReferences']['original']['sha256'])
    rooted={_lexical(repo,item['path']) for item in roots}|{item['sha256'] for item in roots}
    documents=[('evidence',evidence)]+[(kind,D.load(D.checked(repo,item))) for kind,item in sorted(evidence['evidence'].items())]
    for kind,document in documents:
        for item in _pins(document,[]):
            if _lexical(repo,item['path']) in rooted or item['sha256'] in rooted:
                raise ValueError('Pre-fit '+kind+' pins a superseded LIVE root')
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
