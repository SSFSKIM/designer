"""Historical caps preserve misses without widening already-repaired entries."""
import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('w50_references', HERE / 'references.py')
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)


class HistoricalCaps(unittest.TestCase):
    def test_large_current_error_keeps_own_historical_growth_not_new_baseline(self):
        cap, growth = R.historical_cap(native=10, current=18, historical=12, budget=2)
        self.assertEqual((cap, growth), (3, 3))

    def test_repaired_entry_cannot_reopen_former_large_exception(self):
        cap, growth = R.historical_cap(native=10, current=11, historical=18, budget=2)
        self.assertEqual(cap, 1)
        self.assertEqual(growth, -3.5)

    def test_crossing_native_uses_absolute_error_not_signed_direction(self):
        cap, growth = R.historical_cap(native=10, current=4, historical=12, budget=2)
        self.assertEqual((cap, growth), (2, 2))


if __name__ == '__main__':
    unittest.main()
