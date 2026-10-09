"""Production-shaped canonical receipts; all documents and artifacts are disposable synthetic data."""
import copy
import io
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent


def source(path, name):
    module = types.ModuleType(name); module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


A = source(HERE/'analysis.py', 'synthetic_canonical_analysis')


class CanonicalInputsTests(unittest.TestCase):
    def fixture(self, *, renderer='css', abscissa='source', dpr=1, composite=False, scene_id=None):
        directory = self.enterContext(tempfile.TemporaryDirectory())
        repo = Path(directory).resolve(); output = repo/'output'; output.mkdir()
        profile = f'apple-macos-27.0-{dpr}x-dark-standard-glass0.25'
        sid = scene_id or ('photo__stack__rest' if composite else 'dark-solid__rrect-sm__inactive')
        candidate_pin = dict(path='gate0/candidate.json', sha256='a'*64)
        candidate_path = repo/candidate_pin['path']; candidate_path.parent.mkdir(); candidate_path.write_text('{}')
        run = dict(profile=profile, renderer=renderer, sceneSource='canonical', scenes=[sid], sets=['calibration'],
            candidate=candidate_pin, captureRoot=str(output/'captures'), matrixPath=str(output/'matrix.json'))
        scene = dict(id=sid, component='shape', state='rest' if composite else 'inactive', background='dark-solid')
        component = dict(kind='stack') if composite else dict(kind='rrect', size=[120, 44], radius=10)
        document = dict(canvas={'width':320, 'height':200}, profiles=[dict(key=profile, scenes='all')],
            components={'shape':component}, scenes=[scene], split={'calibration':[sid]}, tints={})
        scene_path = repo/'apps/reference-apple/scenes.json'; scene_path.parent.mkdir(parents=True)
        scene_path.write_text(json.dumps(document))
        self.enterContext(patch.object(A.M.A, 'ROOT', repo))
        if hasattr(A, 'C'):
            self.enterContext(patch.object(A.C, 'ROOT', repo))
            self.enterContext(patch.object(A.C, 'SCENES', scene_path))
        self.enterContext(patch.object(A, 'REPO', repo))
        endpoint = dict(profileKey='apple-macos-27.0-1x-dark-standard-glass0.250'+('' if composite else '-receded'),
            resolvedMaterialSha256='c'*16, patch={'backdropToneAbscissa':abscissa},
            source=dict(path='original/receded.json', sha256='b'*64),
            candidateEndpoint=dict(path='gate0/receded.json', sha256='d'*64))
        candidate = dict(document=candidate_pin, position=.25,
            endpoints={'active.dark':dict(endpoint, profileKey='apple-macos-27.0-1x-dark-standard-glass0.250',
                source=dict(path='original/active.json',sha256='e'*64),
                candidateEndpoint=dict(path='gate0/active.json',sha256='d'*64)), 'receded.dark':endpoint},
            originalDocumentPair={'active.dark':'e'*64, 'receded.dark':'b'*64})
        if composite: endpoint = candidate['endpoints']['active.dark']
        material = dict(profileKey=endpoint['profileKey'], resolvedMaterialSha256=endpoint['resolvedMaterialSha256'],
                        tuned=False, glassTintAmount=.25)
        state = dict(activeRenderer=renderer, health='ok', samplingBackend='gpu-texture' if renderer=='webgpu' else 'css-backdrop',
            materialDocument=copy.deepcopy(material), backdropToneAbscissae=[dict(surfaceId='s1', kind='silhouette',
                sampleCount=100, encodedLuminance=.1, linearLuminance=.2, color=[.2]*3)])
        group = dict(id='g1', configuredSource='texture', state=state,
                     backdropTone=dict(level=.010022825574869039, linearLuminance=.2, rgb=[.2]*3))
        bounds = dict(x=100, y=78, width=122 if renderer=='css' and abscissa=='source' else 120,
                      height=46 if renderer=='css' and abscissa=='source' else 44)
        surface = dict(nodeId='s1', groupId='g1', family='fixed-rounded-rect', radius=10, bounds=bounds)
        page = dict(sceneId=sid, materialMode='candidate', candidateDocument=dict(mode='candidate', declarationSha256='a'*12),
            colorScheme='dark', windowActivation='active' if composite else 'inactive', material=copy.deepcopy(material),
            requestedRenderer=renderer, canvas=document['canvas'], pixelSize=[320*dpr,200*dpr],
            devicePixelRatio=dpr, requestedScale=dpr, pressed=False, tint=None, transparentPage=False,
            accessibilityPolicy=dict(reducedTransparency=False, increasedContrast=False, forcedColors=False),
            requestedBackdropMode='texture', requestedBackdropLevel=None,
            background=dict(id='dark-solid', naturalWidth=320*dpr, naturalHeight=200*dpr),
            groups=[group], surfaces=[surface], problems=[])
        if composite:
            page['groups'].append(dict(group, id='g2', state=copy.deepcopy(state)))
            page['surfaces'].append(dict(surface, nodeId='s2', groupId='g2', bounds=None))
            for g in page['groups']:
                g.pop('backdropTone'); g['state'].pop('backdropToneAbscissae')
        web = dict(renderer=renderer, colorSpace='srgb', deterministic=True, repeatNoise=0,
            capturePath=f'candidateDocument={candidate_pin["path"]} declarationSha256={candidate_pin["sha256"][:12]}')
        row = dict(key=dict(profileKey=profile, sceneId=sid, web=web), fixtureSet='calibration')
        matrix = dict(schemaVersion=5, cells=[row]); Path(run['matrixPath']).write_text(json.dumps(matrix))
        folder = Path(run['captureRoot'])/profile/sid; folder.mkdir(parents=True)
        (folder/f'cell__{renderer}.json').write_text(json.dumps(web))
        (folder/f'report__{renderer}.json').write_text(json.dumps(dict(page=page, fallback=False, problems=[])))
        # An actual synthetic PNG, not captured pixels or an invented dimension witness.
        from PIL import Image
        stream = io.BytesIO(); Image.new('RGB', (320*dpr,200*dpr), (20,20,20)).save(stream, format='PNG')
        (folder/f'{sid}__{renderer}.png').write_bytes(stream.getvalue())
        artifacts = {name:dict(path=str(folder/filename), sha256=A.B.sha(folder/filename)) for name,filename in
            [('cell',f'cell__{renderer}.json'), ('report',f'report__{renderer}.json'), ('png',f'{sid}__{renderer}.png')]}
        artifacts['files'] = [dict(path=str(p), sha256=A.B.sha(p)) for p in sorted(folder.iterdir())]
        transport = []
        for filename in (f'census-{sid}.json',f'request-{sid}.json',f'exit-{sid}.json',f'compare-{sid}.log',
                         'request.json','native-request.json',f'native-admission-{sid}.json'):
            p = Path(run['captureRoot'])/filename; p.write_text('synthetic transport only\n')
            transport.append(dict(path=str(p), sha256=A.B.sha(p)))
        artifacts['transport'] = transport
        receipt = dict(profile=profile, renderer=renderer, scene=sid, sceneSource='canonical', lane='current',
            candidate=candidate_pin, endpoint=dict(path=str(repo/endpoint['candidateEndpoint']['path']), sha256='d'*64,
                profileKey=endpoint['profileKey'], resolvedMaterialSha256='c'*16, patch=endpoint['patch'],
                currentSource=dict(path=str(repo/endpoint['source']['path']), sha256=endpoint['source']['sha256'])),
            matrix=dict(path=run['matrixPath'], sha256=A.B.sha(run['matrixPath'])), row=row, artifacts=artifacts,
            coherenceStatus='NOT_APPLICABLE' if renderer=='webgpu' else 'UNMEASURED')
        member = dict(run=run, receipt=receipt, output=str(output), result={'sha256':'f'*64},
                      contract={'sha256':'1'*64}, claim={'sha256':'2'*64})
        return member, candidate, page, bounds

    def rewrite_report(self, member, page):
        pin = member['receipt']['artifacts']['report']; p = Path(pin['path'])
        p.write_text(json.dumps(dict(page=page, fallback=False, problems=[]))); pin['sha256'] = A.B.sha(p)
        for item in member['receipt']['artifacts']['files']:
            if item['path']==str(p): item['sha256']=pin['sha256']

    def test_css_source_receipt_omits_canvas_and_scale_and_keeps_actual_content_box(self):
        member, candidate, _, bounds = self.fixture()
        plan, spec, _, arguments, provenance = A.capture_inputs(member, candidate)
        self.assertEqual(plan['canvas'], {'width':320,'height':200})
        self.assertEqual(spec['scene'], member['receipt']['scene'])
        self.assertEqual(arguments[0]['id'], '|'.join(member['receipt'][k] for k in ('profile','renderer','scene')))
        self.assertEqual(arguments[0]['candidateSha256'], 'a'*64)
        self.assertAlmostEqual(arguments[0]['encodedLuminance'], .1)
        self.assertEqual(arguments[0]['linearLuminance'], .2)
        self.assertEqual(arguments[0]['rgb'], [.2]*3)
        self.assertEqual(arguments[0]['provenance']['surface']['bounds'], bounds)
        self.assertEqual(bounds, {'x':100,'y':78,'width':122,'height':46})
        self.assertEqual(arguments[0]['span'], 46)
        self.assertEqual(arguments[0]['provenance']['declaredSpan'], 44)
        self.assertEqual(arguments[0]['provenance']['actualSolveSpan'], 46)
        self.assertEqual(provenance['geometryDomain'], 'canonical-reported-bounds-not-native-mask-equivalence')
        self.assertEqual(provenance['originalDocumentPair'], candidate['originalDocumentPair'])
        self.assertEqual(provenance['scenesSha256'], A.B.sha(plan['scenesPath']))
        self.assertNotIn('geometry', spec)

    def test_gpu_source_and_silhouette_keep_independent_arguments_at_both_scales(self):
        for abscissa in ('source','silhouette'):
            for scale in (1,2):
                with self.subTest(abscissa=abscissa, scale=scale):
                    member, candidate, _, bounds = self.fixture(renderer='webgpu',abscissa=abscissa,dpr=scale)
                    argument = A.capture_inputs(member,candidate)[3][0]
                    self.assertEqual((argument['dpr'],argument['pose']), (scale,'receded'))
                    self.assertEqual(argument['span'], 44)
                    self.assertEqual(argument['provenance']['declaredSpan'], 44)
                    self.assertEqual(argument['provenance']['actualSolveSpan'], 44)
                    self.assertEqual(argument['linearLuminance'], .2)
                    self.assertEqual(argument['rgb'], [.2]*3)
                    self.assertEqual(argument['provenance']['surface']['bounds'], bounds)
                    self.assertEqual(argument['provenance']['kind'], abscissa)

    def test_silhouette_border_box_and_clear_scene_follow_measured_span_and_runtime_regular_variant(self):
        for renderer in ('css','webgpu'):
            with self.subTest(renderer=renderer):
                member,candidate,_,bounds = self.fixture(renderer=renderer,abscissa='silhouette',
                    scene_id='dark-solid__clear20__inactive')
                argument = A.capture_inputs(member,candidate)[3][0]
                self.assertEqual(bounds, {'x':100,'y':78,'width':120,'height':44})
                self.assertEqual(argument['span'],44)
                self.assertEqual(argument['provenance']['declaredSpan'],44)
                self.assertEqual(argument['provenance']['actualSolveSpan'],44)
                self.assertEqual(argument['variant'],'regular')
                self.assertEqual(argument['provenance']['variant'],'regular')
                self.assertIn('variantSource',argument['provenance'])

    def test_composite_artifact_only_has_no_imputed_argument_and_checks_all_groups(self):
        member, candidate, page, _ = self.fixture(composite=True)
        plan, spec, _, arguments, provenance = A.capture_inputs(member,candidate,argument_required=False)
        self.assertEqual(arguments, [])
        self.assertEqual(spec['component']['kind'], 'stack')
        self.assertEqual(len(provenance['reportedSurfaces']), 2)
        self.assertEqual(provenance['matrix'], member['receipt']['matrix'])
        self.assertEqual(provenance['artifacts'], member['receipt']['artifacts'])
        page['groups'][1]['state']['materialDocument']['resolvedMaterialSha256']='0'*16
        self.rewrite_report(member,page)
        with self.assertRaises(ValueError): A.capture_inputs(member,candidate,argument_required=False)

    def test_canonical_rejects_re_pinned_wrong_identity_and_argument_sources(self):
        for mutation in ('digest','scale','source','background','hint','pair','candidate','rgb','bounds','receipt'):
            with self.subTest(mutation=mutation):
                member,candidate,page,_ = self.fixture()
                if mutation=='digest': page['material']['resolvedMaterialSha256']='0'*16
                elif mutation=='scale': page['requestedScale']=2
                elif mutation=='source': page['groups'][0]['configuredSource']='dom'
                elif mutation=='background': page['background']['id']='other'
                elif mutation=='hint': page['requestedBackdropLevel']=.1
                elif mutation=='pair': member['receipt']['endpoint']['currentSource']['sha256']='0'*64
                elif mutation=='candidate': page['candidateDocument']['declarationSha256']='0'*12
                elif mutation=='rgb': page['groups'][0]['backdropTone']['rgb']=[.3]*3
                elif mutation=='bounds': page['surfaces'][0]['bounds']['width']=float('nan')
                else: member['receipt']['sceneSource']='w50'
                self.rewrite_report(member,page)
                with self.assertRaises(ValueError): A.capture_inputs(member,candidate)

    def test_artifact_only_transport_matrix_and_metadata_are_still_verified(self):
        for mutation in ('transport','files','matrix','metadata','population'):
            with self.subTest(mutation=mutation):
                member,candidate,page,_ = self.fixture(composite=True)
                if mutation in ('transport','files'):
                    Path(member['receipt']['artifacts'][mutation][0]['path']).write_text('changed')
                elif mutation=='matrix': Path(member['receipt']['matrix']['path']).write_text('{}')
                elif mutation=='metadata': member['receipt']['row']['key']['web']['repeatNoise']=.5
                else:
                    page['surfaces'].pop(); self.rewrite_report(member,page)
                with self.assertRaises(ValueError): A.capture_inputs(member,candidate,argument_required=False)

    def test_canonical_source_bounds_do_not_relax_newbed_native_geometry(self):
        member,candidate,page,_ = self.fixture()
        repo = Path(member['output']).parent; g0 = repo/'synthetic-g0'; (g0/'bed').mkdir(parents=True)
        scene = dict(id=member['receipt']['scene'],state='inactive',background='dark-solid',component='shape')
        document = dict(canvas={'width':512,'height':384},scenes=[scene],split={'calibration':[scene['id']]},
                        components={'shape':dict(kind='rrect',size=[64,44],radius=10)})
        (g0/'bed/scenes-w50.json').write_text(json.dumps(document))
        run = dict(member['run'],sceneSource='w50')
        page.update(canvas=document['canvas'],pixelSize=[512,384])
        page['background'].update(naturalWidth=512,naturalHeight=384)
        page['surfaces'][0]['bounds'].update(x=224,y=170)
        with patch.object(A.M.A,'G0',g0), self.assertRaisesRegex(ValueError,'placement'):
            A.M.A.validate_report({'page':page},run,candidate['endpoints']['receded.dark'],abscissa='source',phase='current')

    def test_missing_required_argument_refuses_instead_of_becoming_artifact_only(self):
        member,candidate,page,_ = self.fixture()
        page['groups'][0].pop('backdropTone'); self.rewrite_report(member,page)
        with self.assertRaisesRegex(ValueError,'UNMEASURED'): A.capture_inputs(member,candidate)


class OriginalRouteTests(unittest.TestCase):
    def fixture(self):
        members,rows,required = [],[],{}
        for source_name,count in (('w50',672),('canonical',127)):
            for n in range(count):
                triple = dict(profile='original-profile',renderer='css',scene=f'{source_name}-{n}')
                member = dict(run={'sceneSource':source_name},receipt=triple)
                members.append(member)
                artifact_only = source_name=='canonical' and n>=115
                row = dict(triple,statistic='T1-low' if artifact_only else 'low-end-path-level',
                    role='gate' if source_name=='canonical' else 'calibration',currentEvidence=None if artifact_only else {'sha256':'a'*64},
                    currentMetadata=None if artifact_only else {'sha256':'b'*64})
                rows.append(row)
                if not artifact_only: required['|'.join(triple[k] for k in A.KEY[:3])]=row
        return members,rows,required

    def test_all_original_members_route_115_arguments_and_twelve_missing_t1_without_imputation(self):
        members,rows,required = self.fixture(); original = copy.deepcopy(rows)
        routes = A.current_routes(members,rows,required)
        canonical = [routes['|'.join(m['receipt'][k] for k in A.KEY[:3])] for m in members if m['run']['sceneSource']=='canonical']
        self.assertEqual(sum(r['requiredArgument'] for r in canonical),115)
        missing = [r for r in canonical if not r['requiredArgument']]
        self.assertEqual(len(missing),12)
        self.assertEqual([r['originalReferences'] for r in missing], [[row] for row in rows[-12:]])
        self.assertEqual(rows,original)
        self.assertEqual(set(routes), {'|'.join(m['receipt'][k] for k in A.KEY[:3]) for m in members})

    def test_population_cannot_substitute_an_extra_id_or_relabel_required_argument(self):
        for mutation in ('extra','duplicate','missing','resolved','required'):
            with self.subTest(mutation=mutation):
                members,rows,required = self.fixture()
                if mutation=='extra': members[-1]['receipt']['scene']='unregistered'
                elif mutation=='duplicate': members[-1]=copy.deepcopy(members[-2])
                elif mutation=='missing': members.pop()
                elif mutation=='resolved': rows[-1]['currentEvidence']={'sha256':'f'*64}; rows[-1]['currentMetadata']={'sha256':'f'*64}
                else: required.pop(next(k for k in required if '|canonical-' in k))
                with self.assertRaises(ValueError): A.current_routes(members,rows,required)


if __name__=='__main__': unittest.main()
