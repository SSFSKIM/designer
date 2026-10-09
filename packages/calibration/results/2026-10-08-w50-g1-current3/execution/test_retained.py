"""Retained records must reproduce original report admission, not just hash a filename."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import types
import unittest

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('retained',HERE/'retained.py')
R=importlib.util.module_from_spec(spec);spec.loader.exec_module(R)
OLD=HERE.parents[1]/'2026-10-08-w50-g1-fit/web'
spec=importlib.util.spec_from_file_location('original_web_test_fixture',OLD/'test_adapter.py')
F=importlib.util.module_from_spec(spec);spec.loader.exec_module(F)


class RetainedReconstruction(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.run=F.request();self.run.update(id='original-run',captureRoot=str(self.root),
            matrixPath=str(self.root/'index.json'),candidate={'path':str(self.root/'candidate.json'),'sha256':'a'*64})
        self.run['webSourceClosure']=self.put('closure.json',{'sources':[]})
        plan=F.A.scene_plan(self.run,'current');spec=plan['scenes'][0]
        self.endpoint={**F.endpoint(),'patch':{'backdropToneAbscissa':{'kind':'silhouette'}}}
        candidate={'path':self.run['candidate']['path'],'endpoints':{
            'active.dark':{'patch':{}},'receded.dark':self.endpoint}}
        self.fixture={'backgrounds':[{'key':'grey-004@2x','path':'synthetic','sha256':'b'*64}]}
        self.adapter=types.SimpleNamespace(scene_plan=F.A.scene_plan,read_json=R.load,
            pin_file=lambda pin:R.checked(pin),candidate_info=lambda *a,**k:candidate,
            fixture_info=lambda *a:self.fixture,validate_report=F.A.validate_report)
        report=self.put('report.json',F.report())
        cell=self.put('cell.json',{'renderer':'webgpu','colorSpace':'srgb','deterministic':True,'repeatNoise':0})
        png=self.root/'image.png';png.write_bytes(b'\x89PNG\r\n\x1a\n'+b'\0'*8+(1024).to_bytes(4,'big')+(768).to_bytes(4,'big'))
        image={'path':str(png),'sha256':R.sha(png)}
        request=self.put('request.json',dict(sceneSource='w50',scenesSha256=plan['scenesSha256'],
            candidate=self.run['candidate'],fixture=self.fixture,lane='current',argv=['driver','--renderer','webgpu',
            '--scale','2','--candidate-document',candidate['path'],'--out',str(self.root),self.run['scenes'][0]]))
        census=self.put('census.json',{'passes':True});log=self.put('log.json',{'synthetic':'log'})
        self.entry=dict(profile=self.run['profile'],renderer='webgpu',scene=self.run['scenes'][0],sceneSource='w50',
            candidate=self.run['candidate'],runIndex=11,artifacts={'png':image,'cell':cell,'report':report},
            originalEvidence={'request':request,'census':census,'log':log})

    def put(self,name,doc):
        path=self.root/name;path.write_text(json.dumps(doc)+'\n');return {'path':str(path),'sha256':R.sha(path)}

    def test_last39_without_run_index_reconstructs_through_original_validator(self):
        record=R.reconstruct(self.adapter,self.run,self.entry)
        self.assertEqual(record['scene'],self.run['scenes'][0]);self.assertEqual(record['arguments'][0]['encodedLuminance'],.1)
        self.assertEqual(record['artifacts'],self.entry['artifacts'])
        self.assertNotIn('second',record['artifacts'])

    def test_changed_original_geometry_refuses_even_with_recomputed_hash(self):
        report=F.report();report['page']['surfaces'][0]['bounds']['width']+=2
        self.entry['artifacts']['report']=self.put('report.json',report)
        with self.assertRaisesRegex(ValueError,'placement'):R.reconstruct(self.adapter,self.run,self.entry)

    def test_unstable_original_is_not_a_legacy_byteidentical_pair(self):
        self.entry['artifacts']['cell']=self.put('cell.json',{'renderer':'webgpu','colorSpace':'srgb',
            'deterministic':False,'repeatNoise':.000001})
        with self.assertRaises(ValueError):R.reconstruct(self.adapter,self.run,self.entry)

    def test_missing_transport_evidence_or_false_index_cannot_bless_retention(self):
        original=copy.deepcopy(self.entry)
        self.entry['originalEvidence'].pop('request')
        with self.assertRaises(ValueError):R.reconstruct(self.adapter,self.run,self.entry)
        self.entry=original;self.entry['runIndex']=0
        with self.assertRaises(ValueError):R.reconstruct(self.adapter,self.run,self.entry)
        self.entry['originalEvidence']['index']=self.put('index.json',{'schema':'w50-web-capture-index-1','captures':[]})
        with self.assertRaises(ValueError):R.reconstruct(self.adapter,self.run,self.entry)

    def test_index_and_raw_record_must_equal_source_reconstruction(self):
        record=R.reconstruct(self.adapter,self.run,self.entry)
        self.entry['runIndex']=0
        self.entry['originalEvidence']['index']=self.put('index.json',{'schema':'w50-web-capture-index-1','captures':[record]})
        self.entry['originalEvidence']['record']=self.put('record.json',record)
        self.assertEqual(R.reconstruct(self.adapter,self.run,self.entry),record)
        record['arguments'][0]['linearLuminance']=.9
        self.entry['originalEvidence']['record']=self.put('record.json',record)
        with self.assertRaises(ValueError):R.reconstruct(self.adapter,self.run,self.entry)


if __name__=='__main__':unittest.main()
