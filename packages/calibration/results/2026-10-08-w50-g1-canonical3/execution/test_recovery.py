"""Synthetic DL5k population/failure checks; never reads captured optical evidence."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('canonical_recovery',HERE/'recovery.py')
R=importlib.util.module_from_spec(spec);spec.loader.exec_module(R)

class Recovery(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.repo=Path(self.temp.name).resolve();self.tree=self.repo/'output';self.tree.mkdir()
        self.batch={'schema':'w50-g1-batch-1','phase':'current','cohort':[{'path':'candidate','sha256':'a'*64}],
            'runs':[{'id':'canonical','profile':R.FAILED[0],'renderer':'css','sceneSource':'canonical',
                'candidate':{'path':'candidate','sha256':'a'*64},'sets':['calibration'],
                'scenes':[R.FAILED[2]]+[f'scene-{i}' for i in range(126)],
                'captureRoot':'/old/captures','matrixPath':'/old/matrix.json','webSourceClosure':{'path':'old','sha256':'b'*64}}]}
    def put(self,name,value):
        path=self.repo/name;path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(value)+'\n');return {'path':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
    def test_original_127_is_only_population_even_when_old_tree_has_raw_cell(self):
        new=copy.deepcopy(self.batch);new['runs'][0]['captureRoot']='/fresh/captures'
        new['runs'][0]['matrixPath']='/fresh/matrix.json'
        self.assertEqual(len(R.fixed_batch(self.batch,new)),127)
        for mutate in (lambda b:b['runs'][0]['scenes'].pop(),lambda b:b['runs'][0]['scenes'].reverse(),
                       lambda b:b['runs'][0].update(candidate={'path':'other','sha256':'c'*64}),
                       lambda b:b['runs'][0].update(sceneSource='w50')):
            bad=copy.deepcopy(new);mutate(bad)
            with self.assertRaises(ValueError):R.fixed_batch(self.batch,bad)
    def test_original_population_must_itself_be_canonical_and_127(self):
        bad=copy.deepcopy(self.batch);bad['runs'][0]['scenes'].pop()
        with self.assertRaises(ValueError):R.fixed_batch(bad,bad)
    def failure(self):
        census=self.put('output/census.json',{'passes':False,'refusals':['captureProcessPresent']})
        raw=self.put('output/raw-row.json',{'transportOnly':True})
        files=[{'path':Path(p['path']).relative_to(self.tree).as_posix(),'size':Path(p['path']).stat().st_size,'sha256':p['sha256']} for p in (census,raw)]
        return {'schema':'w50-current-attempt-failure-1','status':'STOPPED_INCOMPLETE_NO_RETRY','candidateVerdict':'NOT_READ',
            'tree':str(self.tree),'fileCount':len(files),'reportCount':1,'retainedPairCount':1,'repeatAdmissionCount':0,
            'validatedDrawCount':0,'successfulBatchResult':False,'files':files,
            'failure':{'kind':'CLASSIFYING_CENSUS_REFUSAL','profile':R.FAILED[0],'renderer':R.FAILED[1],
                'scene':R.FAILED[2],'census':census,'refusals':['captureProcessPresent']}}
    def test_failure_keeps_raw_transport_but_no_validated_member(self):
        failure=self.failure();self.assertEqual(len(R.failed_inventory(self.repo,failure)),2)
        for key in ('repeatAdmissionCount','validatedDrawCount'):
            bad=copy.deepcopy(failure);bad[key]=1
            with self.assertRaises(ValueError):R.failed_inventory(self.repo,bad)
    def test_failure_cannot_substitute_an_unrelated_census_refusal(self):
        failure=self.failure()
        p=Path(failure['failure']['census']['path']);p.write_text('{"passes":false,"refusals":["anotherReason"]}')
        h=hashlib.sha256(p.read_bytes()).hexdigest();failure['failure']['census']['sha256']=h
        for item in failure['files']:
            if item['path']=='census.json':item.update(sha256=h,size=p.stat().st_size)
        with self.assertRaises(ValueError):R.failed_inventory(self.repo,failure)
    def test_failed_log_repository_pin_is_not_interpreted_against_working_directory(self):
        pin=self.put('preserved/dispatcher.log',{'failure':'census'})
        pin['path']='preserved/dispatcher.log'
        self.assertEqual(R.failed_log(self.repo,{'log':pin}),pin)
        (self.repo/pin['path']).write_text('changed')
        with self.assertRaises(ValueError):R.failed_log(self.repo,{'log':pin})
    def test_failure_rejects_unlisted_or_changed_file_and_completed_run(self):
        failure=self.failure();p=self.tree/'extra';p.write_text('changed')
        with self.assertRaises(ValueError):R.failed_inventory(self.repo,failure)
        p.unlink();(self.tree/'raw-row.json').write_text('changed')
        with self.assertRaises(ValueError):R.failed_inventory(self.repo,failure)
    def test_failure_rejects_hidden_admission_or_completion_even_if_manifest_lists_it(self):
        for name in ('repeat-admission__css.json','complete.json'):
            failure=self.failure();p=self.tree/name;p.write_text('{}')
            failure['files'].append({'path':name,'size':2,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()});failure['fileCount']+=1
            with self.assertRaises(ValueError):R.failed_inventory(self.repo,failure)
            p.unlink()

if __name__=='__main__':unittest.main()
