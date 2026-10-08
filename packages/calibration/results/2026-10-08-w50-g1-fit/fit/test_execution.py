"""Synthetic root-bound entry tests: no real execution root/native values/solver is used."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('w50_fit_execution',HERE/'execution.py')
E=importlib.util.module_from_spec(spec);spec.loader.exec_module(E)


class ExecutionBoundaryTests(unittest.TestCase):
    def admitted_root_metadata(self):
        own={'path':str((HERE/'execution.py').relative_to(HERE.parents[4])),
             'sha256':hashlib.sha256((HERE/'execution.py').read_bytes()).hexdigest()}
        config={'path':'registered-initializer.json','sha256':'f'*64}
        return {'schema':'w50-g1-execution-root-1','lifecycle':'logical-phase-attempts-1',
                'repo':str(HERE.parents[4]),'inputs':[own,config],
                'instruments':{'initializer':{'entrypoint':own,'config':config},
                    'fit':{'entrypoint':{'path':'separate-live-evaluator.py','sha256':'a'*64},'config':config}}}

    def test_missing_prefit_refuses_before_native_values_or_solver_or_bridge(self):
        root=self.admitted_root_metadata()
        dispatcher=types.SimpleNamespace(root_doc=lambda p: root,
            verify_prefit=lambda p,d: (_ for _ in ()).throw(ValueError('UNMEASURED pre-fit')))
        with patch.object(E,'_bootstrap',return_value=dispatcher), \
                patch.object(E,'_load',side_effect=AssertionError('native/config opened')), \
                patch.object(E,'_source',side_effect=AssertionError('solver imported')), \
                patch.object(E,'_bridge',side_effect=AssertionError('runtime invoked')):
            for call in (lambda:E.initialize('unused'), lambda:E.bind_arguments('unused', [])):
                with self.assertRaisesRegex(ValueError,'UNMEASURED pre-fit'):call()

    def test_current_only_root_cannot_be_promoted_to_initializer(self):
        dispatcher=types.SimpleNamespace(root_doc=lambda p:{'schema':'w50-g1-current-instrument-root-1'},
            verify_prefit=lambda *args: (_ for _ in ()).throw(AssertionError('must refuse current first')))
        with patch.object(E,'_bootstrap',return_value=dispatcher):
            with self.assertRaisesRegex(ValueError,'live'):E.initialize('unused')

    def test_root_must_select_this_fit_source_before_reading_native_reports(self):
        root=self.admitted_root_metadata()
        root['instruments']['initializer']['entrypoint']={'path':'other.py','sha256':'a'*64}
        dispatcher=types.SimpleNamespace(root_doc=lambda p:root,verify_prefit=lambda *args:{'path':'pre','sha256':'b'*64})
        with patch.object(E,'_bootstrap',return_value=dispatcher), \
                patch.object(E,'_load',side_effect=AssertionError('native/config opened')):
            with self.assertRaisesRegex(ValueError,'fit source'):E.initialize('unused')

    def test_initializer_source_pin_does_not_impersonate_live_fit_evaluator(self):
        root=self.admitted_root_metadata()
        dispatcher=types.SimpleNamespace(root_doc=lambda p:root,
            verify_prefit=lambda *args:{'path':'prefit.json','sha256':'b'*64})
        with patch.object(E,'_bootstrap',return_value=dispatcher):
            self.assertEqual(E._admit('synthetic-root')[3]['sha256'],'b'*64)

    def test_unborn_legacy_live_root_and_singular_aliases_are_not_compatibility_paths(self):
        for legacy in ('missing-lifecycle','currentInstrument','currentResults'):
            root=self.admitted_root_metadata()
            if legacy=='missing-lifecycle':root.pop('lifecycle')
            else:root[legacy]={'synthetic':'virtual alias'}
            dispatcher=types.SimpleNamespace(root_doc=lambda p:root,
                verify_prefit=lambda *args:(_ for _ in ()).throw(AssertionError('legacy root admitted')))
            with patch.object(E,'_bootstrap',return_value=dispatcher),self.assertRaisesRegex(ValueError,'live lifecycle'):
                E._admit('synthetic-root')

    def test_no_public_numeric_observation_or_join_override(self):
        with self.assertRaises(TypeError):E.initialize('unused',readings=[1],joins=[2])
        with self.assertRaises(TypeError):E.bind_arguments('unused',[],records=[1])

    def test_admitted_initializer_selects_and_scores_one_joint_proposal_from_pinned_synthetic_reports(self):
        import shutil
        source=importlib.util.spec_from_file_location('w50_fit_synthetic_inputs',HERE/'test_inputs.py')
        F=importlib.util.module_from_spec(source);source.loader.exec_module(F)
        manifest, scenes, reports, inventory=F.fixture()
        with tempfile.TemporaryDirectory() as name:
            repo=Path(name).resolve(); fit=repo/'fit';fit.mkdir()
            shutil.copyfile(HERE/'uniform.py',fit/'uniform.py')
            def put(path, value):
                path.write_text(json.dumps(value));return {'path':str(path.relative_to(repo)),
                    'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
            report_pins={role:put(repo/(role+'.json'),value) for role,value in reports.items()}
            baselines=[put(repo/f'baseline-{p}.json',{'glassTintAmount':p}) for p in (.25,.5)]
            verified=[]
            state=dict(root={'partOne':{'sha256':'a'*64},'inputs':list(report_pins.values()),
                'baselineDocuments':baselines,'closure':{'sources':{'fit/uniform.py':
                    hashlib.sha256((fit/'uniform.py').read_bytes()).hexdigest()}}},
                repo=repo,completed={'native':{'reports':report_pins}},manifest=manifest,scenes=scenes,
                inventory=inventory,inputs=F.I,prefit={'path':'prefit','sha256':'b'*64},
                config={'completedCurrent':{'path':'current','sha256':'c'*64}},
                dispatcher=types.SimpleNamespace(verify_prefit=lambda *args:verified.append('after')))
            def bridge(state, operation, baseline):
                self.assertEqual(operation,'joins')
                position=json.loads((repo/baseline['path']).read_text())['glassTintAmount']
                return {'position':position,'joins':{f'{pose}.dark.{position}':[
                    dict(span=s,dpr=d,value=90) for s in range(32,225) for d in (1,2)]
                    for pose in ('active','receded')}}
            with patch.object(E,'HERE',fit),patch.object(E,'_state',return_value=state), \
                    patch.object(E,'_bridge',side_effect=bridge):
                result=E.initialize('synthetic-already-admitted')
            self.assertEqual(result['status'],'ANALYTICAL_PROPOSAL_ONLY')
            self.assertEqual(result['observations'],240)
            self.assertEqual(result['analyticalScore']['observations'],240)
            self.assertEqual(result['nativeReports'],report_pins)
            self.assertEqual(verified,['after'])
            self.assertFalse((fit/'candidates').exists())

    def test_persisted_evaluation_wrappers_match_unchanged_g0_evidence_shape(self):
        import shutil
        source=importlib.util.spec_from_file_location('w50_bind_synthetic_inputs',HERE/'test_inputs.py')
        F=importlib.util.module_from_spec(source);source.loader.exec_module(F)
        records, required, captured, evaluation, _=F.BindingTests().fixture()
        with tempfile.TemporaryDirectory() as name:
            repo=Path(name).resolve(); g0=repo/'g0';(g0/'audit').mkdir(parents=True)
            guard=g0/'audit/numerical_guard.py'
            shutil.copyfile(HERE.parents[1]/'2026-10-08-w50-g0-declaration/audit/numerical_guard.py',guard)
            def put(path,value):
                path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value))
                return {'path':str(path.relative_to(repo)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
            part=put(g0/'fit-declaration.json',{'synthetic':True})
            for group in (captured,evaluation):
                for item in group:
                    item.update(put(repo/item['path'],{'glassTintAmount':item['position'],
                                                        'syntheticIdentity':item['path']}))
            for record,before in zip(records,captured):
                record['candidateSha256']=before['sha256']
                record['provenance']['candidateDocument']={k:before[k] for k in ('path','sha256')}
                for key in ('report','capture'):
                    record['provenance'][key]=put(repo/f'{before["position"]}-{key}.json',{'synthetic':key})
            original=copy.deepcopy(records)
            output=repo/'fit/generated'
            state=dict(root={'baselineDocuments':[{k:b[k] for k in ('path','sha256')} for b in captured],
                'partTwo':part,'references':put(repo/'references.json',{'synthetic':True}),
                'closure':{'sources':{'g0/audit/numerical_guard.py':hashlib.sha256(guard.read_bytes()).hexdigest()}}},
                repo=repo,inputs=F.I,inventory={'schema':'w50-reference-inventory-1','cells':list(required.values())},
                completed={'arguments':records},config={'completedCurrent':put(repo/'current.json',{'arguments':records})},
                prefit={'path':'pre','sha256':'e'*64},output=output,
                dispatcher=types.SimpleNamespace(verify_prefit=lambda *args:None))
            def bridge(state,operation,baseline,evaluation):
                self.assertEqual(operation,'transfer')
                position=json.loads((repo/baseline['path']).read_text())['glassTintAmount']
                return dict(schema='w50-held-sampling-proof-1',position=position,
                    capturedCandidate=baseline,evaluationCandidate=evaluation,heldMaterialSha256='e'*64,
                    cssTierMappingSha256='f'*64,lightEndpointSha256s=['1'*64,'2'*64])
            with patch.object(E,'_state',return_value=state),patch.object(E,'_bridge',side_effect=bridge):
                result=E.bind_arguments('synthetic-already-admitted',evaluation)
                with self.assertRaises(FileExistsError):E.bind_arguments('synthetic-already-admitted',evaluation)
            cohort=json.loads((repo/result['cohort']['path']).read_text())
            manifest=json.loads((repo/result['argumentManifest']['path']).read_text())
            self.assertEqual(cohort['schema'],'w50-numerical-cohort-1')
            self.assertEqual(cohort['candidates'],evaluation)
            self.assertEqual(manifest['requiredIds'],sorted(required))
            self.assertEqual(records,original)
            for record in manifest['records']:
                evidence=record['evidence'];fields={k:v for k,v in record.items() if k!='evidence'}
                path=repo/evidence['path']
                self.assertEqual(evidence['sha256'],hashlib.sha256(path.read_bytes()).hexdigest())
                self.assertEqual(json.loads(path.read_text()),{'schema':'w50-measured-tone-argument-1',**fields})
                self.assertNotEqual(record['candidateSha256'],record['capturedCandidateSha256'])
                self.assertEqual(record['capturedArgument']['provenance'],record['provenance'])
            self.assertEqual(result['status'],'EVALUATION_ARGUMENT_BINDING_ONLY')

    def test_runtime_registration_is_a_root_input_not_a_python_source_pin(self):
        import shutil
        with tempfile.TemporaryDirectory() as name:
            repo=Path(name).resolve(); fit=repo/'fit';fit.mkdir()
            sources=[]
            for relative,source in [('fit/runtime-entry.mjs',HERE/'runtime-entry.mjs'),
                ('fit/runtime-bridge.ts',HERE/'runtime-bridge.ts'),('fit/runtime-probe.ts',HERE/'runtime-probe.ts'),
                ('owner/node-guard.mjs',HERE.parent/'owner/node-guard.mjs'),
                ('web/node-guard.mjs',HERE.parent/'web/node-guard.mjs')]:
                target=repo/relative;target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(source,target)
                sources.append({'path':relative,'sha256':E._sha(target)})
            node=Path(shutil.which('node')).resolve();node_pin={'path':str(node),'sha256':E._sha(node)}
            closure={'schema':'w50-fit-runtime-closure-1','sources':sources,'node':node_pin,
                'exercise':{'status':'SYNTHETIC_PRODUCTION_BRIDGE_EXERCISED',
                    'probe':{'path':'fit/runtime-probe.ts','sha256':E._sha(fit/'runtime-probe.ts')},
                    'branches':{'fixedJoinEndpoints':4,'builtCandidates':2,'heldTransfers':2,'heldMutationRefusals':2}}}
            path=repo/'runtime.json';path.write_text(json.dumps(closure))
            pin={'path':'runtime.json','sha256':E._sha(path)}
            root={'inputs':[pin],'closure':{'sources':{'only-python.py':'a'*64}}}
            config={'runtime':{'closure':pin,'node':node_pin}}
            with patch.object(E,'HERE',fit):
                self.assertEqual(E._runtime_spec(root,repo,config),(path,node))
                with self.assertRaises(ValueError):E._runtime_spec({**root,'inputs':[]},repo,config)
                wrong=copy.deepcopy(config);wrong['runtime']['node']['sha256']='0'*64
                with self.assertRaises(ValueError):E._runtime_spec(root,repo,wrong)
                closure['exercise']['branches']['heldTransfers']=0;path.write_text(json.dumps(closure))
                pin['sha256']=E._sha(path)
                with self.assertRaisesRegex(ValueError,'complete production probe'):
                    E._runtime_spec(root,repo,config)

    def test_child_environment_drops_ambient_compiler_and_loader_overrides(self):
        import os
        with patch.dict(os.environ,{'NODE_OPTIONS':'--eval bad','ESBUILD_BINARY_PATH':'/bad/esbuild',
                                    'NODE_PATH':'/bad/modules','PATH':'/bad/path','TSX_DISABLE_CACHE':'0'}):
            env=E._child_environment(Path('/synthetic/repo'),Path('/synthetic/closure.json'),'a'*64)
        self.assertNotIn('NODE_OPTIONS',env)
        self.assertNotIn('ESBUILD_BINARY_PATH',env)
        self.assertNotIn('NODE_PATH',env)
        self.assertEqual(env['PATH'],'/usr/bin:/bin:/usr/sbin:/sbin')
        self.assertEqual(env['TSX_DISABLE_CACHE'],'1')

    def test_output_is_write_once_and_source_bytes_are_not_overwritten(self):
        with tempfile.TemporaryDirectory() as name:
            path=Path(name)/'evidence.json'
            E._write_once(path,{'synthetic':True})
            with self.assertRaises(FileExistsError):E._write_once(path,{'synthetic':False})
            self.assertEqual(json.loads(path.read_text()),{'synthetic':True})


if __name__=='__main__':unittest.main()
