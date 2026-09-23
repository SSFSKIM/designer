#!/usr/bin/env python3.12
import unittest
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import numpy as np
import instrument as I


class Instrument(unittest.TestCase):
    def test_signed_cancellation_cannot_close_absolute_channels(self):
        native=np.array([[4.,0,8],[-4,0,-8],[4,0,8],[-4,0,-8]])
        stat=I.residual(native,np.zeros_like(native))
        self.assertEqual(stat['signedRGB'],[0,0,0])
        self.assertEqual(stat['maeRGB'],[4,0,8])
        self.assertFalse(I.closes(stat,[1,1,1]))

    def test_pairwise_bar_preserves_losing_states_before_plurality(self):
        values=[np.zeros((4,3)),np.zeros((4,3)),np.full((4,3),4.)]
        self.assertEqual(I.pairwise_bar(values),[4,4,4])
        self.assertEqual(I.pairwise_bar(values[:2]),[0,0,0])
        self.assertFalse(I.closes(I.residual(values[2],values[0]),[0,0,0]))

    def test_stadium_strata_and_population_from_geometry_only(self):
        geometry={'kind':'capsule-circular','size':[120,44],
                  'suppliedPaths':[{'frameOrigin':[100,78],'rect':[0,0,120,44],'elements':[]}]}
        d,nx,ny,arc=I.geometry(320,200,geometry,1)
        self.assertAlmostEqual(d[100,99],.5+0.25/(np.hypot(22.5,.5)+22.5))
        masks=I.strata(d,nx,ny,arc)
        total=sum(int(m.sum()) for _,m in masks)
        self.assertEqual(total,int(((d>=-2)&(d<4)).sum()))
        self.assertTrue(any(k[0]=='straight' for k,_ in masks))
        self.assertTrue(any(k[0]=='arc' for k,_ in masks))

    def test_point_closure_without_discrimination_is_not_identification(self):
        rows=[dict(role=role,stratum=str(n),pixels=8,maeRGB=[0,0,0],barRGB=[0,0,0],
                   intervalMAERGB=[0,0,0]) for role in ['calibration','validation'] for n in [0,1]]
        pair={'families':['zero','four-byte'], 'rows':[dict(role=r['role'],stratum=r['stratum'],
            separationRGB=[4,0,0],tauRGB=[1,1,1],nuisanceWidthRGB=[0,0,0]) for r in rows]}
        self.assertEqual(I.closure_verdict(rows,[],True)['outcome'],'insufficient resolution')
        self.assertEqual(I.closure_verdict(rows,[pair],True)['outcome'],'identified within declared families')
        self.assertEqual(I.closure_verdict(rows,[pair],False)['outcome'],'effective rendered contour response')
        wide=copy.deepcopy(pair)
        for r in wide['rows']:r['nuisanceWidthRGB']=[4,4,4]
        self.assertEqual(I.closure_verdict(rows,[wide],True)['outcome'],'insufficient resolution')
        rows[0]['pixels']=3
        self.assertEqual(I.closure_verdict(rows,[pair],True)['outcome'],'insufficient resolution')

    def test_unidentifiable_alignment_remains_an_explicit_nominal_cut(self):
        p=I.synthetic_payload()
        result=I.fit_alignment(p['background'],p['background'],p['component'],1)
        self.assertEqual(result['status'],'insufficient alignment signal')
        self.assertEqual(result.get('translationDevicePx'),[0,0])
        self.assertIsNone(result['physicalContourUncertaintyDevicePx'])

    def test_gradient_envelope_spans_opposite_omitted_quadrant_predictions(self):
        component=I.synthetic_payload()['component']
        d,*_=I.geometry(320,200,component,1)
        y,x=np.mgrid[:200,:320]
        u=(x-160)/60;v=(y-100)/22
        rgb=np.repeat((100+5*u+3*v+12*u*v)[...,None],3,axis=2)
        domain=d<=-6;boundary=np.abs(d)<4
        design=np.stack([np.ones_like(x),x/320-.5,y/200-.5],axis=2)
        full=design@np.linalg.lstsq(design[domain],rgb[domain],rcond=None)[0]
        predictions=[]
        for sx,sy in [(1,1),(1,-1),(-1,1),(-1,-1)]:
            kept=domain&~(((x-160)*sx>=0)&((y-100)*sy>=0))
            predictions.append(design[boundary]@np.linalg.lstsq(design[kept],rgb[kept],rcond=None)[0])
        predictions=np.array(predictions)
        self.assertTrue(np.any((predictions.min(axis=0)<full[boundary]) &
                               (predictions.max(axis=0)>full[boundary])))
        declared=np.max(predictions.max(axis=0)-predictions.min(axis=0),axis=0)
        declared+=np.max(np.abs(rgb[domain]-full[domain]),axis=0)+.5
        np.testing.assert_allclose(I.body_baseline(rgb,d,'linear-gradient')['uncertaintyRGB'],declared)

    def test_forward_composes_body_and_stroke_before_pixel_reduction(self):
        payload=I.synthetic_payload();component=payload['component']
        bg=lambda u,v:np.tile([128,128,128],(len(u),1))
        body=lambda u,v:np.tile([180,180,180],(len(u),1))
        stroke=lambda u,v,nx,ny:(np.full(len(u),.5),np.zeros((len(u),3)))
        prediction=I.forward_circular([(160,77),(160,78)],component,1,bg,body,stroke)
        self.assertEqual(prediction.tolist(),[[64,64,64],[180,180,180]])

    def test_report_never_opens_holdout_and_keeps_a_losing_state(self):
        import archive
        from wave import Wave
        path=Path(__file__).resolve().parent/'report-bars.py'
        loader=importlib.util.spec_from_file_location('report_bars',path)
        report=importlib.util.module_from_spec(loader);loader.loader.exec_module(report)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            scenes={'components':{'shape':{'kind':'capsule-circular','size':[120,44]}},
                'scenes':[{'id':s,'component':'shape'} for s in ['cal','held']],
                'profiles':[{'key':'profile','scenes':'all'}],
                'split':{'probe':['cal','held'],'calibration':[],'validation':[],'holdout':[]}}
            split={'calibration':['cal'],'validation':[],'holdout':['held']}
            for name,value in [('scenes',scenes),('split',split)]:
                (root/(name+'.json')).write_text(json.dumps(value))
            pins={name+'Sha256':hashlib.sha256((root/(name+'.json')).read_bytes()).hexdigest()
                  for name in ['scenes','split']}
            (root/'pins.json').write_text(json.dumps(pins))
            wave=Wave(root/'scenes.json',root/'split.json',root/'pins.json')
            baseline=I.synthetic_payload();minority=copy.deepcopy(baseline);minority['rgb'][77,160]+=4
            records=[dict(cell='profile/'+sid,run=str(run),admitted=True,
                          payload=value,inputHashes={'native':'synthetic'})
                     for sid in ['cal','held'] for run,value in enumerate([baseline,baseline,minority])]
            inventory=archive.produce(records,wave,root/'archive')
            self.assertNotIn('distinctStates',json.dumps(inventory))
            reader=wave.reader(root/'archive');opened=[];original=reader.read
            def guarded(cell,kind):
                opened.append(cell)
                self.assertNotEqual(cell,'profile/held')
                return original(cell,kind)
            reader.read=guarded
            for entry in inventory['entries']:
                if entry['cell']=='profile/held':(root/'archive'/entry['path']).write_bytes(b'UNREADABLE HELD SECRET')
            output=report.report(reader)
            self.assertEqual(len(output),1)
            self.assertEqual(output[0]['distinctStates'],2)
            self.assertTrue(archive.replay(reader,'profile/cal')['identical'])
            self.assertNotIn('UNREADABLE',json.dumps(output))
            self.assertTrue(opened)

    def test_archive_values_replay_the_actual_instrument(self):
        payload=I.synthetic_payload()
        original=I.analyse(payload)
        raw=I.pack(payload)
        restored=I.unpack(raw)
        self.assertEqual(original,I.analyse(restored))
        self.assertEqual(payload['rgb'].tobytes(),restored['rgb'].tobytes())
        self.assertEqual(payload['background'].tobytes(),restored['background'].tobytes())
        self.assertEqual(payload['opaque'].tobytes(),restored['opaque'].tobytes())


if __name__=='__main__':unittest.main()
