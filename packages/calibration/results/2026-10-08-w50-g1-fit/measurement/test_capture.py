"""Synthetic-only measurement tests. No actual native report/export or web capture is opened."""
import base64
import copy
import gzip
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
FIT = HERE.parent
ROOT = HERE.parents[4]
PROFILE = 'apple-macos-27.0-1x-dark-standard-glass0.25'
SCENE = 'cell-impulse-sparse-s096__rest'
CANVAS = {'width': 512, 'height': 384}


def source(path, name):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


R = source(FIT/'native/reader.py', 'w50_measurement_native_test')
A = source(FIT/'web/adapter.py', 'w50_measurement_web_test')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def png(rgb):
    stream = io.BytesIO()
    Image.fromarray(rgb).save(stream, format='PNG')
    return stream.getvalue()


def write_pin(path, value, *, compressed=False, repo=False):
    raw = value if isinstance(value, bytes) else (json.dumps(value, allow_nan=False)+'\n').encode()
    if compressed:
        raw = gzip.compress(raw, mtime=0)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return dict(path=str(path.relative_to(ROOT)) if repo else str(path), sha256=sha(raw))


def native_cell(*, empty=False, role='calibration', scale=1):
    shape = (384*scale, 512*scale, 3)
    rgb = np.full(shape, 70, dtype=np.uint8)
    bg = np.zeros(shape, dtype=np.uint8)
    bg[190*scale:194*scale, 254*scale:258*scale] = 255
    component = {'kind': 'rrect', 'size': [168, 96], 'radius': 20.4}
    analytical = R.S.analytical_masks(component, CANVAS, scale, shape[:2], background=bg, impulse=True)
    silhouette = np.zeros(shape[:2], dtype=bool)
    if not empty:
        silhouette[180*scale, 200*scale:202*scale] = True
    runs = []
    profile = PROFILE.replace('-1x-', f'-{scale}x-')
    for run in (1, 2, 3):
        readings = R.S.read_frame(rgb, bg, component, CANVAS, scale,
            impulse=True, include_structured=True, silhouette_mask=silhouette)
        runs.append(dict(run=run, dependency=profile+'/ref-impulse-sparse__rest',
                         evidence={'sha256': str(run)*64}, readings=readings))
    cell = dict(id=profile+'/'+SCENE, profile=profile, scene=SCENE, family='structured',
                role=role, pose='active', scale=scale, span=96, glass=.25,
                background='impulse-sparse', reference=profile+'/ref-impulse-sparse__rest',
                passName='synthetic', runs=runs, statistics=R.aggregate_runs(runs, reported=empty))
    return cell, analytical, bg


class CoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = source(HERE/'capture.py', 'w50_measurement_core_test')

    def test_keeps_channel_medians_far_luma_and_native_full_silhouette_t1_separate(self):
        for scale in (1, 2):
            cell, masks, _ = native_cell(scale=scale)
            web = np.full((384*scale, 512*scale, 3), [10, 20, 30], dtype=np.uint8)
            web[188*scale:196*scale, 252*scale:260*scale] = [30, 40, 50]
            web[180*scale, 200*scale] = 0
            web[180*scale, 200*scale+1:202*scale] = 255
            result = self.m.evaluate_native_supports(web, cell, masks, renderer='webgpu')
            stats = result['statistics']
            self.assertEqual(stats['deep8-channel-median']['value'], [10, 20, 30])
            self.assertEqual(stats['central8-channel-median']['value'], [30, 40, 50])
            # Population SD on TWO original native pixels at 1x, FOUR at 2x (one black).
            expected_sd = .5 if scale == 1 else np.sqrt(3/16)
            self.assertAlmostEqual(stats['T1-full-silhouette']['value'], expected_sd)
            self.assertEqual(stats['T1-full-silhouette']['units'], 'linear-luma')
            self.assertEqual(stats['T1-full-silhouette']['nativeRepeat'],
                             cell['statistics']['T1-full-silhouette']['repeat'])
            for run in result['runs']:
                self.assertEqual(run['readings']['supports']['full-silhouette']['pixels'], 2*scale)
            self.assertNotEqual(stats['deep8-far24-luma-mean']['value'],
                                stats['deep8-far24-luma-median']['value'])
            self.assertAlmostEqual(stats['deep8-far24-luma-median']['value'], 18.596)
            self.assertNotIn('passes', result)
            self.assertEqual(result['status'], 'MEASURED')

    def test_scalar_aggregation_is_median_of_native_run_support_reads_not_pooling(self):
        cell, masks, _ = native_cell()
        web = np.zeros((384, 512, 3), dtype=np.uint8)
        web[180, 200:203] = [[10]*3, [30]*3, [20]*3]
        for run, index in zip(cell['runs'], (200, 201, 202)):
            mask = np.zeros(web.shape[:2], dtype=bool); mask[180, index] = True
            run['readings']['supports']['full-silhouette'] = R.S.read_support(web, mask, retain_mask=True)
            run['readings']['statistics']['T1-full-silhouette']['value'] = 0.
        cell['statistics'] = R.aggregate_runs(cell['runs'])
        result = self.m.evaluate_native_supports(web, cell, masks, renderer='css')
        self.assertEqual(result['statistics']['T1-full-silhouette']['value'], 0.)
        self.assertEqual([r['readings']['supports']['full-silhouette']['rgbMedianCodes']
                          for r in result['runs']], [[10]*3, [30]*3, [20]*3])
        self.assertEqual(result['statistics']['T1-full-silhouette']['aggregation'],
                         'coordinatewise-median-of-three-run-statistics')

    def test_optional_empty_native_t1_is_null_with_exact_three_run_witnesses(self):
        for role in ('validation', 'blind'):
            cell, masks, _ = native_cell(empty=True, role=role)
            result = self.m.evaluate_native_supports(np.full((384, 512, 3), 255, dtype=np.uint8),
                                                     cell, masks, renderer='webgpu')
            item = result['statistics']['T1-full-silhouette']
            self.assertEqual(item['status'], 'UNMEASURED_EMPTY_SUPPORT')
            self.assertIsNone(item['value'])
            self.assertIsNone(item['B'])
            self.assertEqual(item['runValues'], [None]*3)
            self.assertEqual([w['pixels'] for w in item['nativeSupportWitnesses']], [0]*3)
            self.assertEqual([w['maskPackedBitsSha256'] for w in item['nativeSupportWitnesses']],
                             [sha(bytes(384*512//8))]*3)
            self.assertEqual(result['statistics']['deep8-channel-median']['value'], [255]*3)

    def test_required_empty_t1_cannot_be_relabelled_as_optional(self):
        cell, masks, _ = native_cell(empty=True)
        cell['statistics']['T1-full-silhouette']['required'] = True
        with self.assertRaisesRegex(ValueError, 'required'):
            self.m.evaluate_native_supports(np.zeros((384, 512, 3), dtype=np.uint8), cell, masks, renderer='css')

    def test_changed_native_masks_counts_hashes_and_missing_repetitions_refuse(self):
        for change in ('mask', 'count', 'packed', 'missing', 'wrong-statistic', 'dimensions'):
            cell, masks, _ = native_cell()
            web = np.zeros((384, 512, 3), dtype=np.uint8)
            if change == 'mask':
                masks['deep8'][0, 0] = True
            elif change == 'count':
                cell['runs'][0]['readings']['supports']['center8']['pixels'] += 1
            elif change == 'packed':
                cell['runs'][0]['readings']['supports']['full-silhouette']['maskPackedBitsBase64'] = base64.b64encode(bytes(384*512//8)).decode()
            elif change == 'missing':
                cell['runs'].pop()
            elif change == 'wrong-statistic':
                cell['statistics']['central8-channel-median']['units'] = 'linear-luma'
            else:
                web = web[:-1]
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.m.evaluate_native_supports(web, cell, masks, renderer='webgpu')

    def test_source_probe_exercises_only_synthetic_numerical_paths(self):
        with patch.object(Path, 'glob', side_effect=AssertionError('discovery')):
            result = self.m.source_probe()
        self.assertEqual(result['status'], 'SOURCE_ONLY')


class CaptureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = source(HERE/'capture.py', 'w50_measurement_capture_test')

    def setUp(self):
        self.repo_tmp = tempfile.TemporaryDirectory(dir=HERE)
        self.scratch_tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.repo_tmp.cleanup); self.addCleanup(self.scratch_tmp.cleanup)
        self.repo = Path(self.repo_tmp.name).resolve(); self.scratch = Path(self.scratch_tmp.name).resolve()
        scenes_path = A.G0/'bed/scenes-w50.json'
        self.scenes = dict(path=str(scenes_path.relative_to(ROOT)), sha256=A.sha(scenes_path))
        self.doc = json.loads(scenes_path.read_bytes())
        self.cell, self.masks, bg = native_cell()
        dep = dict(path=f'synthetic/run-1/{PROFILE}/ref-impulse-sparse__rest.png',
                   sha256=sha(png(bg)), roles=['calibration'], kind='frame',
                   cell=self.cell['reference'], run=1)
        self.export = self.scratch/'native-calibration'
        write_pin(self.export/dep['path'], png(bg))
        index_pin = write_pin(self.export/'index.json', dict(schema='w50-role-archive-1', files=[dep]))
        report = dict(schema='w50-native-role-read-1', role='calibration', indexSha256=index_pin['sha256'],
            declarationSha256='1'*64, canvas=CANVAS, ready=True, stops=[],
            supportDefinitions=R.S.SUPPORT_DEFINITIONS,
            repeatRule=dict(runs=3,maxRequiredSpreadCodes=1,barFloorCodes=.5),
            reportedReferenceKeys=[], dependencies=[dict(id=self.cell['reference'],evidence=dep)],
            cells=[self.cell])
        self.native_report = write_pin(self.repo/'native-calibration.json.gz', report, compressed=True, repo=True)
        self.native_batch = write_pin(self.repo/'native-batch.json', dict(schema='w50-native-read-batch-1',
            exports=[dict(role='calibration',root=str(self.export),indexSha256=index_pin['sha256']),
                     dict(role='validation',root=str(self.scratch/'other'),indexSha256='2'*64)],
            inputs=dict(scenes=self.scenes,declaration={'sha256':'1'*64})), repo=True)
        self.endpoint = dict(profileKey='apple-macos-27.0-1x-dark-standard-glass0.250',
                             resolvedMaterialSha256='b'*16, patch={'backdropToneAbscissa':'silhouette'})
        slots = {}
        for pose in ('active','receded'):
            for scheme in ('light','dark'):
                key = f'{pose}.{scheme}'
                value = {**self.endpoint, 'profileKey':f'apple-macos-27.0-1x-{scheme}-standard-glass0.250'+
                         ('-receded' if pose=='receded' else '')}
                slots[key] = write_pin(self.repo/f'{key}.json', value)
        self.candidate = write_pin(self.repo/'candidate.json', dict(kind='vitrea-candidate-material-document',
            schemaVersion=1, glassTintAmount=.25, endpoints=slots, cssTierMappingSha256='c'*64), repo=True)
        self.run = dict(id='test', profile=PROFILE,renderer='webgpu',sceneSource='w50',scenes=[SCENE],
                        sets=['calibration'],candidate=self.candidate,captureRoot=str(self.scratch/'captures'))
        plan = A.scene_plan(self.run)['scenes'][0]
        material = dict(profileKey=self.endpoint['profileKey'],resolvedMaterialSha256='b'*16,
                        glassTintAmount=.25,tuned=False)
        page = dict(sceneId=SCENE, requestedRenderer='webgpu',canvas=CANVAS,pixelSize=[512,384],
            devicePixelRatio=1,requestedScale=1,colorScheme='dark',materialMode='candidate',
            windowActivation='active', material=material,
            candidateDocument=dict(mode='candidate',declarationSha256=self.candidate['sha256'][:12]),
            requestedBackdropMode='texture',requestedBackdropLevel=None,
            background=dict(id='impulse-sparse',naturalWidth=512,naturalHeight=384),
            accessibilityPolicy=dict(reducedTransparency=False,increasedContrast=False,forcedColors=False),
            problems=[],surfaces=[dict(nodeId='s',groupId='g',family='fixed-rounded-rect',
                                      radius=20.4,bounds=plan['geometry'])],
            groups=[dict(id='g',backdropTone=dict(level=.010022825574869039,
                linearLuminance=.2,rgb=[.2]*3),state=dict(activeRenderer='webgpu',samplingBackend='gpu-texture',
                materialDocument=material,health='ok',backdropToneAbscissae=[dict(surfaceId='s',kind='silhouette',
                sampleCount=10,encodedLuminance=.1,linearLuminance=.2,color=[.2]*3)]))])
        folder = self.scratch/'captures'/SCENE
        self.artifacts = dict(
            png=write_pin(folder/f'{SCENE}__webgpu.png',png(np.full((384,512,3),[10,20,30],dtype=np.uint8))),
            report=write_pin(folder/'report__webgpu.json',dict(fallback=None,problems=[],page=page)),
            cell=write_pin(folder/'cell__webgpu.json',dict(renderer='webgpu',colorSpace='srgb',deterministic=True,
                repeatNoise=0,capturePath=f'declarationSha256={self.candidate["sha256"][:12]}')))
        self.receipt = dict(profile=PROFILE,renderer='webgpu',scene=SCENE,candidate=self.candidate,
            lane='candidate',sceneSource='w50',canvas=CANVAS,dpr=1,artifacts=self.artifacts,
            arguments=A.validate_report(dict(fallback=None,problems=[],page=page),self.run,self.endpoint),
            background=dict(key='impulse-sparse@1x',path=str(self.export/dep['path']),sha256=dep['sha256']))
        one = write_pin(self.repo/'one.json',dict(sources=[self.scenes]),repo=True)
        two = write_pin(self.repo/'two.json',dict(sources=[self.scenes]),repo=True)
        self.context = dict(repo=str(ROOT),phase='fit',output=str(self.scratch),executionRoot=str(self.repo/'root.json'),
            inputs=[self.native_report,self.native_batch],baselineDocuments=[],
            batch=dict(phase='fit',runs=[self.run],cohort=[self.candidate]))
        self.dispatcher = types.SimpleNamespace(require_context=lambda c: None,
            require_render_admission=lambda c,r,current=False: None,
            sealed=lambda p: {'partOne':one,'partTwo':two},
            checked=lambda repo,p: Path(repo)/p['path'])
        self.module_patch = patch.dict(sys.modules,{'w50_g1_dispatch':self.dispatcher})
        self.module_patch.start(); self.addCleanup(self.module_patch.stop)

    def measure(self):
        return self.m.measure_capture(self.context,self.native_report,self.receipt,self.scenes,
                                      native_batch_pin=self.native_batch)

    def test_pinned_capture_returns_native_mask_stats_and_independent_actual_report_arguments(self):
        result = self.measure()
        self.assertEqual(result['statistics']['deep8-channel-median']['value'],[10,20,30])
        self.assertEqual(result['arguments'][0]['encodedLuminance'],.1)
        self.assertEqual(result['arguments'][0]['linearLuminance'],.2)
        self.assertEqual(result['arguments'][0]['rgb'],[.2]*3)
        self.assertEqual(result['evidence']['nativeRead'],self.native_report)
        self.assertEqual(result['evidence']['capture'],self.artifacts['png'])
        self.assertEqual(result['evidence']['nativeDependency']['cell'],self.cell['reference'])
        self.assertNotIn('PASS',result.values())

    def test_far24_uses_original_no_glass_dots_not_web_detected_bright_pixels(self):
        web=np.zeros((384,512,3),dtype=np.uint8)
        web[180:184,200:204]=255
        self.artifacts['png'].update(write_pin(Path(self.artifacts['png']['path']),png(web)))
        result=self.measure()
        far=result['statistics']['deep8-far24-luma-mean']
        self.assertGreater(far['value'],0)
        self.assertEqual(far['nativeSupportWitnesses'][0]['maskPackedBitsSha256'],
                         self.cell['runs'][0]['readings']['supports']['deep8_far24']['maskPackedBitsSha256'])
        self.assertLess(far['nativeSupportWitnesses'][0]['pixels'],
                        result['statistics']['deep8-channel-median']['nativeSupportWitnesses'][0]['pixels'])

    def test_cached_receipt_arguments_cannot_override_the_pinned_page_report(self):
        self.receipt['arguments'][0]['encodedLuminance']=.9
        self.receipt['arguments'][0]['linearLuminance']=.9
        self.receipt['arguments'][0]['rgb']=[.9]*3
        argument=self.measure()['arguments'][0]
        self.assertEqual(argument['encodedLuminance'],.1)
        self.assertEqual(argument['linearLuminance'],.2)
        self.assertEqual(argument['rgb'],[.2]*3)

    def test_source_arguments_are_not_derived_from_web_pixels_or_decoded_encoded_mean(self):
        endpoint_path = self.repo/'active.dark.json'
        endpoint = json.loads(endpoint_path.read_bytes()); endpoint['patch']['backdropToneAbscissa']='source'
        pin = write_pin(endpoint_path,endpoint)
        candidate_path = self.repo/'candidate.json'
        candidate = json.loads(candidate_path.read_bytes());candidate['endpoints']['active.dark']=pin
        self.candidate.update(write_pin(candidate_path,candidate,repo=True))
        page = json.loads(Path(self.artifacts['report']['path']).read_bytes())
        page['page']['candidateDocument']['declarationSha256']=self.candidate['sha256'][:12]
        self.artifacts['report'].update(write_pin(Path(self.artifacts['report']['path']),page))
        metadata = dict(renderer='webgpu',colorSpace='srgb',deterministic=True,repeatNoise=0,
                        capturePath=f'declarationSha256={self.candidate["sha256"][:12]}')
        self.artifacts['cell'].update(write_pin(Path(self.artifacts['cell']['path']),metadata))
        result = self.measure()
        self.assertAlmostEqual(result['arguments'][0]['encodedLuminance'],.1)
        self.assertEqual(result['arguments'][0]['linearLuminance'],.2)
        self.assertEqual(result['arguments'][0]['rgb'],[.2]*3)
        self.assertEqual(result['arguments'][0]['provenance']['kind'],'source')

    def test_direct_context_refusal_happens_before_any_input_or_png_read(self):
        self.dispatcher.require_context=lambda c: (_ for _ in ()).throw(ValueError('no capability'))
        with patch.object(Path,'read_bytes',side_effect=AssertionError('input read')):
            with self.assertRaisesRegex(ValueError,'capability'): self.measure()

    def test_wrong_profile_scene_tier_scale_candidate_or_pose_refuses_before_pixel_decode(self):
        changes = [('profile',PROFILE.replace('0.25','0.5')),('scene','foreign'),('renderer','css'),
                   ('dpr',2),('canvas',{'width':320,'height':200}),('candidate',{'path':'other','sha256':'f'*64})]
        for key,value in changes:
            old = self.receipt[key]; self.receipt[key]=value
            with self.subTest(key=key),patch.object(self.m.R.S,'decode_png',side_effect=AssertionError('decode')):
                with self.assertRaises(ValueError): self.measure()
            self.receipt[key]=old
        page = json.loads(Path(self.artifacts['report']['path']).read_bytes())
        page['page']['windowActivation']='inactive'
        self.artifacts['report'].update(write_pin(Path(self.artifacts['report']['path']),page))
        with patch.object(self.m.R.S,'decode_png',side_effect=AssertionError('decode')):
            with self.assertRaises(ValueError): self.measure()

    def test_changed_png_report_native_report_dependency_and_unregistered_pins_refuse(self):
        for name in ('png','report','native','dependency','unregistered'):
            with self.subTest(name=name):
                if name in self.artifacts:
                    path=Path(self.artifacts[name]['path']);old=path.read_bytes();path.write_bytes(old+b'changed')
                elif name=='native':
                    path=ROOT/self.native_report['path'];old=path.read_bytes();path.write_bytes(old+b'changed')
                elif name=='dependency':
                    path=next(self.export.rglob('*.png'));old=path.read_bytes();path.write_bytes(old+b'changed')
                else:
                    old=self.context['inputs'];self.context['inputs']=[]
                with patch.object(self.m.R.S,'decode_png',side_effect=AssertionError('decode')):
                    with self.assertRaises(ValueError): self.measure()
                if name=='unregistered': self.context['inputs']=old
                else: path.write_bytes(old)

    def test_blind_io_is_refused_even_if_caller_puts_blind_report_in_inputs(self):
        path=ROOT/self.native_report['path'];report=json.loads(gzip.decompress(path.read_bytes()))
        report['role']='blind';report['cells'][0]['role']='blind'
        self.native_report.update(write_pin(path,report,compressed=True,repo=True))
        with patch.object(self.m.R.S,'decode_png',side_effect=AssertionError('blind decode')):
            with self.assertRaisesRegex(ValueError,'blind|exposed'): self.measure()

    def test_actual_png_dimensions_are_checked_after_hash_verification(self):
        self.artifacts['png'].update(write_pin(Path(self.artifacts['png']['path']),
                                               png(np.zeros((384,511,3),dtype=np.uint8))))
        with self.assertRaisesRegex(ValueError,'dimensions'): self.measure()


if __name__ == '__main__':
    unittest.main()
