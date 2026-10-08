"""The composition is two actual chains, never a fabricated single-root result."""
import copy
import importlib.util
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('composition',HERE/'composition.py')
M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)

class Composition(unittest.TestCase):
    def setUp(self):
        self.old={'path':'old-root','sha256':'a'*64};self.new={'path':'new-root','sha256':'b'*64}
        self.batches=[{'path':'newbed','sha256':'c'*64},{'path':'canonical','sha256':'d'*64}]
        self.results=[{'path':'old-result','sha256':'e'*64},{'path':'new-result','sha256':'f'*64}]
        self.contracts=[{'path':'old-contract','sha256':'1'*64},{'path':'new-contract','sha256':'2'*64}]
        self.original={'currentBatches':self.batches,'baselineDocuments':[{'path':'candidate','sha256':'3'*64}],
            'repeatAdmission':{'entrypoint':{'path':'repeat','sha256':'4'*64},'config':{'path':'config','sha256':'5'*64}},
            'newBedHost':{'path':'host','sha256':'6'*64}}
        self.recovery={**self.original,'currentBatches':[{'path':'fresh-canonical','sha256':'7'*64}],
            'recoveryAuthority':{'priorRoot':self.old,'completedNewbed':self.results[0]},
            'recovery':{'originalBatch':self.batches[1]}}
        self.doc={'schema':'w50-completed-current-composition-1','originalInstrument':self.old,'chains':[
            {'instrument':self.old,'batch':self.batches[0],'contract':self.contracts[0],'result':self.results[0]},
            {'instrument':self.new,'batch':self.recovery['currentBatches'][0],'contract':self.contracts[1],'result':self.results[1]}]}
    def test_exact_actual_chain_order_is_required(self):
        M.validate_manifest(self.doc,self.original,self.recovery)
        for change in (lambda d:d['chains'].reverse(),lambda d:d['chains'][0].update(instrument=self.new),
                       lambda d:d['chains'][0].update(result=self.results[1]),lambda d:d['chains'].pop()):
            bad=copy.deepcopy(self.doc);change(bad)
            with self.assertRaises(ValueError):M.validate_manifest(bad,self.original,self.recovery)
    def test_different_policy_or_candidate_cannot_be_composed(self):
        for field in ('baselineDocuments','repeatAdmission','newBedHost'):
            bad=copy.deepcopy(self.recovery);bad[field]=None
            with self.assertRaises(ValueError):M.validate_manifest(self.doc,self.original,bad)
    def test_original_canonical_batch_cannot_be_replaced_by_an_arbitrary_batch(self):
        bad=copy.deepcopy(self.recovery);bad['recovery']['originalBatch']=self.batches[0]
        with self.assertRaises(ValueError):M.validate_manifest(self.doc,self.original,bad)

if __name__=='__main__':unittest.main()
