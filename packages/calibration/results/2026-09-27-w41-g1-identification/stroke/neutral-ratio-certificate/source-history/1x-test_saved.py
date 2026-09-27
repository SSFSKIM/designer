"""Saved-evidence replay, sealed interval semantics and source-boundary checks."""
import copy
from fractions import Fraction as F
import unittest
from unittest.mock import patch
import numpy as np
import execute as e


class SavedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m,cls.native,cls.manifest,_=e.boot(e.PROOF)

    def test_saved_replay_never_constructs_native_reader(self):
        with patch.object(self.native,'guarded',side_effect=AssertionError('archive Reader invoked')):
            result=e.replay(e.PROOF)
        self.assertEqual(result['nativeArchiveReads'],0)
        self.assertEqual(result['optimizerCalls'],0)
        for endpoint in e.ENDPOINTS:
            self.assertEqual(result['endpoints'][endpoint]['screenedPairs'],4032)
            self.assertEqual(result['endpoints'][endpoint]['witnessPairs'],0)
            for model in ('M1','M2'):
                self.assertEqual(result['endpoints'][endpoint]['models'][model]['status'],'NOT_DETERMINING')

    def test_original_archive_and_raw_tree_are_actually_denied(self):
        for root in [e.Path.home()/'vitrea-w39',e.Path(self.manifest['archiveRoot'])]:
            with self.assertRaises(PermissionError):
                (root/'__nonexistent_ratio_guard_test__').read_bytes()

    def test_allowance_is_max_not_one_plus_bar(self):
        pixels=np.full((7,4,3),50,dtype=int)
        pixels[0]=48;pixels[1]=52
        result=e.pixel_intervals(pixels,40,self.m)
        self.assertEqual(result['barRGB'],['5/2']*3)
        self.assertEqual({row['bound'] for row in result['rows']},{'5/2'})
        # Intersect 48+-2.5 and 52+-2.5, then subtract input40.
        self.assertEqual(result['departure'],['19/2','21/2'])

    def test_censored_channel_is_omitted_not_treated_as_rgb(self):
        pixels=np.full((7,4,3),50,dtype=int);pixels[0,0,0]=255
        result=e.pixel_intervals(pixels,40,self.m)
        self.assertEqual([r['channel'] for r in result['omittedChannels']],[0])
        self.assertEqual(len(result['rows']),16)
        self.assertEqual({r['channel'] for r in result['rows']},{1,2})
        self.assertEqual(result['departure'],['9','11'])

    def test_population_and_repeat_shortfalls_are_refused(self):
        for shape in [(7,3,3),(6,4,3)]:
            with self.assertRaises(ValueError):e.pixel_intervals(np.full(shape,50),40,self.m)

    def test_reference_level_change_is_refused(self):
        row=dict(self.manifest['records'][0],b=254)
        with self.assertRaisesRegex(ValueError,'reference is not uniform neutral'):
            e.derive([row],self.m,self.native)

    def test_repeat_supplied_geometry_change_is_refused(self):
        unpack=self.native.archive.unpack;calls=0
        def changed(raw):
            nonlocal calls
            p=unpack(raw);calls+=1
            if calls==2:
                p=copy.deepcopy(p)
                p['component']['suppliedPaths'][0]['frameOrigin'][0]+=.25
            return p
        with patch.object(self.native.archive,'unpack',side_effect=changed):
            with self.assertRaisesRegex(ValueError,'geometry differs across seven repeats'):
                e.derive(self.manifest['records'][:1],self.m,self.native)


if __name__=='__main__':unittest.main()
