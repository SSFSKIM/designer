"""A scientific PASS alone never authorizes the gate: both completed pipelines and review do."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE=Path(__file__).resolve().parent

def source(name):
    spec=importlib.util.spec_from_file_location('w51_clearance_test_'+name,HERE/(name+'.py'))
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

class ClearanceTests(unittest.TestCase):
    def setUp(self):
        self.r,self.j=source('root'),source('journal')
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.home=Path(self.temp.name).resolve()
        self.root=self.home/'root.json';self.root.write_text('{}')
        self.doc={'rootPath':str(self.root),'closure':{},'populations':{
            name:{'manifest':{'path':str(self.home/(name+'.json')),'sha256':str(i)*64},'dataset':name}
            for i,name in enumerate(('gate','real-rehearsal','synthetic-rehearsal'),1)},
            'datasets':{'real-rehearsal':{'path':'real','sha256':'a'*64},
                        'synthetic-rehearsal':{'path':'synthetic','sha256':'b'*64}}}
        review=self.j.write_once(self.home/'review.json',{'kind':'reviewer-high','status':'APPROVE','rootSha256':self.r.sha(self.root)})
        self.value={'rootSha256':self.r.sha(self.root),'sourceClosureSha256':self.r.digest({}),
            'populationSha256':'1'*64,'purpose':'gate','reviewEvidence':[review]}
        self.path=self.home/'clearance.json'
    def check(self):
        self.path.write_text(json.dumps(self.value));return self.r.clearance(self.doc,'gate',self.path)
    def test_rehearsal_clearance_cannot_authorize_gate_and_both_rehearsals_are_required(self):
        with self.assertRaisesRegex(ValueError,'both completed'):self.check()
        self.value['purpose']='real-rehearsal'
        with self.assertRaisesRegex(ValueError,'clearance'):self.check()
    def rehearsals(self, real_status='PASS_EXPOSED_OWNER_PENDING'):
        self.value['rehearsals']={};tickets=[]
        for name,status in (('real-rehearsal',real_status),
                            ('synthetic-rehearsal','NEITHER')):
            output=self.home/name
            population=self.j.write_once(self.home/(name+'.json'),
                {'physicalCells':[['toy-profile','webgpu','toy-scene']],
                 'physicalCount':1,'statisticCount':1})
            self.doc['populations'][name]['manifest']=population
            contract=self.j.write_once(output/'contract.json',
                                      {'executionRootSha256':self.r.sha(self.root)})
            payload=self.j.write_once(output/'toy-payload.json',{'metadataOnly':True})
            union=self.j.write_once(output/'toy-union.json',{'logicalContract':contract,
                'members':[{'member':{'run':{'profile':'toy-profile','renderer':'webgpu'},
                                     'scene':'toy-scene'},'payload':payload,'artifacts':[]}]})
            marker=self.j.write_once(Path(str(output/'contract.json')+'.phase/analysis.started.json'),
                                      {'logicalContract':contract,'captures':union})
            witness={'status':'COMPLETE','sourceClosureSha256':self.r.digest({}),
                'executionRoot':self.j.pin(self.root),'population':population,
                'dataset':self.doc['datasets'][name],'analysisClaim':marker,'captureUnion':union,
                'physicalCount':1,'statisticCount':1,'branches':{'producerCarry':True,
                    'textBands':[{'producer':'CANONICAL_NUMPY_GAUSSIAN_LOW'}]}}
            identity={'root':self.r.sha(self.root),'population':population['sha256']}
            tickets.append(self.j.prepare(output,{'status':status},witness,identity))
            self.value['rehearsals'][name]=self.j.pin(output/'result.json')
        return tickets

    def test_preparation_never_clears_gate_and_synthetic_neither_is_allowed(self):
        tickets = self.rehearsals()
        # Complete report/result/prepared-terminal files are not pipeline completion. This
        # remains true if the process dies before it can write any fault record.
        with self.assertRaisesRegex(ValueError,'completion'):self.check()
        for ticket in tickets:self.j.commit(ticket)
        self.assertEqual(self.check(),self.value)
        # A lost final directory entry after crash is fail-closed, not permission to reseal.
        (self.home/'real-rehearsal'/'terminal.json').unlink()
        with self.assertRaisesRegex(ValueError,'completion'):self.check()

    def test_real_scientific_neither_cannot_clear_the_amended_gate(self):
        for ticket in self.rehearsals(real_status='NEITHER'): self.j.commit(ticket)
        with self.assertRaisesRegex(ValueError, 'real rehearsal.*PASS'):
            self.check()

    def test_old_review_cannot_authorize_a_new_policy_root(self):
        self.root.write_text('{"newLandingPolicy":"changed"}')
        with self.assertRaisesRegex(ValueError, 'clearance'): self.check()

    def test_new_root_review_cannot_reuse_old_completed_rehearsals(self):
        for ticket in self.rehearsals(): self.j.commit(ticket)
        self.root.write_text('{"landingPolicy":"prospective-DL5"}')
        self.value['rootSha256'] = self.r.sha(self.root)
        self.value['reviewEvidence'] = [self.j.write_once(self.home/'new-review.json',
            {'kind':'reviewer-high', 'status':'APPROVE', 'rootSha256':self.r.sha(self.root)})]
        with self.assertRaisesRegex(ValueError, 'completion.*exact root'): self.check()

    def test_a_fabricated_complete_report_without_analysis_marker_is_not_a_rehearsal(self):
        self.value['rehearsals']={}
        for name in ('real-rehearsal','synthetic-rehearsal'):
            output=self.home/name
            witness={'status':'COMPLETE','sourceClosureSha256':self.r.digest({}),
                'executionRoot':self.j.pin(self.root),'population':self.doc['populations'][name]['manifest'],
                'dataset':self.doc['datasets'][name],
                'analysisClaim':{'path':str(output/'nonexistent-marker'),'sha256':'0'*64}}
            identity={'root':self.r.sha(self.root),'population':self.doc['populations'][name]['manifest']['sha256']}
            self.j.commit(self.j.prepare(output,{'status':'PASS_EXPOSED_OWNER_PENDING'},witness,identity))
            self.value['rehearsals'][name]=self.j.pin(output/'result.json')
        with self.assertRaisesRegex(ValueError,'terminal artifact'):self.check()
        self.j.fail(self.home/'real-rehearsal','LATER_INVOCATION_FAULT',{})
        self.assertFalse((self.home/'real-rehearsal'/'fault.json').exists())
        with self.assertRaisesRegex(ValueError,'terminal artifact'):self.check()

if __name__=='__main__':unittest.main()
