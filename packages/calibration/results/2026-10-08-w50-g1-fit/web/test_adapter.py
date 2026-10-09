"""Source-only tests: no fixture/archive PNG, browser, or machine observer is read."""
import copy
import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('w50_web', HERE / 'adapter.py')
A = importlib.util.module_from_spec(spec)
spec.loader.exec_module(A)


def request():
    return dict(profile='apple-macos-27.0-2x-dark-standard-glass0.25', renderer='webgpu',
                sceneSource='w50', scenes=['cell-grey-004-s096__inactive'],
                sets=['calibration'], candidate={'path': 'candidate.json', 'sha256': 'a'*64})


def report():
    material = dict(name='apple-macos-27.0-glass0.25', platform='macOS 27.0',
                    glassTintAmount=0.25, profileKey='dark-receded',
                    resolvedMaterialSha256='b'*16, tuned=False)
    return dict(fallback=None, problems=[], page=dict(
        sceneId='cell-grey-004-s096__inactive', requestedRenderer='webgpu',
        canvas={'width':512, 'height':384}, pixelSize=[1024,768], devicePixelRatio=2,
        requestedScale=2, colorScheme='dark', materialMode='candidate',
        windowActivation='inactive', material=material,
        candidateDocument=dict(mode='candidate', declarationSha256='a'*12),
        requestedBackdropMode='texture', requestedBackdropLevel=None,
        background=dict(id='grey-004',naturalWidth=1024,naturalHeight=768),
        accessibilityPolicy=dict(reducedTransparency=False,increasedContrast=False,forcedColors=False), problems=[],
        surfaces=[dict(nodeId='s',groupId='g',family='fixed-rounded-rect',radius=20.4,bounds=dict(x=172,y=144,width=168,height=96))],
        groups=[dict(id='g',backdropTone=None,state=dict(activeRenderer='webgpu',
            samplingBackend='gpu-texture',materialDocument=material,health='ok',
            backdropToneAbscissae=[dict(surfaceId='s',kind='silhouette',
                encodedLuminance=.1,luminance=.010022825574869039,
                linearLuminance=.2,color=[.2,.2,.2],sampleCount=40,level=0,
                sourceWidth=1024,sourceHeight=768,sampledWidth=1024,sampledHeight=768)]))]))


def endpoint():
    return dict(profileKey='dark-receded',resolvedMaterialSha256='b'*16)


class AdapterTests(unittest.TestCase):
    def test_sealed_custom_scene_does_not_use_canonical_canvas(self):
        plan = A.scene_plan(request())
        self.assertEqual(plan['canvas'], {'width':512,'height':384})
        self.assertEqual(plan['scenes'][0]['span'],96)
        self.assertEqual(plan['scenes'][0]['pose'],'receded')
        self.assertEqual(plan['scenes'][0]['geometry'],dict(x=172,y=144,width=168,height=96))

    def test_rejects_invalid_route_scene_profile_tier_and_set(self):
        for key, value in [('sceneSource','other'),('scenes',['impulse__rrect-lg__rest']),
                           ('profile','apple-macos-27.0-2x-light-standard-glass0.25'),
                           ('renderer','auto'),('sets',['holdout'])]:
            with self.subTest(key=key), self.assertRaises(ValueError):
                A.scene_plan({**request(),key:value})

    def test_independent_means_are_kept_not_decoded_from_one_another(self):
        args=A.validate_report(report(),request(),endpoint())
        self.assertEqual(args[0]['encodedLuminance'],.1)
        self.assertEqual(args[0]['linearLuminance'],.2)
        self.assertEqual(args[0]['rgb'],[.2,.2,.2])
        self.assertEqual(args[0]['provenance']['kind'],'silhouette')

    def test_source_argument_uses_recorded_level_not_rgb_mean(self):
        r=report(); g=r['page']['groups'][0]
        del g['state']['backdropToneAbscissae']
        g['backdropTone']=dict(level=.010022825574869039,linearLuminance=.2,rgb=[.2]*3)
        args=A.validate_report(r,request(),endpoint(),abscissa='source')
        self.assertAlmostEqual(args[0]['encodedLuminance'],.1)
        self.assertEqual(args[0]['linearLuminance'],.2)
        self.assertEqual(args[0]['provenance']['kind'],'source')

    def test_missing_silhouette_is_not_replaced_with_source_average(self):
        r=report(); del r['page']['groups'][0]['state']['backdropToneAbscissae']
        r['page']['groups'][0]['backdropTone']=dict(level=.1,linearLuminance=.1,rgb=[.1]*3)
        with self.assertRaises(ValueError): A.validate_report(r,request(),endpoint())

    def test_refuses_wrong_drawn_state_or_canvas(self):
        for mutate in [lambda p:p.update(canvas={'width':320,'height':200}),
                       lambda p:p.update(materialMode='default'),
                       lambda p:p.update(windowActivation='active'),
                       lambda p:p.update(pixelSize=[512,384]),
                       lambda p:p['material'].update(tuned=True),
                       lambda p:p['material'].update(glassTintAmount=.5),
                       lambda p:p['material'].update(resolvedMaterialSha256='c'*16),
                       lambda p:p['candidateDocument'].update(declarationSha256='c'*12),
                       lambda p:p['groups'][0]['state'].update(activeRenderer='css'),
                       lambda p:p['surfaces'][0]['bounds'].update(width=169),
                       lambda p:p['surfaces'][0].update(radius=21),
                       lambda p:p['surfaces'][0].update(family='capsule'),
                       lambda p:p['accessibilityPolicy'].update(reducedTransparency=True),
                       lambda p:p.update(requestedBackdropMode='dom'),
                       lambda p:p['groups'][0]['state']['backdropToneAbscissae'][0].update(kind='hint'),
                       lambda p:p['groups'][0]['state']['backdropToneAbscissae'][0].update(linearLuminance=.3)]:
            r=copy.deepcopy(report()); mutate(r['page'])
            with self.subTest(report=r), self.assertRaises(ValueError):
                A.validate_report(r,request(),endpoint())

    def test_current_requires_all_four_current_endpoint_bytes(self):
        import tempfile
        import hashlib
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp); slots={}
            for pose in ('active','receded'):
                for scheme in ('light','dark'):
                    name=f'{pose}.{scheme}'
                    raw='{"profileKey":"test","resolvedMaterialSha256":"'+ 'b'*16+'","patch":{}}'
                    (p/f'{name}.json').write_text(raw)
                    slots[name]=dict(path=f'{name}.json',sha256=hashlib.sha256(raw.encode()).hexdigest())
            doc=dict(kind='vitrea-candidate-material-document',schemaVersion=1,glassTintAmount=.25,
                     endpoints=slots,cssTierMappingSha256='c'*64)
            (p/'candidate.json').write_text(__import__('json').dumps(doc))
            pin=dict(path=str(p/'candidate.json'),sha256=A.sha(p/'candidate.json'))
            self.assertEqual(len(A.candidate_info(pin,.25)['endpoints']),4)
            with self.assertRaises(ValueError): A.candidate_info(pin,.25,current=True)
            del doc['endpoints']['receded.light']
            (p/'candidate.json').write_text(__import__('json').dumps(doc));pin['sha256']=A.sha(p/'candidate.json')
            with self.assertRaises(ValueError): A.candidate_info(pin,.25)

    def test_current_namespace_only_changes_profile_key(self):
        source=A.read_json(A.CAL/'profiles/apple-macos-27.0-1x-dark-standard-glass0.25-receded.json')
        derived=copy.deepcopy(source)
        derived['profileKey']=source['profileKey'].replace('glass0.25','glass0.250')
        A.validate_current_endpoint(derived,source,.25)
        for mutate in [lambda d:d.update(recordedBy='other'),
                       lambda d:d['patch'].update(lowEndStrength=1),
                       lambda d:d.update(profileKey=d['profileKey'].replace('-receded','')),
                       lambda d:d.update(profileKey=d['profileKey'].replace('0.250','0.500'))]:
            wrong=copy.deepcopy(derived);mutate(wrong)
            with self.assertRaises(ValueError): A.validate_current_endpoint(wrong,source,.25)

    def test_scratch_refuses_other_checkout_and_missing_explicit_scale(self):
        import tempfile
        import json
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/'.git').mkdir()
            with self.assertRaises(ValueError): A.external(root/'captures')
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/'manifest.json').write_text(json.dumps({'backgrounds':{'grey-004':'unscaled.png'}}))
            run={**request(),'fixtures':dict(path=str(root),manifestSha256=A.sha(root/'manifest.json'),backgrounds={})}
            with self.assertRaises(ValueError): A.fixture_info(run,A.scene_plan(run))

    def test_render_admission_refusal_precedes_any_scene_or_candidate_read(self):
        import sys
        import types
        from unittest.mock import patch
        def refuse(context, run, current=False):
            raise ValueError('central render admission refused')
        dispatcher=types.SimpleNamespace(require_context=lambda context:None,
                                         require_render_admission=refuse)
        run={'synthetic':'not a scene request'}
        context={'phase':'fit','batch':{'runs':[run]}}
        with patch.dict(sys.modules,{'w50_g1_dispatch':dispatcher}):
            with self.assertRaisesRegex(ValueError,'central render admission refused'):
                A._capture_run(context,run,current=False)

    def test_direct_call_cannot_launch(self):
        with self.assertRaises(ValueError): A.execute({})


if __name__=='__main__': unittest.main()
