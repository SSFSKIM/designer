"""Actual contract/result/filesystem checks with synthetic transport receipts."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('evidence',HERE/'evidence.py')
E=importlib.util.module_from_spec(spec);spec.loader.exec_module(E)
C=E.C

class Evidence(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory();self.addCleanup(t.cleanup);self.repo=Path(t.name).resolve()
        self.home=self.repo/'execution';self.home.mkdir();self.output=self.repo/'output';self.output.mkdir()
        self.candidate={'path':'candidate.json','sha256':'a'*64}
        self.run={'id':'one','profile':'apple-macos-27.0-1x-dark-standard-glass0.25','renderer':'css',
            'sceneSource':'canonical','candidate':self.candidate,'scenes':['one','two']}
        self.batch={'schema':'w50-g1-batch-1','phase':'current','cohort':[self.candidate],'runs':[self.run]}
        self.bp=self.put('batch.json',self.batch)
        self.root={'repo':str(self.repo),'currentBatches':[self.bp],'bootstrap':{},
            'repeatAdmission':{'config':self.put('repeat-config.json',{'schema':'w50-repeat-config-1'})}}
        self.rp=self.put('execution/current-instrument-root.json',self.root)
        root_path=self.repo/self.rp['path']
        Path(str(root_path)+'.sha256').write_text(f'{C.sha(root_path)}  {root_path.name}\n')
        self.contract=self.home/'current-instrument'/f'{self.bp["sha256"]}.json'
        C.write_sealed(self.contract,{'schema':'w50-g1-phase-contract-1','phase':'current','executionRootSha256':self.rp['sha256'],
            'batch':self.bp,'cohort':[self.candidate],'preFitEvidence':None})
        self.claim=Path(str(self.contract)+'.started.json')
        self.claim.write_text(json.dumps({'phase':'current','contractSha256':C.sha(self.contract),'batchSha256':self.bp['sha256'],
            'numericalAdmission':None,'output':str(self.output)}))
        rows=[]
        for scene in self.run['scenes']:
            artifacts={k:self.put(f'output/{scene}-{k}.json',v,absolute=True) for k,v in {
                'png':{},'cell':{'capturePath':'declarationSha256='+self.candidate['sha256'][:12]},
                'report':{'page':{'sceneId':scene,'requestedRenderer':'css','devicePixelRatio':1,
                    'candidateDocument':{'declarationSha256':self.candidate['sha256'][:12]}}}}.items()}
            pair=self.put(f'output/{scene}-pair.json',{'first':artifacts['png']},absolute=True)
            proof=self.put(f'output/{scene}-proof.json',{'manifest':pair,'pair':C.load(pair['path']),
                'originalArtifacts':artifacts,'config':self.root['repeatAdmission']['config']},absolute=True)
            rows.append({'profile':self.run['profile'],'renderer':'css','scene':scene,'sceneSource':'canonical','lane':'current',
                'candidate':self.candidate,'artifacts':artifacts,'repeatPair':pair,'repeatAdmission':proof,'origin':{'kind':'fresh-canonical-recovery'}})
        self.captures={'status':'CAPTURED','candidateSha256s':[self.candidate['sha256']],'captures':rows}
        A=C.source(C.PRIOR/'execution/admission.py','test_real_receipt_admission')
        self.result={'contractSha256':C.sha(self.contract),'claimSha256':C.sha(self.claim),
            'report':{'status':'CAPTURED','captures':self.captures},'captures':self.captures,
            'captureReceipt':A.validate_captures(self.batch,self.captures,self.output),
            'repeatReceipt':C.D.repeat_artifact_pins(self.repo,self.captures)}
        self.result_path=Path(str(self.contract)+'.result.json');C.write_sealed(self.result_path,self.result)
        self.result_pin=C.pin(self.repo,self.result_path)
    def put(self,name,value,absolute=False):
        p=self.repo/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(value))
        pin=C.pin(self.repo,p)
        if absolute:pin['path']=str(p)
        return pin
    def check(self):return E.completed_batch(self.repo,self.rp,self.root,self.bp,self.result_pin)
    def test_returns_actual_chain_and_both_original_members(self):
        got=self.check();self.assertEqual([m['receipt']['scene'] for m in got['members']],['one','two'])
        self.assertTrue(all(m['instrument']==self.rp for m in got['members']))
        self.assertTrue(all(m['output']==str(self.output) for m in got['members']))
        self.assertEqual(got['result'],{'pin':self.result_pin,'document':self.result})
    def test_rejects_partial_completed_population_even_if_result_resealed(self):
        self.result['captures']['captures'].pop()
        self.reseal()
        with self.assertRaises(ValueError):self.check()
    def test_rejects_result_from_another_contract(self):
        p=self.repo/'other.result.json';p.write_bytes(self.result_path.read_bytes())
        self.result_pin=C.pin(self.repo,p)
        with self.assertRaises(ValueError):self.check()
    def test_rejects_phase_analysis_in_capture_only_chain(self):
        self.result['report']['analysis']={'status':'partial'};self.reseal()
        with self.assertRaises(ValueError):self.check()
    def test_rejects_changed_second_pair_artifact(self):
        p=Path(self.captures['captures'][0]['repeatPair']['path']);p.write_text('{}')
        with self.assertRaises(ValueError):self.check()
    def test_missing_original_root_seal_is_not_archived_authority(self):
        Path(str(self.repo/self.rp['path'])+'.sha256').unlink()
        with self.assertRaises(ValueError):self.check()
    def reseal(self):
        self.result_path.write_text(json.dumps(self.result));Path(str(self.result_path)+'.sha256').write_text(f'{C.sha(self.result_path)}  {self.result_path.name}\n')
        self.result_pin=C.pin(self.repo,self.result_path)

if __name__=='__main__':unittest.main()
