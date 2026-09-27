"""Fixed-domain evidence never narrows admitted membership or fabricates runtime fields."""
from copy import deepcopy
import unittest
import runner
import test_runner as harness

DOMAIN = {'policy':'nominal','variant':'regular','samplingBackend':'gpu-texture',
          'presence':{'identified':1,'intermediate':'unmeasured-linear-interpolation',
                      'zero':'exact-skip'}}


def records(wave, cells, root):
    """Synthetic values in capture-web.ts's actual wrapper and SceneReport shape.

    No runtime variant/presence fields exist. The separate source attestation
    supplies those facts, never these fabricated test observations.
    """
    profiles = runner.load(root/'config.json')['candidates']['standin']['profiles']
    result = {}
    for cell in cells:
        profile, sid = cell.split('/')
        definition = next(p for p in wave.spec['profiles'] if p['key']==profile)
        scale = 2 if '-2x-' in profile else 1
        canvas = wave.spec['canvas']
        size = [canvas['width']*scale, canvas['height']*scale]
        documents = profiles[profile]
        active_document = runner.load(root/documents['material'])
        material = active_document['patch']
        mapping = active_document.get('cssTierMapping')
        receded = runner.load(root/documents['receded'])['patch']
        inactive = wave.scenes[sid]['state']=='inactive'
        # Explicit expected nested merge, not the runner's merge helper. A real
        # inactive candidate capture still reports an active root.
        posed = {**material, 'outerShadow':{**material.get('outerShadow', {}),
                    **receded['outerShadow']}} if inactive else material or None
        page = dict(sceneId=sid, requestedRenderer='webgpu', requestedScale=scale,
            requestedBackdropMode='texture', requestedBackdropLevel=None,
            devicePixelRatio=scale, frames=8, canvas=canvas, pixelSize=size,
            background=dict(id=wave.scenes[sid]['background'], url='/synthetic.png',
                            naturalWidth=size[0], naturalHeight=size[1]),
            pressed=False, transparentPage=False, tint=None, materialProfile=posed,
            recededMaterialProfile=None,
            candidateRecededMaterialProfile=receded if inactive else None,
            windowActivation='active', colorScheme=definition['colorScheme'],
            material=dict(name='synthetic', platform='macOS 27.0', tuned=True),
            cssTierMapping=mapping, accessibilityOverrides=None,
            accessibilityPolicy=dict(reducedTransparency=False, increasedContrast=False,
                                     reducedMotion=False, forcedColors=False),
            groups=[dict(id='synthetic', configuredSource='texture',
                         state=dict(configuredSource='texture', activeRenderer='webgpu',
                                    samplingBackend='gpu-texture', refraction='true',
                                    analysis='exact', health='ok'),
                         unsampledMaterial=None, backdropTone=None)],
            surfaces=[], webgpu=dict(available=True, deviceHealth='ok', ownership='vitrea'),
            rendererActive=True, adapter=dict(ok=True, vendor='synthetic',
                architecture='synthetic', isFallback=False), canvasColorSpace='srgb',
            canvasColorSpaceNote='synthetic observation', diagnostics=[], problems=[])
        result[cell] = dict(descriptor=dict(engine='chromium', engineVersion='synthetic',
            renderer='webgpu', samplingBackend='gpu-texture', gpuAdapter='synthetic/synthetic',
            colorSpace='srgb', capturePath='synthetic stand-in; no browser was launched',
            sceneId=sid, pixelSize=size, deterministic=True, repeatNoise=0),
            report=dict(capturedAt='2026-09-27T00:00:00.000Z', requestedRenderer='webgpu',
                colorScheme=definition['colorScheme'], accessibility=None,
                materialProfile=dict(path=str(root/documents['material']),
                    sha256=runner.sha(root/documents['material'])[:12], patch=material,
                    cssTierMapping=mapping),
                recededProfile=dict(path=str(root/documents['receded']),
                    sha256=runner.sha(root/documents['receded'])[:12], patch=receded),
                fallback=None, problems=[], page=page))
    return result


def evidence(test, cells):
    config = runner.load(test.root/'config.json') if (test.root/'config.json').exists() else {}
    profiles = {}
    for cell in cells:
        profile = cell.split('/')[0]
        scheme = next(p['colorScheme'] for p in test.wave.spec['profiles'] if p['key']==profile)
        documents = {k:f'synthetic-{scheme}-{k}.json' for k in ('material','receded')}
        test.put(documents['material'], {'patch':{'bodyChromaRetention':0.2 if scheme=='light' else 0.4,
            'outerShadow':{'sigmaPx':2,'liftAmplitude':0.01}}})
        test.put(documents['receded'], {'patch':{'outerShadow':{'liftAmplitude':0}}})
        profiles[profile] = documents
    config['candidates'] = {'standin':{'profiles':profiles}}
    test.put('config.json', config)
    test.put('domain-evidence.json', {'attestation':'domain-attestation.json',
                                    'cells':records(test.wave,cells,test.root)})
    source='packages/renderer-webgpu/src/standin.txt'
    if not (test.root/source).exists():
        test.put(source,'synthetic regular full-presence runtime')
    scene='packages/calibration/web/scene.ts'
    test.put(scene,'// Synthetic scene: regular, channels omitted; no runtime measurement.')
    test.put('domain-attestation.json',{
        'basis':'source-derived', 'variant':'regular', 'presence':1,
        'effectivePresenceBasis':'Synthetic source chain only, never native or browser evidence.',
        'limitations':'Variant/presence are authored facts, not observed runtime fields.',
        'sourceChain':[{'path':path,'sha256':runner.sha(test.root/path),
                        'claim':'Synthetic registration/default chain.'} for path in (scene,source)]})


class DomainTests(harness.ExposureTests):
    def freeze(self):
        self.commit()
        return runner.freeze(self.root,self.wave,self.candidates,config='config.json',
                             scorer='scorer.py',declaration='declaration.txt',closure='closure.json',
                             dry_cells=self.cells)

    def test_claim_domain_is_mandatory_not_an_implicit_default(self):
        scope=runner.load(self.root/'claim.json')
        scope.pop('domain',None)
        self.put('claim.json',scope)
        with self.assertRaisesRegex(ValueError,'domain'):
            self.freeze()

    def test_actual_domain_failure_on_unclaimed_endpoint_refuses_freeze(self):
        # All endpoint membership stays present. Domain never offers a selective exclusion.
        data=runner.load(self.root/'domain-evidence.json')
        for key in ('reducedTransparency','increasedContrast','forcedColors'):
            changed=deepcopy(data)
            changed['cells'][self.cells[0]]['report']['page']['accessibilityPolicy'][key]=True
            self.put('domain-evidence.json',changed)
            with self.subTest(key=key), self.assertRaisesRegex(ValueError,'domain'):
                self.freeze()
        changed=deepcopy(data)
        changed['cells'][self.cells[0]]['descriptor']['samplingBackend']='css-backdrop'
        self.put('domain-evidence.json',changed)
        with self.assertRaisesRegex(ValueError,'domain'):
            self.freeze()

    def test_missing_or_unbound_source_chain_is_not_presence_proof(self):
        original=runner.load(self.root/'domain-attestation.json')
        for chain in ([], [dict(original['sourceChain'][0],sha256='0'*64)]):
            self.put('domain-attestation.json',dict(original,sourceChain=chain))
            with self.subTest(chain=chain), self.assertRaisesRegex(ValueError,'domain'):
                self.freeze()

    def test_missing_frozen_capture_domain_record_cannot_reduce_membership(self):
        data=runner.load(self.root/'domain-evidence.json')
        del data['cells'][self.cells[0]]
        self.put('domain-evidence.json',data)
        with self.assertRaisesRegex(ValueError,'domain.*coverage mismatch'):
            self.freeze()

    def test_fresh_capture_policy_and_backend_are_checked(self):
        cell=self.cells[0]
        valid=records(self.wave,[cell],self.root)[cell]
        profiles=runner.load(self.root/'config.json')['candidates']['standin']['profiles']
        documents=runner.domain_documents(self.root,profiles[cell.split('/')[0]])
        runner.validate_domain(self.wave,cell,valid['descriptor'],valid['report'],documents)
        for mutation in ('policy','source','hint','missing'):
            changed=deepcopy(valid)
            if mutation=='policy': changed['report']['page']['accessibilityPolicy']['forcedColors']=True
            if mutation=='source': changed['report']['page']['groups'][0]['state']['samplingBackend']='none'
            if mutation=='hint': changed['report']['page']['requestedBackdropLevel']=0.5
            if mutation=='missing': changed['report']['page'].pop('accessibilityPolicy')
            with self.subTest(mutation=mutation), self.assertRaisesRegex(ValueError,'domain'):
                runner.validate_domain(self.wave,cell,changed['descriptor'],changed['report'],documents)

    def test_empty_active_patch_is_omitted_but_candidate_recede_still_draws(self):
        profiles=runner.load(self.root/'config.json')['candidates']['standin']['profiles']
        profile=next(iter(profiles))
        paths=profiles[profile]
        self.put(paths['material'], {'patch':{},'cssTierMapping':{}})
        documents=runner.domain_documents(self.root,paths)
        allowed=runner.cells_for(self.wave,('calibration',),True)
        for pose in ('rest','inactive'):
            cell=next(c for c in allowed if c.split('/')[0]==profile
                      and self.wave.scenes[c.split('/')[1]]['state']==pose)
            record=records(self.wave,[cell],self.root)[cell]
            page=record['report']['page']
            self.assertEqual(record['report']['materialProfile']['patch'],{})
            self.assertEqual(page['cssTierMapping'],{})
            if pose=='rest':
                self.assertIsNone(page['materialProfile'])
            else:
                self.assertEqual(page['materialProfile'],{'outerShadow':{'liftAmplitude':0}})
            with self.subTest(pose=pose):
                runner.validate_domain(self.wave,cell,record['descriptor'],record['report'],documents)
            for mutation in ('missing','empty-object','wrong-value'):
                changed=deepcopy(record)
                if mutation=='missing':
                    changed['report']['page'].pop('materialProfile')
                else:
                    changed['report']['page']['materialProfile']=(
                        {} if mutation=='empty-object' else None if pose=='inactive' else {'outerShadow':{}})
                with self.subTest(pose=pose,mutation=mutation),self.assertRaisesRegex(ValueError,'domain'):
                    runner.validate_domain(self.wave,cell,changed['descriptor'],changed['report'],documents)



def substitutions(record):
    """Independent bad readings, each still nominal WebGPU texture sampling."""
    mutations = [
        ('descriptor size', ('descriptor','pixelSize'), [1,1]),
        ('page size', ('report','page','pixelSize'), [1,1]),
        ('canvas', ('report','page','canvas'), {'width':1,'height':1}),
        ('requested scale', ('report','page','requestedScale'), 3),
        ('actual scale', ('report','page','devicePixelRatio'), 3),
        ('driver scheme', ('report','colorScheme'), 'wrong'),
        ('actual scheme', ('report','page','colorScheme'), 'wrong'),
        ('actual activation', ('report','page','windowActivation'), 'inactive'),
        ('material hash', ('report','materialProfile','sha256'), '0'*12),
        ('receded hash', ('report','recededProfile','sha256'), '0'*12),
        ('material patch', ('report','materialProfile','patch'), {'bodyChromaRetention':1}),
        ('receded patch', ('report','recededProfile','patch'), {'bodyChromaRetention':1}),
        ('posed patch', ('report','page','materialProfile'), {}),
        ('candidate pose', ('report','page','candidateRecededMaterialProfile'), {'wrong':1}),
        ('runtime recede', ('report','page','recededMaterialProfile'), {}),
        ('fallback', ('report','fallback'), 'software'),
        ('driver problems', ('report','problems'), ['failed']),
        ('page problems', ('report','page','problems'), ['failed']),
    ]
    for name, path, value in mutations:
        changed = deepcopy(record)
        obj = changed
        for key in path[:-1]: obj = obj[key]
        obj[path[-1]] = value
        yield name, changed


class AssociationTests(harness.ProductionScopeTests):
    def test_full_membership_binds_producer_facts_before_any_exposure(self):
        original = runner.load(self.root/'domain-evidence.json')
        manifest = self.freeze()
        self.assertEqual((len(manifest['numericalCells']),len(manifest['renderedCells'])),(648,600))
        # Same scene ID occurs under both schemes/scales. Its label cannot prove
        # that the source record belongs to this profile, including blind rows.
        targets = [next(c for c in self.rendered if self.wave.roles[c.split('/')[1]]==role
                   and f'-{scale}x-{scheme}-' in c
                   and self.wave.scenes[c.split('/')[1]]['state']==pose)
                   for role,scale,scheme,pose in [('holdout',2,'light','inactive'),
                                                  ('calibration',1,'dark','rest')]]
        for cell in targets:
            for name, changed in substitutions(original['cells'][cell]):
                data = deepcopy(original)
                data['cells'][cell] = changed
                self.put('domain-evidence.json',data)
                self.commit()
                with self.subTest(cell=cell, mutation=name), self.assertRaisesRegex(ValueError,'domain'):
                    self.freeze()
        self.put('domain-evidence.json',original)
        self.commit()
        self.assertEqual(len(self.freeze()['renderedCells']),600)

    def test_fresh64_use_the_same_profile_and_document_validation(self):
        from pathlib import Path
        import json
        from unittest.mock import patch
        self.manifest = self.freeze()
        heldout = tuple(c for c in self.rendered if self.wave.roles[c.split('/')[1]]=='holdout')
        self.assertEqual(len(heldout),64)
        original = records(self.wave,heldout,self.root)
        current = deepcopy(original)
        output = self.root/'fresh-synthetic'
        def launch(command, env, check):
            destination = Path(command[command.index('--out')+1])
            for cell, record in current.items():
                profile, sid = cell.split('/')
                if profile!=destination.name: continue
                directory = destination/sid
                directory.mkdir(parents=True,exist_ok=True)
                scale = 2 if '-2x-' in profile else 1
                (directory/(sid+'__webgpu.png')).write_bytes((self.root/f'{scale}x.png').read_bytes())
                for name,key in [('cell','descriptor'),('report','report')]:
                    (directory/f'{name}__webgpu.json').write_text(json.dumps(record[key]))
        configuration = dict(scenes=self.wave.scenes_sha,split=self.wave.split_sha,
            generation=self.manifest['generation'],instrument='synthetic',closure='synthetic',
            candidate='synthetic')
        with runner.boundary.Receipt(self.root/'synthetic-receipt.jsonl',configuration).expose() as token:
            request = runner.CaptureRequest(self.wave,token,self.root,self.manifest,
                'standin',heldout,output)
            with patch.object(runner.subprocess,'run',side_effect=launch):
                self.assertEqual(set(runner.capture_web(request)),set(heldout))
                cell = heldout[0]
                for name, changed in substitutions(original[cell]):
                    current[cell] = changed
                    with self.subTest(mutation=name), self.assertRaisesRegex(ValueError,'domain'):
                        runner.capture_web(request)
                current[cell] = original[cell]
                self.assertEqual(set(runner.capture_web(request)),set(heldout))


def load_tests(loader, standard_tests, pattern):
    return unittest.TestSuite(loader.loadTestsFromName(name,cls)
        for cls in (DomainTests,AssociationTests)
        for name in cls.__dict__ if name.startswith('test_'))
