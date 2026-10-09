"""Synthetic DL5h partition fixtures: no real capture or measured report is read."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('recovery',HERE/'recovery.py')
R=importlib.util.module_from_spec(spec);spec.loader.exec_module(R)


class RecoveryPartition(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.repo=Path(self.tmp.name)/'repo';self.repo.mkdir()
        self.directory=self.repo/R.CURRENT/'execution';self.directory.mkdir(parents=True)
        self.tree=Path(self.tmp.name)/'attempt2';self.tree.mkdir()
        self.candidate=self.put('candidate.json',{'synthetic':'current'});self.cohort=[self.candidate]
        self.runs=[]
        for i in range(16):
            profile=f'apple-macos-27.0-{1 if i<8 else 2}x-dark-standard-glass0.25'
            scenes=[f'synthetic-{i}-{j}' for j in range(42)]
            if i==11:scenes[39]=R.FAILED[2]
            self.runs.append(dict(id=f'run-{i}',profile=profile,renderer='css' if i%2 else 'webgpu',
                sceneSource='w50',scenes=scenes,sets=['calibration'],candidate=self.candidate,fixtures={'fixed':True},
                captureRoot=str(self.tree/f'captures/run-{i}'),matrixPath=str(self.tree/f'indexes/run-{i}.json'),
                webSourceClosure={'path':'source.json','sha256':'a'*64}))
        self.runs[11]['profile']=R.FAILED[0];self.runs[11]['renderer']=R.FAILED[1]
        self.canonical=[dict(self.runs[0],id='canonical',sceneSource='canonical',scenes=[f'canonical-{i}' for i in range(127)],
            captureRoot=str(self.tree/'canonical'),matrixPath=str(self.tree/'canonical.json'))]
        oldbatches=[]
        for name,runs in [('newbed',self.runs),('canonical',self.canonical)]:
            oldbatches.append(self.put(str(R.PRIOR/f'inputs/{name}.json'),
                {'schema':'w50-g1-batch-1','phase':'current','cohort':self.cohort,'runs':runs}))
        old_adapter=self.put_text(str(R.PRIOR/'web/adapter.py'),"def source_probe():return {'status':'SOURCE_ONLY'}\n")
        self.oldroot=self.put(str(R.PRIOR/'execution/current-instrument-root.json'),
            {'schema':'w50-g1-current-instrument-root-1','currentBatches':oldbatches,
             'closure':{'sources':{old_adapter['path']:old_adapter['sha256']}},
             'newBedHost':{'path':'host','sha256':'b'*64}})
        self.seal(self.repo/self.oldroot['path'])
        contract=self.put(str(R.PRIOR/'execution/current-instrument'/f'{oldbatches[0]["sha256"]}.json'),
            {'phase':'current','batch':oldbatches[0],'executionRootSha256':self.oldroot['sha256'],'cohort':self.cohort})
        self.seal(self.repo/contract['path'])
        claim=self.put(contract['path']+'.started.json',{'phase':'current','contractSha256':contract['sha256'],
            'batchSha256':oldbatches[0]['sha256'],'output':str(self.tree)})
        files=[];proof_cells=[]
        for index,(run,scene) in enumerate([(r,s) for r in self.runs for s in r['scenes']][:502]):
            folder=Path(run['captureRoot'])/scene;folder.mkdir(parents=True)
            for name,raw in [(f'{scene}__{run["renderer"]}.png',b'synthetic-png'),
                             (f'report__{run["renderer"]}.json',b'{"synthetic":"report"}'),
                             (f'cell__{run["renderer"]}.json',json.dumps({'renderer':run['renderer'],
                              'deterministic':index<501,'repeatNoise':0 if index<501 else .000001}).encode())]:
                path=folder/name;path.write_bytes(raw)
                files.append({'path':str(path.relative_to(self.tree)),'sha256':R.sha(path),'bytes':len(raw)})
            if index<42:
                png=folder/f'{scene}__webgpu.png'
                proof_cells.append(dict(profile=run['profile'],renderer='webgpu',scene=scene,
                    replacementPng={'path':str(png),'sha256':R.sha(png)},priorPng={'path':'prior','sha256':R.sha(png)}))
        self.proof=self.put(str(R.PRIOR/'execution/gpu-replay-proof.json'),
            {'schema':'w50-current2-gpu-replay-proof-1','status':'BYTE_IDENTICAL',
             'executionRootSha256':self.oldroot['sha256'],'contractSha256':contract['sha256'],
             'claimSha256':claim['sha256'],'cells':proof_cells})
        self.seal(self.repo/self.proof['path'])
        self.failure=dict(schema='w50-current-attempt-failure-1',status='STOPPED_INCOMPLETE_NO_RETRY',
            candidateVerdict='NOT_READ',root=self.oldroot,contract=contract,claim=claim,tree=str(self.tree),
            files=files,reportCount=502,successfulBatchResult=False,
            failure=dict(profile=R.FAILED[0],renderer=R.FAILED[1],scene=R.FAILED[2]))
        failure=self.put(str(R.PRIOR/'evidence/current-attempt2/failure.json'),self.failure)
        ruling=self.put_text('dl5h.txt',R.DL5H)
        self.authority=dict(attempt=3,priorRoot=self.oldroot,priorClaim=claim,priorFailure=failure,
                            ruling=ruling,gpuReplayProof=self.proof)
        self.batches=[]
        for runs in (self.runs,self.canonical):
            new=[]
            for r in runs:
                new.append({**r,'captureRoot':'/fresh/'+r['id'],'matrixPath':'/fresh/'+r['id']+'.json',
                            'webSourceClosure':{'path':'new-source.json','sha256':'c'*64}})
            self.batches.append(dict(schema='w50-g1-batch-1',phase='current',cohort=self.cohort,runs=new))

    def put_text(self,name,text):
        path=self.repo/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
        return {'path':name,'sha256':R.sha(path)}
    def put(self,name,value):return self.put_text(name,json.dumps(value)+'\n')
    def seal(self,path):Path(str(path)+'.sha256').write_text(f'{R.sha(path)}  {path.name}\n')
    def validate(self):return R.derive(self.repo,self.directory,self.authority,self.batches)

    def test_exact501_are_retained_and_only171_plus127_are_fresh(self):
        result=self.validate()
        self.assertEqual(len(result['retained']),501)
        self.assertEqual(len(result['fresh']),298)
        self.assertEqual(sum(c['sceneSource']=='w50' for c in result['fresh']),171)
        self.assertEqual(sum(c['sceneSource']=='canonical' for c in result['fresh']),127)
        self.assertEqual(tuple(result['fresh'][0][k] for k in ('profile','renderer','scene')),R.FAILED)
        self.assertEqual(result['retained'][-1]['scene'],self.runs[11]['scenes'][38])

    def test_caller_cannot_change_skip_reorder_or_rerender_members(self):
        original=copy.deepcopy(self.batches)
        for change in ('drop','swap','candidate'):
            self.batches=copy.deepcopy(original)
            if change=='drop':self.batches[0]['runs'][0]['scenes'].pop()
            if change=='swap':self.batches[0]['runs'][0]['scenes'].reverse()
            if change=='candidate':self.batches[0]['runs'][0]['candidate']={'path':'different','sha256':'d'*64}
            with self.subTest(change=change),self.assertRaises(ValueError):self.validate()

    def test_retained_member_needs_original_true_zero_attestation(self):
        item=next(f for f in self.failure['files'] if f['path'].endswith('cell__webgpu.json'))
        path=self.tree/item['path'];path.write_text(json.dumps({'renderer':'webgpu','deterministic':False,'repeatNoise':0}))
        item.update(sha256=R.sha(path),bytes=path.stat().st_size)
        self.authority['priorFailure']=self.put(str(R.PRIOR/'evidence/current-attempt2/failure.json'),self.failure)
        with self.assertRaises(ValueError):self.validate()

    def test_failed502_cannot_be_retained_and_missing_witness_cannot_be_blessed(self):
        self.failure['files']=[p for p in self.failure['files'] if not p['path'].endswith('synthetic-0-0__webgpu.png')]
        self.authority['priorFailure']=self.put(str(R.PRIOR/'evidence/current-attempt2/failure.json'),self.failure)
        with self.assertRaises(ValueError):self.validate()

    def test_changed_original_validator_cannot_be_resealed_as_recovery_authority(self):
        old=self.repo/R.PRIOR/'web/adapter.py';old.write_text('# changed original validation semantics')
        with self.assertRaises(ValueError):self.validate()

    def test_attempt4_or_different_ruling_is_not_a_generic_retry(self):
        self.authority['attempt']=4
        with self.assertRaises(ValueError):self.validate()
        self.authority['attempt']=3;self.authority['ruling']=self.put_text('wrong.txt','retry anything')
        with self.assertRaises(ValueError):self.validate()


if __name__=='__main__':unittest.main()
