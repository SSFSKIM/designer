"""Synthetic repeat admission and frozen-input checks; no native payload is opened."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

import baseline as b
spec = importlib.util.spec_from_file_location('transfer_v2', Path(__file__).with_name('transfer-v2.py'))
transfer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(transfer)


class TransferV2Tests(unittest.TestCase):
    def test_seven_normal_repeats_survive_one_state_and_long_sentinels_are_separate(self):
        runs = [dict(admitted=True, protocol='normal', state='one-state',
                     run=f'normal-{i}') for i in range(1, 8)]
        runs += [dict(admitted=True, protocol='long', state='one-state',
                      run=f'long-{i}') for i in range(1, 4)]
        runs += [dict(admitted=False, protocol='normal', state='one-state', run='excluded')]
        selected, counts = transfer.select_normal(runs)
        self.assertEqual([r['run'] for r in selected], [f'normal-{i}' for i in range(1, 8)])
        self.assertEqual([r['state'] for r in selected], ['one-state'] * 7)
        self.assertEqual(counts, {'admittedNormal': 7, 'admittedLongSentinel': 3,
                                  'excludedNormal': 1, 'excludedLongSentinel': 0})
        with self.assertRaisesRegex(ValueError, 'seven distinct normal'):
            transfer.select_normal(runs[1:])
        with self.assertRaisesRegex(ValueError, 'seven distinct normal'):
            transfer.select_normal(runs[:6] + [runs[0]] + runs[7:])

    def test_verification_never_requires_pre_w41_runtime_after_capture(self):
        # Runtime can change after the 536 captures, but the sealed scorer,
        # instrument, native metadata and each frozen pixel still must match.
        with patch.object(b, 'verify_preparation', side_effect=AssertionError('live runtime')):
            record, frozen = transfer.verify_frozen_inputs()
        self.assertEqual(len(frozen['captures']), 536)
        self.assertEqual(set(frozen['captures']), set(record['cells']))


if __name__ == '__main__':
    unittest.main()
