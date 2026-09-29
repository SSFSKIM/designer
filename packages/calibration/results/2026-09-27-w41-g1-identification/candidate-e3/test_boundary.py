"""Synthetic native envelopes and fresh web frames; no archive Reader or payload."""
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import scorer as s


def example(structured=False):
    scope,_=s.runner.admitted_scope(s.ROOT,s.wave)
    cell=next(c for c in scope['rendered'] if s.identity(c)[0]=='light-inactive'
              and (s.identity(c)[1]['kind']!='solid')==structured)
    comp,scale=s.base.component(cell)
    w,h=s.runner.dimension(s.wave,cell)
    pixels=np.full((h,w,3),100,dtype=np.uint8)
    return cell,dict(rgb=pixels,noGlass=pixels.copy(),component=comp,scale=scale,
                     scheme='light',pose='inactive')


class BoundaryTests(unittest.TestCase):
    def test_no_authorization_means_no_native_constructor(self):
        with patch.object(s.wave,'reader',side_effect=AssertionError('must not construct')):
            with self.assertRaises(PermissionError):s.native_reader('/nonexistent',('holdout',))
        with self.assertRaises(PermissionError):s.score(SimpleNamespace(authorization=None))

    def test_authorization_failure_precedes_membership_or_file_reads(self):
        class Expired:
            def check(self,*args):raise PermissionError('expired')
        request=SimpleNamespace(authorization=Expired(),wave=s.wave)
        with patch.object(s,'native_reader',side_effect=AssertionError('must not construct')):
            with self.assertRaisesRegex(PermissionError,'expired'):s.score(request)

    def test_seven_normal_repeats_preserved_even_when_one_unique_state(self):
        cell,payload=example()
        archive=s.module('e3_synthetic_archive',s.W39/'w39_archive.py')
        raw=archive.pack(payload); key=archive.sha(raw)
        rows=[dict(admitted=True,protocol='normal',state=key) for _ in range(7)]
        rows += [dict(admitted=False,protocol='normal',state=key),
                 dict(admitted=True,protocol='diagnostic',state=key)]
        class Reader:
            def read(self,identity,kind):
                self_identity=(identity,kind)
                if self_identity!=(cell,'crop'):raise AssertionError(self_identity)
                return archive.bundle(rows,{key:raw})
        observed,states=s.payloads(Reader(),cell)
        self.assertEqual(len(observed),7); self.assertEqual(states,[key]*7)
        rows.pop(0)
        with self.assertRaisesRegex(ValueError,'seven'):s.payloads(Reader(),cell)

    def test_payload_cell_pose_mismatch_refused(self):
        cell,payload=example(); payload['pose']='rest'
        archive=s.module('e3_synthetic_archive_pose',s.W39/'w39_archive.py')
        raw=archive.pack(payload);key=archive.sha(raw)
        rows=[dict(admitted=True,protocol='normal',state=key) for _ in range(7)]
        reader=SimpleNamespace(read=lambda *args:archive.bundle(rows,{key:raw}))
        with self.assertRaisesRegex(ValueError,'identity'):s.payloads(reader,cell)

    def test_structured_deep_worsening_veto_is_binding_on_fresh_png(self):
        cell,payload=example(structured=True)
        native=[payload]*7; comp,scale=s.base.component(cell)
        shapes=s.m.readers.shapes_of(comp)
        geo=s.m.readers.geometry(payload['rgb'].shape[:2],shapes,scale)
        pixels=payload['rgb'].copy()
        deep=(geo.d<=-s.m.readers.DEEP_CSS*scale)
        pixels[deep]=102
        with tempfile.TemporaryDirectory() as t:
            baseline=Path(t)/'baseline.png';candidate=Path(t)/'fresh.png'
            Image.fromarray(payload['rgb']).save(baseline)
            Image.fromarray(pixels).save(candidate)
            scored=s.rendered_score(cell,candidate,baseline,native,['synthetic']*7)
            self.assertFalse(scored['vetoPass'])
            self.assertFalse(scored['passes'])
            self.assertEqual(scored['disposition'],'not claimed (structured backdrop)')
            deep_veto=[v for v in scored['veto'] if v['part']=='deep']
            self.assertTrue(deep_veto)
            self.assertTrue(all(not v['score']['passes'] for v in deep_veto))
            self.assertEqual(len(deep_veto[0]['score']['runs']),7)
            self.assertTrue(scored['rawRendered']['exterior'])
            self.assertTrue(scored['interiorTransfer'])
            self.assertEqual(scored['captureSha256'],s.sha(candidate))
            # The exact same code reads a new path; replacing the fresh frame changes
            # its result without changing a numerical prediction or frozen projection.
            Image.fromarray(payload['rgb']).save(candidate)
            unchanged=s.rendered_score(cell,candidate,baseline,native,['synthetic']*7)
            self.assertTrue(unchanged['vetoPass']);self.assertTrue(unchanged['identityBytesEqual'])

    def test_structured_rendered_diagnostic_is_not_numerical_s0(self):
        cell,payload=example(structured=True)
        native=[payload]*7
        comp,_=s.base.component(cell)
        prediction={'members':[{'member':i,'predictedRGB':[100,100,100]}
                               for i,shape in enumerate(s.m.readers.shapes_of(comp)) if not shape.opaque]}
        numerical=s.numerical(cell,prediction,native,['synthetic']*7)
        self.assertEqual(numerical['diagnostic'],'S0')
        with tempfile.TemporaryDirectory() as t:
            png=Path(t)/'frame.png'
            Image.fromarray(payload['rgb']).save(png)
            rendered=s.rendered_score(cell,png,png,native,['synthetic']*7)
            self.assertEqual(rendered['diagnostic'],'rendered structured deep')

    def test_projection_checks_dependency_runtime_before_image_read(self):
        with patch.object(s.np,'__version__','different'):
            with self.assertRaisesRegex(RuntimeError,'runtime differs'):
                s.project('unused',Path('/nonexistent'))


if __name__=='__main__':unittest.main()
