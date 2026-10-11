"""DL3 keeps every fit statistic but refuses every non-fit real rehearsal identity."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
FIT = REPO/'packages/calibration/results/2026-10-08-w50-g1-fit'
G0 = REPO/'packages/calibration/results/2026-10-08-w50-g0-declaration'
spec = importlib.util.spec_from_file_location('w51_declaration_v2_check', HERE/'check.py')
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)


def load(path):
    return json.loads(path.read_bytes())


class Membership(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = load(FIT/'live-execution/execution-root-3.json')
        cls.inventory = load(G0/'references.json')
        cls.fit = load(FIT/'live-execution/run/fit-batch.json')
        cls.populations = {phase: load(HERE/(phase+'-population.json'))
                           for phase in ('gate', 'exposure', 'rehearsal')}

    def test_exact_fit840_with_all_original_statistics_passes(self):
        C.validate_membership(self.root, self.inventory, self.fit, self.populations)

    def test_equal_count_substitution_of_a_gate_statistic_refuses(self):
        changed = copy.deepcopy(self.populations)
        changed['gate']['statisticKeys'][0][3] = 'unpriced-statistic'
        changed['gate']['statisticKeys'].sort()
        with self.assertRaises(ValueError):
            C.validate_membership(self.root, self.inventory, self.fit, changed)

    def test_dropping_fit_statistic_refuses_even_with_updated_count(self):
        changed = copy.deepcopy(self.populations)
        doc = changed['rehearsal']
        doc['statisticKeys'].pop()
        doc['statisticCount'] -= 1
        with self.assertRaises(ValueError):
            C.validate_membership(self.root, self.inventory, self.fit, changed)

    def test_nonfit_impulse_cell_cannot_be_relabelled_as_a_real_rehearsal(self):
        changed = copy.deepcopy(self.populations)
        doc = changed['rehearsal']
        physical = ['apple-macos-27.0-1x-dark-standard-glass0.25', 'webgpu',
                    'impulse__rrect-ml__rest']
        extra = [k for k in changed['gate']['statisticKeys'] if k[:3] == physical]
        self.assertEqual(len(extra), 2)
        doc['statisticKeys'] += extra
        doc['statisticKeys'].sort()
        doc['physicalCells'].append(physical)
        doc['physicalCells'].sort()
        doc['physicalCount'] += 1
        doc['statisticCount'] += 2
        with self.assertRaises(ValueError):
            C.validate_membership(self.root, self.inventory, self.fit, changed)

    def test_nonfit_text_cell_cannot_be_relabelled_synthetic_in_real_population(self):
        changed = copy.deepcopy(self.populations)
        doc = changed['rehearsal']
        physical = ['apple-macos-27.0-1x-dark-standard-glass0.25', 'webgpu',
                    'hc-text-7__rrect-md__rest']
        doc['statisticKeys'] += [k for k in changed['gate']['statisticKeys'] if k[:3] == physical]
        doc['statisticKeys'].sort()
        doc['populationClass'] = 'SYNTHETIC'
        with self.assertRaises(ValueError):
            C.validate_membership(self.root, self.inventory, self.fit, changed)

    def test_original_role_cannot_be_relabelled_for_rehearsal(self):
        changed = copy.deepcopy(self.populations)
        changed['rehearsal']['originalMetadata'][0]['role'] = 'synthetic'
        with self.assertRaises(ValueError):
            C.validate_membership(self.root, self.inventory, self.fit, changed)


class Amendment(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.amendment = load(HERE/'amendment.json')
        cls.inputs = load(HERE/'inputs.json')
        cls.real = load(HERE/'rehearsal-population.json')
        cls.previous = load(HERE.parent/'declaration/rehearsal-population.json')

    def test_pre_pixel_amendment_preserves_scientific_inputs(self):
        C.validate_amendment(self.amendment, self.inputs, self.real, self.previous)

    def test_amendment_cannot_change_the_candidate_under_a_held_label(self):
        changed = copy.deepcopy(self.amendment)
        changed['heldScientificIdentities']['candidate']['proposalDigest'] = '0'*64
        with self.assertRaises(ValueError):
            C.validate_amendment(changed, self.inputs, self.real, self.previous)

    def test_pre_pixel_attestation_cannot_contain_an_analysis_marker(self):
        changed = copy.deepcopy(self.amendment)
        changed['prePixelAttestation']['captureOrAnalysisMarkers'] = ['analysis.started.json']
        with self.assertRaises(ValueError):
            C.validate_amendment(changed, self.inputs, self.real, self.previous)


if __name__ == '__main__':
    unittest.main()
