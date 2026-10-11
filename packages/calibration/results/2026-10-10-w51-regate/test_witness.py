"""Completeness is about every declared identity, not a plausible row count."""
import importlib.util
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parent

def module():
    spec=importlib.util.spec_from_file_location('w51_witness_test',HERE/'witness.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

class WitnessTests(unittest.TestCase):
    def setUp(self):
        self.m=module();self.rows=[dict(profile='p',renderer='webgpu',scene='s',statistic=s)
                                  for s in ('T1-full-silhouette','low-end-path-level')]
        self.captures=[dict(profile='p',renderer='webgpu',scene='s',lane='candidate')]
    def test_duplicate_or_omitted_statistic_cannot_pass_by_matching_count(self):
        self.m.coverage(self.rows,self.captures,self.rows,self.rows)
        with self.assertRaises(ValueError):self.m.coverage(self.rows,self.captures,[self.rows[0]]*2,self.rows)
        with self.assertRaises(ValueError):self.m.coverage(self.rows,self.captures,self.rows,self.rows[:1])
    def test_duplicate_capture_or_current_lane_refuses(self):
        with self.assertRaises(ValueError):self.m.coverage(self.rows,self.captures*2,self.rows,self.rows)
        with self.assertRaises(ValueError):self.m.coverage(self.rows,[{**self.captures[0],'lane':'current'}],self.rows,self.rows)

if __name__=='__main__':unittest.main()
