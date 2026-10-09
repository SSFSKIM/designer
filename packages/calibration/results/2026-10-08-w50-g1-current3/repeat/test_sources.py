"""Synthetic images only: original masks, both T bands and native-only bars."""
from pathlib import Path
import types
import unittest
import numpy as np

P = Path(__file__).with_name('sources.py')
S = types.ModuleType('repeat_sources'); S.__file__ = str(P)
exec(compile(P.read_bytes(), str(P), 'exec'), S.__dict__)


class SourcesTests(unittest.TestCase):
    def test_canonical_uses_same_original_native_support_for_both_images(self):
        native = np.full((64,64,3),128,dtype=np.uint8)
        background = np.zeros_like(native)
        first = native.copy(); second = native.copy(); second[0:4] = 255
        options = dict(component={'kind':'rrect','size':[48,48],'radius':0},
                       canvas={'width':64,'height':64}, scale=1, text=True)
        declared = [{'statistic':'T1-low','B':None,'stratum':'T','role':'gate'}]
        a,b = S.canonical_statistics(native,background,[native]*7,first,second,declared,
                                      provenance={'own':'synthetic-seven'},**options)
        self.assertEqual(set(a), {'T1-low','T1-fine'})
        self.assertEqual(a['T1-low']['support'], b['T1-low']['support'])
        self.assertEqual(a['T1-low']['repeat']['runs'],7)
        self.assertGreater(b['T1-fine']['value'],a['T1-fine']['value'])

    def test_fixed_t1_bar_does_not_replace_fidelity_band_bar(self):
        image = np.full((64,64,3),128,dtype=np.uint8)
        a,b = S.canonical_statistics(image,np.zeros_like(image),[image]*7,image,image,
            [{'statistic':'T1-low','B':.02,'stratum':'T','role':'gate'}],
            provenance={'own':'synthetic-seven'},component={'kind':'rrect','size':[48,48],'radius':0},
            canvas={'width':64,'height':64},scale=1,text=True)
        self.assertEqual(a['T1-low']['repeat']['bar'],.01)
        self.assertNotEqual(a['T1-fine']['repeat']['bar'],.01)

    def test_solid_undeclared_mean_cannot_veto_but_each_rgb_median_still_can(self):
        native=np.full((64,64,3),128,dtype=np.uint8)
        background=np.zeros_like(native)
        second=native.copy();second[20:28,20:28]=130
        options=dict(component={'kind':'rrect','size':[48,48],'radius':0},
                     canvas={'width':64,'height':64},scale=1)
        measured=S.R.M.canonical_read(native,background,web_rgb=second,**options)
        first_mean=measured['statistics']['deep8-luma-mean']['value']
        second_mean=measured['web']['statistics']['deep8-luma-mean']['value']
        self.assertGreater(second_mean-first_mean,.05)
        declared=[dict(statistic='low-end-path-level',backgroundKind='solid',role='gate')]
        first,repeat=S.canonical_statistics(native,background,[native]*7,native,second,declared,
                                            provenance={'own':'synthetic-seven'},**options)
        admitted=S.C.compare_statistics(first,repeat)
        self.assertEqual(set(admitted),{'deep8-channel-median'})
        self.assertEqual(admitted['deep8-channel-median']['first'],[128.,128.,128.])
        self.assertEqual(admitted['deep8-channel-median']['second'],[128.,128.,128.])
        for channel in range(3):
            moved=native.copy();moved[:,:,channel]=129
            a,b=S.canonical_statistics(native,background,[native]*7,native,moved,declared,
                                      provenance={'own':'synthetic-seven'},**options)
            with self.subTest(channel=channel),self.assertRaises(S.C.InstrumentFault):
                S.C.compare_statistics(a,b)

    def test_low_end_membership_is_backdrop_specific_and_keeps_independent_texture_rows(self):
        low=dict(statistic='low-end-path-level')
        self.assertEqual(set(S.canonical_membership([low,{'statistic':'T1-low'}],impulse=True)),
            {'deep8-far24-luma-mean','deep8-far24-luma-median','T1-low','T1-fine'})
        self.assertEqual(set(S.canonical_membership([low,{'statistic':'T1-full-silhouette'}],solid=True)),
            {'deep8-channel-median','T1-full-silhouette'})
        with self.assertRaises(S.C.InstrumentFault):S.canonical_membership([low])

    def test_owner_only_does_not_invent_statistics(self):
        image=np.full((64,64,3),128,dtype=np.uint8)
        a,b=S.canonical_statistics(image,np.zeros_like(image),[image]*7,image,image,
            [{'statistic':'owner-contracts','B':None}],provenance={'own':'synthetic'},
            component={'kind':'rrect','size':[48,48],'radius':0},canvas={'width':64,'height':64},scale=1)
        self.assertEqual(a,{})
        self.assertEqual(b,{})

class CanonicalSourceTests(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name).resolve()
        path=S.FIT/'references/test_canonical.py'
        self.F=S.source(path,'repeat_canonical_fixture')
        self.config,_,_,_=self.F.trees(self.root)

    def row(self,position):
        profile=self.F.profile(1,position);scene='text__r__rest'
        return dict(profile=profile,renderer='webgpu',scene=scene,stratum='T',
            statistic='T1-low',role='gate',nativeEvidence=self.F.pin(
                Path(self.config['fixtureRoot'])/profile/(scene+'.png')),B=None,
            currentEvidence={'path':'NEVER_OPEN_CURRENT','sha256':'a'*64})

    def test_missing_half_position_budget_uses_own_seven_without_current_baseline(self):
        row=self.row('0.5')
        image=S.R.decode_verified(row['nativeEvidence'],(200,320))
        a,b=S.canonical_pair(self.config,[row],image,image)
        self.assertEqual(set(a),{'T1-low','T1-fine'})
        self.assertEqual(a['T1-low']['repeat']['runs'],7)
        self.assertEqual(a['T1-low']['provenance']['source'],'w29')
        self.assertGreater(a['T1-low']['repeat']['spread'],0)
        self.assertEqual(a,b)

    def test_other_position_cannot_lend_its_native_source_or_floor(self):
        row=self.row('0.25')
        image=S.R.decode_verified(row['nativeEvidence'],(200,320))
        self.config['w43']['fetch']['sha256']='0'*64
        with self.assertRaises(ValueError):S.canonical_pair(self.config,[row],image,image)

if __name__=='__main__': unittest.main()
