"""Catch score paths that bypass supplied-path bins or omit repeats/channels."""
import tempfile
from pathlib import Path
import unittest
import numpy as np
from PIL import Image
import rendered
class RenderedTests(unittest.TestCase):
    def test_actual_png_and_native_share_geometry(self):
        component=dict(kind='capsule-circular',size=[120,44],suppliedPaths=[dict(kind='capsule-circular',rect=[0,0,120,44],frameOrigin=[20,20])])
        a=np.full((90,170,3),128,np.uint8)
        payload=dict(rgb=a,component=component,scale=1)
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'web.png';Image.fromarray(a).save(path)
            same=rendered.score_capture(path,[payload]*7)
            self.assertTrue(same['deep'][0]['survives'])
            self.assertTrue(all(not b['score']['worstChannelFailure'] for b in same['exterior'] if b['pixels']>=4))
            b=a.copy();b[19,42:118,1]=132;Image.fromarray(b).save(path)
            wrong=rendered.score_capture(path,[payload]*7)
            witness=next(v for v in wrong['exterior'] if v['part']=='straight' and v['side']=='top' and v['shell']==0)
            self.assertEqual(witness['score']['median']['errorCodes'],[0,4,0])
            self.assertEqual(len(witness['score']['runs']),7)
            self.assertFalse(witness['score']['survives'])
    def test_resolution_is_not_one_code_closure(self):
        self.assertEqual(rendered.resolution([[0,0,0]],[[2.9,0,0]],.5,.5)['verdict'],'insufficient resolution')
        self.assertEqual(rendered.resolution([[0,0,0]],[[3,0,0]],.5,.5)['verdict'],'separated instances')
if __name__=='__main__':unittest.main()
