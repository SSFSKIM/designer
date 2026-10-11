"""Run one source-sealed W51 population, resuming only pre-analysis capture work.

--population selects declared data, never a different pipeline. Rehearsals have explicit test
output namespaces; the gate has one root-owned slot, so changing --output cannot retry it.
There is deliberately no exposure command. The coordinator supplies clearance after review.
"""
import argparse
import contextlib
import copy
import fcntl
import hashlib
import gzip
import json
import os
from pathlib import Path
import re
import sys
import traceback
import types
import uuid

HERE = Path(__file__).resolve().parent
POPULATIONS = ('real-rehearsal','synthetic-rehearsal','gate')
GPU_LOCK = Path('/tmp/w49-gpu.lock')
_INVOCATION = None


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(path):
    raw=Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if raw.startswith(b'\x1f\x8b') else raw)
def source(path, name):
    module=types.ModuleType(name); module.__file__=str(path); sys.modules[name]=module
    exec(compile(Path(path).read_bytes(),str(path),'exec',dont_inherit=True),module.__dict__)
    return module


def bind_slot(root, population, output):
    """One protected gate across all outputs; named rehearsal outputs are separate test runs."""
    if population not in POPULATIONS: raise ValueError('Exposure is not executable')
    journal=source(HERE/'journal.py','w51_slot_journal')
    root,output=Path(root).resolve(),Path(output).resolve()
    key='gate' if population=='gate' else population+'-'+hashlib.sha256(str(output).encode()).hexdigest()[:20]
    target=root.parent/'execution-slots'/f'{key}.json'
    value={'root':journal.pin(root),'population':population,'output':str(output)}
    if target.exists():
        if load(target)!=value: raise ValueError('Population slot already owns another output/root')
    else: journal.write_once(target,value)
    return target


def alive(pid):
    try: os.kill(pid,0); return True
    except ProcessLookupError: return False
    except PermissionError: return True


@contextlib.contextmanager
def gpu_lease():
    mutex=os.open(str(GPU_LOCK)+'.mutex',os.O_RDWR|os.O_CREAT,0o600)
    token=f'W50 pid={os.getpid()} owner={uuid.uuid4().hex}\n'
    try:
        fcntl.flock(mutex,fcntl.LOCK_EX)
        if GPU_LOCK.exists():
            old=GPU_LOCK.read_text(); match=re.fullmatch(r'W50 pid=([1-9][0-9]*) owner=[a-f0-9]{32}\n',old)
            if match is None or alive(int(match[1])): raise FileExistsError('GPU lease held')
            if GPU_LOCK.read_text()!=old: raise FileExistsError('GPU lease changed')
            GPU_LOCK.unlink()
        with GPU_LOCK.open('x') as handle:
            handle.write(token);handle.flush();os.fsync(handle.fileno())
        stat=GPU_LOCK.stat(); lease={'token':token,'identity':(stat.st_dev,stat.st_ino)}
        fcntl.flock(mutex,fcntl.LOCK_UN)
        try: yield lease
        finally:
            if lease_owned(lease): GPU_LOCK.unlink()
    finally: os.close(mutex)


@contextlib.contextmanager
def private_stream(stream):
    """Quarantine Python, native-extension and child-process streams through preparation."""
    for handle in (sys.stdout,sys.stderr):handle.flush()
    saved=[os.dup(1),os.dup(2)]
    try:
        os.dup2(stream.fileno(),1);os.dup2(stream.fileno(),2)
        with contextlib.redirect_stdout(stream),contextlib.redirect_stderr(stream):
            yield
    finally:
        try:stream.flush();os.fsync(stream.fileno())
        finally:
            for fd,original in zip((1,2),saved):os.dup2(original,fd);os.close(original)


def lease_owned(lease):
    if lease is None: return False
    try:
        stat=GPU_LOCK.stat()
        return (stat.st_dev,stat.st_ino)==lease['identity'] and GPU_LOCK.read_text()==lease['token']
    except FileNotFoundError: return False


class Engine:
    """The only provider of live role capabilities; callers cannot supply their own context."""
    class CensusRefused(RuntimeError): pass

    def __init__(self, prepared, root_module, journal, lease):
        if _INVOCATION is None or _INVOCATION['prepared'] is not prepared or not lease_owned(lease):
            raise ValueError('Engine requires the fenced, admitted single entrypoint')
        journal.checked(_INVOCATION['fence']);journal.checked(_INVOCATION['slot'])
        self.p=prepared;self.R=root_module;self.J=journal;self._LEASE=lease;self.active=None
        self.doc=prepared['root'];self.science=prepared['dataset'];self.output=Path(prepared['output'])
        self.contract=self.output/'contract.json';self.batch=prepared['batch']
        self.L=self.R.source(HERE/'lifecycle.py','w51_lifecycle')
        self.A=self.R.source(self.R.FIT/'live-execution/admission.py','w51_admission')
        self.store=self.L.Store(self.contract,self.batch,self.output)
        self.roles={name:(self.R.source(self.R.checked(self.R.REPO,role['entrypoint']),'w51_role_'+name),role['config'])
                    for name,role in self.science['instruments'].items()}
        sys.modules['w50_g1_dispatch']=self

    sha=staticmethod(sha)
    load=staticmethod(load)
    def checked(self,repo,item): return self.R.checked(repo,item)
    def sealed(self,path): return self.R.sealed(path)
    def admission_module(self,doc): return self.A
    def scientific_inputs(self,context):
        self.require_context(context)
        actual=self.R.dataset(self.doc,context['population'])
        if actual!=self.science or context['datasetPin']!=self.p['datasetPin']:
            raise ValueError('Changed explicit scientific dataset')
        return actual
    def validate_context_population(self,context,doc):
        self.require_context(context);self.R.validate_context_population(context,self.doc,doc)
    def require_context(self,context):
        if self.active is None or context is not self.active['context'] or not lease_owned(self._LEASE):
            raise ValueError('No genuine W51 context/lease')
        if context!=self.active['snapshot'] or any(sha(p)!=h for p,h in self.active['hashes']):
            raise ValueError('Changed W51 context/authority')
        return context
    def policy_authority_hashes(self):
        static = self.R.source(HERE/'static.py', 'w51_active_policy_authority')
        static.bound_landing_policy(self.doc, self.science, self.science['inputs'])
        return [(str(self.R.checked(self.doc['repo'], pin)), pin['sha256'])
                for pin in static.landing_policy_pins(self.doc, self.science)]

    def require_payload(self,context,item):
        self.require_context(context)
        if context['stage']!='analysis' or item not in self.active['payloads']:
            raise ValueError('Payload outside complete analysis union')
    def require_render_admission(self,context,run,current=False):
        self.require_context(context)
        if current or context['stage']!='capture' or not any(m['run']==run for m in self.active['members']):
            raise ValueError('Render outside remaining fixed capture member')
        for name in ('captureRoot','matrixPath'):
            if not self.R.ordinary(run[name]).is_relative_to(self.output):
                raise ValueError('Render destination escaped its owned output')
        self.checked(context['repo'],self.doc['numerical'])
        self.A.endpoints(self.doc,run['candidate'])
        return run
    def render_environment(self,context,run):
        self.require_render_admission(context,run)
        member=next(m for m in self.active['members'] if m['run']==run)
        value={'root':self.J.pin(context['executionRoot']),'contract':self.J.pin(context['contract']),
               'batch':self.J.pin(context['batchPath']),'claim':context['executionClaim'],'member':member}
        path=Path(run['captureRoot']).parent/'render-authority.json'
        pin=self.J.write_once(path,value)
        return {'W51_MEMBER_AUTHORITY':pin['path'],'W51_MEMBER_AUTHORITY_SHA256':pin['sha256']}

    def require_read_admission(self,context,run,current=False):
        self.require_context(context)
        if current or context['stage'] not in ('qualification','analysis') or not any(m['run']==run for m in self.active['members']):
            raise ValueError('Read outside retained member population')
        return run
    def resolve_capture_run(self,context,receipt):
        self.require_context(context)
        if context['stage'] not in ('qualification','analysis'): raise ValueError('No retained-read capability')
        found=[m for m in self.active['members'] if all(receipt.get(k)==m['run'].get(k)
            for k in ('profile','renderer','candidate')) and receipt['scene']==m['scene'] and receipt['lane']==m['lane']]
        if len(found)!=1 or self.active['records'].get(found[0]['id'])!=receipt:
            raise ValueError('Capture receipt differs from original checkpoint')
        return copy.deepcopy(found[0]['run'])

    def context(self,stage,claim,members=(),payloads=()):
        root_path=self.p['rootPath'];batch_path=self.p['batchPath']
        logical=self.J.pin(str(self.contract)+'.started.json')
        value={'repo':self.doc['repo'],'executionRoot':root_path,'contract':str(self.contract),
            'batchPath':batch_path,'batch':self.batch,'phase':'gate','output':str(self.output),
            'population':self.p['population'],'populationPin':self.p['populationPin'],
            'datasetPin':self.p['datasetPin'],'dataOrigin':self.science['dataOrigin'],
            'logicalClaim':logical,'executionClaim':claim,'stage':stage,'inputs':self.science['inputs'],
            'expectedCells':self.p['expectedCells'],'phaseDependencies':self.p['phaseDependencies'],
            'baselineDocuments':self.science['baselineDocuments'],'repeatAdmission':self.science['repeatAdmission'],
            'ownerUnionKeys':self.science['phaseDependencies']['ownerUnionKeys'],
            'unionExpectedCells':[{k:r[k] for k in self.R.KEY} for r in
                self.load(self.checked(self.doc['repo'],self.science['references']))['cells']],
            'gateResult':None,'gateCaptures':None,'gateReport':None}
        hashes=[(root_path,sha(root_path)),(batch_path,sha(batch_path)),(str(self.contract),sha(self.contract)),
                (logical['path'],logical['sha256']),(claim['path'],claim['sha256']),
                *self.policy_authority_hashes()]
        self.active={'context':value,'snapshot':copy.deepcopy(value),'hashes':hashes,
            'members':copy.deepcopy(list(members)),'payloads':copy.deepcopy(list(payloads)),
            'records':{r['member']['id']:self.load(self.L.checked(r['payload'])) for r in self.store.checkpoints()}}
        return value

    def create_contract(self):
        numerical=self.A.validate_numerical(self.doc,self.batch)
        value={'schema':'w51-phase-contract-1','executionRootSha256':sha(self.p['rootPath']),
            'phase':'gate','population':self.p['populationPin'],'dataset':self.p['datasetPin'],
            'batch':self.R.pin(self.p['batchPath']),'cohort':self.batch['cohort'],
            'importedFit':self.doc['importedFit'],'preFitEvidence':self.science['preFitEvidence'],
            'logicalOutput':str(self.output)}
        marker=self.output/self.L.OUTPUT_MARKER
        marker_value={'schema':'w50-live-phase-output-1','contract':str(self.contract)}
        if marker.exists():
            if self.load(marker)!=marker_value: raise ValueError('Changed logical output claim')
        else:self.J.write_once(marker,marker_value)
        value['outputMarker']=self.J.pin(marker)
        self._same_or_write(self.contract,value,sealed=True)
        self._same_or_write(Path(str(self.contract)+'.started.json'),
            {'contractSha256':sha(self.contract),'batchSha256':sha(self.p['batchPath']),
             'phase':'gate','output':str(self.output),'numericalAdmission':numerical})

    def _same_or_write(self,path,value,sealed=False):
        if path.exists():
            if self.load(path)!=value: raise ValueError('Changed immutable phase record')
        else:self.J.write_once(path,value)
        if sealed:
            side=Path(str(path)+'.sha256');text=f'{sha(path)}  {path.name}\n'
            if side.exists():
                if side.read_text()!=text: raise ValueError('Changed phase seal')
            else:
                self.J.write_bytes(side,text.encode())

    def recover_orphans(self,a):
        folder=self.store.attempts/f'{a["ordinal"]:06d}'
        capture,config=self.roles['capture'];done={r['member']['id'] for r in self.store.checkpoints()}
        pending=[m for m in a['members'] if m['id'] not in done and Path(m['run']['captureRoot']).parent.exists()]
        if not pending:return
        ordinal=len(list((folder/'reconciliations').glob('*')))+1
        claim=self.J.write_once(folder/'reconciliations'/f'{ordinal:06d}'/'started.json',
            {'schema':'w50-live-reconciliation-claim-1','logicalContract':self.J.pin(self.contract),
             'failedAttempt':self.J.pin(folder/'contract.json'),'failure':self.J.pin(folder/'failure.json'),
             'ordinal':ordinal,'pid':os.getpid(),'gpuLease':self._LEASE['token']})
        ctx=self.context('qualification',claim,pending)
        for member in pending:
            result=capture.recover(ctx,member,config);self.require_context(ctx)
            if result is not None:
                capture.verify(ctx,member,result['record'],config)
                self.store.adopt(a,member,result['record'],result['artifacts'],claim)

    def captures(self):
        if self.store.analysis_marker.exists():raise ValueError('Analysis already consumed')
        previous=self.store._contracts();a=None
        if previous:
            old=self.load(previous[-1]);folder=previous[-1].parent
            if not (folder/'started.json').exists():a=old
            elif not (folder/'complete.json').exists():
                if not (folder/'failure.json').exists():
                    claim=self.load(folder/'started.json')
                    if alive(claim['pid']) and claim['pid']!=os.getpid():raise ValueError('Prior attempt still alive')
                    self.store.stop(old,'INSTRUMENT_FAULT',stale={'deadPid':claim['pid']})
                self.recover_orphans(old)
        retained=self.store.checkpoints()
        if len(retained)==len(self.store.population):
            last=self.load(self.store._contracts()[-1]);folder=self.store._contracts()[-1].parent
            if not (folder/'complete.json').exists():self.store.finish(last)
            return self.store.complete_union()
        a=a or self.store.plan();claim=self.store.start(a,self._LEASE['token'])
        capture,config=self.roles['capture']
        try:
            if retained:
                ctx=self.context('qualification',claim,[r['member'] for r in retained])
                for item in retained:capture.verify(ctx,item['member'],self.load(self.L.checked(item['payload'])),config)
            for member in a['members']:
                ctx=self.context('capture',claim,[member]);result=capture.capture(ctx,member,config)
                self.require_context(ctx);capture.verify(ctx,member,result['record'],config)
                self.require_context(ctx);self.store.checkpoint(a,member,result['record'],result['artifacts'])
            self.store.finish(a)
        except BaseException as error:
            folder=self.store.attempts/f'{a["ordinal"]:06d}'
            if not (folder/'failure.json').exists():
                self.store.stop(a,'CENSUS_REFUSED' if isinstance(error,self.CensusRefused) else
                                'LEASE_LOST' if not lease_owned(self._LEASE) else 'INSTRUMENT_FAULT')
            raise
        return self.store.complete_union()

    def analyze(self,union,identity):
        if not lease_owned(self._LEASE):raise ValueError('Lease lost before analysis marker')
        if self.store.analysis_marker.exists():raise ValueError('Analysis already consumed')
        self.policy_authority_hashes()
        self.store.start_analysis(self._LEASE['token'])
        self.J.sync_directory(self.store.home)
        claim=self.J.pin(self.store.analysis_marker)
        try:
            members=[r['member'] for r in union['members']];payloads=[r['payload'] for r in union['members']]
            ctx=self.context('analysis',claim,members,payloads)
            captures={'schema':'w50-live-composed-captures-1','status':'CAPTURED',
                'candidateSha256s':sorted(p['sha256'] for p in self.batch['cohort']),
                'captures':[self.load(self.L.checked(p)) for p in payloads]}
            receipt=self.A.validate_captures(self.batch,captures,self.output)
            measurement,config=self.roles['measurement'];measured=measurement.evaluate(ctx,captures,config)
            self.require_context(ctx)
            judge,config=self.roles['judge'];report=judge.evaluate(ctx,{'measurement':measured,'owner':None,'captures':captures},config)
            self.require_context(ctx)
            witness=self.R.source(HERE/'witness.py','w51_witness').verify(self,ctx,union,captures,receipt,measured,report)
            self.require_context(ctx)
            prepared=self.J.prepare(self.output,report,witness,identity)
            self.require_context(ctx)
            return prepared
        except BaseException:
            # Preparation never creates eligibility; a failed fault write cannot restore PASS.
            with contextlib.suppress(BaseException):
                self.J.fail(self.output,'POST_MARKER_INSTRUMENT_FAULT',identity)
            raise
        finally:self.active=None


def bootstrap(root_path):
    """Only the four bootstrap modules execute before the permanent guard is installed."""
    path=Path(root_path).resolve();doc=load(path)
    if Path(str(path)+'.sha256').read_text()!=f'{sha(path)}  {path.name}\n':raise ValueError('Root seal differs')
    repo=Path(doc['repo']).resolve();sources=doc['closure']['sources']
    for name in ('run.py','root.py','journal.py','guard.py'):
        p=HERE/name
        if sources.get(str(p.relative_to(repo)))!=sha(p):raise ValueError('Changed bootstrap source')
    return doc


def analysis_consumed(marker):
    """Only ENOENT proves an absent marker; Path.exists hides other I/O errors too."""
    try:marker.stat()
    except FileNotFoundError:return False
    except OSError:return True
    return True


def existing_completion(output,journal=None):
    """An invocation error is not permission to revoke an earlier terminal commit.

    Before bootstrap succeeds we may inspect presence, but must not execute an unauthenticated
    journal to recover a verdict. Unknown status is operational, never a scientific NEITHER.
    """
    unavailable={'status':'STATUS_UNAVAILABLE','judgeCompleted':None,
                 'analysisConsumed':True,'publication':'UNKNOWN'}
    try:(Path(output)/'terminal.json').stat()
    except FileNotFoundError:return None
    except OSError:return unavailable
    if journal is None:return unavailable
    try:
        result=journal.terminal(output)
        if result is None or not result['judgeCompleted']:return unavailable
        return {'status':result['status'],'judgeCompleted':True,'analysisConsumed':True,
                'publication':'COMMITTED_WITH_INVOCATION_ERROR'}
    except Exception:return unavailable


def invoke(root_path,population,output,clearance_path):
    global _INVOCATION
    # Namespace, authority-file existence, and bootstrap bytes are cheap and read-only. Every
    # substantive reference/source/clearance admission happens after the durable fence.
    if population not in POPULATIONS:raise ValueError('Unknown execution population')
    root_path=Path(root_path).resolve();output=Path(output).absolute();clearance_path=Path(clearance_path).resolve()
    if output.resolve()!=output or output.is_relative_to(HERE.parents[3]) or not clearance_path.is_file():
        raise ValueError('Invalid output namespace or absent clearance')
    doc=bootstrap(root_path)
    forbidden=[Path('/Users/new/Developer/GitHub/designer'),*[Path(p) for p in doc['protectedRoots']]]
    if any(output.is_relative_to(p) for p in forbidden):raise ValueError('Historical/static input tree is not an output namespace')
    journal=source(HERE/'journal.py','w51_journal')
    identity={'root':sha(root_path),'population':doc['populations'][population]['manifest']['sha256'],
              'clearance':sha(clearance_path)}
    output.mkdir(parents=True,exist_ok=True)
    lock=output/'.invocation.lock'
    if lock.is_symlink():raise ValueError('Invocation lock is not an ordinary owned file')
    # This is a one-invocation process. On completion the kernel owns lock release at exit:
    # an explicit close after commit could fail, and closing before commit admits a racing
    # invocation between the final fault check and eligibility. Failure paths close normally.
    descriptor=os.open(lock,os.O_WRONLY|os.O_CREAT|os.O_APPEND,0o600)
    try:fcntl.flock(descriptor,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BaseException:
        os.close(descriptor)
        raise
    marker=Path(str(output/'contract.json')+'.phase/analysis.started.json')
    fence=None;log=None;ticket=None

    def stopped():
        completed=existing_completion(output,journal)
        if completed is not None:
            with contextlib.suppress(BaseException):os.close(descriptor)
            return completed
        # Diagnostics are best effort, never the authority for excluding partial publication.
        # Absence of terminal.json is enough even if every fault/log write fails.
        with contextlib.suppress(BaseException):
            if log is not None:
                with log.open('a') as stream:traceback.print_exc(file=stream)
        consumed=analysis_consumed(marker)
        if consumed:
            with contextlib.suppress(BaseException):
                journal.fail(output,'POST_MARKER_INSTRUMENT_FAULT',identity)
        elif fence is not None:
            with contextlib.suppress(BaseException):
                journal.write_once(Path(fence['path']+'.stop.json'),
                                   {'status':'OPERATIONAL_STOP','log':journal.pin(log)})
        with contextlib.suppress(BaseException):os.close(descriptor)
        return {'status':'NEITHER' if consumed else 'OPERATIONAL_STOP',
                'judgeCompleted':False,'analysisConsumed':consumed}

    try:
        fence=journal.fence(output,identity)
        log=output/'quarantine'/('invocation-'+Path(fence['path']).stem+'.log')
        log.parent.mkdir(parents=True,exist_ok=True)
        guard=source(HERE/'guard.py','w51_guard')
        if guard.environment()!=doc['closure']['environment']:raise ValueError('Interpreter/environment differs')
        guard.enforce(doc['repo'],doc['closure']['sources'])
        roots=source(HERE/'root.py','w51_root')
        prepared=roots.prepare(root_path,population,output)
        roots.clearance(doc,population,clearance_path)
        slot=bind_slot(root_path,population,output)
        _INVOCATION={'prepared':prepared,'fence':fence,'slot':journal.pin(slot)}
        guard.external_reads(doc['repo'],prepared['dataset']['externalInputs'],doc['protectedRoots'])
        if analysis_consumed(marker):
            result=journal.terminal(output)
            if result is None or not result['judgeCompleted']:
                raise ValueError('Interrupted or faulted analysis cannot resume')
        else:
            with log.open('x') as stream, private_stream(stream):
                with gpu_lease() as lease:
                    engine=Engine(prepared,roots,journal,lease)
                    engine.create_contract();union=engine.captures()
                    ticket=engine.analyze(union,identity)
                    policy_hashes=engine.policy_authority_hashes()
            result=ticket['result']
        public={'status':result['status'],'judgeCompleted':result['judgeCompleted'],
                'analysisConsumed':True,'publication':'COMMITTED'}
        # Both CLI outcomes are JSON-compatible before the commit. Formatting/writing the
        # eventual line is only a notification; consumers authenticate terminal.json.
        json.dumps(public,sort_keys=True)
        if ticket is not None:
            if (output/'fault.json').exists():raise ValueError('Faulted preparation cannot commit')
            journal.checked(fence);journal.checked(_INVOCATION['slot'])
            if any(sha(path)!=expected for path,expected in policy_hashes):
                raise ValueError('Changed landing policy before publication')
    except BaseException:
        return stopped()
    finally:
        _INVOCATION=None

    # No context manager or owned cleanup surrounds this boundary. Only the explicitly
    # classified durability flush and cosmetic CLI notification follow the successful link.
    if ticket is not None:
        try:publication=journal.commit(ticket)
        except BaseException:return stopped()  # Reconcile any existing commit before faulting.
        public['publication']=publication
    return public


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',required=True,type=Path)
    parser.add_argument('--population',required=True,choices=POPULATIONS)
    parser.add_argument('--output',required=True,type=Path,help='same output resumes only pre-marker work')
    parser.add_argument('--clearance',required=True,type=Path)
    args=parser.parse_args()
    try:result=invoke(args.root,args.population,args.output,args.clearance)
    except (ValueError,OSError,KeyError):
        # A read-only precondition can fail on a previously spent output too. In particular,
        # an unavailable disk must never turn a post-marker failure into a pre-fence refusal.
        result=existing_completion(args.output)
        if result is None:
            try:
                consumed=analysis_consumed(Path(str(args.output/'contract.json')+'.phase/analysis.started.json'))
                fenced=any((args.output/'fences').glob('*.json'))
            except OSError:consumed=True;fenced=True
            result={'status':'NEITHER' if consumed else
                    'OPERATIONAL_STOP' if fenced else 'REFUSED_BEFORE_FENCE',
                    'judgeCompleted':False,'analysisConsumed':consumed}
    try:
        print(json.dumps(result,sort_keys=True),flush=True)
    except (OSError,ValueError):
        # Publication already committed, if it happened at all. Notification is not a verdict
        # write, and its failure cannot create fault.json or authorize another analysis.
        with contextlib.suppress(OSError,ValueError):
            print('CLI notification failed; terminal.json remains authoritative.',file=sys.stderr,flush=True)
        return 1
    return 0 if result['judgeCompleted'] and result.get('publication')=='COMMITTED' else 1

if __name__=='__main__':raise SystemExit(main())
