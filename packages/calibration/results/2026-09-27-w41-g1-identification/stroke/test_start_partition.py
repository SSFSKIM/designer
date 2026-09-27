"""Partitioning must preserve starts, order, random draws and function globals."""
import unittest
import numpy as np
import start_partition


def example():
    starts = [np.array([1., .4]), *np.random.default_rng(4100).uniform(0, 2, (15, 2))]
    records = []
    for i, start in enumerate(starts):
        records.append(dict(index=i, initial=start.tolist(), answer=float(np.sum(start**2))))
    return records


class PartitionTests(unittest.TestCase):
    def test_partition_union_is_exact_original_order_and_seed(self):
        reference = example()
        combined = []
        for indices in ((0, 3, 6, 9, 12, 15), (1, 4, 7, 10, 13), (2, 5, 8, 11, 14)):
            selected, provenance = start_partition.partition(example, indices)
            self.assertEqual(selected(), [reference[i] for i in indices])
            combined.extend(selected())
            self.assertFalse(provenance['budgetsChanged'])
        self.assertEqual(sorted(combined, key=lambda r: r['index']), reference)
        self.assertEqual(example(), reference)

    def test_empty_or_outside_indices_refused(self):
        for indices in ([], [-1], [16], [1.5]):
            with self.assertRaises(ValueError):
                start_partition.partition(example, indices)


if __name__ == '__main__':
    unittest.main()
