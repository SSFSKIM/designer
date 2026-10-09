"""Synthetic in-memory producer -> numerical boundary; no measured files are opened.

Run with the existing calibration Python environment (NumPy/Pillow/SciPy required).
"""
import importlib.util
from pathlib import Path
import sys
import types
import unittest

import numpy as np

HERE = Path(__file__).resolve().parent


def source(path, name):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


spec = importlib.util.spec_from_file_location('w50_judge_boundary', HERE/'numerical.py')
j = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = j
spec.loader.exec_module(j)
fixtures = source(HERE.parent/'measurement/test_capture.py', 'w50_boundary_synthetic_fixtures')
measurement = source(HERE.parent/'measurement/capture.py', 'w50_boundary_measurement')


class MeasurementBoundaryTests(unittest.TestCase):
    def test_producer_central8_identity_survives_all_channel_comparisons(self):
        native, masks, _ = fixtures.native_cell()
        web = np.full((384, 512, 3), 70, dtype=np.uint8)
        web[masks['center8']] = [70, 72, 70]
        current_pair = j.DocumentPair('a'*64, 'b'*64)
        candidate_pair = j.DocumentPair('e'*64, 'f'*64)
        for renderer in ('webgpu', 'css'):
            with self.subTest(renderer=renderer):
                produced = measurement.evaluate_native_supports(web, native, masks, renderer=renderer)
                pairs = {}
                # Carry the producer's own key, support, units and values unchanged. Evidence
                # identities are synthetic declarations, not an authentication of numeric maps.
                for name, statistic in produced['statistics'].items():
                    if not name.endswith('-channel-median'):
                        continue
                    n = native['statistics'][name]
                    identity = j.RowIdentity(native['profile'], renderer, native['scene'],
                                             name, statistic['support'])
                    def reading(value, pair):
                        return j.Reading('MEASURED', statistic['units'], tuple(value),
                                         j.Evidence('1'*64, '2'*64, pair))
                    reference = j.Reference(identity, '3'*64, reading(n['value'], None),
                        reading(n['value'], current_pair), 1, .5, 1)
                    candidate = j.Candidate(identity, reading(statistic['value'], candidate_pair))
                    pairs[name] = (reference, candidate)
                central = pairs['central8-channel-median']
                self.assertEqual(central[0].identity.support, 'center8')
                channel = j.channel_level(*central)
                self.assertEqual(channel.identity.statistic, 'central8-channel-median')
                self.assertEqual(channel.status, 'EXCEEDS')
                self.assertEqual([c.error for c in channel.components], [0, 2, 0])
                uniform = j.uniform_levels(40, *pairs['deep8-channel-median'], *central)
                self.assertEqual([r.status for r in uniform], ['WITHIN', 'EXCEEDS'])
                if renderer == 'css':
                    css = j.css_level_growth(*central)
                    self.assertEqual(css.identity.statistic, 'central8-channel-median')
                    self.assertEqual(css.status, 'EXCEEDS')
                    self.assertEqual([c.growth for c in css.components], [0, 2, 0])


if __name__ == '__main__':
    unittest.main()
