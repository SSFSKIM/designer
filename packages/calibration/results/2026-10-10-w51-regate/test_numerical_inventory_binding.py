"""Captured synthetic page metadata must not redefine the frozen numerical argument domain.

These fixtures are report JSON only from the first synthetic-2 cell. They never enter a live
root or supply captures. The real canonical validators run; only the dispatcher capability is
provided by the unit test. Scientific arithmetic and required_arguments itself remain original.
"""
import copy
from pathlib import Path
import runpy
import sys
import types
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
R=runpy.run_path(str(HERE/'root.py'))
FIXTURE=HERE/'test-fixtures/synthetic-repeat-report'

class NumericalInventoryBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repeat=R['source'](HERE/'repeat.py','w51_numerical_binding_repeat')
        cls.common=R['source'](HERE/'role_common.py','w51_numerical_binding_common')
        cls.transports={name:R['source'](HERE/path,'w51_numerical_binding_'+name)
                        for name,path in (('canonical','canonical/adapter.py'),('w50','web/adapter.py'))}
        cls.base=R['load'](HERE/'execution-root.rehearsal2.json')

    def setUp(self):
        self.root=copy.deepcopy(self.base)
        self.science=R['dataset'](self.root,'synthetic-rehearsal')
        self.numeric_pin=R['load'](R['checked'](R['REPO'],self.root['numerical']))['referenceInventory']
        self.original=R['load'](R['checked'](R['REPO'],self.numeric_pin))
        self.inventory=R['load'](R['checked'](R['REPO'],self.science['references']))
        # This is the prospective binding, explicit on root and dataset, never an alias for
        # the synthetic statistic inventory. Before the repair the live reader ignores it.
        self.root['numericalInventory']=self.numeric_pin
        self.science['numericalInventory']=self.numeric_pin
        for inputs in (self.root['inputs'],self.science['inputs']):
            if self.numeric_pin not in inputs:inputs.append(self.numeric_pin)
        member=R['load'](FIXTURE/'member.json');self.run=member['run']
        self.record={k:self.run[k] for k in ('profile','renderer','candidate','sceneSource')}
        self.record.update(scene=member['scene'],lane=member['lane'])
        self.retained={'envelope':R['load'](FIXTURE/'envelope.json'),
                       'pages':[R['load'](FIXTURE/'first.json'),R['load'](FIXTURE/'second.json')]}
        self.context={'repo':str(R['REPO']),'phase':'gate','executionRoot':'unit-test-root',
                      'inputs':self.science['inputs']}
        def require_context(context):self.assertIs(context,self.context)
        def require_render(context,run,current=False):
            require_context(context);self.assertEqual(run,self.run);self.assertFalse(current)
        self.live=types.SimpleNamespace(require_context=require_context,require_render_admission=require_render,
            sealed=lambda path:self.root,scientific_inputs=lambda context:self.science,
            load=R['load'],checked=R['checked'])
        self.addCleanup(patch.stopall)
        patch.dict(sys.modules,{'w50_g1_dispatch':self.live}).start()

    def test_actual_synthetic_pages_pass_live_and_retained_canonical_validation(self):
        validators={
            'live':lambda:self.repeat.validate_reports(self.context,self.run,self.record,self.retained,self.inventory),
            'retained':lambda:self.common.validate_pages(self.context,self.repeat,self.transports,self.run,self.record,
                                                        self.retained,self.inventory)}
        for name,validate in validators.items():
            with self.subTest(path=name):validate()

    def test_numeric_domain_stays_real_nonempty_and_synthetic_identities_stay_disjoint(self):
        selector=self.repeat.S.M.N.required_arguments
        with self.assertRaisesRegex(ValueError,'population is empty'):selector(self.inventory)
        bound=self.repeat.S.STATIC.numerical_inventory(self.context)
        required=selector(bound)
        self.assertTrue(required)
        self.assertEqual(required,selector(self.original))
        synthetic={'|'.join(row[k] for k in ('profile','renderer','scene')) for row in self.inventory['cells']}
        self.assertTrue(synthetic.isdisjoint(required))
        self.science=R['dataset'](self.root,'real-rehearsal')
        self.science['numericalInventory']=self.numeric_pin
        if self.numeric_pin not in self.science['inputs']:self.science['inputs'].append(self.numeric_pin)
        self.context['inputs']=self.science['inputs']
        self.assertEqual(selector(self.repeat.S.STATIC.numerical_inventory(self.context)),required)

    def test_bad_page_is_still_rejected_on_both_paths(self):
        self.retained['pages'][1]['requestedRenderer']='css'
        for validate in (
            lambda:self.repeat.validate_reports(self.context,self.run,self.record,self.retained,self.inventory),
            lambda:self.common.validate_pages(self.context,self.repeat,self.transports,self.run,self.record,
                                               self.retained,self.inventory)):
            with self.assertRaisesRegex(ValueError,'capture identity'):validate()

    def test_dataset_cannot_replace_the_imported_numerical_reference(self):
        self.root['numericalInventory']=self.science['references']
        self.science['numericalInventory']=self.science['references']
        with self.assertRaises(ValueError):self.repeat.S.STATIC.numerical_inventory(self.context)

if __name__=='__main__':unittest.main()
