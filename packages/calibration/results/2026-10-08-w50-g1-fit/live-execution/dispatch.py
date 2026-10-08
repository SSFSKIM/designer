"""Prospective LIVE phase/attempt dispatcher with a quarantined qualification boundary.

Consumer hooks are real prospectively pinned modules, not callbacks supplied at launch.
Capture: capture(context, member, config) -> {record, artifacts}; verify(context, member,
record, config) rechecks original reports/repeat admission without scoring. Native:
admit(context, config) at 'native-admission', read-only and before native.started.json, then
prepare(context, config) -> one completed read (lifecycle.native_payload, DL5n: ready or not,
its stops metadata only), with an artifacts pin list. Measurement: evaluate(context, captures,
config). Fit/judge: evaluate(context, evidence, config). Owner: admit(context, config) at
'owner-admission', metadata-only, at the gate's and the exposure's creation and before each of
the exposure's one-shot markers; then evaluate(context, captures, config) in analysis. Fit also exports
fit_record(root, completed), which the gate re-derives. Initializer remains a separate
pre-render entrypoint behind verify_prefit.

Operational stops (DL5k) are always preserved: an exception after an attempt's claim writes
its failure record before propagating; a killed attempt is preserved by stop_stale_attempt
once its process and its GPU lease are both gone. A capture role signals a census refusal by
raising CensusRefused; a lost GPU lease is classified from the lock itself. Every entry takes
the GPU lease through _gpu_lease, which first releases a lease its dead holder left behind
(_release_stale_lock), so no kill between a lock and a claim wedges the phase. The release and
the O_EXCL acquisition run under one sidecar flock, so two dispatchers meeting the same dead
token cannot remove each other's fresh lease (second pre-seal review P2).

Protected payload access is instrument/API enforced plus the wave's role discipline.
It is NOT OS isolation. No agent may open native/quarantine files directly before the
complete-union measurement/judge marker. Every public execution result is allowlisted.

Every entry serves only the newest root of its directory's chain (DL5o): _prepare refuses a
superseded root before it reads or executes anything else, a process already serving a root
included. Each root's phase slots are its own (common.slot): fit/<root stem>.<batch>.json,
<root stem>.gate-contract.json and <root stem>.exposure-contract.json beside the root.
"""
import calendar
import contextlib
import copy
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import types

HERE=Path(__file__).resolve().parent
# common.ROOT_CHAIN, read here before any other repository source executes (test_chain proves
# the two agree).
ROOT_CHAIN=re.compile(r'execution-root(?:-([2-9]|[1-9][0-9]+))?\.json(?:\.sha256)?')
_CORE=None
_ACTIVE=None
_LEASE=None


class CensusRefused(RuntimeError):
    """Raised by a live capture role when the classifying census refuses before a draw."""


class LeaseHeld(FileExistsError):
    """The GPU lock belongs to a live holder or another tool; it was not touched."""


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(path):return json.loads(Path(path).read_text())
def _sealed_bytes(value):return (json.dumps(value,indent=2,allow_nan=False)+'\n').encode()


def _seal_written(path):
    """Write the sidecar of a document whose one write survived a crash before it (current3
    write_sealed writes the document, then its sidecar). The bytes must be exactly that write
    of their own content, so a torn or hand-edited file is never sealed."""
    path=Path(path);raw=path.read_bytes()
    def invalid(value):raise ValueError('Nonfinite JSON constant')
    try:value=json.loads(raw,parse_constant=invalid)
    except ValueError:raise ValueError('Unsealed document is not one complete write') from None
    if _sealed_bytes(value)!=raw:raise ValueError('Unsealed document is not one complete write')
    with Path(str(path)+'.sha256').open('x') as handle:
        handle.write(f'{sha(path)}  {path.name}\n');handle.flush();os.fsync(handle.fileno())
    return value


def _write_sealed(path,value):
    """current3 write_sealed, completing a seal a crash interrupted: when exactly the bytes this
    call would write already exist without their sidecar, only the sidecar is written."""
    path=Path(path)
    if path.exists() and not Path(str(path)+'.sha256').exists():
        if path.read_bytes()!=_sealed_bytes(value):raise ValueError('A different unsealed document holds this slot')
        _seal_written(path);return path
    return _CORE['C'].D.write_sealed(path,value)


def _generation(name):
    match=ROOT_CHAIN.fullmatch(name)
    return None if match is None else int(match.group(1) or 1)


def _superseded(path):
    """common.superseded: a later chain generation, document or sidecar, exists beside the root."""
    own=_generation(path.name);folder=path.parent
    return own is not None and any((_generation(n) or 0)>own for n in (os.listdir(folder) if folder.is_dir() else ()))


def source(path,name):
    m=types.ModuleType(name);m.__file__=str(path);sys.modules[name]=m
    exec(compile(Path(path).read_bytes(),str(path),'exec',dont_inherit=True),m.__dict__)
    return m


def _prepare(path):
    global _CORE
    path=Path(path).resolve()
    if _superseded(path):raise ValueError('Superseded LIVE root: a later generation exists beside it')
    doc=load(path);repo=Path(doc['repo']).resolve()
    if _CORE is not None:
        if _CORE['root']!=str(path) or _CORE['sha']!=sha(path):raise ValueError('A process may serve only its unchanged registered root')
        return _CORE
    sources=doc['closure']['sources']
    if Path(str(path)+'.sha256').read_text()!=f'{sha(path)}  {path.name}\n':raise ValueError('Root seal changed')
    if (repo/doc['bootstrap']['path']).resolve()!=Path(__file__).resolve() or doc['bootstrap']['sha256']!=sha(__file__):
        raise ValueError('Entrypoint is not this sealed dispatcher')
    for relative,digest in sources.items():
        target=(repo/relative).resolve()
        if not target.is_relative_to(repo) or not target.is_file() or sha(target)!=digest:raise ValueError('Unregistered source bytes')
    for name in ('dispatch','guard','common','authority','lifecycle','quarantine'):
        p=HERE/(name+'.py')
        if sources.get(str(p.relative_to(repo)))!=sha(p):raise ValueError('Bootstrap source absent from closure')
    guard=source(HERE/'guard.py','w50_live_guard')
    if guard.environment()!=doc['closure']['environment']:raise ValueError('Interpreter/environment differs from root')
    guard.enforce(repo,sources)
    # From here every repository helper is checked by the permanent in-process guard.
    core={name:source(HERE/(file+'.py'),'w50_live_'+file) for name,file in
        (('C','common'),('A','authority'),('L','lifecycle'),('Q','quarantine'))}
    if guard.discover(repo,repo/doc['probe']['path'],sources)!=doc['closure']:raise ValueError('Exercised closure changed')
    core.update(root=str(path),sha=sha(path),guard=guard);_CORE=core
    return core


def root_doc(path):return _prepare(path)['A'].root_doc(path)
def current_evidence(path,doc=None):
    actual=root_doc(path)
    if doc is not None and doc!=actual:raise ValueError('Current evidence caller changed the admitted root')
    return load(checked(actual['repo'],actual['currentEvidence']))

def sealed(path):return _CORE['C'].D.sealed(path)
def checked(repo,item):return _CORE['C'].D.checked(repo,item)
def admission_module(doc):return _CORE['C'].D.admission_module(doc)
def baseline_run(run):return _CORE['C'].D.baseline_run(run)
def verify_prefit(path,doc):return _prepare(path)['A'].verify_prefit(path,doc)


def result_for(contract):
    D=_CORE['C'].D;result=D.result_for(contract)
    marker=Path(str(contract)+'.phase/analysis.started.json')
    if result.get('analysisClaim')!=_CORE['L'].pin(marker):raise ValueError('Result has no genuine exclusive analysis claim')
    L=_CORE['L'];L.checked(result['captureUnion'])
    if load(marker).get('captures')!=result['captureUnion']:raise ValueError('Result names another complete capture union')
    body=D.sealed(contract);doc=D.sealed(_CORE['root'])
    batch=D.load(D.checked(doc['repo'],body['batch']))
    store=L.Store(contract,batch,body['logicalOutput']);union=store.complete_union()
    if L.read(L.checked(result['captureUnion']))!=union:raise ValueError('Completed checkpoint ownership changed')
    if result['captures']['captures']!=[L.read(L.checked(r['payload'])) for r in union['members']]:
        raise ValueError('Final captures differ from original immutable member records')
    return result


def create_phase(root,batch_path,output,fit_record=None):
    global _ACTIVE,_LEASE
    root=Path(root).resolve();doc=root_doc(root);C=_CORE['C'];D=C.D;repo=Path(doc['repo'])
    batch=D.load(batch_path);phase=batch.get('phase')
    if phase not in ('fit','gate','exposure'):raise ValueError('Only scientific LIVE phases are admitted')
    batch,expected=D.validate_batch(doc,batch_path,phase)
    if phase=='fit' and C.slot(root,'gate').exists():raise ValueError('Gate already froze fitting')
    prefit=verify_prefit(root,doc);output=Path(output).resolve()
    if output.is_relative_to(repo):raise ValueError('Logical phase needs fresh external output')
    extra={};gate_batch=None
    if phase=='gate':
        if fit_record is None:raise ValueError('Gate requires one real completed fit selection')
        record=load(fit_record)
        for item in record.get('completed',[]):result_for(str(D.checked(repo,item)).removesuffix('.result.json'))
        D.validate_fit_record(root,doc,batch['cohort'],fit_record);_one_fit_point(root,doc,fit_record)
        extra['fitRecord']=D.pin(repo,fit_record)
    if phase=='exposure':
        result_for(C.slot(root,'gate'))
        gate,result=_CORE['C'].checked_gate_result(root,doc)
        if D.sealed(gate)['cohort']!=batch['cohort']:raise ValueError('Exposure changes frozen gate cohort')
        extra={'gateContract':D.pin(repo,gate),'gateResult':D.pin(repo,Path(str(gate)+'.result.json'))}
        gate_batch=_gate_batch(doc,extra['gateContract'])
    _live_batch(doc,batch,gate_batch)
    target=C.slot(root,'fit',sha(batch_path)) if phase=='fit' else C.slot(root,phase)
    # Everything the journal derives from the contract is derived before anything is durable, so a
    # malformed batch refuses here instead of burning a one-shot slot.
    L=_CORE['L'];L.Store(target,batch,output)
    if Path(str(target)+'.sha256').exists():raise ValueError('Logical phase slot already exists')
    interrupted=target.exists()
    if not interrupted and output.exists():raise ValueError('Logical phase needs fresh external output')
    if phase in ('gate','exposure'):
        # The owner is first exercised after the exposure's analysis marker; its metadata-only
        # admission runs here first, so a drifted owner input seals nothing (pre-seal review P1).
        # At the gate's creation it already runs the frozen engine on the intrinsic records the
        # exposure must reuse unchanged, so records it would refuse never freeze into a gate
        # (second pre-seal review P1). Like the other two admission points, it runs inside the
        # quarantine: its streams and errors go to a log beside the fresh output, never to the
        # caller (second pre-seal review P3).
        phase_data=(doc,{'phase':phase,**extra},batch_path,batch,expected,None)
        with _gpu_lease():
            try:ok,_=_CORE['Q'].run_private(_fresh_log(Path(str(output)+'.admission'),'owner-admission'),
                lambda:_admit_owner(root,phase_data,None,None))
            finally:_ACTIVE=None
        if not ok:raise ValueError('Owner admission refused before the phase slot; details are quarantined')
    if interrupted:
        # A crash between the contract's two writes: its seal is completed only when the output this
        # call names is the one the unsealed contract claimed and its bytes are what is derived here.
        claimed=output/L.OUTPUT_MARKER
        if not claimed.is_file() or L.read(claimed)!={'schema':'w50-live-phase-output-1','contract':str(target)}:
            raise ValueError('Logical phase slot already exists')
        marker=L.pin(claimed)
    else:marker=L.claim_output(output,target)
    return _write_sealed(target,{'schema':'w50-g1-phase-contract-1','executionRootSha256':sha(root),
        'phase':phase,'batch':D.pin(repo,batch_path),'cohort':batch['cohort'],'preFitEvidence':prefit,
        'logicalOutput':str(output),'outputMarker':marker,**extra})


def _one_fit_point(root,doc,fit_record):
    """DL4's one point. current3's validate_fit_record admits a record naming several completed
    fits; the gate takes only the record the registered fit role derives from its one result."""
    record=load(fit_record)
    if not isinstance(record.get('completed'),list):raise ValueError('Fit record names no completed fit')
    fitter,_=_component(doc,'fit')
    if record!=fitter.fit_record(root,record['completed']):
        raise ValueError('Gate requires the one fit point its registered fit role derives (DL4)')


def _gate_batch(doc,gate_contract):
    D=_CORE['C'].D;return D.load(D.checked(doc['repo'],D.sealed(D.checked(doc['repo'],gate_contract))['batch']))


def _pinned(doc,item):
    """A content pin in the form the owner's Node child compares it: its path resolved against the
    repository LEXICALLY, as path.resolve(repo, pin.path) does (owner-candidate/union.ts
    absolutePin; bridge.ts), never through symlinks. A realpath here would admit two spellings
    of one file that the child, after the analysis marker, reads as different declarations
    (second pre-seal review P3)."""
    if not isinstance(item,dict) or set(item)!={'path','sha256'} or not isinstance(item['path'],str) or \
            not isinstance(item['sha256'],str) or not re.fullmatch('[0-9a-f]{64}',item['sha256']):
        raise ValueError('Owner intrinsic record is not a content pin')
    path=os.path.normpath(os.path.join(doc['repo'],item['path']))
    if not Path(path).is_file() or sha(path)!=item['sha256']:raise ValueError('Owner intrinsic record pin does not resolve')
    return (path,item['sha256'])


RECEDED_RECORDS=('beforeActive','beforeReceded','methods','activeEntries')


def _intrinsic_records(doc,batch):
    """The owner's intrinsic inputs, structurally, before any marker (pre-seal review P1): its
    declarations are exactly the cohort, and both positions' receded records resolve. X76 reads a
    missing record UNMEASURED, which DL5m (5) makes NEITHER; here it refuses while recoverable.
    Their CONTENT is the frozen engine's to refuse; the owner admission at the gate's and the
    exposure's creation runs it on these records (owner-candidate/live.intrinsic_probe)."""
    D=_CORE['C'].D;item=batch.get('ownerIntrinsicRecords')
    if not isinstance(item,dict) or set(item)!={'path','sha256'}:raise ValueError('Gate and exposure name their owner intrinsic records')
    records=D.load(D.checked(doc['repo'],item))
    if not isinstance(records,dict):raise ValueError('Owner intrinsic records are not one record document')
    declarations=records.get('candidateDeclarations')
    if not isinstance(declarations,list) or len(declarations)!=len(batch['cohort']) or \
            {_pinned(doc,p) for p in declarations}!={_pinned(doc,p) for p in batch['cohort']}:
        raise ValueError('Owner intrinsic declarations differ from the candidate cohort')
    receded=records.get('recededRecords')
    if not isinstance(receded,dict) or set(receded)!={'0.25','0.5'} or \
            any(not isinstance(r,dict) or not set(RECEDED_RECORDS)<=set(r) for r in receded.values()):
        raise ValueError('Owner intrinsic records need both positions\' receded records')
    for record in receded.values():
        for name in RECEDED_RECORDS:_pinned(doc,record[name])


def _live_batch(doc,batch,gate_batch=None):
    """LIVE's batch shape beyond the original admission, which treats a baseline as optional and
    leaves the owner's intrinsic records to the owner, after the exposure's analysis marker."""
    if batch['phase']=='exposure' and any(run.get('baselineCandidate') not in doc['baselineDocuments'] for run in batch['runs']):
        raise ValueError('Every exposure run needs its registered same-cell baseline candidate')
    if batch['phase'] in ('gate','exposure'):
        _intrinsic_records(doc,batch)
        if batch['phase']=='exposure' and (gate_batch is None or gate_batch.get('ownerIntrinsicRecords')!=batch['ownerIntrinsicRecords']):
            raise ValueError('Exposure intrinsic records differ from the frozen gate batch')


def _phase(root,contract):
    doc=root_doc(root);C=_CORE['C'];D=C.D;body=D.sealed(contract);repo=Path(doc['repo'])
    phase=body['phase'];batch_path=D.checked(repo,body['batch']);batch,expected=D.validate_batch(doc,batch_path,phase)
    _live_batch(doc,batch,_gate_batch(doc,body['gateContract']) if phase=='exposure' else None)
    target=C.slot(root,'fit',sha(batch_path)) if phase=='fit' else C.slot(root,phase)
    if Path(contract).resolve()!=target.resolve() or body['executionRootSha256']!=sha(root) or body['cohort']!=batch['cohort']:
        raise ValueError('Wrong logical phase authority')
    if body['preFitEvidence']!=verify_prefit(root,doc):raise ValueError('Pre-fit evidence changed')
    if phase=='fit' and C.slot(root,'gate').exists():raise ValueError('Gate froze fitting')
    if phase=='gate':
        fit_record=D.checked(repo,body['fitRecord'])
        D.validate_fit_record(root,doc,batch['cohort'],fit_record);_one_fit_point(root,doc,fit_record)
    if phase=='exposure':
        result_for(D.checked(repo,body['gateContract']));gate,result=_CORE['C'].checked_gate_result(root,doc)
        if body['gateResult']!=D.pin(repo,Path(str(gate)+'.result.json')) or D.sealed(gate)['cohort']!=batch['cohort']:
            raise ValueError('Exposure changed original qualified gate')
    store=_CORE['L'].Store(contract,batch,body['logicalOutput'])
    return doc,body,batch_path,batch,expected,store


def require_context(context):
    if _ACTIVE is None or context is not _ACTIVE['context'] or not _CORE['C'].D.lease_owned():
        raise ValueError('No genuine live context/lease')
    if context!=_ACTIVE['snapshot'] or any(sha(p)!=h for p,h in _ACTIVE['hashes']):
        raise ValueError('Live context or execution authority changed')
    return context


def require_payload(context,item):
    require_context(context)
    if context.get('stage')!='analysis' or item not in _ACTIVE['payloads']:
        raise ValueError('Protected payload is not in the admitted complete analytical union')


def require_render_admission(context,run,current=False):
    require_context(context)
    if context['stage']!='capture' or not any(m['run']==run and (m['lane']=='current')==current for m in _ACTIVE['members']):
        raise ValueError('Rendering is limited to this remaining capture member')
    doc=_ACTIVE['doc']
    if not current:
        if _ACTIVE['numerical'] is None:raise ValueError('Candidate render has no numerical admission')
        checked(doc['repo'],_ACTIVE['numerical'])
    admission_module(doc).endpoints(doc,run['candidate'],current=current)
    return run


def resolve_capture_run(context,receipt):
    require_context(context)
    if context['stage'] not in ('analysis','qualification'):raise ValueError('No authenticated retained-reading stage')
    matches=[m for m in _ACTIVE['members'] if all(receipt.get(k)==m['run'].get(k) for k in ('profile','renderer','candidate'))
        and receipt.get('scene')==m['scene'] and receipt.get('lane')==m['lane']]
    if len(matches)!=1:raise ValueError('Receipt is not a source-bound complete-union member')
    key=matches[0]['id']
    if _ACTIVE.get('records',{}).get(key)!=receipt:raise ValueError('Receipt bytes differ from its original checkpoint')
    return copy.deepcopy(matches[0]['run'])


def require_native_admission(context):
    """Exposure-only, metadata-only pre-start admission (DL5k): the native marker burns the one
    read, so every refusable check runs first, before it exists. Grants no payload, frame or
    render access; those capabilities each refuse this stage."""
    require_context(context)
    if context['stage']!='native-admission' or context['phase']!='exposure':raise ValueError('No live native admission capability')
    if (_ACTIVE['store'].home/'native.started.json').exists():raise ValueError('Native admission belongs before the one-shot native marker')
    return context


def require_owner_admission(context):
    """Metadata-only owner admission (pre-seal review P1). The owner is first exercised after the
    exposure's analysis marker, so its config, closure and pins are admitted at the exposure's
    creation (no contract or claim yet: those context fields are None), before the native marker
    and immediately before the analysis marker. The gate's creation admits it too, because the
    gate batch freezes the intrinsic records the exposure must reuse (second pre-seal review P1);
    a gate grants it at creation only. Grants no payload, frame, native or render access; those
    capabilities each refuse this stage."""
    require_context(context)
    if context['stage']!='owner-admission' or not (context['phase']=='exposure' or
            (context['phase']=='gate' and context['contract'] is None)):raise ValueError('No live owner admission capability')
    store=_ACTIVE['store']
    if store is not None and store.analysis_marker.exists():raise ValueError('Owner admission belongs before the analysis marker')
    return context


def require_native_preparation(context):
    require_context(context)
    if context['stage']!='native' or context['phase']!='exposure':raise ValueError('No live native preparation capability')
    started=_CORE['L'].read(_ACTIVE['store'].home/'native.started.json')
    if started['claim']!=context['executionClaim']:raise ValueError('Native preparation belongs to another active attempt')
    return context


def require_read_admission(context,run,current=False):
    require_context(context)
    if context['stage'] not in ('analysis','qualification') or not any(m['run']==run and (m['lane']=='current')==current for m in _ACTIVE['members']):
        raise ValueError('Run is outside the authenticated retained reading population')
    return run


def qualification_native(context):
    require_context(context)
    if context['stage'] not in ('capture','qualification','analysis'):raise ValueError('Native payload is unavailable')
    item=_ACTIVE['store'].native_metadata()['payload']
    return _CORE['L'].read(_CORE['L'].checked(item))


def _template(root,contract,phase_data):
    """Everything a stage context derives that can refuse, so a caller builds it before the marker
    the stage may follow (pre-seal review P3). `contract` is None at the exposure's creation."""
    doc,body,batch_path,batch,expected,store=phase_data;D=_CORE['C'].D
    context={'repo':doc['repo'],'executionRoot':str(Path(root).resolve()),
        'contract':None if contract is None else str(Path(contract).resolve()),
        'batchPath':str(batch_path),'batch':batch,'phase':body['phase'],'output':None if store is None else str(store.output),
        'logicalClaim':None,'inputs':doc['inputs'],'expectedCells':expected,
        'baselineDocuments':doc['baselineDocuments'],'repeatAdmission':doc['repeatAdmission'],
        'phaseDependencies':doc['phaseDependencies'],'ownerUnionKeys':doc['phaseDependencies']['ownerUnionKeys'],
        'unionExpectedCells':[{k:r[k] for k in D.KEY} for r in D.load(D.checked(doc['repo'],doc['references']))['cells']]}
    hashes=[(context['executionRoot'],sha(root)),(str(batch_path),sha(batch_path))]
    if contract is not None:hashes.append((str(contract),sha(contract)))
    if body['phase']=='exposure':
        gate=result_for(D.checked(doc['repo'],body['gateContract']))
        context.update(gateResult=body['gateResult'],gateCaptures=gate['captures'],gateReport=gate['report'])
        hashes.append((str(D.checked(doc['repo'],body['gateResult'])),body['gateResult']['sha256']))
    else:context.update(gateResult=None,gateCaptures=None,gateReport=None)
    return context,hashes


def _activate(template,phase_data,stage,claim,members=(),payloads=()):
    global _ACTIVE
    doc,body,batch_path,batch,expected,store=phase_data;L=_CORE['L'];D=_CORE['C'].D
    context,hashes=copy.deepcopy(template[0]),list(template[1]);numerical=None
    if store is not None:
        logical=Path(str(store.contract)+'.started.json')
        context['logicalClaim']=L.pin(logical);hashes.append((str(logical),sha(logical)))
        numerical=L.read(logical).get('numericalAdmission')
        if numerical is not None:hashes.append((str(D.checked(doc['repo'],numerical)),numerical['sha256']))
    if claim is not None:hashes.append((claim['path'],claim['sha256']))
    context.update(stage=stage,executionClaim=claim)
    _ACTIVE={'context':context,'snapshot':copy.deepcopy(context),'hashes':hashes,'doc':doc,'store':store,'numerical':numerical,
        'members':list(members),'payloads':list(payloads),
        'records':{r['member']['id']:L.read(L.checked(r['payload'])) for r in store.checkpoints()} if stage in ('analysis','qualification') else {}}
    sys.modules['w50_g1_dispatch']=sys.modules[__name__]
    return context


def _context(root,contract,phase_data,stage,claim,members=(),payloads=()):
    return _activate(_template(root,contract,phase_data),phase_data,stage,claim,members,payloads)


def _admit_owner(root,phase_data,contract,claim):
    """The owner role's metadata-only admission; the caller holds the lease (pre-seal review P1)."""
    owner,config=_component(phase_data[0],'owner')
    ctx=_context(root,contract,phase_data,'owner-admission',claim);owner.admit(ctx,config);require_context(ctx)


def _component(doc,role):
    item=doc['instruments'][role]
    return source(checked(doc['repo'],item['entrypoint']),'w50_live_role_'+role),item['config']


def _record_artifacts(doc,member,record,declared):
    if any(record.get(k)!=member['run'].get(k) for k in ('profile','renderer','candidate')) or record.get('scene')!=member['scene'] or record.get('lane')!=member['lane']:
        raise ValueError('Captured receipt differs from admitted single member')
    # The original pin collector skips a legacy-retained origin; a live draw has none (DL5h (b)).
    if 'origin' in record:raise ValueError('A live member admits no legacy origin')
    if any(not isinstance(record.get(k),dict) or not record[k].get('path') for k in ('repeatPair','repeatAdmission')):
        raise ValueError('A live member needs both content-pinned repeat witnesses')
    pins=_CORE['C'].D.repeat_artifact_pins(doc['repo'],{'captures':[record]})
    artifacts=list(declared)
    for item in [*pins,*(record['artifacts'][k] for k in ('png','cell','report'))]:
        if item not in artifacts:artifacts.append(item)
    for key in ('png','cell','report'):
        if not Path(record['artifacts'][key]['path']).resolve().is_relative_to(Path(member['run']['captureRoot']).resolve()):
            raise ValueError('Capture artifact escaped its actual member destination')
    return artifacts


MONTHS={m:i for i,m in enumerate(('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'),1)}


def _process_start(pid):
    """A running process's start, whole seconds since the epoch, read as the G0 census reads it
    (ps lstart, C locale; in UTC here so no zone or daylight rule enters). None when no such
    process exists or it is a zombie, which has exited; an unreadable table refuses rather than
    reading as gone."""
    result=subprocess.run(['/bin/ps','-o','stat=,lstart=','-p',str(pid)],capture_output=True,text=True,
        env={'LC_ALL':'C','TZ':'UTC0'},check=False)
    fields=result.stdout.split()
    if not fields:
        if result.returncode==1 and not result.stderr.strip():return None
        raise ValueError('Process table unreadable; claim liveness unknown')
    state,_,month,day,clock,year=fields;hour,minute,second=map(int,clock.split(':'))
    if state.startswith('Z'):return None
    return calendar.timegm((int(year),MONTHS[month],int(day),hour,minute,second,0,0,0))


def _alive(pid,since):
    """Whether the process that wrote a claim or lock at `since` (that file's mtime) may still be
    running. A PID with no process is gone, and so is one whose process started after the claim
    was written: that is a reused PID, not the writer (pre-seal review P3). lstart has whole-second
    resolution, so only a start in a later second reads as reuse; anything else reads alive, the
    safe side."""
    if type(pid) is not int or pid<=0:raise ValueError('Claim has no process identity')
    if pid==os.getpid():return True
    try:os.kill(pid,0)
    except ProcessLookupError:return False
    except PermissionError:pass
    started=_process_start(pid)
    return started is not None and started<=since


LEASE_TOKEN=re.compile(r'W50 pid=([1-9][0-9]*) owner=[0-9a-f]{32}\n')


@contextlib.contextmanager
def _lease_mutex():
    """The sidecar mutex every LIVE lease entry holds from reading the lock's token through its
    unlink and current3's O_EXCL create (second pre-seal review P2).

    Without it two dispatchers that read the same dead token race: the first releases it and
    takes its own lease, the second's unlink then removes that fresh lease. The mutex is an
    fcntl.flock on a file beside the lock; it is never unlinked, so its inode is one for every
    holder, and the kernel releases it when its holder exits. A tool that does not release
    stale leases (current3, W49) never needs it: only a releaser unlinks another holder's lock."""
    handle=os.open(str(_CORE['C'].D.GPU_LOCK)+'.mutex',os.O_RDWR|os.O_CREAT,0o600)
    try:
        fcntl.flock(handle,fcntl.LOCK_EX)
        yield
    finally:os.close(handle)


@contextlib.contextmanager
def _gpu_lease():
    """The GPU lease for one LIVE entry: a stale lease released and current3's owned_gpu_lock
    taken under one _lease_mutex, then held, with _LEASE bound, until the block ends. Yields
    _release_stale_lock's result; a lock another holder owns refuses as LeaseHeld, untouched."""
    global _LEASE
    D=_CORE['C'].D
    with contextlib.ExitStack() as stack:
        with _lease_mutex():
            released=_release_unlocked()
            if released=='held':raise LeaseHeld(str(D.GPU_LOCK))
            stack.enter_context(D.owned_gpu_lock())
        _LEASE=D._LEASE
        try:yield released
        finally:_LEASE=None


def _release_stale_lock():
    """Release a GPU lease its dead holder left behind, under the lease mutex. Returns 'absent',
    'held' or ('removed', token). Entries use _gpu_lease, which also acquires under the mutex."""
    with _lease_mutex():return _release_unlocked()


def _release_unlocked():
    """_release_stale_lock's body; the caller holds _lease_mutex (pre-seal review P2).

    A process killed between taking the lock and writing (or finishing) the claim that names it
    leaves a lock that no claim can prove gone. Only a lock in current3 owned_gpu_lock's exact token
    form is considered; its pid must be dead (_alive, against the lock's own write time), and the
    file is unlinked only if it is still the same inode that was read. A live holder's or any other
    tool's lock is never touched. Orphaned renderer children are the census's to refuse, not the
    lock's."""
    lock=_CORE['C'].D.GPU_LOCK
    try:
        with open(lock) as handle:
            token=handle.read();identity=os.fstat(handle.fileno())
    except FileNotFoundError:
        return 'absent'
    match=LEASE_TOKEN.fullmatch(token)
    if match is None or _alive(int(match.group(1)),identity.st_mtime):return 'held'
    try:now=os.stat(lock)
    except FileNotFoundError:return 'absent'
    if (now.st_dev,now.st_ino)!=(identity.st_dev,identity.st_ino):return 'held'
    os.unlink(lock)
    return ('removed',token)


def _claim_alive(path):
    claim=_CORE['L'].read(path)
    return _alive(claim.get('pid'),os.stat(path).st_mtime)


def stop_stale_attempt(root,contract,code):
    """Preserve a killed attempt (claim without failure/completion) as an operational stop.

    Writes the failure record with its inventory, so prepare_attempt's reconciliation runs next."""
    store=_phase(root,contract)[5];D=_CORE['C'].D;L=_CORE['L'];Q=_CORE['Q']
    prior=store._contracts()
    if not prior:raise ValueError('No attempt to preserve')
    folder=prior[-1].parent;attempt=L.read(prior[-1])
    if not (folder/'started.json').exists() or (folder/'failure.json').exists() or (folder/'complete.json').exists():
        raise ValueError('Only a started, unstopped, incomplete attempt can be preserved as stale')
    claim=L.read(folder/'started.json')
    if _claim_alive(folder/'started.json'):raise ValueError('Claim process may still own its lease')
    try:
        with _gpu_lease() as released:
            lock='absent' if released=='absent' else 'removed-same-token' if released[1]==claim.get('gpuLease') else 'removed-dead-holder'
            store.stop(attempt,code,stale={'pid':claim['pid'],'gpuLease':claim['gpuLease'],'lock':lock,
                'stopLease':_LEASE['token']})
    except LeaseHeld:raise ValueError('GPU lock belongs to another lease; not touched') from None
    return Q.public_event(code,phase=store.batch['phase'],attempt=attempt['ordinal'])


def _stop_code(error):
    if not _CORE['C'].D.lease_owned():return 'LEASE_LOST'
    if isinstance(error,CensusRefused):return 'CENSUS_REFUSED'
    return 'INSTRUMENT_FAULT'


def _classified(callback,stop):
    def run():
        try:return callback()
        except BaseException as error:
            stop['code']=_stop_code(error);raise
    return run


def _reconcile(root,contract,data,store,attempt_path,failure_path,failure,orphans):
    """One numbered reconciliation of a stopped attempt's orphans under this process's lease.

    A stopped reconciliation is preserved (claim, log pin, failure) and a successor names it; a
    completed one is never repeated. Adopted members stay adopted by their own claim."""
    global _ACTIVE
    doc=data[0];L=_CORE['L'];Q=_CORE['Q'];digest=sha(failure_path);old=L.read(attempt_path)
    base=store.home/'reconciliations'/digest
    runs=sorted(p for p in base.glob('[0-9]'*6) if p.is_dir()) if base.exists() else []
    if runs and (runs[-1]/'complete.json').exists():return
    predecessor=None
    if runs:
        last=runs[-1]
        if not (last/'failure.json').exists():
            # A killed reconciliation: this process holds the GPU lease, so only its PID remains,
            # read against the claim's own write time so a reused PID is not its writer.
            if _claim_alive(last/'started.json'):raise ValueError('Prior reconciliation may still be running')
            log=store.output/'quarantine'/f'reconciliation-{digest}-{int(last.name):06d}.log'
            L.write_once(last/'failure.json',{'schema':'w50-live-reconciliation-failure-1',
                'claim':L.pin(last/'started.json'),'log':L.pin(log) if log.is_file() else None,'stale':True})
        predecessor={'claim':L.pin(last/'started.json'),'failure':L.pin(last/'failure.json')}
    n=len(runs)+1;home=base/f'{n:06d}'
    log=store.output/'quarantine'/f'reconciliation-{digest}-{n:06d}.log'
    claim=L.write_once(home/'started.json',{'schema':'w50-live-reconciliation-claim-1','logicalContract':L.pin(contract),
        'failedAttempt':L.pin(attempt_path),'failure':L.pin(failure_path),'ordinal':n,
        'predecessor':predecessor,'pid':os.getpid(),'gpuLease':_LEASE['token']})
    def recover():
        ctx=_context(root,contract,data,'qualification',claim,orphans)
        capture,config=_component(doc,'capture')
        admitted={(str(Path(p['path']).resolve()),p['sha256']) for p in failure['inventory']}
        admitted|={(str((Path(doc['repo'])/p['path']).resolve()),p['sha256']) for p in doc['inputs']}
        for member in orphans:
            found=capture.recover(ctx,member,config);require_context(ctx)
            if found is None:
                if any(Path(member['run']['captureRoot']).rglob('repeat-admission__*.json')):
                    raise ValueError('Source-qualified orphan cannot be silently rerendered')
                continue
            capture.verify(ctx,member,found['record'],config);require_context(ctx)
            pins=_record_artifacts(doc,member,found['record'],found['artifacts'])
            if any((str(Path(p['path']).resolve()),p['sha256']) not in admitted for p in pins):
                raise ValueError('Recovery adopted files absent from the preserved failure/source inventory')
            store.adopt(old,member,found['record'],pins,claim)
    try:ok,_=Q.run_private(log,recover)
    finally:_ACTIVE=None
    if not ok:
        L.write_once(home/'failure.json',{'schema':'w50-live-reconciliation-failure-1','claim':claim,'log':L.pin(log)})
        raise ValueError('Source reconciliation stopped; protected details remain quarantined')
    L.write_once(home/'complete.json',{'schema':'w50-live-reconciliation-complete-1','claim':claim,'log':L.pin(log)})


def _fresh_log(folder,name):
    n=1
    while (Path(folder)/f'{name}-{n:06d}.log').exists():n+=1
    return Path(folder)/f'{name}-{n:06d}.log'


def _sealed_result(contract):return Path(str(contract)+'.result.json.sha256').exists()


def prepare_attempt(root,contract):
    """The next attempt to execute, or the phase's metadata-only state when none is due:
    'w50-live-capture-ready-1' when every member is captured and analysis has not started,
    'w50-live-phase-complete-1' once its result is sealed."""
    global _ACTIVE,_LEASE
    data=_phase(root,contract);doc,body,batch_path,batch,expected,store=data
    D=_CORE['C'].D;L=_CORE['L'];prior=store._contracts()
    if store.analysis_marker.exists():
        if _sealed_result(contract):return {'schema':'w50-live-phase-complete-1','logicalContract':L.pin(contract)}
        raise ValueError('Analysis already started')
    if store.native_state()=='incomplete':raise ValueError('Incomplete native subread cannot be replayed')
    ready={'schema':'w50-live-capture-ready-1','logicalContract':L.pin(contract)}
    if prior and not (prior[-1].parent/'started.json').exists():
        # Planned but never claimed: the same centrally derived attempt is still the next one.
        return L.read(prior[-1])
    if prior and (prior[-1].parent/'complete.json').exists():return ready
    if prior:
        old=L.read(prior[-1]);failure_path=prior[-1].parent/'failure.json'
        if not failure_path.exists():raise ValueError('Prior attempt is not a preserved stop (see stop_stale_attempt)')
        failure=L.read(failure_path)
        for item in failure['inventory']:L.checked(item)
        done={r['member']['id'] for r in store.checkpoints()}
        orphans=[m for m in old['members'] if m['id'] not in done and Path(m['run']['captureRoot']).parent.exists()]
        if orphans:
            with _gpu_lease():
                try:_reconcile(root,contract,data,store,prior[-1],failure_path,failure,orphans)
                finally:_ACTIVE=None
    if len(store.checkpoints())==len(store.population):
        # A crash after the last qualified cell may need only the existing attempt's final marker.
        old=L.read(prior[-1]);folder=prior[-1].parent
        if not (folder/'complete.json').exists():store.finish(old)
        return ready
    return store.plan()


def execute_attempt(root,contract,attempt):
    global _ACTIVE,_LEASE
    data=_phase(root,contract);doc,body,batch_path,batch,expected,store=data
    D=_CORE['C'].D;L=_CORE['L'];Q=_CORE['Q']
    numerical=admission_module(doc).validate_numerical(doc,batch)
    with _gpu_lease():
        try:
            claim=store.start(attempt,_LEASE['token'])
            folder=store.attempts/f'{attempt["ordinal"]:06d}'
            try:
                logical=Path(str(contract)+'.started.json')
                if not logical.exists():L.write_once(logical,{'contractSha256':sha(contract),'batchSha256':sha(batch_path),
                    'phase':body['phase'],'pid':os.getpid(),'gpuLease':_LEASE['token'],'output':str(store.output),
                    'numericalAdmission':numerical})
                else:
                    started=L.read(logical)
                    if any(started.get(k)!=v for k,v in {'contractSha256':sha(contract),'batchSha256':sha(batch_path),
                        'phase':body['phase'],'output':str(store.output),'numericalAdmission':numerical}.items()):
                        raise ValueError('Logical phase starter authority changed')
                def work():
                    capture,config=_component(doc,'capture')
                    retained=store.checkpoints();held=[r['member'] for r in retained]
                    native_state=store.native_state()
                    if native_state in ('complete','durable'):
                        ctx=_context(root,contract,data,'qualification',claim,held)
                        native,nconfig=_component(doc,'native')
                        payload=qualification_native(ctx) if native_state=='complete' else store.durable_native()
                        native.verify(ctx,payload,nconfig);require_context(ctx)
                        # A payload whose one write survived a crash before its marker is
                        # checkpointed now, verified again, never re-read (pre-seal review P3).
                        if native_state=='durable':store.complete_native(payload,recovered=claim)
                    if retained:
                        ctx=_context(root,contract,data,'qualification',claim,held)
                        for r in retained:
                            capture.verify(ctx,r['member'],L.read(L.checked(r['payload'])),config)
                            require_context(ctx)
                    if body['phase']=='exposure' and native_state=='none':
                        native,nconfig=_component(doc,'native');owner,oconfig=_component(doc,'owner')
                        # A native read that starts without a checkpoint is never replayed (DL5k),
                        # so a refusable environment (asset, archive tree, pins, the owner's
                        # inputs) is admitted here, read-only, and the native context is built:
                        # a refusal is this attempt's ordinary recoverable stop.
                        ctx=_context(root,contract,data,'native-admission',claim);native.admit(ctx,nconfig);require_context(ctx)
                        ctx=_context(root,contract,data,'owner-admission',claim);owner.admit(ctx,oconfig);require_context(ctx)
                        ctx=_context(root,contract,data,'native',claim)
                        # The one-shot marker is written only under the lease this attempt claimed.
                        if not D.lease_owned():raise ValueError('GPU lease lost before the one-shot native marker')
                        store.start_native(attempt)
                        payload=native.prepare(ctx,nconfig);require_context(ctx)
                        native.verify(ctx,payload,nconfig);require_context(ctx)
                        # DL5n: a completed read is checkpointed ready or not; anything else stops.
                        store.complete_native(payload)
                    for member in attempt['members']:
                        ctx=_context(root,contract,data,'capture',claim,[member])
                        captured=capture.capture(ctx,member,config);require_context(ctx)
                        capture.verify(ctx,member,captured['record'],config);require_context(ctx)
                        record=captured['record']
                        artifacts=_record_artifacts(doc,member,record,captured['artifacts'])
                        store.checkpoint(attempt,member,record,artifacts)
                    store.finish(attempt)
                stop={'code':'INSTRUMENT_FAULT'}
                ok,_=Q.run_private(store.output/'attempts'/f'{attempt["ordinal"]:06d}'/'quarantine/worker.log',_classified(work,stop))
                if not ok:store.stop(attempt,stop['code'])
                return Q.public_event('ATTEMPT_COMPLETE' if ok else stop['code'],phase=body['phase'],attempt=attempt['ordinal'])
            except BaseException as error:
                # Whatever interrupts a claimed attempt outside the worker leaves a preserved stop.
                if not (folder/'failure.json').exists() and not (folder/'complete.json').exists():
                    store.stop(attempt,_stop_code(error))
                raise
        finally:_ACTIVE=None


def _result_value(contract,data,template,result,union):
    """Every check the original invocation and result_for make on a result, short of its seal."""
    doc,body,batch_path,batch,expected,store=data;D=_CORE['C'].D;L=_CORE['L']
    if result.get('contractSha256')!=sha(contract) or result.get('claimSha256')!=sha(str(contract)+'.started.json') or \
            result.get('analysisClaim')!=L.pin(store.analysis_marker) or result.get('captureUnion')!=L.pin(store.home/'captures.complete.json') or \
            L.read(store.analysis_marker).get('captures')!=result['captureUnion'] or L.read(L.checked(result['captureUnion']))!=union:
        raise ValueError('Unsealed result is not bound to this analysis claim and union')
    if result['captures']['captures']!=[L.read(L.checked(r['payload'])) for r in union['members']]:
        raise ValueError('Unsealed result differs from the original immutable member records')
    for item in result.get('captureReceipt',{}).get('artifacts',[])+result.get('repeatReceipt',[]):
        if not Path(item['path']).is_file() or sha(item['path'])!=item['sha256']:raise ValueError('Completed capture artifact changed')
    receipt=admission_module(doc).validate_captures(batch,result['captures'],store.output)
    if not receipt.get('members') or receipt!=result['captureReceipt'] or \
            D.repeat_artifact_pins(doc['repo'],result['captures'])!=result['repeatReceipt']:
        raise ValueError('Unsealed result capture receipts differ')
    report=result['report']
    if body['phase']=='fit':
        if report.get('status')!='CAPTURED' or report.get('captures')!=result['captures'] or \
                not isinstance(report.get('analysis'),dict) or report['analysis'].get('status') in ('PASS','NEITHER',D.GATE_SUCCESS):
            raise ValueError('Unsealed fit result is not one verdict-free analysis')
    else:_CORE['C'].validate_report(doc,batch,expected,report,gate_result=template[0]['gateResult'])


def _seal_interrupted_result(root,contract,data):
    """Complete the seal of a result whose one complete write survived a crash before its sidecar
    (pre-seal review P3). Not a replay: nothing is measured, judged or chosen again; the bytes are
    the original invocation's, checked as that invocation and result_for check them. The caller
    holds the GPU lease the analysis ran under, so the invocation that wrote them has left it.
    Anything else after the analysis marker stays final."""
    body,store=data[1],data[5];Q=_CORE['Q']
    path=Path(str(contract)+'.result.json')
    if not path.is_file() or _sealed_result(contract):raise ValueError('Analysis already started')
    template=_template(root,contract,data)
    def seal():
        union=store.complete_union()
        def invalid(value):raise ValueError('Nonfinite JSON constant')
        _result_value(contract,data,template,json.loads(path.read_bytes(),parse_constant=invalid),union)
        _seal_written(path);result_for(contract)
    ok,_=Q.run_private(_fresh_log(store.output/'quarantine','analysis-seal'),seal)
    return Q.public_event('ANALYSIS_COMPLETE' if ok else 'ANALYSIS_STOPPED',phase=body['phase'])


def execute_analysis(root,contract):
    global _ACTIVE,_LEASE
    data=_phase(root,contract);doc,body,batch_path,batch,expected,store=data
    D=_CORE['C'].D;L=_CORE['L'];Q=_CORE['Q']
    with _gpu_lease():
        try:
            if store.analysis_marker.exists():return _seal_interrupted_result(root,contract,data)
            # Everything that can refuse is built before the one exclusive analysis marker; what
            # remains after it runs inside the quarantine (pre-seal review P3).
            union=store.complete_union();members=[r['member'] for r in union['members']]
            payloads=[r['payload'] for r in union['members']]
            if body['phase']=='exposure':payloads.append(store.native_metadata()['payload'])
            template=_template(root,contract,data)
            names=('measurement','fit') if body['phase']=='fit' else ('measurement','judge','owner') if body['phase']=='exposure' else ('measurement','judge')
            roles={name:_component(doc,name) for name in names}
            if body['phase']=='exposure':
                # The owner's last metadata-only admission before the marker (pre-seal review P1);
                # a refusal starts nothing and is retried by a later invocation.
                def admit():
                    ctx=_activate(template,data,'owner-admission',None);roles['owner'][0].admit(ctx,roles['owner'][1]);require_context(ctx)
                ok,_=Q.run_private(_fresh_log(store.output/'quarantine','owner-admission'),admit);_ACTIVE=None
                if not ok:return Q.public_event('REFUSED',phase=body['phase'])
            # The one exclusive marker is written only under the lease this invocation holds.
            if not D.lease_owned():return Q.public_event('LEASE_LOST',phase=body['phase'])
            store.start_analysis(_LEASE['token'])
            claim=L.pin(store.analysis_marker)
            def work():
                ctx=_activate(template,data,'analysis',claim,members,payloads)
                records=[Q.read_payload(ctx,r['payload']) for r in union['members']]
                captures={'schema':'w50-live-composed-captures-1','status':'CAPTURED',
                    'candidateSha256s':sorted(p['sha256'] for p in batch['cohort']),'captures':records}
                receipt=admission_module(doc).validate_captures(batch,captures,store.output)
                measurement,config=roles['measurement'];measured=measurement.evaluate(ctx,captures,config);require_context(ctx)
                if body['phase']=='fit':
                    fitter,config=roles['fit'];analysis=fitter.evaluate(ctx,measured,config);require_context(ctx)
                    if not isinstance(analysis,dict) or analysis.get('status') in ('PASS','NEITHER',D.GATE_SUCCESS):raise ValueError('Fit cannot issue a verdict')
                    report={'status':'CAPTURED','captures':captures,'analysis':analysis}
                else:
                    owner=None
                    if body['phase']=='exposure':
                        module,config=roles['owner'];owner=module.evaluate(ctx,captures,config);require_context(ctx)
                    judge,config=roles['judge']
                    report=judge.evaluate(ctx,{'measurement':measured,'owner':owner,'captures':captures},config);require_context(ctx)
                    # DL5m (4): current3's validate_report, behind the LIVE UNMEASURED_REPORTED check.
                    _CORE['C'].validate_report(doc,batch,expected,report,gate_result=ctx.get('gateResult'))
                if captures['captures']!=[L.read(L.checked(r['payload'])) for r in union['members']]:
                    raise ValueError('Analysis mutated the immutable original capture records')
                return D.write_sealed(Path(str(contract)+'.result.json'),{'contractSha256':sha(contract),
                    'claimSha256':sha(str(contract)+'.started.json'),'analysisClaim':claim,
                    'captureUnion':L.pin(store.home/'captures.complete.json'),'report':report,'captures':captures,
                    'captureReceipt':receipt,'repeatReceipt':D.repeat_artifact_pins(doc['repo'],captures)})
            ok,_=Q.run_private(store.output/'quarantine/analysis.log',work)
            return Q.public_event('ANALYSIS_COMPLETE' if ok else 'ANALYSIS_STOPPED',phase=body['phase'])
        finally:_ACTIVE=None


def public_status(root,contract):
    try:
        if _CORE is None:_prepare(root)
        def inspect():
            *_,store=_phase(root,contract)
            return store.status()
        ok,value=_CORE['Q'].run_silent(inspect)
        if ok:return value
    except BaseException:
        pass
    return {'schema':'w50-live-public-event-1','code':'REFUSED'}
