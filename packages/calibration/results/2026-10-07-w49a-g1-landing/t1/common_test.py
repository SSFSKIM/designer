"""Guard the receded-only reseal: an active hash alone cannot identify its captures."""
import importlib.util
import sys
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("landing_common", Path(__file__).with_name("w49_inputs.py"))
common = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = common
spec.loader.exec_module(common)


class PairIdentity(unittest.TestCase):
    def test_reference_partition_is_per_cell_not_list_order(self):
        profile = "apple-macos-27.0-2x-dark-standard-glass0.25"
        self.assertEqual(common.selected_reference(profile, "impulse__rrect-lg__inactive"), "d0219cd684bf")
        self.assertEqual(common.selected_reference(profile, "impulse__rrect-ml__inactive"), "b2d074d2df24")
        self.assertEqual(common.selected_reference(profile, "checkerboard-32__rrect-lg__rest"), "d0219cd684bf")
        self.assertEqual(common.selected_reference(profile, "photo__rrect-md__rest"), "b2d074d2df24")

    def test_rejects_previous_receded_under_unchanged_active(self):
        path = ("materialProfile=profiles/active.json sha256:b2d074d2df24 "
                "recededProfile=profiles/receded.json sha256:29da6a888a23")
        self.assertEqual(common.capture_pair(path), ("b2d074d2df24", "29da6a888a23"))
        with self.assertRaises(ValueError):
            common.require_pair(path, common.PAIR)

    def test_accepts_resealed_pair(self):
        path = ("materialProfile=profiles/active.json sha256:b2d074d2df24 "
                "recededProfile=profiles/receded.json sha256:940384c06f73")
        common.require_pair(path, common.PAIR)

    def test_refuses_missing_or_duplicated_document_clause(self):
        with self.assertRaises(ValueError):
            common.capture_pair("materialProfile=active sha256:b2d074d2df24")
        with self.assertRaises(ValueError):
            common.capture_pair("materialProfile=a sha256:b2d074d2df24 "
                                "materialProfile=b sha256:b2d074d2df24 "
                                "recededProfile=r sha256:940384c06f73")


if __name__ == "__main__":
    unittest.main()
