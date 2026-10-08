"""DL5f tests use synthetic bytes only; no real prior capture is opened."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('replacement',HERE/'replacement.py')
R=importlib.util.module_from_spec(spec);spec.loader.exec_module(R)


class Replacement(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.repo=Path(self.tmp.name)/'repo';self.repo.mkdir()
        self.old=self.repo/R.PRIOR
        self.old.mkdir(parents=True)
        self.directory=self.repo/R.CURRENT/'execution';self.directory.mkdir(parents=True)
        self.tree=Path(self.tmp.name)/'prior-pixels';self.tree.mkdir()
        self.scenes=[f'synthetic-{i:02d}' for i in range(42)]
        self.candidate=self.put('candidate.json',{'synthetic':'baseline'})
        self.run=dict(id='prior-gpu',profile='apple-macos-27.0-1x-dark-standard-glass0.25',
            renderer='webgpu',sceneSource='w50',scenes=self.scenes,sets=['calibration'],candidate=self.candidate,
            captureRoot=str(self.tree/'captures/prior-gpu'),matrixPath=str(self.tree/'prior-index.json'),
            fixtures={'synthetic':'same'},webSourceClosure={'path':'old-closure','sha256':'a'*64})
        batch=self.put(str(R.PRIOR/'inputs/batch.json'),{'schema':'w50-g1-batch-1','phase':'current',
            'cohort':[self.candidate],'runs':[self.run]})
        oldroot=self.put(str(R.PRIOR/'execution/current-instrument-root.json'),
            {'schema':'w50-g1-current-instrument-root-1','currentBatches':[batch],
             'partOne':{'sha256':'1'*64},'partTwo':{'sha256':'2'*64}})
        self.seal(self.repo/oldroot['path'])
        contract=self.put(str(R.PRIOR/'execution/current-instrument'/f'{batch["sha256"]}.json'),
            {'schema':'w50-g1-phase-contract-1','phase':'current','executionRootSha256':oldroot['sha256'],
             'batch':batch,'cohort':[self.candidate]})
        self.seal(self.repo/contract['path'])
        claim=self.put(contract['path']+'.started.json',{'contractSha256':contract['sha256'],
                       'batchSha256':batch['sha256'],'phase':'current','output':str(self.tree)})
        files=[]
        for i,scene in enumerate(self.scenes):
            path=self.tree/f'captures/prior-gpu/{scene}/{scene}__webgpu.png'
            path.parent.mkdir(parents=True);path.write_bytes(f'synthetic-png-{i}'.encode())
            files.append(dict(path=str(path.relative_to(self.tree)),sha256=R.sha(path),bytes=path.stat().st_size))
        self.failure=dict(schema='w50-current-attempt-failure-1',status='STOPPED_INCOMPLETE_NO_RETRY',
            candidateVerdict='NOT_READ',root=oldroot,contract=contract,claim=claim,tree=str(self.tree),files=files,
            reportCount=43,successfulBatchResult=False,exitCode=1)
        failure=self.put(str(R.PRIOR/'evidence/current-attempt1/failure.json'),self.failure)
        ruling=self.put_text('dl5f.txt',R.DL5F)
        self.replacement=dict(attempt=2,priorRoot=oldroot,priorClaim=claim,priorFailure=failure,ruling=ruling)
        self.batch={'schema':'w50-g1-batch-1','phase':'current','cohort':[self.candidate],
            'runs':[{**self.run,'id':'replacement-gpu','captureRoot':'/scratch/new-gpu','matrixPath':'/scratch/new.json',
                     'webSourceClosure':{'path':'new-closure','sha256':'b'*64}}]}
        self.output=Path(self.tmp.name)/'new-output';self.output.mkdir()

    def put_text(self,name,text):
        path=self.repo/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text)
        return {'path':name,'sha256':R.sha(path)}

    def put(self,name,data):return self.put_text(name,json.dumps(data)+'\n')

    def seal(self,path):Path(str(path)+'.sha256').write_text(f'{R.sha(path)}  {path.name}\n')

    def validate(self,decl=None,batch=None):
        return R.validate(self.repo,self.directory,decl or self.replacement,[batch or self.batch])

    def records(self,prior):
        rows=[]
        for i,item in enumerate(prior['priorGpu']):
            path=self.output/f'{i}.png';path.write_bytes(Path(item['png']['path']).read_bytes())
            rows.append({k:item[k] for k in ('profile','renderer','scene')}|{
                'candidate':self.candidate,'lane':'current','artifacts':{'png':{'path':str(path),'sha256':R.sha(path)}}})
        return rows

    def test_exact_declared_prior_membership_is_derived_not_caller_selected(self):
        prior=self.validate()
        self.assertEqual(len(prior['priorGpu']),42)
        self.assertEqual([p['scene'] for p in prior['priorGpu']],self.scenes)
        self.assertEqual(prior['attempt'],2)

    def test_other_attempt_or_prior_identity_or_ruling_is_refused(self):
        for field,value in [('attempt',3),('priorRoot',self.candidate),('priorClaim',self.candidate),
                            ('ruling',self.put_text('other-ruling.txt','permission to retry'))]:
            with self.subTest(field=field),self.assertRaises(ValueError):self.validate({**self.replacement,field:value})

    def test_exact_42_required_not_subset_superset_or_changed_first_run(self):
        for scenes in (self.scenes[:-1],self.scenes+['extra'],list(reversed(self.scenes))):
            batch=copy.deepcopy(self.batch);batch['runs'][0]['scenes']=scenes
            with self.assertRaises(ValueError):self.validate(batch=batch)
        batch=copy.deepcopy(self.batch);batch['runs'][0]['renderer']='css'
        with self.assertRaises(ValueError):self.validate(batch=batch)

    def test_missing_prior_png_and_changed_prior_hash_are_not_waived(self):
        self.failure['files'].pop();self.replacement['priorFailure']=self.put(
            str(R.PRIOR/'evidence/current-attempt1/failure.json'),self.failure)
        with self.assertRaises(ValueError):self.validate()

    def test_exact_gpu_bytes_pass_before_css_while_mismatch_and_false_receipt_fail(self):
        prior=self.validate();records=self.records(prior)
        compared=R.compare(prior,records,self.output)
        self.assertEqual(len(compared),42)
        path=Path(records[0]['artifacts']['png']['path']);path.write_bytes(b'wrong')
        records[0]['artifacts']['png']['sha256']=R.sha(path)
        with self.assertRaises(ValueError):R.compare(prior,records,self.output)

    def test_duplicate_missing_and_other_candidate_gpu_records_fail(self):
        prior=self.validate();records=self.records(prior)
        for bad in (records[:-1],records+[records[0]],list(reversed(records))):
            with self.assertRaises(ValueError):R.compare(prior,bad,self.output)
        records[0]['candidate']={'path':'different','sha256':'f'*64}
        with self.assertRaises(ValueError):R.compare(prior,records,self.output)


if __name__=='__main__':unittest.main()
