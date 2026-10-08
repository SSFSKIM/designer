"""Prospective LIVE phase/attempt dispatcher with a quarantined qualification boundary.

Consumer hooks are real prospectively pinned modules, not callbacks supplied at launch.
Capture: capture(context, member, config) -> {record, artifacts}; verify(context, member,
record, config) rechecks original reports/repeat admission without scoring. Native:
prepare(context, config) -> {ready: true, ...}, with an artifacts pin list. Measurement:
evaluate(context, captures, config). Fit/judge/owner: evaluate(context, evidence, config).
Initializer remains a separate pre-render entrypoint behind verify_prefit.

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
    batch,_=D.validate_batch(doc,batch_path,phase)
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
        gate,result=D.checked_gate_result(root,doc)
        if D.sealed(gate)['cohort']!=batch['cohort']:raise ValueError('Exposure changes frozen gate cohort')
        extra={'gateContract':D.pin(repo,gate),'gateResult':D.pin(repo,Path(str(gate)+'.result.json'))}
    target=root.parent/'fit'/f'{sha(batch_path)}.json' if phase=='fit' else root.parent/D.SLOTS[phase]
    return D.write_sealed(target,{'schema':'w50-g1-phase-contract-1','executionRootSha256':sha(root),
        'phase':phase,'batch':D.pin(repo,batch_path),'cohort':batch['cohort'],'preFitEvidence':prefit,
        'logicalOutput':str(output),**extra})


def _phase(root,contract):
    doc=root_doc(root);D=_CORE['C'].D;body=D.sealed(contract);repo=Path(doc['repo'])
    phase=body['phase'];batch_path=D.checked(repo,body['batch']);batch,expected=D.validate_batch(doc,batch_path,phase)
    target=Path(root).parent/'fit'/f'{sha(batch_path)}.json' if phase=='fit' else Path(root).parent/D.SLOTS[phase]
    if Path(contract).resolve()!=target.resolve() or body['executionRootSha256']!=sha(root) or body['cohort']!=batch['cohort']:
        raise ValueError('Wrong logical phase authority')
    if body['preFitEvidence']!=verify_prefit(root,doc):raise ValueError('Pre-fit evidence changed')
    if phase=='fit' and (Path(root).parent/D.SLOTS['gate']).exists():raise ValueError('Gate froze fitting')
    if phase=='gate':D.validate_fit_record(root,doc,batch['cohort'],D.checked(repo,body['fitRecord']))
    if phase=='exposure':
        result_for(D.checked(repo,body['gateContract']));gate,result=D.checked_gate_result(root,doc)
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
    _ACTIVE={'context':context,'snapshot':copy.deepcopy(context),'hashes':hashes,'doc':doc,'store':store,
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
    pins=_CORE['C'].D.repeat_artifact_pins(doc['repo'],{'captures':[record]})
    artifacts=list(declared)
    for item in [*pins,*(record['artifacts'][k] for k in ('png','cell','report'))]:
        if item not in artifacts:artifacts.append(item)
    for key in ('png','cell','report'):
        if not Path(record['artifacts'][key]['path']).resolve().is_relative_to(Path(member['run']['captureRoot']).resolve()):
            raise ValueError('Capture artifact escaped its actual member destination')
    return artifacts


def prepare_attempt(root,contract):
    global _ACTIVE,_LEASE
    data=_phase(root,contract);doc,body,batch_path,batch,expected,store=data
    D=_CORE['C'].D;L=_CORE['L'];Q=_CORE['Q'];prior=store._contracts()
    if store.analysis_marker.exists():raise ValueError('Analysis already started')
    if (store.home/'native.started.json').exists() and not (store.home/'native.complete.json').exists():
        raise ValueError('Incomplete native subread cannot be replayed')
    if prior:
        old=L.read(prior[-1]);failure_path=prior[-1].parent/'failure.json'
        if not failure_path.exists():raise ValueError('Prior attempt is not a preserved stop')
        failure=L.read(failure_path)
        for item in failure['inventory']:L.checked(item)
        done={r['member']['id'] for r in store.checkpoints()}
        orphans=[m for m in old['members'] if m['id'] not in done and Path(m['run']['captureRoot']).parent.exists()]
        if orphans:
            with D.owned_gpu_lock():
                _LEASE=D._LEASE
                try:
                    claim_path=store.home/'reconciliations'/(sha(failure_path)+'.started.json')
                    claim=L.write_once(claim_path,{'schema':'w50-live-reconciliation-claim-1','logicalContract':L.pin(contract),
                        'failedAttempt':L.pin(prior[-1]),'failure':L.pin(failure_path),'pid':os.getpid(),'gpuLease':_LEASE['token']})
                    ctx=_context(root,contract,data,'qualification',claim,orphans)
                    def recover():
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
                    ok,_=Q.run_private(store.output/'quarantine'/('reconciliation-'+sha(failure_path)+'.log'),recover)
                    if not ok:raise ValueError('Source reconciliation stopped; protected details remain quarantined')
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
                    store.start_native(attempt)
                    ctx=_context(root,contract,data,'native',claim)
                    native,nconfig=_component(doc,'native');payload=native.prepare(ctx,nconfig);require_context(ctx)
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
            ok,_=Q.run_private(store.output/'attempts'/f'{attempt["ordinal"]:06d}'/'quarantine/worker.log',work)
            if not ok:store.stop(attempt,'INSTRUMENT_FAULT')
            return Q.public_event('ATTEMPT_COMPLETE' if ok else 'INSTRUMENT_FAULT',phase=body['phase'],attempt=attempt['ordinal'])
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
                    D.validate_report(doc,batch,expected,report,gate_result=ctx.get('gateResult'))
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
