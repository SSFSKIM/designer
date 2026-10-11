"""Real-shape reference/role integration without a capture or candidate-phase reading.

The pair tests use independently generated arrays, not candidate gate PNGs. They exercise the
production repeat math and static admission, including the nonidentity path byte-equal tests miss.
"""
import copy
import json
from pathlib import Path
import runpy
import sys
import types
import unittest
import subprocess
import os
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
R=runpy.run_path(str(HERE/'root.py'))

class IntegratedInputs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc=R['load'](HERE/'execution-root.rehearsal4.json')
        cls.sources=R['source'](HERE/'phase_sources.py','w51_integrated_sources')
        cls.judge=R['source'](HERE/'judge.py','w51_integrated_judge')
        cls.prospective_closure=R['source'](HERE/'build.py','w51_integrated_discovery').discover()

    def case(self,population):
        science=R['dataset'](self.doc,population)
        ctx={'repo':self.doc['repo'],'output':'/Users/new/vitrea-w51/nonexecuting-test',
             'inputs':science['inputs'],'phase':'gate','executionRoot':self.doc['rootPath']}
        live=types.SimpleNamespace(require_context=lambda c:self.assertIs(c,ctx),
            scientific_inputs=lambda c:science,sealed=lambda p:self.doc,checked=R['checked'],load=R['load'])
        config=R['load'](R['checked'](R['REPO'],science['measurementConfig']))
        return science,ctx,live,config

    def test_both_literal_datasets_construct_actual_source_reader_and_target_contracts(self):
        for population in ('real-rehearsal','synthetic-rehearsal'):
            science,ctx,live,config=self.case(population)
            with patch.dict(sys.modules,{'w50_g1_dispatch':live}):
                backend=self.sources.PhaseSources(ctx,science,config)
                inventory=R['load'](R['checked'](R['REPO'],science['references']))
                gate={tuple(k) for k in science['phaseDependencies']['gateKeys']}
                for row in inventory['cells']:
                    if tuple(row[k] for k in R['KEY']) in gate and not row.get('nativeIdentity') and row['statistic']!='owner-contracts':
                        backend.canonical_record(row)
                judge=R['load'](R['checked'](R['REPO'],science['instruments']['judge']['config']))
                targets=R['load'](R['checked'](R['REPO'],judge['targets']))
                cut=R['load'](R['checked'](R['REPO'],targets['cut']))
                self.judge.preflight(inventory,science,cut,targets)

    def guarded_static_inputs(self, population, sources):
        # Root 4 supplies only immutable dataset fixtures, not present source authority. The
        # actual probe discovers current code; its guard stays installed for every later read.
        code="""from pathlib import Path
import json,runpy,sys
here=Path(sys.argv[1]);r=runpy.run_path(str(here/'root.py'))
doc=r['load'](here/'execution-root.rehearsal4.json')
sources=json.loads(sys.stdin.read())
g=runpy.run_path(str(here/'guard.py'));g['enforce'](r['REPO'],sources)
science=r['dataset'](doc,sys.argv[2])
g['external_reads'](r['REPO'],science['externalInputs'],doc['protectedRoots'])
# Historical source pins are not re-authorized: all executed Python is checked against the
# prospective closure above. Non-source fixture inputs retain their original content pins.
for item in science['inputs']:
    if Path(item['path']).suffix!='.py':r['checked'](r['REPO'],item)
r['source'](here/'semantics.py','w51_guarded_differential').verify()
print('ADMITTED_STATIC_AND_SOURCE')
"""
        return subprocess.run([sys.executable,'-I','-B','-c',code,str(HERE),population],
            input=json.dumps(sources),capture_output=True,text=True)

    def test_static_input_policy_composes_with_permanent_source_guard_on_each_dataset(self):
        for population in ('real-rehearsal','synthetic-rehearsal'):
            process=self.guarded_static_inputs(population,self.prospective_closure['sources'])
            self.assertEqual(process.returncode,0,process.stderr)
            self.assertEqual(process.stdout.strip(),'ADMITTED_STATIC_AND_SOURCE')

    def test_prospective_source_omission_is_refused_even_with_unchanged_static_fixtures(self):
        sources=dict(self.prospective_closure['sources'])
        relative=str((HERE/'root.py').relative_to(R['REPO']))
        sources.pop(relative)
        process=self.guarded_static_inputs('real-rehearsal',sources)
        self.assertNotEqual(process.returncode,0)
        self.assertIn('Changed or unsealed executed import: '+relative,process.stderr)
        self.assertNotIn('ADMITTED_STATIC_AND_SOURCE',process.stdout)

    def test_actual_node_guard_accepts_both_dataset_source_closures_without_a_renderer(self):
        seen=set()
        for pin in self.doc['batches'].values():
            for run in R['load'](R['checked'](R['REPO'],pin))['runs']:
                closure=run['webSourceClosure']
                if closure['sha256'] in seen:continue
                seen.add(closure['sha256'])
                env={**os.environ,'W50_WEB_ROOT':str(R['REPO']),
                     'W50_WEB_CLOSURE':str(R['checked'](R['REPO'],closure)),
                     'W50_WEB_CLOSURE_SHA256':closure['sha256']}
                process=subprocess.run(['node','--import',str(R['FIT']/'web/node-guard.mjs'),
                                        '--input-type=module','--eval',''],env=env,capture_output=True,text=True)
                self.assertEqual(process.returncode,0,process.stderr)
        self.assertGreaterEqual(len(seen),2)

    def test_every_population_keeps_original_candidate_numerical_admission(self):
        admission=R['source'](R['FIT']/'live-execution/admission.py','w51_test_numerical_admission')
        for name,pin in self.doc['batches'].items():
            batch=R['load'](R['checked'](R['REPO'],pin))
            self.assertEqual(admission.validate_numerical(self.doc,batch),self.doc['numerical'])
            changed=copy.deepcopy(batch);changed['cohort'][0]['sha256']='0'*64
            with self.assertRaises(ValueError):admission.validate_numerical(self.doc,changed)

    def test_differing_synthetic_repeat_executes_real_canonical_bands(self):
        science,ctx,live,_=self.case('synthetic-rehearsal')
        helper=R['source'](HERE/'repeat_sources.py','w51_test_repeat_canonical')
        config=R['load'](R['checked'](R['REPO'],science['repeatAdmission']['config']))
        canonical=R['load'](R['checked'](R['REPO'],config['canonical']))
        rows=R['load'](R['checked'](R['REPO'],science['references']))['cells']
        chosen=next(row for row in rows if row['statistic']=='T1-low' and row['profile'].endswith('glass0.5'))
        selected=[r for r in rows if all(r[k]==chosen[k] for k in R['KEY'][:3])]
        first=helper.M.np.full((400,640,3),60,dtype=helper.M.np.uint8)
        second=first.copy();second[0,0,0]+=1
        self.assertFalse(helper.M.np.array_equal(first,second))
        a,b=helper.canonical_pair(canonical,selected,first,second)
        self.assertEqual(set(a),{'T1-low','T1-fine'})
        differences=helper.C.compare_statistics(a,b)
        self.assertEqual(set(differences),set(a))

    def test_differing_newbed_repeat_uses_static_batch_not_historical_source_proofs(self):
        science,ctx,live,_=self.case('real-rehearsal')
        helper=R['source'](HERE/'repeat_sources.py','w51_test_repeat_newbed')
        config=R['load'](R['checked'](R['REPO'],science['repeatAdmission']['config']))
        rows=R['load'](R['checked'](R['REPO'],science['references']))['cells']
        selected=[r for r in rows if r.get('nativeIdentity') and r['profile']=='apple-macos-27.0-1x-dark-standard-glass0.25'
                  and r['renderer']=='webgpu' and r['scene']=='cell-grey-000-s044__rest']
        self.assertTrue(selected)
        first=helper.M.np.full((384,512,3),32,dtype=helper.M.np.uint8)
        second=first.copy();second[0,0,0]+=1
        # A corrupt historical instrument pin is not scientific input and is never opened.
        config['native']['instrument']={'path':'must-not-open-historical-root','sha256':'0'*64}
        with patch.dict(sys.modules,{'w50_g1_dispatch':live}):
            a,b=helper.newbed_pair(ctx,{'renderer':'webgpu'},config,selected,first,second)
        differences=helper.C.compare_statistics(a,b)
        self.assertTrue(differences)

if __name__=='__main__':unittest.main()
