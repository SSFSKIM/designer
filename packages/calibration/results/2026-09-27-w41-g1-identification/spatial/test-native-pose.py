"""Archive pose vocabulary must be translated before endpoint grouping."""
import importlib.util
from pathlib import Path
import unittest

p=Path(__file__).with_name('read-spatial-v2.py')
s=importlib.util.spec_from_file_location('read_spatial_v2',p)
reader=importlib.util.module_from_spec(s);s.loader.exec_module(reader)

class NativePoseTests(unittest.TestCase):
    def test_archive_rest_is_active_endpoint(self):
        self.assertEqual(reader.native_endpoint('light','rest'),'light-active')
        self.assertEqual(reader.native_endpoint('dark','inactive'),'dark-inactive')
    def test_unknown_pose_is_not_silently_inactive(self):
        with self.assertRaises(ValueError):reader.native_endpoint('light','unknown')

if __name__=='__main__':unittest.main()
