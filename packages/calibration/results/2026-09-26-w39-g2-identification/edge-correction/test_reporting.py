"""Regression coverage for ordered members, channel-local summaries and scalar bounds."""
import gzip
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
import unittest
import tempfile
import numpy as np
from replay import classify, ordered_blocks, Summary, Output, checked_inputs, CACHE, BASE, HERE


class ReportingTests(unittest.TestCase):
    def test_replay_refuses_to_replace_existing_output(self):
        with tempfile.TemporaryDirectory(dir=HERE) as tmp:
            path = Path(tmp)/'output'
            output = Output(path, False)
            output.document('sentinel.json', {'original': 7})
            original = (path/'sentinel.json').read_bytes()
            with self.assertRaises(FileExistsError):
                Output(path, False)
            self.assertEqual((path/'sentinel.json').read_bytes(), original)
            with self.assertRaises(FileExistsError):
                output.document('sentinel.json', {'replacement': 9})
            self.assertEqual((path/'sentinel.json').read_bytes(), original)

    def test_one_censored_sample_invalidates_whole_required_channel(self):
        native = np.full((5, 3), 100.)
        native[0, 0] = 255
        states = classify(native, native, np.zeros(5, dtype=int),
                          [dict(pixels=5, status='measured')], np.ones((1,3)))
        self.assertEqual(states[0]['channelStatus'], ['UNMEASURED','measured','measured'])
        self.assertEqual(states[0]['upperCensoredCountsRGB'], [1,0,0])
        self.assertEqual(states[0]['uncensoredCountsRGB'], [4,5,5])

    def test_bounds_preserve_direction_and_do_not_establish_a_pass(self):
        native = np.tile([255,0,100], (4,1))
        pred = np.tile([248,7,100], (4,1))
        state = classify(native, pred, np.zeros(4,dtype=int),
                         [dict(pixels=4,status='measured')], np.ones((1,3)))[0]
        self.assertEqual(state['scalarBoundViolationRGB'], [2,2,0])
        self.assertEqual(state['measuredResidualRGB'], [None,None,0])
        self.assertEqual(state['failedChannels'], [])

    def test_absent_bins_remain_unmeasured_without_zero_error(self):
        state = classify(np.empty((0,3)),np.empty((0,3)),np.array([],dtype=int),
                         [dict(pixels=0,status='UNMEASURED')],np.ones((1,3)))[0]
        self.assertEqual(state['channelStatus'], ['UNMEASURED']*3)
        self.assertEqual(state['measuredResidualRGB'], [None]*3)
        self.assertIsNone(state['scalarBoundViolationRGB'])

    def test_geometry_unmeasured_is_not_overridden_by_good_channels(self):
        native = np.full((4,3), 100.)
        state = classify(native, native+3, np.zeros(4,dtype=int),
                         [dict(pixels=4,status='UNMEASURED')],np.ones((1,3)))[0]
        self.assertEqual(state['channelStatus'], ['UNMEASURED']*3)
        self.assertEqual(state['failedChannels'], [])

    def test_median_and_repeat_censoring_are_read_independently(self):
        pred = np.full((4,3),249.)
        median = classify(pred,pred,np.zeros(4,dtype=int),
                          [dict(pixels=4,status='measured')],np.ones((1,3)))[0]
        repeat = classify(pred+1,pred,np.zeros(4,dtype=int),
                          [dict(pixels=4,status='measured')],np.ones((1,3)))[0]
        self.assertEqual(median['channelStatus'], ['measured']*3)
        self.assertEqual(repeat['channelStatus'], ['UNMEASURED']*3)

    def test_summary_retains_failure_beside_censored_channel(self):
        states = classify(np.tile([255,100,100], (4,1)), np.tile([255,103,100], (4,1)),
                          np.zeros(4,dtype=int), [dict(pixels=4,status='measured')],np.ones((1,3)))
        row = dict(endpoint='light-active',scale=1,role='calibration',method='support',
            sourceKind='uniform',cell='example',member=0,part='straight',side='top',bin=1,shell=-14,
            pixels=4,toleranceRGB=[1,1,1],legacyAbsoluteResidualRGB=[[0,3,0]],states=states)
        summary = Summary()
        summary.add(row)
        result = next(r for r in summary.rows() if r['sourceKind']=='all')
        self.assertEqual(result['partlyMeasuredBins'],1)
        self.assertEqual(result['failingChannels'],1)
        self.assertEqual(result['failingCells'],1)
        self.assertEqual(result['worstUncensored']['channel'],1)
        self.assertIsNone(result['worstAllChannelComparison'])

    def test_shared_geometry_member_alias_does_not_merge_column_blocks(self):
        manifest, _, _ = checked_inputs(CACHE)
        records = [r for r in manifest['records'] if r['scheme']=='dark' and r['pose']=='inactive']
        old = json.loads(gzip.decompress((BASE/'edge/dark-inactive-gn/leastSquares-bins.json.gz').read_bytes()))
        blocks = [(r,b,rows) for r,b,rows in ordered_blocks(records, manifest['geometries'], old)
                  if r['scale']==1 and r['cell'].endswith('/v90-column__inactive')]
        self.assertEqual([r['member'] for r,b,rows in blocks],[0,1])
        self.assertEqual([{row['member'] for row in rows} for r,b,rows in blocks],[{0},{0}])
        self.assertNotEqual([row['residualRGB'] for row in blocks[0][2]],
                            [row['residualRGB'] for row in blocks[1][2]])
        # Block association retains each original value instead of aliasing by member0.
        self.assertEqual(sum(len(rows) for r,b,rows in blocks),720)

if __name__ == '__main__':
    unittest.main()
