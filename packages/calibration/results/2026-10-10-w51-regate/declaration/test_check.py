"""Membership mutations must refuse without reading a capture or native payload."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
FIT = REPO/'packages/calibration/results/2026-10-08-w50-g1-fit'
G0 = REPO/'packages/calibration/results/2026-10-08-w50-g0-declaration'
spec = importlib.util.spec_from_file_location('w51_declaration_check', HERE/'check.py')
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

    def test_original_keys_and_finite_rehearsal_additions_pass(self):
        C.validate_membership(self.root, self.inventory, self.fit, self.populations)

    def test_equal_count_substitution_of_a_gate_statistic_refuses(self):
        changed = copy.deepcopy(self.populations)
        keys = changed['gate']['statisticKeys']
        keys[0][3] = 'unpriced-statistic'
        keys.sort()
        with self.assertRaises(ValueError):
            C.validate_membership(self.root, self.inventory, self.fit, changed)

    def test_dropping_text_owner_companion_refuses_even_with_updated_count(self):
        changed = copy.deepcopy(self.populations)
        doc = changed['rehearsal']
        key = next(k for k in doc['statisticKeys']
                   if k[2] == 'hc-text-7__rrect-md__rest' and k[3] == 'owner-contracts')
        doc['statisticKeys'].remove(key)
        doc['statisticCount'] -= 1
        with self.assertRaises(ValueError):
            C.validate_membership(self.root, self.inventory, self.fit, changed)

    def test_withheld_physical_cell_cannot_be_added_to_rehearsal(self):
        changed = copy.deepcopy(self.populations)
        doc = changed['rehearsal']
        key = changed['exposure']['statisticKeys'][0]
        doc['statisticKeys'].append(key)
        doc['statisticKeys'].sort()
        doc['physicalCells'] = sorted({tuple(k[:3]) for k in doc['statisticKeys']})
        doc['physicalCount'] = len(doc['physicalCells'])
        doc['statisticCount'] = len(doc['statisticKeys'])
        with self.assertRaises(ValueError):
            C.validate_membership(self.root, self.inventory, self.fit, changed)

    def test_original_role_cannot_be_relabelled_for_rehearsal(self):
        changed = copy.deepcopy(self.populations)
        changed['rehearsal']['originalMetadata'][0]['role'] = 'blind'
        with self.assertRaises(ValueError):
            C.validate_membership(self.root, self.inventory, self.fit, changed)


if __name__ == '__main__':
    unittest.main()
