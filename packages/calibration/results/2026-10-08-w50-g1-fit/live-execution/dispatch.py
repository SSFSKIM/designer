"""Prospective LIVE phase/attempt dispatcher with a quarantined qualification boundary.

Consumer hooks are real prospectively pinned modules, not callbacks supplied at launch.
Capture: capture(context, member, config) -> {record, artifacts}; verify(context, member,
record, config) rechecks original reports/repeat admission without scoring. Native:
admit(context, config) at 'native-admission', read-only and before native.started.json, then
prepare(context, config) -> {ready: true, ...}, with an artifacts pin list. Measurement:
evaluate(context, captures, config). Fit/judge/owner: evaluate(context, evidence, config).
Initializer remains a separate pre-render entrypoint behind verify_prefit.

Operational stops (DL5k) are always preserved: an exception after an attempt's claim writes
its failure record before propagating; a killed attempt is preserved by stop_stale_attempt
once its process and its GPU lease are both gone. A capture role signals a census refusal by
raising CensusRefused; a lost GPU lease is classified from the lock itself.

Protected payload access is instrument/API enforced plus the wave's role discipline.
It is NOT OS isolation. No agent may open native/quarantine files directly before the
complete-union measurement/judge marker. Every public execution result is allowlisted.
"""
import copy
import hashlib
import json
import os
from pathlib import Path
import sys
import types

HERE=Path(__file__).resolve().parent
_CORE=None
_ACTIVE=None
_LEASE=None


class CensusRefused(RuntimeError):
    """Raised by a live capture role when the classifying census refuses before a draw."""


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(path):return json.loads(Path(path).read_text())
def source(path,name):
    m=types.ModuleType(name);m.__file__=str(path);sys.modules[name]=m
    exec(compile(Path(path).read_bytes(),str(path),'exec',dont_inherit=True),m.__dict__)
    return m


def _prepare(path):
    global _CORE
    path=Path(path).resolve();doc=load(path);repo=Path(doc['repo']).resolve()
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
    root=Path(root).resolve();doc=root_doc(root);D=_CORE['C'].D;repo=Path(doc['repo'])
    batch=D.load(batch_path);phase=batch.get('phase')
    if phase not in ('fit','gate','exposure'):raise ValueError('Only scientific LIVE phases are admitted')
    batch,_=D.validate_batch(doc,batch_path,phase);_live_batch(doc,batch)
    if phase=='fit' and (root.parent/D.SLOTS['gate']).exists():raise ValueError('Gate already froze fitting')
    prefit=verify_prefit(root,doc);output=Path(output).resolve()
    if output.exists() or output.is_relative_to(repo):raise ValueError('Logical phase needs fresh external output')
    extra={}
    if phase=='gate':
        if fit_record is None:raise ValueError('Gate requires one real completed fit selection')
        record=load(fit_record)
        for item in record.get('completed',[]):result_for(str(D.checked(repo,item)).removesuffix('.result.json'))
        D.validate_fit_record(root,doc,batch['cohort'],fit_record);extra['fitRecord']=D.pin(repo,fit_record)
    if phase=='exposure':
        result_for(root.parent/D.SLOTS['gate'])
        gate,result=_CORE['C'].checked_gate_result(root,doc)
        if D.sealed(gate)['cohort']!=batch['cohort']:raise ValueError('Exposure changes frozen gate cohort')
        extra={'gateContract':D.pin(repo,gate),'gateResult':D.pin(repo,Path(str(gate)+'.result.json'))}
    target=root.parent/'fit'/f'{sha(batch_path)}.json' if phase=='fit' else root.parent/D.SLOTS[phase]
    # Everything the journal derives from the contract is derived before anything is durable, so a
    # malformed batch refuses here instead of burning a one-shot slot.
    L=_CORE['L'];L.Store(target,batch,output)
    if target.exists() or Path(str(target)+'.sha256').exists():raise ValueError('Logical phase slot already exists')
    marker=L.claim_output(output,target)
    return D.write_sealed(target,{'schema':'w50-g1-phase-contract-1','executionRootSha256':sha(root),
        'phase':phase,'batch':D.pin(repo,batch_path),'cohort':batch['cohort'],'preFitEvidence':prefit,
        'logicalOutput':str(output),'outputMarker':marker,**extra})


def _live_batch(doc,batch):
    """LIVE's batch shape beyond the original admission, which treats a baseline as optional."""
    if batch['phase']=='exposure' and any(run.get('baselineCandidate') not in doc['baselineDocuments'] for run in batch['runs']):
        raise ValueError('Every exposure run needs its registered same-cell baseline candidate')


def _phase(root,contract):
    doc=root_doc(root);D=_CORE['C'].D;body=D.sealed(contract);repo=Path(doc['repo'])
    phase=body['phase'];batch_path=D.checked(repo,body['batch']);batch,expected=D.validate_batch(doc,batch_path,phase)
    _live_batch(doc,batch)
    target=Path(root).parent/'fit'/f'{sha(batch_path)}.json' if phase=='fit' else Path(root).parent/D.SLOTS[phase]
    if Path(contract).resolve()!=target.resolve() or body['executionRootSha256']!=sha(root) or body['cohort']!=batch['cohort']:
        raise ValueError('Wrong logical phase authority')
    if body['preFitEvidence']!=verify_prefit(root,doc):raise ValueError('Pre-fit evidence changed')
    if phase=='fit' and (Path(root).parent/D.SLOTS['gate']).exists():raise ValueError('Gate froze fitting')
    if phase=='gate':D.validate_fit_record(root,doc,batch['cohort'],D.checked(repo,body['fitRecord']))
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


def _context(root,contract,phase_data,stage,claim,members=(),payloads=()):
    global _ACTIVE
    doc,body,batch_path,batch,expected,store=phase_data;L=_CORE['L'];D=_CORE['C'].D
    logical=Path(str(contract)+'.started.json')
    context={'repo':doc['repo'],'executionRoot':str(Path(root).resolve()),'contract':str(Path(contract).resolve()),
        'batchPath':str(batch_path),'batch':batch,'phase':body['phase'],'stage':stage,'output':str(store.output),
        'logicalClaim':L.pin(logical),'executionClaim':claim,'inputs':doc['inputs'],'expectedCells':expected,
        'baselineDocuments':doc['baselineDocuments'],'repeatAdmission':doc['repeatAdmission'],
        'phaseDependencies':doc['phaseDependencies'],'ownerUnionKeys':doc['phaseDependencies']['ownerUnionKeys'],
        'unionExpectedCells':[{k:r[k] for k in D.KEY} for r in D.load(D.checked(doc['repo'],doc['references']))['cells']]}
    if body['phase']=='exposure':
        gate=result_for(D.checked(doc['repo'],body['gateContract']))
        context.update(gateResult=body['gateResult'],gateCaptures=gate['captures'],gateReport=gate['report'])
    else:context.update(gateResult=None,gateCaptures=None,gateReport=None)
    hashes=[(context['executionRoot'],sha(root)),(str(contract),sha(contract)),(str(batch_path),sha(batch_path)),
        (claim['path'],claim['sha256']),(str(logical),sha(logical))]
    numerical=L.read(logical).get('numericalAdmission')
    for item in (numerical,context['gateResult']):
        if item is not None:hashes.append((str(D.checked(doc['repo'],item)),item['sha256']))
    _ACTIVE={'context':context,'snapshot':copy.deepcopy(context),'hashes':hashes,'doc':doc,'store':store,'numerical':numerical,
        'members':list(members),'payloads':list(payloads),
        'records':{r['member']['id']:L.read(L.checked(r['payload'])) for r in store.checkpoints()} if stage in ('analysis','qualification') else {}}
    sys.modules['w50_g1_dispatch']=sys.modules[__name__]
    return context


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


def _alive(pid):
    """A claim whose process cannot be signalled is gone; a reused PID reads alive (safe side)."""
    if type(pid) is not int or pid<=0:raise ValueError('Claim has no process identity')
    if pid==os.getpid():return True
    try:os.kill(pid,0)
    except ProcessLookupError:return False
    except PermissionError:return True
    return True


def _release_stale_lease(claim):
    """Prove a claim's process and lease are gone; remove the lock only if it is that lease's.

    The lock is touched only when it still carries the claim's own token, read and unlinked as
    the same file. A lock held under another token is another owner's and is never removed."""
    token=claim.get('gpuLease')
    if not isinstance(token,str) or f' pid={claim.get("pid")} ' not in token or _alive(claim.get('pid')):
        raise ValueError('Claim process may still own its lease')
    lock=_CORE['C'].D.GPU_LOCK
    try:
        with open(lock) as handle:
            held=handle.read();identity=os.fstat(handle.fileno())
    except FileNotFoundError:
        return 'absent'
    if held!=token:raise ValueError('GPU lock belongs to another lease; not touched')
    now=os.stat(lock)
    if (now.st_dev,now.st_ino)!=(identity.st_dev,identity.st_ino):raise ValueError('GPU lock changed while checked')
    os.unlink(lock)
    return 'removed-same-token'


def stop_stale_attempt(root,contract,code):
    """Preserve a killed attempt (claim without failure/completion) as an operational stop.

    Writes the failure record with its inventory, so prepare_attempt's reconciliation runs next."""
    global _LEASE
    store=_phase(root,contract)[5];D=_CORE['C'].D;L=_CORE['L'];Q=_CORE['Q']
    prior=store._contracts()
    if not prior:raise ValueError('No attempt to preserve')
    folder=prior[-1].parent;attempt=L.read(prior[-1])
    if not (folder/'started.json').exists() or (folder/'failure.json').exists() or (folder/'complete.json').exists():
        raise ValueError('Only a started, unstopped, incomplete attempt can be preserved as stale')
    claim=L.read(folder/'started.json')
    lock=_release_stale_lease(claim)
    with D.owned_gpu_lock():
        _LEASE=D._LEASE
        try:store.stop(attempt,code,stale={'pid':claim['pid'],'gpuLease':claim['gpuLease'],'lock':lock})
        finally:_LEASE=None
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
        last=runs[-1];started=L.read(last/'started.json')
        if not (last/'failure.json').exists():
            # A killed reconciliation: this process holds the GPU lease, so only its PID remains.
            if _alive(started.get('pid')):raise ValueError('Prior reconciliation may still be running')
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


def prepare_attempt(root,contract):
    global _ACTIVE,_LEASE
    data=_phase(root,contract);doc,body,batch_path,batch,expected,store=data
    D=_CORE['C'].D;L=_CORE['L'];prior=store._contracts()
    if store.analysis_marker.exists():raise ValueError('Analysis already started')
    if (store.home/'native.started.json').exists() and not (store.home/'native.complete.json').exists():
        raise ValueError('Incomplete native subread cannot be replayed')
    if prior and not (prior[-1].parent/'started.json').exists():
        # Planned but never claimed: the same centrally derived attempt is still the next one.
        return L.read(prior[-1])
    if prior:
        old=L.read(prior[-1]);failure_path=prior[-1].parent/'failure.json'
        if not failure_path.exists():raise ValueError('Prior attempt is not a preserved stop (see stop_stale_attempt)')
        failure=L.read(failure_path)
        for item in failure['inventory']:L.checked(item)
        done={r['member']['id'] for r in store.checkpoints()}
        orphans=[m for m in old['members'] if m['id'] not in done and Path(m['run']['captureRoot']).parent.exists()]
        if orphans:
            with D.owned_gpu_lock():
                _LEASE=D._LEASE
                try:_reconcile(root,contract,data,store,prior[-1],failure_path,failure,orphans)
                finally:_ACTIVE=None;_LEASE=None
    if len(store.checkpoints())==len(store.population):
        # A crash after the last qualified cell may need only the existing attempt's final marker.
        old=L.read(prior[-1]);folder=prior[-1].parent
        if not (folder/'complete.json').exists():store.finish(old)
        return {'schema':'w50-live-capture-ready-1','logicalContract':L.pin(contract)}
    return store.plan()


def execute_attempt(root,contract,attempt):
    global _ACTIVE,_LEASE
    data=_phase(root,contract);doc,body,batch_path,batch,expected,store=data
    D=_CORE['C'].D;L=_CORE['L'];Q=_CORE['Q']
    numerical=admission_module(doc).validate_numerical(doc,batch)
    with D.owned_gpu_lock():
        _LEASE=D._LEASE
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
                    retained=store.checkpoints()
                    if body['phase']=='exposure' and (store.home/'native.complete.json').exists():
                        ctx=_context(root,contract,data,'qualification',claim,[r['member'] for r in retained])
                        native,nconfig=_component(doc,'native');native.verify(ctx,qualification_native(ctx),nconfig);require_context(ctx)
                    if retained:
                        ctx=_context(root,contract,data,'qualification',claim,[r['member'] for r in retained])
                        for r in retained:
                            capture.verify(ctx,r['member'],L.read(L.checked(r['payload'])),config)
                            require_context(ctx)
                    if body['phase']=='exposure' and not (store.home/'native.complete.json').exists():
                        native,nconfig=_component(doc,'native')
                        # A native read that starts without a checkpoint is never replayed (DL5k),
                        # so a refusable environment (asset, archive tree, pins) is admitted here,
                        # read-only: a refusal is this attempt's ordinary recoverable stop.
                        ctx=_context(root,contract,data,'native-admission',claim);native.admit(ctx,nconfig);require_context(ctx)
                        store.start_native(attempt)
                        ctx=_context(root,contract,data,'native',claim)
                        payload=native.prepare(ctx,nconfig);require_context(ctx)
                        native.verify(ctx,payload,nconfig);require_context(ctx)
                        store.complete_native(payload,payload.get('artifacts',[]))
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
        finally:_ACTIVE=None;_LEASE=None


def execute_analysis(root,contract):
    global _ACTIVE,_LEASE
    data=_phase(root,contract);doc,body,batch_path,batch,expected,store=data
    D=_CORE['C'].D;L=_CORE['L'];Q=_CORE['Q']
    with D.owned_gpu_lock():
        _LEASE=D._LEASE
        try:
            union=store.complete_union();store.start_analysis(_LEASE['token'])
            claim=L.pin(store.analysis_marker);members=[r['member'] for r in union['members']]
            payloads=[r['payload'] for r in union['members']]
            if body['phase']=='exposure':payloads.append(store.native_metadata()['payload'])
            ctx=_context(root,contract,data,'analysis',claim,members,payloads)
            def work():
                records=[Q.read_payload(ctx,r['payload']) for r in union['members']]
                captures={'schema':'w50-live-composed-captures-1','status':'CAPTURED',
                    'candidateSha256s':sorted(p['sha256'] for p in batch['cohort']),'captures':records}
                receipt=admission_module(doc).validate_captures(batch,captures,store.output)
                measurement,config=_component(doc,'measurement');measured=measurement.evaluate(ctx,captures,config);require_context(ctx)
                if body['phase']=='fit':
                    fitter,config=_component(doc,'fit');analysis=fitter.evaluate(ctx,measured,config);require_context(ctx)
                    if not isinstance(analysis,dict) or analysis.get('status') in ('PASS','NEITHER',D.GATE_SUCCESS):raise ValueError('Fit cannot issue a verdict')
                    report={'status':'CAPTURED','captures':captures,'analysis':analysis}
                else:
                    owner=None
                    if body['phase']=='exposure':
                        module,config=_component(doc,'owner');owner=module.evaluate(ctx,captures,config);require_context(ctx)
                    judge,config=_component(doc,'judge')
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
        finally:_ACTIVE=None;_LEASE=None


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
