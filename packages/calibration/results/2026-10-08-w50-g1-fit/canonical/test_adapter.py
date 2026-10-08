"""Synthetic transport tests: no renderer, fixtures or measured results are opened."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent


def module():
    spec = importlib.util.spec_from_file_location('canonical_adapter', HERE/'adapter.py')
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


class CanonicalTests(unittest.TestCase):
    def setUp(self):
        self.a = module()
        self.run = dict(id='owner', sceneSource='canonical', profile='apple-macos-27.0-1x-dark-standard-glass0.25',
                        renderer='webgpu', scenes=['pressed','stack','tint'], sets=['calibration'],
                        candidate={'path':'candidate.json','sha256':'a'*64})
        self.scenes = dict(canvas={'width':320,'height':200}, profiles=[dict(key=self.run['profile'],
            colorScheme='dark',a11y='standard',scenes=self.run['scenes'])],
            split={'calibration':self.run['scenes']}, components={'stack':{'kind':'stack'},'single':{'kind':'capsule'}},
            scenes=[dict(id='pressed',state='pressed',component='single'),
                    dict(id='stack',state='rest',component='stack'),
                    dict(id='tint',state='inactive',component='single',tint='orange')])

    def test_full_owner_shapes_are_planned_without_single_surface_restriction(self):
        p = self.a.scene_plan(self.run,'gate',self.scenes)
        self.assertEqual([s['id'] for s in p['scenes']], ['pressed','stack','tint'])
        for mutation in ('holdout','other-profile','new512'):
            run, scenes = copy.deepcopy(self.run), copy.deepcopy(self.scenes)
            if mutation=='holdout': scenes['split']={'holdout':run['scenes']}; run['sets']=['holdout']
            if mutation=='other-profile': scenes['profiles'][0]['scenes']=['pressed']
            if mutation=='new512': run['sceneSource']='w50'
            with self.assertRaises(ValueError): self.a.scene_plan(run,'gate',scenes)

    def test_bypass_and_unregistered_run_refuse_before_subprocess(self):
        with patch.object(self.a.subprocess,'run') as launch:
            with self.assertRaises(ValueError): self.a.capture_run({},self.run)
            launch.assert_not_called()

    def test_candidate_capture_requires_central_admission_before_reading_candidate(self):
        class Dispatcher:
            def require_context(self,context): pass
            def require_render_admission(self,context,run,*,current=False):
                raise ValueError('No central numerical admission or owned GPU lease')
        context={'repo':str(self.a.ROOT),'phase':'gate','batch':{'runs':[self.run]}}
        with patch.dict(__import__('sys').modules,{'w50_g1_dispatch':Dispatcher()}), patch.object(self.a,'load_source') as load:
            with self.assertRaisesRegex(ValueError,'central numerical admission'):
                self.a.capture_run(context,self.run)
            load.assert_not_called()

    def test_guard_is_inherited_by_real_synthetic_child_process(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            guard=root/'guard.mjs'; guard.write_text("process.env.GUARDED='yes';")
            child=root/'child.mjs'; child.write_text("console.log(process.env.GUARDED);")
            parent=root/'parent.mjs'; parent.write_text("import {spawnSync} from 'node:child_process'; process.stdout.write(spawnSync(process.execPath,[process.argv[2]],{encoding:'utf8'}).stdout);")
            with patch.dict(__import__('os').environ,{'NODE_OPTIONS':'--require=/untrusted.js',
                    'NODE_PATH':'/untrusted','VITREA_FIXTURES':'/other-bed','W50_INJECT':'other'}):
                env=self.a.capture_environment(root,root/'closure.json','b'*64,root/'captures',root/'matrix.json',guard)
            self.assertNotIn('NODE_PATH',env)
            self.assertNotIn('W50_INJECT',env)
            out=subprocess.run(['node',str(parent),str(child)],env=env,text=True,capture_output=True,check=True)
            self.assertEqual(out.stdout.strip(),'yes')
            self.assertNotIn('VITREA_FIXTURES',env)

    def test_production_guard_survives_npx_tsx_child_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for name in ('node-guard.mjs','vite-guard.mjs'):
                (root/name).write_bytes((self.a.WEB/name).read_bytes())
            (root/'package.json').write_text('{"type":"module"}')
            child=root/'child.ts'; child.write_text('const x: number = 7; console.log(x);')
            parent=root/'parent.mjs'; parent.write_text("import {spawnSync} from 'node:child_process'; const r=spawnSync('npx',['--no-install','tsx',process.argv[2]],{stdio:'inherit'}); process.exit(r.status??1);")
            pins=[{'path':p.name,'sha256':self.a.sha(p)} for p in root.iterdir()]
            closure=root/'closure.json'; closure.write_text(json.dumps({'sources':pins}))
            env=self.a.capture_environment(root,closure,self.a.sha(closure),root/'captures',root/'matrix.json',root/'node-guard.mjs')
            args=['node',str(parent),str(child)]
            result=subprocess.run(args,cwd=self.a.CAL,env=env,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(result.stdout.strip(),'7')
            child.write_text('console.log(8);')
            changed=subprocess.run(args,cwd=self.a.CAL,env=env,capture_output=True,text=True)
            self.assertNotEqual(changed.returncode,0)
            self.assertNotIn('8',changed.stdout)
            # The parent can validate every pinned file without seeing this import. Only
            # the guard inherited by npx/tsx can refuse the newly reached child source.
            (root/'unlisted.ts').write_text("console.log('UNSEALED_CHILD_EXECUTED');")
            child.write_text("import './unlisted.ts';")
            for pin in pins:
                if pin['path']=='child.ts': pin['sha256']=self.a.sha(child)
            closure.write_text(json.dumps({'sources':pins}))
            env['W50_WEB_CLOSURE_SHA256']=self.a.sha(closure)
            unlisted=subprocess.run(args,cwd=self.a.CAL,env=env,capture_output=True,text=True)
            self.assertNotEqual(unlisted.returncode,0)
            self.assertNotIn('UNSEALED_CHILD_EXECUTED',unlisted.stdout)

    def test_each_capture_has_its_own_census_and_failure_stops_remaining_cells(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            script=root/'compare.mjs'
            script.write_text("import {appendFileSync} from 'node:fs'; const scene=process.argv[process.argv.indexOf('--scene')+1]; appendFileSync(process.env.SEEN,scene+'\\n'); if(scene==='stack')process.exit(1);")
            observed=[]
            class Census:
                def observe(self):
                    observed.append('census')
                    return {'passes':True}
            env={**__import__('os').environ,'SEEN':str(root/'seen')}
            with patch.object(self.a,'require'), patch.object(self.a,'load_source',return_value=Census()):
                with self.assertRaises(ValueError):
                    self.a.launch_cells({},self.run,['node',str(script),'--scene',','.join(self.run['scenes'])],env,root)
            self.assertEqual((root/'seen').read_text(),'pressed\nstack\n')
            self.assertEqual(observed,['census','census'])
            self.assertFalse((root/'census-tint.json').exists())
            self.assertEqual(json.loads((root/'exit-stack.json').read_text()),{'returncode':1})

    def test_output_paths_are_fresh_and_inside_claimed_invocation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); output=root/'invocation'; output.mkdir()
            captures=output/'captures'; matrix=output/'matrix.json'
            self.a.validate_destinations(output,captures,matrix)
            for c,m in ((root/'escaped',matrix),(captures,root/'escaped.json'),
                        (captures,captures/'matrix.json'),(captures/'nested',captures)):
                with self.assertRaises(ValueError): self.a.validate_destinations(output,c,m)
            captures.mkdir()
            with self.assertRaises(ValueError): self.a.validate_destinations(output,captures,matrix)

    def test_native_request_uses_original_inventory_pins_without_opening_pngs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); inventory=root/'references.json'; execution=root/'root.json'
            fixtures=root/'original-main-fixtures'; fixtures.mkdir()
            manifest=fixtures/'manifest.json'; manifest.write_text('{}')
            run={**self.run,'nativeManifest':{'path':str(manifest),'sha256':self.a.sha(manifest)}}
            rows=[dict(profile=run['profile'],renderer='webgpu',scene=s,nativeEvidence=
                  {'path':str(fixtures/run['profile']/(s+'.png')),'sha256':'f'*64}) for s in run['scenes']]
            pin=rows[0]['nativeEvidence']
            inventory.write_text(json.dumps({'cells':rows}))
            execution.write_text(json.dumps({'references':{'path':str(inventory),'sha256':self.a.sha(inventory)}}))
            class Dispatcher:
                def checked(self,repo,item):
                    if self_outer.a.sha(item['path'])!=item['sha256']: raise ValueError('Changed original reference')
                    return Path(item['path'])
            self_outer=self
            context={'executionRoot':str(execution)}
            request=self.a.native_request(context,run,Dispatcher())
            self.assertEqual(request['fixtures']['path'],str(fixtures.resolve()))
            self.assertEqual(request['fixtures']['manifest']['sha256'],self.a.sha(manifest))
            self.assertEqual(request['native'][0],{'scene':'pressed',**pin,'path':str(Path(pin['path']).resolve())})
            self.assertFalse(Path(pin['path']).exists())
            rows.append({**rows[0],'nativeEvidence':{**pin,'sha256':'e'*64}})
            inventory.write_text(json.dumps({'cells':rows}))
            execution.write_text(json.dumps({'references':{'path':str(inventory),'sha256':self.a.sha(inventory)}}))
            with self.assertRaisesRegex(ValueError,'conflicting'):
                self.a.native_request(context,self.run,Dispatcher())

    def test_real_production_label_admits_repository_relative_candidate(self):
        import os
        result=subprocess.run(['node','--import','tsx','--test',str(HERE/'native-admission.test.ts')],
            cwd=self.a.CAL,env={**os.environ,'W50_TEST_REPO':str(self.a.ROOT)},capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr+result.stdout)
        label=next(line.split('PRODUCTION_LABEL=',1)[1] for line in result.stdout.splitlines() if 'PRODUCTION_LABEL=' in line)
        run={**self.run,'scenes':['pressed']}
        matrix={'schemaVersion':5,'cells':[dict(key=dict(profileKey=run['profile'],sceneId='pressed',
            web=dict(renderer='webgpu',capturePath=label)),fixtureSet='calibration')]}
        self.a.validate_matrix(matrix,run,self.a.ROOT/'candidate.json')

    def test_matrix_membership_and_candidate_stamp_are_exact(self):
        run={**self.run,'scenes':['pressed']}
        web=dict(renderer='webgpu',capturePath='candidateDocument=/candidate.json declarationSha256='+ 'a'*12)
        matrix={'schemaVersion':5,'cells':[dict(key=dict(profileKey=run['profile'],sceneId='pressed',web=web),fixtureSet='calibration')]}
        self.assertEqual(len(self.a.validate_matrix(matrix,run,Path('/candidate.json'))),1)
        for bad in ('duplicate','stamp','split','profile','scene','schema'):
            m=copy.deepcopy(matrix)
            if bad=='schema': m['schemaVersion']=4
            if bad=='duplicate': m['cells']*=2
            if bad=='stamp': m['cells'][0]['key']['web']['capturePath']+=' crossPosition=0.5'
            if bad=='split': m['cells'][0]['fixtureSet']='holdout'
            if bad=='profile': m['cells'][0]['key']['profileKey']='other'
            if bad=='scene': m['cells'][0]['key']['sceneId']='extra'
            with self.assertRaises(ValueError): self.a.validate_matrix(m,run,Path('/candidate.json'))

    def test_artifacts_reject_unstable_capture_and_wrong_raster_dimensions(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp); scene={'id':'synthetic'}
            web=dict(renderer='webgpu',colorSpace='srgb',deterministic=True,repeatNoise=0)
            (folder/'cell__webgpu.json').write_text(json.dumps(web))
            (folder/'report__webgpu.json').write_text('{}')
            png=folder/'synthetic__webgpu.png'
            png.write_bytes(b'\x89PNG\r\n\x1a\n'+bytes(8)+(320).to_bytes(4,'big')+(200).to_bytes(4,'big'))
            evidence=self.a.capture_artifacts(folder,scene,'webgpu',web,1)
            self.assertEqual(set(evidence),{'png','cell','report','files'})
            web['repeatNoise']=.01
            (folder/'cell__webgpu.json').write_text(json.dumps(web))
            with self.assertRaises(ValueError): self.a.capture_artifacts(folder,scene,'webgpu',web,1)
            web['repeatNoise']=0
            (folder/'cell__webgpu.json').write_text(json.dumps(web))
            with self.assertRaises(ValueError): self.a.capture_artifacts(folder,scene,'webgpu',web,2)

    def test_report_checks_all_groups_not_only_first(self):
        endpoint=dict(profileKey='candidate-key',resolvedMaterialSha256='c'*16)
        material=dict(**endpoint,tuned=False,glassTintAmount=.25)
        state=dict(activeRenderer='webgpu',health='ok',materialDocument=material)
        page=dict(sceneId='stack',materialMode='candidate',candidateDocument=dict(mode='candidate',declarationSha256='a'*12),
            colorScheme='dark',windowActivation='active',material=material,requestedRenderer='webgpu',
            canvas={'width':320,'height':200},pixelSize=[320,200],devicePixelRatio=1,requestedScale=1,
            pressed=False,tint=None,transparentPage=False,accessibilityPolicy=dict(reducedTransparency=False,increasedContrast=False,forcedColors=False),
            groups=[dict(id='base',state=copy.deepcopy(state)),dict(id='over',state=copy.deepcopy(state))],
            surfaces=[dict(nodeId='s1',groupId='base'),dict(nodeId='s2',groupId='over')])
        plan=self.a.scene_plan(self.run,'gate',self.scenes)
        self.a.validate_report({'page':page},self.run,plan,self.scenes['scenes'][1],endpoint)
        incomplete=copy.deepcopy(page); incomplete['surfaces']=incomplete['surfaces'][:1]
        with self.assertRaises(ValueError): self.a.validate_report({'page':incomplete},self.run,plan,self.scenes['scenes'][1],endpoint)
        stack_page=copy.deepcopy(page)
        page['groups']=page['groups'][:1]; page['surfaces']=page['surfaces'][:1]
        tinted={**self.scenes['scenes'][2],'interaction':'pressed'}
        plan['tints']={'orange':{'srgb':[255,149,0],'alpha':.5}}
        page.update(sceneId='tint',windowActivation='inactive',pressed=True,tint='rgb(255 149 0 / 0.5)')
        self.a.validate_report({'page':page},self.run,plan,tinted,endpoint)
        page['tint']='rgb(255 149 0 / 1)'
        with self.assertRaises(ValueError): self.a.validate_report({'page':page},self.run,plan,tinted,endpoint)
        page=stack_page
        page['groups'][1]['state']['materialDocument']['resolvedMaterialSha256']='d'*16
        with self.assertRaises(ValueError): self.a.validate_report({'page':page},self.run,plan,self.scenes['scenes'][1],endpoint)


if __name__=='__main__': unittest.main()
