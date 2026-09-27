"""Synthetic assembly regressions; existing native observations are never reopened."""
from copy import deepcopy
import gzip
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('body_assembly',Path(__file__).with_name('assemble.py'))
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)


class AssemblyTests(unittest.TestCase):
    def test_stream_decodes_complete_cells_and_rejects_duplicates_truncation_trailing(self):
        with tempfile.TemporaryDirectory() as name:
            path=Path(name)/'scores.json.gz'
            def write(text):path.write_bytes(gzip.compress(text.encode(),mtime=0))
            write('{"one":{"value":[1,2,3]},"two":true}')
            self.assertEqual(list(a.entries(path,chunk_size=3)),[('one',{'value':[1,2,3]}),('two',True)])
            for text in ('{"one":1,"one":2}','{"one":{"x":1,"x":2}}','{"one":1','{} trailing',
                         '{"one":NaN}','[]'):
                write(text)
                with self.subTest(text=text),self.assertRaises(ValueError):list(a.entries(path,chunk_size=3))

    def test_stream_scalar_tokens_may_cross_chunk_boundary(self):
        with tempfile.TemporaryDirectory() as name:
            path=Path(name)/'scores.json';path.write_text('{"integer":123456789,"exponent":1.25e-12}')
            self.assertEqual(dict(a.entries(path,chunk_size=3)),{'integer':123456789,'exponent':1.25e-12})

    def test_invalid_early_value_stops_before_consuming_stream(self):
        class TrackingStream(io.StringIO):
            consumed=0
            def read(self,size=-1):
                result=super().read(size);self.consumed+=len(result);return result
        text='{"bad":!'+('x'*4096)+'}'
        for chunk in (1,17,8192):
            stream=TrackingStream(text)
            with self.subTest(chunk=chunk),patch.object(a,'open',return_value=stream,create=True):
                with self.assertRaisesRegex(ValueError,'value.*limit'):
                    list(a.entries('synthetic.json',chunk_size=chunk,max_value_chars=64))
                self.assertLessEqual(stream.consumed,80)

    def test_value_limit_is_characters_inclusive_and_not_whole_document(self):
        with tempfile.TemporaryDirectory() as name:
            path=Path(name)/'scores.json'
            # The quotes count, but UTF-8 byte width and inter-value whitespace do not.
            for text,expected in [(' { "x" : "éééé" , "y" : "界界界界" } ',
                                   {'x':'éééé','y':'界界界界'}),
                                  ('{"x":123456,"y":1.2e-3}',{'x':123456,'y':1.2e-3})]:
                path.write_text(text)
                for chunk in (1,6,100):
                    with self.subTest(text=text,chunk=chunk):
                        self.assertEqual(dict(a.entries(path,chunk_size=chunk,max_value_chars=6)),expected)
            for text in ('{"x":"ééééé"}','{"x":1234567}','{"x":[1,  2]}',
                         '{"toolong":0}'):
                path.write_text(text)
                with self.subTest(text=text),self.assertRaisesRegex(ValueError,'value.*limit'):
                    list(a.entries(path,chunk_size=100,max_value_chars=6))

    def history_fixture(self,root):
        exposure=Path(__file__).resolve().parents[1]
        for name,path in [('bridge.py',exposure/'transition/bridge.py'),
                          ('test_bridge.py',exposure/'transition/test_bridge.py'),
                          ('runner.py',exposure/'runner.py')]:
            (root/name).write_bytes(path.read_bytes())
        (root/'source.py').write_text('retained scorer source\n')
        for name in ('predictions.json','parameters.json','raw.json.gz','admission.json.gz'):
            (root/name).write_bytes(('original '+name).encode())
        sources={'runner.py':'02ed44215ca4f273eb698ab9f514173f2c6cbfb89d09b6a12c837ffee9b4aa96',
                 'source.py':a.sha(root/'source.py')}
        witnesses={}
        for name in ('provenance.json','numerical-summary.json','rendered-summary.json'):
            (root/name).write_text(json.dumps({'sources':sources}))
            witnesses[name]={'sha256':a.sha(root/name),'count':2,'changed':['runner.py']}
        capture=root/'capture';capture.mkdir()
        (capture/'pixels.png').write_bytes(b'synthetic capture')
        (capture/'seal.json').write_text(json.dumps({'sources':list(sources),'inputs':sources}))
        (capture/'frozen.json').write_text(json.dumps({'sealSha256':a.sha(capture/'seal.json'),
            'files':{'capture/pixels.png':a.sha(capture/'pixels.png')}}))
        reading={'oldRunner':{'sha256':sources['runner.py']},'newRunner':{'sha256':a.sha(root/'runner.py')},
            'historicalSourceWitnesses':witnesses,
            'bridgeSources':{name:a.sha(root/name) for name in ('bridge.py','test_bridge.py')},
            'retainedArtifacts':{name:a.sha(root/name) for name in
                ('predictions.json','parameters.json','raw.json.gz','admission.json.gz')},
            'captureFrozen':{'path':'capture/frozen.json','sha256':a.sha(capture/'frozen.json'),'files':1},
            'captureSourceWitness':{'count':2,'changed':['runner.py']}}
        return reading

    def history(self,root,reading):
        return a.historical_inputs(root,reading,root/'bridge.py',root/'runner.py',root/'capture')

    def test_history_accepts_only_guard_transition_and_binds_complete_frontier(self):
        with tempfile.TemporaryDirectory() as name:
            root=Path(name);reading=self.history_fixture(root)
            bridge,paths=self.history(root,reading)
            required={'bridge.py','test_bridge.py','runner.py','source.py','provenance.json',
                      'numerical-summary.json','rendered-summary.json','predictions.json',
                      'parameters.json','raw.json.gz','admission.json.gz',
                      'capture/frozen.json','capture/seal.json','capture/pixels.png'}
            self.assertEqual({str(p.relative_to(root)) for p in paths},required)
            pins={str(p.relative_to(root)):a.sha(p) for p in paths}
            (root/'test_bridge.py').write_text('changed after initial validation')
            with self.assertRaisesRegex(ValueError,'historical artifact changed'):
                bridge.check_artifacts(root,pins)

    def test_history_rejects_modified_retained_evidence_even_if_currently_pinned(self):
        for filename in ('predictions.json','parameters.json','raw.json.gz','admission.json.gz',
                         'provenance.json','numerical-summary.json','rendered-summary.json',
                         'capture/frozen.json','capture/seal.json','capture/pixels.png'):
            with self.subTest(filename=filename),tempfile.TemporaryDirectory() as name:
                root=Path(name);reading=self.history_fixture(root)
                path=root/filename;path.write_bytes(path.read_bytes()+b' ')
                # A new present-day hash cannot replace the bridge's historical pin.
                self.assertTrue(a.sha(path))
                with self.assertRaises(ValueError):self.history(root,reading)

    def test_history_rejects_helper_before_import_and_binds_actual_bridge_test(self):
        for filename in ('bridge.py','test_bridge.py'):
            with self.subTest(filename=filename),tempfile.TemporaryDirectory() as name:
                root=Path(name);reading=self.history_fixture(root)
                (root/filename).write_text('raise AssertionError("unverified helper executed")')
                with self.assertRaisesRegex(ValueError,'bridge source'):
                    self.history(root,reading)

    def test_history_revalidates_document_sources_and_exact_runner_allowance(self):
        for change in ('source','runner','old-pin','new-pin','missing-helper'):
            with self.subTest(change=change),tempfile.TemporaryDirectory() as name:
                root=Path(name);reading=self.history_fixture(root)
                if change=='source':(root/'source.py').write_text('modified scorer')
                elif change=='runner':(root/'runner.py').write_text('modified runner')
                elif change=='old-pin':reading['oldRunner']['sha256']='not the historical runner'
                elif change=='new-pin':reading['newRunner']['sha256']='not the reviewed runner'
                else:del reading['bridgeSources']['test_bridge.py']
                with self.assertRaises(ValueError):self.history(root,reading)

    def test_transition_reading_cannot_be_resealed_to_bless_changed_history(self):
        original=Path(__file__).resolve().parents[1]/'transition/reading-1.json'
        with tempfile.TemporaryDirectory() as name:
            path=Path(name)/'reading.json';path.write_bytes(original.read_bytes())
            self.assertEqual(a.load_transition(path),json.loads(original.read_text()))
            reading=json.loads(path.read_text());reading['retainedArtifacts']={}
            path.write_text(json.dumps(reading))
            with self.assertRaisesRegex(ValueError,'transition reading'):
                a.load_transition(path)

    def test_reducer_preserves_deep_repeats_rails_and_unclaimed_status(self):
        raw={'status':'UNMEASURED','reason':'censored','passes':None,'constraintsPass':True,
             'diagnostic':'rendered structured deep','vetoPass':True,'deep':[{'member':0,'score':{
                 'pixels':[4]*7,'survives':True,'heldoutCoverage':False,
                 'median':{'failed':[False]*3,'railChannels':[True,False,False]},
                 'runs':[{'failed':[False]*3,'railChannels':[True,False,False]} for _ in range(7)]}}],
             'stateMembership':['s']*7,'populationDeficientVetoBins':0,
             'rawRendered':{'huge':[1,2]},'interiorTransfer':[{'huge':True}],
             'veto':[{'member':0,'part':'deep','score':{'passes':True,'status':'measured','pixels':4,
                'median':{'vetoRGB':[False]*3},'runs':[{'vetoRGB':[False]*3} for _ in range(7)]}}]}
        reduced=a.compact('rendered',raw)
        self.assertEqual(reduced['deep'],raw['deep']);self.assertEqual(reduced['stateMembership'],['s']*7)
        self.assertIsNone(reduced['passes']);self.assertTrue(reduced['constraintsPass'])
        self.assertNotIn('rawRendered',reduced);self.assertNotIn('veto',reduced)
        for mutator in (lambda r:r['deep'][0]['score']['runs'][0]['failed'].__setitem__(0,True),
                        lambda r:r.__setitem__('status','measured'),
                        lambda r:r['veto'][0]['score']['runs'][0]['vetoRGB'].__setitem__(1,True),
                        lambda r:r.__setitem__('vetoPass',False)):
            changed=deepcopy(raw);mutator(changed)
            with self.assertRaises(ValueError):a.compact('rendered',changed)

    def test_short_repeat_list_cannot_inherit_survival(self):
        raw={'status':'measured','passes':True,'members':[{'member':0,'score':{
            'pixels':[4]*7,'survives':True,'heldoutCoverage':True,
            'median':{'failed':[False]*3,'railChannels':[False]*3},
            'runs':[{'failed':[False]*3,'railChannels':[False]*3} for _ in range(6)]}}]}
        with self.assertRaisesRegex(ValueError,'seven'):a.compact('numerical',raw)

    def test_exact_maps_validate_hashes_identity_and_membership(self):
        with tempfile.TemporaryDirectory() as name:
            root=Path(name);(root/'candidate.png').write_bytes(b'pixels');(root/'baseline.png').write_bytes(b'pixels')
            (root/'projection.json').write_text('{"deep":1}')
            def row(png):return dict(png=png,pngSha256=a.sha(root/png),projection='projection.json',
                                    projectionSha256=a.sha(root/'projection.json'))
            candidate={'claimed':row('candidate.png'),'identity':row('candidate.png')}
            baseline={'claimed':row('baseline.png'),'identity':row('baseline.png')}
            rendered,identity=a.maps(root,candidate,baseline,['claimed','identity'],{'identity'})
            self.assertEqual(set(rendered['cells']['claimed']),{'png','projection'})
            self.assertEqual(set(identity['cells']),{'identity'})
            with self.assertRaisesRegex(ValueError,'membership'):a.maps(root,candidate,baseline,['claimed'],{'identity'})
            (root/'baseline.png').write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError,'hash'):a.maps(root,candidate,baseline,['claimed','identity'],{'identity'})
            baseline['identity']['pngSha256']=a.sha(root/'baseline.png')
            baseline['claimed']['pngSha256']=a.sha(root/'baseline.png')
            with self.assertRaisesRegex(ValueError,'identity'):a.maps(root,candidate,baseline,['claimed','identity'],{'identity'})

    def test_admission_equivalence_requires_original_unclaimed_wrapper(self):
        raw={'status':'measured','passes':False,'diagnostic':'S0','members':[]}
        expected={'status':'not claimed (structured backdrop)','passes':None,'score':raw}
        self.assertEqual(a.check_admission('not claimed (structured backdrop)',raw,expected),expected)
        with self.assertRaisesRegex(ValueError,'admission'):a.check_admission('not claimed (structured backdrop)',raw,True)
        with self.assertRaisesRegex(ValueError,'claimed'):a.check_admission('claimed uniform body',raw,True)

    def test_actual_runner_assessments_and_membership_survive_reduction(self):
        runner=a.module('assembly_test_runner',Path(__file__).resolve().parents[1]/'runner.py')
        wave=runner.boundary.default_wave()
        cells=runner.cells_for(wave,('calibration',))
        claim={'endpoints':[{'colorScheme':'light','activation':'inactive'}]}
        cell=next(c for c in cells if runner.endpoint(wave,c)==('light','inactive')
                  and wave.spec['backgrounds'][wave.scenes[c.split('/')[1]]['background']]['kind']=='solid')
        raw={'status':'measured','passes':True,'members':[{'member':0,'score':{
            'pixels':[4]*7,'survives':True,'heldoutCoverage':True,
            'median':{'failed':[False]*3,'railChannels':[False]*3},
            'runs':[{'failed':[False]*3,'railChannels':[False]*3} for _ in range(7)]}}]}
        with tempfile.TemporaryDirectory() as name:
            root=Path(name);rp=root/'raw.json.gz';ap=root/'admission.json.gz'
            def write(path,value):path.write_bytes(gzip.compress(json.dumps(value).encode(),mtime=0))
            write(rp,{cell:raw});write(ap,{cell:True})
            result=a.reduce_kind('numerical',rp,ap,{cell},wave,claim,runner,lambda c:'claimed uniform body')
            self.assertEqual(result[1],{cell:True});self.assertEqual(result[3],1)
            write(ap,{})
            with self.assertRaisesRegex(ValueError,'membership'):
                a.reduce_kind('numerical',rp,ap,{cell},wave,claim,runner,lambda c:'claimed uniform body')
            write(ap,{cell:True})
            with self.assertRaisesRegex(ValueError,'membership'):
                a.reduce_kind('numerical',rp,ap,{cell,'missing'},wave,claim,runner,lambda c:'claimed uniform body')
            raw['passes']=False;write(rp,{cell:raw})
            with self.assertRaisesRegex(ValueError,'status'):
                a.reduce_kind('numerical',rp,ap,{cell},wave,claim,runner,lambda c:'claimed uniform body')


if __name__=='__main__':unittest.main()
