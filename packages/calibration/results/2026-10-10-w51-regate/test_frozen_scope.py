"""The fixed canonical reader, projection and judge must agree on each position's operands.

Only independently generated synthetic statistics are routed. Real evidence is checked by its
pre-fit provenance chain, never by opening a gate capture or choosing a new numerical reference.
"""
import copy
import gzip
import json
from pathlib import Path
import runpy
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
R=runpy.run_path(str(HERE/'root.py'))

class FrozenScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root=R['load'](HERE/'execution-root.rehearsal4.json')
        cls.sources=R['source'](HERE/'phase_sources.py','w51_scope_sources')
        cls.judge=R['source'](HERE/'judge.py','w51_scope_judge')

    def reader(self, population='synthetic-rehearsal', change=None):
        root=copy.deepcopy(self.root);science=R['dataset'](root,population)
        config=R['load'](R['checked'](R['REPO'],science['measurementConfig']))
        if change:change(root,science,config)
        ctx={'repo':root['repo'],'output':'/Users/new/vitrea-w51/nonexecuting-test',
             'executionRoot':root['rootPath'],'inputs':science['inputs'],'phase':'gate'}
        live=types.SimpleNamespace(require_context=lambda c:self.assertIs(c,ctx),
            scientific_inputs=lambda c:science,sealed=lambda p:root,checked=R['checked'],load=R['load'])
        with patch.dict(sys.modules,{'w50_g1_dispatch':live}):
            backend=self.sources.PhaseSources(ctx,science,config)
        inventory=R['load'](R['checked'](R['REPO'],science['references']))
        return backend,science,inventory

    def projected(self,backend,science,original):
        q=self.sources.Q;names=q.statistic_names(original,{'family':'texture'})
        readings={};raw={};record=backend.canonical_record(original)
        for name in names:
            current,evidence=backend.current_measurement(original,name=name)
            candidate=copy.deepcopy(current)
            capture={'path':'/generated/candidate.png','sha256':'9'*64}
            ce=copy.deepcopy(evidence);ce['capture']=capture
            source=q.reading(candidate,current,ce,evidence,reported=False,eligible_empty=False)
            source['originalBudgetB']=original.get('B') if name==original['statistic'] else None
            source['evidence']['historical']=q.histories(original,science['references'],name)
            raw[name]=copy.deepcopy(source)
            if name==original['statistic']:
                full=name=='T1-full-silhouette'
                production={'estimator':'PRODUCTION_TS_INTERIOR_LEVEL' if full else 'CANONICAL_NUMPY_GAUSSIAN_LOW',
                    'producer':'packages/calibration/src/metrics/material.ts#interiorLevel' if full else
                        'packages/calibration/results/2026-10-08-w50-g1-fit/references/statistics.py#canonical_read',
                    'field':'material.interiorStdDevWeb' if full else 'web.statistics.T1-low',
                    'statistic':name,'reading':'first','capture':capture,'matrix':{'path':'/generated/matrix.json','sha256':'8'*64},
                    'scene':original['scene'],'units':'linear-luma','value':candidate['value']}
                source=q.frozen_primary(original,record['reference'],source,production,science['references'])
            readings[name]=source
        row=dict(original,originalReference=copy.deepcopy(original),reference=copy.deepcopy(record['reference']),
                 sceneSource='canonical',family='texture',readings=readings)
        return row,raw

    def test_actual_reader_projection_and_routing_cover_full_and_low_at_both_positions(self):
        backend,science,inventory=self.reader()
        for position in ('0.25','0.5'):
            for name in ('T1-full-silhouette','T1-low'):
                with self.subTest(position=position,statistic=name):
                    original=next(x for x in inventory['cells'] if x['profile'].endswith('glass'+position) and x['statistic']==name)
                    row,raw=self.projected(backend,science,original)
                    result=self.judge.R.route_row(row,inventory_sha256=science['references']['sha256'])
                    self.assertTrue(result['complete'])
                    if position=='0.5':
                        self.assertEqual(row['readings'][name],raw[name])
                        current,_=backend.current_measurement(original,name=name)
                        self.assertEqual(row['readings'][name]['current'],current['value'])
                        self.assertEqual(row['readings'][name]['B'],self.sources.Q.budget(current)[2])
                        self.assertTrue(all(x['comparison']['status']=='WITHIN' for x in result['checks']))
                    else:
                        self.assertEqual(row['readings'][name]['routingOperands'],'ORIGINAL_INVENTORY')
                        self.assertEqual(row['readings'][name]['current'],original['current'])
                        self.assertEqual(row['historical'],original['historical'])
                        del row['readings'][name]['routingOperands']
                        with self.assertRaisesRegex(ValueError,'original operands'):
                            self.judge.R.route_row(row,inventory_sha256=science['references']['sha256'])
        self.assertIs(self.judge.R,self.judge.T.R)
        self.assertIs(self.judge.N,self.judge.T.N)

    def test_real_current_or_budget_cannot_be_replaced_even_when_new_file_is_registered(self):
        # A new report may be well-formed and root-registered, but cannot become pre-fit evidence.
        synthetic=R['load'](HERE/'synthetic/generated/canonical-reference-evidence.json')
        for mutation in ('current','B','candidate-produced','post-fit'):
            with self.subTest(mutation=mutation),tempfile.TemporaryDirectory(dir=HERE) as temp:
                altered=copy.deepcopy(synthetic)
                for rows in altered['partitions'].values():
                    for row in rows:
                        for reading in row['readings'].values():
                            if mutation=='current':reading['current']=0.5
                            if mutation=='B':reading['repeat']['B']=0.5
                altered['origin']=mutation
                path=Path(temp)/'replacement.json';path.write_bytes(R['encoded'](altered));pin=R['pin'](path)
                def change(root,science,config):
                    config['canonicalReferenceEvidence']=pin
                    science['inputs'].append(pin);root['inputs'].append(pin)
                with self.assertRaisesRegex(ValueError,'pre-fit'):
                    self.reader('real-rehearsal',change)

    def test_relabelled_real_dataset_cannot_adopt_an_unsealed_synthetic_authority(self):
        with tempfile.TemporaryDirectory(dir=HERE) as temp:
            def change(root,science,config):
                science['dataOrigin']='synthetic'
                forged={'dataOrigin':'synthetic','files':[science['references'],config['canonicalReferenceEvidence']]}
                path=Path(temp)/'forged-fixture.json';path.write_bytes(R['encoded'](forged))
                root['syntheticFixture']=R['pin'](path);root['inputs'].append(root['syntheticFixture'])
            with self.assertRaisesRegex(ValueError,'sealed synthetic fixture'):
                self.reader('real-rehearsal',change)

    def test_newly_registered_fit_declaration_cannot_replace_the_charter_anchor(self):
        with tempfile.TemporaryDirectory(dir=HERE) as temp:
            def change(root,science,config):
                path=Path(temp)/'new-fit-declaration.json'
                path.write_bytes(R['checked'](R['REPO'],root['importedFit']).read_bytes())
                root['importedFit']=R['pin'](path);root['inputs'].append(root['importedFit'])
            with self.assertRaisesRegex(ValueError,'pre-fit'):
                self.reader('real-rehearsal',change)

    def test_original_real_canonical_pin_has_a_fit_bound_prefit_authority(self):
        # Source authentication is the claim; no numeric row from the real archive is routed.
        self.reader('real-rehearsal')

if __name__=='__main__':unittest.main()
