"""Append-only persistence beneath one genuine logical phase/output.

This is the dispatcher's internal journal, not an independent admission API. Only
source-admitted callbacks may supply payloads; public readers get metadata, never the
payload bodies. A stopped attempt is historical evidence, not permission to change a
candidate or retry scientific analysis.
"""
import copy
import hashlib
import json
import os
from pathlib import Path


def digest(raw):return hashlib.sha256(raw).hexdigest()
def sha(path):return digest(Path(path).read_bytes())
def read(path):return json.loads(Path(path).read_text())
def pin(path):return {'path':str(Path(path).resolve()),'sha256':sha(path)}
def checked(item):
    path=Path(item['path'])
    if not path.is_absolute() or path.resolve()!=path or not path.is_file() or sha(path)!=item['sha256']:
        raise ValueError('Changed journal artifact')
    return path

def write_once(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(value,sort_keys=True,allow_nan=False)+'\n').encode()
    with path.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
    return pin(path)


def members(batch):
    result=[]
    for index,run in enumerate(batch['runs']):
        for scene in run['scenes']:
            lanes=[('candidate',run['candidate'])]
            if batch['phase']=='exposure':lanes.append(('current',run['baselineCandidate']))
            for lane,candidate in lanes:
                identity=[run['profile'],run['renderer'],scene,lane,candidate['sha256']]
                key=digest(json.dumps(identity,separators=(',',':')).encode())
                result.append({'id':key,'identity':identity,'runIndex':index,'scene':scene,'lane':lane,'candidate':candidate})
    if len({m['id'] for m in result})!=len(result):raise ValueError('Duplicate logical member')
    return result


class Store:
    def __init__(self,contract,batch,output):
        self.contract=Path(contract).resolve();self.batch=copy.deepcopy(batch);self.output=Path(output).resolve()
        self.home=Path(str(self.contract)+'.phase');self.attempts=self.home/'attempts'
        self.analysis_marker=self.home/'analysis.started.json'
        self.population=members(batch)
    def _contracts(self):return sorted(self.attempts.glob('*/contract.json'))
    def _attempt_dir(self,a):
        p=self.attempts/f'{a["ordinal"]:06d}'
        if read(checked(pin(p/'contract.json')))!=a or a['logicalContract']!=pin(self.contract):
            raise ValueError('Attempt differs from immutable logical phase')
        if type(a['ordinal']) is not int or a['ordinal']<1:raise ValueError('Invalid attempt ordinal')
        previous=None
        if a['ordinal']>1:
            before=self.attempts/f'{a["ordinal"]-1:06d}'
            if not (before/'contract.json').is_file() or not (before/'failure.json').is_file():
                raise ValueError('Append-only attempt predecessor is missing')
            previous={'attempt':pin(before/'contract.json'),'failure':pin(before/'failure.json')}
            failure=read(before/'failure.json')
            if failure.get('attempt')!=previous['attempt'] or failure.get('claim')!=pin(before/'started.json'):
                raise ValueError('Predecessor is not the preserved stopped invocation')
            for artifact in failure['inventory']:checked(artifact)
        if a.get('predecessor')!=previous:raise ValueError('Attempt changed its actual predecessor')
        prior=[r for r in self.checkpoints() if int(Path(r['attempt']['path']).parent.name)<a['ordinal']]
        if a['retained']!=[r['checkpoint'] for r in prior]:raise ValueError('Attempt omitted or invented retained checkpoints')
        done={r['member']['id'] for r in prior}
        if a['members']!=[self._member(m,a['ordinal']) for m in self.population if m['id'] not in done]:
            raise ValueError('Attempt changed centrally derived remaining runs')
        return p
    def _member(self,member,n):
        run=copy.deepcopy(self.batch['runs'][member['runIndex']]);run['scenes']=[member['scene']]
        run['candidate']=member['candidate'];run.pop('baselineCandidate',None)
        base=self.output/'attempts'/f'{n:06d}'/'quarantine'/member['id']
        run['captureRoot']=str(base/'captures');run['matrixPath']=str(base/'matrix.json')
        return {**member,'run':run}
    def _claim(self,a):
        p=self._attempt_dir(a);claim=read(p/'started.json')
        if claim['attempt']!=pin(p/'contract.json') or claim['logicalContract']!=pin(self.contract):
            raise ValueError('Attempt claim changed')
        return p
    def checkpoints(self):
        result=[];seen=set()
        for contract in self._contracts():
            a=read(contract);folder=contract.parent
            if a.get('schema')!='w50-live-attempt-1' or a.get('logicalContract')!=pin(self.contract) or a.get('output')!=str(self.output) or a.get('ordinal')!=int(folder.name):
                raise ValueError('Checkpoint attempt changed logical phase identity')
            for p in sorted([*(folder/'members').glob('*.json'),*(folder/'recovered').glob('*.json')]):
                item=read(p)
                claim=read(folder/'started.json')
                if claim.get('logicalContract')!=pin(self.contract) or claim.get('attempt')!=pin(contract):
                    raise ValueError('Checkpoint claim changed logical phase identity')
                if item['attempt']!=pin(contract) or item['claim']!=pin(folder/'started.json'):
                    raise ValueError('Checkpoint lost actual attempt ownership')
                choices=[m for m in a['members'] if m['id']==item['member']['id']]
                fixed=[self._member(m,a['ordinal']) for m in self.population if m['id']==item['member']['id']]
                if choices!=[item['member']] or fixed!=[item['member']] or item['member']['id'] in seen:
                    raise ValueError('Checkpoint changes or repeats fixed member')
                if 'revalidationClaim' in item:
                    r=read(checked(item['revalidationClaim']))
                    if r.get('schema')!='w50-live-reconciliation-claim-1' or r.get('logicalContract')!=pin(self.contract) or r.get('failedAttempt')!=pin(contract) or r.get('failure')!=pin(folder/'failure.json'):
                        raise ValueError('Recovered checkpoint lost its actual revalidation authority')
                checked(item['payload'])
                for artifact in item['artifacts']:checked(artifact)
                seen.add(item['member']['id']);result.append({**item,'checkpoint':pin(p)})
        return result
    def plan(self):
        if self.analysis_marker.exists():raise ValueError('Scientific analysis already started; recovery forbidden')
        if (self.home/'native.started.json').exists() and not (self.home/'native.complete.json').exists():
            raise ValueError('Native subread started without complete checkpoint; no replay')
        if (self.home/'native.complete.json').exists():self.native_metadata()
        prior=self._contracts()
        predecessor=None
        if prior:
            last=prior[-1];failure=last.parent/'failure.json'
            if not failure.exists():raise ValueError('Previous capture attempt is not a preserved operational stop')
            fail=read(failure)
            if fail.get('attempt')!=pin(last) or fail.get('claim')!=pin(last.parent/'started.json'):
                raise ValueError('Failed attempt authority changed')
            for item in fail['inventory']:checked(item)
            predecessor={'attempt':pin(last),'failure':pin(failure)}
        retained=self.checkpoints();done={r['member']['id'] for r in retained}
        n=len(prior)+1;pending=[]
        for member in self.population:
            if member['id'] in done:continue
            pending.append(self._member(member,n))
        if not pending:raise ValueError('Capture population already complete; no new attempt')
        a={'schema':'w50-live-attempt-1','logicalContract':pin(self.contract),'ordinal':n,
            'output':str(self.output),'predecessor':predecessor,'retained':[r['checkpoint'] for r in retained],
            'members':pending}
        write_once(self.attempts/f'{n:06d}'/'contract.json',a)
        return a
    def start(self,a,lease):
        if self.analysis_marker.exists():raise ValueError('Analysis blocks capture restart')
        folder=self._attempt_dir(a)
        self.output.mkdir(parents=True,exist_ok=True)
        return write_once(folder/'started.json',{'attempt':pin(folder/'contract.json'),
            'logicalContract':pin(self.contract),'pid':os.getpid(),'gpuLease':lease,'output':str(self.output)})
    def checkpoint(self,a,member,payload,artifacts):
        folder=self._claim(a)
        if self.analysis_marker.exists() or (folder/'failure.json').exists() or (folder/'complete.json').exists():
            raise ValueError('Attempt no longer captures')
        if member not in a['members']:raise ValueError('Checkpoint is not a centrally derived member')
        target=folder/'members'/f'{member["id"]}.json'
        if target.exists():raise FileExistsError(str(target))
        for item in artifacts:checked(item)
        destination=self.output/'attempts'/f'{a["ordinal"]:06d}'/'quarantine'/member['id']/'record.json'
        payload_pin=write_once(destination,payload)
        return write_once(target,{'schema':'w50-live-member-checkpoint-1','member':member,
            'attempt':pin(folder/'contract.json'),'claim':pin(folder/'started.json'),
            'payload':payload_pin,'artifacts':artifacts})
    def adopt(self,a,member,payload,artifacts,revalidation):
        folder=self._claim(a)
        if self.analysis_marker.exists() or not (folder/'failure.json').exists() or member not in a['members']:
            raise ValueError('Only a preserved failed attempt member can be source-revalidated')
        if member['id'] in {r['member']['id'] for r in self.checkpoints()}:raise ValueError('Original member is already retained')
        r=read(checked(revalidation))
        if r.get('schema')!='w50-live-reconciliation-claim-1' or r.get('logicalContract')!=pin(self.contract) or r.get('failedAttempt')!=pin(folder/'contract.json') or r.get('failure')!=pin(folder/'failure.json'):
            raise ValueError('Reconciliation claim differs from original failed authority')
        for item in artifacts:checked(item)
        target=self.output/'quarantine/recovered'/str(a['ordinal'])/(member['id']+'.json')
        payload_pin=write_once(target,payload)
        return write_once(folder/'recovered'/(member['id']+'.json'),{'schema':'w50-live-member-checkpoint-1',
            'member':member,'attempt':pin(folder/'contract.json'),'claim':pin(folder/'started.json'),
            'payload':payload_pin,'artifacts':artifacts,'revalidationClaim':revalidation})
    def stop(self,a,code):
        if code not in {'INSTRUMENT_FAULT','CENSUS_REFUSED','LEASE_LOST'}:raise ValueError('Not an operational stop')
        folder=self._claim(a)
        if self.analysis_marker.exists():raise ValueError('Cannot recover scientific analysis')
        tree=self.output/'attempts'/f'{a["ordinal"]:06d}'
        inventory=[pin(p) for p in sorted(tree.rglob('*')) if p.is_file()]
        return write_once(folder/'failure.json',{'schema':'w50-live-attempt-failure-1','code':code,
            'attempt':pin(folder/'contract.json'),'claim':pin(folder/'started.json'),'inventory':inventory})
    def finish(self,a):
        folder=self._claim(a)
        found={c['member']['id'] for c in self.checkpoints() if c['attempt']==pin(folder/'contract.json')}
        if found!={m['id'] for m in a['members']}:raise ValueError('Attempt capture population incomplete')
        return write_once(folder/'complete.json',{'attempt':pin(folder/'contract.json'),'members':len(found)})
    def start_native(self,a):
        if self.batch['phase']!='exposure':raise ValueError('Native blind preparation is exposure-only')
        folder=self._claim(a)
        return write_once(self.home/'native.started.json',{'logicalContract':pin(self.contract),
            'attempt':pin(folder/'contract.json'),'claim':pin(folder/'started.json')})
    def complete_native(self,payload,artifacts=()):
        started=self.home/'native.started.json'
        if not started.exists() or payload.get('ready') is not True:raise ValueError('Native subread not completely ready')
        for item in artifacts:checked(item)
        payload_pin=write_once(self.output/'native-blind/quarantine/checkpoint.json',payload)
        return write_once(self.home/'native.complete.json',{'schema':'w50-live-native-checkpoint-1',
            'logicalContract':pin(self.contract),'started':pin(started),'payload':payload_pin,'artifacts':list(artifacts)})
    def native_metadata(self):
        p=self.home/'native.complete.json';m=read(p)
        if m['logicalContract']!=pin(self.contract) or m['started']!=pin(self.home/'native.started.json'):
            raise ValueError('Native checkpoint names another logical exposure')
        checked(m['payload'])
        for item in m['artifacts']:checked(item)
        return {**m,'checkpoint':pin(p)}
    def complete_union(self):
        rows=self.checkpoints();by_id={r['member']['id']:r for r in rows}
        if set(by_id)!={m['id'] for m in self.population}:raise ValueError('Full logical capture population is incomplete')
        if self.batch['phase']=='exposure':native=self.native_metadata()['checkpoint']
        else:native=None
        contracts=self._contracts()
        if not contracts or not (contracts[-1].parent/'complete.json').exists():raise ValueError('Final attempt has not completed')
        return {'schema':'w50-live-capture-union-1','logicalContract':pin(self.contract),
            'native':native,'members':[by_id[m['id']] for m in self.population]}
    def start_analysis(self,lease):
        union=self.complete_union()
        path=self.home/'captures.complete.json'
        if path.exists():
            if read(path)!=union:raise ValueError('Previously complete capture union changed')
        else:write_once(path,union)
        value={'schema':'w50-live-analysis-claim-1','logicalContract':pin(self.contract),'captures':pin(path),
            'pid':os.getpid(),'gpuLease':lease,'output':str(self.output)}
        write_once(self.analysis_marker,value)
        return value
    def status(self):
        done=len(self.checkpoints());attempts=self._contracts()
        return {'schema':'w50-live-public-status-1','phase':self.batch['phase'],'attempts':len(attempts),
            'retained':done,'remaining':len(self.population)-done,'analysisStarted':self.analysis_marker.exists(),
            'nativeComplete':(self.home/'native.complete.json').exists()}
