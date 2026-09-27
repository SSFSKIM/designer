"""Checks on the additive report, including the observed defect and support verdict."""
import gzip
import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
import unittest

HERE = Path(__file__).resolve().parent
OUTPUT = HERE / 'attempt-2'


def rows(name):
    with gzip.open(OUTPUT / name, 'rt') as f:
        for line in f:
            yield json.loads(line)


class ArtifactTests(unittest.TestCase):
    def test_recorded_white_exterior_is_no_longer_a_measured_pass(self):
        for method in ('leastSquares','minimax'):
            row = next(r for r in rows(f'light-inactive-{method}.jsonl.gz')
                       if r['cell'].endswith('/g255-c-c44__inactive') and r['scale']==1
                       and r['side']=='top' and r['shell']==1)
            self.assertEqual(row['geometryStatus'],'measured')
            self.assertEqual(row['legacyAbsoluteResidualRGB'], [[0,0,0]]*8)
            self.assertEqual(len(row['states']),8)
            for state in row['states']:
                self.assertEqual(state['channelStatus'], ['UNMEASURED']*3)
                self.assertEqual(state['upperCensoredCountsRGB'], [76]*3)
                self.assertEqual(state['measuredResidualRGB'], [None]*3)

    def test_real_censored_red_preserves_four_code_green_failure(self):
        row = next(r for r in rows('light-active-leastSquares.jsonl.gz')
                   if r['cell'].endswith('/g255-c-c44__rest') and r['scale']==1
                   and r['side']=='top' and r['shell']==-14)
        state = row['states'][0]
        self.assertEqual(state['channelStatus'], ['UNMEASURED','measured','UNMEASURED'])
        self.assertEqual(state['measuredResidualRGB'], [None,4.0,None])
        self.assertEqual(state['failedChannels'], [1])

    def test_corrected_column_members_retain_distinct_residual_blocks(self):
        old = json.loads(gzip.decompress((HERE.parent/
            'edge/dark-inactive-gn/leastSquares-bins.json.gz').read_bytes()))
        old = [r for r in old if r['cell'].endswith('/v90-column__inactive') and r['scale']==1]
        new = [r for r in rows('dark-inactive-leastSquares.jsonl.gz')
               if r['cell'].endswith('/v90-column__inactive') and r['scale']==1]
        self.assertEqual([r['member'] for r in new], [0]*360 + [1]*360)
        self.assertEqual([r['legacyMember'] for r in new], [0]*720)
        self.assertEqual([r['legacyAbsoluteResidualRGB'][0] for r in new],
                         [r['residualRGB'] for r in old])

    def test_all_eight_strata_have_uncensored_support_failure_in_every_run(self):
        report = json.loads((OUTPUT/'summary.json').read_text())
        support = [r for r in report['summary'] if r['method']=='support'
                   and r['role']=='calibration' and r['sourceKind']=='all']
        self.assertEqual(len(support),64)
        self.assertEqual({r['stateIndex'] for r in support},set(range(8)))
        for row in support:
            self.assertGreater(row['failingChannels'],0)
            self.assertGreater(row['failingCells'],0)
            worst=row['worstUncensored']
            self.assertEqual(worst['channelStatus'][worst['channel']], 'measured')
            self.assertGreater(worst['codes'], worst['toleranceCodes'])
        source_rows = [r for r in report['summary'] if r['method']=='support'
                       and r['role']=='calibration' and r['stateIndex']==0 and r['sourceKind']!='all']
        self.assertEqual(len(source_rows),16)
        self.assertEqual({r['sourceKind'] for r in source_rows},{'uniform','gradient'})

if __name__ == '__main__':
    unittest.main()
