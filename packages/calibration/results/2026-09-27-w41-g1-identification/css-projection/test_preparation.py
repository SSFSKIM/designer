"""Public membership and proof gates; these tests never launch a browser."""
import tempfile
import json
import hashlib
import subprocess
import numpy as np
from unittest.mock import patch
from pathlib import Path
import unittest
from PIL import Image
import prepare as p


class Preparation(unittest.TestCase):
    def test_only_uniform_lightinactive_admitted_calval(self):
        cells=p.cells()
        self.assertEqual(len(cells),130)
        self.assertEqual(sum(v['role']=='calibration' for v in cells.values()),112)
        self.assertEqual(sum(v['role']=='validation' for v in cells.values()),18)
        self.assertEqual({v['scale'] for v in cells.values()},{1,2})
        self.assertTrue(all('light-' in c and c.endswith('__inactive') for c in cells))
        self.assertTrue(all(len(v['rgb'])==3 for v in cells.values()))

    def test_browser_proof_requires_pixels_not_computed_css(self):
        for scale in (1,2):
            image=Image.new('RGB',(320*scale,280*scale))
            for row in p.proof_rows():
                rgb=tuple(round(x) for x in row['expectedRGB'])
                x,y=row['sample'];image.putpixel((x*scale,y*scale),rgb)
            result=p.proof_pixels(image,scale)
            self.assertTrue(result['passes'])
            # A browser that ignores all filters cannot pass the witness.
            for row in p.proof_rows():
                x,y=row['sample'];image.putpixel((x*scale,y*scale),tuple(row['rgb']))
            self.assertFalse(p.proof_pixels(image,scale)['passes'])

    def test_wrong_order_fails_proof(self):
        image=Image.new('RGB',(320,280))
        for row in p.proof_rows():
            rgb=tuple(round(x) for x in row['expectedRGB'])
            image.putpixel(tuple(row['sample']),rgb)
        first=p.proof_rows()[0]
        image.putpixel(tuple(first['sample']),(64,64,64))
        self.assertFalse(p.proof_pixels(image,1)['passes'])

    def test_generated_proof_hashes_text_in_browser_not_restricted_cli_vm(self):
        with tempfile.TemporaryDirectory() as tmp:
            public=Path(tmp)/'public';p.build(public)
            run=subprocess.run(['node',str(p.HERE/'proof-vm-test.cjs'),str(public)],
                               capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stderr)
            result=p.parse_run_log(run.stdout,kind='proof',scale=1,
                manifest_sha=p.s.sha(public/'manifest.json'),
                config_sha=p.s.sha(public/'playwright-1x.json'),
                script_sha=p.s.sha(public/'proof-1x.js'),
                paths={('proof','proof'):str(p.CAPTURES/'proof-1x.png')})
            self.assertEqual(result['rows'][0]['sha256'],
                hashlib.sha256(b'offline mock screenshot').hexdigest())

    def test_chromatic_proof_rejects_ignored_and_linear_light_saturation(self):
        rows=p.proof_rows()
        chromatic=[r for r in rows if r['filter']=='saturate(2)']
        self.assertEqual(len(chromatic),8)
        self.assertTrue(any(r.get('plateAlpha',0)>0 and r.get('plateRGB')==255 for r in chromatic))
        self.assertTrue(any(r.get('plateAlpha',0)>0 and r.get('plateRGB')==0 for r in chromatic))
        self.assertTrue(any(r['intermediateClips'] for r in chromatic))
        image=Image.new('RGB',(320,280))
        for row in rows:image.putpixel(tuple(row['sample']),tuple(round(c) for c in row['expectedRGB']))
        self.assertTrue(p.proof_pixels(image,1)['passes'])
        for row in chromatic:
            a=row.get('plateAlpha',0);n=row.get('plateRGB',0)
            ignored=np.asarray(row['rgb'])*(1-a)+a*n
            image.putpixel(tuple(row['sample']),tuple(round(c) for c in ignored))
        self.assertFalse(p.proof_pixels(image,1)['passes'])
        for row in chromatic:
            x=np.asarray(row['rgb'])/255
            linear=np.where(x<=.04045,x/12.92,((x+.055)/1.055)**2.4)
            l=linear @ p.p.CSS_W
            saturated=np.clip(l+2*(linear-l),0,1)
            encoded=np.where(saturated<=.0031308,12.92*saturated,1.055*saturated**(1/2.4)-.055)
            image.putpixel(tuple(row['sample']),tuple(round(c) for c in
                255*((1-row.get('plateAlpha',0))*encoded+row.get('plateAlpha',0)*row.get('plateRGB',0)/255)))
        self.assertFalse(p.proof_pixels(image,1)['passes'])

    def test_run_log_rejects_forged_membership_and_stale_manifest(self):
        row=dict(cell='a/b',route='plate',scale=1,path='/capture/a.png',sha256='f'*64,
                 observed=dict(cell='a/b',route='plate',dpr=1,filter='saturate(2)',bodyOnly=True,productionTier=False))
        record=dict(kind='capture',manifestSha256='a'*64,configSha256='b'*64,
                    proofSha256='c'*64,scriptSha256='d'*64,proofRunIds=['proof-one','proof-two'],runId='capture-one',browserName='chromium',version='123.0.0',
                    userAgent='Chrome/123',dpr=1,viewport=dict(width=320,height=280),rows=[row])
        raw='W41_CSS_RUN:'+json.dumps(record)+'\n'
        parsed=p.parse_run_log(raw,kind='capture',scale=1,manifest_sha='a'*64,
            config_sha='b'*64,script_sha='d'*64,paths={('a/b','plate'):'/capture/a.png'},proof_sha='c'*64)
        self.assertEqual(parsed,record)
        for changed in [dict(record,manifestSha256='0'*64),dict(record,rows=[]),
                        dict(record,rows=[row,row]),dict(record,scriptSha256='e'*64),dict(record,runId=''),dict(record,browserName='firefox'),
                        dict(record,rows=[dict(row,observed=dict(row['observed'],dpr=2))])]:
            with self.assertRaises(ValueError):
                p.parse_run_log('W41_CSS_RUN:'+json.dumps(changed),kind='capture',scale=1,
                    manifest_sha='a'*64,config_sha='b'*64,script_sha='d'*64,
                    paths={('a/b','plate'):'/capture/a.png'},proof_sha='c'*64)

    def test_existing_pngs_alone_cannot_be_attested_as_a_capture_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);public=root/'public';public.mkdir()
            (public/'manifest.json').write_text('{}')
            for scale in (1,2):
                Image.new('RGB',(320*scale,280*scale)).save(root/f'proof-{scale}x.png')
            (public/'proof-passed.json').write_text(json.dumps(dict(passes=True,sources={},
                results=[dict(png=str(root/f'proof-{scale}x.png'),sha256=p.s.sha(root/f'proof-{scale}x.png')) for scale in (1,2)])))
            path=root/'plate'/'a'/'b.png';path.parent.mkdir(parents=True)
            Image.new('RGB',(320,280)).save(path)
            other=root/'affine'/'a'/'b.png';other.parent.mkdir(parents=True)
            Image.new('RGB',(320,280)).save(other)
            with patch.object(p,'verify_public',return_value={'sources':{},'cells':{'a/b':{'scale':1}}}),\
                 patch.object(p,'CAPTURES',root),patch.object(p,'verify_passed_proof',return_value={'runIds':['one','two']}),\
                 patch.object(p,'capture_path',side_effect=lambda route,scale,cell:root/route/'a'/'b.png'):
                with self.assertRaises(ValueError):p.capture_manifest(public,root/'captures.json',(root/'missing1.txt',root/'missing2.txt'))
                self.assertFalse((root/'captures.json').exists())

    def test_body_only_projection_does_not_claim_active_shadow(self):
        web=dict(composite='complete opaque web frame; active shadow included',members=[{'member':'one'}])
        result=p.body_projection(web)
        self.assertEqual(result['members'],web['members'])
        self.assertIn('BODY-only',result['composite'])
        self.assertNotIn('shadow included',result['composite'])

    def test_score_rejects_missing_run_records_before_native_reader(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);public=root/'public';public.mkdir()
            (public/'manifest.json').write_text('{}');(public/'proof-passed.json').write_text('{}')
            captures=root/'captures.json'
            captures.write_text(json.dumps(dict(publicManifestSha256=p.s.sha(public/'manifest.json'),
                proofSha256=p.s.sha(public/'proof-passed.json'),captures={'a/b':{}},cliRuns=[])))
            with patch.object(p,'verify_public',return_value={'cells':{'a/b':{'scale':1}}}),\
                 patch.object(p,'verify_passed_proof',return_value={'runIds':['one','two']}),\
                 patch.object(p.s,'native_reader') as reader:
                with self.assertRaises(ValueError):p.score(public,captures,root/'scores')
                reader.assert_not_called()

    def test_capture_path_never_escapes_owned_tree(self):
        with self.assertRaises(ValueError):p.capture_path('../escape',1,'a/b')
        with self.assertRaises(ValueError):p.capture_path('affine',1,'../../escape')


if __name__=='__main__':unittest.main()
